# school_major_profile

## 1. 工具原理

`school_major_profile` 查询“某学校某专业”的证据链画像。它组合学校解析、专业解析、院系专业目录、招生计划、录取历史、专业组、学科评估、双一流和就业摘要等信息。

## 2. 输入与输出

- 主要输入：`school_text`、`major_text`，可选 `province`、`subject_type`、`year`。
- 关键输出：`school`、`major`、`school_major_evidence`、`evidence_summary`、`evidence_gaps`。
- 重要说明：需要区分院系目录证据、招生计划证据和录取证据。

## 3. 状态语义

- `ok`：证据链足以支持学校专业关系。
- `partial`：仅有部分证据或上下文证据不足。
- `not_found`：学校或专业未命中，或无有效证据。
- `needs_clarification`：学校或专业输入缺失或歧义。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖原始招生专业名、目录证据、计划证据、录取证据、上下文不足、证据缺口和状态合成。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 这是高风险组合工具，最需要避免“无证据但下结论”。
- 需要补充真实库 smoke，确认各证据表能正确联动。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 设计文档：[docs/specs/retrieval-function-calls.md](../../../docs/specs/retrieval-function-calls.md)
