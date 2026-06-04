# Major Intel 当前状态快照

更新时间：2026-06-04

## 已完成的主干能力

### 1. 本地检索与 function call 层

当前已落地 30 个正式可调用检索入口：

```text
school_lookup
major_lookup
school_profile
major_profile
school_major_list
major_school_list
school_major_profile
score_to_rank
rank_to_school_match
rank_to_major_match
specialty_group_lookup
subject_requirement_lookup
school_department_major_list
plan_history
employment_summary
source_trace_lookup
transfer_policy_lookup
fee_and_campus_lookup
specialty_group_risk
comparison_query
major_streaming_policy_lookup
civil_service_mapping
policy_rule_lookup
admission_history
major_market_reference
civil_service_role_search
data_gap_detection
web_evidence_search
web_evidence_fetch
web_gap_fill
```

配套能力：

- `src/major_intel/function_calls/retrieval_tools.py`：标准工具层。
- `src/major_intel/function_calls/registry.py`：function schema 注册与 dispatcher。
- `src/major_intel/evaluation/run_retrieval_smoke_cases.py`：本地 smoke case runner。
- `src/major_intel/storage/local_retrieval_mvp.py`：面向本地 MySQL 的 CLI MVP。
- `src/major_intel/storage/setup_entity_aliases.py`：创建和维护 `entity_aliases`、`entity_alias_candidates`。
- `src/major_intel/agents/natural_language_entrypoint.py`：第一版自然语言总入口，能把高频中文问题解析为 intent、slots 和底层工具调用计划。
- `src/major_intel/agents/deepseek_retrieval_agent.py`：DeepSeek function-call agent，能把 function schema 暴露给模型并执行本地 dispatcher。
- `src/major_intel/agents/retrieval_agent_entrypoint.py`：统一入口，自动协调离线规则入口和 DeepSeek agent。
- `src/major_intel/storage/agent_query_storage.py`：统一入口的 MySQL 查询日志、缓存和工具轨迹存储层。
- `scripts/*.py`：保留兼容 CLI wrapper，原手动测试命令仍可继续使用。

已经完成的关键修复和增强：

- 修复 MySQL CLI TSV 解析：长文本字段中的换行不再被拆成假结果行。
- 修复录取历史表与学校表的关联键：`edu_school_admission_stats.school_id` 应按 `edu_university.code + name` 关联，不能按内部 `edu_university.school_id` 关联。
- `school_lookup` 已接入数据库确认别名表 `entity_aliases`，例如“杭电”可以命中“杭州电子科技大学”；学校短简称不再只依赖学校基础表里的 `short` 字段。
- `major_lookup` 的常用简称已经从代码内置迁入数据库确认别名表 `entity_aliases`，例如“计科”优先命中“计算机科学与技术”；短简称不再直接走危险模糊匹配。
- `rank_to_school_match` 已能按分数或位次返回学校层面的冲/稳/保参考。
- `rank_to_major_match` 已能按分数或位次 + 专业偏好返回学校-专业行层面的冲/稳/保参考。
- `comparison_query` 已能对学校、专业、学校-专业方案做第一版结构化并列对比，不直接替用户下最终选择。
- `major_streaming_policy_lookup`、`policy_rule_lookup`、`civil_service_mapping` 已有保守接口：能返回上下文、样本和 data_gaps，但不做高风险正式结论。
- 第一版 SQL-first RAG 已具备：30 个本地 function call 作为 retriever，MySQL 查询结果和证据补全结果作为 context，agent 只负责路由、编排和表达。
- 自然语言总入口已完成离线规则第一版：支持工具自动选择、缺槽追问、多工具编排、结果口径聚合和 `--no-execute` 纯计划模式。
- DeepSeek LLM function-call agent 已有实现，并已通过统一入口接入：高频明确问题优先走规则入口，复杂/未知问题交给 DeepSeek 自动选择工具。
- 统一入口已接入第一版 MySQL 运营存储：`query_logs`、`retrieval_cache`、`agent_tool_traces`、`data_gap_queue`，通过 `--enable-storage` 开启。
- 缺口队列本地前置层已补齐：`source_documents` 与 `data_gap_evidence_tasks` 可建表，`pending` 缺口可生成 `ready` 证据检索任务。
- 本轮新增 9 个正式工具：专业组查询、选科要求、院系专业、招生计划、学校级就业摘要、来源追踪、转专业政策、学费线索/校区缺口、专业组风险初筛。
- 招生计划/学费等混合来源表已经改成“专业代码精确 + 专业名精确 + 专业名包含”的匹配，能命中带校区、中外合作、学费说明等后缀的专业名。
- 核心 SQL-first 工具的真实库 smoke 矩阵已补齐：`data/retrieval_smoke_cases.json` 当前展开后为 305 个用例；新增联网证据补全工具另有 `tests/function_calls/web_*` 覆盖。
- `major_school_list` 已完成专项边界修复与真实库审计：按 `edu_university.code OR edu_university.school_id` 双键召回学校，支持常见省份后缀归一化，传播专业解析 warning，并对 `limit<=0` 返回结构化 `needs_clarification`。

### 1.1 工具完成状态

正式已完成：

```text
school_lookup
major_lookup
school_profile
major_profile
school_major_list
major_school_list
school_major_profile
score_to_rank
rank_to_school_match
rank_to_major_match
specialty_group_lookup
subject_requirement_lookup
school_department_major_list
plan_history
employment_summary
source_trace_lookup
transfer_policy_lookup
fee_and_campus_lookup
specialty_group_risk
comparison_query
major_streaming_policy_lookup
civil_service_mapping
policy_rule_lookup
admission_history
data_gap_detection
web_evidence_search
web_evidence_fetch
web_gap_fill
```

提前完成：

```text
major_market_reference
civil_service_role_search
```

保守接口已完成，但还不是正式结论型能力：

```text
civil_service_mapping
major_streaming_policy_lookup
policy_rule_lookup
```

当前验证：

- 单元测试：`python -m unittest discover -s tests` 已通过 734 个测试。
- smoke 抽样：`python scripts/run_retrieval_smoke_cases.py --sample-per-tool 1 --report reports/retrieval_smoke_restructure_sample.json` 已通过 30/30，结构失败 0 个，质量提示 0 个。
- 烟测矩阵：`data/retrieval_smoke_cases.json` 已覆盖核心 SQL-first 工具和新增 web 证据工具的抽样入口，当前抽样覆盖 30 个注册工具。
- 人工逐个测试命令已整理到 `docs/status/retrieval-tool-manual-test-commands.md`，包含每个工具的推荐命令、可选参数和检查重点。
- 真实库抽样：`python scripts/run_retrieval_smoke_cases.py --sample-per-tool 1 --report reports/retrieval_smoke_sample_27_tools.json` 曾跑通核心 SQL-first 工具抽样，结构失败 0 个。
- 真实库全量：`python scripts/run_retrieval_smoke_cases.py --report reports/retrieval_smoke_27_tools_full.json --timeout 60` 跑通 305/305，结构失败 0 个，质量提示 0 个。
- 质量提示已完成第一轮清零：`school_major_profile` 的 `partial` 口径已在 smoke 中校准；`score_to_rank` 支持文理科与物理/历史的保守别名回退；考公岗位检索支持 K/T/TK 专业代码后缀；`rank_to_school_match` 的“双一流”筛选已使用结构化字段。
- `major_school_list` 专项：`python scripts/evaluate_major_school_list_boundaries.py --jsonl-report reports/major_school_list_boundary_eval_20260602.jsonl --markdown-report reports/major_school_list_boundary_eval_20260602.md` 跑通 16/16；相关单测 `python -m pytest tests\function_calls\major_school_list tests\test_retrieval_tools.py -q` 跑通 78/78。

### 1.2 原始需求完成度

这里按最初聊天记录里的业务需求来对齐，而不是按工具名对齐。

| 原始需求 | 当前状态 | 已经能做什么 | 还缺什么 |
|---|---|---|---|
| 每个院校专业的浅层解读：行业薪资、对口企业、学科评估、结合官网专业介绍 | 部分完成 | `school_major_profile` 能合并学校、专业、学科评估、专业通用薪资/就业方向和缺口提示；`major_market_reference` 能给第三方市场样本 | 校专业级对口企业 Top 10、学校官网专业介绍证据链、官方校专业就业质量仍缺 |
| 某校某专业：就业、升学、薪资、对口企业、双一流、其他亮点 | 部分完成 | 学校基础、双一流、学科评估、专业基础、学校级就业/升学摘要可查 | 校专业级就业地域、薪资分布、升学去向、对口企业仍缺；不能把学校级就业当作专业级结论 |
| 某专业组：分流比例、分流到冷门专业比例、转专业政策 | 部分完成 | `specialty_group_lookup` 能查专业组和组内专业；`specialty_group_risk` 能按组内构成做风险初筛；`transfer_policy_lookup` 能查第三方转专业线索 | 真实分流比例、冷门专业人工标签、官方转专业政策复核仍缺 |
| 覆盖多数高校，尤其 211 以下中等学校 | 部分完成 | 工具层已经完全基于本地 MySQL，可覆盖库里已有学校和专业；`school_lookup`、`major_lookup`、列表类工具可通用查询 | 覆盖率取决于本地表实际数据完整度；还没有做覆盖率报告和缺口优先级排序 |
| 就业情况：工作地域分布、工资分布、Top 10 对口公司、考公对口岗位 | 部分完成 | `employment_summary` 有学校级就业/升学摘要；`major_market_reference` 有专业通用市场样本；`civil_service_role_search` 有考公岗位文本命中样本 | 校专业级地域/工资/公司 Top 10 仍缺；`civil_service_mapping` 尚未做到正式可报判定 |
| 第一版 SQL-first RAG：学生提问时由 agent 选择 function call，查本地 SQL 并基于结构化上下文回答 | 第一版已完成 | 已有 30 个 function schema、工具层、`source_trace_lookup`、`data_gap_detection`、自然语言规则入口、DeepSeek tool-call agent、统一入口、查询缓存/日志表、`data_gap_queue` 入队和 `data_gap_evidence_tasks` 本地任务生成；核心 SQL-first 工具真实库 smoke 矩阵已补齐并全量跑通，当前质量提示为 0 | 仍需继续人工抽测真实问题，发现更细的别名、口径和数据覆盖问题 |
| V2 联网证据补全 RAG：本地不命中后搜索官方来源、缓存、入库，搜不到抛给人工 | 未完成 | 已有 `data_gap_queue` 和 `data_gap_evidence_tasks` 作为后台任务入口 | 联网搜索 agent、抽取校验、人工复核和写回闭环还没正式落地 |
| 学生可能问题的检索总入口和 function call 自动选择 | 第一版已完成 | 已新增规则入口、DeepSeek agent、统一入口和查询存储层；实现已迁入 `src/major_intel`，`scripts/*.py` 保留兼容 CLI；能做规则优先路由、复杂问题 LLM tool-call、缺槽追问、工具计划生成、多工具编排、结构化对比、结果口径聚合、缓存、查询日志和缺口入队；30 个底层 function call 工具已注册 | 还没有接入人工复核处理流 |

### 1.3 当前最重要的缺口

1. 校专业级就业事实：地域分布、工资分布、Top 10 企业、升学去向。
2. 官方证据链：学校官网专业介绍、官方转专业政策、招生章程/批次规则。
3. 大类分流事实：真实分流比例、冷门专业比例、专业组调剂后果。
4. 考公正式映射：从岗位文本命中升级到可报条件判定。
5. 第一版 SQL-first RAG 验收：自然语言入口、DeepSeek tool-call agent、统一入口、缓存/日志、缺口队列和 27 工具真实库 smoke 矩阵已完成第一版；下一步是基于人工抽测继续发现真实问题。

### 2. rysxai 专业市场数据

已完成：

- 专业列表 seed：`data/seeds/rysxai_professions.full.csv`。
- 市场样本 crawler：`scripts/rysxai_market_crawler.py`。
- Markdown 报告渲染：`scripts/rysxai_market_report.py`。
- 市场概览与 dashboard 构建：`scripts/build_rysxai_overview.py`、`scripts/build_rysxai_dashboards.py`。
- 单元测试：`tests/test_rysxai_market_crawler.py`、`tests/test_rysxai_market_report.py`。

边界：

- 该数据是第三方专业市场观察，只能用于专业通用就业方向、招聘样本、城市/行业/薪资观察。
- 不能直接回答某校某专业真实就业去向、真实薪资或官方就业质量。

### 3. rysxai 公考岗位数据

已完成：

- 2026 公考岗位详情 crawler：`scripts/rysxai_civil_service_crawler.py`。
- JSONL 到 CSV 展平能力。
- 本地检索工具 `civil_service_role_search` 已能读取已接入样本。
- 单元测试：`tests/test_rysxai_civil_service_crawler.py`。

边界：

- 当前只能说明岗位文本命中过某些专业样本。
- 不能声明某专业一定可报某岗位；最终可报范围仍要以当年官方岗位表和招录公告为准。

### 4. rysxai 转专业政策数据

本轮新增：

- 学校列表 seed：`data/seeds/rysxai_universities.csv`。
- 转专业政策 crawler：`scripts/rysxai_transfer_policy_crawler.py`。
- 转专业政策静态 dashboard：`scripts/build_rysxai_transfer_policy_dashboard.py`。
- 单元测试：`tests/test_rysxai_transfer_policy_crawler.py`、`tests/test_rysxai_transfer_policy_dashboard.py`。

边界：

- rysxai 转专业文本按 C 级第三方线索处理。
- 高风险使用前必须回到学校官网、教务处通知或招生章程复核。
- 接口空白不等于学校无转专业政策，只能说明抓取时第三方接口未暴露相关字段。

## 当前未纳入版本历史的本地产物

以下内容保留在本地，但默认忽略，不提交：

- `data/raw/`、`data/processed/`、`data/logs/`
- `reports/rysxai/`
- `reports/retrieval_smoke*.json`
- `gaokao_test_*.sql`
- `gaokao-zhiyuan-projects/`
- `docs/superpowers/`

当前仍保留的未跟踪报告文件，继续按生成物处理，默认不提交：

- `reports/deepseek_agent_manual_test_20260520_205645.md`
- `reports/deepseek_agent_plain_style_check.md`
- `reports/deepseek_tool_selection_matrix.json`

## 下一步建议

1. 先按人工测试手册逐个抽测 27 个工具，收集不符合预期的真实问题样例。
2. 为 `major_streaming_policy_lookup`、`policy_rule_lookup`、`civil_service_mapping` 明确后续事实表和写回字段。
3. 后续再让联网 agent 消费 `data_gap_evidence_tasks.ready`，完成官方来源发现、网页/PDF 抓取和人工复核。
4. 继续增强复杂志愿方案解析，包括偏好权重、城市偏好和家庭约束。
