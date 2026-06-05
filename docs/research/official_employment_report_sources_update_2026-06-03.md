# Official Employment / Further-Study Report Sources Update - 2026-06-03

Scope: supplemental official school-level employment and further-study report data. The first pass covered the 15 schools that remain uncovered by B-class official row-level recommendation/admission lists; the follow-up pass expands the same source/metric schema to additional 430-school coverage candidates.

This track is intentionally separate from B-class row-level recommendation/admission records. It captures school-level employment/further-study indicators from official employment quality reports, undergraduate teaching quality reports, or official careers pages. It must not be used as proof of row-level recommendation/admission list coverage.

## Outputs

| Artifact | Rows | Notes |
| --- | ---: | --- |
| `data/cleaned/graduate_outcomes/official_employment_report_sources.csv` | 74 | Source-status rows for the initial 15 uncovered schools plus follow-up official report candidates. |
| `data/cleaned/graduate_outcomes/official_employment_report_metrics.csv` | 326 | Cleaned indicators from official materials or official/government pages quoting school reports where the source body/PDF was crawlable and extractable. |
| `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx` | 8 sheets | Includes `Undergrad_Source_Outcomes`, `Recommendation_Source_Attempts`, `Employment_Report_Sources`, and `Employment_Metrics` in the data package. |

## Extracted Metric Coverage

| School | Official material | Extracted indicator rows |
| --- | --- | ---: |
| 北京电影学院 | 2023-2024 undergraduate teaching quality report PDF | 6 |
| 北京服装学院 | 2023 graduate employment quality report PDF | 9 |
| 北京林业大学 | 2023-2024 undergraduate teaching quality report PDF | 11 |
| 宁波诺丁汉大学 | 2024 careers report page | 7 |
| 宁波诺丁汉大学 | 2024-2025 Careers and Employability Annual Report PDF | 62 |
| 西北师范大学 | 2023-2024 undergraduate teaching quality report PDF | 6 |
| 浙江中医药大学 | 2023-2024 undergraduate teaching quality report PDF | 10 |
| 中国科学技术大学 | 2023-2024 undergraduate teaching quality report PDF | 5 |
| 北京交通大学 | 2023-2024 undergraduate teaching quality report PDF | 6 |
| 天津科技大学 | 2023 graduate employment quality report PDF | 9 |
| 河北科技大学 | 2023-2024 undergraduate teaching quality report PDF | 6 |
| 天津科技大学 | 2023-2024 undergraduate teaching quality report PDF | 7 |
| 北京理工大学 | 2023-2024 undergraduate teaching quality report PDF | 4 |
| 北京科技大学 | 2023-2024 undergraduate teaching quality report PDF | 7 |
| 北京师范大学 | 2023 graduate employment quality report PDF | 6 |
| 东北电力大学 | 2023-2024 undergraduate teaching quality report PDF | 10 |
| 中国医科大学 | 2023-2024 undergraduate teaching quality report PDF | 5 |
| 南京财经大学 | 2023 postgraduate education quality report PDF | 7 |
| 大连海洋大学 | 2023-2024 undergraduate teaching quality report PDF | 13 |
| 南京大学 | 2023-2024 undergraduate teaching quality report PDF | 16 |
| 中山大学 | 2023-2024 undergraduate teaching quality report PDF | 6 |
| 新疆大学 | 2023-2024 undergraduate teaching quality report PDF | 16 |
| 北京化工大学 | 2023-2024 undergraduate teaching quality report PDF | 30 |
| 中国传媒大学 | 2023-2024 undergraduate teaching quality report PDF | 16 |
| 重庆邮电大学 | 2016-2017 undergraduate teaching quality report PDF | 6 |
| 中国政法大学 | 2018 official information-disclosure employment/further-study page | 14 |
| 成都体育学院 | National Sports Administration page quoting 2022 graduate employment quality report | 2 |

对外经济贸易大学 has a reachable official teaching quality report PDF, but this pass did not find a school-level destination implementation rate or overall further-study rate; experimental-class further-study ratios were not ingested as school-level metrics.

## Follow-up Source Evidence

| School | Official candidate | Result |
| --- | --- | --- |
| 中国科学技术大学 | `https://www.teach.ustc.edu.cn/wp-content/uploads/2024/12/%E4%B8%AD%E5%9B%BD%E7%A7%91%E5%AD%A6%E6%8A%80%E6%9C%AF%E5%A4%A7%E5%AD%A62023-2024%E5%AD%A6%E5%B9%B4%E6%9C%AC%E7%A7%91%E6%95%99%E5%AD%A6%E8%B4%A8%E9%87%8F%E6%8A%A5%E5%91%8A.pdf` | Official PDF downloaded and 5 indicators extracted. |
| 安徽师范大学 | `https://xxgk.ahnu.edu.cn/info/1039/6791.htm` | Official page opens, but PDF attachment download requires verification code. |
| 陕西师范大学 | `https://jwc.snnu.edu.cn/info/1613/28904.htm` | Official page opens, but PDF attachment download requires verification code. |
| 天津职业技术师范大学 | `https://www.tute.edu.cn/info/1054/13814.htm` | Official page opens, but PDF attachment download requires verification code and fingerprint script. |
| 哈尔滨工业大学 | `https://hituc.hit.edu.cn/2025/0319/c20004a364562/page.htm` | Local official fetch returns invalid article-parameter error page. |
| 杭州电子科技大学 | `https://xxgk.hdu.edu.cn/_upload/article/files/dc/19/3ce49da947cc96e56028f9a968c2/fd69d44c-1e20-49dd-af27-38e524d25b8b.pdf` | Official candidate PDF returns HTTP 403. |
| 江苏师范大学 | `http://www.jsnu.edu.cn/_upload/article/files/da/78/1ba9aa7141ac9e95addcc86c6cf2/24225062-cd3b-4d33-b4c1-7392b9544551.pdf` | Official candidate PDF returns HTTP 404. |
| 浙江师范大学 | `https://xxgk.zjnu.edu.cn/_upload/article/files/2e/22/511e84bf41bba6f6e99ba716c775/a7809c10-9324-4300-8a53-5468c35612d9.pdf` | Official candidate PDF returns HTTP 404. |
| 北京交通大学 | `https://www.bjtu.edu.cn/docs/2024-12/89565391005f434c98ccf577d877ac9f.pdf` | Official PDF downloaded and 6 further-study indicators extracted. |
| 天津科技大学 | `https://jy.tust.edu.cn/Uploads/file/20231225/1703488272164016.pdf` | Official PDF downloaded and 9 destination/further-study indicators extracted. |
| 河北科技大学 | `https://gaojs.web.hebust.edu.cn/docs//2024-12/0765ffabc8ff4dcb9c4b29e0eb173d19.pdf` | Official PDF downloaded and 6 employment/further-study indicators extracted. |
| 天津科技大学 | `https://xxgk.tust.edu.cn/docs/2024-12/ac881bf8148c42f4b9abbb6b50da3951.pdf` | Official PDF downloaded and 7 undergraduate employment/further-study indicators extracted. |
| 北京理工大学 | `https://xxgk.bit.edu.cn/docs/2024-12/cbdbc5da18604d5496444fa909061351.pdf` | Official PDF downloaded and 4 further-study indicators extracted. |
| 北京科技大学 | `https://xxgk.ustb.edu.cn/attach/file/xinxigongkaimulu/jiaoxuezhiliang/benkejiaoxue/2024-12-05/1c217c649caaf1920249462747783058.pdf` | Official PDF downloaded and 7 undergraduate destination/further-study indicators extracted. |
| 北京师范大学 | `https://xxgk.bnu.edu.cn/docs/2024-10/4ded41d493374a3786e2a423e2e64301.pdf` | Official PDF downloaded and 6 destination implementation indicators extracted. |
| 对外经济贸易大学 | `https://xxgk.uibe.edu.cn/docs/2025-01/2e4e63533af44568b63901b3ef6924ef.pdf` | Official PDF downloaded; retained as source-only because no school-level destination/further-study metric was found. |
| 北京邮电大学 | `https://xxgk.bupt.edu.cn/info/1043/4055.htm` | Official information page returned a JavaScript challenge shell; no PDF was downloaded. |
| 北京工业大学 | `https://xxgk.bjut.edu.cn/info/1081/2090.htm` | Official page opens, but the attachment download bridge requires a verification code. |
| 东北电力大学 | `https://jwc.neepu.edu.cn/__local/E/40/D5/0C4EA9CFE8E9A27C7590AE4D99A_BCD746F5_210F96.pdf` | Official PDF downloaded and 10 undergraduate destination/further-study indicators extracted. |
| 南京财经大学 | `https://jwc.nufe.edu.cn/info/1026/17607.htm` | Official page opens, but the attachment download bridge returns HTML rather than a PDF. |
| 云南民族大学 | `https://www.ymu.edu.cn/__local/0/9F/9E/0F2CC30655799025ADF6D9D35EB_CE351191_196BEB.pdf` | Official candidate PDF URL returned HTTP 521/WAF HTML, not a PDF. |
| 中国医科大学 | `https://www.cmu.edu.cn/__local/C/1D/E1/AC88BE4F18774C3F05D19DF7273_0B2A1A8C_89672.pdf` | Official PDF downloaded and 5 undergraduate employment/further-study indicators extracted. |
| 南京财经大学 | `https://yjsc.nufe.edu.cn/__local/F/36/37/1B7A4D3A677114FB89D7953082B_1BB725DA_E9954.pdf` | Official PDF downloaded and 7 postgraduate employment/further-study indicators extracted. |
| 大连海洋大学 | `https://xxgk.dlou.edu.cn/_upload/article/files/fe/8a/99654027428bb853f857fe721d43/757bbef2-d8ec-4db8-8d2a-c39ffccd4f9a.pdf` | Official PDF downloaded and 13 undergraduate employment/further-study indicators extracted. |
| 成都体育学院 | `https://jxzlpgzx.cdsu.edu.cn/info/1119/2898.htm` | Official teaching-quality center page returned Safeline human-verification HTML. |
| 成都体育学院 | `https://jxzlpgzx.cdsu.edu.cn/info/1125/2788.htm` | Official 2022-2023 teaching-quality page returned Safeline `WEB 应用防火墙` HTML; no report body or PDF retrieved. |
| 成都体育学院 | `https://jxzlpgzx.cdsu.edu.cn/__local/8/99/8E/50422AC9389EB21E42E759D6891_D1062E2B_5C7C6.pdf?e=.pdf` | Official 2017-2018 teaching-quality PDF candidate returned Safeline `WEB 应用防火墙` HTML; no report PDF retrieved. |
| 成都体育学院 | `https://jxzlpgzx.cdsu.edu.cn/__local/D/D6/4D/4EC9148A9A68BB280D09B7F5C6C_70D2EAC2_AB2F0.pdf?e=.pdf` | 2026-06-03 live retest returned HTTP 200 Safeline bot-challenge HTML with `safeline_bot_challenge`; local artifacts `tmp/cdsu_2020_quality_pdf_retest_current.pdf` and `.headers.txt` show the body is not a PDF. |
| 成都体育学院 | `https://www.sport.gov.cn/n20001280/n20745751/c25688138/content.html` | National Sports Administration page, reposted from 中国体育报, quotes 成都体育学院《2022年毕业生就业质量报告》 and exposes 2 school-report indicators: 2022 graduate count 2804 and sports-industry employment-field share 61.92%. Because this is a government page quoting the school report rather than the school report body itself, the extracted metric quality is marked `medium`. |
| 云南民族大学 | `https://www.ymu.edu.cn/info/1161/68811.htm` | Official page returned HTTP 521/WAF HTML. |
| 西藏农牧大学 | `http://www.xza.edu.cn/xww/info/1121/147561.htm` | Official teaching-quality report candidate page reset the connection on repeated live requests; no report body or PDF was retrieved. |
| 西藏农牧大学 | `http://www.xza.edu.cn/xww/info/1121/147561.htm` | 2026-06-03 live retest again reset the connection (`curl: (56) Recv failure: Connection was reset`); only zero-byte header artifact `tmp/xza_2023_2024_quality_retest_current.headers.txt` exists and no body file was produced. |
| 西藏农牧大学 | `http://www.xza.edu.cn/xww/info/1121/75221.htm` and `http://www.xza.edu.cn/news/News_View.asp?NewsID=7192` | Additional official 2022-2023 and old 2021-2022 teaching-quality page candidates reset the connection on live requests. |
| 云南民族大学 | `https://www.ymu.edu.cn/__local/A/A1/AA/90F5868660743B27277806117B4_73FFDA0B_22C94C.pdf` | Alternate official PDF candidate is web-visible as official PDF text and 24 undergraduate graduation, degree-award, further-study, employment-channel, enterprise-share, and employer-satisfaction indicators were extracted; local curl still returned HTTP 521/WAF HTML, so the source is marked `official_pdf_web_visible`. |
| 中国政法大学 | `https://xxgk.cupl.edu.cn/system/_content/download.jsp?owner=1748948722&urltype=news.DownloadAttachUrl&wbfileid=7596037` | Official attachment download entry returned a JavaScript challenge page; no PDF was downloaded. |
| 中国政法大学 | `https://xxgk.cupl.edu.cn/__local/6/A3/74/B097FE57D1582EB8CB877E6F1FB_FFFAF046_162257.pdf?e=.pdf` | Official 2022 graduate-education quality report PDF candidate returned HTTP 403 / 96-byte HTML, not a PDF. |
| 中国政法大学 | `https://news.cupl.edu.cn/info/1011/1047.htm` | Official 2015 employment/further-study news page candidate returned a dynamic JavaScript challenge shell on local current fetch; no metrics ingested. |
| 中国政法大学 | `https://xxgk.cupl.edu.cn/info/1064/2494.htm` | Official information-disclosure page body is web-visible and 14 cohort employment/further-study indicators were extracted; local curl returned a `dynamic_challenge` shell, so no local report artifact is stored. |
| 宁波诺丁汉大学 | `https://www.nottingham.edu.cn/en/careers/documents/202425/2025-annual-report.pdf` | Official 2024-2025 careers and employability annual report PDF downloaded; 62 cohort scale, bachelor/master/PhD employment, further-study, industry, employer-type, and regional indicators extracted. |
| 重庆邮电大学 | `https://job.cqupt.edu.cn/attached/file/2021-01-21/1611215082117%E9%87%8D%E5%BA%86%E9%82%AE%E7%94%B5%E5%A4%A7%E5%AD%A62020%E5%B1%8A%E6%AF%95%E4%B8%9A%E7%94%9F%E5%B0%B1%E4%B8%9A%E8%B4%A8%E9%87%8F%E5%B9%B4%E5%BA%A6%E6%8A%A5%E5%91%8A.pdf` | Official employment-system attachment redirected to the off-campus VPN-required blocker page, not a PDF. |
| 重庆邮电大学 | `https://job.cqupt.edu.cn/portal/home/bulletin-info-detail.html?id=864&menuId=10` | Official employment-system report page redirected to the off-campus VPN-required blocker page. |
| 重庆邮电大学 | `https://xxgk.cqupt.edu.cn/info/1013/3012.htm` | More precise official 2023-2024 undergraduate teaching-quality report candidate returns HTTP 412 JavaScript challenge HTML. Local artifacts: `tmp/employment_cqupt_2023_2024_teaching_quality_3012_current.html`; `tmp/employment_cqupt_2023_2024_teaching_quality_3012_current.headers.txt`. |
| 重庆邮电大学 | `https://www.cqupt.edu.cn/__local/6/77/35/030BC5BB3EB8D927D67ABDA31ED_023C1745_1C0152.pdf?e=.pdf` | Official 2016-2017 undergraduate teaching quality report PDF downloaded; 6 graduation, degree-award, employment-rate, and employer-satisfaction indicators extracted. |
| 清华大学 | `https://www.tsinghua.edu.cn/__local/C/9B/FD/BA078DEA9FD003289CCF5BADF97_A846EFE9_88225.pdf` | Official undergraduate teaching quality report PDF downloaded; retained as source-only because it did not disclose directly comparable graduate destination or further-study rates. |
| 清华大学 | `https://career.tsinghua.edu.cn/__local/5/C6/80/089CE0AFE8A783B297D52B3EABF_65C0671C_3817C.pdf` | Official career center PDF downloaded; retained as source-only because it is an employment-work award notice with qualitative wording. |
| 北京航空航天大学 | `https://jiaowu.buaa.edu.cn/info/1125/4991.htm` | Official page returned a campus-network-only access message. |
| 北京外国语大学 | `https://xxgk.bfsu.edu.cn/info/1097/1894.htm` | Official page opened, but the PDF attachment download bridge required a verification code. |
| 北京语言大学 | `https://www.blcu.edu.cn/info/2812/20413.htm` | Official page opened, but the PDF attachment download bridge required a verification code. |
| 南京大学 | `https://xxgk.nju.edu.cn/_upload/article/files/14/01/54cc170c4271b5c86a2c3067ed50/3ca04149-cc15-41e2-ab5d-78e627f397ba.pdf` | Official PDF downloaded and 16 undergraduate further-study, region, industry, and employer-satisfaction indicators extracted. |
| 中山大学 | `https://xxgk.sysu.edu.cn/sites/default/files/2025-10/%E4%B8%AD%E5%B1%B1%E5%A4%A7%E5%AD%A62023-2024%E5%AD%A6%E5%B9%B4%E6%9C%AC%E7%A7%91%E6%95%99%E5%AD%A6%E8%B4%A8%E9%87%8F%E6%8A%A5%E5%91%8A.pdf` | Official PDF downloaded and 6 undergraduate graduation, degree-award, and grassroots employment indicators extracted. |
| 华中科技大学 | `https://ugs.hust.edu.cn/info/1131/6627.htm` | Official page opened, but the PDF attachment download bridge required a verification code. |
| 西南大学 | `https://xxgk.swu.edu.cn/info/1133/4628.htm` | Official page opened, but the PDF attachment download bridge required a verification code. |
| 中国地质大学（武汉） | `https://xxgk.cug.edu.cn/info/1056/2549.htm` | Official page opened, but the PDF attachment download bridge required a verification code. |
| 华侨大学 | `https://xwgk.hqu.edu.cn/info/1015/13567.htm` | Official page opened, but the PDF attachment download bridge required a verification code. |
| 南开大学 | `https://xxgk.nankai.edu.cn/_upload/article/files/72/86/d52599154097941e454e84873ee7/3d123c16-13a5-47ee-b2d1-6d2679584a28.pdf` | Official PDF candidate returned HTTP 404 HTML, not a PDF. |
| 上海交通大学 | `https://gk.sjtu.edu.cn/Assets/userfiles/sys_eb538c1c-65ff-4e82-8e6a-a1ef01127fed/files/20251106/20251106103243184.pdf` | Official PDF downloaded, but the file captured only pages 4-6 of the report and did not include the graduate destination chapter; retained as source-only. |
| 新疆大学 | `https://xxgk.xju.edu.cn/__local/9/71/85/352DA3892EB0E277695B93E2E32_B82179C5_18B803.pdf` | Official PDF downloaded and 16 undergraduate graduation, degree-award, destination implementation, further-study, employment-unit, and employer-satisfaction indicators extracted. |
| 北京化工大学 | `https://xxgk.buct.edu.cn/_upload/article/files/a1/19/d4b9d6b142f8a8fd0b67d95d2700/b41e218f-91b3-47fb-9bae-1af858a5eb20.pdf` | Official PDF downloaded and 30 undergraduate graduation, degree-award, destination, further-study, employment-unit, and employer-satisfaction indicators extracted. |
| 中国传媒大学 | `https://xxgk.cuc.edu.cn/_upload/article/files/c2/31/79006e624554992cf8c080ae40ab/d21b0e01-caa3-44f5-a6bc-454c05c871fd.pdf` | Official PDF downloaded and 16 undergraduate graduation, degree-award, further-study, recommendation-exemption, and destination implementation indicators extracted. |
| 北京中医药大学 | `https://jxw.bucm.edu.cn/docs/2024-12/197749f9fd6e4bd690018b760290fcb9.pdf` | Official candidate PDF timed out in both sandbox and authorized live requests; no PDF was downloaded. |
| 中央财经大学 | `https://op.cufe.edu.cn/info/1149/15050.htm` | Official candidate page returned HTTP 403 HTML; no metrics ingested. |

## Remaining Source Blockers

西藏农牧大学 still lacks any `metrics_extracted` official employment/further-study report body or attachment in this pass. 成都体育学院 now has 2 medium-confidence indicators from a National Sports Administration page quoting the school 2022 graduate employment-quality report, but the school-hosted report pages/PDFs themselves still return Safeline challenge HTML.

中国政法大学 now has school-level 2018 cohort metrics from a web-visible official information-disclosure page, but its local current fetches for several report/body/attachment candidates still return JavaScript challenge or HTTP-blocker responses. Those blocker rows are retained for provenance.

Observed blocker types include Safeline/WAF bot challenge, JavaScript challenge, HTTP 403/404/412/521, connection reset, VPN-required access, missing official report URL, or source pages that are only news/announcement context rather than structured employment report material.

Additional follow-up candidates with crawl blockers: 北京邮电大学 (JavaScript challenge shell), 北京工业大学 (verification-code attachment download bridge), 南京财经大学 undergraduate report page (attachment bridge HTML; postgraduate report PDF was crawlable), 西藏农牧大学 (connection reset), 云南民族大学 local live fetches (HTTP 521/WAF HTML; one official PDF is now web-visible and metrics_extracted), 中国政法大学 current attachment/PDF candidates (JavaScript challenge / HTTP blocker), 重庆邮电大学 (VPN-required access), 成都体育学院 (Safeline challenge), 北京中医药大学 (connection timeout), 中央财经大学 (HTTP 403).

## Validation

Fresh validation on 2026-06-03:

- B-class official row-level recommendation/admission coverage is 418 / 430 schools after the Northeast Electric Power University, Beijing Forestry University, and China University of Political Science and Law follow-up rows were ingested.
- Employment/further-study source table has 74 rows.
- Employment/further-study metric table has 326 rows across 26 schools/sources.
- 中国政法大学 contributes 14 high-confidence 2018 cohort school-level indicators from `https://xxgk.cupl.edu.cn/info/1064/2494.htm`; local curl for the same page returns only `dynamic_challenge`, so the source row is marked `official_page_web_visible`.
- 云南民族大学 contributes 24 high-confidence 2023-2024 undergraduate graduation, degree-award, further-study, employment-channel, enterprise-share, and employer-satisfaction indicators from the official PDF `https://www.ymu.edu.cn/__local/A/A1/AA/90F5868660743B27277806117B4_73FFDA0B_22C94C.pdf`; local curl for the same PDF returns HTTP 521/WAF HTML, so the source row is marked `official_pdf_web_visible`.
- 宁波诺丁汉大学 contributes 62 high-confidence 2025 cohort indicators from the official careers PDF; the PDF was downloaded as `application/pdf` and retained under `data/raw/official_employment_report_20260603_unnc_2025_careers/`.
- Workbook package includes `Undergrad_Source_Outcomes`, `Recommendation_Source_Attempts`, `Employment_Report_Sources`, and `Employment_Metrics`; row counts match the cleaned CSV files.
