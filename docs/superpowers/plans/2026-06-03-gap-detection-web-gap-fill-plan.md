# 高考志愿 Agent 缺口检测与网页补全实施计划

> **给执行 Agent 的要求：** 实施本计划时，按任务逐项推进。每完成一个任务，都要先运行对应测试，再进入下一项。不要把网页搜索结果的摘要直接当作事实，最终答案只能引用已抓取、已校验、可追溯的证据。

**目标：** 建立一套确定性的缺口识别和缺口补全流程。高考志愿 Agent 先使用本地数据库工具回答；如果本地结果为空、部分缺失或证据不足，则结构化识别缺口，再通过官方网页证据进行有限轮次补全。对于仍无法确认的信息，明确返回未补全缺口，不编造结论。

**适用场景：** 专业开设院校、学校开设专业、录取历史、招生章程、选科要求、就业去向、培养方案等高考志愿相关问答。

**技术栈：** Python、pytest、现有 `RetrievalTools` 返回 envelope、现有 function-call registry、DeepSeek function-call agent、SearXNG JSON API、`web_evidence_fetch`。

---

## 一、当前问题

当前工具链已经具备本地数据库检索能力，也新增了网页证据搜索和抓取能力，但二者之间还缺少一个严谨的“缺口判断层”。

主要问题如下：

- 本地工具返回 `not_found` 或核心列表为空时，Agent 目前只能做较粗糙的一次性网页搜索。
- `data_gap_detection` 现在更像静态槽位检查，没有充分利用各工具真实返回结果。
- 多个工具都有“核心结果字段”，例如 `major_school_list.data.schools`、`school_major_list.data.majors`、`admission_history.data.records`，但还没有统一注册表描述这些字段。
- 网页工具 `web_evidence_fetch` 能搜索和抓网页，但不知道自己正在补哪个缺口，因此无法稳定判断“是否已经补上”。
- 第三方搜索结果可能有参考价值，但不能直接变成事实；必须由官网、考试院、阳光高考等可信来源确认。
- 用户问法经常带有地区、层级、年份、科类等限制，本地工具缺少数据时，Agent 需要知道到底缺的是“关系数据”“地区字段”“历史分数”还是“官方规则”。

---

## 二、目标流程

目标流程是：先本地，后缺口检测，再官方网页补全，最后带证据回答。

```text
用户问题
  -> Agent 选择本地检索工具
  -> 本地工具返回结构化结果
  -> 检测 status、核心字段、data_gaps、normalized_slots
  -> 生成结构化 gap_items
  -> 筛选 resolvable_by_web=true 的缺口
  -> 调用 web_gap_fill 做有限轮次搜索、抓取、证据评估
  -> 返回 filled_items、accepted_evidence、unfilled_gaps
  -> Agent 只基于本地结果和 accepted_evidence 回答
```

回答规则：

- 本地数据库命中且核心字段完整：直接回答，可附带数据来源为本地库。
- 本地数据库未命中但网页官方证据补上：回答时说明“本地库未命中，以下根据官方网页证据补充”。
- 只搜到第三方结果，未抓取到官方证据：不能当作已确认事实，只能说明“未能从可信来源确认”。
- 达到搜索轮次或抓取上限仍未补上：返回明确的未补全缺口。

---

## 三、涉及文件

需要修改的主要文件：

- `scripts/retrieval_tools.py`
  - 增加核心字段注册表。
  - 升级 `data_gap_detection`。
  - 增加 `_detect_tool_result_gaps`。
  - 新增 `web_gap_fill`。
  - 增加 CLI parser 和 dispatcher。

- `scripts/retrieval_function_registry.py`
  - 注册 `web_gap_fill`。
  - 补充 schema 测试。

- `scripts/deepseek_retrieval_agent.py`
  - 调整工具 fallback 顺序。
  - 优先调用 `web_gap_fill`，再考虑底层 `web_evidence_fetch`。
  - 最终答案只使用 accepted evidence。

- `tests/test_gap_detection_registry.py`
  - 新增缺口检测注册表测试。

- `tests/test_web_gap_fill.py`
  - 新增网页缺口补全测试。

- `tests/test_retrieval_tools.py`
  - 更新 `data_gap_detection` 的状态语义测试。

- `tests/test_retrieval_function_registry.py`
  - 增加 `web_gap_fill` 注册测试。

- `tests/test_deepseek_retrieval_agent.py`
  - 增加 Agent fallback 优先级测试。

- `tests/function_calls/web_gap_fill/README.md`
  - 新增工具说明、测试范围、测试结果和改进建议。

- `.env.example`
  - 如需要，补充网页补全轮次和抓取上限配置。

---

## 四、核心设计

### 1. 核心结果字段注册表

不同工具的“查到数据”不能只看 `status=ok`。应该明确每个工具的核心字段。

示例：

```python
TOOL_CORE_FIELDS = {
    "school_major_list": ["data.majors"],
    "major_school_list": ["data.schools"],
    "admission_history": ["data.records"],
    "rank_to_school_match": ["data.matches"],
    "rank_to_major_match": ["data.matches"],
}
```

判断原则：

- 核心字段不存在：视为缺口。
- 核心字段是空列表：视为缺口。
- 核心字段是空字典：视为缺口。
- 核心字段是空字符串：视为缺口。
- 核心字段非空：视为该维度有结果。

### 2. 结构化 gap_items

`data_gap_detection` 不应只返回字符串列表。它应该返回结构化缺口对象，供 Agent 和后续工具稳定消费。

建议结构：

```json
{
  "gap_key": "major_school_relation",
  "label": "专业开设院校关系",
  "question_type": "major_school_list",
  "missing_fields": ["major_school_relation"],
  "resolvable_by_web": true,
  "preferred_source_types": ["chsi", "exam_authority", "official"],
  "evidence_requirements": [
    "school_name",
    "major_name_or_code",
    "undergraduate_level",
    "source_url",
    "evidence_snippet"
  ],
  "normalized_slots": {
    "major_name": "人工智能",
    "major_code": "080717T",
    "province_filter": "上海",
    "school_level_filter": "本科"
  }
}
```

状态语义：

- `ok`：已知问题类型，且没有发现缺口。
- `partial`：已知问题类型，发现部分缺口。
- `not_found`：核心查询对象不存在，或核心结果为空且没有其它可用信息。
- `needs_clarification`：缺少必要槽位，或者 `question_type` 未知。

未知问题类型必须返回：

```json
{
  "status": "needs_clarification",
  "data": {
    "supported_question_types": ["..."]
  }
}
```

不能再返回 `ok + missing_items=[]`。

### 3. GAP_REGISTRY

建议增加确定性的缺口注册表。

第一版至少覆盖这些缺口：

```python
GAP_REGISTRY = {
    "major_school_relation": {
        "label": "专业开设院校关系",
        "question_types": ["major_school_list"],
        "required_fields": ["major_school_relation"],
        "resolvable_by_web": True,
        "preferred_source_types": ["chsi", "exam_authority", "official"],
        "evidence_requirements": [
            "school_name",
            "major_name_or_code",
            "undergraduate_level",
            "source_url",
            "evidence_snippet",
        ],
    },
    "school_major_catalog": {
        "label": "学校开设专业目录",
        "question_types": ["school_major_list"],
        "required_fields": ["school_major_catalog"],
        "resolvable_by_web": True,
        "preferred_source_types": ["official", "chsi"],
        "evidence_requirements": [
            "school_name",
            "major_name_or_code",
            "source_url",
            "evidence_snippet",
        ],
    },
    "admission_history": {
        "label": "专业录取历史",
        "question_types": ["admission_history"],
        "required_fields": ["admission_history"],
        "resolvable_by_web": True,
        "preferred_source_types": ["exam_authority", "official"],
        "evidence_requirements": [
            "school_name",
            "major_name",
            "province",
            "year",
            "score_or_rank",
            "source_url",
        ],
    },
    "official_admission_rule": {
        "label": "官方招生规则原文",
        "question_types": ["policy_rule_lookup"],
        "required_fields": ["official_admission_rule"],
        "resolvable_by_web": True,
        "preferred_source_types": ["official"],
        "evidence_requirements": [
            "school_name",
            "policy_text",
            "source_url",
            "evidence_snippet",
        ],
    },
    "streaming_ratio": {
        "label": "真实分流比例",
        "question_types": ["major_streaming_policy_lookup"],
        "required_fields": ["streaming_ratio"],
        "resolvable_by_web": False,
        "non_resolvable_reason": "真实分流比例通常不是稳定公开数据，不能通过网页自动确认。",
        "preferred_source_types": [],
        "evidence_requirements": [],
    },
}
```

后续可以逐步把 27 个工具都纳入这个注册表，但第一版不要一次性追求全覆盖。先覆盖高频、风险最高的志愿问答链路。

---

## 五、实施任务

## Task 1：增加核心结果字段注册表

**目标：** 用统一方式判断工具是否真的查到了核心结果。

**修改文件：**

- `scripts/retrieval_tools.py`
- `tests/test_gap_detection_registry.py`

**步骤：**

- [ ] 新增 `TOOL_CORE_FIELDS`。
- [ ] 新增 `_get_path_value(payload, path)`，支持 `data.schools` 这种点路径。
- [ ] 新增 `_core_field_empty(payload, field_path)`。
- [ ] 新增 `_infer_available_fields(tool_name, result)`。
- [ ] 写测试覆盖：
  - `major_school_list.data.schools=[]` 判定为空。
  - `school_major_list.data.majors=[]` 判定为空。
  - `admission_history.data.records=[]` 判定为空。
  - 非空列表被识别为可用字段。

**建议测试命令：**

```powershell
python -m pytest tests/test_gap_detection_registry.py -q
```

**验收标准：**

- 空核心字段不会被误判为完整数据。
- 可用字段推断不依赖自然语言字符串。

---

## Task 2：升级 data_gap_detection

**目标：** 让 `data_gap_detection` 从静态槽位检查升级为结构化缺口判断接口。

**修改文件：**

- `scripts/retrieval_tools.py`
- `tests/test_retrieval_tools.py`
- `tests/function_calls/data_gap_detection/README.md`

**步骤：**

- [ ] 引入 `GAP_REGISTRY`。
- [ ] 让 `data_gap_detection` 返回 `gap_items`。
- [ ] 对已知问题类型：
  - 无缺口返回 `ok`。
  - 有缺口返回 `partial`。
- [ ] 对未知问题类型：
  - 返回 `needs_clarification`。
  - 返回 `supported_question_types`。
- [ ] 保留 `missing_items`，但它只作为兼容字段。
- [ ] README 更新状态语义。

**关键测试：**

```python
def test_data_gap_detection_returns_partial_with_gap_items():
    result = tools.data_gap_detection(
        question_type="major_school_list",
        available_fields=["major_basic", "major_code", "province", "school_level"],
    )

    assert result["status"] == "partial"
    assert result["data"]["gap_items"][0]["gap_key"] == "major_school_relation"
    assert result["data"]["gap_items"][0]["resolvable_by_web"] is True
```

**验收标准：**

- `unknown_question_type` 不再返回 `ok`。
- `missing_items` 非空时不再返回 `ok`。
- 下游 Agent 可以直接读取 `gap_items`。

---

## Task 3：从工具结果中自动识别缺口

**目标：** 不只依赖用户显式调用 `data_gap_detection`，而是能根据每个工具返回结果自动生成缺口。

**修改文件：**

- `scripts/retrieval_tools.py`
- `tests/test_gap_detection_registry.py`

**步骤：**

- [ ] 新增 `_detect_tool_result_gaps(tool_name, result)`。
- [ ] 读取工具 `status`。
- [ ] 检查 `TOOL_CORE_FIELDS`。
- [ ] 合并工具返回的 `data_gaps`。
- [ ] 合并 `normalized_slots`。
- [ ] 给每个缺口标记触发原因：
  - `status_not_found`
  - `core_result_empty`
  - `explicit_data_gaps`
  - `missing_required_slot`
- [ ] 返回可直接传给 `web_gap_fill` 的结构化 gap 对象。

**示例：**

```python
gaps = _detect_tool_result_gaps("major_school_list", result)

assert gaps[0]["gap_key"] == "major_school_relation"
assert gaps[0]["normalized_slots"]["major_name"] == "人工智能"
assert gaps[0]["normalized_slots"]["province_filter"] == "上海"
```

**验收标准：**

- `major_school_list` 查询上海本科人工智能为空时，能识别为 `major_school_relation` 缺口。
- 结果中保留原始工具名、触发原因、标准化槽位。

---

## Task 4：注册 web_gap_fill 工具

**目标：** 增加一个面向 Agent 的高级网页补全工具，不让 Agent 直接拼多轮搜索策略。

**修改文件：**

- `scripts/retrieval_tools.py`
- `scripts/retrieval_function_registry.py`
- `tests/test_retrieval_function_registry.py`

**工具职责：**

`web_gap_fill` 接收一个或多个结构化缺口，内部调用搜索、抓取和证据评估逻辑，输出已补全项和未补全项。

**建议 schema：**

```json
{
  "name": "web_gap_fill",
  "description": "基于可信网页证据补全本地数据库未命中的高考志愿信息缺口。",
  "parameters": {
    "type": "object",
    "properties": {
      "gap_items": {
        "type": "array",
        "items": {"type": "object"}
      },
      "question": {"type": "string"},
      "max_rounds": {"type": "integer", "default": 3},
      "max_fetches_per_round": {"type": "integer", "default": 5},
      "source_policy": {
        "type": "string",
        "enum": ["official_only", "trusted_first", "any"],
        "default": "official_only"
      }
    },
    "required": ["gap_items"]
  }
}
```

**返回结构：**

```json
{
  "status": "ok | partial | not_found | needs_clarification | error",
  "data": {
    "filled_items": [],
    "accepted_evidence": [],
    "rejected_evidence": [],
    "unfilled_gaps": [],
    "rounds": []
  }
}
```

**验收标准：**

- registry 中能看到 `web_gap_fill`。
- CLI 可以直接运行该工具。
- schema 中包含 `gap_items`、`max_rounds`、`source_policy`。

---

## Task 5：实现 major_school_relation 查询规划

**目标：** 对“某地区哪些院校开设某专业”这类问题，生成更稳定的搜索查询。

**修改文件：**

- `scripts/retrieval_tools.py`
- `tests/test_web_gap_fill.py`

**输入示例：**

```json
{
  "gap_key": "major_school_relation",
  "normalized_slots": {
    "major_name": "人工智能",
    "major_code": "080717T",
    "province_filter": "上海",
    "school_level_filter": "本科"
  }
}
```

**查询策略：**

第一轮：权威来源优先。

```text
人工智能 080717T 上海 本科 开设 院校 site:gaokao.chsi.com.cn
人工智能 上海 本科 招生专业 site:*.edu.cn
上海 人工智能 本科 招生专业 学校
```

第二轮：候选学校扩展。

```text
上海 高校 人工智能专业 招生
上海 本科 人工智能 专业目录
```

第三轮：逐校验证。

```text
{学校名} 人工智能 本科 招生专业
{学校名} 080717T 招生专业
{学校名} 本科招生专业 人工智能
```

**注意：**

- 搜索结果只能提供候选，不直接成为事实。
- 真正进入 `filled_items` 必须通过抓取页面文本并通过证据评估。
- 如果本地库地区字段缺失，不应把“未搜到上海”直接解释为“上海没有院校开设”。

**验收标准：**

- 查询语句包含专业名、专业代码、地区、学校层级。
- 能基于候选学校继续逐校验证。
- 每轮查询有上限，避免无限搜索。

---

## Task 6：实现证据评估器

**目标：** 判断抓取到的网页内容是否真的补上了缺口。

**修改文件：**

- `scripts/retrieval_tools.py`
- `tests/test_web_gap_fill.py`

**major_school_relation 的证据要求：**

网页文本至少要满足：

- 出现专业名或专业代码，例如 `人工智能` 或 `080717T`。
- 能识别学校名。
- 能判断本科层级，或来源本身是本科招生专业目录。
- 来源类型符合策略：
  - `official_only`：只接受学校官网、考试院、阳光高考等。
  - `trusted_first`：优先官方，必要时保留第三方为 rejected 或参考候选。
  - `any`：允许更宽来源，但最终答案必须标注证据等级。

**评估输出：**

```json
{
  "accepted": true,
  "gap_key": "major_school_relation",
  "school_name": "上海交通大学",
  "major_name": "人工智能",
  "major_code": "080717T",
  "source_url": "https://...",
  "source_type": "official",
  "evidence_snippet": "...人工智能...",
  "confidence": "high"
}
```

**拒绝原因：**

- `source_policy_rejected`
- `missing_major_name`
- `missing_school_name`
- `wrong_level`
- `third_party_only`
- `fetch_failed`
- `content_too_short`

**验收标准：**

- 第三方页面不会被误放入 `accepted_evidence`。
- 官方页面中没有专业名时不会被接受。
- 通过的证据必须包含 URL、source_type、snippet。

---

## Task 7：实现 web_gap_fill 主循环

**目标：** 把查询规划、网页抓取和证据评估串成一个有上限的补全工具。

**修改文件：**

- `scripts/retrieval_tools.py`
- `tests/test_web_gap_fill.py`

**主循环逻辑：**

```text
for round_index in range(max_rounds):
    1. 根据未补全 gap 生成搜索 query
    2. 调用 web_evidence_fetch
    3. 遍历 fetched_pages
    4. 用 evidence evaluator 判断是否接受
    5. accepted -> filled_items
    6. rejected -> rejected_evidence
    7. 如果 gap 已满足，移出 unfilled_gaps
    8. 如果没有新增候选或达到上限，停止
```

**状态规则：**

- 所有 gap 都补上：`ok`
- 部分 gap 补上：`partial`
- 一个都没补上：`not_found`
- 输入缺少 `gap_items` 或 gap 类型未知：`needs_clarification`
- 搜索服务异常：`error`

**去重规则：**

- 同一 URL 不重复抓取。
- 同一学校 + 专业 + 来源不重复进入 `filled_items`。
- 不同来源能相互补强，但不要重复输出相同事实。

**验收标准：**

- `max_rounds` 生效。
- `max_fetches_per_round` 生效。
- 返回 `rounds` 调试轨迹。
- 返回 `unfilled_gaps`，不静默吞掉未解决的问题。

---

## Task 8：调整 Agent fallback 优先级

**目标：** 让 Agent 在本地数据库缺失时优先调用高级补全工具，而不是直接调用底层搜索工具。

**修改文件：**

- `scripts/deepseek_retrieval_agent.py`
- `tests/test_deepseek_retrieval_agent.py`

**新优先级：**

```text
本地检索工具
  -> _detect_tool_result_gaps
  -> web_gap_fill
  -> 必要时 web_evidence_fetch
  -> 最终回答
```

**最终回答约束：**

- 可以引用 `filled_items`。
- 可以引用 `accepted_evidence`。
- 可以说明 `unfilled_gaps`。
- 不能把 `rejected_search_results` 或 `rejected_evidence` 写成事实。
- 如果只有第三方线索，必须说明“未能通过可信来源确认”。

**验收标准：**

- 对本地 `major_school_list not_found`，Agent 会优先调用 `web_gap_fill`。
- `web_gap_fill` 返回 `not_found` 时，Agent 不编造学校列表。
- `web_gap_fill` 返回 `partial` 时，Agent 明确区分已确认和未确认部分。

---

## Task 9：文档和真实烟测

**目标：** 给每个新增工具补齐中文 README，并用真实 API 做最小闭环验证。

**修改文件：**

- `tests/function_calls/web_gap_fill/README.md`
- 可能修改 `tests/function_calls/README_TEMPLATE.md`

**README 必须包含：**

- 工具原理。
- 输入参数。
- 输出字段。
- 测试范围。
- 测试结果。
- 已知限制。
- 后续改进建议。

**建议真实烟测问题：**

```text
人工智能专业，上海有哪些本科院校开设？
杭州电子科技大学本科招生章程是什么？
上海交通大学是否开设人工智能本科专业？
华东师范大学人工智能专业是否有本科招生？
```

**建议命令：**

```powershell
python -m pytest tests/test_gap_detection_registry.py -q
python -m pytest tests/test_web_gap_fill.py -q
python -m pytest tests/test_retrieval_tools.py -q
python -m pytest tests/test_retrieval_function_registry.py -q
python -m pytest tests/test_deepseek_retrieval_agent.py -q
```

如需真实网页测试，需要先确认：

```powershell
docker ps
$env:SEARXNG_BASE_URL="http://127.0.0.1:8081"
```

---

## 六、第一版边界

第一版只建议覆盖高频且证据相对可验证的缺口：

- `major_school_relation`：某专业有哪些学校开设。
- `school_major_catalog`：某学校开设哪些专业。
- `admission_history`：某专业或学校的录取历史。
- `official_admission_rule`：官方招生规则、招生章程。

暂不自动补全：

- 真实转专业成功率。
- 真实分流比例。
- 非公开就业明细。
- 需要登录、验证码或复杂 JS 渲染的数据。
- 无法稳定追溯到官方来源的论坛、营销号、问答平台内容。

这些数据可以进入 `unfilled_gaps`，由 Agent 明确提示用户“当前无法通过可信公开来源确认”。

---

## 七、风险和防护

### 1. 第三方结果污染

风险：搜索引擎结果页或第三方网站给出学校名单，Agent 直接复述。

防护：

- 默认 `source_policy=official_only`。
- 第三方结果只能进入 `rejected_evidence` 或候选列表。
- 最终答案不读取 rejected 作为事实。

### 2. 本地地区数据缺失导致错误结论

风险：本地库缺地区字段，导致“上海没有院校开设人工智能”这种错误结论。

防护：

- 地区字段缺失时，gap 类型应标记为 `scope_or_location_gap` 或在 `unfilled_gaps` 中说明。
- 不能把本地过滤后的空结果直接解释为客观不存在。

### 3. 网页内容不完整

风险：官网页面是 PDF、图片、附件或 JS 渲染，普通 HTML 抓取不到。

防护：

- `web_evidence_fetch` 已支持 PDF 时继续复用。
- 对图片、Excel、JS 页面第一版可以返回 `content_too_short` 或 `unsupported_content_type`。
- 后续再加 OCR、Excel 解析、浏览器渲染。

### 4. 多轮搜索失控

风险：Agent 为了补一个缺口不断搜索。

防护：

- `max_rounds` 默认 3。
- `max_fetches_per_round` 默认 5。
- URL 去重。
- 每个 gap 有状态迁移，无法补上就进入 `unfilled_gaps`。

---

## 八、验收标准

最终实现完成后，需要满足：

- `data_gap_detection` 能返回结构化 `gap_items`。
- `unknown_question_type` 返回 `needs_clarification` 和支持的问题类型列表。
- 空核心列表不会返回 `ok`。
- `major_school_list` 的空结果能被识别为 `major_school_relation` 缺口。
- `web_gap_fill` 能进行有限轮次搜索、抓取、证据评估。
- 第三方结果不会进入 `accepted_evidence`。
- Agent 优先使用 `web_gap_fill` 补缺口。
- Agent 最终回答能区分：
  - 本地库命中。
  - 官方网页补充确认。
  - 未能通过可信来源确认。
- 新增和修改的测试全部通过。
- `tests/function_calls/web_gap_fill/README.md` 用中文说明工具原理、测试范围、测试结果和改进方向。

---

## 九、建议实施顺序

推荐按以下顺序执行：

1. 先实现核心字段注册表和 `_infer_available_fields`。
2. 再升级 `data_gap_detection`。
3. 实现 `_detect_tool_result_gaps`。
4. 注册 `web_gap_fill`，先做空壳和 schema 测试。
5. 实现 `major_school_relation` 的 query planner。
6. 实现证据评估器。
7. 串起 `web_gap_fill` 主循环。
8. 修改 Agent fallback。
9. 补 README 和真实 API 烟测记录。

不建议一开始就覆盖全部 27 个工具。应该先把一条高频链路做严谨：

```text
用户问：人工智能专业，上海有哪些本科院校开设？
本地工具：major_school_list
缺口检测：major_school_relation
网页补全：web_gap_fill
最终回答：只输出官方证据确认过的学校，并说明未确认项
```

这条链路跑通后，再把同样模式扩展到其它志愿工具。
