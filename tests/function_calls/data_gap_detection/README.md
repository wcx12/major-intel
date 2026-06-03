# data_gap_detection

## 1. 工具原理

`data_gap_detection` 根据问题类型和当前可用字段判断还缺哪些数据。它不查业务事实表，主要用于让上层 agent 明确数据缺口。

## 2. 输入与输出

- 主要输入：`question_type`、`available_fields`。
- 关键输出：`missing_items`、支持的问题类型、缺口说明。
- 重要说明：未知问题类型不能返回空缺口并伪装成功。

## 3. 状态语义

- `ok`：已知问题类型且没有缺口。
- `partial`：已知问题类型但存在缺口。
- `needs_clarification`：未知问题类型。
- `not_found`：当前工具通常不使用该状态。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖未知问题类型、空 available_fields、部分字段已具备、无缺口和多问题类型。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 需要保持问题类型列表与业务工具同步。
- 需要补充未知类型不返回 `ok` 的专属回归测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 通用测试：[tests/test_retrieval_tools.py](../../test_retrieval_tools.py)
