# Major Intel

Major Intel 是一个面向高考志愿、院校专业选择和数据可信问答的本地检索与 agent 系统。

这个项目的目标不是做一个“凭模型记忆回答”的聊天机器人，而是把学校、专业、录取位次、招生计划、专业组、就业市场、考公岗位、转专业政策等信息整理成一套可追溯、可测试、可复核的 function call 工具。agent 可以自然语言接入，但事实必须来自本地 MySQL、已接入的数据表或明确的证据链；本地没有数据时，要返回缺口，而不是编造结论。

## 当前快照

更新时间：2026-05-21

当前已经完成：

- 本地 MySQL 检索工具层。
- 30 个正式 function call schema 与 dispatcher，其中包含 3 个联网证据补全入口。
- 核心本地检索工具的真实库 smoke 矩阵，当前展开后为 305 个用例。
- 第一版 SQL-first RAG：本地 function call 负责检索，MySQL 查询结果作为回答上下文。
- DeepSeek function-call agent。
- 离线规则自然语言入口。
- 统一 agent 入口，能在规则入口和 DeepSeek agent 之间自动协调。
- 查询日志、缓存、工具轨迹和数据缺口队列四类 MySQL 运营表。
- rysxai 专业市场、考公岗位、转专业政策等第三方数据接入链路。

当前仍未完成：

- 大类分流、招生政策、考公映射已有保守 function call 接口，但官方证据和正式判定仍未完成。
- V2 联网证据补全 RAG/人工复核闭环：`data_gap_queue` 已能记录缺口，并能生成本地证据检索任务；联网找源、抽取、校验和人工审核写回还没接通。
- 校专业级就业事实库：就业地域分布、薪资分布、Top 公司、升学去向、学校官网专业介绍证据链。

更细的阶段性状态见 [docs/status/current-state.md](docs/status/current-state.md)。

如果要人工逐个测试底层工具，命令清单见 [docs/status/retrieval-tool-manual-test-commands.md](docs/status/retrieval-tool-manual-test-commands.md)。

## 系统分层

```text
用户自然语言问题
  -> scripts/retrieval_agent_entrypoint.py
       兼容 CLI wrapper，真实实现位于 src/major_intel/agents/
  -> src/major_intel/agents/retrieval_agent_entrypoint.py
       auto 模式：先走离线规则入口，复杂/未知问题回退 DeepSeek
  -> src/major_intel/agents/natural_language_entrypoint.py
       规则识别 intent、slots、tool_plan
  -> src/major_intel/agents/deepseek_retrieval_agent.py
       DeepSeek 基于完整 function schema 自动选择工具
  -> src/major_intel/function_calls/registry.py
       function schema 注册、参数校验、dispatcher
  -> src/major_intel/function_calls/retrieval_tools.py
       MySQL 检索工具真实实现
  -> src/major_intel/storage/agent_query_storage.py
       query_logs / retrieval_cache / agent_tool_traces / data_gap_queue
```

第一版 RAG 的口径是 SQL-first：

- `retrieval_function_registry.py` 暴露的 30 个 function call 就是 retriever。
- `retrieval_tools.py` 查询本地 MySQL 后返回 `data`、`scope_notes`、`warnings`、`data_gaps` 和 `source_tables`。
- agent 只基于这些工具结果组织回答，不能绕过工具凭模型记忆补事实。
- 查不到的数据进入 `data_gap_queue` 和 `data_gap_evidence_tasks`，后续再由联网/人工流程补证据。

核心原则：

1. 模型只能选择工具和组织表达，不能绕过工具编造事实。
2. 学校级、专业通用级、校专业级、招生专业组级、录取统计级数据不能混用。
3. 第三方市场样本只能作为市场观察，不能当成官方校专业就业结论。
4. 历史录取位次只能作为历史参考，不保证未来录取。
5. 数据缺失时返回 `data_gaps`，后续进入缺口队列或人工复核。

## 目录结构

```text
src/major_intel/function_calls/        function schema、dispatcher、检索工具实现
src/major_intel/agents/                规则入口、DeepSeek agent、统一 agent 入口
src/major_intel/storage/               MySQL client、缓存、轨迹、缺口队列和别名初始化
src/major_intel/evaluation/            smoke runner、边界评测和 oracle 代码
src/major_intel/datasets/dialogue/     高考志愿对话数据集清洗与构建逻辑
src/major_intel/crawlers/              rysxai 等第三方数据 crawler 实现
src/major_intel/ingestion/             爬取数据写入 MySQL 的入库实现
src/major_intel/reporting/             爬取数据报告和 dashboard 构建实现

scripts/*.py                           兼容 CLI wrapper，保留原手动测试命令
scripts/datasets/                      数据集任务的结构化 CLI wrapper
scripts/crawlers/                      crawler 任务的结构化 CLI wrapper
scripts/ingestion/                     入库任务的结构化 CLI wrapper
scripts/reports/                       报告/dashboard 任务的结构化 CLI wrapper
scripts/evaluation/                    评估任务的结构化 CLI wrapper
scripts/rysxai_*                       第三方数据采集、报告、dashboard 脚本
scripts/one_off/official_sources/      历史批次官网证据采集和补数脚本，不作为稳定 API

docs/architecture/                     仓库结构与系统架构
docs/datasets/                         数据集来源、清洗口径和使用边界
docs/research/                         起点调研与背景材料
docs/specs/                            设计文档、工具规划、数据接入方案
docs/status/current-state.md           当前状态快照

tests/agents/                          Agent 入口测试
tests/retrieval/                       function call registry 与底层检索测试
tests/evaluation/                      边界评估和 smoke runner 测试
tests/crawlers/                        通用 crawler 和证据检索测试
tests/ingestion/                       入库、清洗、数据包构建测试
tests/reporting/                       报告和 dashboard 构建测试
tests/datasets/                        对话数据集构建测试
tests/one_off/official_sources/        历史批次脚本回归测试
datasets/dialogue/                     已提交的对话数据集快照和清单
data/seeds/                            可提交的小型种子数据
data/raw/、data/processed/、tmp/        本地数据与临时产物，默认不提交
```

## 本地环境

代码默认使用本地 MySQL CLI 访问数据库。默认数据库配置来自环境变量：

```powershell
$env:GAOKAO_DB_HOST = "127.0.0.1"
$env:GAOKAO_DB_PORT = "3306"
$env:GAOKAO_DB_USER = "root"
$env:GAOKAO_DB_NAME = "gaokao_test_local"
$env:GAOKAO_DB_PASSWORD = "<你的本地密码>"
```

注意：

- 本机当前可见的库名是 `gaokao_test_local`，不是 `gaokao_test`。
- 密码只应通过环境变量或本地 `.env` 注入，不要写进代码、文档或提交历史。
- 如果你的实际库名不同，改 `GAOKAO_DB_NAME` 即可。

## 已完成的正式 Function Call

当前正式注册并可被 agent 调用的 function call 一共 30 个。兼容 CLI 入口是 [scripts/retrieval_function_registry.py](scripts/retrieval_function_registry.py)，真实注册实现是 [src/major_intel/function_calls/registry.py](src/major_intel/function_calls/registry.py)，真实检索实现是 [src/major_intel/function_calls/retrieval_tools.py](src/major_intel/function_calls/retrieval_tools.py)。

| 工具 | 作用 | 当前口径 |
|---|---|---|
| `school_lookup` | 解析学校名称、简称或代码 | 实体解析，不直接给结论 |
| `major_lookup` | 解析专业名称、简称或代码 | 已接数据库别名，避免短简称误匹配 |
| `school_profile` | 学校概况 | 学校基础、双一流、学科评估、学校级就业摘要 |
| `major_profile` | 专业概况 | 专业通用信息；保留解析 warning、画像缺口和后缀上下文，不代表某校某专业 |
| `school_major_list` | 某学校开设专业列表 | 不等于某省当年招生计划 |
| `major_school_list` | 开设某专业的学校列表 | 可做省份/层次粗筛；已覆盖 code/school_id 双键召回、省份后缀归一化和 limit 校验 |
| `school_major_profile` | 某校某专业综合画像 | 合并学校、专业、学科评估、缺口提示 |
| `score_to_rank` | 分数转位次 | 按省份、科类、年份换算 |
| `rank_to_school_match` | 按分数/位次推荐学校 | 输出冲/稳/保学校桶，历史参考 |
| `rank_to_major_match` | 按分数/位次和专业推荐学校专业 | 输出学校-专业行冲/稳/保桶，历史参考 |
| `specialty_group_lookup` | 查询专业组和组内专业 | 招生专业组，不等于入学后真实分流 |
| `subject_requirement_lookup` | 查询选科要求 | 来自专业组样本抽取 |
| `school_department_major_list` | 查询院系和院系下专业 | 院系关系，不等于招生计划 |
| `plan_history` | 查询招生计划变化 | 计划数不等于实际录取人数 |
| `employment_summary` | 学校级就业/升学摘要 | 不能代表某专业就业 |
| `source_trace_lookup` | 解释数据来源和可信度 | 可追踪工具对应表和口径 |
| `transfer_policy_lookup` | 查询转专业政策线索 | 第三方线索，需官方复核 |
| `fee_and_campus_lookup` | 查询学费、校区、住宿线索 | 校区字段不稳定时会返回缺口 |
| `specialty_group_risk` | 专业组调剂风险初筛 | 基于组内构成，非真实分流比例 |
| `comparison_query` | 学校/专业/方案结构化对比 | 只做并列证据，不直接替用户下最终选择 |
| `major_streaming_policy_lookup` | 大类/专业分流政策缺口查询 | 只返回上下文和缺口，不编真实分流比例 |
| `civil_service_mapping` | 考公映射线索 | 包装岗位样本，明确不是正式可报判定 |
| `policy_rule_lookup` | 招生章程/政策规则缺口查询 | 无官方来源时只返回待补字段 |
| `admission_history` | 历年录取分和位次 | 历史参考，不保证未来 |
| `major_market_reference` | 专业通用市场样本 | 第三方招聘/薪资样本，不是校专业就业 |
| `civil_service_role_search` | 考公岗位文本命中样本 | 命中不等于正式可报 |
| `data_gap_detection` | 缺口检测 | 描述本地当前缺失，不代表事实不存在 |

审计结果：

- 27 个 schema 全部有同名 `RetrievalTools` 方法。
- 没有“schema 已注册但底层方法缺失”的工具。
- 没有“底层公开方法已实现但未注册给 agent”的工具。
- DeepSeek agent 默认通过 `get_function_schemas()` 获取完整 27 个 schema。
- DeepSeek agent 工具执行统一走 `call_retrieval_function()`，会做参数校验、未知工具拦截和缺槽提示。

## 已有接口但仍缺正式事实的能力

这些名字已经是正式注册的 function call，但当前只能返回线索和缺口，不能当成最终结论：

| 能力 | 当前状态 | 后续做法 |
|---|---|---|
| `major_streaming_policy_lookup` | 保守接口已完成 | 需要新增真实分流政策/比例数据源，缺官方来源时进缺口队列 |
| `policy_rule_lookup` | 保守接口已完成 | 需要联网/人工确认招生章程、批次规则、身体限制、单科要求 |
| `civil_service_mapping` | 保守接口已完成 | 后续要做专业代码、学历、学位、岗位条件的正式判定 |

所以当前结论是：

- 接口层：27 个正式 function call 已闭环。
- agent 调用层：已能调用全部正式 function call。
- 业务能力层：高风险政策、分流、考公仍缺官方证据链和正式判定。

## Agent 入口

### 1. 离线规则入口

适合测试高频明确问题，不需要 API Key，不需要 LLM。

```powershell
python scripts/natural_language_entrypoint.py "广东物理 580 想学计算机" --no-execute
```

输出包含：

```text
status
intent
slots
tool_plan
tool_trace
data_gaps
warnings
answer_markdown
```

### 2. DeepSeek Function-Call Agent

适合复杂自然语言问题，由模型基于完整 function schema 自动选择工具。

```powershell
python scripts/deepseek_retrieval_agent.py "杭电计算机怎么样？" --show-trace
```

需要配置：

```powershell
$env:DEEPSEEK_API_KEY = "<你的 DeepSeek API Key>"
```

### 3. 统一入口

推荐后续业务都走统一入口：

```powershell
python scripts/retrieval_agent_entrypoint.py "广东物理 580 想学计算机" --mode auto --json
```

模式说明：

| 模式 | 行为 |
|---|---|
| `auto` | 先走规则入口；复杂/未知问题回退 DeepSeek |
| `rules` | 只走离线规则入口，不调用 DeepSeek |
| `deepseek` | 直接走 DeepSeek function-call agent |

只看工具计划，不执行检索：

```powershell
python scripts/retrieval_agent_entrypoint.py "广东物理 580 想学计算机" --mode auto --no-execute --json
```

启用查询日志和缓存：

```powershell
python scripts/retrieval_agent_entrypoint.py "广东物理 580 想学计算机" --mode auto --enable-storage --session-id demo001 --json
```

## 查询日志、缓存与缺口队列

已新增 [scripts/agent_query_storage.py](scripts/agent_query_storage.py)，负责创建和维护六类运营表：

| 表 | 作用 |
|---|---|
| `query_logs` | 记录用户问题、模式、route、intent、slots、tool_plan、tool_trace、answer |
| `retrieval_cache` | 缓存同一规范化查询的结果，减少重复查库和重复生成 |
| `agent_tool_traces` | 将每次工具调用拆成可检索的行，便于排查和统计 |
| `data_gap_queue` | 记录本地库无法可靠回答的缺口，供后续联网 agent 或人工复核处理 |
| `source_documents` | 保存后续联网/人工补证据得到的网页、PDF、招生章程等来源 |
| `data_gap_evidence_tasks` | 把 pending 缺口转成“该搜索什么、优先搜哪些来源”的本地任务 |

建表：

```powershell
python scripts/agent_query_storage.py
```

只打印建表 SQL：

```powershell
python scripts/agent_query_storage.py --print-sql
```

查看待补证据任务，不写库：

```powershell
python scripts/agent_query_storage.py --plan-gap-tasks --limit 10
```

将 `data_gap_queue.pending` 转成 `data_gap_evidence_tasks.ready`：

```powershell
python scripts/agent_query_storage.py --enqueue-gap-tasks --limit 10
```

缓存键第一版由以下内容计算：

```text
agent-cache-v1 + 规范化问题 + mode + route + intent + slots + tool_plan
```

当前真实烟测已经验证：

- `query_logs` 能写入。
- `retrieval_cache` 能写入。
- `agent_tool_traces` 能写入。
- `data_gap_queue` 能在结果存在 `data_gaps` 或关键 `not_found` 时去重入队。
- `data_gap_evidence_tasks` 能把缺口生成稳定搜索任务，供后续联网 agent 或人工复核消费。
- 同一问题第二次查询能返回 `cache_hit: true`。

## 常用命令

运行完整单元测试：

```powershell
python -m unittest discover -s tests
```

列出所有正式 function call：

```powershell
python scripts/retrieval_function_registry.py list-names
```

导出 function schema：

```powershell
python scripts/retrieval_function_registry.py list-schemas
```

直接调用某个 function：

```powershell
python scripts/retrieval_function_registry.py call --tool major_lookup --arguments-json "{\"major_text\":\"计科\"}"
```

本地工具 CLI 示例：

```powershell
python scripts/retrieval_tools.py major_lookup --major "计科"
python scripts/retrieval_tools.py major_profile --major "计算机科学与技术（师范）"
python scripts/retrieval_tools.py school_major_list --school "杭州电子科技大学"
python scripts/retrieval_tools.py rank_to_major_match --province "广东" --subject-type "物理" --score 580 --major "计算机"
```

运行 smoke cases：

```powershell
python scripts/run_retrieval_smoke_cases.py --cases data/retrieval_smoke_cases.json
```

每个工具抽样 1 条真实库用例：

```powershell
python scripts/run_retrieval_smoke_cases.py --sample-per-tool 1 --report reports/retrieval_smoke_sample_27_tools.json
```

## 当前测试状态

最近一次结构迁移验证：

```text
python -m compileall -q src scripts tests
OK

python -m unittest discover -s tests
Ran 734 tests in 95.976s
OK
```

最近一次真实库 smoke 验证记录：

```text
python scripts/run_retrieval_smoke_cases.py --report reports/retrieval_smoke_27_tools_full.json --timeout 60
total 305, passed 305, failed 0, quality_misses 0
```

专项覆盖：

- function registry 与 dispatcher。
- 27 个底层检索工具。
- DeepSeek function-call loop。
- 离线规则自然语言入口。
- 统一 agent 入口。
- 查询日志、缓存、工具轨迹存储层。
- rysxai 市场、考公、转专业数据处理链路。
- 升学/官网证据 crawler、clean package、dashboard 的历史批次回归测试。

## 数据边界

默认不提交：

- `data/raw/`
- `data/processed/`
- `data/logs/`
- `reports/rysxai/`
- `reports/retrieval_smoke*.json`
- `gaokao_test_*.sql`
- 本地数据库 dump
- 本地 `.env`

可以提交：

- 代码。
- 单元测试。
- 小型 seed 数据。
- 设计文档。
- 状态文档。

## 接下来怎么做

建议后续先验收第一版 SQL-first RAG，再进入联网证据补全。

当前最优先：

1. 继续人工抽测 27 个工具，记录命令、输入、预期和异常样例。
2. 为分流、招生政策、考公映射补事实表和写回字段。
3. 最后让联网 agent 消费 `data_gap_evidence_tasks.ready`，做官方来源发现、抓取、抽取和人工复核。

下面是已经完成或规划过的阶段记录。

### 第 1 步：补 `data_gap_queue`（已完成第一版）

目标：把工具返回的 `data_gaps`、本地未命中、高风险政策问题写入缺口队列。

已完成：

- 新建 `data_gap_queue` 表。
- 新建 `source_documents` 与 `data_gap_evidence_tasks` 表。
- 统一入口执行后扫描 `data_gaps`、`warnings`、`status`。
- 同一个缺口做去重和计数，避免重复刷屏。
- 记录用户问题、规范化槽位、缺失字段、已有字段、建议来源和预期写回目标。
- 可把 `pending` 缺口转成稳定的本地证据任务，明确搜索词、优先来源和预期写回目标。

仍未完成：

- 让联网 agent 消费 `data_gap_evidence_tasks.ready` 并自动找官方来源。
- 抽取结果的人工复核、冲突处理和写回事实表。
- 对校专业级就业、官网专业介绍、官方转专业政策、真实分流比例、招生章程规则做稳定事实库。

### 第 2 步：实现 `comparison_query`（已完成第一版）

目标：支持“杭电和浙大怎么选”“A 专业和 B 专业怎么比”“两个志愿方案哪个更稳”。

已完成：

- 先做结构化对比，不直接输出主观结论。
- 可复用 `school_profile`、`major_profile`、`school_major_profile`、`admission_history`、`employment_summary`。
- 缺少目标、省份、科类、分数/位次时返回 `needs_clarification`。

仍未完成：

- 对“两个完整志愿方案”的复杂解析仍需要后续增强。
- 还没有把用户偏好权重、城市偏好、家庭约束等纳入排序模型。

### 第 3 步：设计并实现 `major_streaming_policy_lookup`（保守接口已完成）

目标：查询大类分流政策、分流比例、冷门专业比例。

难点：

- 当前本地库没有稳定真实分流比例来源。
- 不能用专业组内计划数冒充真实入学后分流比例。

已完成：

- 先接收学校、专业组/大类、年份、专业。
- 本地没有官方数据时写 `data_gap_queue`。
- 有学校官网或教务处政策后再入库。

仍未完成：官方分流政策抓取、真实分流比例和冷门专业比例入库。

### 第 4 步：升级 `civil_service_mapping`（保守接口已完成）

目标：从“岗位文本命中”升级到“可报条件判定”。

需要补：

- 专业代码映射。
- 学历要求。
- 学位要求。
- 政治面貌、基层经历、应届身份等限制。
- 岗位表官方来源。
- 人工确认状态。

### 第 5 步：实现 `policy_rule_lookup`（保守接口已完成）

目标：查询招生章程、批次规则、特殊限制。

包括：

- 身体条件限制。
- 单科成绩限制。
- 外语语种限制。
- 中外合作/校区规则。
- 转专业和培养模式限制。
- 各省批次和专业组规则。

这类信息高风险，必须优先官方来源；没有官方来源时不能给确定结论。

### 第 6 步：动态 RAG 与人工复核

目标：当本地库没有数据时，系统自动补证据，但不直接编事实。

当前已完成本地前置层：`data_gap_queue.pending` 可以生成 `data_gap_evidence_tasks.ready`，同时预留 `source_documents` 作为证据落库表。下一步才是真正的联网搜索、抓取、抽取和人工复核。

推荐流程：

```text
统一入口发现缺口
  -> 写 data_gap_queue
  -> 生成 data_gap_evidence_tasks
  -> SourceDiscoveryAgent 找官方来源
  -> CrawlerAgent 抓网页/PDF
  -> ExtractorAgent 抽取结构化字段
  -> VerifierAgent 校验年份、来源等级和冲突
  -> 低置信度进入人工审核
  -> WriterAgent 写回 source_documents / 事实表
  -> 缓存失效并重算答案
```

## 相关文档

- [当前状态快照](docs/status/current-state.md)
- [自然语言总入口设计](docs/specs/natural-language-entrypoint.md)
- [Function Call 工具设计](docs/specs/retrieval-function-calls.md)
- [考生问题地图](docs/specs/candidate-question-map.md)
- [汇总版设计文档](docs/specs/major-intel-consolidated-design.md)
- [数据缺口队列设计](docs/specs/data-gap-queue.md)
