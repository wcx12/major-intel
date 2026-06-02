# school_profile

## 1. 工具原理

`school_profile` 查询学校层面的画像信息。它先复用 `school_lookup` 解析学校，再汇总学校基础信息、学科评估、双一流和学校层面就业摘要等信息。

## 2. 输入与输出

- 主要输入：`school_text`。
- 关键输出：`school`、`subject_evals`、`dual_class`、`latest_employment`。
- `latest_employment` 是学校级最新就业/升学摘要；如果没有记录会返回 `{}`，如果只有年份且 `employment_data`、就业率、升学率、薪资、行业/地域/雇主等核心字段都为空，会在 `data_gaps` 标出“学校级就业/升学摘要有效字段”。
- 重要说明：学校层面就业信息不能直接当作某专业就业结论。

## 3. 状态语义

- `ok`：学校实体解析成功，并返回学校画像结构。
- `not_found`：学校实体未命中。
- `needs_clarification`：学校名称缺失、简称存在歧义，或 fallback 检索命中多个候选。
- 当前实现对“学校已解析但就业摘要缺失”的情况保持 `ok`，同时通过 `data_gaps` 和 `warnings` 说明缺口；是否改为 `partial` 需要后续统一画像类工具的状态语义。

## 4. 测试范围

已覆盖学校解析失败传播、模糊学校不能被压成第一候选、别名来源表合并、就业摘要缺失和就业摘要空字段。后续可继续覆盖学科评估缺失、双一流缺失和真实库样本漂移。

## 5. 测试结果

- 最近运行日期：2026-06-02。
- 运行命令：`python -m unittest tests.test_retrieval_tools`
- 运行结果：57 tests OK。

## 6. 已知风险与待改善

- 学校层面数据和专业层面数据必须保持边界：本工具不能回答某校某专业就业结论。
- 缺少就业摘要时当前不会把整体状态降为 `partial`，而是保留学校画像并标记 `data_gaps`。
- README 与实现已统一为 `latest_employment` 字段；不要再使用旧字段名 `employment` 或不存在的 `available_fields`。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 来源说明：[docs/specs/retrieval-function-calls.md](../../../docs/specs/retrieval-function-calls.md)
