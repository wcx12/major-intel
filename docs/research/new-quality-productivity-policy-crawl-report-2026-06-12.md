# 新质生产力相关新兴专业数据爬取报告

日期：2026-06-12

## 结论

本轮爬取策略已经从“围绕 AI、低空经济等关键词找专业”调整为“先尽量完整抓取官方专业目录、年度备案/审批结果和政策证据，再在下一阶段做方向映射”。这样可以最大限度降低遗漏风险：现阶段保留所有官方候选，不提前用关键词过滤专业名称。

截至本报告更新，第一阶段官方候选池和政策证据库已经形成可复现产物：

| 数据层 | 最新 run | 覆盖结果 |
| --- | --- | ---: |
| 本科目录/备案审批候选库 | `emerging_major_seed_20260612_v5` | 16 个官方页面、22 个附件、33,981 条候选、1,280 个去重专业 |
| 高职专科专业设置备案库 | `vocational_major_register_2013_2026` | 2013-2026 共 814,328 条备案记录、2,737 个跨年去重专业 |
| 官方专业目录库 | `official_major_catalog_20260612_v2` | 职教目录与研究生目录共 1,530 条目录专业 |
| 政策语料证据库 | `policy_evidence_seed_20260612_v5` | 17 篇中央/部委政策文档、1,019 条方向命中证据 |

需要注意：这仍不是最终“新质生产力专业名单”，而是可追溯的官方候选池。是否属于新质生产力方向、与本地 `edu_major` 如何映射，应作为下一阶段处理。

## 本次补充

本次根据“尽量把所有新兴专业都爬下来，不先做已有专业映射”的要求，补了三类工作：

1. 专业候选源补到 2026 最新本科专业目录，继续保留所有目录/备案/审批候选。
2. 政策证据 seed 从 4 条扩到 17 条，新增发改委、工信部/多部委、科技部、国家数据局、网信办、民航局等官方来源。
3. 政策证据爬虫新增 PDF 解析，支持 `pdftotext` 优先、`pypdf` 回退，并扩展了未来产业、具身智能、人形机器人、低空技术、元宇宙、合成生物、空天信息等关键词。

## 已完成数据

### 1. 本科目录与年度备案审批

最新产物：

- `data/processed/policy_documents/emerging_major_candidates_emerging_major_seed_20260612_v5.csv`
- `data/processed/policy_documents/emerging_major_unique_majors_emerging_major_seed_20260612_v5.csv`
- `reports/policy_documents/emerging_major_coverage_emerging_major_seed_20260612_v5.md`

覆盖范围：

- 2012 年《普通高等学校本科专业目录》及新旧专业对照。
- 2013-2024 年度普通高校本科专业备案和审批结果。
- 2020-2026 年版本科专业目录附件，其中已补入 2026-04-28 教育部最新《普通高等学校本科专业目录（2026年）》。
- 教育部低空技术与工程等新专业政策解读页面作为补充线索。

质量控制：

- 页面抓取成功数：16，失败数：0。
- 附件数：22，`needs_review` 附件数：0。
- 2019 年两份图片型 PDF 已通过 Windows OCR 解析，覆盖报告中 `parse_status=ok`。
- 2026 年本科目录 PDF 已解析，贡献 875 条目录候选。

### 2. 高职专科备案结果

最新产物：

- `data/processed/vocational_major_register/vocational_major_records_2013_2026.csv`
- `data/processed/vocational_major_register/vocational_major_unique_2013_2026.csv`
- `reports/vocational_major_register/vocational_major_register_coverage_2013_2026.md`

数据来自教育部政务服务平台“高等职业教育专科专业设置备案结果查询”接口：

- API 年份覆盖：2013-2026。
- 总记录数：814,328。
- 跨年去重专业数：2,737。
- 每年均校验 `record_count == total_reported` 且 `failure_count == 0`。
- 对接口偶发 500 的年份新增了按失败页补抓修复入口，避免整年重跑和缺页混入。

### 3. 官方专业目录

最新产物：

- `data/processed/official_major_catalog/official_major_catalog_records_official_major_catalog_20260612_v2.csv`
- `reports/official_major_catalog/official_major_catalog_coverage_official_major_catalog_20260612_v2.md`

覆盖范围：

| 来源 | 层次 | 记录数 |
| --- | --- | ---: |
| 《职业教育专业目录（2021年）》 | 中等职业教育 | 358 |
| 《职业教育专业目录（2021年）》 | 高等职业教育专科 | 744 |
| 《职业教育专业目录（2021年）》 | 高等职业教育本科 | 247 |
| 《研究生教育学科专业目录（2022年）》 | 研究生教育 | 181 |

补充说明：高职本科目前先以 2021 职业教育目录为目录级全量源；高职专科的动态设置情况以政务服务平台 2013-2026 备案 API 为准。

### 4. 政策语料证据

最新产物：

- `data/processed/policy_evidence/policy_documents_policy_evidence_seed_20260612_v5.jsonl`
- `data/processed/policy_evidence/policy_mentions_policy_evidence_seed_20260612_v5.csv`
- `reports/policy_evidence/policy_evidence_coverage_policy_evidence_seed_20260612_v5.md`

当前覆盖：

- 2024、2025、2026 年政府工作报告。
- 国务院“人工智能+”行动意见。
- 发改委低空保险、招投标领域人工智能推广应用、生物经济规划、十五五规划纲要。
- 工信部等多部委未来产业、人工智能+制造、人形机器人、元宇宙行动计划。
- 科技部等六部门人工智能场景创新指导意见。
- 网信办/国务院数字中国建设规划、国家数据局数据要素行动计划、民航局人工智能+民航政策。

方向命中结果：

- 成功文档数：17。
- 失败文档数：0。
- 方向证据段落数：1,019。
- 覆盖方向包括 `future_industries`、`artificial_intelligence`、`low_altitude_economy`、`commercial_space`、`bio_manufacturing`、`quantum_technology`、`integrated_circuit`、`advanced_manufacturing`、`green_low_carbon`、`digital_economy`、`new_materials`。

## 数据结构建议

后续建议保留三张主表，而不是把不同层次强行混成一张表：

1. `official_emerging_major_candidates`：本科目录、年度备案审批、新增目录候选。
2. `official_vocational_major_register`：高职专科备案结果，保留学校、省份、年份、专业代码。
3. `official_major_catalog`：职业教育目录、研究生目录等目录级专业。

政策证据单独保留：

1. `policy_evidence_documents`：政策文档。
2. `policy_direction_mentions`：AI、低空经济、未来产业等方向命中片段。

这样做的原因是：本科备案、高职专科备案、职业教育目录、研究生目录的层级和字段语义不同。先分层保真，后续再统一映射到本地专业库和新质生产力方向。

## 防遗漏机制

本轮新增或确认了这些控制点：

- 种子 URL 使用教育部、国务院/国家机关转载、发改委、工信部/多部委、科技部、国家数据局、网信办、民航局等官方来源。
- 附件不只抓 HTML，还解析 PDF、Word、Excel、旧版 DOC。
- 图片型 PDF 不再直接标失败，已支持 Windows OCR 兜底。
- 政策证据 PDF 已支持文本抽取，民航局、人形机器人、生物经济、十五五规划等 PDF 能进入证据库。
- 高职专科 API 逐年校验总数，失败页单独补抓。
- 职业教育目录支持带 `K` 的国控专业代码，避免漏掉临床医学、教育、公安司法类专业。
- 2026 最新本科目录已经补入 seed，避免停留在 2025 版目录。

## 仍需后续处理

严格说，“不遗漏”只能在当前已公开官方来源范围内成立，后续还要持续监控新增政策和目录：

- 如果教育部后续发布新的高职本科目录增补清单，需要继续补到 `official_major_catalog`。
- 如果发改委、工信部、科技部、民航局等继续发布新政策，需要追加到 `policy_evidence_sources.csv` 后复跑。
- MySQL 写库脚本已实现并更新默认路径，但真实入库需要提供数据库凭据。
- 本地 `edu_major` 映射、新质生产力方向标签和置信度评分尚未执行；这是第二阶段任务，不应影响第一阶段候选池完整性。

## 验收口径

第一阶段验收不看“是否已经判断某专业属于新质生产力”，而看：

- 官方来源是否覆盖到最新。
- 附件是否下载并解析。
- 是否有失败页、失败附件、`needs_review` 附件。
- 是否能追溯到来源页面、附件 URL、原始文件和抓取时间。

按这个口径，本轮本科目录/备案审批、高职专科备案、职业教育目录、研究生目录和政策证据的核心爬取链路已经形成可复现产物。
