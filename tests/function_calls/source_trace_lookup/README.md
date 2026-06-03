# source_trace_lookup

## 1. 工具原理

`source_trace_lookup` 查询每个 function call 的来源表、数据口径和可信度说明。它读取工具内部 `_SOURCE_TRACE_REGISTRY`，不直接查业务数据库。

## 2. 输入与输出

- 主要输入：可选 `tool_name`。
- 关键输出：指定工具或全部工具的来源说明。
- 重要字段：`source_tables`、`scope_notes`、`reliability`。

## 3. 状态语义

- `ok`：返回指定工具或全部工具来源说明。
- `not_found`：指定工具未登记来源说明。
- `needs_clarification`：当前工具通常不使用该状态。
- `partial`：当前工具不使用该状态。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖查询单个工具、查询全部工具、未知工具、registry 与 27 个 schema 对齐。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 需要防止新增工具时忘记登记来源说明。
- 需要补充来源说明字段完整性测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- Registry：[scripts/retrieval_function_registry.py](../../../scripts/retrieval_function_registry.py)
