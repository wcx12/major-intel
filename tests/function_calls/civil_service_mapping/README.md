# civil_service_mapping

## 1. 工具原理

`civil_service_mapping` 查询专业与考公岗位方向的映射线索。它复用岗位搜索结果，并整理专业、岗位和缺口信息。

## 2. 输入与输出

- 主要输入：`major_text`。
- 可选输入：年份、省份、limit。
- 关键输出：专业信息、岗位方向、岗位样本、风险提示。

## 3. 状态语义

- `ok`：命中岗位映射或岗位样本。
- `not_found`：专业未命中或没有岗位样本。
- `needs_clarification`：专业输入缺失。
- `partial`：仅有岗位文本线索，不能正式判断可报。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖专业未命中、岗位为空、年份省份过滤、上游 role search 状态传播。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 考公可报必须看岗位表正式专业、学历、学位、政治面貌等条件。
- 需要补充“文本命中不等于正式可报”的 warnings 测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 上游工具：`civil_service_role_search`
