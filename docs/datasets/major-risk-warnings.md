# Major Risk Warning Dataset

This dataset collects publicly fetchable employment-warning and
professional-setting risk data for Chinese college majors. The primary scope is
MyCOS/employment-blue-book style red/yellow/green major warnings, plus official
professional-setting controls such as warning lists, stop-enrollment notices,
and Ministry of Education cancellation filings.

## Build

```powershell
python scripts/crawlers/major_risk_warning_crawler.py
# Rebuild processed tables from existing raw/source cache without network fetches:
python scripts/crawlers/major_risk_warning_crawler.py --skip-fetch
```

The build fetches source pages/PDFs into `data/raw/major_risk_warnings/` and
writes structured outputs into `data/processed/major_risk_warnings/`.

## Current Build Snapshot

The current build contains 570 red/yellow/green employment-warning records,
1,314 numeric and school-level metrics, 9,151 official policy warning records,
458 source entries, and 953 referenced raw/text/image files. The latest incremental
sources added in this pass supply 2026 undergraduate/high-vocational green
majors, the previously missing 2019 undergraduate yellow-list majors,
additional official university professional-adjustment notices, Zhejiang A&F
University's 2025 official cancellation PDF, and direct Education Online /
Gaokaozhitongche secondary summaries for 2025 university-level adjustments.
The newest source-audit pass replaces the blocked Scribd source for the 2024
undergraduate yellow-list majors with a fetchable China.com education page and
structures four 2010-2024 cumulative yellow-warning count metrics. It also
splits the 2012 higher-vocational yellow-list archive abbreviations from broad
category labels, reducing low-confidence employment-warning records to two
category-only rows (`建筑类`, `水利类`) that cannot be reliably mapped to a single
current specialty code.
The newest 2026 employment-quality pass structures 15 additional metrics from
the already archived Sina/MyCOS 2026 green-major source, covering 2025-cohort
undergraduate average monthly income, survey sample size, covered major,
occupation, and industry counts, top industry employment shares, and
2021-to-2025 manufacturing-industry share changes.
The newest higher-vocational official pass adds the Education Ministry's 2026
higher-vocational specialty setup results notice and national controlled
specialty approval PDF. It contributes eight high-confidence metrics covering
69,414 proposed enrolling specialty points, 12 controlled-specialty
applications, eight approvals, and four rejections, plus 12 row-level official
policy records for approved or rejected controlled specialty points such as
early education, preschool education, specialized correctional education, and
offender psychological measurement and correction technology.
A separate full-register support dataset now preserves the Ministry government
service platform's high-vocational specialty registration query results for
2013-2026. It covers 814,328 official specialty-point rows across 14 years and
32 province-level regions, with 69,414 rows in 2026. The enhanced table adds
unique row IDs, API duplicate flags, and links to this dataset's high-vocational
red/yellow/green employment warnings and official policy warning rows. Its
professional-level summary contains 2,737 cross-year major-code/name pairs, of
which 121 can be linked to red/yellow high-vocational employment warnings and
196 can be linked to official high-vocational policy warning records.
A separate undergraduate official-event support dataset now cleans the Ministry
undergraduate catalog / filing-approval candidate crawl. It keeps 33,173 valid
undergraduate official events from 33,981 extracted candidate rows, covering
2012 catalog baseline rows, 2013-2024 annual filing/approval results, and the
2026 undergraduate catalog. The enhanced event table links these official
setting events back to this dataset's undergraduate employment-warning and
official policy-warning rows. Its major-level summary contains 1,081
major-code/name pairs, of which 67 link to red/yellow undergraduate employment
warnings and 627 link to official undergraduate policy warning records. The
manifest also retains 808 rejected table-header / non-standard-code rows and
109 school-level filing rows where OCR text no longer exposes a reliable school
name.
A broader official catalog and policy-evidence support package is also included.
The official catalog crawl contributes 1,530 catalog records from the 2021
vocational education catalog and 2022 graduate education catalog, covering
secondary vocational, higher-vocational associate, vocational undergraduate,
and graduate layers. The policy-evidence crawl contributes 17 national policy
documents and 1,019 direction-level evidence paragraphs for artificial
intelligence, advanced manufacturing, low-altitude economy, commercial space,
bio-manufacturing, quantum technology, integrated circuits, digital economy,
green low-carbon, new materials, and future industries.
A separate new-quality-productivity major support dataset adds a positive
policy-support dimension. It packages 2,053 local major evaluation rows, 8,212
school-tier sample rows, and 33 official policy source rows, then links each
major back to employment warnings, official professional-setting risk rows, AI
replacement risk, rysxai market observations, civil-service opportunities, and
transfer-policy mentions. It classifies 263 majors as core new-quality
directions, 400 as related, 470 as weak-related, and 920 as not-related.
A separate AI replacement-risk support dataset adds a non-official market-risk
dimension. It uses 1,616 rysxai Chinese recruiting-market snapshots and a
transparent heuristic scoring model to produce 1,612 major-level AI replacement
risk profiles, 65,473 major-job candidate rows, and 18,248 normalized job-risk
seed rows. This source is marked `source_level=C`; it is useful for ranking,
sampling, and downstream review, but it must not be read as an official
employment warning or deterministic prediction.
A separate rysxai market-observation support dataset exposes those third-party
market snapshots directly as analysis-ready tables. It structures 1,616 local
market snapshots into 1,616 major market profiles, 6,814 safe recruiting job
samples, 6,459 city salary aggregates, 39,659 macro distribution rows, 33,414
demand/salary ranking rows, 28,492 skill summary rows, and 214 group
summaries. It links 84 profiles back to red/yellow employment warnings, 564 to
official policy rows, 238 to medium-or-higher AI replacement risk, 1,090 to
civil-service opportunity rows, and 806 to transfer-policy mentions.
A separate rysxai civil-service opportunity support dataset adds a
source-level C public-exam fit dimension. It parses 20,714 crawled 2026
civil-service role rows into 20,714 role parse rows, 888,025 role-major bridge
rows, and 1,653 major opportunity profiles. Of the local major seed rows,
1,110 have at least one matched civil-service role. The table keeps exact
six-digit-code/name matches separate from broad class or prefix matches, and
links 83 matched majors back to red/yellow employment warnings, 560 to official
policy rows, and 1,613 to AI replacement-risk rows.
A separate major risk master-index dataset now joins the professional-level
signals into a single wide screening table. It contains 4,028 major rows across
undergraduate and associate/higher-vocational levels, with 657 rows in the
`high_risk_review` bucket, 945 rows linked to official professional-setting
policy warnings, 174 linked to red/yellow employment warnings, 45 carrying a
high AI-replacement signal, and 1,133 carrying new-quality-productivity support
signals. The table preserves source flags and source-level mix so official
records, public warning summaries, and third-party market signals remain
separable.
A separate major risk evidence-profile dataset now adds the long-form
traceability layer behind that master index. It contributes 20,664 evidence
records and 4,028 per-major evidence summaries, including 9,143 official policy
warning rows, 570 employment-warning rows, and derived AI, market,
civil-service, new-quality, emerging-major, and vocational-register evidence
rows. Where source IDs are available, the evidence table resolves source
titles, URLs, publishers, and raw/text paths.
A separate major risk review-release dataset now turns the master index and
evidence layer into direct analyst tables. It contributes 2,267 high-risk /
risk-watch shortlist rows, with 657 in `tier_1_high_risk_review`, and a unified
4,428-row source-document index containing 3,660 public/source URL rows, 764
local raw/text path rows, and four local derived-profile source rows. The source
index records local path availability for all 4,428 rows, including the four
derived-profile rows now resolved to processed profile tables; no URL row or
local-profile row remains without a local path. The review release resolves
3,232 RYSXAI API URL rows back to existing local raw JSON archives and joins a
separate source-archive dataset for the remaining public URLs.
A separate major risk source-archive dataset now captures the review-release URL
gap. It archives 161 unique public source URLs covering 166 source-index rows,
with 161 successful/cached raw downloads and 161 text/metadata files. The raw
archive includes Ministry, NDRC, school information-disclosure pages, news
mirrors, PDF, DOC, XLS, image, and download-handler sources. Binary fallbacks
extract legacy Office strings, ZIP member text, image metadata, and scanned-PDF
metadata when full text is not machine-readable.
A separate source-content index now turns those archived text/metadata files
into searchable evidence tables. It contributes 161 document rows, 5,076
keyword-snippet rows, and 32 keyword-summary rows. The snippet layer preserves
keyword groups for risk adjustment (865 rows), official policy language (2,267),
employment signals (858), and opportunity signals (1,086), making it easier to
audit source lines that mention cancellation, stopped enrollment, red/yellow
cards, professional-setting approvals, employment terms, or policy-supported
emerging directions.
A separate rysxai transfer-policy profile support dataset adds a source-level C
major mobility dimension. It structures 2,948 school transfer-major policy rows
into 2,948 school profiles, 2,386 faculty-policy profiles, 1,653 major-mention
profiles, and 55 group summaries. It extracts transparent keyword flags for
GPA/ranking requirements, written tests, interviews, quota limits, special
enrollment restrictions, physical-condition restrictions, and open-transfer
signals, then assigns a heuristic difficulty level for screening. It links 76
mentioned majors back to red/yellow employment warnings, 468 to official
policy rows, and 805 to AI replacement-risk rows.
A separate rysxai major-introduction support dataset adds source-level C text
profiles for 1,653 majors. It keeps major introduction, course, graduate-study
transition, similar-major, selection-advice, enrollment-scale, and university
count fields, then links each profile back to employment warnings, official
policy risk rows, and AI replacement-risk scores. It contributes 147 profiles
linked to employment-warning rows, 84 profiles linked to red/yellow employment
warnings, 564 profiles linked to official policy risk rows, and 1,613 profiles
linked to AI replacement-risk profiles.
A separate graduate-outcome support dataset aggregates 285,608 public masked
official-source recommendation/admission records into 4,534 major-flow rows.
It keeps undergraduate-major and admission-major roles separate, normalizes
leading programme codes for matching, and links flows back to this dataset's
employment-warning, official-policy, and AI-risk rows. It contributes 85
major-flow rows linked to red/yellow employment warnings, 424 linked to official
policy risk rows, and 493 linked to AI replacement-risk rows. These counts are
official-source outcome row counts, not employment rates.
A separate graduate-outcome school-year profile support dataset now combines
the same 285,608 public masked recommendation/admission records with 326
official employment or teaching-quality report metrics, 74 official report
source rows, 430 school-level coverage rows, and 15 source-attempt audit rows.
It produces 860 school-year profiles and 524 school summaries. These rows keep
public list sample counts separate from official rate fields, so downstream
analysis can compare observed official-source recommendation/admission samples
with report-backed employment, destination-implementation, further-study, and
overseas-study indicators without treating sample counts as true rates.
The newest Ministry-level catalog pass adds the Education Ministry's 2026
undergraduate catalog notice, official PDF, and release news. It contributes
10 high-confidence aggregate metrics: the 2026 catalog's 13 disciplines, 92
major categories, 883 majors, 15 cross-discipline catalog majors, four newly
listed cross-discipline majors, 9 schools adding embodied intelligence, 1.02万
new undergraduate major points during the 14th Five-Year Plan period, and 1.22万
cancelled-or-stopped undergraduate major points in the same period. The latter
is retained as a combined exit metric because the source does not split
cancellation and stop-enrollment counts.
The latest Ministry-level metric pass adds two Education Ministry government
service platform pages for the 2024 undergraduate professional-setting results.
It contributes 18 high-confidence national/provincial aggregate metrics,
including 1,839 new major points, 157 degree/duration adjustment points, 2,220
stopped major points, 1,428 cancelled major points, 6.28万个 current national
undergraduate major points, 845 catalog majors, 29 newly added catalog majors,
and regional matching pilot indicators for Heilongjiang, Zhejiang, Henan, and
Shaanxi.
The latest official teaching-quality-report pass adds West China Normal
University, Fujian Normal University, and Jiangsu Normal University's
2023-2024 official PDFs. These sources contribute 16 school-level
professional-setting/adjustment metrics and four high-confidence Fujian Normal
University stop-enrollment rows for hotel management, animation, environmental
science, and composite materials and engineering. West China Normal
University's report gives only the count of five recently cancelled
"double-low" majors, so that evidence is retained as a metric rather than
invented row-level names.
The newest official-page increment adds Tibet University's 2025 undergraduate
professional-setting adjustment notice, contributing four high-confidence
proposed-cancellation rows and three school-level adjustment metrics. It also
adds Changchun University of Electronic Science and Technology's 2023 proposed
cancellation notice, upgrading two existing Ministry cancellation rows with
school-level evidence and adding two related metrics.
It further adds Jilin Engineering Normal University's 2023 proposed-cancellation
notice, upgrading the existing Ministry cancellation row for administrative
management with school-level evidence and one related metric.
The newest Beijing Jiaotong University pass adds the 2025 undergraduate
professional-setting adjustment notice and its official application-materials
zip. The zip's decoded directory exposes six application-to-cancel materials,
adding six high-confidence cancellation rows for majors that were previously
only represented as 2025 stop-enrollment rows, plus one school-level metric.
A further information-disclosure pass adds Shanghai Jiao Tong University's
2020-2024 annual professional-setting and stop-enrollment pages, contributing
six high-confidence stop-enrollment rows and 20 school-level annual metrics.
It also adds Northeast Normal University's official 2025 notice page as
source-linkage evidence for the existing medium-confidence cancellation rows,
and Zhejiang University of Finance & Economics' official training-system news
as a school-level source for recent cancellation, stop-enrollment, new-major,
and application/pre-application counts.
The newest Zhejiang University of Finance & Economics pass adds the official
2023-2024 undergraduate teaching quality report PDF. It contributes six
professional-setting/admission metrics and one high-confidence official
warning-list row: asset appraisal is listed in the university's dynamic
professional-adjustment warning list.
The newest Northeast Normal University pass adds the official 2023-2024
undergraduate teaching quality report PDF, contributing nine high-confidence
2024 cancellation rows for named majors that had been stopped for at least
five years, plus six school-level professional-setting and adjustment metrics.
The report states ten cancellations, but only nine major names are visible in
the extracted text/page image; the dataset structures only the visible names
and keeps the count as a separate metric.
The newest official-source expansion adds university information-disclosure
tables/PDFs for 2025 stop-enrollment majors from Shanghai Business School,
South China Normal University, Shanghai University of Finance and Economics,
Jilin University, Beijing Jiaotong University, Jinan University, Nanjing Tech
University, Wuhan Institute of Technology, Jiangsu University, Guangdong
University of Finance and Economics, Northeast Forestry University, and Wuhan
Polytechnic University, plus newly verified official pages/attachments from
Hubei University of Automotive Technology, Xi'an Eurasia University, and
Central South University. Follow-up official-source passes also added Jiangxi
Normal University, Jinggangshan University, Ningbo University, Chongqing Normal
University, and Quanzhou University of Information Engineering 2025
undergraduate cancellation/adjustment notices, reducing the 2025 secondary-only
school-level rows. The latest secondary-source enrichment added crawlable
Hualong/CQNews and Tencent/Zhangshang Gaokao mirrors for 2025 university-level
adjustments, strengthening the evidence chain for Chengdu University of
Information Technology, Fujian Normal University, China West Normal University,
Ma'anshan University, Hefei Normal University, and Sichuan Fine Arts Institute.
The newest Chengdu University of Information Technology pass adds its official
2023-2024 undergraduate teaching quality report PDF. It contributes seven
school-level professional-setting and professional-adjustment metrics and two
high-confidence 2024 cancellation rows for materials physics and information
countermeasure technology.
A follow-up table-style secondary source from New Phase Education was also
added for 2025 adjustment lists, especially strengthening Changchun University
and Quanzhou University of Information Engineering rows still lacking complete
official-text lists. Additional targeted sources from Gaokao Information
Network, Gaokaozhitongche, and Tencent/Qingta further strengthen Chuxiong
Normal University and Shanghai Jiao Tong University rows; Chuxiong rows now
include source-table major codes, study durations, degree categories, and
college ownership. The newest expansion adds 2025 public notices and
summaries for additional university-level cancellations, including Chengdu
University of Technology, Jilin Agricultural University, Jiangsu Normal
University, Northeast Normal University, Kunming University of Science and
Technology, Northwest A&F University, Jinan University, Yangzhou University,
Shenyang Aerospace University, Qilu University of Technology, Xinyang Normal
University, Beijing University of Technology, and Shanghai Normal University
Tianhua College. Official high-confidence pages were added for Tangshan
University, Central South University of Forestry and Technology College,
Hebei University of Technology, and Shanghai Normal University Tianhua
College. A follow-up Gaokao Information Network mirror strengthens Beijing
University of Technology's 2025 four-major cancellation record. The same
follow-up pass corrected the 2025 Qilu University of Technology and Xinyang
Normal University rows against the fetched Acabridge source text. A further
source-linkage pass attached the fetched Youzy/Sichuan admissions guidance
summary to Shanghai Jiao Tong University and Fujian Normal University rows
where it explicitly lists the same 2025 cancellation majors.
The latest source-linkage pass further mined the fetched New Phase Education
topic page and attached `xmhbjy_2025_multi_university_cancellation` to 79
matching 2025 cancellation/stop-enrollment rows across 20 universities,
including Liaoning University, Guangxi University of Science and Technology,
Beijing Information Science & Technology University, Ningbo University,
Jiangxi Normal University, Nanyang Institute of Technology, Chengdu University
of Information Technology, Jianghan University, Quanzhou University of
Information Engineering, Gansu Agricultural University, and others.
The newest official-source additions are Guizhou Normal University's 2025
undergraduate major-setting notice and Shenyang Normal University's 2025 Word
attachment notice, adding eight high-confidence cancellation rows with
source-provided major codes.
The latest 2025 Ministry application-material pass adds Wuhan Wenli
University's AI Education application PDF, contributing six high-confidence
stop-enrollment rows and nine high-confidence cancellation rows from the
source's professional adjustment history section.
A subsequent Ministry application-material pass adds a second Wuhan Wenli
University PDF as corroborating evidence, Central Minzu University's directly
named Korean stop-enrollment row, Shanghai University of Sport's unadmitted
and stop/cancel professional-history rows, and Qiongtai Normal University's
2023-2025 continuous stop-enrollment records for Art Design.
The newest official application-material pass adds directly named
professional-history rows from Guizhou Medical University, Gannan Normal
University, Hubei Enshi College, Northwest University of Political Science and
Law, Sichuan Normal University, Tianjin University of Finance and Economics
Pearl River College, and Wuhan Sports University Sports Science and Technology
College.
The latest 2026 official-source pass adds Shanghai University of Electric
Power's professional-optimization meeting news, contributing three proposed
stop-enrollment rows and one proposed cancellation row.
The newest secondary-statistics pass adds People's Daily Client/Education
Online and Tencent News/Zhangshang Gaokao 2026 summaries of 70 undergraduate
institutions and 525 stop-enrollment major instances, plus embedded frequency
table images covering 40 visible frequently paused majors by school count.
The latest school-level evidence pass adds official 2024 cancellation pages
from Liaoning University and Cangzhou Jiaotong College, linking ten already
known Ministry cancellation rows back to their university notices.
A further official-source pass added Nanchang Institute of Science and
Technology's 2025 notice page plus the embedded cancellation-table image,
adding four high-confidence cancellation rows for majors stopped from
2020 through 2025.
The latest official-source pass added Wuhan College's 2025 cancellation notice
and Guizhou University of Finance and Economics' 2025 PDF notice, adding eight
more high-confidence rows with source-provided major codes, college ownership,
and degree categories where available.
It also added Hechi University's 2025 official cancellation notice, contributing
two high-confidence rows with source-provided codes, study duration, and degree
category.
The newest official-source increment adds Wanjiang University of Technology's
2025 notice, contributing three high-confidence cancellation rows and one
high-confidence stop-enrollment row with source-provided codes, degree
categories, and stop-enrollment start years.
A further official-source increment adds Liaoning Normal University, Shanxi
University of Electronic Science and Technology, and Guilin Institute of
Information Technology 2025 public notices, contributing ten high-confidence
cancellation rows backed by fetched school pages.
The latest crawl pass adds or upgrades 2025 official evidence from Longyan
University, Xinyang Normal University, Beijing University of Technology,
Northwest A&F University, Henan Agricultural University, Jiangxi Institute of
Fashion Technology, Liaoning Normal University Haihua College, and Guilin
College. It also parses Guilin College Word attachments, adding three
high-confidence cancellation rows and eight high-confidence stop-enrollment
rows.
The latest Shanghai/Zhejiang professional-setting pass adds official
information-disclosure or school pages from Shanghai Ocean University,
Shanghai Theatre Academy, Shanghai Lixin University of Accounting and Finance,
Tongji University, Anhui University of Chinese Medicine, University of Shanghai
for Science and Technology, and a crawlable Shanghai Electric Power University
page. It contributes new high-confidence
stop-enrollment/cancellation rows for these schools, keeps the Shanghai
Electric Power University and Zhejiang University of Finance & Economics lists
at medium confidence where only crawlable secondary text exposes the full
list, and fixes old Office binary suffix detection so the 2019/2020
machine-readable Ministry cancellation mirrors continue to parse correctly.
A follow-up official-source pass adds Chaohu University and Shenzhen
University information-disclosure attachments. Chaohu's 2025 PDF contributes
nine high-confidence current-year stop-enrollment rows with source-provided
codes, study duration, degree category, and college ownership. Shenzhen
University's 2025 Word attachment contributes 26 high-confidence stop-enrollment
status rows, preserving the source distinction between current-year stop
enrollment and prior-year stop-enrollment remarks.
Another official PDF pass adds Jiangnan University and China University of
Petroleum (East China) 2025 professional-setting files. Jiangnan contributes
two high-confidence rows, including a partial-class stop-enrollment note for
Chinese language and literature, while China University of Petroleum (East
China) contributes seven high-confidence stop-enrollment-with-current-students
rows.
The latest evidence-quality pass adds Shanghai Jiao Tong University's 2025
psychology application PDF as an official metric source for its near-five-year
professional adjustment counts, and corrects Shanghai University of Finance and
Economics' 2025 stop-enrollment list to include the previously omitted logistics
management row marked with a black-diamond stop-enrollment marker in the PDF.
The newest official-source pass adds Hubei University of Economics'
2023-2024 undergraduate teaching quality report PDF and Nanjing University of
Information Science & Technology's 2024/2025 stop-enrollment and 2024
cancellation list images, adding 25 high-confidence official policy rows and
three high-confidence school-level adjustment metrics.
A subsequent teaching-quality-report pass adds Wuhan University of Science and
Technology's 2023-2024 undergraduate teaching quality report and Longdong
College's 2023-2024 undergraduate teaching quality report. These sources add 43
net high-confidence stop-enrollment rows or source upgrades and eight
high-confidence school-level adjustment metrics, including WUST's 2024
stop-enrollment/cancellation counts and Longdong College's 2022-2024
non-enrollment, paused-enrollment, and cancellation counts.
The newest teaching-quality-report expansion adds six more official PDFs from
Dalian University of Technology, Shenyang Institute of Engineering, Huzhou
University, Shenyang Normal University, Nanjing Normal University Taizhou
College, and Sichuan Conservatory of Music. These reports add 29 net
high-confidence stop-enrollment or not-enrolled rows, upgrade 20 existing
Ministry cancellation rows with school-report evidence, and add 20
school-level professional-adjustment metrics.
A follow-up teaching-quality-report pass adds official PDFs from Hunan
Agricultural University, Zhejiang University of Science and Technology, Huaibei
Normal University, and Wenzhou University of Technology. It also mines the
already archived Sichuan Conservatory of Music report for its support-data stop
list. This pass adds 22 net high-confidence stop-enrollment rows, upgrades 15
existing Ministry cancellation rows with school-report evidence, and adds 18
school-level professional-adjustment metrics.
A further official-report pass adds Chizhou University's official report page,
Beijing Wuzi University's report PDF, and Xuchang University's report PDF. It
adds 12 net high-confidence stop-enrollment rows, upgrades seven existing
Ministry cancellation rows with school-report evidence, and adds ten
school-level professional-adjustment metrics.
A subsequent Shanghai official-report pass adds Shanghai Ocean University's and
Shanghai University's 2023-2024 undergraduate teaching-quality report PDFs. It
adds six net high-confidence stop-enrollment rows, upgrades Shanghai University's
2024 Packaging Engineering Ministry cancellation row with school-report
evidence, and adds six school-level professional-adjustment metrics.
Another official teaching-quality-report pass adds Inner Mongolia University of
Finance and Economics, Chongqing University of Arts and Sciences, Northeast
Petroleum University, and Chongqing University of Science and Technology. It
adds 15 high-confidence official warning rows or source upgrades from explicitly
named majors and 20 school-level professional-adjustment metrics while keeping
partial "and others" lists as count metrics only.
The next official-report pass adds Yichun University, Shandong University of
Aeronautics, University of Science and Technology Beijing, Guizhou University of
Finance and Economics, and Shanghai University of Engineering Science. It adds
19 net high-confidence official stop-enrollment rows, upgrades four existing
Ministry cancellation rows with school-report evidence, and adds 18
school-level professional-adjustment metrics; partial "and others" lists remain
as count metrics unless the report explicitly names the major.
A subsequent official Word-attachment pass adds Jingdezhen Ceramic University's
undergraduate major-setting table, contributing four high-confidence
stop-enrollment rows for 2021 and 2022 with source-provided major codes.
The latest official-source pass adds Jingdezhen Ceramic University's
2023-2024 academic-year major-setting status page and Chongqing Normal
University's 2022-2023 information-disclosure attachment. It contributes 14
additional high-confidence stop-enrollment status rows with source-provided
major codes, table row numbers, college ownership or degree categories where
available.
A follow-up Chongqing Normal University pass adds the 2023-2024 HTML
professional-setting table, contributing 10 more high-confidence annual
stop-enrollment status rows.
Another official-source pass adds Tsinghua University's 2023-2024
professional-setting page, contributing two high-confidence not-enrolling rows
for microelectromechanical systems engineering and advertising.
The same pass also adds University of Electronic Science and Technology of
China's historical professional-setting page, contributing one high-confidence
2017 stop-enrollment row for environmental engineering.
The latest official-source pass adds Huanggang Normal University's 2025 XLS
stop/cancellation list and 2022 HTML stop-enrollment table, contributing 15
high-confidence rows with source-provided college ownership, major codes,
degree categories, adjustment type, and historical stop-enrollment notes.
A follow-up official-source pass adds Beijing Normal University's
2024-2025 professional-setting information-disclosure index and PDF,
contributing nine high-confidence paused-enrollment rows with source-provided
major codes, study duration, and degree categories.
The latest official-source pass adds Central South University's 2025
undergraduate major-setting page and embedded PDF, contributing 15
high-confidence stop-enrollment rows with source-provided college ownership,
major codes, degree categories, and study duration.
A further official-source pass adds Hohhot Minzu College's 2024-2025
undergraduate teaching quality report PDF, contributing four high-confidence
2025 stop-enrollment rows whose report text also states the school applied to
cancel the same four majors.
A subsequent official-source pass adds Tianjin Foreign Studies University
Binhai School of Foreign Affairs' 2024-2025 undergraduate teaching quality
report HTML page, contributing five high-confidence 2025 stop-enrollment rows
for International Affairs and International Relations, Journalism,
E-commerce, Financial Management, and Advertising with source-provided major
codes.
A further official-source pass adds Shanxi University of Finance and
Economics' 2025 stop-enrollment table and Hubei Minzu University's 2021-2025
stop-enrollment information-disclosure pages. These sources contribute nine
additional high-confidence stop-enrollment rows, while the 2021 and 2023 Hubei
Minzu pages are archived as explicit no-stop-enrollment annual evidence.
A high-vocational official-source pass adds Xiangyang Polytechnic's
2021-2025 stop-enrollment PDF tables and archives its 2020 Print2Flash PDF.
The extractable 2021-2025 PDFs contribute 42 high-confidence higher-vocational
stop-enrollment rows with source-provided specialty codes and study durations;
the 2020 PDF is retained as raw evidence but not structured because text
extraction only exposes the Print2Flash watermark.
A further higher-vocational official-source pass adds Huizhou Economics and
Polytechnic College's 2024-2025 professional-setting information-disclosure
page and PDF. The PDF contributes 14 high-confidence stop-enrollment rows:
nine 2024 stop-enrollment specialties and five 2025 stop-enrollment
specialties, all with source-provided department ownership, specialty codes,
and study durations.
A subsequent higher-vocational official-source pass adds Guangdong Jiangmen
Chinese Medicine College's 2024-2025 professional-setting PDF. The source
contributes three high-confidence 2024 stop-enrollment rows for Elderly Care
and Management, Reproductive Health Management, and Respiratory Therapy
Technology; the PDF does not provide specialty codes, so codes in the
structured table come from the local professional catalog where matched.
A further higher-vocational official-source pass adds Xuzhou College of
Industrial Technology's information-disclosure pages and PDF/HTML tables for
2021, 2022, 2024, and 2025 stop-enrollment specialties. These sources
contribute 13 high-confidence rows with source-provided specialty codes and
source-table row numbers; 2019 remains unstructured because only a SWF
attachment was exposed in the public list.
A follow-up undergraduate official-source pass adds Wuhan University of
Science and Technology's 2023-2026 information-disclosure pages for stopped
undergraduate majors. The 2023 HTML table contributes seven high-confidence
stop-enrollment rows with source-provided college ownership, major codes,
study duration, and discipline; the 2024-2026 pages are archived as public
annual coverage pages because the fetched body does not list individual
stopped majors.
A further undergraduate official-source pass adds Wuchang Shouyi University's
2018-2025 information-disclosure pages for stopped undergraduate majors. The
2019, 2020, 2021, 2023, 2024, and 2025 HTML tables contribute 56
high-confidence rows preserving internal major names, standard major names,
major codes, school ownership, setup years, study duration, degree categories,
and current/prior stop-enrollment status. The 2018 and 2022 pages are retained
as explicit no-stop-enrollment annual coverage evidence.
A subsequent historical official-source pass adds Jinan University's 2018-2024
professional-setting pages, contributing 88 high-confidence stop-enrollment
rows parsed directly from the HTML remarks column with source row numbers,
major codes, specialty classes, duration, and degree categories. The existing
2025 Jinan University source remains the current-year row source and is not
duplicated by the historical parser.
The same pass adds East China Normal University's 2014-2023 professional-setting
pages. The 2023 table contributes 16 high-confidence paused-enrollment rows
with source row numbers and major codes; the 2014-2022 pages are archived as
coverage pages because their parsed tables did not expose paused-enrollment
remarks.
It also adds Beijing Normal University's 2022-2023 professional-setting PDF,
contributing 12 high-confidence paused-enrollment rows with source-provided
major codes, study duration, and degree categories.
A further historical official-source pass adds Nanjing Tech University's
2019-2024 undergraduate professional-setting pages. These HTML tables
contribute high-confidence stop-enrollment rows from remarks such as
`今年停招`, `2019年停招`, `2022年停招`, and `2024年停招`; repeated historical
rows across adjacent annual pages are merged with supplemental source IDs and
evidence text, yielding 32 net additional official policy rows.
A further Jiangsu University pass adds the school's 2020-2024 undergraduate
professional-setting pages and the 2020/2021 annual new-major/stop-enrollment
coverage pages. The parsed setting tables contribute 45 net additional
high-confidence rows from remarks or `是否停招` columns, while the 2020 and
2021 standalone list pages are retained as explicit no-new-or-stop annual
coverage evidence.
A further Shanghai University of Finance and Economics pass adds the school's
2014-2024 historical information-disclosure pages plus the 2025 notice page.
The parser extracts 93 additional high-confidence historical stop-enrollment
or no-enrollment rows from annual HTML table markers such as `◆`, `■`, `***`,
`****`, and remarks-column values `停招`/`未招生`; the 2025 structure remains
backed by the already parsed PDF attachment, and the duplicated 2017-2018
reference page is retained as raw source coverage without duplicate records.
The newest official-source increment adds Fudan University's 2023 and 2024
professional-setting/adjustment pages. These official pages contribute seven
high-confidence rows: three 2023 stopped undergraduate majors, three 2024
stopped undergraduate majors, and one 2024 stopped second-bachelor's-degree
project.
A further official-source increment adds Tongji University's 2020-2024
information-disclosure stop-enrollment pages, completing the visible 2020-2025
Tongji stop-enrollment run. The newly added 2020-2024 pages contribute 16
high-confidence undergraduate stop-enrollment rows; where the source provides
only internal specialty numbers, those values are retained in evidence text and
catalog codes are filled from the local professional catalog rather than copied
from the source.
A further official-source increment adds Huazhong University of Science and
Technology's 2016 and 2018-2025 professional-setting information-disclosure
pages. The 2018, 2019, 2020, 2021, and 2025 tables contribute 57
high-confidence rows from remarks such as `已停止招生`, `停止招生`, `暂停招生`,
and `暂未招生`; the 2016 and 2022-2024 pages are retained as coverage pages
because their parsed tables did not expose stop-enrollment remarks.
A further 2025 official-source upgrade adds Kunming University of Science and
Technology's school-level major-setting recommendation notice and Qilu
University of Technology (Shandong Academy of Sciences)' official cancellation
notice, and reclassifies the already archived Shenyang Aerospace University
notice after verifying that its HTML text exposes the full list. These sources
upgrade 13 school-level 2025 cancellation rows from medium to high confidence:
four for Kunming University of Science and Technology, six for Shenyang
Aerospace University, and three for Qilu University of Technology.
A subsequent evidence-quality pass upgrades East China Normal University's
2025 visible stop-enrollment list from medium to high confidence:
the official information-disclosure page states that 24 majors were stopped,
but its HTML body and meta description explicitly name 22 majors. The dataset
continues to structure only those 22 visible names and leaves the two unnamed
items unfilled rather than inferring them.
A further official-policy pass adds Shanghai Municipal Education Commission
Word attachments for the 2012, 2013, 2014, and 2016 undergraduate warning-major
notices. The crawler now converts legacy `.doc` files to text, verifies the
official lists, and adds or upgrades Shanghai warning rows: 18 official 2012
majors, 15 official 2013 majors, seven official 2014 majors, and ten official
2016 majors. Secondary rows from the CCTV/Xinhua summary that do not appear in
those official attachments remain at medium confidence for source-audit
visibility.
A further 2014 source-audit pass adds the China Education and Research Network
page for the Ministry of Education's national low-employment undergraduate
list and the Ministry of Education portal's Shanghai 2014 warning-major news
page. The `edu_cn_2014_low_employment_warning` source is attached to 105
national/first-ten-region low-employment rows where its text exposes the list,
and `moe_2014_shanghai_warning_news` is attached to the seven high-confidence
Shanghai 2014 official warning rows already verified from the Shanghai
Municipal Education Commission Word attachment.
A follow-up pagination audit adds the second China Education and Research
Network page for the 2014 Ministry of Education low-employment undergraduate
list. `edu_cn_2014_low_employment_warning_page2` is attached to 153
Zhejiang-through-Xinjiang Production and Construction Corps regional
low-employment rows; combined with page 1, 258 national/regional 2014
low-employment rows now carry a crawlable `edu.cn` source in addition to the
CCTV/Xinhua summary.
A subsequent source-detail pass adds the Ministry of Education Government
Service Platform JSON detail for the 2019 undergraduate professional-setting
notice. It is attached to all 367 medium-confidence 2019 cancellation rows as
official notice text confirming the 367 cancelled majors and linking the
official scanned PDF; the rows remain medium because row-level structure still
comes from a machine-readable XLS mirror rather than OCR of the official PDF.
An additional municipal official-source pass adds the Beijing Municipal
Education Commission Word attachment for 2019 municipal undergraduate
professional-setting results. Its撤销本科专业 table upgrades Beijing Film
Academy's Advertising and Public Service Administration cancellation rows to
high confidence, with official major codes, degree categories, study duration,
and source-table row numbers.
Another provincial official-source pass adds the Hunan Department of Education
2019 undergraduate enrollment-major catalog notice and its XLS attachment. The
notice states that majors marked `拟撤销` stop enrollment from 2019 and must be
formally submitted for cancellation in July 2019; the attachment provides 14
row-level `拟撤销` majors from University of South China, Jishou University, and
Hunan Institute of Science and Technology. These rows merge into the matching
2019 Ministry cancellation rows and upgrade them from medium to high
confidence while preserving the Ministry notice/PDF/XLS mirror sources.
A subsequent school official-source pass adds South China Normal University's
2018-2019 undergraduate teaching quality report PDF. Its professional-building
section states that the university applied to cancel seven majors: Mechanical
and Electronic Engineering, Industrial Design, Statistics, Economic Statistics,
Fashion and Apparel Design, Photography, and Film and Television Photography
and Production. These seven rows merge into the matching 2019 Ministry
cancellation records and are upgraded from medium to high confidence.
The same school-report pass adds Sichuan University of Science & Engineering's
2018-2019 undergraduate teaching quality report PDF. Its professional-building
section states that the university applied to cancel eight majors: Statistics,
Economic Statistics, Physics, Chemical Biology, Rail Transit Signal and
Control, Industrial Engineering, Social Work, and Information Management and
Information System. These rows merge into the matching 2019 Ministry
cancellation records and are upgraded from medium to high confidence.
A subsequent school-report pass adds Yunnan Normal University's 2018-2019
undergraduate teaching quality report PDF. Table 3 lists seven 2019 cancellation
applications with source-provided major codes and colleges: Applied Statistics,
Science Education, Tourism Management and Service Education, Marketing, Applied
Biological Science, Software Engineering, and Network Engineering. These seven
rows merge into the matching 2019 Ministry cancellation records and are upgraded
from medium to high confidence.
Another school-report pass adds Dezhou University's 2018-2019 undergraduate
teaching quality report PDF and Harbin University's 2019-2020 undergraduate
teaching quality report PDF. These reports contribute 12 high-confidence
stop-enrollment rows: five Dezhou 2019 stopped majors and seven Harbin 2020
same-year stopped majors. Harbin's report also explicitly states that the
school cancelled History, Psychology, Physical Education, Geography Science,
Fine Arts, and Biological Science in 2020; those six rows merge into the
matching 2019 Ministry cancellation records and are upgraded from medium to
high confidence. Dezhou's report is still structured as stop-enrollment evidence
only because it does not state cancellation.
A further official-source pass adds Changchun University of Science and
Technology's 2020 applied-statistics professional filing PDF. Its school
history section contributes three high-confidence stop-enrollment rows for
Economics, Materials Physics, and Network Engineering, and upgrades five
matching 2019 Ministry cancellation rows to high confidence for Industrial
Design, Environmental Science, Labor and Social Security, Fashion and Apparel
Design, and Rail Transit Signal and Control.
Another 2019 evidence-linkage pass adds an Our Jiangsu crawlable secondary
article sourced to the Ministry of Education website. It attaches text evidence
to 13 medium-confidence Jiangsu cancellation rows for Nanjing Tech University,
Nantong University, Communication University of China Nanguang College, and
Jiangsu Normal University Kewen College without changing those rows to high
confidence.
Another official information-disclosure pass adds Guangxi University of Science
and Technology's 2015-2016 undergraduate setting page, contributing 14
high-confidence stop-enrollment rows with major codes for Education Technology,
Materials Forming and Control Engineering, Management Science, Statistics,
Electronic Information Science and Technology, Computer Science and Technology,
Fashion Design and Engineering, Mechanical and Electronic Engineering, Public
Affairs Management, Economic Statistics, Food Quality and Safety, Product
Design, Mechanical and Electrical Technology Education, and Mathematics and
Applied Mathematics.
Another media-evidence pass adds a crawlable China Youth Daily article on
Hangzhou Dianzi University's 2018 professional-structure adjustment. It
contributes 11 medium-confidence planned stop-enrollment rows and attaches
secondary evidence to five 2019 Ministry cancellation rows for Function
Materials, Packaging Engineering, Printing Engineering, Applied Statistics,
and Smart Grid Information Engineering without upgrading those rows to high.
A further official-source pass adds Xi'an Polytechnic University's 2019
professional dynamic-adjustment notice. It upgrades five 2019 Ministry
cancellation rows to high confidence, adds three 2020 planned stop-enrollment
rows, and adds eight 2019 professional-warning rows with source-provided
college ownership, major codes, and degree categories.
Another official-source linkage pass adds Zhejiang Normal University's
school-college page citing MOE notice 教高函〔2020〕2号. It upgrades three 2019
Ministry cancellation rows to high confidence for Education, Art Education,
and Environmental Science.
A further official-source pass adds Jiangxi Agricultural University's smart
agriculture professional filing PDF. It attaches official school-history
evidence to 2018 and 2020 cancellation rows, upgrades four 2019 Ministry
cancellation rows to high confidence for Environmental Science, Environmental
Engineering, Marketing, and Urban-Rural Planning, and contributes two
high-confidence stop-enrollment rows for Business English and Information and
Computing Science.
Another secondary-table pass adds China Education Online's 2019 cancellation
table for 11 MOE-directly-administered university rows. This source does not
cover the full 367-row 2019 cancellation list, but it fills study-duration
fields and adds a crawlable table source for rows such as Huazhong Normal
University, Tongji University, Sichuan University, Wuhan University of
Technology, and Chang'an University.
Another official-source linkage pass adds Hebei University's discipline
inspection and supervision professional filing PDF from the Ministry application
materials platform. Its school-history section lists cancelled majors including
Network Engineering and Information and Computing Science; these two rows merge
into the matching 2019 Ministry cancellation records and are upgraded from
medium to high confidence. The same source does not mention Standardization
Engineering, so that Hebei University 2019 cancellation row remains medium
confidence pending a more specific source.
Another official-source linkage pass adds Kunming University of Science and
Technology's stomatology professional filing PDF from the Ministry application
materials platform. Its school-history section lists merged or cancelled majors
including Metallic Materials Engineering, Inorganic Non-metallic Materials
Engineering, Ideological and Political Education, Educational Technology, and
Natural Geography and Resource Environment; these five rows merge into matching
2019 Ministry cancellation records and are upgraded from medium to high
confidence.
Another application-materials pass adds professional filing PDFs for Nanchang
Hangkong University Science and Technology College, Qujing Normal University,
and Anqing Normal University. These official PDFs contribute 28
high-confidence stop-enrollment rows across 2015-2016 and 2025 application
years, and attach application-material evidence to 16 existing Ministry
cancellation rows for the same schools across 2020, 2022, 2023, and 2024.
A follow-up official-source pass adds Guilin University of Technology's
2018-2019 undergraduate teaching quality report and two Yuxi Normal University
2025 professional filing PDFs. Guilin University of Technology contributes
eight high-confidence stop-enrollment rows from its teaching-quality report.
Yuxi Normal University's filings add seven high-confidence stop-enrollment
rows and attach evidence to 13 existing Ministry cancellation rows, including
four 2019 cancellation rows upgraded from medium to high confidence.
A further application-materials pass adds Zhejiang Chinese Medical University's
nursing professional filing PDF and Chuxiong Normal University's UAV and
intelligent-network professional filing PDF. Zhejiang Chinese Medical University
contributes six high-confidence stop-enrollment rows and one cancellation
source linkage. Chuxiong Normal University's filing attaches official evidence
to seven Ministry cancellation rows, upgrading the 2019 Applied Physics and
Sports Rehabilitation rows from medium to high confidence.
Another application-materials pass adds 2025 Ministry-platform professional
filing PDFs for Nantong University, Tianjin University of Commerce, and Central
South University of Forestry and Technology. These official PDFs contribute 44
additional high-confidence stop-enrollment rows: 20 from Nantong University, 5
from Tianjin University of Commerce, and 19 from Central South University of
Forestry and Technology. The Nantong and Tianjin filings also mention cancelled
majors without row-level years; those cancellation mentions are retained as
source context but are not expanded into dated cancellation rows in this build.
Another official-source pass adds Shanghai University of Electric Power
information-disclosure pages for 2019, 2021, and 2023 plus its 2023-2024
undergraduate teaching quality report PDF. These sources add 14 dated
high-confidence stop-enrollment records across 2019, 2021, 2022, 2023, and
2024, and upgrade the seven 2025 Shanghai University of Electric Power
stop-enrollment rows from medium to high confidence by attaching the official
PDF evidence that lists the same stopped majors.
Another official information-disclosure pass adds Chaohu University's 2019-2022
undergraduate professional-setting tables and 2023-2024 professional-setting
PDF attachments. These eight source entries contribute 62 high-confidence,
row-level stop-enrollment records with source row numbers, major codes, study
durations, degree categories, and school-unit notes.
Another 2025 university-adjustment pass adds official HTML notices from
Southwest Jiaotong University and Jingzhou University. These two pages add seven
high-confidence proposed-cancellation rows: five from Southwest Jiaotong
University and two from Jingzhou University, with standard undergraduate
catalog codes attached during enrichment.
Another official notice adds Jinzhou Medical University's 2025 undergraduate
major cancellation page. It contributes one high-confidence cancellation record
for Insurance, with the page stating that the major had been stopped for more
than five years and had no remaining enrolled students.
Another application-materials pass adds Pingxiang University's smart
construction professional filing PDF. The filing contributes three
high-confidence stop-enrollment rows for Ideological and Political Education,
Digital Media Technology, and Engineering Cost, plus one 2025 proposed
cancellation row for Facility Agricultural Science and Engineering.
The Chuxiong Normal University UAV and smart-network filing is also parsed for
explicit stop-enrollment evidence. It adds four high-confidence 2025
stop-enrollment rows for Chinese Minority Language and Literature, Urban and
Rural Planning, Public Administration, and Music Performance; the remaining
unnamed items in the source's "11 stopped majors" statement are not expanded.
Another application-materials pass adds Wuhan University of Science and
Technology's fintech professional filing PDF. It contributes six high-confidence
2025 stop-enrollment rows for Human Geography and Urban-Rural Planning,
Automobile Service Engineering, E-Commerce, Transportation, Marxist Theory, and
Optoelectronic Information Science and Engineering, plus one official
application-materials linkage for the already captured Landscape Architecture
cancellation.
Another application-materials pass adds Beijing Institute of Graphic
Communication's digital-economy professional filing PDF. It contributes six
high-confidence 2025 stop-enrollment rows for Photography, Electronic
Information Engineering, Logistics Management, Logistics Engineering,
Industrial Design, and Marketing.
Another application-materials pass adds Hebei College of Science and
Technology's cybersecurity professional filing PDF. It contributes 17
high-confidence stop-enrollment rows across 2020-2023 and attaches official
application-materials evidence to the already captured 2021, 2023, and 2024
cancellation rows for Building Electricity and Intelligence, Landscape
Architecture, and Investment.
Another provincial-result pass adds a PDF mirror of the 2019 Guizhou ordinary
undergraduate professional-setting filing and approval results. Its cancellation
section provides 11 row-level records for Guizhou Minzu University, Guiyang
University, and Guizhou Minzu University College of Humanities and Science,
including source-provided major codes, degree categories, and study durations;
the matching 2019 Ministry cancellation rows are upgraded from medium to high
confidence.
A further source-linkage pass adds a crawlable Gaokaozhitongche/Qiuxue article
for Shandong University's 2023-2024 undergraduate professional-setting
adjustment. It independently lists the same 27 suspended-enrollment majors and
10 cancelled majors already captured from the ScienceNet repost of the
Shandong University undergraduate school article; these 37 rows remain medium
confidence because the original university page has not yet been located, but
they now carry two independent crawlable source ids.
A targeted school-official pass adds Hebei Normal University's 2019 functional
performance target PDF from the university development-planning office. The
document states that the university cancelled ten undergraduate majors and had
reported them to the Ministry of Education for filing and approval: Secretarial
Science, Radio and Television, Drama and Film Literature, Economics, Economic
Statistics, Applied Physics, Real Estate Development and Management, Social
Sports Guidance and Management, Automotive Service Engineering, and
Performance. These ten rows merge into the matching 2019 Ministry cancellation
records and are upgraded from medium to high confidence.
Another school information-disclosure pass adds Anhui University of Finance and
Economics' 2019 professional-setting table, cancellation-notice page, and
official scanned PDF. The PDF lists 13 cancelled undergraduate majors or
directions, upgrading 12 matching 2019 Ministry cancellation rows from medium to
high confidence and adding the cancelled Financial Studies (International
Finance) direction. The professional-setting HTML table also contributes 14
high-confidence same-year stop-enrollment rows with source-provided major codes
and source row numbers.
The same pass adds a Hebei Department of Education 2019 undergraduate
application-policy PDF mirror and parses its 2018 graduating-cohort
undergraduate initial-employment table. This contributes 924 high-confidence
metric rows: initial employment rate, graduate count, and employed count for
308 reported undergraduate majors.
A further provincial-warning pass adds a Liaoning Province 2016 government
news source from the Liaoning Department of Science and Technology site. The
page reports that the provincial education department advised universities to
temporarily avoid adding 66 undergraduate majors in 2016, lists all 66 names,
and states the basis as many local program sites, persistently low employment
rates, and unsuitability for duplicate setup. These rows are retained at
medium confidence because the page is a government-site news repost rather
than the original provincial education department attachment; the 11 majors
previously visible only in the 21st Century Business Herald article are merged
with this complete list and now carry both source ids.
The latest undergraduate official-source pass adds Hunan University's 2024 and
2025 undergraduate major catalog PDFs from the university information-disclosure
site. These two PDFs contribute 21 high-confidence current-year stop-enrollment
rows with source-provided major codes, study duration, and source row numbers,
plus eight school-level professional-adjustment metrics covering total majors,
enrolling majors, newly added majors, and stopped majors in 2024 and 2025.
The newest undergraduate official-source pass adds Anyang Institute of
Technology's 2025 information-disclosure stop-enrollment table and Northwestern
Polytechnical University's 2024/2025 undergraduate major-setting PDFs. These
three sources contribute 26 high-confidence current-year stop-enrollment rows
with source-provided major codes, study duration where available, discipline
labels where available, and source row numbers, plus seven school-level
professional-adjustment metrics.
The latest Anhui/Jilin official-source pass adds Anhui University of Chinese
Medicine's 2024 stop-enrollment notice, its 2024 and 2025 major-setting pages,
and Jilin Engineering Normal University's 2023-2024 and 2024-2025 undergraduate
teaching-quality report PDFs. This contributes 18 additional high-confidence
official rows: four Anhui University of Chinese Medicine 2024 stop-enrollment
rows, ten Jilin Engineering Normal University 2024 table-noted stop-enrollment
rows, and four Jilin Engineering Normal University 2025 cancellation rows. It
also adds 13 school-level professional-adjustment metrics and upgrades the
existing Anhui University of Chinese Medicine 2025 stop-enrollment rows with
source-provided major codes from the major-setting table.
The newest official-source pass adds Jiangsu Ocean University's 2025
undergraduate professional-setting notice, Zhejiang University's undergraduate
major-status table, and Zhejiang A&F University Jiyang College's 2024
professional-setting notice. These sources add four high-confidence 2025
Jiangsu Ocean University cancellation rows, 28 high-confidence Zhejiang
University rows whose table remarks mark them as already stopped, and official
university-page source linkage for two Jiyang College 2024 cancellation rows
already present in the Ministry filing table. They also add seven school-level
professional-adjustment metrics covering new/pre-filing/cancellation counts and
catalog/stopped-major counts.
The newest official-source increment adds Hefei Institute of Technology's 2025
information-disclosure professional-setting table and Xinjiang Normal
University's 2025 undergraduate professional-setting notice. These sources add
31 high-confidence Hefei Institute of Technology current-year stop-enrollment
rows and one Xinjiang Normal University 2025 cancellation row for Dance
Performance, plus seven school-level metrics for catalog size, enrolling/new
major counts, pre-filing counts, and cancellation/stop-enrollment counts.
The latest official-source linkage pass adds Changchun Institute of Technology's
2023 undergraduate professional-cancellation notice. Its six school-level
proposed cancellation rows are merged with the existing 2023 Ministry filing
rows for the same majors, adding the university's direct source evidence and
one school-level metric for six applied cancellations after five-plus years of
stop-enrollment.
The latest metrics pass adds a crawlable Sichuan Online provincial aggregate
for Sichuan's 2025 undergraduate professional adjustments, adding 13
medium-confidence province-level metrics for new, stop-enrollment, cancellation,
degree/duration-adjustment, three-year cumulative, industry-match, and selected
popular-new-major school counts. It also backfills eight high-confidence
school-level metrics from already archived East China Normal University,
Xinyang Normal University, and Nanyang Institute of Technology 2025 official
pages.
The newest image-table pass adds Wuhan University of Technology's 2025 official
undergraduate major catalog page. The page embeds two image tables; the raw
package keeps both images plus a reviewed transcription of the stop-enrollment
marks. This adds 24 high-confidence official stop-enrollment rows and two
school-level metrics covering total stop-enrollment marks and 2025 current-year
stop-enrollment marks.
The latest table-source increment adds Shaoxing Institute of Technology's 2025
professional-setting and enrollment-status table from its academic affairs
office. It contributes five high-confidence annual stop-enrollment rows for
Mechanical Electronic Engineering, Cross-border E-commerce, and Electronic
Packaging Technology, plus three school-level metrics for 2025 new-major and
stop-enrollment counts.
The latest official-publicity pass adds Anhui Science and Technology
University's 2025 undergraduate professional-adjustment notice, contributing two
high-confidence cancellation rows for Public Service Administration and
Facility Agriculture Science and Engineering, plus three school-level metrics
for pre-filing, cancellation, and study-duration-adjustment counts.
The newest official-source linkage pass adds Baoding Institute of Technology's
2024 undergraduate new/cancellation notice. Its two cancellation rows merge with
existing Ministry 2024 cancellation filings for Mechanical Electronic
Engineering and Architecture, strengthening those rows with direct school
evidence and adding two school-level new/cancellation count metrics.
The latest 2026 official-publicity pass adds Xianyang Normal University's
undergraduate major-adjustment notice, contributing one high-confidence proposed
cancellation row for Visual Communication Design and three school-level metrics
for proposed new, proposed cancellation, and pre-filing major counts. The page's
attachments were not redistributed in the raw package; the public page text
itself contains the structured evidence used here.

## Outputs

| File | Purpose |
|---|---|
| `major_risk_warning_records.csv` | One row per year, level, risk label, and major. |
| `major_risk_warning_records.jsonl` | Same records in JSON Lines format. |
| `major_risk_warning_metrics.csv` | Numeric employment-quality metrics extracted from crawlable sources. |
| `major_risk_warning_official_policy_warnings.csv` | Provincial/national professional-setting warning rules, explicit warning lists, stop-enrollment records, and cancellation filings. |
| `major_risk_warning_dataset_latest.xlsx` | Excel workbook with records, metrics, official warnings, summaries, sources, and coverage. |
| `major_risk_warning_major_summary.csv` | Frequency summary by standardized major name. |
| `major_risk_warning_year_summary.csv` | Year-level lists by education level and risk label. |
| `major_risk_warning_sources.csv` | Source URL, fetch status, raw path, text path, hash, and notes. |
| `major_risk_warning_coverage.csv` | Whether each year-level-risk slot has records. |
| `reports/major_risk_warnings/major_risk_warning_dataset_report_2026-06-12.md` | Human-readable build report. |
| `data/processed/vocational_major_register/vocational_major_records_2013_2026.csv` | Full 2013-2026 Ministry high-vocational specialty registration rows. |
| `data/processed/vocational_major_register/vocational_major_records_2013_2026_annotated.csv` | Same registration rows with unique row IDs, API duplicate flags, and warning/policy link fields. |
| `data/processed/vocational_major_register/vocational_major_risk_link_summary_2013_2026.csv` | Major-code/name summary with counts, latest-year coverage, and high-vocational risk/policy linkage fields. |
| `reports/vocational_major_register/vocational_major_risk_links_2013_2026.md` | Human-readable report for the high-vocational full-register support dataset. |
| `data/processed/policy_documents/undergraduate_major_official_events_20260612_v5.csv` | Clean undergraduate catalog / filing-approval official events with warning/policy link fields. |
| `data/processed/policy_documents/undergraduate_major_official_event_summary_20260612_v5.csv` | Major-code/name summary for undergraduate official events and risk links. |
| `data/processed/policy_documents/undergraduate_major_official_events_rejected_20260612_v5.csv` | Rejected table-header / non-standard-code rows retained for audit. |
| `reports/policy_documents/undergraduate_major_official_events_20260612_v5.md` | Human-readable report for the undergraduate official-event support dataset. |
| `data/processed/official_major_catalog/official_major_catalog_records_official_major_catalog_20260612_v2.csv` | Official vocational/graduate catalog rows. |
| `data/processed/policy_evidence/policy_documents_policy_evidence_seed_20260612_v5.jsonl` | National policy source-document metadata and crawl metrics. |
| `data/processed/policy_evidence/policy_mentions_policy_evidence_seed_20260612_v5.csv` | Direction-level policy evidence paragraph hits. |
| `data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv` | Major-level new-quality-productivity support profiles with linked risk/opportunity fields. |
| `data/processed/new_quality_major_profiles/new_quality_major_tier_samples_2026.csv` | Four-tier school sample rows for the support profile workbook. |
| `data/processed/new_quality_major_profiles/new_quality_policy_sources_2026.csv` | Policy source rows used by the new-quality-productivity direction rules. |
| `data/processed/new_quality_major_profiles/new_quality_major_profile_summary_2026.csv` | Summary by support category, confidence, major class, and direction. |
| `data/processed/ai_replacement/major_ai_replacement_ranking.csv` | Major-level AI replacement risk ranking from Chinese recruiting-market snapshots. |
| `data/processed/ai_replacement/major_job_candidates.csv` | Major-job candidate evidence and job-level risk scores. |
| `data/processed/ai_replacement/job_ai_risk_seed.csv` | Normalized job-title AI risk seed scores. |
| `data/processed/rysxai_market/market_major_profiles_2026.csv` | Major-level market observation profiles with demand, salary, job-sample, risk-link, civil-service, and transfer-policy features. |
| `data/processed/rysxai_market/market_job_samples_2026.csv` | Safe recruiting job samples used for market observation features. |
| `data/processed/rysxai_market/market_city_salary_2026.csv` | Per-major city salary aggregates from retained recruiting samples. |
| `data/processed/rysxai_market/market_macro_distributions_2026.csv` | Long table for industry, region, and job-direction distributions. |
| `data/processed/rysxai_market/market_rankings_2026.csv` | Long table for demand and salary ranking observations. |
| `data/processed/rysxai_market/market_skill_summary_2026.csv` | Per-major skill frequency summaries from job samples. |
| `data/processed/rysxai_market/market_profile_summary_2026.csv` | Summary by all, level, category, and subject. |
| `data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv` | Major-level civil-service opportunity and competition profiles from 2026 role text. |
| `data/processed/rysxai_civil_service/civil_service_role_match_summary_2026.csv` | Role-level professional-requirement parse summary. |
| `data/processed/rysxai_civil_service/civil_service_role_major_matches_2026.csv` | Role-major bridge table with exact/broad match scope. |
| `data/processed/rysxai_civil_service/civil_service_unmatched_profession_terms_2026.csv` | Unmatched professional requirement terms retained for review. |
| `data/processed/rysxai_transfer_policies/transfer_policy_school_profiles_2026.csv` | School-level transfer-major policy availability, restrictions, heuristic difficulty, and risk-linked major mention counts. |
| `data/processed/rysxai_transfer_policies/transfer_policy_faculty_profiles_2026.csv` | Faculty-level transfer-major policy blocks parsed from source JSON. |
| `data/processed/rysxai_transfer_policies/transfer_policy_major_mentions_2026.csv` | Major-level transfer-policy text mention summary with risk links. |
| `data/processed/rysxai_transfer_policies/transfer_policy_profile_summary_2026.csv` | Transfer-policy summary by all schools, province, school type, property, and level. |
| `data/processed/rysxai_major_intros/major_introductions_full_20260611_intro.csv` | Source-level C major introduction, course, transition, and similar-major text profiles. |
| `data/processed/rysxai_major_intros/major_intro_risk_profiles_20260611.csv` | Risk-linkable major-introduction profiles with employment-warning, official-policy, and AI-risk linkage fields. |
| `data/processed/rysxai_major_intros/major_intro_risk_profile_summary_20260611.csv` | Level-level summary for major-introduction coverage and risk linkage. |
| `data/processed/graduate_outcomes/major_outcome_flow_summary_20260604.csv` | Major-level flow summary from public masked official recommendation/admission records. |
| `data/processed/graduate_outcomes/major_outcome_flow_role_summary_20260604.csv` | Role-level summary for undergraduate-major and admission-major flows. |
| `data/processed/graduate_outcomes/graduate_outcome_school_year_profiles_20260604.csv` | School-year profile table combining public masked recommendation/admission samples with official report metrics and source coverage fields. |
| `data/processed/graduate_outcomes/graduate_outcome_school_summary_20260604.csv` | School-level rollup across public sample years, official metric years, coverage-only schools, and source-attempt audit rows. |
| `data/cleaned/graduate_outcomes/official_employment_report_metrics.csv` | School-level official employment/further-study metrics extracted from official reports. |

See `docs/datasets/vocational-major-register.md` for the full support-dataset
schema and packaging notes. See
`docs/datasets/undergraduate-major-official-events.md` for the undergraduate
official-event schema and packaging notes. See
`docs/datasets/official-catalog-policy-evidence.md` for official catalog and
policy-evidence package notes. See
`docs/datasets/new-quality-major-profiles.md` for the new-quality-productivity
major support dataset. See
`docs/datasets/major-ai-replacement-risk.md` for the AI replacement-risk
support dataset. See
`docs/datasets/rysxai-market-observations.md` for the rysxai market-observation
support dataset. See
`docs/datasets/rysxai-civil-service-major-opportunities.md` for the
civil-service opportunity support dataset. See
`docs/datasets/rysxai-transfer-policy-profiles.md` for the transfer-policy
profile support dataset. See
`docs/datasets/rysxai-major-introductions.md` for the
major-introduction support dataset. See
`docs/datasets/graduate-outcome-major-flows.md` for the graduate-outcome major
flow support dataset. See
`docs/datasets/graduate-outcome-school-year-profiles.md` for the
graduate-outcome school-year profile support dataset. See
`docs/datasets/dialogue-function-call-eval.md` for the dialogue function-call
evaluation support dataset. See
`docs/datasets/graduate-official-source-coverage.md` for the graduate official
source-coverage metadata support dataset. See
`docs/datasets/graduate-chsi-public-sources.md` for the separate CHSI public
source/provenance support dataset. See
`docs/datasets/graduate-source-discovery.md` for the graduate official-source
discovery queue support dataset. See
`docs/datasets/graduate-official-batch-inventory.md` for the metadata-only
inventory of graduate official-site batch outputs. See
`docs/datasets/emerging-major-candidate-details.md` for the detailed official
emerging-major candidate support dataset. See
`docs/datasets/emerging-major-source-attachments.md` for the official
source-page and attachment provenance index behind those candidate records.
See `docs/datasets/reference-seed-inventory.md` for the seed/reference files
used to reproduce crawls and join profession, school, policy, and official-site
sources. See `docs/datasets/raw-source-inventory.md` for the metadata-only
inventory of raw crawl files and crawl logs. See
`docs/datasets/processed-asset-inventory.md` for the metadata-only catalog of
processed, cleaned, report, and dataset-document assets. See
`docs/datasets/major-risk-master-index.md` for the unified per-major screening
index that joins the professional-level risk and opportunity signals. See
`docs/datasets/major-risk-evidence-profiles.md` for the evidence long table
behind that master index. See `docs/datasets/major-risk-review-release.md` for
the sortable high-risk/risk-watch shortlist and unified source-document index.
See `docs/datasets/major-risk-source-content-index.md` for the searchable
document, snippet, and keyword-summary tables derived from the archived public
source URLs.

## Packages

| Package | Purpose |
|---|---|
| `outputs/major_risk_warnings_dataset_20260612.zip` | Core risk-warning processed files only. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Core risk-warning processed files plus all processed support datasets built in this pass. |
| `outputs/major_risk_warnings_raw_sources_20260612.zip` | Raw/text/image sources for the core risk-warning crawl. |
| `outputs/vocational_major_register_dataset_20260612.zip` | High-vocational register processed files, reports, docs, and reproducible scripts. |
| `outputs/vocational_major_register_raw_pages_20260612.zip` | Raw Ministry API JSON pages and crawl logs for the high-vocational register. |
| `outputs/undergraduate_major_official_events_dataset_20260612.zip` | Clean undergraduate official-event files, reports, docs, and reproducible scripts. |
| `outputs/undergraduate_major_official_events_raw_sources_20260612.zip` | Raw Ministry undergraduate catalog / filing-approval pages, attachments, and crawl logs. |
| `outputs/official_catalog_policy_evidence_dataset_20260612.zip` | Official vocational/graduate catalog plus policy-evidence processed files, reports, docs, and scripts. |
| `outputs/official_catalog_policy_evidence_raw_sources_20260612.zip` | Raw official catalog attachments and policy-evidence source pages. |
| `outputs/new_quality_major_profiles_dataset_20260612.zip` | New-quality-productivity processed profiles, tier samples, policy sources, summary, report, docs, workbook, scripts, and tests. |
| `outputs/major_ai_replacement_dataset_20260612.zip` | AI replacement-risk processed files, report, docs, and reproducible script. |
| `outputs/major_ai_replacement_source_snapshots_20260612.zip` | rysxai raw API payloads, normalized market snapshots, and crawl logs used as source evidence. |
| `outputs/rysxai_market_observations_dataset_20260612.zip` | Rysxai market observation processed tables, report, docs, scripts, crawler/report modules, and tests. |
| `outputs/rysxai_market_raw_sources_20260612.zip` | Rysxai market raw API payloads, normalized snapshots, crawl logs, and market crawler spec. |
| `outputs/rysxai_civil_service_major_opportunities_dataset_20260612.zip` | Civil-service processed source table, major opportunities, role parse summary, role-major bridge, report, docs, scripts, and tests. |
| `outputs/rysxai_civil_service_raw_sources_20260612.zip` | Raw rysxai civil-service JSONL crawl and failure log if present. |
| `outputs/rysxai_transfer_policy_profiles_dataset_20260612.zip` | Transfer-policy processed source table, school/faculty/major profiles, summary, report, docs, scripts, and tests. |
| `outputs/rysxai_transfer_policy_raw_sources_20260612.zip` | Raw rysxai transfer-policy JSONL crawl and failure log if present. |
| `outputs/rysxai_major_introductions_dataset_20260612.zip` | rysxai major-introduction processed files, risk-link profiles, report, docs, scripts, and tests. |
| `outputs/rysxai_major_introductions_raw_sources_20260612.zip` | rysxai major-introduction raw API payloads, normalized snapshots, aggregate source files, and crawl logs. |
| `outputs/graduate_outcomes_major_flows_dataset_20260612.zip` | Public masked graduate-outcome records, major-flow summaries, official employment metrics, workbook package, report, docs, scripts, and tests. |
| `outputs/graduate_outcomes_school_year_profiles_dataset_20260612.zip` | Graduate-outcome school-year profiles, school summaries, public/official source tables, report, docs, scripts, and tests. |
| `outputs/dialogue_function_call_eval_dataset_20260612.zip` | Public-ASR-derived dialogue question bank, function-call eval cases, summary tables, source inventory, report, docs, scripts, and tests. |
| `outputs/graduate_official_source_coverage_dataset_20260612.zip` | Graduate official source coverage rollups, school-year source summaries, remaining-source attempt decisions, employment metrics, artifact hash inventory, report, docs, scripts, and tests. |
| `outputs/graduate_chsi_public_sources_dataset_20260612.zip` | Masked CHSI public records, school-index inventory, bulletin seed inventory, CHSI document metadata, crawl-batch summary, report, docs, scripts, and tests. |
| `outputs/graduate_source_discovery_dataset_20260612.zip` | Graduate source-discovery task queues, official URL candidates, search probe results, seed/failure inventories, summaries, report, docs, scripts, and tests. |
| `outputs/graduate_official_batch_inventory_dataset_20260612.zip` | Metadata-only graduate official-site batch directory/file/document inventory, privacy summaries, report, docs, scripts, and tests. |
| `outputs/emerging_major_candidate_details_dataset_20260612.zip` | Detailed official Ministry emerging/undergraduate major candidate JSONL and CSV, source document summaries, normalized official event tables, report, docs, scripts, and tests. |
| `outputs/emerging_major_source_attachments_dataset_20260612.zip` | Official Ministry source-page and attachment index, coverage summaries, raw-file inventory, crawl manifest/failure log, report, docs, scripts, and tests. |
| `outputs/reference_seed_inventory_dataset_20260612.zip` | All seed/reference files plus normalized crawled-source seed inventories, policy source tables, RYSXAI profession/university summaries, report, docs, scripts, and tests. |
| `outputs/raw_source_inventory_dataset_20260612.zip` | Metadata-only inventory of raw crawl files and logs, including path, source family, byte size, hash status, zip package memberships, report, docs, scripts, and tests. |
| `outputs/processed_asset_inventory_dataset_20260612.zip` | Metadata-only catalog of processed, cleaned, report, and dataset-document assets with privacy flags, row/hash status, package memberships, report, docs, scripts, and tests. |
| `outputs/major_risk_master_index_dataset_20260612.zip` | Unified per-major risk/opportunity screening index, summaries, source coverage, manifest, report, docs, script, source module, and tests. |
| `outputs/major_risk_evidence_profiles_dataset_20260612.zip` | Long-form evidence records behind the master index, per-major evidence summaries, source summaries, manifest, report, docs, script, source module, and tests. |
| `outputs/major_risk_review_release_dataset_20260612.zip` | Sortable high-risk/risk-watch shortlist, unified source-document index, summary, manifest, report, docs, script, source module, and tests. |
| `outputs/major_risk_source_archive_dataset_20260612.zip` | Metadata index, manifest, report, docs, source module, CLI wrapper, and tests for public review-source URLs archived in this pass. |
| `outputs/major_risk_source_content_index_dataset_20260612.zip` | Searchable document, snippet, keyword-summary, manifest, report, docs, source module, CLI wrapper, and tests for archived public source text/metadata files. |
| `outputs/major_risk_source_archive_raw_sources_20260612.zip` | Raw and text files archived from public review-source URLs that previously lacked local paths. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Record Fields

| Field | Meaning |
|---|---|
| `report_year` | Employment report/list year. |
| `graduate_cohort` | Approximate graduating cohort, usually `report_year - 1`. |
| `education_level` | `本科` or `高职高专`. |
| `risk_level` | `red`, `yellow`, or `green`. |
| `reported_major_name` | Major name as reported by the source. |
| `standard_major_name` | Best-effort normalized current name. |
| `major_code` | Matched code from `data/seeds/rysxai_professions.full.csv` when available. |
| `discipline` | Matched discipline/category from the local catalog. |
| `major_category` | Matched major class from the local catalog. |
| `source_ids` | Semicolon-separated source ids in `major_risk_warning_sources.csv`. |
| `evidence_type` | Whether the row is an explicit list, derived from consecutive-count text, or a low-confidence candidate. |
| `confidence` | `high`, `medium`, or `low`. |

## Metric Fields

| Field | Meaning |
|---|---|
| `report_year` | Report/list year that published the metric. |
| `graduate_cohort` | Graduating cohort measured by the source. |
| `education_level` | `本科` or `高职高专`. |
| `reported_major_name` | Major name as reported by the source. |
| `metric_name` | Numeric metric name, including employment-quality metrics such as `monthly_income` and school-level professional-adjustment counts such as `school_current_year_stop_enrollment_major_count`. |
| `metric_value` | Numeric metric value. |
| `metric_unit` | Unit for the numeric value, such as `CNY/month`, `percent`, `majors`, `schools`, or `major-instances`. |
| `metric_rank` | Rank when the source explicitly gives or implies an ordered list. |
| `rank_scope` | Population for the rank, such as本科专业毕业半年后月收入前10. |

## Official Policy Warning Fields

This table is separate from MyCOS red/yellow/green records. It covers official
professional-setting risk controls such as provincial warning lists, negative
lists, enrollment-plan reductions, and exit mechanisms.

The Ministry of Education complete cancellation filings currently parsed into
this table are:

| Policy year | Source row count |
|---|---:|
| 2011 | 32 |
| 2013 | 26 |
| 2014 | 67 |
| 2015 | 118 |
| 2016 | 149 |
| 2017 | 241 |
| 2018 | 416 |
| 2019 | 367 |
| 2020 | 518 |
| 2021 | 804 |
| 2022 | 925 |
| 2023 | 1670 |
| 2024 | 1428 |

| Field | Meaning |
|---|---|
| `policy_year` | Year of the policy or warning publication. |
| `region` | Province, national scope, or school name for school-level cancellation/stop-enrollment rows. |
| `education_level` | Education level or scoped label, usually `本科`. |
| `record_type` | `major_warning_list`, `major_warning_partial_list`, `major_stop_enrollment`, `major_cancel`, `national_low_employment_list`, `provincial_low_employment_list`, or `policy_rule`. |
| `warning_label` | Source label, such as省级本科专业预警名单. |
| `reported_major_name` | Major name as reported by the source. |
| `standard_major_name` | Best-effort normalized current name. |
| `major_code` | Official source code when a source table provides one; otherwise matched from the local catalog when available. |
| `discipline` | Matched discipline/category from the local catalog. |
| `major_category` | Matched major class from the local catalog. |
| `policy_action` | Suggested/required action such as reducing enrollment, stopping enrollment, or no longer supporting new setup. |
| `criterion_text` | Criteria used by the policy source. |
| `source_row_no` | Source-table row number when available, such as the Ministry of Education attachment serial number. |
| `study_duration` | Source-table study duration when available. |
| `source_ids` | Semicolon-separated source ids in `major_risk_warning_sources.csv`. |
| `evidence_text` | Short source-backed evidence sentence. |
| `confidence` | `high`, `medium`, or `low`. |

## Confidence

| Confidence | Use |
|---|---|
| `high` | The fetched source text or PDF text explicitly lists the major. |
| `medium` | The row is supported by a public secondary summary, crawlable official mirror, or consecutive-year count text but still needs priority review against the school/government original where possible. |
| `low` | The row is retained as a candidate because the source was discoverable but blocked or needs OCR/manual verification. |

## Caveats

- Red/yellow/green labels reflect national employment warning analysis, not a ban on applying to a major.
- Ministry of Education cancellation rows are official filing records for professional-setting adjustment; they do not describe individual students' enrollment status.
- A complete 2012 Ministry of Education cancellation table has not yet been found in a crawlable, verifiable source; 2012 rows in the official warning table come from provincial/policy sources already listed in `source_ids`.
- The 2019 Ministry of Education annual PDF is archived as a raw scanned source. Its structured rows come from a machine-readable XLS mirror whose row count matches the 367-row cancellation list, but that mirror only carries school, major, and major code, so `study_duration` is blank for 2019 Ministry rows.
- Historical high-vocational specialty names changed across catalog revisions. Keep both `reported_major_name` and `standard_major_name` when analyzing trends.
- `data/raw/` and `data/processed/` are local data asset directories and may be ignored by Git. Package them separately if the dataset needs to be shared outside this workspace.
- The 2026 pass found publicly fetchable undergraduate and high-vocational green-list data. No high-confidence 2026 red/yellow list was found in this crawl.
