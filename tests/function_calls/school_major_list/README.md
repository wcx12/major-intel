# school_major_list

## 1. 工具原理

`school_major_list` 查询某学校在本地库记录的开设专业列表。它先通过 `school_lookup` 解析学校实体，再查询学校-专业关系和专业基础表，返回该校开设专业清单。

这个工具的核心语义是“学校开设专业目录”，不是某省某年招生计划。已有审计重点包括：学校关联键混用、院系专业源补充、同号不同校、分类筛选、同名跨层次专业、危险简称和 `limit` 边界。

更详细的工具说明见：

```text
docs/specs/school-major-list-tool.md
```

## 2. 输入与输出

- 主要输入：`school_text`、`major_category`、`limit`。
- 关键输出：`data.school`、`data.majors`。
- 重要字段：`status`、`normalized_slots.school_id`、`normalized_slots.school_name`、`data_gaps`、`warnings`、`source_tables`。
- 明确边界：不要向 `school_major_list` 传 `major_text`。如果用户问“某学校是否开设某专业”，应调用 `school_major_profile`；如果用户问“某专业有哪些学校开设”，应调用 `major_school_list`。

## 3. 状态语义

- `ok`：学校实体解析成功，且本地库命中至少一条开设专业记录。
- `not_found`：学校实体解析成功，但本地库未命中该校开设专业记录。
- `needs_clarification`：学校名称缺失、学校简称存在歧义，或 `limit` 不是正整数。
- `error`：工具运行异常或 dispatcher 层调用失败。

## 4. 测试范围

当前目录维护 function-call 级测试资料，重点不是重复普通单测，而是保留真实库边界样例和可审计入口。

- `boundary_cases.json`：真实 MySQL 审计用例清单，覆盖学校键混用、院系专业源、同号不同校、分类筛选、同名跨层次专业、危险简称和 limit 边界。
- `test_boundary_cases_manifest.py`：校验 `boundary_cases.json` 的结构、`case_id` 唯一性和关键风险场景是否还在。
- 审计脚本会调用工具本身，同时用独立 oracle SQL 做对照，不只是检查“有返回”。

主要判定维度：

- `status_mismatch`：工具状态和 case 的 `expected_status` 不一致。
- `key_mismatch`：oracle 通过 `code/school_id` 双键发现更多专业，工具漏召回。
- `category_filter_gap`：`major_category` 没覆盖应覆盖的门类、专业类或专业名字段。
- `catalog_noise`：同名跨层次目录导致本科/高职语义混淆。
- `limit_truncated`：正数 limit 截断结果，属于可接受现象。
- `input_validation_gap`：无效 limit 等参数没有被工具入口拦截，属于失败。

## 5. 测试结果

- 最近运行日期：2026-06-02
- 运行命令：`python -m unittest discover tests/function_calls/school_major_list -p "test_*.py"`
- 真实库审计命令：

```powershell
python scripts/evaluate_school_major_list_boundaries.py `
  --jsonl-report reports/school_major_list_boundary_eval_20260602.jsonl `
  --markdown-report reports/school_major_list_boundary_eval_20260602.md
```

- 最近一次真实库审计结果：用例总数 `36`，通过 `35`，失败 `1`，需要复核 `0`。

剩余 1 个失败是暂不处理项：

- `huada_alias`：危险简称“华大”仍会误命中，需要后续统一处理学校简称歧义策略。

`cupl_limit_0` 和 `cupl_limit_negative` 已改为期望通过：工具应返回 `needs_clarification`，并要求补正 `limit`。

## 6. 已知风险与待改善

- 危险简称仍需要统一实体歧义策略，例如“华大”这类可能误命中的简称。
- `school_major_list` 只能说明学校维度开设专业，不能替代省份、年份、科类维度的招生计划。
- `school_major_list` 不承担学校+专业精确关系查询；Agent 工具选择应避免把具体专业名作为 `major_text` 塞给该工具。
- `major_category` 筛选需要持续防止本科/高职目录噪声混入。
- 如果未来 `huada_alias` 被修掉，需要同步更新 `boundary_cases.json`、`test_boundary_cases_manifest.py`、`docs/specs/school-major-list-tool.md` 和本文档的当前基线。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- Schema：[scripts/retrieval_function_registry.py](../../../scripts/retrieval_function_registry.py)
- 专属测试：[tests/function_calls/school_major_list/test_boundary_cases_manifest.py](test_boundary_cases_manifest.py)
- 边界用例：[tests/function_calls/school_major_list/boundary_cases.json](boundary_cases.json)
- 规格文档：[docs/specs/school-major-list-tool.md](../../../docs/specs/school-major-list-tool.md)
