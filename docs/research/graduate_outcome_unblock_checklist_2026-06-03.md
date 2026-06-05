# Graduate Outcome Remaining Official-Source Unblock Checklist

Date: 2026-06-03

This checklist covers the 9 schools still not counted in the official final row-level recommendation/admission coverage. The current package remains 421 / 430 because the sources below either are blocked by public-access controls, have been removed, expose only non-final/non-row-level material, or do not publish a public person-level list.

To unblock ingestion for any school, provide an official page/PDF/XLS/XLSX body that exposes person-level final recommendation/admission rows. Search snippets, third-party mirrors, login-only pages, WAF/CAPTCHA pages, and non-final score/shortlist materials are not sufficient.

| School | Current official candidates | Current blocker | What would unblock ingestion |
| --- | --- | --- | --- |
| 北京电影学院 | `https://www.bfa.edu.cn/yanjiusheng/info/1031/4573.htm`; `https://www.bfa.edu.cn/yanjiusheng/info/1031/4667.htm`; historical candidates `4320`, `4037`, `3724`, `2939`; candidate-number PDF `https://www.bfa.edu.cn/yanjiusheng/2026niantuimiankaoshengkaoshengbianhao.pdf` | Final-list pages return HTTP 412 JavaScript challenge. The PDF is only a recommendation-exemption candidate-number list and has no final admitted/result status. | Official article body or attachment for a final `拟录取` / admitted list with names/candidate IDs and result status. |
| 北京服装学院 | `https://yjs.bift.edu.cn/zsgz/zsxx/c61dba4634ec4dc1bfae869808f0be4f.htm`; `https://yjs.bift.edu.cn/zsgz/zsxx/0ede7f1a1a9f4061a3f5334ea483d24f.htm`; `https://yjs.bift.edu.cn/zsgz/zsxx/7e8b0b26573f4f6e998ca00a06ff5f68.htm`; doctoral auxiliary page/PDF under `cf66...` | Older final-list candidates redirect to custom 404. Current material-collection notice is non-row-level. Doctoral comprehensive-assessment PDF is a non-final shortlist. | Official final master's recommendation/admission list or final doctoral admitted list, not a shortlist/materials notice. |
| 成都体育学院 | `https://yjsy.cdsu.edu.cn/chengdoutiyuxueyuan2025nianjieshouyouxiuyingjiebenkebiyeshengmianshigongdushuoshixueweiyanjiushengniluqumingdanyi.pdf`; `...niluqumingdaner.pdf`; `https://yjsy.cdsu.edu.cn/info/1021/4966.htm`; `https://yjsy.cdsu.edu.cn/info/1021/6518.htm` | Public requests return Safeline WAF HTML rather than PDF/article body. | Official PDF/article content after normal access that contains the full final person-level list. |
| 宁波诺丁汉大学 | `https://www.nottingham.edu.cn/cn/graduateschool/`; `https://www.nottingham.edu.cn/cn/study-with-us/postgraduate-taught/how-to-apply.aspx`; official press release for recommendation-exemption qualification | Official pages are public but only contain portal, admissions process, offer/deposit, and qualification news. No public person-level final list found. | Official public person-level recommendation/admission list, if the school publishes one. |
| 西北师范大学 | `https://yjsy.nwnu.edu.cn/2025/1120/c2713a265316/page.htm`; `https://yjsy.nwnu.edu.cn/2024/1114/c2713a244341/page.htm`; `https://yjsy.nwnu.edu.cn/2025/0402/c2701a251529/page.htm`; `https://yjsy.nwnu.edu.cn/2025/0507/c2701a253546/page.htm`; direct uploaded PDF candidates | Local requests return HTTP 412 JavaScript challenge, direct admitted-list PDF candidate returns 404, and available PDF material is aggregate/professional statistics rather than names. Search snippets expose only summaries and are not ingestible. | Official article/PDF/XLS body with full row-level final recommendation/admission rows. |
| 西藏农牧大学 | `https://www.xza.edu.cn/yjsc/info/1040/5983.htm`; `http://www.xza.edu.cn/yjsc/1040/list.htm`; `http://www.xza.edu.cn/gljg/yjsc/main/news.asp?id=261` | `5983.htm` is an official 513-row adjustment score table and is stored as auxiliary non-final data. It has score fields but no final `拟录取` status. Other list/legacy candidates reset connection. | Official final admitted-list page or attachment with person-level admission status. |
| 浙江中医药大学 | `https://yjsgl.zcmu.edu.cn/show/5925`; `show/5810`; `show/5850`; `show/5751`; attachments including `1760945588435481.xlsx`, `1760944454983762.xlsx`, `1751195765896878.xlsx`, `1750841684110661.xlsx`, `1737107101746617.xls`, `1737102375378758.xls` | Attachment URLs are official and promising, but direct requests return HTTP 412 CT2-WAAP verification HTML. Downloaded bodies are 22,856-byte HTML pages starting with `<!doctype html>`, not XLS/XLSX. | Actual official XLS/XLSX/PDF/article body after normal authorized access, with final row-level records. |
| 中国医科大学 | `https://www.cmu.edu.cn/system/_content/download.jsp?owner=1778759152&urltype=news.DownloadAttachUrl&wbfileid=13255969`; article candidates `9236`, `9515`, `9514`, `9811`, `9398`, `9608`, `9660`, `9671` | Attachment candidate is a verification-code download bridge. Article candidates currently return 404 system prompt pages. | Official attachment or restored article body for recommendation/admission list, without CAPTCHA bridge. |
| 重庆邮电大学 | `https://yjs.cqupt.edu.cn/`; detail candidates `12634`, `11244`, `14304`, `14564`, `14574`, `11614` | Homepage is HTTP 200 and exposes candidate links, but only titles/links. Detail pages return HTTP 412 JavaScript challenge HTML/empty dynamic body, not article/list content. | Official detail article body or attachment containing final row-level list. |

## Current Verified Package State

- Official final row-level coverage: 421 / 430 schools
- Remaining uncovered: 9 schools listed above
- Public records: 283,749 rows
- Auxiliary non-final row-level records: 641 rows
- Source-attempt evidence rows: 15 rows
- Workbook: `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx`

