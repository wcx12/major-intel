# score_to_rank

## 1. 工具原理

`score_to_rank` 将省份、科类、分数和年份转换为一分一段位次区间。核心数据来自 `edu_score_rank`。

## 2. 输入与输出

- 主要输入：`province`、`subject_type`、`score`，可选 `year`。
- 关键输出：`rank_range`、同分人数、匹配年份和匹配科类。
- 重要字段：`matched_subject_type` 用于提示传统文理科和新高考科类映射。

## 3. 状态语义

- `ok`：命中一分一段记录。
- `not_found`：没有对应记录。
- `needs_clarification`：缺省份、科类或分数。
- `partial`：当前工具不使用该状态。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖缺槽、未知省份、理科映射物理、文科映射历史、年份为空、边界分数、未命中。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 需要验证不同省份科类口径差异。
- 需要避免跨省、跨科类、跨年份比较。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 数据表：`edu_score_rank`
