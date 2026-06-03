# 远端新增表说明

日期：2026-06-02

本文档记录本次从本地库补充到远端库的表，以及这些表在 retrieval function call 和 agent 调用链中的作用。

本次补表只针对远端缺失表执行新增；未对远端已有表做结构修改、清空、覆盖或删除。

## 总览

本次新增到远端的表分为两类：

1. Function call 会直接查询的事实/参考数据表：支撑专业就业、公务员岗位映射、转专业政策和实体别名解析。
2. Agent 运行时会使用的运营/任务表：支撑统一入口日志、缓存、工具调用轨迹、数据缺口队列和后续证据补全闭环。

## Function Call 事实/参考表

这些表会被 `scripts/retrieval_tools.py` 中的 retrieval function call 直接或间接读取。缺少这些表时，相关工具即使逻辑存在，也会因为远端库缺表而无法完整运行。

| 表名 | 远端导入后行数 | 主要使用方 |
|---|---:|---|
| `entity_aliases` | 173 | `school_lookup`、`major_lookup` 以及所有依赖实体解析的工具 |
| `rysxai_civil_service_roles` | 20714 | `civil_service_role_search`、`civil_service_mapping` |
| `civil_service_major_role_candidates` | 22661 | `civil_service_role_search`、`civil_service_mapping` |
| `rysxai_major_market_snapshots` | 1616 | `major_market_reference` |
| `rysxai_major_job_samples` | 6813 | `major_market_reference` |
| `rysxai_transfer_policies` | 2948 | `transfer_policy_lookup` |

### `entity_aliases`

`entity_aliases` 是已确认实体别名表，用于把用户输入中的简称、别称、校区简称或专业简称归一到标准实体。

典型用途：

- 学校简称解析，例如“杭电”归一到“杭州电子科技大学”。
- 专业简称解析，例如“计科”归一到“计算机科学与技术”。
- 校区简称解析，例如“哈工深”“北邮宏福”“人大苏州”等归一到对应校区实体。
- 降低危险模糊匹配风险，避免短词直接在学校表、专业表里乱匹配。

调用链：

- `school_lookup` 会先查 `entity_aliases` 中 `entity_type = 'school'` 的记录。
- `major_lookup` 会先查 `entity_aliases` 中 `entity_type = 'major'` 的记录。
- 其他工具只要先调用学校或专业解析，就会间接依赖这个表。

使用注意：

- 这是“已确认别名”表，不是候选表。进入该表的记录应当是人工确认或规则高度确定的别名。
- `source`、`confidence`、`status`、`deleted` 等字段用于区分别名来源、可信度和有效状态。
- 如果远端缺少此表，agent 面对简称问题会显著退化，可能返回 `not_found` 或误命中。

### `rysxai_civil_service_roles`

`rysxai_civil_service_roles` 保存公务员岗位原始/标准化岗位信息，是公务员适配相关工具的岗位事实表。

典型用途：

- 查询某个专业可报考、可能匹配或历史上关联过的公务员岗位。
- 给 `civil_service_role_search` 返回岗位名称、招录单位、地区、年份、岗位要求等信息。
- 给 `civil_service_mapping` 提供从专业到岗位方向的证据。

调用链：

- `civil_service_role_search` 通过 `civil_service_major_role_candidates` 找到候选岗位后，JOIN 到 `rysxai_civil_service_roles` 补全岗位详情。
- `civil_service_mapping` 会复用同一条候选岗位证据链，生成专业到公务员方向的映射结果。

使用注意：

- 该表是岗位事实明细，不能单独说明某个专业一定可报某个岗位；需要结合候选匹配表的匹配依据和置信度。
- 公务员岗位具有年份和地区差异，回答时应保留年份、地区、岗位条件等上下文。
- 如果远端缺少该表，公务员相关 function call 只能找到候选关系或完全失败，无法展示岗位详情。

### `civil_service_major_role_candidates`

`civil_service_major_role_candidates` 保存“专业”和“公务员岗位”之间的候选匹配关系，是专业到岗位的桥接表。

典型用途：

- 把专业代码、专业名称映射到可能匹配的公务员岗位。
- 保存匹配来源、匹配方式、置信度或候选解释。
- 支撑“学这个专业能考哪些公务员岗位”“某专业公务员方向怎么样”等问题。

调用链：

- `civil_service_role_search` 先解析专业，再查询该表找候选岗位。
- 查到候选岗位后，再 JOIN `rysxai_civil_service_roles` 获取岗位详情。

使用注意：

- 这是候选匹配表，不等同于官方报考资格结论。
- 最终是否可报考仍应以当年公务员职位表、专业目录和招考公告为准。
- 回答中应避免把候选匹配表解释为“保证能报”。

### `rysxai_major_market_snapshots`

`rysxai_major_market_snapshots` 保存专业就业市场概览快照，供专业市场参考工具使用。

典型用途：

- 给某个专业返回就业市场概览，例如岗位需求、城市分布、薪资区间、样本摘要等。
- 支撑 `major_market_reference` 中的 summary/snapshot 部分。
- 辅助回答“这个专业就业怎么样”“市场需求如何”“岗位方向有哪些”等问题。

调用链：

- `major_market_reference` 先调用 `major_lookup` 解析专业。
- 然后查询 `rysxai_major_market_snapshots` 获取专业级市场快照。
- 同时查询 `rysxai_major_job_samples` 获取具体岗位样本。

使用注意：

- 该表是市场参考数据，不是教育部或学校官方就业质量报告。
- 回答时应明确这是“市场样本/参考”，不能替代学校官方就业质量报告。
- 市场数据存在时间敏感性，建议结合抓取时间、样本规模和来源说明。

### `rysxai_major_job_samples`

`rysxai_major_job_samples` 保存专业相关岗位样本，是就业市场参考的明细样本表。

典型用途：

- 展示某个专业对应的招聘岗位样本。
- 支撑岗位名称、城市、企业类型、学历要求、经验要求、薪资区间、技能关键词等明细。
- 与 `rysxai_major_market_snapshots` 搭配使用：快照负责概览，样本负责举例。

调用链：

- `major_market_reference` 查询专业快照后，会按专业继续查询岗位样本。
- 返回时通常会限制样本数量，避免输出过长。

使用注意：

- 岗位样本不是完整市场全集，只能作为参考。
- 薪资、岗位要求和城市分布会随时间变化。
- 回答时应避免从少量样本过度推出确定性结论。

### `rysxai_transfer_policies`

`rysxai_transfer_policies` 保存学校转专业政策线索和政策文本，是 `transfer_policy_lookup` 的核心数据表。

典型用途：

- 查询某所学校是否有转专业政策文本或政策线索。
- 返回转专业申请条件、限制、时间窗口、学院/专业限制、政策来源等信息。
- 支撑“这个学校能不能转专业”“转专业难不难”“有什么限制”等问题。

调用链：

- `transfer_policy_lookup` 先调用 `school_lookup` 解析学校。
- 然后按学校名称、学校编码或相关字段查询 `rysxai_transfer_policies`。

使用注意：

- 该表中的政策数据可能来自第三方抓取或整理，需要区分“官方原文”和“第三方线索”。
- 如果不是学校官网、招生章程或教务处官方文件，应在回答中提示需要官方复核。
- 转专业政策通常每年变化，回答时应保留年份、抓取时间或来源时间。

## Agent 运营/任务表

这些表不属于高考事实数据本身。它们主要服务于 agent 作为统一入口调用 function call 时的运行记录、缓存和后续补证据流程。

如果只执行 `python scripts/retrieval_tools.py <tool>`，这些表通常不会被触发。

如果执行 `scripts/retrieval_agent_entrypoint.py` 并开启 `--enable-storage`，这些表会被 `scripts/agent_query_storage.py` 使用。

| 表名 | 远端导入后行数 | 主要使用方 |
|---|---:|---|
| `query_logs` | 6 | 统一 agent 入口查询日志 |
| `retrieval_cache` | 1 | 统一 agent 入口结果缓存 |
| `agent_tool_traces` | 5 | 统一 agent 入口工具调用轨迹 |
| `data_gap_queue` | 0 | 数据缺口队列 |
| `data_gap_evidence_tasks` | 0 | 后续联网/人工补证据任务 |
| `source_documents` | 0 | 后续证据来源沉淀 |
| `entity_alias_candidates` | 0 | 别名候选发现与人工确认 |

### `query_logs`

`query_logs` 是 agent 查询日志表，用于记录一次用户问题从进入系统到产生答案的主要上下文。

典型记录内容：

- 用户原始问题。
- 会话 ID。
- 路由模式，例如 rules、deepseek、auto。
- 识别出的 intent 和 slots。
- function call 工具计划。
- 工具调用结果汇总。
- 最终 answer markdown。
- warnings、data_gaps、scope_notes 等诊断字段。

调用链：

- `scripts/retrieval_agent_entrypoint.py` 在 `--enable-storage` 时创建 `MysqlAgentQueryStorage`。
- 每次 agent 运行后调用 `write_query_log()` 写入 `query_logs`。

作用价值：

- 复盘某个回答是怎么来的。
- 统计哪些问题最常被问。
- 统计哪些 intent、工具或数据缺口最常出现。
- 支撑后续调试、评测和产品分析。

### `retrieval_cache`

`retrieval_cache` 是统一入口的查询结果缓存表，用于减少重复问题的重复检索或重复模型调用。

典型记录内容：

- cache key。
- cache key 的来源 JSON，例如问题、mode、route、intent、slots、tool_plan。
- 缓存的完整结果 JSON。
- 缓存文本副本。
- 过期时间。
- 命中次数和最近命中时间。

调用链：

- agent 启用存储后，会先通过规则入口生成稳定的 cache identity。
- 若 `retrieval_cache` 命中且未过期，则直接返回缓存结果。
- 若未命中，执行 function call 或 DeepSeek tool-call 后，再写入缓存。

作用价值：

- 降低重复查询成本。
- 减少对远端数据库和 LLM 的重复压力。
- 保留可复查的历史结构化结果。

使用注意：

- 如果底层事实数据更新，旧缓存可能暂时保留旧答案。
- 需要结合 `cache_ttl_seconds` 或后续缓存失效策略使用。

### `agent_tool_traces`

`agent_tool_traces` 是工具调用轨迹明细表，用于把一次 agent 回答中的多个 function call 拆成可查询的行。

典型记录内容：

- 对应的 `query_log_id`。
- 工具调用顺序。
- tool name。
- arguments JSON。
- result status。
- result JSON。

调用链：

- agent 入口执行完工具调用后，`write_tool_traces()` 会把 `tool_trace` 展开写入该表。

作用价值：

- 排查某次回答到底调用了哪些工具。
- 比较不同工具的命中率、失败率和常见参数。
- 定位某个 function call 是否经常返回 `not_found`、`partial` 或 `needs_clarification`。

### `data_gap_queue`

`data_gap_queue` 是数据缺口队列表，用于记录本地库无法可靠回答的问题。

典型触发场景：

- 工具返回 `not_found`。
- 工具返回 `data_gap`。
- 工具结果中包含 `data_gaps`。
- 政策、章程、就业、录取历史等关键字段缺失。

典型记录内容：

- 缺口唯一键 `gap_key`，用于去重。
- question type。
- 学校、专业、省份、科类、年份、批次等槽位。
- 缺失字段列表。
- 已有字段。
- 原始用户问题。
- 优先级。
- 状态，例如 pending、failed、resolved、rejected。
- 建议来源约束。
- 预期写回目标。

调用链：

- agent 入口运行结束后，`build_data_gap_items()` 从结果中抽取缺口。
- `write_data_gap_items()` 将缺口写入 `data_gap_queue`。

作用价值：

- 把“答不上来”的问题沉淀成可处理任务，而不是静默丢失。
- 统计真实用户最需要补的数据。
- 给后续联网检索、人工复核和数据补全提供任务入口。

### `data_gap_evidence_tasks`

`data_gap_evidence_tasks` 是证据检索任务表，用于把 `data_gap_queue` 中的缺口转换成可执行的搜索任务。

典型记录内容：

- 对应的 gap id 和 gap key。
- question type。
- search query。
- preferred sources。
- expected outputs。
- task status。
- attempt count。
- result document id。

调用链：

- `MysqlAgentQueryStorage.prepare_evidence_tasks()` 会读取 pending/failed 缺口。
- 根据缺口生成 search query。
- 将生成的任务写入 `data_gap_evidence_tasks`。

作用价值：

- 让后续联网 agent 不需要重新理解用户问题，直接按任务搜索。
- 将“缺什么”转换成“应该搜什么、优先搜哪些来源、最后写回哪里”。
- 支撑未来官方来源发现、PDF/网页抓取、人工审核和事实表写回。

### `source_documents`

`source_documents` 是证据来源表，用于保存后续联网或人工补证据得到的网页、PDF、招生章程、就业质量报告等来源材料。

典型记录内容：

- source key。
- source type。
- source URL。
- 标题。
- 发布方。
- 发布日期。
- 抓取时间。
- 内容 hash。
- 原文文本。
- 元数据 JSON。
- 可信度等级。

调用链：

- 当前 27 个 function call 不直接读取该表。
- 后续联网 agent 或人工复核流程会把检索到的官方来源写入该表。
- `data_gap_evidence_tasks.result_document_id` 可指向该表中的证据文档。

作用价值：

- 保存事实结论的来源证据。
- 支持后续从证据文档抽取字段并写回事实表。
- 支持回答时追溯“这个结论来自哪个官方文件”。

使用注意：

- 该表保存的是来源材料，不等同于最终结构化事实。
- 需要后续抽取、校验和人工审核，才能把其中的信息写入事实表或作为高可信结论使用。

### `entity_alias_candidates`

`entity_alias_candidates` 是候选别名表，用于保存自动发现但尚未确认的实体别名。

典型用途：

- 从用户问题、测试命令、抓取文本或模型建议中发现可能的学校简称、专业简称、校区简称。
- 将候选别名暂存，等待人工审核。
- 审核通过后，再写入正式别名表 `entity_aliases`。

调用链：

- 当前 27 个 function call 不读取该表。
- `scripts/setup_entity_aliases.py` 会创建和维护该表结构。
- 后续别名发现/审核流程可以使用该表。

作用价值：

- 避免未经确认的别名直接污染 `entity_aliases`。
- 支撑别名体系持续迭代。
- 对真实用户高频简称、错别字和校区简称进行沉淀。

使用注意：

- 该表中的记录不能直接用于正式实体解析，除非经过审核并迁入 `entity_aliases`。
- 它是“候选池”，不是“可信别名表”。

## 使用边界

### 只跑单个 function call

例如：

```bash
python scripts/retrieval_tools.py major_market_reference --major "计算机科学与技术"
```

这种方式主要依赖事实/参考表，不会写入 agent 运营表。

### 通过 agent 调用 function call

例如：

```bash
python scripts/retrieval_agent_entrypoint.py "广东物理 580 想学计算机" --mode auto --enable-storage --json
```

这种方式会同时依赖两类表：

- 事实/参考表：用于 function call 查询真实数据。
- agent 运营/任务表：用于缓存、日志、工具轨迹和缺口队列。

## 后续维护建议

1. `entity_aliases` 应只接收已确认别名；候选别名先进入 `entity_alias_candidates`。
2. 公务员岗位匹配表应保持“候选证据”语义，回答时不要说成确定报考资格。
3. 市场就业表应标注为市场样本参考，不能替代官方就业质量报告。
4. 转专业政策表要区分官方原文和第三方线索，关键结论建议进入官方复核流程。
5. Agent 运营表可以持续写入远端，用于后续分析真实问题、缺口频率和工具质量。
6. `data_gap_queue` 和 `data_gap_evidence_tasks` 应作为后续联网补证据闭环的任务源。
7. `source_documents` 后续应优先保存学校官网、招生章程、考试院文件、就业质量报告等可复核来源。
