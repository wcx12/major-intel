# 数据资产提交与 Release 说明（2026-06-18）

本文档记录 2026-06-18 这一轮数据资产整理、Git 提交范围、GitHub Release 打包范围和明确排除项。目标是让远端仓库能保存代码、文档和可审查的小型报告，同时把较大的爬取数据和结构化中间产物放到 Release 资产中，避免把本地数据库、密钥、实验大包或本地工具环境误提交到公开仓库。

## 本轮目标

本轮处理的是 2026-06-12 至 2026-06-15 前后新增或更新的数据资产，重点覆盖：

- 教育部/官方本科专业目录、专业增设/撤销/调整相关证据。
- 高职专业备案/专业目录抓取结果。
- 新质生产力专业政策证据、专业画像和三层院校口径评估。
- AI 可替代性专业数据集和分层样例。
- 高危专业风险证据、风险索引、审查发布表。
- RYSXAI 市场、考公、转专业数据的结构化派生结果。
- 研究生去向数据的派生索引、学校/年份汇总、来源覆盖和 CHSI 公开来源索引。
- 专业核心课程、学科适合度、升学适配度等报告。

## Git 提交范围

Git 只提交适合代码审查、日常 diff 和长期维护的内容：

| 类别 | 路径 | 说明 |
| --- | --- | --- |
| 数据集说明文档 | `docs/datasets/` | 每个派生数据集的含义、字段、来源和使用边界。 |
| 研究/规格文档 | `docs/research/`、`docs/specs/`、`docs/status/` | 新质生产力政策爬取报告、AI 可替代性方案、数据资产发布说明。 |
| 小型报告 | `reports/`，但排除 `reports/volunteer_matching/` | 面向审查和业务使用的 CSV/MD/XLSX 报告，通常可直接阅读或二次分析。 |
| 爬虫脚本 | `scripts/crawlers/`、`src/major_intel/crawlers/` | 官方目录、政策证据、RYSXAI 专业介绍、高危专业、高职目录等抓取入口。 |
| 数据集构建脚本 | `scripts/datasets/`、`src/major_intel/datasets/` | AI 可替代性、对话评测等数据集构建。 |
| 入库/派生脚本 | `scripts/ingestion/`、`src/major_intel/ingestion/` | 从原始/处理数据生成结构化索引、画像和报告输入。 |
| 报告脚本 | `scripts/reports/` | 分层考公、核心课程、工作分布、新质生产力评估等报告生成。 |
| 测试 | `tests/crawlers/`、`tests/datasets/`、`tests/ingestion/` | 覆盖本轮新增爬虫、ingestion、dataset 构建逻辑。 |

本轮发布分支从 `main` 创建，分支名为：

```text
codex/data-assets-release-20260618
```

这样可以避免把当前本地 `codex/volunteer-matching-code` 分支里的志愿匹配算法提交夹带进数据发布 PR。

## GitHub Release 资产

大体量原始抓取、结构化中间产物和生成输出不直接进 Git，而是发布为 GitHub Release 资产。目标 Release tag：

```text
data-assets-2026-06-18
```

当前本地已生成的 Release 资产如下：

| 文件 | 大小 | 条目数 | 内容 |
| --- | ---: | ---: | --- |
| `major-intel-raw-policy-risk-catalog-2026-06-18.zip` | 469.23 MB | 19,529 | 官方专业目录、高职目录、政策证据、高危专业证据的原始抓取与日志。 |
| `major-intel-processed-policy-risk-ai-2026-06-18.zip` | 49.59 MB | 159 | 官方目录、政策证据、新质生产力、AI 可替代性、高危专业风险、资产清单等处理结果。 |
| `major-intel-processed-vocational-register-2026-06-18.zip` | 113.17 MB | 66 | 高职专业备案/目录处理结果。 |
| `major-intel-processed-rysxai-derived-2026-06-18.zip` | 34.68 MB | 21 | RYSXAI 考公、市场、转专业结构化派生结果。 |
| `major-intel-processed-graduate-derived-indexes-2026-06-18.zip` | 2.50 MB | 82 | 研究生去向的派生索引、来源覆盖、学校/年份画像、CHSI 公开来源索引。 |
| `major-intel-generated-outputs-2026-06-18.zip` | 1.82 MB | 7 | 新质生产力专业评估工作簿和汇总输出，已排除 `node_modules`。 |
| `major-intel-data-assets-release-manifest-2026-06-18.json` | 小文件 | - | Release 资产大小、SHA256、排除项和生成信息。 |

SHA256 校验值以 `major-intel-data-assets-release-manifest-2026-06-18.json` 为准。

## 明确排除项

以下内容本轮不提交到 Git，也不上传到 Release：

| 排除项 | 原因 |
| --- | --- |
| MySQL dump，例如 `gaokao_test_*.sql` | 用户已明确要求核心数据库不要上传。 |
| `.env`、`.env.*`、密钥、密码、API token | 公开仓库安全边界。 |
| `reports/volunteer_matching/` | 用户已明确说“志愿匹配实验/评测报告数据不用上传”；该目录本地约 4.34 GB。 |
| `.agents/`、`.aris/`、`.claude/`、`external/`、`AGENTS.md`、`CLAUDE.md` | 本地工具/技能/外部仓库环境，不属于项目数据本体。 |
| `node_modules/`、`.pnpm/`、`__pycache__/`、`*.pyc` | 可再生依赖或缓存。 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 内部完整清洗表，存在未脱敏姓名/编号风险。 |
| `data/cleaned/graduate_outcomes/` 整目录 | 为避免误传未脱敏研究生主表，本轮不整体上传 cleaned 研究生目录。需要使用时优先使用脱敏公开表或既有公开包。 |
| 历史研究生去向 raw/processed 大批次 | 体量较大且包含人员级官方名单原文；本轮只上传派生索引，不重复上传原始人员级批次。 |

## 与既有 Release 的关系

本轮不是替代所有历史 Release，而是新增一轮数据资产：

- `rysxai-major-intros-2026-06-11`：已包含 RYSXAI 专业介绍原始/处理数据和 manifest，本轮不重复打包完整专业介绍大包。
- `full-local-assets-2026-06-05` / `crawled-data-2026-06-05`：保存早期全量本地资产或爬取数据，本轮只补充 2026-06-12 之后新增/派生的数据。
- `data-assets-2026-06-18`：本轮新增官方目录、政策证据、高危专业、新质生产力、AI 可替代性、RYSXAI 衍生和研究生派生索引。

## 下载后如何恢复

假设仓库克隆在：

```powershell
C:\Users\10627\Desktop\major-intel
```

下载 Release 资产后，可以在仓库根目录执行：

```powershell
Expand-Archive .\major-intel-raw-policy-risk-catalog-2026-06-18.zip -DestinationPath .
Expand-Archive .\major-intel-processed-policy-risk-ai-2026-06-18.zip -DestinationPath .
Expand-Archive .\major-intel-processed-vocational-register-2026-06-18.zip -DestinationPath .
Expand-Archive .\major-intel-processed-rysxai-derived-2026-06-18.zip -DestinationPath .
Expand-Archive .\major-intel-processed-graduate-derived-indexes-2026-06-18.zip -DestinationPath .
Expand-Archive .\major-intel-generated-outputs-2026-06-18.zip -DestinationPath .
```

恢复后，目录会回到仓库约定位置，例如：

- `data/raw/...`
- `data/processed/...`
- `data/logs/...`
- `outputs/new_quality_major_eval_20260613/...`

## 如何使用这些数据

优先阅读 `docs/datasets/` 中的数据集说明，再进入对应报告或处理结果：

| 需求 | 推荐入口 |
| --- | --- |
| 看现有数据资产总览 | `docs/status/data-catalog-and-requirement-coverage-2026-06-12.md` |
| 看新质生产力专业 | `reports/new_quality_major_three_tier_20260614/`、`docs/datasets/new-quality-major-profiles.md` |
| 看 AI 可替代性 | `reports/ai_replacement/`、`docs/datasets/major-ai-replacement-risk.md` |
| 看高危专业 | `reports/major_risk_*`、`docs/datasets/major-risk-master-index.md` |
| 看官方专业目录/新增撤销 | `reports/official_major_catalog/`、`docs/datasets/undergraduate-major-official-events.md` |
| 看高职专业备案 | `reports/vocational_major_register/`、`docs/datasets/vocational-major-register.md` |
| 看专业核心课程 | `reports/major_core_courses_by_tier/` |
| 看学科适合度 | `reports/major_subject_fit_20260614/` |
| 看升学适配度 | `reports/major_graduate_study_fit_20260615/` |
| 看考公适配 | `reports/rysxai_civil_service/` |
| 看就业/工作分布 | `reports/rysxai_market/` |
| 看转专业政策画像 | `reports/rysxai_transfer_policies/` |
| 看研究生去向派生汇总 | `reports/graduate_outcomes/`、`reports/graduate_*` |

## 验证记录

本轮打包后做过以下静态核验：

- 所有 Release zip 均显式列目录生成，不使用整仓库打包。
- Release zip 路径扫描未发现：
  - `volunteer_matching`
  - `.env` / `.env.*`
  - `gaokao_test_*.sql` / `.sql`
  - `master_records_clean.csv`
  - `data/cleaned/graduate_outcomes`
  - `external/`
  - `.agents/` / `.aris/` / `.claude/`
  - `node_modules` / `.pnpm`
- `major-intel-generated-outputs-2026-06-18.zip` 曾发现 `node_modules` 被误打入，已重建并复核通过。

本轮发布分支上执行过轻量测试：

```powershell
python -m pytest tests/crawlers tests/datasets tests/ingestion tests/test_civil_service_major_fit_by_tier.py -q
```

结果：

```text
390 passed, 16 skipped
```

其中 16 个 skipped 来自 `tests/ingestion/test_graduate_outcomes_workbook_package.py`。该测试依赖 `data/cleaned/graduate_outcomes` 和 `outputs/graduate_outcomes` 下的本地大包资产；这些资产按本轮公开边界没有提交进 Git，因此在干净仓库中跳过是预期行为。

## 剩余本地未上传内容

本轮完成后，本地仍会保留一些不上传内容：

- `reports/volunteer_matching/`：志愿匹配实验/评测报告数据，按用户要求不上传。
- `.agents/`、`.aris/`、`.claude/`、`external/`：本地工具环境。
- `tmp/`、`__pycache__/`、`.pyc`、`node_modules/`：缓存和依赖。
- 本地 MySQL 数据库和 dump：不上传。
- 研究生去向未脱敏清洗主表和人员级 raw 批次：本轮不公开上传，避免误传敏感人员级信息。
