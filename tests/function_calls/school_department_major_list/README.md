# school_department_major_list

## 1. 工具原理

`school_department_major_list` 查询学校院系和院系下专业目录。它先解析学校，可选解析专业，再查询院系和院系专业关系。

## 2. 输入与输出

- 主要输入：`school_text`。
- 可选输入：`major_text`、`department_keyword`、limit。
- 关键输出：院系列表、院系下专业列表。

## 3. 状态语义

- `ok`：命中院系或专业目录。
- `not_found`：没有院系专业记录。
- `needs_clarification`：学校输入缺失或歧义。
- `partial`：当前工具通常不使用该状态。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖内部 `school_id` 使用、专业过滤、院系关键词过滤、空结果。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 需要避免混用学校代码和内部 `school_id`。
- 需要补充院系名称变化和专业名称不标准的测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
