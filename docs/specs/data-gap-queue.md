# 数据缺口队列设计

## 目标

`data_gap_queue` 用于记录当前数据库无法可靠回答的问题。

它的作用不是直接回答用户，而是把缺失数据转化为后续联网 agent 或人工复核可以执行的任务。

系统第一阶段必须做到：

```text
查得到就基于已有数据回答；
查不到就明确标记缺口；
低置信度不编造，进入补数队列。
```

## 为什么需要缺口队列

高校专业问答里有很多高风险问题：

- 某校某专业就业地域分布
- 某校某专业薪资分布
- 某校某专业 Top 10 对口公司
- 专业组分流到冷门专业的比例
- 入学后大类分流规则
- 转专业难度和成功率
- 考公岗位是否对口

这些问题很多时候不是现有结构化库能直接回答的。如果没有缺口队列，模型很容易为了满足用户而编造。

## 建议表结构

```text
id
gap_key
question_type
school_id
school_name
major_code
major_name
province_id
province_name
year
batch
subject_type

missing_fields
available_fields
user_question
normalized_question

priority
status
confidence_level
reason

assigned_agent
source_constraints
expected_outputs

created_at
updated_at
resolved_at
reviewer
review_note
```

## 字段说明

### `gap_key`

缺口唯一键，用来避免重复创建任务。

建议规则：

```text
question_type + school_id + major_code + province_id + year
```

示例：

```text
school_major_employment:10252:080202::2025
transfer_policy:10252:::2025
major_group_diversion:10252::31:2025
```

### `question_type`

建议取值：

```text
school_major_official_intro
school_major_employment
salary_distribution
top_employers
transfer_policy
major_diversion_policy
major_group_risk
civil_service_positions
source_document_missing
entity_alias_missing
conflicting_sources
```

### `missing_fields`

记录缺失字段，建议 JSON 数组。

示例：

```json
[
  "employment_region_distribution",
  "salary_distribution",
  "top_employers"
]
```

### `available_fields`

记录当前已有字段，方便 agent 判断补充范围。

示例：

```json
[
  "school_basic_info",
  "major_basic_info",
  "school_level_employment_rate",
  "major_general_salary"
]
```

### `priority`

建议取值：

```text
0 = 紧急，用户正在等待或高频问题
1 = 高优先级，核心字段缺失
2 = 中优先级，可异步补充
3 = 低优先级，长尾问题
```

### `status`

建议取值：

```text
pending
searching
extracted
needs_review
resolved
rejected
failed
```

含义：

- `pending`: 已记录，尚未处理。
- `searching`: agent 正在找来源。
- `extracted`: 已抽取字段，等待校验或入库。
- `needs_review`: 来源冲突、低置信度或需要人工判断。
- `resolved`: 已补齐并写回数据库。
- `rejected`: 经确认无法获取或不适合回答。
- `failed`: 自动处理失败，等待重试或人工。

### `source_constraints`

约束 agent 优先搜索哪些来源。

示例：

```json
{
  "preferred_domains": [
    "school_official_site",
    "school_admission_site",
    "school_career_site",
    "moe.gov.cn",
    "chsi.com.cn"
  ],
  "forbidden_sources": [
    "unverified_forums",
    "unsourced_social_posts"
  ]
}
```

### `expected_outputs`

定义 agent 应该补回什么结构化结果。

示例：

```json
{
  "fields": [
    "source_url",
    "source_title",
    "publish_date",
    "evidence_text",
    "employment_region_distribution",
    "salary_distribution",
    "top_employers"
  ],
  "write_targets": [
    "source_documents",
    "school_major_fact_cards",
    "fact_evidence_links"
  ]
}
```

## 缺口创建规则

### 1. 学校专业不存在于索引

如果 `school_major_index` 未确认该校开设该专业：

```text
question_type = source_document_missing
reason = 当前数据库未确认该学校专业组合
priority = 1
```

用户回答中应说：

```text
当前数据库未确认该校开设该专业，可能存在专业名称差异、方向名称差异或数据未覆盖。已记录为待核验项。
```

### 2. 只有学校级就业，没有专业级就业

如果用户问的是某校某专业就业，但库里只有 `edu_university_employment`：

```text
question_type = school_major_employment
missing_fields = ["major_level_employment_rate", "employment_region_distribution", "top_employers", "salary_distribution"]
available_fields = ["school_level_employment_rate", "school_level_further_study_rate", "major_general_job_direction"]
priority = 0 或 1
```

### 3. 只有专业通用薪资，没有学校专业薪资

如果用户问“某校某专业薪资”：

```text
question_type = salary_distribution
missing_fields = ["school_major_salary_distribution"]
available_fields = ["major_general_salary"]
priority = 1
```

回答时必须提示：

```text
当前薪资为专业通用参考，不代表该校该专业毕业生薪资。
```

### 4. 问转专业政策

如果没有学校转专业政策：

```text
question_type = transfer_policy
missing_fields = ["transfer_policy_document", "transfer_conditions", "transfer_timeline", "transfer_quota"]
priority = 0 或 1
```

优先来源：

- 学校教务处
- 本科生院
- 招生章程
- 学生手册
- 学院通知

### 5. 问专业组分流比例

如果只有招生专业组，没有大类分流细则：

```text
question_type = major_diversion_policy
missing_fields = ["diversion_policy_document", "diversion_ratio", "cold_major_risk"]
available_fields = ["admission_group_majors", "plan_count", "score_rank"]
priority = 1
```

回答时必须提示：

```text
当前只能基于招生专业组构成做风险初筛，不能确认入学后的实际分流比例。
```

### 6. 问考公岗位

如果没有公务员职位表映射：

```text
question_type = civil_service_positions
missing_fields = ["position_list", "major_requirement_mapping", "year", "province"]
priority = 2
```

优先来源：

- 国家公务员局职位表
- 各省公务员考试职位表
- 专业目录

## 缺口去重规则

写入前先按 `gap_key` 查询。

如果已存在：

1. 不重复插入。
2. 增加一次 `hit_count`。
3. 更新最近一次用户问题。
4. 如果新问题更具体，可以追加到 `user_question_examples`。

建议后续扩展字段：

```text
hit_count
last_seen_at
user_question_examples
```

## 与联网 Agent 的关系

后续 agent 只消费 `pending` 或 `failed` 状态的数据缺口。

流程：

```text
data_gap_queue.pending
  -> SourceDiscoveryAgent 找来源
  -> CrawlerAgent 抓取文档
  -> ExtractorAgent 抽取字段
  -> VerifierAgent 校验来源和冲突
  -> WriterAgent 写回数据库
  -> data_gap_queue.resolved 或 needs_review
```

## 与用户回答的关系

用户不需要看到内部任务 ID，但需要看到清楚的缺失说明。

推荐表达：

```text
当前数据库已有学校级就业和专业通用就业方向，但缺少该校该专业单独就业地域、薪资分布和重点就业单位。因此下面只能提供参考信息，不能替代该专业的真实就业报告。
```

如果系统创建了缺口任务，可以提示：

```text
这个问题已被标记为待补充数据，后续会优先检索学校就业质量报告和学院官网。
```

## 第一阶段验收标准

完成后应满足：

1. 当结构化数据缺失时，系统能创建缺口记录。
2. 相同学校、专业、问题类型不会重复创建大量任务。
3. 每个缺口有明确的缺失字段。
4. 每个缺口有建议来源和预期输出。
5. 回答中能明确说明缺失，而不是编造。
6. 后续联网 agent 可以直接按队列消费任务。
