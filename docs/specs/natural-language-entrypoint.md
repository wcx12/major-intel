# Major Intel 自然语言总入口设计

## 设计状态

本文档是自然语言总入口的第一版详细设计。它的目标是把用户一句自然语言问题，稳定转成：

1. 规范化意图。
2. 结构化槽位。
3. 一组本地 function call 调用。
4. 可追溯的工具结果。
5. 明确的数据口径、缺口和追问。
6. 给用户看的最终回答。

当前结论：

- 27 个底层检索工具已经具备 function call schema 和 dispatcher。
- 自然语言总入口的详细设计从本文件开始作为主设计口径。
- 离线规则入口已落地到 `scripts/natural_language_entrypoint.py`，并由 `tests/test_natural_language_entrypoint.py` 覆盖第一批高频场景。
- DeepSeek function-call agent 已落地到 `scripts/deepseek_retrieval_agent.py`，统一入口已落地到 `scripts/retrieval_agent_entrypoint.py`。

## 目标与边界

### 目标

自然语言总入口要解决的是“用户不需要知道工具名，也不需要知道数据库字段”。用户可以直接问：

```text
广东物理 580 想学计算机，有哪些稳一点的学校？
杭电计算机怎么样？
这个专业组会不会被调剂到冷门专业？
软件工程适合考公吗？
浙大和杭电计算机怎么选？
```

系统负责完成：

- 意图识别。
- 槽位抽取和规范化。
- 缺槽追问。
- 工具自动选择。
- 多工具调用顺序编排。
- 数据口径合并。
- 缺口识别。
- 拒答或人工兜底。
- 输出结构化 JSON 和可读回答。

### 非目标

第一版不做以下事情：

- 不做聊天前端。
- 不直接联网补数据。
- 不让大模型凭记忆回答事实。
- 不把学校级就业数据说成校专业级就业数据。
- 不把岗位文本命中说成考公岗位正式可报。
- 不把专业组构成说成真实分流比例。

## 总体架构

```text
用户自然语言问题
  -> EntryPoint.run(question, session_context)
  -> 文本清洗与候选槽位抽取
  -> 实体解析：学校、专业、省份、科类、年份、分数、位次
  -> 意图识别
  -> 槽位完整性检查
  -> 如果缺关键槽位：返回 needs_clarification
  -> 生成工具调用计划
  -> 读取缓存
  -> 执行本地 function call
  -> 合并工具结果
  -> 运行数据缺口检测
  -> 写 query_logs / retrieval_cache / data_gap_queue
  -> 生成最终回答
```

第一版建议采用“规则优先 + LLM 兜底”的混合路线：

- 高频问题用规则路由，便于测试和控风险。
- 规则无法稳定识别时，再交给 LLM 根据 function schema 自动选择工具。
- LLM 不直接生成事实，只能基于工具结果组织语言。

## 核心模块

| 模块 | 职责 | 建议文件 |
|---|---|---|
| `NaturalLanguageEntryPoint` | 总入口编排器 | `scripts/natural_language_entrypoint.py` |
| `IntentRouter` | 把自然语言归一成 intent | `scripts/natural_language_entrypoint.py` 第一版内置 |
| `SlotExtractor` | 从文本抽取省份、科类、分数、位次、学校、专业等槽位 | `scripts/natural_language_entrypoint.py` 第一版内置 |
| `ToolPlanner` | 根据 intent 和 slots 生成工具调用计划 | `scripts/natural_language_entrypoint.py` 第一版内置 |
| `ToolExecutor` | 调用 `call_retrieval_function` 并记录 trace | 复用 `scripts/retrieval_function_registry.py` |
| `ResultComposer` | 合并工具结果并形成输出 JSON | `scripts/natural_language_entrypoint.py` 第一版内置 |
| `AnswerWriter` | 生成可读 Markdown 或纯文本 | 第一版先用模板，后续接 LLM |
| `DeepSeekRetrievalAgent` | LLM function-call loop | `scripts/deepseek_retrieval_agent.py` |
| `HybridRetrievalEntryPoint` | 协调规则入口和 DeepSeek agent | `scripts/retrieval_agent_entrypoint.py` |
| `QueryLogger` | 写查询日志、缓存和工具轨迹 | 已接入 `scripts/agent_query_storage.py` |

第一版可以先把这些类放在同一个文件里，避免过早拆分。等逻辑稳定后再拆成独立模块。

## 输入输出协议

### 输入

```json
{
  "question": "广东物理 580 想学计算机，有哪些稳一点的学校？",
  "session_context": {
    "province": null,
    "subject_type": null,
    "score": null,
    "rank": null,
    "school_text": null,
    "major_text": null
  }
}
```

`session_context` 用于多轮对话。例如用户第一句说“我是广东物理 580”，第二句说“想学计科”，第二轮就可以继承第一轮槽位。

### 输出

```json
{
  "status": "ok",
  "intent": "rank_to_major_match",
  "slots": {
    "province": "广东",
    "subject_type": "物理",
    "score": 580,
    "rank": null,
    "major_text": "计算机"
  },
  "needs_clarification": [],
  "tool_plan": [
    {
      "tool_name": "rank_to_major_match",
      "arguments": {
        "province": "广东",
        "subject_type": "物理",
        "score": 580,
        "major_text": "计算机",
        "limit": 30
      }
    }
  ],
  "tool_trace": [],
  "data_gaps": [],
  "scope_notes": [],
  "warnings": [],
  "answer_markdown": "..."
}
```

### 状态枚举

| 状态 | 含义 |
|---|---|
| `ok` | 已经调用工具并形成可回答结果 |
| `partial` | 有部分数据，但关键口径不完整 |
| `needs_clarification` | 缺少必要槽位，需要追问 |
| `not_found` | 本地库未命中实体或数据 |
| `data_gap` | 问题需要本地库没有的数据，应进入缺口队列 |
| `error` | 入口或工具异常 |

## 槽位规范

| 槽位 | 类型 | 示例 | 说明 |
|---|---|---|---|
| `school_text` | string | 杭电、杭州电子科技大学 | 原始学校文本，后续由 `school_lookup` 规范化 |
| `major_text` | string | 计科、软件工程、计算机 | 原始专业文本，后续由 `major_lookup` 规范化 |
| `province` | string | 广东、浙江 | 考生所在省份或招生省份 |
| `subject_type` | string | 物理、历史、综合、理科、文科 | 高考科类 |
| `score` | number | 580 | 高考分数 |
| `rank` | number | 45000 | 省内位次，优先级高于分数 |
| `year` | integer | 2025 | 数据年份，不给时由工具使用可用历史数据 |
| `reference_years` | integer[] | [2023, 2024, 2025] | 历史参考年份 |
| `group_code` | string | 204 | 专业组代码 |
| `department_text` | string | 计算机学院 | 院系筛选词 |
| `city_preference` | string[] | 杭州、广州 | 城市偏好 |
| `school_level_filter` | string | 211、双一流、本科 | 学校层次偏好 |
| `risk_preference` | string | 冲、稳、保 | 志愿风险偏好 |
| `career_preference` | string | 就业、考公、读研 | 职业目标 |
| `budget_constraint` | string | 学费低、不接受中外合作 | 费用约束 |
| `comparison_targets` | object[] | A 校 B 校 | 对比对象 |

## 意图体系

### 已可直接落地的意图

| Intent | 用户典型问法 | 必填槽位 | 主要工具 | 数据口径 |
|---|---|---|---|---|
| `school_lookup` | 这个学校是哪所？杭电是哪个学校？ | `school_text` | `school_lookup` | 学校实体 |
| `major_lookup` | 计科是什么专业？软工代码是多少？ | `major_text` | `major_lookup` | 专业实体 |
| `school_profile` | 杭电怎么样？这学校是不是双一流？ | `school_text` | `school_profile` | 学校级 |
| `major_profile` | 计算机科学与技术学什么？就业方向如何？ | `major_text` | `major_profile`, `major_market_reference` | 专业通用级 |
| `school_major_list` | 杭电有什么专业？ | `school_text` | `school_major_list` | 学校开设专业 |
| `major_school_list` | 哪些学校有软件工程？ | `major_text` | `major_school_list` | 学校专业关系 |
| `school_major_profile` | 杭电计算机怎么样？ | `school_text`, `major_text` | `school_major_profile`, `admission_history`, `employment_summary` | 混合口径，必须标注 |
| `score_to_rank` | 广东物理 580 对应多少位次？ | `province`, `subject_type`, `score` | `score_to_rank` | 一分一段 |
| `rank_to_school_match` | 45000 位次能上哪些学校？ | `province`, `subject_type`, `rank` 或 `score` | `rank_to_school_match` | 历史录取位次参考 |
| `rank_to_major_match` | 广东物理 580 想学计算机能报哪些？ | `province`, `subject_type`, `major_text`, `rank` 或 `score` | `rank_to_major_match` | 历史专业录取参考 |
| `admission_history` | 杭电计算机广东录取位次是多少？ | `school_text` 或 `major_text` | `admission_history` | 历史录取统计 |
| `plan_history` | 这个专业招生计划几年变化如何？ | `school_text` | `plan_history` | 招生计划 |
| `specialty_group_lookup` | 这个专业在哪个专业组？这个组有哪些专业？ | `school_text` | `specialty_group_lookup` | 招生专业组 |
| `subject_requirement_lookup` | 软件工程要选什么科？ | `major_text` | `subject_requirement_lookup` | 招生选科样本 |
| `specialty_group_risk` | 这个专业组风险大吗？会不会调剂？ | `school_text` | `specialty_group_risk` | 组内构成初筛 |
| `school_department_major_list` | 杭电计算机学院有哪些专业？ | `school_text` | `school_department_major_list` | 院系专业关系 |
| `employment_summary` | 这个学校就业率和升学率怎样？ | `school_text` | `employment_summary` | 学校级就业 |
| `transfer_policy_lookup` | 这个学校能转专业吗？ | `school_text` | `transfer_policy_lookup` | 第三方政策线索 |
| `fee_and_campus_lookup` | 这个专业学费多少，在哪个校区？ | `school_text` | `fee_and_campus_lookup` | 学费线索，校区缺口 |
| `source_trace_lookup` | 这些数据靠谱吗？来自哪里？ | 当前回答上下文 | `source_trace_lookup` | 工具来源说明 |

### 暂不完整的意图

| Intent | 当前状态 | 第一版处理方式 |
|---|---|---|
| `comparison_query` | 已完成第一版 | 调用正式 `comparison_query`，返回学校/专业/校专业方案的结构化并列对比 |
| `major_streaming_policy_lookup` | 保守接口已完成 | 返回专业组上下文和分流政策缺口，不编造比例 |
| `civil_service_mapping` | 保守接口已完成 | 包装岗位文本命中样本，明确不是可报判定 |
| `policy_rule_lookup` | 保守接口已完成 | 返回招生章程/政策规则缺口，等待联网 agent 或人工 |
| 校专业级就业 Top 企业/薪资分布 | 数据缺口 | 返回 `data_gap`，不能用专业通用市场样本替代 |

## 路由规则

### 规则优先级

总入口按以下顺序识别意图：

1. 明确分数/位次问题。
2. 明确学校 + 专业组合问题。
3. 专业组、选科、调剂、分流问题。
4. 转专业、政策、费用、校区等高风险问题。
5. 就业、升学、考公问题。
6. 对比问题。
7. 单学校或单专业画像问题。
8. 来源可信度追问。
9. 无法识别时返回澄清。

这样排序是为了避免误路由。例如“杭电计算机 580 能不能上”不应只走 `school_major_profile`，而应优先进入分数/位次匹配。

### 关键词规则

| 关键词/模式 | 候选 intent |
|---|---|
| `分`、`位次`、`排名`、`能上`、`冲`、`稳`、`保` | `rank_to_school_match` 或 `rank_to_major_match` |
| `怎么样`、`值不值得`、`好不好` + 学校 + 专业 | `school_major_profile` |
| `有什么专业`、`开设哪些专业` | `school_major_list` |
| `哪些学校有`、`想学某专业` | `major_school_list` 或 `rank_to_major_match` |
| `专业组`、`组内`、`调剂` | `specialty_group_lookup` 或 `specialty_group_risk` |
| `选科`、`再选`、`物化`、`科目要求` | `subject_requirement_lookup` |
| `转专业`、`换专业` | `transfer_policy_lookup` |
| `学费`、`校区`、`住宿费`、`中外合作` | `fee_and_campus_lookup` |
| `就业`、`升学`、`保研` | `employment_summary`、`major_market_reference` |
| `考公`、`公务员`、`岗位`、`编制` | `civil_service_role_search` |
| `对比`、`哪个好`、`怎么选`、`A 和 B` | `comparison_query` |
| `来源`、`靠谱吗`、`数据哪里来的` | `source_trace_lookup` |

## 槽位完整性与追问

| Intent | 必填槽位 | 缺失时追问 |
|---|---|---|
| `school_profile` | `school_text` | “你想查哪所学校？” |
| `major_profile` | `major_text` | “你想查哪个专业？” |
| `school_major_profile` | `school_text`, `major_text` | “你想看哪所学校的哪个专业？” |
| `score_to_rank` | `province`, `subject_type`, `score` | “请补充省份、科类和分数。” |
| `rank_to_school_match` | `province`, `subject_type`, `score` 或 `rank` | “请补充省份、科类，以及分数或位次。” |
| `rank_to_major_match` | `province`, `subject_type`, `major_text`, `score` 或 `rank` | “请补充省份、科类、分数或位次，以及想看的专业方向。” |
| `specialty_group_lookup` | `school_text` | “请先告诉我学校；如果是具体报考场景，也建议补充省份、科类、年份。” |
| `specialty_group_risk` | `school_text` | “请告诉我学校和专业组；如果没有专业组代码，请补充省份、科类、年份，我先帮你查组。” |
| `transfer_policy_lookup` | `school_text` | “你想查哪所学校的转专业政策？” |
| `fee_and_campus_lookup` | `school_text` | “你想查哪所学校？如果关心某专业，也请补充专业名。” |
| `comparison_query` | `target_type`, `comparison_targets` | “你想比较哪几个学校、专业或方案？” |

追问输出必须使用 `needs_clarification`，不能先猜一个省份、科类或年份继续查。

## 工具编排策略

### 单工具场景

适合简单查询：

```text
“杭电是哪所学校？” -> school_lookup
“软件工程学什么？” -> major_profile
“杭电能转专业吗？” -> transfer_policy_lookup
```

### 多工具场景

#### 学校 + 专业评价

用户问题：

```text
杭电计算机怎么样？
```

调用计划：

```text
school_major_profile
employment_summary
admission_history
data_gap_detection
```

回答要求：

- 先说能确定的：学校层次、专业基础、学科/专业建设、录取参考。
- 再说不确定的：校专业级就业、真实薪资、Top 企业、官网专业介绍证据链。
- 不能把学校级就业率说成计算机专业就业率。

#### 分数 + 专业匹配

用户问题：

```text
广东物理 580 想学计算机，有哪些稳一点的学校？
```

调用计划：

```text
rank_to_major_match
```

工具内部已能在提供 score 时调用 `score_to_rank` 逻辑，所以总入口不必重复调用 `score_to_rank`，除非用户只问分数对应位次。

回答要求：

- 使用位次解释，不只看分数。
- 返回冲/稳/保或按用户风险偏好筛选。
- 明确历史录取不保证未来录取。
- 对专业大类、试验班、中外合作等变体给提示。

#### 专业组风险

用户问题：

```text
这个专业组会不会被调剂到冷门专业？
```

调用计划：

```text
specialty_group_lookup
specialty_group_risk
transfer_policy_lookup
data_gap_detection
```

回答要求：

- 只说“组内构成风险初筛”。
- 不说真实分流比例。
- 如果用户没给学校、省份、科类、年份或组代码，先追问。

#### 就业与考公

用户问题：

```text
软件工程就业和考公怎么样？
```

调用计划：

```text
major_profile
major_market_reference
civil_service_role_search
data_gap_detection
```

回答要求：

- 市场样本是专业通用观察，不是某校毕业去向。
- 考公结果是岗位文本命中，不是正式可报判定。
- 校专业级薪资、地域、Top 公司若没有数据，必须列为缺口。

#### 来源可信度追问

用户问题：

```text
这些数据靠谱吗？
```

调用计划：

```text
source_trace_lookup
```

如果是多轮对话，应读取上一轮 `tool_trace` 中的工具名，逐个调用 `source_trace_lookup`。

## 缓存、日志与缺口队列

第一版可以先不落库，但输出结构要预留这些字段。第二版接入 MySQL。

### `query_logs`

当前已由 `scripts/agent_query_storage.py` 建表。可执行：

```powershell
python scripts/agent_query_storage.py
```

第一版字段：

| 字段 | 含义 |
|---|---|
| `id` | 主键 |
| `session_id` | 会话 ID |
| `question_text` | 用户原始问题 |
| `intent` | 识别出的主意图 |
| `slots_json` | 槽位 JSON |
| `tool_plan_json` | 工具调用计划 |
| `tool_trace_json` | 工具执行结果 |
| `route` | `rules` / `deepseek` / `none` |
| `mode` | `auto` / `rules` / `deepseek` |
| `cache_key` | 命中的缓存键 |
| `cache_hit` | 是否来自缓存 |
| `status` | `ok` / `partial` / `needs_clarification` / `data_gap` / `error` |
| `created_at` | 创建时间 |

### `retrieval_cache`

缓存键建议由以下内容组成：

```text
intent + normalized_slots + tool_plan_version + data_version
```

不要只按原始问题文本缓存，因为“杭电计科怎么样”和“杭州电子科技大学计算机怎么样”应共享实体归一后的缓存。

第一版已经通过 `build_cache_identity()` 实现稳定缓存键：

```text
agent-cache-v1 + 规范化问题 + mode + route + intent + slots + tool_plan
```

### `agent_tool_traces`

第一版新增该表，用于把 `tool_trace_json` 拆成可检索行：

| 字段 | 含义 |
|---|---|
| `query_log_id` | 对应 `query_logs.id` |
| `tool_order` | 工具调用顺序 |
| `tool_name` | 工具名 |
| `arguments_json` | 工具入参 |
| `result_status` | 工具结果状态 |
| `result_json` | 工具完整结果 |

### `data_gap_queue`

第一版已在 `scripts/agent_query_storage.py` 落地，并由 `scripts/retrieval_agent_entrypoint.py` 在 `--enable-storage` 模式下自动写入。

写入条件：

- 工具返回 `data_gaps`。
- 用户问的是高风险事实，但本地库没有官方来源。
- 工具状态为 `not_found`，且该事实对回答用户问题是关键。
- intent 属于 `major_streaming_policy_lookup`、`policy_rule_lookup`、校专业级就业等官方证据链尚未接入的范围。

队列任务必须包含：

- 学校。
- 专业。
- 省份。
- 年份。
- 问题类型。
- 需要补的字段。
- 已有工具结果。
- 推荐来源类型，例如官网、就业质量报告、招生章程、教务处通知。

当前第一版已经记录 `gap_key`、`query_log_id`、`session_id`、问题类型、学校/专业/省份/科类/年份/批次、缺失字段、已有字段、用户原问题、规范化问题、优先级、状态、原因、建议来源和预期写回目标。后续联网 agent 和人工复核系统只需要消费 `pending` 队列即可。

## 动态 RAG 流程

动态 RAG 不应让联网搜索直接面对用户。推荐流程：

```text
总入口发现缺口
  -> 写 data_gap_queue
  -> SourceDiscoveryAgent 找官方来源
  -> CrawlerAgent 抓网页/PDF
  -> ExtractorAgent 抽取结构化字段
  -> VerifierAgent 校验年份、来源等级和冲突
  -> 低置信度进入人工审核
  -> WriterAgent 写回 source_documents / 事实表
  -> 缓存失效并重算答案
```

如果联网搜索也找不到，最终状态应是：

```json
{
  "status": "data_gap",
  "answer_markdown": "本地库和自动检索都没有找到可复核来源，不能给确定结论，已进入人工复核。",
  "data_gaps": ["校专业级就业地域分布", "Top 10 对口企业"]
}
```

## 回答生成规则

总入口的最终回答必须遵守：

1. 先回答用户真正问的问题。
2. 再说明依据来自哪些工具和数据口径。
3. 对 `scope_notes`、`warnings`、`data_gaps` 做用户可理解的压缩表达。
4. 缺口不能写成事实。
5. 高风险政策、转专业、分流、考公可报必须提示官方复核。
6. 分数/位次建议必须说明历史参考，不保证录取。
7. 输出不要堆数据库字段名，除非用户要求。

第一版可以用模板生成回答。LLM 只负责把结构化结果改写成自然语言，不能新增事实。

## 验收样例

| 用户问题 | 期望 intent | 期望工具 | 期望状态 |
|---|---|---|---|
| 杭电怎么样？ | `school_profile` | `school_profile` | `ok` 或 `not_found` |
| 杭电有什么专业？ | `school_major_list` | `school_major_list` | `ok` 或 `not_found` |
| 杭电计算机怎么样？ | `school_major_profile` | `school_major_profile`, `employment_summary`, `admission_history` | `partial` 可接受 |
| 广东物理 580 想学计算机 | `rank_to_major_match` | `rank_to_major_match` | `ok` 或 `not_found` |
| 45000 位次能冲什么？ | `rank_to_school_match` | 无，先追问 | `needs_clarification` |
| 软件工程要选什么科？ | `subject_requirement_lookup` | `subject_requirement_lookup` | `ok` 或 `not_found` |
| 杭电能转专业吗？ | `transfer_policy_lookup` | `transfer_policy_lookup` | `ok` / `partial` / `not_found` |
| 这个专业组会不会调剂到冷门？ | `specialty_group_risk` | 无，先追问 | `needs_clarification` |
| 软件工程适合考公吗？ | `civil_service_mapping` | `civil_service_mapping` | `partial` |
| A 和 B 怎么选？ | `comparison_query` | `comparison_query` | `ok` 或 `needs_clarification` |

## 实施分期

### 第 1 期：离线规则入口

目标：不用联网、不接真实 LLM，先让 10 个高频问题能稳定映射到工具。

建议实现：

- `scripts/natural_language_entrypoint.py`
- `tests/test_natural_language_entrypoint.py`

当前状态：已完成第一版。该版本不联网、不依赖真实 LLM；可以在执行模式下调用本地 function dispatcher，也可以用 `--no-execute` 只输出工具计划，适合手工检查路由是否正确。
当前专项测试覆盖 10 个场景：位次/分数推荐、缺槽追问、分数转位次、专业市场样本、学校专业列表、学校专业画像、考公样本、专业组风险追问、会话上下文补槽和 CLI 纯计划模式。

必须覆盖：

- 意图识别。
- 槽位抽取。
- 缺槽追问。
- 工具计划生成。
- 工具结果合并。
- 不混用就业口径。

### 第 2 期：接入 LLM tool-call loop

目标：把未提交的 DeepSeek agent 草稿整理进主干，作为 LLM 自动选择工具的实现。

当前状态：已完成第一版。`scripts/deepseek_retrieval_agent.py` 负责 DeepSeek function-call loop，`scripts/retrieval_agent_entrypoint.py` 负责统一入口；`auto` 模式下高频明确问题优先走规则入口，未知/复杂问题回退到 DeepSeek。

要求：

- 复用 `scripts/retrieval_function_registry.py` 的 schema。
- 保留 `tool_trace`。
- 对无效 JSON 参数、未知工具、过多工具轮次做保护。
- 禁止模型绕过工具直接回答事实。

### 第 3 期：缓存、日志与缺口记录

目标：把 `query_logs`、`retrieval_cache`、`agent_tool_traces` 和 `data_gap_queue` 接入 MySQL。

当前状态：已完成第一版。新增 `scripts/agent_query_storage.py`，并在 `scripts/retrieval_agent_entrypoint.py` 中通过 `--enable-storage` 接入 `query_logs`、`retrieval_cache`、`agent_tool_traces`、`data_gap_queue`。

要求：

- 同一规范化查询可命中缓存。
- 缓存必须记录工具版本和数据版本。
- 查询日志可复盘 intent、slots、tool_plan 和 tool_trace。
- 数据缺口可去重入队，供后续动态 RAG 和人工复核消费。

### 第 4 期：缺口队列与动态 RAG

目标：把 `data_gap_queue`、联网 agent 和人工复核闭环接起来。

当前状态：缺口队列第一版已完成；联网找源、抓取、抽取、校验、人工审核和写回仍未实现。

要求：

- 本地工具不命中时不编造。
- 自动检索只写证据，不直接生成最终事实。
- 来源冲突或低置信度进入人工复核。
- 人工确认后写回正式事实表或来源表。

## 当前完成判定

自然语言总入口的状态应更新为：

```text
详细设计：已完成第一版
离线规则入口：已完成第一版（`scripts/natural_language_entrypoint.py` + `tests/test_natural_language_entrypoint.py`）
LLM tool-call 入口：已完成第一版（`scripts/deepseek_retrieval_agent.py` + `tests/test_deepseek_retrieval_agent.py`）
统一入口：已完成第一版（`scripts/retrieval_agent_entrypoint.py` + `tests/test_retrieval_agent_entrypoint.py`）
缓存/日志：已完成第一版（`scripts/agent_query_storage.py` + `tests/test_agent_query_storage.py`）
缺口队列：已完成第一版（`data_gap_queue` 建表、去重入队、统一入口接入）
动态 RAG/人工复核闭环：未实现
```
