# B 类：高校官网推免/升学名单抓取更新

更新日期：2026-06-02

## 本轮结论

B 类数据最可行的抓取方式是：先用搜索命中的高校官网名单页做种子，再抓取页面正文、表格和可下载附件。直接从学校首页批量扫“教务处/本科生院/推免名单”的命中率很低，且很多高校子域名会出现 SSL 握手失败、证书不匹配或反爬拦截。

此前 batch120/batch121/batch122/batch123/batch124/batch125/batch126/batch127/batch128/batch129/batch130 继续使用搜索命中的高校官网名单页和栏目页扩展 B 类官网源。batch120 主要用于排查湖南大学、华中师范大学、福建师范大学、福建农林大学、集美大学、华侨大学、北京语言大学、济南大学等入口，其中多处附件进入验证码下载桥或公示结束页，未形成可入库记录；同时新增“后台管理”等页面导航噪声过滤。batch121 命中广西师范大学 2026 年硕士研究生拟录取名单直链 PDF 和桂林理工大学学院级推免 PDF，补入 1,797 条人员级记录。batch122 继续排查山东、宁夏、湖北等未覆盖院校，最终从宁夏医科大学官网 PDF 补入 74 条人员级记录。batch123 从济南大学官网 PDF 补入 110 条 2026 年拟录取人员级记录，并剔除江西师范大学非人员级推免名额分配表。batch124 修正徐州医科大学和浙江理工大学官网入口后，补入 1,555 条人员级记录；其中徐州医科大学源 PDF 无专业列，已保留成绩并标记需复核。batch125 从贵州医科大学、广西艺术学院、兰州交通大学和广州医科大学补入 1,920 条人员级记录。batch126 从桂林电子科技大学、大连工业大学、东华理工大学和吉林师范大学补入 2,272 条人员级记录。batch127 从山东财经大学官网 VSB 内嵌 PDF 补入 6 条人员级记录。batch128 从上海师范大学官网 PDF 和安徽财经大学推免递补正文补入 174 条人员级记录。batch129 从海南师范大学、福建中医药大学、福建医科大学和首都经济贸易大学官网 PDF/页面补入 2,537 条人员级记录。batch130 将西南大学总入口展开到学院页后，补入 129 条人员级记录。合并到 B 类官网总表后：

- 清洗总表：`data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`
- 脱敏公开表：`data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`
- 学校/年份汇总：`data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`
- 截至最新 batch354，当前 B 类官网总表：263,813 条清洗记录，442 个学校/年份/文档类型汇总组。

## 2026-06-02 batch354：陕西科技大学 2025 年硕士拟录取 PDF 入库

batch353 继续尝试天津财经大学 2026 年硕博连读拟录取资格名单，项目爬虫实时返回 404；随后用普通 `curl.exe -L` 复核同一官方 URL，下载结果仍为官网 404 页面，因此留证不入库。

batch354 命中陕西科技大学研究生招生信息网“陕西科技大学2025年硕士研究生拟录取考生名单公示”页面，页面正文暴露官方 PDF 附件。通用爬虫可下载 PDF 并抽取候选行，但通用清洗漏掉准考证号，且无法处理专业代码 `0822Z3`、专业名称换行、推免行无初试/复试成绩等表格形态。本批新增专项清洗脚本，使用 PyMuPDF word 坐标重组表格行与续行，解析 `姓名/准考证号/学院名称/学院代码/专业代码/专业名称/学习形式/初试总成绩/复试成绩/总成绩/备注`。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 陕西科技大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,959 | 0 |

可追溯来源：
- 陕西科技大学 2025 年硕士研究生拟录取考生名单公示页：`https://yjszs.sust.edu.cn/info/1014/3429.htm`
- 官方 PDF 附件：`https://yjszs.sust.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1276705140&wbfileid=D57A0CEF4D463A6B1590A67CC8146F6A`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch354_sust_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch354_sust_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch354_sust_admission/`
- `scripts/curate_batch354_sust_admission.py`
- `tests/test_curate_batch354_sust_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch354_sust_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：263,813 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：263,813 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：442 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：269,518 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：269,518 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：594 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，390 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch354_sust_admission tests.test_curate_batch350_bisu_admission`：6 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：128 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch354 陕西科技大学记录 1,959 条；空姓名 0，空准考证号 0，空学院 0，空拟录取专业 0，需复核 0，重复关键记录 0，最低质量分 93。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无既定排除短语残留。
- 工作簿已重建：Overview 15 行、Source_Summary 595 行（含表头）、Coverage 431 行（含表头）、Public_Records 269,519 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch350-batch352：北京第二外国语学院与太原科技大学入库

batch340-batch352 继续筛查剩余覆盖缺口。华中科技大学、东北师范大学、南京财经大学、中国药科大学、中国医科大学、云南民族大学、中国政法大学、山西中医药大学、沈阳体育学院、大连海洋大学等官网源已留证；主要未入库原因为实时 404/410/412/521、JS challenge、验证码下载桥、公示期结束后不再暴露人员附件，或仅有公告正文无人员表。北京协和医学院页面可抓取历史录取名单入口但附件进入验证码下载桥；北京服装学院命中页实时返回 404。

北京第二外国语学院官网 PDF 直链可下载 2025 年研究生招生考试一志愿拟录取名单。通用爬虫能保存 PDF，但因表格文本中部分“姓名+考生编号”粘连，未直接产出记录。本批新增专项脚本，使用 PyMuPDF word 坐标按行重组，解析 `姓名/考生编号/初试成绩/复试成绩/录取成绩/培养单位/专业`，并保留末尾“退役大学生士兵专项计划”标记。

太原科技大学信息公开专网公开 2025 年学术型博士研究生复试结果公示（第二批），正文明确为第二批学术型博士研究生拟录取名单，表格包含“是否拟录取”列且抓取到的 6 行均为“是”。通用爬虫直接抽取 6 条人员记录，经状态词扫描后合并。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 北京第二外国语学院 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 428 | 0 |
| 太原科技大学 | 2025 | doctoral_admission_list | postgraduate_exam_or_admission | 6 | 0 |

可追溯来源：
- 北京第二外国语学院 2025 年研究生招生考试一志愿拟录取名单 PDF：`https://www.bisu.edu.cn/bucketeducation/67eca8b8e4b078dee86ea4c3.pdf`
- 太原科技大学 2025 年学术型博士研究生复试结果公示（第二批）：`https://xxgk.tyust.edu.cn/info/1141/3712.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch350_beijing_admission_cluster.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch352_tyust_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch350_beijing_admission_cluster/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch352_tyust_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch350_beijing_admission_cluster/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch352_tyust_admission/`
- `scripts/curate_batch350_bisu_admission.py`
- `tests/test_curate_batch350_bisu_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch350_bisu_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：261,854 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：261,854 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：441 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：267,559 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：267,559 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：593 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，389 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch350_bisu_admission tests.test_curate_batch339_tute_admission`：6 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：125 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch350 北京第二外国语学院记录 428 条；空姓名 0，空考生编号 0，空拟录取专业 0，需复核 0，重复关键记录 0，最低质量分 93。
- batch352 太原科技大学记录 6 条；空姓名 0，空报名号 0，空拟录取专业 0，需复核 0，最低质量分 93。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无既定排除短语残留。
- 工作簿已重建：Overview 15 行、Source_Summary 594 行（含表头）、Coverage 431 行（含表头）、Public_Records 267,560 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch339：天津职业技术师范大学 2025 年硕士拟录取 PDF 入库

batch330-batch338 继续筛选剩余覆盖缺口。浙江中医药大学 2025 硕士拟录取公告页返回 HTTP 412、附件下载返回 405；大连外国语大学、沈阳体育学院、沈阳航空航天大学搜索命中页实时返回 404；西北师范大学博士拟录取 PDF 直链实时返回 404；中国人民公安大学 2025/2024 公示页可抓取公告正文，但当前 HTML 不再暴露人员附件；重庆邮电大学博士拟录取页返回 HTTP 412；山西中医药大学页面可抓取，但附件进入验证码下载桥；齐鲁工业大学 2026 公示页显示“公示已结束”，不再暴露人员名单，2025 页返回 HTTP 410；北京第二外国语学院 PDF 下载桥返回 HTTP 502。上述来源均按规则留证不入库。

天津职业技术师范大学官网公开 2025 年硕士研究生拟录取名单 PDF 直链，文本层完整可复现。通用爬虫抽取 526 条候选记录并保留 525 条；专项复核发现 PDF 中另有 1 条“免初试”拟录取人员行无考生编号，通用清洗会丢失。本批新增专项清洗脚本，按 PDF 原文结构解析 `考生编号/姓名/专业代码/拟录取专业/初试成绩/复试成绩/总成绩/学习形式/备注`，并保留无考生编号的免初试行。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 天津职业技术师范大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 526 | 0 |

可追溯来源：
- 天津职业技术师范大学 2025 年硕士研究生拟录取名单 PDF：`https://yjsh.tute.edu.cn/__local/C/8A/6E/B9219C8F5C980B9B37E7A8F165F_C99922C3_54DC6.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch330_zcmu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch331_dlufl_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch332_nwnu_doctor_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch333_syty_sau_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch334_ppsuc_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch335_cqupt_doctor_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch336_qlu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch337_bisu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch338_sxtcm_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch339_tute_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch339_tute_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch339_tute_admission/`
- `scripts/curate_batch339_tute_admission.py`
- `tests/test_curate_batch339_tute_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch339_tute_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：261,420 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：261,420 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：439 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：267,125 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：267,125 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：591 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，387 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch339_tute_admission`：3 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：122 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch339 天津职业技术师范大学记录 526 条；空姓名 0，空考生编号 1（官网原文无编号的免初试行），空拟录取专业 0，需复核 0，重复关键记录 0，最低质量分 81。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无既定排除短语残留。
- 工作簿已重建：Overview 15 行、Source_Summary 592 行（含表头）、Coverage 431 行（含表头）、Public_Records 267,126 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch329：渤海大学 2025 年硕士拟录取 PDF 入库

batch329 从剩余覆盖缺口中继续检索官网源。渤海大学研究生招生信息网公开“渤海大学2025年全国硕士研究生招生拟录取名单公示”页面，页面正文暴露官方 PDF 附件路径。通用爬虫可下载 PDF 并抽取 1,618 条候选记录，但通用 PDF 解析会在部分行中把“学院+专业+就业方式+成绩”错列，例如录取专业误变成 `非定向就业`；因此本批不直接合并通用解析结果，改用专项脚本按 PDF 文本行结构解析。

专项清洗只保留 15 位考生编号开头、且同时具备学院、拟录取专业、拟录取类别、初试成绩、复试成绩、综合成绩和学习方式的人员行。最终入库 1,618 条渤海大学 2025 年硕士拟录取记录，需复核 0 条。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 渤海大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,618 | 0 |

可追溯来源：
- 渤海大学 2025 年全国硕士研究生招生拟录取名单公示页：`https://yjszsxxw.bhu.edu.cn/engine2/general/4173827/detail?engineInstanceId=656393&pageId=85721&typeId=`
- 官方 PDF 附件：`https://yjszsxxw.bhu.edu.cn/engine/upload/engine/2025-04/20250425164722875P.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch329_bhu_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch329_bhu_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch329_bhu_admission/`
- `scripts/curate_batch329_bhu_admission.py`
- `tests/test_curate_batch329_bhu_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch329_bhu_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：260,894 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：260,894 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：438 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：266,599 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：266,599 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：590 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，386 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch329_bhu_admission`：3 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：119 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch329 渤海大学记录 1,618 条；空姓名 0，空考生编号 0，空学院 0，空拟录取专业 0，需复核 0，重复关键记录 0，最低质量分 93。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无既定排除短语残留。
- 工作簿已重建：Overview 15 行、Source_Summary 591 行（含表头）、Coverage 431 行（含表头）、Public_Records 266,600 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch328：新疆医科大学 2023 年硕士拟录取 PDF 入库

batch326-batch327 继续筛选剩余覆盖缺口。大连海洋大学研究生院页面实时归一为 `page.psp` 提示信息页，PDF 直链返回 404，留证不入库；中国政法大学研究生院多篇拟录取公告页实时返回 JS challenge 页面，按规则不绕过、不入库。

新疆医科大学研究生学院官网仍公开 2023 年硕士研究生招生一志愿拟录取名单和调剂第一批拟录取名单 PDF 直链。通用爬虫可下载 PDF 并抽取 3,866 条候选行，但源 PDF 同时包含 `拟录取`、`放弃`、`不予拟录取`、`不予复试`、`计划受限` 等状态，不能直接并表。本批新增专项清洗脚本，使用 `pdftotext -raw` 保留表格顺序，只保留官方状态为 `拟录取` 的人员行，并排除放弃、未录取、未进入复试和计划受限行。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 新疆医科大学 | 2023 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,551 | 0 |

可追溯来源：
- 新疆医科大学 2023 年硕士研究生招生考试一志愿拟录取名单 PDF：`https://yjsxy.xjmu.edu.cn/__local/6/B3/61/0EB24D18B758B3BE925C033E05C_22900A4B_98C6E.pdf`
- 新疆医科大学 2023 年硕士研究生招生考试调剂第一批拟录取名单 PDF：`https://yjsxy.xjmu.edu.cn/__local/F/C8/BE/0B5E79C116DC41A6D4B82162359_7DA3B66E_F6164.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch326_dlou_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch327_cupl_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch328_xjmu_2023_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch328_xjmu_2023_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch328_xjmu_2023_admission/`
- `scripts/curate_batch328_xjmu_admission.py`
- `tests/test_curate_batch328_xjmu_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch328_xjmu_2023_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：259,276 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：259,276 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：437 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：264,981 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：264,981 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：589 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，385 所已精确匹配官网记录

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：116 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch328 新疆医科大学记录 1,551 条，其中一志愿 PDF 1,049 条、调剂第一批 PDF 502 条；空姓名 0，空考生编号 0，空专业 0，需复核 0；最低质量分 93。
- 专项诊断：一志愿 PDF 中 `拟录取` 状态块 1,049/1,049 全部解析成功；调剂第一批 PDF 中 `拟录取` 状态块 502/502 全部解析成功。
- 本批及 B 类 master/public、A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无既定排除短语残留。
- 工作簿已重建：Overview 15 行、Source_Summary 590 行（含表头）、Coverage 431 行（含表头）、Public_Records 264,982 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch325：内蒙古民族大学博士拟录取图片名单入库

batch319-batch324 继续筛选剩余缺口。中国药科大学 2020 推免页实时返回 HTTP 410，2021 博士 PDF 直链返回 404；东北师范大学 2025 硕士拟录取入口返回 404；天津财经大学 2026 硕博连读拟录取资格页返回 404。内蒙古民族大学研究生院首页可抓取，并公开博士拟录取结果、硕士调剂公告和一志愿复试通知；其中两个调剂 PDF 为调剂公告、一志愿 PDF 明确为“进入复试名单”，均不入库。

内蒙古民族大学 2026 年博士招生拟录取结果公示页指向蒙医药学院官网，学院页公开“中药学专业博士研究生招生‘申请-考核’制拟录取名单公示”，名单主体为官方 PNG 图片。图片含 25 行，其中 22 行“是否拟录取=是”、2 行“否”、1 行“放弃”；本批只按官方图片转写并保留“是”的 22 条人员级记录，需复核 0 条。

可追溯来源：
- 研究生院博士结果公示页：`https://yjsy.imun.edu.cn/info/1083/1518.htm`
- 蒙医药学院拟录取名单公示页：`https://myy.imun.edu.cn/info/1063/2220.htm`
- 官方名单 PNG：`https://myy.imun.edu.cn/__local/0/C8/95/43F3387BE2D24CBC0D43A264999_F64151A5_6B4E.png`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch325_imun_doctor_png.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch325_imun_doctor_png/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch325_imun_doctor_png/`
- `scripts/curate_batch325_imun_doctor_png.py`
- `tests/test_curate_batch325_imun_doctor_png.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch325_imun_doctor_png_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：257,725 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：257,725 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：436 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：263,430 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：263,430 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：588 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，384 所已精确匹配官网记录

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：115 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch325 内蒙古民族大学记录 22 条；空姓名 0，需复核 0；“否/放弃”行未入库。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无既定排除短语残留。
- 工作簿已重建：Overview 15 行、Source_Summary 589 行（含表头）、Coverage 431 行（含表头）、Public_Records 263,431 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch318：上海科技大学历史拟录取 HTML 入库与 batch314-317 留证

batch314-batch317 继续围绕剩余覆盖缺口复核官网源。福建师范大学部分旧 URL 返回“无效的文章参数”提示页；华东师范大学和东北师范大学页面可抓取公告正文，但公示结束后未暴露人员级表格或附件 href；北京林业大学页面指向 `http://bz.yzb.bjfu.edu.cn:8080/user` 查询系统，公开 PDF 为政审表模板而非名单；山东理工大学多个公告页只暴露说明附件或仅在正文中保留附件名，真实名单附件不再公开；上海科技大学 2026 调剂拟录取页实时返回 HTTP 410。上述来源均按规则留证不入库。

上海科技大学招生网“原网站数据”中仍公开 4 个历史拟录取 HTML 表格页，均为官网静态页面且可复现。通用爬虫对其中 3 页可抽出部分记录，但会把表头/缺专业列标为需复核，博士页未被通用规则识别；本批新增专项清洗脚本，按 HTML 表格结构解析并去除表头，最终入库 792 条人员级记录，需复核 0 条。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海科技大学 | 2017 | incoming_recommendation_admission_list | recommendation_exemption | 126 | 0 |
| 上海科技大学 | 2017 | postgraduate_admission_list | postgraduate_exam_or_admission | 535 | 0 |
| 上海科技大学 | 2018 | incoming_recommendation_admission_list | recommendation_exemption | 131 | 0 |

可追溯来源：
- 上海科技大学 2017 年推荐免试研究生拟录取名单公示：`https://yanzhao.shanghaitech.edu.cn/2016/1026/c1616a12865/page.htm`
- 上海科技大学 2017 年硕士研究生统考复试拟录取名单公示：`https://yanzhao.shanghaitech.edu.cn/2017/0502/c1616a12870/page.htm`
- 上海科技大学硕博连读 2017 年秋季入学博士研究生拟录取名单公示：`https://yanzhao.shanghaitech.edu.cn/2017/0612/c1616a12871/page.htm`
- 上海科技大学 2018 年推荐免试研究生拟录取名单公示：`https://yanzhao.shanghaitech.edu.cn/2017/1116/c1616a12872/page.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch317_shanghaitech_probe.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch318_shanghaitech_historic.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch318_shanghaitech_historic/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch318_shanghaitech_historic/`
- `scripts/curate_batch318_shanghaitech_historic.py`
- `tests/test_curate_batch318_shanghaitech_historic.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch318_shanghaitech_historic_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：257,703 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：257,703 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：435 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：263,408 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：263,408 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：587 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，383 所已精确匹配官网记录

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：114 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch318 上海科技大学记录 792 条；4 个来源分别为 126、339、196、131 条；空姓名 0，需复核 0。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 588 行（含表头）、Coverage 431 行（含表头）、Public_Records 263,409 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch313：西华师范大学硕士拟录取 PDF 与博士拟录取 HTML 入库

batch313 继续从剩余缺口中检索官网源。西华师范大学研究生院 2025 年硕士研究生拟录取名单、第二批拟录取名单和博士研究生拟录取名单页面均可由官网页面/附件复现；东北师范大学相关官网页本轮可抓取页面正文，但未解析出人员级表格或可直接下载附件，暂留证不入库。

可入库来源为西华师范大学研究生院 2025 年硕士研究生拟录取名单第一批、第二批 PDF 附件，以及 2025 年博士研究生拟录取名单 HTML 表格。硕士 PDF 的姓名字段已由学校公开源做星号遮蔽，本批保留官方发布形态，并在 public 表再次脱敏。第一批 PDF 文本层含 1,979 个唯一考生编号，第二批含 2 个唯一考生编号；博士 HTML 表格含 12 条人员记录。本批按 TDD 新增专项清洗脚本，处理 PDF 中学院名、专业名和研究方向跨行拆列问题，最终保留 1,993 条人员级记录，需复核 0 条。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西华师范大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,993 | 0 |

可追溯来源：
- 西华师范大学 2025 年硕士研究生拟录取名单公示：`https://yjsy.cwnu.edu.cn/info/1014/16892.htm`
- 第一批官方 PDF 附件：`https://yjsy.cwnu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1514373409&wbfileid=00C2D4C07C9B7982EC071FBCFCCFA53B`
- 西华师范大学 2025 年硕士研究生拟录取名单公示（第二批）：`https://yjsy.cwnu.edu.cn/info/1014/17022.htm`
- 第二批官方 PDF 附件：`https://yjsy.cwnu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1514373409&wbfileid=F95E88AA4D8F2CE21F1AB4D8695B1F7B`
- 西华师范大学 2025 年博士研究生拟录取名单公示：`https://yjsy.cwnu.edu.cn/info/1014/17372.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch313_cwnu_nenu_probe.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch313_cwnu_nenu_probe/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch313_cwnu_nenu_probe/`
- `scripts/curate_batch313_cwnu_admission.py`
- `tests/test_curate_batch313_cwnu_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch313_cwnu_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：256,911 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：256,911 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：432 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：262,616 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：262,616 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：584 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，382 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch313_cwnu_admission`：2 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：112 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch313 西华师范大学记录 1,993 条；硕士 PDF 考生编号 1,981 个且唯一；空姓名 0，硕士 PDF 空学院 0，空录取专业 0，需复核 0。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 585 行（含表头）、Coverage 431 行（含表头）、Public_Records 262,617 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch312：长春师范大学一志愿拟录取 PDF 入库与剩余缺口留证

batch312 继续从剩余缺口中检索官网源。中国药科大学、中国医科大学、浙江中医药大学、桂林医科大学、南京理工大学、中国海洋大学、长春师范大学等均建立 seed 复核；其中中国药科大学返回 HTTP 410，浙江中医药大学返回 HTTP 412/405，桂林医科大学返回 404 或远端断开，南京理工大学返回 HTTP 410，中国医科大学附件为 3805 字节下载桥。中国海洋大学工程学院页面可抓取，但附件已随“公示已结束”不暴露真实下载链接，未入库。

可入库来源为长春师范大学研究生院“2026 年硕士研究生招生考试一志愿拟录取名单及未录取名单公示”。官网页面公开 VSB `download.jsp` 附件，项目爬虫可带页面上下文跟进下载 PDF。该 PDF 同时包含拟录取与未录取人员；本批按 TDD 新增专项清洗脚本，使用 `pdftotext -raw` 保持表格逻辑顺序，解析出 908 条状态记录，其中 `是` 823 条、`否` 85 条，只保留 `是否拟录取=是` 的人员行。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 长春师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 823 | 0 |

可追溯来源：
- 长春师范大学 2026 年硕士研究生招生考试一志愿拟录取名单及未录取名单公示：`https://yjs.ccsfu.edu.cn/info/1007/265600.htm`
- 官方 PDF 附件：`https://yjs.ccsfu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1321085661&wbfileid=0C498A5A7D40ACAC245F44889FE994B2`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch312_remaining_failed_probes.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch312_ccsfu_attachment_probe/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch312_ccsfu_attachment_probe/`
- `scripts/curate_batch312_ccsfu_admission.py`
- `tests/test_curate_batch312_ccsfu_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch312_ccsfu_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：254,918 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：254,918 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：431 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：260,623 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：260,623 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：583 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，381 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch312_ccsfu_admission`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：110 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- batch312 长春师范大学记录 823 条，考生编号唯一 823，空姓名 0，空学院 0，空录取专业 0，需复核 0。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 584 行（含表头）、Coverage 431 行（含表头）、Public_Records 260,624 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch311：上海体育大学旧年度博士拟录取 PDF 文本入库

batch311 继续围绕剩余覆盖缺口查找官网可复现来源。成都体育学院、东北师范大学、上海体育大学 2026 年拟录取/推免相关官网页均可由搜索定位，但从当前工作区直接请求时返回源站重定向到 `127.0.0.1:9`，按规则不绕过、不入库。上海体育大学（源文件发布时校名为“上海体育学院”）另有 2020 年博士研究生“申请-考核”制拟录取名单官方 PDF 被搜索索引公开出文本层；本批将该官方 PDF 文本层作为 raw evidence 保存，并只抽取带 `201900xx` 报名号、姓名、专业、报考类别和最终成绩的人员行。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海体育大学 | 2020 | postgraduate_admission_list | postgraduate_exam_or_admission | 23 | 0 |

可追溯来源：
- 上海体育学院 2020 年博士研究生“申请-考核”制拟录取名单公示 PDF：`https://yjsc.sus.edu.cn/__local/C/9B/29/2E3E4C2B32BCCD234FFA36D4DE2_850177CB_4B537.pdf?e=.pdf`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch311_sus_doctoral_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch311_sus_doctoral_admission/yjsc.sus.edu.cn/sus_2020_doctoral_admission_web_pdf_text.txt`
- `scripts/curate_batch311_sus_doctoral_admission.py`
- `tests/test_curate_batch311_sus_doctoral_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch311_sus_doctoral_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：254,095 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：254,095 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：430 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：259,800 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：259,800 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：582 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，380 所已精确匹配官网记录

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：109 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- B 类 master/public 与 A+B clean/public 的 `remarks`、`quality_flags` 状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 583 行（含表头）、Coverage 431 行（含表头）、Public_Records 259,801 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 追加进展：batch226 四川美术学院官网 PDF 名单入库

batch226 继续从剩余缺口中筛选官网拟录取来源。本批确认四川美术学院招生处 2026 年硕士研究生一志愿拟录取名单、调剂拟录取名单和接收推免生拟录取名单均可访问，附件 PDF 可直接下载。此前 batch225 抓取了大连外国语大学和南京财经大学官网公示页，但其附件下载页均要求输入验证码，自动化请求只取得验证码下载桥 HTML；本轮不绕过验证码，保留抓取证据但不入库。

通用爬虫 3 个种子抓取 7 个文档，通用解析得到 159 条，但质检发现大量表头、学院名和分数字段被误识别为人员记录。按 TDD 新增 `scripts/curate_batch226_scfai.py` 和 `tests/test_curate_batch226_scfai.py`，用 `pdftotext -raw` 按 PDF 表格文本结构重建人员记录：一志愿 505 条、调剂 3 条、推免 82 条，最终得到 590 条人员级记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：233,673 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：233,673 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：388 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：239,383 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：239,383 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：540 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，341 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 239,384 行（含表头），Source_Summary 541 行（含表头），Coverage 431 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch226 清洗记录 590 条，空姓名 0，空考生编号 0，空录取专业 0，需复核 0，重复键 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0，表头词 `复试成绩/口语听力` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：72 tests OK。

## 2026-05-28 追加进展：batch224 中国石油大学（华东）硕士拟录取扫描 PDF 入库

batch224 继续从剩余缺口中筛选官网拟录取来源。本批确认中国石油大学（华东）研究生招生网 2026 年硕士研究生拟录取名单公示页和官方 PDF 附件可访问。同期复核的中国海洋大学搜索直链 PDF 返回 404，本轮不入库。

通用爬虫 1 个种子抓取 2 个文档，页面和 PDF 均未被通用解析抽出人员记录；其中 PDF 为 31 页扫描图像，`pdftotext` 无可抽取文本。按 TDD 新增 `scripts/curate_batch224_upc_admission.py` 和 `tests/test_curate_batch224_upc_admission.py`，用 `pdftoppm` 200dpi 渲染页面、`RapidOCR` 做文字识别，并结合表格横线重建真实单元格行，处理跨栏、跨页、跨行学院/专业/姓名。质检时对 5 个 OCR 漏字姓名单元格和 3 个长专业标题做人工图像校正。最终得到 2,463 条硕士拟录取记录。

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
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch224_upc_admission/`
- `scripts/curate_batch224_upc_admission.py`
- `tests/test_curate_batch224_upc_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch224_upc_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：233,083 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：233,083 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：386 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：238,793 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：238,793 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：538 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，340 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 238,794 行（含表头），Source_Summary 539 行（含表头），Coverage 431 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch224 清洗记录 2,463 条，空姓名 0，空考生编号 0，空学院 0，空专业 0，需复核 0，重复键 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：71 tests OK。

## 2026-05-28 追加进展：batch223 中央民族大学博士拟录取名单入库

batch223 继续从剩余缺口中筛选可直接抓取的官网拟录取来源。本批确认中央民族大学研究生招生网 2026 年博士研究生拟录取公示页可访问，页面附件包含学术学位博士、专业学位博士和第二批博士拟录取名单。同期复核的中国政法大学 2026 年推免拟录取公示页返回浏览器挑战脚本，自动化请求无法取得真实正文，本轮不绕过挑战、不入库。

通用爬虫 3 个种子抓取 23 个文档，原始结构化 159 条；其中 14 个老式 `.xls` 附件被学校站点下载为无扩展名 OLE `.bin`，通用爬虫未进入 Excel 解析。按 TDD 新增 `scripts/curate_batch223_muc_doctoral_admission.py` 和 `tests/test_curate_batch223_muc_doctoral_admission.py`，使用 `xlrd` 读取 legacy xls/bin，用 `openpyxl` 读取 xlsx，按“姓名、报名号、报考院系、报考专业、研究方向、专项计划、报考类别、拟录取意见”抽取人员级记录。最终从 19 个附件得到 540 条博士拟录取记录。

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
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch223_muc_doctoral_admission/`
- `scripts/curate_batch223_muc_doctoral_admission.py`
- `tests/test_curate_batch223_muc_doctoral_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch223_muc_doctoral_admission_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：230,620 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：230,620 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：385 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：236,330 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：236,330 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：537 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，339 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 236,331 行（含表头），Source_Summary 538 行（含表头），Coverage 431 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch223 清洗记录 540 条，空姓名 0，空报名号 0，需复核 0，来源附件 19 个，重复键 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：70 tests OK。

## 2026-05-28 追加进展：batch222 北方民族/西北民族官网拟录取名单入库

batch222 继续从剩余缺口中筛选可直接抓取的官网拟录取来源。本批确认并入库北方民族大学 2026 年硕士研究生招生拟录取名单、北方民族大学 2026 年博士研究生“申请-考核”拟录取名单，以及西北民族大学 2026 年全国硕士研究生招生一志愿拟录取名单公示页下的 3 个官方 PDF 附件。

通用爬虫 3 个种子抓取 6 个文档，原始结构化 1,511 条，通用清洗保留 1,332 条。质检发现西北民族大学 PDF 被通用表格解析错位：`person_name` 被填成“麻醉学”等专业名，`student_id` 被填成方向码 `00`；同时少干计划 PDF 实际 47 人、退役士兵专项实际 10 人，通用解析分别少取/多取。按 TDD 新增 `scripts/curate_batch222_minzu_universities.py` 和 `tests/test_curate_batch222_minzu_universities.py`，保留北方民族大学通用清洗中的 1,025 条正确记录，并用 `pdftotext -raw` 按序号、院系、专业代码、方向码、姓名、考生编号和成绩列重解西北民族大学 3 个 PDF，最终得到 1,515 条人员级记录。

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
- `data/logs/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities/`
- `scripts/curate_batch222_minzu_universities.py`
- `tests/test_curate_batch222_minzu_universities.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：230,080 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：230,080 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：384 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：235,790 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：235,790 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：536 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，338 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 235,791 行（含表头），Source_Summary 537 行（含表头），Coverage 431 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch222 清洗记录 1,515 条，空姓名 0，需复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0，西北民族错位 `person_name=麻醉学`/`student_id=00` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：69 tests OK。

## 2026-05-28 追加进展：batch221 华东政法/河南财经政法/湖北中医药官网名单入库

batch221 继续从剩余缺口中筛选可直接抓取的官网名单源。本批确认并入库华东政法大学 2025 年推免生拟录取 PDF、河南财经政法大学 2025 年推免生拟录取 HTML 表格、湖北中医药大学 2026 年博士补录拟录取 HTML 正文。同期复核的华东政法大学 2025 年统考硕士拟录取 PDF 搜索直链在实时请求中返回 HTTP 404，未入库。

通用爬虫 4 个种子中抓取 3 个文档，原始结构化 889 条；其中华东政法 PDF 被水印“华东政法大学研招未经许可严禁转载”打散，通用解析膨胀到 888 条噪声记录，湖北中医药补录正文因无表格通用解析为 0 条。本批按 TDD 新增 `scripts/curate_batch221_ecupl_huel_hbucm.py` 和 `tests/test_curate_batch221_ecupl_huel_hbucm.py`，使用 `pdftotext -raw` 重组华东政法 PDF，并用 HTML 表格/正文正则补齐河南财经政法和湖北中医药记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：228,565 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：228,565 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：382 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：234,275 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：234,275 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：534 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，336 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 234,276 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch221 清洗记录 351 条，空姓名 0，需复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0，PDF 水印碎片残留 0。
- 合并时使用包含 `ranking` 的批次去重键，避免华东政法脱敏同名同专业记录被误判重复；本批 351 条全部入库。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages tests.test_curate_batch212_more_remaining_medical_tianjin_pages tests.test_curate_batch213_more_remaining_major_universities tests.test_curate_batch216_xatu_recommendation tests.test_curate_batch217_sdca_art_colleges tests.test_curate_batch220_zafu_doctoral_supplement tests.test_curate_batch221_ecupl_huel_hbucm`：306 tests OK。

## 2026-05-28 追加进展：batch220 浙江农林大学博士补录拟录取 HTML 入库

batch220 从剩余缺口中定位到浙江农林大学研究生招生信息网 2026 年博士研究生拟录取名单补录公示。两条详情页均为官网 HTML 表格，每页 1 条补录记录，可直接结构化。同期复核的广东药科大学旧线索返回 404，中国石油大学（华东）候选页返回模板参数错误，北京林业大学研招站连接失败，均未入库。

通用爬虫 2 个种子中抓取 2 个页面，原始结构化 2 条。通用解析遗漏考生编号、研究方向、综合考核成绩和招生方式，本批按 TDD 新增 `scripts/curate_batch220_zafu_doctoral_supplement.py` 和 `tests/test_curate_batch220_zafu_doctoral_supplement.py`，从 HTML 表格补齐字段后输出 curated 记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：228,214 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：228,214 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：379 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：233,924 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：233,924 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：531 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，333 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 233,925 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch220 清洗记录 2 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages tests.test_curate_batch212_more_remaining_medical_tianjin_pages tests.test_curate_batch213_more_remaining_major_universities tests.test_curate_batch216_xatu_recommendation tests.test_curate_batch217_sdca_art_colleges tests.test_curate_batch220_zafu_doctoral_supplement`：305 tests OK。

## 2026-05-28 追加进展：batch219 五邑大学硕士拟录取 PDF 入库

batch219 继续从剩余缺口中筛选官网直链 PDF。五邑大学 2026 年硕士研究生拟录取名单 PDF 位于学校官网 `__local` 静态文件路径，可直接下载并含可抽取文本层。同期检索到的桂林医科大学若干名单线索在实时请求中返回 404/403，未入库。

通用爬虫 1 个种子中抓取 1 个 PDF，原始结构化 532 条。通用清洗后保留 510 条人员级记录，剔除的是 21 条表头“姓名”和 1 条错位院系行；本批记录包含姓名、拟录取学院、拟录取专业代码/名称和成绩备注，原文未公开考生编号。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：228,212 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：228,212 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：378 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：233,922 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：233,922 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：530 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，332 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 233,923 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch219 清洗记录 510 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages tests.test_curate_batch212_more_remaining_medical_tianjin_pages tests.test_curate_batch213_more_remaining_major_universities tests.test_curate_batch216_xatu_recommendation tests.test_curate_batch217_sdca_art_colleges`：304 tests OK。

## 2026-05-28 追加进展：batch218 河南科技大学硕士统考拟录取 PDF 入库

batch218 从剩余缺口中定位到河南科技大学研究生院 2026 年硕士研究生统考拟录取名单公示。页面为静态官网公告，正文通过 `showVsbpdfIframe` 嵌入官方 PDF，PDF 可直接下载并含可抽取文本层。

通用爬虫 1 个种子中抓取 2 个页面/附件，原始结构化 2,293 条，均来自官方 PDF。通用解析已能提取考生编号、姓名、录取学院、录取专业、学习方式、初试成绩、复试成绩和总成绩；通用清洗后全部保留为人员级记录，本批未新增专项解析代码。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：227,702 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：227,702 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：377 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：233,412 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：233,412 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：529 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，331 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 233,413 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch218 清洗记录 2,293 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages tests.test_curate_batch212_more_remaining_medical_tianjin_pages tests.test_curate_batch213_more_remaining_major_universities tests.test_curate_batch216_xatu_recommendation tests.test_curate_batch217_sdca_art_colleges`：304 tests OK。

## 2026-05-28 追加进展：batch217 山东艺术学院美术学院推免资格 PDF 入库

batch217 继续从艺术类院校缺口中查找官网推免名单。山东艺术学院美术学院 2026 年推荐免试攻读硕士研究生资格名单页面可访问，附件 PDF 可直接下载且含文本层；戏剧学院名单页为图片正文，艺术管理学院名单页包含扫描 PDF，均已留存原始证据但未强行转写入库。

通用爬虫 5 个种子中抓取 9 个页面/附件，原始结构化 17 条，均来自美术学院 PDF。由于通用解析混入 2 条表头/折行噪声，本批新增 `scripts/curate_batch217_sdca_art_colleges.py` 和 `tests/test_curate_batch217_sdca_art_colleges.py`，按 PDF 文本中的 9 位学号行重建记录，最终保留 15 条人员级记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：225,409 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：225,409 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：376 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：231,119 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：231,119 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：528 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，330 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 231,120 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch217 清洗记录 15 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages tests.test_curate_batch212_more_remaining_medical_tianjin_pages tests.test_curate_batch213_more_remaining_major_universities tests.test_curate_batch216_xatu_recommendation tests.test_curate_batch217_sdca_art_colleges`：304 tests OK。

## 2026-05-28 追加进展：batch216 西安工业大学校级推免拟推荐名单入库

batch216 从剩余缺口中定位到西安工业大学研究生院校级 2026 年推荐优秀应届本科毕业生免试攻读研究生拟推荐人员名单。页面为静态 HTML 表格，字段包含序号、学号、学生姓名、学院、本科专业代码和本科专业名称，可直接结构化。

通用爬虫 1 个种子中抓取 2 个页面，原始结构化 230 条，均来自校级名单页。由于通用解析只保留了专业代码且全部标记为需复核，本批新增 `scripts/curate_batch216_xatu_recommendation.py` 和 `tests/test_curate_batch216_xatu_recommendation.py`，按 HTML 表格补齐本科专业名称和推荐状态，最终保留 230 条人员级记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：225,394 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：225,394 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：375 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：231,104 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：231,104 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：527 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，329 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 231,105 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch216 清洗记录 230 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages tests.test_curate_batch212_more_remaining_medical_tianjin_pages tests.test_curate_batch213_more_remaining_major_universities tests.test_curate_batch216_xatu_recommendation`：303 tests OK。

## 2026-05-28 追加进展：batch213 武汉理工大学交通与物流学院推免拟录取 PDF 入库

batch213 继续从剩余缺口中筛选重点高校官网源。武汉理工大学交通与物流工程学院 2026 年接收推荐免试攻读硕士学位和直接攻读博士学位研究生拟录取名单 PDF 可直接下载并含文本层；东北师范大学页面可访问但名单跳转到查询系统后实时返回“录取名单尚未公布”；北京协和医学院公示页给出的查询系统当前显示 2027 年空表；中国政法大学页面返回 JavaScript challenge 页，均留证不入库。

通用爬虫 4 个种子中抓取 8 个页面/附件，原始结构化 89 条，均来自武汉理工大学 PDF。由于通用解析把附件 URL 日期误判为 2025，并将接收推免拟录取名单映射为普通推免名单，本批新增 `scripts/curate_batch213_more_remaining_major_universities.py` 和 `tests/test_curate_batch213_more_remaining_major_universities.py`，专项修正年份、文档类型和路径，最终保留 89 条人员级记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：225,164 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：225,164 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：374 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：230,874 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：230,874 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：526 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，328 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 230,875 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch213 清洗记录 89 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages tests.test_curate_batch212_more_remaining_medical_tianjin_pages tests.test_curate_batch213_more_remaining_major_universities`：302 tests OK。

## 2026-05-28 追加进展：batch212 石家庄铁道大学一志愿拟录取 PDF 入库

batch212 继续从剩余缺口中筛选医学、天津和华北院校官网源。石家庄铁道大学研究生学院一志愿复试成绩和拟录取名单 PDF 可直接下载并含文本层；山西中医药大学附件进入验证码下载桥页；天津科技大学外国语学院页面陷入自跳转 302 循环；云南中医药大学和天津职业技术师范大学入口实时返回 404，均留证不入库。

通用爬虫 5 个种子中抓取 5 个页面/附件，原始结构化 1,207 条，均来自石家庄铁道大学 PDF。复核发现通用解析混入表头碎片、空白录取状态行、`缺考` 和 `复试不合格` 行；本批新增 `scripts/curate_batch212_more_remaining_medical_tianjin_pages.py` 和 `tests/test_curate_batch212_more_remaining_medical_tianjin_pages.py`，只保留录取状态明确为 `拟录取` 的考生，最终保留 1,016 条人员级记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：225,075 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：225,075 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：373 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：230,785 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：230,785 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：525 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，327 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 230,786 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch212 清洗记录 1,016 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages tests.test_curate_batch212_more_remaining_medical_tianjin_pages`：301 tests OK。

## 2026-05-28 追加进展：batch211 同济大学口腔医学院官网名单入库

batch211 继续从剩余覆盖缺口中筛选可实时复现的官网源。南京财经大学官网页可访问但 PDF 附件进入验证码下载桥页；西安电子科技大学页面只保留“公示期已过”文字且无静态名单；浙江农林大学入口实时返回 404，上海科技大学和中国药科大学入口返回 410。最终可入库来源为同济大学口腔医学院 2026 届本科生推荐免试研究生结果公示 HTML 表格。

通用解析 6 个种子中抓取 5 个页面/附件，原始结构化 34 条，均来自同济大学口腔医学院。通用解析只识别人名，本批新增 `scripts/curate_batch211_more_remaining_promising_pages.py` 和 `tests/test_curate_batch211_more_remaining_promising_pages.py`，按 HTML 表格保留 `学硕/专硕`、复试总分、`拟录取` 状态和退伍军人备注，最终保留 34 条人员级记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：224,059 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：224,059 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：372 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：229,769 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：229,769 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：524 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，326 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 229,770 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch211 清洗记录 34 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages tests.test_curate_batch211_more_remaining_promising_pages`：300 tests OK。

## 2026-05-28 追加进展：batch210 贵师大/长春中医/内蒙古农大官网名单入库

batch210 继续从剩余覆盖缺口中筛选可实时复现的官网源。贵州师范大学教务处 2026 年推免生拟推荐名单 XLSX 可直接下载；长春中医药大学研究生院 2026 年接收推免生拟录取公示页内嵌 PDF 可直接下载；内蒙古农业大学动物科学学院 2026 届推免名单嵌在官网 JPEG 图片中，已下载官方图片并逐行转写核对。云南民族大学实时返回 HTTP 521，甘肃农业大学种子页返回 404，沈阳化工大学附件进入验证码下载桥页，河北农业大学栏目当前只命中硕博连读/硕士非推免页面，均留证不入库。

通用爬虫 7 个种子中抓取 11 个页面/附件，原始结构化 566 条。复核发现贵州师范大学附件中只有 Sheet1 的 209 行 `拟推荐` 可入库，19 行 `候补` 与两个无推荐状态的附加 sheet 不并入；长春中医药大学 PDF 末尾直博生方向跨行导致通用解析出现 3 条错位姓名；内蒙古农业大学页面正文未含表格文本，需要以官方 JPEG 为来源转写。本批新增 `scripts/curate_batch210_remaining_promising_pages.py` 和 `tests/test_curate_batch210_remaining_promising_pages.py`，最终保留 301 条人员级记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：224,025 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：224,025 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：371 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：229,735 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：229,735 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：523 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，325 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 229,736 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch210 清洗记录 301 条，空姓名 0，需复核 0，重复关键记录 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/候补` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages tests.test_curate_batch210_remaining_promising_pages`：299 tests OK。

## 2026-05-27 追加进展：batch209 黑龙江/重庆/武汉官网名单入库

batch209 从剩余覆盖缺口中继续筛选可实时复现的官网名单页和直链 PDF。黑龙江大学 2026 年硕士研究生拟录取公示页可展开官方 PDF 附件；重庆师范大学教务处 PDF 直链可下载，包含普通类、农村硕士计划和研究生支教团三个推免公示名单；武汉纺织大学服装学院、武汉体育学院竞技体育学院 HTML 表格可直接解析。山东理工大学页面可访问但未暴露静态名单附件，天津科技大学外国语学院页面实时返回 302，均留证不入库。

通用爬虫 6 个种子中抓取 10 个页面/附件，原始结构化 157 条。复核发现黑龙江大学 PDF 大表错位且漏掉部分 `免试/推免生` 行，武汉纺织大学候补表混入记录，武汉体育学院自动跟进实施细则页产生赛事评分表噪声。本批新增 `scripts/curate_batch209_remaining_promising_pages.py` 和 `tests/test_curate_batch209_remaining_promising_pages.py`，按 PDF/HTML 表结构重新清洗，最终保留 547 条人员级记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：223,724 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：223,724 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：368 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：229,434 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：229,434 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：520 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，322 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 229,435 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch209 清洗记录 547 条，空姓名 0，需复核 0，重复关键记录 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages tests.test_curate_batch209_remaining_promising_pages`：296 tests OK。

## 2026-05-27 追加进展：batch208-batch208b 政法/浙江上海缺口源复核与杭州师范入库

batch208 继续从剩余缺口中复核中央民族大学、中国音乐学院、中国药科大学、中国政法大学、华东政法大学和中国人民大学等官网入口。中央民族大学搜索索引页可见 21 个 XLSX 附件，但详情页实时返回 404，附件直链进入“请输入验证码下载附件”桥页；中国音乐学院和中国人民大学页面实时返回 404，中国药科大学返回 410；中国政法大学页面只返回站点提示页，华东政法大学页面只保留“公示期已结束”文字且无静态名单附件，均不入库。

batch208b 改抓上海理工大学、杭州师范大学和浙江农林大学等浙江/上海缺口源。上海理工大学两个搜索命中的拟录取页实时返回站点提示页，浙江农林大学茶学学院页面返回 404；杭州师范大学临床医学院（口腔医学院）2026 年临床医学专业学位硕士研究生招生拟录取名单（推免生）附件可直接下载，通用解析形成 2 条人员级记录。由于通用解析把附件日期误判为 2025 年，并将推免名单映射到普通拟录取路径，本批新增 `scripts/curate_batch208b_zhejiang_shanghai_pages.py` 和 `tests/test_curate_batch208b_zhejiang_shanghai_pages.py`，专项修正年份、路径和录取专业字段。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：223,177 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：223,177 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：364 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：228,887 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：228,887 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：516 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，318 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 228,888 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch208b 清洗记录 2 条，空姓名 0，需复核 0，重复关键记录 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources tests.test_curate_batch208b_zhejiang_shanghai_pages`：293 tests OK。

## 2026-05-27 追加进展：batch207 西安石油大学校级推免拟录取 PDF 入库

batch207 继续从覆盖缺口中筛选可实时复现的官网名单入口，种子覆盖东北电力大学、西安石油大学、南京理工大学和浙江中医药大学。西安石油大学研究生招生信息网校级推免拟录取公告可访问，并可直接下载 `2026年推免生拟录取名单.pdf`；东北电力大学详情页实时返回 404，南京理工大学详情页实时返回 410，浙江中医药大学详情页实时返回 412，均留证不入库。

本批通用爬虫 6 个种子中写入 4 个文档，原始结构化 18 条：经济管理学院 9 月拟接收表 12 条，校级 PDF 直博生 6 条。复核 PDF 文本层后确认校级 10 月正式名单实际包含 54 条人员级记录，通用解析遗漏了非直博普通推免行。因此新增 `scripts/curate_batch207_promising_remaining_sources.py` 和 `tests/test_curate_batch207_promising_remaining_sources.py`，专项解析校级 PDF。经济管理学院拟接收表和化学化工学院无表格页面仅保留原始抓取证据；合并时只采用校级最终 PDF，避免把未出现在校级最终名单中的学院预接收人员计入毕业出路结果。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：223,175 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：223,175 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：363 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：228,885 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：228,885 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：515 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，317 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 228,886 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch207 清洗记录 54 条，空姓名 0，需复核 0，重复关键记录 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources tests.test_curate_batch207_promising_remaining_sources`：291 tests OK。

## 2026-05-27 追加进展：batch206 艺术/音乐院校官网名单入库

batch206 继续从 118 所覆盖缺口中筛选艺术、音乐类官网源。鲁迅美术学院硕士拟录取附件为官方 XLSX，可直接下载；中国美术学院 2026 年港澳台硕士博士拟录取 HTML 可直接解析；四川音乐学院 2026 年推免拟推荐名单 PDF 可直接下载，但 PDF 文本折行严重；集美大学美术与设计学院官方 XLSX 同时包含正选和备选名单。四川美术学院两个名单附件进入验证码下载桥，山东艺术学院列表未暴露人员级名单，中国美术学院推免旧 URL 实时返回 404，均留证不入库。

本批通用爬虫原始形成 395 条记录，其中川音只抽到 9 条且混入页内噪声，四川美院混入公众号名称，国美成绩错位到 `major` 字段。本批新增 `scripts/curate_batch206_art_music_sources.py` 和 `tests/test_curate_batch206_art_music_sources.py`，专项重组鲁美 XLSX、国美 HTML、川音 PDF 和集美 XLSX，最终保留 433 条干净记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：223,121 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：223,121 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：362 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：228,831 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：228,831 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：514 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，316 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 228,832 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch206 清洗记录 433 条，空姓名 0，需复核 0，重复关键记录 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources tests.test_curate_batch206_art_music_sources`：288 tests OK。

## 2026-05-27 追加进展：batch204-batch205 艺术院校官网名单入库

batch204 继续从缺口院校中筛选高概率官网页面。中国政法大学页面返回动态挑战脚本；中央民族大学推免/硕士公示搜索索引存在，但实时请求返回 404；华东师范大学旧系统页实时返回 404；北京协和医学院推免公告可访问，但公开结果页当前已切换为 2027 空表，统考/港澳台 PDF 附件进入“请输入验证码下载附件”桥页，自动化不绕过验证码。本批保留原始页面、失败日志和留证下载页，不并入人员级主表。

batch205 转向可实时复现的艺术院校静态源。中央美术学院官网两个 PDF 可直接下载，西安美术学院招生信息网 HTML 表格可直接解析。通用爬虫原始抽取 788 条，但中央美术学院 PDF 重复页表头被当作姓名；本批新增 `scripts/curate_batch205_art_school_sources.py` 和 `tests/test_curate_batch205_art_school_sources.py`，按 PDF 行结构和 HTML 表格重新清洗，最终保留 776 条干净记录。

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
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch204_promising_official_pages/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260527_batch204_promising_official_pages/graduate_outcome_failures.jsonl`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch205_art_school_sources.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources/`
- `scripts/curate_batch205_art_school_sources.py`
- `tests/test_curate_batch205_art_school_sources.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：222,688 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：222,688 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：358 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：228,398 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：228,398 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：510 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，312 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 228,399 行（含表头），公式单元格 0，公式错误 0。
- 本批 batch205 清洗记录 776 条，空姓名 0，需复核 0，重复关键记录 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs tests.test_curate_batch178_ynu tests.test_curate_batch179_zjgsu tests.test_curate_batch181_njupt tests.test_curate_batch183_cug tests.test_curate_batch184_uestc tests.test_curate_batch190_swust tests.test_curate_batch192_sicnu tests.test_curate_batch197_wmu tests.test_curate_batch199_promising_pages tests.test_curate_batch202_sdutcm_doctor_pdf tests.test_curate_batch203_ecust_image_ocr tests.test_curate_batch205_art_school_sources`：284 tests OK。

## 2026-05-27 追加进展：batch203 华东理工大学图片名单 OCR 入库

batch203 复核上海理工大学、东北师范大学、华东理工大学、上海体育大学等覆盖缺口。上海理工大学若干页面和华东理工大学旧博士/专项页面返回“提示信息”；东北师范大学公示页可访问，但链接到校内查询系统，实时返回“录取名单尚未公布”，未绕过动态系统；上海体育大学页面返回脚本拦截内容，未形成静态名单。

华东理工大学 2026 年硕士研究生拟录取名单公示页可访问，名单主体为 74 张内嵌 JPG 图片。此前因无 OCR 链路未入库，本批新增 `scripts/curate_batch203_ecust_image_ocr.py` 和 `tests/test_curate_batch203_ecust_image_ocr.py`，使用 Windows 本机 `zh-Hans-CN` OCR 输出词坐标，再按列坐标重组人员级记录；同时修复 `0817Z3` 字母专业代码和 `0805m` 这类 OCR 将 `00` 识别成 `m` 的常见问题。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 华东理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,676 | 161 |

可追溯来源：
- 华东理工大学 2026 年硕士研究生拟录取名单公示页：`https://gschool.ecust.edu.cn/2026/0506/c12750a190107/page.htm`
- 内嵌名单图片：`https://gschool.ecust.edu.cn/_upload/article/images/60/9d/10a1fa174adea027add09da0ffa2/...jpg`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch203_search_refresh_pages.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages/ecust_images/`
- `scripts/curate_batch203_ecust_image_ocr.py`
- `tests/test_curate_batch203_ecust_image_ocr.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch203_search_refresh_pages_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：221,912 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：221,912 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：355 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：227,622 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：227,622 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：507 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，310 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 227,623 行（含表头），公式单元格 0，公式错误 0。
- 本批华东理工大学 OCR 清洗记录 2,676 条，空姓名 36，需复核 161，准考证号长度异常 0，重复准考证号 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加进展：batch200-batch202 山东中医药大学博士拟录取与多校留证

batch200 继续尝试缺口院校详情页，batch201 验证剩余直接附件候选。山东农业大学返回 403；西安外国语大学、沈阳航空航天大学、桂林医科大学、贵州师范大学、聊城大学等旧页返回 404；南京理工大学、中国药科大学页面返回 410；重庆邮电大学返回 412；天津科技大学直接 PDF 仍为 302；重庆师范大学旧 PDF 继续返回 404。沈阳师范大学和西安电子科技大学页面可访问，但附件已变成“公示期已结束”文字，HTML 不暴露可下载 URL，未入库。

batch202 通过网页搜索补充山东中医药大学 2026 年全日制博士研究生第一批次拟录取名单官方 PDF。PDF 文本层清晰，但通用解析未覆盖该博士表格格式；本批新增 `scripts/curate_batch202_sdutcm_doctor_pdf.py` 和 `tests/test_curate_batch202_sdutcm_doctor_pdf.py`，按报名号、学院、姓名、报考专业代码/名称、材料综合成绩、综合考核成绩和总成绩抽取。

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
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch202_sdutcm_doctor_pdf/`
- `scripts/curate_batch202_sdutcm_doctor_pdf.py`
- `tests/test_curate_batch202_sdutcm_doctor_pdf.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch202_sdutcm_doctor_pdf_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：219,236 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：219,236 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：354 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：224,946 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：224,946 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：506 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，309 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 224,947 行（含表头），公式单元格 0，公式错误 0。
- 本批山东中医药大学清洗记录 133 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加进展：batch199 山西财经等四校硕士拟录取

batch199 从当前覆盖缺口中选取 20 个研究生院具体公示页继续抓取。山西财经大学、佳木斯大学、哈尔滨商业大学、青海民族大学的拟录取公示页可展开官方附件并形成可用人员级记录；哈尔滨商业大学 PDF 通用解析混入重复页码和标题行，本批新增 `scripts/curate_batch199_promising_pages.py` 和 `tests/test_curate_batch199_promising_pages.py`，剔除 39 条页眉页脚噪声。

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
- 三峡大学 `https://graduate.ctgu.edu.cn/info/1064/7058.htm` 连接被远端重置。
- 东北电力大学、北方民族大学、广东药科大学、天津财经大学、河北农业大学、皖南医学院、重庆交通大学、武汉体育学院等旧公示页实时返回 404。
- 中国医科大学 `https://graduate.cmu.edu.cn/zsxc/info/1014/2123.htm` 和 `https://graduate.cmu.edu.cn/zsxc/info/1014/2125.htm` 返回 502。
- 华北理工大学公示页可访问但未形成名单记录。

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch199_promising_pages.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch199_promising_pages/`
- `scripts/curate_batch199_promising_pages.py`
- `tests/test_curate_batch199_promising_pages.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch199_promising_pages_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：219,103 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：219,103 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：353 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：224,813 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：224,813 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：505 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，308 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 224,814 行（含表头），公式单元格 0，公式错误 0。
- 本批清洗记录 2,956 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加进展：batch193-batch198 多校源复核与温州医科大学硕士拟录取

batch193-batch198 继续从缺口院校中优先尝试具体公示页和直接 PDF。南京财经大学一志愿/调剂/推免页面可访问，但附件下载进入验证码桥或页面未暴露真实附件 URL；山东理工大学硕士拟录取页面未暴露名单附件，推免 PDF 仅能抽出水印文本；上海科技大学旧公示页返回 410；batch196 中北京电影学院返回 412，北京服装学院和华侨大学跳转 404，杭州师范大学、江汉大学、三峡大学旧 URL 404，中国医科大学因旧式 SSL 协商失败未抓取；大连外国语大学名单附件进入验证码桥；华东政法大学页面只保留附件文件名，无实际 href。batch198 尝试中国药科大学 2024/2025 直接 PDF，实时均返回 404。

batch197 的温州医科大学 2025 年第一批、第二批硕士拟录取 PDF 可直接访问。通用解析能读出文本但会把表头“号后五/位”、页脚水印和断行姓名混入记录；本批新增 `scripts/curate_batch197_wmu.py` 和 `tests/test_curate_batch197_wmu.py`，使用 PDF 文本行结构重新抽取人员级字段，并补齐带字母专业代码（如 `1001Z2`、`1204Z1`）和断行少数民族姓名。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 温州医科大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,309 | 0 |

可追溯来源：
- 温州医科大学 2025 年硕士研究生第一批拟录取名单 PDF：`https://yjsy.wmu.edu.cn/__local/7/37/B7/FE9C98AACCA77F365E9E1FFEF3E_3CC368F6_D989A.pdf`
- 温州医科大学 2025 年硕士研究生第二批拟录取名单 PDF：`https://yjsy.wmu.edu.cn/__local/1/19/A9/D49C9A4BC1536107F46B238B538_C5F6557A_9AED5.pdf`
- 南京财经大学验证码留证页：`https://yjsc.nufe.edu.cn/info/1012/6891.htm`
- 山东理工大学硕士拟录取留证页：`https://yjsh.sdut.edu.cn/2026/0402/c5153a561202/page.htm`
- 上海科技大学 410 留证页：`https://yanzhao.shanghaitech.edu.cn/2026/0421/c9737a1120984/page.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch193_nufe.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch194_sdut.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch195_shanghaitech.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch196_multi_promising.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch197_direct_pdfs.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch198_cpu_direct_pdfs.csv`
- `scripts/curate_batch197_wmu.py`
- `tests/test_curate_batch197_wmu.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch197_wmu_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：216,147 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：216,147 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：349 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：221,857 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：221,857 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：501 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，304 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 221,858 行（含表头），公式单元格 0，公式错误 0。
- 本批温州医科大学清洗记录 2,309 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试/复试不合格` 残留 0。

## 2026-05-27 追加进展：batch191/batch192 重庆师范留证与四川师范大学硕士拟录取

batch191 先尝试重庆师范大学官网中搜索索引命中的 2025/2026 拟录取 PDF 和页面，但实时请求均返回 404，保留种子和失败日志，不入库。batch192 转向四川师范大学研究生院招生新闻栏目，2026 年硕士研究生第一、第二、第三批拟录取名单公示页面均可访问，并能展开 PDF 附件。第一、第二批 PDF 由通用解析形成稳定人员级记录；第三批 PDF 只抽出 1 条分数错位噪声，本批新增 `scripts/curate_batch192_sicnu.py` 和 `tests/test_curate_batch192_sicnu.py` 进行批次过滤。

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

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch191_cqnu.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch192_sicnu.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch192_sicnu/`
- `scripts/curate_batch192_sicnu.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch192_sicnu_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：213,838 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：213,838 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：348 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：219,548 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：219,548 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：500 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，303 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 219,549 行（含表头），公式单元格 0，公式错误 0。
- 本批四川师范大学清洗记录 1,033 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试` 残留 0。

## 2026-05-27 追加进展：batch190 西南科技大学硕士与推免拟录取

batch190 先复核中国海洋大学、中国石油大学（华东）、天津科技大学、五邑大学和青岛理工大学等缺口院校。中国海洋大学官网页当前仅有“附件：名单（公示已结束）”文字，无附件 URL；中国石油大学（华东）PDF 为扫描图像，当前环境无 OCR；天津科技大学实时请求为 302 自循环；五邑大学实时返回 404；青岛理工大学附件入口进入验证码下载桥，均未入库。随后转向西南科技大学研究生招生网，其 2026 年硕士拟录取公示页可展开官方 PDF，推免/直博拟录取公示页为 HTML 表格。本批新增 `scripts/curate_batch190_swust.py` 和 `tests/test_curate_batch190_swust.py`，重新按 PDF 文本行结构抽取人员级字段，并丢弃页脚口号与重复表头。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,237 | 0 |
| 西南科技大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 37 | 0 |

可追溯来源：
- 西南科技大学 2026 年拟录取硕士研究生名单公示页：`https://gs.swust.edu.cn/zs/2026/0506/c7797a236234/page.htm`
- 西南科技大学 2026 年拟录取硕士研究生名单 PDF：`https://gs.swust.edu.cn/_upload/article/files/c5/a8/47903d32491cbaedf86ee1dad05e/e8a0424a-f45b-448c-9f79-270eeb383e7a.pdf`
- 西南科技大学 2026 年研究生（直博生、推免生）拟录取名单公示页：`https://gs.swust.edu.cn/zs/2024/1012/c7797a206495/page.htm`

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch190_swust.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch190_swust/`
- `scripts/curate_batch190_swust.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch190_swust_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：212,805 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：212,805 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：347 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：218,515 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：218,515 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：499 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，302 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 218,516 行（含表头），公式单元格 0，公式错误 0。
- 本批专项清洗记录 2,274 条，空姓名 0，需复核 0，`不予录取/拟不录取/放弃复试` 残留 0。

## 2026-05-27 追加进展：batch180/batch180b 华东师范留证与南京师范大学外国语学院

batch180 验证华东师范大学 2026 年硕士研究生拟录取名单公示页。页面可访问，但当前仅保留“公示已结束”的附件文字，HTML 中未暴露可下载名单链接，暂不入库。batch180b 转向南京师范大学外国语学院官网，硕士拟录取和博士拟录取页面均可直接展开官方 PDF，通用 PDF 表格解析形成可用记录。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：210,677 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：210,677 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：342 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：216,387 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：216,387 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：494 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，298 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 216,388 行（含表头），公式单元格 0，公式错误 0。
- 本批南京师范大学清洗记录 177 条，空姓名 0，需复核 0，重复 0，`不予录取/拟不录取` 残留 0。

## 2026-05-27 追加进展：batch179 浙江工商大学博士拟录取 PDF 专项清洗

batch179 抓取浙江工商大学研究生招生信息网 2026 年硕士一志愿、调剂和博士“申请-考核”制拟录取公示入口。硕士一志愿和调剂页面当前实时返回 410，未入库；博士页面可直接展开两份官方 PDF。通用解析未覆盖该 PDF 表格版式，本批新增 `scripts/curate_batch179_zjgsu.py` 和 `tests/test_curate_batch179_zjgsu.py`，按完整行字段抽取博士拟录取人员。

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
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch179_zjgsu/`
- `scripts/curate_batch179_zjgsu.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch179_zjgsu_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：210,500 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：210,500 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：341 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：216,210 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：216,210 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：493 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，297 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 216,211 行（含表头），公式单元格 0，公式错误 0。
- 本批专项清洗记录 143 条，空姓名 0，需复核 0，重复 0，`不予录取/拟不录取` 残留 0。

## 2026-05-27 追加进展：batch178 云南大学博士拟录取 PDF 专项清洗

batch178 抓取云南大学西南联合研究生院官方公示页和 PDF 附件，覆盖 2026 年博士研究生“申请-考核”制第一批次拟录取名单，以及 2026 年硕博连读拟录取名单。通用清洗只保留 30 条且存在“研究方向/专业名误入姓名”的错位，本批新增 `scripts/curate_batch178_ynu.py` 和 `tests/test_curate_batch178_ynu.py`，按 PDF 文本完整行严格抽取人员级字段。

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
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch178_ynu/`
- `scripts/curate_batch178_ynu.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch178_ynu_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：210,357 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：210,357 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：340 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：216,067 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：216,067 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：492 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，296 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 216,068 行（含表头），公式单元格 0，公式错误 0。
- 本批专项清洗记录 452 条，空姓名 0，需复核 0，`不予录取/拟不录取` 残留 0。

## 2026-05-27 追加进展：batch177/batch177b 内蒙古大学与山东师范大学

batch177 先验证内蒙古大学研究生院 2026 年硕士一志愿、调剂、港澳台和博士拟录取入口。实时抓取确认，硕士一志愿/调剂/港澳台页面当前返回 404，且页面所列硕士附件下载桥需要验证码，未并入；博士第一批次拟录取公示页为 HTML 表格，形成可用人员级记录。batch177b 随后追加山东师范大学多个学院博士拟录取公示页，最终通用解析稳定抽出物理与光电学院、新闻与传媒学院、经济学院三类 HTML 公示记录。

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
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch177_imu.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch177b_imu_sdnu.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch177_imu/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch177b_imu_sdnu/records_clean.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：209,905 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：209,905 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：339 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：215,615 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：215,615 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：491 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，295 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 215,616 行（含表头），公式单元格 0，公式错误 0。
- 本批清洗记录 282 条，空姓名 0，需复核 0，`不予录取/拟不录取` 残留 0。

## 2026-05-27 追加进展：batch176 石河子大学 PDF/HTML 严格清洗

batch176 回到此前搜索命中的石河子大学官网入口，先抓取信息科学与技术学院、法学院、外国语学院、理学院、药学院和能材学院页面，再展开可直接访问的内嵌 PDF。通用解析能从部分表格中抽出人员行，但会把“拟不录取/不予录取”行一并保留；本批新增 `scripts/curate_batch176_shzu_pdfs.py` 和 `tests/test_curate_batch176_shzu_pdfs.py`，按行级录取意见严格筛选：PDF 行文本必须明确包含“拟录取”且不含“拟不录取/不予录取”，HTML 表格必须由“学院意见”列给出“拟录取”。

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

排除说明：
- 外国语学院另一份第二批调剂 PDF 的 5 行均为“不予录取”，未入库。
- 药学院第一轮调剂 PDF 当前无可抽取文本层，保留原始文件但不强行 OCR 入库。
- 理学院、能材学院入口实时返回提示页，未形成可解析名单。

产物：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch176_shzu.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch176b_shzu_pdfs.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch176_shzu/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch176b_shzu_pdfs/`
- `scripts/curate_batch176_shzu_pdfs.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch176_shzu_curated/records_clean_curated.csv`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：209,623 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：209,623 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：337 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：215,333 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：215,333 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：489 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，293 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 215,334 行（含表头），公式单元格 0，公式错误 0。
- `python -m unittest tests.test_graduate_outcome_crawler tests.test_curate_batch176_shzu_pdfs`：241 tests OK（仅保留既有 ResourceWarning）。

## 2026-05-27 追加进展：batch175 新疆财经大学与黑龙江中医药大学

batch175 先复核搜索索引中的中国海洋大学、中国药科大学等旧 PDF 直链，实时官网请求已返回 404，未入库。随后改用可实时下载的新疆财经大学官网 PDF，并回扫此前已下载但通用解析错位的黑龙江中医药大学推免 PDF。黑龙江中医药大学 PDF 表格有清晰文本层，本批新增 `scripts/curate_batch175_hljucm_pdf.py`，按 `序号、拟录取类别、姓名、性别、拟录取院系、拟录取专业代码、学位类型、拟录取专业、毕业学校、毕业院系、毕业专业、复试成绩、指导教师、备注` 结构重抽字段。

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

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：209,532 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：209,532 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：336 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：215,242 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：215,242 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：488 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，292 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 215,243 行（含表头），公式单元格 0，公式错误 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。

## 2026-05-26 追加进展：batch174 青海大学 XLS 补解析

batch174 处理此前已下载但通用解析器未能读取的青海大学官方 `.xls` 文件。由于运行环境缺少 `xlrd`，本批使用本机 Excel COM 后台读取工作簿，并新增 `scripts/curate_batch174_qhu_xls_with_excel.py` 生成批次级 curated 清洗结果。原表共 1,273 行，其中首行为标题、第二行为表头，后续 1,271 行为人员级记录。

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 青海大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,271 | 0 |

可追溯来源：
- 青海大学 2025 年硕士研究生招生拟录取名单（一志愿考生）XLS：`https://yjs.qhu.edu.cn/docs/2025-04/615da678d8de4fbd974bea45ae6cfaa5.xls`

产物：
- `scripts/curate_batch174_qhu_xls_with_excel.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch174_qhu_xls_curated/records_clean_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch174_qhu_xls_curated/school_year_summary_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch174_qhu_xls_curated/curation_notes.txt`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：208,858 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：208,858 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：333 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：214,568 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：214,568 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：485 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，290 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 214,569 行（含表头），公式单元格 0，公式错误 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。

## 2026-05-26 追加进展：batch173 既有原始文件补解析

batch173 回扫此前批次已下载、但通用解析器未能结构化的官方原始文件。优先选择文本层可抽取且字段稳定的 PDF：西安交通大学医学部 2026 年硕士研究生拟录取名单、中山大学智能工程学院 2026 届推免拟推荐名单、长安大学能电学院 2026 届推免拟推荐及递补拟推荐名单。本批新增 `scripts/curate_batch173_existing_raw.py` 作为批次级补解析脚本，不改主爬虫规则。

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

产物：
- `scripts/curate_batch173_existing_raw.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch173_existing_raw_curated/records_clean_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch173_existing_raw_curated/school_year_summary_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch173_existing_raw_curated/curation_notes.txt`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：207,587 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：207,587 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：332 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：213,297 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：213,297 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：484 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，289 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 213,298 行（含表头），公式单元格 0，公式错误 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。

## 2026-05-26 追加进展：batch172/batch172b 长春理工大学

batch172 初始使用实时检索命中的官方入口继续补覆盖缺口，种子覆盖长安大学、石河子大学、新疆财经大学、长春理工大学、天津科技大学、太原科技大学、浙江工商大学、皖南医学院、重庆邮电大学、温州医科大学、云南中医药大学和浙江中医药大学等。轻量探测后发现，长安大学入口连接超时，天津科技大学入口重定向循环，太原科技大学超时，浙江工商大学返回 403，皖南医学院候选页 404，重庆邮电大学/温州医科大学/云南中医药大学/浙江中医药大学为 412、483 或 502。为避免批量进程被慢站点拖住，batch172b 仅保留石河子大学、新疆财经大学和长春理工大学 3 个响应稳定入口。

batch172b 实际抓取 26 个页面/附件，原始结构化 1,855 条，通用清洗 1,033 条。质检后确认新疆财经大学命中的原始记录主要来自“进入复试名单”“复试分数线”“学费标准”等非拟录取名单，保留证据但不合并。长春理工大学 6 个 PDF 标题均为“拟录取/录取名单”，但 PDF 表格将“全日制”读入姓名列，真实姓名位于 `admission_major` 字段末尾；本批额外生成 `records_clean_curated.csv`，按 `专业代码 专业名 方向代码 姓名` 结构校正姓名和录取专业字段，最终保留 534 条人员级记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch172.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch172b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch172b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch172b/records_clean_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch172b/school_year_summary_curated.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch172b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch172b/`

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

质量说明：
- 长春理工大学记录具备姓名、考生编号和录取专业；缺失本科来源学校，因此统一带 `missing_undergraduate_school` 质量标记。
- 石河子大学入口实时返回“提示信息”，未暴露可解析人员名单。
- 新疆财经大学抓到的 PDF 不属于拟录取名单，未合并。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：207,071 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：207,071 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：329 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：212,781 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：212,781 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：481 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，286 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 212,782 行（含表头），公式单元格 0，公式错误 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。

## 2026-05-26 追加进展：batch171 华中师范/沈阳音乐/新疆师范

batch171 继续从覆盖缺口中筛选“能打开官方原文、且可跟到正文表格或附件”的入口，覆盖北方民族大学、佳木斯大学、首都师范大学、武汉体育学院、沈阳音乐学院、华中师范大学、华东师范大学、新疆师范大学和上海理工大学等。实际抓取 36 个页面/附件，原始结构化 4,157 条，通用清洗 3,990 条。

本批额外生成 `records_clean_curated.csv`：华中师范大学附件标题仅写学院代码和学院名，通用年份识别会把 `001/002/015/017` 等代码误落成 2000/2002/2015/2017；沈阳音乐学院 PDF 标题明确为 2026，但入口页年份识别落成 2025。按父级公示页和附件标题复核后统一校正为 2026 年，并重新走既有去重/过滤规则，最终保留 3,990 条人员级记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch171.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch171/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch171/records_clean_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch171/school_year_summary_curated.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch171/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch171/`

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
- 三个入库来源均为硕士研究生拟录取人员级名单，记录具备姓名和考生编号；缺失本科来源学校，因此统一带 `missing_undergraduate_school` 质量标记。
- 北方民族大学候选页实时 404；佳木斯大学、武汉体育学院、上海理工大学候选页实时 502；首都师范大学入口跳转后未暴露可解析名单；华东师范大学页面显示公示已结束且无人员级明细，均未合并。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：206,537 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：206,537 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：328 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：212,247 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：212,247 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：480 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，285 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 212,248 行（含表头），公式单元格 0，公式错误 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 tests OK（仅保留既有 ResourceWarning）。

## 2026-05-26 追加进展：batch170 华东交通/山西农业等

batch170 继续从覆盖缺口中筛选能直接抓取正文表格或附件的官网来源，覆盖华东交通大学、内蒙古工业大学、内蒙古农业大学、山西农业大学、陕西师范大学、景德镇陶瓷大学和暨南大学等。实际抓取 47 个页面/附件，原始结构化 4,072 条，通用清洗 2,502 条。

本批额外生成 `records_clean_curated.csv`：剔除华东交通大学正文页导航误抽、PDF 表头行、内蒙古工大“名次”表头、陕西师大“主动放弃”行，并从华东交通大学附件标题补回专业代码/专业名。最终保留 2,480 条人员级记录，丢弃 22 条噪声/无效行。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch170.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch170/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch170/records_clean_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch170/school_year_summary_curated.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch170/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch170/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 内蒙古工业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 23 | 0 |
| 华东交通大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 264 | 49 |
| 山西农业大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,764 | 0 |
| 山西农业大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 2 | 0 |
| 山西农业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 287 | 0 |
| 山西农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 41 | 0 |
| 景德镇陶瓷大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 81 | 0 |
| 陕西师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 18 | 0 |

可追溯来源：
- 华东交通大学人文社会科学学院 2026 年硕士研究生拟录取名单：`https://rwxy.ecjtu.edu.cn/info/1064/6084.htm`
- 华东交通大学电气与自动化工程学院 2026 年硕士研究生拟录取名单：`https://dqxy.ecjtu.edu.cn/info/1090/12192.htm`
- 华东交通大学体育与健康学院入口：`https://phe.ecjtu.edu.cn/`
- 山西农业大学研究生院招生工作栏目：`https://grs.sxau.edu.cn/zsgz.htm`
- 山西农业大学草业学院研究生教育栏目：`https://cyxy.sxau.edu.cn/jyjx/yjsjy.htm`
- 陕西师范大学美术学院 2026 年推免拟推荐名单：`https://meishuxy.snnu.edu.cn/info/1013/6445.htm`
- 景德镇陶瓷大学 2026 年推荐免试硕士研究生拟录取名单：`https://zs.jci.edu.cn/info/1006/2211.htm`
- 景德镇陶瓷大学信息工程学院 2026 年推免拟推荐名单：`https://xxgc.jci.edu.cn/info/1044/4978.htm`

质量说明：
- 华东交通大学体育与健康学院 49 条记录没有稳定专业字段，保留为 `needs_review=true`。
- 暨南大学 PDF 直链当前返回 403，内蒙古农业大学和陕西师范大学数学学院入口实时 404，均未合并。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：202,547 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：202,547 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：325 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：208,257 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：208,257 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：477 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，282 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 208,258 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加进展：batch167/batch168/batch169 浙江财经等官网来源

batch167 先验证浙江财经大学 2026 年推免拟录取学院页。14 个入口中，数据科学学院和艺术学院两页可直接从 HTML 表格/页面摘要结构化，清洗 5 条；浙江财经大学其余学院旧入口实时 404，西安电子科技大学校级公示页只显示公示说明且未暴露人员名单，西安交通大学机械学院入口为浏览器挑战页，均暂不合并。

batch168 继续试探搜索命中的静态页和 PDF 直链，18 个入口只抓到 4 个提示页、404 跳转或非名单内容，清洗记录 0 条，作为留证批次保留。

batch169 改用“搜索摘要里能看到表头/样例行”的来源筛选策略，优先抓取正文表格和可直接下载的 PDF。16 个入口写入 14 个文档，原始结构化 863 条，清洗 842 条；与既有 B 类主表去重后净新增 556 条。连同 batch167，本轮合并净新增 561 条。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch167.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch168.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch169.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch167/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch169/records_clean.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch167/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch168/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch169/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch167/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch168/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch169/`

本轮清洗结果：

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

可追溯来源：
- 浙江财经大学数据科学学院 2026 年接收推荐免试硕士研究生拟录取名单：`https://ds.zufe.edu.cn/info/1237/14593.htm`
- 浙江财经大学艺术学院 2026 年接收推荐免试硕士研究生拟录取名单：`https://ys.zufe.edu.cn/info/1038/9492.htm`
- 四川大学建筑与环境学院 2026 年硕士研究生拟录取名单：`https://acem.scu.edu.cn/info/1003/13968.htm`
- 四川大学电子信息学院 2026 年硕士拟录取名单：`https://eie.scu.edu.cn/info/1025/14978.htm`
- 中国石油大学（北京）新能源与材料学院 2026 年接收推荐免试研究生拟录取名单：`https://www.cup.edu.cn/cnem/tzgg/6822e1949ee64c3da67c3b229f5c4909.htm`
- 湖南大学化学化工学院 2026 年推荐免试研究生名单：`https://cc.hnu.edu.cn/info/1102/12491.htm`
- 东北农业大学 2026 年拟录取免试攻读硕士研究生名单：`https://graduate.neau.edu.cn/info/1146/4239.htm`
- 上海交通大学设计学院 2026 年拟录取推荐免试研究生名单：`https://designschool.sjtu.edu.cn/dynamic/notice/detail/68f59251e8e233cad44211ec`
- 中央戏剧学院 2026 年接收推荐免试攻读硕士学位研究生拟录取名单 PDF：`https://chntheatre.edu.cn/Uploads/Cad/Picture/2025/10/13/001.%E4%B8%AD%E5%A4%AE%E6%88%8F%E5%89%A7%E5%AD%A6%E9%99%A2%202026%20%E5%B9%B4%E6%8E%A5%E6%94%B6%E6%8E%A8%E8%8D%90%E5%85%8D%E8%AF%95%E6%94%BB%E8%AF%BB%E7%A1%95%E5%A3%AB%E5%AD%A6%E4%BD%8D%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95%E5%85%AC%E7%A4%BA.20251013100734.pdf`

质量说明：
- batch167 清洗表 5 条，需人工复核 0。
- batch169 清洗表 842 条，需人工复核 2；这 2 条来自中国农业大学资源与环境学院 PDF，源文本只稳定暴露人员、考生编号和专业代码 `083000`，缺专业名，保留为低字段复核记录。
- batch169 合并时发现中央戏剧学院、天津理工大学、上海交通大学和东北农业大学部分来源已在主表中存在，已按人员级键去重，未重复计入。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：200,067 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：200,067 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：317 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：205,777 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：205,777 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：469 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，277 所已精确匹配官网记录

验证：
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 205,778 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加进展：batch166 上海中医药大学

batch164 继续从覆盖缺口中尝试杭州师范大学、上海理工大学、上海体育大学、温州医科大学和上海中医药大学。杭师入口实时 404，温州医科大学入口返回 483，上海理工大学返回“无效的文章参数”，上海体育大学页面为 JS 保护且未形成静态明细。上海中医药大学页面正文只显示公示说明，但 `meta description` 暴露名单前段摘要，因此 batch166 仅对该摘要片段中完整记录做结构化入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch165.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch166/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch166/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch166/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch166/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海中医药大学 | 2025 | incoming_recommendation_admission_list | recommendation_exemption | 11 | 0 |

可追溯来源：
- 上海中医药大学 2025 年推免硕士研究生拟录取名单公示：`https://yjsy.shutcm.edu.cn/2025/1013/c1143a169399/page.htm`

质量修正：
- 新增“推免硕士研究生拟录取/推免硕士研究生拟录取名单”分类关键词。
- 新增上海中医药大学 `meta description` 专项解析，保留学院代码/学院名称、专业代码/专业名称、复试成绩、推荐学校；备注字段标注 `source_fragment meta_description`，明确该来源为网页摘要片段。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：199,506 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：199,506 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：312 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：205,216 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：205,216 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：464 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，275 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 205,217 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加进展：batch163 厦门大学

batch162 从当前覆盖缺口中继续尝试大连外国语大学、青岛理工大学、电子科技大学、厦门大学、北京第二外国语学院等入口；可稳定结构化的是厦门大学两个学院 PDF。初跑时通用 PDF 表格解析只能抽取姓名、考生编号和分数，专业字段为空，177 条全部需要复核；batch163 新增厦门大学分段专业表解析后重新跑干净目录，专业字段全部补齐。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch162.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch163/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch163/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch163/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch163/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 厦门大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 177 | 0 |

可追溯来源：
- 厦门大学材料学院 2026 年硕士研究生拟录取名单：`https://cm.xmu.edu.cn/info/1271/25755.htm`
- 厦门大学环境与生态学院/海洋与海岸带发展研究院 2026 年硕士研究生拟录取名单：`https://cee.xmu.edu.cn/info/1051/40415.htm`
- 大连外国语大学 2026 年推免生拟录取名单页面已留证，附件为验证码桥页，未入库：`https://gd.dlufl.edu.cn/info/1013/2921.htm`
- 青岛理工大学 2026 年硕士研究生拟录取名单页面已留证，页面未暴露静态附件，未入库：`https://yjsh.qut.edu.cn/info/1406/3291.htm`
- 电子科技大学信息与通信工程学院 2026 年推免生拟录取名单页面已留证，PDF 无文本层，未入库：`https://www.sice.uestc.edu.cn/info/1142/15723.htm`

质量修正：
- 新增厦门大学 PDF 专项解析，按“专业代码和专业名称”分段继承专业代码/名称，并抽取人员行中的初试总分、复试成绩、总成绩、学习方式和录取类别。
- batch163 清洗表 177 条；缺少人员姓名 0，缺少专业字段 0，需人工复核 0。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：199,495 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：199,495 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：311 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：205,205 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：205,205 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：463 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，274 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：236 个测试通过。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 205,206 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加进展：batch161 江西师范/广州美术/新疆农业/河北/宁波

batch161 先从 batch159 的 17 个候选入口中筛掉 404、验证码下载桥、无人员级表格和误抽风险较高的入口，只保留 5 个已验证可结构化的官方来源重跑到干净目录。沈阳师范大学页面正文能抽到的是工作组成员和联系方式，真实学生名单在图片里，当前不并入清洗表。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch160.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch161/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch161/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch161/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch161/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
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
- 广州美术学院 2026 年接收优秀应届毕业生免试攻读硕士学位研究生拟录取名单：`https://zs.gzarts.edu.cn/info/1038/4249.htm`
- 新疆农业大学 2026 年接收优秀应届本科毕业生免试攻读硕士研究生拟录取名单：`https://yjsc.xjau.edu.cn/2025/1017/c2155a110462/page.htm`
- 河北大学 2026 年拟录取推免研究生名单：`https://yjsy.hbu.edu.cn/info/1114/4087.htm`
- 宁波大学关于 2026 年拟接收推荐免试研究生的公示：`https://graduate.nbu.edu.cn/info/1073/25521.htm`

质量修正：
- 新增“推免拟录取/推免拟录取名单”关键词，修正宁波大学文档分类。
- 新增宁波大学 PDF 专项解析，按“姓名/性别/复试成绩/接收学院/接收专业代码/接收专业名称/录取类型”抽取，避免复试成绩误入学院字段。
- 新增江西师范大学推免资格和推免接收 PDF 专项解析，修正通用表格解析把专业名误当姓名的问题。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：199,318 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：199,318 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：310 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：205,028 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：205,028 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：462 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，273 所已精确匹配官网记录

验证：
- batch161 清洗表：1,629 条清洗记录，需人工复核 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：235 个测试通过。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`；Public_Records 205,029 行（含表头），公式单元格 0，公式错误 0。

## 2026-05-26 追加进展：batch158 海南医科大学

batch158 继续处理未覆盖院校。海南医科大学 2026 年接收推荐免试攻读硕士研究生复试考核成绩及拟录取名单页面可公开访问，附件为 VSB `download.jsp` xlsx。此前该入口会返回验证码桥页；本批修正 crawler 在跟进附件时传递父页面 Referer，并过滤“上一篇/下一篇”文章导航，最终只抓取目标公告和目标 xlsx 附件。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch158.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch158/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch158/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch158/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch158/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 海南医科大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 21 | 0 |

可追溯来源：
- 海南医科大学 2026 年接收推荐免试攻读硕士研究生复试考核成绩及拟录取名单（一）：`https://www.muhn.edu.cn/zsw/info/1091/10434.htm`
- xlsx 附件下载入口：`https://www.muhn.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1698349489&wbfileid=533C403A675D3C31AD5FBA3FACF6D8C0`

质量修正：
- 新增父页面 Referer 传递，支持 VSB `download.jsp` 直接返回 xlsx 附件。
- 新增推免拟录取 Excel 表专项解析，保留脱敏身份证号、报考学院、报考专业、学位类型、学习方式、复试成绩、录取状态。
- 新增“上一篇/下一篇”等导航链接过滤，避免相邻复试名单公告混入当前拟录取批次。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：197,689 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：197,689 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：301 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：203,399 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：203,399 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：453 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，268 所已精确匹配官网记录

验证：
- batch158 清洗表：21 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0。
- `python -m unittest tests.test_graduate_outcome_crawler`：231 个测试通过。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch130 西南大学学院页展开

batch130 继续处理未覆盖院校。西南大学、电子科技大学、中国海洋大学等官网存在全校拟录取名单总入口；其中西南大学和电子科技大学总入口均为跨学院子域名链接清单，当前爬虫不会自动跨域追踪，因此本批先将总入口中的学院链接展开为种子。最终可稳定入库记录来自西南大学外国语学院和音乐学院；电子科技大学多处页面/附件为下载桥或当前通用解析器未能直接抽取人员级表格，中国海洋大学直链 PDF 返回 403，暂不并入。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch130.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch130b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch130b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch130b/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch130b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch130b/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 129 | 0 |

可追溯来源：

- 西南大学 2026 年硕士研究生一志愿拟录取名单总入口：`https://yz.swu.edu.cn/info/1005/3492.htm`
- 西南大学外国语学院 2026 年硕士研究生拟录取名单：`http://foreign.swu.edu.cn/info/1005/7986.htm`
- 西南大学音乐学院 2026 年硕士研究生拟录取名单：`https://music.swu.edu.cn/info/1050/4305.htm`

质量修正：
- 将西南大学总入口中的跨学院链接展开为二级种子，解决同校不同学院子域名无法自动跟进的问题。
- 过滤“下载中心/主题教育/党务公开/位置导航/邮编/辅修”等导航或页脚字段，避免学院页面菜单被误当作人员姓名。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：172,176 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：172,176 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：279 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：177,886 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：177,886 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：431 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，250 所已精确匹配官网记录

验证：
- batch130b 清洗表：129 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，导航/页脚误抽 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch129 海南师范大学/福建中医药大学/福建医科大学/首都经济贸易大学

batch129 继续优先抓取可静态下载的官网名单页和 PDF 附件，种子覆盖东北师范大学、首都经济贸易大学、天津财经大学、海南师范大学、海南医科大学、福建医科大学和福建中医药大学。最终可入库记录来自海南师范大学、福建中医药大学、福建医科大学和首都经济贸易大学；海南医科大学附件当前返回下载桥页，天津财经大学其中一个入口返回 404，东北师范大学本轮入口未形成可解析人员级表格。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch129.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch129d/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch129d/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch129d/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch129d/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 海南师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,331 | 0 |
| 福建中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 868 | 0 |
| 福建医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 156 | 0 |
| 首都经济贸易大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 182 | 0 |

可追溯来源：

- 海南师范大学 2026 年普通招考博士研究生拟录取名单 PDF：`https://yjsc.hainnu.edu.cn/_upload/article/files/7f/63/6d5cda0e4308a31c33b58b9101d3/8617f23c-f8c9-4888-93a5-fb56074ca1cb.pdf`
- 海南师范大学 2026 年全国硕士研究生招生考试拟录取考生名单 PDF：`https://yjsc.hainnu.edu.cn/_upload/article/files/00/ca/d543640f40b880950eb3dfc8144e/69e862e5-0824-4cbc-aa7c-8480629d3cb9.pdf`
- 福建医科大学 2026 年推免生拟录取名单 PDF：`https://yjsy.fjmu.edu.cn/_upload/article/files/c5/cc/81c46394465685bac1e4c6f032ac/fd6f1b5d-be0a-4cbb-ad68-bf52ac51db03.pdf`
- 福建中医药大学 2026 年统考硕士复试录取公示名单 PDF：`https://yjsy.fjtcm.edu.cn/_upload/article/files/4c/19/7f491c3743d9bf30a442427ee1d2/3beb20c7-d01b-484e-bb15-9da01bafa336.pdf`
- 首都经济贸易大学 2026 年博士研究生拟录取名单第一批 PDF：`https://yjs.cueb.edu.cn/docs/2026-05/033170a1e92b49f59c19e6b6ba353642.pdf`
- 首都经济贸易大学 2026 年博士研究生拟录取名单第二批 PDF：`https://yjs.cueb.edu.cn/docs/2026-05/3d31449bc83c46da9f7714d17d359307.pdf`

质量修正：
- 新增海南师范大学硕士/博士拟录取 PDF 专项解析，识别“学院代码/专业代码/初试/复试/总成绩”等列。
- 新增福建医科大学推免拟录取 PDF 专项解析，修正学院代码、学院名称、专业代码、专业名称错位问题。
- 新增福建中医药大学统考硕士名单专项解析，处理“专业类型+专业代码+专业名称”合并、姓名与考生号合并、导师单位与成绩合并等 PDF 换行问题；该 PDF 中 304 条仅能可靠保留专业代码。
- 新增首都经济贸易大学博士拟录取 PDF 专项解析，处理学院/专业跨行拆分。
- 过滤海南医科大学页面中的“体重/肝功能/血常规”等体检项目，避免误当作人员姓名。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：172,047 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：172,047 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：278 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：177,757 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：177,757 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：430 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，249 所已精确匹配官网记录

验证：
- batch129d 清洗表：2,537 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，体检项目误抽 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch128 上海师范大学/安徽财经大学

batch128 继续从剩余未覆盖院校中筛选官方静态名单入口，种子覆盖南京师范大学、上海师范大学、安徽财经大学、北京第二外国语学院和南京邮电大学。上海师范大学数理学院主页可追到 2026 年硕士研究生调剂拟录取名单 PDF，安徽财经大学研究生招生信息网可追到 2026 年推免递补名单正文；南京师范大学附件下载为 HTML 下载桥或无可解析文本，南京邮电大学页面未暴露名单表，北二外栏目本轮未发现静态人员级名单，暂不并入。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch128.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch128e/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch128e/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch128e/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch128e/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 172 | 0 |
| 安徽财经大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 | 0 |

可追溯来源：

- 上海师范大学数理学院 2026 年硕士研究生调剂拟录取名单入口：`https://mathsc.shnu.edu.cn/f5/9e/c33037a849310/page.htm`
- 上海师范大学数理学院调剂拟录取名单 PDF：`https://mathsc.shnu.edu.cn/_upload/article/files/b8/4a/4cb367404b75b86b5cd7b8a2cd83/08806d8e-ad8c-4fbb-8646-47042a113f2d.pdf`
- 安徽财经大学会计学院 2026 年推免递补名单公示：`https://yz.aufe.edu.cn/2025/0918/c13923a238434/page.htm`
- 安徽财经大学金融学院 2026 年推免递补名单公示：`https://yz.aufe.edu.cn/2025/0916/c13923a238317/page.htm`

质量修正：
- 修复 PDF 表格中“考生编号 + 调剂专业名称”粘在同一列、下一列为“非定向就业”时的错位，避免就业方式误写入 `admission_major`。
- 新增安徽财经大学推免递补正文键值解析，将“姓名/专业名称/综合成绩”等行合成为人员级记录。
- 过滤“组长/副组长/成员/工作职责/特此通知”等推荐工作通知噪声，避免工作小组成员或正文尾句混入人员名单。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：169,510 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：169,510 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：274 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：175,220 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：175,220 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：426 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，245 所已精确匹配官网记录

验证：
- batch128e 清洗表：174 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，就业方式误入 `admission_major` 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch127 山东财经大学

batch127 继续从剩余未覆盖院校中筛选官方静态名单入口，种子覆盖厦门大学、华东理工大学、杭州师范大学、广东药科大学、山西财经大学、华北理工大学、山东财经大学、山东农业大学、河北大学等。华东理工大学名单主体为图片，山西财经大学和河北大学附件进入验证码下载桥，厦门大学、杭州师范大学、广东药科大学等入口实时返回 404，山东农业大学学院页返回 403 或章程页，未形成可结构化人员级记录；可入库来源集中在山东财经大学。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch127.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch127d/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch127d/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch127d/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch127d/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山东财经大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 6 | 0 |

可追溯来源：

- 山东财经大学研究生招生信息网：`https://yjszs.sdufe.edu.cn/index.htm`
- 山东财经大学 2026 年“硕博连读”、“申请考核”博士研究生拟录取名单公示（第二批）：`https://yjszs.sdufe.edu.cn/info/1034/2889.htm`
- 山东财经大学 VSB 内嵌 PDF：`https://yjszs.sdufe.edu.cn/virtual_attach_file.vsb?afc=TL7ntfUmG4U4v4njzQ2UzG8nN78U4Vw7o7lbnlWRnmv8oR90gihFp2hmCIa0MSyYUYysUYh7U4vaMzvYMz-YLR-inm-bM7W2UzvDLlWVM7MFUNCZnmLDMNVFLzQ7LRNJv2nto4OeosT/vsX4CInxqIZ0qIbtpYyPLRL8g4-ZoRNJqdXnx&oid=1601757823&tid=1034&nid=2889&e=.pdf`

质量修正：
- 将 `virtual_attach_file.vsb?...&e=.pdf` 识别为附件链接，使 VSB 内嵌 PDF 能被继续下载解析。
- 新增山东财经大学博士拟录取 PDF 专项解析，处理“录取专业代码/名称”跨行和“录取学院”跨行，避免导师姓名误入 `admission_major`。
- 扩充“拟录取考生名单/待录取考生名单”分类关键词，使列表页中的硕士拟录取公告也能进入后续抓取；本轮山东财经硕士公告页正文仅显示“公示期已结束”，未暴露名单附件。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：169,336 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：169,336 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：272 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：175,046 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：175,046 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：424 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，243 所已精确匹配官网记录

验证：
- batch127d 清洗表：6 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，代码-only `admission_major` 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch126 东华理工/吉林师范/大连工业/桂林电子科技

batch126 继续从剩余未覆盖院校中筛选官方静态名单入口，种子覆盖渤海大学、东华理工大学、吉林师范大学、桂林电子科技大学、大连工业大学、电子科技大学、华东交通大学、哈尔滨师范大学等。渤海大学、电子科技大学、华东交通大学、哈尔滨师范大学等入口本轮未形成静态可解析人员级记录；可入库来源集中在东华理工大学、吉林师范大学、大连工业大学和桂林电子科技大学。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch126.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch126d/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch126d/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch126b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch126b/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 桂林电子科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,227 | 0 |
| 大连工业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 31 | 0 |
| 东华理工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 11 | 0 |
| 吉林师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 3 | 0 |

可追溯来源：

- 东华理工大学 2026 年接收推免生拟录取名单公示：`https://yjsy.ecut.edu.cn/0c/1a/c427a134170/page.htm`
- 东华理工大学拟录取名单 PDF：`https://yjsy.ecut.edu.cn/_upload/article/files/05/aa/2cfc558945c6a660cda604beb4a5/bbbe6726-02a9-433c-aa4d-0e93916ffca7.pdf`
- 吉林师范大学 2026 年接收推免生拟录取名单公示：`https://www.jlnu.edu.cn/yjsy/info/1032/2813.htm`
- 桂林电子科技大学 2026 年硕士研究生拟录取名单公示入口：`https://www.guet.edu.cn/yjszs/2026/0323/c4245a150076/page.htm`
- 大连工业大学 2026 年接收推荐免试研究生拟录取名单公示入口：`http://yjs.dep.dlpu.edu.cn/_infolist/info_1.asp?f_menu_id=70&f_id=367`
- 大连工业大学拟录取名单 Excel：`http://yjs.dep.dlpu.edu.cn/_uploadimg/file/20251027/20251027093735453545.xlsx`

质量修正：
- 新增桂林电子科技大学 PDF 专项解析，处理“学院+考号”“考号+姓名”“序号单独占行”“专业代码+专业名+初试分数”等多种 PDF 文本层拆行形态。
- 修正通用表头映射，将“录取专业代码”写入 `major`、“录取专业名称”写入 `admission_major`，并识别“毕业单位”为 `undergraduate_school`，修复大连工业大学 Excel 中专业代码误入 `admission_major` 的问题。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：169,330 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：169,330 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：271 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：175,040 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：175,040 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：423 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，242 所已精确匹配官网记录

验证：
- batch126d 清洗表：2,272 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，代码-only `admission_major` 0，桂林电子科技大学异常学号 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch125 贵州医科/广西艺术/兰州交通/广州医科

batch125 继续从剩余未覆盖院校中筛选官方静态 PDF 和公告入口，种子覆盖北京服装学院、东北电力大学、黑龙江中医药大学、贵州医科大学、广西艺术学院、西南交通大学、广州医科大学、华东交通大学和兰州交通大学等。北京服装学院、东北电力大学、黑龙江中医药大学、西南交通大学、华东交通大学等入口本轮未形成静态可解析人员级记录；可入库来源集中在贵州医科大学、广西艺术学院、兰州交通大学和广州医科大学。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch125.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch125d/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch125d/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch125d/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch125d/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 贵州医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,437 | 0 |
| 广西艺术学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 305 | 0 |
| 兰州交通大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 176 | 0 |
| 广州医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2 | 0 |

可追溯来源：

- 贵州医科大学 2026 年硕士考试一志愿考生拟录取名单公示：`https://yjsxy.gmc.edu.cn/info/1118/2465.htm`
- 贵州医科大学 2026 年硕士研究生调剂拟录取名单公示（一）：`https://yjsxy.gmc.edu.cn/info/1118/2479.htm`
- 贵州医科大学 2026 年硕士研究生调剂拟录取名单公示（二）：`https://yjsxy.gmc.edu.cn/info/1118/2488.htm`
- 广西艺术学院 2026 年硕士研究生招生一志愿复试成绩及拟录取名单：`https://zsb.gxau.edu.cn/yjszs/tzgg1/content_314769`
- 广西艺术学院调剂复试成绩及拟录取名单 PDF：`https://zsb.gxau.edu.cn/upload/zsb/contentmanage/article/file/2026/04/14/%E9%99%84%E4%BB%B6%EF%BC%9A%E5%B9%BF%E8%A5%BF%E8%89%BA%E6%9C%AF%E5%AD%A6%E9%99%A22026%E5%B9%B4%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9B%E7%94%9F%E8%B0%83%E5%89%82%E5%A4%8D%E8%AF%95%E6%88%90%E7%BB%A9%E5%8F%8A%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95.pdf`
- 兰州交通大学自动化与电气工程学院拟录取名单 PDF：`https://dqxy.lzjtu.edu.cn/__local/5/09/74/C017F3F87EA00B3FE66396680E1_9CD8D819_2FF2C.pdf`
- 兰州交通大学数理学院调剂第二批拟录取名单 PDF：`https://slxy.lzjtu.edu.cn/__local/6/D3/A1/C68C8B7F6476032BBBF7397BBAA_6137CA26_292E3.pdf`
- 广州医科大学附属番禺中心医院校外调剂拟录取名单：`https://www.pyhospital.com.cn/show.php?id=4312`

质量修正：
- 新增贵州医科大学 PDF 专项解析，正确拆出学院代码/名称、专业代码/名称、研究方向代码/名称和成绩，避免研究方向代码 `00` 误写入 `admission_major`。
- 新增广西艺术学院 PDF 专项解析，处理跨行列头、课程名折行和“学术/专业 + 学位”拆行，只保留拟录取行。
- 新增兰州交通大学 PDF 专项解析，将拟录取专业代码和拟录取专业名称合并为 `admission_major`。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：167,058 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：167,058 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：267 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：172,768 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：172,768 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：419 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，238 所已精确匹配官网记录

验证：
- batch125d 清洗表：1,920 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，数字/代码-only `admission_major` 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch124 徐州医科大学/浙江理工大学

batch124 继续从未覆盖院校中筛选官网列表页、公告页和 PDF 直链，种子覆盖徐州医科大学、中国医科大学、中国药科大学、皖南医学院、温州医科大学、浙江工商大学、浙江理工大学、福建医科大学、南方医科大学等。首轮入口中，徐州医科大学、温州医科大学、浙江理工大学等旧地址返回 404，中国医科大学返回 502，中国药科大学详情页返回 410，南方医科大学附件进入验证码下载桥；浙江工商大学列表页只形成旧导航片段，清洗后未入库。batch124b/batch124c 修正徐州医科大学和浙江理工大学官方入口后，形成可入库人员级记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch124.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch124b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch124c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch124c/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch124c/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch124c/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 徐州医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,391 | 1,391 |
| 浙江理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 164 | 0 |

可追溯来源：

- 徐州医科大学 2026 年硕士研究生招生复试拟录取名单相关公告：`https://yjs.xzhmu.edu.cn/info/1247/7093.htm`
- 徐州医科大学 2026 年硕士研究生招生复试拟录取名单相关公告：`https://yjs.xzhmu.edu.cn/info/1247/7107.htm`
- 徐州医科大学拟录取名单 PDF：`https://yjs.xzhmu.edu.cn/__local/0/AC/3C/1B36EB9E0F7A102E846F71FB082_281F6E74_199C11.pdf`
- 徐州医科大学拟录取名单 PDF：`https://yjs.xzhmu.edu.cn/__local/1/CF/50/793F3821EDE3C218B5DB062CF23_82114451_129DB3.pdf`
- 浙江理工大学 2026 年硕士研究生拟录取名单公示：`https://gradadmission.zstu.edu.cn/info/1011/3347.htm`
- 浙江理工大学拟录取名单 PDF：`https://gradadmission.zstu.edu.cn/__local/4/DD/31/2866B6FC65A3F4F7063047AC8CC_A7FE3C0D_781EF.pdf`
- 浙江理工大学拟录取名单 PDF：`https://gradadmission.zstu.edu.cn/__local/8/CC/B3/7ECF8148258592AC06FCBE86A79_4474591E_7FAF2.pdf`

质量修正：
- 新增徐州医科大学 PDF 专项解析，识别“考生编号 / 姓名 / 初试成绩 / 复试成绩 / 总成绩 / 备注”版式；源 PDF 不含专业列，因此保留成绩到 `remarks`，并标记 `missing_major;needs_review`。
- 新增浙江理工大学 PDF 专项解析，识别“报名号 / 考生姓名 / 综合考核总成绩 / 拟录取专业 / 录取类别 / 学位类型 / 备注”版式，避免通用解析把综合成绩误写入 `admission_major`。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：165,138 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：165,138 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：263 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：170,848 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：170,848 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：415 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，234 所已精确匹配官网记录

验证：
- batch124c 清洗表：1,555 条清洗记录；徐州医科大学 1,391 条因源 PDF 无专业列需复核，浙江理工大学 164 条缺少人员姓名 0、缺少录取专业 0、需人工复核 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch111 上海应用技术大学

batch111 继续从 208 所未精确覆盖院校中筛选当前官网仍可访问的材料入口。南京财经大学、南方医科大学、杭州师范大学、上海海事大学、上海应用技术大学作为本轮种子；最终只有上海应用技术大学 2026 年接收推免生拟录取名单 HTML 表格形成可结构化记录。南京财经大学、南方医科大学页面均转入验证码下载桥；杭州师范大学本地请求返回 404；上海海事大学页面无人员级明细。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch111.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch111/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch111/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch111/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch110b/batch110c 北华大学/贵州民族大学

batch110 先复核北京电影学院、大连外国语大学、福建中医药大学、贵州师范大学、桂林理工大学、华东理工大学、东北师范大学、贵州民族大学、北华大学、中南民族大学等缺口入口。可静态结构化的来源最终集中在北华大学 HTML 表格和贵州民族大学硕士招生栏目；大连外国语大学、海南医科大学、黑龙江中医药大学等页面可访问但附件下载桥要求验证码，华东理工大学名单为图片嵌入，当前无本地 OCR 链路，暂未并入。

batch110b/batch110c 新增并验证两类 HTML 表头规则：`姓名 + 报考专业代码 + 报考专业名称 + 报考学习形式 + 复试成绩`，以及 `拟录取学院 + 考生姓名 + 拟录取专业代码 + 拟录取专业`。修复后专业代码进入 `major`，代码和专业名合并进入 `admission_major`，学习形式、复试成绩或性别进入 `remarks`。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch110.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch110b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch110c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch110c/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch110c/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch109/batch109b 广东财经大学

batch109 先复核广东财经大学、桂林电子科技大学、电子科技大学、华中科技大学、东北师范大学、中央民族大学等缺口入口。广东财经大学研招办列表页可访问并暴露各批次“硕士拟录取状态信息表”附件；桂林电子科技大学页面静态正文未暴露名单明细，华中科技大学附件下载页要求验证码，东北师范大学页面未保留人员级名单，电子科技大学和中央民族大学候选地址本地返回 404，均暂未并入。

batch109b 从广东财经大学列表页抽取 39 个详情页并跟进 PDF 附件。原始 PDF 版式包括“学院名称”跨行、额外复试分项和专业排名列，通用表格解析会把分数错写进专业字段；本轮新增专项回归测试和解析规则后，保留姓名、考生编号、学院、专业代码、专业名称、总成绩和来源 URL，并只纳入状态列含“拟录取”的人员行。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch109.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch109b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch109b_fixed2/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch109b_fixed2/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch109b_fixed2/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch106-108b 河北工程/河北经贸/上海财经

batch106/b 补河北缺口，河北大学附件需要验证码、华北理工大学页面未返回名单正文、南京邮电大学直链返回提示页，暂未并入；成功补入河北工程大学 8 条、河北经贸大学 4 条 2026 年拟录取推免生记录。batch107 试探上海高校校级页面，其中华东政法大学仅有“拟录取 377 名”的公告正文而无名单明细，上海师范大学静态页面无附件链接，上海财经大学校级 AnyShare 外链接口返回“外链不存在”，均暂未并入。batch108b 转向上海财经大学院系官网最终/候补名单，补入商学院 130 条、会计学院 92 条；预报名考核名单和报名通知保留抓取证据但不并入交付主表，会计学院 PDF 中水印导致错位的低信息行已剔除。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch106.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch106b.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch107.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch108.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch106_merged/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch106_merged/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch108b/records_clean_outcome_subset.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch108b/records_public_outcome_subset.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch108b/school_year_summary_outcome_subset.csv`

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

## 2026-05-25 追加进展：batch105b 广州中医药大学

batch104/b 先试探安徽财经大学、北京协和医学院、北京语言大学、大连外国语大学、东北师范大学、东华理工大学和电子科技大学等官网入口，其中部分页面返回 403/404/502，部分页面抓取成功但为验证码附件、空公示系统或无人员级正文表格，暂未并入。随后 batch105 转向广东、广西、海南等剩余缺口院校，batch105b 使用修正后的嵌套表格解析器，成功补入广州中医药大学 2026 年推免生拟录取名单 319 条人员级记录。该页面字段包含考生姓名、院所名称、录取专业代码/名称、研究方向和接收导师。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch104.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch104b.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch105.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch105b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch105b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch105b/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch105b/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch103c 西藏大学

batch103 先试探甘肃农业大学、福建医科大学、新疆农业大学和兰州大学等入口，其中福建医科大学、新疆农业大学、青海大学、海南师范大学页面或附件抓取成功但未形成可解析人员级记录，兰州大学附件直链本地返回 502。随后 batch103c 转向西藏大学，成功补入校级 PDF 与信息科学技术学院官网正文名单，共 90 条人员级记录。校级 PDF 字段包含姓名、学院和专业；学院正文名单字段包含姓名、学号、专业和排名。两份来源中有 1 个同名人员重复出现，暂按不同来源保留，后续可做跨来源同名融合。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch103.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch103b.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch103c.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch103c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch103c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch103c/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch103b/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch102 河北北方学院

batch102 转向河北缺口院校。本轮成功补入河北北方学院 2026 年推免相关官方 PDF 两份，共 100 条人员级记录：教务处本科推免推荐名单 86 条，字段包含姓名、学号、学院和本科专业；研究生院免试攻读硕士研究生拟录取第一批名单 14 条，字段包含姓名、拟录取专业代码和学习方式。河北经贸大学候选入口本地抓取返回 502；河北大学、河北农业大学等后续种子因慢请求拖长，本轮中断后未并入。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch102.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch102/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch102/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch102/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch102/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch101/batch101b 安徽大学

batch101 继续面向未覆盖院校补 B 类官网材料。本轮成功补入安徽大学 2026 年拟录取推免生公示名单 PDF。该 PDF 为“姓名、性别、毕业单位、拟录取学院、拟录取专业、考核成绩、备注”版式，原通用 PDF 表格解析会把性别、本科院校和成绩错位；本轮新增专项回归测试和解析规则后，清洗表中姓名不再带性别，本科院校、拟录取学院、拟录取专业和考核成绩均落到可用字段。为避免同一输出目录追加旧记录，修正后的干净产物使用 `batch101b` 目录。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch101.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch101b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch101b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch101b/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch101b/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch100 扬州大学

batch100 继续补 B 类官网材料。扬州大学法学院 PDF 可直接下载并解析，正文名单位于“学生名单如下”之后，现已新增专门的 PDF 纯姓名名单解析规则，处理“如下”跨行和单字姓换行的情况，最终抽取 17 条真实人员记录。该 PDF 没有学生编号、专业、学院、排名等字段，清洗后全部保留 `needs_review=true`。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch100.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch100/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch100/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch100/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch100/graduate_outcome_failures.jsonl`

batch100 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 扬州大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 17 | 17 |

可追溯来源：

- 扬州大学法学院 2025 年推荐优秀应届本科毕业生免试攻读研究生通过答辩公示 PDF：`https://fxy.yzu.edu.cn/__local/4/42/E7/036779B02BE9F95A16FEDC83F20_594D2C91_17F41.pdf`

本批试探但暂未并入的典型入口：

- 浙江工商大学 2026 推免相关页面实时返回 410。
- 浙江理工大学、华东师范大学部分页面可访问，但静态页面未暴露最终名单附件或附件已随公示期关闭。
- 中国海洋大学、中山大学、东北电力大学、上海科技大学候选直链返回 404/410。
- 东北师范大学动态查询后端已关闭，返回“录取名单尚未公布”等提示，未暴露人员表。
- 扬州大学化学与材料学院附件可下载，但内容是工作通知，不是人员名单，未并入。

本批合并后交付版：

- B 类官网总表：158,325 条清洗记录，239 个学校/年份/文档类型汇总组
- 统一清洗包：164,035 条记录，391 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，212 所已精确匹配官网记录，218 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：170 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch100 清洗表：17 条，17 条需复核；公开版 17 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 164,036 行（含表头），公开明细 164,035 行。

## 2026-05-25 追加进展：batch99 西华大学

batch99 转向四川缺口高校。西华大学研究生院 2026 年拟录取推荐免试攻读硕士研究生名单公示页可从 HTML 表格中抽取 7 条真实推免拟录取记录，字段包含姓名、录取学院、专业代码、录取专业和录取类别，清洗后 0 条需复核。西南科技大学候选入口在本轮抓取中出现 502/长时间无响应，已保留日志并中止该慢请求。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch99.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch99/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch99/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch99/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch99/graduate_outcome_failures.jsonl`

batch99 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西华大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 7 | 0 |

可追溯来源：

- 西华大学 2026 年拟录取推荐免试攻读硕士研究生名单公示页：`https://yjs.xhu.edu.cn/88/a7/c10021a231591/page.htm`
- 西南科技大学候选列表：`https://gs.swust.edu.cn/zs/7797/list.htm`

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

batch96 覆盖西安外国语大学、西安邮电大学、西安电子科技大学候选入口；batch97 覆盖杭州师范大学、温州医科大学、西湖大学候选入口；batch98 覆盖山西财经大学、山西农业大学候选入口。三批均完成抓取或部分抓取，并输出种子/日志/原始记录。batch96 新增清洗回归规则：剔除“张老师/刘老师”等联系方式以及列表页 `DATE` 字段错位形成的索引碎片。batch97 主要受 404、温州医科大学 483、 西湖大学 500 影响；batch98 主要受山西财经大学 502 和山西农业大学/西南科技等慢请求影响，未并入主数据。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch96.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch97.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch98.csv`

## 2026-05-25 追加进展：batch95 宁夏大学

batch95 转向宁夏缺口高校。宁夏大学研究生院 2026 年接收推荐免试攻读硕士研究生拟录取名单、2026 年硕士研究生招生拟录取名单第一批/第二批页面均暴露可解析附件，现有解析链条结构化 3,124 条，清洗后 0 条需复核。宁夏医科大学候选页本轮部分入口返回 404 或仅抓到通知列表，暂未形成可并入记录。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch95.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch95/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch95/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch95/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch95/graduate_outcome_failures.jsonl`

batch95 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 宁夏大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 33 | 0 |
| 宁夏大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,091 | 0 |

可追溯来源：

- 宁夏大学 2026 年接收推荐免试攻读硕士研究生拟录取名单公示页：`https://graduate.nxu.edu.cn/info/1054/8503.htm`
- 宁夏大学 2026 年硕士研究生招生拟录取名单公示（第一批）：`https://graduate.nxu.edu.cn/info/1020/8544.htm`
- 宁夏大学 2026 年硕士研究生招生拟录取名单公示（第二批）：`https://graduate.nxu.edu.cn/info/1020/8555.htm`
- 宁夏医科大学候选页：`https://www.nxmu.edu.cn/yjsy/info/1040/3477.htm`

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

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch93.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch94.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch93/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch94/records_clean.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch93/graduate_outcome_failures.jsonl`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch94/graduate_outcome_failures.jsonl`

## 2026-05-25 追加进展：batch92 青岛大学

batch92 转向山东缺口高校，并补入一个云南候选入口。青岛大学研究生院 2026 年硕士研究生招生拟录取名单公告暴露 PDF 附件，现有 PDF 解析链条结构化 3,955 条，字段包含姓名、考生编号、学院代码、学院名称、录取专业代码和备注代码，清洗后 0 条需复核。新增清洗回归规则：剔除青岛大学 PDF 中由学院/方向文字、括号尾部和被截断姓名片段错位形成的无上下文伪姓名。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch92.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch92/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch92/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch92/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch92/graduate_outcome_failures.jsonl`

batch92 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 青岛大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,955 | 0 |

可追溯来源：

- 青岛大学 2026 年硕士研究生招生拟录取名单公示页：`https://grad.qdu.edu.cn/info/1118/4499.htm`
- 青岛大学拟录取名单 PDF：`https://grad.qdu.edu.cn/__local/2/98/3D/B248B48C86D3D7841621B0C6706_4D28F42B_A8AE1.pdf`
- 青岛理工大学候选页：`https://yjsh.qut.edu.cn/info/1406/3291.htm`
- 山东理工大学招生工作列表：`https://yjsh.sdut.edu.cn/zsgz/list.htm`
- 山东农业大学候选页：`https://yjsc.sdau.edu.cn/info/17/41579.htm`
- 昆明理工大学候选页：`https://www.kmust.edu.cn/info/1166/56845.htm`

本批合并后交付版：

- B 类官网总表：155,177 条清洗记录，235 个学校/年份/文档类型汇总组
- 统一清洗包：160,887 条记录，387 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，209 所已精确匹配官网记录，221 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：168 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch92 清洗表：3,955 条，0 条需复核；公开版 3,955 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 160,888 行（含表头），公开明细 160,887 行。

## 2026-05-25 追加进展：batch91 河北医科大学、河北科技大学

batch91 转向河北缺口高校。河北医科大学研究生学院一志愿复试成绩及拟录取结果公告暴露 Excel 附件，清洗后保留 194 条；河北科技大学硕士研究生一志愿考生复试成绩及拟录取名单公告暴露 PDF 附件，清洗后保留 1,088 条。新增清洗回归规则：剔除河北科技大学 PDF 中由成绩、加试分数、括号方向和孤立无上下文字段片段错位形成的伪姓名，同时保留带考生编号和专业上下文的真实名单行。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch91.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch91/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch91/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch91/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch91/graduate_outcome_failures.jsonl`

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
- 河北大学招生工作/信息公开列表：`https://yjsy.hbu.edu.cn/zsgz.htm`、`https://yjsy.hbu.edu.cn/zsgz/xxgk.htm`
- 河北农业大学候选页：`https://yanjiusheng.hebau.edu.cn/info/1110/4717.htm`
- 河北北方学院候选页：`https://yjs.hebeinu.edu.cn/zsgl/tzgg/146595.htm`

本批合并后交付版：

- B 类官网总表：151,222 条清洗记录，234 个学校/年份/文档类型汇总组
- 统一清洗包：156,932 条记录，386 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，208 所已精确匹配官网记录，222 所暂无精确匹配
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：167 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch91 清洗表：1,282 条，0 条需复核；公开版 1,282 条
- 工作簿导出校验：公式错误扫描 0 条，`Public_Records` 156,933 行（含表头），公开明细 156,932 行。

## 2026-05-25 追加进展：batch90 南通大学

batch90 转向江苏/南京缺口高校。南通大学研究生招生网 2026 年接收推荐免试研究生拟录取名单页面暴露 PDF 附件，现有 PDF 解析链条结构化 179 条，字段包含姓名、学号、学院和录取专业代码，清洗后 0 条需复核。南京邮电大学硕士招生列表页本身可抓取，但跟进命中的是 2021 年旧页面，未并入本批；南京理工大学两个候选官方页返回 410；南京财经大学两个候选官方页返回 404，均暂未并入。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch90.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch90/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch90/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch90/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch90/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch89 广西医科大学、青海师范大学

batch89 继续补覆盖缺口高校。广西医科大学研究生院 2026 年接收推荐免试研究生拟录取名单页面暴露 PDF 附件，现有 PDF 解析链条结构化 106 条；青海师范大学研究生院 2026 年推荐免试硕士研究生拟录取名单页面可从 HTML 表格保留 9 条带学院和学习方式的记录。大连外国语大学列表页及一志愿/调剂/推免公告页、北华大学、福建师范大学、福建农林大学、云南师范大学等候选入口已抓取，但页面/附件桥未形成可静态抽取的人员级记录；安徽大学历史 PDF 直链返回 404，暂未并入。

本批新增清洗回归规则：剔除青海师范页面中由正文问候语错位形成的“各位 推免生”伪专业碎片，同时保留带学院上下文的真实名单行；剔除广西医科 PDF 标题被拆成“广/西/医/科/大/学”等单字姓名的无上下文碎片。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch89.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch89/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch89/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch89/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch89/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch88 成都大学

batch88 继续补覆盖缺口高校。成都大学研究生处页面中 `8189.htm` 可结构化 1 条退役大学生士兵专项相关拟录取记录；`8187.htm` 主公示页和附件下载桥已抓取，但下载桥返回 HTML/验证码类页面，未形成更多结构化名单。大连大学候选入口返回 404；大连海洋大学、青岛理工大学、浙江理工大学候选页已抓取，但页面/PDF/附件未形成可静态抽取的人员级记录，暂不并入主表。

本批新增清洗回归规则：剔除文章页正文抽取中误入人员字段的“一审/二审/三审”等审核标签，以及“二等战功”等荣誉文本单独成为姓名的碎片；带有学号和专业字段的真实记录仍正常保留。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch88.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch88/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch88/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch88/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch88/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch87 蚌埠医科大学、兰州财经大学

batch87 继续补覆盖缺口高校。蚌埠医科大学研究生院 2026 年推免生拟录取名单页面可直接从 HTML 结构化 5 条；兰州财经大学研究生院 2026 年接收应届本科毕业生免试攻读硕士研究生拟录取名单页面正文可结构化 4 条。蚌埠医科大学 2026 年硕士研究生拟录取名单页正文仅保留“公示已结束”附件说明，未暴露可下载名单；北京协和医学院推免系统当前已切到 2027 年空表；北方民族大学、北京语言大学、渤海大学、安徽财经大学、青海师范大学、东北电力大学、北华大学等候选入口分别遇到 404、403、502、验证码/空表或无静态名单，未并入本批结构化主表。

本批新增清洗回归规则：对正文抽取中“只有拟录取状态、没有学院/专业上下文/学号”的碎片行进行剔除，避免兰州财经页面中的“王雅萱/拟录取”重复行以及“数字经济/拟录取”“金融工程/拟录取”等专业名误入姓名列。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch87.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch87b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch87/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch87b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch87/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch87b/records_public.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch87/graduate_outcome_failures.jsonl`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch87b/graduate_outcome_failures.jsonl`

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

## 2026-05-25 追加进展：batch86 天津医药类高校

batch86 继续补天津缺口高校。天津医科大学 2026 年硕士研究生招生拟录取名单公示页暴露 PDF 附件，现有 PDF 表格链条结构化 1,211 条；天津中医药大学研究生院多个学院/附属医院接收推免拟录取名单页面可直接从 HTML 表格结构化，合并清洗后保留 156 条。天津体育学院候选页和附件下载桥已抓取，但未形成可结构化人员级记录；天津医科大学旧 PDF 直链返回 404，未并入。

本批新增清洗回归规则：剔除天津中医药页面中误入姓名列的“硕士”“直博生”，以及天津医科 PDF 表头错位产生的“方向”“院系所”等标签，避免标题、层级和表头文本污染清洗表。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch86.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch86/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch86/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch86/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch86/graduate_outcome_failures.jsonl`

batch86 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 天津医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,211 |
| 天津中医药大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 156 |

可追溯来源：

- 天津医科大学 2026 年硕士研究生招生拟录取名单公示页：`https://gs.tmu.edu.cn/2026/0429/c3146a87608/page.htm`
- 天津医科大学拟录取名单 PDF：`https://gs.tmu.edu.cn/_upload/article/files/37/c0/a5cbb16440048fbdd5fdfdd8ef64/fd97bfc7-7f09-4d16-9486-871a9419a00f.pdf`
- 天津中医药大学附属医院拟录取名单页：`https://yjsy.tjutcm.edu.cn/info/1976/9429.htm`
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

## 2026-05-25 追加进展：batch85 天津缺口高校

batch85 继续补天津缺口高校。天津美术学院 2026 年硕士研究生招生拟录取名单页面暴露 PDF 附件，现有 PDF 链条结构化 374 条；天津理工大学采用研究生院汇总页加学院公示页入口，抓取计算机、语言文化、理学院、电气、管理、马克思主义、聋人工学院等页面，清洗后保留 16 条；天津商业大学研究生处入口未发现 2026 拟录取明细，但历史 2024 接收推免拟录取公示可结构化 3 条。天津科技大学页面和 PDF 直链均持续同 URL 302 循环，暂未并入。

本批新增清洗回归规则：剔除天津理工页面中误入姓名列的“会计”“合作院校”“工商管理学”“管理科学与工程”“支教团”“天开杯”“科研项目”等专业、栏目或说明文本；同时把“学院名误入 major 字段”的重复行转为学院字段后与更完整记录去重。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260525_batch85.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch85/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch85/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch85/school_year_summary.csv`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch85/graduate_outcome_failures.jsonl`

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

## 2026-05-24 追加进展：batch84 天津缺口高校

batch84 面向天津缺口高校继续补源，同时复核北京、辽宁、山东若干候选入口。南开大学统计与数据科学学院官网页面可直接结构化 33 条；天津外国语大学研究生院页面暴露附件下载桥，手动读取验证码后保存官方 PDF 并生成 32 条拟录取记录；天津大学教务处公示汇总页列出各学院名单入口，本批抓取理学院、马克思主义学院、仁爱学院/人文艺术相关学院页，清洗后得到 56 条有效记录。天津大学中有 10 条学院页未公开专业字段，保留 `needs_review=true`。本批新增导航文本过滤回归，剔除“滨海校区”“研究生院”“学业指导”“教师发展”“办公网”“图书馆”“学号”“教务处”“财务系统”等被误抽到姓名列的站点文本。

补充入口复核中，沈阳航空航天大学和中央民族大学搜索命中页实时返回 404；中国海洋大学 PDF 直链仍返回 404；南开大学招生办主页面跳转统一身份认证；天津大学 `mstu.tju.edu.cn` 页面仅形成站点导航碎片，均未并入本批主表。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch84.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch84_tju_colleges.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch84/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch84/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch84/school_year_summary.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch84/records_valid.jsonl`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260524_batch84_manual/tjfsu_recommendation_list.pdf`

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

## 2026-05-24 追加进展：batch83 辽宁缺口高校

batch83 面向辽宁缺口高校继续补源。辽宁工程技术大学官网 2026 年一志愿待录取硕士研究生公示页内嵌 PDF，现有 PDF 表格解析链条可直接结构化。辽宁中医药大学 2026 年拟录取推免生（含直博生）名单和大连医科大学 2026 年接收推免硕士/直博拟录取名单均通过官网附件下载桥公开，下载桥需要验证码；手动读取验证码后保存 PDF，并按测试先行新增辽宁中医药、大连医科 PDF 解析规则，覆盖学院、拟录取专业、研究方向、成绩、硕士/直博备注，以及大连医科院系/专业/研究方向跨行错位版式。

补充入口复核中，渤海大学 2026 年待录取推荐免试攻读研究生名单公示页正文仅说明“拟接收……六名”，云盘附件字段为空，未公开人员明细；中国海洋大学 2026 年推荐免试研究生拟录取名单公示页仅暴露二维码图片，HTML 未给出可下载名单文件；天津科技大学候选页和直连 PDF 均返回同 URL 302 循环，暂未并入本批主表。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch83.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch83_extra.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch83/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch83/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch83/school_year_summary.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch83/records_manual.jsonl`

batch83 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 大连医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 15 |
| 辽宁中医药大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 76 |
| 辽宁工程技术大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,145 |

可追溯来源：

- 辽宁中医药大学 2026 年拟录取推免生（含直博生）名单公示页：`https://yjs.lnutcm.edu.cn/info/1193/12058.htm`
- 辽宁中医药大学名单 PDF 下载桥：`https://yjs.lnutcm.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1970425294&wbfileid=7CA79EBE0FD8357E097A0627FB7DEF45`
- 大连医科大学 2026 年接收推荐优秀本科毕业生免试攻读研究生拟录取名单公示页：`https://yjs.dmu.edu.cn/info/1017/9089.htm`
- 大连医科大学推免硕士名单 PDF 下载桥：`https://yjs.dmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1383548158&wbfileid=2700161`
- 大连医科大学直博名单 PDF 下载桥：`https://yjs.dmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1383548158&wbfileid=2700163`
- 辽宁工程技术大学 2026 年一志愿待录取硕士研究生公示页：`https://yjsy.lntu.edu.cn/info/1132/4128.htm`
- 辽宁工程技术大学内嵌 PDF：`https://yjsy.lntu.edu.cn/__local/B/FF/92/8B9A90243AC1CDB5E29EBB7384F_91CB59B8_3FE9C.pdf`

本批合并后交付版：

- B 类官网总表：147,755 条清洗记录，217 个学校/年份/文档类型汇总组
- 统一清洗包：153,465 条记录，369 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，192 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：161 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch83 清洗表：1,236 条，0 条需复核，1,236 个唯一 `record_id`
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T153466`，公式错误扫描 0 条，并已渲染 4 个工作表预览。

## 2026-05-24 追加进展：batch82 辽宁缺口高校

batch82 面向辽宁、天津等仍缺口高校继续补源。大连海事大学官网页面公开 2026 年推免研究生（含直博生）拟录取考生名单，附件下载桥需要验证码；手动读取验证码后成功下载 PDF，并按测试先行新增大连海事 PDF 解析规则，覆盖专业名称换行、含字母专业代码、学位类别和姓名挤在同列、直博生段缺少本行学位列等版式。沈阳工业大学原搜索命中页为旧 404，改从硕士招生列表页定位到 2026 年接收推荐免试研究生拟录取名单公示页，正文 HTML 表格可直接结构化，并新增沈阳工业 HTML 表格规则以保留证件号码、招生类型、学习方式和复试成绩。天津科技大学候选页返回自身 302 循环，暂未并入；中国医科大学可访问研究生院招生信息页，但主统考页面只提供拟录取类别确认通知，无公开人员明细，暂未并入本批主表。

本批还新增清洗回归规则：有效中文姓名即便以“名”结尾也不应被误判为“姓名/名单”表头；无证件号名单中同名同专业但序号不同的记录应保留为不同考生，避免 PDF 序号名单被去重误合并。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch82.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch82/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch82/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch82/school_year_summary.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch82/records_manual.jsonl`

batch82 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 大连海事大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 466 |
| 沈阳工业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 132 |

可追溯来源：

- 大连海事大学 2026 年推免研究生（含直博生）拟录取名单公示页：`https://grs.dlmu.edu.cn/info/1139/24351.htm`
- 大连海事大学拟录取名单 PDF 下载桥：`https://grs.dlmu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2074486004&wbfileid=A2E1BF3744CFD7FB0FD1E0B93A4F6BFC`
- 沈阳工业大学 2026 年接收推荐免试研究生拟录取名单公示页：`https://yjsxy.sut.edu.cn/info/1311/10141.htm`
- 沈阳工业大学硕士招生列表定位页：`https://yjsxy.sut.edu.cn/zsgz/sszs.htm`

本批合并后交付版：

- B 类官网总表：146,519 条清洗记录，214 个学校/年份/文档类型汇总组
- 统一清洗包：152,229 条记录，366 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，189 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：158 个测试通过（仅保留既有临时 CSV 文件 ResourceWarning）
- batch82 清洗表：598 条，0 条需复核，598 个唯一 `record_id`
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T152230`，公式错误扫描 0 条，并已渲染 4 个工作表预览。

## 2026-05-24 追加进展：batch81b 江苏、内蒙古缺口高校

batch81 继续补江苏、北京、上海、内蒙古等覆盖缺口高校。第一轮种子中部分搜索索引旧地址返回 404/410，华东政法大学页面仅公布拟录取总人数而无人员明细，中国政法大学页面返回动态挑战页，北京语言大学附件下载桥返回 HTML 校验页，正文误抽出的页脚链接已被清洗规则剔除。batch81b 修正入口后，江苏大学和内蒙古师范大学页面均暴露附件下载桥；使用来源页 Referer 手动下载后确认均为真实 PDF，并由现有 PDF 表格解析链条结构化。

本批还新增清洗回归规则：剔除研究生院页面导航栏目误入姓名列的记录，如“下载专区”“学位授予”“硕士招生”“科研工作”等，避免正文导航区污染清洗表。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch81.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch81b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch81b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch81b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch81b/school_year_summary.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch81b/records_manual.jsonl`

batch81b 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 江苏大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4,386 |
| 内蒙古师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,205 |

可追溯来源：

- 江苏大学 2026 年全国统考硕士研究生拟录取名单公示页：`https://yz.ujs.edu.cn/info/1010/8497.htm`
- 江苏大学拟录取名单 PDF 下载桥：`https://yz.ujs.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1347509089&wbfileid=4E4ACCD2B8D73EED6EEFB4A00353E43B`
- 内蒙古师范大学 2026 年硕士研究生招生考试一志愿考生拟录取名单公示页：`https://yjsc.imnu.edu.cn/info/1004/5118.htm`
- 内蒙古师范大学拟录取名单 PDF 下载桥：`https://yjsc.imnu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1551731048&wbfileid=6F4216E57B8D71E27058BF0C7ECC8F5D`

本批合并后交付版：

- B 类官网总表：145,921 条清洗记录，212 个学校/年份/文档类型汇总组
- 统一清洗包：151,631 条记录，364 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，187 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：154 个测试通过
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T151632`，公式错误扫描 0 条，并已渲染 4 个工作表预览。
- 全量质量扫描：缺少身份 0、表头/联系人文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch81b 清洗表 5,591 条；Excel `Public_Records` 151,631 行。

## 2026-05-24 追加进展：batch80b 江苏缺口高校

batch80 面向江苏、四川、上海、北京等覆盖缺口高校继续补源。初始 batch80 发现南京工业大学 2026 年调剂硕士研究生拟录取名单 PDF 可访问，但表格换行会造成错位行；按测试先行新增南京工业大学专用 PDF 文本行解析后，使用 batch80b 干净目录重跑，稳定结构化 558 条。南京财经大学附件下载桥返回 3,805 字节 HTML 验证页；电子科技大学信息与通信工程学院附件可用 Referer 下载为 PDF，但文本层仅 13 个字符，属于扫描图片型，暂不强行并入。西南交通大学候选页 502、江苏大学候选页 404、南京理工大学候选页 410，部分电子科技大学学院页返回 412，均暂不并入主表。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch80.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch80b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch80b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch80b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch80b/school_year_summary.csv`

batch80b 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 南京工业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 558 |

可追溯来源：

- 南京工业大学 2026 年调剂硕士研究生拟录取名单 PDF：`https://gra.njtech.edu.cn/__local/2/16/D8/A73E329CA807825895EA1EA38DA_0A488B68_7C0D9.pdf`
- 电子科技大学信息与通信工程学院附件 PDF 已下载至本地原始目录，但因扫描图片型暂未结构化：`data/raw/graduate_outcomes_official_site_websearch_web_20260524_batch80b_manual/uestc_sice.pdf`

本批合并后交付版：

- B 类官网总表：140,330 条清洗记录，210 个学校/年份/文档类型汇总组
- 统一清洗包：146,040 条记录，362 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，185 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：153 个测试通过
- 工作簿反向导入校验：`Overview`、`Source_Summary`、`Coverage`、`Public_Records` 均存在，`Public_Records` 范围为 `A1:T146041`，公式错误扫描 0 条，并已渲染 4 个工作表预览。
- 全量质量扫描：缺少身份 0、表头/联系人文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch80b 清洗表 558 条；Excel `Public_Records` 146,040 行。

## 2026-05-24 追加进展：batch79b 江苏、海南、陕西、四川缺口高校

batch79 面向江苏、海南、陕西、四川等仍缺口高校继续补源。初始 batch79 证实中国矿业大学、西藏民族大学 PDF 均可访问，但需要新增 PDF 文本行规则：前者为“序号、姓名、录取学院代码/名称、录取专业代码/名称、成绩、招生类型”结构，后者需要把“姓名 身份证号”拆成姓名和脱敏证件号。按测试先行补充解析后，使用干净目录重跑为 batch79b。西南交通大学附件返回验证码页、浙江理工大学页面附件未暴露可下载链接，南昌大学和华北电力大学候选链接实时 404，暂不并入。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch79.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch79b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch79b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch79b/school_year_summary.csv`

batch79b 清洗结果：

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

本批合并后交付版：

- B 类官网总表：139,772 条清洗记录，209 个学校/年份/文档类型汇总组
- 统一清洗包：145,482 条记录，361 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，184 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：152 个测试通过
- 全量质量扫描：缺少身份 0、表头/联系人文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch79b 清洗表 1,377 条；Excel `Public_Records` 145,482 行。

## 2026-05-24 追加进展：batch78 辽宁、山东、四川缺口高校

batch78 补辽宁、山东、四川缺口高校。山东第一医科大学官方页面可自动发现 PDF 附件并结构化；大连理工大学和西南医科大学初始候选 URL 有 404 或附件验证码页问题，batch78b 使用修正后的官方页面并带来源页 Referer 下载真实 PDF 后成功结构化。大连海事大学、大连医科大学候选页实时 404，暂不并入。本批新增联系人碎片过滤规则，避免正文中的“姜老师”“联系方式”等联系人字段误入名单。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch78.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch78b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch78b/school_year_summary.csv`

batch78/78b 清洗结果：

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

本批合并后交付版：

- B 类官网总表：138,631 条清洗记录，205 个学校/年份/文档类型汇总组
- 统一清洗包：144,341 条记录，357 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，180 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：150 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航/主题切换/联系人文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch78/78b 清洗表 2,765 条；Excel `Public_Records` 144,341 行。

## 2026-05-24 追加进展：batch77 东北片区缺口高校

batch77 转向东北片区缺口高校。延边大学、哈尔滨医科大学页面默认附件下载页返回验证码 HTML，使用来源页 Referer 后可下载真实 PDF 并结构化；东北林业大学研究生招生候选页实时 404，但信息公开站 PDF 直链可访问并结构化。东北师范大学页面仅公开公示说明、未暴露个人名单明细；哈尔滨师范大学生命科学与技术学院名单为长图图片，本轮未 OCR，均暂不并入。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch77.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch77/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch77/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch77/school_year_summary.csv`

batch77 清洗结果：

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

本批合并后交付版：

- B 类官网总表：135,866 条清洗记录，202 个学校/年份/文档类型汇总组
- 统一清洗包：141,576 条记录，354 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，177 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：149 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航/主题切换文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch77 清洗表 353 条；Excel `Public_Records` 141,576 行。

## 2026-05-24 追加进展：batch76 河南、湖南缺口高校

batch76 继续补河南、湖南缺口高校。湖南工商大学官方 PDF 可直接抓取；湖南科技大学和南华大学附件在默认抓取下分别返回“非法访问”或验证码下载页，加上来源页 Referer 后可下载真实 PDF，并成功结构化。湖南大学附件也可用 Referer 下载真实 PDF，但 PDF 文本层未抽出人员记录，暂不并入；河南医药大学页面正文只暴露“名单见附件”说明但未暴露可下载附件链接；河南科技大学软件学院候选页实时返回 404；郑州轻工业大学页面误抽到的主题切换文本已通过新增清洗规则过滤，未并入。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch76.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch76/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch76/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch76/school_year_summary.csv`

batch76 清洗结果：

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

本批合并后交付版：

- B 类官网总表：135,513 条清洗记录，199 个学校/年份/文档类型汇总组
- 统一清洗包：141,223 条记录，351 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，174 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：149 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航/主题切换文本误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch76 清洗表 431 条；Excel `Public_Records` 141,223 行。

## 2026-05-24 追加进展：batch75 河南缺口高校

batch75 继续补 B 类官网推免/拟录取名单。河南理工大学、河南农业大学官方页面正文表格可直接结构化，清洗后合计新增 36 条并入 B 类官网主表。中国人民公安大学研招网页面可访问，正文仅公开 2026 年硕士推免生拟录取总数，附件下载页返回验证码页面，未获取到个人名单明细，本轮隔离未并入。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch75.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch75/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch75/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch75/school_year_summary.csv`

batch75 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 河南农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 19 |
| 河南理工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 17 |

可追溯来源：

- 河南理工大学 2026 级推免生拟录取名单公示：`https://adge.hpu.edu.cn/info/1031/14117.htm`
- 河南农业大学 2026 年推免硕士研究生拟录取名单公示：`https://gra.henau.edu.cn/a/zhaoshenggongzuo/20251021/4754.html`
- 中国人民公安大学 2026 年硕士推免生拟录取名单公示页（附件验证码，未并入）：`https://yzb.ppsuc.edu.cn/info/1008/5394.htm`

本批合并后交付版：

- B 类官网总表：135,082 条清洗记录，196 个学校/年份/文档类型汇总组
- 统一清洗包：140,792 条记录，348 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，171 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：148 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch75 清洗表 36 条；Excel `Public_Records` 140,792 行。

## 2026-05-24 追加进展：batch74 北京缺口高校

batch74 继续补北京艺术类院校缺口。中央戏剧学院官方 PDF 可直接抓取并结构化；北京服装学院种子实时跳转 404 页面，中央美术学院 PDF 直链返回 404，北京电影学院研究生院页面返回 412，均隔离未并入。本批还修正了一个清洗边界：官方脱敏姓名如 `*芷名` 末尾含“名”时，不再误判为表头字段。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch74.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch74/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch74/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch74/school_year_summary.csv`

batch74 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 中央戏剧学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 95 |

可追溯来源：

- 中央戏剧学院 2026 年接收推荐免试攻读硕士学位研究生拟录取名单公示：`https://chntheatre.edu.cn/Uploads/Cad/Picture/2025/10/13/001.%E4%B8%AD%E5%A4%AE%E6%88%8F%E5%89%A7%E5%AD%A6%E9%99%A2%202026%20%E5%B9%B4%E6%8E%A5%E6%94%B6%E6%8E%A8%E8%8D%90%E5%85%8D%E8%AF%95%E6%94%BB%E8%AF%BB%E7%A1%95%E5%A3%AB%E5%AD%A6%E4%BD%8D%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95%E5%85%AC%E7%A4%BA.20251013100734.pdf`

本批合并后交付版：

- B 类官网总表：135,046 条清洗记录，194 个学校/年份/文档类型汇总组
- 统一清洗包：140,756 条记录，346 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，169 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：148 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch74 清洗表 95 条；Excel `Public_Records` 140,756 行。

## 2026-05-24 追加进展：batch73c 北京缺口高校

batch73 继续补北京覆盖缺口学校。中央民族大学页面在浏览器可见，但爬虫访问页面返回 404；其 21 个官方附件直链均返回验证码下载页，暂不并入。北京语言大学页面可访问，但附件同样返回验证码下载页，页面正文误抽到 footer 链接，本批新增 footer 导航标签过滤规则后清洗为 0 条。随后 `batch73c` 改用中央音乐学院官方正文页，页面直接列出 2026 年硕士推免生拟录取名单，成功结构化 95 条。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch73.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch73b.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch73c.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73b/documents.jsonl`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch73c/school_year_summary.csv`

batch73c 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 中央音乐学院 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 95 |

可追溯来源：

- 中央音乐学院 2026 年硕士推免生拟录取名单：`https://www.ccom.edu.cn/info/10711/258051.htm`

本批合并后交付版：

- B 类官网总表：134,951 条清洗记录，193 个学校/年份/文档类型汇总组
- 统一清洗包：140,661 条记录，345 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，168 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：147 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0、排名表头残留 0；batch73c 清洗表 95 条；Excel `Public_Records` 140,661 行。

## 2026-05-24 追加进展：batch72b 北京缺口高校

batch72 继续补北京覆盖缺口学校。首轮人大旧域名实时返回 404，法大研究生院页面出现动态挑战，北航若干学院旧路径返回 404，均隔离未并入。随后 `batch72b` 改用北航真实学院页和官方 PDF 直链，成功结构化经济管理学院、宇航学院 2026 年拟推免生名单。化学学院 PDF 和机械学院附件本轮未抽到人员记录，暂不并入。

本批还补充了一个清洗规则：PDF 表格抽取中如果 `ranking` 字段残留 `专业`、`专业排名` 等表头词，会在解析/清洗阶段清空，避免列头进入可用字段。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch72.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch72b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch72b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch72b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch72b/school_year_summary.csv`

batch72b 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 北京航空航天大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 128 |

可追溯来源：

- 北航经济管理学院 2026 年拟推免生名单 PDF：`https://sem.buaa.edu.cn/__local/E/B8/97/77956D5A542FB4D8E1CE763C7FF_FA52EDC9_2C085.pdf`
- 北航宇航学院 2026 年拟推免生名单 PDF：`https://www.sa.buaa.edu.cn/__local/E/90/F3/5C92854D30AE5036697E11FCF28_6864631E_1B81F.pdf`

本批合并后交付版：

- B 类官网总表：134,856 条清洗记录，192 个学校/年份/文档类型汇总组
- 统一清洗包：140,566 条记录，344 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，167 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：146 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch72b 清洗表 128 条；Excel `Public_Records` 140,566 行。

## 2026-05-24 追加进展：batch71 北京缺口高校

batch71 转向北京覆盖缺口学校。北京工商大学教务处中心公示页面可访问，正文说明 2026 届本科生推免资格结果，并提供 `公示名单.xlsx` 附件。附件结构为 `正式（256人）` 与 `候补` 两列姓名；本批新增 Excel 状态姓名列解析规则，只将正式名单并入 B 类主表，候补人员不进入正式推荐记录。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch71.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch71/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch71/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch71/school_year_summary.csv`

batch71 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 北京工商大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 256 |

可追溯来源：

- 北京工商大学教务处 2026 年应届本科毕业生拟获推免资格名单公示：`https://jwc.btbu.edu.cn/jwkw/yjstm/ae2e1fd7667043dd9983b4b3b086744a.htm`
- 公示名单附件：`https://jwc.btbu.edu.cn/docs/2025-09/96a96ec18a6145bba2ee34bc19a9f5b9.xlsx`

本批合并后交付版：

- B 类官网总表：134,728 条清洗记录，191 个学校/年份/文档类型汇总组
- 统一清洗包：140,438 条记录，343 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，166 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：144 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch71 清洗表 256 条；Excel `Public_Records` 140,438 行。

## 2026-05-24 追加进展：batch70c 辽宁缺口高校

batch70 转向辽宁覆盖缺口学校。首轮沈阳农业大学植物保护学院、水利学院、动物科学与医学学院旧路径均返回 404/502；校验搜索索引后修正了植物保护学院和动物科学与医学学院真实 URL，并额外验证沈阳师范大学文学院页面。动物科学与医学学院表格存在合并单元格错位，沈阳师范大学文学院页面误抽到推免工作小组成员，均隔离未并入。最终 `batch70c` 仅并入沈阳农业大学植物保护学院人员级名单。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch70c.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch70c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch70c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch70c/school_year_summary.csv`

batch70c 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 沈阳农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 21 |

本批合并后交付版：

- B 类官网总表：134,472 条清洗记录，190 个学校/年份/文档类型汇总组
- 统一清洗包：140,182 条记录，342 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，165 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：143 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch70c 清洗表 21 条；Excel `Public_Records` 140,182 行。

## 2026-05-24 追加进展：batch69c 湖北缺口高校

batch69 继续补湖北覆盖缺口学校。华中师范大学页面可访问但附件为验证码下载，暂不结构化；中南民族大学、湖北大学网络空间安全学院的搜索命中路径实时返回 404。最终 `batch69c` 并入湖北大学楚才学院官网正文名单。该页面为“学生名单公示如下：姓名串 / 候补名单”的版式，本批新增普通正文名单解析规则，并在“候补名单”处停止，避免把候补人员并入正式推荐名单。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch69b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch69c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch69c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch69c/school_year_summary.csv`

batch69c 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 湖北大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 20 |

本批合并后交付版：

- B 类官网总表：134,451 条清洗记录，189 个学校/年份/文档类型汇总组
- 统一清洗包：140,161 条记录，341 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，164 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：143 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch69c 清洗表 20 条；Excel `Public_Records` 140,161 行。

## 2026-05-24 追加进展：batch68b 湖北缺口高校

batch68 先尝试从武汉大学信息管理学院、动力与机械学院、物理学院首页追踪 2026 届推免公告；首页会暴露大量新闻/导航上下文，已隔离未并入。随后改用明确的武汉大学信息管理学院公告原文作为 `batch68b`，正文为“专业名称 / 推免名单 / 专业 / 人数 / 姓名串”的竖排行结构。本批新增结构化正文行解析规则，支持该版式并过滤括号内“工程硕博专项”等说明。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch68b.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch68b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch68b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch68b/school_year_summary.csv`

batch68b 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 武汉大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 65 |

本批合并后交付版：

- B 类官网总表：134,431 条清洗记录，188 个学校/年份/文档类型汇总组
- 统一清洗包：140,141 条记录，340 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，163 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：142 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch68b 清洗表 65 条；Excel `Public_Records` 140,141 行。

## 2026-05-24 追加进展：batch67d 湖北缺口高校

本批转向湖北覆盖缺口学校。首轮验证武汉理工大学、中国地质大学（武汉）、武汉工程大学研究生院、武汉科技大学医学院、江汉大学、三峡大学等入口；武汉理工大学名单为 96MB 扫描版 PDF，CUG/WIT 研究生院附件返回验证码下载桥页，江汉大学/三峡大学/武汉科技大学医学院部分搜索命中实时 404/410，暂不并入。随后改用学院官网正文名单和可直链 PDF，最终并入武汉工程大学化工与制药学院、武汉科技大学 6 个学院来源。

本批新增导航容器过滤规则，避免 `nav/menu/aside/sidebar/header/footer` 中的“招生专业、培养动态”等导航项被正文名单解析误收；管理学院二级表头/合并单元格表暂时隔离，未并入。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch67d.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch67d/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch67d/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch67d/school_year_summary.csv`

batch67d 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 武汉工程大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 35 |
| 武汉科技大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 101 |

本批合并后交付版：

- B 类官网总表：134,366 条清洗记录，187 个学校/年份/文档类型汇总组
- 统一清洗包：140,076 条记录，339 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，162 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：141 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch67d 清洗表 136 条；Excel `Public_Records` 140,076 行。

## 2026-05-24 追加进展：batch66b 江苏缺口高校

本批继续补江苏覆盖缺口学校，验证南京农业大学、苏州大学、江苏大学、南京财经大学、南京理工大学、南京医科大学等入口。江苏大学、南京财经大学附件下载仍返回验证码页；南京理工大学、南京医科大学部分搜索命中实时返回站点提示页或无效文章参数，暂不并入。南京农业大学外国语学院、农学院正文名单可稳定抽取；苏州大学音乐学院两个 PDF 直链可直接下载并解析。

本批新增 HTML 正文名单解析规则，支持“专业：姓名 姓名”和“专业：”后姓名单独成段的版式；重跑时使用 `batch66b`、`max-depth 0`，避免把“工作方案”等非名单页面通过上一篇/下一篇链接带入。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch66.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch66b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch66b/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch66b/school_year_summary.csv`

batch66b 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 南京农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 126 |
| 苏州大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 13 |

本批合并后交付版：

- B 类官网总表：134,230 条清洗记录，185 个学校/年份/文档类型汇总组
- 统一清洗包：139,940 条记录，337 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，160 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：140 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch66b 清洗表 139 条；Excel `Public_Records` 139,940 行。

## 2026-05-24 追加进展：batch65c 江苏缺口高校

本批转向江苏覆盖缺口学校，验证江苏科技大学、常州大学、南京邮电大学、江苏大学等入口。江苏大学公告入口实时 404；南京邮电大学信息公开列表可访问，但自动追到的 2021 年“推免生拟录取人数统计”不是人员级名单，清洗阶段未并入。江苏科技大学经济管理学院、船舶与海洋工程学院、机械工程学院 PDF 以及海洋学院 HTML 表格可稳定解析；常州大学推免名单为正文表格。

本批新增江苏科技大学复试排序 PDF 行解析规则，并增加回归测试，避免多列表头断裂时将姓名、考生编号和专业字段错位。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch65.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch65c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch65c/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch65c/school_year_summary.csv`

batch65c 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 江苏科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 649 |
| 常州大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 7 |

本批合并后交付版：

- B 类官网总表：134,091 条清洗记录，183 个学校/年份/文档类型汇总组
- 统一清洗包：139,801 条记录，335 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，158 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：138 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch65c 清洗表 656 条；Excel `Public_Records` 139,801 行。

## 2026-05-24 追加进展：batch64 上海缺口高校

本批转向上海覆盖缺口学校，验证上海音乐学院、上海理工大学、上海体育大学、华东政法大学、上海对外经贸大学、上海财经大学、华东理工大学、同济大学、上海中医药大学、上海师范大学、华东师范大学、上海海事大学、上海应用技术大学等入口。上海理工大学理学院 PDF 直链实时 404；华东理工大学、上海师范大学等页面仅保留公告正文/图片或动态查询入口；最终可稳定结构化的是上海音乐学院和上海对外经贸大学。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch64.csv`

产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch64/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch64/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch64/school_year_summary.csv`

batch64 清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 上海对外经贸大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,200 |
| 上海对外经贸大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 21 |
| 上海音乐学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 227 |
| 上海音乐学院 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 94 |

本批合并后交付版：

- B 类官网总表：133,435 条清洗记录，181 个学校/年份/文档类型汇总组
- 统一清洗包：139,145 条记录，333 个学校/年份/来源汇总组
- 覆盖追踪：430 所院校，156 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：137 个测试通过
- 全量质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；batch64 清洗表 2,542 条；Excel `Public_Records` 139,145 行。

## 新增抓取批次

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260522.csv`

抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260522/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260522/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260522/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260522/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260522/graduate_outcome_failures.jsonl`

新增批次中可结构化出数的主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 华南师范大学 | 2026 | 推免/接收推免名单页 | 73 |
| 上海交通大学 | 2026 | 推免/接收推免名单页 | 59 |
| 长沙理工大学 | 2026 | 推免名单页 | 3 |
| 长沙理工大学 | 2025 | 研究生录取名单页 | 22 |

本批失败入口：

- 太原理工大学研究生院：证书域名不匹配。
- 吉林大学研究生院：SSL 握手超时。
- 西北大学：搜索结果页面返回 404。
- 中国社会科学院大学：搜索结果页面返回 404。

## 当前 B 类官网总表汇总

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 湖南师范大学 | 2026 | postgraduate_admission_list | 3,877 |
| 广西大学 | 2025 | postgraduate_admission_list | 3,377 |
| 河北工业大学 | 2026 | postgraduate_admission_list | 3,244 |
| 贵州大学 | 2026 | postgraduate_admission_list | 5,076 |
| 华南农业大学 | 2026 | postgraduate_admission_list | 4,231 |
| 山西大学 | 2026 | incoming_recommendation_admission_list | 391 |
| 河北地质大学 | 2026 | postgraduate_admission_list | 883 |
| 河北工业大学 | 2026 | incoming_recommendation_admission_list | 365 |
| 河北地质大学 | 2026 | incoming_recommendation_admission_list | 13 |
| 昆明医科大学 | 2026 | postgraduate_admission_list | 2,083 |
| 河北师范大学 | 2026 | postgraduate_admission_list | 1,684 |
| 贵州中医药大学 | 2026 | postgraduate_admission_list | 1,531 |
| 安徽中医药大学 | 2026 | postgraduate_admission_list | 1,409 |
| 江西中医药大学 | 2026 | postgraduate_admission_list | 1,359 |
| 广西中医药大学 | 2026 | postgraduate_admission_list | 989 |
| 湖南中医药大学 | 2026 | postgraduate_admission_list | 628 |
| 广西民族大学 | 2026 | postgraduate_admission_list | 512 |
| 广西大学 | 2026 | postgraduate_admission_list | 475 |
| 广西大学 | 2026 | incoming_recommendation_admission_list | 201 |
| 东华大学 | 2026 | postgraduate_admission_list | 2,521 |
| 上海电力大学 | 2026 | postgraduate_admission_list | 696 |
| 杭州电子科技大学 | 2026 | postgraduate_admission_list | 547 |
| 河南大学 | 2026 | incoming_recommendation_admission_list | 312 |
| 北方工业大学 | 2026 | postgraduate_admission_list | 216 |
| 延安大学 | 2026 | recommendation_exemption_list | 196 |
| 上海交通大学 | 2026 | recommendation_exemption_list | 89 |
| 燕山大学 | 2026 | recommendation_exemption_list | 84 |
| 湘潭大学 | 2026 | recommendation_exemption_list | 78 |
| 华南师范大学 | 2026 | recommendation_exemption_list | 73 |
| 西南财经大学 | 2026 | recommendation_exemption_list | 46 |
| 安徽工业大学 | 2026 | recommendation_exemption_list | 32 |
| 上海海洋大学 | 2026 | recommendation_exemption_list | 30 |
| 西安建筑科技大学 | 2026 | recommendation_exemption_list | 26 |
| 苏州科技大学 | 2026 | recommendation_exemption_list | 24 |
| 长沙理工大学 | 2025 | postgraduate_admission_list | 22 |
| 华北水利水电大学 | 2026 | recommendation_exemption_list | 19 |
| 上海大学 | 2026 | recommendation_exemption_list | 18 |
| 内蒙古医科大学 | 2026 | incoming_recommendation_admission_list | 18 |
| 四川农业大学 | 2026 | incoming_recommendation_admission_list | 13 |
| 成都中医药大学 | 2026 | incoming_recommendation_admission_list | 6 |
| 华南农业大学 | 2026 | recommendation_exemption_list | 28 |
| 上海工程技术大学 | 2026 | postgraduate_admission_list | 2,266 |
| 上海对外经贸大学 | 2026 | postgraduate_admission_list | 2,200 |
| 上海音乐学院 | 2026 | postgraduate_admission_list | 227 |
| 上海音乐学院 | 2026 | incoming_recommendation_admission_list | 94 |
| 上海对外经贸大学 | 2026 | incoming_recommendation_admission_list | 21 |
| 江苏科技大学 | 2026 | postgraduate_admission_list | 649 |
| 常州大学 | 2026 | recommendation_exemption_list | 7 |
| 南京农业大学 | 2026 | recommendation_exemption_list | 126 |
| 苏州大学 | 2026 | recommendation_exemption_list | 13 |
| 西安理工大学 | 2026 | postgraduate_admission_list | 3,165 |
| 西安科技大学 | 2026 | postgraduate_admission_list | 2,385 |
| 天津师范大学 | 2026 | postgraduate_admission_list | 58 |
| 天津师范大学 | 2026 | incoming_recommendation_admission_list | 15 |
| 闽南师范大学 | 2026 | postgraduate_admission_list | 9 |
| 长沙理工大学 | 2026 | recommendation_exemption_list | 3 |

## 本轮验证过的发现通道

- 高校官网目录入口：从公开高校官网目录匹配到 430 所有保研资格学校官网入口，可作为后续学校清单底座。
- 学校首页/门户扫链：命中率低，本轮前 20 所学校没有新增可用名单种子。
- 常见教务/本科生院入口探测：已加入候选入口生成，如 `dean.*`、`jwc.*`、`/jwc/`、`/bks/`，但真实小样本仍受 SSL/慢站影响。
- Bing RSS：返回大量 Microsoft/Office 噪声，不适合批量发现。
- Bing HTML：触发 Turnstile 验证，不适合无登录批量发现。
- DuckDuckGo HTML：触发 bot challenge，不适合无登录批量发现。
- Web 搜索命中结果手工入种子：目前最有效，本轮 17 个种子产出 157 条清洗记录。

## 可追溯来源示例

- 昆明医科大学 2026 年硕士研究生拟录取名单公示：https://www.kmmc.cn/Pages_320_60032.aspx
- 湖南师范大学 2026 年硕士研究生拟录取名单 PDF：https://yjsy.hunnu.edu.cn/__local/8/CC/35/F6403C4A83ABD86B4E526FCD947_D3122556_E4493.pdf
- 杭州电子科技大学 2026 年硕士研究生调剂待录取名单 Excel：https://grs.hdu.edu.cn/_upload/article/files/b4/9b/5e47907d4d1a90eb009768309737/37e33fec-6572-465c-bb9d-8018827b21ec.xlsx
- 河南大学 2026 年推免生攻读研究生拟录取名单 PDF：https://grs.henu.edu.cn/__local/0/9C/CC/AB1D35D70B8A30DAD92EBA0C546_E22DB7AE_2967E.pdf
- 河北师范大学 2026 年硕士研究生拟录取名单一志愿 PDF：https://yjsy.hebtu.edu.cn/dynamic/download.jsp?id=74f8a79ac01f41a591cef805c52541f9
- 河北工业大学 2026 年推免研究生拟录取名单公示：https://yjs.hebut.edu.cn/zsgz/zzsszszl/gszl3/3fb67fe563ed4e9d873c86f6cf81a9e6.htm
- 河北工业大学 2026 年硕士生调剂考生拟录取名单公示：https://yjs.hebut.edu.cn/zsgz/ssyjszszl/gszl1/562872aec6a24596b47d8ddf0e005054.htm
- 河北地质大学 2026 年硕士研究生招生复试拟录取名单 PDF：https://www.hgu.edu.cn/__local/8/55/3D/7BFA2BB25DC13CDAEB509F1B9D5_45D1FA28_BC070.pdf
- 河北地质大学 2026 年硕士研究生招生推免生拟录取名单公示：https://yjsxy.hgu.edu.cn/info/1026/2156.htm
- 河北地质大学 2026 年硕士研究生招生推免生拟录取名单 PDF：https://yjsxy.hgu.edu.cn/__local/D/40/F6/3B87BE1737DDB97E8C9B9427A5E_51DAD33F_D288.pdf
- 广西大学 2026 年接收推荐免试研究生拟录取名单公示：https://yjsc.gxu.edu.cn/info/1007/4172.htm
- 广西大学 2026 年博士研究生第一批（一）拟录取名单公示：https://yjsc.gxu.edu.cn/info/1021/4496.htm
- 广西大学 2025 年硕士研究生招生一志愿考生拟录取名单公示：https://yjsc.gxu.edu.cn/info/1007/3714.htm
- 广西大学 2025 年硕士研究生招生调剂复试拟录取名单公示：https://yjsc.gxu.edu.cn/info/1007/3807.htm
- 广西民族大学 2026 年硕士研究生招生专题页：https://yjs.gxmzu.edu.cn/info/1081/23594.htm
- 广西民族大学民族学与社会学学院 2026 年硕士研究生招生第一志愿拟录取名单公示：https://msy.gxmzu.edu.cn/info/1003/60147.htm
- 广西民族大学民族学与社会学学院 2026 年硕士研究生招生调剂拟录取名单 PDF：https://msy.gxmzu.edu.cn/__local/A/1A/31/E32FAD8320D319477196694A452_290B747B_23182.pdf
- 山西大学 2026 年推免生（含直博生）拟录取名单 PDF：https://yjszsw.sxu.edu.cn/docs/2025-10/6a4533211f9c40bb91203ff9e820b553.pdf
- 内蒙古医科大学 2026 年接收推荐免试研究生拟录取名单公示：https://yjsy.immu.edu.cn/info/1051/5165.htm
- 成都中医药大学现代中药产业学院 2026 年推免生拟录取名单（第一批）：https://www.cdutcm.edu.cn/xdzycyxy/info/1161/1851.htm
- 四川农业大学马克思主义学院 2026 年接收推免研究生拟录取结果公示：https://mkszyxy.sicau.edu.cn/info/1841/11156.htm
- 四川农业大学机电学院 2026 年推免研究生招生拟录取名单公示：https://jdxy.sicau.edu.cn/info/1033/3874.htm
- 贵州大学 2026 年硕士研究生拟录取名单公示（一）：https://gs.gzu.edu.cn/2026/0402/c11835a266982/pagem.htm
- 贵州大学 2026 年硕士研究生拟录取名单公示（二）：https://gs.gzu.edu.cn/2026/0408/c11835a267217/pagem.htm
- 贵州大学 2026 年硕士研究生拟录取名单公示（三）：https://gs.gzu.edu.cn/2026/0421/c11835a271324/pagem.htm
- 贵州大学 2026 年硕士研究生拟录取名单公示（四）：https://gs.gzu.edu.cn/2026/0423/c11835a271647/pagem.htm
- 贵州大学 2026 年硕士研究生拟录取名单公示（五）：https://gs.gzu.edu.cn/2026/0427/c11835a271881/pagem.htm
- 华南农业大学 2026 年硕士研究生拟录取公示页：https://yzb.scau.edu.cn/2026/0506/c2138a433804/page.htm
- 华南农业大学 2026 年硕士研究生拟录取名单 PDF：https://yzb.scau.edu.cn/_upload/article/files/6f/06/fe14ac6047c992bd27926c92c962/0f244edf-4464-4a6c-9c30-7496d69f5fc9.pdf
- 华南农业大学 2026 年拟录取推荐免试直博生名单公示页：https://yzb.scau.edu.cn/2025/1022/c2137a420201/page.htm
- 华南农业大学 2026 年拟录取推荐免试直博生名单 PDF：https://yzb.scau.edu.cn/_upload/article/files/b3/7e/16cc77f64791807ec0ae9abe5cac/abc129f3-e625-457d-b3b2-f71fccee97b9.pdf
- 天津师范大学心理学部 2026 年硕士研究生拟录取名单公示：https://psych.tjnu.edu.cn/info/1044/3699.htm
- 天津师范大学体育科学学院 2026 年硕士研究生拟录取名单 PDF：https://tykx.tjnu.edu.cn/__local/7/76/DE/5107A13CFEA618D4F8C386790C5_F7D8746C_1A6B4.pdf
- 天津师范大学政治与行政学院 2026 年接收推免硕士研究生拟录取名单 PDF：https://zzyxz.tjnu.edu.cn/__local/4/77/24/76137066967FB3D96473FB18B7E_FA31512A_252F0.pdf
- 闽南师范大学新闻传播学院 2026 年硕士研究生一志愿拟录取名单公示：https://sjc.mnnu.edu.cn/info/1058/7074.htm
- 上海工程技术大学艺术设计学院 2026 年硕士研究生招生复试成绩及拟录取名单公示页：https://xb.sues.edu.cn/84/05/c25048a295941/page.htm
- 上海工程技术大学 2026 年硕士研究生拟录取公示名单 PDF：https://xb.sues.edu.cn/_upload/article/files/c4/f8/703297f445029fec10c863354a89/b4cf6bd6-663c-4f12-974c-62d9af275ed1.pdf
- 上海音乐学院 2026 年硕士研究生拟录取名单 PDF：https://yjsb.shcmusic.edu.cn/_upload/article/files/f4/02/813646224fff8e987ebe5d623cd1/6378ef38-d182-48bf-820a-a0b1f83fd80d.pdf
- 上海音乐学院 2026 年推免生拟录取名单 PDF：https://yjsb.shcmusic.edu.cn/_upload/article/files/1a/50/2f399c5c4f7a97976c98d83bd435/362b48e0-1601-426f-aac2-7343fcc50ca7.pdf
- 上海对外经贸大学 2026 年硕士待录取名单第一批 PDF：https://www.suibe.edu.cn/_upload/article/files/0c/ce/bebeee46488ab48790cd01bb17f8/0dcc12e0-0827-480d-b60f-13bbf85fdef7.pdf
- 上海对外经贸大学 2026 年硕士研究生待录取名单第二批 PDF：https://www.suibe.edu.cn/_upload/article/files/ff/83/63e04e3445aa9ffceea17302a145/fddafa62-db21-4312-9563-95235a6e93b0.pdf
- 上海对外经贸大学 2026 年接收推荐免试研究生拟录取名单 PDF：https://www.suibe.edu.cn/_upload/article/files/0f/e6/d7852cd84fbd9cf45e46f5a9770b/eba14a72-121d-42da-a36e-c9cc66bbea55.pdf
- 江苏科技大学海洋学院 2026 年硕士研究生招生调剂补录公示：https://ocean.just.edu.cn/2026/0413/c10660a372170/page.htm
- 江苏科技大学经济管理学院 2026 硕士研究生复试拟录取名单 PDF：https://sem.just.edu.cn/_upload/article/files/65/02/edbb71c547f79ac7e9beec7bd3b1/9455ab54-b177-4b8d-8ca0-c952081f215a.pdf
- 江苏科技大学船舶与海洋工程学院 2026 硕士研究生复试拟录取名单 PDF：https://naoe.just.edu.cn/_upload/article/files/13/a2/d321e0c1480eb3a7fac0eefd1a6e/d7ccf873-0698-48f0-a912-f2a21a545277.pdf
- 江苏科技大学机械工程学院 2026 硕士研究生复试拟录取名单 PDF：https://jixie.just.edu.cn/_upload/article/files/05/7d/fa748fe3411a89b1563f39e2e528/8b0437aa-382d-49f4-9aa8-8437c2fa1648.pdf
- 常州大学 2026 年拟接收推荐免试研究生名单：https://gs.cczu.edu.cn/2025/1030/c13235a403294/page.htm
- 南京农业大学外国语学院 2026 年推荐优秀应届本科毕业生免试攻读研究生拟推荐名单公示：https://foreign.njau.edu.cn/info/1053/6846.htm
- 南京农业大学农学院 2026 年推荐优秀应届本科毕业生免试攻读研究生拟推荐名单公示：https://nx.njau.edu.cn/info/1112/10565.htm
- 苏州大学音乐学院 2026 年推荐优秀应届本科毕业生免试攻读研究生公示页：https://music.suda.edu.cn/4b/ef/c9903a674799/page.htm
- 苏州大学音乐学院音乐表演专业推免初选名单 PDF：https://music.suda.edu.cn/_upload/article/files/07/2f/5427ae054892a1febec7b0ed277a/478cb752-e4ab-4d41-a2bb-b653830447c3.pdf
- 苏州大学音乐学院音乐学专业推免初选名单 PDF：https://music.suda.edu.cn/_upload/article/files/07/2f/5427ae054892a1febec7b0ed277a/9c89fe41-dbcc-4d95-b6c1-379edb40b0ed.pdf
- 西安科技大学 2026 年硕士研究生拟录取名单公示：https://yjs.xust.edu.cn/info/1200/7691.htm
- 西安理工大学 2026 年硕士研究生拟录取名单公示页：https://yjsy.xaut.edu.cn/info/1064/4984.htm
- 西安理工大学 2026 年硕士研究生拟录取名单 PDF：https://yjsy.xaut.edu.cn/__local/D/AE/29/1A7661F34F67418399A88D88B3F_60D17CE1_1970E1.pdf
- 安徽中医药大学 2026 年硕士研究生一志愿复试结果及录取名单：https://yjsb.ahtcm.edu.cn/info/1381/73801.htm
- 贵州中医药大学 2026 年硕士研究生招生考试拟录取名单公示：https://yjs.gzy.edu.cn/info/2034/2602.htm
- 广西中医药大学 2026 年硕士研究生招生考试第一批次拟录取名单 PDF：https://www.gxtcmu.edu.cn/upload/yjsy/contentmanage/article/file/2026/03/30/%E5%B9%BF%E8%A5%BF%E4%B8%AD%E5%8C%BB%E8%8D%AF%E5%A4%A7%E5%AD%A62026%E5%B9%B4%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9B%E7%94%9F%E8%80%83%E8%AF%95%E7%AC%AC%E4%B8%80%E6%89%B9%E6%AC%A1%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95%E5%85%AC%E7%A4%BA%EF%BC%88%E5%8F%91%E5%B8%83%E5%AE%98%E7%BD%91%EF%BC%89.pdf
- 湖南中医药大学 2026 年硕士研究生招生考试一志愿考生拟录取名单 PDF：https://yjsy.hnucm.edu.cn/__local/9/4E/A7/CB732256BCE87CC56A4F2C4BCE9_6BD103BD_3B120.pdf
- 江西中医药大学 2026 年硕士研究生拟录取名单公示：https://yjsy.jxutcm.edu.cn/info/1041/20245.htm
- 中山大学智能工程学院：https://ise.sysu.edu.cn/article/1558
- 华南师范大学数学科学学院：https://maths.scnu.edu.cn/a/20250925/8484.html
- 上海交通大学设计学院：https://designschool.sjtu.edu.cn/dynamic/notice/detail/68f59251e8e233cad44211ec
- 华中师范大学教务处：https://jwc.ccnu.edu.cn/info/1102/26541.htm
- 青岛理工大学教务处：https://jw.qut.edu.cn/info/1005/4453.htm
- 长沙理工大学教务处：https://www.csust.edu.cn/jwc/info/1101/7257.htm
- 高校官网目录来源：https://laosheng.top/fuwu/yuanxiao

## 重要边界

1. 公开 HTML 表格、正文名单最容易结构化。
2. PDF 附件已经能保存，但部分高校 PDF 字体编码导致文本抽取乱码，目前不强行写入清洗表。
3. `download.jsp` 类附件有时返回验证码/中转页，脚本会保存证据，但不能在无人机验证码输入的情况下直接拿到 Excel。
4. 当前结果是“已命中的官网名单样本”，还不是 430 所保研资格院校底表的全量覆盖。

## 2026-05-24 追加进展：batch62

本批继续补覆盖表缺口院校。华中师范大学页面可访问，但附件下载返回 HTML 中转页，暂不能形成文本层名单；青岛理工大学入口实时 404，西南交通大学入口实时 502。西安科技大学官网 HTML 名单和西安理工大学研究生院 PDF 名单均可稳定解析。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch62.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch62/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch62/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch62/school_year_summary.csv`

batch62 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 西安科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,385 |
| 西安理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,165 |

同步更新（历史记录，batch65c 后规模以上方最新交付版为准）：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：130,893 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：130,893 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：177 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：136,603 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：136,603 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，154 所已精确匹配官网记录，276 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 136,603 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：137 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；Excel `Public_Records` 136,603 行

## 2026-05-24 追加进展：batch61

本批继续补覆盖表缺口院校。厦门大学多个搜索入口实时返回 404，上海对外经贸大学和上海海事大学入口返回 410，天津大学、山东财经大学页面及附件未形成结构化记录；上海工程技术大学艺术设计学院页面挂出的校级 2026 年硕士研究生拟录取公示名单 PDF 可直接下载并稳定解析。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch61.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch61/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch61/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch61/school_year_summary.csv`

batch61 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 上海工程技术大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,266 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：125,343 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：125,343 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：174 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：131,053 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：131,053 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，152 所已精确匹配官网记录，278 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 131,053 行

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：137 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；Excel `Public_Records` 131,053 行

## 2026-05-24 追加进展：batch60

本批继续补覆盖表缺口院校。北京工商大学 PDF、福建师范大学页面等入口已抓取留证，但未从文本层形成可靠清洗记录；天津师范大学心理学部 HTML、体育科学学院 PDF、政治与行政学院推免 PDF，以及闽南师范大学新闻传播学院 HTML 表格可稳定解析并并入主表。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch60.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch60/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch60/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch60/school_year_summary.csv`

batch60 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 天津师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 58 |
| 天津师范大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 15 |
| 闽南师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 9 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：123,077 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：123,077 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：173 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：128,787 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：128,787 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，151 所已精确匹配官网记录，279 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 128,787 行

质量修正：

- 过滤 PDF 表格中被误抽到姓名列的单独括号说明项，如“（定向、非定向）”，避免培养类型说明进入人员身份字段。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：137 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；Excel `Public_Records` 128,787 行

## 2026-05-24 追加进展：batch59

本批继续补覆盖表缺口院校。华中师范大学、华东师范大学本轮 seed URL 返回 404，未并入清洗表；华南农业大学研究生招生信息网的 2026 年硕士拟录取公示和推荐免试直博生名单公示均提供可直接下载的 PDF 附件，可稳定解析。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch59.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch59_final/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch59_final/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch59_final/school_year_summary.csv`

batch59 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 华南农业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4,231 |
| 华南农业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 28 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：122,995 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：122,995 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：170 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：128,705 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：128,705 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，149 所已精确匹配官网记录，281 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 128,705 行

质量修正：

- 修正通用表格解析中的错位行：当“专业代码|专业名”被 PDF 抽取到姓名列时，不再作为姓名入库，而是转入录取专业并标记复核。
- 过滤无姓名且 `student_id` 不是编号的短续行，避免专业/研究方向残片误入身份字段。
- 修正 Excel 构建脚本在超过 12 万行时对 `Math.max(...rows.map(...))` 的调用栈溢出问题。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：136 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0、无姓名且非编号 student_id 0；Excel `Public_Records` 128,705 行

## 2026-05-24 追加进展：batch57/batch58

本批继续补覆盖表缺口院校。河北大学、北京航空航天大学、东北林业大学及四川农业大学资源学院等页面本身可访问，但名单附件进入验证码下载页或中转页，不能无人值守取得真实文件；四川农业大学马克思主义学院、机电学院页面提供 HTML 表格，贵州大学研究生院硕士招生栏目提供 2026 年硕士拟录取名单（一）至（五）PDF 附件，均可稳定抓取并结构化。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch57.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch58.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch57_fixed/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch57_fixed/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch58/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch58/records_public.csv`

batch57/58 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 四川农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 13 |
| 贵州大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 5,076 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：118,736 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：118,736 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：168 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：124,446 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：124,446 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，148 所已精确匹配官网记录，282 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 124,446 行

质量修正：

- 修正正文段落名单解析：不再把“学院专业”这类泛化标题当作专业名，避免从“择优遴选”等正文措辞中误提取伪人名。
- 贵州大学 5 个 PDF 附件由现有表格解析规则提取考生编号、姓名、学院、录取专业、初试/复试/总成绩等字段；batch58 清洗后 `needs_review` 为 0。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：134 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0；Excel `Public_Records` 124,446 行

## 2026-05-24 追加进展：batch56

本批继续补覆盖表缺口院校。前置验证中，北京语言大学、西南林业大学、大连海事大学、大连医科大学、大连理工大学等页面虽然有公示入口，但附件下载返回验证码/中转页，不能无人值守取得真实名单文件；东北电力大学部分搜索命中页返回 404；北京工商大学、北京协和医学院等入口未直接给出可结构化名单。最终采用 3 个可直接解析的官方源：山西大学 PDF 直链、内蒙古医科大学研究生院 HTML 表格、成都中医药大学现代中药产业学院 HTML 表格。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch56.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch56_final/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch56_final/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch56_final/school_year_summary.csv`

batch56 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 山西大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 391 |
| 内蒙古医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 18 |
| 成都中医药大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 6 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：113,647 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：113,647 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：166 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：119,357 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：119,357 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，146 所已精确匹配官网记录，284 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 119,357 行

质量修正：

- 增加山西大学 2026 年推免 PDF 7 列表解析，提取排名、姓名、录取层次、录取学院、专业代码、专业名称和复试成绩；清洗后 1-391 序号连续。
- 修正“推免生（含直博生）拟录取名单”标题分类，避免被普通“拟录取名单”关键词归入统考拟录取。
- 增加成都中医药大学 HTML 表格解析，补齐现代中药产业学院、专业代码及名称、研究方向、综合面试成绩和导师字段。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：133 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0；batch56 清洗表 `needs_review` 0；Excel `Public_Records` 119,357 行

## 2026-05-24 追加进展：batch54

本批选择覆盖表仍缺口的广西大学。广西大学研究生院官网硕士招生列表中 2026 年硕士统考主公示搜索命中链接当前返回 404；但 2026 年接收推免生拟录取名单、2026 年博士研究生第一批三份拟录取名单、2025 年硕士一志愿/调剂/补录等公示页和附件可稳定抓取。少数民族骨干计划 PDF 存在姓名、考号、专项类型跨多行碎裂，本轮暂不并入清洗表，以避免产生无姓名伪记录。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch54.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch54_fixed/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch54_fixed/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch54_fixed/school_year_summary.csv`

batch54 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 广西大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,377 |
| 广西大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 201 |
| 广西大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 475 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：113,232 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：113,232 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：163 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：118,942 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：118,942 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，143 所已精确匹配官网记录，287 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 118,942 行

质量修正：

- 增加广西大学推免 PDF 定宽表解析，提取姓名、录取学院、录取专业、招生类型、计划、学习方式、研究方向、录取类别和复试成绩。
- 增加广西大学博士拟录取 PDF 解析，处理“学院+成绩”粘连列。
- 增加广西大学 2025 年硕士拟录取 PDF 解析，覆盖一志愿、调剂和补录的多种拆分表头。
- 对广西大学 PDF 未命中专用解析时停止回退通用表格解析，避免把无姓名记录并入清洗表。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：130 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0；batch54 清洗表姓名为空 0、`needs_review` 0；Excel `Public_Records` 118,942 行

## 2026-05-24 追加进展：batch53

本批选择覆盖表仍缺口的广西民族大学。该校研究生院 2026 年硕士招生专题页集中列出学院级推免拟录取、一志愿拟录取和调剂拟录取公示页，适合作为官方目录源。实际抓取中，部分学院附件为 `download.jsp` 中转，直接下载不能拿到真实文件；可结构化数据主要来自学院页内嵌的 VSB `__local` 静态 PDF。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch53.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch53/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch53/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch53/school_year_summary.csv`

batch53 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 广西民族大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 512 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：109,179 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：109,179 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：160 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：114,889 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：114,889 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，142 所已精确匹配官网记录，288 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 114,889 行

质量修正：

- 增加广西民族大学拟录取 PDF 宽表解析，处理“序号、复试批次、考生编号、姓名、专业代码及名称、研究方向、拟录取情况、总成绩、排名”等字段。
- 过滤学院页 HTML 中的“关闭窗口、当前位置、快速通道、通知公告、详细信息”等导航残片，避免误入人员记录。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：128 个测试通过
- 质量扫描：缺少身份 0、表头/科目/导航误入姓名 0、数字姓名 0；Excel `Public_Records` 114,889 行

## 2026-05-24 追加进展：batch52

本批从覆盖表仍缺口的高校继续验证官方源。大连理工大学、大连海事大学和河北经贸大学等候选页面的附件入口返回验证码或 `download.jsp` 中转页；东北师范大学外部查询页未直接给出可解析名单。河北地质大学官网和研究生学院站点提供静态 PDF，适合无人值守抓取，因此进入本批。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch52.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch52/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch52/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch52/school_year_summary.csv`

batch52 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 河北地质大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 13 |
| 河北地质大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 883 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：108,667 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：108,667 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：159 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：114,377 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：114,377 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，141 所已精确匹配官网记录，289 所暂未匹配
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 114,377 行

质量修正：

- 增加河北地质大学硕士拟录取 PDF 专用解析，处理水印把行拆开的情况，清洗后序号 1-883 连续。
- 增加河北地质大学推免 PDF 解析，拆出姓名、本科生学号、二级招生单位、专业和复试总成绩。
- 修正非人名过滤顺序，保留带有效编号的合法中文姓名，避免“王浩名”这类真实姓名被表头规则误删。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：126 个测试通过
- 质量扫描：缺少身份 0、表头/科目姓名 0、数字姓名 0；Excel `Public_Records` 114,377 行

## 2026-05-24 追加进展：batch51

本批先从覆盖表仍缺口的高校中验证候选源。北航、大连医科、大连外国语的附件入口会返回验证码页或 `download.jsp` 中转页，北京工商大学页面只保留公示说明，不适合作为无人值守批量源；河北工业大学研究生院公示页可直接抓取详情页和静态 PDF，进入本批。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch51.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch51_v3/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch51_v3/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch51_v3/school_year_summary.csv`

batch51 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 河北工业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 365 |
| 河北工业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,244 |

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：107,771 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：107,771 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：157 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：113,481 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：113,481 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，140 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 113,481 行

质量修正：

- 增加河北工业大学 PDF 专用宽表解析，保留学院、录取专业、考生编号、姓名、复试/初试/总成绩。
- 将“推免研究生拟录取名单”识别为接收推免名单，附件继承父页面/种子的招生年份。
- 跳过“录取人数”汇总表，并过滤“性别”等表头碎片误入姓名列。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：123 个测试通过
- 质量扫描：缺少身份 0、表头/科目姓名 0、数字姓名 0；Excel `Public_Records` 113,481 行

## 2026-05-24 追加进展：batch50

本批优先选择“覆盖表仍缺口、且官网源可直接下载/解析”的中医药类院校。安徽中医药大学、贵州中医药大学、江西中医药大学为官网 HTML 大表，广西中医药大学与湖南中医药大学为静态 PDF。候选源中，天津中医药大学页面混有复试成绩表与拟录取表，青岛理工大学页面只保留公告正文，山西中医药大学 `download.jsp` 附件返回中转页，暂未并入本批。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch50.csv`

新增抓取产物：

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

同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：104,163 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：104,163 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：155 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：109,873 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：109,873 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，139 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 109,873 行

质量修正：

- 对 PDF 抽取中“考生编号 + 学院”挤到同一列的情况，自动拆出考生编号。
- 继续过滤“业代码/分制/纯分数”等 PDF 表头碎片误入姓名列。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：117 个测试通过
- 质量扫描：缺少身份 0、缺少核心身份字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0

## 2026-05-24 追加进展：batch49

本批优先选择“此前覆盖表仍缺口、且官方源可直接下载/解析”的院校。昆明医科大学为官网 HTML 大表，湖南师范大学与河南大学为 VSB `__local` PDF，杭州电子科技大学为静态 `_upload` xlsx，河北师范大学为可直接返回 PDF 的动态下载链接。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch49.csv`

新增抓取产物：

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

batch49 当时同步更新：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：98,247 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：98,247 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：150 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：103,957 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：103,957 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，134 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：已同步重建，公开明细 103,957 行

质量修正：

- `.xlsx` 附件即使被服务器声明成 `application/vnd.ms-excel`，也按 zip/xlsx 魔数识别后交给 openpyxl 解析。
- 河南大学“推免生攻读研究生拟录取”标题归入 `incoming_recommendation_admission_list`，并新增对应 PDF 行式解析。
- 剔除“总分/成绩/语听力”等 PDF 表头续行误入姓名列的历史残留。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：115 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0、性别+序号碎片 0

## 2026-05-22 追加进展：batch4

在继续推进 B 类官网名单时，又补充了一批搜索命中的官方 HTML 名单页。相比 PDF 和搜索引擎缓存页，这一批页面正文/表格更稳定，结构化效果明显更好。

新增种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260522_batch4.csv`

新增抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260522_batch4/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260522_batch4/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260522_batch4/school_year_summary.csv`

batch4 抓取结果：

- 种子：11 条
- 实际抓到页面/附件：14 个
- 抓取失败：0 个
- 原始结构化记录：275 条
- 清洗后记录：237 条
- 汇总组：10 个

batch4 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 河南工业大学 | 2026 | recommendation_exemption_list | 53 |
| 河南师范大学 | 2026 | recommendation_exemption_list | 36 |
| 湖北工业大学 | 2026 | recommendation_exemption_list | 33 |
| 东北石油大学 | 2026 | recommendation_exemption_list | 30 |
| 中国科学院大学 | 2026 | recommendation_exemption_list | 27 |
| 中央财经大学 | 2026 | recommendation_exemption_list | 18 |
| 南京体育学院 | 2026 | recommendation_exemption_list | 16 |
| 天津工业大学 | 2026 | recommendation_exemption_list | 12 |
| 遵义医科大学 | 2026 | recommendation_exemption_list | 6 |
| 江西财经大学 | 2026 | recommendation_exemption_list | 6 |

合并后的 B 类官网总表已更新为：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：977 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：977 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：24 个学校/年份/类型汇总组

本轮还增强了 crawler：

- HTTPS 证书错误时先使用不校验证书的 SSL context 重试。
- HTTPS 仍然 SSL EOF/握手失败时，尝试同域名 HTTP 回退。
- 官方站点发现器增加 `--official-site-workers`，可并发探测多所学校，避免慢站拖垮整批。

验证命令：

- `python -m unittest tests.test_graduate_outcome_crawler`
- 当前结果：54 个测试通过。

## 2026-05-22 追加进展：batch5 与统一清洗包

继续使用“搜索命中官网名单页 -> 种子 -> 批量抓取清洗”的路线，新增 batch5：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260522_batch5.csv`
- 抓取产物：`data/processed/graduate_outcomes_official_site_websearch_web_20260522_batch5/`
- 种子：10 条
- 抓到文档：10 个
- 原始结构化记录：305 条
- 清洗记录：305 条
- 汇总组：7 个

batch5 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 上海外国语大学 | 2026 | recommendation_exemption_list | 79 |
| 四川大学 | 2026 | recommendation_exemption_list | 69 |
| 中南大学 | 2026 | recommendation_exemption_list | 60 |
| 郑州大学 | 2026 | recommendation_exemption_list | 32 |
| 内蒙古科技大学 | 2026 | recommendation_exemption_list | 29 |
| 上海交通大学 | 2026 | recommendation_exemption_list | 18 |
| 安徽农业大学 | 2026 | recommendation_exemption_list | 18 |

B 类官网主表随之更新为：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：1,282 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：1,282 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：30 个学校/年份/类型汇总组

同时生成 A+B 统一清洗包：

- `data/cleaned/graduate_outcomes/master_records_clean.csv`：8,854 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：8,854 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：182 行
- 说明文档：`docs/research/graduate_outcome_clean_data_package_2026-05-22.md`

## 2026-05-22 追加进展：batch6

继续追加一批结构化友好的官网 HTML 名单页：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260522_batch6.csv`
- 抓取产物：`data/processed/graduate_outcomes_official_site_websearch_web_20260522_batch6/`
- 种子：10 条
- 抓到页面：11 个
- 原始结构化记录：328 条
- 清洗记录：328 条
- 汇总组：7 个

batch6 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 黑龙江科技大学 | 2026 | recommendation_exemption_list | 157 |
| 北京交通大学 | 2026 | recommendation_exemption_list | 41 |
| 中南大学 | 2026 | recommendation_exemption_list | 35 |
| 中南财经政法大学 | 2026 | recommendation_exemption_list | 34 |
| 南京中医药大学 | 2026 | recommendation_exemption_list | 31 |
| 中北大学 | 2026 | recommendation_exemption_list | 25 |
| 内蒙古科技大学 | 2026 | recommendation_exemption_list | 5 |

B 类官网主表随之更新为：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：1,610 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：1,610 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：35 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：

- `data/cleaned/graduate_outcomes/master_records_clean.csv`：9,182 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：9,182 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：187 行

## 2026-05-22 追加进展：batch7 与 Excel 工作簿

新增 batch7 官网名单页：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260522_batch7.csv`
- 抓取产物：`data/processed/graduate_outcomes_official_site_websearch_web_20260522_batch7/`
- 种子：8 条
- 抓到页面：8 个
- 抓取失败：0 个
- 原始结构化记录：336 条
- 清洗记录：336 条
- 汇总组：7 个

batch7 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 成都信息工程大学 | 2026 | recommendation_exemption_list | 188 |
| 华南师范大学 | 2026 | incoming_recommendation_admission_list | 51 |
| 湖北工业大学 | 2026 | recommendation_exemption_list | 32 |
| 燕山大学 | 2026 | recommendation_exemption_list | 25 |
| 中国社会科学院大学 | 2026 | recommendation_exemption_list | 14 |
| 苏州科技大学 | 2026 | recommendation_exemption_list | 13 |
| 河南中医药大学 | 2026 | recommendation_exemption_list | 13 |

B 类官网主表随之更新为：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：1,946 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：1,946 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：39 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：

- `data/cleaned/graduate_outcomes/master_records_clean.csv`：9,518 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：9,518 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：191 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，37 所已精确匹配官网推免记录

新增 Excel 交付版：

- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch12b 辽宁大学官网 PDF

batch12 面向辽宁未覆盖高校补入口。首轮 batch12 证实辽宁大学 PDF 可访问，但 `pypdf` 提取表格布局不稳定；已补充 `pdftotext -layout` 优先解析、保留多空格列边界、以及“专业代码及名称/研究方向代码及名称”拆列对齐规则。为保留首轮失败证据，成功复跑产物记为 batch12b。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch12.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch12b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch12b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch12b/`

抓取结果：
- 种子：4 条
- 抓到文档/PDF：6 个
- 抓取失败：2 个（沈阳农业大学 404、辽宁师范大学 502）
- 原始结构化记录：401 条
- 清洗记录：352 条
- 汇总组：1 个

batch12b 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 辽宁大学 | 2026 | recommendation_exemption_list | 352 |

可追溯来源示例：

- 辽宁大学研究生院公示页：https://grs.lnu.edu.cn/info/12169/71843.htm
- 辽宁大学附件 PDF：https://grs.lnu.edu.cn/26tmgsmd.pdf
- 大连理工大学研究生院工作动态页：https://gs.dlut.edu.cn/yjszs/gzdt/gzdt/7.htm
- 沈阳农业大学植物保护学院入口：https://zbxy.syau.edu.cn/info/1062/7369.htm
- 辽宁师范大学计算机与人工智能学院入口：https://computer.lnnu.edu.cn/bkjy/jxgz.htm

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：2,759 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：2,759 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：46 个学校/年份/类型汇总组

说明：本次合并重新核对了早期 `direct_probe`、`websearch_probe`、batch2 至 batch12b 的全部 B 源 JSONL，避免遗漏早期官网批次。
- 工作表包括：Overview、Source_Summary、Coverage、Public_Records。

## 2026-05-23 追加进展：batch13c 北京高校官网 PDF/页面

batch13 首先尝试对未覆盖院校做官网主页/教务门户自动探测，但北京前 20-80 所批次被慢站点拖住，未形成稳定种子；随后改用搜索结果驱动，人工筛出可访问的清华大学、北京邮电大学、北京航空航天大学、北京科技大学官网公示入口。batch13b 抓取后发现北邮博士 PDF 有两条记录被 `pdftotext` 换行拆断，导致身份证号进入姓名列；已补充“姓名字段为身份证号式字符串时剔除”的质量规则，并复跑为 batch13c。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch13b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch13c/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch13c/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch13c/`

抓取结果：
- 种子：17 条
- 抓到文档/PDF：15 个
- 抓取失败：7 个（部分清华院系旧链接 404）
- 原始结构化记录：1,965 条
- 清洗记录：1,641 条
- 汇总组：2 个

batch13c 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 北京邮电大学 | 2026 | recommendation_exemption_list | 1432 |
| 清华大学 | 2026 | recommendation_exemption_list | 209 |

可追溯来源示例：

- 清华大学建筑学院公示页：https://www.arch.tsinghua.edu.cn/info/gg/2984
- 清华大学电子工程系 PDF：https://www.ee.tsinghua.edu.cn/__local/5/86/73/D4BAC6FE05443FC1A07060EE09A_A7F3F1C0_1F713.pdf
- 清华大学网络科学与网络空间研究院 PDF：https://www.insc.tsinghua.edu.cn/20251030-1.pdf
- 北京航空航天大学研究生招生信息网公示页：https://yzb.buaa.edu.cn/info/1036/3445.htm
- 北京邮电大学硕士推免 PDF：https://yzb.bupt.edu.cn/2026sstm.pdf
- 北京邮电大学博士推免 PDF：https://yzb.bupt.edu.cn/2026bstm.pdf
- 北京科技大学冶金与生态工程学院公示页：https://metall.ustb.edu.cn/tzgg/9731d142281d4d7baa7545b71d9a5485.htm

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：4,400 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：4,400 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：48 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：11,968 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：11,968 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：200 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，45 所已精确匹配官网推免记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

质量修正：
- 过滤 CHSI/A 源旧表中 4 条“姓名字段为纯证件号式字符串”的错位记录。
- batch13c 复跑后，B 源主表中此类错位姓名记录为 0。

## 2026-05-23 追加进展：batch14 北京高校整校级入口

batch14 继续补北京未覆盖高校，优先使用整校级研究生招生网/推免名单公示入口，减少院系散点重复。抓取后发现北京外国语大学两个入口指向同一批名单，已调整 `_record_dedupe_key()`，跨来源按“学校+年份+类型+路线+姓名/编号+学院+专业”去重，而不再把 `source_url` 当成同一人员同一项目的区分项。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch14.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch14/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch14/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch14/`

抓取结果：
- 种子：8 条
- 抓到文档/页面：9 个
- 抓取失败：1 个（中国农业大学入口 404）
- 原始结构化记录：1,941 条
- 清洗记录：1,373 条
- 汇总组：3 个

batch14 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 北京工业大学 | 2026 | recommendation_exemption_list | 732 |
| 北京外国语大学 | 2026 | incoming_recommendation_admission_list | 564 |
| 中国矿业大学（北京） | 2026 | postgraduate_admission_list | 77 |

可追溯来源示例：

- 北京工业大学公示页：https://yanzhao.bjut.edu.cn/info/1019/17865.htm
- 北京外国语大学硕士推免公示页：https://graduate.bfsu.edu.cn/info/1048/4006.htm
- 北京外国语大学博士推免公示页：https://graduate.bfsu.edu.cn/info/1074/4016.htm
- 中国矿业大学（北京）研究生招生网：https://yz.cumtb.edu.cn/
- 中国政法大学研究生院推免栏目：https://yjsy.cupl.edu.cn/yjszs/ndsszs/tjms.htm
- 北京化工大学研究生招生网：https://graduate.buct.edu.cn/yjszsw/list.htm
- 北京建筑大学公示页：https://yjsy.bucea.edu.cn/zs/zstzgg/e0f3b06c205843428298d48371a858b2.htm

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：6,006 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：6,006 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：51 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：13,574 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：13,574 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：203 行

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch8b

batch8 初版遇到一批搜索缓存旧 URL 返回 404，因此改用当前可访问的官网 URL 重新组成 batch8b：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch8b.csv`
- 抓取产物：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch8b/`
- 种子：5 条
- 抓到页面：5 个
- 抓取失败：0 个
- 原始结构化记录：100 条
- 清洗记录：99 条
- 汇总组：5 个

batch8b 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 河南工业大学 | 2026 | recommendation_exemption_list | 36 |
| 上海外国语大学 | 2026 | recommendation_exemption_list | 27 |
| 中南林业科技大学 | 2026 | recommendation_exemption_list | 17 |
| 中南大学 | 2026 | recommendation_exemption_list | 11 |
| 郑州大学 | 2026 | recommendation_exemption_list | 8 |

B 类官网主表随之更新为：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：2,045 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：2,045 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：40 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：

- `data/cleaned/graduate_outcomes/master_records_clean.csv`：9,617 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：9,617 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：192 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，38 所已精确匹配官网推免记录

Excel 交付版已同步重建：

- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch11

batch11 使用江苏未覆盖高校的官网列表页作为入口，验证列表页自动跟进详情页的效果：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch11.csv`
- 抓取产物：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch11/`
- 种子：8 条
- 抓到页面：15 个
- 抓取失败：1 个
- 原始结构化记录：32 条
- 清洗记录：32 条
- 汇总组：1 个

batch11 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 东南大学 | 2025 | recommendation_exemption_list | 32 |

B 类官网主表随之更新为：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：2,407 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：2,407 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：45 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：

- `data/cleaned/graduate_outcomes/master_records_clean.csv`：9,979 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：9,979 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：197 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，42 所已精确匹配官网推免记录

Excel 交付版已同步重建：

- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch10b

batch10 初版尝试北京地区研究生院/统一入口时，多数 URL 返回 404/412。随后改用学院实际可访问页面组成 batch10b：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch10b.csv`
- 抓取产物：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch10b/`
- 种子：5 条
- 抓到页面/PDF：4 个
- 抓取失败：1 个
- 原始结构化记录：241 条
- 清洗记录：241 条
- 汇总组：2 个

batch10b 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 北京理工大学 | 2026 | recommendation_exemption_list | 171 |
| 北京理工大学 | 2026 | incoming_recommendation_admission_list | 70 |

B 类官网主表随之更新为：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：2,375 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：2,375 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：44 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：

- `data/cleaned/graduate_outcomes/master_records_clean.csv`：9,947 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：9,947 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：196 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，41 所已精确匹配官网推免记录

Excel 交付版已同步重建：

- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch9

batch9 重点补安徽地区保研资格院校官网页面：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch9.csv`
- 抓取产物：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch9/`
- 种子：7 条
- 抓到页面/附件：8 个
- 抓取失败：0 个
- 原始结构化记录：89 条
- 清洗记录：89 条
- 汇总组：2 个

batch9 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 合肥工业大学 | 2026 | recommendation_exemption_list | 83 |
| 安徽师范大学 | 2026 | recommendation_exemption_list | 6 |

B 类官网主表随之更新为：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：2,134 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：2,134 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：42 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：

- `data/cleaned/graduate_outcomes/master_records_clean.csv`：9,706 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：9,706 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：194 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，40 所已精确匹配官网推免记录

Excel 交付版已同步重建：

- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 最新状态：batch12b 合并后

- B 类官网主表：2,759 条，46 个学校/年份/类型汇总组
- A+B 统一清洗包：10,331 条，198 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，43 所已精确匹配官网推免记录
- Excel 交付版已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`
- crawler 测试：`python -m unittest tests.test_graduate_outcome_crawler`，58 个测试通过

## 2026-05-23 追加进展：batch15 / batch15b 北京高校官网入口

batch15 继续补北京高校官网 B 源，入口包括中国传媒大学信息公开列表、北京语言大学推免拟录取公告、北京中医药大学推免拟录取公告、中国地质大学（北京）研究生院/院系公示页，以及中国石油大学（北京）研究生院和多个学院公示页。中国传媒大学公告页的名单 PDF 通过 `pdfsrc` 嵌入，补跑 batch15b 使用 PDF 直达链接抽取。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch15.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch15b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch15/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch15b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch15/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch15b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch15/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch15b/`

抓取结果：
- batch15：种子 12 条，抓到文档/页面 26 个，抓取失败 1 个，原始结构化记录 1,151 条，清洗记录 1,109 条
- batch15b：种子 4 条，抓到文档 3 个，抓取失败 1 个，原始结构化记录 2,249 条，清洗记录 2,191 条
- 两批合计新增清洗记录：3,300 条

batch15 / batch15b 清洗后主要来源：

| 学校 | 年份 | 类型 | 记录数 |
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

可追溯来源示例：

- 中国传媒大学 2026 推免 PDF：https://yz.cuc.edu.cn/_upload/article/files/eb/d1/936c84234eb6bb9db365bd9b62fb/69de9c96-d1d1-483c-a318-2fce72c3eae6.pdf
- 中国传媒大学 2026 硕士一志愿 PDF：https://yz.cuc.edu.cn/_upload/article/files/cf/90/3d0847db4b29a69224357ed857d2/ba252736-5b6f-4d5e-a309-49400abd4ed6.pdf
- 中国传媒大学 2026 硕士调剂 PDF：https://yz.cuc.edu.cn/_upload/article/files/8d/26/d503f1d44fea82eaf18f5af2394b/2d43489d-ab1f-417c-9f38-1602506f4491.pdf
- 北京中医药大学推免 PDF：https://yanjiusheng.bucm.edu.cn/docs/2025-10/4507a4b2fdd942bfa334fc1af0e45300.pdf
- 中国地质大学（北京）科学研究院 PDF：https://bm.cugb.edu.cn/yjsyzsb/upload/resources/file/2025/09/30/274567.pdf
- 中国石油大学（北京）研究生院汇总页：https://grs.cup.edu.cn/zssstzgg/91291.jhtml

未入库/失败说明：
- 北京语言大学公告页可访问，但附件下载页要求验证码，本轮无法自动结构化抽取。
- 中国石油大学（北京）机械与储运工程学院入口返回 404。
- 中国地质大学（北京）海洋学院补充入口返回 404。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：9,306 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：9,306 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：60 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：16,874 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：16,874 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：212 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，52 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-24 追加进展：北京 batch48

batch48 针对北方工业大学官网 2026 年各学院/专业复试结果继续补人员级拟录取记录。该校研究生院总页公开了各学院入口，但实际数据分散在多个学院子域名；部分学院页面通过 `showVsbpdfIframe(...)` 嵌入 PDF。本轮新增 VSB PDF iframe 附件发现规则，并新增“学科专业代码/名称 + 学习方式 + 考生编号/姓名 + 成绩 + 是否拟录取”版式解析，只保留“是否拟录取=是”的行。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch48.csv`

抓取/清洗产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch48/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch48/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch48/school_year_summary.csv`

batch48 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 北方工业大学 | 2026 | postgraduate_admission_list | 216 |

未入库/失败说明：
- 电气与控制工程学院 4 个入口、人工智能与计算机学院 1 个入口实时返回 404。
- 理学院 2 个附件为下载桥页，无法直接结构化。

最新交付版：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：89,745 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：89,745 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：145 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：95,455 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：95,455 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：297 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，129 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：公开明细 95,455 行、汇总 297 行、覆盖追踪 430 行

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：110 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0、性别+序号碎片 0

## 2026-05-24 追加进展：上海 batch47

batch47 继续针对覆盖缺口院校补官网人员级名单。本批补入东华大学、上海电力大学 2 所学校：东华大学公告页可自动跟到内嵌 PDF，并新增“学院代码 + 学院名 + masked 考生号 + 姓名 + 学位类型 + 专业代码/名称 + 成绩”版式解析；上海电力大学第二批、第三批官网 PDF 可直接下载，但源文件只公开姓名、考试编号、成绩、专项计划、报考类别和学习方式，不含专业字段，已如实保留专业为空并将成绩写入备注。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch47.csv`

抓取/清洗产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch47/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch47/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch47/school_year_summary.csv`

batch47 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 东华大学 | 2026 | postgraduate_admission_list | 2,521 |
| 上海电力大学 | 2026 | postgraduate_admission_list | 696 |

最新交付版：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：89,531 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：89,531 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：144 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：95,241 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：95,241 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：296 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，128 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：公开明细 95,241 行、汇总 296 行、覆盖追踪 430 行

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：107 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0、性别+序号碎片 0

## 2026-05-24 追加进展：安徽/海南/辽宁/湖北 batch46

batch46 继续针对覆盖缺口院校补官网人员级名单。本批补入安徽理工大学、海南大学、大连交通大学、长江大学 4 所学校：长江大学两批硕士拟录取 PDF 与免试攻读研究生拟录取 PDF 已新增专项解析；安徽理工大学 PDF 使用“学院代码 + 学院名 + 专业代码/名称 + 考生编号/姓名 + 成绩”版式解析；海南大学推免 PDF 和大连交通大学推免 HTML 表格进入清洗表。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch46.csv`

抓取/清洗产物：
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
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：86,314 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：86,314 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：142 个学校/年份/类型汇总组
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：92,024 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：92,024 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：294 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，126 所已精确匹配官网记录
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`：公开明细 92,024 行、汇总 294 行、覆盖追踪 430 行

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：105 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头/科目姓名 0、碎片学号 0、性别+序号碎片 0

## 2026-05-24 追加进展：安徽/福建/云南 batch42

batch42 继续补当前未覆盖院校中可静态解析的官网名单入口，重点使用官方 PDF 直链和可自动跟到附件的官网公示页。福州大学、云南财经大学、安徽建筑大学、安徽医科大学均形成可用人员级记录；南京财经大学官网公示页本轮已检查，页面正文未暴露名单表或附件，暂不入库。

本批还新增两条清洗回归规则：剔除“专业代码进入姓名列、学院名进入学号列”的 PDF 错位行，以及“工程/院”“工程/信息工程大学）”这类由学院/专业换行导致的断词残片。清洗后批次质量扫描中数字姓名、表头姓名和断词残片均为 0。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch42.csv`

抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch42/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch42/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch42/school_year_summary.csv`

抓取结果：

- 种子 5 条，抓到页面/附件 5 个，原始结构化记录 9,285 条，清洗记录 7,925 条，抓取失败 1 个。
- 安徽建筑大学本科教务推免公示页实时返回 502；研究生院硕士拟录取公示页自动跟到 PDF 并入库。

batch42 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 福州大学 | 2026 | postgraduate_admission_list | 5293 |
| 云南财经大学 | 2026 | postgraduate_admission_list | 1810 |
| 安徽建筑大学 | 2026 | postgraduate_admission_list | 819 |
| 安徽医科大学 | 2026 | postgraduate_admission_list | 3 |

可追溯来源：

- 福州大学 2026 年硕士研究生招生拟录取名单公示页：https://yjsy.fzu.edu.cn/info/1077/5901.htm
- 福州大学 2026 年硕士研究生招生拟录取名单 PDF：https://yjsy.fzu.edu.cn/system/_content/download.jsp?owner=1744984943&urltype=news.DownloadAttachUrl&wbfileid=18265061
- 云南财经大学 2026 年硕士研究生招生一志愿拟录取名单 PDF：https://www.ynufe.edu.cn/__local/D/B2/1A/F363D5CBFD24DD547DC3EAA8072_CCC20BB7_A9F2B.pdf
- 安徽建筑大学 2026 年硕士研究生一志愿拟录取名单公示：https://www.ahjzu.edu.cn/yjsc/_t131/2026/0427/c5263a269249/page.htm
- 安徽建筑大学拟录取名单 PDF：https://www.ahjzu.edu.cn/_upload/article/files/01/61/294374d34766b97570b5f6c03a1d/b853dc05-f08d-440e-8e92-d73176acdbf7.pdf
- 安徽医科大学第一附属医院 2026 年硕士生招生调剂二轮复试结果及拟录取名单 PDF：https://www.ayfy.com/__local/0/AD/5A/3C02C79D52B6AC047DB196C80DB_A062B827_91F3.pdf

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：58,879 条，121 个学校/年份/类型汇总组
- A+B 统一清洗包：64,589 条，273 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，107 所已精确匹配官网记录

验证：

- 新增回归测试：专业代码/学院名错位行剔除；学院/专业换行断词残片剔除。
- batch42 批次质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头姓名 0、断词残片 0。
- 工作簿重建输出：公开明细 64,589 行、汇总 273 行、覆盖追踪 430 行。

## 2026-05-24 追加进展：黑龙江/湖南/江苏 batch43

batch43 转向黑龙江、湖南、江苏和北京的未覆盖院校，入口包括哈尔滨工业大学、哈尔滨医科大学、黑龙江中医药大学、哈尔滨体育学院、哈尔滨师范大学、湖南师范大学、湖南农业大学、江南大学、北京工商大学。可直接形成清洗记录的是哈尔滨工业大学 PDF、湖南农业大学 PDF、江南大学食品学院 PDF；其它页面或附件下载桥页已抓取留证，但当前未形成静态可解析人员级名单。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch43.csv`

抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch43/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch43/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch43/school_year_summary.csv`

抓取结果：

- 种子 9 条，抓到页面/附件 16 个，原始结构化记录 3,321 条，清洗记录 3,192 条，抓取失败 0 个。

batch43 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 湖南农业大学 | 2026 | postgraduate_admission_list | 2815 |
| 江南大学 | 2026 | postgraduate_admission_list | 301 |
| 哈尔滨工业大学 | 2026 | postgraduate_admission_list | 76 |

可追溯来源：

- 哈尔滨工业大学 2026 年硕士研究生招生考试拟录取名单 PDF：https://sa.hit.edu.cn/_upload/article/files/44/0d/bc5caca740649aaa03609adbffd5/0d01e1fa-ec0c-48e2-99b1-a3c97362322b.pdf
- 湖南农业大学 2026 年硕士研究生招生拟录取名单公示页：https://yjsy.hunau.edu.cn/yjszs/sszs/zytz_1592/202604/t20260430_518203.html
- 湖南农业大学 2026 年硕士研究生拟录取名单 PDF：https://yjsy.hunau.edu.cn/yjszs/sszs/zytz_1592/202604/P020260430631407939267.pdf
- 江南大学食品学院 2026 年硕士研究生建议录取名单：https://foodsci.jiangnan.edu.cn/info/1172/19005.htm
- 江南大学食品学院拟录取名单 PDF：https://foodsci.jiangnan.edu.cn/__local/3/C5/56/1F8BADBFFBD02A2C8D0742408AD_D08B694D_244CB.pdf

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：62,071 条，124 个学校/年份/类型汇总组
- A+B 统一清洗包：67,781 条，276 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，110 所已精确匹配官网记录

验证：

- batch43 批次质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头姓名 0、断词残片 0。
- 工作簿重建输出：公开明细 67,781 行、汇总 276 行、覆盖追踪 430 行。

## 2026-05-24 追加进展：陕西/北京/重庆 batch45

batch45 继续使用可直接下载的官方 PDF 直链，并纳入可静态解析的官网 HTML 表格。成功入库西北农林科技大学、西北大学、西北工业大学、北京建筑大学、西南政法大学 5 所学校的 2026 年推免/硕士拟录取人员级名单。西安交通大学医学部 PDF、天津师范大学经济学院 PDF 已抓取留证，但当前文本层未形成稳定清洗记录。本轮新增西南政法大学“两行一条记录”PDF 解析规则、北京建筑大学拆分表头 PDF 解析规则，并补充回归测试。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch45.csv`

抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch45_final/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch45_final/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch45_final/school_year_summary.csv`

抓取结果：

- 种子 11 条，抓到页面/附件 12 个，原始结构化记录 7,840 条，清洗记录 4,196 条，抓取失败 0 个。

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

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：81,963 条，137 个学校/年份/类型汇总组
- A+B 统一清洗包：87,673 条，289 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，122 所已精确匹配官网记录

验证：

- batch45 批次质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头姓名 0、性别+序号碎片 0。
- 工作簿重建输出：公开明细 87,673 行、汇总 289 行、覆盖追踪 430 行。

## 2026-05-24 追加进展：湖北/江西/重庆 batch44

batch44 转向实时可下载的官方 PDF 直链，避免验证码附件桥页。成功入库华中农业大学、南昌大学、江西农业大学、南昌航空大学、江西理工大学、重庆大学、四川外国语大学的 2026 年硕士拟录取人员级名单；四川农业大学管理学院 PDF 虽可下载，但当前解析未形成稳定人员级记录。重庆大学统考 PDF 存在字段错位，清洗阶段已新增“脱敏身份证号+性别/真实姓名错位”修复测试；同时剔除推免 PDF 中“女 001”这类性别+序号碎片。四川外国语大学 PDF 存在成绩列前置导致“分数进入姓名列”的错位，已补充清洗修复。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch44.csv`

抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch44/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch44/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch44/school_year_summary.csv`

抓取结果：

- 种子 24 条，抓到页面/附件 24 个，原始结构化记录 20,113 条，清洗记录 15,696 条，抓取失败 0 个。

batch44 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 南昌大学 | 2026 | postgraduate_admission_list | 5597 |
| 重庆大学 | 2026 | postgraduate_admission_list | 4038 |
| 华中农业大学 | 2026 | postgraduate_admission_list | 2883 |
| 江西农业大学 | 2026 | postgraduate_admission_list | 1601 |
| 南昌航空大学 | 2026 | postgraduate_admission_list | 1528 |
| 四川外国语大学 | 2026 | postgraduate_admission_list | 25 |
| 江西理工大学 | 2026 | postgraduate_admission_list | 24 |

可追溯来源：

- 华中农业大学 2026 年硕士研究生招生拟录取名单直链 PDF（示例）：https://yjs.hzau.edu.cn/301ssnlq2026.pdf
- 南昌大学 2026 年硕士研究生分学院拟录取名单 PDF：https://yjsy.ncu.edu.cn/__local/1/40/DD/D4363BDFFF0E263221936E949A8_19E1FF08_ECD9D.pdf
- 江西农业大学 2026 年硕士研究生拟录取名单 PDF：https://yzb.jxau.edu.cn/__local/C/49/9C/C0B42CFD28F6B06CDBB5D794103_FF810152_6DDF3.pdf
- 南昌航空大学 2026 年硕士研究生拟录取名单 PDF：https://yjs.nchu.edu.cn/upload/yjs/contentmanage/article/file/2026/04/30/%E5%8D%97%E6%98%8C%E8%88%AA%E7%A9%BA%E5%A4%A7%E5%AD%A62026%E5%B9%B4%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95.pdf?t=1777552560888
- 重庆大学 2026 年硕士研究生拟录取名单 PDF：https://yz.cqu.edu.cn/upload/202605/4b1f5c4d.pdf
- 四川外国语大学 2026 年硕士研究生拟录取名单 PDF：https://graduate.sisu.edu.cn/docs/2026-03/99977a52496d44c5a3a1c14e6c5d131c.pdf

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：77,767 条，131 个学校/年份/类型汇总组
- A+B 统一清洗包：83,477 条，283 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，117 所已精确匹配官网记录

验证：

- batch44 批次质量扫描：缺少身份 0、缺少核心字段 0、未知文档类型 0、数字姓名 0、表头姓名 0、性别+序号碎片 0。
- 工作簿重建输出：公开明细 83,477 行、汇总 283 行、覆盖追踪 430 行。

## 2026-05-24 追加进展：上海 batch40/batch40b 与中科大 batch41

batch40/batch40b 继续排查上海未覆盖高校入口。华东理工大学研究生院列表和详情页可抓取，但名单正文主要以图片页形式嵌入，当前文本/PDF 解析链路无法直接形成可靠人员级记录；上海海事大学、上海科技大学部分搜索入口实时返回 410；上海理工大学入口返回站点提示页。该批保留原始页面和失败日志，作为后续 OCR 或人工下载补抓边界。

batch41 转向可静态解析的中国科学技术大学学院/实验室公示页，成功从 HTML 表格补入 2026 年硕士研究生拟录取名单 1 条。

种子文件：

- `data/seeds/official_site_recommendation_websearch_web_20260524_batch40.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch40b.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260524_batch41.csv`

抓取产物：

- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch40/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch40b/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch41/`

batch41 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 中国科学技术大学 | 2026 | postgraduate_admission_list | 1 |

可追溯来源：

- 中国科学技术大学精准智能化学全国重点实验室 2026 年硕士研究生拟录取名单：https://pichem.ustc.edu.cn/2026/0402/c40930a725330/page.htm
- 华东理工大学研究生院招生录取列表：https://gschool.ecust.edu.cn/12750/list.htm
- 华东理工大学 2026 年硕士研究生拟录取名单公示：https://gschool.ecust.edu.cn/2026/0506/c12750a190107/page.htm
- 华东理工大学 2026 年推免生拟录取名单公示：https://gschool.ecust.edu.cn/2025/1021/c12750a183665/page.htm

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：50,996 条，116 个学校/年份/类型汇总组
- A+B 统一清洗包：56,706 条，268 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，103 所已精确匹配官网记录

验证：

- batch41 抓取：1 个种子，抓到 1 个页面，原始结构化记录 1 条，清洗记录 1 条，失败 0 个。
- 工作簿重建输出：公开明细 56,706 行、汇总 268 行、覆盖追踪 430 行。

## 2026-05-24 追加进展：广东 batch35 与验证码/权限边界复核

本轮先复核了广东高校入口。暨南大学 2026 级硕士拟录取名单公示页在搜索索引中可见，且 HEAD 请求返回 200，但正文 GET 返回“无效的文章参数(02)”错误页；页面公开的 45 个 xlsx 附件直链在本地返回 403，即使带站点 cookie 和 referer 仍不能静态下载。北京航空航天大学 2026 推免拟录取公告页可访问，但硕士/博士 PDF 附件均进入验证码下载桥页，未进入人员级主表。

随后使用广东工业大学研究生招生网公开 PDF 直链作为 batch35，成功补入广东工业大学 2026 年推免生拟录取名单 330 条清洗记录。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260524_batch35.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch35/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch35/records_public.csv`

batch35 新增可用清洗记录：330 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 广东工业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 330 |

可追溯来源：

- 暨南大学 2026 级硕士研究生拟录取名单公示：https://yz.jnu.edu.cn/2026/0403/c33059a853000/page.htm
- 北京航空航天大学接收推荐免试攻读 2026 年研究生拟录取名单公示：https://yzb.buaa.edu.cn/info/1036/3445.htm
- 广东工业大学 2026 年推免生拟录取名单 PDF：https://yzw.gdut.edu.cn/guangdonggongyedaxue2026niantuimianshengniluqumingdangongshi.pdf

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：43,347 条，109 个学校/年份/类型汇总组
- A+B 统一清洗包：49,057 条，261 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，96 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：92 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩/科目碎片 0、计划文本残留于考生编号 0、未知文档类型 0、长姓名无编号可疑项 0

## 2026-05-24 追加进展：广东 batch37 海大/广大入口

batch37 继续补广东未覆盖高校。本批使用广东海洋大学研究生院“硕士生招生信息”列表页及其 2026 年拟录取/推免相关详情页，以及广州大学建筑与城市规划学院、管理学院公告入口。广东海洋大学列表页可静态发现调剂、一志愿、退役士兵专项、推免等页面；其中退役士兵专项计划调剂考生拟录取名单为 HTML 表格，成功抽取 31 条清洗记录。广州大学建筑与城市规划学院调剂考生待录取名单为 HTML 表格，成功抽取 20 条；管理学院列表页本轮跟到的是转专业拟录取公示，清洗后未进入研究生人员级主表。

重建主表时同步补充“业务课一/业务课二”考试科目表头碎片清洗规则，并剔除中国石油大学（北京）历史记录中的 1 条“业务课一/外语”错位行。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260524_batch37.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch37/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch37/records_public.csv`

batch37 新增可用清洗记录：51 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 广东海洋大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 31 |
| 广州大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 20 |

可追溯来源：

- 广东海洋大学硕士生招生信息列表：https://grs.gdou.edu.cn/zsgz/ssszsxx.htm
- 广东海洋大学 2026 年退役士兵专项计划调剂考生拟录取名单：https://grs.gdou.edu.cn/info/1029/7931.htm
- 广东海洋大学 2026 年硕士研究生拟录取名单（调剂）公示：https://grs.gdou.edu.cn/info/1029/7991.htm
- 广东海洋大学 2026 年推荐免试研究生拟录取名单公示：https://grs.gdou.edu.cn/info/1029/7493.htm
- 广州大学 2026 年硕士研究生调剂考生待录取名单（建筑与城市规划学院）：https://arch.gzhu.edu.cn/info/1047/12975.htm
- 广州大学管理学院通知公告列表：https://bas.gzhu.edu.cn/index/tzgg/18.htm

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：43,400 条，112 个学校/年份/类型汇总组
- A+B 统一清洗包：49,110 条，264 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，99 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：92 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩/科目碎片（含“业务课一/外语”）0、计划文本残留于考生编号 0、未知文档类型 0、长姓名无编号可疑项 0

## 2026-05-24 追加进展：广东 batch38 汕大/南科大入口

batch38 继续补广东未覆盖高校，入口包括南方医科大学、汕头大学和南方科技大学。汕头大学 2026 年硕士研究生拟录取名单 PDF 从官网详情页自动跟取成功；南方科技大学 2025 年硕士研究生拟录取名单 PDF 直链可解析。南方医科大学 2026 年统考拟录取与推免拟录取公示页均可访问，但附件在本轮表现为下载桥页，未形成可解析人员级明细。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260524_batch38.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch38/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch38/records_public.csv`

batch38 批次清洗记录：2,796 条；合并进 B 类主表时按 `record_id` 去重后，B 类主表净增 2,794 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 南方科技大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 984 |
| 汕头大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1812 |

可追溯来源：

- 南方科技大学 2025 年硕士研究生拟录取名单 PDF：https://gs.sustech.edu.cn/static/upload/file/20250526/17482477527744.pdf
- 汕头大学 2026 年硕士研究生拟录取名单公示页：https://www.gs.stu.edu.cn/list/11/post/dccff0ab-00bd-4b4b-a6ed-0bc98437c93c
- 汕头大学研究生院招生动态列表：https://www.gs.stu.edu.cn/list/11
- 南方医科大学 2026 年硕士研究生拟录取考生名单公示：https://portal.smu.edu.cn/yzw/info/1031/12211.htm
- 南方医科大学 2026 年招收推荐免试研究生拟录取名单公示：https://portal.smu.edu.cn/yzw/info/1002/11811.htm

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：46,194 条，114 个学校/年份/类型汇总组
- A+B 统一清洗包：51,904 条，266 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，101 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- 批次质量扫描：缺少身份 0、缺少核心字段 0、考试科目表头碎片 0、未知文档类型 0
- 工作簿重建输出：公开明细 51,904 行、汇总 266 行、覆盖追踪 430 行

## 2026-05-24 追加进展：上海 batch39/batch39b 复旦入口

batch39 转向上海未覆盖高校，入口包括复旦大学、华东师范大学、同济大学和上海财经大学。首轮抓取中复旦大学 2026 年考试招生硕士拟录取名单 PDF 成功下载，但通用 PDF 表格解析把“考生编号后五位”误放入姓名列，导致只保留少量错位记录。已新增复旦 PDF 专项解析规则，按“考生编号后五位、脱敏姓名、拟录取院系、初试总成绩、复试成绩、总成绩、备注”恢复人员级记录，并补充脱敏同名但编号不同不得误去重的规则。batch39b 使用干净目录复跑后成功形成可用清洗记录 4,801 条。

华东师范大学与同济大学本轮入口实时返回 404；上海财经大学录取情况列表可访问但未暴露人员级静态表格或附件。复旦推免 `.htm` 入口跳转到 `.psp` 后存在重定向循环，本轮未形成推免明细。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260524_batch39.csv`
- 复旦推免重试种子：`data/seeds/official_site_recommendation_websearch_web_20260524_batch39c.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch39b/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch39b/records_public.csv`

batch39b 新增可用清洗记录：4,801 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 复旦大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4801 |

可追溯来源：

- 复旦大学 2026 年拟录取硕士研究生（不含推荐免试硕士生）名单公示：https://gsao.fudan.edu.cn/e6/ec/c15906a780012/page.htm
- 复旦大学 2026 年考试招生硕士拟录取名单 PDF：https://gsao.fudan.edu.cn/_upload/article/files/d1/72/6e8596f944a29d458e36f9607ff2/2a832c05-0a12-4904-87a0-24ca8cf25633.pdf
- 上海财经大学录取情况列表：https://gongkai.sufe.edu.cn/lqqk/list.htm

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：50,995 条，115 个学校/年份/类型汇总组
- A+B 统一清洗包：56,705 条，267 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，102 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- 新增回归测试：复旦后五位编号 PDF 版式解析；脱敏同名但后五位编号不同保留为不同人员。
- 批次质量扫描：缺少身份 0、数字误入姓名列 0。
- 工作簿重建输出：公开明细 56,705 行、汇总 267 行、覆盖追踪 430 行

## 2026-05-24 追加进展：广东 batch36 广外入口

batch36 继续补广东未覆盖高校，转向广东外语外贸大学研究生招生信息网。官网硕士信息公告列表中可访问的 2026 年拟录取相关页面包括港澳台拟录取名单、硕士拟录取查询通知、统考拟录取名单第二/三批及变动公示。本轮可直接从 HTML 正文表格结构化的是港澳台研究生招生拟录取名单 3 条；统考/调剂名单附件进入 `download.jsp` 验证码下载桥页，未自动抽到附件明细。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260524_batch36.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch36/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch36/records_public.csv`

batch36 新增可用清洗记录：3 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 广东外语外贸大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3 |

可追溯来源：

- 广东外语外贸大学 2026 年港澳台研究生招生拟录取名单公示：https://yz.gdufs.edu.cn/info/1017/2976.htm
- 广东外语外贸大学关于 2026 年硕士（含推免、统考与调剂）拟录取情况查询的通知：https://yz.gdufs.edu.cn/info/1017/2906.htm
- 广东外语外贸大学 2026 年硕士研究生统考拟录取名单（第三批）和调剂拟录取名单公示：https://yz.gdufs.edu.cn/info/1017/2846.htm
- 广东外语外贸大学 2026 年硕士研究生统考拟录取名单（第二批）公示：https://yz.gdufs.edu.cn/info/1017/2806.htm

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：43,350 条，110 个学校/年份/类型汇总组
- A+B 统一清洗包：49,060 条，262 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，97 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`：92 个测试通过
- 质量扫描：缺少身份 0、缺少核心字段 0、姓名疑似表头/成绩/科目碎片 0、计划文本残留于考生编号 0、未知文档类型 0、长姓名无编号可疑项 0

## 2026-05-23 追加进展：batch28 北京高校入口

batch28 继续补北京未覆盖高校入口。本批抓取北京航空航天大学、北京语言大学、中央民族大学、中国政法大学、北京协和医学院、北京体育大学、国际关系学院等官方页面。北航、北语附件下载页返回验证码桥页；中国政法页面返回 JS 动态挑战；中央民族、协和、北体部分详情页返回 404。本轮可直接静态解析并入库的是北京体育大学硕士拟录取名单 PDF 与国际关系学院硕士调剂拟录取名单页面。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch28.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch28/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch28/records_public.csv`

batch28 新增可用清洗记录：1,430 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 北京体育大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 592 |
| 北京体育大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 682 |
| 国际关系学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 156 |

可追溯来源：

- 北京体育大学 2026 年硕士招生调剂考生拟录取名单 PDF：https://zs.bsu.edu.cn/docs/2026-04/aac1528e12484d42a2b441dad2299972.pdf
- 北京体育大学 2026 年硕士研究生（一志愿）拟录取名单 PDF：https://zs.bsu.edu.cn/docs/2026-03/a5366f8d92c34b37abe72e69fdd91cdd.pdf
- 北京体育大学 2025 年硕士研究生（一志愿）拟录取名单 PDF：https://zs.bsu.edu.cn/docs/2025-03/7105c8e1ab284d729be64d90ad6094a1.pdf
- 国际关系学院 2026 年硕士研究生招生考试拟录取名单（调剂）：https://yjszs.uir.cn/info/1421/7631.htm

质量修正：

- 新增清洗规则，把“少干计划/士兵计划/专项计划”等计划类型从 `student_id` 尾部移入 `remarks`，避免计划文本参与考生编号去重。

最新总量：

- A 类 CHSI 主表：5,709 条，151 个学校/年份/类型汇总组
- B 类官网主表：40,862 条，104 个学校/年份/类型汇总组
- A+B 统一清洗包：46,571 条，255 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，91 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch29 北京高校入口

batch29 继续补北京未覆盖高校。本批重点使用官方直链 PDF 与招生公告列表，成功补入北京信息科技大学、北京物资学院、北京联合大学 3 所高校的人员级记录；北京建筑大学 PDF 文本层乱码严重，仅产生表头碎片，已通过清洗规则剔除，暂不入人员级主表。北京信息科技大学推免 PDF、中央美术学院 PDF 返回 404；中央戏剧学院招生公告列表返回 502；中央音乐学院附件页返回下载桥页，未得到静态可解析名单文件。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch29.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch29/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch29/records_public.csv`

batch29 新增可用清洗记录：2,145 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 北京信息科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1312 |
| 北京联合大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 686 |
| 北京物资学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 147 |

可追溯来源：

- 北京信息科技大学 2026 年硕士研究生招生考试拟录取名单 PDF：https://yanjiusheng.bistu.edu.cn/docs/2026-04/8faa7dc22b4342538fc6e82adcdfa02b.pdf
- 北京物资学院经济学院 2026 年硕士研究生调剂拟录取名单公示：https://jjxy.bwu.edu.cn/info/1074/17208.htm
- 北京联合大学 2026 年硕士研究生招生复试录取通知列表：https://graduate.buu.edu.cn/col/col30688/index.html
- 北京联合大学 2026 年硕士研究生拟录取名单 PDF：https://graduate.buu.edu.cn/module/download/downfile.jsp?classid=0&filename=b40da89569424705af6c3f7ef7293bc2.pdf

质量修正：

- 新增碎片表头清洗规则，剔除 PDF 文本层中的“业代码/号”“业务一/外语”“管理类综/英语”等误入人员身份列的行。
- 使用全部 CHSI 原始抓取批次重建 A 类主表，重新剔除历史考试科目表头碎片。

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：43,007 条，107 个学校/年份/类型汇总组
- A+B 统一清洗包：48,717 条，259 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，94 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-24 追加进展：batch30 辽宁高校入口

batch30 转向当前缺口最多的辽宁高校。首轮 batch30 中大连海事大学站点响应缓慢并返回 502，拖住批次；随后将大连海事单独隔离，用 batch30c 先补跑大连理工大学、大连医科大学、沈阳建筑大学等校正后的官方入口。本轮成功补入沈阳建筑大学 2026 年推荐免试硕士研究生拟录取名单 10 条。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260524_batch30.csv`
- 校正种子文件：`data/seeds/official_site_recommendation_websearch_web_20260524_batch30b.csv`
- 可用补跑种子文件：`data/seeds/official_site_recommendation_websearch_web_20260524_batch30c.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch30c/records_clean.csv`
- 批次公开表：`data/processed/graduate_outcomes_official_site_websearch_web_20260524_batch30c/records_public.csv`

batch30c 新增可用清洗记录：10 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 沈阳建筑大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 10 |

可追溯来源：

- 沈阳建筑大学 2026 年推荐免试硕士研究生拟录取名单公示：https://grs.sjzu.edu.cn/info/1174/19359.htm
- 沈阳建筑大学 2026 年推荐免试硕士研究生拟录取名单 PDF：https://gh.sjzu.edu.cn/__local/C/96/18/1032A0F9A70B280174CD2149477_D149B21E_16DEC.pdf

未入库/失败说明：

- 大连海事大学入口 `https://grs.dlmu.edu.cn/info/1139/34211.htm`、`https://grs.dlmu.edu.cn/info/1139/24351.htm` 等在本地抓取中超时或返回 502，已暂时隔离，避免拖住批量任务。
- 大连理工大学、大连医科大学页面可访问，但附件下载页返回桥页/下载页，未得到静态可解析名单文件。
- 沈阳建筑大学建筑与规划学院 PDF 可下载，但 PDF 文本层抽取为表头/空姓名/考号碎片，清洗后不进入人员级主表。

最新总量：

- A 类 CHSI 主表：5,710 条，152 个学校/年份/类型汇总组
- B 类官网主表：43,017 条，108 个学校/年份/类型汇总组
- A+B 统一清洗包：48,727 条，260 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，95 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 质量回扫：性别值误入姓名列

batch26 质检时发现少量历史记录存在姓名列仅为“男/女”的错列行。已新增清洗规则并重建 CHSI 主表、B 类官网主表、统一清洗包和 Excel 工作簿。

重建后当前总量：

- A 类 CHSI 主表：5,728 条，152 个学校/年份/类型汇总组
- B 类官网主表：37,889 条，97 个学校/年份/类型汇总组
- A+B 统一清洗包：43,617 条，249 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，85 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加批次：batch27/batch27c 江苏高校入口

本批次转向江苏未覆盖高校。batch27 成功补入南京信息工程大学、南京航空航天大学和南京艺术学院；batch27c 在修复 TLS/curl 回退、`charset=yaml.NULL` 解码、以及“拟录取名单（不含推荐免试）”误分类后，补入南京大学现代工程与应用科学学院 2026 年硕士统考拟录取名单。

主要产物：

- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch27.csv`
- 种子文件：`data/seeds/official_site_recommendation_websearch_web_20260523_batch27b.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch27/records_clean.csv`
- 批次清洗表：`data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch27c/records_clean.csv`

batch27/batch27c 本轮可用清洗记录合计：1,723 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 南京信息工程大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 776 |
| 南京艺术学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 606 |
| 南京艺术学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 123 |
| 南京航空航天大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 109 |
| 南京大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 109 |

可追溯来源示例：

- 南京信息工程大学 2026 年优秀应届本科毕业生免试攻读研究生拟推荐名单附件：https://jwc.nuist.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1698604008&wbfileid=15396852
- 南京航空航天大学航空学院 2026 届本科毕业生申请推免资格公示名单 PDF：https://aero.nuaa.edu.cn/_upload/article/files/73/a2/463dc2ef4641be88123e5c9f1479/50170a31-2510-4d71-a143-3ea7f3b57387.pdf
- 南京艺术学院 2026 接收推荐免试攻读硕士学位研究生名单 PDF：https://grad.nua.edu.cn/_upload/article/files/e3/b9/1f9058b54203ab6406e1fa34a36b/b34f5d1d-8458-4d15-98c0-3101632a98b7.pdf
- 南京大学现代工学院 2026 年硕士研究生招生复试成绩及拟录取名单（不含推荐免试硕士生）PDF：https://eng.nju.edu.cn/_upload/article/files/b4/a0/327781a54865b56a7a71a8d88c6d/0501bfa0-6e16-4e56-88ab-a75f8bc94ca7.pdf

未入库/失败说明：

- 南京理工大学公告页对 GET 请求实时返回 410；HEAD 可见 200，但正文不可下载，暂不入库。
- 南京大学研究生招生办 70MB 左右的大 PDF 在 35 秒超时内未完整下载；本轮只保留已成功抓取解析的现代工学院 PDF。
- 江苏大学、南京财经大学、南京农业大学、徐州医科大学等入口能抓到页面或附件，但本轮静态解析未形成可用人员级记录；南京邮电大学推免统计页为汇总/人数信息，因缺少人员身份未进入人员级主表。

质量修正：

- 新增 curl 回退和异常编码回退，处理南京大学等站点的 Python TLS/charset 兼容问题。
- 新增“拟录取名单（不含推荐免试）”分类规则，避免统考拟录取 PDF 被误归为推免名单。
- 新增 PDF 表格对齐规则，修复“研究方向组”空列导致分数进入姓名列的问题。
- 进一步剔除分数、推荐书说明、考试科目/面试说明等误入姓名列的历史脏行；保留带中点的少数民族姓名。

质量回扫后最新总量：

- A 类 CHSI 主表：5,709 条，151 个学校/年份/类型汇总组
- B 类官网主表：39,432 条，101 个学校/年份/类型汇总组
- A+B 统一清洗包：45,141 条，252 个学校/年份/类型汇总组
- 覆盖追踪：430 所院校，89 所已精确匹配官网记录
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch26c/26e 黑龙江高校入口

batch26 转向黑龙江未覆盖高校。首轮 batch26c 成功补入东北农业大学、黑龙江八一农垦大学；随后用校正后的官方 PDF/公告入口补跑 batch26e，成功补入哈尔滨工程大学、哈尔滨理工大学。黑龙江中医药大学列表页可访问，但本轮展开链接返回 404 或未形成静态名单记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch26.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch26d.csv`

抓取/解析产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch26c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch26e/records_clean.csv`

batch26c/26e 合并新增清洗记录：1,394 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 东北农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 191 |
| 黑龙江八一农垦大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 39 |
| 哈尔滨工程大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 1111 |
| 哈尔滨理工大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 53 |

可追溯来源：

- 东北农业大学 2026 年拟录取免试攻读硕士研究生名单公示：https://graduate.neau.edu.cn/info/1146/4239.htm
- 黑龙江八一农垦大学 2026 年推免生拟录取名单公示：https://yanjiu.byau.edu.cn/2025/1011/c1415a139945/page.htm
- 黑龙江八一农垦大学名单 PDF：https://yanjiu.byau.edu.cn/_upload/article/files/9a/5f/a901e0514ef7a5547b25788b9cf9/12812a17-ee6b-4935-ba52-be6b79ba1c5b.pdf
- 哈尔滨工程大学 2026 年推荐免试硕士研究生、直博生拟录取名单 PDF：https://yzb.hrbeu.edu.cn/_upload/article/files/8a/2d/36431e0944acb4e0059406b1cb92/3667c458-8867-43d3-98bf-8b5b4c8120cf.pdf
- 哈尔滨理工大学 2026 年拟录取推荐免试研究生名单公示：https://graduate.hrbust.edu.cn/2025/1027/c3907a100470/pagem.htm
- 哈尔滨理工大学名单 PDF：https://graduate.hrbust.edu.cn/_upload/article/files/cb/cb/128f957c428a9effae45c0f17428/3a521490-b850-4af6-8623-70ad833bcbd1.pdf

说明：

- 黑龙江八一农垦 PDF 的学院名有时作为独立行出现，本批次新增“学院段落 + 人员行”解析规则，避免把性别误作姓名。
- 哈尔滨工程和哈尔滨理工 PDF 使用不同的表格结构，本批次新增两类 PDF 行解析规则，以保留“专业代码 + 专业名称”、本科所在单位、拟录取学院、招生类型和成绩等字段。
- 哈尔滨工程旧搜索 PDF 直链返回 404，改用新的官方 PDF 直链后成功解析；哈尔滨理工旧入口返回 404，改用 `pagem.htm` 公告后成功跟进附件。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：37,892 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：37,892 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：97 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：43,641 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：43,641 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：248 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，85 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch25b 吉林高校入口

batch25b 转向吉林未覆盖高校。吉林大学 2026 年接收推免拟录取 PDF、长春工业大学 2026 年推荐免试拟录取 PDF、吉林财经大学公告页成功入库；吉林农业大学列表页扩展到 2025 年拟录取/推免名单并按页面正文年份校正为 2025。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch25b.csv`

抓取/解析产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_combined/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_combined/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_jlu_manual/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_i04/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_i05/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch25b_i06c/`

batch25b 合并清洗后新增记录：3,307 条。

| 学校 | 年份 | 类型 | 路径 | 清洗记录数 |
| --- | --- | --- | --- | ---: |
| 吉林大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 3058 |
| 吉林农业大学 | 2025 | incoming_recommendation_admission_list | recommendation_exemption | 198 |
| 吉林农业大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 33 |
| 吉林财经大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4 |
| 长春工业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 14 |

可追溯来源：

- 吉林大学 2026 年接收推荐免试攻读研究生拟录取名单 PDF：https://yjsy.jlu.edu.cn/__local/1/9F/EB/697526DFBAC1FCAA1C62A8CC626_EF9067B3_2BA725.pdf?e=.pdf
- 吉林财经大学 2026 年推免生复试拟录取名单：https://yzb.jlufe.edu.cn/info/1009/1653.htm
- 长春工业大学 2026 年推荐免试研究生拟录取名单 PDF：https://yjsy.ccut.edu.cn/__local/1/06/26/8BC4BE19A53B2EBA1C01F2DDA9D_CD638202_14DA1.pdf
- 吉林农业大学 2025 年接收推免研究生拟录取名单：https://yjsy.jlau.edu.cn/news.php?nid=573
- 吉林农业大学 2025 年硕士研究生拟录取名单：https://yjsy.jlau.edu.cn/news.php?nid=694

说明：

- batch25 初始搜索直链多处实时返回 404/502，未入库；batch25b 使用可访问的研究生院页面或 PDF 直链分站点重跑。
- 延边大学公告页可访问，但附件下载需要验证码，未形成可解析名单；东北电力大学入口返回 404；长春理工大学列表页抓到多个 XLS 附件，但本轮未形成可用人员级记录。
- 吉林大学 PDF 抽取时“姓名 + 专业代码”存在粘连列，且部分行省略学院名；本批次新增专用 PDF 行解析测试和规则，避免通用表格解析把学院名误当姓名。
- 吉林农业大学列表页含历史公告，本批次新增“正文年份优先于种子年份”的测试和规则，避免把 2025 页面误标为 2026。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：36,498 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：36,498 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：93 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：42,247 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：42,247 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：244 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，81 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch24b 浙江高校入口

batch24b 转向浙江未覆盖高校，入口包括浙江大学、浙江工业大学、浙江理工大学、浙江师范大学、浙江工商大学、浙江财经大学、中国美术学院、杭州师范大学等。浙江工业大学研招网两个 PDF、浙江师范大学外国语学院公示页、浙江大学历史学院 PDF 成功形成清洗记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch24.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch24b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch24b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch24b/`

抓取结果：
- 种子 14 条，抓到文档/页面 10 个，原始结构化记录 11,389 条，清洗记录 5,598 条，抓取失败 8 个。
- 浙江工业大学两个 PDF 的表头被 PDF 文本抽取拆分，已新增窄口径解析规则：识别“学院代码/学院名/专业代码/专业名/姓名/准考证号/脱敏身份证”行，以及“序号/姓名/脱敏身份证/性别/拟录取类型/学院/专业”行。
- 浙江工业大学软件学院入口返回 502；浙江工商大学入口返回 410；浙江财经大学、中国美术学院、杭州师范大学部分入口实时返回 404，保留失败日志。

batch24b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 浙江大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 17 |
| 浙江工业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 5193 |
| 浙江工业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 252 |
| 浙江师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 136 |

可追溯来源：

- 浙江大学历史学院 2026 届免试研究生推荐名单公示 PDF：https://ls.zju.edu.cn/_upload/article/files/bc/d6/eda878fd485aaf06f4dc78a2ec44/33139054-a1f6-44a1-8583-73767ab73e6c.pdf
- 浙江工业大学 2026 年硕士研究生拟录取名单 PDF：http://www.yz.zjut.edu.cn/_upload/article/files/83/3f/65d8614a42679678f76f305d5c67/c84277c9-3803-4949-944f-c71ca78131d3.pdf
- 浙江工业大学 2026 年拟接收推荐免试硕士研究生、直博生名单 PDF：http://www.yz.zjut.edu.cn/_upload/article/files/0e/d7/1dd8bbfa4e5383c3b51249e7ef9d/e7379bf3-8382-4e8d-a67a-145a85916bfc.pdf
- 浙江师范大学外国语学院 2026 年一志愿报考硕士研究生拟录取名单公示：https://flc.zjnu.edu.cn/2026/0401/c18547a550406/page.htm

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：33,191 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：33,191 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：88 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：38,940 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：38,940 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：239 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，77 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch23/23b 山东高校入口

batch23 转向山东未覆盖高校，先用学校研招网公告页和搜索发现的直链作为入口；batch23b 随后补了一轮更具体的 PDF/学院公示页。两批次成功补入青岛科技大学、青岛农业大学、曲阜师范大学、山东大学、山东建筑大学、山东科技大学等记录。中国海洋大学、山东中医药大学、山东理工大学等页面多为公告或附件桥页，部分直链出现 403/502，暂未形成可用人员级记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch23.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch23b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch23/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch23b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch23/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch23b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch23/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch23b/`

抓取结果：
- batch23：种子 14 条，抓到文档/页面 39 个，原始结构化记录 540 条，清洗记录 513 条，抓取失败 5 个。
- batch23b：种子 14 条，抓到文档/页面 24 个，原始结构化记录 526 条，清洗记录 512 条，抓取失败 5 个。
- 质量修正：补充规则剔除“其他事项/奖学金/招收条件”等招生通知章节；补充规则修复 PDF 中“研究方向码及名称”粘连到姓名列的情况，并剔除分数列误入姓名/学号位置的记录。

batch23/23b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 青岛科技大学 | 2021 | recommendation_exemption_list | recommendation_exemption | 227 |
| 青岛科技大学 | 2022 | recommendation_exemption_list | recommendation_exemption | 267 |
| 青岛农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 3 |
| 曲阜师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 16 |
| 山东大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 |
| 山东建筑大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 399 |
| 山东科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 111 |

可追溯来源：

- 青岛农业大学 2026 年拟录取推免硕士研究生名单公示：https://grad.qau.edu.cn/content/zhaoshengxinxi/f951bd22001f4e9fb38d77c3af516478
- 曲阜师范大学 2026 年招收攻读博士学位研究生拟录取名单公示（二）：https://yjs.qfnu.edu.cn/info/1045/5184.htm
- 青岛科技大学 2021 届推荐免试硕士研究生拟推荐名单公示：https://yzs.qust.edu.cn/info/1120/1516.htm
- 青岛科技大学 2022 届推荐免试硕士研究生拟推荐名单公示：https://yzs.qust.edu.cn/info/1120/1524.htm
- 山东大学公共卫生学院 2026 年推荐免试硕士研究生拟录取名单（四）附件页：https://www.sph.sdu.edu.cn/info/1704/19344.htm
- 山东建筑大学 2026 年硕士研究生拟录取名单公示第二批次 PDF：https://www.sdjzu.edu.cn/__local/D/83/BE/FB8E932CE18FFFEB2AF3F081718_5A4BA384_B18D7.pdf
- 山东科技大学能源与矿业工程学院 2026 年硕士研究生招生考试一志愿复试结果公示：https://cms.sdust.edu.cn/info/1076/10880.htm

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：27,593 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：27,593 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：84 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：33,342 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：33,342 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：235 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，74 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch22b 辽宁高校入口

batch22b 继续补辽宁未覆盖高校，入口包括东北大学、辽宁师范大学、沈阳建筑大学、沈阳工业大学、大连外国语大学、中国医科大学。东北大学与辽宁师范大学 2026 年硕士拟录取 PDF 成功形成清洗记录；辽宁师范大学 PDF 采用“学院代码 + 学院名 + 准考证号 + 脱敏姓名”的横向版式，本批次补充了对应 PDF 文本行解析规则。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch22.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch22b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch22b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch22b/`

抓取结果：
- 种子 7 条，抓到文档/页面 8 个，原始结构化记录 10,862 条，清洗记录 7,586 条，抓取失败 2 个。
- 沈阳工业大学入口实时返回 404。
- 中国医科大学入口因站点 SSL legacy renegotiation 被当前运行时拒绝，保留失败日志。
- 辽宁师范大学推免页、沈阳建筑大学页、大连外国语大学页及附件下载桥页未形成可用人员级记录。
- 清洗规则同步修正：当 PDF 抽取把数字学院码误放入 `person_name` 且已有准考证号时，清空假姓名并标记复核，避免数字进入姓名列。

batch22b 清洗后来源：

| 学校 | 年份 | 类型 | 路径 | 记录数 |
| --- | --- | --- | --- | ---: |
| 东北大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 4129 |
| 东北大学 | 2026 | postgraduate_admission_list | recommendation_exemption | 1524 |
| 辽宁师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1933 |

可追溯来源：

- 东北大学 2026 年硕士研究生拟录取名单 PDF：https://yz.neu.edu.cn/_upload/article/files/48/0d/e64dce244c78904cafa6cebc2ca3/db5353cf-3160-41df-b76d-ada13eb4a4ca.pdf
- 辽宁师范大学 2026 年硕士研究生全补考生拟录取名单 PDF：https://yjszs.lnnu.edu.cn/2026nianshuoshiyanjiushengquanbukaoshengniluqumingdanhuizong.pdf

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：26,568 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：26,568 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：77 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：32,317 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：32,317 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：228 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，68 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch17 / batch17b 华南与上海入口

batch17 尝试补华南/上海若干未覆盖高校和一个北京未覆盖高校，入口包括中山大学、深圳大学、华南理工大学、同济大学、东华大学、上海财经大学、华东理工大学、北京电子科技学院。batch17b 单独补同济大学跨域系统公示页。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch17.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch17b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch17/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch17b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch17/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch17b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch17/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch17b/`

抓取结果：
- batch17：种子 8 条，抓到文档/页面 43 个，抓取失败 1 个，原始结构化记录 1,173 条，清洗记录 121 条
- batch17b：种子 2 条，抓到文档/页面 2 个，抓取失败 0 个，原始结构化记录 0 条

batch17 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 北京电子科技学院 | 2026 | recommendation_exemption_list | 71 |
| 华南理工大学 | 2026 | postgraduate_admission_list | 49 |
| 深圳大学 | 2025 | incoming_recommendation_admission_list | 1 |

可追溯来源示例：

- 华南理工大学 PDF：https://www2.scut.edu.cn/_upload/article/files/1d/98/e102b0f54b59b5393c22914468e5/dd451052-cb29-46a1-a1b9-0452c70a0104.pdf
- 北京电子科技学院 PDF：https://www.besti.edu.cn/files/2025/11/20251120133432964.pdf
- 深圳大学公示页：https://yz.szu.edu.cn/info/1031/13916.htm
- 同济大学系统公示页：https://yzbm.tongji.edu.cn/xxgs/tmsLq

质量修正：
- 剔除无姓名/无编号的伪人员记录，避免将专业汇总表、序号表和空身份行混入人员级数据。
- 剔除表头/说明词被误识别为姓名的记录，例如“申请学院”“毕业学校”“其他”“在机械”等。
- 修复 CHSI 旧表中“姓名列为考生编号、专业列为真实姓名”的错位行。
- CHSI 主表已按新规则重建：`data/processed/graduate_outcomes_chsi/master_records_clean.csv` 现为 6,548 条。

未入库/失败说明：
- 中山大学入口返回 404。
- 深圳大学 2026 公示页说明有附件，但静态 HTML 未暴露附件链接，本轮只抽到后续页面中的少量历史公示记录。
- 同济大学系统公示页为动态页面，静态抓取未形成结构化记录。
- 上海财经大学、华东理工大学、东华大学部分页面主要是汇总或动态附件，清洗阶段剔除非人员行后仅保留可靠记录。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：13,915 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：13,915 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：67 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：20,463 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：20,463 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：223 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，59 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch16 / batch16b 北京重点高校入口

batch16 继续补北京重点高校官网 B 源，入口包括北京大学拟录取推荐免试研究生公示 PDF、北京大学医学部推免拟录取 PDF、北京师范大学拟录取硕士研究生名单 PDF、北京航空航天大学推免拟录取公告、对外经济贸易大学推免生招生公告列表、北京科技大学推免/统考公示汇总页。batch16b 对首轮未跟到的资源做补抓，重点是对外经济贸易大学隐藏 PDF 直链和北京科技大学各学院/培养单位公示页。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch16.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch16b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch16/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch16b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch16/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch16b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch16/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch16b/`

抓取结果：
- batch16：种子 10 条，抓到文档/页面 21 个，抓取失败 2 个，原始结构化记录 3,330 条，清洗记录 3,157 条
- batch16b：种子 29 条，抓到文档/页面 35 个，抓取失败 9 个，原始结构化记录 1,357 条，清洗记录 1,318 条
- 两批合计新增清洗记录：4,475 条

batch16 / batch16b 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 北京大学 | 2026 | recommendation_exemption_list | 2463 |
| 北京师范大学 | 2026 | postgraduate_admission_list | 694 |
| 北京科技大学 | 2026 | incoming_recommendation_admission_list | 576 |
| 对外经济贸易大学 | 2026 | incoming_recommendation_admission_list | 742 |

可追溯来源示例：

- 北京大学 2026 推免公示 PDF：https://admission.pku.edu.cn/docs/20251020170521359415.pdf
- 北京大学医学部 2026 推免公示 PDF：https://yjsy.bjmu.edu.cn/docs/2025-10/bbc2611c394e4424a2ad0a7132d5bdef.pdf
- 北京师范大学 2026 硕士拟录取第二批 PDF：https://yz.bnu.edu.cn/content/docs/ss_nlqmd/2026%E5%B9%B4%E5%8C%97%E4%BA%AC%E5%B8%88%E8%8C%83%E5%A4%A7%E5%AD%A6%E6%8B%9F%E5%BD%95%E5%8F%96%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E5%90%8D%E5%8D%95%E5%85%AC%E7%A4%BA%EF%BC%88%E7%AC%AC%E4%BA%8C%E6%89%B9%EF%BC%89.pdf
- 对外经济贸易大学 2026 推免结果公示页：https://yjsy.uibe.edu.cn/cms/infoSingleArticle.do?articleId=7678&columnId=2398
- 北京科技大学推免拟录取名单汇总页：https://yzxc.ustb.edu.cn/gkgs/8c5fbd019bbe4ae78c30323d173c783b.htm

质量修正：
- 对外经济贸易大学 PDF 只公开脱敏姓名，本轮新增回归测试并修正清洗去重规则：无学号且姓名含 `*` 的记录不再按脱敏姓名合并，以避免低估记录数。

未入库/失败说明：
- 北京航空航天大学附件下载页返回验证码/下载校验页，本轮未能自动抽取 PDF。
- 北京师范大学推免 PDF 直链和中国人民大学教务处入口返回 404。
- 北京科技大学部分学院/培养单位页面返回 404，成功入口已入库，失败项保留在 batch16b 日志。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：13,833 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：13,833 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：64 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：21,401 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：21,401 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：216 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，56 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch18 / batch18b 江苏浙江及直连 PDF 入口

batch18 继续补江苏、浙江和部分可直达 PDF 的未覆盖高校。首轮入口包括南京大学、浙江大学、浙江理工大学、南京理工大学、河海大学、南昌大学、华北电力大学；由于部分搜索结果已失效、系统页动态化或站点对抓取请求返回 403/404，batch18b 改用更稳的官方 PDF 直链，并新增南京林业大学学院级名单。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch18.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch18b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch18/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch18b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch18/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch18b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch18/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch18b/`

抓取结果：
- batch18：种子 7 条，抓到文档/页面 1 个，原始结构化记录 0 条，抓取失败 6 个。
- batch18b：种子 6 条，抓到文档/PDF 3 个，原始结构化记录 1,269 条，清洗记录 1,249 条，抓取失败 3 个。

batch18b 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 河海大学 | 2025 | incoming_recommendation_admission_list | 1228 |
| 南京林业大学 | 2026 | postgraduate_admission_list | 21 |

可追溯来源示例：

- 河海大学 2025 接收推荐免试研究生拟录取名单 PDF：https://gs.hhu.edu.cn/_upload/article/files/1a/6f/4212477244a7b181b0a645a614ff/e6a752ac-e89f-4e9e-98ba-a79e3449578f.pdf
- 南京林业大学家居与工业设计学院 2026 推免接收拟录取名单 PDF：https://jiaju.njfu.edu.cn/DFS/file/2025/10/13/20251013082150107mlns6n.pdf

未入库/失败说明：
- 浙江大学公示系统页为动态系统页，静态抓取未形成结构化记录。
- 浙江理工大学公告页可访问，但静态 HTML 中未暴露名单表格。
- 南京大学官网页触发 SSL 握手失败；后续可尝试浏览器自动化或离线下载附件。
- 南昌大学、华北电力大学搜索索引中的 PDF 直链在爬虫侧返回 404，暂不入库。

质量修正：
- 验证阶段发现 14 条错位进入姓名列的非人员标签，例如“公示期间”“院代码”“金融学(FRM方向)”。已补充回归测试，并将这类行从清洗主表中剔除。
- CHSI 主表也按同一规则重建，A 源从 6,548 条调整为 5,754 条。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：15,150 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：15,150 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：69 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：20,904 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：20,904 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：221 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，61 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch19 北京与江苏高价值入口

batch19 继续补未覆盖高校，入口包括中国农业大学、中国药科大学、南京农业大学、南京邮电大学、北京工业大学、北京化工大学、首都医科大学。抓取中同时覆盖“接收推免拟录取”和“硕士拟录取”两类毕业出路数据。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch19.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch19/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch19/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch19/`

抓取结果：
- 种子 7 条，抓到文档/页面 29 个，原始结构化记录 2,612 条，清洗记录 2,091 条，抓取失败 1 个。
- 中国药科大学搜索结果页返回 410，暂未入库。
- 南京农业大学、南京邮电大学入口页可访问，但本轮未从静态页面形成可用人员级记录。

batch19 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 中国农业大学 | 2026 | incoming_recommendation_admission_list | 1329 |
| 北京工业大学 | 2026 | recommendation_exemption_list | 733 |
| 北京化工大学 | 2026 | postgraduate_admission_list | 20 |
| 首都医科大学 | 2025 | recommendation_exemption_list | 9 |

可追溯来源示例：

- 中国农业大学 2026 接收推免生拟录取名单 PDF：https://gradsch1.cau.edu.cn/module/download/downfile.jsp?classid=0&filename=a7d5cacb5f2a498a88e3fe5401aed173.pdf
- 北京工业大学 2026 推荐免试攻读研究生拟录取名单公示：https://yanzhao.bjut.edu.cn/info/1019/17865.htm
- 北京化工大学 2026 年硕士研究生拟录取名单公示：https://graduate.buct.edu.cn/2026/0415/c1392a218537/page.htm

质量修正：
- 新增回归测试并剔除“类别/学习方式/分数”等表头行。
- 新增规则剔除姓名列为短数字序号且无学号的专业目录行；首都医科大学 2026 目录型 PDF 因此未作为人员级名单入库。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：17,240 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：17,240 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：72 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：22,989 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：22,989 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：223 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，64 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch20 北京未覆盖高校

batch20 继续补北京未覆盖高校，入口包括中央民族大学、中国政法大学、北京信息科技大学、外交学院。外交学院 PDF 成功入库；其余入口因实时 404 或未暴露静态附件暂不入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch20.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch20/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch20/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch20/`

抓取结果：
- 种子 4 条，抓到文档/页面 2 个，原始结构化记录 111 条，清洗记录 110 条，抓取失败 2 个。
- 中国政法大学页面可访问，但静态 HTML 未暴露附件或表格。
- 中央民族大学页面实时返回 404；尝试附件直链只返回短 HTML 响应。
- 北京信息科技大学搜索索引 PDF 直链返回 404。

batch20 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 外交学院 | 2026 | postgraduate_admission_list | 110 |

可追溯来源：

- 外交学院 2026 年硕士推免拟录取名单 PDF：https://yjsb.cfau.edu.cn/docs/2025-10/0f710beef1664e5481a6aacb930bdfc4.pdf

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：17,350 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：17,350 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：73 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：23,099 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：23,099 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：224 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，65 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-23 追加进展：batch21 辽宁高校入口

batch21 转向辽宁未覆盖高校，入口包括大连海事大学、大连理工大学、东北财经大学、大连医科大学。东北财经大学 2026 年硕士统考拟录取 PDF 成功入库；其它入口主要抓到公告页或附件下载桥页，未形成可用人员级记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260523_batch21.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260523_batch21/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260523_batch21/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260523_batch21/`

抓取结果：
- 种子 7 条，抓到文档/页面 23 个，原始结构化记录 4,527 条，清洗记录 1,632 条，抓取失败 1 个。
- 大连理工大学建设工程学院入口返回 404。
- 大连海事大学、大连理工大学、大连医科大学多处附件下载桥页返回 HTML，未得到可解析的实际名单文件。

batch21 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 东北财经大学 | 2026 | postgraduate_admission_list | 1632 |

可追溯来源：

- 东北财经大学 2026 年硕士研究生拟录取名单公示页：https://graduate.dufe.edu.cn/content_98814.html
- 东北财经大学 2026 统考拟录取名单 PDF：https://graduate.dufe.edu.cn/file/d9bd4578-5052-11f1-8b6b-005056a49984/%E9%99%84%E4%BB%B61%EF%BC%9A2026%E7%BB%9F%E8%80%83%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95%EF%BC%88%E4%B8%8D%E5%90%AB%E6%8E%A8%E5%85%8D%E7%94%9F%EF%BC%89.pdf

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：18,982 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：18,982 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：74 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：24,731 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：24,731 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：225 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，66 所已精确匹配官网记录

Excel 交付版已同步重建：
- `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch113s 太原理工大学

batch113s 继续补 B 类官方站点缺口，种子包括首都经济贸易大学、太原理工大学、首都师范大学。最终可入库来源为太原理工大学研究生院两个 2026 年官方 PDF：接收推免拟录取名单与硕士一志愿拟录取名单。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch113.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch113s/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch113s/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch113s/`

抓取结果：
- 种子 6 条，抓到文档/页面 9 个，原始结构化记录 345 条，清洗记录 345 条，抓取失败 0 个。
- 首都经济贸易大学 3 个公告页可访问，但静态附件仅形成定向就业协议 DOCX，未形成可解析人员级名单。
- 首都师范大学搜索入口实时跳转到学校首页，本轮新增防护后不再误解析首页栏目词。

batch113s 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 太原理工大学 | 2026 | postgraduate_admission_list | 174 |
| 太原理工大学 | 2026 | recommendation_exemption_list | 171 |

可追溯来源：

- 太原理工大学接收 2026 届优秀本科毕业生免试攻读研究生拟录取名单公示：https://www.gs.tyut.edu.cn/info/1261/14959.htm
- 太原理工大学 2026 年硕士研究生招生一志愿拟录取名单公示：http://www.gs.tyut.edu.cn/info/1261/15649.htm
- 太原理工大学推免拟录取名单 PDF：https://www.gs.tyut.edu.cn/__local/E/CF/72/60E339DF1567346F1D6D1EF0EE1_5913842E_270E3.pdf
- 太原理工大学一志愿拟录取名单 PDF：http://www.gs.tyut.edu.cn/__local/3/91/82/57C0EDCA2879AD0D5B22C8623B8_581A69CE_CD34D.pdf

质量修正：
- 新增回归测试，防止详情页跳转到学校首页时沿用种子文档类型并误抽首页导航词。
- 新增太原理工推免 PDF 专项解析，识别“姓名+毕业院校 / 学院代码与名称 / 专业代码与名称 / 研究方向 / 学习方式 / 招生类型 / 复试成绩”表格版式。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,163 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,163 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：252 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：166,873 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：166,873 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：404 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，224 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：179 个测试通过（仅既有 ResourceWarning）。
- Excel 交付版已同步重建并通过结构校验：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch114/batch115 兰州大学

batch114 继续排查 B 类官方站点缺口，种子覆盖北京语言大学、东北师范大学、电子科技大学、北京协和医学院。该批次未形成可入库人员级记录：北京语言大学附件进入验证码下载桥页，东北师范大学公告仅指向动态查询系统，电子科技大学主公告的 48 个学院链接多为验证码附件或 HTTP 412，协和医学院结果页当前为空表。

batch115 随后补入华东师范大学与兰州大学。华东师范大学招生系统页面可访问但未暴露静态名单；兰州大学法学院 PDF 可直接下载并成功清洗出 101 条 2026 年推免拟录取记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch114.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch114_uestc_links.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch115.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch114/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch114_uestc_links/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch115c/`

抓取结果：
- batch114：种子 6 条，抓到文档/页面 19 个，原始结构化记录 8 条但均为页面导航/页脚噪声，清洗记录 0 条。
- batch114 UESTC 学院链接：种子 48 条，抓到文档/页面 55 个，清洗记录 0 条，5 个链接返回 HTTP 412。
- batch115c：种子 3 条，抓到文档/页面 3 个，兰州大学 PDF 原始去重后清洗记录 101 条，抓取失败 0 个。

batch115c 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 兰州大学 | 2026 | recommendation_exemption_list | 101 |

可追溯来源：

- 兰州大学法学院 2026 年接收推荐免试攻读硕士学位研究生拟录取名单 PDF：https://laws.lzu.edu.cn/laws/upload/files/20250924/8beed878bbfc40b99d4bfe824b07fde3.pdf

质量修正：
- 新增兰州大学法学院 PDF 专项解析，识别“报考专业 / 报考研究方向 / 姓名 / 专业面试成绩 / 外语口语及听力测试成绩 / 复试总成绩 / 备注”版式。
- 修正旧通用解析将面试成绩误写入 `major` 的问题；明确跳过“放弃”行，并兼容备注列空白、姓名后粘页码和带 `·` 的较长姓名。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,264 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,264 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：253 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：166,974 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：166,974 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：405 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，225 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：180 个测试通过（仅既有 ResourceWarning）。
- 批次质量扫描：101 条清洗记录，缺少人员姓名 0、缺少录取专业 0、数字误入专业字段 0、需人工复核 0、包含“放弃”记录 0。
- Excel 交付版已同步重建并通过结构校验：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch116 上海海事大学

batch116 继续补 B 类官方站点缺口，种子包括河北大学、山西财经大学、华东政法大学、山东师范大学、贵州师范大学、上海海事大学。最终可入库来源为上海海事大学 2026 年博士研究生拟录取名单 HTML 表格。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch116.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch116b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch116b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch116b/`

抓取结果：
- 种子 7 条，抓到文档/页面 7 个，原始结构化记录 154 条，清洗记录 154 条。
- 河北大学、山西财经大学官方公示页可访问，但附件下载 URL 为桥页，未形成静态人员级名单。
- 华东政法大学公示页未暴露人员级明细。
- 山东师范大学、贵州师范大学线索 URL 返回 404。
- 上海海事大学硕士拟录取公示页可访问但未暴露静态人员表；博士拟录取公示页成功解析。

batch116b 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 上海海事大学 | 2026 | postgraduate_admission_list | 154 |

可追溯来源：

- 上海海事大学 2026 年博士研究生拟录取名单公示：https://yz.shmtu.edu.cn/2026/0522/c8926a293126/page.htm

质量修正：
- 新增 HTML 表格专项解析，识别“考生编号 / 姓名 / 一级学科名称 / 报考类别 / 综合面试成绩 / 备注”版式。
- 将一级学科名称写入 `admission_major`，报考类别和综合面试成绩写入 `remarks`，避免只保留姓名和考生编号的低质量记录。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,418 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,418 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：255 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：167,128 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：167,128 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：407 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，226 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：181 个测试通过（仅既有 ResourceWarning）。
- 批次质量扫描：154 条清洗记录，缺少人员姓名 0、缺少录取学科 0、需人工复核 0。
- Excel 交付版已同步重建并通过结构校验：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch117 西北政法大学

batch117 继续补 B 类官方站点缺口，种子包括西安交通大学、西安电子科技大学、西北政法大学、桂林医科大学、海南医科大学、西北师范大学。最终可入库来源为西北政法大学 2026 年推荐免试硕士研究生拟录取名单旧版 `.xls` 附件。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch117.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch117b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch117b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch117b/`

抓取结果：
- 种子 11 条，抓到文档/页面 6 个，原始结构化记录 179 条，清洗记录 179 条。
- 西安交通大学机械、材料、能动学院页可访问但页面未暴露可解析人员表；医学部入口返回 502。
- 西安电子科技大学校级推免/统考公示页可访问但未暴露可解析人员表。
- 西北政法大学公告页 URL 返回 404，但直接附件 URL 可访问并解析成功。
- 桂林医科大学远端断开；海南医科大学返回 404；西北师范大学列表页返回 412。

batch117b 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 西北政法大学 | 2026 | recommendation_exemption_list | 179 |

可追溯来源：

- 西北政法大学 2026 年推荐免试硕士研究生拟录取名单附件：https://grs.nwupl.edu.cn/wcm.files/upload/CMSgrs/202511/20251105085754878.xls

质量修正：
- 新增旧版 `.xls` 解析兜底，Windows 环境下调用本机 Excel 将 BIFF `.xls` 临时转换为 `.xlsx`，再复用已有表格抽取逻辑。
- 新增回归测试验证旧 `.xls` 转换后能进入 Excel 表格解析管线。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,597 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,597 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：256 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：167,307 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：167,307 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：408 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，227 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：182 个测试通过（仅既有 ResourceWarning）。
- 批次质量扫描：179 条清洗记录，缺少人员姓名 0、缺少学院/专业 0、需人工复核 0。
- Excel 交付版已同步重建并通过结构校验：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch118/batch119 大连大学

batch118 继续补 B 类官方站点缺口，种子包括昆明理工大学、西南交通大学、西南林业大学、西安交通大学、西南医科大学。该批次未形成可入库人员级记录：昆明理工大学、西南交通大学、西南林业大学、西南医科大学等页面可访问但附件下载进入验证码桥页；西安交通大学相关入口未暴露可解析人员表。

batch119 随后补入宁波大学、大连大学、哈尔滨师范大学、南京财经大学、南京医科大学、东北电力大学、上海师范大学等入口。最终可入库来源为大连大学 2026 年接收推荐免试研究生拟录取名单 PDF。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch118.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch119.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch118/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch119b/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch119b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch119b/`

抓取结果：
- batch118：种子 5 条，清洗记录 0 条。主要阻断为验证码下载桥页。
- batch119b：种子 7 条，抓到文档/页面 12 个，原始结构化记录去重后清洗记录 5 条，抓取失败 1 个。
- 宁波大学、哈尔滨师范大学、南京财经大学附件下载 URL 返回验证码桥页；东北电力大学入口返回 404；南京医科大学、上海师范大学页面未形成可解析人员级明细。

batch119b 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 大连大学 | 2026 | incoming_recommendation_admission_list | 5 |

可追溯来源：

- 大连大学 2026 年接收推荐免试研究生拟录取名单公示页：https://yjs.dlu.edu.cn/info/1065/3633.htm
- 大连大学 2026 年接收推荐免试研究生拟录取名单 PDF：https://yjs.dlu.edu.cn/__local/0/A6/6B/E8A23D395901FC1BB2DE886318C_48A9DBCA_1F13D.pdf

质量修正：
- 新增大连大学 PDF 专项解析，识别“报考院系 / 拟录取专业代码 / 拟录取专业名称 / 研究方向 / 复试成绩 / 学习方式 / 层次”版式。
- 专业代码写入 `major`，代码和专业名合并写入 `admission_major`，研究方向、复试成绩、全日制和硕士层次写入 `remarks`。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：161,602 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：161,602 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：257 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：167,312 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：167,312 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：409 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，228 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：183 个测试通过（仅既有 ResourceWarning）。
- batch119b 清洗表：5 条清洗记录，缺少人员姓名 0、缺少专业字段 0、需人工复核 0。
- Excel 交付版已同步重建并通过结构校验：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch120/batch121 广西师范大学/桂林理工大学

batch120 继续补 B 类官方站点缺口，种子包括湖南大学、华中师范大学、福建师范大学、福建农林大学、集美大学、中南民族大学、华侨大学、北京语言大学、济南大学。该批次未形成可入库人员级记录：湖南大学、华中师范大学、集美大学等名单附件进入验证码下载桥页；福建师范大学返回提示页；华侨大学、北京语言大学、济南大学部分搜索命中页返回 404 或公示结束页；中国海洋大学通知列表仅保留附件标题而无实际名单下载。

batch121 转向更可能静态解析的正文表格与直链 PDF，种子覆盖河南医药大学、广州医科大学、云南师范大学、广西师范大学、桂林理工大学等。最终可入库来源为广西师范大学 2026 年硕士研究生拟录取名单 PDF 和桂林理工大学计算机科学与工程学院软件工程专业推免拟录取 PDF。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch120.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch120b.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch121.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch120/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch120b/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch121c/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch121c/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch121c/`

抓取结果：
- batch120：种子 9 条，抓到文档/页面 9 个，清洗记录 0 条，主要阻断为验证码下载桥。
- batch120b：种子 7 条，抓到文档/页面 16 个；原始 1 条中国海洋大学页面导航噪声，修正规则后清洗记录 0 条。
- batch121c：种子 8 条，抓到文档/页面 12 个，原始结构化记录 1,798 条，清洗记录 1,797 条，抓取失败 1 个。

batch121c 清洗后来源：

| 学校 | 年份 | 类型 | 记录数 |
| --- | --- | --- | ---: |
| 广西师范大学 | 2026 | postgraduate_admission_list | 1,796 |
| 桂林理工大学 | 2026 | incoming_recommendation_admission_list | 1 |

可追溯来源：

- 广西师范大学 2026 年硕士研究生一志愿考生拟录取名单公示页：http://www.yz.gxnu.edu.cn/2026/0403/c4626a339485/page.htm
- 广西师范大学 2026 年硕士研究生拟录取名单 PDF：http://www.yz.gxnu.edu.cn/_upload/article/files/06/ce/18fa0a8b4ef4a461bad796725b2f/a788bd4e-af69-4569-9849-784d29b6a3c9.pdf
- 桂林理工大学计算机科学与工程学院软件工程专业推免拟录取名单 PDF：https://cise.glut.edu.cn/jisuanjixueyuan2026nianshuoshiyanjiushengtuimianshengniluqumingdangongshi.pdf

质量修正：
- 新增“后台管理”等站点导航标签过滤，避免页面维护入口被误识别为人员姓名。
- 新增广西师范大学 PDF 专项解析，正确抽取报考单位、学习方式、专业代码/名称、研究方向代码、初试总分、复试成绩和总成绩。
- 新增桂林理工大学 PDF 专项解析，修复学院名、专业名被 PDF 文本层拆到上下行后通用解析只保留分数的问题。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：163,399 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：163,399 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：259 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：169,109 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：169,109 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：411 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，230 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：185 个测试通过（仅既有 ResourceWarning）。
- batch121c 清洗表：1,797 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，学习方式/分数误入 `admission_major` 0。
- Excel 交付版已同步重建并通过结构校验：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch122 宁夏医科大学

batch122 继续从未覆盖院校中筛选官网硕士拟录取名单入口，种子覆盖青岛理工大学、山东财经大学、山东理工大学、山东农业大学、山东师范大学、齐鲁工业大学、宁夏医科大学和三峡大学。青岛理工大学、山东财经大学、齐鲁工业大学等页面可访问但多为公示结束公告或未暴露人员级附件；山东理工大学列表本地返回提示页；山东农业大学、山东师范大学、三峡大学入口未形成可结构化明细。宁夏医科大学硕士招生栏目可追到 2026 年硕士研究生招生调剂考生拟录取名单 PDF，形成 74 条人员级记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch122.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch122b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch122b/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch122b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch122b/`

本批清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 宁夏医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 74 | 0 |

可追溯来源：

- 宁夏医科大学硕士招生列表：https://www.nxmu.edu.cn/yjsy/zsgz/ssszs.htm
- 宁夏医科大学 2026 年硕士研究生招生调剂考生拟录取名单公示页：https://www.nxmu.edu.cn/yjsy/info/1010/3492.htm
- 宁夏医科大学拟录取名单 PDF：https://www.nxmu.edu.cn/__local/0/F2/C0/2B2F969F4AEBEB4142256E093A4_430D14D0_1A8DA.pdf

质量修正：
- 新增宁夏医科大学 PDF 专项解析，识别“考生编号 / 姓名 / 专项计划 / 录取院系所码 / 录取院系所名称 / 录取专业代码 / 录取专业名称 / 录取研究方向 / 录取学习方式 / 初试总分 / 复试总成绩 / 录取成绩”版式。
- 专业代码写入 `major`，代码和专业名合并写入 `admission_major`，专项计划、研究方向、学习方式和成绩写入 `remarks`。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：163,473 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：163,473 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：260 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：169,183 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：169,183 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：412 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，231 所已精确匹配官网记录

验证：
- batch122b 清洗表：74 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，代码-only `admission_major` 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加进展：batch123 济南大学

batch123 继续从未覆盖院校中筛选官网列表页和拟录取入口，种子覆盖聊城大学、江西师范大学、济南大学、上海理工大学、上海师范大学、南京理工大学、南京邮电大学、山西医科大学、山西中医药大学和山东中医药大学等。多数入口只保留公告、列表或验证码下载桥，未形成可入库人员级明细。江西师范大学抓到多份 PDF，其中 2026 PDF 为推免名额/专业分配表，通用解析会把专业名误当姓名；本轮新增清洗规则剔除这类“无学号、学院代码、学院名、专业代码-only”的非人员级配额行，暂不并入江西师范记录。济南大学官网 PDF 形成 110 条 2026 年博士研究生拟录取人员级记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch123.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch123b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch123b_usable/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch123b_usable/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch123b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch123b/`

本批可入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 济南大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 110 | 0 |

可追溯来源：

- 济南大学招生工作进展列表：https://yz.ujn.edu.cn/yzgz/zsgzjz.htm
- 济南大学 2026 年博士研究生拟录取名单公示页：https://yz.ujn.edu.cn/info/1032/4424.htm
- 济南大学 2026 年博士研究生拟录取名单 PDF：https://yz.ujn.edu.cn/__local/A/FA/00/1E84870EF082236A617634A28FC_77DA86B0_16EA4.pdf

质量修正：
- 新增济南大学 PDF 专项解析，识别“序号 / 考生编号 / 姓名 / 报考院系代码 / 报考院系 / 报考专业代码 / 报考专业 / 学习形式 / 考试方式”版式。
- 专业代码写入 `major`，代码和专业名合并写入 `admission_major`，学习形式和考试方式写入 `remarks`。
- 新增非人员级推免名额分配表过滤，避免专业名被误当 `person_name`。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：163,583 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：163,583 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：261 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：169,293 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：169,293 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：413 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，232 所已精确匹配官网记录

验证：
- batch123b 可用子集：110 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，代码-only `admission_major` 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch131/batch132 华南师范大学、南京医科大学

batch131 覆盖华东师范大学、中国药科大学、南京医科大学、皖南医学院、重庆医科大学等入口。南京医科大学研究生招生网官方 PDF 可直接下载，形成 774 条“考生编号/姓名/注册学号”记录；该 PDF 不含专业或学院字段，因此保留为 `needs_review=true` 的低字段官方记录。其余入口多为 410/404/403、正文未暴露附件，或附件下载桥，暂未并入人员级明细。

batch132 重点处理华中师范大学、云南师范大学、新疆师范大学、华南师范大学。华中师范大学、云南师范大学、新疆师范大学正文页可访问，但附件均进入“请输入验证码下载附件”的下载桥，未能自动抓取 PDF 明细。华南师范大学 2026 年硕士研究生拟录取公示页暴露 `statics.scnu.edu.cn` 静态 PDF 直链，批量下载 35 个学院/单位 PDF，成功入库 7,305 条结构化记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch131.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch132.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch132b.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch132c.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch131/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch132d/records_clean.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch132d/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch132d/`

本批可入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 华南师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 6,502 | 0 |
| 华南师范大学 | 2026 | postgraduate_admission_list | recommendation_exemption | 803 | 0 |
| 南京医科大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 774 | 774 |

可追溯来源：
- 华南师范大学 2026 年硕士研究生拟录取名单公示页：https://yz.scnu.edu.cn/a/20260407/672.html
- 华南师范大学 35 个学院/单位 PDF：来自上述公示页的 `https://statics.scnu.edu.cn/pics/yz/2026/...pdf` 静态直链
- 南京医科大学 2026 年推荐免试研究生考生编号查询页面：https://yjszs.njmu.edu.cn/2026/0512/c10193a301057/page.htm

质量修正：
- 新增华南师范大学 PDF 专项解析，识别“序号 / 考生编号 / 姓名 / 考试方式 / 调剂类别 / 成绩 / 拟录取专业 / 学习方式 / 录取类别 / 是否拟录取 / 备注”版式。
- 修复华南师范大学 PDF 中“非全日制”粘连在专业名后的右移问题，确保 `admission_major`、学习方式、录取类别和是否拟录取字段不串列。
- 新增分页标签过滤，剔除 HTML 正文中“最后一页 / 标签”等非人员级片段。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：180,255 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：180,255 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：282 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：185,965 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：185,965 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：434 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，251 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：212 个测试通过（仅保留既有 ResourceWarning）。
- batch132d 清洗表：7,305 条清洗记录，缺少人员姓名 0、缺少专业字段 0、缺少考生编号 0、需人工复核 0；其中“是否拟录取=是”5,187 条，“否”2,118 条。
- batch131 清洗表：774 条官方低字段记录，缺少人员姓名 0、缺少考生编号 0、缺少专业字段 774、需人工复核 774。
- 工作簿结构校验：Overview 15 行、Source_Summary 435 行、Coverage 431 行、Public_Records 185,966 行；公式单元格 0，公式错误 0。

## 2026-05-25 追加批次：batch133 西安邮电大学

batch133 继续从未覆盖院校筛选官网入口，覆盖西南交通大学、沈阳师范大学、南京邮电大学和西安邮电大学。西南交通大学拟录取入口本地返回 502；沈阳师范大学列表可访问但本轮仅跟到定向协议文档，未暴露人员级名单；南京邮电大学列表只暴露 2026 第四批公示标题但文章参数页本地返回“无效的文章参数”，另误跟到 2021 推免人数统计，未并入。西安邮电大学 2026 年推荐免试研究生拟录取 PDF 可直接下载并入库 17 条。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch133.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch133b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch133c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch133c/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch133c/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch133c/`

本批可入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西安邮电大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 17 | 0 |

可追溯来源：
- 西安邮电大学 2026 年推荐免试研究生拟录取名单公示页：https://gr.xupt.edu.cn/info/1172/9158.htm
- 西安邮电大学 2026 年推荐免试研究生拟录取名单 PDF：https://gr.xupt.edu.cn/__local/2/8A/F1/8CA9DC8223FFBF435008FCC62BD_018718C2_140F9.pdf

质量修正：
- 新增西安邮电大学 PDF 专项解析，修复“身份证号 / 后四位”跨行表头导致通用解析把证件后四位错放入学院字段的问题。
- 证件后四位写入 `student_id`，学院写入 `college`，专业代码写入 `major`，代码与专业名合并写入 `admission_major`，并在 `remarks` 标注“证件后四位”。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：180,272 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：180,272 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：283 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：185,982 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：185,982 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：435 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，252 所已精确匹配官网记录

验证：
- batch133c 清洗表：17 条清洗记录，缺少人员姓名 0，缺少专业字段 0，缺少证件后四位 0，需人工复核 0。
- Excel 交付版已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

## 2026-05-25 追加批次：batch134 福建农林大学/中南民族大学/沈阳药科大学

batch134 继续从未覆盖学校中筛选可直接下载的官网 PDF。福建农林大学研究生院公开 2026 年接收推免名单和 2025 年硕士拟录取名单 PDF；中南民族大学研究生院公开 2026 年接收硕士推免生拟录取名单 PDF；沈阳药科大学研究生院公开 2025 年硕士复试结果及拟录取名单一志愿和多批调剂 PDF。沈阳体育学院搜索缓存可见 2026 推免标题，但官网实时列表未定位到对应人员级页面，本批未并入。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch134.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch134c/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch134c/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch134c/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch134c/`

本批可入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 福建农林大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 41 | 0 |
| 福建农林大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,515 | 0 |
| 中南民族大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 52 | 0 |
| 沈阳药科大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,946 | 0 |

可追溯来源：
- 福建农林大学 2026 年接收推荐免试攻读研究生名单公示页：https://yjsy.fafu.edu.cn/57/3e/c3604a415550/page.htm
- 福建农林大学 2026 年接收推荐免试攻读研究生名单 PDF：https://yjsy.fafu.edu.cn/_upload/article/files/5b/8d/b16c34814f80b5343a1123109efe/95e39fc0-b4f4-454c-864c-40d8e4bb87a3.pdf
- 福建农林大学 2025 年拟录取硕士研究生名单公示页：https://yjsy.fafu.edu.cn/3d/c3/c3604a409027/page.htm
- 福建农林大学 2025 年拟录取硕士研究生名单 PDF：https://yjsy.fafu.edu.cn/_upload/article/files/1e/41/8b9c8fa64b58a1f5594cb46dc953/e316667d-0ba1-4253-9f22-8620b0d22931.pdf
- 中南民族大学 2026 年接收硕士推免生拟录取名单公示页：https://www.scuec.edu.cn/yjsy/info/1007/3533.htm
- 中南民族大学 2026 年接收硕士推免生拟录取名单 PDF：https://www.scuec.edu.cn/__local/B/4C/6F/9073B321BC7503E71FCC086161B_346AEF18_20DE2.pdf
- 沈阳药科大学 2025 年硕士复试结果及拟录取名单 PDF：`https://grs.syphu.edu.cn/__local/...pdf` 五个官方直链，见 batch134 种子文件。

质量修正：
- 新增沈阳药科大学 PDF 专项解析，修复宽表中“考生编号 / 姓名 / 复试批次 / 学院 / 专业方向 / 分数 / 排名 / 结果”错位到姓名和学院字段的问题。
- 新增中南民族大学 PDF 专项解析，合并 `085402 通信工程（含宽带网络、移动通信等）` 的跨行专业名，避免续行文本误识别为人员姓名。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：185,826 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：185,826 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：287 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：191,536 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：191,536 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：439 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，255 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：216 个测试通过（仅保留既有 ResourceWarning）。
- batch134c 清洗表：5,554 条清洗记录，缺少人员姓名 0，缺少专业字段 0，需人工复核 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 440 行、Coverage 431 行、Public_Records 191,537 行；公式单元格 0，公式错误 0。

## 2026-05-25 追加批次：batch135 验证码阻断与 batch136b 重庆医科大学

batch135 复核黑龙江大学和湖南大学官网拟录取/推免公示入口。两校页面可访问，但附件下载均进入 VSB `download.jsp` 验证码桥页（页面提示“请输入验证码下载附件”），本轮未自动并入。batch136b 转向可直接追踪附件的重庆医科大学第一临床学院官网页面，来源页自动发现 18 个官方 PDF，新增 2026 年硕士研究生第一志愿拟录取人员级记录 185 条。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch135.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch136b.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch136b/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch136b/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch136b/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch136b/`

本批可入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 重庆医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 185 | 0 |

可追溯来源：
- 重庆医科大学第一临床学院 2026 年硕士研究生第一志愿复试成绩公示页：https://www.hospital-cqmu.com/gzb_yxjy_yjsjyn_zsgl/010082100041738.html
- 该页面自动发现的 18 个官方 PDF：`https://www.hospital-cqmu.com/oss/20260331/*.pdf` 和 `https://www.hospital-cqmu.com/oss/20260403/*.pdf`，详见 batch136b `documents.jsonl`。
- 黑龙江大学 2025 年硕士研究生拟录取公示页：https://yjsy.hlju.edu.cn/info/1009/9937.htm（附件验证码阻断）
- 湖南大学 2026 年硕士研究生拟录取名单公示页：https://gra.hnu.edu.cn/info/1075/10449.htm（附件验证码阻断）

质量修正：
- 新增重庆医科大学第一临床学院 PDF 专项解析，按“专业代码 / 专业名称（方向） / 考生编号 / 姓名 / 初试成绩 / 复试成绩 / 总成绩 / 是否拟录取”表格抽取，只保留“是否拟录取=是”的人员行。
- 来源页导航噪声未进入清洗表；batch136b 清洗表缺少人员姓名 0，缺少考生编号 0，缺少专业字段 0，需人工复核 0。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：186,011 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：186,011 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：288 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：191,721 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：191,721 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：440 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，256 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：217 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，公开明细 191,721 行、汇总 440 行、覆盖追踪 430 行。

## 2026-05-25 追加批次：batch137-batch143 山西医科/辽宁大学/北京外国语大学

batch137-batch143 继续从剩余缺口中筛选官网静态名单入口。山西医科大学药学院页面为可直接解析的 HTML 表格，新增 19 条 2026 年推免硕士拟录取记录；辽宁大学 2026 年接收推免生 PDF 已在主表中存在，本轮复抓后和主表去重，仅补入 2 条此前漏抽的记录；北京外国语大学 2026 年硕士研究生调剂拟录取结果公示页为 HTML 表格，新增 36 条记录。

未并入来源说明：
- 东北师范大学公告指向 `yz.nenu.edu.cn` 动态查询系统，当前返回“录取名单尚未公布”。
- 华东师范大学、上海中医药大学、北京外国语大学一志愿页面正文已替换为“公示已结束”，不再暴露名单。
- 南京理工大学、中国药科大学、南京邮电大学候选页返回 410/404 或站点提示页。
- 同济大学公示系统当前显示“尚未开放”。
- 北京语言大学、北京协和医学院、黑龙江大学、湖南大学等 VSB 附件入口返回 `download.jsp` 验证码桥页，未自动并入。
- 北京外国语大学“硕博连读研究生拟录取”页面清洗得到 7 条博士方向记录，因不属于本轮保研/考研主口径，暂不并入。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch137.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch138.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch139.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch140.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch141.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch142.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch143.csv`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山西医科大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 19 | 0 |
| 辽宁大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 | 0 |
| 北京外国语大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 36 | 0 |

可追溯来源：
- 山西医科大学药学院 2026 年推免硕士研究生拟录取名单公示页：https://www.sxmu.edu.cn/yxy/info/2408/7170.htm
- 辽宁大学 2026 年接收推荐免试攻读研究生拟录取名单 PDF：https://grs.lnu.edu.cn/26tmgsmd.pdf
- 北京外国语大学 2026 年硕士研究生调剂拟录取结果公示页：https://graduate.bfsu.edu.cn/info/1048/4206.htm

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：186,068 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：186,068 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：290 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：191,778 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：191,778 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：442 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，257 所已精确匹配官网记录

验证：
- batch137 清洗表 19 条、batch138 清洗表 389 条、batch143 清洗表 36 条；最终入库新增 57 条，缺少人员姓名 0，需人工复核 0。
- 工作簿已同步重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，公开明细 191,778 行、汇总 442 行、覆盖追踪 430 行。

## 2026-05-25 追加批次：batch144-batch151 昆明理工大学与缺口入口复核

batch144-batch151 继续从剩余缺口中筛选官网静态名单入口。batch144-batch150 覆盖山东、浙江、辽宁、湖北等院校的研究生院公告页和学院页，多数页面是招生通知、栏目页、404/410、扫描 PDF 或 VSB `download.jsp` 验证码桥，未形成可自动入库记录。batch151 命中昆明理工大学 2026 年硕士研究生拟录取名单公示页；页面附件同样需要验证码，但经人工下载核验后，PDF 含可抽取文本层，最终新增 5,652 条人员级记录。

未并入来源说明：
- 青岛理工大学、齐鲁工业大学、山东中医药大学、中国石油大学（华东）、山东理工大学、中国药科大学等入口为公告/栏目页或附件下载桥，未形成可结构化人员表。
- 浙江工商大学、杭州师范大学、北京电影学院、北京服装学院、沈阳航空航天大学、浙江财经大学等候选页返回 404/410 或站点提示页。
- 大连外国语大学、华中师范大学等 VSB 附件入口返回 `download.jsp` 验证码桥，自动抓取无法直接取得真实附件。
- 武汉理工大学官方 PDF 已下载但为 115 页扫描/图片型 PDF，当前无文本层可直接解析，暂不并入。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch144.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch145.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch146.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch147.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch148.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch149.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch150.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch151.csv`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 昆明理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 5,652 | 0 |

可追溯来源：
- 昆明理工大学 2026 年硕士研究生拟录取名单公示页：https://www.kmust.edu.cn/info/1166/56845.htm
- 昆明理工大学附件下载入口：`https://www.kmust.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1534810118&wbfileid=17827351`

质量修正：
- 新增昆明理工大学硕士拟录取 PDF 专项解析，优先使用 `pypdf` 文本顺序，避免 `pdftotext` 版式输出把 423 页名单拆成错位记录。
- 处理姓名、专业名称、学习方式和录取类别中的 PDF 换行空格，例如复姓/四字姓名、`非全日 制`、`非定向就 业`。
- batch151 清洗表 5,652 条；序号 1-5652 连续无缺口，缺少人员姓名 0，缺少考生编号 0，缺少录取专业 0，需人工复核 0。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：191,720 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：191,720 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：291 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：197,430 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：197,430 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：443 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，258 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：218 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 444 行（含表头）、Coverage 431 行（含表头）、Public_Records 197,431 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-25 追加批次：batch152 云南师范/新疆大学/云南农业大学

batch152 继续从剩余缺口中筛选可结构化官网来源。云南师范大学硕士招生栏目可追到 2026 年硕士研究生拟录取名单附件，但附件进入 VSB 验证码桥，已人工下载并按 PDF 文本层专项解析；新疆大学多个学院页和嵌入 PDF 可直接解析；云南农业大学推免拟录取名单 PDF 可直接解析。新疆师范大学栏目页及若干附件仍为 `download.jsp` 验证码桥，未自动入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch152.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch152/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch152/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch152/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch152/`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 云南师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 3,016 | 4 |
| 新疆大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 162 | 0 |
| 云南农业大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 12 | 0 |

可追溯来源：
- 云南师范大学硕士招生栏目：https://grs.ynnu.edu.cn/zsxx/sszs.htm
- 云南师范大学 2026 年硕士研究生招生考试拟录取名单公示页：https://grs.ynnu.edu.cn/info/1035/1503.htm
- 云南农业大学 2026 年推荐免试研究生拟录取名单公示页：https://yjs.ynau.edu.cn/info/1012/5865.htm
- 云南农业大学 2026 年推荐免试研究生拟录取名单 PDF：https://yjs.ynau.edu.cn/__local/2/1F/E3/2C6883BB5A5F687874C23A4F2A5_55729CC5_1C773.pdf
- 新疆大学中国语言文学学院 2026 年硕士研究生招生考试复试成绩及拟录取名单公示：https://rwxy.xju.edu.cn/info/1075/2899.htm
- 新疆大学地理与遥感科学学院 2026 年硕士拟录取相关公示入口：https://geography.xju.edu.cn/info/1026/1701.htm
- 新疆大学智能科学与技术学院 2026 年硕士拟录取相关公示入口：https://wljs.xju.edu.cn/info/1022/1675.htm
- 新疆大学电气工程学院 2026 年硕士拟录取名单 PDF：https://dqxy.xju.edu.cn/__local/3/08/41/4F250DCC596A7C141B7BE6D1BD6_B2831A51_19603.pdf
- 新疆大学材料科学与工程学院 2026 年推免硕士拟录取名单 PDF：https://clxy.xju.edu.cn/__local/0/E9/96/79EA790833D82154C6C58D6D2F9_7B0D7986_4E3FC.pdf

质量修正：
- 新增云南师范大学 PDF 专项解析，按“考生编号/姓名/录取院系所码/录取院系所名称/录取专业代码/录取专业名称/学习方式/复试成绩/综合成绩”抽取。
- 修复同校同专业同名但考生编号不同的清洗去重误合并问题。
- 云南师范大学 PDF 中 4 条源文本层缺少学习方式或成绩的记录已保留并标记需复核；batch152 清洗表缺少人员姓名 0，缺少专业字段 0。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：194,910 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：194,910 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：294 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：200,620 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：200,620 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：446 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，261 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：220 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 447 行（含表头）、Coverage 431 行（含表头）、Public_Records 200,621 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-25 追加批次：batch153 西南交通大学推免名单

batch153 继续从剩余缺口中筛选可结构化官网来源。自动抓取覆盖西南交通大学、中山大学、北京语言大学、华东师范大学、华东理工大学和上海中医药大学等入口；最终可入库记录来自西南交通大学 2026 年推荐免试研究生拟录取名单 PDF。该 PDF 附件进入 VSB 验证码桥，已人工下载并专项解析。北京语言大学硕士/推免名单附件仍为验证码桥，华东师范大学、华东理工大学页面多为“公示已结束”或图片名单，上海中医药大学页面未暴露可结构化人员表，中山大学旧入口返回 404，均暂未并入。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch153.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch153/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch153/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch153/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch153/`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南交通大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 1,815 | 0 |

可追溯来源：
- 西南交通大学 2026 年推荐免试研究生拟录取名单公示页：https://gsnews.swjtu.edu.cn/info/2127/32054.htm
- 西南交通大学附件下载入口：`https://gsnews.swjtu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1451357554&wbfileid=364628EA365C3A38DB41182B7860E005`
- 北京语言大学 2026 年硕士研究生拟录取名单通知：https://yjsy.blcu.edu.cn/info/1048/8229.htm
- 北京语言大学 2026 年硕士推免生拟录取名单通知：https://yjsy.blcu.edu.cn/info/1071/6569.htm
- 华东师范大学 2026 年硕士研究生拟录取名单公示：https://yjszs.ecnu.edu.cn/95/93/c43463a759187/page.htm
- 华东理工大学 2026 年硕士研究生拟录取名单公示：https://gschool.ecust.edu.cn/2026/0506/c12750a190107/page.htm
- 上海中医药大学 2026 年硕士研究生拟录取名单公示：https://yjsy.shutcm.edu.cn/2026/0429/c1125a173095/page.htm

质量修正：
- 新增西南交通大学推免 PDF 专项解析，修正通用表格解析将专业代码误作学院、分数误作专业的问题。
- 处理 PDF 文本层中“姓名+脱敏证件号”和“招生类型/学院/专业/成绩”跨行的个别记录。
- batch153 清洗表 1,815 条；缺少人员姓名 0，缺少证件号 0，缺少专业字段 0，需人工复核 0。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：196,725 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：196,725 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：295 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：202,435 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：202,435 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：447 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，262 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：221 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 448 行（含表头）、Coverage 431 行（含表头）、Public_Records 202,436 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-25 追加批次：batch154 西南林业/天津体育/哈尔滨体育推免名单

batch154 继续从剩余缺口中筛选可结构化官网来源。自动抓取覆盖西南林业大学、天津体育学院、哈尔滨体育学院 3 个官网公示页；3 个附件均进入 VSB 验证码下载桥，已人工下载 PDF，并按各自表格结构专项解析。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260525_batch154.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch154/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260525_batch154/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch154/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260525_batch154/`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南林业大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 2 | 0 |
| 天津体育学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 50 | 0 |
| 哈尔滨体育学院 | 2026 | recommendation_exemption_list | recommendation_exemption | 8 | 0 |

可追溯来源：
- 西南林业大学 2026 年推荐免试研究生（含直博生）拟录取名单公示：https://yjsy.swfu.edu.cn/info/1522/10996.htm
- 天津体育学院 2026 年接收优秀应届本科毕业生免试攻读硕士研究生拟录取名单公示：https://yjsb.tjus.edu.cn/info/1004/4527.htm
- 哈尔滨体育学院 2026 年硕士研究生接收推免生拟录取名单公示：https://www.hrbipe.edu.cn/yjsy/info/1011/1634.htm

质量修正：
- 新增西南林业大学 PDF 专项解析，修正通用表格解析把“序号/考生编号”误作学院和专业的问题。
- 新增天津体育学院 PDF 专项解析，保留脱敏身份证号、复试分数和报考专业。
- 新增哈尔滨体育学院 PDF 专项解析，过滤跨行表头“考试成绩”，避免其被误抽为人员姓名。
- batch154 清洗表 60 条；缺少人员姓名 0，缺少专业字段 0，需人工复核 0。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：196,785 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：196,785 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：298 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：202,495 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：202,495 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：450 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，265 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：224 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 451 行（含表头）、Coverage 431 行（含表头）、Public_Records 202,496 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch155 北京语言大学推免名单

batch155 继续从剩余缺口中筛选可结构化官网来源。北京语言大学 2026 年硕士推免生（含直博）拟录取名单官网页可访问，附件进入 VSB 验证码下载桥；已人工下载硕士推免生和直博生两个 PDF，并新增专项解析。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch155.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch155/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch155/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch155/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch155/`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 北京语言大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 286 | 0 |

可追溯来源：
- 北京语言大学关于公布 2026 年硕士推免生（含直博）拟录取名单的通知：https://yjsy.blcu.edu.cn/info/1071/6569.htm
- 北京语言大学 2026 年硕士推免生拟录取名单附件：`https://yjsy.blcu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2070671048&wbfileid=3D0BFB0D5FE199D871A062447C4B36DD`
- 北京语言大学 2026 年直博生拟录取名单附件：`https://yjsy.blcu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2070671048&wbfileid=A893CEE625ABFB88369DA21B25090546`

质量修正：
- 新增北京语言大学推免 PDF 专项解析，保留脱敏身份证号、专业代码、专业名称、复试成绩；直博名单额外保留录取导师。
- 过滤 PDF 页脚“第 1 页，共 1 页”，并未将官网页脚“友情链接/常用链接”进入正式清洗表。
- batch155 清洗表 286 条；缺少人员姓名 0，缺少证件号 0，缺少专业字段 0，需人工复核 0。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：197,071 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：197,071 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：299 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：202,781 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：202,781 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：451 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，266 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：226 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 452 行（含表头）、Coverage 431 行（含表头）、Public_Records 202,782 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-26 追加批次：batch156 南方医科大学推免名单

batch156 继续从剩余缺口中筛选可结构化官网来源。南方医科大学 2026 年招收推荐免试研究生拟录取名单官网页可访问，PDF 附件进入 VSB 验证码下载桥；已人工下载 PDF，并新增 `pdftotext` 编码回退和南方医科大学表格专项解析。湖南大学同批官网页和 PDF 附件也已抓取，但 PDF 为扫描图像型，本轮未将低可信 OCR 数据并入主表。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260526_batch156.csv`

抓取产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch156/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch156/school_year_summary.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch156/`
- `data/logs/graduate_outcomes_official_site_websearch_web_20260526_batch156/`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 南方医科大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 597 | 0 |

可追溯来源：
- 南方医科大学 2026 年招收推荐免试研究生拟录取名单公示：https://portal.smu.edu.cn/yzw/info/1002/11811.htm
- 南方医科大学附件下载入口：`https://portal.smu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1322327945&wbfileid=B12A2A520BE4CBEA794194760B200EF6`
- 湖南大学 2026 年推荐免试研究生拟录取名单公示（已抓取原始 PDF，未结构化入表）：https://gra.hnu.edu.cn/info/1075/10263.htm

质量修正：
- 新增 `pdftotext` 输出解码回退，在 Windows 下可正确读取 GBK/GB18030 字节输出。
- 新增南方医科大学 PDF 专项解析，保留身份证后 6 位、分委会、专业代码、专业名称、研究方向、学位类型、复试成绩和类别。
- 支持 `0710J3`、`0831Z1`、`1001Z1` 等含字母专业代码。
- batch156 清洗表 597 条；缺少人员姓名 0，缺少身份证后 6 位 0，缺少专业字段 0，需人工复核 0。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：197,668 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：197,668 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：300 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：203,378 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：203,378 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：452 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，267 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_graduate_outcome_crawler`：228 个测试通过（仅保留既有 ResourceWarning）。
- 工作簿结构校验：Overview 15 行、Source_Summary 453 行（含表头）、Coverage 431 行（含表头）、Public_Records 203,379 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-27 batch184：电子科技大学硕博拟录取名单

本轮从剩余缺口中继续筛选 B 类官网源。电子科技大学校级硕士拟录取公示页和博士拟录取公示页均可访问，已从校级页面展开 71 个学院/调剂链接。部分学院站点返回 HTTP 412 或站点挑战脚本，自动化爬虫无法取得真实正文；本轮仅合并可复现下载的 6 个官方 PDF 附件。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch184_uestc.csv`

抓取/清洗产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc_curated/records_clean_curated.csv`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 电子科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 918 | 0 |

可追溯来源：
- 电子科技大学 2026 年硕士研究生拟录取名单公示：https://yz.uestc.edu.cn/info/1007/5774.htm
- 电子科技大学 2026 年博士研究生拟录取名单公示：https://yz.uestc.edu.cn/info/1004/5834.htm
- 信息与通信工程学院 2026 年“骨干计划”南疆高校教师专项硕士研究生招生拟录取名单：`https://www.sice.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1938011446&wbfileid=16789389`
- 信息与通信工程学院 2026 年硕士研究生招生拟录取名单（调剂）：`https://www.sice.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1938011446&wbfileid=16787168`
- 信息与通信工程学院 2026 年博士研究生招生拟录取名单：`https://www.sice.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1938011446&wbfileid=16800526`
- 经济与管理学院 MBA 2026 年招生拟录取名单：`https://www.mba.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2019218082&wbfileid=16781468`
- 经济与管理学院 MBA 2026 年招生递补拟录取名单：`https://www.mba.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2019218082&wbfileid=16787567`
- 公共管理学院 2026 年 MPA 硕士研究生招生拟录取名单：`https://mpa.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1877930436&wbfileid=17965777`

质量修正：
- 新增电子科技大学 PDF 专项解析，修复通用解析把 MBA/MPA 表格拆成空姓名/分数字段，以及把信通学院博士外语成绩误作专业的问题。
- 统一保留初试总成绩、笔试/思政成绩、外语测试成绩、综合考核成绩、复试总成绩、加权总成绩、方向码、学习方式、录取类别等到 `remarks`。
- 对站点挑战脚本和 HTTP 412 页面不做伪造抓取，保留失败日志：`data/logs/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc/graduate_outcome_failures.jsonl`。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：210,531 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：210,531 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：345 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：216,241 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：216,241 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：497 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，301 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch184_uestc`：4 个测试通过。
- batch184 curated：918 条，缺少人员姓名 0，缺少专业字段 0，需人工复核 0，明确非拟录取状态 0。
- B 主表全局非拟录取状态扫描：`是否拟录取: 否`、`放弃复试`、`拟不录取`、`不予录取`、`进入复试名单`、`复试不合格` 命中 0 条。
- 工作簿结构校验：Overview 15 行、Source_Summary 498 行（含表头）、Coverage 431 行（含表头）、Public_Records 216,242 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-27 batch181/batch183：南京邮电大学、中国地质大学（武汉）及全局非拟录取过滤

本轮从剩余缺口中继续筛选 B 类官网源。南京邮电大学博士信息公开页可直接下载嵌入 PDF；中国地质大学（武汉）多个学院官网页可直接抓取附件或页面内名单。南京理工大学 2026 年硕士拟录取公示页已检索到，但本地请求校级页返回 410，直链 PDF 返回“出错啦”HTML，暂作为不可复现下载源留证，不并入主表。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch181_njupt.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch182_njust.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260527_batch183_cug.csv`

抓取/清洗产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch181_njupt/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch181_njupt_curated/records_clean_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch182_njust/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch183_cug/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch183_cug_curated/records_clean_curated.csv`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 南京邮电大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 227 | 0 |
| 中国地质大学（武汉） | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,010 | 0 |

可追溯来源：
- 南京邮电大学 2026 年博士研究生拟录取名单（第一批次）：http://yzb.njupt.edu.cn/2026/0430/c11142a301278/page.htm
- 南京邮电大学嵌入 PDF：http://yzb.njupt.edu.cn/_upload/article/files/0c/78/68d6839f485bba868e143392ce53/e542a67a-aa12-4aa3-a677-661a9f53feb7.pdf
- 中国地质大学（武汉）经济管理学院：https://jgxy.cug.edu.cn/info/1137/17504.htm
- 中国地质大学（武汉）国家 GIS 工程技术研究中心：https://gis.cug.edu.cn/info/1019/2638.htm
- 中国地质大学（武汉）材料与化学学院：https://chxy.cug.edu.cn/info/1060/35491.htm
- 中国地质大学（武汉）环境学院：https://ses.cug.edu.cn/info/1121/14494.htm
- 中国地质大学（武汉）地信学院：https://xgxy.cug.edu.cn/info/1013/35910.htm
- 中国地质大学（武汉）地质过程与矿产资源国家重点实验室：https://gpmr.cug.edu.cn/info/1017/3963.htm
- 中国地质大学（武汉）地球物理与空间信息学院：https://dkxy.cug.edu.cn/info/1037/7673.htm
- 中国地质大学（武汉）工程学院：https://gcxy.cug.edu.cn/info/1186/7476.htm
- 中国地质大学（武汉）地质调查研究院招生录取列表：https://ddy.cug.edu.cn/rcpy/zslq.htm

质量修正：
- 新增南京邮电大学博士 PDF 专项解析，修正通用解析将“身份证后四位”列误作 `person_name` 的问题；保留官方脱敏姓名、考生编号、后四位、考试方式、学院和专业。
- 新增中国地质大学（武汉）批次修复器，修复 GIS 中心 PDF 中姓名错位到 `major` 的记录；将分数/排名片段从 `college` 移入 `remarks`；按“姓名+考生号+来源”折叠 78 条互补重复；剔除 20 条 `放弃复试` 等非拟录取状态。
- 对 B 主表做全局非拟录取过滤，删除早前混入的 2,301 条明确非拟录取记录（华南师范大学 2,118 条、沈阳药科大学 104 条、河北医科大学 77 条、江苏科技大学 1 条、海南医科大学 1 条）。过滤说明见 `data/processed/graduate_outcomes_official_site_recommendation_master/non_admission_filter_20260527.txt`。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：209,613 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：209,613 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：344 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：215,323 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：215,323 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：496 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，300 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch181_njupt tests.test_curate_batch183_cug`：9 个测试通过。
- 批次质量扫描：南京邮电大学 227 条、中国地质大学（武汉）1,010 条，缺少人员姓名 0，需人工复核 0。
- B 主表全局非拟录取状态扫描：`是否拟录取: 否`、`放弃复试`、`拟不录取`、`不予录取`、`进入复试名单`、`复试不合格` 命中 0 条。
- 工作簿结构校验：Overview 15 行、Source_Summary 497 行（含表头）、Coverage 431 行（含表头）、Public_Records 215,324 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch227：天津科技大学拟录取 PDF 专项解析

本轮从剩余缺口中继续筛选 B 类官网源。天津科技大学信息公开页需要携带站点 cookie 才能访问，通用爬虫未跟随 302 进入正文；已从官方信息公开页和正文 iframe 定位 5 个 PDF 并专项解析入库。山东理工大学和青岛理工大学页面已抓取留证，但山东理工关键“附件1.pdf”在页面 HTML 中未暴露真实链接，青岛理工公示正文当前无名单附件链接，本轮不合并其人员记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch227_tust_sdut_qut.csv`

抓取/清洗产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch227_tust_sdut_qut/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch227_tust_sdut_qut_curated/records_clean_curated.csv`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 天津科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,062 | 0 |
| 天津科技大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 28 | 0 |

可追溯来源：
- 天津科技大学 2026 年硕士研究生一志愿拟录取考生名单公示（第一批）：https://yjs.tust.edu.cn/zsgz/tzggzs/817ec904ff9640869b7b4c9efaa58fe6.htm
- 天津科技大学 2026 年硕士研究生一志愿拟录取考生名单公示（第二批）：https://yjs.tust.edu.cn/zsgz/tzggzs/ddb0f6e59614476d8acc495351f15b53.htm
- 天津科技大学 2026 年硕士研究生调剂拟录取考生名单公示（第一批）：https://yjs.tust.edu.cn/zsgz/tzggzs/9fa250a69a9f4867a7e37b0042c4742b.htm
- 天津科技大学 2026 年硕士研究生调剂拟录取考生名单公示（第二批）：https://yjs.tust.edu.cn/zsgz/tzggzs/5572f8f278f3412ebbf0ded60cdb83ad.htm
- 天津科技大学接收 2026 届优秀应届本科毕业生免试攻读硕士学位研究生拟录取名单公示：https://yjs.tust.edu.cn/zsgz/tzggzs/a9a5f560dda246a8a0b60245f6111800.htm

质量修正：
- 新增 `scripts/curate_batch227_tust.py`，使用 `pdftotext -layout` 专项解析 WPS 导出的横向 PDF 表格。
- 修复少数民族姓名、专业方向和学位类别跨行导致的姓名/方向缺失；接收推免名单源表无考生编号，保留空 `student_id` 并用姓名、排名、来源 URL 建立稳定记录。
- 山东理工、青岛理工只保留官方页面抓取证据；未对缺失附件链接做猜测下载。

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：235,763 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：235,763 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：389 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：241,473 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：241,473 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：542 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，342 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch227_tust`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：73 个测试通过。
- batch227 curated：2,090 条，缺少人员姓名 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 543 行（含表头）、Coverage 431 行（含表头）、Public_Records 241,474 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch228：哈尔滨师范大学一志愿拟录取 PDF

本轮继续从剩余缺口中补可复现官网源。哈尔滨师范大学研究生学院 2026 年硕士研究生招生一志愿拟录取名单公示页可直接访问，并暴露官方 PDF 附件；通用爬虫已抓取页面和 PDF，但 PDF 带斜向水印，通用解析无法结构化。新增专项解析，按 15 位考生编号定位表格行并剔除水印干扰。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch228_hrbnu.csv`

抓取/清洗产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch228_hrbnu/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch228_hrbnu_curated/records_clean_curated.csv`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 哈尔滨师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,665 | 0 |

可追溯来源：
- 哈尔滨师范大学 2026 年硕士研究生招生一志愿拟录取名单公示：http://yjsxy.hrbnu.edu.cn/info/1045/26630.htm
- 官方 PDF 附件：http://yjsxy.hrbnu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1255513605&wbfileid=D94C4D5DD4B897AB9BB988B9EB8141C1

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：237,428 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：237,428 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：391 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：243,138 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：243,138 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：543 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，343 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch228_hrbnu`：1 个测试通过。
- batch228 curated：1,665 条，缺少人员姓名 0，缺少考生编号 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 544 行（含表头）、Coverage 431 行（含表头）、Public_Records 243,139 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch231-batch232：山西师范大学、陕西中医药大学官网 PDF

本轮继续补 B 类官网人员级拟录取数据。山西师范大学官网博士拟录取公告正文通过 `showVsbpdfIframe` 直嵌官方 PDF；陕西中医药大学研招网一志愿拟录取公告正文直接链接 `img.sntcm.edu.cn` 官方 PDF。两者均可无验证码复现下载。山西中医药大学、广东药科大学、大连外国语大学、桂林医科大学、南京财经大学等页面虽有官网公告，但附件下载当前要求验证码；沈阳师范大学、华东师范大学、齐鲁工业大学、聊城大学等页面当前只保留公告正文或“公示已结束”文字，名单链接未暴露或已撤下，本轮不做猜测下载。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch231_sxnu_doctor.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch232_sntcm.csv`

抓取/清洗产物：
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch231_sxnu_doctor/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch231_sxnu_doctor_curated/records_clean_curated.csv`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch232_sntcm/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch232_sntcm_curated/records_clean_curated.csv`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 山西师范大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 82 | 0 |
| 陕西中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 769 | 0 |

可追溯来源：
- 山西师范大学 2026 年招收以普通招考方式攻读博士学位研究生拟录取名单公示：https://grc.sxnu.edu.cn/info/1077/10914.htm
- 山西师范大学官方 PDF：https://grc.sxnu.edu.cn/__local/9/76/BC/DE6CBD556A901D06BAEC8EA2DAD_7E02CD11_13685.pdf
- 陕西中医药大学 2026 年硕士研究生拟录取考生名单公示（一志愿）：http://yzb.sntcm.edu.cn/xwdt/125213.htm
- 陕西中医药大学官方 PDF：http://img.sntcm.edu.cn/HIWCMyzb/202604/202604040418058.pdf

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：238,279 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：238,279 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：393 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：243,989 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：243,989 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：545 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，345 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm`：2 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：76 个测试通过。
- batch231/batch232 curated：合计 851 条，缺少人员姓名 0，缺少考生编号 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 546 行（含表头）、Coverage 431 行（含表头）、Public_Records 243,990 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch233：兰州理工大学学院官网内嵌 PDF

本轮继续补 B 类官网人员级拟录取数据。兰州理工大学微电子现代产业学院一志愿拟录取公告和机电工程学院二次调剂拟录取公告均可直接访问，正文通过 `showVsbpdfIframe` 直嵌官方 PDF；同期复核的石油化工学院、土木工程学院等页面附件仍进入验证码下载桥，本轮不绕过验证码、不入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch233_lut_embedded_pdfs.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch233_lut_embedded_pdfs/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch233_lut_embedded_pdfs/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch233_lut_embedded_pdfs_curated/records_clean_curated.csv`
- `scripts/curate_batch233_lut_embedded_pdfs.py`
- `tests/test_curate_batch233_lut_embedded_pdfs.py`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 兰州理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 12 | 0 |

可追溯来源：
- 兰州理工大学微电子现代产业学院 2026 年硕士研究生招生复试一志愿拟录取结果公示：https://weidianzi.lut.edu.cn/info/1019/1934.htm
- 微电子现代产业学院官方 PDF：https://weidianzi.lut.edu.cn/__local/6/43/26/A4180401571DB8887F1DE1E3243_60345B89_AD3E.pdf
- 兰州理工大学机电工程学院 2026 年硕士研究生招生复试（二次调剂）拟录取结果公示：https://jidian.lut.edu.cn/info/1870/18350.htm
- 机电工程学院官方 PDF：https://jidian.lut.edu.cn/__local/0/7B/F1/83EF0F22F94E82FE64142ED0575_B962DAF0_1D137.pdf

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：238,291 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：238,291 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：394 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：244,001 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：244,001 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：546 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，346 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs`：3 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：77 个测试通过。
- batch233 curated：12 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 547 行（含表头）、Coverage 431 行（含表头）、Public_Records 244,002 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch234：中国音乐学院官网 PDF

本轮继续补 B 类官网人员级拟录取数据。中国音乐学院研究生院“面向港澳台地区研究生招生考试拟录取名单公示”页面可访问，正文内嵌站内 PDF，PDF 直链返回 `application/pdf`。同站“全国硕士研究生招生拟录取考生提交体检报告”页面和 PDF 也可访问，但内容只是体检报告提交通知，不含名单，留证不入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch234_ccmusic.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch234_ccmusic/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch234_ccmusic/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch234_ccmusic_curated/records_clean_curated.csv`
- `scripts/curate_batch234_ccmusic.py`
- `tests/test_curate_batch234_ccmusic.py`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中国音乐学院 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 2 | 0 |

可追溯来源：
- 中国音乐学院 2026 年面向港澳台地区研究生招生考试拟录取名单公示：https://yjsy.ccmusic.edu.cn/zsgz/ssyjszs/aadc4ffd447541e8a4850b8a7aaadf3a.htm
- 官方 PDF：https://yjsy.ccmusic.edu.cn/docs/2026-05/eac5066c44af43d596ea79dbb6833684.pdf
- 中国音乐学院 2026 年全国硕士研究生招生拟录取考生提交体检报告的通知（留证，未入库）：https://yjsy.ccmusic.edu.cn/zsgz/ssyjszs/9c0334d6898e408e8874f0372adc1b3c.htm

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：238,293 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：238,293 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：395 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：244,003 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：244,003 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：547 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，347 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch234_ccmusic`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic`：4 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：78 个测试通过。
- batch234 curated：2 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0，页面误抽 `研究生院/受理时段` 残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 548 行（含表头）、Coverage 431 行（含表头）、Public_Records 244,004 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch235：香港中文大学（深圳）数据科学学院 HTML/XLSX

本轮继续补 B 类官网人员级推免/拟录取数据。香港中文大学（深圳）数据科学学院 2025 年拟录取推荐免试硕士研究生名单正文表格可直接解析；同院 2026 年秋季入学直硕拟录取名单以官网 XLSX 附件发布，可直接下载并解析。同期复核的医学院页面当前返回“您未被授权访问此页面”，留证但不入库。

通用爬虫 3 个种子抓取 3 个文档，原始结构化 38 条。为校正 2026 XLSX 的入学年份、补齐学院/本科专业字段，并规范页面中的异体字，新增 `scripts/curate_batch235_cuhk_sz.py` 和 `tests/test_curate_batch235_cuhk_sz.py` 专项清洗。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch235_cuhk_sz.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch235_cuhk_sz/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch235_cuhk_sz/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch235_cuhk_sz_curated/records_clean_curated.csv`
- `scripts/curate_batch235_cuhk_sz.py`
- `tests/test_curate_batch235_cuhk_sz.py`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 香港中文大学（深圳） | 2025 | recommendation_exemption_list | recommendation_exemption | 9 | 0 |
| 香港中文大学（深圳） | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 29 | 0 |

可追溯来源：
- 香港中文大学（深圳）数据科学学院 2025 年拟录取推荐免试硕士研究生名单公示：https://sds.cuhk.edu.cn/article/2036
- 香港中文大学（深圳）数据科学学院直硕拟录取名单公示：https://sds.cuhk.edu.cn/article/2309
- 2026 年秋季入学直硕拟录取名单 XLSX：https://sds.cuhk.edu.cn/sites/default/files/2025-11/%E9%A6%99%E6%B8%AF%E4%B8%AD%E6%96%87%E5%A4%A7%E5%AD%A6%EF%BC%88%E6%B7%B1%E5%9C%B3%EF%BC%89%E6%95%B0%E6%8D%AE%E7%A7%91%E5%AD%A6%E5%AD%A6%E9%99%A2%E7%9B%B4%E7%A1%95%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95%EF%BC%882026%E5%B9%B4%E7%A7%8B%E5%AD%A3%E5%85%A5%E5%AD%A6%EF%BC%89.xlsx
- 医学院候选页（未授权访问，未入库）：https://medpg.cuhk.edu.cn/article/103

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：238,331 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：238,331 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：397 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：244,041 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：244,041 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：549 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，348 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch235_cuhk_sz`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz`：5 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：79 个测试通过。
- batch235 curated：38 条，缺少人员姓名 0，缺少录取专业 0，缺少学院 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 550 行（含表头）、Coverage 431 行（含表头）、Public_Records 244,042 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch236：中国人民大学 2018 年硕士统考拟录取 HTML

本轮继续补 B 类官网人员级拟录取数据。中国人民大学研究生院 2018 年硕士研究生全国统考拟录取名单第一批、第二批页面仍可公开访问，正文为完整 HTML 表格。虽然年份较早，但来源稳定、字段完整，可作为“考研拟录取”方向官网数据补入覆盖缺口。

通用爬虫 2 个种子抓取 2 个文档，原始结构化 2,805 条；质检发现第一批页面中 1 条表头被误抽为人员记录，且第一批因页面导航词被误分类为推免。按 TDD 新增 `scripts/curate_batch236_ruc_2018_admission.py` 和 `tests/test_curate_batch236_ruc_2018_admission.py`，统一更正为 `postgraduate_admission_list / postgraduate_exam_or_admission`，并保留研究方向、学习形式、初试/复试/加权成绩和备注，最终入库 2,804 条人员级记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch236_ruc_2018_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch236_ruc_2018_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch236_ruc_2018_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch236_ruc_2018_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch236_ruc_2018_admission.py`
- `tests/test_curate_batch236_ruc_2018_admission.py`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中国人民大学 | 2018 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,804 | 0 |

可追溯来源：
- 中国人民大学 2018 年硕士研究生全国统考拟录取名单公示（第一批）：https://grs.ruc.edu.cn/info/1083/1273.htm
- 中国人民大学 2018 年硕士研究生全国统考拟录取名单公示（第二批）：https://grs.ruc.edu.cn/info/1083/1348.htm

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：241,135 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：241,135 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：398 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：246,845 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：246,845 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：550 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，349 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch236_ruc_2018_admission`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz tests.test_curate_batch236_ruc_2018_admission`：6 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：80 个测试通过。
- batch236 curated：2,804 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0，表头残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 551 行（含表头）、Coverage 431 行（含表头）、Public_Records 246,846 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch237：中国民航大学 2025 年拟录取 PDF

本轮继续补 B 类官网人员级拟录取和推免接收数据。中国民航大学研究生院 2025 年硕士研究生拟录取名单公示页、2025 年接收推荐免试攻读硕士研究生拟录取名单公示页均可访问，页面附件可直接下载 PDF。通用爬虫自动跟取两个 PDF，原始结构化 1,439 条。

通用解析能抽取人员和代码，但硕士拟录取 PDF 的录取专业字段为空。按 TDD 新增 `scripts/curate_batch237_cauc.py` 和 `tests/test_curate_batch237_cauc.py`，从 PDF 文本层重新抽取：2025 年硕士拟录取 1,422 条，2025 年接收推免生拟录取 17 条；补齐 `admission_major`，并保留成绩、学习形式、录取类别、拟录取状态和专项计划备注。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch237_cauc.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch237_cauc/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch237_cauc/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch237_cauc_curated/records_clean_curated.csv`
- `scripts/curate_batch237_cauc.py`
- `tests/test_curate_batch237_cauc.py`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 中国民航大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,422 | 0 |
| 中国民航大学 | 2025 | incoming_recommendation_admission_list | recommendation_exemption | 17 | 0 |

可追溯来源：
- 中国民航大学 2025 年硕士研究生拟录取名单公示：https://www.cauc.edu.cn/yjsy/info/1124/2230.htm
- 2025 年拟录取名单公示 PDF：https://www.cauc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1787525762&wbfileid=11984439
- 中国民航大学 2025 年接收推荐免试攻读硕士研究生拟录取名单公示：https://www.cauc.edu.cn/yjsy/info/1124/2087.htm
- 2025 年接收推免生拟录取名单 PDF：https://www.cauc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1787525762&wbfileid=11977509

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：242,574 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：242,574 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：400 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：248,284 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：248,284 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：552 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，350 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch237_cauc`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz tests.test_curate_batch236_ruc_2018_admission tests.test_curate_batch237_cauc`：7 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：81 个测试通过。
- batch237 curated：1,439 条，缺少人员姓名 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 553 行（含表头）、Coverage 431 行（含表头）、Public_Records 248,285 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch238：成都理工大学推免 PDF

本轮继续补 B 类官网推免拟录取数据。成都理工大学研究生院主公告页实时返回 HTTP 412，但同校计算机与网络安全学院官网保留了静态 PDF 直链，PDF 可直接下载并包含 2025 年推荐免试研究生拟录取名单。通用解析抽出 8 条，其中混入 `研究生/支教团` 两条碎片且学院名跨行错位；本批新增 `scripts/curate_batch238_cdut_recommendation.py` 和 `tests/test_curate_batch238_cdut_recommendation.py`，按 PDF 文本结构重建 6 条真实人员记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch238_cdut_recommendation.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch238_cdut_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch238_cdut_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch238_cdut_recommendation_curated/records_clean_curated.csv`
- `scripts/curate_batch238_cdut_recommendation.py`
- `tests/test_curate_batch238_cdut_recommendation.py`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 成都理工大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 6 | 0 |

可追溯来源：
- 成都理工大学 2025 年推荐免试研究生（含直博生）拟录取名单公示（返回 412，留证）：https://gra.cdut.edu.cn/info/1007/3934.htm
- 计算机与网络安全学院官方 PDF：https://cist.cdut.edu.cn/__local/1/3C/A8/76104FAC3A34A88B53467FDBB02_B5BB8255_2AFE1.pdf

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：242,580 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：242,580 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：401 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：248,290 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：248,290 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：553 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，351 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch238_cdut_recommendation`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz tests.test_curate_batch236_ruc_2018_admission tests.test_curate_batch237_cauc tests.test_curate_batch238_cdut_recommendation`：8 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：82 个测试通过。
- batch238 curated：6 条，缺少人员姓名 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0，`研究生/支教团` 碎片姓名残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 554 行（含表头）、Coverage 431 行（含表头）、Public_Records 248,291 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch239：武汉轻工大学 2025 年硕士拟录取 PDF

本轮继续补 B 类官网人员级拟录取数据。武汉轻工大学信息公开网保留 2025 年硕士研究生拟录取名单官方 PDF 直链，PDF 文本层规整，通用解析可抽取 1,293 条人员记录。为保留更完整的成绩字段，新增 `scripts/curate_batch239_whpu_admission.py` 和 `tests/test_curate_batch239_whpu_admission.py`，按 PDF 表格行重建初试总分、复试总分、综合成绩、学习形式和备注。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch239_whpu_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch239_whpu_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch239_whpu_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch239_whpu_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch239_whpu_admission.py`
- `tests/test_curate_batch239_whpu_admission.py`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 武汉轻工大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,293 | 0 |

可追溯来源：
- 武汉轻工大学 2025 年硕士研究生拟录取名单 PDF：https://xxgkw.whpu.edu.cn/__local/0/12/BB/9B2441AF41EA488AA5E18F18FF3_3E926D35_5B255.pdf

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：243,873 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：243,873 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：402 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：249,583 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：249,583 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：554 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，352 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch239_whpu_admission`：1 个测试通过。
- `python -m unittest tests.test_curate_batch231_sxnu_doctor tests.test_curate_batch232_sntcm tests.test_curate_batch233_lut_embedded_pdfs tests.test_curate_batch234_ccmusic tests.test_curate_batch235_cuhk_sz tests.test_curate_batch236_ruc_2018_admission tests.test_curate_batch237_cauc tests.test_curate_batch238_cdut_recommendation tests.test_curate_batch239_whpu_admission`：9 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：83 个测试通过。
- batch239 curated：1,293 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 555 行（含表头）、Coverage 431 行（含表头）、Public_Records 249,584 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch240：西南石油大学学院级拟录取 PDF

本轮继续补 B 类官网人员级拟录取数据。西南石油大学官网保留石油与天然气工程学院 2025 年硕士研究生递补拟录取 PDF、土木工程与测绘学院 2025 年硕士研究生调剂第一批拟录取 PDF 两份静态附件。通用解析只得到 6 条且存在字段错位；本批新增 `scripts/curate_batch240_swpu_admission_pdfs.py` 和 `tests/test_curate_batch240_swpu_admission_pdfs.py`，按 PDF 文本层重建 25 条人员记录。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch240_swpu_admission_pdfs.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch240_swpu_admission_pdfs/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch240_swpu_admission_pdfs/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch240_swpu_admission_pdfs_curated/records_clean_curated.csv`
- `scripts/curate_batch240_swpu_admission_pdfs.py`
- `tests/test_curate_batch240_swpu_admission_pdfs.py`

本批入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西南石油大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 25 | 0 |

可追溯来源：
- 石油与天然气工程学院 2025 年硕士研究生递补拟录取名单 PDF：https://www.swpu.edu.cn/__local/8/15/C7/92E70E0AC85E6ADA3E0D0EB5EEC_5CAC0528_2642D.pdf
- 土木工程与测绘学院 2025 年硕士研究生调剂第一批拟录取名单 PDF：https://www.swpu.edu.cn/__local/2/3D/18/462CA89B77DEAFBE7381FAAFCB4_3FD01EB0_FB65.pdf

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：243,898 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：243,898 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：403 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：249,608 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：249,608 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：555 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，353 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch240_swpu_admission_pdfs`：1 个测试通过。
- `python -m unittest tests.test_curate_batch236_ruc_2018_admission tests.test_curate_batch237_cauc tests.test_curate_batch238_cdut_recommendation tests.test_curate_batch239_whpu_admission tests.test_curate_batch240_swpu_admission_pdfs`：5 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：238 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：84 个测试通过。
- batch240 curated：25 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 556 行（含表头）、Coverage 431 行（含表头）、Public_Records 249,609 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-28 batch241-batch242：西安电子科技大学与青岛理工大学官网 PDF 入库

本轮继续从剩余缺口中筛选可直接抓取的官网拟录取来源。西安电子科技大学数学与统计学院两份 2025 年硕士研究生拟录取 PDF 可直接下载，通用解析得到 62 条；新增 `scripts/curate_batch241_xidian_math_admission.py` 和 `tests/test_curate_batch241_xidian_math_admission.py`，补齐学院字段并规范化输出。青岛理工大学 2025 年度硕士研究生拟录取名单为整校 PDF，通用解析得到 1,509 条；新增 `scripts/curate_batch242_qut_admission_pdf.py` 和 `tests/test_curate_batch242_qut_admission_pdf.py` 做批次可复现清洗。

同步修复 `scripts/graduate_outcome_crawler.py` 汇总逻辑：从 CSV 读回的 `"False"` 不再被误计为 `needs_review_count`，并新增对应回归测试。

本轮探测但未入库的官网源：
- 东北师范大学多学院附件页返回验证码下载桥，本轮不绕过验证码。
- 中国海洋大学 2026 推免 PDF 裸请求和同站 Referer 请求均返回 403，本轮不绕过访问限制。
- 南京财经大学、江苏师范大学部分公示页已过公示期或搜索命中旧页，官网页面未保留可下载名单 href。
- 上海科技大学名单正文为图片嵌入，本轮未将图片 OCR 结果作为稳定管道入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch241_xidian_math_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260528_batch242_qut_admission_pdf.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch241_xidian_math_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch241_xidian_math_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch241_xidian_math_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch241_xidian_math_admission.py`
- `tests/test_curate_batch241_xidian_math_admission.py`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch242_qut_admission_pdf/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch242_qut_admission_pdf/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch242_qut_admission_pdf_curated/records_clean_curated.csv`
- `scripts/curate_batch242_qut_admission_pdf.py`
- `tests/test_curate_batch242_qut_admission_pdf.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西安电子科技大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 62 | 0 |
| 青岛理工大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,509 | 0 |

可追溯来源：
- 西安电子科技大学数学与统计学院 2025 年硕士研究生招生一志愿拟录取名单 PDF：`https://math.xidian.edu.cn/system/_content/download.jsp?owner=1558931063&urltype=news.DownloadAttachUrl&wbfileid=C1F63EAFA2A1DFD80238811641165286`
- 西安电子科技大学数学与统计学院 2025 年硕士研究生招生统计学调剂拟录取名单 PDF：`https://math.xidian.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1558931063&wbfileid=FF194589103FB42711E4C20037EBF9BB`
- 青岛理工大学 2025 年度硕士研究生拟录取名单 PDF：`https://yjsh.qut.edu.cn/__local/6/A0/E7/B022F1443037165009E1D58BC1B_59F44F96_78727.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：245,469 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：245,469 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：405 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,179 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,179 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：557 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，355 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch241_xidian_math_admission tests.test_curate_batch242_qut_admission_pdf`：2 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：86 个测试通过。
- batch241 curated：62 条，缺少人员姓名 0，缺少考生编号 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- batch242 curated：1,509 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，明确非拟录取状态 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 558 行（含表头）、Coverage 431 行（含表头）、Public_Records 251,180 行（含表头）；公式单元格 0，公式错误 0。

## 2026-05-29 batch243：塔里木大学硕士一志愿录取结果 PDF

本轮继续补 B 类官网人员级拟录取数据。塔里木大学研究生处通知公告页保留 2026 年硕士研究生一志愿考生复试成绩及录取结果 PDF 直链，附件可直接下载。同期抓取的“塔里木大学2026年硕士研究生拟录取结果公示”PDF 为公示说明正文，文本中提示“详见附件”但未包含人员名单，本轮留存原始文档证据、不入库。

通用解析从一志愿 PDF 得到 439 条候选记录，但其中含 7 条分页表头和 61 条“是否录取=否”的行。新增 `scripts/curate_batch243_taru_admission.py` 和 `tests/test_curate_batch243_taru_admission.py`，按 PDF 文本层重建人员记录，只保留最终录取标记为“是”的考生，最终入库 371 条。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260529_batch243_taru_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260529_batch243_taru_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260529_batch243_taru_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260529_batch243_taru_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch243_taru_admission.py`
- `tests/test_curate_batch243_taru_admission.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 塔里木大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 371 | 0 |

可追溯来源：
- 塔里木大学 2026 年硕士研究生招生第一批次一志愿考生复试成绩及录取结果公示 PDF：`https://yjsb.taru.edu.cn/__local/3/9F/D4/8F60D02C5578C92BD23BF082ADE_9B5FB6D3_40612.pdf`
- 塔里木大学 2026 年硕士研究生拟录取结果公示说明 PDF：`https://yjsb.taru.edu.cn/__local/3/26/BC/AF946E085A4885689C22411A2E0_7B43EA37_B9F2.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：245,840 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：245,840 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：406 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,550 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,550 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：558 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，356 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch243_taru_admission`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：87 个测试通过。
- batch243 curated：371 条，缺少人员姓名 0，坏考生编号 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/复试成绩不合格/加试不合格/缺考/候补` 残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 559 行（含表头）、Coverage 431 行（含表头）、Public_Records 251,551 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch244：三峡大学健康医学院拟录取 PDF

本轮继续补 B 类官网人员级拟录取数据。三峡大学健康医学院官网首页“招生工作”栏目直接列出 2026 年硕士研究生拟录取考生名单公示第一批和调剂复试拟录取考生名单公示第二批，页面内嵌 PDF 均可直接下载。通用解析得到 107 条候选记录，但字段存在姓名/考生编号错位、专业代码误入姓名等问题。新增 `scripts/curate_batch244_ctgu_health_admission.py` 和 `tests/test_curate_batch244_ctgu_health_admission.py`，按 PDF 文本层重建人员记录，最终入库 102 条。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch244_ctgu_health_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch244_ctgu_health_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch244_ctgu_health_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch244_ctgu_health_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch244_ctgu_health_admission.py`
- `tests/test_curate_batch244_ctgu_health_admission.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 三峡大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 102 | 0 |

可追溯来源：
- 健康医学院 2026 年硕士研究生拟录取考生名单公示第一批 PDF：`https://jkyxy.ctgu.edu.cn/__local/B/F3/04/645C9F3068D17EA0D7B220A9E0C_BF8D961B_167C5.pdf`
- 健康医学院 2026 年硕士研究生调剂复试拟录取考生名单公示第二批 PDF：`https://jkyxy.ctgu.edu.cn/__local/4/7E/9D/5B34B462C4AACEDB21A986B4802_07C184C4_C3F9.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：245,942 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：245,942 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：407 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,652 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,652 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：559 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，357 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch244_ctgu_health_admission`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：88 个测试通过。
- batch244 curated：102 条，缺少人员姓名 0，坏考生编号 0，空学院 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- 工作簿结构校验：Overview 15 行、Source_Summary 560 行（含表头）、Coverage 431 行（含表头）、Public_Records 251,653 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch245：上海理工大学理学院一志愿拟录取 PDF

本轮继续补 B 类官网人员级拟录取数据。上海理工大学理学院官网静态 PDF 可直接下载，通用解析得到 33 条人员记录，但学院、录取专业和成绩字段未结构化且全部标记需复核。新增 `scripts/curate_batch245_usst_lxy_admission.py` 和 `tests/test_curate_batch245_usst_lxy_admission.py`，按 PDF 文本层重建一志愿拟录取记录，补齐学院、专业、初试成绩、复试成绩、总成绩和退役大学生士兵专项计划备注，最终入库 33 条。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch245_usst_lxy_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch245_usst_lxy_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch245_usst_lxy_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch245_usst_lxy_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch245_usst_lxy_admission.py`
- `tests/test_curate_batch245_usst_lxy_admission.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 上海理工大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 33 | 0 |

可追溯来源：
- 上海理工大学理学院 2026 年硕士研究生一志愿复试录取结果公示 PDF：`https://lxy.usst.edu.cn/_upload/article/files/88/d2/23dc2812494e8d088def5148c24d/7193cd58-d41f-42a9-902d-041d09138d7a.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：245,975 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：245,975 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：408 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,685 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,685 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：560 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，358 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch245_usst_lxy_admission`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：89 个测试通过。
- batch245 curated：33 条，缺少人员姓名 0，坏考生编号 0，空录取专业 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- 工作簿已重建：Overview 15 行、Source_Summary 561 行（含表头）、Coverage 431 行（含表头）、Public_Records 251,686 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch246：聊城大学推免拟录取 PDF

本轮继续补 B 类官网人员级推免拟录取数据。聊城大学研究生招生网 2025 年推荐免试硕士研究生拟录取名单 PDF 可直接下载。通用解析得到 170 条候选记录，其中 7 条为分页表头误识别；新增 `scripts/curate_batch246_lcu_recommendation.py` 和 `tests/test_curate_batch246_lcu_recommendation.py`，按 PDF 文本层重建真实人员记录，保留学院、专业代码、专业名称、复试成绩和专项计划备注，最终入库 163 条。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch246_lcu_recommendation.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch246_lcu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch246_lcu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch246_lcu_recommendation_curated/records_clean_curated.csv`
- `scripts/curate_batch246_lcu_recommendation.py`
- `tests/test_curate_batch246_lcu_recommendation.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 聊城大学 | 2025 | recommendation_exemption_list | recommendation_exemption | 163 | 0 |

可追溯来源：
- 聊城大学 2025 年推荐免试硕士研究生拟录取名单 PDF：`https://yz.lcu.edu.cn/docs/20241018150049513144.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：246,138 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：246,138 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：409 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,848 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,848 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：561 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，359 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch246_lcu_recommendation`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：90 个测试通过。
- batch246 curated：163 条，缺少人员姓名 0，分页表头姓名 0，缺少学院 0，缺少录取专业 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。名单原文不含考生编号，163 条均保留 `missing_student_id` 质量标记。
- 工作簿已重建：Overview 15 行、Source_Summary 562 行（含表头）、Coverage 431 行（含表头）、Public_Records 251,849 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch247：江苏师范大学推免拟录取 PDF

本轮继续补 B 类官网人员级推免拟录取数据。通过检索命中江苏师范大学研究生院 2026 年推荐免试硕士研究生拟录取名单公示页，页面内嵌 `pdfsrc` 指向官方 PDF，直连返回 `200 application/pdf`。通用爬虫成功保存页面和 PDF，但通用解析只得到 1 条错位记录；新增 `scripts/curate_batch247_jsnu_recommendation.py` 和 `tests/test_curate_batch247_jsnu_recommendation.py`，按 PDF 文本层重建序号、姓名、脱敏身份证号、拟录取学院、专业代码、专业名称、学习形式和推免类型，最终入库 113 条。

同期复核山东理工大学 2026 年一志愿、第二批次和推免拟录取官网公示页；页面正文可访问，但名单附件在 HTML 中仅剩 `附件1.pdf` 或名单文件名文本，没有可请求的附件链接。按“不猜隐藏地址、不绕过站点限制”的规则，本轮记录为可见但不可自动抓取，不入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch247_jsnu_recommendation.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch247_jsnu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch247_jsnu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch247_jsnu_recommendation_curated/records_clean_curated.csv`
- `scripts/curate_batch247_jsnu_recommendation.py`
- `tests/test_curate_batch247_jsnu_recommendation.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 江苏师范大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 113 | 0 |

可追溯来源：
- 江苏师范大学 2026 年推荐免试硕士研究生拟录取名单公示：`http://yjsy.jsnu.edu.cn/2e/d9/c10944a405209/page.htm`
- 官方 PDF 附件：`http://yjsy.jsnu.edu.cn/_upload/article/files/ca/08/ec9ecd2d4c2daa9bb3a54722897c/0baf68fa-b026-4a15-a7e3-2b00b68a4728.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：246,251 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：246,251 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：410 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：251,961 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：251,961 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：562 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，360 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch247_jsnu_recommendation`：1 个测试通过。
- batch247 curated：113 条，缺少人员姓名 0，缺少脱敏身份证号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补` 残留 0。
- 工作簿已重建：Overview 15 行、Source_Summary 563 行（含表头）、Coverage 431 行（含表头）、Public_Records 251,962 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch248：重庆交通大学硕士一志愿拟录取 PDF

本轮继续补 B 类官网人员级硕士拟录取数据。重庆交通大学研究生招生信息网 2025 年硕士招生成绩及拟录取结果公示（一志愿）PDF 为官方静态附件，直连返回 `200 application/pdf`。通用爬虫可下载 PDF，但默认解析把专业行误作 2,084 条候选记录，全部缺少姓名和准考证号且需复核。新增 `scripts/curate_batch248_cqjtu_admission.py` 和 `tests/test_curate_batch248_cqjtu_admission.py`，按 PDF 文本层以准考证号定位人员行，只保留 `拟录取` 状态，剔除 `不合格` 109 条和 `名额受限` 131 条，最终入库 1,813 条。

同期复核北京第二外国语学院官网旧推免 PDF、山西中医药大学调剂拟录取附件、沈阳师范大学 2026 拟录取公示页、齐鲁工业大学和南京理工大学公示页：北京第二外国语学院域名当前无法解析；山西中医药大学附件进入验证码下载桥；沈阳师范大学页面只有附件名文本无可请求链接；齐鲁工业大学公示页没有名单链接；南京理工大学附件跳转 404/无效文章参数。上述来源本轮均不入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch248_cqjtu_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch248_cqjtu_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch248_cqjtu_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch248_cqjtu_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch248_cqjtu_admission.py`
- `tests/test_curate_batch248_cqjtu_admission.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 重庆交通大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,813 | 0 |

可追溯来源：
- 重庆交通大学 2025 年硕士招生成绩及拟录取结果公示（一志愿）PDF：`https://yjszs.cqjtu.edu.cn/__local/E/EB/D8/88DAF14D0F7C9C26C90E97E6BF5_FE0B182C_A1952.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：248,064 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：248,064 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：411 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：253,774 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：253,774 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：563 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，361 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch248_cqjtu_admission`：1 个测试通过。
- batch248 curated：1,813 条，缺少人员姓名 0，缺少准考证号 0，缺少学院 0，缺少录取专业 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限` 残留 0。
- 工作簿已重建：Overview 15 行、Source_Summary 564 行（含表头）、Coverage 431 行（含表头）、Public_Records 253,775 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch249-batch253：暨南大学、山东农业大学、西安外国语大学、皖南医学院

本轮继续从剩余缺口中筛选可自动抓取的官网人员级来源，并严格跳过验证码、HTTP 412、JS challenge 和已移除附件。

入库来源包括：暨南大学 2026 年第二批拟录取博士研究生 Excel、山东农业大学 2025 年硕士研究生全校拟录取 PDF、西安外国语大学 2026 年硕士研究生调剂拟录取官网表格、皖南医学院 2025 年硕士研究生拟录取 PDF。通用解析中，暨南大学 Excel 可抽取人员行但丢失院系名称和成绩字段；山东农业大学 PDF 未被通用解析识别；西安外国语大学 HTML 表格丢失准考证号并误抓联系方式；皖南医学院 PDF 被通用解析误作 802 条且元数据需纠正。上述 4 个来源均按 TDD 新增专项清洗脚本和测试，最终入库 3,420 条，需复核 0 条。

同期复核并跳过的来源：大连外国语大学、桂林医科大学和太原科技大学附件均进入验证码下载桥；浙江中医药大学 Excel 普通浏览可见但爬虫请求返回 HTTP 412；中国海洋大学官网公示页附件已移除且直链 404；华侨大学旧附件跳转 404；云南中医药大学搜索直链返回 404。上述来源均不绕过限制、不入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch249_jnu_doctor_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch250_sdau_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch251_xisu_adjustment_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch252_zcmu_recommendation.csv`（HTTP 412，未入库）
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch253_wnmc_recommendation.csv`

抓取/清洗产物：
- `scripts/curate_batch249_jnu_doctor_admission.py`
- `scripts/curate_batch250_sdau_admission.py`
- `scripts/curate_batch251_xisu_adjustment_admission.py`
- `scripts/curate_batch253_wnmc_admission.py`
- `tests/test_curate_batch249_jnu_doctor_admission.py`
- `tests/test_curate_batch250_sdau_admission.py`
- `tests/test_curate_batch251_xisu_adjustment_admission.py`
- `tests/test_curate_batch253_wnmc_admission.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 暨南大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 228 | 0 |
| 山东农业大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 2,266 | 0 |
| 西安外国语大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 158 | 0 |
| 皖南医学院 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 768 | 0 |

可追溯来源：
- 暨南大学 2026 年第二批次拟录取博士研究生名单 Excel：`https://yz.jnu.edu.cn/_upload/article/files/99/b1/1fb265f14ab3a02802f00c1b0d79/c7235e9d-63f1-4efc-8781-7d1090e91a28.xlsx`
- 山东农业大学 2025 年硕士研究生拟录取名单 PDF：`https://yjsc.sdau.edu.cn/cms/viewPdf/f7887010dce34b0a9fc8589e584200ed`
- 西安外国语大学 2026 年硕士研究生招生考试调剂考生拟录取名单公示：`https://yzw.xisu.edu.cn/info/1080/4622.htm`
- 皖南医学院 2025 年硕士研究生招生拟录取名单 PDF：`https://www.wnmc.edu.cn/__local/A/C6/DA/A19EA1BD793B172B18AD6C3E700_229104C8_44124.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：251,484 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：251,484 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：415 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：257,194 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：257,194 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：567 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，365 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch249_jnu_doctor_admission tests.test_curate_batch250_sdau_admission tests.test_curate_batch251_xisu_adjustment_admission tests.test_curate_batch253_wnmc_admission`：4 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：96 个测试通过。
- 本轮 4 个 curated 文件合计：3,420 条，缺少人员姓名 0，缺少考生编号 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限` 残留 0。
- 工作簿已重建：Overview 15 行、Source_Summary 568 行（含表头）、Coverage 431 行（含表头）、Public_Records 257,195 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch254：齐齐哈尔大学硕士拟录取 PDF

本轮继续从剩余缺口中筛选 B 类官网可直接抓取来源。齐齐哈尔大学研究生部 2025 年硕士研究生拟录取考生名单公示页可访问，正文下的官方 PDF 附件直连返回 `200 application/pdf`，且 PDF 带可抽取文本层。通用爬虫可抓取 PDF，但默认解析把名单尾部 2 条“放弃一志愿录取资格”也纳入候选，共得到 1,192 条；按 TDD 新增专项清洗脚本后，只保留 PDF 正文说明中的 1,190 条拟录取记录，并剔除排名 1191、1192 两条放弃资格记录。

同期复核并跳过的来源：天津财经大学旧公示 URL 返回 404；重庆邮电大学返回 HTTP 412 / JS challenge；南京财经大学附件进入验证码下载桥；中国药科大学搜索命中页返回无效文章参数；沈阳航空航天大学返回 403；沈阳体育学院旧页返回 404；内蒙古民族大学及其附属医院旧官网线索返回 404。上述来源均不绕过验证码、挑战页或失效链接，不入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch254_qqhru_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch254_qqhru_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch254_qqhru_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch254_qqhru_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch254_qqhru_admission.py`
- `tests/test_curate_batch254_qqhru_admission.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 齐齐哈尔大学 | 2025 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,190 | 0 |

可追溯来源：
- 齐齐哈尔大学 2025 年硕士研究生拟录取考生名单公示页：`https://yjs.qqhru.edu.cn/info/1065/1813.htm`
- 齐齐哈尔大学 2025 年硕士研究生拟录取考生名单 PDF：`https://yjs.qqhru.edu.cn/__local/8/F5/EE/02D0C56D2494576D6694F9C54A6_C1B2A0DC_FAA2C.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,674 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,674 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：416 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,384 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,384 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：568 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，366 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch254_qqhru_admission`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：97 个测试通过。
- batch254 curated：1,190 条，缺少人员姓名 0，缺少考生编号 0，缺少学院 0，缺少专业 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格` 残留 0，排名 1191/1192 残留 0。
- 工作簿已重建：Overview 15 行、Source_Summary 569 行（含表头）、Coverage 431 行（含表头）、Public_Records 258,385 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch255：喀什大学推免拟录取图片型 PDF

本轮继续从剩余缺口中筛选可入库官网源。喀什大学研究生处 2026 年拟接收优秀应届本科毕业生免试攻读全日制硕士研究生名单公示页可直接访问，正文通过 `showVsbpdfIframe` 嵌入官方 PDF 附件。通用爬虫可抓取页面和 PDF，但 PDF 为图片型，`pdftotext` 无文本层，通用解析得到 0 条记录。新增 `scripts/curate_batch255_ksu_recommendation.py` 和 `tests/test_curate_batch255_ksu_recommendation.py`，按 300dpi 渲染图片、Windows OCR 词块坐标分栏，并对 OCR 明确漏读的姓名做限定修正，最终入库 60 条。

同期复核并跳过的来源：西北师范大学官网详情页返回 JS challenge，搜索命中的 `_upload` PDF 直链实时返回 404；陕西科技大学官网页面返回 403；中国医科大学恢复出的官网路径返回 404；东北电力大学搜索命中旧页返回 404；江汉大学搜索命中页实时返回“无效的文章参数”；喀什大学正文摘要本身不含人员级明细，但嵌入 PDF 可抓取，因此只入库 PDF OCR 结果。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch255_ksu_recommendation.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch255_ksu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch255_ksu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch255_ksu_recommendation_curated/records_clean_curated.csv`
- `scripts/curate_batch255_ksu_recommendation.py`
- `tests/test_curate_batch255_ksu_recommendation.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 喀什大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 60 | 0 |

可追溯来源：
- 喀什大学 2026 年拟接收优秀应届本科毕业生免试攻读全日制硕士研究生名单公示页：`https://yjsc.ksu.edu.cn/info/1034/2832.htm`
- 喀什大学名单嵌入 PDF：`https://yjsc.ksu.edu.cn/virtual_attach_file.vsb?afc=tU8nj2UlLDnRU8nwzf7ozl4Uz94LR9XZMRf2MRNZnzCDMRL0gihFp2hmCIa0LYyaLYh7MkhVMNM7MzQVLN7bnRfVUlMkM87snRr2U4-4UzQFMNnRMl-iUzVFM7LZLNlJv2nto4OeosT/vDL0qIbtpYyPLRL8g4-ZL4-Jqd/nx&oid=1120997853&tid=1034&nid=2832&e=.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,734 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,734 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：417 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,444 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,444 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：569 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，367 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch255_ksu_recommendation`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：98 个测试通过。
- batch255 curated：60 条，缺少人员姓名 0，缺少证件号 0，缺少学院 0，缺少专业 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格` 残留 0。
- 工作簿已重建：Overview 15 行、Source_Summary 570 行（含表头）、Coverage 431 行（含表头）、Public_Records 258,445 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch256：河南医药大学推免拟录取 HTML 表格

本轮继续从剩余缺口中筛选可直接抓取的官网人员级来源。覆盖底表中的“河南医药大学”对应官网为 `xxmu.edu.cn`，其研究生处官网发布了 2026 年推荐免试攻读硕士研究生拟录取名单公示，正文为 HTML 表格，包含院系所代码、院系所名称、姓名、证件号码、专业代码、专业名称和学位类型。通用爬虫可抽到 4 条人员记录，但漏掉证件号码和院系字段；按 TDD 新增专项清洗脚本，完整保留表格字段，最终入库 4 条。

同期复核并跳过的来源：西湖大学 2026 推免直博生公示页实时返回 500；华侨大学校级公示页跳转 404，搜索命中的 `virtual_attach_file.vsb` 附件直链同样跳转 404；上述来源本轮仅留证不入库。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch256_hnmu_recommendation.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch256_hnmu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch256_hnmu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch256_hnmu_recommendation_curated/records_clean_curated.csv`
- `scripts/curate_batch256_hnmu_recommendation.py`
- `tests/test_curate_batch256_hnmu_recommendation.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河南医药大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 4 | 0 |

可追溯来源：
- 河南医药大学 2026 年推荐免试攻读硕士研究生拟录取名单公示：`https://www.xxmu.edu.cn/yjsc/info/1013/4466.htm`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,738 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,738 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：418 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,448 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,448 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：570 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，368 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch256_hnmu_recommendation`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：99 个测试通过。
- batch256 curated：4 条，缺少人员姓名 0，缺少证件号 0，缺少学院 0，缺少专业 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格` 残留 0。
- 工作簿已重建：Overview 15 行、Source_Summary 571 行（含表头）、Coverage 431 行（含表头）、Public_Records 258,449 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch257：河北农业大学硕博连读拟录取 PDF

本轮继续从剩余缺口中筛选可直接抓取的官网人员级来源。河北农业大学研究生学院招生信息栏目可访问，2026 年接收推免相关页面仅为工作办法和复试时间说明，未公开人员级名单；同栏目发布的“河北农业大学2026级硕博连读研究生拟录取名单公示”正文通过 `showVsbpdfIframe` 嵌入校内 `__local` PDF，可直接下载。通用爬虫可抓取页面和 PDF，但表格行被错抽为 1 条无效记录；按 TDD 新增专项清洗脚本，基于 PDF 文本层解析序号、学号、姓名、拟录取学院、拟录取专业、导师、考核成绩和拟录取类别，最终入库 42 条。

同期复核并跳过的来源：中国药科大学搜索命中的 2026 推免拟录取名单页实时返回“无效的文章参数”，公开公示列表仅能访问推免工作办法和非人员级专业目录；中国海洋大学 2026 推免拟录取公示页可访问，但公示结束后附件链接已从正文移除，搜索索引暴露的同站 `_upload` PDF 直链实时返回 404。本轮均只留检索证据，不绕过失效/隐藏附件。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch257_hebau_doctor_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch257_hebau_doctor_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch257_hebau_doctor_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch257_hebau_doctor_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch257_hebau_doctor_admission.py`
- `tests/test_curate_batch257_hebau_doctor_admission.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河北农业大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 42 | 0 |

可追溯来源：
- 河北农业大学 2026 级硕博连读研究生拟录取名单公示：`https://yanjiusheng.hebau.edu.cn/info/1109/4694.htm`
- 河北农业大学名单嵌入 PDF：`https://yanjiusheng.hebau.edu.cn/__local/B/8A/32/0EF1F4B72A57F5B93FA41D72EF8_926A5724_1C059.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,780 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,780 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：419 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,490 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,490 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：571 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，369 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch257_hebau_doctor_admission`：1 个测试通过。
- batch257 curated：42 条，缺少人员姓名 0，缺少学号 0，缺少学院 0，缺少专业 0，需人工复核 0，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格` 残留 0。
- 工作簿已重建：Overview 15 行、Source_Summary 572 行（含表头）、Coverage 431 行（含表头）、Public_Records 258,491 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch258：陆军军医大学推免拟录取 PDF

本轮继续从剩余缺口中筛选可直接抓取的官网人员级来源。陆军军医大学招生就业网发布“公示2026年接收推荐免试硕士研究生拟录取名单”，页面公网可访问，正文包含两个同站 PDF 附件：地方计划推荐免试硕士研究生拟录取名单、入伍计划推荐免试硕士研究生拟录取名单。公告中的“应届军人本科毕业生”名单只说明“详见强军网”，未提供公网附件，本轮不纳入。

通用爬虫可抓取公告页和两个 PDF，但默认 PDF 表格解析未形成记录。按 TDD 新增 `scripts/curate_batch258_tmmu_recommendation.py` 和 `tests/test_curate_batch258_tmmu_recommendation.py`，基于 PDF 文本层解析姓名、性别和名单计划类型，最终入库 38 条。源 PDF 不含学号、学院或专业字段，因此 38 条均保留 `needs_review=true` 及缺失字段质量标记。

同期复核并跳过的来源：华东师范大学 2026 推免拟录取公示页可访问但附件已随“公示已结束”从 HTML 移除；北京第二外国语学院搜索命中的旧详情页实时 404；重庆邮电大学与佛山大学页面返回 JS challenge；中国政法大学返回“访问被限制”；北京协和医学院公开结果页当前切到 2027 空表。上述来源均不绕过访问限制、挑战页、失效附件或动态空表。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch258_tmmu_recommendation.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch258_tmmu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch258_tmmu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch258_tmmu_recommendation_curated/records_clean_curated.csv`
- `scripts/curate_batch258_tmmu_recommendation.py`
- `tests/test_curate_batch258_tmmu_recommendation.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 陆军军医大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 38 | 38 |

可追溯来源：
- 陆军军医大学 2026 年接收推荐免试硕士研究生拟录取名单公示：`https://zs.tmmu.edu.cn/zsjy/news_show.aspx?master=y&newsid=3238`
- 地方计划 PDF：`https://zs.tmmu.edu.cn/zsjy/houtai/eWebEditorV12/uploads/20251120/20251120181938689.pdf`
- 入伍计划 PDF：`https://zs.tmmu.edu.cn/zsjy/houtai/eWebEditorV12/uploads/20251120/20251120181948390.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,818 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,818 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：420 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,528 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,528 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：572 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，370 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch258_tmmu_recommendation`：1 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：101 个测试通过。
- batch258 curated：38 条，缺少人员姓名 0，缺少学号 38，缺少学院 38，缺少专业 38，需人工复核 38，`进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格` 残留 0。
- B 类 master / public 与 A+B clean / public 四份 CSV 的硬排除词扫描均无命中。
- 工作簿已重建：Overview 15 行、Source_Summary 573 行（含表头）、Coverage 431 行（含表头）、Public_Records 258,529 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-01 batch259 留证：太原科技大学附件验证码

batch259 继续复核剩余缺口中的太原科技大学。研究生学院硕士招生列表可访问，并定位到两个 2026 年拟录取公示页：一志愿考生拟录取结果公示、拟录取名单公示（二）。两页 HTML 均公开说明“名单见附件”，但附件链接进入学校 VSB `download.jsp` 验证码下载页，自动化请求只能取得“请输入验证码下载附件”的 HTML，不取得真实 PDF。本轮不绕过验证码、不入库，仅保留种子、原始页面和下载桥证据。

留证产物：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch259_tyust_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch259_tyust_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch259_tyust_admission/`

留证来源：
- 太原科技大学 2026 年硕士研究生招生一志愿考生拟录取结果公示：`https://yjsxy.tyust.edu.cn/info/1203/3652.htm`
- 太原科技大学 2026 年硕士研究生招生考试拟录取名单公示（二）：`https://yjsxy.tyust.edu.cn/info/1203/3665.htm`

## 2026-06-01 batch260-batch262：辽宁石油化工大学、辽宁科技大学、华北理工大学

本轮继续从剩余缺口中筛选可直接抓取的官网人员级来源。辽宁石油化工大学研究生院“2026年接收推免待录取考生情况公示”页面通过 `showVsbpdfIframe` 嵌入同站 PDF，通用爬虫自动抓取并解析 7 条推免待录取记录。辽宁科技大学 2026 年博士研究生拟录取名单官网公告页已失效，但同站 `__local` 官方 PDF 直链仍可直接下载；通用解析初次混入重复表头并错位部分记录，按 TDD 新增 `scripts/curate_batch261_ustl_doctor_admission.py` 和 `tests/test_curate_batch261_ustl_doctor_admission.py`，基于 PDF 文本层重建 69 条真实考生记录。华北理工大学 2026 年接收推免研究生复试及拟录取名单公示页可访问，PDF 藏在在线预览器参数中；通用解析抓到 31 条但混入缺考、拒绝待录取和差额未录取并发生字段错位，按 TDD 新增 `scripts/curate_batch262_ncst_recommendation.py` 和 `tests/test_curate_batch262_ncst_recommendation.py`，仅保留状态为“拟录取”的 16 条。

同期复核并跳过的来源：沈阳师范大学 2026 年拟录取公示页只保留附件标题和“公示期已结束”，HTML 中无真实附件 URL；南京财经大学附件下载进入验证码页；浙江中医药大学页面返回人机验证；中国药科大学搜索命中的旧公示页返回“无效的文章参数”；广东药科大学搜索命中的旧页实时 404。本轮均不绕过验证码、人机验证、失效页面或已移除附件。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch260_lnpu_recommendation.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch261_ustl_doctor_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260601_batch262_ncst_recommendation.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch260_lnpu_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch260_lnpu_recommendation/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch261_ustl_doctor_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch261_ustl_doctor_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch261_ustl_doctor_admission_curated/records_clean_curated.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch262_ncst_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch262_ncst_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch262_ncst_recommendation_curated/records_clean_curated.csv`
- `scripts/curate_batch261_ustl_doctor_admission.py`
- `tests/test_curate_batch261_ustl_doctor_admission.py`
- `scripts/curate_batch262_ncst_recommendation.py`
- `tests/test_curate_batch262_ncst_recommendation.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 辽宁石油化工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 7 | 0 |
| 辽宁科技大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 69 | 0 |
| 华北理工大学 | 2026 | incoming_recommendation_admission_list | recommendation_exemption | 16 | 0 |

可追溯来源：
- 辽宁石油化工大学 2026 年接收推免待录取考生情况公示：`https://ges.lnpu.edu.cn/info/1063/7032.htm`
- 辽宁石油化工大学嵌入 PDF：`https://ges.lnpu.edu.cn/__local/8/2C/96/1FC08EB35AF4EB3B9663D588788_C45516F8_A6A6.pdf`
- 辽宁科技大学 2026 年博士研究生拟录取名单 PDF：`https://www.ustl.edu.cn/__local/B/40/97/A3412639680E6B74A5353D9A038_100A03EA_2749A.pdf`
- 华北理工大学 2026 年接收推免研究生复试及拟录取名单公示（第一批次）：`https://yjsxy.ncst.edu.cn/col/1695864352045/2025/09/26/1758869299867.html`
- 华北理工大学名单 PDF：`https://yjsxy.ncst.edu.cn/atm/7/20250926144423420.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：252,618 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：252,618 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：423 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：258,323 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：258,323 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：575 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，373 所已精确匹配官网记录

本轮合并后做了一次跨批次状态字段清理：从 B 类历史主表中移除 292 条带有明确非录取状态的记录，其中缺考 186 条、候补 70 条、不合格 36 条；同时从 CHSI 清洗源中移除 5 条缺考/不合格记录。清理只依据记录字段（姓名、学号、本科信息、学院、专业、序号、备注等）中的状态词；来源标题中出现“拟录取及候补资格名单”但记录字段本身未标记候补的行不按此规则删除。

验证：
- `python -m unittest tests.test_curate_batch261_ustl_doctor_admission tests.test_curate_batch262_ncst_recommendation`：2 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：103 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- CHSI clean、B 类 master/public 与 A+B clean/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 576 行（含表头）、Coverage 431 行（含表头）、Public_Records 258,324 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch263：江汉大学硕士/博士拟录取名单

本轮继续从剩余覆盖缺口中筛选可直接抓取的官网人员级来源。江汉大学研究生院 2026 年硕士研究生招生拟录取名单公示页、2026 年博士研究生招生拟录取名单公示页均可访问，页面通过 PDF 预览参数暴露同站 `_upload` PDF 直链。通用爬虫可抓取页面和附件，但硕士 PDF 的跨行学院字段、末行退役军人备注等版式未被通用规则完整识别；按 TDD 新增 `scripts/curate_batch263_jhun_admission.py` 和 `tests/test_curate_batch263_jhun_admission.py`，基于 PDF 文本层重建硕士 1,050 条、博士 38 条人员级记录。

同期复核并跳过的来源：搜索命中的江汉大学推免相关页面 `https://gs.jhun.edu.cn/59/e4/c1956a219620/page.htm` 及移动端变体实时返回“无效的文章参数！(02)”，不入库、不使用缓存页面。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch263_jhun_admission.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch263_jhun_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch263_jhun_admission/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch263_jhun_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch263_jhun_admission.py`
- `tests/test_curate_batch263_jhun_admission.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 江汉大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 1,050 | 2 |
| 江汉大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 38 | 0 |

可追溯来源：
- 江汉大学 2026 年硕士研究生招生拟录取名单公示页：`https://gs.jhun.edu.cn/7b/98/c1956a228248/page.htm`
- 江汉大学 2026 年硕士研究生招生拟录取名单 PDF：`https://gs.jhun.edu.cn/_upload/article/files/03/70/0ba7d8654dd49cc10a4b83d080c5/0e8e8a8e-f708-4002-89fa-4d7bc5276fce.pdf`
- 江汉大学 2026 年博士研究生招生拟录取名单公示页：`https://gs.jhun.edu.cn/7e/e6/c1956a229094/page.htm`
- 江汉大学 2026 年博士研究生招生拟录取名单 PDF：`https://gs.jhun.edu.cn/_upload/article/files/bb/53/6cf23a744e65af0a031032a991c3/4deb0b5b-02d6-430b-a15e-7c0e2e8dc55e.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：253,706 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：253,706 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：424 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：259,411 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：259,411 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：576 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，374 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch263_jhun_admission`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：104 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- CHSI clean、B 类 master/public 与 A+B clean/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 577 行（含表头）、Coverage 431 行（含表头）、Public_Records 259,412 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch264-batch268c：吉首大学博士拟录取 PNG 入库与缺口留证

本轮继续从 batch263 后剩余缺口中筛选官网来源。中国海洋大学研究生招生信息网推荐免试名单页面可访问，但正文只保留“见附件”文字，未暴露真实附件 href；搜索恢复的 `_upload` PDF 直链实时返回 404，未入库。中国政法大学研究生院两条推免/直博入口返回浏览器 JS challenge；中国药科大学研招网推免公示页实时返回 410；重庆邮电大学研究生院首页可见两个 2026 年博士拟录取公示标题，但详情页均返回 412。上述来源均留证不绕过、不入库。

可入库来源为吉首大学研究生院“2026 年拟录取博士研究生情况公示”。正文公开 3 个 PNG 附件，分别为人文学院、体育科学学院、生命科学学院博士拟录取公示。通用爬虫已保存官方原图，但图片附件不走通用文本解析；按 TDD 新增 `scripts/curate_batch268c_jsu_doctor_pngs.py` 和 `tests/test_curate_batch268c_jsu_doctor_pngs.py`，逐行转写公开图片表格，仅保留“是否拟录取”为拟录取的人员，剔除放弃复试、未参加面试和自愿放弃拟录取行。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch264_ouc_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch265_cupl_recommendation.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch266_cpu_recommendation.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch267_cqupt_probe.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch268_jsu_recommendation.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch268b_jsu_doctor_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch268c_jsu_doctor_pngs.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch264_ouc_admission/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch265_cupl_recommendation/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch267_cqupt_probe/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch268b_jsu_doctor_admission/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch268c_jsu_doctor_pngs/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch268c_jsu_doctor_pngs_curated/records_clean_curated.csv`
- `scripts/curate_batch268c_jsu_doctor_pngs.py`
- `tests/test_curate_batch268c_jsu_doctor_pngs.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 吉首大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 37 | 0 |

可追溯来源：
- 吉首大学 2026 年拟录取博士研究生情况公示：`https://yjsc.jsu.edu.cn/zsgz/bszs/ddb92781965243fa91dbebdd2af3babc.htm`
- 人文学院 PNG：`https://yjsc.jsu.edu.cn/docs/2026-06/d913622cbe834762b72c402287fb35dd.png`
- 体育科学学院 PNG：`https://yjsc.jsu.edu.cn/docs/2026-06/fe46a846c5d24df2885ca40caed4ebf3.png`
- 生命科学学院 PNG：`https://yjsc.jsu.edu.cn/docs/2026-04/c133ae78e2324b2a9329e07ff96fc82e.png`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：253,743 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：253,743 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：425 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：259,448 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：259,448 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：577 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，375 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch263_jhun_admission tests.test_curate_batch268c_jsu_doctor_pngs`：2 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：105 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- CHSI clean、B 类 master/public 与 A+B clean/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 578 行（含表头）、Coverage 431 行（含表头）、Public_Records 259,449 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch269-batch271：西湖大学博士拟录取 PDF 入库与缺口留证

本轮继续从剩余覆盖缺口中筛选可访问官网源。福建师范大学马克思主义学院搜索命中的复试结果 PDF 直链实时返回空内容，未形成可用名单；北京协和医学院推免预报名系统结果页可访问，但当前实时页面已切换为 2027 年标题且表格为空，未使用搜索缓存入库。

可入库来源为西湖大学研究生招生通知公告页“2026级博士研究生拟录取名单公示（4月批次）”。页面正文说明名单见附件，并在页面脚本中公开 PDF 下载地址；通用爬虫可直接抓取 PDF 并抽出 168 条记录。因通用解析把“姓名+证件号码”合并进姓名字段，本批按 TDD 新增 `scripts/curate_batch270b_westlake_admission_pdf.py` 和 `tests/test_curate_batch270b_westlake_admission_pdf.py`，将申请号、姓名、脱敏证件号、拟录取学院、拟录取专业、面试成绩、学制和备注拆分为可用字段。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch269_fjnu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch270_westlake_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch270b_westlake_admission_pdf.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch271_pumc_recommendation.csv`

抓取/清洗产物：
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch269_fjnu_admission/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch270_westlake_admission/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch270b_westlake_admission_pdf/`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch271_pumc_recommendation/`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch270b_westlake_admission_pdf_curated/records_clean_curated.csv`
- `scripts/curate_batch270b_westlake_admission_pdf.py`
- `tests/test_curate_batch270b_westlake_admission_pdf.py`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 西湖大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 168 | 0 |

可追溯来源：
- 西湖大学 2026 级博士研究生拟录取名单公示（4月批次）：`https://www.westlake.edu.cn/admissions/graduate/information/announcements/202605/t20260507_66370.html`
- 西湖大学 2026 级博士生拟录取名单公示 PDF：`https://www.westlake.edu.cn/admissions/graduate/information/announcements/202605/P020260507325813095887.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：253,911 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：253,911 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：426 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：259,616 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：259,616 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：578 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，376 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch270b_westlake_admission_pdf`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：106 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- CHSI clean、B 类 master/public 与 A+B clean/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 579 行（含表头）、Coverage 431 行（含表头）、Public_Records 259,617 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch304-batch310：剩余缺口复核与不可入库源留证

本轮继续从剩余 51 所覆盖缺口中复核官网来源，重点尝试广东药科大学、重庆邮电大学、太原科技大学、北京电影学院、首都师范大学、沈阳化工大学、东北电力大学等。所有命中均按“官网实时可复现、不得绕过验证码/人机验证/HTTP 412/404/502”的规则处理；本轮未形成可入库人员行，B 类主表规模保持 batch303 后的 254,072 条。

种子与日志：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch304_gdpu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch305_cqupt_doctoral_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch306_tyust_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch307_bfa_recommendation.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch308_cnu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch309_syuct_recommendation.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch310_neepu_recommendation.csv`
- 对应失败日志位于 `logs/graduate_outcomes_official_site_websearch_web_20260602_batch304_gdpu_admission/` 至 `logs/graduate_outcomes_official_site_websearch_web_20260602_batch310_neepu_recommendation/`

主要留证结果：
- 广东药科大学：`https://yjsxy.gdpu.edu.cn/info/1012/2555.htm`、`https://yjsxy.gdpu.edu.cn/info/1012/2495.htm` 实时均为 HTTP 404。
- 中国医科大学：第三方仅用于恢复官方附件直链，`https://www.cmu.edu.cn/system/_content/download.jsp?...wbfileid=13255969` 实时返回“请输入验证码下载附件”页面，未绕过。
- 南京财经大学：推免 PDF 附件 `https://yjsc.nufe.edu.cn/system/_content/download.jsp?...wbfileid=15731866` 实时返回验证码下载桥；硕士一志愿公示页仅保留正文无人员名单。
- 西北师范大学：官网公示页实时返回 JS challenge/人机识别脚本，无可解析正文或附件，未绕过。
- 重庆邮电大学：`https://yjs.cqupt.edu.cn/info/1179/14574.htm` 与 `https://yjs.cqupt.edu.cn/info/1179/14564.htm` 实时 HTTP 412。
- 成都体育学院：2026 推免页面为 WAF 人机识别；2025 两个官方 PDF 直链实时也返回 WAF challenge HTML，未入库。
- 太原科技大学：`https://yjsxy.tyust.edu.cn/info/1203/3665.htm` 实时 HTTP 502。
- 北京电影学院：`https://www.bfa.edu.cn/yanjiusheng/info/1031/4573.htm` 实时 HTTP 412。
- 首都师范大学：第三方恢复的 `https://grad.cnu.edu.cn/zs1/sszs/bc030d53d474459eaf64d310e15a412a.htm` 抓取后跳转到学校首页，无名单正文或附件。
- 沈阳化工大学：`https://waiyu.syuct.edu.cn/info/1049/1923.htm` 页面可抓，但人员名单在两个附件中，附件均返回“请输入验证码下载附件”，正文无人员表。
- 东北电力大学：`https://grad.neepu.edu.cn/info/1050/3430.htm` 与 `https://grad.neepu.edu.cn/info/1050/3500.htm` 实时 HTTP 404。

当前计数保持不变：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：254,072 条
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：259,777 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，379 所已精确匹配官网记录

## 2026-06-02 batch303：华侨大学博士拟录取名单入库

本轮继续从剩余覆盖缺口中筛选官网来源。华侨大学硕士统考拟录取公示搜索命中 `https://yjszs.hqu.edu.cn/info/1013/4709.htm`，但实时抓取返回校站 404；搜索索引中暴露的同域 `virtual_attach_file.vsb` 硕士附件直链实时也返回 404，因此不入库。华侨大学研究生院“2026 年第二批次硕博连读和申请审核制博士研究生拟录取名单公示”页面实时可访问，正文内嵌 VSB PDF iframe，4 个 JPEG 预览页和 1 个 PDF 主文件均可下载；PDF 文本层可复现抽取。

按 TDD 新增 `scripts/curate_batch303_hqu_doctoral_admission.py` 与 `tests/test_curate_batch303_hqu_doctoral_admission.py`，只保留带 10 位考生报名号的完整拟录取记录；跨行专业名“华侨华人与区域/国别研究”和跨行备注“国际产学研用联/培博士计划”均合并到单条记录字段。最终入库 146 条博士拟录取记录，需复核 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch303_hqu_admission.csv`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch303_hqu_admission/grs.hqu.edu.cn/2bb7ab1362e6ed7c.htm`
- `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch303_hqu_admission/grs.hqu.edu.cn/hqu_2026_doctoral_admission_second_batch.pdf`
- `scripts/curate_batch303_hqu_doctoral_admission.py`
- `tests/test_curate_batch303_hqu_doctoral_admission.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch303_hqu_admission_curated/records_clean_curated.csv`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 华侨大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 146 | 0 |

可追溯来源：
- 华侨大学 2026 年第二批次硕博连读和申请审核制博士研究生拟录取名单公示：`https://grs.hqu.edu.cn/info/1176/18010.htm`
- 官方 VSB PDF 附件：`https://grs.hqu.edu.cn/virtual_attach_file.vsb?afc=wMmAXVM8CDMm6kU/NlDLRnVMlCiL8CKiLmLPLRlaUlU4Lz90gihFp2hmCIa0USh7MYh2L1hVLR6koRNanllDM8CYL8l4UlUiMm-PLzf7M7MFM7L4nlQVUlnFLmU8M87Jv2nto4OeosT/vsTFptrsgDTJQty0Lz7sM1yPoRGPLkbw62O8c`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：254,072 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：254,072 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：429 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：259,777 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：259,777 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：581 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，379 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch303_hqu_doctoral_admission`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：108 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- CHSI clean、B 类 master/public 与 A+B clean/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 582 行（含表头）、Coverage 431 行（含表头）、Public_Records 259,778 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch300-batch302：河北中医药大学推免拟录取 Excel 入库与失效源留证

本轮继续从剩余 B 类覆盖缺口中筛选官网来源。大连海洋大学 2025/2026 搜索命中的官方 PDF 线索实时 404 或连接失败；沈阳航空航天大学 2026 年推免拟录取官网页可定位，但自动化请求失败且 `curl` 返回学校 WAF 403 `Access Forbidden by SAU`，未绕过；沈阳师范大学、中国海洋大学、北京第二外国语学院、齐鲁工业大学、华东师范大学等页面可访问但附件已随公示期结束移除或不暴露真实 href；长春师范大学、沈阳体育学院站点连接超时；北京服装学院可访问页面为复试办法/公告索引，未取得最终名单；华中科技大学强基名单主体为 SWF 且下载返回 403。上述来源均留证不入库。

可入库来源为河北中医药大学研究生学院“2026 年拟录取推免生公示（第一批）”。官网页面公开同站 legacy `.xls` 附件，使用 `xlrd` 读取后只保留状态以“待录取”开头的人员行；`未参加复试/放弃待录取通知/拒绝待录取通知/拒绝复试通知/已被其他院校录取` 以及空状态行全部剔除。第二批页面未暴露附件或人员表，暂不入库。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch300_dlou_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch301_sau_recommendation.csv`
- `scripts/curate_batch302_hebcm_recommendation.py`
- `tests/test_curate_batch302_hebcm_recommendation.py`
- `data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch302_hebcm_recommendation_curated/records_clean_curated.csv`

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 河北中医药大学 | 2026 | recommendation_exemption_list | recommendation_exemption | 16 | 0 |

可追溯来源：
- 河北中医药大学 2026 年拟录取推免生公示（第一批）：`https://yjsxy.hebcm.edu.cn/col/1628824153772/2025/09/26/1758884165127.html`
- 官方 Excel 附件：`https://yjsxy.hebcm.edu.cn/download.jsp?pathfile=/atm/7/20250926184432892.xls`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：253,926 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：253,926 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：428 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：259,631 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：259,631 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：580 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，378 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch302_hebcm_recommendation`：1 个测试通过。
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：107 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- CHSI clean、B 类 master/public 与 A+B clean/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 581 行（含表头）、Coverage 431 行（含表头）、Public_Records 259,632 行（含表头）；公式单元格 0，公式错误 0。

## 2026-06-02 batch272-batch299：云南中医药大学硕博连读名单入库与剩余缺口留证

本轮继续从剩余覆盖缺口中筛选官网来源。多数命中属于“公示已结束后附件不再暴露”、验证码下载桥、HTTP 410/412/404、JS challenge 或 WAF 页面，均按规则留证不绕过、不入库。特别注意：天津职业技术师范大学 `https://yzb.tute.edu.cn/info/1551/8182.htm` 及其 PDF 虽可抓取并被通用解析出 87 条候选，但页面标题和 PDF 原文均为“2026 年硕士研究生招生考试一志愿复试名单”，不是拟录取名单，已排除不合并。

可入库来源为云南中医药大学“2026 年硕博连读研究生选拔拟录取名单公示”。官网正文直接公开 6 条人员表格，通用爬虫可结构化抽取，字段包含姓名、学号、学院和拟录取专业。

种子文件：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch272_gsau_recommendation.csv` 至 `data/seeds/official_site_recommendation_websearch_web_20260602_batch299_fosu_admission.csv`
- 本批成功入库种子：`data/seeds/official_site_recommendation_websearch_web_20260602_batch297_ynucm_glmc.csv`

主要留证结果：
- 甘肃农业大学、天津财经大学、北京服装学院、山东理工大学、广东药科大学、佛山大学等：官方搜索命中 URL 实时 404/412 或页面不再可访问。
- 华东师范大学、中国海洋大学、齐鲁工业大学、南京财经大学、山东理工大学、大连外国语大学、北京协和医学院等：公示页可访问但名单附件不暴露、进入验证码下载桥，或只保留“公示已结束/见附件”正文。
- 上海体育大学、中国政法大学、首都师范大学、重庆邮电大学、北京电影学院、西北师范大学等：JS challenge/WAF/HTTP 412，未绕过。
- 山西中医药大学、南京财经大学、大连外国语大学、北京协和医学院等 VSB 附件下载页返回“请输入验证码下载附件”，未绕过。
- 天津职业技术师范大学：可下载 PDF 为复试名单，不属于拟录取/推免拟录取数据，未入库。

本轮入库清洗结果：

| 学校 | 年份 | 类型 | 路径 | 新增记录数 | 需复核 |
| --- | --- | --- | --- | ---: | ---: |
| 云南中医药大学 | 2026 | postgraduate_admission_list | postgraduate_exam_or_admission | 6 | 0 |

同时清理历史遗留非录取状态：
- 从 B 类官网主表删除江西中医药大学 7 条备注含“未参加面试”的历史记录。

可追溯来源：
- 云南中医药大学 2026 年硕博连读研究生选拔拟录取名单公示：`https://yjs.ynucm.edu.cn/info/1023/1163.htm`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：253,910 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：253,910 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：427 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：259,615 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：259,615 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：579 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，377 所已精确匹配官网记录

验证：
- `python -m unittest discover -s tests -p "test_curate_batch*.py"`：106 个测试通过。
- `python -m unittest tests.test_graduate_outcome_crawler`：239 个测试通过（仅保留既有 ResourceWarning）。
- CHSI clean、B 类 master/public 与 A+B clean/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取` 残留。
- 工作簿已重建：Overview 15 行、Source_Summary 580 行（含表头）、Coverage 431 行（含表头）、Public_Records 259,616 行（含表头）；公式单元格 0，公式错误 0。
### 2026-06-02 batch355-batch371：B 类剩余院校官网可抓性筛查

本轮在 batch354 入库后，继续对 B 类剩余院校做官网入口与附件实时抓取筛查。以下源只作为证据留存，未并入主表：

- 山东理工大学：2026 一志愿/第二批次页面可抓，但名单附件仅剩无 href 的“附件1.pdf”文字，实际可下载附件为联系方式 PDF，未入库。
- 齐鲁工业大学：2026 一志愿/硕士拟录取公示页可抓，但公示结束后正文无名单附件链接，未入库。
- 大连外国语大学、南京财经大学：页面可抓，附件下载落到验证码页，未绕过验证码，未入库。
- 沈阳师范大学、华东师范大学：页面可抓，但名单附件仅剩文本名或图片占位，无真实 href，未入库。
- 沈阳航空航天大学、重庆邮电大学、西北师范大学、云南民族大学、中国海洋大学、中国药科大学、大连海洋大学、广东药科大学：官网入口或直链实时返回 404/412/521/错误页，未入库。
- 中国政法大学：返回动态 challenge 页面，未绕过；未入库。
- 中国人民公安大学：2026 推免只可下载统计表 PDF，非个人名单；2025 页面源码无名单附件链接，未入库。

这些失败批次的原始页面、下载页或失败日志已保存在对应的 `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch355_*` 至 `batch371_*` 和 `logs/graduate_outcomes_official_site_websearch_web_20260602_batch355_*` 至 `batch371_*` 目录中。

### 2026-06-02 batch372-batch385：B 类剩余院校二轮官网可抓性筛查

继续从覆盖缺口中复核 2026/2025 官网入口、推免结果系统和历史录取页。以下源均留证但未入库：

- 福建师范大学 2026 推免拟录取页：官网 URL 实时落到错误提示页，未取得名单正文。
- 佛山大学 2026 硕士拟录取页、重庆邮电大学 2025 硕士拟录取页、西北师范大学页面：实时返回 HTTP 412 或 404，未入库。
- 成都体育学院 2025 推免 PDF：官网静态 PDF URL 实时返回 Web 应用防火墙/人机识别页面，未入库。
- 首都师范大学 2026/2025 拟录取公告：`grad.cnu.edu.cn` 跳转至学校首页，未取得公告正文。
- 南京理工大学 2026 公告页/直链：公告页 HTTP 410，直链落到学校错误页，未入库。
- 桂林医科大学 2026 硕士拟录取页、沈阳体育学院 2025 硕士拟录取页、甘肃农业大学 2025 硕士拟录取页、东北电力大学 2026 推免/学院拟录取页：实时返回 HTTP 404，未入库。
- 山西中医药大学 2026 一志愿/调剂拟录取公告、北京协和医学院 2026 硕士/推免/博士及历史录取公告、南京财经大学 2026 调剂拟录取公告：公告正文可抓，但人员名单均在附件下载验证码桥，未绕过验证码，未入库。
- 北京协和医学院 `yzbtm.pumc.edu.cn/result/result/formalResult` 官方结果页可抓，但当前页面为 2027 推免空表；不使用搜索索引中的历史行数据。

对应证据目录为 `data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch372_*` 至 `batch385_*`，失败日志在 `logs/graduate_outcomes_official_site_websearch_web_20260602_batch372_*` 至 `batch385_*`。

### 2026-06-02 batch386-batch394：华中科技大学推免 PDF 入库与剩余缺口留证

本轮继续从剩余 B 类覆盖缺口中筛选可结构化官网来源。以下源只作为证据留存，未并入主表：

- 广东药科大学 2026/2025 新官网入口：`https://yjsxy.gdpu.edu.cn/info/1012/2555.htm`、`https://yjsxy.gdpu.edu.cn/info/1012/2495.htm`、`https://yjsxy.gdpu.edu.cn/info/1012/2306.htm` 实时均为 HTTP 404。
- 郑州轻工业大学 2024 年博士研究生拟录取名单公告页可抓取，但正文仅写“名单请见附件”，当前 HTML 中附件节点已不暴露，未入库。
- 北京林业大学 2025 年博士研究生拟录取公告页可抓取，但可下载附件为“政审表.pdf”模板，不是人员名单；2026 年博士公告指向结果查询系统，未入库。
- 东北师范大学 2026 年推免拟录取公告页可抓取，但正文仅保留公告事项、无人员表或附件；2025 年硕士 URL 实时 HTTP 404。
- 天津财经大学 2026 年硕博连读拟录取资格名单官方 URL 本地爬虫与 `curl.exe -L -I` 复核均为 HTTP 404；不使用搜索索引行数据。
- 中国药科大学 2025 年硕士 PDF 直链实时 HTTP 404，2026 年推免公示页实时 HTTP 410。
- 浙江中医药大学 2025 年硕士/博士拟录取页面实时 HTTP 412/405，未绕过。
- 华中科技大学 2025/2024 硕士拟录取官方 URL 实时 HTTP 404；2021 年硕士名单主体为 SWF，未作为可结构化数据入库。

可入库来源为华中科技大学研究生招生信息网“2024 年接收推荐免试攻读硕士学位和直接攻读博士学位研究生拟录取名单公示”。公告页正文公开嵌入同站 `__local` PDF：

- 公告页：`https://gszs.hust.edu.cn/info/1106/3712.htm`
- 官方 PDF：`https://gszs.hust.edu.cn/__local/D/9F/71/CE5F0511A0D45E40D020485F894_5E25830F_FCCF6.pdf`

通用爬虫对官方 PDF 抽取 4,033 条候选记录，清洗器保留 3,830 条；专项复核发现 PDF 页脚 `1/99` 至 `99/99` 被误作姓名保留。按 TDD 新增 `scripts/curate_batch394_hust_recommendation_pdf.py` 和 `tests/test_curate_batch394_hust_recommendation_pdf.py`，只过滤 `person_name` 满足 `N/N` 的页码伪记录，最终形成 3,731 条华中科技大学 2024 年推免拟录取记录，坏词命中 0、页码伪姓名命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch386_gdpu_2026_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch387_zzuli_doctor_2024.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch388_bjfu_doctor_2025.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch389_nenu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch390_tjufe_doctor_2026.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch391_cpu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch392_zcmu_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch393_hust_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch394_hust_recommendation_pdf.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch394_hust_recommendation_pdf_curated/records_clean_curated.csv`
- `scripts/curate_batch394_hust_recommendation_pdf.py`
- `tests/test_curate_batch394_hust_recommendation_pdf.py`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：267,544 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：267,544 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：443 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：273,249 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：273,249 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：595 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，391 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch394_hust_recommendation_pdf`：2 个测试通过。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 华中科技大学在覆盖表中匹配为 True，记录数 3,731；B 主表中 `person_name` 页码伪行命中 0。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 273,249 条、Source_Summary 595 条、Coverage 430 条。

### 2026-06-02 batch395-batch397：中国人民公安大学旧年度官方 PDF 入库

本轮继续从剩余覆盖缺口中筛选官网来源。以下源留证但未入库：

- 北京电影学院 2025 年硕士拟录取名单及体检通知（第一志愿考生）：`https://www.bfa.edu.cn/yanjiusheng/info/1031/4405.htm` 实时 HTTP 412，未绕过。
- 中国海洋大学 2026 年推荐免试攻读研究生（含直博生）拟录取名单官方 PDF 直链：`https://yz.ouc.edu.cn/_upload/article/files/8b/c8/9273a1a047369c7f2ddb3c59dc2e/85e3c515-1f4b-462e-8dd5-14b287ab30b5.pdf` 实时 HTTP 404，未入库。

可入库来源为中国人民公安大学研究生招生办公室官网 2014 年硕士研究生招生复试情况及拟录取名单 PDF。该来源虽然年份较早，但为官网直链，PDF 文本层可复现抽取，且原文含“是否拟录取”状态列。

- 官方 PDF：`https://yzb.ppsuc.edu.cn/__local/9/4F/D1/6028C1BCA976E6639F8E94AF1A4_4303F51F_97DED.pdf?e=.pdf`

通用爬虫可下载 PDF 但未抽出记录。按 TDD 新增 `scripts/curate_batch397_ppsuc_2014_admission.py` 和 `tests/test_curate_batch397_ppsuc_2014_admission.py`，按 15 位考生编号分段解析，只保留状态为 `是` 或 `调剂是` 的记录；73 条 `否` 状态记录全部排除，2 条 `调剂是` 记录保留并在备注中记录 `status_prefix: 调剂`。最终入库 406 条考生编号级拟录取记录。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch395_bfa_admission_2025.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch396_ouc_recommendation_2026.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch397_ppsuc_2014_admission_pdf.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch397_ppsuc_2014_admission_pdf_curated/records_clean_curated.csv`
- `scripts/curate_batch397_ppsuc_2014_admission.py`
- `tests/test_curate_batch397_ppsuc_2014_admission.py`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：267,950 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：267,950 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：444 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：273,655 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：273,655 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：596 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，392 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch397_ppsuc_2014_admission`：4 个测试通过。
- 本批 406 条均含 `official_admission_status: 是`，`official_admission_status: 否` 命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 273,655 条、Source_Summary 596 条、Coverage 430 条。

### 2026-06-02 batch398-batch401：甘肃农业大学生命科学技术学院一志愿拟录取 PDF 入库

本轮继续从剩余覆盖缺口中筛选官网来源。以下源留证但未入库：

- 南京理工大学 2026 年硕士研究生招生拟录取名单公示、2026 年推荐免试研究生拟录取名单公示，以及搜索恢复出的实际公告 URL，实时均为 HTTP 410。
- 华东师范大学 2026 年硕士研究生拟录取名单公示、2026 年招收优秀应届本科毕业生免试攻读研究生拟录取名单公示、2026 年面向港澳台地区招收研究生拟录取名单公示，公告页均可抓取，但公示结束后附件不暴露真实 href，仅保留附件标题或“公示已结束”文本。

可入库来源为甘肃农业大学生命科学技术学院官网“2024 年硕士研究生招生拟录取名单（一志愿）公示”。公告页公开同站 `download.jsp` PDF 附件，PDF 文本层可复现抽取。

- 公告页：`http://smkx.gsau.edu.cn/info/1003/7682.htm`
- 官方 PDF 附件：`http://smkx.gsau.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1058947186&wbfileid=C60A7EB8CE87B56AB2C64DD8D54FC201`

通用爬虫从 PDF 中抽出 20 条候选，但因表头跨页和列拥挤导致字段错列，通用清洗仅保留 1 条且该条为伪记录。按 TDD 新增 `scripts/curate_batch401_gsau_life_2024_admission.py` 和 `tests/test_curate_batch401_gsau_life_2024_admission.py`，基于“序号 + 姓名 + 15 位考生编号”切分记录，保留姓名、考生编号、第一志愿专业、拟录取专业、入学总成绩、笔试/面试/复试成绩、推免/调剂/同等学力标志、录取类别和学习方式。PDF 中三列 `否` 是推免/调剂/同等学力标志，不是拟录取否定状态；本批全部按标题中的拟录取名单入库，并在备注写入 `official_admission_status: 拟录取`。最终入库 41 条，需复核 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch398_njust_2026_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch399_njust_master_2026_actual.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch400_ecnu_2026_admission.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch401_gsau_life_2024_admission.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch401_gsau_life_2024_admission_curated/records_clean_curated.csv`
- `scripts/curate_batch401_gsau_life_2024_admission.py`
- `tests/test_curate_batch401_gsau_life_2024_admission.py`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：267,991 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：267,991 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`：445 个学校/年份/类型汇总组

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：273,696 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：273,696 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：597 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，393 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch401_gsau_life_2024_admission`：2 个测试通过。
- 本批 41 条均含 `official_admission_status: 拟录取`，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 273,696 条、Source_Summary 597 条、Coverage 430 条。

### 2026-06-02 batch402-batch408：东北师范大学学院官网 PDF 入库

本轮继续从剩余覆盖缺口中筛选官网来源。以下源留证但未入库：

- 北京服装学院 2026 年统考硕士研究生拟录取名单公示：`https://yjs.bift.edu.cn/zsgz/zsxx/0ede7f1a1a9f4061a3f5334ea483d24f.htm` 实时落到 `https://www.bift.edu.cn/apachehtml/custom404.html`，正文为“没有找到文件或目录”。
- 天津财经大学 2026 年硕士研究生招生复试调剂拟录取名单公示：`https://yjsy.tjufe.edu.cn/info/1082/3800.htm` 实时 HTTP 404；官方硕士生招生栏目可访问，但 4 页标题中未发现“拟录取/录取名单”候选入口。
- 中国药科大学 2025 年学术学位/专业学位硕士拟录取名单 PDF 直链实时 HTTP 404；2026 年硕士研究生拟录取名单调剂批次页面 `https://yjszs.cpu.edu.cn/98/c3/c10916a235715/page.htm` 实时 HTTP 410。
- 中国政法大学 2025 年统考硕士研究生拟录取名单公示页 `https://yjsy.cupl.edu.cn/info/1022/12344.htm` 返回 JavaScript 动态挑战页，未绕过。
- 东北师范大学研究生院主站 2025 年硕士研究生拟录取名单公示页 `https://yjsy.nenu.edu.cn/info/1216/6867.htm` 实时 HTTP 404。

可入库来源为东北师范大学二级学院官网 2025 年硕士研究生拟录取名单页面及同站 `download.jsp` 附件。通用爬虫成功抓取 10 个官方页面/附件，原始抽取 589 条，通用清洗保留 548 条考生编号级记录，坏词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch402_bift_2026_master.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch403_tjufe_2026_adjustment.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch404_cpu_2025_master_first_batch.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch405_cpu_2026_adjustment.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch406_cupl_2025_master.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch407_nenu_2025_master.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch408_nenu_colleges_2025.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch408_nenu_colleges_2025/records_clean.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch408_nenu_colleges_2025/records_public.csv`

入库来源：
- 东北师范大学文学院 2025 年硕士研究生拟录取名单：`https://chinese.nenu.edu.cn/info/1111/10401.htm`
- 东北师范大学生命科学学院 2025 年全日制硕士研究生拟录取名单：`https://sky.nenu.edu.cn/info/1029/3693.htm`
- 东北师范大学教育学部 2025 年硕士研究生拟录取名单：`https://edu.nenu.edu.cn/info/1085/8717.htm`
- 东北师范大学化学学院 2025 年硕士研究生拟录取名单：`https://chem.nenu.edu.cn/info/1042/5323.htm`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：268,539 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：268,539 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：274,244 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：274,244 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：598 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，394 所已精确匹配官网记录

验证：
- batch408 clean/public：548 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 274,244 条、Source_Summary 598 条、Coverage 430 条。

### 2026-06-02 batch409-batch410：福建师范大学生命科学学院复试结果 PDF 入库

本轮继续处理福建师范大学缺口。以下源留证但未入库：

- 福建师范大学马克思主义学院 2025 年硕士研究生招生复试结果公布 PDF：`https://mkszyxy.fjnu.edu.cn/_upload/article/files/f1/9d/867a374943ea96e25ba9611ee449/88585828-a477-4777-b247-1d59d7826dab.pdf` 实时 HTTP 200，但 `Content-Type: text/html;charset=UTF-8` 且 `Content-Length: 0`，本地 `curl.exe -L` 下载 0 字节，不可复现抽取。

可入库来源为福建师范大学生命科学学院官网“2024 年硕士研究生招生复试结果公布（一志愿）”。公告页公开同站 PDF 附件，PDF 文本层可复现抽取，原表含“拟录取意见”列。通用爬虫对附件未抽出记录，按 TDD 新增专项解析，只保留 `拟录取意见 == 建议录取` 的记录；空状态、`不予录取`、`放弃复试` 行全部排除。最终入库 148 条考生编号级建议录取记录。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch409_fjnu_mks_2025_result.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch410_fjnu_life_2024_result.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch410_fjnu_life_2024_result_curated/records_clean_curated.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch410_fjnu_life_2024_result_curated/records_public_curated.csv`
- `scripts/curate_batch410_fjnu_life_2024_result.py`
- `tests/test_curate_batch410_fjnu_life_2024_result.py`

入库来源：
- 福建师范大学生命科学学院 2024 年硕士研究生招生复试结果公布（一志愿）：`https://life.fjnu.edu.cn/e2/f9/c4509a385785/page.htm`
- 官方 PDF 附件：`https://life.fjnu.edu.cn/_upload/article/files/1c/75/429798164f80a01743a8f27b70c0/d450bf92-3d86-426c-b470-9d177b6666f9.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：268,687 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：268,687 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：274,392 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：274,392 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：599 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，395 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch410_fjnu_life_2024_result`：3 个测试通过。
- batch410 curated/public：148 条，均含 `official_admission_status: 建议录取`，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 274,392 条、Source_Summary 599 条、Coverage 430 条。

### 2026-06-02 batch411：沈阳师范大学公示查询系统过期未入库

沈阳师范大学研究生处官网“2024 年全国硕士研究生招生考试拟录取名单公示”页面可抓取，但正文中的名单入口显示为“点击此处，公示期已结束”，未暴露真实名单链接、附件或可结构化候选人表格，因此不入库。

种子：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch411_synu_2024_master.csv`

留证来源：
- `https://yjs.synu.edu.cn/2024/0424/c3649a93125/page.htm`

### 2026-06-02 batch412-batch420：佛山大学官方 PDF 入库

本轮继续从剩余覆盖缺口中筛选官网来源。以下源留证但未入库：

- 大连外国语大学 2025 年一志愿拟录取名单公示页 `https://gd.dlufl.edu.cn/info/1013/2867.htm` 实时 HTTP 404。
- 东北电力大学 2026 年推荐免试研究生拟录取名单页 `https://grad.neepu.edu.cn/info/1050/3500.htm` 和电气工程学院 2026 年硕士拟录取页 `https://grad.neepu.edu.cn/info/1044/2660.htm` 实时 HTTP 404。
- 大连海洋大学 2025 年调剂第一批拟录取名单 PDF 直链实时 HTTP 404。
- 沈阳体育学院 2025 年一志愿拟录取名单公示页实时 HTTP 404。
- 沈阳师范大学 2025 年拟录取名单公示页可抓取，但附件仅显示“公示期已结束”，未暴露真实 href。
- 北京协和医学院 2025 年拟录取名单页面 `https://graduate.pumc.edu.cn/zsw/info/1007/2098.htm` 实时 HTTP 404；其历年硕士录取名单页可抓取，但附件下载页要求验证码，未绕过；公开结果系统 `https://yzbtm.pumc.edu.cn/result/result/formalResult` 当前表格为空。
- 南京财经大学 2025 年一志愿拟录取名单页面可抓取，但附件仅显示“已过公示期”，未暴露真实 href。
- 成都体育学院 2025 年拟录取名单页返回 WEB 应用防火墙人机识别/验证码页，未绕过。
- 云南民族大学 2025 年全校 PDF 直链实时 HTTP 521；马克思主义学院、文化学院、体育学院官方页实时 HTTP 502。
- 中国海洋大学 2025 年硕士拟录取名单公告页可抓取，但附件仅显示“公示已结束”，未暴露真实 href。
- 广东药科大学 2025 年一志愿拟录取名单页实时 HTTP 404。
- 西北师范大学教育科学学院 2025 年第一志愿复试结果页实时 HTTP 412。

可入库来源为佛山大学官网 `www.fosu.edu.cn` 的 2025 年硕士研究生拟录取名单 PDF。该官方 PDF 直链可复现抓取，通用爬虫抽出 1,903 条候选记录，清洗后保留 1,012 条考生编号级拟录取记录，硬排除词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch412_dlu_neepu_dlou.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch413_syty_synu_2025.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch414_pumc_nufe_cdsu_2025.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch415_pumc_master_list_index.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch416_ymu_2025_master_pdf.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch417_ymu_colleges_2025.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch418_ouc_2025_master_page.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch419_gdpu_nwnu_2025.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch420_fosu_2025_master_pdf.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch420_fosu_2025_master_pdf/records_clean.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch420_fosu_2025_master_pdf/records_public.csv`

入库来源：
- 佛山大学 2025 年硕士研究生拟录取名单官方 PDF：`https://www.fosu.edu.cn/yanjiusheng/wp-content/uploads/sites/105/2025/05/%E4%BD%9B%E5%B1%B1%E5%A4%A7%E5%AD%A62025%E5%B9%B4%E7%A1%95%E5%A3%AB%E7%A0%94%E7%A9%B6%E7%94%9F%E6%8B%9F%E5%BD%95%E5%8F%96%E5%90%8D%E5%8D%95.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：269,699 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：269,699 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：275,404 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：275,404 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：600 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，396 所已精确匹配官网记录

验证：
- batch420 clean/public：1,012 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 275,404 条、Source_Summary 600 条、Coverage 430 条。

### 2026-06-02 batch421-batch423：沈阳化工大学官方 PDF 入库

本轮继续从剩余覆盖缺口中筛选官网来源。以下源留证但未入库：

- 齐鲁工业大学研究生招生信息网 2025 年一志愿复试录取相关页面 `https://yjszs.qlu.edu.cn/2025/0402/c6601a255579/page.htm` 与 `https://yjszs.qlu.edu.cn/2025/0421/c6602a256488/page.htm` 均可抓取，但正文仅显示“公示已结束”，未暴露附件 href 或考生编号表格，通用爬虫记录数 0。
- 山西中医药大学研究生学院 2025 年复试录取公告 `https://yjsb.sxtcm.edu.cn/info/1100/4511.htm` 可抓取，页面列出 6 个 PDF 附件入口；实际附件入口返回“请输入验证码下载附件”HTML 页，未绕过验证码，记录数 0。

可入库来源为沈阳化工大学研究生院官网 2024 年硕士研究生一志愿拟录取结果。官网页面通过公开详情 JSON 暴露 PDF 附件直链；主 PDF 通用爬虫抽出 615 条，士兵专项 PDF 通用爬虫未识别表格，按 TDD 新增专项解析，只保留附件名单中 `拟录取状态 == 拟录取` 的 5 条记录，并忽略正文录取办法中的 `不予录取` 规则文字。最终入库 620 条考生编号级拟录取记录。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch421_qlu_2025_master.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch422_sxtcm_2025_master.csv`
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch423_syuct_2024_master_pdf.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch423_syuct_2024_master_pdf/records_clean.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch423_syuct_2024_master_pdf/records_public.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch423_syuct_2024_soldier_curated/records_clean_curated.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch423_syuct_2024_soldier_curated/records_public_curated.csv`
- `scripts/curate_batch423_syuct_2024_soldier.py`
- `tests/test_curate_batch423_syuct_2024_soldier.py`

入库来源：
- 沈阳化工大学 2024 年硕士研究生招生考试一志愿拟录取结果（不含大学生士兵专项）：`https://grs.syuct.edu.cn/content.html?id=630124648704513475&divcol=202404`
- 官方 PDF 附件：`https://zbhk-new.lnyun.com.cn/www/hgdxyjsy/pdf/202404/630124584615547872.pdf`
- 沈阳化工大学 2024 年硕士研究生招生“退役大学生士兵计划”一志愿考生拟录取结果公示：`https://grs.syuct.edu.cn/content.html?id=630116855725429338&divcol=202404`
- 官方 PDF 附件：`https://zbhk-new.lnyun.com.cn/www/hgdxyjsy/pdf/202404/630116749978637260.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：270,319 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：270,319 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：276,024 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：276,024 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：602 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，397 所已精确匹配官网记录

验证：
- `python -m unittest tests.test_curate_batch423_syuct_2024_soldier`：3 个测试通过。
- batch423 合计 620 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 276,024 条、Source_Summary 602 条、Coverage 430 条。

### 2026-06-02 batch424-batch427：后续官方源复核未入库

本轮继续复核剩余缺口中的官方源，未新增可入库记录，B 类官网主表和 A+B 清洗包计数保持 batch423 后状态。

留证但未入库：
- 山东理工大学研究生院 2024 年硕士研究生第一志愿复试成绩及拟录取结果公示页 `https://yjsh.sdut.edu.cn/2024/0403/c5153a512719/page.htm` 可抓取，正文说明“名单见附件1”，但 HTML 中仅输出 `附件1.pdf/附件2.pdf` 文字与 PDF 图标，未暴露附件 href 或结构化候选人表格；通用爬虫记录数 0。
- 沈阳航空航天大学 2025 年推免生拟录取公示页 `https://yjs.sau.edu.cn/info/1002/4267.htm` 实时 HTTP 404。
- 重庆邮电大学 2025 年拟录取直博生、推免生名单公示页 `https://yjs.cqupt.edu.cn/info/1180/9944.htm` 实时 HTTP 412。
- 中国医科大学 2025 年拟接收推免硕士名单公示页 `https://www.cmu.edu.cn/cmuyjs/info/1905/9515.htm` 使用爬虫访问触发 SSL legacy renegotiation 错误；`curl.exe -L` 可连接但返回站点 404 错误提示页。
- 华东师范大学 2025 年推免拟录取名单公示页 `https://yjszs.ecnu.edu.cn/de/c2/c43264a646850/page.htm` 可抓取，但标题和正文均显示“公示已结束”，附件位置仅显示“附件：（公示已结束）”，无 href；正文另含 1 名考生放弃拟录取资格的变动说明，未入库。
- 天津财经大学 2025 年接收推免生名单公示页 `https://yjsy.tjufe.edu.cn/info/1082/3531.htm` 实时 HTTP 404。
- 南京理工大学 2025 年接收推荐免试研究生拟录取名单公示页 `https://gs.njust.edu.cn/zsw/31/b3/c4587a340403/page.htm` 实时 HTTP 410。
- 中国海洋大学 2025 年推免拟录取名单公示页 `http://yz.ouc.edu.cn/2024/1030/c31626a487896/page.htm` 跳转为提示信息页，记录数 0。
- 成都体育学院 2025 年接收推免生拟录取名单（一、二）页面 `https://yjsy.cdsu.edu.cn/info/1021/4966.htm`、`https://yjsy.cdsu.edu.cn/info/1021/4980.htm` 均返回 WEB 应用防火墙人机识别/验证码页，未绕过。
- 浙江中医药大学 2025 年硕士研究生拟录取名单公示页 `https://yjsgl.zcmu.edu.cn/show/5810` 实时 HTTP 412。
- 桂林医科大学 2026 年接收推免生拟录取名单公示页 `https://www.glmu.edu.cn/yjszs/info/1071/4416.htm` 实时 HTTP 404。

### 2026-06-02 batch428-batch440：大连外国语大学官方 PDF 入库

本轮继续复核剩余覆盖缺口中的官网来源，新增大连外国语大学 2020 年硕士研究生一志愿考生拟录取名单 371 条。以下源已留证但未入库：

- 首都师范大学研究生院 2023 年拟录取相关页面 `https://grad.cnu.edu.cn/info/1014/2274.htm` 抓取时跳转至 `https://www.cnu.edu.cn/` 首页，未取得名单正文或附件。
- 中国政法大学 2020 年推免官方 PDF 直链 `https://yjsy.cupl.edu.cn/__local/3/20/C3/A3E73F09AF99BB7B2D01C983967_9A3F2211_11ACAB.pdf?e=.pdf` 返回 `text/html` 动态挑战页，未绕过 JS challenge。
- 北京电影学院研究生院 2020-2021 年拟录取相关官方页面 `https://www.bfa.edu.cn/yanjiusheng/info/1031/3842.htm`、`https://www.bfa.edu.cn/yanjiusheng/info/1031/3848.htm`、`https://www.bfa.edu.cn/yanjiusheng/info/1031/3724.htm`、`https://www.bfa.edu.cn/yanjiusheng/info/1049/2939.htm` 均实时 HTTP 412。
- 中国药科大学研究生招生网 2024 年推免官方 PDF 直链 `https://yjszs.cpu.edu.cn/_upload/article/files/de/e5/645fdb114b57a11d58330e90c989/289649dc-8399-4e8e-b808-abcfc46dfb88.pdf` 实时 HTTP 404。
- 北京服装学院研究生院 2023 年招生信息页 `https://yjs.bift.edu.cn/zsgz/zsxx/9bbe264e20d94a0e8b697e3b0bb35b39.htm` 跳转至站点 `custom404.html`。
- 东北电力大学研究生院 2024 年推免相关页面 `https://grad.neepu.edu.cn/info/1050/2230.htm` 实时 HTTP 404。
- 南京理工大学研究生招生网 2025 年接收推荐免试研究生拟录取名单公示页 `https://gs.njust.edu.cn/zsw/31/b3/c4587a340403/page.psp` 实时 HTTP 410。
- 甘肃中医药大学研究生院旧版参数页 `http://yjsc.gszy.edu.cn/index.php?m=content&c=index&a=show&catid=12&id=1441` 抓取后跳至新版站点首页，未取得名单正文或附件。
- 广东药科大学研究生院 2024 年拟录取相关页面 `https://yjsxy.gdpu.edu.cn/info/1012/2262.htm`、`https://yjsxy.gdpu.edu.cn/info/1012/2287.htm` 均实时 HTTP 404。
- 郑州轻工业大学研究生处 2024 年拟录取相关页面 `https://yjsc.zzuli.edu.cn/2024/0424/c2878a311408/page.htm` 可抓取，正文提示名单“见附件”且“公示已结束”，HTML 未暴露附件 href 或考生编号表格，记录数 0。
- 沈阳体育学院研究生处 2025 年推免拟录取相关页面 `https://yjs.syty.edu.cn/info/1010/2384.htm` 实时 HTTP 404。
- 大连海洋大学 2025 年推免相关页面 `https://www.dlou.edu.cn/2024/1023/c5860a177424/page.htm` 抓取为提示信息页，记录数 0。

可入库来源为大连外国语大学研究生处官网 2020 年硕士研究生招生一志愿考生拟录取名单（普通计划）官方 PDF。通用爬虫抽取 371 条考生编号级记录，清洗后 371 条全部进入 public 表，硬排除词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch439_dlufl_2020_master_pdf.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch439_dlufl_2020_master_pdf/records_clean.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch439_dlufl_2020_master_pdf/records_public.csv`

入库来源：
- 大连外国语大学 2020 年硕士研究生招生一志愿考生拟录取名单（普通计划）官方 PDF：`https://gd.dlufl.edu.cn/__local/8/66/30/88772C2D11625E2FEC4182315DF_0427F83B_74F11.pdf?e=.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：270,690 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：270,690 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：276,395 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：276,395 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：603 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，398 所已精确匹配官网记录，32 所仍未完成

验证：
- batch439 clean/public：371 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 276,395 条、Source_Summary 603 条、Coverage 430 条。

### 2026-06-02 batch441-batch446：北京协和医学院官方 PDF 入库

本轮继续从剩余 32 所覆盖缺口中检索实时可复现的官网来源，新增北京协和医学院 2019 年博士（申请审核及硕转博）拟录取名单 658 条。以下源已留证但未入库：

- 东北电力大学 2026 年推荐免试研究生拟录取名单公示页 `https://grad.neepu.edu.cn/info/1050/3500.htm` 搜索索引可见，但 `https` 与 `http` 实时访问均返回站点 404 提示页；栏目页 `https://grad.neepu.edu.cn/1050/list.htm` 也返回 404 提示页。
- 大连海洋大学 2024 年全国硕士研究生招生调剂第二批考生拟录名单官方 PDF 直链 `https://www.dlou.edu.cn/_upload/article/files/e7/fb/e8bdbb4040f4a9987ac2d09f5ee4/d048fe33-6d3d-463f-8c74-203b3176890b.pdf` 实时 HTTP 404；搜索恢复的正文页进入统一身份认证登录页，未入库。
- 中国药科大学 2020 推免公示页实时 HTTP 410，2021 博士拟录取 PDF 直链实时 HTTP 404。
- 西北师范大学 2025 博士拟录取名单 PDF 直链实时 HTTP 404。
- 西藏农牧大学/西藏农牧学院研究生处列表页 `https://www.xza.edu.cn/yjsc/1040/list.htm` 证书链不受本机信任；使用 `curl -k` 后跳转到 `127.0.0.1:9`，无法复现官网列表。
- 广东药科大学 2026 年博士研究生拟录取名单公示页 `https://yjsxy.gdpu.edu.cn/info/1012/2571.htm` 可抓取，但附件入口 `download.jsp?...wbfileid=16648748` 返回 3,805 字节 HTML 下载桥页，不是真 PDF；页面误抽出的“下载专区/规章制度”为导航噪声，未入库。
- 云南民族大学 2025 年博士拟录取及递补公示页 `https://web.ymu.edu.cn/yjsy/info/1201/3611.htm`、`https://web.ymu.edu.cn/yjsy/info/1201/3621.htm`、`https://web.ymu.edu.cn/yjsy/info/1201/3631.htm` 实时 HTTP 521。
- 山东理工大学 2026 推免公示页与 2026 博士拟录取公示页可抓取，但未暴露可结构化人员表或可下载名单附件，记录数 0。
- 天津财经大学 2026 年具备硕博连读拟录取资格名单页 `https://yjsy.tjufe.edu.cn/info/1044/3736.htm` 实时 HTTP 404。
- 浙江中医药大学 2025 年硕士拟录取页实时 HTTP 412；2025 年博士拟录取三条页面实时 HTTP 405。
- 桂林医科大学 2026 年硕士拟录取名单正文页可访问，但附件下载要求验证码；旧域 `https://www.glmc.edu.cn/yjszs/NLQMDGS.pdf` 实时返回 403 或远端断开。
- 北京服装学院 2026 年硕士统考拟录取页与推免拟录取页均跳转至 `https://www.bift.edu.cn/apachehtml/custom404.html`。
- 中国政法大学 2017 年硕士拟录取名单官方 PDF 直链实时返回 `text/html` JavaScript challenge 页，不绕过。
- 中国医科大学 2024 年硕士研究生招生统考拟录取名单公示页在 Python 抓取中触发 SSL legacy renegotiation 错误；`curl.exe -L` 可连接但返回站点 404 提示页。

可入库来源为北京协和医学院研究生招生办公室官网 2019 年博士（申请审核及硕转博）拟录取名单官方 PDF。通用爬虫实时下载 PDF 并抽取 724 条原始记录；清洗后保留 658 条人员级记录，均含考生编号和录取专业代码，需复核 0 条，硬排除词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch446_pumc_2019_doctor_pdf.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch446_pumc_2019_doctor_pdf/records_clean.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch446_pumc_2019_doctor_pdf/records_public.csv`

入库来源：
- 北京协和医学院 2019 年博士（申请审核及硕转博）拟录取名单官方 PDF：`https://graduate.pumc.edu.cn/__local/7/7F/91/4FC58AE8E036660A73097550DD0_7453A99D_A9C96.pdf?e=.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,348 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,348 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,053 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,053 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：604 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，399 所已精确匹配官网记录，31 所仍未完成

验证：
- batch446 clean/public：658 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 277,053 条、Source_Summary 604 条、Coverage 430 条。

### 2026-06-02 batch447-batch451：南京理工大学官方 HTML 表格入库

本轮继续从剩余 31 所覆盖缺口中筛选官网来源，新增南京理工大学 2024 年公开招考博士研究生拟录取名单（四）3 条。以下源已留证但未入库：

- 成都体育学院 2025 年接收推免生拟录取名单（一）（二）官方 `__local` PDF 直链可被搜索恢复，但实时抓取返回标题为“WEB 应用防火墙”的 HTML 页面，`content_type=text/html`，不是真 PDF，未绕过。
- 华东师范大学信息公开网 2024 年硕士研究生拟录取名单公示页 `https://xxgk.ecnu.edu.cn/c7/7d/c29049a640893/page.htm` 可抓取，并可跟到官方 PDF `https://xxgk.ecnu.edu.cn/_upload/article/files/43/58/18a922cb497eb0a5b79b1e8f9239/3677d138-8ae7-43e0-9fc6-829a045e25b8.pdf`；但 PDF 为 74 页、加密、禁止复制，文本层仅抽出“禁止转载”水印，当前无可靠人员级文本表，不做 OCR 猜测入库。
- 重庆邮电大学 2024 年硕士研究生拟录取名单公示（第一批）官网页 `http://yjs.cqupt.edu.cn/info/1180/7864.htm` 实时 HTTP 412。
- 沈阳体育学院 2024 年硕士研究生一志愿拟录取名单公示页 `https://yjs.syty.edu.cn/info/1010/2330.htm` 实时 HTTP 404。
- 山东理工大学 2026 年推免和博士拟录取页面复核确认仍只保留“附件1.pdf/2026年拟录取推免生名单.pdf”等文字，无 href 或可请求附件链接，未猜测隐藏地址。

可入库来源为南京理工大学研究生院官网 2024 年公开招考博士研究生拟录取名单（四）HTML 表格。通用爬虫初次抽取 21 条，其中混入页面通讯录导航噪声；按 TDD 新增 `scripts/curate_batch451_njust_2024_doctor_html.py` 与 `tests/test_curate_batch451_njust_2024_doctor_html.py`，仅保留表头为“序号/拟录取学院/拟录取专业代码/拟录取专业名称/姓名/备注”的真实名单表，最终入库 3 条人员级记录。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch451_njust_2024_doctor_html.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch451_njust_2024_doctor_html_curated/records_clean_curated.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch451_njust_2024_doctor_html_curated/records_public_curated.csv`
- `scripts/curate_batch451_njust_2024_doctor_html.py`
- `tests/test_curate_batch451_njust_2024_doctor_html.py`

入库来源：
- 南京理工大学 2024 年公开招考博士研究生拟录取名单（四）：`https://gs.njust.edu.cn/18/9f/c14687a333983/page.htm`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,351 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,351 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,056 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,056 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：605 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，400 所已精确匹配官网记录，30 所仍未完成

验证：
- `python -m unittest tests.test_curate_batch451_njust_2024_doctor_html`：2 个测试通过。
- batch451 curated/public：3 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 277,056 条、Source_Summary 605 条、Coverage 430 条。

### 2026-06-02 batch452-batch462：齐鲁工业大学官方 HTML 表格入库

本轮先复核用户提到的 B 类缺口，新增齐鲁工业大学 2025 年图书情报专业一志愿拟录取名单 12 条。以下源已留证但未入库：

- 首都师范大学 2022 年硕士研究生招生考试一志愿拟录取结果公示官方 `__local` PDF 直链实时返回首都师范大学首页 HTML，`content_type=text/html`，不是真 PDF，未入库。
- 中国政法大学 2024 年硕士研究生招生考试拟录取名单通知页可抓取，但页面无人员名单表；中国药科大学 2024 年硕士拟录取官方 PDF 线索实时 HTTP 404，未入库。
- 南京财经大学 2024 年硕士研究生一志愿拟录取名单公示页可抓取，但附件已过公示期且页面未暴露 href，未入库。
- 郑州轻工业大学 2024 年硕士研究生拟录取名单公示页可抓取，但正文仅余公告与联系表，名单附件已撤；东北电力大学 2026 年推免拟录取页面实时 HTTP 404，未入库。
- 山西中医药大学 2024 年硕士研究生招生考试复试录取公告（一）可抓取并发现 6 个附件入口，但附件下载页要求验证码，未绕过。
- 沈阳体育学院 2025 年硕士研究生一志愿拟录取名单公示页实时 HTTP 404；广东药科大学 2025 年硕士一志愿拟录取名单公示页实时 HTTP 404；西北师范大学 2024 年硕士拟录取公示页实时 HTTP 412；云南民族大学民族文化学院 2024 年硕士拟录取名单页实时 HTTP 521，均未入库。

可入库来源为齐鲁工业大学图书馆（山东省科学院情报研究所）官网招生信息栏目。通用爬虫从列表页跟进到 `https://lib.qlu.edu.cn/2025/0325/c13718a254296/page.htm`，抽取 13 条原始记录；清洗后剔除 1 条空姓名/空考生编号的落款噪声，保留 12 条人员级记录，需复核 0 条，硬排除词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch462_qlu_lib_2024_master.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch462_qlu_lib_2024_master/records_clean.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch462_qlu_lib_2024_master/records_public.csv`

入库来源：
- 齐鲁工业大学图书情报专业一志愿拟录取名单：`https://lib.qlu.edu.cn/2025/0325/c13718a254296/page.htm`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,363 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,363 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,068 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,068 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：606 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，401 所已精确匹配官网记录，29 所仍未完成

验证：
- batch462 clean/public：12 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建并复核：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 277,069 行（含表头）、Source_Summary 607 行（含表头）、Coverage 431 行（含表头）。

### 2026-06-02 batch463-batch467：沈阳航空航天大学官方 PDF 入库

本轮继续从剩余 29 所覆盖缺口中检索可复现官网来源，新增沈阳航空航天大学航空发动机学院 2022 级博士研究生申请考核制拟录取考生名单 4 条。以下源已留证但未入库：

- 北京林业大学 2026 年博士研究生拟录取结果通知页 `https://graduate.bjfu.edu.cn/zsgl/zsdt/8e929739678b4b4ea9e1ce40790c629d.html` 可抓取，并可跟到官方 docx `https://graduate.bjfu.edu.cn/docs/2026-04/9de398956e2d4132be9986b6858098a9.docx`；但 docx 内容为“政治审查表”，不是人员名单，未入库。
- 中国海洋大学 2026 年推荐免试攻读研究生拟录取名单官方 PDF 线索 `https://yz.ouc.edu.cn/_upload/article/files/8b/c8/9273a1a047369c7f2ddb3c59dc2e/85e3c515-1f4b-462e-8dd5-14b287ab30b5.pdf` 实时 HTTP 404，未入库。
- 北京电影学院 2025 年硕士拟录取名单及体检通知官方页 `https://www.bfa.edu.cn/yanjiusheng/info/1031/4405.htm` 实时 HTTP 412，未入库。
- 北京服装学院 2025 年硕士研究生招生考试拟录取名单官方线索 `https://yjs.bift.edu.cn/zsgz/zsxx/3656978fc0084cf5abca17d26055a922.htm` 最终跳转至 `https://www.bift.edu.cn/apachehtml/custom404.html`，未入库。

可入库来源为沈阳航空航天大学研究生院官网 `__local` PDF 直链。通用爬虫实时下载 PDF 并抽取 4 条原始记录；清洗后保留 4 条人员级记录，需复核 0 条，硬排除词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch467_sau_2022_doctor_pdf.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch467_sau_2022_doctor_pdf/records_clean.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch467_sau_2022_doctor_pdf/records_public.csv`

入库来源：
- 沈阳航空航天大学航空发动机学院 2022 级博士研究生申请考核制拟录取考生名单：`https://yjs.sau.edu.cn/__local/7/46/7E/BD24B1756017798876E19BCFE52_9517D8A5_92BD.pdf?e=.pdf`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,367 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,367 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,072 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,072 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：607 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，402 所已精确匹配官网记录，28 所仍未完成

验证：
- batch467 clean/public：4 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建并复核：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 277,073 行（含表头）、Source_Summary 608 行（含表头）、Coverage 431 行（含表头）。

### 2026-06-02 batch468-batch476：剩余缺口官网源复核但无新增入库

本轮继续从剩余 28 所覆盖缺口中复核可复现官网来源。以下源均为官方域名或由搜索结果恢复出的官方原文/直链；因实时不可下载、无公开附件地址、动态挑战或无可用文本层等原因仅留证，不入库：

- 沈阳师范大学 2025 年全国硕士研究生招生考试拟录取名单公示页 `https://yjs.synu.edu.cn/2025/0424/c3649a99767/page.htm` 可抓取；页面正文显示“附件：沈阳师范大学2025年全国硕士研究生招生考试拟录取名单.pdf（公示期已结束）”，但源码仅保留附件文字与 PDF 图标，未暴露 href，未猜测隐藏文件名。
- 浙江中医药大学 2025 年硕士研究生拟录取名单公示页 `https://yjsgl.zcmu.edu.cn/show/5810` 实时 HTTP 412，未入库。
- 重庆邮电大学 2025 年硕士研究生一志愿考生拟录取名单公示页 `https://yjs.cqupt.edu.cn/info/1180/11244.htm` 实时 HTTP 412，未入库。
- 东北电力大学电气工程学院 2026 年硕士研究生招生拟录取名单页 `https://grad.neepu.edu.cn/info/1044/2660.htm` 实时 HTTP 404，未入库。
- 大连海洋大学 2025 年硕士研究生一志愿普通计划及调剂第一、第二、第三、第五批拟录取官方 PDF 直链均实时 HTTP 404，未入库。
- 中国药科大学 2025 年硕士研究生拟录取名单公示第二、第三批次官方 PDF 直链均实时 HTTP 404，未入库。
- 华东师范大学 2025 年全国硕士研究生招生考试拟录取名单公示页 `https://xxgk.ecnu.edu.cn/fc/45/c11832a719941/page.htm` 可抓取并跟到官方 PDF `https://xxgk.ecnu.edu.cn/_upload/article/files/91/2c/c572f8d244cd849ec879f177dae4/fa6b90ed-39b0-4359-bf44-3482c5c03c46.pdf`；PDF 为 79 页、不加密但无可抽取文本层，`pypdf` 前三页提取为空，`pdftotext -layout` 仅输出换页符，未做 OCR 猜测入库。
- 中国政法大学 2025 年统考硕士研究生拟录取名单公示页 `https://yjsy.cupl.edu.cn/info/1022/12344.htm` 返回动态 challenge HTML，未绕过。
- 广东药科大学 2026 年硕士研究生招生一志愿拟录取名单公示页 `https://yjsxy.gdpu.edu.cn/info/1012/2555.htm` 实时 HTTP 404，未入库。

本轮无新增记录，B 类官网主表与 A+B 统一清洗包维持上一批次计数：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,367 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,072 条
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，402 所已精确匹配官网记录，28 所仍未完成

### 2026-06-02 batch477-batch480：山东理工大学官方 HTML 表格入库

本轮继续从剩余 28 所覆盖缺口中复核官网来源，新增山东理工大学化学工程与技术学科 2026 年博士研究生补录名单 1 条。以下源已留证但未入库：

- 首都师范大学 2026 年硕士研究生拟录取名单第一批、第三批及 2025 年一志愿考生拟录取名单页面实时抓取均跳转到 `https://www.cnu.edu.cn/` 首页 HTML，不是真正名单页，未入库。
- 桂林医科大学 2026 年接收推免生攻读硕士研究生拟录取名单公示页 `https://mgmt.glmc.edu.cn/yjszs/info/1252/4415.htm` 本地 crawler 报 `RemoteDisconnected`；`curl.exe -L -I` 复核为 `Recv failure: Connection was reset`，未入库。
- 山东理工大学招生工作列表 `https://yjsh.sdut.edu.cn/5139/list1.htm` 可抓取；列表页本身无人员表。2026 年博士拟录取公示页 `https://yjsh.sdut.edu.cn/2026/0519/c5139a564543/page.htm` 可抓取但通用解析无记录，未单独入库。

可入库来源为山东理工大学研究生工作部官网 HTML 表格 `https://yjsh.sdut.edu.cn/2026/0528/c5139a565537/page.htm`。通用爬虫抽取 1 条原始记录；清洗后根据页面标题/正文补充学科“化学工程与技术”，根据表格补充招生方式“申请-考核”和就业方式“非定向”，最终入库 1 条人员级记录。该页正文说明因其他拟录取考生放弃资格而补录；入库记录本身为补录拟录取人员，硬排除词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch480_sdut_2026_doctor.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch480_sdut_2026_doctor_curated/records_clean_curated.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch480_sdut_2026_doctor_curated/records_public_curated.csv`

入库来源：
- 山东理工大学化学工程与技术学科 2026 年博士研究生补录名单公示：`https://yjsh.sdut.edu.cn/2026/0528/c5139a565537/page.htm`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,368 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,368 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,073 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,073 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：608 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，403 所已精确匹配官网记录，27 所仍未完成

验证：
- batch480 curated/public：1 条，硬排除词扫描命中 0。
- B 类 master/public 与 A+B master/public 的记录状态字段扫描均无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建并复核：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 277,074 行（含表头）、Source_Summary 609 行（含表头）、Coverage 431 行（含表头）。

### 2026-06-02 batch481：天津财经大学官网硕博连读拟录取资格名单入库

本轮继续从剩余 27 所覆盖缺口中复核官网来源，新增天津财经大学 2026 年具备硕博连读拟录取资格名单 5 条。以下源已留证但未入库：

- 中国海洋大学 2025 年推免拟录取名单官方页 `https://yz.ouc.edu.cn/2024/1030/c31648a487896/page.htm` 可抓取；正文仅保留“附件：中国海洋大学2025年推荐免试研究生拟录取名单（公示已结束）”文字，无可下载 href，未入库。
- 华东师范大学 2025 年推荐免试攻读研究生拟录取名单官方页 `https://yjszs.ecnu.edu.cn/de/c2/c43463a646850/page.htm` 可抓取；附件位置均显示“公示已结束”，无公开下载地址，且页面含 1 名拟录取考生放弃资格的变动说明，未入库。
- 中国医科大学 2026 年拟接收优秀免试攻读硕士学位研究生名单官网附件入口 `https://www.cmu.edu.cn/system/_content/download.jsp?owner=1778759152&urltype=news.DownloadAttachUrl&wbfileid=13255969` 返回“请输入验证码下载附件”，未绕过验证码，未入库。
- 南京财经大学 2025 年硕士研究生一志愿拟录取名单公示页 `https://yjsc.nufe.edu.cn/info/1012/6524.htm` 可抓取；正文仅保留“附件：南京财经大学2025年硕士研究生一志愿拟录取名单公示(已过公示期)”文字，无可下载 href，未入库。
- 山西中医药大学 2024 年硕士研究生招生考试复试录取公告（一）`https://yjsb.sxtcm.edu.cn/info/1100/3939.htm` 可抓取并暴露 6 个 PDF 附件下载入口，但下载入口均返回验证码页面，未绕过验证码，未入库。
- 郑州轻工业大学 2024 年博士研究生拟录取名单公示页 `https://yjsc.zzuli.edu.cn/2024/0603/c20542a314281/page.htm` 可抓取；正文仅说明“名单请见附件/公示已结束”，页面表格为站点布局而非人员名单，无公开附件 href，未入库。
- 天津财经大学 2026 年具备硕博连读拟录取资格名单官网页 `https://yjsy.tjufe.edu.cn/info/1044/3736.htm` 本地 crawler 与 `curl.exe -L` 实时返回 HTTP 404；但通过网页检索打开同一学校官网 URL 可读到完整正文表格。本批仅从该官网页面正文手工校验入库，未使用第三方行数据。

可入库来源为天津财经大学研究生院官网 HTML 表格 `https://yjsy.tjufe.edu.cn/info/1044/3736.htm`。页面列出报名号、姓名、拟录取专业等字段；清洗后入库 5 条人员级记录，硬排除词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch481_tjufe_2026_master_doctor.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch481_tjufe_2026_master_doctor_curated/records_clean_curated.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch481_tjufe_2026_master_doctor_curated/records_public_curated.csv`

入库来源：
- 天津财经大学 2026 年具备硕博连读拟录取资格名单：`https://yjsy.tjufe.edu.cn/info/1044/3736.htm`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,373 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,373 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,078 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,078 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：609 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，404 所已精确匹配官网记录，26 所仍未完成

验证：
- batch481 curated/public：5 条，硬排除词扫描命中 0。
- A+B master public 的记录状态字段扫描无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建并复核：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 277,079 行（含表头）、Source_Summary 610 行（含表头）、Coverage 431 行（含表头）。

### 2026-06-02 batch482：沈阳体育学院官网调剂递补拟录取名单入库

本轮新增沈阳体育学院 2025 年硕士研究生调剂志愿拟录取名单公示（递补）1 条。官方页面 `https://yjs.syty.edu.cn/info/1010/2471.htm` 本地 crawler 与 `curl.exe -L` 实时返回 HTTP 404；但通过网页检索打开同一学校官网 URL 可读到正文表格。本批仅从该官网页面正文手工校验入库，未使用第三方行数据。同期复核沈阳体育学院博士递补拟录取页面 `https://yjs.syty.edu.cn/info/1010/2497.htm`，名单为图片形式且本地请求 404，未 OCR 入库。

可入库记录为调剂递补拟录取考生，非“待递补”。清洗后入库 1 条人员级记录，硬排除词扫描命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch482_syty_2025_master_replacement.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch482_syty_2025_master_replacement_curated/records_clean_curated.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch482_syty_2025_master_replacement_curated/records_public_curated.csv`

入库来源：
- 沈阳体育学院 2025 年硕士研究生调剂志愿拟录取名单公示（递补）：`https://yjs.syty.edu.cn/info/1010/2471.htm`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：271,374 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：271,374 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：277,079 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：277,079 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：610 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，405 所已精确匹配官网记录，25 所仍未完成

验证：
- batch482 curated/public：1 条，硬排除词扫描命中 0。
- A+B master public 的记录状态字段扫描无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补` 残留。
- 工作簿已重建并复核：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 277,080 行（含表头）、Source_Summary 611 行（含表头）、Coverage 431 行（含表头）。

### 2026-06-02 batch483：甘肃中医药大学官方 PDF 拟录取名单入库

本轮从第三方转载页仅恢复出学校官网 PDF 直链，未使用第三方人员行数据。可入库来源为甘肃中医药大学研究生院官网 PDF：

- `https://yjsc.gszy.edu.cn/ueditor/php/upload/file/20240507/1715071988136303.pdf`

该 PDF 可直接下载，文本层可抽取。通用爬虫可抽出 1166 条原始记录，但缺姓名和状态字段，未直接合并；新增 `scripts/curate_batch483_gszy_2024_master_pdf.py` 定向解析 PDF 文本层，并新增单测 `tests/test_curate_batch483_gszy_2024_master_pdf.py` 覆盖普通拟录取行、多行专业名、士兵计划、推免及“5+3”、非拟录取/不合格/缺明确体检结果排除。单测 `python -m unittest tests.test_curate_batch483_gszy_2024_master_pdf` 通过。

清洗策略：
- 统考/调剂部分：保留 `录取情况=拟录取` 且 `体检结果=合格` 的记录。该部分 PDF 未发布姓名，保留考生编号、专业、成绩、志愿类型。
- 推免及“5+3”部分：保留 `拟录取` 且 `合格` 的记录。该部分 PDF 未发布考生编号，保留姓名、专业和推免/5+3 标记。
- 文本层中 5 条缺少明确体检结果的断行未入库。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch483_gszy_2024_master_pdf.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch483_gszy_2024_master_pdf_curated/records_clean_curated.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch483_gszy_2024_master_pdf_curated/records_public_curated.csv`

本批入库：
- 统考/调剂硕士拟录取：1164 条
- 推免及“5+3”：81 条
- 合计：1245 条

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：272,619 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：272,619 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：278,324 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：278,324 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：612 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，406 所已精确匹配官网记录，24 所仍未完成

验证：
- batch483 curated/public：1245 条，硬排除词扫描命中 0。
- A+B master public 的记录状态字段扫描无 `进入复试名单/拟不录取/不予录取/是否拟录取: 否/admission_status: 否/official_admission_status: 否/放弃复试/复试不合格/缺考/候补/不合格/名额受限/放弃一志愿录取资格/拒绝待录取/因差额未录取/被其他学校待录取/未参加面试/自愿放弃拟录取/拒绝复试通知/放弃待录取通知/未参加复试/被其他院校录取/待递补/拟淘汰` 残留。
- 工作簿已重建并复核：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 278,325 行（含表头）、Source_Summary 613 行（含表头）、Coverage 431 行（含表头）。

### 2026-06-02 batch486：华东师范大学官方图片 PDF OCR 入库

本轮新增华东师范大学 2025 年全国硕士研究生招生考试拟录取名单 3688 条。来源为华东师范大学信息公开官网页面及其官方 PDF 附件：

- 页面：`https://xxgk.ecnu.edu.cn/fc/45/c11832a719941/page.htm`
- PDF：`https://xxgk.ecnu.edu.cn/_upload/article/files/91/2c/c572f8d244cd849ec879f177dae4/fa6b90ed-39b0-4359-bf44-3482c5c03c46.pdf`

该 PDF 为图片型表格，`pdftotext -layout` 仅返回换页符，不能通过文本层抽取。新增 `scripts/curate_batch486_ecnu_2025_ocr_pdf.py`，用 `pdftoppm` 渲染 79 页 PNG，再用 RapidOCR 识别词块，并按固定表格列重组姓名、考生编号、院系、学科、学习方式、初试成绩、复试成绩和总成绩。新增单测 `tests/test_curate_batch486_ecnu_2025_ocr_pdf.py` 覆盖普通行、非行文本跳过、拆分/噪声考生编号修复。

OCR 质量控制：
- 入库记录：3688 条。
- 3 条 OCR 行因缺失可靠姓名或院系字段未入库，未凭上下文猜测姓名。
- 全量记录无空姓名、空考生编号、空院系、空录取专业、空来源 URL。
- curated/public 坏词扫描命中 0，重复键命中 0。

种子与产物：
- `data/seeds/official_site_recommendation_websearch_web_20260602_batch486_cupl_ecnu_ouc_2025_2026.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch486_cupl_ecnu_ouc_2025_2026_ecnu_curated/records_clean_curated.csv`
- `data/processed/official_site_recommendation_websearch_web_20260602_batch486_cupl_ecnu_ouc_2025_2026_ecnu_curated/records_public_curated.csv`
- `tmp/pdfs/ecnu486/ocr_items.jsonl`

B 类官网主表随之更新为：
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`：276,307 条
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`：276,307 条

A+B 统一清洗包随之更新为：
- `data/cleaned/graduate_outcomes/master_records_clean.csv`：282,012 条
- `data/cleaned/graduate_outcomes/master_records_public.csv`：282,012 条
- `data/cleaned/graduate_outcomes/school_year_source_summary.csv`：613 行
- `data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv`：430 所院校覆盖追踪，407 所已精确匹配官网记录，23 所仍未完成

验证：
- `python -m unittest tests.test_curate_batch486_ecnu_2025_ocr_pdf`：3 项通过。
- batch486 ECNU curated/public：3688 条，硬排除词扫描命中 0。
- A+B master public：282,012 条，状态字段坏词扫描命中 0。
- 工作簿已重建并复核：`outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`，Public_Records 282,013 行（含表头）、Source_Summary 614 行（含表头）、Coverage 431 行（含表头）。

同轮未入库探测摘要：
- 山西中医药大学附件下载页要求验证码，未绕过。
- 云南民族大学页面返回 HTTP 521，西北师范学院页返回 HTTP 412，未绕过。
- 中国政法大学页面为 JS dynamic challenge，中国海洋大学 PDF 直链返回 404 且页面附件已撤，未入库。
- 大连海洋大学 PDF、东北电力大学页面、中国药科大学 PDF、广东药科大学页面均本地返回 404，未入库。
- 北京电影学院返回 HTTP 412；成都体育学院为 Web 应用防火墙；北京服装学院跳转 custom404，未入库。
