# data_gap_detection

## 1. 工具原理

`data_gap_detection` 根据问题类型和当前可用字段判断还缺哪些数据。它不查业务事实表，主要用于让上层 agent 明确本地库无法支撑哪些回答维度。

当前实现基于 `GAP_REGISTRY` 返回结构化 `gap_items`。每个缺口会说明 `gap_key`、中文标签、缺失字段、是否可通过网页补全、优先来源类型和证据要求。这个结果可以直接交给 `web_gap_fill` 做后续官方网页证据补全。

## 2. 输入与输出

- 主要输入：`question_type`、`available_fields`。
- 关键输出：`missing_items`、`gap_items`、`supported_question_types`。
- 重要字段：`gap_key`、`missing_fields`、`resolvable_by_web`、`preferred_source_types`、`evidence_requirements`。
- 重要说明：未知问题类型不能返回空缺口并伪装成功。

## 3. 状态语义

- `ok`：已知问题类型且没有缺口。
- `partial`：已知问题类型但存在缺口。
- `needs_clarification`：未知问题类型，并返回 `supported_question_types`。
- `not_found`：当前工具通常不使用该状态。

## 4. 测试范围

- 已覆盖未知问题类型返回 `needs_clarification`，不再返回 `ok + missing_items=[]`。
- 已覆盖已知问题类型存在缺口时返回 `partial`。
- 已覆盖 `school_major_profile` 的多项缺口，包括转专业政策、校专业级薪资、就业地域等。
- 已通过 `test_gap_detection_registry.py` 覆盖核心字段空列表和工具结果缺口识别。

## 5. 测试结果

- 最近运行日期：2026-06-03
- 运行命令：`python -m pytest tests -q`
- 运行结果：`784 passed in 72.87s`

## 6. 已知风险与待改善

- 需要持续保持 `GAP_REGISTRY` 与业务工具同步。
- 第一版只重点覆盖高频志愿缺口，后续应逐步把 27 个工具的核心字段和缺口类型补齐。
- `missing_items` 保留为兼容字段；新 Agent 应优先读取 `gap_items`。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 通用测试：[tests/test_retrieval_tools.py](../../test_retrieval_tools.py)
- 缺口注册表测试：[tests/test_gap_detection_registry.py](../../test_gap_detection_registry.py)
- 网页补全工具：[tests/function_calls/web_gap_fill/README.md](../web_gap_fill/README.md)
