# 学校官网保研名单抓取样本记录

更新日期：2026-05-22

## 这轮先抓了什么

本轮先按“学校/学院官网公开保研资格、拟推荐名单”路线做样本抓取。入口来自一批已经命中标题的官网页面，主要关键词是：

- 2026届 / 2026年
- 推荐免试 / 推免资格 / 拟推荐名单
- 公示 / 名单

种子文件：

- `data/seeds/official_site_recommendation_websearch_probe.csv`

抓取结果目录：

- `data/processed/graduate_outcomes_official_site_websearch_probe_v2/`
- `data/raw/graduate_outcomes_official_site_websearch_probe_v2/`
- `data/logs/graduate_outcomes_official_site_websearch_probe_v2/`

## 当前可用数据

主要可看表：

- `data/processed/graduate_outcomes_official_site_recommendation_master/records_public.csv`
- `data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv`
- `data/processed/graduate_outcomes_official_site_websearch_probe_v2/records_public.csv`
- `data/processed/graduate_outcomes_official_site_websearch_probe_v2/records_clean.csv`
- `data/processed/graduate_outcomes_official_site_websearch_probe_v2/school_year_summary.csv`

当前官网保研主表：

- 输入官网抽取记录：628 行
- 清洗去重后记录：583 行
- 脱敏交付记录：583 行
- 覆盖学校/学院来源：11 组

抓取规模：

- 官网入口种子：13 条
- 成功获取页面/附件：19 个
- 抓取失败：0 个
- 原始抽取记录：317 行
- 清洗后记录：317 行
- 对外交付用脱敏记录：317 行
- 有效出数的学校/学院来源汇总：5 组

汇总计数：

| 学校 | 年份 | 类型 | 记录数 | 备注 |
| --- | --- | --- | --- | --- |
| 延安大学 | 2026 | 保研拟推荐名单 | 196 | HTML 页面可解析 |
| 西南财经大学 | 2026 | 保研资格名单 | 46 | HTML 表格可解析 |
| 上海交通大学 | 2026 | 推免资格公示 | 30 | HTML 表格可解析 |
| 西安建筑科技大学 | 2026 | 保研拟推荐名单 | 26 | HTML 页面可解析 |
| 华北水利水电大学 | 2026 | 拟推荐免试名单 | 19 | 字段较少，已标记复核 |

新增第二批出数：

| 学校 | 年份 | 类型 | 记录数 | 备注 |
| --- | --- | --- | --- | --- |
| 燕山大学 | 2026 | 保研拟推荐名单 | 84 | HTML 页面可解析 |
| 湘潭大学 | 2026 | 保研拟推荐名单 | 78 | HTML 页面可解析 |
| 安徽工业大学 | 2026 | 保研拟推荐名单 | 32 | PDF/页面来源，字段较少，已标记复核 |
| 上海海洋大学 | 2026 | 保研拟推荐名单 | 30 | 段落名单已可解析 |
| 苏州科技大学 | 2026 | 保研拟推荐名单 | 24 | HTML 表格可解析 |
| 上海大学 | 2026 | 保研拟推荐名单 | 18 | 表格错位已在清洗阶段修复并去重 |

## 本轮已经补强的爬虫能力

代码文件：

- `scripts/graduate_outcome_crawler.py`
- `tests/test_graduate_outcome_crawler.py`

新增/修复能力：

- 能跟进页面里无文件后缀的下载链接，例如 `download.jsp?...`，只要链接文本包含 `.xlsx`、`.pdf` 等附件名。
- 能识别页面内嵌 PDF 播放器里的 `pdfsrc` / `filesrc` 附件地址。
- 能根据响应 `Content-Type` 判断 `.xlsx`、`.docx`、`.pdf` 等真实文件后缀。
- 能根据 PDF 文件头识别 `application/octet-stream` 但实际是 PDF 的下载。
- 能把中文 URL 路径转成 percent-encoding，避免 `urllib` 请求中文附件路径时报编码错误。
- 能从公开高校官网目录匹配本地 450 所“保研”院校，已生成 430 所官网入口：`data/processed/graduate_outcomes/school_official_sites_recommended_laosheng.csv`。
- 能从学校首页进入同一学校根域下的教务处/本科生院等门户页，再查找推免名单链接。
- 能解析“专业标题 + 姓名顿号列表”这类段落式名单。
- 能在清洗阶段修复“序号/姓名错位”造成的姓名字段纯数字问题，并保留质量更高的重复记录。

验证：

- `python -m unittest tests.test_graduate_outcome_crawler`
- 结果：49 个测试通过。

## 本轮看到的边界

1. 南京农业大学部分学院附件下载返回验证码中转页，页面已保存，但不能在无验证码输入的情况下直接下载 Excel。
2. 多个 PDF 附件已经成功保存，但 PDF 内部中文编码不可稳定抽取，当前不把乱码表格强行写入清洗表。
3. Bing RSS 在本环境中会返回大量 Microsoft/Office 噪声；Bing HTML 会触发 Turnstile 验证，不适合做无登录批量发现。
4. 学校首页直扫命中很低，必须进入教务处/本科生院/学院门户或使用已命中的官网名单页作为种子。
5. 这轮仍是官网保研名单样本，不等于 450 所保研资格学校的全量结果。

## 官网入口覆盖

本轮使用公开高校官网目录作为官网入口来源，和本地 `rysxai_universities.csv` 对齐：

- 本地“保研”标签本科院校：450 所
- 成功匹配官网入口：430 所
- 未匹配：20 所，主要是医学部、分校、异地校区、军校或命名差异。

入口表：

- `data/processed/graduate_outcomes/school_official_sites_recommended_laosheng.csv`

## 可追溯来源示例

- 西南财经大学财税学院：`https://spft.swufe.edu.cn/info/1043/29573.htm`
- 上海交通大学生命科学技术学院：`https://life.sjtu.edu.cn/Data/View/8636`
- 延安大学教务处：`https://jwc.yau.edu.cn/info/1003/19171.htm`
- 西安建筑科技大学建筑设备科学与工程学院：`https://bsse.xauat.edu.cn/info/1003/7459.htm`
- 华北水利水电大学能源与动力工程学院：`https://www2.ncwu.edu.cn/nydl/info/1040/2434.htm`
- 燕山大学信息科学与工程学院：`https://ise.ysu.edu.cn/info/1072/8938.htm`
- 湘潭大学自动化与电子信息学院：`https://aei.xtu.edu.cn/info/1078/4826.htm`
- 苏州科技大学土木工程学院：`https://civil.usts.edu.cn/info/1044/3541.htm`
