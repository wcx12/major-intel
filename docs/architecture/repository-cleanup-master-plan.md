# 仓库整理总计划

更新时间：2026-06-04  
适用分支：`codex/repository-restructure`  
审查目的：把当前仓库里的三类内容整理成结构清晰、可公开提交、后续可持续开发的工程仓库。

## 1. 背景与目标

当前仓库主要包含三类内容：

1. function call / 本地检索 Agent 相关文件：面向学生问题的工具层、自然语言入口、评估与测试。
2. 高考志愿对话数据集相关文件：对话样本、数据集构建脚本、快照与清洗策略。
3. 各类数据爬取相关文件：就业、考公、升学、官网证据、转专业政策等爬虫、入库、报告与校验脚本。

本轮整理的目标不是重新设计业务功能，而是先把仓库形态整理清楚：

- 让核心代码进入 `src/major_intel/`，形成可导入、可测试、可复用的 Python package。
- 保留 `scripts/` 作为人工运行入口，但逐步把它收敛为轻量 wrapper，不再堆满核心逻辑。
- 把稳定数据集、爬虫、入库、报告、评估、文档放到固定目录。
- 明确哪些本地文件可以进入公开仓库，哪些只能本地保留或写入 `.gitignore`。
- 在不破坏现有命令的前提下完成迁移，让你可以继续手动测试。

## 2. 当前整理原则

1. **先保兼容，再迁移结构**  
   已经能跑的命令不要直接废掉。旧的 `scripts/*.py` 入口优先改成 wrapper，真正逻辑迁到 `src/major_intel/`。

2. **核心代码可提交，批次临时文件谨慎提交**  
   通用 crawler、ingestion、retrieval、agent、evaluation 代码可以进入仓库；大量一次性批次 CSV、JSONL、OCR 中间文件、网页探测结果应先默认本地保留。

3. **公开仓库必须先做安全审查**  
   任何包含账号、密钥、数据库连接串、原始大文件、第三方敏感内容的文件，都不能直接提交。

4. **数据资产要有 manifest 或 README**  
   能提交的数据集样本需要说明来源、字段、用途、是否脱敏、是否为全量。

5. **后续新增 Python 代码必须有足够注释**  
   你的要求已经纳入规则：后面新增或重构的核心代码，需要在复杂逻辑、数据口径、边界条件处添加较丰富的中文或英文注释。

## 3. 目标目录结构

| 目录 | 定位 | 当前状态 |
| --- | --- | --- |
| `src/major_intel/retrieval/` | SQL 检索工具、底层查询能力 | 已完成主体迁移 |
| `src/major_intel/agent/` | function call Agent、工具注册、自然语言入口 | 已完成主体迁移 |
| `src/major_intel/storage/` | 数据库连接、配置、缓存、结构化存储 | 已完成主体迁移 |
| `src/major_intel/evaluation/` | 工具选择、边界样例、答案质量评估 | 已迁移一部分，仍需继续收敛 |
| `src/major_intel/datasets/dialogue/` | 对话数据集构建逻辑 | 已完成主体迁移 |
| `src/major_intel/crawlers/` | 可复用爬虫逻辑 | rysxai 已迁移，升学官网相关未完成 |
| `src/major_intel/ingestion/` | 爬取数据入库、清洗、manifest 更新 | rysxai 已迁移，升学官网相关未完成 |
| `src/major_intel/reporting/` | 数据质量报告、dashboard、overview | rysxai 已迁移，升学官网相关未完成 |
| `scripts/` | 人工命令入口和兼容 wrapper | 已开始整理，仍有大量遗留脚本 |
| `datasets/dialogue/` | 可提交的对话数据集快照 | 已建立结构 |
| `data/seeds/` | 可提交的少量种子或样例数据 | 需要审查，当前有大量未跟踪批次文件 |
| `reports/` | 本地生成报告输出 | 需要默认忽略或只提交精选报告 |
| `docs/` | 设计、状态、计划、研究记录 | 主体可用，需要进一步合并入口 |
| `tests/` | 自动化测试 | 可用，但部分测试仍依赖旧路径 |

## 4. 已完成工作

| 状态 | 工作项 | 证据 | 说明 |
| --- | --- | --- | --- |
| 已完成 | 建立仓库结构设计文档 | `docs/architecture/repository-structure.md` | 定义了长期目录布局。 |
| 已完成 | 建立阶段性整理计划 | `docs/architecture/repository-reorganization-plan.md` | 记录了前几轮迁移任务。 |
| 已完成 | function call / 检索核心迁入 package | commit `bd6e5a0` | 核心逻辑迁入 `src/major_intel/`，保留脚本兼容入口。 |
| 已完成 | 对话数据集构建逻辑迁移 | commit `412a310` | `build_dialogue_assets` 进入 package，正式快照进入 `datasets/dialogue/claude_full`。 |
| 已完成 | rysxai 爬虫、入库、报告模块迁移 | commit `cf6f662` | 市场、考公、转专业政策相关稳定脚本进入 crawler/ingestion/reporting 分层。 |
| 已完成 | 本地文件盘点 | commit `584f6a0` | 生成 `docs/status/local-workspace-inventory-2026-06-04.md`，识别大量未跟踪文件来源。 |
| 已完成 | 保留旧命令兼容性 | 多个 `scripts/*.py` wrapper | 旧命令仍可作为人工测试入口。 |
| 已完成 | 当前工具层功能注册 | `scripts/deepseek_retrieval_agent.py` 及 package 模块 | 之前确认 Agent 侧 function call 接口已留好，RAG 网络搜索后置。 |

## 5. 部分完成工作

| 状态 | 工作项 | 当前问题 | 后续处理 |
| --- | --- | --- | --- |
| 部分完成 | `scripts/` 目录分层 | 已有 wrapper 和部分 `scripts/crawlers`、`scripts/ingestion`、`scripts/reports`，但根目录仍有大量 `curate_*`、`update_*`、`evaluate_*` 脚本。 | 按“稳定通用脚本”和“一次性批次脚本”分类迁移或归档。 |
| 部分完成 | evaluation 体系整理 | 核心评估脚本仍有一部分在 `scripts/` 根目录。 | 迁入 `src/major_intel/evaluation/`，保留 wrapper。 |
| 部分完成 | `.gitignore` 与公开仓库规则 | 已有初步保护，但大量报告、种子、清洗结果仍显示未跟踪。 | 增补忽略规则，并为可提交样例建立白名单。 |
| 部分完成 | 文档入口整理 | 已有设计、状态、研究文档，但入口较多。 | 保留本总计划作为整理主入口，后续把过时计划降级为历史记录。 |
| 部分完成 | 测试路径整理 | 测试可跑，但部分测试仍围绕旧脚本路径。 | 迁移到 package import，旧 wrapper 只做兼容测试。 |
| 部分完成 | 本地数据资产审查 | 已盘点数量和类型，但未判断每个数据文件是否适合提交。 | 先做 manifest，再决定提交、忽略或本地归档。 |

## 6. 未完成工作总表

| 优先级 | 状态 | 工作项 | 为什么要做 |
| --- | --- | --- | --- |
| P0 | 未完成 | 公开仓库安全审查 | 防止密钥、数据库连接、原始敏感数据被提交。 |
| P0 | 未完成 | `.gitignore` 最终加固 | 避免再次出现大量临时 CSV、JSONL、报告输出进入待提交列表。 |
| P1 | 未完成 | 升学 / 官网证据 / CHSI 数据管线整理 | 当前相关脚本和数据最多，也最容易污染仓库。 |
| P1 | 未完成 | `curate_*` 批次脚本归档策略 | 这些脚本多数是一次性修补或网页证据采集，不能全部放在根目录。 |
| P1 | 未完成 | `evaluate_*` 评估脚本迁移 | 评估应成为 package 的一部分，便于持续回归。 |
| P1 | 未完成 | `reports/` 输出治理 | 报告输出应默认本地生成，只提交关键审查报告。 |
| P2 | 未完成 | `tests/` 目录重组 | 测试要按 retrieval、agent、crawler、dataset、evaluation 分层。 |
| P2 | 未完成 | 数据集 manifest 与样例策略 | 明确哪些是正式样本、哪些是临时批次结果。 |
| P2 | 未完成 | README 导航更新 | 让新读者知道如何运行工具、构建数据集、运行爬虫与测试。 |
| P3 | 未完成 | 本地旧文件移动或清理 | 需要你确认后才能移动、压缩或删除。 |

## 7. 后续执行阶段

### 阶段 A：公开仓库安全审查

状态：未完成  
建议优先级：P0  

要做的事：

1. 扫描仓库中可能包含敏感内容的文件类型：`.env`、`.json`、`.toml`、`.ini`、`.sql`、`.csv`、`.jsonl`、日志文件。
2. 检查是否存在数据库密码、API key、cookie、token、个人账号、私有 URL。
3. 把敏感样例改成 `.example` 或文档说明，不提交真实值。
4. 更新 `.gitignore`，覆盖临时输出、缓存、大文件、原始抓取结果。

验收标准：

- `git status --short` 不再出现明显临时文件。
- `rg` 搜索常见敏感关键词无真实凭据。
- README 或配置文档只保留示例变量，不出现真实密码。

建议命令：

```powershell
rg -n "password|passwd|token|api[_-]?key|secret|cookie|Authorization|Bearer" .
git status --short
```

### 阶段 B：升学 / 官网证据数据管线整理

状态：未完成  
建议优先级：P1  

要做的事：

1. 审查当前未跟踪的升学、官网、CHSI 相关脚本：
   - `scripts/graduate_outcome_crawler.py`
   - `scripts/rebuild_graduate_outcome_package.py`
   - `scripts/update_graduate_outcome_package_manifest.py`
   - `scripts/build_graduate_outcomes_dashboard.py`
   - `scripts/probe_remaining_official_urls.py`
   - `scripts/inspect_remaining_seed_candidates.py`
2. 区分三类代码：
   - 可复用 crawler：迁入 `src/major_intel/crawlers/`。
   - 入库 / manifest 构建：迁入 `src/major_intel/ingestion/`。
   - 报告 / dashboard：迁入 `src/major_intel/reporting/`。
3. 对 `data/seeds/graduate_*` 和 `official_site_*` 文件做 manifest 审查。
4. 只提交小型样例、字段说明和必要种子；批量网页搜索结果默认不提交。

验收标准：

- 升学官网相关核心逻辑不再散落在 `scripts/` 根目录。
- 旧脚本入口仍可运行。
- 数据样例有 manifest 或 README。
- 大量 batch CSV 不进入默认提交集合。

### 阶段 C：`curate_*` 和 `update_*` 批次脚本归档

状态：未完成  
建议优先级：P1  

要做的事：

1. 统计所有 `scripts/curate_*.py`、`scripts/update_*.py`。
2. 按用途分类：
   - 官方网页证据采集。
   - PDF / OCR 解析。
   - 具体学校的一次性修补。
   - 就业报告清洗。
   - 升学录取或推免数据补全。
3. 可复用能力抽象为 package 模块。
4. 一次性批次脚本移动到 `scripts/archive/` 或 `scripts/one_off/`。
5. 对每类保留最少 README，说明不要作为稳定 API 使用。

验收标准：

- `scripts/` 根目录只保留稳定命令入口。
- 批次脚本不影响日常人工测试视线。
- 仍能通过历史文件追溯某批数据是怎么来的。

注意：

- 这一步会涉及大量文件移动，执行前需要确认目标目录命名。
- 不删除文件，只做移动和归档。

### 阶段 D：评估脚本和测试体系整理

状态：未完成  
建议优先级：P1/P2  

要做的事：

1. 把以下评估脚本迁入 `src/major_intel/evaluation/`：
   - `scripts/evaluate_deepseek_tool_selection.py`
   - `scripts/evaluate_rank_to_major_match_boundaries.py`
   - `scripts/evaluate_rank_to_school_match_boundaries.py`
   - `scripts/evaluate_score_to_rank_boundaries.py`
   - `scripts/rank_to_major_match_oracles.py`
   - `scripts/rank_to_school_match_oracles.py`
2. 保留 `scripts/evaluate_*.py` wrapper。
3. 将测试目录按模块重组：
   - `tests/retrieval/`
   - `tests/agent/`
   - `tests/crawlers/`
   - `tests/ingestion/`
   - `tests/reporting/`
   - `tests/datasets/`
   - `tests/evaluation/`
4. 优先让测试 import package 模块，而不是 import 根目录脚本。

验收标准：

- `python -m pytest` 通过。
- 关键人工命令仍可运行。
- 测试路径能反映业务模块边界。

### 阶段 E：数据与报告输出治理

状态：未完成  
建议优先级：P2  

要做的事：

1. 明确 `data/` 下哪些目录是可提交资产，哪些是本地运行缓存。
2. 为可提交数据建立 manifest：
   - 文件名。
   - 生成脚本。
   - 字段说明。
   - 来源说明。
   - 是否脱敏。
   - 是否可公开。
3. `reports/` 默认作为本地输出目录，只把关键审查报告放入 `docs/status/`。
4. 对 `clean/`、`tmp/`、`outputs/` 等目录建立忽略或归档策略。

验收标准：

- 新生成报告不会自动污染 `git status`。
- 可公开数据和本地缓存边界明确。
- 你能快速判断一个文件是否应该提交。

### 阶段 F：README 与人工测试入口更新

状态：未完成  
建议优先级：P2  

要做的事：

1. 更新根 README，给出清晰入口：
   - 本地数据库配置。
   - function call 工具测试。
   - Agent 入口。
   - 数据集构建。
   - 爬虫和入库。
   - 评估与测试。
2. 更新或合并已有手动测试文档：
   - `docs/status/retrieval-tool-manual-test-commands.md`
   - `docs/status/retrieval-tool-broad-test-command-dataset.md`
3. 标明哪些命令需要本地 MySQL，哪些只依赖文件。

验收标准：

- 新人只看 README 就知道怎么跑核心功能。
- 你人工测试每个工具时不需要翻历史聊天记录。

### 阶段 G：最终提交前审查

状态：未完成  
建议优先级：P0/P1  

要做的事：

1. 查看完整待提交列表。
2. 分批提交：
   - 结构迁移。
   - 文档整理。
   - `.gitignore` 与仓库卫生。
   - 数据样例和 manifest。
3. 跑完整测试。
4. 再次做敏感信息扫描。
5. 推送到远端。

验收标准：

- 提交历史按主题清晰。
- 没有大型临时文件误提交。
- 没有敏感信息。
- 核心测试通过。

## 8. 不建议现在直接做的事

以下动作需要你明确确认后才能执行：

1. 删除 `clean/`、`reports/`、`tmp/`、`outputs/` 中的任何文件。
2. 批量移动几百个 `data/seeds/*.csv` 文件。
3. 把所有爬取结果直接提交到公开仓库。
4. 改动数据库结构或导入新表。
5. 移除旧 `scripts/*.py` 命令入口。
6. 将大量一次性 `curate_*` 脚本直接删除。

## 9. 建议你这次重点审查的问题

请优先审查下面几个决策点：

1. **批次脚本保留策略**  
   `curate_*` 和 `update_*` 是放到 `scripts/archive/`，还是放到更明确的 `scripts/one_off/official_sources/`？

2. **数据文件公开策略**  
   `data/seeds/official_site_recommendation_websearch_*.csv` 这类批量搜索结果，是完全不提交，还是只提交抽样版和 manifest？

3. **研究文档公开策略**  
   `docs/research/` 里的升学、官网、清洗策略文档是否都可以公开？如果其中有未验证结论，需要标注为调研记录。

4. **报告留存策略**  
   `reports/` 下的评估输出是否全部本地忽略，只把最终结论写入 `docs/status/`？

5. **测试迁移粒度**  
   是先只迁移 retrieval/agent 测试，还是一次性把 crawler 和 curate 测试也重组？

## 10. 我建议的下一步

如果你审查通过，我建议下一步按这个顺序执行：

1. 先做阶段 A：公开仓库安全审查和 `.gitignore` 最终加固。
2. 再做阶段 B：升学 / 官网证据数据管线整理。
3. 然后做阶段 D：评估脚本和测试目录整理。
4. 最后做阶段 C 和 E：批次脚本归档、数据与报告输出治理。

这个顺序的原因是：先控制公开仓库风险，再整理当前最混乱、文件最多的数据管线；评估和测试紧跟其后，保证结构调整不会破坏已有 function call 工具。

## 11. 当前结论

仓库整理已经完成了“核心工程化迁移”的第一段：function call、对话数据集、rysxai 数据管线已经进入 package 分层，并保留旧命令兼容。

还没有完成的是“公开仓库卫生”和“大量本地爬取资产治理”：主要集中在升学官网数据、批次爬虫脚本、报告输出、测试目录和 `.gitignore` 最终加固。

本文件后续可以作为唯一的仓库整理总计划；其他历史计划文档保留为过程记录，不再作为主审查入口。

## 12. 2026-06-04 执行进展

本轮已经按计划完成以下迁移：

| 状态 | 阶段 | 完成内容 |
| --- | --- | --- |
| 已完成 | 阶段 A：公开仓库安全审查与忽略规则 | 扫描常见敏感关键词，未发现真实密码或 API Key 进入待提交文件；加固 `.gitignore`，默认忽略批量 `data/seeds/*.csv/*.jsonl`、临时报告、SQL dump、`clean/`、`clean_*.py`。 |
| 已完成 | 阶段 B：升学 / 官网证据数据管线整理 | `graduate_outcome_crawler` 迁入 `src/major_intel/crawlers/`；升学 clean package 与 manifest 构建迁入 `src/major_intel/ingestion/`；dashboard 迁入 `src/major_intel/reporting/`；旧 CLI 和结构化 CLI wrapper 均已保留。 |
| 已完成 | 阶段 D：评估脚本迁移 | `score_to_rank`、`rank_to_school_match`、`rank_to_major_match`、`major_school_list`、`school_major_list`、`school_major_profile`、DeepSeek 工具选择等评估代码迁入 `src/major_intel/evaluation/`，旧 `scripts/evaluate_*.py` 继续可用。 |
| 已完成 | 阶段 C：一次性批次脚本归档 | 115 个 `curate*.py` / `update*.py` 历史脚本移动到 `scripts/one_off/official_sources/`，并新增 README 说明其非稳定 API 定位。 |
| 已完成 | 阶段 D：测试目录重组 | 根目录测试已按 agents、retrieval、evaluation、crawlers、ingestion、reporting、datasets、one_off 分层；one-off 历史脚本测试移动到 `tests/one_off/official_sources/`。 |
| 已完成 | 阶段 E：数据与报告输出治理 | 批量抓取 seed、临时 reports、输出目录、清洗中间目录默认本地保留，不进入普通提交列表；可提交 seed 继续通过白名单保留。 |
| 已完成 | 阶段 F：README 导航更新 | README 已同步当前目录结构、测试结构和最新结构迁移验证结果。 |

本轮新增或调整的稳定入口：

- `src/major_intel/crawlers/graduate_outcome_crawler.py`
- `src/major_intel/crawlers/official_url_probe.py`
- `src/major_intel/ingestion/graduate_outcome_package.py`
- `src/major_intel/ingestion/graduate_outcome_package_manifest.py`
- `src/major_intel/ingestion/remaining_seed_candidates.py`
- `src/major_intel/reporting/graduate_outcomes_dashboard.py`
- `src/major_intel/evaluation/*.py`
- `scripts/crawlers/*`
- `scripts/ingestion/*`
- `scripts/reports/build_graduate_outcomes_dashboard.py`
- `scripts/evaluation/*`
- `scripts/one_off/official_sources/*`

验证结果：

```text
python -m compileall -q src scripts tests
OK

python -m unittest discover -s tests
Ran 734 tests in 95.976s
OK
```

剩余事项：

1. 提交前仍需做最终 `git status` 审查，确认没有本地大文件或临时文件被误加入。
2. 如要推送公开仓库，建议再跑一次敏感信息扫描，并人工确认 `docs/research/` 的研究记录可以公开。
3. 后续如果要继续强化工程化，可以补充 CI 配置和更完整的依赖锁定；本轮已新增最小 `pyproject.toml`，让 `src/major_intel` 具备标准 package 元数据。
