# 本地工作区盘点报告

盘点日期：2026-06-04

本报告只记录本地文件状态和整理建议。本次盘点没有移动、删除或提交未跟踪数据文件。

## 当前状态

- 当前分支：`codex/repository-restructure`
- 已跟踪文件状态：干净
- 未跟踪文件：约 896 个
- `git status --short` 输出行数：859 行，部分目录被折叠显示
- 主要未跟踪目录分布：

| 顶层目录 | 未跟踪数量 | 初步判断 |
|---|---:|---|
| `data/` | 587 | 以本地 seed、批次 CSV 为主，需要筛选后才能提交 |
| `scripts/` | 126 | 以一次性补数、评测、graduate outcome 脚本为主 |
| `tests/` | 107 | 以一次性补数脚本对应测试为主 |
| `clean/` | 38 | 对话数据集历史/实验产物，正式快照已迁入 `datasets/dialogue/claude_full/` |
| `reports/` | 28 | 评测报告和 JSONL 结果，默认应视为可再生成产物 |
| `docs/` | 9 | 研究文档，部分可提交但需要审查来源和口径 |
| 根目录 | 1 | `clean_gaokao_dialogue_candidates.py`，旧实验脚本 |

## 文件类型分布

| 类型 | 数量 | 说明 |
|---|---:|---|
| `.csv` | 584 | 主要是 official-site websearch 批次和少量 CHSI / graduate outcome seed |
| `.py` | 234 | 主要是 `curate_*`、`update_*`、评测和 graduate outcome 脚本 |
| `.jsonl` | 40 | 主要是评测结果、失败记录、对话清洗产物 |
| `.md` | 32 | 主要是评测报告和研究文档 |
| `.json` | 5 | 少量清洗/报告产物 |
| `.gitkeep` | 1 | `clean/dialogue/.gitkeep` |

## 大文件和大目录

当前本地体量较大的目录：

| 目录 | 约占用 |
|---|---:|
| `.git/` | 3.1GB |
| `data/` | 2.9GB |
| `tmp/` | 491MB |
| `gaokao-zhiyuan-projects/` | 64MB |
| `reports/` | 50MB |
| `outputs/` | 34MB |

未跟踪大文件主要集中在 `reports/*.jsonl`、`docs/research/*.md`、`scripts/graduate_outcome_crawler.py`、`tests/test_graduate_outcome_crawler.py` 和 `clean/dialogue/*.jsonl`。这些不是当前应该直接加入公开仓库的对象。

## 分类判断

### 1. 本地数据产物：默认不提交

代表内容：

- `data/seeds/official_site_recommendation_websearch_web_*.csv`：575 个批次文件。
- `data/seeds/official_site_*.csv`：7 个其他 official-site seed。
- `data/seeds/chsi_*`：3 个 CHSI 相关 seed。
- `data/seeds/*graduate_outcome*`：2 个 graduate outcome sample seed。
- `data/raw/`、`data/processed/`、`data/cache/`、`tmp/`、`outputs/`：已被忽略或应继续作为本地产物处理。
- `gaokao_test_*.sql`：数据库 dump，已被忽略，不应进入公开仓库。
- `.env`：已被忽略，不应进入公开仓库。

建议：

- 不直接提交 575 个批次 CSV。
- 后续如果需要公开一部分 seed，应先合并成小型、去重、脱敏、带 manifest 的 `data/seeds/*.sample.csv` 或 `datasets/samples/` 文件。

### 2. 生成报告：默认不提交

代表内容：

- `reports/rank_to_*_boundary_eval_*.jsonl`
- `reports/rank_to_*_boundary_eval_*.md`
- `reports/score_to_rank_boundary_eval_*.jsonl`
- `reports/school_major_profile_answer_eval_agent_sample.*`

建议：

- `reports/*.jsonl` 默认继续视为可再生成结果。
- 如果某份 `.md` 是阶段性结论，可以挑选后迁入 `docs/status/` 或 `docs/research/`，不要把整批 `reports/` 直接提交。

### 3. 对话数据集历史产物：等待确认后归档或删除

代表内容：

- `clean/dialogue/`
- `clean/dialogue_claude_sample/`
- `clean/dialogue_claude_full_check/`
- `clean/gaokao_dialogue_candidates_cleaned.json`
- `clean_gaokao_dialogue_candidates.py`

现状：

- 正式可提交快照已经迁入 `datasets/dialogue/claude_full/`。
- `clean/` 下内容多数是历史生成物或校验副本。

建议：

- 短期：加入更明确的忽略规则或迁入 `local/archive/dialogue/`。
- 删除前必须人工确认，因为这些文件可能仍有调试价值。

### 4. Legacy 补数脚本和测试：适合单独归档，不适合混入 `src`

代表内容：

- `scripts/curate_batch*.py` 和 `scripts/curate_*.py`：约 107 个。
- `tests/test_curate*.py`：约 103 个。
- `scripts/update_*.py`：约 8 个。

判断：

- 这些脚本看起来是官方来源补数、PDF/HTML/OCR 修复、缺口批次补录的历史作业。
- 它们有对应测试，说明有保留价值。
- 但它们多数是一次性脚本，不应进入 `src/major_intel/crawlers/` 的稳定实现层。

建议：

- 如果要公开提交，迁入：
  - `scripts/crawlers/legacy_batches/`
  - `tests/crawlers/legacy_batches/`
- 同时加 `README.md` 说明它们是历史补数脚本，不是稳定产品 API。
- 先抽样审查 3-5 个脚本，确认没有本地路径、账号、cookie、个人信息或不可公开原始数据。

### 5. Graduate outcome 链路：下一批优先整理

代表内容：

- `scripts/graduate_outcome_crawler.py`
- `scripts/rebuild_graduate_outcome_package.py`
- `scripts/build_graduate_outcomes_dashboard.py`
- `tests/test_graduate_outcome_crawler.py`
- `tests/test_graduate_outcomes_dashboard.py`
- `tests/test_graduate_outcomes_workbook_package.py`
- `docs/research/graduate_outcome_*.md`

判断：

- 这一块和项目核心需求“校专业级就业、升学、薪资、去向证据链”最相关。
- 文件较大，且已有测试，优先级高于普通 legacy batch。

建议：

- 下一批先做 graduate outcome 专项重构：
  - 稳定 crawler/解析逻辑进入 `src/major_intel/crawlers/graduate_outcomes/`
  - dashboard/report 进入 `src/major_intel/reporting/`
  - package rebuild / manifest 进入 `src/major_intel/ingestion/` 或 `src/major_intel/datasets/`
  - 旧 `scripts/*.py` 保留 wrapper
  - 相关测试迁入 `tests/crawlers/graduate_outcomes/` 或继续保持兼容导入

### 6. 研究文档：可提交，但需要审查

代表内容：

- `docs/research/2026-05-22-graduate-outcome-data-source-research.md`
- `docs/research/2026-05-23-dialogue-cleaning-strategy.md`
- `docs/research/official_site_recommendation_crawl_update_2026-05-22.md`
- `docs/research/graduate_outcome_remaining_blockers_2026-06-03.md`

建议：

- 这些文档可以作为项目知识沉淀，但提交前需要确认：
  - 是否包含不可公开 URL、账号、cookie、内部路径或个人信息。
  - 是否包含未核验事实断言。
  - 是否应该拆成“公开摘要”和“本地操作日志”两类。

## 建议的下一步执行顺序

1. **graduate outcome 专项整理**
   这是最贴近产品需求的数据链路，优先迁入结构化目录并保留 wrapper。

2. **补 `.gitignore`**
   针对 `reports/*.jsonl`、`clean/`、批量 websearch CSV、临时 OCR/HTML/PDF 包继续加防误提交规则。

3. **legacy batch 归档试点**
   选 3-5 个 `curate_batch*.py` 做试点迁移，确认目录、测试和文档模式后再批量处理。

4. **研究文档审查**
   从 graduate outcome 相关文档开始，挑选可以公开提交的摘要，避免把过程日志全部塞进远端。

5. **本地物理归档或删除**
   等你确认后，再把 `clean/`、部分 `reports/`、过期 `tmp/` 迁入本地归档目录或删除。默认不删除。
