# school_major_list 工具说明

## 目标

`school_major_list` 用来查询某所学校当前库中记录的开设专业列表，也可以用 `major_category` 做专业名、门类或专业类筛选。它返回的是“学校开设专业”口径，不是某省、某年份、某批次的招生计划。

这个工具适合回答：

- “杭州电子科技大学有哪些计算机相关专业？”
- “中国政法大学有没有法学类专业？”
- “电子科技大学开设哪些电子信息类专业？”

它不适合直接回答：

- “广东 2026 年能不能报这个专业？”这类问题应继续查招生计划、专业组和录取历史。
- “这个专业今年一定招生吗？”当前工具只能说明库中开设专业，不代表当年招生。
- “学校简称很模糊时是哪一所？”这种输入应返回 `needs_clarification`，不能强行选第一候选。

## 输入

```json
{
  "school_text": "杭州电子科技大学",
  "major_category": "计算机类",
  "limit": 100
}
```

字段说明：

| 字段 | 必填 | 说明 |
|---|---:|---|
| `school_text` | 是 | 学校全称、已确认别名或用户输入的学校文本。先经 `school_lookup` 规范化。 |
| `major_category` | 否 | 专业筛选词。可以是专业名、门类、专业类或宽泛关键词。 |
| `limit` | 否 | 返回条数上限。必须是正整数；`0`、负数或无法转成整数的值会返回 `needs_clarification`，不会进入 SQL 层。 |

## 输出

成功时返回统一工具外壳，核心数据在 `data` 中：

```json
{
  "tool_name": "school_major_list",
  "status": "ok",
  "normalized_slots": {
    "school": {
      "school_id": "10124",
      "code": "10336",
      "name": "杭州电子科技大学"
    },
    "major_category": "计算机类"
  },
  "data": {
    "school": {},
    "majors": [
      {
        "major_code": "080901",
        "major_name": "计算机科学与技术",
        "level_name": "本科",
        "menlei_name": "工学",
        "level3_name": "计算机类",
        "record_source": "edu_university_department_major"
      }
    ]
  },
  "scope_notes": [
    "学校开设专业不等于某省当年招生专业。"
  ],
  "source_tables": [
    "edu_university",
    "edu_school_major",
    "edu_university_department",
    "edu_university_department_major",
    "edu_major"
  ]
}
```

状态语义：

| 状态 | 含义 |
|---|---|
| `ok` | 找到学校，并召回至少 1 个符合条件的专业。 |
| `not_found` | 学校不存在，或学校存在但筛选后没有专业。 |
| `needs_clarification` | 学校输入命中多个候选、简称高度歧义，或 `limit` 不是正整数。 |
| `error` | 数据库查询或工具执行异常。 |

## 数据来源与召回顺序

当前实现会合并两类来源，但不会简单相加。

1. `edu_school_major`
   - 这是基础学校专业表。
   - 历史数据里 `edu_school_major.school_id` 既可能存 `edu_university.code`，也可能存 `edu_university.school_id`。
   - 因此查询会同时使用学校的 `code` 和内部 `school_id`，并继续保留 `school_name` 精确约束，避免同号不同校串数据。

2. `edu_university_department_major`
   - 这是院系专业表，对杭电等学校更完整。
   - 只有当院系网址域名能和学校官网域名匹配时，才把该来源纳入。
   - 如果某学校存在通过域名校验的院系来源，工具优先使用院系专业源；否则回退到 `edu_school_major`。

这样做是为了同时解决两个问题：一边避免漏召回真实专业，一边避免把同一个数字在不同表里的不同学校误合并。

## `major_category` 的语义边界

`major_category` 不是只匹配一个字段。它应覆盖以下几类用户表达：

| 用户表达 | 例子 | 匹配范围 |
|---|---|---|
| 专业名 | `软件工程`、`数字媒体技术` | `major_name` / `special_name` |
| 专业类 | `计算机类`、`电子信息类` | `edu_major.level3_name`，以及学校专业表中的分类字段 |
| 门类 | `工学`、`法学` | `edu_major.level2_name`，以及学校专业表中的门类字段 |
| 宽泛关键词 | `计算机`、`航空航天` | 专业名和分类字段的模糊匹配 |

同时它不能跨层次误匹配。例如本科专业 `080906 数字媒体技术` 不能因为高职目录里也有同名专业，就被归到“电子与信息大类”。所以目录关联优先按专业代码匹配，只有当来源记录没有专业代码时，才允许按专业名兜底。

专业代码匹配会做 `K/T/TK` 后缀归一：

- `080904` 可以匹配目录中的 `080904K`
- `080907` 可以匹配目录中的 `080907T`
- `080911` 可以匹配目录中的 `080911TK`

## 已知边界

当前仍保留 1 个暂缓项，并在审计用例里持续暴露：

| case_id | 问题 | 当前处理 |
|---|---|---|
| `huada_alias` | “华大”简称危险，可能指向多所学校。 | 暂不修，后续统一处理学校简称歧义策略。 |

`limit=0` 和 `limit=-1` 已在工具入口修复：返回 `needs_clarification`，`needs_clarification=["limit"]`，并且不会查询数据库。

除上述暂缓项外，最新真实库审计基线为 36 个用例中 35 个通过、1 个失败、0 个需要复核。

## 测试与审计

轻量测试：

```powershell
python -m unittest discover tests/function_calls/school_major_list -p "test_*.py"
python -m unittest tests.test_school_major_list_boundary_audit
python -m unittest tests.test_retrieval_tools
```

真实数据库审计：

```powershell
python scripts/evaluate_school_major_list_boundaries.py `
  --jsonl-report reports/school_major_list_boundary_eval_20260602.jsonl `
  --markdown-report reports/school_major_list_boundary_eval_20260602.md
```

审计脚本默认读取：

```text
tests/function_calls/school_major_list/boundary_cases.json
```

审计不是只检查“有没有返回”。它会把工具结果和独立 oracle SQL 对比，关注：

- 工具状态是否符合预期。
- 召回数量是否少于 oracle。
- 是否出现学校键混用导致的漏召回。
- `major_category` 是否覆盖该覆盖的分类字段。
- 是否混入高职同名目录噪声。
- 是否把已知暂缓项误判为通过。

## 维护原则

新增测试用例时优先覆盖一种明确风险，而不是堆学校名单。每条 case 建议写清：

- 这条 case 验证哪类历史 bug 或潜在误召回。
- 期望状态是什么，是否是暂缓项。
- 为什么这个学校或分类词能代表该风险。

修改 SQL 时至少跑三类验证：

```powershell
python -m unittest discover tests/function_calls/school_major_list -p "test_*.py"
python -m unittest tests.test_school_major_list_boundary_audit
python scripts/evaluate_school_major_list_boundaries.py `
  --jsonl-report reports/school_major_list_boundary_eval_20260602.jsonl `
  --markdown-report reports/school_major_list_boundary_eval_20260602.md
```

如果真实库审计出现新失败，先判断是数据缺口、参数校验、学校歧义、分类语义还是 SQL 召回问题，再决定修工具、修数据或把 case 标成明确暂缓项。
