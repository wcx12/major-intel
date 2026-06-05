# 毕业出路数据清洗包说明

更新日期：2026-06-03

## 可直接使用的数据文件

统一数据包目录：

- `data/cleaned/graduate_outcomes/master_records_clean.csv`
- `data/cleaned/graduate_outcomes/master_records_public.csv`
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`
- `data/cleaned/graduate_outcomes/undergraduate_school_outcome_summary.csv`
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`
- `data/cleaned/graduate_outcomes/official_recommendation_source_attempts.csv`
- `data/cleaned/graduate_outcomes/official_employment_report_sources.csv`
- `data/cleaned/graduate_outcomes/official_employment_report_metrics.csv`
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

当前规模：

| 数据源 | 记录数 | 学校/年份/类型汇总组 |
| --- | ---: | ---: |
| CHSI/研招网录取公示 | 5,705 | 152 |
| 高校官网推免/拟录取名单 | 277,305 | 470 |
| 合计 | 283,010 | 622 |

新增可用汇总：

| 汇总表 | 行数 | 用途 |
| --- | ---: | --- |
| `undergraduate_school_outcome_summary.csv` | 642 | 按本科来源学校、年份、去向学校、路径汇总已抓取的推免/拟录取去向样本 |
| `official_recommendation_source_attempts.csv` | 15 | 记录原 15 所 B 类缺口院校官方源 live 复测结果、阻断类型和入库状态 |
| `official_employment_report_sources.csv` | 64 | 官方就业/教学质量报告候选源状态与阻断证据 |
| `official_employment_report_metrics.csv` | 218 | 已可抽取的就业、升学、深造等指标 |

## 文件选择建议

- 优先给分析、展示、共享使用：`master_records_public.csv`
- 内部复核或继续清洗使用：`master_records_clean.csv`
- 做覆盖率、院校年份统计使用：`school_year_source_summary.csv`
- 做“某本科院校学生去了哪些学校/路径”的去向汇总：`undergraduate_school_outcome_summary.csv`
- 追踪保研资格院校官网名单覆盖：`official_recommendation_school_coverage.csv`
- 查看原 15 所缺口的 live 复测与当前入库状态：`official_recommendation_source_attempts.csv`
- Excel 筛选和快速浏览：`graduate_outcomes_clean_data_package.xlsx`

`public` 表已去掉明文姓名和学号，只保留脱敏姓名/脱敏学号。`clean` 表保留从公开网页中抽取到的明文字段，便于核验原始来源。

## 主要字段

| 字段 | 含义 |
| --- | --- |
| source_dataset | 来源批次。`chsi_yanzhao` 为研招网/CHSI，`official_site_recommendation` 为高校官网推免名单 |
| record_id / public_record_id | 记录唯一 ID |
| school_name | 发布名单的学校或招生单位 |
| year | 名单年份 |
| document_type | 文档类型，如推免名单、拟录取名单 |
| route | 路径类型，如 `recommendation_exemption`、`postgraduate_exam_or_admission` |
| person_name_masked | 脱敏姓名 |
| student_id_masked | 脱敏学号 |
| undergraduate_school | 本科毕业学校 |
| undergraduate_major | 本科专业 |
| college | 发布学院、录取学院或名单中的学院字段 |
| major / admission_major | 专业、录取专业或名单中的专业字段 |
| ranking | 排名/序号 |
| remarks | 备注 |
| source_url | 可追溯来源 URL |
| title | 来源页面标题或名单标题 |
| needs_review | 是否建议人工复核 |
| quality_score | 记录质量分 |
| quality_flags | 缺失字段、疑似错位等质量标记 |

`undergraduate_school_outcome_summary.csv` 的核心字段：

| 字段 | 含义 |
| --- | --- |
| undergraduate_school | 本科来源学校 |
| destination_school | 去向/录取学校，即原明细表中的 `school_name` |
| year | 名单年份 |
| source_dataset | 来源批次 |
| document_type / route | 文档类型与升学路径 |
| record_count / unique_person_count | 该组合下记录数与去重人数 |
| with_student_id_count / with_admission_major_count | 有学号、录取专业信息的记录数 |
| source_document_count | 该组合涉及的官方来源文档数 |

`official_recommendation_source_attempts.csv` 的核心字段：

| 字段 | 含义 |
| --- | --- |
| school_name | 仍未完成官网行级名单覆盖的学校 |
| source_title / source_url | 已复测的官方候选源标题与 URL |
| live_status / content_type | live 请求返回状态和实际内容类型 |
| decision | 是否入库；当前 15 条均为 `no_ingest` |
| blocker_type | 阻断类型，如 JS challenge、WAF、验证码桥、页面移除、非行级名单 |
| notes / last_checked_date | 简要说明与最后复测日期 |

## 数据源边界

1. CHSI/研招网部分以公开招生单位公告为主，覆盖录取/拟录取方向，不等同于各学校本科推免资格全量名单。
2. 高校官网部分以公开命中的推免名单页为主，HTML 表格/正文名单解析效果最好。
3. PDF 已保存原文档，但部分高校 PDF 字体编码导致中文抽取乱码，当前不强行并入清洗表。
4. 学校首页自动发现命中率低；当前高收益路线是搜索命中的官网名单页入种子，再批量抓取清洗。
5. 当前清洗包是“已公开抓取且可结构化”的可用数据集，不代表所有高校全量覆盖已完成。

## 官网推免覆盖追踪

`official_recommendation_school_coverage.csv` 以公开高校官网目录中已匹配到的 430 所保研资格院校为底表，按学校名精确匹配当前 B 类官网推免主表。

当前结果：

- 底表院校：430 所
- 已精确匹配官网记录：416 所
- 暂无精确匹配：14 所

注意：这个覆盖率是严格按学校名精确匹配的进度追踪。部分学院页、分校区、医学部、研究院或名称变体可能已有记录，但还需要后续做别名归并后才会提高覆盖数。

## 2026-06-03 追加批次：官方就业/升学报告补充

本轮继续补充官方就业质量报告/本科教学质量报告指标。新增北京化工大学 2023-2024 学年本科教学质量报告 30 条指标、中国传媒大学 2023-2024 学年本科教学质量报告 16 条指标；同步记录北京中医药大学官方候选 PDF 连接超时、中央财经大学官方候选页 HTTP 403，均未入库指标。

重建后 `official_employment_report_sources.csv` 为 64 行，`official_employment_report_metrics.csv` 为 218 行，指标覆盖 22 所学校；Excel 包已同步到 `Employment_Report_Sources` 和 `Employment_Metrics` 两个 sheet。

## 2026-06-03 追加批次：东北电力大学推免补录

本轮从东北电力大学研究生院官网补入 2026 年接收推荐免试研究生拟录取名单补录公示 1 条。主名单 `https://grad.neepu.edu.cn/info/1050/3500.htm` 本地 live 请求仍返回 1.7KB 404 壳，未采用搜索缓存内容；补录页 `https://grad.neepu.edu.cn/info/1050/3790.htm` 为官方行级名单源，本次入 B 类 master。重建后 B 类官网记录为 277,305 条，总包记录为 283,010 条，B 类覆盖提升至 416 / 430。

## 2026-06-02 追加批次：batch398-batch401 甘肃农业大学

batch398-batch400 继续复核南京理工大学与华东师范大学官方源。南京理工大学 2026 硕士/推免拟录取公告页及搜索恢复出的实际公告 URL 实时均为 HTTP 410，留证不入库。华东师范大学 2026 硕士、推免、港澳台拟录取公告页均可抓取，但公示结束后正文仅保留“附件/公示已结束”文本，未暴露真实 PDF href，未入库。

batch401 从甘肃农业大学生命科学技术学院官网抓取 2024 年硕士研究生招生拟录取名单（一志愿）公告及官方 PDF 附件。通用解析可抽出候选但表格跨页表头导致错列；按 TDD 新增 `scripts/curate_batch401_gsau_life_2024_admission.py` 与 `tests/test_curate_batch401_gsau_life_2024_admission.py`，按“序号 + 姓名 + 15 位考生编号”重建 41 条人员记录。PDF 中重复出现的 `否` 为“是否推免/是否调剂/是否同等学力”字段，不是拟录取否定状态；本批备注统一保留 `official_admission_status: 拟录取`。

可追溯来源：
- 甘肃农业大学生命科学技术学院 2024 年硕士研究生招生拟录取名单（一志愿）公示：`http://smkx.gsau.edu.cn/info/1003/7682.htm`
- 官方 PDF 附件：`http://smkx.gsau.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1058947186&wbfileid=C60A7EB8CE87B56AB2C64DD8D54FC201`

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 267,991 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 267,991 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 273,696 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 273,696 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 597 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，393 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch401_gsau_life_2024_admission`：2 个测试通过。
- 本批 41 条均含 `official_admission_status: 拟录取`，硬排除词扫描命中 0。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 273,696 条、Source_Summary 597 条、Coverage 430 条。

## 2026-06-02 追加批次：batch395-batch397 中国人民公安大学

batch395 北京电影学院 2025 年硕士拟录取官方页实时 HTTP 412，未绕过；batch396 中国海洋大学 2026 年推免拟录取官方 PDF 直链实时 HTTP 404，未入库。

batch397 从中国人民公安大学研究生招生办公室官网直链 PDF 抓取 2014 年硕士研究生招生复试情况及拟录取名单。该 PDF 文本层完整，但通用爬虫未能抽取；按 TDD 新增 `scripts/curate_batch397_ppsuc_2014_admission.py` 与 `tests/test_curate_batch397_ppsuc_2014_admission.py`，按考生编号分段，只保留“是否拟录取”为 `是` 或 `调剂是` 的行，剔除 73 条 `否` 状态行，最终入库 406 条考生编号级拟录取记录。

可追溯来源：
- 中国人民公安大学 2014 年硕士研究生招生复试情况及拟录取名单（不含校外调剂）官方 PDF：`https://yzb.ppsuc.edu.cn/__local/9/4F/D1/6028C1BCA976E6639F8E94AF1A4_4303F51F_97DED.pdf?e=.pdf`

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 267,950 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 267,950 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 273,655 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 273,655 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 596 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，392 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch397_ppsuc_2014_admission`：4 个测试通过。
- 本批 406 条均含 `official_admission_status: 是`，`official_admission_status: 否` 命中 0。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 273,655 条、Source_Summary 596 条、Coverage 430 条。

## 2026-06-02 追加批次：batch386-batch394 华中科技大学

batch386-batch393 继续复核剩余 B 类缺口院校。广东药科大学 2026/2025 新官网 URL 实时 404；郑州轻工业大学 2024 博士拟录取公告页可抓但附件已不暴露；北京林业大学 2025 博士公告页可抓但唯一附件为政审表模板；东北师范大学 2026 推免公告页仅保留公告正文、无人员表，2025 硕士页实时 404；天津财经大学、中国药科大学、浙江中医药大学等官方 URL 或 PDF 直链实时返回 404/410/412/405；上述来源均留证不入库。

batch393 复核华中科技大学官网时发现 2024 年推免拟录取公告页正文公开嵌入同站 `__local` PDF，batch394 将该官方 PDF 作为直链种子抓取。通用解析抽出 4,033 条候选，清洗后 3,830 条；专项复核发现 99 条 `1/99` 至 `99/99` PDF 页码伪记录，按 TDD 新增 `scripts/curate_batch394_hust_recommendation_pdf.py` 与 `tests/test_curate_batch394_hust_recommendation_pdf.py` 剔除页码行，最终入库 3,731 条华中科技大学 2024 年推免拟录取记录。

可追溯来源：
- 华中科技大学 2024 年接收推荐免试攻读硕士学位和直接攻读博士学位研究生拟录取名单公示：`https://gszs.hust.edu.cn/info/1106/3712.htm`
- 官方 PDF：`https://gszs.hust.edu.cn/__local/D/9F/71/CE5F0511A0D45E40D020485F894_5E25830F_FCCF6.pdf`

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 267,544 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 267,544 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 273,249 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 273,249 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 595 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，391 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch394_hust_recommendation_pdf`：2 个测试通过。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 华中科技大学入库 3,731 条，`person_name` 页码伪行命中 0。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 273,249 条、Source_Summary 595 条、Coverage 430 条。

## 2026-06-02 追加批次：batch354 陕西科技大学

batch353 尝试天津财经大学 2026 年硕博连读拟录取资格名单，项目爬虫和 `curl.exe -L` 复核均得到官网 404 页面，留证不入库。

batch354 从陕西科技大学研究生招生信息网公开公告页下载官方 PDF 附件，并补入 2025 年硕士研究生拟录取考生名单。通用解析可保存 PDF，但会漏掉准考证号并错处理专业名称换行；本批新增专项脚本，按 PyMuPDF word 坐标重组表格行，保留准考证号、学院代码、专业代码、学习形式、成绩和备注。最终入库 1,959 条，需复核 0 条。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 263,813 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 263,813 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 269,518 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 269,518 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 594 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，390 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch354_sust_admission tests.test_curate_batch350_bisu_admission`：6 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：128 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 595 行、Coverage 431 行、Public_Records 269,519 行；公式单元格 0，公式错误 0。

## 2026-06-02 继续筛查：batch372-batch385

batch372-batch385 继续围绕剩余 40 所 B 类缺口院校检索和实时抓取官网源。福建师范大学、佛山大学、成都体育学院、首都师范大学、南京理工大学、桂林医科大学、东北电力大学、山西中医药大学、北京协和医学院、沈阳体育学院、甘肃农业大学、南京财经大学等均已建立 seed 并留证。未入库原因包括实时 404/410/412、跳转学校首页、Web 应用防火墙/人机识别页、附件下载验证码桥、错误页，以及北京协和医学院官方结果系统当前为 2027 空表。该轮没有向主表追加记录，避免将搜索索引、验证码页、统计/空表或错误页误并入最终可用数据。

## 2026-06-02 追加批次：batch350-batch352 北京第二外国语学院、太原科技大学

batch340-batch352 继续筛查剩余覆盖缺口。华中科技大学、东北师范大学、南京财经大学、中国药科大学、中国医科大学、云南民族大学、中国政法大学、山西中医药大学、沈阳体育学院、大连海洋大学等官网源已留证；主要未入库原因为实时 404/410/412/521、JS challenge、验证码下载桥、公示期结束后不再暴露人员附件，或仅有公告正文无人员表。

batch350 从北京第二外国语学院官网直链 PDF 补入 2025 年研究生招生考试一志愿拟录取名单。因 PDF 表格存在“姓名+考生编号”粘连，本批新增专项脚本按 PyMuPDF word 坐标重组表格行，最终入库 428 条。

batch352 从太原科技大学信息公开专网补入 2025 年学术型博士研究生复试结果公示（第二批）中的 6 条拟录取记录。页面正文明确为拟录取名单，表格含“是否拟录取”列，抓取行均为“是”。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 261,854 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 261,854 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 267,559 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 267,559 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 593 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，389 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch350_bisu_admission tests.test_curate_batch339_tute_admission`：6 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：125 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 594 行、Coverage 431 行、Public_Records 267,560 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch339 天津职业技术师范大学

batch330-batch338 继续筛选剩余覆盖缺口。浙江中医药大学、大连外国语大学、西北师范大学、沈阳体育学院、沈阳航空航天大学、中国人民公安大学、重庆邮电大学、齐鲁工业大学、北京第二外国语学院和山西中医药大学相关官网源均已留证；主要未入库原因为 HTTP 412/405/404/410/502、公示结束后不再暴露名单附件，或附件进入验证码下载桥。

batch339 从天津职业技术师范大学官网 PDF 直链补入 2025 年硕士研究生拟录取名单。通用解析能提取 525 条标准考生编号行；专项复核发现还有 1 条“免初试”拟录取行没有考生编号，本批新增专项脚本保留该行，最终入库 526 条。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 261,420 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 261,420 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 267,125 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 267,125 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 591 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，387 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch339_tute_admission`：3 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：122 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 592 行、Coverage 431 行、Public_Records 267,126 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch329 渤海大学

batch329 从渤海大学研究生招生信息网公开公告页恢复官方 PDF 附件路径，并补入 2025 年全国硕士研究生招生拟录取名单。通用 PDF 解析可抽出候选行，但存在局部错列风险；本批新增专项脚本，按 `考生编号 姓名 学院 专业 拟录取类别 初试 复试 综合 学习方式 备注` 的文本结构解析，只保留完整人员行。

本批新增渤海大学 2025 年硕士拟录取记录 1,618 条，空姓名 0、空考生编号 0、空学院 0、空拟录取专业 0、需复核 0、重复关键记录 0。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 260,894 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 260,894 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 266,599 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 266,599 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 590 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，386 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch329_bhu_admission`：3 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：119 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 591 行、Coverage 431 行、Public_Records 266,600 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch328 新疆医科大学

batch326-batch327 继续筛选剩余覆盖缺口。大连海洋大学页面实时归一为提示信息页且 PDF 直链返回 404；中国政法大学拟录取公告页实时返回 JS challenge。上述来源均留证不入库。

batch328 从新疆医科大学研究生学院官网公开 PDF 直链补入 2023 年硕士研究生一志愿拟录取名单和调剂第一批拟录取名单。源 PDF 同时包含拟录取、放弃、不予拟录取、不予复试和计划受限等状态，本批专项清洗只保留官方状态为 `拟录取` 的人员行，最终新增 1,551 条记录，其中一志愿 1,049 条、调剂第一批 502 条，需复核 0 条。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 259,276 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 259,276 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 264,981 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 264,981 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 589 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，385 所已精确匹配 |

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：116 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 590 行、Coverage 431 行、Public_Records 264,982 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch325 内蒙古民族大学

batch319-batch324 继续筛选剩余覆盖缺口。中国药科大学、东北师范大学、天津财经大学命中的官网入口实时返回 410/404，留证不入库；内蒙古民族大学研究生院可抓取，硕士调剂 PDF 为公告、一志愿 PDF 为复试名单，均不入库。博士拟录取结果页指向蒙医药学院官网，学院页公开官方 PNG 名单。

本批按官方 PNG 图片转写内蒙古民族大学 2026 年中药学专业博士研究生招生“申请-考核”制拟录取名单。图片含 25 行，其中 22 行“是否拟录取=是”、2 行“否”、1 行“放弃”；只保留 22 条明确拟录取记录，需复核 0 条。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 257,725 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 257,725 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 263,430 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 263,430 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 588 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，384 所已精确匹配 |

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：115 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 589 行、Coverage 431 行、Public_Records 263,431 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch318 上海科技大学

batch314-batch317 继续复核剩余覆盖缺口。福建师范大学旧 URL 返回“无效的文章参数”；华东师范大学、东北师范大学页面只保留公告正文且不暴露人员级附件；北京林业大学页面指向查询系统且公开 PDF 为政审表模板；山东理工大学公告页未暴露真实名单附件；上海科技大学 2026 调剂拟录取页返回 HTTP 410。上述来源均留证不入库。

batch318 转向上海科技大学招生网仍公开的“原网站数据”历史拟录取页面。4 个官方 HTML 表格页可复现，专项清洗脚本去除表头并补入博士页，最终新增上海科技大学 2017/2018 年推免、硕士统考和硕博连读博士拟录取记录 792 条，需复核 0 条。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 257,703 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 257,703 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 263,408 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 263,408 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 587 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，383 所已精确匹配 |

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：114 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 588 行、Coverage 431 行、Public_Records 263,409 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch313 西华师范大学

batch313 继续围绕剩余覆盖缺口复核官网源。西华师范大学研究生院 2025 年硕士研究生拟录取名单第一批、第二批 PDF 附件可由官网页面公开 VSB `download.jsp` 链接复现；2025 年博士研究生拟录取名单以 HTML 表格公开。东北师范大学相关官网页本轮可抓取页面正文，但未解析出人员级表格或可直接下载附件，暂留证不入库。

本批按 TDD 新增专项清洗脚本，处理 PDF 中学院、专业、研究方向跨行拆列问题。硕士第一批 PDF 解析 1,979 条唯一考生编号，第二批 PDF 解析 2 条唯一考生编号；博士 HTML 表格解析 12 条人员记录。最终新增 1,993 条西华师范大学 2025 年拟录取记录，需复核 0 条。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 256,911 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 256,911 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 262,616 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 262,616 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 584 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，382 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch313_cwnu_admission`：2 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：112 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 585 行、Coverage 431 行、Public_Records 262,617 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch312 长春师范大学

batch312 继续围绕剩余缺口复核官网源。中国药科大学、中国医科大学、浙江中医药大学、桂林医科大学、南京理工大学、中国海洋大学等入口本轮均留证不入库，主要原因为 HTTP 410/412/405/404、下载桥或公示结束后附件不暴露。长春师范大学官网页面可抓取，且 VSB 附件可由项目爬虫跟进下载。

长春师范大学源 PDF 同时包含一志愿拟录取名单和未录取名单。专项清洗脚本从 PDF 文本层解析出 908 条状态记录，其中 `是否拟录取=是` 823 条、`否` 85 条；最终只保留 823 条拟录取记录，剔除全部未录取记录。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 254,918 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 254,918 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 260,623 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 260,623 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 583 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，381 所已精确匹配 |

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：110 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 584 行、Coverage 431 行、Public_Records 260,624 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch311 上海体育大学

batch311 继续从覆盖缺口中查找可复现官网源。成都体育学院、东北师范大学、上海体育大学 2026 年官网拟录取/推免页面可由搜索定位，但当前请求均被源站重定向到 `127.0.0.1:9`，未绕过、不入库。上海体育大学旧年度官方 PDF 直链可由搜索索引读取文本层；源文件发布时校名为“上海体育学院”，本批按覆盖底表归一为“上海体育大学”，并在备注中保留 `official_source_school_name: 上海体育学院`。

本批新增 23 条 2020 年博士研究生“申请-考核”制拟录取记录，字段包括报名号、姓名、报考专业、报考类别、外语/专业课/复试/综合成绩及备注。来源 PDF：`https://yjsc.sus.edu.cn/__local/C/9B/29/2E3E4C2B32BCCD234FFA36D4DE2_850177CB_4B537.pdf?e=.pdf`。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 254,095 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 254,095 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 259,800 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 259,800 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 582 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，380 所已精确匹配 |

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：109 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的状态字段排除词扫描命中 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 583 行、Coverage 431 行、Public_Records 259,801 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch304-batch310 缺口源复核

batch304-batch310 继续围绕剩余 51 所覆盖缺口尝试官网源。广东药科大学、太原科技大学、北京电影学院、重庆邮电大学、东北电力大学等搜索命中 URL 实时返回 404/412/502；中国医科大学、南京财经大学、沈阳化工大学等附件进入验证码下载桥；西北师范大学、成都体育学院页面返回 JS challenge/WAF；首都师范大学恢复出的 URL 跳转到学校首页，无名单正文。上述来源均留证不入库。

本轮没有新增可合并人员行，交付规模保持 batch303 后状态：B 类官网数据 254,072 条，A+B 总清洗包 259,777 条，覆盖追踪 430 所中 379 所已精确匹配。

## 2026-06-02 追加批次：batch303 华侨大学

batch303 继续筛选剩余覆盖缺口。华侨大学硕士统考拟录取公示搜索命中页面和同域虚拟附件直链实时返回 404，留证不入库；华侨大学研究生院“2026 年第二批次硕博连读和申请审核制博士研究生拟录取名单公示”页面实时可访问，正文内嵌 VSB PDF iframe，PDF 主文件可下载且文本层完整。本批新增专项清洗脚本，处理跨行专业名和跨行备注，入库 146 条博士拟录取记录。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 254,072 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 254,072 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 259,777 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 259,777 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 581 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，379 所已精确匹配 |

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 华侨大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 146 | 0 |

来源：
- 华侨大学 2026 年第二批次硕博连读和申请审核制博士研究生拟录取名单公示：https://grs.hqu.edu.cn/info/1176/18010.htm

验证：
- `python -m unittest tests.test_curate_batch303_hqu_doctoral_admission`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：108 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- 记录状态字段扫描：CHSI clean、B 类 master/public 与 A+B clean/public 均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿结构校验：Overview 15 行、Source_Summary 582 行、Coverage 431 行、Public_Records 259,778 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch300-batch302 河北中医药大学

batch300-batch302 继续筛选剩余覆盖缺口。大连海洋大学搜索命中的官方 PDF 线索实时 404 或连接失败；沈阳航空航天大学可定位到 2026 年推免拟录取官网页，但自动化请求失败且学校 WAF 返回 403；沈阳师范大学、中国海洋大学、北京第二外国语学院、齐鲁工业大学、华东师范大学等页面可访问但附件已随公示期结束移除或不暴露真实 href；长春师范大学、沈阳体育学院连接超时；北京服装学院当前可访问页不是最终名单；华中科技大学名单主体 SWF 下载返回 403。上述来源均留证不入库。

河北中医药大学研究生学院官网公开“2026 年拟录取推免生公示（第一批）”及同站 `.xls` 附件，本批用专项清洗脚本读取 legacy Excel，只保留状态以“待录取”开头的人员行，剔除 `未参加复试/放弃待录取通知/拒绝待录取通知/拒绝复试通知/已被其他院校录取` 等非录取状态，入库 16 条。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 253,926 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 253,926 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 259,631 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 259,631 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 580 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，378 所已精确匹配 |

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河北中医药大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 16 | 0 |

来源：
- 河北中医药大学 2026 年拟录取推免生公示（第一批）：https://yjsxy.hebcm.edu.cn/col/1628824153772/2025/09/26/1758884165127.html
- 官方 Excel 附件：https://yjsxy.hebcm.edu.cn/download.jsp?pathfile=/atm/7/20250926184432892.xls

验证：
- `python -m unittest tests.test_curate_batch302_hebcm_recommendation`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：107 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- 记录状态字段扫描：CHSI clean、B 类 master/public 与 A+B clean/public 均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿结构校验：Overview 15 行、Source_Summary 581 行、Coverage 431 行、Public_Records 259,632 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch272-batch299 云南中医药大学

batch272-batch299 继续筛选剩余覆盖缺口。多数命中属于公示结束后附件不再暴露、验证码下载桥、HTTP 410/412/404、JS challenge 或 WAF 页面，均留证不入库；天津职业技术师范大学页面和 PDF 可抓取，但原文为“复试名单”而非拟录取名单，未合并。云南中医药大学研究生处官网正文公开 2026 年硕博连读研究生选拔拟录取名单，本批入库 6 条人员级记录。

本批同时清理历史遗留非录取状态：从 B 类官网主表删除江西中医药大学 7 条备注含“未参加面试”的记录。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 253,910 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 253,910 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 259,615 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 259,615 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 579 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，377 所已精确匹配 |

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 云南中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 6 | 0 |

来源：
- 云南中医药大学 2026 年硕博连读研究生选拔拟录取名单公示：https://yjs.ynucm.edu.cn/info/1023/1163.htm

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：106 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- 记录状态字段扫描：CHSI clean、B 类 master/public 与 A+B clean/public 均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取` 残留。
- 工作簿结构校验：Overview 15 行、Source_Summary 580 行、Coverage 431 行、Public_Records 259,616 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch269-batch271 西湖大学

batch269-batch271 继续筛选剩余覆盖缺口。福建师范大学搜索命中的官方 PDF 直链实时返回空内容；北京协和医学院推免系统结果页实时切换为 2027 年空表，均留证不入库。西湖大学研究生招生通知公告页公开 2026 级博士生拟录取名单 PDF，本批入库 168 条，并通过专项清洗拆分申请号、姓名、脱敏证件号、学院、专业、面试成绩、学制和备注。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 253,911 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 253,911 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 259,616 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 259,616 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 578 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，376 所已精确匹配 |

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西湖大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 168 | 0 |

来源：
- 西湖大学 2026 级博士研究生拟录取名单公示（4月批次）：https://www.westlake.edu.cn/admissions/graduate/information/announcements/202605/t20260507_66370.html

验证：
- `python -m unittest tests.test_curate_batch270b_westlake_admission_pdf`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：106 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 579 行、Coverage 431 行、Public_Records 259,617 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch264-batch268c 吉首大学

batch264-batch268c 继续筛选剩余覆盖缺口。中国海洋大学页面不暴露真实附件且恢复出的 PDF 直链实时 404；中国政法大学页面返回 JS challenge；中国药科大学页面返回 410；重庆邮电大学详情页返回 412，均留证不入库。吉首大学研究生院博士拟录取公示页公开 3 个 PNG 附件，本批按图片表格逐行转写入库 37 条，只保留明确拟录取人员。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 253,743 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 253,743 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 259,448 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 259,448 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 577 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，375 所已精确匹配 |

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 吉首大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 37 | 0 |

来源：
- 吉首大学 2026 年拟录取博士研究生情况公示：https://yjsc.jsu.edu.cn/zsgz/bszs/ddb92781965243fa91dbebdd2af3babc.htm

验证：
- `python -m unittest tests.test_curate_batch263_jhun_admission tests.test_curate_batch268c_jsu_doctor_pngs`：2 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：105 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 578 行、Coverage 431 行、Public_Records 259,449 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch263 江汉大学

batch263 从江汉大学研究生院官网补入 2026 年硕士研究生招生拟录取名单 1,050 条、2026 年博士研究生招生拟录取名单 38 条。两份来源页面均可访问并暴露同站 PDF 直链；通用解析未完整覆盖硕士 PDF 的跨行学院字段，因此新增专项清洗脚本按 PDF 文本层重建记录。搜索命中的江汉大学推免旧页实时返回“无效的文章参数！(02)”，未入库。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 253,706 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 253,706 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 259,411 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 259,411 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 576 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，374 所已精确匹配 |

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 江汉大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,050 | 2 |
| 江汉大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 38 | 0 |

来源：
- 江汉大学 2026 年硕士研究生招生拟录取名单公示页：https://gs.jhun.edu.cn/7b/98/c1956a228248/page.htm
- 江汉大学 2026 年博士研究生招生拟录取名单公示页：https://gs.jhun.edu.cn/7e/e6/c1956a229094/page.htm

验证：
- `python -m unittest tests.test_curate_batch263_jhun_admission`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：104 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 577 行、Coverage 431 行、Public_Records 259,412 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch260-batch262 辽宁石油化工大学、辽宁科技大学、华北理工大学

batch260 从辽宁石油化工大学研究生院公网公告页及同站嵌入 PDF 补入 2026 年接收推免待录取考生 7 条；batch261 从辽宁科技大学官方 PDF 补入 2026 年博士研究生拟录取考生 69 条；batch262 从华北理工大学官方页面和 PDF 补入 2026 年接收推免研究生拟录取 16 条。华北理工大学源名单同时列出缺考、拒绝待录取、因差额未录取和被其他学校待录取人员，清洗时只保留状态为“拟录取”的行；辽宁科技大学源 PDF 的重复表头和错位行已通过专项清洗脚本剔除。

本轮还同步清理历史主表中的明确非录取状态记录：B 类 292 条（缺考 186、候补 70、不合格 36），CHSI 5 条（缺考 2、不合格 3）。清理依据记录字段中的状态词，不按来源标题中的“候补资格名单”等字样删除记录。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 252,618 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 252,618 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 258,323 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 258,323 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 575 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，373 所已精确匹配 |

## 2026-06-01 追加批次：batch257-batch258 河北农业大学、陆军军医大学

batch257 从河北农业大学研究生学院官网直链 PDF 补入 2026 级硕博连读研究生拟录取名单 42 条；batch258 从陆军军医大学招生就业网公网公告和两个同站 PDF 补入 2026 年接收推荐免试硕士研究生拟录取名单 38 条。陆军军医大学源 PDF 只有姓名、性别和出生年月，清洗包只保留姓名、计划类型和性别，未把出生年月写入公开备注；因缺少学号、学院和专业，38 条均标记 `needs_review=true`。

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 252,818 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 252,818 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 258,528 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 258,528 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 572 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，370 所已精确匹配 |

## 2026-05-28 追加批次：batch241-batch242 西安电子科技大学、青岛理工大学

batch241 从西安电子科技大学数学与统计学院官网直链 PDF 补入 2025 年硕士研究生一志愿和统计学调剂拟录取名单 62 条；batch242 从青岛理工大学研究生院整校 PDF 补入 2025 年度硕士研究生拟录取名单 1,509 条。两批均新增专项清洗脚本和测试，保留官方 source_url。

本轮同时修复汇总逻辑：CSV 中的 `"False"` 不再被误计为 `needs_review_count`。交付包已按修复后的汇总逻辑重建。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西安电子科技大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 62 | 0 |
| 青岛理工大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,509 | 0 |

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 245,469 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 245,469 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 251,179 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 251,179 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 557 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，355 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch241_xidian_math_admission tests.test_curate_batch242_qut_admission_pdf`：2 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：86 个测试通过。
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：Overview 15 行、Source_Summary 558 行、Coverage 431 行、Public_Records 251,180 行，公式单元格 0，错误单元格 0。

## 2026-05-29 追加批次：batch243 塔里木大学

batch243 从塔里木大学研究生处官网补入 2026 年硕士研究生招生第一批次一志愿考生复试成绩及录取结果 PDF。通用解析得到 439 条候选记录，但其中包含分页表头和“是否录取=否”的行；新增专项清洗脚本与测试后，仅保留最终录取标记为“是”的人员记录 371 条。同步抓取的“硕士研究生拟录取结果公示”PDF 为说明正文，不含人员名单，本轮只作为原始证据留存。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 塔里木大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 371 | 0 |

可追溯来源：
- 塔里木大学 2026 年硕士研究生招生第一批次一志愿考生复试成绩及录取结果公示 PDF：`https://yjsb.taru.edu.cn/__local/3/9F/D4/8F60D02C5578C92BD23BF082ADE_9B5FB6D3_40612.pdf`
- 塔里木大学 2026 年硕士研究生拟录取结果公示说明 PDF：`https://yjsb.taru.edu.cn/__local/3/26/BC/AF946E085A4885689C22411A2E0_7B43EA37_B9F2.pdf`

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 245,840 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 245,840 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 251,550 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 251,550 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 558 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，356 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch243_taru_admission`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：87 个测试通过。
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：Overview 15 行、Source_Summary 559 行、Coverage 431 行、Public_Records 251,551 行，公式单元格 0，错误单元格 0。

## 2026-06-01 追加批次：batch244 三峡大学

batch244 从三峡大学健康医学院官网补入 2026 年硕士研究生拟录取考生名单公示第一批和调剂复试拟录取考生名单公示第二批。两份官网内嵌 PDF 均可直接下载；通用解析候选记录存在姓名/考生编号错位和专业代码误入姓名的问题，新增专项清洗脚本与测试后，保留 102 条人员级记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 三峡大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 102 | 0 |

可追溯来源：
- 健康医学院 2026 年硕士研究生拟录取考生名单公示第一批 PDF：`https://jkyxy.ctgu.edu.cn/__local/B/F3/04/645C9F3068D17EA0D7B220A9E0C_BF8D961B_167C5.pdf`
- 健康医学院 2026 年硕士研究生调剂复试拟录取考生名单公示第二批 PDF：`https://jkyxy.ctgu.edu.cn/__local/4/7E/9D/5B34B462C4AACEDB21A986B4802_07C184C4_C3F9.pdf`

更新后的交付规模：

| 文件 | 行数 |
| --- | ---: |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv` | 245,942 |
| `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv` | 245,942 |
| `data/cleaned/graduate_outcomes/master_records_clean.csv` | 251,652 |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | 251,652 |
| `data/cleaned/graduate_outcomes/school_year_source_summary.csv` | 559 |
| `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv` | 430 所，357 所已精确匹配 |

验证：
- `python -m unittest tests.test_curate_batch244_ctgu_health_admission`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：88 个测试通过。
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：Overview 15 行、Source_Summary 560 行、Coverage 431 行、Public_Records 251,653 行，公式单元格 0，错误单元格 0。

## 2026-05-28 追加批次：batch226 四川美术学院官网 PDF 名单入库

batch226 从剩余缺口中补入四川美术学院 2026 年硕士研究生一志愿拟录取、调剂拟录取和接收推免生拟录取名单。此前 batch225 抓取了大连外国语大学和南京财经大学官网公示页，但附件均为验证码下载桥，自动化请求只取得验证码 HTML，本轮不绕过验证码、不入库。

四川美术学院通用解析得到 159 条，但大量为表头、学院名和分数字段错位。本批按 TDD 新增 `scripts/curate_batch226_scfai.py` 和 `tests/test_curate_batch226_scfai.py`，用 `pdftotext -raw` 重解 3 个官方 PDF 表格，最终保留 590 条人员级记录，其中一志愿 505 条、调剂 3 条、推免 82 条。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 四川美术学院 | 2026 | postgraduate_admission_list / recommendation_exemption_list | postgraduate_exam_or_admission / recommendation_exemption | 590 | 0 |

可追溯来源：
- 四川美术学院 2026 年硕士研究生招生拟录取名单（第一志愿）公示：`https://www.scfai.edu.cn/zsb/info/1001/4386.htm`
- 四川美术学院 2026 年硕士研究生招生调剂复试成绩查询及拟录取名单公示：`https://www.scfai.edu.cn/zsb/info/1001/4436.htm`
- 四川美术学院 2026 年接收推荐免试攻读硕士学位研究生拟录取名单公示：`https://www.scfai.edu.cn/zsb/info/1001/4106.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch225_dlufl_nufe.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch225_dlufl_nufe/`
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch226_scfai.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch226_scfai/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch226_scfai/`
- `scripts/curate_batch226_scfai.py`
- `tests/test_curate_batch226_scfai.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch226_scfai_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 233,673 条；A+B 统一清洗包为 239,383 条；覆盖追踪 430 所院校中已有 341 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 239,384 行（含表头），Source_Summary 541 行（含表头），Coverage 431 行（含表头），公式单元格 0，公式错误 0。通用爬虫测试 238 个通过，批次专项清洗器测试 72 个通过；本批清洗记录 590 条，空姓名 0，空考生编号 0，空录取专业 0，需复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch224 中国石油大学（华东）硕士拟录取扫描 PDF 入库

batch224 从剩余缺口中补入中国石油大学（华东）2026 年硕士研究生拟录取名单。来源为研究生招生网公示页及官方 PDF 附件；同期复核的中国海洋大学搜索直链 PDF 返回 404，本轮不入库。

通用爬虫抓取页面和 PDF 后未抽出人员记录，因为 PDF 是 31 页扫描图像。按 TDD 新增 `scripts/curate_batch224_upc_admission.py` 和 `tests/test_curate_batch224_upc_admission.py`，用 `pdftoppm` 渲染、`RapidOCR` 识别，并结合表格横线重建单元格行，处理跨栏、跨页和跨行姓名/学院/专业。质检中人工校正 5 个 OCR 漏字姓名单元格和 3 个长专业标题。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中国石油大学（华东） | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,463 | 0 |

可追溯来源：
- 中国石油大学（华东）2026 年硕士研究生拟录取名单公示：`https://yz.upc.edu.cn/2026/0513/c10708a490438/page.htm`
- 官方 PDF 附件：`https://yz.upc.edu.cn/_upload/article/files/0c/d5/e987be3444428e06eb7652dac2ed/17989726-14ad-4441-bb76-17ff5ffe0695.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch224_upc_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch224_upc_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch224_upc_admission/`
- `scripts/curate_batch224_upc_admission.py`
- `tests/test_curate_batch224_upc_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch224_upc_admission_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 233,083 条；A+B 统一清洗包为 238,793 条；覆盖追踪 430 所院校中已有 340 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 238,794 行（含表头），Source_Summary 539 行（含表头），Coverage 431 行（含表头），公式单元格 0，公式错误 0。通用爬虫测试 238 个通过，批次专项清洗器测试 71 个通过；本批清洗记录 2,463 条，空姓名 0，空考生编号 0，空学院 0，空专业 0，需复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch223 中央民族大学博士拟录取名单入库

batch223 从剩余缺口中补入中央民族大学 2026 年博士研究生拟录取名单。来源为中央民族大学研究生招生网 3 个校级公示页：2026 年“申请-考核制”学术学位博士、专业学位博士和第二批博士拟录取名单。同期复核的中国政法大学 2026 年推免拟录取公示页返回浏览器挑战脚本，自动化请求无法取得真实正文，本轮不绕过挑战、不入库。

通用爬虫 3 个种子抓取 23 个文档，原始结构化 159 条；其中 14 个老式 `.xls` 附件被站点下载成无扩展名 OLE `.bin`，通用爬虫无法按 Excel 文件解析。本批按 TDD 新增 `scripts/curate_batch223_muc_doctoral_admission.py` 和 `tests/test_curate_batch223_muc_doctoral_admission.py`，用 `xlrd` 读取 legacy xls/bin，用 `openpyxl` 读取 xlsx，按“姓名、报名号、报考院系、报考专业、研究方向、专项计划、报考类别、拟录取意见”抽取人员记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中央民族大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 540 | 0 |

可追溯来源：
- 中央民族大学 2026 年“申请-考核制”学术学位博士研究生拟录取名单公示：`https://grs.muc.edu.cn/yjsyzsw/info/1069/5819.htm`
- 中央民族大学 2026 年“申请-考核制”专业学位博士研究生拟录取名单公示：`https://grs.muc.edu.cn/yjsyzsw/info/1069/5849.htm`
- 中央民族大学 2026 年博士研究生拟录取名单公示（第二批）：`https://grs.muc.edu.cn/yjsyzsw/info/1069/5869.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch223_muc_doctoral_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch223_muc_doctoral_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch223_muc_doctoral_admission/`
- `scripts/curate_batch223_muc_doctoral_admission.py`
- `tests/test_curate_batch223_muc_doctoral_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch223_muc_doctoral_admission_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 230,620 条；A+B 统一清洗包为 236,330 条；覆盖追踪 430 所院校中已有 339 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 236,331 行（含表头），公式单元格 0，公式错误 0。通用爬虫测试 238 个通过，批次专项清洗器测试 70 个通过；本批清洗记录 540 条，空姓名 0，空报名号 0，需复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch222 北方民族/西北民族官网拟录取名单入库

batch222 从剩余缺口中补入 2 所院校的官网可结构化名单：北方民族大学 2026 年硕士研究生招生拟录取名单、北方民族大学 2026 年博士研究生“申请-考核”拟录取名单，以及西北民族大学 2026 年一志愿硕士拟录取公示页下的普通计划、少干计划、退役士兵专项 3 个 PDF 附件。

通用爬虫 3 个种子抓取 6 个文档，原始结构化 1,511 条，通用清洗 1,332 条。质检发现西北民族大学 PDF 通用解析发生列错位，会把专业名误填入 `person_name`、把方向码 `00` 误填入 `student_id`；同时 PDF 官方文本实际为普通计划 433 人、少干计划 47 人、退役士兵专项 10 人。本批按 TDD 新增 `scripts/curate_batch222_minzu_universities.py` 和 `tests/test_curate_batch222_minzu_universities.py`，保留北方民族大学通用清洗中的正确记录，并用 `pdftotext -raw` 重解西北民族大学 PDF。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 北方民族大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,025 | 0 |
| 西北民族大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 490 | 0 |

可追溯来源：
- 北方民族大学 2026 年硕士研究生招生拟录取名单公示：`https://yjsc.nmu.edu.cn/info/1086/2384.htm`
- 北方民族大学 2026 年博士研究生“申请-考核”拟录取名单公示（一）：`https://yjsc.nmu.edu.cn/info/1086/2386.htm`
- 西北民族大学 2026 年全国硕士研究生招生一志愿拟录取考生名单公示：`https://www.xbmu.edu.cn/yz/info/1351/3771.htm`
- 西北民族大学普通计划含照顾政策 PDF：`https://www.xbmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1867476930&wbfileid=49CB0FDB0E003E86DC589CB2AEB17C43`
- 西北民族大学少数民族高层次骨干人才计划 PDF：`https://www.xbmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1867476930&wbfileid=BE44F92838B97297D30483C9712CE660`
- 西北民族大学退役大学生士兵专项计划 PDF：`https://www.xbmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1867476930&wbfileid=EC3EF7210D4C7FC587258D47929B0A7A`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch222_minzu_universities.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities/`
- `scripts/curate_batch222_minzu_universities.py`
- `tests/test_curate_batch222_minzu_universities.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 230,080 条；A+B 统一清洗包为 235,790 条；覆盖追踪 430 所院校中已有 338 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 235,791 行（含表头），公式单元格 0，公式错误 0。通用爬虫测试 238 个通过，批次专项清洗器测试 69 个通过；本批清洗记录 1,515 条，空姓名 0，需复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch221 华东政法/河南财经政法/湖北中医药官网名单入库

batch221 从剩余缺口中补入 3 所院校的官网可结构化名单：华东政法大学 2025 年推免生拟录取 PDF、河南财经政法大学 2025 年推免生拟录取 HTML 表格、湖北中医药大学 2026 年博士补录拟录取 HTML 正文。同期复核的华东政法大学 2025 年统考硕士拟录取 PDF 搜索直链实时返回 HTTP 404，未入库。

通用爬虫 4 个种子中抓取 3 个文档，原始结构化 889 条；其中华东政法 PDF 受水印影响被通用解析膨胀为 888 条噪声记录，湖北中医药正文因无表格通用解析为 0 条。本批按 TDD 新增 `scripts/curate_batch221_ecupl_huel_hbucm.py` 和 `tests/test_curate_batch221_ecupl_huel_hbucm.py`，用 `pdftotext -raw` 重组华东政法 PDF，并用 HTML 表格/正文正则补齐另外两校记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 华东政法大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 349 | 0 |
| 河南财经政法大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 1 | 0 |
| 湖北中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1 | 0 |

可追溯来源：
- 华东政法大学 2025 年硕士研究生推免生拟录取名单 PDF：`https://gs.ecupl.edu.cn/_upload/article/files/26/cb/dcd083e548c78ce11fb84064ffca/60fc7d5b-7999-4ce4-8f70-00931a2ade78.pdf`
- 河南财经政法大学 2025 年推免生拟录取名单公示：`https://yjs.huel.edu.cn/info/1007/4302.htm`
- 湖北中医药大学 2026 年博士研究生补录名单公示：`https://yjs.hbucm.edu.cn/info/1029/11261.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch221_ecupl_huel_hbucm.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm/graduate_outcome_failures.jsonl`
- `scripts/curate_batch221_ecupl_huel_hbucm.py`
- `tests/test_curate_batch221_ecupl_huel_hbucm.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 228,565 条；A+B 统一清洗包为 234,275 条；覆盖追踪 430 所院校中已有 336 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 234,276 行（含表头），公式单元格 0，公式错误 0。相关单测 306 个通过；本批清洗记录 351 条，空姓名 0，需复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0，PDF 水印碎片残留 0。

## 2026-05-28 追加批次：batch220 浙江农林大学博士补录拟录取 HTML 入库

batch220 从剩余缺口中定位到浙江农林大学研究生招生信息网 2026 年博士研究生拟录取名单补录公示。两条详情页均为官网 HTML 表格，每页 1 条补录记录，可直接结构化。同期复核的广东药科大学旧线索返回 404，中国石油大学（华东）候选页返回模板参数错误，北京林业大学研招站连接失败，均未入库。

通用解析能得到 2 条人员记录，但遗漏考生编号、研究方向、综合考核成绩和招生方式。本批按 TDD 新增 `scripts/curate_batch220_zafu_doctoral_supplement.py` 和 `tests/test_curate_batch220_zafu_doctoral_supplement.py`，从 HTML 表格补齐字段后输出 curated 记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 浙江农林大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2 | 0 |

可追溯来源：
- 浙江农林大学博士补录拟录取公示页 1：`https://yjszs.zafu.edu.cn/info/1109/3307.htm`
- 浙江农林大学博士补录拟录取公示页 2：`https://yjszs.zafu.edu.cn/info/1109/3304.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch220_zafu_doctoral_supplement.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch220_zafu_doctoral_supplement/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch220_zafu_doctoral_supplement/`
- `scripts/curate_batch220_zafu_doctoral_supplement.py`
- `tests/test_curate_batch220_zafu_doctoral_supplement.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch220_zafu_doctoral_supplement_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 228,214 条；A+B 统一清洗包为 233,924 条；覆盖追踪 430 所院校中已有 333 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 233,925 行（含表头），公式单元格 0，公式错误 0。相关单测 305 个通过；本批清洗记录 2 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch219 五邑大学硕士拟录取 PDF 入库

batch219 继续从剩余缺口中筛选官网直链 PDF。五邑大学 2026 年硕士研究生拟录取名单 PDF 位于学校官网 `__local` 静态文件路径，可直接下载并含可抽取文本层。同期检索到的桂林医科大学若干名单线索在实时请求中返回 404/403，未入库。

通用解析从五邑大学 PDF 形成 532 条原始记录，通用清洗后保留 510 条人员级记录，剔除的是 21 条表头“姓名”和 1 条错位院系行。本批记录包含姓名、拟录取学院、拟录取专业代码/名称和成绩备注；原文未公开考生编号，因此 `student_id` 为空，但全部 `needs_review=false`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 五邑大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 510 | 0 |

可追溯来源：
- 五邑大学 2026 年硕士研究生拟录取名单 PDF：`https://www.wyu.edu.cn/__local/E/44/D7/4FF5E163C6926F40AF45273AA25_A76E9BBA_44C67.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch219_wyu_postgraduate_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch219_wyu_postgraduate_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch219_wyu_postgraduate_admission/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch219_wyu_postgraduate_admission/graduate_outcome_failures.jsonl`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch219_wyu_postgraduate_admission/records_clean.csv`

本批合并后，B 类官网主表为 228,212 条；A+B 统一清洗包为 233,922 条；覆盖追踪 430 所院校中已有 332 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 233,923 行（含表头），公式单元格 0，公式错误 0。相关单测 304 个通过；本批清洗记录 510 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch218 河南科技大学硕士统考拟录取 PDF 入库

batch218 从剩余缺口中定位到河南科技大学研究生院 2026 年硕士研究生统考拟录取名单公示。页面为静态官网公告，正文通过 `showVsbpdfIframe` 嵌入官方 PDF，PDF 可直接下载并含可抽取文本层。

通用解析直接形成 2,293 条人员级记录，字段包含考生编号、姓名、录取学院、录取专业、学习方式、初试成绩、复试成绩和总成绩。经通用清洗后全部 `needs_review=false`，本批未新增专项解析代码。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河南科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,293 | 0 |

可追溯来源：
- 河南科技大学 2026 年硕士研究生统考拟录取名单公示页：`https://yjsc.haust.edu.cn/info/1053/8412.htm`
- 河南科技大学名单 PDF：`https://yjsc.haust.edu.cn/__local/8/24/42/1544F2FDBF67B9245E0CA068056_C16A785F_2B8C28.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch218_haust_postgraduate_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch218_haust_postgraduate_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch218_haust_postgraduate_admission/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch218_haust_postgraduate_admission/graduate_outcome_failures.jsonl`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch218_haust_postgraduate_admission/records_clean.csv`

本批合并后，B 类官网主表为 227,702 条；A+B 统一清洗包为 233,412 条；覆盖追踪 430 所院校中已有 331 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 233,413 行（含表头），公式单元格 0，公式错误 0。相关单测 304 个通过；本批清洗记录 2,293 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch217 山东艺术学院美术学院推免资格 PDF 入库

batch217 继续从艺术类院校缺口中查找官网推免名单。山东艺术学院美术学院 2026 年推荐免试攻读硕士研究生资格名单页面可访问，附件 PDF 可直接下载且含文本层；戏剧学院名单页为图片正文，艺术管理学院名单页包含扫描 PDF，均已留存原始证据但未强行转写入库。

通用解析从美术学院 PDF 形成 17 条原始记录，其中 2 条为表头/折行噪声。本批新增 `scripts/curate_batch217_sdca_art_colleges.py` 和 `tests/test_curate_batch217_sdca_art_colleges.py`，按 PDF 文本中的 9 位学号行重建记录，补齐性别、政治面貌、本科专业代码、专业组和推荐状态，最终保留 15 条，全部 `needs_review=false`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山东艺术学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 15 | 0 |

可追溯来源：
- 山东艺术学院美术学院名单公示页：`https://msxy.sdca.edu.cn/info/1031/5793.htm`
- 山东艺术学院美术学院名单 PDF：`https://msxy.sdca.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1302396566&wbfileid=1B0D6EB37D9B0E7C74800362ACADB78F`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch217_sdca_art_colleges.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch217_sdca_art_colleges/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch217_sdca_art_colleges/graduate_outcome_failures.jsonl`
- `scripts/curate_batch217_sdca_art_colleges.py`
- `tests/test_curate_batch217_sdca_art_colleges.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch217_sdca_art_colleges_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 225,409 条；A+B 统一清洗包为 231,119 条；覆盖追踪 430 所院校中已有 330 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 231,120 行（含表头），公式单元格 0，公式错误 0。相关单测 304 个通过；本批清洗记录 15 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch216 西安工业大学校级推免拟推荐名单入库

batch216 从剩余缺口中定位到西安工业大学研究生院校级 2026 年推荐优秀应届本科毕业生免试攻读研究生拟推荐人员名单。页面为静态 HTML 表格，字段包含序号、学号、学生姓名、学院、本科专业代码和本科专业名称，可直接结构化。

通用解析已形成 230 条记录，但因只保留了专业代码且全部标记 `needs_review=true`。本批新增 `scripts/curate_batch216_xatu_recommendation.py` 和 `tests/test_curate_batch216_xatu_recommendation.py`，按表格重建记录，补齐本科专业名称、序号和推荐状态，最终保留 230 条，全部 `needs_review=false`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西安工业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 230 | 0 |

可追溯来源：
- 西安工业大学 2026 年推荐优秀应届本科毕业生免试攻读研究生名单公示：`https://grs.xatu.edu.cn/info/1024/4652.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch216_xatu_recommendation.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch216_xatu_recommendation/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch216_xatu_recommendation/graduate_outcome_failures.jsonl`
- `scripts/curate_batch216_xatu_recommendation.py`
- `tests/test_curate_batch216_xatu_recommendation.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch216_xatu_recommendation_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 225,394 条；A+B 统一清洗包为 231,104 条；覆盖追踪 430 所院校中已有 329 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 231,105 行（含表头），公式单元格 0，公式错误 0。相关单测 303 个通过；本批清洗记录 230 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch213 武汉理工大学交通与物流学院推免拟录取 PDF 入库

batch213 继续从剩余缺口中筛选重点高校官网源。武汉理工大学交通与物流工程学院 2026 年接收推荐免试攻读硕士学位和直接攻读博士学位研究生拟录取名单 PDF 可直接下载并含文本层；东北师范大学页面可访问但名单跳转到查询系统后实时返回“录取名单尚未公布”；北京协和医学院公示页给出的查询系统当前显示 2027 年空表；中国政法大学页面返回 JavaScript challenge 页，均留证不入库。

通用解析从武汉理工大学 PDF 形成 89 条记录，但因附件 URL 中日期为 202512，年份被误判为 2025，且文档类型需归入接收推免拟录取。本批新增 `scripts/curate_batch213_more_remaining_major_universities.py` 和 `tests/test_curate_batch213_more_remaining_major_universities.py`，按 PDF 文本行重建记录，将年份修正为 2026，文档类型修正为 `incoming_recommendation_admission_list`，最终保留 89 条，全部 `needs_review=false`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 武汉理工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 89 | 0 |

可追溯来源：
- 武汉理工大学交通与物流工程学院拟录取名单公示页：`https://stle.whut.edu.cn/yjsjx/zsxx/202512/t20251223_1375280.shtml`
- 武汉理工大学名单 PDF：`https://stle.whut.edu.cn/yjsjx/zsxx/202512/P020251223575245846523.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch213_more_remaining_major_universities.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch213_more_remaining_major_universities/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch213_more_remaining_major_universities/graduate_outcome_failures.jsonl`
- `scripts/curate_batch213_more_remaining_major_universities.py`
- `tests/test_curate_batch213_more_remaining_major_universities.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch213_more_remaining_major_universities_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 225,164 条；A+B 统一清洗包为 230,874 条；覆盖追踪 430 所院校中已有 328 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 230,875 行（含表头），公式单元格 0，公式错误 0。相关单测 302 个通过；本批清洗记录 89 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch212 石家庄铁道大学一志愿拟录取 PDF 入库

batch212 继续从剩余缺口中筛选医学、天津和华北院校官网源。石家庄铁道大学研究生学院一志愿复试成绩和拟录取名单 PDF 可直接下载并含文本层；山西中医药大学附件进入验证码下载桥页；天津科技大学外国语学院页面陷入自跳转 302 循环；云南中医药大学和天津职业技术师范大学入口实时返回 404，均留证不入库。

通用解析从石家庄铁道大学 PDF 形成 1,207 条记录，但其中混入表头碎片、空白录取状态行、`缺考` 和 `复试不合格` 行。本批新增 `scripts/curate_batch212_more_remaining_medical_tianjin_pages.py` 和 `tests/test_curate_batch212_more_remaining_medical_tianjin_pages.py`，按 PDF 文本行重新解析，只保留录取状态明确为 `拟录取` 的考生，最终保留 1,016 条，全部 `needs_review=false`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 石家庄铁道大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,016 | 0 |

可追溯来源：
- 石家庄铁道大学 2026 年硕士研究生复试成绩和拟录取名单公告（第一志愿）：`https://yjs.stdu.edu.cn/enrollment/masters-degree-admission/3747-202604020003`
- 石家庄铁道大学名单 PDF：`https://yjs.stdu.edu.cn/sitedata/yjs/files/zhaosheng/2026/2shuoshi/fushi/石家庄铁道大学2026年硕士研究生第一志愿复试成绩和拟录取名单第一批正式稿2.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch212_more_remaining_medical_tianjin_pages.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch212_more_remaining_medical_tianjin_pages/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch212_more_remaining_medical_tianjin_pages/graduate_outcome_failures.jsonl`
- `scripts/curate_batch212_more_remaining_medical_tianjin_pages.py`
- `tests/test_curate_batch212_more_remaining_medical_tianjin_pages.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch212_more_remaining_medical_tianjin_pages_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 225,075 条；A+B 统一清洗包为 230,785 条；覆盖追踪 430 所院校中已有 327 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 230,786 行（含表头），公式单元格 0，公式错误 0。相关单测 301 个通过；本批清洗记录 1,016 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。

## 2026-05-28 追加批次：batch211 同济大学口腔医学院官网名单入库

batch211 继续从剩余缺口中筛选可实时复现的官网源。南京财经大学官网页可访问但 PDF 附件进入验证码下载桥页；西安电子科技大学页面只保留“公示期已过”文字且无静态名单；浙江农林大学入口实时返回 404，上海科技大学和中国药科大学入口返回 410。最终可入库来源为同济大学口腔医学院 2026 届本科生推荐免试研究生结果公示 HTML 表格。

通用解析已识别 34 个人名，但未保留“推免资格类型/复试总分/录取情况”等字段。本批新增 `scripts/curate_batch211_more_remaining_promising_pages.py` 和 `tests/test_curate_batch211_more_remaining_promising_pages.py`，按 HTML 表格重组记录，将 `学硕/专硕`、复试总分、`拟录取` 状态和退伍军人备注写入 `remarks`，最终保留 34 条，全部 `needs_review=false`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 同济大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 34 | 0 |

可追溯来源：
- 同济大学口腔医学院 2026 届本科生推荐免试研究生结果公示：`https://dent.tongji.edu.cn/info/1191/11811.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch211_more_remaining_promising_pages.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch211_more_remaining_promising_pages/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch211_more_remaining_promising_pages/graduate_outcome_failures.jsonl`
- `scripts/curate_batch211_more_remaining_promising_pages.py`
- `tests/test_curate_batch211_more_remaining_promising_pages.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch211_more_remaining_promising_pages_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 224,059 条；A+B 统一清洗包为 229,769 条；覆盖追踪 430 所院校中已有 326 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 229,770 行（含表头），公式单元格 0，公式错误 0。相关单测 300 个通过；本批清洗记录 34 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/候补` 残留 0。

## 2026-05-28 追加批次：batch210 贵师大/长春中医/内蒙古农大官网名单入库

batch210 继续从剩余覆盖缺口中筛选可实时复现的官网名单页。贵州师范大学教务处 XLSX 附件可直接下载；长春中医药大学研究生院页面内嵌 PDF 可直接下载；内蒙古农业大学动物科学学院名单嵌在官网 JPEG 图片中，已下载官方图片并逐行转写核对。云南民族大学实时返回 HTTP 521，甘肃农业大学种子页返回 404，沈阳化工大学附件进入验证码下载桥页，河北农业大学当前栏目命中硕博连读/硕士非推免页面，均留证不入库。

通用爬虫原始形成 566 条记录，但贵州师范大学附件中只有 Sheet1 的 209 行 `拟推荐` 可入库，19 行 `候补` 与两个无推荐状态的附加 sheet 不并入；长春中医药大学 PDF 末尾直博生方向跨行导致通用解析出现 3 条错位姓名。本批新增 `scripts/curate_batch210_remaining_promising_pages.py` 和 `tests/test_curate_batch210_remaining_promising_pages.py`，最终保留 301 条高可信记录，全部 `needs_review=false`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 贵州师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 209 | 0 |
| 长春中医药大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 70 | 0 |
| 内蒙古农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 22 | 0 |

可追溯来源：
- 贵州师范大学关于 2026 年推荐优秀应届本科毕业生免试攻读研究生拟推名单公示：`https://jwc.gznu.edu.cn/info/2002/89615.htm`
- 贵州师范大学 2026 年推免生拟推荐名单 XLSX：`https://jwc.gznu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=846466970&wbfileid=1F65483464235CA6EC033608A96BEADF`
- 长春中医药大学 2026 年接收推免生拟录取公示：`https://y.ccucm.edu.cn/info/1205/18311.htm`
- 长春中医药大学嵌入 PDF：`https://y.ccucm.edu.cn/__local/4/A7/4A/9631AD6B7EA1C063F1269E068CD_CA2DF7C2_21F1A.pdf`
- 内蒙古农业大学动物科学学院 2026 届推荐优秀应届本科毕业生免试攻读硕士学位研究生名单公示：`https://dky.imau.edu.cn/info/1052/37701.htm`
- 内蒙古农业大学名单 JPEG：`https://dky.imau.edu.cn/__local/D/CF/0A/3FE4079D006971F76427BC83DF8_9B89890E_26D68.jpeg`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch210_remaining_promising_pages.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch210_remaining_promising_pages/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch210_remaining_promising_pages/graduate_outcome_failures.jsonl`
- `scripts/curate_batch210_remaining_promising_pages.py`
- `tests/test_curate_batch210_remaining_promising_pages.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch210_remaining_promising_pages_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 224,025 条；A+B 统一清洗包为 229,735 条；覆盖追踪 430 所院校中已有 325 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 229,736 行（含表头），公式单元格 0，公式错误 0。相关单测 299 个通过；本批清洗记录 301 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/候补` 残留 0。

## 2026-05-27 追加批次：batch209 黑龙江/重庆/武汉官网名单入库

batch209 从剩余覆盖缺口中继续筛选可实时复现的官网名单页和直链 PDF。黑龙江大学 2026 年硕士研究生拟录取公示页可展开官方 PDF 附件；重庆师范大学教务处 PDF 直链可下载，包含普通类、农村硕士计划和研究生支教团三个推免公示名单；武汉纺织大学服装学院、武汉体育学院竞技体育学院 HTML 表格可直接解析。山东理工大学页面可访问但未暴露静态名单附件，天津科技大学外国语学院页面实时返回 302，均留证不入库。

通用爬虫原始形成 157 条记录，但黑龙江大学 PDF 大表错位且漏掉部分推免行，武汉纺织大学候补表混入记录，武汉体育学院自动跟进实施细则页产生赛事评分表噪声。本批新增 `scripts/curate_batch209_remaining_promising_pages.py` 和 `tests/test_curate_batch209_remaining_promising_pages.py`，按 PDF/HTML 表结构重新清洗：黑龙江大学只保留 `免试/推免生` 行；重庆师范大学按三个名单段分别标注 `普通类`、`农村硕士计划`、`研究生支教团`；武汉纺织大学只保留正式推荐表、剔除候补排名表；武汉体育学院只保留拟推荐名单页、剔除实施细则页。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 黑龙江大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 219 | 0 |
| 重庆师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 313 | 0 |
| 武汉纺织大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 7 | 0 |
| 武汉体育学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 8 | 0 |

可追溯来源：
- 黑龙江大学 2026 年硕士研究生拟录取公示页：`https://yjsy.hlju.edu.cn/info/1009/10185.htm`
- 黑龙江大学 2026 年硕士研究生拟录取公示 PDF：`https://yjsy.hlju.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1784155087&wbfileid=16028760`
- 重庆师范大学推荐 2026 届优秀本科毕业生免试攻读硕士学位研究生名单公示 PDF：`https://jwc.cqnu.edu.cn/__local/B/F6/4A/74BE256853C47E3593F9E096CEF_C5029819_BF71A.pdf`
- 武汉纺织大学服装学院拟推荐 2026 届毕业生免试攻读硕士研究生名单公示：`https://fashion.wtu.edu.cn/info/1006/14611.htm`
- 武汉体育学院竞技体育学院 2026 届优秀应届本科生毕业生免试攻读硕士学位研究生拟推荐名单公示：`https://jtxy.whsu.edu.cn/info/1327/8401.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch209_remaining_promising_pages.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages/graduate_outcome_failures.jsonl`
- `scripts/curate_batch209_remaining_promising_pages.py`
- `tests/test_curate_batch209_remaining_promising_pages.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 223,724 条；A+B 统一清洗包为 229,434 条；覆盖追踪 430 所院校中已有 322 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 229,435 行（含表头），公式单元格 0，公式错误 0。本批清洗记录 547 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加批次：batch208-batch208b 政法/浙江上海缺口源复核与杭州师范入库

batch208 继续复核中央民族大学、中国音乐学院、中国药科大学、中国政法大学、华东政法大学和中国人民大学等剩余缺口来源。中央民族大学搜索索引页可见 21 个 XLSX 附件，但详情页实时返回 404，附件直链进入“请输入验证码下载附件”桥页；中国音乐学院和中国人民大学页面实时返回 404，中国药科大学返回 410；中国政法大学页面只返回站点提示页，华东政法大学页面只保留“公示期已结束”文字且无静态名单附件，均不入库。

batch208b 改抓上海理工大学、杭州师范大学和浙江农林大学等浙江/上海缺口源。上海理工大学两个搜索命中的拟录取页实时返回站点提示页，浙江农林大学茶学学院页面返回 404；杭州师范大学临床医学院（口腔医学院）2026 年临床医学专业学位硕士研究生招生拟录取名单（推免生）附件可直接下载，通用解析形成 2 条人员级记录。本批新增 `scripts/curate_batch208b_zhejiang_shanghai_pages.py` 和 `tests/test_curate_batch208b_zhejiang_shanghai_pages.py`，把附件日期误判出的 2025 年修正为标题年份 2026，并把路径统一为 `recommendation_exemption`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 杭州师范大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 2 | 0 |

可追溯来源：
- 杭州师范大学 2026 年临床医学专业学位硕士研究生招生拟录取名单公示（推免生）附件：`https://lcyxy.hznu.edu.cn/upload/resources/file/2025/09/24/7899961.xls`
- 杭州师范大学临床医学院（口腔医学院）公示页：`https://lcyxy.hznu.edu.cn/c/2025-09-24/3111521.shtml`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch208_remaining_official_pages.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch208b_zhejiang_shanghai_pages.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch208_remaining_official_pages/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch208b_zhejiang_shanghai_pages/`
- `scripts/curate_batch208b_zhejiang_shanghai_pages.py`
- `tests/test_curate_batch208b_zhejiang_shanghai_pages.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch208b_zhejiang_shanghai_pages_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 223,177 条；A+B 统一清洗包为 228,887 条；覆盖追踪 430 所院校中已有 318 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 228,888 行（含表头），公式单元格 0，公式错误 0。本批清洗记录 2 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加批次：batch207 西安石油大学校级推免拟录取 PDF 入库

batch207 继续从剩余覆盖缺口中筛选可实时复现的官网源，种子覆盖东北电力大学、西安石油大学、南京理工大学和浙江中医药大学。西安石油大学研究生招生信息网校级 `2026年推免生拟录取名单.pdf` 可直接下载并含文本层；东北电力大学详情页实时返回 404，南京理工大学详情页实时返回 410，浙江中医药大学详情页实时返回 412，均留证不入库。

本批通用爬虫可抓取西安石油大学校级页面、经济管理学院页面、化学化工学院页面和校级 PDF。通用解析只从校级 PDF 抽到 6 条直博生，并从经济管理学院 9 月拟接收表抽到 12 条；复核 PDF 文本后发现校级 10 月正式名单实际包含 54 条人员级记录。因此新增 `scripts/curate_batch207_promising_remaining_sources.py` 和 `tests/test_curate_batch207_promising_remaining_sources.py`，只以更晚、更权威的校级拟录取 PDF 入库；经济管理学院拟接收表和化学化工学院无表格页面仅作原始留证，避免把未出现在校级最终 PDF 的人员误计入。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西安石油大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 54 | 0 |

可追溯来源：
- 西安石油大学 2026 年推免生拟录取名单 PDF：`https://yjszs.xsyu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2074804384&wbfileid=5656530`
- 西安石油大学 2026 年推免生拟录取名单公示页：`https://yjszs.xsyu.edu.cn/info/1032/1515.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch207_promising_remaining_sources.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch207_promising_remaining_sources/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260527_batch207_promising_remaining_sources/graduate_outcome_failures.jsonl`
- `scripts/curate_batch207_promising_remaining_sources.py`
- `tests/test_curate_batch207_promising_remaining_sources.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch207_promising_remaining_sources_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 223,175 条；A+B 统一清洗包为 228,885 条；覆盖追踪 430 所院校中已有 317 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 228,886 行（含表头），公式单元格 0，公式错误 0。本批清洗记录 54 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加批次：batch206 艺术/音乐院校官网名单入库

batch206 继续围绕艺术、音乐类缺口院校筛选可实时复现的官网源。鲁迅美术学院官方 XLSX、四川音乐学院官方 PDF、集美大学美术与设计学院官方 XLSX、中国美术学院港澳台硕博拟录取 HTML 均可结构化；四川美术学院公告页可访问但真实 PDF 附件进入验证码下载桥，山东艺术学院列表和办法页未暴露人员级名单，中国美术学院推免拟录取旧 URL 实时返回 404，均只留证不入库。

本批新增 `scripts/curate_batch206_art_music_sources.py` 和 `tests/test_curate_batch206_art_music_sources.py`：鲁迅美院按 XLSX 学科段落补齐研究方向和成绩；四川音乐学院按 PDF 序号重组 52 条折行记录；中国美术学院把成绩从 `major` 错位字段移入备注；集美大学只保留 `正选` 行，剔除备选候补。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 鲁迅美术学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 361 | 0 |
| 四川音乐学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 52 | 0 |
| 集美大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 11 | 0 |
| 中国美术学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 9 | 0 |

可追溯来源：
- 鲁迅美术学院 2026 年硕士研究生招生考试拟录取名单附件：`https://www.lumei.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2099302842&wbfileid=8D5779C52999BBF461947A172DD13D80`
- 四川音乐学院 2026 年推免生拟推荐名单 PDF：`https://www.sccm.edu.cn/upload/202509/09/202509091749344443.pdf`
- 集美大学美术与设计学院拟推荐 2026 届免试硕士研究生名单附件：`https://arts.jmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2039804140&wbfileid=242BE61F30C9C48A08D937A3A5A14ABD`
- 中国美术学院 2026 年港澳台硕士博士研究生拟录取名单公示：`https://zb.caa.edu.cn/info/1021/7101.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch206_art_music_sources.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch206b_scfai_attachments.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch206_art_music_sources/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch206b_scfai_attachments/`
- `scripts/curate_batch206_art_music_sources.py`
- `tests/test_curate_batch206_art_music_sources.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch206_art_music_sources_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 223,121 条；A+B 统一清洗包为 228,831 条；覆盖追踪 430 所院校中已有 316 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 228,832 行（含表头），公式单元格 0，公式错误 0。本批清洗记录 433 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加批次：batch204-batch205 艺术院校官网名单入库

batch204 先复核中国政法大学、中央民族大学、北京协和医学院、华东师范大学等缺口来源。中国政法大学页面返回动态挑战脚本；中央民族大学、华东师范大学搜索索引命中的页面/附件实时返回 404；北京协和医学院推免结果页当前已切换为 2027 空表，统考/港澳台附件进入验证码下载桥，均不绕过、不入库。

batch205 转向可实时复现的艺术院校官网源。中央美术学院两个官方 PDF 可直接下载，西安美术学院官网 HTML 表格可直接解析。通用解析能出记录，但会把中央美术学院 PDF 重复表头混入姓名列；本批新增 `scripts/curate_batch205_art_school_sources.py` 和 `tests/test_curate_batch205_art_school_sources.py`，按 PDF/HTML 表格结构重新抽取人员级字段，并保留推荐院系、拟录取院系、研究方向、准考证号、成绩与推荐类型。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中央美术学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 205 | 0 |
| 中央美术学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 488 | 0 |
| 西安美术学院 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 83 | 0 |

可追溯来源：
- 中央美术学院 2026 年接收推荐免试攻读硕士学位研究生拟录取名单 PDF：`https://www.cafa.edu.cn/library/dynamic.images/info/2025926135710903.pdf`
- 中央美术学院 2026 年硕士研究生招生考试拟录取名单 PDF：`https://www.cafa.edu.cn/library/dynamic.images/info/202642152347107.pdf`
- 西安美术学院 2026 年优秀应届本科毕业生免试攻读硕士学位研究生拟录取名单公示：`https://zhshch.xafa.edu.cn/info/1012/4216.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch204_promising_official_pages.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch205_art_school_sources.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources/`
- `scripts/curate_batch205_art_school_sources.py`
- `tests/test_curate_batch205_art_school_sources.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 222,688 条；A+B 统一清洗包为 228,398 条；覆盖追踪 430 所院校中已有 312 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 228,399 行（含表头），公式单元格 0，公式错误 0。本批清洗记录 776 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加批次：batch203 华东理工大学图片名单 OCR 入库

batch203 继续复核上海理工大学、东北师范大学、华东理工大学、上海体育大学等覆盖缺口。上海理工大学和华东理工大学部分旧链接返回“提示信息”；东北师范大学公告页可访问，但校内查询系统实时返回“录取名单尚未公布”，未绕过动态系统；上海体育大学页面返回脚本拦截页，未入库。

华东理工大学 2026 年硕士研究生拟录取名单公示页仍公开可访问，名单主体为 74 张内嵌 JPG 图片。本批新增 Windows OCR 清洗链路：`scripts/curate_batch203_ecust_image_ocr.py` 调用本机 `zh-Hans-CN` OCR 识别词和坐标，再按表格列坐标重组准考证号、姓名、录取学院、录取专业、学习方式、初试/复试/综合成绩、录取类别和备注；新增 `tests/test_curate_batch203_ecust_image_ocr.py` 覆盖图片 URL 提取、坐标重组、字母专业代码和 OCR 常见 `00` 误识别修复。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 华东理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,676 | 161 |

可追溯来源：
- 华东理工大学 2026 年硕士研究生拟录取名单公示页：`https://gschool.ecust.edu.cn/2026/0506/c12750a190107/page.htm`
- 名单图片保存在：`data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages/ecust_images/`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch203_search_refresh_pages.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages/`
- `scripts/curate_batch203_ecust_image_ocr.py`
- `tests/test_curate_batch203_ecust_image_ocr.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 221,912 条；A+B 统一清洗包为 227,622 条；覆盖追踪 430 所院校中已有 310 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 227,623 行（含表头），公式单元格 0，公式错误 0。本批 OCR 清洗记录 2,676 条，空姓名 36，需复核 161，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加批次：batch200-batch202 山东中医药大学博士拟录取与多校留证

batch200 继续尝试 20 个缺口院校详情页，batch201 尝试剩余直接附件候选。多数旧 URL 已失效或不再暴露附件，其中山东农业大学详情页返回 403，西安外国语大学、沈阳航空航天大学、桂林医科大学、贵州师范大学、聊城大学等旧页返回 404，南京理工大学、中国药科大学页面返回 410，重庆邮电大学返回 412。沈阳师范大学、西安电子科技大学页面可访问，但附件仅保留“公示期已结束”文字，无实际下载 URL，未入库。

batch202 通过网页搜索补充到山东中医药大学 2026 年全日制博士研究生第一批次拟录取名单官方 PDF。通用解析未覆盖该博士表格版式，本批新增 `scripts/curate_batch202_sdutcm_doctor_pdf.py` 和 `tests/test_curate_batch202_sdutcm_doctor_pdf.py`，按报名号、学院、姓名、报考专业、材料综合成绩、综合考核成绩和总成绩抽取。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山东中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 133 | 0 |

可追溯来源：
- 山东中医药大学 2026 年全日制博士研究生第一批次拟录取名单 PDF：`https://yjs.sdutcm.edu.cn/__local/8/82/E8/08B98A973B57AE574FEE8244163_76DB338B_5BA11.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch200_more_detail_pages.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch201_remaining_direct_files.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch202_sdutcm_doctor_pdf.csv`
- `scripts/curate_batch202_sdutcm_doctor_pdf.py`
- `tests/test_curate_batch202_sdutcm_doctor_pdf.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch202_sdutcm_doctor_pdf_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 219,236 条；A+B 统一清洗包为 224,946 条；覆盖追踪 430 所院校中已有 309 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 224,947 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch199 山西财经等四校硕士拟录取

batch199 从覆盖缺口中选取 20 个研究生院具体公示页继续抓取。山西财经大学、佳木斯大学、哈尔滨商业大学、青海民族大学的公示页均可展开官方附件，通用解析得到人员级记录；哈尔滨商业大学 PDF 同时混入重复页码和标题行，本批新增 `scripts/curate_batch199_promising_pages.py` 和 `tests/test_curate_batch199_promising_pages.py`，剔除页眉页脚噪声后入库。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山西财经大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,380 | 0 |
| 佳木斯大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 519 | 0 |
| 哈尔滨商业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 579 | 0 |
| 青海民族大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 478 | 0 |

可追溯来源：
- 山西财经大学 2026 年硕士研究生招生第一志愿拟录取名单公示页：`https://yjs.sxufe.edu.cn/info/1012/7843.htm`
- 山西财经大学拟录取名单附件：`https://yjs.sxufe.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1400463185&wbfileid=33D524C133D0BB87F44BF3598CD767EB`
- 佳木斯大学 2026 年硕士研究生招生一志愿考生拟录取名单公示页：`https://yjs.jmsu.edu.cn/info/1061/3688.htm`
- 佳木斯大学拟录取名单附件：`https://yjs.jmsu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1843095195&wbfileid=3085D6EB92D01E8F5E9198FD3FDD359A`
- 哈尔滨商业大学 2026 年硕士研究生招生考试一志愿拟录取全日制考生名单公示页：`https://yjsc.hrbcu.edu.cn/info/1115/5681.htm`
- 哈尔滨商业大学拟录取名单附件：`https://yjsc.hrbcu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1470188546&wbfileid=E95FD41322B3160FBEE16427EC6B48DE`
- 青海民族大学 2026 年硕士研究生招生考试第一志愿考生拟录取名单公示页：`https://yjsy.qhmu.edu.cn/info/1006/3150.htm`
- 青海民族大学拟录取名单附件：`https://yjsy.qhmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1696603605&wbfileid=374DBF47CF982786356770BBBA1502E3`

排除说明：
- 三峡大学 `https://graduate.ctgu.edu.cn/info/1064/7058.htm` 连接被远端重置，未入库。
- 东北电力大学、北方民族大学、广东药科大学、天津财经大学、河北农业大学、皖南医学院、重庆交通大学、武汉体育学院等本轮命中的旧公示页实时返回 404，未入库。
- 中国医科大学新域名公示页实时返回 502，未入库。
- 华北理工大学公示页可访问但为简短 HTML 跳转/空页，未形成记录。

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch199_promising_pages.csv`
- `scripts/curate_batch199_promising_pages.py`
- `tests/test_curate_batch199_promising_pages.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch199_promising_pages_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 219,103 条；A+B 统一清洗包为 224,813 条；覆盖追踪 430 所院校中已有 308 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 224,814 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch193-batch198 温州医科大学与多校源复核

batch193-batch198 继续围绕 B 类缺口院校尝试“具体公示页/直接 PDF”抓取。南京财经大学、大连外国语大学等附件入口进入验证码下载桥；上海科技大学旧公示页返回 410；北京电影学院返回 412；杭州师范大学、江汉大学、三峡大学、华侨大学、中国药科大学等旧 URL 返回 404；中国医科大学出现旧式 SSL 协商失败；华东政法大学页面仅保留附件文件名，无可请求下载 URL；山东理工大学可抓到的推免 PDF 为扫描/水印文本，硕士拟录取附件未在页面暴露可下载名单 URL，均未入库。

本轮可用新增来自温州医科大学官网 2025 年硕士研究生第一批、第二批拟录取 PDF。通用解析会把 PDF 表头、页脚水印和断行姓名混入人员记录，本批新增 `scripts/curate_batch197_wmu.py` 和 `tests/test_curate_batch197_wmu.py`，按 `考生编号后五位、姓名、专业代码、专业名称/研究方向、初试总分、复试成绩、总成绩、学习方式、备注` 重新抽取。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 温州医科大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,309 | 0 |

可追溯来源：
- 温州医科大学 2025 年硕士研究生第一批拟录取名单 PDF：`https://yjsy.wmu.edu.cn/__local/7/37/B7/FE9C98AACCA77F365E9E1FFEF3E_3CC368F6_D989A.pdf`
- 温州医科大学 2025 年硕士研究生第二批拟录取名单 PDF：`https://yjsy.wmu.edu.cn/__local/1/19/A9/D49C9A4BC1536107F46B238B538_C5F6557A_9AED5.pdf`

排除说明：
- 南京财经大学 `download.jsp` 附件、大连外国语大学 `download.jsp` 附件均要求验证码，不绕过。
- 上海科技大学 `https://yanzhao.shanghaitech.edu.cn/2026/0421/c9737a1120984/page.htm` 返回 410。
- 山东理工大学 `https://yjsh.sdut.edu.cn/2026/0402/c5153a561202/page.htm` 页面未暴露“附件1”名单下载 URL；推免 PDF `https://yjsh.sdut.edu.cn/2025/1127/c5139a554981/page.htm` 展开的 PDF 仅抽出水印文本，未入库。
- 中国药科大学 2024/2025 直接 PDF 旧 URL 实时返回 404，未入库。

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch197_direct_pdfs.csv`
- `scripts/curate_batch197_wmu.py`
- `tests/test_curate_batch197_wmu.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch197_wmu_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 216,147 条；A+B 统一清洗包为 221,857 条；覆盖追踪 430 所院校中已有 304 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 221,858 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch192 四川师范大学硕士拟录取

batch192 抓取四川师范大学研究生院招生新闻中 2026 年硕士研究生第一、第二、第三批拟录取名单公示。三个官网页面均可展开 PDF，通用解析从第一、第二批 PDF 中抽取人员级记录；第三批 PDF 仅抽出 1 条分数错位噪声，本批新增 `scripts/curate_batch192_sicnu.py` 和 `tests/test_curate_batch192_sicnu.py`，保留第一、第二批真实人员记录并剔除第三批噪声。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 四川师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,033 | 0 |

可追溯来源：
- 四川师范大学 2026 年硕士研究生第一批拟录取名单公示页：`https://yjsc.sicnu.edu.cn/p/0/?StId=st_app_news_i_x639111957680008910`
- 四川师范大学 2026 年硕士研究生第一批拟录取名单 PDF：`https://yjsc.sicnu.edu.cn/files/yjs/news/639111969476232211_d.pdf`
- 四川师范大学 2026 年硕士研究生第二批拟录取名单公示页：`https://yjsc.sicnu.edu.cn/p/0/?StId=st_app_news_i_x639119526920167985`
- 四川师范大学 2026 年硕士研究生第二批拟录取名单 PDF：`https://yjsc.sicnu.edu.cn/files/yjs/news/639119533275173333_d.pdf`
- 四川师范大学 2026 年硕士研究生第三批拟录取名单公示页（留证，未入库）：`https://yjsc.sicnu.edu.cn/p/0/?StId=st_app_news_i_x639129712534171090`

排除说明：
- 第三批 PDF `https://yjsc.sicnu.edu.cn/files/yjs/news/639129848568869336_d.pdf` 通用文本抽取只形成 1 条分数错位记录，未作为人员级数据入库。
- 重庆师范大学搜索索引命中的官网 PDF/HTML 旧 URL 实时返回 404，未入库。

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch192_sicnu.csv`
- `scripts/curate_batch192_sicnu.py`
- `tests/test_curate_batch192_sicnu.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch192_sicnu_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 213,838 条；A+B 统一清洗包为 219,548 条；覆盖追踪 430 所院校中已有 303 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 219,549 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch190 西南科技大学硕士与推免拟录取

batch190 抓取西南科技大学研究生招生网 2026 年硕士拟录取公示页，以及 2026 年研究生（直博生、推免生）拟录取公示页。硕士公示页可展开官方 PDF，通用解析能识别人员行但会把表头和页脚口号混入，并对长姓名行错位；本批新增 `scripts/curate_batch190_swust.py` 和 `tests/test_curate_batch190_swust.py`，按 PDF 文本行结构重新抽取 `考生编号、姓名、学院、录取专业、学习方式、录取类别、初试/复试/总成绩`，并保留官网 HTML 中 37 条推免/直博记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,237 | 0 |
| 西南科技大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 37 | 0 |

可追溯来源：
- 西南科技大学 2026 年拟录取硕士研究生名单公示页：`https://gs.swust.edu.cn/zs/2026/0506/c7797a236234/page.htm`
- 西南科技大学 2026 年拟录取硕士研究生名单 PDF：`https://gs.swust.edu.cn/_upload/article/files/c5/a8/47903d32491cbaedf86ee1dad05e/e8a0424a-f45b-448c-9f79-270eeb383e7a.pdf`
- 西南科技大学 2026 年研究生（直博生、推免生）拟录取名单公示页：`https://gs.swust.edu.cn/zs/2024/1012/c7797a206495/page.htm`

排除说明：
- 中国海洋大学 2026 硕士/推免官网页当前仅保留“附件：名单（公示已结束）”文字，HTML 未暴露可下载名单链接，留证未入库。
- 中国石油大学（华东）2026 硕士官方 PDF 已下载，但文件为扫描图像且当前环境无 OCR 引擎，未强行结构化。
- 天津科技大学官网实时请求进入 302 自循环，五邑大学检索页实时返回 404，青岛理工大学附件入口需要验证码下载，均未入库。

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch190_swust.csv`
- `scripts/curate_batch190_swust.py`
- `tests/test_curate_batch190_swust.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch190_swust_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 212,805 条；A+B 统一清洗包为 218,515 条；覆盖追踪 430 所院校中已有 302 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 218,516 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch180/batch180b 华东师范留证与南京师范大学外国语学院

batch180 验证华东师范大学 2026 年硕士研究生拟录取名单公示页，页面当前仅保留“公示已结束”的附件文字，HTML 中未暴露可下载名单链接，因此留证不入库。batch180b 转向南京师范大学外国语学院官网，页面可展开 2026 年硕士拟录取和博士拟录取两个 PDF，通用 PDF 解析可稳定抽出人员级记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 南京师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 177 | 0 |

可追溯来源：
- 南京师范大学外国语学院 2026 年硕士研究生拟录取名单公示页：`https://wy.njnu.edu.cn/info/1061/12836.htm`
- 南京师范大学外国语学院 2026 年博士研究生拟录取名单公示页：`https://wy.njnu.edu.cn/info/1061/12746.htm`
- 华东师范大学 2026 年硕士研究生拟录取名单公示页（留证未入库）：`https://yjszs.ecnu.edu.cn/95/93/c43264a759187/page.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch180_ecnu.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch180b_njnu.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch180_ecnu/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch180b_njnu/records_clean.csv`

本批合并后，B 类官网主表为 210,677 条；A+B 统一清洗包为 216,387 条；覆盖追踪 430 所院校中已有 298 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 216,388 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch179 浙江工商大学博士拟录取 PDF 专项清洗

batch179 抓取浙江工商大学研究生招生信息网 2026 年“申请-考核”制博士研究生拟录取名单公示页。硕士一志愿和调剂公示入口当前实时返回 410，未入库；博士页面可展开两份官方 PDF。通用解析未覆盖该 PDF 表格版式，本批新增 `scripts/curate_batch179_zjgsu.py` 和 `tests/test_curate_batch179_zjgsu.py`，按“序号、一级学科、招生学院、录取专业代码/名称、报名号、姓名、录取类别、总成绩、备注”完整行抽取。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 浙江工商大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 143 | 0 |

可追溯来源：
- 浙江工商大学 2026 年“申请-考核”制博士研究生拟录取名单公示页：`https://yjszs.zjgsu.edu.cn/2026/0514/c466a222899/page.htm`
- 浙江工商大学 2026 年“申请-考核”制博士研究生拟录取名单（第一批）PDF：`https://yjszs.zjgsu.edu.cn/_upload/article/files/45/8a/c9d72c20400aa85f9baea3e0124c/13e52e06-fbc4-4368-9e81-3fb8c907048f.pdf`
- 浙江工商大学 2026 年“申请-考核”制博士研究生拟录取名单（第二批）PDF：`https://yjszs.zjgsu.edu.cn/_upload/article/files/45/8a/c9d72c20400aa85f9baea3e0124c/8dc16439-8987-4c80-bd5c-9f0b7fa295c1.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch179_zjgsu.csv`
- `scripts/curate_batch179_zjgsu.py`
- `tests/test_curate_batch179_zjgsu.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch179_zjgsu_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 210,500 条；A+B 统一清洗包为 216,210 条；覆盖追踪 430 所院校中已有 297 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 216,211 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch178 云南大学博士拟录取 PDF 专项清洗

batch178 抓取云南大学西南联合研究生院官方公示，覆盖 2026 年博士研究生“申请-考核”制第一批次拟录取名单，以及 2026 年硕博连读拟录取名单。通用解析会把折行后的研究方向和专业名称误当成人名，本批新增 `scripts/curate_batch178_ynu.py` 和 `tests/test_curate_batch178_ynu.py`，按 PDF 文本完整行中的学院代码、专业代码、报名号/学号、姓名、综合考核成绩进行严格抽取。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 云南大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 452 | 0 |

可追溯来源：
- 云南大学 2026 年博士研究生“申请-考核”制（第一批次）拟录取名单 PDF：`https://www.swugs.ynu.edu.cn/upload/c7874379671c1812327452dcd.pdf`
- 云南大学 2026 年硕博连读拟录取名单 PDF：`https://www.swugs.ynu.edu.cn/upload/c7874379671c1812327452dca.pdf`
- 云南大学 2026 年博士研究生“申请-考核”制（第一批次）拟录取名单公示页：`https://www.swugs.ynu.edu.cn/news/notice/post/nX2La5Yakq`
- 云南大学 2026 年硕博连读拟录取名单公示页：`https://www.swugs.ynu.edu.cn/news/notice/post/PIzMdtKem6`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch178_ynu.csv`
- `scripts/curate_batch178_ynu.py`
- `tests/test_curate_batch178_ynu.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch178_ynu_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 210,357 条；A+B 统一清洗包为 216,067 条；覆盖追踪 430 所院校中已有 296 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 216,068 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch177b 内蒙古大学与山东师范大学博士拟录取

batch177b 继续补 B 类官网来源。内蒙古大学研究生院博士第一批次拟录取公示页为 HTML 表格，可直接结构化；山东师范大学若干学院官网发布博士研究生拟录取公示，其中物理与光电学院、新闻与传媒学院、经济学院页面被通用解析器稳定抽出人员级记录。内蒙古大学硕士一志愿/调剂附件入口当前为验证码下载桥或搜索索引旧页，本批留证但不并入。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 内蒙古大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 238 | 0 |
| 山东师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 44 | 0 |

可追溯来源：
- 内蒙古大学 2026 年博士研究生第一批次拟录取名单公示：`https://gs.imu.edu.cn/info/1021/2301.htm`
- 山东师范大学物理与光电学院 2026 年博士研究生拟录取名单：`https://physics.sdnu.edu.cn/info/1093/32341.htm`
- 山东师范大学新闻与传媒学院 2026 年博士研究生拟录取名单：`https://cbxy.sdnu.edu.cn/info/1501/31141.htm`
- 山东师范大学经济学院 2026 年博士研究生拟录取名单：`https://sde.sdnu.edu.cn/info/1081/28749.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch177b_imu_sdnu.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch177b_imu_sdnu/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch177b_imu_sdnu/school_year_summary.csv`

本批合并后，B 类官网主表为 209,905 条；A+B 统一清洗包为 215,615 条；覆盖追踪 430 所院校中已有 295 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 215,616 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch176 石河子大学 PDF/HTML 严格清洗

batch176 针对石河子大学官网入口继续补 B 类来源。通用解析可以从法学院 HTML 和若干学院 PDF 中抽出人员行，但会把“拟不录取/不予录取”行混入；本批新增 `scripts/curate_batch176_shzu_pdfs.py`，只保留 PDF 行文本或 HTML“学院意见”单元格明确为“拟录取”的记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 石河子大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 91 | 0 |

可追溯来源：
- 石河子大学信息科学与技术学院电子信息全日制普通计划复试情况汇总表 PDF：`https://cs.shzu.edu.cn/_upload/article/files/8f/67/333b32dd42698899822ce2ed188b/4bfc9f39-ad61-4bf4-85cc-8d603d950957.pdf`
- 石河子大学信息科学与技术学院电子信息全日制专项计划复试情况汇总表 PDF：`https://cs.shzu.edu.cn/_upload/article/files/8f/67/333b32dd42698899822ce2ed188b/7708cc68-3d00-44ab-9b9e-0a9874f78653.pdf`
- 石河子大学信息科学与技术学院网络空间安全复试情况汇总表 PDF：`https://cs.shzu.edu.cn/_upload/article/files/8f/67/333b32dd42698899822ce2ed188b/952065ad-ff23-442c-9067-8fb643b6c722.pdf`
- 石河子大学信息科学与技术学院图书情报全日制普通计划复试情况汇总表 PDF：`https://cs.shzu.edu.cn/_upload/article/files/8f/67/333b32dd42698899822ce2ed188b/db504591-a00d-43d1-afe8-6d4fa0fbaec0.pdf`
- 石河子大学信息科学与技术学院图书情报全日制专项计划复试情况汇总表 PDF：`https://cs.shzu.edu.cn/_upload/article/files/8f/67/333b32dd42698899822ce2ed188b/4385370d-4141-4a1b-bdc3-babcdf1f459d.pdf`
- 石河子大学信息科学与技术学院图书情报非全日制复试情况汇总表 PDF：`https://cs.shzu.edu.cn/_upload/article/files/8f/67/333b32dd42698899822ce2ed188b/8edf5819-8ead-423a-847b-e2295e424113.pdf`
- 石河子大学外国语学院翻译专业第二批调剂复试结果公示 PDF：`https://wyxy.shzu.edu.cn/_upload/article/files/c0/64/138f2ffb4f66ae4aa6f647df9247/ff53eef5-fd74-455a-971e-1e86db482458.pdf`
- 石河子大学法学院 2026 年硕士研究生调剂复试情况公示页面：`https://zfxy.shzu.edu.cn/2026/0417/c12845a231298/page.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch176_shzu.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch176b_shzu_pdfs.csv`
- `scripts/curate_batch176_shzu_pdfs.py`
- `tests/test_curate_batch176_shzu_pdfs.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch176_shzu_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 209,623 条；A+B 统一清洗包为 215,333 条；覆盖追踪 430 所院校中已有 293 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 215,334 行（含表头），公式单元格 0，公式错误 0；`python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs` 为 241 tests OK。

## 2026-05-27 追加批次：batch175 新疆财经大学与黑龙江中医药大学

batch175 继续补 B 类官网来源。先尝试中国海洋大学、中国药科大学等搜索索引中的旧 PDF 直链，但官网实时请求已返回 404，未入库。随后切换到可实时下载的新疆财经大学官网 PDF，以及此前已下载但通用解析错位的黑龙江中医药大学推免 PDF。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 新疆财经大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 577 | 0 |
| 新疆财经大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 12 | 0 |
| 黑龙江中医药大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 85 | 0 |

可追溯来源：
- 新疆财经大学 2026 年硕士研究生招生调剂考生拟录取名单 PDF：`https://yjsy.xjufe.edu.cn/docs/2026-04/0ea28793ae3c480c9bfddcb09148973a.pdf`
- 新疆财经大学 2026 年推荐免试攻读硕士学位研究生复试成绩及拟录取名单公示 PDF：`https://yjsy.xjufe.edu.cn/docs/20251010073515960651.pdf`
- 黑龙江中医药大学 2026 年接收推荐免试攻读硕士研究生名单 PDF：`https://yjsy.hljucm.net/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1139447238&wbfileid=B9EC50127D176F5D5C41A17BAA6CCB23`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch175b.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch175b/records_clean.csv`
- `scripts/curate_batch175_hljucm_pdf.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch175_hljucm_curated/records_clean_curated.csv`

本批合并后，B 类官网主表为 209,532 条；A+B 统一清洗包为 215,242 条；覆盖追踪 430 所院校中已有 292 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 215,243 行（含表头），公式单元格 0，公式错误 0；`python -m unittest tests.test_graduate_outcome_crawler` 为 238 tests OK。

## 2026-05-26 追加批次：batch174 青海大学 XLS 补解析

batch174 处理此前已下载但通用解析器未能读取的青海大学官方 `.xls` 文件。由于运行环境缺少 `xlrd`，本批使用本机 Excel COM 后台读取工作簿，并新增 `scripts/curate_batch174_qhu_xls_with_excel.py` 生成批次级 curated 清洗结果。原表共 1,273 行，其中首行为标题、第二行为表头，后续 1,271 行为人员级记录，字段包含考生编号、姓名、报考院系、报考专业、研究方向、专项计划、初试/复试/总成绩和录取状态。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 青海大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,271 | 0 |

可追溯来源：
- 青海大学 2025 年硕士研究生招生拟录取名单（一志愿考生）XLS：`https://yjs.qhu.edu.cn/docs/2025-04/615da678d8de4fbd974bea45ae6cfaa5.xls`

本批合并后，B 类官网主表为 208,858 条；A+B 统一清洗包为 214,568 条；覆盖追踪 430 所院校中已有 290 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 214,569 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch173 既有原始文件补解析

batch173 不新增大规模网络抓取，而是回扫此前批次已经下载、但通用解析器未能结构化的官方原始文件。优先选择文本层清晰、字段可稳定识别的 PDF：西安交通大学医学部 2026 年硕士研究生拟录取名单、中山大学智能工程学院 2026 届推免拟推荐名单、长安大学能电学院 2026 届推免拟推荐及递补拟推荐名单。

本批新增脚本 `scripts/curate_batch173_existing_raw.py`，只做批次级补解析，不改主爬虫规则。西安交通大学医学部 PDF 的名单行被页眉/考试方式列拆成多行，脚本按 `序号 考生编号 姓名 专业码 初试 复试 总成绩` 抽取 373 条，并修复 2 个跨行复姓名；中山大学和长安大学 PDF 均为推荐名单表，分别抽取 71 条、72 条。最终保留 516 条人员级记录，需复核 0 条。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中山大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 71 | 0 |
| 西安交通大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 373 | 0 |
| 长安大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 72 | 0 |

可追溯来源：
- 中山大学智能工程学院 2026 届本科毕业生免试攻读研究生学位拟推荐名单（含候补）：`https://ise.sysu.edu.cn/sites/default/files/2025-09/%E6%99%BA%E8%83%BD%E5%B7%A5%E7%A8%8B%E5%AD%A6%E9%99%A22026%E5%B1%8A%E6%9C%AC%E7%A7%91%E6%AF%95%E4%B8%9A%E7%94%9F%E5%85%8D%E8%AF%95%E6%94%BB%E8%AF%BB%E7%A0%94%E7%A9%B6%E7%94%9F%E5%AD%A6%E4%BD%8D%E6%8B%9F%E6%8E%A8%E8%8D%90%E5%90%8D%E5%8D%95%EF%BC%88%E5%90%AB%E5%80%99%E8%A1%A5%EF%BC%89.pdf`
- 西安交通大学医学部 2026 年硕士研究生拟录取名单公示：`https://medgs.xjtu.edu.cn/202641.pdf`
- 长安大学能电学院 2026 年优秀应届本科毕业生免试攻读研究生拟推荐及递补拟推荐名单：`https://ndxy.chd.edu.cn/__local/2/C6/2C/0592A417ABE23CB7EFE0DD4954B_F7E86CF6_11390.pdf`

本批合并后，B 类官网主表为 207,587 条；A+B 统一清洗包为 213,297 条；覆盖追踪 430 所院校中已有 289 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 213,298 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch172b 长春理工大学

batch172 初始种子覆盖长安大学、石河子大学、新疆财经大学、长春理工大学、天津科技大学、太原科技大学、浙江工商大学、皖南医学院、重庆邮电大学、温州医科大学、云南中医药大学和浙江中医药大学等入口。轻量探测发现，长安大学入口连接超时，天津科技大学入口重定向循环，太原科技大学超时，浙江工商大学返回 403，皖南医学院候选页 404，重庆邮电大学/温州医科大学/云南中医药大学/浙江中医药大学为 412、483 或 502，故收缩为 batch172b，只抓取石河子大学、新疆财经大学和长春理工大学 3 个响应稳定入口。

batch172b 实际抓取 26 个页面/附件，原始结构化 1,855 条，通用清洗 1,033 条。质检后确认新疆财经大学命中的 1,320 条原始记录主要来自“进入复试名单”“复试分数线”“学费标准”等非拟录取名单，全部保留抓取证据但不合并。长春理工大学 6 个 PDF 标题均为“拟录取/录取名单”，但 PDF 表格把“全日制”读入姓名列，真实姓名位于 `admission_major` 末尾；本批额外生成 `records_clean_curated.csv`，按 `专业代码 专业名 方向代码 姓名` 结构校正姓名和专业字段，最终保留 534 条人员级记录，需复核 0 条。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 长春理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 534 | 0 |

可追溯来源：
- 长春理工大学调剂1拟录取名单公示（线上复试专业）：`https://yzb.cust.edu.cn/docs/2026-04/4ffdc00ee1054e69a4f2e2de2714eeb4.pdf`
- 长春理工大学调剂1拟录取名单公示（线下复试专业）：`https://yzb.cust.edu.cn/docs/2026-04/f1277507e34d455393740257523d6c69.pdf`
- 长春理工大学调剂复试增补拟录取名单：`https://yzb.cust.edu.cn/docs/2026-04/f5d9632ceff74f0abc42ce15a28d34dd.pdf`
- 长春理工大学调剂2拟录取名单公示（线上复试专业）：`https://yzb.cust.edu.cn/docs/2026-04/b911dc3428fd4528ba2a6dff73ff63dc.pdf`
- 长春理工大学调剂2拟录取名单公示（线下复试专业）：`https://yzb.cust.edu.cn/docs/2026-04/c9e41f181f18483ca20ade057cbba478.pdf`
- 长春理工大学一志愿复试增补录取名单：`https://yzb.cust.edu.cn/docs/2026-04/fe54c2e447374842b6b881343861ebca.pdf`

本批合并后，B 类官网主表为 207,071 条；A+B 统一清洗包为 212,781 条；覆盖追踪 430 所院校中已有 286 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 212,782 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch171 华中师范/沈阳音乐/新疆师范

batch171 继续优先选择“搜索结果能指向官方原文、且页面能跟到附件”的 B 类官网来源。种子覆盖北方民族大学、佳木斯大学、首都师范大学、武汉体育学院、沈阳音乐学院、华中师范大学、华东师范大学、新疆师范大学和上海理工大学等 11 个入口。实际抓取 36 个页面/附件，原始结构化 4,157 条。

本批额外生成 `records_clean_curated.csv`：华中师范大学各学院 PDF 附件标题不含年份，通用解析会把学院代码误识别为 2000、2010、2015 等年份；沈阳音乐学院 PDF 标题为 2026，但通用解析受站点页面年份影响落成 2025。经来源页和附件标题复核后，本批统一校正为 2026 年并复用既有去重/过滤规则，最终保留 3,990 条人员级记录，需复核 0 条。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 华中师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,678 | 0 |
| 沈阳音乐学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 281 | 0 |
| 新疆师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 31 | 0 |

可追溯来源：
- 华中师范大学 2026 年硕士研究生拟录取名单公示：`https://gs.ccnu.edu.cn/info/1028/6263.htm`
- 沈阳音乐学院 2026 年硕士研究生拟录取名单 PDF：`https://www.sycm.edu.cn/video/%E6%B2%88%E9%98%B3%E9%9F%B3%E4%B9%90%E5%AD%A6%E9%99%A22026%E5%B9%B4%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95.pdf`
- 新疆师范大学 2026 年硕士研究生招生拟录取名单公示（递补）：`https://yjsc.xjnu.edu.cn/info/1040/7481.htm`

质量说明：
- 华中师范大学 28 个学院/单位附件均来自同一个 2026 年校级公示页，年份已按父级公示页校正为 2026。
- 沈阳音乐学院附件标题明确为 2026 年拟录取名单，年份已按附件标题校正为 2026。
- 北方民族大学候选页实时 404；佳木斯大学、武汉体育学院、上海理工大学候选页实时 502；首都师范大学入口跳转后未暴露可解析名单；华东师范大学页面显示公示已结束且无人员级明细，均未合并。

本批合并后，B 类官网主表为 206,537 条；A+B 统一清洗包为 212,247 条；覆盖追踪 430 所院校中已有 285 所精确匹配官网记录。Excel 交付版已同步重建，Public_Records 212,248 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch170 华东交通/山西农业等

batch170 继续从 153 所覆盖缺口中筛选可静态抓取的官网名单源，种子覆盖华东交通大学、内蒙古工业大学、内蒙古农业大学、山西农业大学、陕西师范大学、景德镇陶瓷大学和暨南大学等。实际抓取 47 个页面/附件，原始结构化 4,072 条，通用清洗 2,502 条。

本批做了批次级二次质检：剔除华东交通大学人文社科页面导航误抽、PDF 表头行、内蒙古工大“名次”表头、陕西师大“主动放弃”行，并把华东交通大学附件标题中的专业代码/专业名补回人员记录。最终 `records_clean_curated.csv` 保留 2,480 条，丢弃 22 条噪声/无效行。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 内蒙古工业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 23 | 0 |
| 华东交通大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 264 | 49 |
| 山西农业大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,764 | 0 |
| 山西农业大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 2 | 0 |
| 山西农业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 287 | 0 |
| 山西农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 41 | 0 |
| 景德镇陶瓷大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 81 | 0 |
| 陕西师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 18 | 0 |

可追溯来源示例：
- 华东交通大学人文社会科学学院 2026 年硕士研究生拟录取名单：`https://rwxy.ecjtu.edu.cn/info/1064/6084.htm`
- 华东交通大学电气与自动化工程学院 2026 年硕士研究生拟录取名单：`https://dqxy.ecjtu.edu.cn/info/1090/12192.htm`
- 山西农业大学研究生院招生工作栏目：`https://grs.sxau.edu.cn/zsgz.htm`
- 山西农业大学草业学院研究生教育栏目：`https://cyxy.sxau.edu.cn/jyjx/yjsjy.htm`
- 陕西师范大学美术学院 2026 年推免拟推荐名单：`https://meishuxy.snnu.edu.cn/info/1013/6445.htm`
- 景德镇陶瓷大学 2026 年推荐免试硕士研究生拟录取名单：`https://zs.jci.edu.cn/info/1006/2211.htm`
- 景德镇陶瓷大学信息工程学院 2026 年推免拟推荐名单：`https://xxgc.jci.edu.cn/info/1044/4978.htm`

质量说明：
- 华东交通大学体育与健康学院 49 条记录缺少专业代码/专业名，已保留姓名、考生编号和成绩，并标记 `needs_review=true`。
- 暨南大学 PDF 直链当前返回 403，内蒙古农业大学和陕西师范大学数学学院入口实时 404，保留失败日志但不入库。

数据包同步更新：
- B 类官网清洗表：202,547 条，325 个学校/年份/类型汇总组。
- A+B 统一清洗表：208,257 条，477 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 282 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- batch170 curated 清洗表：2,480 条清洗记录，需人工复核 49。
- 工作簿结构校验：Overview 15 行、Source_Summary 478 行（含表头）、Coverage 431 行（含表头）、Public_Records 208,258 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch167/batch169 浙江财经等官网来源

batch167 先验证浙江财经大学 2026 年推免拟录取学院页，14 个入口中数据科学学院和艺术学院两页可直接结构化，清洗后新增 5 条记录；其余入口多为实时 404，西电校级公示页只保留公示说明且不暴露人员名单，西交机械学院入口需要浏览器挑战，均暂不入库。

batch168 用搜索命中的静态页和 PDF 直链继续试探，18 个入口仅抓到 4 个提示页/404 跳转或非名单内容，未形成清洗记录，保留原始留证但不合并。

batch169 改为优先选择搜索摘要中可见表头/样例行的官网正文表格和 PDF 直链，16 个入口写入 14 个文档，原始结构化 863 条、清洗 842 条；与既有主表按学校/年份/类型/姓名/学号/来源/专业等字段去重后，净新增 556 条。连同 batch167，本轮 B 类官网主表净增 561 条。

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 浙江财经大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 5 | 0 |
| 上海交通大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 59 | 0 |
| 东北农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 191 | 0 |
| 中国农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 | 2 |
| 中国地质大学（北京） | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 20 | 0 |
| 中国石油大学（北京） | 2026 | recommendation_exemption_list | recommendation_exemption | 25 | 0 |
| 中央戏剧学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 95 | 0 |
| 四川大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 281 | 0 |
| 天津理工大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 4 | 0 |
| 清华大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 17 | 0 |
| 湖南大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 148 | 0 |

可追溯来源示例：
- 浙江财经大学数据科学学院 2026 年接收推荐免试硕士研究生拟录取名单：`https://ds.zufe.edu.cn/info/1237/14593.htm`
- 浙江财经大学艺术学院 2026 年接收推荐免试硕士研究生拟录取名单：`https://ys.zufe.edu.cn/info/1038/9492.htm`
- 四川大学建筑与环境学院 2026 年硕士研究生拟录取名单：`https://acem.scu.edu.cn/info/1003/13968.htm`
- 四川大学电子信息学院 2026 年硕士拟录取名单：`https://eie.scu.edu.cn/info/1025/14978.htm`
- 中国石油大学（北京）新能源与材料学院 2026 年接收推荐免试研究生拟录取名单：`https://www.cup.edu.cn/cnem/tzgg/6822e1949ee64c3da67c3b229f5c4909.htm`
- 湖南大学化学化工学院 2026 年推荐免试研究生名单：`https://cc.hnu.edu.cn/info/1102/12491.htm`
- 东北农业大学 2026 年拟录取免试攻读硕士研究生名单：`https://graduate.neau.edu.cn/info/1146/4239.htm`
- 上海交通大学设计学院 2026 年拟录取推荐免试研究生名单：`https://designschool.sjtu.edu.cn/dynamic/notice/detail/68f59251e8e233cad44211ec`

质量说明：
- 中国农业大学资源与环境学院 PDF 仅稳定抽到 2 条人员姓名、考生编号和专业代码 `083000`，缺专业名，保留为 `needs_review=true`。
- batch169 中中央戏剧学院、天津理工大学、上海交通大学和东北农业大学部分来源已在既有主表中出现，本轮合并时按人员级键去重，避免重复计入。

数据包同步更新：
- B 类官网清洗表：200,067 条，317 个学校/年份/类型汇总组。
- A+B 统一清洗表：205,777 条，469 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 277 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- batch167 清洗表：5 条清洗记录，需人工复核 0。
- batch169 清洗表：842 条清洗记录，需人工复核 2。
- 工作簿结构校验：Overview 15 行、Source_Summary 470 行（含表头）、Coverage 431 行（含表头）、Public_Records 205,778 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch166 上海中医药大学

batch164 尝试杭州师范大学、上海理工大学、上海体育大学、温州医科大学和上海中医药大学等缺口入口。杭师两个入口实时 404，温州医科大学入口返回 483，上海理工大学页面返回“无效的文章参数”，上海体育大学页面为 JS 保护/无静态明细，暂不入库。上海中医药大学页面正文未暴露表格，但 `meta description` 中包含名单前段摘要；batch166 新增专项解析，仅保留该摘要中完整可解析的人员记录，最后被截断的记录不入库。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海中医药大学 | 2025 | incoming_recommendation_admission_list | recommendation_exemption | 11 | 0 |

可追溯来源：
- 上海中医药大学 2025 年推免硕士研究生拟录取名单公示：`https://yjsy.shutcm.edu.cn/2025/1013/c1143a169399/page.htm`

质量修正：
- 新增“推免硕士研究生拟录取/推免硕士研究生拟录取名单”分类关键词，避免此类标题被归入普通统考拟录取。
- 新增上海中医药大学 `meta description` 专项解析，按“序号/姓名/拟录取学院/专业代码/专业名称/复试成绩/推荐学校”抽取；`remarks` 标记 `source_fragment meta_description`，提示这是页面摘要片段而非完整正文表格。

数据包同步更新：
- B 类官网清洗表：199,506 条，312 个学校/年份/类型汇总组。
- A+B 统一清洗表：205,216 条，464 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 275 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 465 行（含表头）、Coverage 431 行（含表头）、Public_Records 205,217 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch163 厦门大学

batch163 继续从覆盖缺口院校中筛选官网静态入口。batch162 初跑覆盖大连外国语大学、青岛理工大学、电子科技大学、厦门大学和北京第二外国语学院；可稳定结构化入库的是厦门大学材料学院、环境与生态学院/海洋与海岸带发展研究院两个 2026 年硕士拟录取 PDF。大连外国语大学附件进入验证码桥页，电子科技大学信通学院 PDF 无可抽取文本层，青岛理工大学页面为公示说明但未暴露静态名单附件，北二外官方 PDF 下载当前返回 502，均暂不并入。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 厦门大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 177 | 0 |

可追溯来源：
- 厦门大学材料学院 2026 年硕士研究生拟录取名单：`https://cm.xmu.edu.cn/info/1271/25755.htm`
- 厦门大学环境与生态学院/海洋与海岸带发展研究院 2026 年硕士研究生拟录取名单：`https://cee.xmu.edu.cn/info/1051/40415.htm`
- 本轮留证但未入库：大连外国语大学接收 2026 年推免生拟录取名单公示 `https://gd.dlufl.edu.cn/info/1013/2921.htm`
- 本轮留证但未入库：青岛理工大学 2026 年硕士研究生拟录取名单（含推免） `https://yjsh.qut.edu.cn/info/1406/3291.htm`
- 本轮留证但未入库：电子科技大学信息与通信工程学院 2026 年推免生拟录取名单 `https://www.sice.uestc.edu.cn/info/1142/15723.htm`

质量修正：
- 新增厦门大学分段 PDF 专项解析，识别“专业代码和专业名称：080500材料科学与工程”等专业段落，并把后续人员行挂到对应专业。
- 修正通用解析只抽姓名/考生编号/成绩、缺少 `admission_major` 导致全量 `needs_review` 的问题；本批 177 条均保留专业代码、专业名称、初试总分、复试成绩、总成绩、学习方式和录取类别。

数据包同步更新：
- B 类官网清洗表：199,495 条，311 个学校/年份/类型汇总组。
- A+B 统一清洗表：205,205 条，463 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 274 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：236 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 464 行（含表头）、Coverage 431 行（含表头）、Public_Records 205,206 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch161 江西师范/广州美术/新疆农业/河北/宁波

batch161 使用已验证的官网名单页做种子，重新跑入干净目录，覆盖江西师范大学、广州美术学院、新疆农业大学、河北大学和宁波大学。此前 batch159 中沈阳师范大学页面正文只能抽到推免工作组/联系方式，学生名单在图片中，暂不并入；若要补该校需要单独 OCR。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 江西师范大学 | 2024 | postgraduate_admission_list | postgraduate_exam_or_admission | 212 | 0 |
| 江西师范大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 202 | 0 |
| 江西师范大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 347 | 0 |
| 江西师范大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 79 | 0 |
| 江西师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 477 | 0 |
| 广州美术学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 46 | 0 |
| 新疆农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 35 | 0 |
| 河北大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 66 | 0 |
| 宁波大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 165 | 0 |

可追溯来源：
- 江西师范大学公示栏目：`https://yz.jxnu.edu.cn/6248/list.htm`
- 江西师范大学 2026 年推免生接收名单 PDF：`https://yz.jxnu.edu.cn/_upload/article/files/45/86/efc27e5c4978b4822fbde828963d/d9ad60df-0ca4-4af4-b100-388d34f52fd6.pdf`
- 江西师范大学 2026 届优秀本科毕业生获得推荐免试攻读研究生资格名单 PDF：`https://yz.jxnu.edu.cn/_upload/article/files/55/c2/03f237804daf95f7eab591e83bd9/44c6e346-66dc-47d5-abd3-720adfe02041.pdf`
- 广州美术学院 2026 年接收推免硕士拟录取名单：`https://zs.gzarts.edu.cn/info/1038/4249.htm`
- 新疆农业大学 2026 年硕士研究生（推免生）拟录取名单：`https://yjsc.xjau.edu.cn/2025/1017/c2155a110462/page.htm`
- 河北大学 2026 年拟录取推免研究生名单：`https://yjsy.hbu.edu.cn/info/1114/4087.htm`
- 宁波大学 2026 年拟接收推荐免试研究生公示：`https://graduate.nbu.edu.cn/info/1073/25521.htm`

质量修正：
- 新增“推免拟录取/推免拟录取名单”分类关键词，避免宁波大学 PDF 被归入统考拟录取。
- 新增宁波大学 PDF 专项解析，按“姓名/性别/复试成绩/接收学院/接收专业代码/接收专业名称/录取类型”抽取，修正学院、专业代码和专业名称错位。
- 新增江西师范大学推免资格/推免接收 PDF 专项解析，过滤页眉页码和拆分表头，保留学院代码、学院名称、专业代码、专业名称、性别、综合成绩或备注。

数据包同步更新：
- B 类官网清洗表：199,318 条，310 个学校/年份/类型汇总组。
- A+B 统一清洗表：205,028 条，462 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 273 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：235 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 463 行（含表头）、Coverage 431 行（含表头）、Public_Records 205,029 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch158 海南医科大学推免名单

batch158 继续处理 B 类缺口院校。海南医科大学 2026 年接收推荐免试攻读硕士研究生复试考核成绩及拟录取名单官网页公开可访问，附件为 VSB `download.jsp` xlsx。此前 crawler 使用固定外部 Referer 时会拿到验证码桥页；本批修正为跟进附件时使用父页面作为 Referer，并过滤“上一篇/下一篇”导航链接，避免混入复试名单页面。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 海南医科大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 21 | 0 |

可追溯来源：
- 海南医科大学 2026 年接收推荐免试攻读硕士研究生复试考核成绩及拟录取名单（一）：`https://www.muhn.edu.cn/zsw/info/1091/10434.htm`
- 海南医科大学 xlsx 附件下载入口：`https://www.muhn.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1698349489&wbfileid=533C403A675D3C31AD5FBA3FACF6D8C0`

质量修正：
- 新增父页面 Referer 传递，支持此类 VSB 附件直接下载为 xlsx。
- 新增“姓名/身份证号/报考学院/报考专业/学位类型/学习方式/复试成绩/录取状态”Excel 表专项解析，保留脱敏身份证号、复试成绩、录取状态等字段。
- 新增“上一篇/下一篇”等文章导航链接过滤，避免同站相邻公告被误纳入当前批次。

数据包同步更新：
- B 类官网清洗表：197,689 条，301 个学校/年份/类型汇总组。
- A+B 统一清洗表：203,399 条，453 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 268 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：231 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 454 行（含表头）、Coverage 431 行（含表头）、Public_Records 203,400 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch156 南方医科大学推免名单

batch156 继续处理 B 类缺口院校。南方医科大学 2026 年招收推荐免试研究生拟录取名单官网页公开可访问，PDF 附件进入 VSB 验证码下载桥；已人工下载附件。该 PDF 在 Windows 下 `pdftotext` 输出为 GBK 字节，本批新增 `pdftotext` 编码回退和南方医科大学表格专项解析，保留身份证后 6 位、分委会、专业代码、专业名称、研究方向、学位类型、复试成绩和类别字段。

湖南大学同批官网页和 PDF 附件也已抓取，但 PDF 为扫描图像型，当前未将低可信 OCR 结果并入清洗表。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 南方医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 597 | 0 |

可追溯来源：
- 南方医科大学 2026 年招收推荐免试研究生拟录取名单公示：`https://portal.smu.edu.cn/yzw/info/1002/11811.htm`
- 南方医科大学附件下载入口：`https://portal.smu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1322327945&wbfileid=B12A2A520BE4CBEA794194760B200EF6`
- 湖南大学 2026 年推荐免试研究生拟录取名单公示（已抓取原始 PDF，未结构化入表）：`https://gra.hnu.edu.cn/info/1075/10263.htm`

质量修正：
- 新增 `pdftotext` 输出解码回退，在 UTF-8 解码失败或替换字符过多时尝试 GB18030/GBK。
- 新增南方医科大学 PDF 专项解析，支持 `0710J3`、`0831Z1`、`1001Z1` 等含字母专业代码。
- batch156 清洗表 597 条；缺少人员姓名 0，缺少身份证后 6 位 0，缺少专业字段 0，需人工复核 0。

数据包同步更新：
- B 类官网清洗表：197,668 条，300 个学校/年份/类型汇总组。
- A+B 统一清洗表：203,378 条，452 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 267 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：228 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 453 行（含表头）、Coverage 431 行（含表头）、Public_Records 203,379 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch155 北京语言大学

batch155 继续处理 B 类缺口院校。北京语言大学官网 2026 年硕士推免生（含直博）拟录取名单页面公开可访问，两个 PDF 附件进入 VSB 验证码下载桥；已人工下载附件，并新增北京语言大学 PDF 专项解析以保留脱敏身份证号、专业代码、复试成绩和直博导师字段。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 北京语言大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 286 | 0 |

可追溯来源：
- 北京语言大学关于公布 2026 年硕士推免生（含直博）拟录取名单的通知：`https://yjsy.blcu.edu.cn/info/1071/6569.htm`

质量修正：
- 新增北京语言大学 PDF 专项解析，修正通用解析遗漏身份证号/成绩的问题。
- 过滤 PDF 页脚“第 1 页，共 1 页”和官网页脚“友情链接/常用链接”等非人员字段。
- batch155 清洗表 286 条；缺少人员姓名 0，缺少证件号 0，缺少专业字段 0，需人工复核 0。

数据包同步更新：
- B 类官网清洗表：197,071 条，299 个学校/年份/类型汇总组。
- A+B 统一清洗表：202,781 条，451 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 266 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：226 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 452 行（含表头）、Coverage 431 行（含表头）、Public_Records 202,782 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-25 追加批次：batch154 西南林业/天津体育/哈尔滨体育

batch154 继续处理 B 类缺口院校。本批官网页面均可公开访问，但 PDF 附件进入 VSB 验证码下载桥；已人工下载附件并新增 3 个小表格 PDF 解析规则，避免通用解析把表头或考生编号错当作专业字段。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南林业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 | 0 |
| 天津体育学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 50 | 0 |
| 哈尔滨体育学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 8 | 0 |

可追溯来源：
- 西南林业大学 2026 年推荐免试研究生（含直博生）拟录取名单公示：`https://yjsy.swfu.edu.cn/info/1522/10996.htm`
- 天津体育学院 2026 年接收优秀应届本科毕业生免试攻读硕士研究生拟录取名单公示：`https://yjsb.tjus.edu.cn/info/1004/4527.htm`
- 哈尔滨体育学院 2026 年硕士研究生接收推免生拟录取名单公示：`https://www.hrbipe.edu.cn/yjsy/info/1011/1634.htm`

质量修正：
- 新增西南林业大学 PDF 解析，按“序号/考生编号/姓名/层次/院系/专业/成绩/录取类别”抽取。
- 新增天津体育学院 PDF 解析，保留脱敏身份证号、复试分数和报考专业。
- 新增哈尔滨体育学院 PDF 解析，过滤跨行表头“考试成绩”，保留考生编号、专业和复试成绩。

数据包同步更新：
- B 类官网清洗表：196,785 条，298 个学校/年份/类型汇总组。
- A+B 统一清洗表：202,495 条，450 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 265 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：224 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 451 行（含表头）、Coverage 431 行（含表头）、Public_Records 202,496 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-25 追加批次：batch153 西南交通大学

本轮继续处理 B 类缺口院校。batch153 覆盖西南交通大学、中山大学、北京语言大学、华东师范大学、华东理工大学、上海中医药大学等入口；其中西南交通大学推免拟录取附件需要 VSB 验证码，已人工下载并新增专项解析。北京语言大学多个名单附件同样进入验证码桥页，华东师范大学和华东理工大学页面为公示已结束或图片名单，中山大学入口返回 404，本轮暂未入库。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南交通大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 1,815 | 0 |

质量修正：
- 新增西南交通大学推免 PDF 专项解析，按“姓名/证件号码/招生类型/录取院系所/录取专业代码/录取专业名称/复试成绩”抽取。
- 处理 PDF 文本层中个别“姓名+证件号”与后续列分行的情况。
- batch153 清洗表缺少人员姓名 0，缺少证件号 0，缺少专业字段 0，需人工复核 0。

数据包同步更新：
- B 类官网清洗表：196,725 条，295 个学校/年份/类型汇总组。
- A+B 统一清洗表：202,435 条，447 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 262 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch152 云南师范/新疆大学/云南农业大学

本轮继续从 B 类未覆盖院校中筛选官网名单入口。batch152 通过搜索命中的官网栏目页和学院页新增云南师范大学、新疆大学、云南农业大学三校记录；其中云南师范大学附件需要 VSB 验证码下载，已人工取得 PDF 并新增专项解析。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 云南师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,016 | 4 |
| 新疆大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 162 | 0 |
| 云南农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 12 | 0 |

质量修正：
- 新增云南师范大学硕士拟录取 PDF 专项解析，修正“学院代码/学院名称/专业代码/专业名称”错位问题。
- 修复清洗去重逻辑：同校同专业同名但考生编号不同的记录不再被误合并。
- 云南师范大学 PDF 中 4 行因文本层缺少学习方式或成绩，已保留人员信息并标记 `needs_review=True`。

数据包同步更新：
- B 类官网清洗表：194,910 条，294 个学校/年份/类型汇总组。
- A+B 统一清洗表：200,620 条，446 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 261 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch144-batch151 昆明理工大学

本轮继续优先处理 B 类高校官网来源。batch144-batch150 复核青岛理工大学、齐鲁工业大学、山东中医药大学、中国石油大学（华东）、浙江工商大学、杭州师范大学、北京电影学院、北京服装学院、沈阳航空航天大学、沈阳师范大学、大连外国语大学、辽宁石油化工大学、中国地质大学（武汉）、武汉理工大学、武汉纺织大学、武汉体育学院、武汉轻工大学、浙江财经大学、华中师范大学等缺口入口，多数为 404/410、站点提示页、扫描 PDF 或 VSB `download.jsp` 验证码桥，未形成可自动入库记录。batch151 对昆明理工大学官网公示页的验证码附件做人工下载复核，并新增 5,652 条 2026 年硕士研究生拟录取人员级记录。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 昆明理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 5,652 | 0 |

质量修正：
- 新增昆明理工大学硕士拟录取 PDF 专项解析，处理 PDF 文本层中的姓名、学习方式、录取类别和专业名称跨行空格。
- 校验源 PDF 序号 1-5652 连续无缺口；清洗表缺少人员姓名 0、缺少考生编号 0、缺少录取专业 0、需人工复核 0。
- 因该附件需要验证码下载，记录的 `source_url` 统一指向可公开核验的官网公示页。

数据包同步更新：
- B 类官网清洗表：191,720 条，291 个学校/年份/类型汇总组。
- A+B 统一清洗表：197,430 条，443 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 258 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch137-batch143 山西医科/辽宁大学/北京外国语大学

本轮继续优先处理 B 类高校官网来源。batch137 从山西医科大学药学院 HTML 表格新增 19 条 2026 年推免硕士拟录取记录；batch138 复抓辽宁大学官方 PDF，和既有记录去重后补入 2 条漏行；batch143 从北京外国语大学 2026 年硕士研究生调剂拟录取结果公示页新增 36 条记录。batch139-batch142 中南京理工大学、中国药科大学等页面返回 410/404，北京语言大学与北京协和医学院附件进入验证码下载桥，同济大学公示系统显示“尚未开放”，北外“硕博连读”记录暂不并入本硕升学主表。

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山西医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 19 | 0 |
| 辽宁大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 | 0 |
| 北京外国语大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 36 | 0 |

数据包同步更新：
- B 类官网清洗表：186,068 条，290 个学校/年份/类型汇总组。
- A+B 统一清洗表：191,778 条，442 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 257 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch135/batch136b 验证码阻断与重庆医科大学

batch135 复核黑龙江大学和湖南大学官网拟录取/推免公示入口，但两校附件下载均进入 VSB 验证码桥页，未形成可自动入库记录。batch136b 转向重庆医科大学第一临床学院官网页面，来源页自动发现 18 个 PDF，并新增 185 条 2026 年硕士研究生第一志愿拟录取人员级记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 重庆医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 185 | 0 |

质量修正：
- 新增重庆医科大学第一临床学院 PDF 专项解析，只保留“是否拟录取=是”的人员行。
- batch136b 清洗表缺少人员姓名 0，缺少考生编号 0，缺少专业字段 0，需人工复核 0。

数据包同步更新：
- B 类官网清洗表：186,011 条，288 个学校/年份/类型汇总组。
- A+B 统一清洗表：191,721 条，440 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 256 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch130 西南大学学院页展开

batch130 继续处理未覆盖院校。西南大学、电子科技大学、中国海洋大学等官网存在全校拟录取名单总入口；其中西南大学和电子科技大学总入口均为跨学院子域名链接清单，当前先将总入口中的学院链接展开为种子。最终可稳定入库记录来自西南大学外国语学院和音乐学院；电子科技大学多处页面/附件为下载桥或当前通用解析器未能直接抽取人员级表格，中国海洋大学直链 PDF 返回 403，暂不并入。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 129 | 0 |

质量修正：
- 将西南大学总入口中的跨学院链接展开为二级种子。
- 过滤学院页面菜单/页脚字段，避免“下载中心/主题教育/党务公开/位置导航/邮编/辅修”等混入人员名单。

数据包同步更新：
- B 类官网清洗表：172,176 条，279 个学校/年份/类型汇总组。
- A+B 统一清洗表：177,886 条，431 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 250 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch129 海南师范大学/福建中医药大学/福建医科大学/首都经济贸易大学

batch129 继续从未覆盖院校中筛选官方静态名单入口，种子覆盖东北师范大学、首都经济贸易大学、天津财经大学、海南师范大学、海南医科大学、福建医科大学和福建中医药大学。最终可结构化入库记录来自海南师范大学、福建中医药大学、福建医科大学和首都经济贸易大学；海南医科大学附件当前返回下载桥页，天津财经大学其中一个入口返回 404，东北师范大学本轮入口未形成可解析人员级表格。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 海南师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,331 | 0 |
| 福建中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 868 | 0 |
| 福建医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 156 | 0 |
| 首都经济贸易大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 182 | 0 |

质量修正：
- 新增海南师范大学硕士/博士拟录取 PDF、福建医科大学推免拟录取 PDF、福建中医药大学统考硕士 PDF、首都经济贸易大学博士拟录取 PDF 的专项解析规则。
- 过滤海南医科大学页面中的体检项目，避免“体重/血常规/肝功能”等非人员字段混入名单。
- 福建中医药大学 PDF 的 868 条已完整抽取；其中 304 条因源 PDF 换行破碎，仅可靠保留专业代码，后续如需要可继续做人工映射补全专业名称。

数据包同步更新：
- B 类官网清洗表：172,047 条，278 个学校/年份/类型汇总组。
- A+B 统一清洗表：177,757 条，430 个学校/年份/类型汇总组。
- 官网覆盖追踪：430 所院校中 249 所已精确匹配官网记录。
- Excel 交付版：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch128 上海师范大学/安徽财经大学

batch128 继续从未覆盖院校中筛选官方静态名单入口，种子覆盖南京师范大学、上海师范大学、安徽财经大学、北京第二外国语学院和南京邮电大学。上海师范大学数理学院主页可追到 2026 年硕士研究生调剂拟录取名单 PDF，安徽财经大学研究生招生信息网可追到 2026 年推免递补名单正文；南京师范大学附件下载为 HTML 下载桥或无可解析文本，南京邮电大学页面为工作安排/公告壳，北二外栏目本轮未发现静态人员级名单，暂不并入。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 172 | 0 |
| 安徽财经大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 | 0 |

质量修正：
- 修复 PDF 表格中“考生编号 + 调剂专业名称”粘在同一列、下一列为“非定向就业”时的错位，避免把就业方式误写入 `admission_major`。
- 新增安徽财经大学推免递补正文键值解析，将“姓名/专业名称/综合成绩”等行合成为人员级记录。
- 过滤“组长/副组长/成员/工作职责/特此通知”等推荐工作通知噪声，避免工作小组成员或正文尾句混入人员名单。

本批最终并入 B 类官网主表 174 条。合并后交付版同步更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：169,510 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：169,510 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：175,220 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：175,220 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：426 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，245 所已精确匹配官网记录

## 2026-05-25 追加批次：batch127 山东财经大学

batch127 继续从未覆盖院校中筛选官方静态名单入口，种子覆盖厦门大学、华东理工大学、杭州师范大学、广东药科大学、山西财经大学、华北理工大学、山东财经大学、山东农业大学、河北大学等。华东理工大学名单主体为图片，山西财经大学和河北大学附件进入验证码下载桥，厦门大学、杭州师范大学、广东药科大学等入口实时返回 404，山东农业大学学院页返回 403 或章程页，未形成可结构化人员级记录。本批可入库来源集中在山东财经大学研究生招生信息网内嵌 VSB PDF。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山东财经大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 6 | 0 |

质量修正：
- 将 `virtual_attach_file.vsb?...&e=.pdf` 识别为附件链接，使 VSB 内嵌 PDF 能被继续下载解析。
- 新增山东财经大学博士拟录取 PDF 专项解析，处理“录取专业代码/名称”跨行和“录取学院”跨行，避免导师姓名误入 `admission_major`。
- 扩充官网列表页分类关键词，识别“拟录取考生名单/待录取考生名单”，避免同类公告页在列表页阶段被漏掉。

本批最终并入 B 类官网主表 6 条。合并后交付版同步更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：169,336 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：169,336 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：175,046 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：175,046 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：424 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，243 所已精确匹配官网记录

## 2026-05-25 追加批次：batch126 东华理工/吉林师范/大连工业/桂林电子科技

batch126 继续从未覆盖院校中筛选官方静态名单入口，种子覆盖渤海大学、东华理工大学、吉林师范大学、桂林电子科技大学、大连工业大学、电子科技大学、华东交通大学、哈尔滨师范大学等。可入库来源集中在东华理工大学推免 PDF、吉林师范大学推免 HTML 公示、大连工业大学推免/拟录取 Excel，以及桂林电子科技大学校级硕士拟录取公示页展开的 81 份学院 PDF；渤海大学、电子科技大学、华东交通大学、哈尔滨师范大学等入口本轮未形成静态可解析人员级记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 桂林电子科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,227 | 0 |
| 大连工业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 31 | 0 |
| 东华理工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 11 | 0 |
| 吉林师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 3 | 0 |

质量修正：
- 新增桂林电子科技大学 PDF 专项解析，处理“学院+考号”“考号+姓名”“序号单独占行”“专业代码+专业名+初试分数”多种 `pdftotext` 拆行形态，避免专业名误作姓名、考号误入学院字段。
- 修正通用表头映射，将“录取专业代码”写入 `major`、“录取专业名称”写入 `admission_major`，并识别“毕业单位”为 `undergraduate_school`。

本批最终并入 B 类官网主表 2,272 条。合并后交付版同步更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：169,330 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：169,330 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：175,040 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：175,040 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：423 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，242 所已精确匹配官网记录

## 2026-05-25 追加批次：贵州医科/广西艺术/兰州交通/广州医科 batch125

batch125 继续从剩余未覆盖院校中筛选官方静态 PDF 和公告入口，种子包括北京服装学院、东北电力大学、黑龙江中医药大学、贵州医科大学、广西艺术学院、西南交通大学、广州医科大学、华东交通大学和兰州交通大学等。可入库来源集中在贵州医科大学 3 份硕士拟录取 PDF、广西艺术学院一志愿/调剂复试成绩及拟录取 PDF、兰州交通大学两个学院 PDF，以及广州医科大学附属番禺中心医院 HTML 公告；东北电力、黑龙江中医药、西南交通、华东交通等入口本轮仍未形成静态可解析人员级记录。

本批新增三类 PDF 专项解析：贵州医科大学解析“学院代码/名称、专业代码/名称、研究方向代码/名称、初试/复试/总成绩”，避免研究方向代码 `00` 误入 `admission_major`；广西艺术学院解析跨行列头和“学术/专业 + 学位”拆行版式，只保留拟录取行；兰州交通大学解析“考生编号 / 姓名 / 拟录取专业代码 / 拟录取专业名称”，避免专业字段只剩代码。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 贵州医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,437 | 0 |
| 广西艺术学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 305 | 0 |
| 兰州交通大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 176 | 0 |
| 广州医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2 | 0 |

主要入口：

- 贵州医科大学 2026 年硕士考试一志愿考生拟录取名单公示：`https://yjsxy.gmc.edu.cn/info/1118/2465.htm`
- 贵州医科大学 2026 年硕士研究生调剂拟录取名单公示（一）：`https://yjsxy.gmc.edu.cn/info/1118/2479.htm`
- 广西艺术学院 2026 年硕士研究生招生一志愿复试成绩及拟录取名单：`https://zsb.gxau.edu.cn/yjszs/tzgg1/content_314769`
- 兰州交通大学自动化与电气工程学院拟录取名单 PDF：`https://dqxy.lzjtu.edu.cn/__local/5/09/74/C017F3F87EA00B3FE66396680E1_9CD8D819_2FF2C.pdf`
- 广州医科大学附属番禺中心医院校外调剂拟录取名单：`https://www.pyhospital.com.cn/show.php?id=4312`

本批合并后交付版：

- B 类官网总表：167,058 条清洗记录，267 个学校/年份/文档类型汇总组
- 统一清洗包：172,768 条记录，419 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，238 所已精确匹配官网记录，192 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：徐州医科大学/浙江理工大学 batch124

batch124 继续从未覆盖院校中筛选官网列表页、拟录取公告页和 PDF 直链，种子包括徐州医科大学、中国医科大学、中国药科大学、皖南医学院、温州医科大学、浙江工商大学、浙江理工大学、福建医科大学、南方医科大学等。首轮命中中存在旧链接 404、附件验证码下载桥和页面导航噪声；修正为 batch124b/batch124c 后，徐州医科大学和浙江理工大学形成可入库人员级记录。

本批新增两类 PDF 专项解析：徐州医科大学硕士拟录取名单为“考生编号 / 姓名 / 初试成绩 / 复试成绩 / 总成绩 / 备注”版式，源文件本身没有专业列，因此保留姓名、脱敏考号与成绩到 `remarks`，并标记 `missing_major;needs_review`；浙江理工大学拟录取名单为“报名号 / 考生姓名 / 综合考核总成绩 / 拟录取专业 / 录取类别 / 学位类型 / 备注”版式，录取专业写入 `admission_major`，总成绩、录取类别和学位类型写入 `remarks`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 徐州医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,391 | 1,391 |
| 浙江理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 164 | 0 |

主要入口：

- 徐州医科大学 2026 年硕士研究生招生复试拟录取名单相关公告：`https://yjs.xzhmu.edu.cn/info/1247/7093.htm`
- 徐州医科大学 2026 年硕士研究生招生复试拟录取名单相关公告：`https://yjs.xzhmu.edu.cn/info/1247/7107.htm`
- 浙江理工大学 2026 年硕士研究生拟录取名单公示：`https://gradadmission.zstu.edu.cn/info/1011/3347.htm`

本批合并后交付版：

- B 类官网总表：165,138 条清洗记录，263 个学校/年份/文档类型汇总组
- 统一清洗包：170,848 条记录，415 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，234 所已精确匹配官网记录，196 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：宁夏医科大学 batch122

batch122 继续从未覆盖院校中筛选官网硕士拟录取名单入口，种子包括青岛理工大学、山东财经大学、山东理工大学、山东农业大学、山东师范大学、齐鲁工业大学、宁夏医科大学和三峡大学。多数页面只保留公告壳、公示结束提示或未暴露可下载名单；宁夏医科大学研究生院硕士招生栏目可追到 2026 年硕士研究生招生调剂考生拟录取名单 PDF，形成 74 条可结构化人员级记录。

本批新增宁夏医科大学 PDF 专项解析，保留考生编号、姓名、录取院系所代码/名称、录取专业代码/名称、研究方向、初试总分、复试总成绩、录取成绩和专项计划。并入后 B 类官网主表为 163,473 条，A+B 统一清洗包为 169,183 条，覆盖追踪提升到 231/430 所。

## 2026-05-25 追加批次：济南大学 batch123

batch123 继续筛选未覆盖院校中的官网列表页与拟录取入口，种子包括聊城大学、江西师范大学、济南大学、上海理工大学、上海师范大学、南京理工大学、南京邮电大学、山西医科大学、山西中医药大学和山东中医药大学等。多数入口未暴露可结构化人员级名单；江西师范大学抓到的 2026 PDF 为推免名额/专业分配表，已通过清洗规则剔除，未并入人员级主表。济南大学官网 PDF 形成 110 条 2026 年博士研究生拟录取人员级记录。

本批新增济南大学 PDF 专项解析，保留考生编号、姓名、报考院系代码/名称、报考专业代码/名称、学习形式和考试方式。并入后 B 类官网主表为 163,583 条，A+B 统一清洗包为 169,293 条，覆盖追踪提升到 232/430 所。

## 2026-05-25 追加批次：上海应用技术大学 batch111

batch111 继续筛选剩余缺口院校中当前官网仍可访问的名单页。南京财经大学、南方医科大学页面可访问但名单附件进入验证码下载桥；杭州师范大学搜索命中页本地返回 404；上海海事大学页面仅保留“公示已结束”说明而无人员级明细，均暂未并入。上海应用技术大学研究生院通知公告列表可追到 2026 年接收推免生拟录取名单 HTML 表格，形成 8 条可结构化人员级记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海应用技术大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 8 | 0 |

主要入口：

- 上海应用技术大学研究生招生通知公告列表：`https://gs.sit.edu.cn/zsxx/tzgg.htm`
- 上海应用技术大学 2026 年接收优秀应届本科毕业生免试攻读硕士研究生拟录取名单公示：`https://gs.sit.edu.cn/info/1271/9982.htm`

本批合并后交付版：

- B 类官网总表：160,818 条清洗记录，250 个学校/年份/文档类型汇总组
- 统一清洗包：166,528 条记录，402 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，223 所已精确匹配官网记录，207 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- batch111 清洗表：8 条，0 条需复核，姓名/专业缺失 0 条，数字专业误读 0 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 166,529 行（含表头），公开明细 166,528 行。

## 2026-05-25 追加批次：北华大学/贵州民族大学 batch110b/batch110c

batch110 继续从缺口院校中筛选官方研究生院/招生网站入口。北京电影学院返回 412，大连外国语大学、海南医科大学、黑龙江中医药大学等页面只暴露附件下载桥，附件下载页要求验证码；华东理工大学为图片名单，当前无本地 OCR 链路，均暂未并入。batch110b/batch110c 从可静态解析的 HTML 表格中补入北华大学 8 条、贵州民族大学 7 条 2026 年推免/拟录取人员级记录。

本批新增两类表头解析规则：`姓名 + 报考专业代码 + 报考专业名称 + 报考学习形式 + 复试成绩`，以及 `拟录取学院 + 考生姓名 + 拟录取专业代码 + 拟录取专业`。修复后专业代码进入 `major`，代码和专业名合并进入 `admission_major`，学习形式、复试成绩或性别进入 `remarks`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 北华大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 8 | 0 |
| 贵州民族大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 7 | 0 |

主要入口：

- 北华大学 2026 年推免生复试拟录取名单公示：`https://grad.beihua.edu.cn/info/1071/3062.htm`
- 贵州民族大学 2026 年接收推荐免试攻读硕士研究生拟录取名单公示：`https://yjsy.gzmu.edu.cn/info/1084/5986.htm`

本批合并后交付版：

- B 类官网总表：160,810 条清洗记录，249 个学校/年份/文档类型汇总组
- 统一清洗包：166,520 条记录，401 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，222 所已精确匹配官网记录，208 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：177 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch110c 清洗表：15 条，0 条需复核，姓名/专业缺失 0 条，数字专业误读 0 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 166,521 行（含表头），公开明细 166,520 行。

## 2026-05-25 追加批次：广东财经大学 batch109/batch109b

batch109 先用搜索命中的官方入口复核广东财经大学、桂林电子科技大学、电子科技大学、华中科技大学、东北师范大学、中央民族大学等缺口。桂林电子科技大学页面静态正文未暴露人员名单表格，华中科技大学附件下载需要验证码，东北师范大学页面未保留人员级明细，电子科技大学和中央民族大学候选地址本地返回 404，均暂未并入。广东财经大学研究生招生办公室“硕士拟录取状态信息表”列表可访问，batch109b 抽取 39 个官方详情页并跟进 PDF 附件，最终形成 40 个附件来源的 2026 年硕士拟录取人员级数据。

广东财经大学 PDF 表格存在多种宽表版式：部分“学院名称”被 PDF 文本抽取拆到上一行/下一行，部分表含“专业与情景化面试、无领导小组面试、思想政治理论、复试总分、专业排名”等额外列。已新增专项解析规则，只保留状态列含“拟录取”的行，剔除“候选”和“不予录取”，并避免把初试/复试分数误写为专业字段。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 广东财经大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,195 | 0 |

主要入口：

- 广东财经大学 2026 年硕士拟录取状态信息列表：`https://yzb.gdufe.edu.cn/4695/list.htm`
- 广东财经大学 2026 年硕士拟录取状态信息列表第 2 页：`https://yzb.gdufe.edu.cn/4695/list2.htm`

本批合并后交付版：

- B 类官网总表：160,795 条清洗记录，247 个学校/年份/文档类型汇总组
- 统一清洗包：166,505 条记录，399 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，220 所已精确匹配官网记录，210 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：175 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch109b_fixed2 清洗表：1,195 条，0 条需复核，姓名/专业缺失 0 条，数字专业误读 0 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 166,506 行（含表头），公开明细 166,505 行。

## 2026-05-25 追加批次：河北工程/河北经贸/上海财经 batch106-108b

batch106/b 继续补河北缺口，成功补入河北工程大学 8 条、河北经贸大学 4 条 2026 年拟录取推免生人员级记录。batch107 试探华东政法大学、上海师范大学、上海财经大学校级页面：华东政法大学页面仅保留拟录取 377 名的公告正文但无名单明细，上海师范大学页面写明“名单见下附件”但静态页面无附件链接，上海财经大学校级 AnyShare 外链接口返回“外链不存在”，均暂未并入。随后 batch108b 转向上海财经大学院系官网最终/候补名单，补入商学院 130 条、会计学院 92 条。上财预报名考核名单和报名通知只作为抓取证据保留，未并入交付主表；会计学院 PDF 中水印导致错位的低信息行已剔除。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河北工程大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 8 | 0 |
| 河北经贸大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 4 | 0 |
| 上海财经大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 222 | 0 |

可追溯来源：

- 河北工程大学 2026 年拟录取推免生名单：`https://yanjs.hebeu.edu.cn/info/1089/9213.htm`
- 河北经贸大学 2026 年拟录取推免生名单：`https://yjs.hueb.edu.cn/info/1016/3465.htm`
- 上海财经大学商学院 2026 年推荐免试研究生拟录取及候补资格名单：`https://cob.sufe.edu.cn/Home/Detail/26771`
- 上海财经大学会计学院 2026 年推荐免试研究生拟录取及候补资格名单 PDF：`https://sa.sufe.edu.cn/_upload/article/files/f0/c0/68bd751149f0b2bf2d39864eb4b0/ef1594c6-8f1c-43ef-b497-8a2ebf92491a.pdf`

本批合并后交付版：

- B 类官网总表：159,600 条清洗记录，246 个学校/年份/文档类型汇总组
- 统一清洗包：165,310 条记录，398 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，219 所已精确匹配官网记录，211 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：173 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch106 合并清洗表：12 条；batch108b 上财最终/候补名单子集：222 条，0 条需复核
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 165,311 行（含表头），公开明细 165,310 行。

## 2026-05-25 追加批次：广州中医药大学 batch105b

batch104/b 先试探安徽财经大学、北京协和医学院、北京语言大学、大连外国语大学、东北师范大学、东华理工大学和电子科技大学等官网入口，其中部分页面返回 403/404/502，部分页面抓取成功但为验证码附件、空公示系统或无人员级正文表格，暂未并入。随后 batch105 转向广东、广西、海南等剩余缺口院校，batch105b 使用修正后的嵌套表格解析器，成功补入广州中医药大学 2026 年推免生拟录取名单 319 条人员级记录。该页面字段包含考生姓名、院所名称、录取专业代码/名称、研究方向和接收导师。

batch105b 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 广州中医药大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 319 | 0 |

可追溯来源：

- 广州中医药大学 2026 年推免生拟录取名单公示：`https://yjsy.gzucm.edu.cn/info/1004/17006.htm`

本批合并后交付版：

- B 类官网总表：159,366 条清洗记录，243 个学校/年份/文档类型汇总组
- 统一清洗包：165,076 条记录，395 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，216 所已精确匹配官网记录，214 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：172 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch105b 清洗表：319 条，0 条需复核；公开版 319 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 165,077 行（含表头），公开明细 165,076 行。

## 2026-05-25 追加批次：西藏大学 batch103c

batch103 先试探甘肃农业大学、福建医科大学、新疆农业大学和兰州大学等入口，其中福建医科大学、新疆农业大学、青海大学、海南师范大学页面或附件抓取成功但未形成可解析人员级记录，兰州大学附件直链本地返回 502。随后 batch103c 转向西藏大学，成功补入校级 PDF 与信息科学技术学院官网正文名单，共 90 条人员级记录。校级 PDF 字段包含姓名、学院和专业；学院正文名单字段包含姓名、学号、专业和排名。两份来源中有 1 个同名人员重复出现，暂按不同来源保留，后续可做跨来源同名融合。

batch103c 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西藏大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 90 | 0 |

可追溯来源：

- 西藏大学拟推荐免试研究生名单公示 PDF：`https://jwc.utibet.edu.cn/__local/E/66/E7/23629DEA8469E25E771D56820DA_A2CA05DB_7F72B.pdf?e=.pdf`
- 西藏大学信息科学技术学院拟推荐 2026 届优秀应届本科毕业生免试攻读硕士学位研究生学生名单公示：`https://it.utibet.edu.cn/info/1021/1561.htm`

本批合并后交付版：

- B 类官网总表：159,047 条清洗记录，242 个学校/年份/文档类型汇总组
- 统一清洗包：164,757 条记录，394 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，215 所已精确匹配官网记录，215 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：171 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch103c 清洗表：90 条，0 条需复核；公开版 90 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 164,758 行（含表头），公开明细 164,757 行。

## 2026-05-25 追加批次：河北北方学院 batch102

batch102 转向河北缺口院校。本轮成功补入河北北方学院 2026 年推免相关官方 PDF 两份，共 100 条人员级记录：教务处本科推免推荐名单 86 条，字段包含姓名、学号、学院和本科专业；研究生院免试攻读硕士研究生拟录取第一批名单 14 条，字段包含姓名、拟录取专业代码和学习方式。河北经贸大学候选入口本地抓取返回 502；河北大学、河北农业大学等后续种子因慢请求拖长，本轮中断后未并入。

batch102 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河北北方学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 100 | 0 |

可追溯来源：

- 河北北方学院 2026 年免试攻读硕士研究生拟录取名单第一批 PDF：`https://yjs.hebeinu.edu.cn/uploads/file1/20251009/68e77d75d9a23.pdf`
- 河北北方学院关于 2026 年拟推荐优秀应届本科毕业生免试攻读研究生名单的公示 PDF：`https://jwc.hebeinu.edu.cn/upload/file/20250912/1757648381176731.pdf`

本批合并后交付版：

- B 类官网总表：158,957 条清洗记录，241 个学校/年份/文档类型汇总组
- 统一清洗包：164,667 条记录，393 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，214 所已精确匹配官网记录，216 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：171 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch102 清洗表：100 条，0 条需复核；公开版 100 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 164,668 行（含表头），公开明细 164,667 行。

## 2026-05-25 追加批次：安徽大学 batch101/batch101b

batch101 继续面向未覆盖院校补 B 类官网材料。本轮成功补入安徽大学 2026 年拟录取推免生公示名单 PDF。该 PDF 为“姓名、性别、毕业单位、拟录取学院、拟录取专业、考核成绩、备注”版式，原通用 PDF 表格解析会把性别、本科院校和成绩错位；本轮新增专项回归测试和解析规则后，清洗表中姓名不再带性别，本科院校、拟录取学院、拟录取专业和考核成绩均落到可用字段。为避免同一输出目录追加旧记录，修正后的干净产物使用 `batch101b` 目录。

batch101b 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 安徽大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 532 | 0 |

可追溯来源：

- 安徽大学 2026 年拟录取推免生公示名单 PDF：`https://graschool.ahu.edu.cn/_upload/article/files/a7/b8/034991d549a982efa455ba84784a/0778f668-e7cf-4661-bcbf-6b6cf9f0c819.pdf`

本批试探但暂未并入的典型入口：

- 中央民族大学推免/硕士拟录取公示页面在本地抓取时返回 404。
- 四川师范大学多条拟录取公示页在本地抓取时返回 483。
- 安徽财经大学、中南民族大学、南京财经大学页面可访问，但附件下载接口返回 HTML 桥页，未形成可解析人员名单。

本批合并后交付版：

- B 类官网总表：158,857 条清洗记录，240 个学校/年份/文档类型汇总组
- 统一清洗包：164,567 条记录，392 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，213 所已精确匹配官网记录，217 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：171 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch101b 清洗表：532 条，0 条需复核；公开版 532 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 164,568 行（含表头），公开明细 164,567 行。

## 2026-05-25 追加批次：扬州大学 batch100

batch100 继续查找 B 类官网可爬取材料。本轮成功补入扬州大学法学院 2025 年推荐优秀应届本科毕业生免试攻读研究生通过答辩公示 PDF，从正文名单抽取 17 条人员级记录。该 PDF 只披露姓名和“通过答辩”结论，没有学号、专业或排名字段，因此 17 条均保留 `needs_review=true` 作为后续人工复核标记。

batch100 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 扬州大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 17 | 17 |

可追溯来源：

- 扬州大学法学院 2025 年推荐优秀应届本科毕业生免试攻读研究生通过答辩公示 PDF：`https://fxy.yzu.edu.cn/__local/4/42/E7/036779B02BE9F95A16FEDC83F20_594D2C91_17F41.pdf`

本批合并后交付版：

- B 类官网总表：158,325 条清洗记录，239 个学校/年份/文档类型汇总组
- 统一清洗包：164,035 条记录，391 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，212 所已精确匹配官网记录，218 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：170 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch100 清洗表：17 条，17 条需复核；公开版 17 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 164,036 行（含表头），公开明细 164,035 行。

## 2026-05-25 追加批次：西华大学 batch99

batch99 转向四川缺口高校。西华大学研究生院 2026 年拟录取推荐免试攻读硕士研究生名单公示页可从 HTML 表格中抽取 7 条真实推免拟录取记录，字段包含姓名、录取学院、专业代码、录取专业和录取类别，清洗后 0 条需复核。西南科技大学候选入口在本轮抓取中出现 502/长时间无响应，已保留日志并中止该慢请求。

batch99 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西华大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 7 | 0 |

可追溯来源：

- 西华大学 2026 年拟录取推荐免试攻读硕士研究生名单公示页：`https://yjs.xhu.edu.cn/88/a7/c10021a231591/page.htm`

本批合并后交付版：

- B 类官网总表：158,308 条清洗记录，238 个学校/年份/文档类型汇总组
- 统一清洗包：164,018 条记录，390 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，211 所已精确匹配官网记录，219 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：169 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch99 清洗表：7 条，0 条需复核；公开版 7 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 164,019 行（含表头），公开明细 164,018 行。

## 2026-05-25 追加调研：batch96/batch97/batch98 暂无可并入记录

batch96 覆盖西安外国语大学、西安邮电大学、西安电子科技大学候选入口；batch97 覆盖杭州师范大学、温州医科大学、西湖大学候选入口；batch98 覆盖山西财经大学、山西农业大学候选入口。三批均完成抓取或部分抓取，并输出种子/日志/原始记录。batch96 新增清洗回归规则：剔除“张老师/刘老师”等联系方式以及列表页 `DATE` 字段错位形成的索引碎片。batch97 主要受 404、温州医科大学 483、 西湖大学 500 影响；batch98 主要受山西财经大学 502 和山西农业大学慢请求影响，未并入主数据。

## 2026-05-25 追加批次：宁夏大学 batch95

batch95 转向宁夏缺口高校。宁夏大学研究生院 2026 年接收推荐免试攻读硕士研究生拟录取名单、2026 年硕士研究生招生拟录取名单第一批/第二批页面均暴露可解析附件，现有解析链条结构化 3,124 条，清洗后 0 条需复核。宁夏医科大学候选页本轮部分入口返回 404 或仅抓到通知列表，暂未形成可并入记录。

batch95 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 宁夏大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 33 | 0 |
| 宁夏大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,091 | 0 |

可追溯来源：

- 宁夏大学 2026 年接收推荐免试攻读硕士研究生拟录取名单公示页：`https://graduate.nxu.edu.cn/info/1054/8503.htm`
- 宁夏大学 2026 年硕士研究生招生拟录取名单公示（第一批）：`https://graduate.nxu.edu.cn/info/1020/8544.htm`
- 宁夏大学 2026 年硕士研究生招生拟录取名单公示（第二批）：`https://graduate.nxu.edu.cn/info/1020/8555.htm`

本批合并后交付版：

- B 类官网总表：158,301 条清洗记录，237 个学校/年份/文档类型汇总组
- 统一清洗包：164,011 条记录，389 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，210 所已精确匹配官网记录，220 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：168 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch95 清洗表：3,124 条，0 条需复核；公开版 3,124 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 164,012 行（含表头），公开明细 164,011 行。

## 2026-05-25 追加调研：batch93/batch94 暂无可并入记录

batch93 覆盖山东中医药大学、华东师范大学、华东理工大学、上海理工大学、同济大学候选入口；batch94 覆盖大连外国语大学、大连大学、大连海洋大学候选入口。两批均完成抓取并输出原始页面/日志，但本轮没有形成可静态抽取并安全并入的人员级记录。主要原因包括：附件下载页被包装为 HTML、候选直链返回 404、动态公示系统未直接暴露结构化表格、部分 PDF 直链已失效。

## 2026-05-25 追加批次：青岛大学 batch92

batch92 转向山东缺口高校，并补入一个云南候选入口。青岛大学研究生院 2026 年硕士研究生招生拟录取名单公告暴露 PDF 附件，现有 PDF 解析链条结构化 3,955 条，字段包含姓名、考生编号、学院代码、学院名称、录取专业代码和备注代码，清洗后 0 条需复核。青岛理工大学、山东理工大学、山东农业大学、昆明理工大学候选入口本轮抓取到页面或附件，但未形成可静态抽取并安全并入的人员级记录。

本批新增清洗回归规则：剔除青岛大学 PDF 中由学院/方向文字、括号尾部和被截断姓名片段错位形成的无上下文伪姓名。

batch92 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 青岛大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,955 | 0 |

可追溯来源：

- 青岛大学 2026 年硕士研究生招生拟录取名单公示页：`https://grad.qdu.edu.cn/info/1118/4499.htm`
- 青岛大学拟录取名单 PDF：`https://grad.qdu.edu.cn/__local/2/98/3D/B248B48C86D3D7841621B0C6706_4D28F42B_A8AE1.pdf`

本批合并后交付版：

- B 类官网总表：155,177 条清洗记录，235 个学校/年份/文档类型汇总组
- 统一清洗包：160,887 条记录，387 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，209 所已精确匹配官网记录，221 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：168 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch92 清洗表：3,955 条，0 条需复核；公开版 3,955 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 160,888 行（含表头），公开明细 160,887 行。

## 2026-05-25 追加批次：河北医科大学、河北科技大学 batch91

batch91 转向河北缺口高校。河北医科大学研究生学院一志愿复试成绩及拟录取结果公告暴露 Excel 附件，清洗后保留 194 条；河北科技大学硕士研究生一志愿考生复试成绩及拟录取名单公告暴露 PDF 附件，清洗后保留 1,088 条。河北大学页面和附件本轮未形成可静态抽取的人员级记录，河北农业大学、河北北方学院部分候选页返回 404，暂未并入。

本批新增清洗回归规则：剔除河北科技大学 PDF 中由成绩、加试分数、括号方向和孤立无上下文字段片段错位形成的伪姓名，同时保留带考生编号和专业上下文的真实名单行。

batch91 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河北医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 194 | 0 |
| 河北科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,088 | 0 |

可追溯来源：

- 河北医科大学 2026 年统招硕士研究生一志愿复试成绩及拟录取结果公告：`https://gschool.hebmu.edu.cn/a/2026/04/21/DDE5D55AA71D4A0CA7EA44FCB0C75EE2.html`
- 河北医科大学拟录取 Excel 附件：`https://gschool.hebmu.edu.cn/resources/43/202604/1776730940400044092.xlsx`
- 河北医科大学拟录取 Excel 附件：`https://gschool.hebmu.edu.cn/resources/43/202604/1776730940408091776.xlsx`
- 河北医科大学拟录取 Excel 附件：`https://gschool.hebmu.edu.cn/resources/43/202604/1776736111390081963.xlsx`
- 河北科技大学 2026 年硕士研究生一志愿考生复试成绩及拟录取名单公告：`http://yjsxy.web.hebust.edu.cn/tzgg/fd9e92136cbc490a9ad3b9d4caed0205.htm`
- 河北科技大学拟录取名单 PDF：`http://yjsxy.web.hebust.edu.cn/docs/2026-04/1cc1c8ffd8134e019d18c7896d752bfb.pdf`

本批合并后交付版：

- B 类官网总表：151,222 条清洗记录，234 个学校/年份/文档类型汇总组
- 统一清洗包：156,932 条记录，386 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，208 所已精确匹配官网记录，222 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：167 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch91 清洗表：1,282 条，0 条需复核；公开版 1,282 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 156,933 行（含表头），公开明细 156,932 行。

## 2026-05-25 追加批次：南通大学 batch90

batch90 转向江苏/南京缺口高校。南通大学研究生招生网 2026 年接收推荐免试研究生拟录取名单页面暴露 PDF 附件，现有 PDF 解析链条结构化 179 条，字段包含姓名、学号、学院和录取专业代码，清洗后 0 条需复核。南京邮电大学硕士招生列表页本身可抓取，但跟进命中的是 2021 年旧页面，未并入本批；南京理工大学两个候选官方页返回 410；南京财经大学两个候选官方页返回 404，均暂未并入。

batch90 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 南通大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 179 | 0 |

可追溯来源：

- 南通大学 2026 年接收推荐免试研究生拟录取名单公示页：`https://yjszs.ntu.edu.cn/2025/1022/c7626a275143/page.htm`
- 南通大学拟录取名单 PDF：`https://yjszs.ntu.edu.cn/_upload/article/files/61/b6/479f2995487f8eb842776dd90eb0/3e0d077b-d4c0-46c7-9361-c852caffcd09.pdf`
- 南通大学一志愿拟录取候选页：`https://yjszs.ntu.edu.cn/2026/0402/c7623a288559/page.htm`
- 南京邮电大学硕士招生列表页：`https://yzb.njupt.edu.cn/7815/list1.htm`
- 南京理工大学候选页：`https://gs.njust.edu.cn/zsw/8a/2e/c4587a363054/page.htm`
- 南京财经大学候选页：`https://yjsc.nufe.edu.cn/info/1011/6807.htm`

本批合并后交付版：

- B 类官网总表：149,940 条清洗记录，232 个学校/年份/文档类型汇总组
- 统一清洗包：155,650 条记录，384 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，206 所已精确匹配官网记录，224 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：166 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch90 清洗表：179 条，0 条需复核；公开版 179 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 155,651 行（含表头），公开明细 155,650 行。

## 2026-05-25 追加批次：广西医科大学、青海师范大学 batch89

batch89 继续补覆盖缺口高校。广西医科大学研究生院 2026 年接收推荐免试研究生拟录取名单页面暴露 PDF 附件，现有 PDF 解析链条结构化 106 条；青海师范大学研究生院 2026 年推荐免试硕士研究生拟录取名单页面可从 HTML 表格保留 9 条带学院和学习方式的记录。大连外国语大学列表页及一志愿/调剂/推免公告页、北华大学、福建师范大学、福建农林大学、云南师范大学等候选入口已抓取，但页面/附件桥未形成可静态抽取的人员级记录；安徽大学历史 PDF 直链返回 404，暂未并入。

本批新增清洗回归规则：剔除青海师范页面中由正文问候语错位形成的“各位 推免生”伪专业碎片，同时保留带学院上下文的真实名单行；剔除广西医科 PDF 标题被拆成“广/西/医/科/大/学”等单字姓名的无上下文碎片。

batch89 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 广西医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 106 | 0 |
| 青海师范大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 9 | 9 |

可追溯来源：

- 广西医科大学 2026 年接收推荐免试研究生拟录取名单公示页：`https://yjs.gxmu.edu.cn/zsgz/zsgg/t219536.html`
- 广西医科大学拟录取名单 PDF：`https://yjs.gxmu.edu.cn/zsgz/zsgg/P020250930676216023923.pdf`
- 青海师范大学 2026 年推荐免试硕士研究生拟录取名单公示页：`https://yjsb.qhnu.edu.cn/info/1059/2842.htm`
- 大连外国语大学硕士招生列表页：`https://gd.dlufl.edu.cn/zsgz/sszs.htm`
- 北华大学候选页：`https://grad.beihua.edu.cn/info/1071/3071.htm`
- 福建师范大学候选页：`https://yjsy.fjnu.edu.cn/8b/14/c4227a428820/page.htm`
- 福建农林大学硕士生招生列表页：`https://yjsy.fafu.edu.cn/3604/list.htm`
- 云南师范大学候选页：`https://grs.ynnu.edu.cn/info/1035/1503.htm`

本批合并后交付版：

- B 类官网总表：149,761 条清洗记录，231 个学校/年份/文档类型汇总组
- 统一清洗包：155,471 条记录，383 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，205 所已精确匹配官网记录，225 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：166 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch89 清洗表：115 条，其中青海师范 9 条因页面未给出专业字段保留 `needs_review=true`；公开版 115 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 155,472 行（含表头），公开明细 155,471 行。

## 2026-05-25 追加批次：成都大学 batch88

batch88 继续优先补覆盖缺口高校。成都大学研究生处页面中 `8189.htm` 可结构化 1 条退役大学生士兵专项相关拟录取记录；`8187.htm` 主公示页和附件下载桥已抓取，但下载桥返回 HTML/验证码类页面，未形成更多结构化名单。大连大学候选入口返回 404；大连海洋大学、青岛理工大学、浙江理工大学候选页已抓取，但页面/PDF/附件未形成可静态抽取的人员级记录，暂不并入主表。

本批新增清洗回归规则：剔除文章页正文抽取中误入人员字段的“一审/二审/三审”等审核标签，以及“二等战功”等荣誉文本单独成为姓名的碎片；带有学号和专业字段的真实记录仍正常保留。

batch88 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 成都大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1 |

可追溯来源：

- 成都大学 2026 年相关拟录取名单页：`https://yjsc.cdu.edu.cn/info/1028/8189.htm`
- 成都大学候选主公示页：`https://yjsc.cdu.edu.cn/info/1028/8187.htm`
- 大连海洋大学候选页：`https://master.dlou.edu.cn/2026/0401/c9037a204274/page.htm`
- 青岛理工大学候选页：`https://yjsh.qut.edu.cn/info/1406/3291.htm`
- 浙江理工大学候选页：`https://gradadmission.zstu.edu.cn/info/1011/3353.htm`
- 大连大学候选页：`https://yjs.dlu.edu.cn/info/1065/3222.htm`

本批合并后交付版：

- B 类官网总表：149,646 条清洗记录，229 个学校/年份/文档类型汇总组
- 统一清洗包：155,356 条记录，381 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，203 所已精确匹配官网记录，227 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：164 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch88 清洗表：1 条，0 条需复核；公开版 1 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 155,357 行（含表头），公开明细 155,356 行。

## 2026-05-25 追加批次：蚌埠医科大学、兰州财经大学 batch87

batch87 继续补覆盖缺口高校。蚌埠医科大学研究生院 2026 年推免生拟录取名单页面可直接从 HTML 结构化 5 条；兰州财经大学研究生院 2026 年接收应届本科毕业生免试攻读硕士研究生拟录取名单页面正文可结构化 4 条。蚌埠医科大学 2026 年硕士研究生拟录取名单页正文仅保留“公示已结束”附件说明，未暴露可下载名单；北京协和医学院推免系统当前已切到 2027 年空表；北方民族大学、北京语言大学、渤海大学、安徽财经大学、青海师范大学、东北电力大学、北华大学等候选入口分别遇到 404、403、502、验证码/空表或无静态名单，未并入本批结构化主表。

本批新增清洗回归规则：对正文抽取中“只有拟录取状态、没有学院/专业上下文/学号”的碎片行进行剔除，避免兰州财经页面中的“王雅萱/拟录取”重复行以及“数字经济/拟录取”“金融工程/拟录取”等专业名误入姓名列。

batch87 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 蚌埠医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 5 |
| 兰州财经大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 4 |

可追溯来源：

- 蚌埠医科大学 2026 年推免生拟录取名单公示页：`https://yjsy.bbmu.edu.cn/info/1049/7712.htm`
- 兰州财经大学 2026 年接收应届本科毕业生免试攻读硕士研究生拟录取名单公示页：`https://yjsy.lzufe.edu.cn/info/1093/3192.htm`

本批合并后交付版：

- B 类官网总表：149,645 条清洗记录，228 个学校/年份/文档类型汇总组
- 统一清洗包：155,355 条记录，380 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，202 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：163 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch87/batch87b 清洗表：9 条，0 条需复核；公开版 9 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 范围为 `A1:T155356`，公开明细 155,355 行。

## 2026-05-25 追加批次：天津医科大学、天津中医药大学 batch86

batch86 继续补天津缺口高校。天津医科大学 2026 年硕士研究生招生拟录取名单公示页暴露 PDF 附件，现有 PDF 表格链条结构化 1,211 条；天津中医药大学研究生院多个学院/附属医院接收推免拟录取名单页面可直接从 HTML 表格结构化，合并清洗后保留 156 条。天津体育学院候选页和附件下载桥已抓取，但未形成可结构化人员级记录；天津医科大学旧 PDF 直链返回 404，未并入。

本批新增清洗回归规则：剔除天津中医药页面中误入姓名列的“硕士”“直博生”，以及天津医科 PDF 表头错位产生的“方向”“院系所”等标签，避免标题、层级和表头文本污染清洗表。

batch86 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 天津医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,211 |
| 天津中医药大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 156 |

可追溯来源：

- 天津医科大学 2026 年硕士研究生招生拟录取名单公示页：`https://gs.tmu.edu.cn/2026/0429/c3146a87608/page.htm`
- 天津医科大学拟录取名单 PDF：`https://gs.tmu.edu.cn/_upload/article/files/37/c0/a5cbb16440048fbdd5fdfdd8ef64/fd97bfc7-7f09-4d16-9486-871a9419a00f.pdf`
- 天津中医药大学第一附属医院拟录取名单页：`https://yjsy.tjutcm.edu.cn/info/1976/9429.htm`
- 天津中医药大学中药学院拟录取名单页：`https://yjsy.tjutcm.edu.cn/info/1976/9483.htm`
- 天津体育学院候选页：`https://yjsb.tjus.edu.cn/info/1004/4550.htm`

本批合并后交付版：

- B 类官网总表：149,636 条清洗记录，226 个学校/年份/文档类型汇总组
- 统一清洗包：155,346 条记录，378 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，200 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：162 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch86 清洗表：1,367 条，0 条需复核；公开版 1,367 条
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T155347`，公式错误扫描 0 条，并已渲染 4 个工作表预览。

## 2026-05-25 追加批次：天津美术学院、天津理工大学、天津商业大学 batch85

batch85 继续补天津缺口高校。天津美术学院 2026 年硕士研究生招生拟录取名单页面暴露 PDF 附件，现有 PDF 链条结构化 374 条；天津理工大学采用研究生院汇总页加学院公示页入口，抓取计算机、语言文化、理学院、电气、管理、马克思主义、聋人工学院等页面，清洗后保留 16 条；天津商业大学研究生处入口未发现 2026 拟录取明细，但历史 2024 接收推免拟录取公示可结构化 3 条。天津科技大学页面和 PDF 直链均持续同 URL 302 循环，暂未并入。

本批新增清洗回归规则：剔除天津理工页面中误入姓名列的“会计”“工商管理学”“管理科学与工程”“支教团”“天开杯”“科研项目”等专业、栏目或说明文本；同时把“学院名误入 major 字段”的重复行转为学院字段后与更完整记录去重。

batch85 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 天津美术学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 374 |
| 天津理工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 3 |
| 天津理工大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 13 |
| 天津商业大学 | 2024 | recommendation_exemption_list | recommendation_exemption | 3 |

可追溯来源：

- 天津美术学院 2026 年硕士研究生招生拟录取名单公示页：`https://www.tjarts.edu.cn/info/1156/18244.htm`
- 天津美术学院拟录取名单 PDF：`https://www.tjarts.edu.cn/__local/F/EA/18/FF54064EDB3EB319DED67D72FFF_1CF91BA7_37399.pdf`
- 天津理工大学 2026 年接收推荐免试攻读硕士学位研究生拟录取名单公示汇总页：`https://yjs.tjut.edu.cn/index/xsfw/8.htm`
- 天津理工大学计算机科学与工程学院拟录取名单页：`https://cs.tjut.edu.cn/info/1062/2763.htm`
- 天津理工大学管理学院拟录取名单页：`https://ms.tjut.edu.cn/info/1059/5855.htm`
- 天津商业大学 2024 届接收推免拟录取名单公示页：`https://gs.tjcu.edu.cn/info/1097/3372.htm`

本批合并后交付版：

- B 类官网总表：148,269 条清洗记录，224 个学校/年份/文档类型汇总组
- 统一清洗包：153,979 条记录，376 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，198 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：162 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch85 清洗表：393 条，其中天津美术 374 条因 PDF 未抽出专业字段保留 `needs_review=true`；公开版 393 条
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T153980`，公式错误扫描 0 条，并已渲染 4 个工作表预览。

## 2026-05-24 追加批次：南开大学、天津大学、天津外国语大学 batch84

batch84 先补天津缺口高校，并同步复核若干北京、辽宁、山东候选入口。南开大学招生办主入口当前跳转统一身份认证，未并入；统计与数据科学学院官网页面可直接结构化 33 条。天津外国语大学研究生院页面暴露附件下载桥，下载桥需要验证码；手动读取验证码后保存官方 PDF，并按 PDF 文本生成 32 条拟录取记录。天津大学教务处主页面是各学院拟推荐名单汇总入口，本批抓取理学院、马克思主义学院、仁爱学院/人文艺术相关学院页形成 56 条有效记录；其中 10 条学院页未公开专业字段，保留 `needs_review=true` 便于后续人工复核。`mstu.tju.edu.cn` 页面抽到的“办公网”“图书馆”“教务处”等站点导航已由新增回归规则剔除。

补充复核中，沈阳航空航天大学和中央民族大学搜索命中页实时返回 404；中国海洋大学 PDF 直链仍返回 404；南开大学招生办主页面进入身份认证，均未并入本批主表。

batch84 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 南开大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 33 |
| 天津大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 56 |
| 天津外国语大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 32 |

可追溯来源：

- 南开大学统计与数据科学学院 2026 年拟接收推荐免试硕士研究生公示页：`https://stat.nankai.edu.cn/2025/1010/c12341a580793/page.htm`
- 天津外国语大学 2026 年接收推免生拟录取名单公示页：`https://grad.tjfsu.edu.cn/info/1075/3519.htm`
- 天津外国语大学拟录取名单 PDF 下载桥：`https://grad.tjfsu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1783168760&wbfileid=3868248`
- 天津大学 2026 年拟推荐免试攻读研究生名单公示汇总页：`https://oaa.tju.edu.cn/info/1056/8290.htm`
- 天津大学理学院拟推荐名单页：`https://science.tju.edu.cn/info/1136/3428.htm`
- 天津大学马克思主义学院拟推荐名单页：`https://marxism.tju.edu.cn/info/1060/4197.htm`
- 天津大学学院页：`https://rwys.tju.edu.cn/info/1015/2898.htm`

本批合并后交付版：

- B 类官网总表：147,876 条清洗记录，220 个学校/年份/文档类型汇总组
- 统一清洗包：153,586 条记录，372 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，195 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：161 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch84 清洗表：121 条，其中 10 条需复核；公开版 121 条
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T153587`，公式错误扫描 0 条，并已渲染 4 个工作表预览。

## 2026-05-24 追加批次：辽宁中医药大学、大连医科大学、辽宁工程技术大学 batch83

batch83 继续优先补辽宁缺口高校。辽宁工程技术大学官网页面内嵌 2026 年一志愿待录取硕士研究生 PDF，现有 PDF 表格链条可直接抽取。辽宁中医药大学和大连医科大学的名单附件均为验证码下载桥，手动读取验证码后保存原始 PDF，并按测试先行新增两类 PDF 解析规则：辽宁中医药规则保留学院、拟录取专业、研究方向、总分和硕士/直博备注；大连医科规则处理院系/专业/研究方向跨行错位、硕士推免名单和直接攻博名单。

补充复核中，渤海大学官网正文仅公开“6 名”的汇总口径且云盘附件字段为空，未公开人员明细；中国海洋大学官网页面的“附件”实际为二维码图片，HTML 未暴露名单文件；天津科技大学页面仍为同 URL 302 循环，均未并入本批主表。

batch83 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 大连医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 15 |
| 辽宁中医药大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 76 |
| 辽宁工程技术大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,145 |

本批合并后交付版：

- B 类官网总表：147,755 条清洗记录，217 个学校/年份/文档类型汇总组
- 统一清洗包：153,465 条记录，369 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，192 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：161 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch83 清洗表：1,236 条，0 条需复核，1,236 个唯一 `record_id`
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T153466`，公式错误扫描 0 条，并已渲染 4 个工作表预览。

## 2026-05-24 追加批次：大连海事大学、沈阳工业大学 batch82

batch82 聚焦辽宁、天津等覆盖缺口高校。大连海事大学官网页面公开 2026 年推免研究生（含直博生）拟录取考生名单，附件下载桥需要验证码；手动读取验证码后成功下载 PDF，并新增大连海事 PDF 表格解析规则，覆盖普通硕士、专业名称换行、含字母专业代码和直博生段。沈阳工业大学原搜索命中页为旧 404，改从硕士招生列表定位到 2026 年接收推荐免试研究生拟录取名单公示页，正文 HTML 表格可直接结构化。天津科技大学候选页持续 302 到自身并设置站点签名 cookie，暂未并入；中国医科大学主统考页面仅公开拟录取类别确认通知，无人员名单，暂不混入本批主数据。

batch82 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 大连海事大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 466 |
| 沈阳工业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 132 |

本批合并后交付版：

- B 类官网总表：146,519 条清洗记录，214 个学校/年份/文档类型汇总组
- 统一清洗包：152,229 条记录，366 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，189 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-24 追加批次：江苏大学、内蒙古师范大学 batch81b

batch81 继续补江苏、北京、上海、内蒙古等覆盖缺口高校。第一轮种子中部分搜索索引旧地址返回 404/410，华东政法大学页面仅公布拟录取总人数而无人员明细，中国政法大学页面返回动态挑战页，北京语言大学附件下载桥返回 HTML 校验页，正文误抽出的页脚链接已被清洗规则剔除。batch81b 修正入口后，江苏大学和内蒙古师范大学页面均暴露附件下载桥；使用来源页 Referer 手动下载后确认均为真实 PDF，并由现有 PDF 表格解析链条结构化。

本批还新增清洗回归规则：剔除研究生院页面导航栏目误入姓名列的记录，如“下载专区”“学位授予”“硕士招生”“科研工作”等，避免正文导航区污染清洗表。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch81.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch81b.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch81b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch81b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch81b/school_year_summary.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch81b/records_manual.jsonl`

batch81b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 江苏大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4,386 |
| 内蒙古师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,205 |

可追溯来源：

- 江苏大学 2026 年全国统考硕士研究生拟录取名单公示页：`https://yz.ujs.edu.cn/info/1010/8497.htm`
- 江苏大学拟录取名单 PDF 下载桥：`https://yz.ujs.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1347509089&wbfileid=4E4ACCD2B8D73EED6EEFB4A00353E43B`
- 内蒙古师范大学 2026 年硕士研究生招生考试一志愿考生拟录取名单公示页：`https://yjsc.imnu.edu.cn/info/1004/5118.htm`
- 内蒙古师范大学拟录取名单 PDF 下载桥：`https://yjsc.imnu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1551731048&wbfileid=6F4216E57B8D71E27058BF0C7ECC8F5D`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：145,921 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：145,921 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：151,631 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：151,631 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：364 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，187 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 151,631 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：154 个测试通过
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T151632`，公式错误扫描 0 条，并已渲染 4 个工作表预览。
- 质量扫描：batch81b 清洗表 5,591 条，`needs_review` 0，姓名错位 0；全量官网主表缺少身份 0、表头/联系人文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0。

## 2026-05-24 追加批次：南京工业大学 batch80b

batch80 面向江苏、四川、上海、北京等覆盖缺口高校继续补源。初始 batch80 发现南京工业大学 2026 年调剂硕士研究生拟录取名单 PDF 可访问，但表格换行会造成错位行；按测试先行新增南京工业大学专用 PDF 文本行解析后，使用 batch80b 干净目录重跑，稳定结构化 558 条。南京财经大学附件下载桥返回 3,805 字节 HTML 验证页；电子科技大学信息与通信工程学院附件可用 Referer 下载为 PDF，但文本层仅 13 个字符，属于扫描图片型，暂不强行并入。西南交通大学候选页 502、江苏大学候选页 404、南京理工大学候选页 410，部分电子科技大学学院页返回 412，均暂不并入主表。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch80.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch80b.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch80b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch80b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch80b/school_year_summary.csv`

batch80b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 南京工业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 558 |

可追溯来源：

- 南京工业大学 2026 年调剂硕士研究生拟录取名单 PDF：`https://gra.njtech.edu.cn/__local/2/16/D8/A73E329CA807825895EA1EA38DA_0A488B68_7C0D9.pdf`
- 电子科技大学信息与通信工程学院附件 PDF 已下载至本地原始目录，但因扫描图片型暂未结构化：`data/raw/graduate_outcomes_official_site_websearch_web_20260524_batch80b_manual/uestc_sice.pdf`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：140,330 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：140,330 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：146,040 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：146,040 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：362 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，185 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 146,040 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：153 个测试通过
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T146041`，公式错误扫描 0 条，并已渲染 4 个工作表预览。
- 质量扫描：batch80b 清洗表 558 条，`needs_review` 0，姓名错位 0；全量官网主表缺少身份 0、表头/联系人文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0。

## 2026-05-24 追加批次：中国矿业大学、海南大学、西安工程大学、西藏民族大学、西南民族大学 batch79b

batch79 面向江苏、海南、陕西、四川等仍缺口高校继续补源。初始 batch79 证实中国矿业大学、西藏民族大学 PDF 均可访问，但需要新增 PDF 文本行规则：前者为“序号、姓名、录取学院代码/名称、录取专业代码/名称、成绩、招生类型”结构，后者需要把“姓名 身份证号”拆成姓名和脱敏证件号。按测试先行补充解析后，使用干净目录重跑为 batch79b。西南交通大学附件返回验证码页、浙江理工大学页面附件未暴露可下载链接，南昌大学和华北电力大学候选链接实时 404，暂不并入。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch79.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch79b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch79b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch79b/school_year_summary.csv`

batch79b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 中国矿业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 1,054 |
| 海南大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 236 |
| 西安工程大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 44 |
| 西藏民族大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 40 |
| 西南民族大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 3 |

可追溯来源：

- 中国矿业大学 2026 年接收推荐免试研究生拟录取名单 PDF：`https://yz.cumt.edu.cn/2026jieshoutuimianyanjiushengniluqurenyuanmingdan.pdf`
- 海南大学 2026 年接收推荐免试攻读研究生拟录取名单 PDF：`https://gs.hainanu.edu.cn/__local/B/AF/C7/027A6037D67D67D22F19A94F593_A17A0DA6_2F93A.pdf`
- 西安工程大学 2026 年推荐免试研究生拟录取名单公示页：`https://yzw.xpu.edu.cn/info/1033/2808.htm`
- 西藏民族大学 2026 年接收推荐免试攻读硕士研究生拟录取名单 PDF：`https://www1.xzmu.edu.cn/yjsc/userfiles/file/3876ed1c-4a44-4dea-89cc-2f216cad5bc1.pdf`
- 西南民族大学 2026 年接收推荐免试研究生拟录取名单第二批 PDF：`https://yjsglxt.swun.edu.cn/__local/1/EB/63/BD387086F277F5CC1E7CFF6F582_DCE38893_A000.pdf?e=.pdf`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：139,772 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：139,772 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：145,482 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：145,482 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：361 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，184 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 145,482 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：152 个测试通过
- 质量扫描：batch79b 清洗表 1,377 条，姓名字段中联系人/数字/表头/证件号残留均为 0；全量官网主表缺少身份 0、表头/联系人文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；Excel `Public_Records` 145,482 行。

## 2026-05-24 追加批次：大连理工大学、山东第一医科大学、西南医科大学 batch78

batch78 补辽宁、山东、四川缺口高校。山东第一医科大学官方页面可自动发现 PDF 附件并结构化；大连理工大学和西南医科大学初始候选 URL 有 404 或附件验证码页问题，batch78b 使用修正后的官方页面并带来源页 Referer 下载真实 PDF 后成功结构化。大连海事大学、大连医科大学候选页实时 404，暂不并入。本批新增联系人碎片过滤规则，避免正文中的“姜老师”“联系方式”等联系人字段误入名单。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch78.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch78b.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78b/school_year_summary.csv`

batch78/78b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 大连理工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 2,645 |
| 山东第一医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 68 |
| 西南医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 52 |

可追溯来源：

- 大连理工大学 2026 年接收推荐免试攻读硕士（博士）学位研究生拟录取名单公示页：`https://info.dlut.edu.cn/info/1167/14166.htm`
- 大连理工大学附件下载页：`https://info.dlut.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1830974987&wbfileid=B9AF594A0ABEA559FA4C4E8A1AD18298`
- 山东第一医科大学 2026 年接收推免生拟录取名单公示页：`https://yz.sdfmu.edu.cn/info/1019/3355.htm`
- 山东第一医科大学附件 PDF：`https://yz.sdfmu.edu.cn/__local/1/A8/49/B6978A187A806BBC757529EB60F_A6978F4D_13369.pdf`
- 西南医科大学 2026 年推荐免试硕士研究生拟录取名单公示页：`https://yjs.swmu.edu.cn/info/1014/9929.htm`
- 西南医科大学附件下载页：`https://yjs.swmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1472804872&wbfileid=4D0EC6F459B86A4BBC9B7E6FEEA545B8`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：138,631 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：138,631 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：144,341 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：144,341 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：357 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，180 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 144,341 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：150 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航/主题切换/联系人文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch78/78b 清洗表 2,765 条；Excel `Public_Records` 144,341 行。

## 2026-05-24 追加批次：延边大学、哈尔滨医科大学、东北林业大学 batch77

batch77 转向东北片区缺口高校。延边大学、哈尔滨医科大学页面默认附件下载页返回验证码 HTML，使用来源页 Referer 后可下载真实 PDF 并结构化；东北林业大学研究生招生候选页实时 404，但信息公开站 PDF 直链可访问并结构化。东北师范大学页面仅公开公示说明、未暴露个人名单明细；哈尔滨师范大学生命科学与技术学院名单为长图图片，本轮未 OCR，均暂不并入。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch77.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch77/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch77/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch77/school_year_summary.csv`

batch77 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 延边大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 175 |
| 哈尔滨医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 111 |
| 东北林业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 67 |

可追溯来源：

- 延边大学 2026 年推荐免试攻读研究生拟录取公示页：`https://grad.ybu.edu.cn/info/1188/6590.htm`
- 延边大学附件下载页：`https://grad.ybu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1254623853&wbfileid=4748894`
- 哈尔滨医科大学 2026 年推免生（含本科直博生）和医学长学制转段研究生拟录取名单公示页：`https://yjsy.hrbmu.edu.cn/info/1024/3093.htm`
- 哈尔滨医科大学附件下载页：`https://yjsy.hrbmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1703217425&wbfileid=17809565`
- 东北林业大学 2026 年接收推荐免试本科直博研究生拟录取名单 PDF：`https://xxgk.nefu.edu.cn/__local/2/01/71/7CB4B466839821FF3916276CE97_C2F17A25_1B632.pdf`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：135,866 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：135,866 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：141,576 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：141,576 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：354 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，177 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 141,576 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：149 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航/主题切换文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch77 清洗表 353 条；Excel `Public_Records` 141,576 行。

## 2026-05-24 追加批次：湖南科技大学、南华大学、湖南工商大学 batch76

batch76 继续补河南、湖南缺口高校。湖南工商大学官方 PDF 可直接抓取；湖南科技大学和南华大学附件在默认抓取下分别返回“非法访问”或验证码下载页，加上来源页 Referer 后可下载真实 PDF，并成功结构化。湖南大学附件也可用 Referer 下载真实 PDF，但 PDF 文本层未抽出人员记录，暂不并入；河南医药大学页面正文只暴露“名单见附件”说明但未暴露可下载附件链接；河南科技大学软件学院候选页实时返回 404；郑州轻工业大学页面误抽到的主题切换文本已通过新增清洗规则过滤，未并入。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch76.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch76/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch76/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch76/school_year_summary.csv`

batch76 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 湖南科技大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 382 |
| 南华大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 36 |
| 湖南工商大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 13 |

可追溯来源：

- 湖南科技大学 2026 年推荐免试攻读硕士学位研究生推荐审定会公示名单：`https://jwc.hnust.edu.cn/docs/2025-09/bd52548ca2d84a1e857498744bcdf8a7.pdf`
- 南华大学 2026 年接收推荐免试攻读硕士学位研究生拟录取名单公示页：`https://yjs.usc.edu.cn/info/1313/12741.htm`
- 南华大学附件下载页：`https://yjs.usc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=999409215&wbfileid=13160656`
- 湖南工商大学 2026 年推荐免试研究生拟录取公示名单 PDF：`https://gra.hutb.edu.cn/u/cms/yjsy/202511/26102530ao1d.pdf`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：135,513 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：135,513 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：141,223 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：141,223 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：351 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，174 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 141,223 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：149 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航/主题切换文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch76 清洗表 431 条；Excel `Public_Records` 141,223 行。

## 2026-05-24 追加批次：河南理工大学、河南农业大学 batch75

batch75 继续补 B 类官网推免/拟录取名单。河南理工大学、河南农业大学官方页面正文表格可直接结构化，清洗后合计新增 36 条并入 B 类官网主表。中国人民公安大学研招网页面可访问，正文仅公开 2026 年硕士推免生拟录取总数，附件下载页返回验证码页面，未获取到个人名单明细，本轮隔离未并入。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch75.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch75/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch75/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch75/school_year_summary.csv`

batch75 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 河南农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 19 |
| 河南理工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 17 |

可追溯来源：

- 河南理工大学 2026 级推免生拟录取名单公示：`https://adge.hpu.edu.cn/info/1031/14117.htm`
- 河南农业大学 2026 年推免硕士研究生拟录取名单公示：`https://gra.henau.edu.cn/a/zhaoshenggongzuo/20251021/4754.html`
- 中国人民公安大学 2026 年硕士推免生拟录取名单公示页（附件验证码，未并入）：`https://yzb.ppsuc.edu.cn/info/1008/5394.htm`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：135,082 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：135,082 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,792 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,792 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：348 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，171 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,792 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：148 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch75 清洗表 36 条；Excel `Public_Records` 140,792 行。

## 2026-05-24 追加批次：中央戏剧学院 batch74

batch74 继续补北京艺术类院校缺口。中央戏剧学院官方 PDF 可直接抓取并结构化；北京服装学院种子实时跳转 404 页面，中央美术学院 PDF 直链返回 404，北京电影学院研究生院页面返回 412，均隔离未并入。本批还修正了一个清洗边界：官方脱敏姓名如 `*芷名` 末尾含“名”时，不再误判为表头字段。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch74.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch74/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch74/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch74/school_year_summary.csv`

batch74 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 中央戏剧学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 95 |

可追溯来源：

- 中央戏剧学院 2026 年接收推荐免试攻读硕士学位研究生拟录取名单公示：`https://chntheatre.edu.cn/Uploads/Cad/Picture/2025/10/13/001.%E4%B8%AD%E5%A4%AE%E6%88%8F%E5%89%A7%E5%AD%A6%E9%99%A2%202026%20%E5%B9%B4%E6%8E%A5%E6%94%B6%E6%8E%A8%E8%8D%90%E5%85%8D%E8%AF%95%E6%94%BB%E8%AF%BB%E7%A1%95%E5%A3%AB%E5%AD%A6%E4%BD%8D%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95%E5%85%AC%E7%A4%BA.20251013100734.pdf`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：135,046 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：135,046 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,756 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,756 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：346 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，169 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,756 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：148 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch74 清洗表 95 条；Excel `Public_Records` 140,756 行。

## 2026-05-24 追加批次：中央音乐学院 batch73c

batch73 继续补北京覆盖缺口学校。中央民族大学页面在浏览器可见，但爬虫访问页面返回 404；其 21 个官方附件直链均返回验证码下载页，暂不并入。北京语言大学页面可访问，但附件同样返回验证码下载页，页面正文误抽到 footer 链接，本批新增 footer 导航标签过滤规则后清洗为 0 条。随后 `batch73c` 改用中央音乐学院官方正文页，页面直接列出 2026 年硕士推免生拟录取名单，成功结构化 95 条。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch73.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch73b.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch73c.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73b/documents.jsonl`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73c/school_year_summary.csv`

batch73c 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 中央音乐学院 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 95 |

可追溯来源：

- 中央音乐学院 2026 年硕士推免生拟录取名单：`https://www.ccom.edu.cn/info/10711/258051.htm`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,951 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,951 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,661 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,661 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：345 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，168 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,661 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：147 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch73c 清洗表 95 条；Excel `Public_Records` 140,661 行。

## 2026-05-24 追加批次：北京航空航天大学 batch72b

batch72 继续补北京覆盖缺口学校。首轮人大旧域名实时返回 404，法大研究生院页面出现动态挑战，北航若干学院旧路径返回 404，均隔离未并入。随后 `batch72b` 改用北航真实学院页和官方 PDF 直链，成功结构化经济管理学院、宇航学院 2026 年拟推免生名单。化学学院 PDF 和机械学院附件本轮未抽到人员记录，暂不并入。

本批还补充了一个清洗规则：PDF 表格抽取中如果 `ranking` 字段残留 `专业`、`专业排名` 等表头词，会在解析/清洗阶段清空，避免列头进入可用字段。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch72.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch72b.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch72b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch72b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch72b/school_year_summary.csv`

batch72b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 北京航空航天大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 128 |

可追溯来源：

- 北航经济管理学院 2026 年拟推免生名单 PDF：`https://sem.buaa.edu.cn/__local/E/B8/97/77956D5A542FB4D8E1CE763C7FF_FA52EDC9_2C085.pdf`
- 北航宇航学院 2026 年拟推免生名单 PDF：`https://www.sa.buaa.edu.cn/__local/E/90/F3/5C92854D30AE5036697E11FCF28_6864631E_1B81F.pdf`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,856 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,856 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,566 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,566 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：344 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，167 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,566 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：146 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch72b 清洗表 128 条；Excel `Public_Records` 140,566 行。

## 2026-05-24 追加批次：北京工商大学 batch71

batch71 转向北京覆盖缺口学校，优先抓取北京工商大学教务处中心公示。该页面正文明确公示 2026 届本科生推免资格结果，并提供 `公示名单.xlsx` 附件；附件为两列姓名表，左列 `正式（256人）`、右列 `候补`。本批新增 Excel“正式/候补”姓名列解析规则，只将正式名单并入主表，候补列保留在原始附件中不进入正式推免记录。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch71.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch71/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch71/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch71/school_year_summary.csv`

batch71 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 北京工商大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 256 |

可追溯来源：

- 北京工商大学教务处 2026 年应届本科毕业生拟获推免资格名单公示：`https://jwc.btbu.edu.cn/jwkw/yjstm/ae2e1fd7667043dd9983b4b3b086744a.htm`
- 公示名单附件：`https://jwc.btbu.edu.cn/docs/2025-09/96a96ec18a6145bba2ee34bc19a9f5b9.xlsx`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,728 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,728 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,438 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,438 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：343 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，166 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,438 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：144 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch71 清洗表 256 条；Excel `Public_Records` 140,438 行。

## 2026-05-24 追加批次：沈阳农业大学 batch70c

batch70 转向辽宁覆盖缺口学校。首轮沈阳农业大学植物保护学院、水利学院、动物科学与医学学院旧路径均返回 404/502；校验搜索索引后修正了植物保护学院和动物科学与医学学院真实 URL，并额外验证沈阳师范大学文学院页面。动物科学与医学学院表格存在合并单元格错位，沈阳师范大学文学院页面误抽到推免工作小组成员，均隔离未并入。最终 `batch70c` 仅并入沈阳农业大学植物保护学院人员级名单。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch70c.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch70c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch70c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch70c/school_year_summary.csv`

batch70c 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 沈阳农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 21 |

可追溯来源：

- 沈阳农业大学植物保护学院 2026 年优秀应届本科毕业生免试攻读硕士研究生人员名单公示：`https://zbxy.syau.edu.cn/info/1038/5593.htm`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,472 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,472 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,182 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,182 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：342 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，165 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,182 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：143 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch70c 清洗表 21 条；Excel `Public_Records` 140,182 行。

## 2026-05-24 追加批次：湖北大学 batch69c

batch69 继续补湖北覆盖缺口学校。华中师范大学页面可访问但附件为验证码下载，暂不结构化；中南民族大学、湖北大学网络空间安全学院的搜索命中路径实时返回 404。最终 `batch69c` 并入湖北大学楚才学院官网正文名单。该页面为“学生名单公示如下：姓名串 / 候补名单”的版式，本批新增普通正文名单解析规则，并在“候补名单”处停止，避免把候补人员并入正式推荐名单。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch69b.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch69c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch69c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch69c/school_year_summary.csv`

batch69c 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 湖北大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 20 |

可追溯来源：

- 湖北大学楚才学院推荐 2026 届优秀本科毕业生免试攻读研究生名单公示：`https://ccxy.hubu.edu.cn/info/1009/4691.htm`

batch69c 合并后的交付版（历史记录，batch70c 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,451 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,451 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,161 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,161 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：341 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，164 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,161 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：143 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch69c 清洗表 20 条；Excel `Public_Records` 140,161 行。

## 2026-05-24 追加批次：武汉大学 batch68b

batch68 先尝试从武汉大学信息管理学院、动力与机械学院、物理学院首页追踪 2026 届推免公告；首页会暴露大量新闻/导航上下文，已隔离未并入。随后改用明确的武汉大学信息管理学院公告原文作为 `batch68b`，正文为“专业名称 / 推免名单 / 专业 / 人数 / 姓名串”的竖排行结构。本批新增结构化正文行解析规则，支持该版式并过滤括号内“工程硕博专项”等说明。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch68b.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch68b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch68b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch68b/school_year_summary.csv`

batch68b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 武汉大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 65 |

可追溯来源：

- 武汉大学信息管理学院关于 2026 届本科毕业生免试攻读硕士学位研究生推荐名单的公告：`https://sim.whu.edu.cn/info/1776/108742.htm`

batch68b 合并后的交付版（历史记录，batch69c 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,431 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,431 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,141 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,141 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：340 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，163 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,141 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：142 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch68b 清洗表 65 条；Excel `Public_Records` 140,141 行。

## 2026-05-24 追加批次：武汉工程大学、武汉科技大学 batch67d

batch67d 转向湖北覆盖缺口学校。首轮验证武汉理工大学、中国地质大学（武汉）、武汉工程大学研究生院、武汉科技大学医学院、江汉大学、三峡大学等入口；武汉理工大学名单为 96MB 扫描版 PDF，CUG/WIT 研究生院附件返回验证码下载桥页，江汉大学/三峡大学/武汉科技大学医学院部分搜索命中实时 404/410，暂不并入。随后改用学院官网正文名单和可直链 PDF，最终并入武汉工程大学化工与制药学院、武汉科技大学 6 个学院来源。

本批新增导航容器过滤规则，避免 `nav/menu/aside/sidebar/header/footer` 中的“招生专业、培养动态”等导航项被正文名单解析误收；管理学院二级表头/合并单元格表暂时隔离，未并入。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch67d.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch67d/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch67d/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch67d/school_year_summary.csv`

batch67d 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 武汉工程大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 35 |
| 武汉科技大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 101 |

可追溯来源：

- 武汉工程大学化工与制药学院 2026 届推免名单公示：`https://mep.wit.edu.cn/info/1102/52172.htm`
- 武汉科技大学外国语学院 2026 届推免名单公示：`https://wgy.wust.edu.cn/info/1521/32092.htm`
- 武汉科技大学体育学院 2026 届推免名单公示：`https://tyxy.wust.edu.cn/info/1401/17492.htm`
- 武汉科技大学城市建设学院 2026 届推免名单 PDF：`https://cjxy.wust.edu.cn/__local/6/7D/0C/94487F7F915900CDAC791C17357_1C0D1D07_14D6D.pdf`
- 武汉科技大学生命科学与健康学院 2026 届推免名单 PDF：`https://smkx.wust.edu.cn/__local/1/FE/49/A828995B6914BB5EB775415FD07_0F325004_1D5A6.pdf`
- 武汉科技大学电子信息学院 2026 届推免名单 PDF：`https://dx.wust.edu.cn/__local/0/11/8D/8285F41407BB04CA6212B129A26_5CB79BB4_1B889.pdf`
- 武汉科技大学理学院 2026 届推免名单 PDF：`https://lixueyuan.wust.edu.cn/__local/1/6C/C3/56CD0BBF5745CFBBBC82FA2D414_8A3EC583_EDD4.pdf`

batch67d 合并后的交付版（历史记录，batch68b 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,366 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,366 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：140,076 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：140,076 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：339 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，162 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 140,076 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：141 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch67d 清洗表 136 条；Excel `Public_Records` 140,076 行。

## 2026-05-24 追加批次：南京农业大学、苏州大学 batch66b

batch66b 继续补江苏覆盖表缺口院校。本轮验证南京农业大学、苏州大学、江苏大学、南京财经大学、南京理工大学、南京医科大学等官方入口；江苏大学、南京财经大学附件仍返回验证码下载页，南京理工大学/南京医科大学部分搜索命中实时返回站点提示页，暂不并入。最终并入的是南京农业大学两个学院官网正文名单，以及苏州大学音乐学院两个可直接下载的 PDF 名单。

本批新增了“专业标题 + 空格分隔姓名/单独成段姓名”的 HTML 正文名单解析规则，并用 `batch66b` 限制抓取深度，避免把“工作方案”类非名单页面误并入。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch66.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch66b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch66b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch66b/school_year_summary.csv`

batch66b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 南京农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 126 |
| 苏州大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 13 |

可追溯来源：

- 南京农业大学外国语学院 2026 年推荐优秀应届本科毕业生免试攻读研究生拟推荐名单公示：`https://foreign.njau.edu.cn/info/1053/6846.htm`
- 南京农业大学农学院 2026 年推荐优秀应届本科毕业生免试攻读研究生拟推荐名单公示：`https://nx.njau.edu.cn/info/1112/10565.htm`
- 苏州大学音乐学院 2026 年推荐优秀应届本科毕业生免试攻读研究生公示页：`https://music.suda.edu.cn/4b/ef/c9903a674799/page.htm`
- 苏州大学音乐学院音乐表演专业推免初选名单 PDF：`https://music.suda.edu.cn/_upload/article/files/07/2f/5427ae054892a1febec7b0ed277a/478cb752-e4ab-4d41-a2bb-b653830447c3.pdf`
- 苏州大学音乐学院音乐学专业推免初选名单 PDF：`https://music.suda.edu.cn/_upload/article/files/07/2f/5427ae054892a1febec7b0ed277a/9c89fe41-dbcc-4d95-b6c1-379edb40b0ed.pdf`

batch66b 合并后的交付版（历史记录，batch67d 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,230 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,230 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：139,940 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：139,940 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：337 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，160 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 139,940 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：140 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch66b 清洗表 139 条；Excel `Public_Records` 139,940 行

## 2026-05-24 追加批次：江苏科技大学、常州大学 batch65c

batch65c 转向江苏覆盖表缺口院校。本轮验证江苏科技大学、常州大学、南京邮电大学、江苏大学等官方入口；江苏大学公告入口实时 404，南京邮电大学列表自动追到的 2021 年“推免生拟录取人数统计”不是人员级名单，已在清洗阶段过滤。最终并入的是江苏科技大学三个学院 PDF 与一个学院 HTML 表格、常州大学推免正文表格。

本批新增了江苏科技大学复试排序 PDF 行解析规则，解决“姓名/考生编号在同一行但多列表头断裂”导致的错位问题。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch65.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch65c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch65c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch65c/school_year_summary.csv`

batch65c 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 江苏科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 649 |
| 常州大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 7 |

可追溯来源：

- 江苏科技大学海洋学院 2026 年硕士研究生招生调剂补录公示：`https://ocean.just.edu.cn/2026/0413/c10660a372170/page.htm`
- 江苏科技大学经济管理学院 2026 硕士研究生复试拟录取名单 PDF：`https://sem.just.edu.cn/_upload/article/files/65/02/edbb71c547f79ac7e9beec7bd3b1/9455ab54-b177-4b8d-8ca0-c952081f215a.pdf`
- 江苏科技大学船舶与海洋工程学院 2026 硕士研究生复试拟录取名单 PDF：`https://naoe.just.edu.cn/_upload/article/files/13/a2/d321e0c1480eb3a7fac0eefd1a6e/d7ccf873-0698-48f0-a912-f2a21a545277.pdf`
- 江苏科技大学机械工程学院 2026 硕士研究生复试拟录取名单 PDF：`https://jixie.just.edu.cn/_upload/article/files/05/7d/fa748fe3411a89b1563f39e2e528/8b0437aa-382d-49f4-9aa8-8437c2fa1648.pdf`
- 常州大学 2026 年拟接收推荐免试研究生名单：`https://gs.cczu.edu.cn/2025/1030/c13235a403294/page.htm`

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：134,091 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：134,091 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：139,801 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：139,801 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：335 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，158 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 139,801 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：138 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch65c 清洗表 656 条；Excel `Public_Records` 139,801 行

## 2026-05-24 追加批次：上海对外经贸大学、上海音乐学院 batch64

batch64 转向上海覆盖表缺口院校。本轮验证上海音乐学院、上海理工大学、上海体育大学、华东政法大学、上海对外经贸大学、上海财经大学、华东理工大学、同济大学、上海中医药大学、上海师范大学、华东师范大学、上海海事大学、上海应用技术大学等官方入口。多数公告页已撤下名单、改成动态查询或只保留公告正文；最终可稳定解析并入库的是上海音乐学院 PDF 名单和上海对外经贸大学公告页自动发现的 PDF 附件。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch64.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch64/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch64/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch64/school_year_summary.csv`

batch64 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 上海对外经贸大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,200 |
| 上海对外经贸大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 21 |
| 上海音乐学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 227 |
| 上海音乐学院 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 94 |

可追溯来源：

- 上海音乐学院 2026 年硕士研究生拟录取名单 PDF：`https://yjsb.shcmusic.edu.cn/_upload/article/files/f4/02/813646224fff8e987ebe5d623cd1/6378ef38-d182-48bf-820a-a0b1f83fd80d.pdf`
- 上海音乐学院 2026 年推免生拟录取名单 PDF：`https://yjsb.shcmusic.edu.cn/_upload/article/files/1a/50/2f399c5c4f7a97976c98d83bd435/362b48e0-1601-426f-aac2-7343fcc50ca7.pdf`
- 上海对外经贸大学 2026 年硕士待录取名单第一批 PDF：`https://www.suibe.edu.cn/_upload/article/files/0c/ce/bebeee46488ab48790cd01bb17f8/0dcc12e0-0827-480d-b60f-13bbf85fdef7.pdf`
- 上海对外经贸大学 2026 年硕士研究生待录取名单第二批 PDF：`https://www.suibe.edu.cn/_upload/article/files/ff/83/63e04e3445aa9ffceea17302a145/fddafa62-db21-4312-9563-95235a6e93b0.pdf`
- 上海对外经贸大学 2026 年接收推荐免试研究生拟录取名单 PDF：`https://www.suibe.edu.cn/_upload/article/files/0f/e6/d7852cd84fbd9cf45e46f5a9770b/eba14a72-121d-42da-a36e-c9cc66bbea55.pdf`

batch64 合并后的交付版（历史记录，batch65c 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：133,435 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：133,435 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：139,145 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：139,145 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：333 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，156 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 139,145 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：137 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch64 清洗表 2,542 条；Excel `Public_Records` 139,145 行

## 2026-05-24 追加批次：西安科技大学、西安理工大学 batch62

batch62 继续补覆盖表缺口院校。本轮验证华中师范大学、青岛理工大学、西南交通大学、西安科技大学、西安理工大学等官网入口；华中师范大学附件下载返回 HTML 中转页，青岛理工大学入口实时 404，西南交通大学入口实时 502。最终可稳定解析的是西安科技大学官网 HTML 名单和西安理工大学研究生院 PDF 名单。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch62.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch62/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch62/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch62/school_year_summary.csv`

batch62 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 西安科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,385 |
| 西安理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,165 |

可追溯来源：

- 西安科技大学 2026 年硕士研究生拟录取名单公示：`https://yjs.xust.edu.cn/info/1200/7691.htm`
- 西安理工大学 2026 年硕士研究生拟录取名单公示页：`https://yjsy.xaut.edu.cn/info/1064/4984.htm`
- 西安理工大学 2026 年硕士研究生拟录取名单 PDF：`https://yjsy.xaut.edu.cn/__local/D/AE/29/1A7661F34F67418399A88D88B3F_60D17CE1_1970E1.pdf`

batch62 合并后的交付版（历史记录，batch65c 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：130,893 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：130,893 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：136,603 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：136,603 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：329 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，154 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 136,603 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：137 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch62 清洗表 5,550 条；Excel `Public_Records` 136,603 行

## 2026-05-24 追加批次：上海工程技术大学 batch61

batch61 继续补覆盖表缺口院校。本轮验证厦门大学、天津大学、上海工程技术大学、上海对外经贸大学、上海海事大学、山东财经大学等官方入口；厦门大学若干搜索结果实时返回 404，上海对外经贸大学和上海海事大学入口返回 410，天津大学、山东财经大学页面未形成可结构化人员级记录。最终可稳定解析的是上海工程技术大学 2026 年硕士研究生拟录取公示 PDF。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch61.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch61/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch61/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch61/school_year_summary.csv`

batch61 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 上海工程技术大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,266 |

可追溯来源：

- 上海工程技术大学艺术设计学院 2026 年硕士研究生招生复试成绩及拟录取名单公示页：`https://xb.sues.edu.cn/84/05/c25048a295941/page.htm`
- 上海工程技术大学 2026 年硕士研究生拟录取公示名单 PDF：`https://xb.sues.edu.cn/_upload/article/files/c4/f8/703297f445029fec10c863354a89/b4cf6bd6-663c-4f12-974c-62d9af275ed1.pdf`

batch61 合并后的交付版（历史记录，batch62 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：125,343 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：125,343 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：131,053 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：131,053 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：326 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，152 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 131,053 行

batch61 验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：137 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch61 清洗表 2,266 条；Excel `Public_Records` 131,053 行

## 2026-05-24 追加批次：天津师范大学、闽南师范大学 batch60

batch60 继续补覆盖表缺口院校。本轮优先使用可静态解析的学院官网 HTML 表格和 `__local` PDF 直链；北京工商大学、福建师范大学等入口已抓取留证，但当前未从文本层形成可靠人员级记录，未并入清洗主表。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch60.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch60/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch60/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch60/school_year_summary.csv`

batch60 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 天津师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 58 |
| 天津师范大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 15 |
| 闽南师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 9 |

可追溯来源：

- 天津师范大学心理学部 2026 年硕士研究生拟录取名单公示：`https://psych.tjnu.edu.cn/info/1044/3699.htm`
- 天津师范大学心理学部 2026 年硕士研究生拟录取名单公示调剂：`https://psych.tjnu.edu.cn/info/1044/3719.htm`
- 天津师范大学心理学部 2026 年硕士研究生拟录取名单公示：`https://psych.tjnu.edu.cn/info/1044/3720.htm`
- 天津师范大学体育科学学院 2026 年硕士研究生拟录取名单 PDF：`https://tykx.tjnu.edu.cn/__local/7/76/DE/5107A13CFEA618D4F8C386790C5_F7D8746C_1A6B4.pdf`
- 天津师范大学政治与行政学院 2026 年接收推免硕士研究生拟录取名单 PDF：`https://zzyxz.tjnu.edu.cn/__local/4/77/24/76137066967FB3D96473FB18B7E_FA31512A_252F0.pdf`
- 天津师范大学政治与行政学院 2026 年接收推免硕士研究生拟录取名单二批次 PDF：`https://zzyxz.tjnu.edu.cn/__local/7/5E/97/B6D796FF7E2244E0B26C6E2607E_FC9F52FB_1A93B.pdf`
- 闽南师范大学新闻传播学院 2026 年硕士研究生一志愿拟录取名单公示：`https://sjc.mnnu.edu.cn/info/1058/7074.htm`

本批新增解析/质量规则：

- 过滤 PDF 表格中被误抽到姓名列的单独括号说明项，如“（定向、非定向）”，避免培养类型说明进入人员身份字段。

batch60 合并后的交付版（历史记录，batch61 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：123,077 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：123,077 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：128,787 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：128,787 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：325 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，151 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 128,787 行

batch60 验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：137 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch60 清洗表 82 条；Excel `Public_Records` 128,787 行

## 2026-05-24 追加批次：华南农业大学 batch59

batch59 继续补覆盖表缺口院校。本轮验证华南农业大学、华中师范大学、华东师范大学等官方源；华中师范大学和华东师范大学本次 seed URL 返回 404，保留失败证据但不并入。华南农业大学研究生招生信息网硕士拟录取公示和推荐免试直博生名单公示可直接下载 PDF 附件并解析。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch59.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch59_final/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch59_final/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch59_final/school_year_summary.csv`

batch59 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 华南农业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4,231 |
| 华南农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 28 |

可追溯来源：

- 华南农业大学 2026 年硕士研究生拟录取公示页：`https://yzb.scau.edu.cn/2026/0506/c2138a433804/page.htm`
- 华南农业大学 2026 年硕士研究生拟录取名单 PDF：`https://yzb.scau.edu.cn/_upload/article/files/6f/06/fe14ac6047c992bd27926c92c962/0f244edf-4464-4a6c-9c30-7496d69f5fc9.pdf`
- 华南农业大学 2026 年拟录取推荐免试直博生名单公示页：`https://yzb.scau.edu.cn/2025/1022/c2137a420201/page.htm`
- 华南农业大学 2026 年拟录取推荐免试直博生名单 PDF：`https://yzb.scau.edu.cn/_upload/article/files/b3/7e/16cc77f64791807ec0ae9abe5cac/abc129f3-e625-457d-b3b2-f71fccee97b9.pdf`

本批新增解析/质量规则：

- 修正通用表格解析中的错位行：当“专业代码|专业名”被 PDF 抽取到姓名列时，不再作为姓名入库，而是转入录取专业并标记复核。
- 过滤无姓名且“student_id”不是编号的短续行，避免专业/研究方向残片误入身份字段。
- 修正 Excel 构建脚本 `normalizeRows` 对大表使用展开参数导致的调用栈溢出，改为循环求最大列数。

batch59 合并后的交付版（历史记录，batch60 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：122,995 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：122,995 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：128,705 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：128,705 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：322 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，149 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 128,705 行

batch59 验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：136 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch59 清洗表 4,259 条；Excel `Public_Records` 128,705 行

## 2026-05-24 追加批次：四川农业大学 batch57、贵州大学 batch58

batch57/58 继续补覆盖表缺口院校。本轮先验证河北大学、北京航空航天大学、四川农业大学、东北林业大学等候选源；河北大学、北航、东北林业大学及四川农业大学资源学院等附件入口返回验证码下载页或中转页，保留抓取证据但不并入清洗主表。最终可结构化入库的是四川农业大学两个学院 HTML 表格，以及贵州大学研究生院 2026 年硕士拟录取名单（一）至（五）的 PDF 附件。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch57.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch58.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch57_fixed/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch57_fixed/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch58/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch58/records_public.csv`

batch57/58 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 四川农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 13 |
| 贵州大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 5,076 |

可追溯来源：

- 四川农业大学马克思主义学院 2026 年接收推免研究生拟录取结果公示：`https://mkszyxy.sicau.edu.cn/info/1841/11156.htm`
- 四川农业大学机电学院 2026 年推免研究生招生拟录取名单公示：`https://jdxy.sicau.edu.cn/info/1033/3874.htm`
- 贵州大学 2026 年硕士研究生拟录取名单公示（一）：`https://gs.gzu.edu.cn/2026/0402/c11835a266982/pagem.htm`
- 贵州大学 2026 年硕士研究生拟录取名单公示（二）：`https://gs.gzu.edu.cn/2026/0408/c11835a267217/pagem.htm`
- 贵州大学 2026 年硕士研究生拟录取名单公示（三）：`https://gs.gzu.edu.cn/2026/0421/c11835a271324/pagem.htm`
- 贵州大学 2026 年硕士研究生拟录取名单公示（四）：`https://gs.gzu.edu.cn/2026/0423/c11835a271647/pagem.htm`
- 贵州大学 2026 年硕士研究生拟录取名单公示（五）：`https://gs.gzu.edu.cn/2026/0427/c11835a271881/pagem.htm`

本批新增解析/质量规则：

- 修正正文段落名单解析：不再把“学院专业”这类泛化标题当作专业名，避免从“择优遴选”等正文措辞中误提取伪人名。
- 贵州大学 PDF 附件可由现有 PDF 表格规则解析，清洗后保留考生编号、姓名、学院、录取专业、初试/复试/总成绩等字段。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：118,736 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：118,736 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：124,446 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：124,446 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：320 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，148 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 124,446 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：134 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0；batch57 清洗表 13 条、batch58 清洗表 5,076 条；Excel `Public_Records` 124,446 行

## 2026-05-24 追加批次：山西大学、内蒙古医科大学、成都中医药大学 batch56

batch56 继续补覆盖表缺口院校。前置验证中，北京语言大学、西南林业大学、大连海事大学、大连医科大学、大连理工大学等页面的附件入口返回验证码/附件下载中转页，无法无人值守取得真实名单文件；本批最终采用可直接解析的 3 个官方源：山西大学 PDF 直链、内蒙古医科大学研究生院 HTML 表格、成都中医药大学现代中药产业学院 HTML 表格。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch56.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch56_final/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch56_final/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch56_final/school_year_summary.csv`

batch56 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 山西大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 391 |
| 内蒙古医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 18 |
| 成都中医药大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 6 |

可追溯来源：

- 山西大学 2026 年推免生（含直博生）拟录取名单 PDF：`https://yjszsw.sxu.edu.cn/docs/2025-10/6a4533211f9c40bb91203ff9e820b553.pdf`
- 内蒙古医科大学 2026 年接收推荐免试研究生拟录取名单公示：`https://yjsy.immu.edu.cn/info/1051/5165.htm`
- 成都中医药大学现代中药产业学院 2026 年推免生拟录取名单（第一批）：`https://www.cdutcm.edu.cn/xdzycyxy/info/1161/1851.htm`

本批新增解析/质量规则：

- 增加山西大学推免 PDF 7 列表解析，提取排名、姓名、录取层次、录取学院、专业代码、专业名称和复试成绩。
- 修正“推免生（含直博生）拟录取名单”标题分类，避免被普通“拟录取名单”关键词归为统考拟录取。
- 增加成都中医药大学 HTML 表格解析，补齐现代中药产业学院、专业代码及名称、研究方向、综合面试成绩和导师字段。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：113,647 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：113,647 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：119,357 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：119,357 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：318 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，146 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 119,357 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：133 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0；batch56 清洗表 `needs_review` 0；Excel `Public_Records` 119,357 行

## 2026-05-24 追加批次：广西大学 batch54

batch54 继续补覆盖表缺口院校。本批采用广西大学研究生院官网招生工作栏目和官网公示页，纳入 2026 年接收推荐免试研究生拟录取名单、2026 年博士研究生第一批三份拟录取名单，以及 2025 年硕士研究生一志愿、调剂、补录和退役士兵计划拟录取名单。2026 年硕士统考主公示搜索命中链接当前返回 404，未并入。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch54.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch54_fixed/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch54_fixed/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch54_fixed/school_year_summary.csv`

batch54 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 广西大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,377 |
| 广西大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 201 |
| 广西大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 475 |

可追溯来源：

- 广西大学 2026 年接收推荐免试研究生拟录取名单公示：`https://yjsc.gxu.edu.cn/info/1007/4172.htm`
- 广西大学 2026 年博士研究生第一批（一）拟录取名单公示：`https://yjsc.gxu.edu.cn/info/1021/4496.htm`
- 广西大学 2026 年博士研究生第一批（二）拟录取名单公示：`https://yjsc.gxu.edu.cn/info/1021/4502.htm`
- 广西大学 2026 年博士研究生第一批（三）拟录取名单公示：`https://yjsc.gxu.edu.cn/info/1021/4507.htm`
- 广西大学 2025 年硕士研究生招生一志愿考生拟录取名单公示：`https://yjsc.gxu.edu.cn/info/1007/3714.htm`
- 广西大学 2025 年硕士研究生招生调剂复试拟录取名单公示：`https://yjsc.gxu.edu.cn/info/1007/3807.htm`
- 广西大学 2025 年硕士研究生招生调剂复试补录的拟录取考生名单公示：`https://yjsc.gxu.edu.cn/info/1007/3825.htm`

本批新增解析/质量规则：

- 增加广西大学 PDF 定宽表解析，处理“学院代码/学院/姓名/招生类型/计划/录取专业/复试成绩”的推免名单。
- 增加广西大学博士拟录取 PDF 解析，提取序号、姓名、录取专业代码及名称、录取学院、总成绩。
- 增加广西大学 2025 年硕士拟录取 PDF 解析，处理一志愿、调剂、补录等多种表头拆分形态；对排版碎裂严重且姓名/编号跨多行的少数民族骨干计划 PDF 暂不并入清洗表，避免产生无姓名伪记录。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：113,232 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：113,232 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：118,942 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：118,942 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：315 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，143 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 118,942 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：130 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0；batch54 清洗表姓名为空 0、`needs_review` 0；Excel `Public_Records` 118,942 行

## 2026-05-24 追加批次：广西民族大学 batch53

batch53 继续补覆盖表缺口院校。本批采用广西民族大学研究生院 2026 年硕士招生专题页作为官方目录，从中抽取 49 个学院级推免拟录取、一志愿拟录取、调剂拟录取公示页。实际抓取中，部分学院附件为 `download.jsp` 中转页，直接下载只返回中转/验证页面；可结构化入库的主要来自学院页内嵌的 VSB `__local` 静态 PDF。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch53.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch53/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch53/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch53/school_year_summary.csv`

batch53 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 广西民族大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 512 |

可追溯来源：

- 广西民族大学 2026 年硕士研究生招生专题页：`https://yjs.gxmzu.edu.cn/info/1081/23594.htm`
- 广西民族大学民族学与社会学学院 2026 年硕士研究生招生第一志愿拟录取名单公示：`https://msy.gxmzu.edu.cn/info/1003/60147.htm`
- 广西民族大学民族学与社会学学院 2026 年硕士研究生招生调剂拟录取名单 PDF：`https://msy.gxmzu.edu.cn/__local/A/1A/31/E32FAD8320D319477196694A452_290B747B_23182.pdf`
- 广西民族大学化学化工学院 2026 年硕士研究生招生调剂拟录取名单 PDF：`https://chem.gxmzu.edu.cn/__local/A/71/5F/6AA34C44303C5C812D403C45663_7D4DEA13_4C088.pdf`

本批新增解析/质量规则：

- 增加广西民族大学“拟录取考生汇总表”PDF 宽表解析，提取考生编号、姓名、专业代码及名称、研究方向、拟录取状态、总成绩、复试成绩和初试总分。
- 补充网页导航/公告残片过滤，剔除“关闭窗口、当前位置、快速通道、通知公告、详细信息”等从学院页正文误入人员表的记录。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：109,179 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：109,179 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：114,889 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：114,889 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：312 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，142 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 114,889 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：128 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0；Excel `Public_Records` 114,889 行

## 2026-05-24 追加批次：河北地质大学 batch52

batch52 继续从覆盖表缺口院校里找可无人值守抓取的官方源。本批验证大连理工大学、大连海事大学、东北师范大学、河北大学、河北经贸大学、河北地质大学等候选源；大连理工、大连海事、河北经贸等附件入口返回验证码或 `download.jsp` 中转页，东北师范大学外部查询页未直接给出名单表。最终采用河北地质大学官网静态 PDF 与研究生学院推免公示 PDF。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch52.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch52/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch52/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch52/school_year_summary.csv`

batch52 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 河北地质大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 13 |
| 河北地质大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 883 |

可追溯来源：

- 河北地质大学 2026 年硕士研究生招生复试拟录取名单 PDF：`https://www.hgu.edu.cn/__local/8/55/3D/7BFA2BB25DC13CDAEB509F1B9D5_45D1FA28_BC070.pdf`
- 河北地质大学 2026 年硕士研究生招生推免生拟录取名单公示页：`https://yjsxy.hgu.edu.cn/info/1026/2156.htm`
- 河北地质大学 2026 年硕士研究生招生推免生拟录取名单 PDF：`https://yjsxy.hgu.edu.cn/__local/D/40/F6/3B87BE1737DDB97E8C9B9427A5E_51DAD33F_D288.pdf`

本批新增解析/质量规则：

- 增加河北地质大学 PDF 专用解析，处理水印字符把每页部分行拆成“序号/姓名”和“考生编号/学院/成绩”的情况；硕士拟录取名单清洗后 1-883 序号连续。
- 增加河北地质大学推免 PDF 解析，拆出“姓名、普通计划、本科生学号、二级招生单位、专业代码、专业名称、学习方式、复试总成绩”。
- 修正清洗过滤顺序，保留“王浩名”等带有效考生编号、但姓名末尾含“名”的真实人名，避免被表头规则误删。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：108,667 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：108,667 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：114,377 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：114,377 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：311 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，141 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 114,377 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：126 个测试通过
- 质量扫描：缺少身份 0、表头/科目姓名 0、数字姓名 0；Excel `Public_Records` 114,377 行

## 2026-05-24 追加批次：河北工业大学 batch51

batch51 先验证北京航空航天大学、大连医科大学、大连外国语大学、河北工业大学、北京工商大学等候选源。北航、大连医科与大连外国语的附件入口返回验证码下载页或 `download.jsp` 中转页，北京工商大学页面只保留公示说明，暂不并入无人值守抓取。本批最终采用河北工业大学研究生院普通 HTML 公示页与静态 PDF 附件。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch51.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch51_v3/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch51_v3/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch51_v3/school_year_summary.csv`

batch51 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 河北工业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 365 |
| 河北工业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,244 |

本批新增解析/质量规则：

- 增加河北工业大学 PDF 专用宽表解析，提取招生单元、考生编号、姓名、录取专业、复试/初试/总成绩。
- 将“推免研究生拟录取名单”归入接收推免名单类型，并让附件继承父页面/种子的招生年份，避免把 `/docs/2025-10/` 发布时间误判为招生年份。
- 跳过只有“学院代码/专业代码/录取人数”的汇总表，继续过滤“性别”等表头碎片误入姓名列。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：107,771 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：107,771 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：113,481 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：113,481 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：309 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，140 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 113,481 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：123 个测试通过
- 质量扫描：缺少身份 0、表头/科目姓名 0、数字姓名 0；Excel `Public_Records` 113,481 行

## 2026-05-24 追加批次：中医药高校 batch50

batch50 继续优先补“覆盖表仍为 0、且官网 HTML/PDF 可稳定解析”的院校，新增安徽中医药大学、贵州中医药大学、广西中医药大学、湖南中医药大学、江西中医药大学 5 所学校。候选源中，天津中医药大学页面混有复试成绩表与拟录取表，青岛理工大学页面只保留公告正文，山西中医药大学 `download.jsp` 附件返回中转页，暂不并入本批。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch50.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch50/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch50/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch50/school_year_summary.csv`

batch50 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 安徽中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,409 |
| 贵州中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,531 |
| 广西中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 989 |
| 湖南中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 628 |
| 江西中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,359 |

本批新增解析/质量规则：

- 当 PDF 把“考生编号 + 学院”挤进同一列时，自动拆出考生编号并保留学院字段。
- 继续过滤 PDF 表头碎片和纯分数误入姓名列的记录。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：104,163 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：104,163 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：109,873 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：109,873 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：307 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，139 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 109,873 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：117 个测试通过
- 质量扫描：缺少身份 0、缺少核心身份字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0

## 2026-05-24 追加批次：综合 batch49

batch49 补入 5 所此前未覆盖或未充分覆盖院校的官网人员级名单：昆明医科大学、湖南师范大学、杭州电子科技大学、河南大学、河北师范大学。候选源中，湖南大学、河北大学等 `download.jsp` 附件会返回验证码/中转页，未纳入自动种子；电子科技大学为校级索引页但跨学院子域名较多，暂未并入本批。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch49.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch49_fixed3/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch49_fixed3/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch49_fixed3/school_year_summary.csv`

batch49 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 昆明医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,083 |
| 湖南师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,877 |
| 杭州电子科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 547 |
| 河南大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 312 |
| 河北师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,684 |

本批新增解析/质量规则：

- 兼容服务器把 `.xlsx` 声明为 `application/vnd.ms-excel` 的情况，优先用文件魔数识别真实 xlsx。
- 新增河南大学“推免生攻读研究生拟录取”PDF 行式解析，并补充该标题分类为接收推免拟录取。
- 过滤 PDF 每页重复表头续行，补充“总分/成绩/语听力”等表头词非人名规则。

batch49 当时交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：98,247 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：98,247 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：103,957 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：103,957 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：302 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，134 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 103,957 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：115 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0、性别+序号碎片 0

## 2026-05-24 追加批次：北京 batch48

batch48 补入北方工业大学 2026 年各学院/专业复试结果中的拟录取人员记录。该校官网总页把入口分散到多个学院子域名，部分学院页用 VSB PDF iframe 内嵌 PDF；本轮新增了该类 iframe PDF 发现规则，并新增“复试结果（含是否拟录取）”PDF 解析规则，只保留“是否拟录取=是”的行。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch48.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch48/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch48/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch48/school_year_summary.csv`

batch48 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 北方工业大学 | 2026 | postgraduate_admission_list | 216 |

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：89,745 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：89,745 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：95,455 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：95,455 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：297 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，129 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 95,455 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：110 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0、性别+序号碎片 0

## 2026-05-24 追加批次：上海 batch47

batch47 补入东华大学、上海电力大学 2 所此前覆盖缺口院校。东华大学官网公告页内嵌 PDF 可直接下载，新增“学院代码 + 学院名 + masked 考生号 + 姓名 + 学位类型 + 专业代码/名称 + 成绩”版式解析；上海电力大学第二批、第三批官网 PDF 只公开姓名、考试编号、成绩、专项计划、报考类别和学习方式，不含专业字段，已如实保留为空并将成绩写入备注。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch47.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch47/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch47/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch47/school_year_summary.csv`

batch47 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 东华大学 | 2026 | postgraduate_admission_list | 2,521 |
| 上海电力大学 | 2026 | postgraduate_admission_list | 696 |

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：89,531 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：89,531 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：95,241 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：95,241 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：296 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，128 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 95,241 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：107 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0、性别+序号碎片 0

## 早期新增官网批次：batch11

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260523_batch11.csv`

抓取结果：

- 种子：8 条
- 抓到文档：15 个
- 抓取失败：1 个
- 原始结构化记录：32 条
- 清洗记录：32 条
- 汇总组：1 个

batch11 主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 东南大学 | 2025 | recommendation_exemption_list | 32 |

batch11 可追溯来源示例：

- 东南大学数学学院列表：https://math.seu.edu.cn/jwxx/list.htm
- 东南大学网络空间安全学院首页：https://cyber.seu.edu.cn/main.htm
- 东南大学微电子学院列表：https://wx.seu.edu.cn/5269/list.htm
- 东南大学生命健康高等研究院列表：https://ins.seu.edu.cn/45100/list.htm
- 河海大学地球科学与工程学院首页：https://dxy.hhu.edu.cn/_t262/mainm.htm
- 苏州大学金螳螂建筑学院列表：https://arch.suda.edu.cn/5572/list1.htm

说明：batch11 证明列表页可以跟进到详情页，但 2026 年东南大学多个页面多为附件或弱结构正文；当前稳定抽出结构化记录的是东南大学生命健康高等研究院 2025 页。

## 之前新增官网批次：batch10b

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260523_batch10b.csv`

抓取结果：

- 种子：5 条
- 抓到文档：4 个
- 抓取失败：1 个
- 原始结构化记录：241 条
- 清洗记录：241 条
- 汇总组：2 个

batch10b 主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 北京理工大学 | 2026 | recommendation_exemption_list | 171 |
| 北京理工大学 | 2026 | incoming_recommendation_admission_list | 70 |

batch10b 可追溯来源示例：

- 北京理工大学法学院：https://law.bit.edu.cn/zsjy/yjszs/0ddd212fd73a45b0846586d810873777.htm
- 北京理工大学人工智能学院：https://ai.bit.edu.cn/tzgg/7b2adb3d0fbc4824bec98fc405783e1d.htm
- 北京理工大学化学与化工学院：https://cce.bit.edu.cn/tzgg/e948f639849142a5be23ee15adf2a770.htm
- 北京航空航天大学新媒体艺术与设计学院 PDF：https://art.buaa.edu.cn/__local/F/F4/F6/E7918456418D24A76B4CF39FADD_7ABCFD85_2CFA0.pdf

说明：batch10 初版中的北京统一入口多为 404/412，已改用学院实际可访问页面组成 batch10b。北航 PDF 已保存，但未稳定抽出结构化记录。

## 之前新增官网批次：batch9

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260523_batch9.csv`

抓取结果：

- 种子：7 条
- 抓到文档：8 个
- 抓取失败：0 个
- 原始结构化记录：89 条
- 清洗记录：89 条
- 汇总组：2 个

batch9 主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 合肥工业大学 | 2026 | recommendation_exemption_list | 83 |
| 安徽师范大学 | 2026 | recommendation_exemption_list | 6 |

batch9 可追溯来源示例：

- 合肥工业大学化学与化工学院：https://hgxy.hfut.edu.cn/2025/0911/c9386a314587/page.htm
- 安徽师范大学法学院：https://law.ahnu.edu.cn/info/1271/32996.htm
- 安徽师范大学数学与统计学院：https://math.ahnu.edu.cn/info/1218/24510.htm
- 安徽师范大学化学与材料科学学院：https://chemjxw.ahnu.edu.cn/info/1036/3097.htm
- 安徽中医药大学护理学院：https://hlxy.ahtcm.edu.cn/info/1571/5841.htm

说明：batch9 中部分安徽师范大学/安徽中医药大学页面为图片、附件或弱结构正文，已保存证据页，但当前只有合肥工业大学和安徽师范大学化材学院解析出结构化记录。

## 之前新增官网批次：batch8b

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260523_batch8b.csv`

抓取结果：

- 种子：5 条
- 抓到文档：5 个
- 抓取失败：0 个
- 原始结构化记录：100 条
- 清洗记录：99 条
- 汇总组：5 个

batch8b 主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 河南工业大学 | 2026 | recommendation_exemption_list | 36 |
| 上海外国语大学 | 2026 | recommendation_exemption_list | 27 |
| 中南林业科技大学 | 2026 | recommendation_exemption_list | 17 |
| 中南大学 | 2026 | recommendation_exemption_list | 11 |
| 郑州大学 | 2026 | recommendation_exemption_list | 8 |

batch8b 可追溯来源示例：

- 上海外国语大学国际工商管理学院：https://sbm.shisu.edu.cn/0b/f6/c7293a199670/page.htm
- 河南工业大学电气工程学院：https://cee.haut.edu.cn/info/1013/11301.htm
- 郑州大学基础医学院：https://www5.zzu.edu.cn/jcyxy/info/1107/4580.htm
- 中南大学体育教研部：https://sports.csu.edu.cn/info/2323/8359.htm
- 中南林业科技大学食品科学与工程学院：https://spxy.csuft.edu.cn/info/1561/5981.htm

说明：batch8 初版中有若干搜索缓存旧 URL 返回 404，因此已用 batch8b 的可访问官网 URL 替换。

## 之前新增官网批次：batch7

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260522_batch7.csv`

抓取结果：

- 种子：8 条
- 抓到文档：8 个
- 抓取失败：0 个
- 原始结构化记录：336 条
- 清洗记录：336 条
- 汇总组：7 个

batch7 主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 成都信息工程大学 | 2026 | recommendation_exemption_list | 188 |
| 华南师范大学 | 2026 | incoming_recommendation_admission_list | 51 |
| 湖北工业大学 | 2026 | recommendation_exemption_list | 32 |
| 燕山大学 | 2026 | recommendation_exemption_list | 25 |
| 中国社会科学院大学 | 2026 | recommendation_exemption_list | 14 |
| 苏州科技大学 | 2026 | recommendation_exemption_list | 13 |
| 河南中医药大学 | 2026 | recommendation_exemption_list | 13 |

batch7 可追溯来源示例：

- 河南中医药大学医学院：https://hnyxy.hactcm.edu.cn/info/1049/32427.htm
- 湖北工业大学生命科学与健康工程学院：https://life.hbut.edu.cn/info/1052/2996.htm
- 燕山大学西里西亚智能科学与工程学院：https://scise.ysu.edu.cn/info/1051/1551.htm
- 华南师范大学生命科学学院：https://life.scnu.edu.cn/a/20251011/6586.html
- 成都信息工程大学教务处：https://jwc.cuit.edu.cn/info/1243/3439.htm
- 中国社会科学院大学政府管理学院：https://sg.ucass.edu.cn/info/1149/4984.htm

## 之前新增官网批次：batch6

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260522_batch6.csv`

抓取结果：

- 种子：10 条
- 抓到文档：11 个
- 原始结构化记录：328 条
- 清洗记录：328 条
- 汇总组：7 个

batch6 主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 黑龙江科技大学 | 2026 | recommendation_exemption_list | 157 |
| 北京交通大学 | 2026 | recommendation_exemption_list | 41 |
| 中南大学 | 2026 | recommendation_exemption_list | 35 |
| 中南财经政法大学 | 2026 | recommendation_exemption_list | 34 |
| 南京中医药大学 | 2026 | recommendation_exemption_list | 31 |
| 中北大学 | 2026 | recommendation_exemption_list | 25 |
| 内蒙古科技大学 | 2026 | recommendation_exemption_list | 5 |

batch6 可追溯来源示例：

- 中北大学电气与控制工程学院：https://ece.nuc.edu.cn/info/1009/19035.htm
- 黑龙江科技大学教务处：https://jwc.usth.edu.cn/info/1003/2285.htm
- 南京中医药大学针灸推拿学院/养生康复学院：https://el.njucm.edu.cn/2025/0909/c1670a160424/pagem.htm
- 中南财经政法大学公共管理学院：https://ggglxy.zuel.edu.cn/2025/0913/c11247a405436/pagem.htm
- 北京交通大学软件学院：https://sse.bjtu.edu.cn/cms/item/1088.html

## 之前新增官网批次：batch5

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260522_batch5.csv`

抓取结果：

- 种子：10 条
- 抓到文档：10 个
- 原始结构化记录：305 条
- 清洗记录：305 条
- 汇总组：7 个

batch5 主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 上海外国语大学 | 2026 | recommendation_exemption_list | 79 |
| 四川大学 | 2026 | recommendation_exemption_list | 69 |
| 中南大学 | 2026 | recommendation_exemption_list | 60 |
| 郑州大学 | 2026 | recommendation_exemption_list | 32 |
| 内蒙古科技大学 | 2026 | recommendation_exemption_list | 29 |
| 上海交通大学 | 2026 | recommendation_exemption_list | 18 |
| 安徽农业大学 | 2026 | recommendation_exemption_list | 18 |

batch5 可追溯来源示例：

- 上海外国语大学卓越学院：https://www.honors.shisu.edu.cn/0c/1b/c5475a199707/page.htm
- 郑州大学公共卫生学院：https://sph.zzu.edu.cn/info/1212/5226.htm
- 四川大学建筑与环境学院：https://acem.scu.edu.cn/info/1003/13570.htm
- 中南大学粉末冶金研究院：https://pmri.csu.edu.cn/info/1126/5318.htm
- 上海交通大学体育系：https://tiyuxi.sjtu.edu.cn/info/1077/29121.htm

## 验证记录

- crawler 测试：`python -m unittest tests.test_graduate_outcome_crawler`
- 最新通过：59 个测试通过
- 统一包计数：`master_records_clean.csv` 11,968 条，`master_records_public.csv` 11,968 条，`school_year_source_summary.csv` 200 行
- A 类 CHSI/研招网主表：`master_records_clean.csv` 7,568 条，`master_records_public.csv` 7,568 条，`master_school_year_summary.csv` 152 行
- B 类官网主表：`records_clean.csv` 4,400 条，`records_public.csv` 4,400 条，`school_year_summary.csv` 48 行
- 覆盖表：`official_recommendation_school_coverage.csv` 430 所院校，45 所已精确匹配官网推免记录
- Excel 工作簿：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch12b

本批次面向辽宁未覆盖院校，成功从辽宁大学研究生院官网公示页及附件 PDF 抽取 2026 年接收推荐免试攻读研究生拟录取名单。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch12.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch12b/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch12b/records_public.csv`

batch12b 结果：

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 辽宁大学 | 2026 | recommendation_exemption_list | 352 |

来源：

- 辽宁大学研究生院公示页：https://grs.lnu.edu.cn/info/12169/71843.htm
- 辽宁大学附件 PDF：https://grs.lnu.edu.cn/26tmgsmd.pdf

## 2026-05-23 追加批次：batch13c

本批次补北京地区官网 B 源，使用搜索结果筛选出的官网公示页/PDF 作为入口。batch13b 初次清洗后发现北京邮电大学博士推免 PDF 中两条长姓名换行导致列错位，已补充质量规则并复跑为 batch13c，主表只合并 batch13c。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch13b.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch13c/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch13c/records_public.csv`

batch13c 结果：

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 北京邮电大学 | 2026 | recommendation_exemption_list | 1432 |
| 清华大学 | 2026 | recommendation_exemption_list | 209 |

来源：

- 清华大学建筑学院公示页：https://www.arch.tsinghua.edu.cn/info/gg/2984
- 清华大学电子工程系 PDF：https://www.ee.tsinghua.edu.cn/__local/5/86/73/D4BAC6FE05443FC1A07060EE09A_A7F3F1C0_1F713.pdf
- 清华大学网络科学与网络空间研究院 PDF：https://www.insc.tsinghua.edu.cn/20251030-1.pdf
- 北京邮电大学硕士推免 PDF：https://yzb.bupt.edu.cn/2026sstm.pdf
- 北京邮电大学博士推免 PDF：https://yzb.bupt.edu.cn/2026bstm.pdf

## 2026-05-23 追加批次：batch14

本批次继续补北京地区整校级官网入口，并修正跨入口重复问题：北京外国语大学两个公示入口会解析出同一批名单，现已在清洗阶段按“学校+年份+类型+路线+姓名/编号+学院+专业”去重。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch14.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch14/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch14/records_public.csv`

batch14 结果：

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 北京工业大学 | 2026 | recommendation_exemption_list | 732 |
| 北京外国语大学 | 2026 | incoming_recommendation_admission_list | 564 |
| 中国矿业大学（北京） | 2026 | postgraduate_admission_list | 77 |

来源：

- 北京工业大学公示页：https://yanzhao.bjut.edu.cn/info/1019/17865.htm
- 北京外国语大学硕士推免公示页：https://graduate.bfsu.edu.cn/info/1048/4006.htm
- 北京外国语大学博士推免公示页：https://graduate.bfsu.edu.cn/info/1074/4016.htm
- 中国矿业大学（北京）研究生招生网：https://yz.cumtb.edu.cn/

## 2026-05-23 追加批次：batch15 / batch15b

本批次继续补北京地区官网 B 源，重点抓取中国传媒大学、北京中医药大学、中国地质大学（北京）和中国石油大学（北京）的推免/拟录取公示。中国传媒大学官网使用嵌入式 `pdfsrc` 播放器，首轮从列表页只到公告页，补跑 batch15b 使用 PDF 直达链接完成解析。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch15.csv`
- 补跑种子：`data/seeds/official_site_recommendation_websearch_web_20260523_batch15b.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch15/records_clean.csv`
- 补跑清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch15b/records_clean.csv`

batch15 / batch15b 合并新增清洗记录：3,300 条。

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 中国传媒大学 | 2026 | recommendation_exemption_list | 817 |
| 中国传媒大学 | 2026 | postgraduate_admission_list | 1374 |
| 中国传媒大学 | 2025 | postgraduate_admission_list | 59 |
| 北京中医药大学 | 2026 | incoming_recommendation_admission_list | 382 |
| 中国地质大学（北京） | 2026 | recommendation_exemption_list | 11 |
| 中国石油大学（北京） | 2026 | incoming_recommendation_admission_list | 374 |
| 中国石油大学（北京） | 2026 | postgraduate_admission_list | 165 |
| 中国石油大学（北京） | 2026 | recommendation_exemption_list | 59 |
| 中国石油大学（北京） | 2025 | incoming_recommendation_admission_list | 59 |

说明：

- 北京语言大学公告页可访问，但附件下载入口要求验证码，本轮未形成结构化记录。
- 中国石油大学（北京）机械与储运工程学院入口返回 404；中国地质大学（北京）海洋学院补充入口返回 404，均保留在失败日志中。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

最新总量：

- B 类官网主表：9,306 条，60 个学校/年份/类型汇总组
- A+B 统一清洗包：16,874 条，212 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，52 所已精确匹配官网记录

## 2026-05-23 追加批次：batch16 / batch16b

本批次继续补北京重点高校官网 B 源，优先选择整校级或较高产入口：北京大学、北京师范大学、对外经济贸易大学、北京科技大学。对外经济贸易大学 PDF 使用脱敏姓名（如 `王**`），本轮同步修正清洗去重规则：没有学号且姓名为脱敏形式的记录不再按“姓名+学院+专业”合并，避免误删真实学生。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch16.csv`
- 补跑种子：`data/seeds/official_site_recommendation_websearch_web_20260523_batch16b.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch16/records_clean.csv`
- 补跑清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch16b/records_clean.csv`

batch16 / batch16b 合并新增清洗记录：4,475 条。

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 北京大学 | 2026 | recommendation_exemption_list | 2463 |
| 北京师范大学 | 2026 | postgraduate_admission_list | 694 |
| 北京科技大学 | 2026 | incoming_recommendation_admission_list | 576 |
| 对外经济贸易大学 | 2026 | incoming_recommendation_admission_list | 742 |

说明：

- 北京航空航天大学官网附件下载入口要求下载页校验，本轮未形成结构化记录。
- 北京师范大学推免 PDF 直链和中国人民大学教务处入口返回 404，已保留失败日志；北京师范大学硕士第二批 PDF 成功入库。
- 北京科技大学整校汇总页链接到多个学院/培养单位子站，batch16b 已补抓其中可访问的附件和页面；部分学院链接返回 404。

最新总量：

- B 类官网主表：13,833 条，64 个学校/年份/类型汇总组
- A+B 统一清洗包：21,401 条，216 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，56 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch17 / batch17b

本批次尝试补华南/上海和一个北京未覆盖高校，入口包括中山大学、深圳大学、华南理工大学、同济大学、东华大学、上海财经大学、华东理工大学、北京电子科技学院。抓取后发现部分站点采用动态系统页、跨域公示页或附件不在静态 HTML 中，未形成结构化名单；同时发现东华大学 PDF 中的专业汇总/表头行会被误识别为人员行，因此新增清洗质量规则。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch17.csv`
- 补跑种子：`data/seeds/official_site_recommendation_websearch_web_20260523_batch17b.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch17/records_clean.csv`
- batch17b 抓取无结构化记录，保留抓取文档和日志用于后续排查。

batch17 新增清洗记录：121 条。

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 北京电子科技学院 | 2026 | recommendation_exemption_list | 71 |
| 华南理工大学 | 2026 | postgraduate_admission_list | 49 |
| 深圳大学 | 2025 | incoming_recommendation_admission_list | 1 |

质量修正：

- 清洗阶段剔除无姓名/无编号的伪人员记录。
- 清洗阶段剔除表头/说明词被误识别为姓名的记录，例如“申请学院”“毕业学校”“其他”“在机械”等。
- 修复一类 CHSI 旧表错位：姓名列为考生编号、专业列为真实姓名时，自动将编号放入 `student_id`、真实姓名放入 `person_name`。
- 重建 CHSI 主表后，A 源从 7,568 条调整为 6,548 条，主要原因是剔除了历史残留的表头、序号和无身份伪记录。

最新总量：

- A 类 CHSI 主表：6,548 条，156 个学校/年份/类型汇总组
- B 类官网主表：13,915 条，67 个学校/年份/类型汇总组
- A+B 统一清洗包：20,463 条，223 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，59 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch18 / batch18b

本批次转向江苏、浙江及可直达 PDF 的未覆盖高校。batch18 首轮使用搜索结果中的公告页和系统页，发现部分入口已失效、动态化或对爬虫请求返回 403/404；batch18b 改用可直接访问的官方 PDF 直链，并保留南京大学、浙江理工大学公告页用于后续人工排查。

主要产物：

- 首轮种子：`data/seeds/official_site_recommendation_websearch_web_20260523_batch18.csv`
- 补跑种子：`data/seeds/official_site_recommendation_websearch_web_20260523_batch18b.csv`
- 补跑清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch18b/records_clean.csv`
- 补跑公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch18b/records_public.csv`

batch18b 新增清洗记录：1,249 条。

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 河海大学 | 2025 | incoming_recommendation_admission_list | 1228 |
| 南京林业大学 | 2026 | postgraduate_admission_list | 21 |

说明：

- 河海大学官网 PDF 成功解析 1,248 条原始记录，清洗后保留 1,228 条人员级记录。
- 南京林业大学家居与工业设计学院 PDF 成功解析 21 条记录，属于学院级公开名单。
- 浙江大学公示系统页和浙江理工大学公告页未暴露静态名单表格；南京大学官网页触发 SSL 握手失败；南昌大学、华北电力大学搜索索引中的 PDF 直链返回 404，均保留失败日志。
- 验证阶段新增一条清洗规则：剔除“公示期间”“院代码”“金融学(FRM方向)”等错位进入姓名列的非人员标签；B 源因此从 15,164 条调整为 15,150 条，A 源按同一规则重建为 5,754 条。

最新总量：

- A 类 CHSI 主表：5,754 条，152 个学校/年份/类型汇总组
- B 类官网主表：15,150 条，69 个学校/年份/类型汇总组
- A+B 统一清洗包：20,904 条，221 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，61 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch19

本批次继续补北京、江苏未覆盖高校，并同时纳入“推免接收拟录取”和“硕士统考拟录取”两类公开名单。成功入库来源包括中国农业大学、北京工业大学、北京化工大学、首都医科大学；中国药科大学搜索结果页返回 410，暂未入库。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch19.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch19/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch19/records_public.csv`

batch19 新增清洗记录：2,091 条。

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 中国农业大学 | 2026 | incoming_recommendation_admission_list | 1329 |
| 北京工业大学 | 2026 | recommendation_exemption_list | 733 |
| 北京化工大学 | 2026 | postgraduate_admission_list | 20 |
| 首都医科大学 | 2025 | recommendation_exemption_list | 9 |

质量修正：

- 补充规则剔除“类别/学习方式/分数”等表头行。
- 补充规则剔除姓名列为短数字序号（如 `01`）且无学号的专业目录行；首都医科大学 2026 目录型 PDF 因此未作为人员级名单入库。

最新总量：

- A 类 CHSI 主表：5,749 条，151 个学校/年份/类型汇总组
- B 类官网主表：17,240 条，72 个学校/年份/类型汇总组
- A+B 统一清洗包：22,989 条，223 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，64 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch20

本批次继续补北京未覆盖高校，优先尝试中央民族大学、中国政法大学、北京信息科技大学、外交学院四个官方入口。外交学院 PDF 成功解析；中国政法大学公告页未暴露静态附件；中央民族大学和北京信息科技大学搜索索引中的页面/PDF 在实时请求中返回 404，暂未入库。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch20.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch20/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch20/records_public.csv`

batch20 新增清洗记录：110 条。

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 外交学院 | 2026 | postgraduate_admission_list | 110 |

说明：

- 外交学院 PDF 可访问并成功抽取 111 条原始记录，清洗后保留 110 条人员级记录。
- 中央民族大学页面在搜索索引中可见，但实时官网请求返回 404；尝试附件直链仅返回短 HTML 响应，未作为证据入库。
- 北京信息科技大学 PDF 直链返回 404；中国政法大学页面可访问但未暴露静态附件。

最新总量：

- A 类 CHSI 主表：5,749 条，151 个学校/年份/类型汇总组
- B 类官网主表：17,350 条，73 个学校/年份/类型汇总组
- A+B 统一清洗包：23,099 条，224 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，65 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch21

本批次转向辽宁未覆盖高校，入口包括大连海事大学、大连理工大学、东北财经大学、大连医科大学。东北财经大学 2026 年硕士统考拟录取 PDF 成功形成大批量人员级记录；其它学校入口多为公告页或附件下载桥页，未能直接形成结构化记录。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch21.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch21/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch21/records_public.csv`

batch21 新增清洗记录：1,632 条。

| 学校 | 年份 | 类型 | 清洗记录数 |
| --- | --- | --- | ---: |
| 东北财经大学 | 2026 | postgraduate_admission_list | 1632 |

说明：

- 东北财经大学 2026 统考拟录取名单 PDF 成功解析 4,527 条原始记录，清洗去重后保留 1,632 条人员级记录。
- 东北财经大学推免名单 PDF、档案接收信息 PDF 以及大连海事、大连理工、大连医科的多个附件下载桥页未形成可用表格记录。
- 大连理工大学建设工程学院入口返回 404，保留失败日志。

最新总量：

- A 类 CHSI 主表：5,749 条，151 个学校/年份/类型汇总组
- B 类官网主表：18,982 条，74 个学校/年份/类型汇总组
- A+B 统一清洗包：24,731 条，225 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，66 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch22b

本批次继续辽宁未覆盖高校，入口包括东北大学、辽宁师范大学、沈阳建筑大学、沈阳工业大学、大连外国语大学、中国医科大学。东北大学和辽宁师范大学 PDF 成功形成清洗记录；其余入口暂未形成可用人员级名单。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch22.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch22b/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch22b/records_public.csv`

batch22b 新增清洗记录：7,586 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 东北大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4129 |
| 东北大学 | 2026 | postgraduate_admission_list | recommendation_exemption | 1524 |
| 辽宁师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1933 |

说明：

- 东北大学 PDF 解析后保留 5,653 条人员级记录；其中少量少数民族姓名在 PDF 文本中跨行，清洗规则已避免把数字学院码误写入姓名列。
- 辽宁师范大学 PDF 解析后保留 1,933 条人员级记录，姓名为源文件中的脱敏姓名。
- 沈阳工业大学入口返回 404；中国医科大学入口因 SSL legacy renegotiation 被当前运行时拒绝；辽宁师范大学推免页、沈阳建筑大学、大连外国语大学附件桥页未形成可用表格记录。

最新总量：

- A 类 CHSI 主表：5,749 条，151 个学校/年份/类型汇总组
- B 类官网主表：26,568 条，77 个学校/年份/类型汇总组
- A+B 统一清洗包：32,317 条，228 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，68 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch23/23b

本批次转向山东未覆盖高校。batch23 先跑学校研招网公告页和搜索直链，batch23b 追加更具体的 PDF/学院公示页；成功补入青岛科技大学、青岛农业大学、曲阜师范大学、山东大学、山东建筑大学、山东科技大学等记录。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch23.csv`
- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch23b.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch23/records_clean.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch23b/records_clean.csv`

batch23 新增清洗记录：513 条。batch23b 新增清洗记录：512 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 青岛科技大学 | 2021 | recommendation_exemption_list | recommendation_exemption | 227 |
| 青岛科技大学 | 2022 | recommendation_exemption_list | recommendation_exemption | 267 |
| 青岛农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 3 |
| 曲阜师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 16 |
| 山东大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 |
| 山东建筑大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 399 |
| 山东科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 111 |

说明：

- 中国海洋大学、山东中医药大学、山东理工大学、山东农业大学等入口遇到 403/502、附件桥页或实时 404，保留失败日志，未把不可验证内容入库。
- 针对山东建筑大学 PDF 的表格抽取问题，补充清洗规则：剔除分数字段误入身份列的行；修复“研究方向码及名称”粘连到姓名列的情况；剔除招生通知章节被误抽为人员记录的情况。
- CHSI 主表、B 类官网主表和统一包均已按新清洗规则重建。

最新总量：

- A 类 CHSI 主表：5,749 条，151 个学校/年份/类型汇总组
- B 类官网主表：27,593 条，84 个学校/年份/类型汇总组
- A+B 统一清洗包：33,342 条，235 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，74 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch24b

本批次转向浙江未覆盖高校。浙江工业大学两个 PDF、浙江师范大学外国语学院公示页、浙江大学历史学院 PDF 成功形成清洗记录；浙江理工大学等页面暂未暴露可用静态表格，浙江工商大学、浙江财经大学、中国美术学院、杭州师范大学部分入口实时返回 410/404 或 502。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch24.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch24b/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch24b/records_public.csv`

batch24b 新增清洗记录：5,598 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 浙江大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 17 |
| 浙江工业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 5193 |
| 浙江工业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 252 |
| 浙江师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 136 |

说明：

- 浙江工业大学 PDF 表头跨多行，通用表格解析只能识别到学院/专业列。本批次新增 PDF 行解析规则后，能够从“姓名 + 准考证号/脱敏身份证号”行中恢复人员记录。
- 旧版 batch24 只保留 153 条；新版 batch24b 重新抓取解析后保留 5,598 条。
- CHSI 主表、B 类官网主表和统一包均已按新解析/清洗规则重建。

最新总量：

- A 类 CHSI 主表：5,749 条，151 个学校/年份/类型汇总组
- B 类官网主表：33,191 条，88 个学校/年份/类型汇总组
- A+B 统一清洗包：38,940 条，239 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，77 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch25b

本批次转向吉林未覆盖高校。成功补入吉林大学、长春工业大学、吉林财经大学，以及吉林农业大学历史公告中的 2025 年推免/拟录取数据；延边大学附件需验证码、东北电力入口 404、长春理工附件暂未形成结构化人员记录。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch25b.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_combined/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_combined/records_public.csv`
- 吉林大学 PDF 本地解析产物：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_jlu_manual/records.jsonl`

batch25b 新增清洗记录：3,307 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 吉林大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 3058 |
| 吉林农业大学 | 2025 | incoming_recommendation_admission_list | recommendation_exemption | 198 |
| 吉林农业大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 33 |
| 吉林财经大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4 |
| 长春工业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 14 |

说明：

- 吉林大学 118 页 PDF 使用专用解析规则处理“姓名 + 专业代码”粘连和部分行省略学院名的问题，清洗后保留 3,058 条人员级记录。
- 吉林农业大学列表页抓到 2025 年公告；已把网页正文识别出的年份优先级调高，避免继承入口种子 2026 年。
- CHSI 主表、B 类官网主表和统一包均已按新解析/年份规则重建。

最新总量：

- A 类 CHSI 主表：5,749 条，151 个学校/年份/类型汇总组
- B 类官网主表：36,498 条，93 个学校/年份/类型汇总组
- A+B 统一清洗包：42,247 条，244 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，81 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch26c/26e

本批次转向黑龙江未覆盖高校。batch26c 补入东北农业大学、黑龙江八一农垦大学；batch26e 根据校正后的官方入口补入哈尔滨工程大学和哈尔滨理工大学。黑龙江中医药大学列表页可访问，但展开链接返回 404 或未形成静态名单记录。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch26.csv`
- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch26d.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch26c/records_clean.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch26e/records_clean.csv`

batch26c/26e 新增清洗记录：1,394 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 东北农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 191 |
| 黑龙江八一农垦大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 39 |
| 哈尔滨工程大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 1111 |
| 哈尔滨理工大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 53 |

说明：

- 黑龙江八一农垦 PDF 使用学院段落式排版，本批次新增解析规则，修复“男/女”被误作姓名的问题。
- 哈尔滨工程 PDF 原始行含“姓名、拟录取学院、专业代码、专业名称、招生类型”，本批次新增规则保留完整专业名称。
- 哈尔滨理工 PDF 原始行含“序号、姓名、招生类型、本科所在单位、拟录取学院、专业代码、专业名称、研究方向、成绩、备注”，本批次新增规则恢复本科所在单位、学院、专业和备注信息。
- CHSI 主表、B 类官网主表和统一包均已按新解析规则重建。

最新总量：

- A 类 CHSI 主表：5,749 条，151 个学校/年份/类型汇总组
- B 类官网主表：37,889 条，97 个学校/年份/类型汇总组
- A+B 统一清洗包：43,617 条，249 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，85 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 质量回扫

batch26 质检时发现少量历史记录存在姓名列仅为“男/女”的错列行。已新增清洗规则并重建 CHSI 主表、B 类官网主表、统一清洗包和 Excel 工作簿。

质量回扫后最新总量：

- A 类 CHSI 主表：5,728 条，152 个学校/年份/类型汇总组
- B 类官网主表：37,889 条，97 个学校/年份/类型汇总组
- A+B 统一清洗包：43,617 条，249 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，85 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：江苏 batch27 与最终质量回扫

江苏 batch27/batch27c 补入南京信息工程大学、南京航空航天大学、南京艺术学院、南京大学 4 所高校的官网人员级记录。新增可用清洗记录 1,723 条；其中南京大学工程学院 PDF 经“非推免/不含推荐免试”分类修正后归入 `postgraduate_admission_list`。

本轮同时对 CHSI 与官网主表重新应用质量规则，剔除分数、推荐书说明、考试科目/面试说明等误入姓名列的历史脏行。

最终交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,709 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：39,432 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：45,141 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：45,141 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：252 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，89 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

## 2026-05-23 追加批次：北京 batch28

北京 batch28 补入北京体育大学 2025/2026 年硕士拟录取名单与国际关系学院 2026 年硕士调剂拟录取名单，新增可用清洗记录 1,430 条。北航、北语附件下载页返回验证码桥页；中国政法页面返回 JS 动态挑战；中央民族、协和、北体部分详情页返回 404，暂未进入人员级主表。

本轮同时新增清洗规则，把“少干计划/士兵计划/专项计划”等计划类型从 `student_id` 尾部移入 `remarks`，并重建 B 类官网主表、统一清洗包和 Excel 工作簿。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,709 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：40,862 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：40,862 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：46,571 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：46,571 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：255 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，91 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：90 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩 0、计划文本残留于考生编号 0、未知文档类型 0

## 2026-05-23 追加批次：北京 batch29

北京 batch29 补入北京信息科技大学、北京联合大学、北京物资学院 3 所高校的 2026 年硕士拟录取人员级记录，新增可用清洗记录 2,145 条。北京建筑大学 PDF 文本层乱码严重，只产生表头碎片，已剔除；北京信息科技大学推免 PDF、中央美术学院 PDF 返回 404；中央戏剧学院招生公告列表返回 502；中央音乐学院附件页返回下载桥页，暂未进入人员级主表。

本轮同时新增碎片表头清洗规则，剔除“业代码/号”“业务一/外语”“管理类综/英语”等误入身份列的 PDF 文本层残片；并用全部 CHSI 原始抓取批次重建 A 类主表，清除历史考试科目表头碎片。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：43,007 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：43,007 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：48,717 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：48,717 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：259 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，94 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：92 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩/科目碎片 0、计划文本残留于考生编号 0、未知文档类型 0

## 2026-05-24 追加批次：安徽/海南/辽宁/湖北 batch46

batch46 补入安徽理工大学、海南大学、大连交通大学、长江大学 4 所此前覆盖缺口院校。长江大学两批 2026 年硕士拟录取 PDF 和 2026 年免试攻读研究生拟录取 PDF 均已结构化；安徽理工大学 2026 年硕士拟录取 PDF 因官网反盗链，使用已验证下载件作为本批本地证据补入；海南大学推免 PDF、大连交通大学推免 HTML 表格可直接解析。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch46.csv`

新增抓取/清洗产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch46_final_complete/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch46_final_complete/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch46_final_complete/school_year_summary.csv`

batch46 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 长江大学 | 2026 | postgraduate_admission_list | 2,422 |
| 安徽理工大学 | 2026 | postgraduate_admission_list | 1,487 |
| 海南大学 | 2026 | recommendation_exemption_list | 236 |
| 长江大学 | 2026 | recommendation_exemption_list | 202 |
| 大连交通大学 | 2026 | incoming_recommendation_admission_list | 4 |

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：86,314 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：86,314 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：92,024 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：92,024 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：294 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，126 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：105 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0、性别+序号碎片 0

## 2026-05-24 最新补充：安徽/福建/云南 batch42

batch42 补入福州大学、云南财经大学、安徽建筑大学、安徽医科大学 4 所此前未精确覆盖院校的官网人员级拟录取记录。原始结构化记录 9,285 条，经清洗和错位剔除后保留 7,925 条；同时用新增规则回扫剔除历史 PDF 抽取残片 42 条，因此当前 B 类官网主表相对上一版净增 7,883 条。

本批清洗中新增了“专业代码/学院名错位”和“学院/专业换行断词残片”两类回归规则，避免 PDF 表格抽取时将专业代码、学院残片误当姓名。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：58,879 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：58,879 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：64,589 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：64,589 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：273 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，107 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 福州大学 2026 年硕士研究生招生拟录取名单公示页：https://yjsy.fzu.edu.cn/info/1077/5901.htm
- 福州大学 2026 年硕士研究生招生拟录取名单 PDF：https://yjsy.fzu.edu.cn/system/_content/download.jsp?owner=1744984943&urltype=news.DownloadAttachUrl&wbfileid=18265061
- 云南财经大学 2026 年硕士研究生招生一志愿拟录取名单 PDF：https://www.ynufe.edu.cn/__local/D/B2/1A/F363D5CBFD24DD547DC3EAA8072_CCC20BB7_A9F2B.pdf
- 安徽建筑大学 2026 年硕士研究生一志愿拟录取名单公示：https://www.ahjzu.edu.cn/yjsc/_t131/2026/0427/c5263a269249/page.htm
- 安徽医科大学第一附属医院 2026 年硕士生招生调剂二轮复试结果及拟录取名单 PDF：https://www.ayfy.com/__local/0/AD/5A/3C02C79D52B6AC047DB196C80DB_A062B827_91F3.pdf

验证：

- batch42 抓取清洗：7,925 条记录，质量扫描中缺身份、缺核心字段、未知文档类型、数字姓名、表头姓名、断词残片均为 0。
- 工作簿重建输出：公开明细 64,589 行、汇总 273 行、覆盖追踪 430 行。

## 2026-05-24 最新补充：黑龙江/湖南/江苏 batch43

batch43 补入哈尔滨工业大学、湖南农业大学、江南大学 3 所此前未精确覆盖院校的官网人员级拟录取记录。哈尔滨医科大学、黑龙江中医药大学、哈尔滨体育学院、哈尔滨师范大学、湖南师范大学、北京工商大学等页面和附件下载桥页已抓取留证，但本轮未形成静态可解析人员明细。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：62,071 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：62,071 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：67,781 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：67,781 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：276 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，110 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 哈尔滨工业大学 2026 年硕士研究生招生考试拟录取名单 PDF：https://sa.hit.edu.cn/_upload/article/files/44/0d/bc5caca740649aaa03609adbffd5/0d01e1fa-ec0c-48e2-99b1-a3c97362322b.pdf
- 湖南农业大学 2026 年硕士研究生招生拟录取名单公示页：https://yjsy.hunau.edu.cn/yjszs/sszs/zytz_1592/202604/t20260430_518203.html
- 湖南农业大学 2026 年硕士研究生拟录取名单 PDF：https://yjsy.hunau.edu.cn/yjszs/sszs/zytz_1592/202604/P020260430631407939267.pdf
- 江南大学食品学院 2026 年硕士研究生建议录取名单：https://foodsci.jiangnan.edu.cn/info/1172/19005.htm
- 江南大学食品学院拟录取名单 PDF：https://foodsci.jiangnan.edu.cn/__local/3/C5/56/1F8BADBFFBD02A2C8D0742408AD_D08B694D_244CB.pdf

验证：

- batch43 抓取清洗：原始结构化记录 3,321 条，清洗记录 3,192 条，抓取失败 0 个。
- batch43 批次质量扫描：缺身份 0、缺核心字段 0、未知文档类型 0、数字姓名 0、表头姓名 0、断词残片 0。
- 工作簿重建输出：公开明细 67,781 行、汇总 276 行、覆盖追踪 430 行。

## 2026-05-24 最新补充：陕西/北京/重庆 batch45

batch45 继续优先使用实时可直接下载的官方 PDF 直链，并补充可静态解析的官网 HTML 表格页。本批成功补入西北农林科技大学、西北大学、西北工业大学、北京建筑大学、西南政法大学 5 所学校的 2026 年推免/硕士拟录取人员级记录。西安交通大学医学部 PDF、天津师范大学经济学院 PDF 已抓取留证，但当前文本层未形成稳定清洗记录。本轮新增西南政法大学“两行一条记录”PDF 解析规则、北京建筑大学拆分表头 PDF 解析规则，并补充回归测试。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：81,963 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：81,963 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：87,673 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：87,673 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：289 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，122 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

batch45 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 西北农林科技大学 | 2026 | incoming_recommendation_admission_list | 1759 |
| 西南政法大学 | 2026 | incoming_recommendation_admission_list / postgraduate_admission_list | 946 |
| 西北大学 | 2026 | postgraduate_admission_list | 679 |
| 北京建筑大学 | 2026 | postgraduate_admission_list | 565 |
| 西北工业大学 | 2026 | postgraduate_admission_list | 247 |

可追溯来源：

- 西北农林科技大学 2026 年接收推荐免试研究生拟录取名单 PDF：https://yz.nwafu.edu.cn/docs/2025-10/c6371e81d1134a85a0e13282846f684c.pdf
- 西北大学 2026 年硕士研究生拟录取名单 PDF：https://yjs.nwu.edu.cn/xibeidaxue2026nianshuoshiyanjiushengniluqumingdangongshi.pdf
- 西北工业大学计算机学院 2026 年硕士研究生拟录取名单：https://jsj.nwpu.edu.cn/info/1599/29155.htm
- 北京建筑大学 2026 年硕士研究生拟录取名单 PDF：https://yjsy.bucea.edu.cn/docs/2026-04/7986cc391a7644a0bd4d1ccde8823c6a.pdf
- 西南政法大学 2026 年推荐免试研究生拟录取名单 PDF：https://yjsy.swupl.edu.cn/docs/2025-10/1a7a0515d32443db9cc9c93a1d73a444.pdf

验证：

- batch45 最终抓取：11 个种子，实际抓到页面/附件 12 个，原始结构化记录 7,840 条，抓取失败 0 个。
- batch45 清洗：4,196 条有效记录；缺身份 0、缺核心字段 0、未知文档类型 0、数字姓名 0、表头姓名 0、性别+序号碎片 0。
- 工作簿重建输出：公开明细 87,673 行、汇总 289 行、覆盖追踪 430 行。

## 2026-05-24 最新补充：湖北/江西/重庆 batch44

batch44 优先使用实时请求可直接下载的官网 PDF 直链，剔除验证码附件桥页和 404 页面。成功补入华中农业大学、南昌大学、江西农业大学、南昌航空大学、江西理工大学、重庆大学、四川外国语大学 7 所学校的 2026 年硕士拟录取人员级记录；四川农业大学管理学院 PDF 可下载但本轮未形成稳定结构化记录。重庆大学 PDF 存在“脱敏身份证号+性别进入姓名列、真实姓名进入学号列”的字段错位，本轮新增回归测试并修复；四川外国语大学 PDF 存在成绩列前置导致“分数进入姓名列”的错位，已补充清洗修复。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：77,767 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：77,767 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：83,477 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：83,477 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：283 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，117 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 华中农业大学 2026 年硕士研究生招生拟录取名单直链 PDF（示例）：https://yjs.hzau.edu.cn/301ssnlq2026.pdf
- 南昌大学 2026 年硕士研究生分学院拟录取名单 PDF：https://yjsy.ncu.edu.cn/__local/1/40/DD/D4363BDFFF0E263221936E949A8_19E1FF08_ECD9D.pdf
- 江西农业大学 2026 年硕士研究生拟录取名单 PDF：https://yzb.jxau.edu.cn/__local/C/49/9C/C0B42CFD28F6B06CDBB5D794103_FF810152_6DDF3.pdf
- 南昌航空大学 2026 年硕士研究生拟录取名单 PDF：https://yjs.nchu.edu.cn/upload/yjs/contentmanage/article/file/2026/04/30/%E5%8D%97%E6%98%8C%E8%88%AA%E7%A9%BA%E5%A4%A7%E5%AD%A62026%E5%B9%B4%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95.pdf?t=1777552560888
- 重庆大学 2026 年硕士研究生拟录取名单 PDF：https://yz.cqu.edu.cn/upload/202605/4b1f5c4d.pdf
- 四川外国语大学 2026 年硕士研究生拟录取名单 PDF：https://graduate.sisu.edu.cn/docs/2026-03/99977a52496d44c5a3a1c14e6c5d131c.pdf

验证：

- batch44 抓取：24 个源全部成功，原始结构化记录 20,113 条，抓取失败 0 个。
- batch44 清洗：15,696 条有效记录；缺身份 0、数字姓名 0、表头姓名 0、性别+序号碎片 0。
- 工作簿重建输出：公开明细 83,477 行、汇总 283 行、覆盖追踪 430 行。

## 2026-05-24 最新补充：上海 batch40/batch40b 与中科大 batch41

上海 batch40/batch40b 用于验证一批未覆盖高校的官网入口可爬性。华东理工大学详情页和列表页可以抓到，但名单主体为图片页，当前清洗链路暂未做 OCR，因此不并入人员级主表；上海海事大学、上海科技大学若干搜索入口实时返回 410；上海理工大学入口返回提示页。相关原始 HTML 和失败日志已保留在批次目录中。

中科大 batch41 从精准智能化学全国重点实验室官网 HTML 表格补入 2026 年硕士研究生拟录取名单 1 条，并入 B 类官网主表后净增 1 条。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：50,996 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：50,996 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：56,706 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：56,706 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：268 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，103 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 中国科学技术大学精准智能化学全国重点实验室 2026 年硕士研究生拟录取名单：https://pichem.ustc.edu.cn/2026/0402/c40930a725330/page.htm
- 华东理工大学研究生院招生录取列表：https://gschool.ecust.edu.cn/12750/list.htm
- 华东理工大学 2026 年硕士研究生拟录取名单公示：https://gschool.ecust.edu.cn/2026/0506/c12750a190107/page.htm

验证：

- batch41 抓取和清洗：1 条记录，失败 0 个。
- 工作簿重建输出：公开明细 56,706 行、汇总 268 行、覆盖追踪 430 行。

## 2026-05-24 追加批次：广东 batch35

广东 batch35 使用广东工业大学研究生招生网公开 PDF 直链，成功补入广东工业大学 2026 年推免生拟录取名单 330 条。同步复核的暨南大学页面存在正文 GET 410 与附件 403；北京航空航天大学附件进入验证码下载桥页，均暂未进入人员级主表。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：43,347 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：43,347 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：49,057 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：49,057 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：261 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，96 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：92 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩/科目碎片 0、计划文本残留于考生编号 0、未知文档类型 0、长姓名无编号可疑项 0

## 2026-05-24 追加批次：广东 batch37

广东 batch37 补入广东海洋大学和广州大学官网人员级记录。广东海洋大学退役士兵专项计划调剂考生拟录取名单抽取 31 条；广州大学建筑与城市规划学院调剂考生待录取名单抽取 20 条。广东海洋大学其它调剂/一志愿/推免页面和广州大学管理学院列表页已保存证据，但本轮未形成更多可用人员级明细。

同步质量回扫补充“业务课一/业务课二”考试科目表头碎片规则，并从中国石油大学（北京）历史官网记录中剔除 1 条“业务课一/外语”错位行。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：43,400 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：43,400 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：49,110 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：49,110 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：264 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，99 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：92 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩/科目碎片（含“业务课一/外语”）0、计划文本残留于考生编号 0、未知文档类型 0、长姓名无编号可疑项 0

## 2026-05-24 追加批次：广东 batch38

广东 batch38 补入汕头大学和南方科技大学官网人员级记录。汕头大学 2026 年硕士研究生拟录取名单抽取 1,812 条；南方科技大学 2025 年硕士研究生拟录取名单抽取 984 条。南方医科大学 2026 年统考拟录取与推免拟录取公示页已抓取留证，但附件在本轮进入下载桥页，暂未形成可解析明细。

批次清洗记录为 2,796 条；合并进 B 类官网主表时按 `record_id` 去重后净增 2,794 条。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：46,194 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：46,194 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：51,904 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：51,904 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：266 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，101 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 南方科技大学 2025 年硕士研究生拟录取名单 PDF：https://gs.sustech.edu.cn/static/upload/file/20250526/17482477527744.pdf
- 汕头大学 2026 年硕士研究生拟录取名单公示页：https://www.gs.stu.edu.cn/list/11/post/dccff0ab-00bd-4b4b-a6ed-0bc98437c93c
- 南方医科大学 2026 年硕士研究生拟录取考生名单公示：https://portal.smu.edu.cn/yzw/info/1031/12211.htm
- 南方医科大学 2026 年招收推荐免试研究生拟录取名单公示：https://portal.smu.edu.cn/yzw/info/1002/11811.htm

验证：

- 批次质量扫描：缺少身份 0、缺少核心字段 0、考试科目表头碎片 0、未知文档类型 0
- 工作簿重建输出：公开明细 51,904 行、汇总 266 行、覆盖追踪 430 行

## 2026-05-24 追加批次：上海 batch39/batch39b

上海 batch39/batch39b 补入复旦大学 2026 年考试招生硕士拟录取名单 4,801 条。复旦 PDF 使用“考生编号后五位 + 脱敏姓名 + 拟录取院系 + 分数”版式，本轮新增专项解析规则，并修正脱敏同名去重逻辑，避免“王*、张*”等同院系同名记录因编号不同仍被合并。华东师范大学、同济大学入口本轮实时返回 404；上海财经大学列表页可访问但未形成静态人员级明细；复旦推免页出现重定向循环，暂未入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：50,995 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：50,995 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：56,705 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：56,705 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：267 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，102 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 复旦大学 2026 年拟录取硕士研究生（不含推荐免试硕士生）名单公示：https://gsao.fudan.edu.cn/e6/ec/c15906a780012/page.htm
- 复旦大学 2026 年考试招生硕士拟录取名单 PDF：https://gsao.fudan.edu.cn/_upload/article/files/d1/72/6e8596f944a29d458e36f9607ff2/2a832c05-0a12-4904-87a0-24ca8cf25633.pdf
- 上海财经大学录取情况列表：https://gongkai.sufe.edu.cn/lqqk/list.htm

验证：

- 新增回归测试：复旦后五位编号 PDF 版式解析；脱敏同名但后五位编号不同保留为不同人员。
- 批次质量扫描：缺少身份 0、数字误入姓名列 0。
- 工作簿重建输出：公开明细 56,705 行、汇总 267 行、覆盖追踪 430 行

## 2026-05-24 追加批次：广东 batch36

广东 batch36 补入广东外语外贸大学研究生招生信息网的 2026 年港澳台研究生招生拟录取名单 3 条。同步抓取的硕士拟录取查询通知、统考第二/三批及变动公示页面均可访问，但附件进入验证码下载桥页，暂未形成静态可解析明细。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：43,350 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：43,350 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：49,060 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：49,060 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：262 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，97 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：92 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩/科目碎片 0、计划文本残留于考生编号 0、未知文档类型 0、长姓名无编号可疑项 0

## 2026-05-24 追加批次：辽宁 batch30

辽宁 batch30 针对当前覆盖缺口最多的省份补跑。首轮入口中大连海事大学站点响应缓慢并返回 502，已隔离；batch30c 成功补入沈阳建筑大学 2026 年推荐免试硕士研究生拟录取名单 10 条。大连理工大学、大连医科大学页面可访问但附件下载页返回桥页，未得到静态可解析名单文件；沈阳建筑大学建筑与规划学院 PDF 文本层仅抽出表头/空姓名/考号碎片，已剔除。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：43,017 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：43,017 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：48,727 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：48,727 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：260 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，95 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：92 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩/科目碎片 0、计划文本残留于考生编号 0、未知文档类型 0

## 2026-05-25 追加批次：batch113s 太原理工大学

batch113s 补入太原理工大学研究生院 2026 年官方 PDF 数据 345 条，其中硕士研究生一志愿拟录取名单 174 条、接收优秀本科毕业生免试攻读研究生拟录取名单 171 条。本轮同时修复两类解析问题：失效详情页跳转到学校首页时不再沿用种子文档类型，避免首页导航词误入人员名单；新增太原理工推免 PDF 的“姓名+毕业院校 / 学院代码 / 专业代码 / 研究方向 / 学习方式 / 招生类型 / 复试成绩”版式解析。

首都经济贸易大学 3 个拟录取公告页本轮可访问但仅下载到定向就业协议 DOCX，未形成静态人员级明细；首都师范大学搜索入口实时跳转到学校首页，已作为无人员级记录处理。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,163 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,163 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：166,873 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：166,873 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：404 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，224 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 太原理工大学接收 2026 届优秀本科毕业生免试攻读研究生拟录取名单公示：https://www.gs.tyut.edu.cn/info/1261/14959.htm
- 太原理工大学 2026 年硕士研究生招生一志愿拟录取名单公示：http://www.gs.tyut.edu.cn/info/1261/15649.htm
- 太原理工大学推免拟录取名单 PDF：https://www.gs.tyut.edu.cn/__local/E/CF/72/60E339DF1567346F1D6D1EF0EE1_5913842E_270E3.pdf
- 太原理工大学一志愿拟录取名单 PDF：http://www.gs.tyut.edu.cn/__local/3/91/82/57C0EDCA2879AD0D5B22C8623B8_581A69CE_CD34D.pdf

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：179 个测试通过（仅保留既有 ResourceWarning）。
- 批次质量扫描：345 条清洗记录，缺少人员姓名 0、缺少录取专业 0、数字误入录取专业 0、需人工复核 0。
- 工作簿结构校验：Overview 14 行、Source_Summary 405 行、Coverage 431 行、Public_Records 166,874 行；公式单元格 9，错误单元格 0，危险公式样式字符串 0。

## 2026-05-25 追加批次：batch114/batch115 兰州大学

batch114 先验证北京语言大学、东北师范大学、电子科技大学、北京协和医学院等缺口入口：北京语言大学附件进入验证码下载桥页，东北师范大学为动态查询入口，电子科技大学 48 个学院链接多数进入验证码附件或 HTTP 412，协和医学院当前结果页为 2027 空表，均未形成可静态爬取的人员级记录。

batch115 转向华东师范大学与兰州大学。华东师范大学两个招生系统页面可访问但未暴露静态名单；兰州大学法学院 2026 年接收推荐免试攻读硕士学位研究生拟录取名单 PDF 成功入库 101 条。本轮新增兰大法学院 PDF 专项解析：`报考专业` 写入 `admission_major`，`报考研究方向` 写入 `major`，面试/外语/总成绩写入 `remarks`；明确跳过“放弃”行，同时兼容备注列空白、姓名后粘页码和带 `·` 的较长姓名。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,264 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,264 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：166,974 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：166,974 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：405 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，225 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 兰州大学法学院 2026 年接收推荐免试攻读硕士学位研究生拟录取名单 PDF：https://laws.lzu.edu.cn/laws/upload/files/20250924/8beed878bbfc40b99d4bfe824b07fde3.pdf

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：180 个测试通过（仅保留既有 ResourceWarning）。
- 批次质量扫描：101 条清洗记录，缺少人员姓名 0、缺少录取专业 0、数字误入专业字段 0、需人工复核 0、包含“放弃”记录 0。
- 工作簿结构校验：Overview 14 行、Source_Summary 406 行、Coverage 431 行、Public_Records 166,975 行；公式单元格 9，错误单元格 0，危险公式样式字符串 0。

## 2026-05-25 追加批次：batch116 上海海事大学

batch116 继续排查缺口院校，种子覆盖河北大学、山西财经大学、华东政法大学、山东师范大学、贵州师范大学、上海海事大学。河北大学、山西财经大学官方推免公示页可访问但附件仍进入下载桥页；华东政法大学公示页未暴露人员级明细；山东师范大学与贵州师范大学线索 URL 返回 404。上海海事大学 2026 年博士研究生拟录取名单公示页直接包含 HTML 表格，成功入库 154 条。

本轮新增 HTML 表格解析：识别“考生编号 / 姓名 / 一级学科名称 / 报考类别 / 综合面试成绩 / 备注”版式，将一级学科写入 `admission_major`，报考类别与面试成绩写入 `remarks`，解决通用表头映射遗漏“一级学科名称”导致专业字段为空的问题。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,418 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,418 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：167,128 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：167,128 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：407 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，226 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 上海海事大学 2026 年博士研究生拟录取名单公示：https://yz.shmtu.edu.cn/2026/0522/c8926a293126/page.htm

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：181 个测试通过（仅保留既有 ResourceWarning）。
- 批次质量扫描：154 条清洗记录，缺少人员姓名 0、缺少录取学科 0、需人工复核 0。
- 工作簿结构校验：Overview 14 行、Source_Summary 408 行、Coverage 431 行、Public_Records 167,129 行；公式单元格 9，错误单元格 0，危险公式样式字符串 0。

## 2026-05-25 追加批次：batch117 西北政法大学

batch117 覆盖西安交通大学、西安电子科技大学、西北政法大学、桂林医科大学、海南医科大学、西北师范大学等缺口院校。西安交通大学多个学院页和西电校级公示页可访问但未暴露可解析人员表；西安交通大学医学部入口返回 502，桂林医科大学远端断开，海南医科大学返回 404，西北师范大学返回 412。西北政法大学官方 `.xls` 附件成功入库 179 条。

本轮新增旧版 `.xls` 解析兜底：Windows 环境下使用本机 Excel 将 BIFF `.xls` 临时转换为 `.xlsx`，再复用现有表格解析；解决官方旧 Excel 附件无法由 `openpyxl` 直接读取的问题。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,597 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,597 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：167,307 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：167,307 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：408 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，227 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 西北政法大学 2026 年推荐免试硕士研究生拟录取名单附件：https://grs.nwupl.edu.cn/wcm.files/upload/CMSgrs/202511/20251105085754878.xls

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：182 个测试通过（仅保留既有 ResourceWarning）。
- 批次质量扫描：179 条清洗记录，缺少人员姓名 0、缺少学院/专业 0、需人工复核 0。
- 工作簿结构校验：Overview 14 行、Source_Summary 409 行、Coverage 431 行、Public_Records 167,308 行；公式单元格 9，错误单元格 0，危险公式样式字符串 0。

## 2026-05-25 追加批次：batch118/batch119 大连大学

batch118 继续排查昆明理工大学、西南交通大学、西南林业大学、西安交通大学、西南医科大学等缺口入口。可访问页面多指向 `download.jsp` 附件下载桥，页面要求验证码下载附件；西安交通大学相关页面未暴露静态人员级名单，因此本批未并入记录。

batch119 转向宁波大学、大连大学、哈尔滨师范大学、南京财经大学、南京医科大学、东北电力大学、上海师范大学等入口。大连大学 2026 年接收推荐免试研究生拟录取名单 PDF 可直接下载并成功入库 5 条；宁波大学、哈尔滨师范大学、南京财经大学附件仍进入验证码下载桥，东北电力大学入口返回 404，其余页面未形成可解析人员级记录。

本轮新增大连大学 PDF 专项解析：识别“报考院系 / 拟录取专业代码 / 拟录取专业名称 / 研究方向 / 复试成绩 / 学习方式 / 层次”版式，将专业代码写入 `major`，代码和专业名合并写入 `admission_major`，研究方向、复试成绩、全日制和硕士层次写入 `remarks`。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,602 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,602 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：167,312 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：167,312 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：409 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，228 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 大连大学 2026 年接收推荐免试研究生拟录取名单公示页：https://yjs.dlu.edu.cn/info/1065/3633.htm
- 大连大学 2026 年接收推荐免试研究生拟录取名单 PDF：https://yjs.dlu.edu.cn/__local/0/A6/6B/E8A23D395901FC1BB2DE886318C_48A9DBCA_1F13D.pdf

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：183 个测试通过（仅保留既有 ResourceWarning）。
- batch119b 清洗表：5 条清洗记录，缺少人员姓名 0、缺少专业字段 0、需人工复核 0。
- 工作簿结构校验：Overview 14 行、Source_Summary 410 行、Coverage 431 行、Public_Records 167,313 行；公式错误扫描 0 条。

## 2026-05-25 追加批次：batch120/batch121 广西师范大学/桂林理工大学

batch120 继续排查缺口院校官方入口，覆盖湖南大学、华中师范大学、福建师范大学、福建农林大学、集美大学、中南民族大学、华侨大学、北京语言大学、济南大学等。湖南大学、华中师范大学、集美大学等页面的名单附件均进入验证码下载桥；福建师范大学、华侨大学、北京语言大学、济南大学部分搜索命中页返回提示页或 404；中国海洋大学通知列表仅保留“公示已结束”附件文字，未暴露人员名单文件。本批未合并记录，但新增“后台管理”页面导航噪声过滤，避免站点维护入口被误识别为人员姓名。

batch121 转向正文表格或直链 PDF。广西师范大学 2026 年硕士研究生拟录取名单 PDF 可直接下载并解析，补入 1,796 条；桂林理工大学计算机科学与工程学院软件工程专业推免拟录取 PDF 补入 1 条。河南医药大学、广州医科大学、云南师范大学页面可访问但未暴露静态人员级明细或附件进入验证码下载桥，暂未并入。

本轮新增两类专项解析：广西师范大学 PDF 的“考生编号 / 姓名 / 报考单位 / 学习方式 / 专业代码 / 专业名称 / 研究方向代码 / 初试总分 / 复试成绩 / 总成绩”版式；桂林理工大学 PDF 中跨上下行拆分的学院名和专业名版式。修复后专业代码写入 `major`，代码和专业名合并写入 `admission_major`，学习方式、研究方向代码和成绩写入 `remarks`。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：163,399 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：163,399 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：169,109 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：169,109 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：411 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，230 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 广西师范大学 2026 年硕士研究生一志愿考生拟录取名单公示页：http://www.yz.gxnu.edu.cn/2026/0403/c4626a339485/page.htm
- 广西师范大学 2026 年硕士研究生拟录取名单 PDF：http://www.yz.gxnu.edu.cn/_upload/article/files/06/ce/18fa0a8b4ef4a461bad796725b2f/a788bd4e-af69-4569-9849-784d29b6a3c9.pdf
- 桂林理工大学计算机科学与工程学院软件工程专业推免拟录取名单 PDF：https://cise.glut.edu.cn/jisuanjixueyuan2026nianshuoshiyanjiushengtuimianshengniluqumingdangongshi.pdf

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：185 个测试通过（仅保留既有 ResourceWarning）。
- batch121c 清洗表：1,797 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，学习方式/分数误入 `admission_major` 0。
- 工作簿结构校验：Overview 14 行、Source_Summary 412 行、Coverage 431 行、Public_Records 169,110 行；公式错误扫描 0 条。

## 2026-05-25 追加批次：batch131/batch132 华南师范大学/南京医科大学

本轮把华南师范大学 2026 年硕士研究生拟录取公示页中的 35 个静态 PDF 附件解析入库，新增 7,305 条结构化记录；其中 6,502 条为考研/招生录取路径，803 条为推荐免试路径。另将南京医科大学官方“推荐免试研究生考生编号查询（含长学制）”PDF 入库 774 条，该源只含姓名、考生编号和注册学号，不含学院/专业，保留为 `needs_review=true` 的低字段记录。

华中师范大学、云南师范大学、新疆师范大学本轮均确认存在官网公示页，但附件下载进入验证码桥，自动化抓取未拿到人员级 PDF 明细，覆盖状态暂不变。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：180,255 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：180,255 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：185,965 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：185,965 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：434 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，251 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 22,314,898 字节

来源：

- 华南师范大学 2026 年硕士研究生拟录取名单公示页：https://yz.scnu.edu.cn/a/20260407/672.html
- 华南师范大学 PDF 直链来源：上述页面中的 `https://statics.scnu.edu.cn/pics/yz/2026/...pdf`
- 南京医科大学 2026 年推荐免试研究生考生编号查询页面：https://yjszs.njmu.edu.cn/2026/0512/c10193a301057/page.htm

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：212 个测试通过（仅保留既有 ResourceWarning）。
- 华南师范大学 batch132d：7,305 条清洗记录，缺少人员姓名 0，缺少考生编号 0，缺少专业字段 0，需人工复核 0；“是否拟录取=是”5,187 条，“否”2,118 条。
- 南京医科大学 batch131：774 条清洗记录，缺少人员姓名 0，缺少考生编号 0，缺少专业字段 774，需人工复核 774。
- 工作簿结构校验：Overview 15 行、Source_Summary 435 行、Coverage 431 行、Public_Records 185,966 行；公式单元格 0，公式错误 0。

## 2026-05-25 追加批次：batch133 西安邮电大学

本轮补入西安邮电大学 2026 年推荐免试研究生拟录取名单 PDF，新增 17 条人员级记录。该 PDF 只公开身份证后四位，不公开完整考生编号；清洗表将后四位写入 `student_id`，并在 `remarks` 标注“证件后四位”。

西南交通大学入口返回 502，沈阳师范大学列表未暴露人员级名单，南京邮电大学 2026 公示页本地返回“无效的文章参数”，这些学校本轮不并入。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：180,272 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：180,272 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：185,982 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：185,982 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：435 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，252 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

来源：

- 西安邮电大学 2026 年推荐免试研究生拟录取名单公示页：https://gr.xupt.edu.cn/info/1172/9158.htm
- 西安邮电大学 2026 年推荐免试研究生拟录取名单 PDF：https://gr.xupt.edu.cn/__local/2/8A/F1/8CA9DC8223FFBF435008FCC62BD_018718C2_140F9.pdf

验证：

- batch133c 清洗表：17 条清洗记录，缺少人员姓名 0，缺少证件后四位 0，缺少专业字段 0，需人工复核 0。

## 2026-05-25 追加批次：batch134 福建农林大学/中南民族大学/沈阳药科大学

本轮补入福建农林大学 2026 年接收推荐免试攻读研究生名单、福建农林大学 2025 年拟录取硕士研究生名单、中南民族大学 2026 年接收硕士推免生拟录取名单，以及沈阳药科大学 2025 年硕士复试结果及拟录取名单一志愿和调剂批次 PDF。新增 5,554 条人员级记录，全部 `needs_review=false`。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：185,826 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：185,826 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：191,536 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：191,536 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：439 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，255 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 23,055,097 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 福建农林大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 41 |
| 福建农林大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,515 |
| 中南民族大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 52 |
| 沈阳药科大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,946 |

来源：

- 福建农林大学 2026 年接收推荐免试攻读研究生名单公示页：https://yjsy.fafu.edu.cn/57/3e/c3604a415550/page.htm
- 福建农林大学 2026 年接收推荐免试攻读研究生名单 PDF：https://yjsy.fafu.edu.cn/_upload/article/files/5b/8d/b16c34814f80b5343a1123109efe/95e39fc0-b4f4-454c-864c-40d8e4bb87a3.pdf
- 福建农林大学 2025 年拟录取硕士研究生名单公示页：https://yjsy.fafu.edu.cn/3d/c3/c3604a409027/page.htm
- 福建农林大学 2025 年拟录取硕士研究生名单 PDF：https://yjsy.fafu.edu.cn/_upload/article/files/1e/41/8b9c8fa64b58a1f5594cb46dc953/e316667d-0ba1-4253-9f22-8620b0d22931.pdf
- 中南民族大学 2026 年接收硕士推免生拟录取名单公示页：https://www.scuec.edu.cn/yjsy/info/1007/3533.htm
- 中南民族大学 2026 年接收硕士推免生拟录取名单 PDF：https://www.scuec.edu.cn/__local/B/4C/6F/9073B321BC7503E71FCC086161B_346AEF18_20DE2.pdf
- 沈阳药科大学 2025 年硕士复试结果及拟录取名单 PDF：五个 `https://grs.syphu.edu.cn/__local/...pdf` 官方直链，见 `data/seeds/official_site_recommendation_websearch_web_20260525_batch134.csv`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：216 个测试通过（仅保留既有 ResourceWarning）。
- batch134c 清洗表：5,554 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 440 行、Coverage 431 行、Public_Records 191,537 行；公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch184 电子科技大学

本轮继续补 B 类官网人员级拟录取数据。电子科技大学校级硕士/博士拟录取公示页可访问，并展开得到 71 个学院/调剂链接；其中部分学院站点返回 HTTP 412 或站点挑战脚本，暂不硬抓。可复现下载的 6 个官方 PDF 附件已专项解析入库，新增 918 条人员级记录。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：210,531 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：210,531 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：216,241 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：216,241 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：497 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，301 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 26,375,249 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 电子科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 918 | 0 |

来源：

- 电子科技大学 2026 年硕士研究生拟录取名单公示：https://yz.uestc.edu.cn/info/1007/5774.htm
- 电子科技大学 2026 年博士研究生拟录取名单公示：https://yz.uestc.edu.cn/info/1004/5834.htm
- 可复现 PDF 附件来自信息与通信工程学院、经济与管理学院 MBA、公共管理学院 MPA 等学院页面，详见 `data/seeds/official_site_recommendation_websearch_web_20260527_batch184_uestc.csv`

验证：

- `python -m unittest tests.test_curate_batch184_uestc`：4 个测试通过。
- batch184 curated：918 条，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，明确非拟录取状态 0。
- B 主表全局非拟录取状态扫描：`是否拟录取: 否`、`放弃复试`、`拟不录取`、`不予录取`、`进入复试名单`、`复试不合格` 命中 0 条。
- 工作簿结构校验：Overview 15 行、Source_Summary 498 行、Coverage 431 行、Public_Records 216,242 行；公式单元格 0，公式错误 0。

## 2026-05-27 追加批次：batch181/batch183 南京邮电大学/中国地质大学（武汉）

本轮继续补 B 类官网人员级拟录取数据。新增南京邮电大学 2026 年博士研究生拟录取名单（第一批次）227 条；新增中国地质大学（武汉）多个学院 2026 年硕士研究生拟录取/复试成绩公示 1,010 条。南京理工大学硕士公示页已留证，但本地请求校级页返回 410，直链 PDF 返回“出错啦”HTML，本轮不合并。

同时做了一次 B 主表全局质量修正：删除早前混入的 2,301 条明确非拟录取记录，主要是华南师范大学表内 `是否拟录取: 否`，以及少量 `放弃复试`、`不予录取`、`复试不合格` 状态。修正记录保存在 `data/processed/graduate_outcomes_official_site_recommendation_master/non_admission_filter_20260527.txt`。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：209,613 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：209,613 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：215,323 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：215,323 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：496 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，300 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 26,253,200 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 南京邮电大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 227 | 0 |
| 中国地质大学（武汉） | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,010 | 0 |

来源：

- 南京邮电大学 2026 年博士研究生拟录取名单（第一批次）：http://yzb.njupt.edu.cn/2026/0430/c11142a301278/page.htm
- 南京邮电大学嵌入 PDF：http://yzb.njupt.edu.cn/_upload/article/files/0c/78/68d6839f485bba868e143392ce53/e542a67a-aa12-4aa3-a677-661a9f53feb7.pdf
- 中国地质大学（武汉）经济管理学院 2026 年硕士研究生复试成绩及拟录取名单：https://jgxy.cug.edu.cn/info/1137/17504.htm
- 中国地质大学（武汉）国家 GIS 工程技术研究中心 2026 年硕士研究生拟录取名单：https://gis.cug.edu.cn/info/1019/2638.htm
- 中国地质大学（武汉）材料与化学学院、环境学院、地信学院、地矿全重、地空学院、工程学院、地质调查研究院等学院官网页，见 `data/seeds/official_site_recommendation_websearch_web_20260527_batch183_cug.csv`

验证：

- `python -m unittest tests.test_curate_batch181_njupt tests.test_curate_batch183_cug`：9 个测试通过。
- 南京邮电大学 batch181 curated：227 条，缺少人员姓名 0，需人工复核 0。
- 中国地质大学（武汉） batch183 curated：1,010 条，缺少人员姓名 0，需人工复核 0；剔除 20 条非拟录取状态，折叠 78 条同源互补重复。
- B 主表全局非拟录取状态扫描：`是否拟录取: 否`、`放弃复试`、`拟不录取`、`不予录取`、`进入复试名单`、`复试不合格` 命中 0 条。
- 工作簿结构校验：Overview 15 行、Source_Summary 497 行、Coverage 431 行、Public_Records 215,324 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch227 天津科技大学

本轮继续补 B 类官网人员级拟录取数据。天津科技大学研究生院信息公开页可访问，但需要保存站点 cookie 才能进入正文；通用爬虫记录了 302 失败日志，随后从官方正文 iframe 下载 5 个 PDF，专项解析一志愿、调剂和接收推免拟录取名单，新增 2,090 条人员级记录。

山东理工大学与青岛理工大学已保留官方页面抓取证据，但山东理工关键“附件1.pdf”未在页面 HTML 中暴露真实 href，青岛理工当前公示正文无名单附件链接，本轮不做猜测下载、不并入记录。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：235,763 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：235,763 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：241,473 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：241,473 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：542 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，342 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 29,604,163 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 天津科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,062 | 0 |
| 天津科技大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 28 | 0 |

来源：

- 天津科技大学 2026 年硕士研究生一志愿拟录取考生名单公示（第一批）：https://yjs.tust.edu.cn/zsgz/tzggzs/817ec904ff9640869b7b4c9efaa58fe6.htm
- 天津科技大学 2026 年硕士研究生一志愿拟录取考生名单公示（第二批）：https://yjs.tust.edu.cn/zsgz/tzggzs/ddb0f6e59614476d8acc495351f15b53.htm
- 天津科技大学 2026 年硕士研究生调剂拟录取考生名单公示（第一批）：https://yjs.tust.edu.cn/zsgz/tzggzs/9fa250a69a9f4867a7e37b0042c4742b.htm
- 天津科技大学 2026 年硕士研究生调剂拟录取考生名单公示（第二批）：https://yjs.tust.edu.cn/zsgz/tzggzs/5572f8f278f3412ebbf0ded60cdb83ad.htm
- 天津科技大学接收 2026 届优秀应届本科毕业生免试攻读硕士学位研究生拟录取名单公示：https://yjs.tust.edu.cn/zsgz/tzggzs/a9a5f560dda246a8a0b60245f6111800.htm

验证：

- `python -m unittest tests.test_curate_batch227_tust`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：73 个测试通过。
- batch227 curated：2,090 条，缺少人员姓名 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 543 行、Coverage 431 行、Public_Records 241,474 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch228 哈尔滨师范大学

本轮继续补 B 类官网人员级拟录取数据。哈尔滨师范大学研究生学院 2026 年硕士研究生招生一志愿拟录取名单公示页可访问，官方 PDF 附件可直接下载。PDF 含斜向水印，通用解析无法结构化；新增专项解析按考生编号定位真实表格行，新增 1,665 条人员级记录。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：237,428 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：237,428 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：243,138 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：243,138 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：543 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，343 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 29,803,940 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 哈尔滨师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,665 | 0 |

来源：

- 哈尔滨师范大学 2026 年硕士研究生招生一志愿拟录取名单公示：http://yjsxy.hrbnu.edu.cn/info/1045/26630.htm
- 官方 PDF 附件：http://yjsxy.hrbnu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1255513605&wbfileid=D94C4D5DD4B897AB9BB988B9EB8141C1

验证：

- `python -m unittest tests.test_curate_batch228_hrbnu`：1 个测试通过。
- batch228 curated：1,665 条，缺少人员姓名 0，缺少考生编号 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 544 行、Coverage 431 行、Public_Records 243,139 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch231 山西师范大学、batch232 陕西中医药大学

本轮继续补 B 类官网人员级拟录取数据。新增山西师范大学 2026 年普通招考博士拟录取名单 82 条、陕西中医药大学 2026 年硕士一志愿拟录取名单 769 条，均来自学校官网可直接复现下载的 PDF。已将通用解析结果替换为专项解析结果：山西师范大学剔除 PDF 表头误识别行并补入学科代码/名称、成绩备注；陕西中医药大学补入准考证号、表内序号和成绩备注，并将 `▲/*/**/***` 政策标记转入备注。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：238,279 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：238,279 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：243,989 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：243,989 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：545 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，345 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 29,906,632 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山西师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 82 | 0 |
| 陕西中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 769 | 0 |

来源：

- 山西师范大学 2026 年招收以普通招考方式攻读博士学位研究生拟录取名单公示：https://grc.sxnu.edu.cn/info/1077/10914.htm
- 山西师范大学官方 PDF：https://grc.sxnu.edu.cn/__local/9/76/BC/DE6CBD556A901D06BAEC8EA2DAD_7E02CD11_13685.pdf
- 陕西中医药大学 2026 年硕士研究生拟录取考生名单公示（一志愿）：http://yzb.sntcm.edu.cn/xwdt/125213.htm
- 陕西中医药大学官方 PDF：http://img.sntcm.edu.cn/HIWCMyzb/202604/202604040418058.pdf

验证：

- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm`：2 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：76 个测试通过。
- batch231/batch232 curated：合计 851 条，缺少人员姓名 0，缺少考生编号 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 546 行、Coverage 431 行、Public_Records 243,990 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch233 兰州理工大学

本轮继续补 B 类官网人员级拟录取数据。新增兰州理工大学 2026 年硕士研究生一志愿拟录取和二次调剂拟录取记录 12 条，来源为微电子现代产业学院、机电工程学院官网公告中可直接复现下载的内嵌 PDF。通用解析可抽取微电子现代产业学院 11 条，但机电工程学院 PDF 的备注列跨行导致单行记录被跳过；已按 TDD 新增专项解析，补齐学院、录取专业、序号、成绩和专项计划备注。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：238,291 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：238,291 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：244,001 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：244,001 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：546 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，346 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 29,908,687 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 兰州理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 12 | 0 |

来源：

- 兰州理工大学微电子现代产业学院 2026 年硕士研究生招生复试一志愿拟录取结果公示：https://weidianzi.lut.edu.cn/info/1019/1934.htm
- 微电子现代产业学院官方 PDF：https://weidianzi.lut.edu.cn/__local/6/43/26/A4180401571DB8887F1DE1E3243_60345B89_AD3E.pdf
- 兰州理工大学机电工程学院 2026 年硕士研究生招生复试（二次调剂）拟录取结果公示：https://jidian.lut.edu.cn/info/1870/18350.htm
- 机电工程学院官方 PDF：https://jidian.lut.edu.cn/__local/0/7B/F1/83EF0F22F94E82FE64142ED0575_B962DAF0_1D137.pdf

验证：

- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs`：3 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：77 个测试通过。
- batch233 curated：12 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 547 行、Coverage 431 行、Public_Records 244,002 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch234 中国音乐学院

本轮继续补 B 类官网人员级拟录取数据。新增中国音乐学院 2026 年面向港澳台地区研究生招生考试拟录取名单 2 条，来源为研究生院官网页面中内嵌的站内 PDF。同期复核的“全国硕士研究生招生拟录取考生提交体检报告”页面和 PDF 只包含体检报告提交流程，不含名单，留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：238,293 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：238,293 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：244,003 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：244,003 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：547 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，347 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 29,909,256 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中国音乐学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2 | 0 |

来源：

- 中国音乐学院 2026 年面向港澳台地区研究生招生考试拟录取名单公示：https://yjsy.ccmusic.edu.cn/zsgz/ssyjszs/aadc4ffd447541e8a4850b8a7aaadf3a.htm
- 官方 PDF：https://yjsy.ccmusic.edu.cn/docs/2026-05/eac5066c44af43d596ea79dbb6833684.pdf
- 中国音乐学院 2026 年全国硕士研究生招生拟录取考生提交体检报告的通知（留证，未入库）：https://yjsy.ccmusic.edu.cn/zsgz/ssyjszs/9c0334d6898e408e8874f0372adc1b3c.htm

验证：

- `python -m unittest tests.test_curate_batch234_ccmusic`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic`：4 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：78 个测试通过。
- batch234 curated：2 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0，页面误抽 `研究生院/受理时段` 残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 548 行、Coverage 431 行、Public_Records 244,004 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch235 香港中文大学（深圳）

本轮继续补 B 类官网人员级推免/拟录取数据。新增香港中文大学（深圳）数据科学学院 2025 年拟录取推荐免试硕士研究生名单 9 条，以及 2026 年秋季入学直硕拟录取名单 29 条。前者来自官网正文 HTML 表格，后者来自官网 XLSX 附件；同期复核的医学院候选页当前返回未授权访问，不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：238,331 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：238,331 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：244,041 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：244,041 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：549 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，348 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 29,914,616 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 香港中文大学（深圳） | 2025 | recommendation_exemption_list | recommendation_exemption | 9 | 0 |
| 香港中文大学（深圳） | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 29 | 0 |

来源：

- 香港中文大学（深圳）数据科学学院 2025 年拟录取推荐免试硕士研究生名单公示：https://sds.cuhk.edu.cn/article/2036
- 香港中文大学（深圳）数据科学学院直硕拟录取名单公示：https://sds.cuhk.edu.cn/article/2309
- 2026 年秋季入学直硕拟录取名单 XLSX：https://sds.cuhk.edu.cn/sites/default/files/2025-11/%E9%A6%99%E6%B8%AF%E4%B8%AD%E6%96%87%E5%A4%A7%E5%AD%A6%EF%BC%88%E6%B7%B1%E5%9C%B3%EF%BC%89%E6%95%B0%E6%8D%AE%E7%A7%91%E5%AD%A6%E5%AD%A6%E9%99%A2%E7%9B%B4%E7%A1%95%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95%EF%BC%882026%E5%B9%B4%E7%A7%8B%E5%AD%A3%E5%85%A5%E5%AD%A6%EF%BC%89.xlsx
- 医学院候选页（未授权访问，未入库）：https://medpg.cuhk.edu.cn/article/103

验证：

- `python -m unittest tests.test_curate_batch235_cuhk_sz`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz`：5 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：79 个测试通过。
- batch235 curated：38 条，缺少人员姓名 0，缺少录取专业 0，缺少学院 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 550 行、Coverage 431 行、Public_Records 244,042 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch236 中国人民大学

本轮继续补 B 类官网人员级拟录取数据。新增中国人民大学研究生院 2018 年硕士研究生全国统考拟录取名单第一批、第二批共 2,804 条。两个来源均为官网 HTML 表格；专项清洗剔除了通用解析误抽的 1 条表头，并将第一批页面从误判的推免类型更正为硕士统考拟录取类型。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：241,135 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：241,135 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：246,845 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：246,845 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：550 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，349 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 30,258,298 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中国人民大学 | 2018 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,804 | 0 |

来源：

- 中国人民大学 2018 年硕士研究生全国统考拟录取名单公示（第一批）：https://grs.ruc.edu.cn/info/1083/1273.htm
- 中国人民大学 2018 年硕士研究生全国统考拟录取名单公示（第二批）：https://grs.ruc.edu.cn/info/1083/1348.htm

验证：

- `python -m unittest tests.test_curate_batch236_ruc_2018_admission`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz tests.test_curate_batch236_ruc_2018_admission`：6 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：80 个测试通过。
- batch236 curated：2,804 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0，表头残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 551 行、Coverage 431 行、Public_Records 246,846 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch237 中国民航大学

本轮继续补 B 类官网人员级拟录取和推免接收数据。新增中国民航大学 2025 年硕士研究生拟录取名单 1,422 条，以及 2025 年接收推免生拟录取名单 17 条。来源为研究生院官网页面附件 PDF；专项清洗补齐了通用解析遗漏的录取专业字段，并保留成绩、学习形式、录取类别和专项计划备注。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：242,574 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：242,574 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：248,284 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：248,284 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：552 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，350 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 30,432,779 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中国民航大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,422 | 0 |
| 中国民航大学 | 2025 | incoming_recommendation_admission_list | recommendation_exemption | 17 | 0 |

来源：

- 中国民航大学 2025 年硕士研究生拟录取名单公示：https://www.cauc.edu.cn/yjsy/info/1124/2230.htm
- 2025 年拟录取名单公示 PDF：https://www.cauc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1787525762&wbfileid=11984439
- 中国民航大学 2025 年接收推荐免试攻读硕士研究生拟录取名单公示：https://www.cauc.edu.cn/yjsy/info/1124/2087.htm
- 2025 年接收推免生拟录取名单 PDF：https://www.cauc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1787525762&wbfileid=11977509

验证：

- `python -m unittest tests.test_curate_batch237_cauc`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz tests.test_curate_batch236_ruc_2018_admission tests.test_curate_batch237_cauc`：7 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：81 个测试通过。
- batch237 curated：1,439 条，缺少人员姓名 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 553 行、Coverage 431 行、Public_Records 248,285 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch238 成都理工大学

本轮继续补 B 类官网推免拟录取数据。新增成都理工大学 2025 年推荐免试研究生拟录取名单 6 条，来源为同校计算机与网络安全学院官网静态 PDF。研究生院主公告页实时返回 HTTP 412，已留证；PDF 直链可直接下载。专项清洗剔除了通用解析混入的 `研究生/支教团` 碎片姓名，并把跨行学院名拼回为 `计算机与网络安全学院（示范性软件学院）`。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：242,580 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：242,580 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：248,290 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：248,290 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：553 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，351 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 30,433,791 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 成都理工大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 6 | 0 |

来源：

- 成都理工大学 2025 年推荐免试研究生（含直博生）拟录取名单公示（返回 412，留证）：https://gra.cdut.edu.cn/info/1007/3934.htm
- 计算机与网络安全学院官方 PDF：https://cist.cdut.edu.cn/__local/1/3C/A8/76104FAC3A34A88B53467FDBB02_B5BB8255_2AFE1.pdf

验证：

- `python -m unittest tests.test_curate_batch238_cdut_recommendation`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz tests.test_curate_batch236_ruc_2018_admission tests.test_curate_batch237_cauc tests.test_curate_batch238_cdut_recommendation`：8 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：82 个测试通过。
- batch238 curated：6 条，缺少人员姓名 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0，`研究生/支教团` 碎片姓名残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 554 行、Coverage 431 行、Public_Records 248,291 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch239 武汉轻工大学

本轮继续补 B 类官网人员级拟录取数据。新增武汉轻工大学 2025 年硕士研究生拟录取名单 1,293 条，来源为信息公开网官方 PDF 直链。专项清洗按 PDF 表格行保留初试总分、复试总分、综合成绩、学习形式和专项计划备注。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：243,873 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：243,873 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：249,583 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：249,583 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：554 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，352 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 30,605,751 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 武汉轻工大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,293 | 0 |

来源：

- 武汉轻工大学 2025 年硕士研究生拟录取名单 PDF：https://xxgkw.whpu.edu.cn/__local/0/12/BB/9B2441AF41EA488AA5E18F18FF3_3E926D35_5B255.pdf

验证：

- `python -m unittest tests.test_curate_batch239_whpu_admission`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz tests.test_curate_batch236_ruc_2018_admission tests.test_curate_batch237_cauc tests.test_curate_batch238_cdut_recommendation tests.test_curate_batch239_whpu_admission`：9 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：83 个测试通过。
- batch239 curated：1,293 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 555 行、Coverage 431 行、Public_Records 249,584 行；公式单元格 0，公式错误 0。

## 2026-05-28 追加批次：batch240 西南石油大学

本轮继续补 B 类官网人员级拟录取数据。新增西南石油大学 2025 年硕士研究生学院级拟录取名单 25 条，来源为石油与天然气工程学院递补拟录取 PDF、土木工程与测绘学院调剂第一批拟录取 PDF 两份官网静态附件。专项清洗修复了通用解析的姓名/专业/考生编号错位。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：243,898 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：243,898 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：249,608 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：249,608 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：555 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，353 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，大小 30,609,241 字节

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南石油大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 25 | 0 |

来源：

- 石油与天然气工程学院 2025 年硕士研究生递补拟录取名单 PDF：https://www.swpu.edu.cn/__local/8/15/C7/92E70E0AC85E6ADA3E0D0EB5EEC_5CAC0528_2642D.pdf
- 土木工程与测绘学院 2025 年硕士研究生调剂第一批拟录取名单 PDF：https://www.swpu.edu.cn/__local/2/3D/18/462CA89B77DEAFBE7381FAAFCB4_3FD01EB0_FB65.pdf

验证：

- `python -m unittest tests.test_curate_batch240_swpu_admission_pdfs`：1 个测试通过。
- `python -m unittest tests.test_curate_batch236_ruc_2018_admission tests.test_curate_batch237_cauc tests.test_curate_batch238_cdut_recommendation tests.test_curate_batch239_whpu_admission tests.test_curate_batch240_swpu_admission_pdfs`：5 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：84 个测试通过。
- batch240 curated：25 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 556 行、Coverage 431 行、Public_Records 249,609 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch245 上海理工大学

本轮继续补 B 类官网人员级拟录取数据。新增上海理工大学理学院 2026 年硕士研究生一志愿复试录取结果 33 条，来源为理学院官网静态 PDF。专项清洗按 PDF 文本层补齐学院、专业、初试成绩、复试成绩、总成绩和退役大学生士兵专项计划备注。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：245,975 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：245,975 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,685 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,685 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：560 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，358 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 33 | 0 |

来源：

- 上海理工大学理学院 2026 年硕士研究生一志愿复试录取结果公示 PDF：https://lxy.usst.edu.cn/_upload/article/files/88/d2/23dc2812494e8d088def5148c24d/7193cd58-d41f-42a9-902d-041d09138d7a.pdf

验证：

- `python -m unittest tests.test_curate_batch245_usst_lxy_admission`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：89 个测试通过。
- batch245 curated：33 条，缺少人员姓名 0，缺少考生编号 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 561 行、Coverage 431 行、Public_Records 251,686 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch246 聊城大学

本轮继续补 B 类官网人员级推免拟录取数据。新增聊城大学 2025 年推荐免试硕士研究生拟录取名单 163 条，来源为研究生招生网官方 PDF 直链。专项清洗按 PDF 文本层剔除 7 条分页表头误识别记录，保留学院、专业代码、专业名称、复试成绩和专项计划备注。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：246,138 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：246,138 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,848 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,848 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：561 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，359 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 聊城大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 163 | 0 |

来源：

- 聊城大学 2025 年推荐免试硕士研究生拟录取名单 PDF：https://yz.lcu.edu.cn/docs/20241018150049513144.pdf

验证：

- `python -m unittest tests.test_curate_batch246_lcu_recommendation`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：90 个测试通过。
- batch246 curated：163 条，缺少人员姓名 0，分页表头姓名 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0；名单原文不含考生编号，163 条均保留 `missing_student_id` 质量标记。
- 工作簿结构校验：Overview 15 行、Source_Summary 562 行、Coverage 431 行、Public_Records 251,849 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch247 江苏师范大学

本轮继续补 B 类官网人员级推免拟录取数据。新增江苏师范大学 2026 年推荐免试硕士研究生拟录取名单 113 条，来源为研究生院官网公示页内嵌 PDF 直链。专项清洗按 PDF 文本层补齐脱敏身份证号、拟录取学院、专业代码、专业名称、学习形式和推免类型。同期复核山东理工大学官网公示页，名单附件没有可请求链接，本轮不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：246,251 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：246,251 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,961 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,961 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：562 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，360 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 江苏师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 113 | 0 |

来源：

- 江苏师范大学 2026 年推荐免试硕士研究生拟录取名单公示：http://yjsy.jsnu.edu.cn/2e/d9/c10944a405209/page.htm
- 官方 PDF 附件：http://yjsy.jsnu.edu.cn/_upload/article/files/ca/08/ec9ecd2d4c2daa9bb3a54722897c/0baf68fa-b026-4a15-a7e3-2b00b68a4728.pdf

验证：

- `python -m unittest tests.test_curate_batch247_jsnu_recommendation`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：91 个测试通过。
- batch247 curated：113 条，缺少人员姓名 0，缺少脱敏身份证号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 563 行、Coverage 431 行、Public_Records 251,962 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch248 重庆交通大学

本轮继续补 B 类官网人员级硕士拟录取数据。新增重庆交通大学 2025 年硕士招生成绩及拟录取结果公示（一志愿）1,813 条，来源为研究生招生信息网官方静态 PDF。专项清洗按准考证号定位人员行，保留学院、专业代码、专业名称、初试总分、复试笔试、复试面试、复试政治和综合成绩；同时剔除 `不合格` 109 条和 `名额受限` 131 条。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：248,064 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：248,064 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：253,774 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：253,774 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：563 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，361 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 重庆交通大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,813 | 0 |

来源：

- 重庆交通大学 2025 年硕士招生成绩及拟录取结果公示（一志愿）PDF：https://yjszs.cqjtu.edu.cn/__local/E/EB/D8/88DAF14D0F7C9C26C90E97E6BF5_FE0B182C_A1952.pdf

验证：

- `python -m unittest tests.test_curate_batch248_cqjtu_admission`：1 个测试通过。
- batch248 curated：1,813 条，缺少人员姓名 0，缺少准考证号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 564 行、Coverage 431 行、Public_Records 253,775 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch249-batch253 暨南大学、山东农业大学、西安外国语大学、皖南医学院

本轮新增 4 个可入库官网源，共 3,420 条人员级记录：暨南大学 2026 年拟录取博士研究生名单 228 条、山东农业大学 2025 年硕士拟录取名单 2,266 条、西安外国语大学 2026 年调剂拟录取名单 158 条、皖南医学院 2025 年硕士拟录取名单 768 条。浙江中医药大学附件请求返回 HTTP 412，大连外国语大学、桂林医科大学、太原科技大学附件进入验证码下载桥，均未入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：251,484 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：251,484 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：257,194 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：257,194 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：567 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，365 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 暨南大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 228 | 0 |
| 山东农业大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,266 | 0 |
| 西安外国语大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 158 | 0 |
| 皖南医学院 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 768 | 0 |

来源：

- 暨南大学 2026 年第二批次拟录取博士研究生名单 Excel：https://yz.jnu.edu.cn/_upload/article/files/99/b1/1fb265f14ab3a02802f00c1b0d79/c7235e9d-63f1-4efc-8781-7d1090e91a28.xlsx
- 山东农业大学 2025 年硕士研究生拟录取名单 PDF：https://yjsc.sdau.edu.cn/cms/viewPdf/f7887010dce34b0a9fc8589e584200ed
- 西安外国语大学 2026 年硕士研究生招生考试调剂考生拟录取名单公示：https://yzw.xisu.edu.cn/info/1080/4622.htm
- 皖南医学院 2025 年硕士研究生招生拟录取名单 PDF：https://www.wnmc.edu.cn/__local/A/C6/DA/A19EA1BD793B172B18AD6C3E700_229104C8_44124.pdf

验证：

- `python -m unittest tests.test_curate_batch249_jnu_doctor_admission tests.test_curate_batch250_sdau_admission tests.test_curate_batch251_xisu_adjustment_admission tests.test_curate_batch253_wnmc_admission`：4 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：96 个测试通过。
- 本轮 4 个 curated 文件合计：3,420 条，缺少人员姓名 0，缺少考生编号 0，需人工复核 0，明确排除状态残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 568 行、Coverage 431 行、Public_Records 257,195 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch254 齐齐哈尔大学

本轮新增齐齐哈尔大学 2025 年硕士研究生拟录取考生名单 1,190 条，来源为研究生部官网公示页和官方静态 PDF。通用解析曾抽到 1,192 条候选，其中尾部 1191、1192 两条为“放弃一志愿录取资格”；专项清洗只保留拟录取记录，并将这两条明确非录取状态排除。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,674 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,674 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,384 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,384 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：568 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，366 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 齐齐哈尔大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,190 | 0 |

来源：

- 齐齐哈尔大学 2025 年硕士研究生拟录取考生名单公示页：https://yjs.qqhru.edu.cn/info/1065/1813.htm
- 齐齐哈尔大学 2025 年硕士研究生拟录取考生名单 PDF：https://yjs.qqhru.edu.cn/__local/8/F5/EE/02D0C56D2494576D6694F9C54A6_C1B2A0DC_FAA2C.pdf

验证：

- `python -m unittest tests.test_curate_batch254_qqhru_admission`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：97 个测试通过。
- batch254 curated：1,190 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少专业 0，需人工复核 0，明确排除状态残留 0，排名 1191/1192 残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 569 行、Coverage 431 行、Public_Records 258,385 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch255 喀什大学

本轮新增喀什大学 2026 年拟接收推荐免试攻读全日制硕士研究生拟录取名单 60 条。来源为研究生处官网公示页和页面嵌入的官方 PDF；PDF 为图片型，无可抽取文本层，因此采用 300dpi 渲染加 OCR 坐标分栏，并对 OCR 明确漏读的少量姓名做限定修正。证件号码按原图公开形式保留为中间星号遮蔽格式。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,734 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,734 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,444 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,444 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：569 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，367 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 喀什大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 60 | 0 |

来源：

- 喀什大学 2026 年拟接收优秀应届本科毕业生免试攻读全日制硕士研究生名单公示页：https://yjsc.ksu.edu.cn/info/1034/2832.htm
- 喀什大学名单嵌入 PDF：https://yjsc.ksu.edu.cn/virtual_attach_file.vsb?afc=tU8nj2UlLDnRU8nwzf7ozl4Uz94LR9XZMRf2MRNZnzCDMRL0gihFp2hmCIa0LYyaLYh7MkhVMNM7MzQVLN7bnRfVUlMkM87snRr2U4-4UzQFMNnRMl-iUzVFM7LZLNlJv2nto4OeosT/vDL0qIbtpYyPLRL8g4-ZL4-Jqd/nx&oid=1120997853&tid=1034&nid=2832&e=.pdf

验证：

- `python -m unittest tests.test_curate_batch255_ksu_recommendation`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：98 个测试通过。
- batch255 curated：60 条，缺少人员姓名 0，缺少证件号 0，缺少学院 0，缺少专业 0，需人工复核 0，明确排除状态残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 570 行、Coverage 431 行、Public_Records 258,445 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch256 河南医药大学

本轮新增河南医药大学 2026 年推荐免试攻读硕士研究生拟录取名单 4 条。来源为研究生处官网 HTML 表格，字段包含院系所代码、院系所名称、姓名、证件号码、专业代码、专业名称和学位类型；专项清洗补齐通用解析遗漏的证件号和学院字段。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,738 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,738 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,448 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,448 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：570 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，368 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河南医药大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 4 | 0 |

来源：

- 河南医药大学 2026 年推荐免试攻读硕士研究生拟录取名单公示：https://www.xxmu.edu.cn/yjsc/info/1013/4466.htm

验证：

- `python -m unittest tests.test_curate_batch256_hnmu_recommendation`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：99 个测试通过。
- batch256 curated：4 条，缺少人员姓名 0，缺少证件号 0，缺少学院 0，缺少专业 0，需人工复核 0，明确排除状态残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 571 行、Coverage 431 行、Public_Records 258,449 行；公式单元格 0，公式错误 0。

## 2026-06-01 追加批次：batch257 河北农业大学

本轮新增河北农业大学 2026 级硕博连读研究生拟录取名单 42 条。来源为研究生学院官网公示页和页面嵌入的官方 PDF；PDF 有可抽取文本层，但通用解析只得到 1 条无效记录，因此专项清洗重建表格字段，保留学号、姓名、拟录取学院、拟录取专业、导师、考核成绩和拟录取类别。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,710 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,710 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,780 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,780 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,490 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,490 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：571 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，369 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河北农业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 42 | 0 |

来源：

- 河北农业大学 2026 级硕博连读研究生拟录取名单公示：https://yanjiusheng.hebau.edu.cn/info/1109/4694.htm
- 河北农业大学名单嵌入 PDF：https://yanjiusheng.hebau.edu.cn/__local/B/8A/32/0EF1F4B72A57F5B93FA41D72EF8_926A5724_1C059.pdf

验证：

- `python -m unittest tests.test_curate_batch257_hebau_doctor_admission`：1 个测试通过。
- batch257 curated：42 条，缺少人员姓名 0，缺少学号 0，缺少学院 0，缺少专业 0，需人工复核 0，明确排除状态残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 572 行、Coverage 431 行、Public_Records 258,491 行；公式单元格 0，公式错误 0。

## 2026-06-02 追加批次：batch408 东北师范大学

本轮新增东北师范大学 2025 年硕士研究生拟录取名单 548 条。来源为东北师范大学文学院、生命科学学院、教育学部、化学学院官网公示页及同站附件；记录为考生编号级拟录取数据。北京服装学院、天津财经大学、中国药科大学、中国政法大学、东北师范大学主站等候选官网源因实时 404/410、跳转 404、JavaScript 动态挑战或栏目未暴露名单入口，仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：268,539 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：268,539 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：274,244 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：274,244 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：598 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，394 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 东北师范大学 | 2025 | master_admission_list | postgraduate_exam_or_admission | 548 | 0 |

来源：

- 东北师范大学文学院 2025 年硕士研究生拟录取名单：https://chinese.nenu.edu.cn/info/1111/10401.htm
- 东北师范大学生命科学学院 2025 年全日制硕士研究生拟录取名单：https://sky.nenu.edu.cn/info/1029/3693.htm
- 东北师范大学教育学部 2025 年硕士研究生拟录取名单：https://edu.nenu.edu.cn/info/1085/8717.htm
- 东北师范大学化学学院 2025 年硕士研究生拟录取名单：https://chem.nenu.edu.cn/info/1042/5323.htm

验证：

- batch408 clean/public：548 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格等状态残留。
- 工作簿已重建：Public_Records 274,244 条、Source_Summary 598 条、Coverage 430 条。

## 2026-06-02 追加批次：batch410 福建师范大学

本轮新增福建师范大学生命科学学院 2024 年硕士研究生招生复试结果 148 条。来源为学院官网公示页及同站 PDF 附件；原表含“拟录取意见”列，专项清洗仅保留 `建议录取`，排除空状态、`不予录取` 和 `放弃复试`。福建师范大学马克思主义学院 2025 年 PDF 直链实时返回 0 字节空响应，仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：268,687 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：268,687 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：274,392 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：274,392 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：599 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，395 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 福建师范大学 | 2024 | master_admission_list | postgraduate_exam_or_admission | 148 | 0 |

来源：

- 福建师范大学生命科学学院 2024 年硕士研究生招生复试结果公布（一志愿）：https://life.fjnu.edu.cn/e2/f9/c4509a385785/page.htm
- 官方 PDF 附件：https://life.fjnu.edu.cn/_upload/article/files/1c/75/429798164f80a01743a8f27b70c0/d450bf92-3d86-426c-b470-9d177b6666f9.pdf

验证：

- `python -m unittest tests.test_curate_batch410_fjnu_life_2024_result`：3 个测试通过。
- batch410 curated/public：148 条，均含 `official_admission_status: 建议录取`，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格等状态残留。
- 工作簿已重建：Public_Records 274,392 条、Source_Summary 599 条、Coverage 430 条。

## 2026-06-02 追加批次：batch420 佛山大学

本轮新增佛山大学 2025 年硕士研究生拟录取名单 1,012 条。来源为佛山大学研究生院官网 PDF 直链；第三方页面仅用于恢复官方附件 URL，入库数据只来自 `www.fosu.edu.cn` 官方 PDF。同期复核大连外国语大学、东北电力大学、大连海洋大学、沈阳体育学院、沈阳师范大学、北京协和医学院、南京财经大学、成都体育学院、云南民族大学、中国海洋大学、广东药科大学、西北师范大学等候选源，因实时 404/412/502/521、WAF/验证码、附件过公示期无 href 等原因仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：269,699 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：269,699 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：275,404 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：275,404 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：600 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，396 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 佛山大学 | 2025 | master_admission_list | postgraduate_exam_or_admission | 1,012 | 0 |

来源：

- 佛山大学 2025 年硕士研究生拟录取名单官方 PDF：https://www.fosu.edu.cn/yanjiusheng/wp-content/uploads/sites/105/2025/05/%E4%BD%9B%E5%B1%B1%E5%A4%A7%E5%AD%A62025%E5%B9%B4%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95.pdf

验证：

- batch420 clean/public：1,012 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格等状态残留。
- 工作簿已重建：Public_Records 275,404 条、Source_Summary 600 条、Coverage 430 条。

## 2026-06-02 追加批次：batch423 沈阳化工大学

本轮新增沈阳化工大学 2024 年硕士研究生一志愿拟录取结果 620 条。来源为沈阳化工大学研究生院官网详情页及其公开 PDF 附件；主名单 PDF 通用爬虫抽取 615 条，退役大学生士兵计划 PDF 按 TDD 新增专项解析补入 5 条，只保留附件名单中 `拟录取状态 == 拟录取` 的记录。齐鲁工业大学页面“公示已结束”且无 href，山西中医药大学附件入口要求验证码，均仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：270,319 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：270,319 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：276,024 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：276,024 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：602 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，397 所已精确匹配官网记录，33 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 沈阳化工大学 | 2024 | master_admission_list | postgraduate_exam_or_admission | 620 | 0 |

来源：

- 沈阳化工大学 2024 年硕士研究生招生考试一志愿拟录取结果（不含大学生士兵专项）：https://grs.syuct.edu.cn/content.html?id=630124648704513475&divcol=202404
- 官方 PDF 附件：https://zbhk-new.lnyun.com.cn/www/hgdxyjsy/pdf/202404/630124584615547872.pdf
- 沈阳化工大学 2024 年硕士研究生招生“退役大学生士兵计划”一志愿考生拟录取结果公示：https://grs.syuct.edu.cn/content.html?id=630116855725429338&divcol=202404
- 官方 PDF 附件：https://zbhk-new.lnyun.com.cn/www/hgdxyjsy/pdf/202404/630116749978637260.pdf

验证：

- `python -m unittest tests.test_curate_batch423_syuct_2024_soldier`：3 个测试通过。
- batch423 合计 620 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建：Public_Records 276,024 条、Source_Summary 602 条、Coverage 430 条。

## 2026-06-02 追加批次：batch439 大连外国语大学

本轮新增大连外国语大学 2020 年硕士研究生招生一志愿考生拟录取名单（普通计划）371 条。来源为大连外国语大学研究生处官网 PDF 直链；同期复核首都师范大学、中国政法大学、北京电影学院、中国药科大学、北京服装学院、东北电力大学、南京理工大学、甘肃中医药大学、广东药科大学、郑州轻工业大学、沈阳体育学院、大连海洋大学等候选源，因实时 404/410/412、跳转首页或 404 页、动态挑战页、附件过公示期无 href 等原因仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：270,690 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：270,690 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：276,395 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：276,395 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：603 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，398 所已精确匹配官网记录，32 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 大连外国语大学 | 2020 | postgraduate_admission_list | postgraduate_exam_or_admission | 371 | 0 |

来源：

- 大连外国语大学 2020 年硕士研究生招生一志愿考生拟录取名单（普通计划）官方 PDF：https://gd.dlufl.edu.cn/__local/8/66/30/88772C2D11625E2FEC4182315DF_0427F83B_74F11.pdf?e=.pdf

验证：

- batch439 clean/public：371 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建：Public_Records 276,395 条、Source_Summary 603 条、Coverage 430 条。

## 2026-06-02 追加批次：batch446 北京协和医学院

本轮新增北京协和医学院 2019 年博士（申请审核及硕转博）拟录取名单 658 条。来源为北京协和医学院研究生招生办公室官网 `__local` PDF 直链；同期复核东北电力大学、大连海洋大学、中国药科大学、西北师范大学、西藏农牧大学、广东药科大学、云南民族大学、山东理工大学、天津财经大学、浙江中医药大学、桂林医科大学、北京服装学院、中国政法大学、中国医科大学等候选源，因实时 404/410/405/412/521、统一身份认证、验证码下载桥、动态挑战页、SSL legacy renegotiation、附件不暴露或 HTML 下载桥等原因仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,348 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,348 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,053 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,053 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：604 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，399 所已精确匹配官网记录，31 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 北京协和医学院 | 2019 | postgraduate_admission_list | postgraduate_exam_or_admission | 658 | 0 |

来源：

- 北京协和医学院 2019 年博士（申请审核及硕转博）拟录取名单官方 PDF：https://graduate.pumc.edu.cn/__local/7/7F/91/4FC58AE8E036660A73097550DD0_7453A99D_A9C96.pdf?e=.pdf

验证：

- batch446 clean/public：658 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建：Public_Records 277,053 条、Source_Summary 604 条、Coverage 430 条。

## 2026-06-02 追加批次：batch451 南京理工大学

本轮新增南京理工大学 2024 年公开招考博士研究生拟录取名单（四）3 条。来源为南京理工大学研究生院官网 HTML 表格；同期复核成都体育学院、华东师范大学、重庆邮电大学、沈阳体育学院、山东理工大学等候选源，因实时 WAF HTML、加密且无人员文本层 PDF、HTTP 412/404、附件文字无 href 等原因仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,351 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,351 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,056 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,056 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：605 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，400 所已精确匹配官网记录，30 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 南京理工大学 | 2024 | postgraduate_admission_list | postgraduate_exam_or_admission | 3 | 0 |

来源：

- 南京理工大学 2024 年公开招考博士研究生拟录取名单（四）：https://gs.njust.edu.cn/18/9f/c14687a333983/page.htm

验证：

- `python -m unittest tests.test_curate_batch451_njust_2024_doctor_html`：2 个测试通过。
- batch451 curated/public：3 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建：Public_Records 277,056 条、Source_Summary 605 条、Coverage 430 条。

## 2026-06-02 追加批次：batch462 齐鲁工业大学

本轮新增齐鲁工业大学 2025 年图书情报专业一志愿拟录取名单 12 条。来源为齐鲁工业大学图书馆（山东省科学院情报研究所）官网招生信息栏目；同期复核首都师范大学、中国药科大学、中国政法大学、南京财经大学、郑州轻工业大学、东北电力大学、山西中医药大学、沈阳体育学院、广东药科大学、西北师范大学、云南民族大学等候选源，因实时跳转首页 HTML、HTTP 404/412/521、附件已过公示期不暴露 href、验证码下载页、页面无人员名单表等原因仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,363 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,363 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,068 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,068 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：606 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，401 所已精确匹配官网记录，29 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 齐鲁工业大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 12 | 0 |

来源：

- 齐鲁工业大学图书情报专业一志愿拟录取名单：https://lib.qlu.edu.cn/2025/0325/c13718a254296/page.htm

验证：

- batch462 clean/public：12 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建并复核：Public_Records 277,069 行（含表头）、Source_Summary 607 行（含表头）、Coverage 431 行（含表头）。

## 2026-06-02 追加批次：batch467 沈阳航空航天大学

本轮新增沈阳航空航天大学航空发动机学院 2022 级博士研究生申请考核制拟录取考生名单 4 条。来源为沈阳航空航天大学研究生院官网 `__local` PDF 直链；同期复核北京林业大学、中国海洋大学、北京电影学院、北京服装学院等候选源，因附件为政治审查表而非名单、实时 HTTP 404/412、跳转 custom404 等原因仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,367 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,367 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,072 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,072 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：607 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，402 所已精确匹配官网记录，28 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 沈阳航空航天大学 | 2022 | postgraduate_admission_list | postgraduate_exam_or_admission | 4 | 0 |

来源：

- 沈阳航空航天大学航空发动机学院 2022 级博士研究生申请考核制拟录取考生名单：https://yjs.sau.edu.cn/__local/7/46/7E/BD24B1756017798876E19BCFE52_9517D8A5_92BD.pdf?e=.pdf

验证：

- batch467 clean/public：4 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建并复核：Public_Records 277,073 行（含表头）、Source_Summary 608 行（含表头）、Coverage 431 行（含表头）。

## 2026-06-02 追加批次：batch480 山东理工大学

本轮新增山东理工大学化学工程与技术学科 2026 年博士研究生补录名单 1 条。来源为山东理工大学研究生工作部官网 HTML 表格；同期复核首都师范大学、桂林医科大学、山东理工大学 2026 年博士拟录取公示列表页等候选源，因实时跳转首页 HTML、连接重置、列表页无人员表等原因仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,368 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,368 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,073 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,073 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：608 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，403 所已精确匹配官网记录，27 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山东理工大学 | 2026 | doctoral_admission_list | postgraduate_exam_or_admission | 1 | 1 |

来源：

- 山东理工大学化学工程与技术学科 2026 年博士研究生补录名单公示：https://yjsh.sdut.edu.cn/2026/0528/c5139a565537/page.htm

验证：

- batch480 curated/public：1 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建并复核：Public_Records 277,074 行（含表头）、Source_Summary 609 行（含表头）、Coverage 431 行（含表头）。

## 2026-06-02 追加批次：batch481 天津财经大学

本轮新增天津财经大学 2026 年具备硕博连读拟录取资格名单 5 条。来源为天津财经大学研究生院官网 HTML 表格；同期复核中国海洋大学、华东师范大学、中国医科大学、南京财经大学、山西中医药大学、郑州轻工业大学等候选源，因附件公示结束无 href、验证码下载入口、正文仅剩附件提示等原因仅留证不入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,373 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,373 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,078 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,078 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：609 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，404 所已精确匹配官网记录，26 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 天津财经大学 | 2026 | doctoral_admission_list | postgraduate_exam_or_admission | 5 | 0 |

来源：

- 天津财经大学 2026 年具备硕博连读拟录取资格名单：https://yjsy.tjufe.edu.cn/info/1044/3736.htm

验证：

- batch481 curated/public：5 条，硬排除词扫描命中 0。
- A+B master public 的记录状态字段扫描无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建并复核：Public_Records 277,079 行（含表头）、Source_Summary 610 行（含表头）、Coverage 431 行（含表头）。

## 2026-06-02 追加批次：batch482 沈阳体育学院

本轮新增沈阳体育学院 2025 年硕士研究生调剂志愿拟录取名单公示（递补）1 条。来源为沈阳体育学院研究生处官网 HTML 正文；该页本地 crawler/curl 返回 HTTP 404，但通过网页检索打开同一学校官网 URL 可读到正文名单。同期复核同校博士递补拟录取页面，因名单为图片且本地请求 404 未 OCR 入库。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,374 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,374 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,079 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,079 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：610 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，405 所已精确匹配官网记录，25 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 沈阳体育学院 | 2025 | master_admission_list | postgraduate_exam_or_admission | 1 | 0 |

来源：

- 沈阳体育学院 2025 年硕士研究生调剂志愿拟录取名单公示（递补）：https://yjs.syty.edu.cn/info/1010/2471.htm

验证：

- batch482 curated/public：1 条，硬排除词扫描命中 0。
- A+B master public 的记录状态字段扫描无明确非录取、放弃、缺考、候补、不合格、待递补等状态残留。
- 工作簿已重建并复核：Public_Records 277,080 行（含表头）、Source_Summary 611 行（含表头）、Coverage 431 行（含表头）。

## 2026-06-02 追加批次：batch483 甘肃中医药大学

本轮新增甘肃中医药大学 2024 年硕士研究生招生考试拟录取名单 1245 条。来源为甘肃中医药大学研究生院官网 PDF 直链；第三方转载页仅用于恢复官网 PDF URL，未使用第三方人员行数据。通用爬虫抽出的原始记录缺姓名和状态字段，未直接合并；新增定向解析脚本与单测后，按 PDF 文本层保留明确 `拟录取` 且 `合格` 的记录，排除 5 条缺明确体检结果的断行。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：272,619 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：272,619 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：278,324 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：278,324 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：612 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，406 所已精确匹配官网记录，24 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 甘肃中医药大学 | 2024 | master_admission_list | postgraduate_exam_or_admission | 1164 | 0 |
| 甘肃中医药大学 | 2024 | recommendation_admission_list | recommendation_exemption | 81 | 0 |

来源：

- 甘肃中医药大学 2024 年硕士研究生招生考试拟录取名单公示：https://yjsc.gszy.edu.cn/ueditor/php/upload/file/20240507/1715071988136303.pdf

验证：

- `python -m unittest tests.test_curate_batch483_gszy_2024_master_pdf`：3 项通过。
- batch483 curated/public：1245 条，硬排除词扫描命中 0。
- A+B master public 的记录状态字段扫描无明确非录取、放弃、缺考、候补、不合格、待递补、拟淘汰等状态残留。
- 工作簿已重建并复核：Public_Records 278,325 行（含表头）、Source_Summary 613 行（含表头）、Coverage 431 行（含表头）。

## 2026-06-02 追加批次：batch486 华东师范大学

本轮新增华东师范大学 2025 年全国硕士研究生招生考试拟录取名单 3688 条。来源为华东师范大学信息公开官网页面及官方 PDF 附件；PDF 为图片型表格，无可用文本层，因此新增 OCR 定制解析脚本。脚本渲染 79 页 PDF，使用 RapidOCR 识别表格词块，再按固定列重组姓名、考生编号、院系、学科、学习方式和成绩字段。3 条 OCR 行因缺可靠姓名或院系未入库，未凭上下文猜测姓名。

最新交付版：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`：5,705 条
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`：5,705 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：276,307 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：276,307 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：282,012 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：282,012 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：613 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校，407 所已精确匹配官网记录，23 所仍未完成
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建

本批新增明细：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 华东师范大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 3688 | 0 |

来源：

- 华东师范大学 2025 年全国硕士研究生招生考试拟录取名单公示：https://xxgk.ecnu.edu.cn/fc/45/c11832a719941/page.htm
- 官方 PDF：https://xxgk.ecnu.edu.cn/_upload/article/files/91/2c/c572f8d244cd849ec879f177dae4/fa6b90ed-39b0-4359-bf44-3482c5c03c46.pdf

新增脚本与测试：

- `scripts/curate_batch486_ecnu_2025_ocr_pdf.py`
- `tests/test_curate_batch486_ecnu_2025_ocr_pdf.py`

验证：

- `python -m unittest tests.test_curate_batch486_ecnu_2025_ocr_pdf`：3 项通过。
- batch486 ECNU curated/public：3688 条；空关键字段 0，重复键 0，硬排除词扫描命中 0。
- A+B master public：282,012 条，状态字段坏词扫描命中 0。
- 工作簿已重建并复核：Public_Records 282,013 行（含表头）、Source_Summary 614 行（含表头）、Coverage 431 行（含表头）。
