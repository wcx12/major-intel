# major_profile

## 1. 工具原理

`major_profile` 查询专业通用画像。它先复用 `major_lookup` 解析专业，再返回专业门类、专业类、修业年限、学位和通用就业方向等信息。

## 2. 输入与输出

- 主要输入：`major_text`。
- 关键输出：`major`、专业基础字段、就业描述清洗字段。
- 重要说明：这是专业通用画像，不代表某校该专业的真实就业或培养质量。

## 3. 状态语义

- `ok`：专业实体解析成功。
- `not_found`：专业实体未命中。
- `needs_clarification`：缺少 `major_text`。
- `partial`：当前工具通常不使用该状态。

## 4. 测试范围

已覆盖标准专业、专业代码、确认别名、歧义别名、宽泛词、未命中、画像字段缺口和来源说明。

重点边界：

- `major_profile` 必须继承 `major_lookup` 的歧义/层次 warning。
- 歧义输入不能为了画像查询把候选列表压窄到 1 条。
- 薪资和就业方向为空、为 `0` 或为 `暂无数据` 时必须标注 `data_gaps`。
- `师范`、`中外合作办学` 等后缀归一上下文必须保留在 `normalized_slots` 或 warning 中。
- 超长就业方向文本必须压缩到可控长度并标 warning。
- 通用专业画像不能替代某校某专业就业或培养质量结论。

## 5. 测试结果

- 最近运行日期：2026-06-02。
- 运行命令：

```powershell
python -m unittest tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_preserves_lookup_cross_level_warning tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_keeps_clarification_candidates_wide tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_marks_missing_salary_and_job_direction_gaps tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_filters_placeholder_job_direction_as_gap tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_preserves_normalized_suffix_context tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_compacts_long_job_direction_text
python -m unittest tests.test_retrieval_tools
python -m unittest discover -s tests
```

- 运行结果：新增 6 条回归测试通过；`tests.test_retrieval_tools` 共 58 条通过；全量 unittest discover 共 545 条通过。
- Live 审计报告：[reports/major_profile_capability_audit_20260602.md](../../../reports/major_profile_capability_audit_20260602.md)。

## 6. 已知风险与待改善

- 仍需防止把通用专业就业方向误写成学校专业结论。
- 当前就业方向长文本处理是截断摘要片段，不是语义级总结；如需更漂亮的摘要，应放到上层 agent 或专门清洗流程。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- SQL 构造：[scripts/local_retrieval_mvp.py](../../../scripts/local_retrieval_mvp.py)
