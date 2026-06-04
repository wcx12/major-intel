# 毕业出路数据爬取阶段材料：CHSI/研招网公开公告

更新时间：2026-05-22

## 这次抓取了什么

本轮优先爬取“B 类数据源”：CHSI/研招网院校库里的招生单位公开公告。策略是从 CHSI 院校库第 0-46 页抓取招生单位索引，再进入各单位公告列表，筛选标题明确指向“硕士研究生拟录取名单/拟录取名单”等名单类公告的公开页面。

本轮没有绕过登录，也没有抓取需要账号权限的页面；只处理公开可访问页面和附件。

## 当前产出

主数据文件：

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`
- `data/processed/graduate_outcomes_chsi/master_school_year_summary.csv`

证据与中间文件：

- `data/processed/graduate_outcomes_chsi/crawl_*/documents.jsonl`
- `data/processed/graduate_outcomes_chsi/crawl_*/records.jsonl`
- `data/raw/graduate_outcomes_chsi*/`

代码与测试：

- `scripts/graduate_outcome_crawler.py`
- `tests/test_graduate_outcome_crawler.py`

## 数据规模

- CHSI 院校库范围：第 0-46 页，约 939 个招生单位。
- 首层严格名单入口：228 条。
- 加深到每校最多 6 个公告列表后，严格名单入口：234 条。
- 名单入口抓取成功：234 条，入口抓取失败 0 条。
- 原始抽取记录：7,610 行。
- 清洗去重后记录：7,572 行。
- 可交付脱敏记录：7,572 行。
- 覆盖单位：64 个。
- 学校-年份汇总行：152 行。
- 年份范围：2008-2026。
- 清洗后缺失年份：0 行。

## 可用表说明

优先给分析和外部查看使用：

- `master_records_public.csv`

这个表不包含原始 `person_name` 和 `student_id` 字段，只保留：

- `public_record_id`
- `person_name_masked`
- `student_id_masked`
- 学校、年份、类型、专业、来源 URL、质量分和质量标记等字段。

内部核查和去重使用：

- `master_records_clean.csv`

这个表仍保留原始姓名和考生号字段，便于内部追溯和去重；对外分享时优先使用 public 表。

## 质量分布

- 100 分：27 条。
- 93 分：3,553 条。
- 81 分：1,722 条。
- 69 分：1,587 条。
- 57 分：683 条。

低分主要来自源公告本身缺少本科院校、录取专业或需要人工复核字段，不代表页面抓取失败。

## 年份分布

- 2008：553
- 2009：1,372
- 2011：168
- 2012：167
- 2014：6
- 2015：535
- 2016：25
- 2017：52
- 2018：1,030
- 2019：16
- 2020：77
- 2021：308
- 2022：835
- 2023：166
- 2024：351
- 2025：774
- 2026：1,137

## 目前局限

- 这仍不是全部“保研资格名单”。保研资格名单很多发布在本科教务处、本科生院、学院、推免专题页，需要另走学校官网发现流程。
- 公开搜索引擎在当前环境不稳定：Bing HTML 和 DuckDuckGo HTML 会出现反爬/验证码，Bing RSS 能返回但中文相关性不稳定。
- 本轮抽取了 450 个带“保研”标签的本科院校，生成了官网发现队列：`data/processed/graduate_outcomes/official_site_discovery_queue_recommendation_exemption.csv`。
- 对 1,350 个“推荐免试名单”搜索任务做了 Bing RSS 小样本验证：前 30 个任务返回 150 条结果，但转成有效 seed 为 0，主要噪声是百科、城市和旅游页。
- 阳光高考院校库和文件下载样例在脚本访问下返回 HTTP 412，暂时不能作为无登录批量官网 URL 来源；后续需要浏览器会话/cookie、人工导入或其他官方来源补齐官网域名。
- PDF 和旧 `.doc` 的表格抽取仍是弱项；HTML、xlsx/xlsm、docx 的可用性更高。
- 一些单位公告访问失败发生在“入口发现阶段”；已发现的名单入口抓取失败为 0。
- CHSI 多公告列表加深带来的新增有限，说明 CHSI 院校库的名单类公告主要集中在首个公告分类，但不能替代各学校官网抓取。

## 建议下一步

1. 用教育部高校名单和本地 `rysxai_universities.csv` 对齐本科院校范围。
2. 针对保研资格名单，优先抓学校教务处/本科生院/学院官网。
3. 为学校官网发现增加站内 sitemap、官网栏目链接、已知域名优先级和失败重试清单。
4. 对 PDF/旧 `.doc` 增强解析或输出人工复核队列。
