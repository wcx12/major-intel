# comparison_query

## 1. 工具原理

`comparison_query` 对多个学校、专业或学校专业目标做结构化并列比较。它复用已有画像、录取、就业和市场样本工具，不直接替用户下最终选择。

## 2. 输入与输出

- 主要输入：`target_type`、`target_texts`。
- 可选输入：省份、科类、年份、分数、位次等上下文。
- 关键输出：多个目标的 supporting_results、data_gaps、warnings。

## 3. 状态语义

- `ok`：所有目标可比较且返回结构化结果。
- `partial`：部分目标缺数据或部分上游工具返回缺口。
- `not_found`：目标无法解析或没有可比较数据。
- `needs_clarification`：目标类型或目标文本缺失。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖 school/major/school_major 三类比较、缺目标、未知 target_type、上游 partial 合成。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 比较工具容易被误用为“直接推荐”。
- 需要补充 warnings 聚合和 data_gaps 合并测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
