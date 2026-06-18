# 高职专科专业设置备案明细与风险关联报告

- 源平台：https://zwfw.moe.gov.cn/zyyxzy/
- 覆盖年份：2013-2026（14 年）
- 官方专业点明细行数：814328
- 跨年去重专业数：2737
- 最新年份 2026 覆盖专业数：788
- API 完全重复自然键组数：125
- API 完全重复超额行数：125
- 可关联红/黄就业预警的高职专科专业数：121
- 可关联官方政策/停招/撤销/控制专业记录的高职专科专业数：196
- 行级就业预警关联数：244486
- 行级官方政策关联数：252845

## 输出文件

- 明细增强表：`data\processed\vocational_major_register\vocational_major_records_2013_2026_annotated.csv`
- 专业级关联汇总：`data\processed\vocational_major_register\vocational_major_risk_link_summary_2013_2026.csv`
- Manifest：`data\processed\vocational_major_register\vocational_major_risk_links_manifest_2013_2026.json`

## 使用说明

- `record_id` 是增强表唯一行 ID；`source_record_id` 保留原始自然键哈希，因此可用于识别教育部接口返回的重复自然键。
- `has_employment_high_risk_warning=true` 表示该高职专科专业在已抓取就业预警中出现过红牌或黄牌记录。
- `has_official_policy_warning=true` 表示该专业可按专业代码或专业名关联到已抓取的官方停招、撤销、低就业、控制专业审批等政策记录。
- 关联只使用高职高专/专科口径的就业预警和政策记录；本科口径保留在主数据集，不混入本表。
