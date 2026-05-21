# Major Intel 检索 Function Call 工具规划

## 阅读说明

本文定义后续 agent 可以调用的检索工具。这里的 function call 不是按用户自然语言问法拆分，而是按稳定的底层检索能力拆分。用户可以问很多种问题，但 agent 应该把问题解析成槽位，然后自动选择一个或多个工具组合调用。

目标是先把所有需要制作的工具列完整，再分阶段实现。第一阶段只做核心高频能力，但文档会保留完整工具表，避免后续遗漏。

## 总体调用流程

```text
用户自然语言问题
  -> agent 识别意图和槽位
  -> 判断是否缺少关键信息
  -> 调用一个或多个检索 function
  -> function 查询本地 MySQL、缓存或缺口队列
  -> function 返回结构化 JSON、口径说明、缺失项
  -> agent 组织最终回答
```

工具层必须坚持三个原则：

1. 工具只返回可追踪的结构化事实、口径说明和缺口，不替用户做无证据判断。
2. 工具缺少必要参数时返回 `needs_clarification`，不猜省份、科类、年份、学校或专业。
3. 工具必须区分学校级、专业通用级、校专业级、招生专业组级、录取统计级数据口径。

## 通用输出结构

所有工具尽量返回统一外壳，便于 agent 合并结果。

```json
{
  "tool_name": "school_lookup",
  "status": "ok",
  "input": {},
  "normalized_slots": {},
  "data": {},
  "scope_notes": [],
  "data_gaps": [],
  "needs_clarification": [],
  "source_tables": [],
  "warnings": []
}
```

字段含义：

| 字段 | 含义 |
|---|---|
| `tool_name` | 工具名 |
| `status` | `ok`、`not_found`、`needs_clarification`、`partial`、`error` |
| `input` | 原始输入 |
| `normalized_slots` | 规范化后的学校、专业、省份、科类、分数、位次等 |
| `data` | 工具返回的结构化结果 |
| `scope_notes` | 数据口径说明 |
| `data_gaps` | 本地库缺失但回答该问题需要的数据 |
| `needs_clarification` | 需要追问用户的槽位 |
| `source_tables` | 使用到的本地 MySQL 表 |
| `warnings` | 风险提示，例如“历史录取不代表录取保证” |

## Function Call 工具总表与实现状态

状态口径：

- `已完成`：已经有本地检索方法、function schema、dispatcher 支持、单元测试和基础烟测。
- `提前完成`：原计划不是第一阶段，但因为数据已经接入，已经先落地可调用工具。
- `部分完成`：底层数据或样本检索已具备，但还没有达到正式结论型工具的口径。
- `待制作`：尚未实现工具入口。

### 当前已落地能力快照

截至 2026-05-20，当前已经落地 23 个可调用检索入口：

```text
school_lookup
major_lookup
school_profile
major_profile
school_major_list
major_school_list
school_major_profile
score_to_rank
rank_to_school_match
rank_to_major_match
specialty_group_lookup
subject_requirement_lookup
school_department_major_list
plan_history
employment_summary
source_trace_lookup
transfer_policy_lookup
fee_and_campus_lookup
specialty_group_risk
admission_history
major_market_reference
civil_service_role_search
data_gap_detection
```

已经具备的核心能力：

- 能解析学校实体，并返回规范学校与候选学校。
- 能解析专业实体，并返回规范专业与候选专业；已接入数据库确认别名表 `entity_aliases`，例如“计科”会优先命中“计算机科学与技术”。
- 能查询学校画像、专业画像、学校开设专业、专业开设学校。
- 能查询学校 + 专业组合画像，并在校专业级就业、薪资、转专业、分流等数据不足时返回 `data_gaps`。
- 能把同省、同科类、同年份分数转换为位次区间。
- 能查询历年录取分和位次。
- 能按分数或位次返回学校层面的冲/稳/保参考，并在请求年份缺数时标记历史年份回退。
- 能按分数或位次 + 专业偏好返回学校-专业行层面的冲/稳/保参考，并保留专业大类、试验班、方向等变体提示。
- 能查询招生专业组、组内专业、选科要求，并基于组内构成做调剂风险初筛；明确不等于真实分流比例。
- 能查询学校院系专业关系、招生计划历史、学校级就业/升学摘要、转专业政策线索、学费线索和来源可信度说明。
- 能读取已接入的专业市场样本和考公岗位样本。
- 能识别当前问题还缺哪些本地数据，避免 agent 编造。

已经完成的基础设施能力：

- 已完成 `scripts/retrieval_tools.py` 工具层。
- 已完成 `scripts/retrieval_function_registry.py` function schema 注册层和 dispatcher。
- 已完成 `scripts/run_retrieval_smoke_cases.py` 本地批量烟测脚本。
- 已修复 MySQL CLI 长文本换行解析问题，避免专业介绍字段里的换行被拆成假候选记录。
- 已修复录取历史表和学校基础表的学校关联键问题：`edu_school_admission_stats.school_id` 应按 `edu_university.code + name` 关联，而不是按 `edu_university.school_id` 关联。

| 阶段 | 工具名 | 优先级 | 主要解决的问题 | 当前数据支持 | 实现状态 | 落地说明 |
|---|---|---:|---|---|---|---|
| 1 | `school_lookup` | P0 | 解析学校实体 | A | 已完成 | 已接入 `retrieval_tools.py`、`retrieval_function_registry.py`、烟测用例 |
| 1 | `major_lookup` | P0 | 解析专业实体 | A | 已完成 | 已接入工具层、function schema、烟测用例；常用专业简称已迁入 `entity_aliases`，短简称不再走危险模糊匹配 |
| 1 | `school_profile` | P0 | 给学校查概况 | A | 已完成 | 返回学校基础、双一流、学科评估、学校级就业升学 |
| 1 | `major_profile` | P0 | 给专业查概况 | A/B | 已完成 | 返回专业通用信息；明确不代表某校某专业就业 |
| 1 | `school_major_list` | P0 | 给学校查专业列表 | A | 已完成 | 按学校代码查询开设专业；明确不等于某省招生计划 |
| 1 | `major_school_list` | P0 | 给专业查开设学校 | A | 已完成 | 支持省份、学校层次粗筛；明确不等于当年招生计划 |
| 1 | `school_major_profile` | P0 | 学校 + 专业深度解读 | A/B | 已完成 | 能合并多口径信息并返回 `data_gaps`；数据不足时返回 `partial` |
| 1 | `score_to_rank` | P0 | 分数转位次 | A | 已完成 | 按省份、科类、年份转换位次区间 |
| 1 | `admission_history` | P0 | 查历年录取分和位次 | A | 已完成 | 支持学校、专业、省份、科类、年份筛选 |
| 1 | `data_gap_detection` | P0 | 识别缺失数据 | A | 已完成 | 返回当前问题缺少哪些本地数据，不编造 |
| 2 | `rank_to_school_match` | P0 | 按位次推荐学校 | A/B | 已完成 | 支持输入位次或分数，输出冲/稳/保学校桶；请求年份缺数时明确标记历史参考 |
| 2 | `rank_to_major_match` | P0 | 按位次和专业推荐学校专业 | A/B | 已完成 | 支持输入位次或分数 + 专业偏好，输出学校-专业行冲/稳/保桶 |
| 2 | `specialty_group_lookup` | P0 | 查专业组和组内专业 | A | 已完成 | 独立工具已落地；按学校、专业、省份、科类、年份、专业组代码筛选 |
| 2 | `plan_history` | P1 | 查招生计划变化 | A | 已完成 | 读取 `edu_qjjh_plan`；计划数不等于实际录取人数 |
| 2 | `subject_requirement_lookup` | P1 | 查选科要求 | A/B | 已完成 | 从专业组样本抽取去重选科要求，并保留原始记录 |
| 2 | `school_department_major_list` | P1 | 查院系和院系下专业 | A | 已完成 | 读取院系与院系专业表；不等于某省招生计划 |
| 3 | `specialty_group_risk` | P0 | 专业组调剂风险初筛 | B | 已完成 | 基于组内专业数量、计划数和目标专业占比初筛；真实分流比例仍列缺口 |
| 3 | `comparison_query` | P1 | 学校/专业/方案对比 | B | 待制作 | 需要复用已有画像工具组合 |
| 3 | `employment_summary` | P1 | 学校级就业升学摘要 | B | 已完成 | 学校级摘要已独立成工具；不能代表校专业级就业 |
| 3 | `major_market_reference` | P1 | 专业通用市场参考 | B | 提前完成 | 已接入 rysxai 市场样本表；明确不是校专业就业 |
| 3 | `source_trace_lookup` | P1 | 解释数据来源和可信度 | B/C | 已完成 | 已登记 23 个正式工具的数据表、口径和可信度等级 |
| 4 | `transfer_policy_lookup` | P1 | 查转专业政策 | C | 已完成 | 已接入 `rysxai_transfer_policies`；第三方线索必须官方复核 |
| 4 | `major_streaming_policy_lookup` | P1 | 查大类分流政策和比例 | C | 待制作 | 需要新增或确认分流比例数据源 |
| 4 | `civil_service_role_search` | P1 | 专业到考公岗位样本检索 | C | 提前完成 | 已接入考公岗位样本；仅表示岗位文本命中，不等于最终可报 |
| 4 | `civil_service_mapping` | P1 | 专业到考公岗位映射与可报判定 | C | 部分完成 | 样本检索已完成；正式映射、人工确认和可报判定未完成 |
| 4 | `fee_and_campus_lookup` | P2 | 学费、校区、住宿等 | B/C | 已完成 | 可返回学费线索；当前库无稳定校区字段时返回 `校区信息` 缺口 |
| 4 | `policy_rule_lookup` | P2 | 招生政策、批次规则 | C | 待制作 | 需要联网/人工确认后入库 |

未完成工具摘要：

- 第三阶段还缺 `comparison_query`。
- 第四阶段还缺 `major_streaming_policy_lookup`、`policy_rule_lookup`。
- `civil_service_mapping` 不是从零开始，但还没有达到正式可调用工具标准；当前只有 `civil_service_role_search` 样本检索。

## 分阶段实现路线

### 第一阶段：核心实体与基础检索

目标：先让 agent 能查学校、查专业、查学校专业组合、查录取历史，并能把缺失数据说清楚。

本阶段工具：

```text
school_lookup
major_lookup
school_profile
major_profile
school_major_list
major_school_list
school_major_profile
score_to_rank
admission_history
data_gap_detection
```

验收标准：

- 输入学校名，能返回规范化学校实体和候选列表。
- 输入专业名，能返回规范化专业实体和候选列表。
- 输入学校，能返回学校概况和专业列表。
- 输入专业，能返回专业概况和开设学校。
- 输入学校 + 专业，能返回校专业解读和缺失数据。
- 输入省份、科类、分数，能转成位次。
- 输入学校/专业/省份/科类，能查历年录取。
- 每个工具都有测试覆盖正常路径、缺参路径、未命中路径。

### 第二阶段：分数位次匹配与专业组

目标：覆盖高考报考最核心场景，也就是“我这个分数/位次能报什么”。

本阶段工具：

```text
rank_to_school_match
rank_to_major_match
specialty_group_lookup
plan_history
subject_requirement_lookup
school_department_major_list
```

验收标准：

- 输入省份、科类、位次，能输出冲稳保学校列表。
- 输入省份、科类、位次、专业偏好，能输出可报学校专业。
- 输入学校、专业、省份、年份，能查对应专业组和选科要求。
- 推荐结果必须带年份、位次、风险分层和“不保证录取”的提示。
- 缺少省份、科类、分数/位次时必须返回追问槽位。

### 第三阶段：风险解释与对比决策

目标：让系统从“查数据”升级到“辅助解释风险”，但仍然保持有证据边界。

本阶段工具：

```text
specialty_group_risk
comparison_query
employment_summary
major_market_reference
source_trace_lookup
```

验收标准：

- 能对专业组构成做冷门风险初筛，但不声称真实分流比例。
- 能对两个学校、两个专业、两个学校专业组合做维度化对比。
- 能输出学校级就业和专业通用市场参考，并明确口径。
- 能回答“这些数据来自哪里/可信度如何”的基础问题。

### 第四阶段：政策、就业深水区与人工/agent 补数

目标：覆盖转专业、大类分流、考公、政策规则等高风险问题。这一阶段需要新增数据表、联网 agent 和人工审核。

本阶段工具：

```text
transfer_policy_lookup
major_streaming_policy_lookup
civil_service_mapping
fee_and_campus_lookup
policy_rule_lookup
```

验收标准：

- 没有官方来源时不能给确定结论。
- 能把缺失政策写入 `data_gap_queue`。
- 联网 agent 抓取结果必须经过来源记录和可信度标注。
- 人工确认后的数据才能进入正式可回答范围。

## 第一阶段工具详细定义

### 1. `school_lookup`

用途：解析学校实体，返回最可能的学校和候选学校列表。

典型调用场景：

- 用户提到学校简称、全称、旧名。
- 其他工具需要先确认学校。

输入：

```json
{
  "school_text": "杭电",
  "limit": 5
}
```

输出 `data`：

```json
{
  "selected_school": {
    "school_id": "10124",
    "code": "10336",
    "name": "杭州电子科技大学",
    "province_name": "浙江",
    "city_name": "杭州市",
    "is211": false,
    "is_dual_class": false
  },
  "candidates": []
}
```

使用表：

```text
edu_university
entity_aliases
entity_alias_candidates
```

第一阶段可以先只用 `edu_university`，别名表后续补。

### 2. `major_lookup`

用途：解析专业实体，返回最可能的专业和候选专业列表。

当前实现状态：

- 已可按专业全称、专业代码、`special_id` 和专业名模糊匹配查询 `edu_major`。
- 已修复 MySQL CLI 长文本换行解析问题，专业介绍字段里的换行不会再被拆成假候选记录。
- 已接入数据库确认别名表 `entity_aliases`：例如“计科”优先命中“计算机科学与技术”，“软工”优先命中“软件工程”。
- 已新增 `entity_alias_candidates` 作为后续自动发现候选别名的沉淀表；候选别名仍需人工确认后才能进入正式解析链路。

输入：

```json
{
  "major_text": "计算机科学与技术",
  "limit": 5
}
```

输出 `data`：

```json
{
  "selected_major": {
    "code": "080901",
    "special_name": "计算机科学与技术",
    "level2_name": "工学",
    "level3_name": "计算机类"
  },
  "candidates": []
}
```

使用表：

```text
edu_major
entity_aliases
```

配套表：

```text
entity_alias_candidates
```

### 3. `school_profile`

用途：给一个学校返回学校概况。

输入：

```json
{
  "school_text": "杭州电子科技大学"
}
```

输出 `data`：

```json
{
  "school": {},
  "dual_class": [],
  "subject_evals": [],
  "latest_employment": {}
}
```

使用表：

```text
edu_university
edu_dual_class
edu_university_subject_eval
edu_university_employment
```

口径说明：

- 学校基础信息是学校级事实。
- 就业升学是学校级数据，不代表某个专业。

### 4. `major_profile`

用途：给一个专业返回专业概况、学习内容、就业方向和通用薪资参考。

输入：

```json
{
  "major_text": "机械设计制造及其自动化"
}
```

输出 `data`：

```json
{
  "major": {},
  "salary_reference": {},
  "job_directions": []
}
```

使用表：

```text
edu_major
```

口径说明：

- 薪资是专业通用参考，不代表某校某专业真实薪资。
- 就业方向是通用方向，不代表具体毕业去向。

### 5. `school_major_list`

用途：给学校查开设专业列表。

输入：

```json
{
  "school_text": "杭州电子科技大学",
  "major_category": "计算机类",
  "limit": 100
}
```

输出 `data`：

```json
{
  "school": {},
  "majors": []
}
```

使用表：

```text
edu_school_major
edu_university_department_major
edu_major
```

口径说明：

- 学校开设专业不等于某省当年招生专业。
- 如果用户带省份和年份，应该改用招生计划相关工具。

### 6. `major_school_list`

用途：给专业查开设学校列表。

输入：

```json
{
  "major_text": "计算机科学与技术",
  "province_filter": "广东",
  "school_level_filter": "双一流",
  "limit": 50
}
```

输出 `data`：

```json
{
  "major": {},
  "schools": []
}
```

使用表：

```text
edu_school_major
edu_university_department_major
edu_university
edu_university_subject_eval
```

### 7. `school_major_profile`

用途：给学校 + 专业生成深度检索结果。这个工具已经有 CLI MVP，后续需要改造成标准 function call 输出。

输入：

```json
{
  "school_text": "杭州电子科技大学",
  "major_text": "机械设计制造及其自动化",
  "province": "浙江",
  "subject_type": "物理",
  "year": 2025
}
```

输出 `data`：

```json
{
  "school": {},
  "major": {},
  "school_major": {},
  "subject_evals": [],
  "dual_class": [],
  "employment": {},
  "specialty_groups": []
}
```

使用表：

```text
edu_university
edu_major
edu_school_major
edu_university_subject_eval
edu_dual_class
edu_university_employment
edu_college_specialty_group
edu_specialty_group_major
```

### 8. `score_to_rank`

用途：把分数转换为某省某科类某年的位次。

输入：

```json
{
  "province": "广东",
  "subject_type": "物理",
  "score": 580,
  "year": 2025
}
```

输出 `data`：

```json
{
  "score": 580,
  "rank_range": {
    "highest_rank": 43000,
    "lowest_rank": 45500
  },
  "same_count": 2500
}
```

使用表：

```text
edu_score_rank
```

口径说明：

- 分数只在同省、同科类、同年份内有意义。
- 后续匹配应优先用位次。

### 9. `admission_history`

用途：查学校、专业、专业组的历年录取分数和位次。

输入：

```json
{
  "school_text": "杭州电子科技大学",
  "major_text": "计算机科学与技术",
  "province": "广东",
  "subject_type": "物理",
  "years": [2023, 2024, 2025]
}
```

输出 `data`：

```json
{
  "records": [
    {
      "year": 2025,
      "lowest_score": 580,
      "lowest_rank": 45000,
      "plan_count": 5,
      "batch": "本科批"
    }
  ]
}
```

使用表：

```text
edu_school_admission_stats
edu_university_score_config
edu_university_score_group
edu_university_score_special
```

### 10. `data_gap_detection`

用途：根据当前问题和已返回数据，判断哪些关键事实缺失。

输入：

```json
{
  "question_type": "school_major_profile",
  "school_text": "杭州电子科技大学",
  "major_text": "计算机科学与技术",
  "available_fields": [
    "school_basic",
    "major_basic",
    "subject_eval"
  ]
}
```

输出 `data`：

```json
{
  "missing_items": [
    "校专业级薪资分布",
    "校专业级Top对口公司",
    "转专业政策"
  ],
  "queue_candidates": []
}
```

使用表：

```text
data_gap_queue
```

第一阶段可以先返回内存中的缺口列表，第二阶段再落库。

## 第二阶段工具简要定义

### `rank_to_school_match`

输入省份、科类、位次或分数，返回冲稳保学校列表。

当前实现：

- 直接输入位次时，用该位次匹配学校；只输入分数时，先调用 `score_to_rank` 取保守位次。
- 查询 `edu_school_admission_stats` 的 `chong_rank`、`stable_rank`、`bao_rank`，映射为 `rush`、`stable`、`safe` 三个桶。
- 请求年份缺少录取数据时，可以回退到最近历史年份，并在 `reference.history_fallback` 和 `warnings` 中明确说明。
- 广东等历史记录缺少科类字段时，会把空科类作为谨慎历史参考纳入，并返回提示，不把它伪装成精确科类数据。
- 结果只代表学校层面历史位次参考，不代表某个专业或专业组一定可录取。

核心表：

```text
edu_school_admission_stats
edu_university
edu_score_rank
```

### `rank_to_major_match`

输入省份、科类、位次、专业偏好，返回可报学校专业列表。

当前实现：

- 先调用 `major_lookup` 解析专业，支持 `entity_aliases` 中已确认简称，例如“计科”。
- 直接输入位次时用位次匹配；只输入分数时先调用 `score_to_rank` 取保守位次。
- 查询 `edu_school_admission_stats` 中的专业录取行，按 `chong_rank`、`stable_rank`、`bao_rank` 映射为 `rush`、`stable`、`safe` 三个桶。
- 专业历史行会保留 `major_code`、`major_name`、`subject_requirement`、`plan_count`、`batch`、`remark`，方便后续继续查专业组和招生计划。
- 结果是历史专业行参考，不保证未来录取；专业大类、试验班、方向等变体需要结合当年招生计划继续确认。

核心表：

```text
edu_school_admission_stats
edu_major
entity_aliases
edu_university
edu_score_rank
```

### `specialty_group_lookup`

输入学校、专业、省份、年份，返回专业组和组内专业。

核心表：

```text
edu_college_specialty_group
edu_specialty_group_major
edu_university_plan_special_group
edu_university_plan_special
```

### `plan_history`

输入学校、专业、省份、年份，返回招生计划变化。

核心表：

```text
edu_university_plan_config
edu_university_plan_special_group
edu_university_plan_special
```

### `subject_requirement_lookup`

输入学校、专业、省份、年份，返回选科要求。

核心表：

```text
edu_specialty_group_major
edu_university_plan_special_group
edu_university_plan_special
```

### `school_department_major_list`

输入学校，返回院系和院系下专业。

核心表：

```text
edu_university_department
edu_university_department_major
```

## 第三阶段工具简要定义

### `specialty_group_risk`

基于专业组构成、用户目标专业、组内低偏好专业数量、计划数和录取位次做风险初筛。

注意：该工具不能声称真实调剂概率，也不能替代学校真实分流政策。

### `comparison_query`

把两个或多个对象拆成维度对比，例如学校层次、城市、专业实力、录取风险、就业升学、费用、数据缺口。

### `employment_summary`

输出学校级就业升学摘要。

注意：该工具不能把学校级就业率写成某专业就业率。

### `major_market_reference`

输出专业通用市场参考。

注意：该工具不能把专业通用薪资写成某校某专业真实薪资。

### `source_trace_lookup`

解释某个结论来自哪些表、哪些字段、是否有外部来源链接。

## 第四阶段工具简要定义

### `transfer_policy_lookup`

查转专业政策，需要新增官方来源表。

### `major_streaming_policy_lookup`

查大类分流政策和比例，需要新增官方来源表。

### `civil_service_mapping`

查专业对应考公岗位，需要新增专业代码到岗位的映射表。

### `fee_and_campus_lookup`

查学费、校区、住宿、生活成本。学费可部分来自招生计划表，住宿和生活成本需要额外来源。

### `policy_rule_lookup`

查省份批次规则、平行志愿、专项计划、体检限制等政策问题，需要高可信官方来源。

## 建议新增支撑表

为了让 function call 工具可追踪、可缓存、可人工兜底，建议逐步增加以下表。

| 表名 | 阶段 | 作用 |
|---|---|---|
| `query_logs` | 1 | 记录用户原始问题、识别槽位、调用工具 |
| `retrieval_cache` | 1 | 缓存工具调用结果 |
| `data_gap_queue` | 1 | 保存缺失数据和后续补数任务 |
| `entity_aliases` | 1 | 已落地；保存人工确认别名，当前 `major_lookup` 已使用 |
| `entity_alias_candidates` | 1 | 已落地；保存自动发现的候选别名，待人工确认后进入正式别名表 |
| `source_documents` | 3 | 保存网页、PDF、招生章程等来源 |
| `school_major_evidence` | 3 | 保存学校官网专业介绍和培养方案 |
| `transfer_policy_sources` | 4 | 保存转专业政策 |
| `major_streaming_sources` | 4 | 保存大类分流政策 |
| `civil_service_major_roles` | 4 | 保存专业到考公岗位映射 |

## 第一阶段实现建议

第一阶段建议创建一个工具层脚本或模块，例如：

```text
scripts/retrieval_tools.py
tests/test_retrieval_tools.py
```

同时逐步把现有 `scripts/local_retrieval_mvp.py` 中的逻辑拆出来复用。

实现顺序建议：

1. `school_lookup`
2. `major_lookup`
3. `school_profile`
4. `major_profile`
5. `school_major_list`
6. `major_school_list`
7. `school_major_profile`
8. `score_to_rank`
9. `admission_history`
10. `data_gap_detection`

每做一个工具，都必须先写测试，再实现。每个工具都要有丰富注释，尤其解释 SQL 关联字段和数据口径。

## Agent 调用策略示例

自然语言总入口的完整设计见 `docs/specs/natural-language-entrypoint.md`。本节只保留 function call 层面的调用示例。

用户问题：

```text
广东物理 580 想学计算机，有哪些稳一点的学校？
```

agent 应抽取：

```json
{
  "province": "广东",
  "subject_type": "物理",
  "score": 580,
  "major_text": "计算机",
  "risk_preference": "稳"
}
```

调用：

```text
score_to_rank
rank_to_major_match
admission_history
data_gap_detection
```

用户问题：

```text
杭州电子科技大学计算机怎么样？
```

agent 应抽取：

```json
{
  "school_text": "杭州电子科技大学",
  "major_text": "计算机"
}
```

调用：

```text
school_major_profile
admission_history
data_gap_detection
```

用户问题：

```text
这个专业组会不会被调剂到冷门专业？
```

如果缺少专业组、省份、年份，agent 应先追问，而不是直接调用工具生成判断。

```json
{
  "status": "needs_clarification",
  "needs_clarification": ["school_text", "province", "year", "group_code"]
}
```

## 验收清单

当前完成记录（2026-05-21）：

- 第一阶段 10 个 P0 工具已经全部实现。
- 第二阶段 `rank_to_school_match`、`rank_to_major_match`、`specialty_group_lookup`、`plan_history`、`subject_requirement_lookup`、`school_department_major_list` 已完成第一版，可覆盖位次匹配、专业组、招生计划、选科和院系专业关系。
- 第三阶段 `specialty_group_risk`、`employment_summary`、`major_market_reference`、`source_trace_lookup` 已完成第一版；`comparison_query` 仍待制作。
- 第四阶段 `transfer_policy_lookup`、`fee_and_campus_lookup` 已完成第一版；`major_streaming_policy_lookup`、`policy_rule_lookup` 仍待制作；`civil_service_mapping` 仍是部分完成。
- `major_market_reference` 和 `civil_service_role_search` 已经提前实现，用于读取已经接入的市场样本和考公岗位样本。
- 已完成 agent function schema 注册层：`scripts/retrieval_function_registry.py`。
- 已完成自然语言总入口离线规则第一版：`scripts/natural_language_entrypoint.py`，可把高频中文问题自动映射到 intent、slots 和工具计划。
- 已完成 DeepSeek function-call agent：`scripts/deepseek_retrieval_agent.py`，可让 LLM 基于同一套 function schema 自动选择本地工具。
- 已完成统一入口：`scripts/retrieval_agent_entrypoint.py`，可在 `auto` 模式下优先使用规则入口，并把复杂/未知问题交给 DeepSeek agent。
- 已完成统一入口缓存/日志/缺口队列存储层：`scripts/agent_query_storage.py`，可创建 `query_logs`、`retrieval_cache`、`agent_tool_traces`、`data_gap_queue`。
- 已完成本地批量烟测脚本：`scripts/run_retrieval_smoke_cases.py`。
- 已完成数据库别名初始化脚本：`scripts/setup_entity_aliases.py`，会创建/维护 `entity_aliases` 与 `entity_alias_candidates`。
- 已修复 MySQL CLI 长文本换行解析问题，`major_lookup` 不会再把专业介绍里的“关键词/课程列表”拆成假候选记录。
- 已完成 `major_lookup` 数据库别名解析，真实库验证“计科”返回“计算机科学与技术”，“软工”返回“软件工程”。
- 当前单元测试覆盖：`python -m unittest discover -s tests`，最近一次验证为 115 个测试通过；自然语言入口专项测试为 10 个场景，统一入口专项测试为 8 个场景，缓存/日志/缺口队列专项测试为 5 个场景。
- 当前烟测用例矩阵覆盖 23 个工具入口；完整真实库结构烟测 290/290 通过，新增 9 个工具 strict-target 烟测 27/27 通过且质量预期 0 miss。

第一阶段完成时应满足：

- 工具清单中第一阶段 10 个工具均可被本地代码调用。
- 每个工具都有输入 schema、输出 schema 和测试。
- 每个工具都能返回 `scope_notes` 和 `data_gaps`。
- 缺少必要参数时不会猜测，而是返回 `needs_clarification`。
- 不存在实体时返回 `not_found`，不生成事实结论。
- 分数匹配相关工具优先使用位次，不只用分数判断。
- 所有新增代码均遵守 `CONTRIBUTING.md` 的丰富注释要求。
