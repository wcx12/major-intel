# admission_history

## 1. 工具原理

`admission_history` 查询学校或学校专业的历史录取记录。它可解析学校和专业，并按省份、科类、年份筛选录取历史。

## 2. 输入与输出

- 主要输入：可选 `school_text`、可选 `major_text`，以及省份、科类、年份。
- 关键输出：历史录取记录、分数、位次、年份。
- 重要说明：历史录取不代表未来录取保证。

## 3. 状态语义

- `ok`：命中完整上下文下的录取历史。
- `partial`：缺少省份或科类时只能返回宽泛样本。
- `not_found`：没有录取历史记录。
- `needs_clarification`：学校或专业输入歧义，或必要输入缺失。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖空 records 返回 `not_found`、缺省份科类返回 `partial`、学校专业解析传播、年份过滤。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 录取历史口径受批次、省份、科类、专业组影响。
- 需要补充无数据不返回 `ok` 的回归测试到专属目录。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 通用测试：[tests/test_retrieval_tools.py](../../test_retrieval_tools.py)
