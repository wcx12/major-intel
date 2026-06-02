# school_major_list 测试与审计说明

这个目录收纳 `school_major_list` 的 function-call 级测试资料。它和通用单测不同：这里重点维护真实库边界样例、人工判定语义和可重复审计入口。

工具能力、输入输出、数据来源和 `major_category` 语义边界见：

```text
docs/specs/school-major-list-tool.md
```

## 文件说明

- `boundary_cases.json`：真实 MySQL 审计用例清单。覆盖学校键混用、院系专业源、同号不同校、分类筛选、同名跨层次专业、危险简称和 limit 边界。
- `test_boundary_cases_manifest.py`：轻量单测，校验 `boundary_cases.json` 的结构、case_id 唯一性和关键风险场景是否还在。
- `README.md`：说明本目录的测试目的、运行方式、审计基线和剩余已知问题。

## 覆盖重点

1. 学校关联键混用：`edu_school_major.school_id` 可能存 `edu_university.code`，也可能存 `edu_university.school_id`。
2. 院系专业源补充：杭电等学校的开设专业在 `edu_university_department_major` 中更完整，必须通过院系网址域名校验后再使用。
3. 同号不同校：同一个数字在不同表里可能表示不同学校，不能跨表盲目双键合并。
4. 分类筛选：`major_category` 应覆盖专业名、门类、专业类等字段，但不能把高职目录噪声混进本科专业。
5. 专业代码后缀：`080904` 应能和目录中的 `080904K` 归一匹配，`T/TK` 同理。
6. 负样例：危险简称、无效 limit 等已知未修问题要留在审计里持续暴露。

## 用例结构

`boundary_cases.json` 的每条 case 至少包含：

| 字段 | 说明 |
|---|---|
| `case_id` | 稳定用例 id，用于报告、断言和问题追踪。 |
| `school` | 输入给工具的学校文本。可以是全称，也可以是故意保留的歧义简称。 |
| `major_category` | 可选筛选词，用来覆盖专业名、专业类、门类和宽泛关键词。 |
| `limit` | 返回条数上限。`0` 和负数目前作为已知暂缓项保留。 |
| `expected_status` | 可选。用于标注 `not_found`、`needs_clarification` 等预期状态。 |
| `note` | 人工解释：这条 case 为什么存在、对应哪类风险、是否暂不修。 |

## 运行命令

只检查本目录测试资产：

```powershell
python -m unittest discover tests/function_calls/school_major_list -p "test_*.py"
```

运行 `school_major_list` 审计单测：

```powershell
python -m unittest tests.test_school_major_list_boundary_audit
```

连接本地 `.env` 数据库跑完整真实库审计：

```powershell
python scripts/evaluate_school_major_list_boundaries.py `
  --jsonl-report reports/school_major_list_boundary_eval_20260602.jsonl `
  --markdown-report reports/school_major_list_boundary_eval_20260602.md
```

脚本默认读取：

```text
tests/function_calls/school_major_list/boundary_cases.json
```

也可以显式指定另一份用例清单：

```powershell
python scripts/evaluate_school_major_list_boundaries.py `
  --cases tests/function_calls/school_major_list/boundary_cases.json
```

## 审计判定

真实库审计会调用工具本身，同时用独立 oracle SQL 做对照，不是只检查“有返回”。主要判定维度包括：

- `status_mismatch`：工具状态和 case 的 `expected_status` 不一致。
- `key_mismatch`：oracle 通过 `code/school_id` 双键发现更多专业，工具漏召回。
- `category_filter_gap`：`major_category` 没覆盖应覆盖的门类、专业类或专业名字段。
- `catalog_noise`：同名跨层次目录导致本科/高职语义混淆。
- `limit_truncated`：正数 limit 截断结果，属于可接受现象。
- `input_validation_gap`：无效 limit 等参数校验暂未完成。

## 当前基线

最近一次真实库审计结果：

```text
用例总数：36
通过：33
失败：3
需要复核：0
```

剩余 3 个失败是暂不处理项：

- `huada_alias`：危险简称“华大”仍会误命中，需要后续统一处理学校简称歧义策略。
- `cupl_limit_0`：`limit=0` 仍未提前做参数校验。
- `cupl_limit_negative`：`limit=-1` 仍可能进入 SQL 层或返回错误。

如果未来这 3 个暂缓项被修掉，需要同步更新：

- `boundary_cases.json` 中的 `expected_status` 和 `note`。
- `tests/function_calls/school_major_list/test_boundary_cases_manifest.py` 里的暂缓项断言。
- `docs/specs/school-major-list-tool.md` 和本 README 的当前基线。

## 新增用例原则

新增 case 时优先覆盖一种明确风险，而不是堆砌学校名单。建议每条 case 至少说明：

- 为什么选择这个学校或分类词。
- 它对应哪类历史 bug 或潜在误召回。
- 是否是期望失败，如果是，note 里要写明原因和是否暂不修。
