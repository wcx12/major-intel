# major_school_list

## 1. 工具原理

`major_school_list` 查询开设某专业的学校列表。它先通过 `major_lookup` 解析专业，再查学校专业关系和学校基础表，可按省份、学校层级过滤。

## 2. 输入与输出

- 主要输入：`major_text`、可选 `province_filter`、可选 `school_level_filter`、可选 `limit`。
- 关键输出：`major`、`schools`。
- 重要字段：学校名称、省份、学校层级、学校类型、专业层级。

## 3. 状态语义

- `ok`：专业命中且存在学校记录。
- `not_found`：专业命中但学校列表为空，或专业未命中。
- `needs_clarification`：专业输入缺失。
- `partial`：当前工具不使用该状态。

## 4. 测试范围

当前专项测试集中在本目录：

- `boundary_cases.json`：真实 MySQL 审计用例清单。覆盖学校关联键混用、专业别名、模糊专业、专业不存在、省份归一化、985/双一流筛选、同名跨层次 warning 和 limit 边界。
- `test_boundary_cases_manifest.py`：轻量单测，校验用例结构、case_id 唯一性和关键风险场景是否还在。
- `test_boundary_audit.py`：轻量单测，校验审计脚本、oracle SQL 和分类逻辑。

真实库审计由 `scripts/evaluate_major_school_list_boundaries.py` 执行。它会调用 `major_school_list`，再用独立 oracle SQL 对照返回学校数、漏召回样本、状态、warning 和 data_gaps。

## 5. 测试结果

- 最近运行日期：2026-06-02。
- 单测命令：

```powershell
python -m pytest tests\function_calls\major_school_list\test_boundary_cases_manifest.py tests\function_calls\major_school_list\test_boundary_audit.py tests\test_retrieval_tools.py -q
```

- 单测结果：`78 passed`。
- 真实库审计命令：

```powershell
python scripts\evaluate_major_school_list_boundaries.py --jsonl-report reports\major_school_list_boundary_eval_20260602.jsonl --markdown-report reports\major_school_list_boundary_eval_20260602.md
```

- 真实库审计结果：16 条用例，16 条通过，0 条失败。

## 6. 已知风险与待改善

- 已修复 `edu_school_major.school_id` 同时匹配 `edu_university.code` 和 `edu_university.school_id` 时的漏召回。
- 已修复 `province_filter` 常见省份后缀归一化，例如 `浙江省` 会按 `浙江` 查询。
- 已修复 `major_lookup` 对同名跨层次专业产生的 warning 传播。
- 已修复 `limit=0` / `limit<0` 的结构化参数校验。
- 需要持续保护 `school_level_filter` 只使用有效学校层级字段。
- 需要防止把开设学校列表误当成招生计划。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 真实库审计脚本：[scripts/evaluate_major_school_list_boundaries.py](../../../scripts/evaluate_major_school_list_boundaries.py)
- 独立 oracle SQL：[scripts/major_school_list_oracles.py](../../../scripts/major_school_list_oracles.py)
- 通用测试：[tests/test_retrieval_tools.py](../../test_retrieval_tools.py)
