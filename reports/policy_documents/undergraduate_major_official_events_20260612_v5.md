# 本科专业目录/备案审批事件清洗与风险关联报告

- 来源候选行数：33981
- 清洗后有效本科专业事件：33173
- 拒收噪声/非标准行：808
- 重复来源 candidate_id 超额数：32
- 输出事件表重复 event_record_id：0
- 去重专业代码/名称数：1081
- 通过目录标准名修复的专业名行数：19
- 备案/审批新增事件中仍无法可靠推断学校名的行数：109
- 可关联红/黄就业预警的本科专业数：67
- 可关联官方政策风险记录的本科专业数：627
- 行级就业预警关联数：7429
- 行级官方政策关联数：27377

## 事件类型

- `undergraduate_catalog_entry`: 5197
- `undergraduate_filing_or_approval_added`: 27976

## 年份覆盖

- 2012: 1156
- 2013: 1900
- 2014: 1773
- 2015: 2368
- 2016: 2362
- 2017: 2602
- 2018: 2523
- 2019: 2948
- 2020: 2870
- 2021: 2843
- 2022: 3591
- 2023: 2528
- 2024: 2834
- 2026: 875

## 拒收原因

- `invalid_or_missing_undergraduate_major_code`: 808

## 输出文件

- 清洗事件表：`data\processed\policy_documents\undergraduate_major_official_events_20260612_v5.csv`
- 专业级汇总：`data\processed\policy_documents\undergraduate_major_official_event_summary_20260612_v5.csv`
- 拒收行表：`data\processed\policy_documents\undergraduate_major_official_events_rejected_20260612_v5.csv`
- Manifest：`data\processed\policy_documents\undergraduate_major_official_events_manifest_20260612_v5.json`
