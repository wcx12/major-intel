# 学校就业摘要数据质量审计

日期：2026-06-02

## 审计目标

判断 `edu_university_employment` 是否足以支撑 `school_profile` 和 `employment_summary` 的学校级就业/升学回答，并区分两类问题：

- 数据表本身缺记录。
- 工具没有取出已有的有效字段，导致误报缺口。

## 数据口径

有效就业摘要字段包括：

- `employment_data`
- `employment_rate`
- `further_study_rate`
- `avg_salary`
- `top_employment_industries`
- `top_employment_regions`
- `top_employers`

只有 `year` 而上述字段都为空的记录，不能支撑就业质量判断。

## 真实库摘要

本次从本地 MySQL 读取：

| 指标 | 数量 |
|---|---:|
| 学校基础表学校数 | 3003 |
| 就业摘要表记录数 | 2869 |
| 至少有一条就业摘要记录的学校数 | 2336 |
| 完全没有就业摘要记录的学校数 | 667 |
| 有有效就业字段的就业摘要记录数 | 2869 |
| 只有年份、核心字段为空的就业摘要记录数 | 0 |

结论：就业摘要表内已有记录整体不是“只有年份”的问题；更大的缺口是 667 所学校没有任何就业摘要记录。

## 重要修正

旧版 `school_profile` 只读取 `employment_rate`、`further_study_rate`、`avg_salary`、行业/地域/雇主字段，没有读取 `employment_data`。

这导致类似 `北京邮电大学` 的记录被误判为“只有年份”：该校 2026 年记录的摘要列为空，但 `employment_data` 中有保研率、院士数等结构化字段。

本轮已修正：

- `build_latest_employment_sql` 增加 `employment_data`。
- `school_profile` 解码 `employment_data`。
- `school_profile` 缺口判断把 `employment_data` 计入有效字段。
- `employment_summary` 有记录但核心字段全空时返回 `partial`。

## 抽样结果

| 学校 | `school_profile` 当前判断 | 说明 |
|---|---|---|
| 北京邮电大学 | `ok`，无就业缺口 | 2026 年记录有 `employment_data` |
| 杭州电子科技大学 | `ok`，无就业缺口 | 2025 年记录有 `employment_data` 和升学率 |
| 西安电子科技大学 | `ok + data_gaps=["学校级就业/升学摘要"]` | 就业摘要表没有该校记录 |

## 缺记录样本

以下样本来自“学校基础表存在，但就业摘要表没有记录”的学校集合：

| 学校 | 省份 | 城市 |
|---|---|---|
| 上海中医药大学 | 上海 | 浦东新区 |
| 上海公安学院 | 上海 | 浦东新区 |
| 中国人民大学 | 北京 | 海淀区 |
| 三亚城市职业学院 | 海南 | 三亚市 |
| 上海工艺美术职业学院 | 上海 | 嘉定区 |

这里不代表这些学校没有就业数据，只表示当前本地库 `edu_university_employment` 尚未接入。

## 建议

1. 优先补高频本科院校的就业摘要记录，例如本次审计暴露的 `西安电子科技大学`。
2. 对没有就业摘要的 667 所学校按学校层次、是否 985/211/双一流、用户高频度排序，分批补数据。
3. 保留 `employment_data`，不要只依赖摘要列；有些学校的有效信息在 JSON 字段里。
4. 上层回答就业问题时优先调用 `employment_summary`；`school_profile` 只能作为学校画像中的就业摘要线索。
