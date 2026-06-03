# civil_service_role_search

## 1. 工具原理

`civil_service_role_search` 按专业查询考公岗位样本。它先解析专业，再查岗位候选表和岗位原始表，返回可观察岗位文本线索。

## 2. 输入与输出

- 主要输入：`major_text`。
- 可选输入：年份、省份、limit。
- 关键输出：岗位列表、部门、职位名称、专业条件文本。

## 3. 状态语义

- `ok`：命中岗位样本。
- `not_found`：专业未命中或没有岗位样本。
- `needs_clarification`：专业输入缺失。
- `partial`：岗位文本命中但不足以正式判断可报。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖专业代码 K 后缀、年份省份过滤、岗位为空、专业未命中。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 岗位文本匹配不等于正式可报。
- 需要补充学历、学位、政治面貌等条件缺失提示测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 通用测试：[tests/test_retrieval_tools.py](../../test_retrieval_tools.py)
