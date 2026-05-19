# 本地检索 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于本地 MySQL `gaokao_test_local` 先跑通一个 SQL-first 的学校专业检索闭环，让系统能回答已有数据，并清楚标记缺失数据。

**Architecture:** 第一阶段只使用本地结构化数据库，不接联网 agent，不做前端。先建立统一学校专业索引、数据状态视图、缺口队列表，再用最小检索脚本把查询结果整理成标准上下文包。

**Tech Stack:** MySQL 8.0、本地数据库 `gaokao_test_local`、SQL 视图、Python 3、Pytest、命令行检索脚本。

---

## 0. 当前约定

后续所有数据库操作默认使用本地库：

```text
host: 127.0.0.1
port: 3306
database: gaokao_test_local
user: root
```

密码不得写入仓库。执行脚本时通过环境变量、交互输入或本地开发工具提供。

第一阶段不使用远程腾讯云数据库，不把联网搜索作为学生问答链路的一部分。

## 1. 已有数据基础

本地库已确认有以下核心表：

```text
edu_university                  院校基础信息
edu_major                       专业基础信息
edu_school_major                院校开设专业关联表
edu_university_department       院系设置表
edu_university_department_major 院系-专业关联表
edu_dual_class                  双一流学科表
edu_university_subject_eval     学科评估表
edu_university_employment       大学就业数据表
edu_college_specialty_group     院校专业组表
edu_specialty_group_major       专业组与专业关联表
edu_university_plan_config      招生计划配置表
edu_university_plan_special     招生专业详情表
edu_university_plan_special_group 招生专业组表
edu_university_score_config     分数线配置表
edu_university_score_group      专业组分数线表
edu_university_score_special    专业分数线表
edu_school_admission_stats      学校录取统计表
edu_score_rank                  一分一段表
```

这些表足够支撑第一版“结构化检索 MVP”。

## 2. 第一阶段不做什么

第一阶段暂不做：

- 联网 agent。
- 学生端前端页面。
- 大规模网页/PDF 抓取。
- 向量库。
- LLM 自动写 SQL。
- 自动生成最终志愿推荐方案。
- 对原始业务表做破坏性改表。

第一阶段的任务是把现有 MySQL 数据组织成稳定检索层。

## 3. 文件结构

建议新增以下文件：

```text
sql/views/v_school_major_index.sql
sql/views/v_school_major_data_status.sql
sql/tables/data_gap_queue.sql
sql/checks/school_major_index_quality.sql
sql/checks/data_status_summary.sql

src/major_intel/__init__.py
src/major_intel/config.py
src/major_intel/db.py
src/major_intel/retrieval/__init__.py
src/major_intel/retrieval/entities.py
src/major_intel/retrieval/context_builder.py
src/major_intel/retrieval/gaps.py

scripts/query_school_major.py
scripts/check_local_db.py

tests/test_context_builder.py
tests/test_gap_detection.py
tests/test_entity_normalization.py

data/seeds/sample_questions.csv
data/seeds/entity_aliases.sample.csv
```

各文件职责：

- `sql/views/v_school_major_index.sql`: 统一学校、专业、学校专业组合、专业通用信息、学校标签。
- `sql/views/v_school_major_data_status.sql`: 为每个学校专业组合标记已有数据和缺失数据。
- `sql/tables/data_gap_queue.sql`: 保存缺口任务，供后续联网 agent 消费。
- `sql/checks/*.sql`: 数据质量检查，不修改数据。
- `src/major_intel/config.py`: 读取本地数据库连接配置。
- `src/major_intel/db.py`: 创建数据库连接。
- `src/major_intel/retrieval/entities.py`: 学校和专业实体解析。
- `src/major_intel/retrieval/context_builder.py`: 把 SQL 查询结果整理成标准上下文包。
- `src/major_intel/retrieval/gaps.py`: 根据问题类型和已有字段判断缺口。
- `scripts/query_school_major.py`: 命令行检索入口。
- `scripts/check_local_db.py`: 检查本地库是否可用。
- `tests/*.py`: 先测纯函数逻辑，数据库集成测试单独执行。
- `data/seeds/*.csv`: 第一版样例问题和别名样本。

## 4. 实施任务

### Task 1: 本地数据库连接约定

**Files:**

- Create: `src/major_intel/config.py`
- Create: `src/major_intel/db.py`
- Create: `scripts/check_local_db.py`
- Test: `scripts/check_local_db.py`

- [ ] **Step 1: 定义配置读取规则**

`src/major_intel/config.py` 读取以下环境变量：

```text
MAJOR_INTEL_DB_HOST 默认 127.0.0.1
MAJOR_INTEL_DB_PORT 默认 3306
MAJOR_INTEL_DB_NAME 默认 gaokao_test_local
MAJOR_INTEL_DB_USER 默认 root
MAJOR_INTEL_DB_PASSWORD 无默认值
```

密码不写入文件。

- [ ] **Step 2: 写本地库检查脚本**

`scripts/check_local_db.py` 应执行：

```sql
SELECT DATABASE(), VERSION(), CURRENT_USER();
SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE();
SELECT COUNT(*) FROM edu_university;
SELECT COUNT(*) FROM edu_major;
SELECT COUNT(*) FROM edu_school_major;
```

- [ ] **Step 3: 验证脚本**

运行：

```powershell
$env:MAJOR_INTEL_DB_PASSWORD = "本地密码"
python scripts/check_local_db.py
```

预期输出应包含：

```text
database: gaokao_test_local
edu_university rows: 大于 0
edu_major rows: 大于 0
edu_school_major rows: 大于 0
```

### Task 2: 创建学校专业统一索引视图

**Files:**

- Create: `sql/views/v_school_major_index.sql`
- Test: `sql/checks/school_major_index_quality.sql`

- [ ] **Step 1: 用 `edu_school_major` 作为主来源**

视图应优先使用：

```text
edu_school_major.school_id
edu_school_major.school_name
edu_school_major.major_code
edu_school_major.major_name
edu_school_major.special_id
edu_school_major.degree_level
edu_school_major.level_name
edu_school_major.is_dual_class
edu_school_major.nation_first_class
edu_school_major.xueke_rank_score
```

- [ ] **Step 2: 关联学校基础信息**

关联 `edu_university`：

```sql
CAST(edu_school_major.school_id AS CHAR) = edu_university.school_id
```

或在必要时使用：

```sql
CAST(edu_school_major.school_id AS CHAR) = edu_university.code
```

输出字段包含：

```text
province_name
city_name
type_name
school_nature_name
level_name
is985
is211
is_dual_class
school_site
site
content
```

- [ ] **Step 3: 关联专业基础信息**

优先用 `major_code = edu_major.code` 关联。

输出字段包含：

```text
special_id
special_name
code
level2_name
level3_name
limit_year
degree
content
job
is_what
learn_what
do_what
salaryavg
fivesalaryavg
jobdetail
professionalsalary
jobrate
mostemploymentindustry
mostemploymentarea
```

- [ ] **Step 4: 设置来源和置信度**

视图中加入：

```text
source_priority = 1
source_table = 'edu_school_major'
confidence_level = 'high'
```

- [ ] **Step 5: 执行质量检查**

`sql/checks/school_major_index_quality.sql` 至少输出：

```sql
SELECT COUNT(*) AS total_rows FROM v_school_major_index;
SELECT COUNT(*) AS missing_school_rows FROM v_school_major_index WHERE resolved_school_id IS NULL;
SELECT COUNT(*) AS missing_major_rows FROM v_school_major_index WHERE resolved_major_code IS NULL;
SELECT school_id, major_code, COUNT(*) AS duplicate_count
FROM v_school_major_index
GROUP BY school_id, major_code
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 50;
```

### Task 3: 创建学校专业数据状态视图

**Files:**

- Create: `sql/views/v_school_major_data_status.sql`
- Test: `sql/checks/data_status_summary.sql`

- [ ] **Step 1: 基于 `v_school_major_index` 判断基础字段**

状态字段包括：

```text
has_school_basic_info
has_major_basic_info
has_major_intro
has_major_job_info
has_major_general_salary
has_subject_eval
has_dual_class_info
```

- [ ] **Step 2: 关联学校级就业数据**

关联 `edu_university_employment`：

```sql
v_school_major_index.school_id = edu_university_employment.school_id
```

状态字段包括：

```text
has_school_employment
school_employment_year
has_employment_report_links
```

- [ ] **Step 3: 标记第一阶段缺失项**

缺失项字段包括：

```text
missing_school_major_official_intro
missing_school_major_employment
missing_salary_distribution
missing_top_employers
missing_transfer_policy
missing_major_diversion_policy
missing_civil_service_positions
```

第一版中，以下字段默认缺失：

```text
missing_school_major_employment = 1
missing_salary_distribution = 1
missing_top_employers = 1
missing_transfer_policy = 1
missing_major_diversion_policy = 1
missing_civil_service_positions = 1
```

原因：当前已有表主要能支撑学校级就业、专业通用就业，不足以支撑某校某专业的精确就业和政策回答。

- [ ] **Step 4: 输出数据状态汇总**

`sql/checks/data_status_summary.sql` 输出：

```sql
SELECT COUNT(*) AS total_school_major_count FROM v_school_major_data_status;
SELECT SUM(has_major_intro) AS major_intro_count FROM v_school_major_data_status;
SELECT SUM(has_school_employment) AS school_employment_count FROM v_school_major_data_status;
SELECT SUM(missing_school_major_employment) AS missing_school_major_employment_count FROM v_school_major_data_status;
SELECT SUM(missing_transfer_policy) AS missing_transfer_policy_count FROM v_school_major_data_status;
```

### Task 4: 创建数据缺口队列表

**Files:**

- Create: `sql/tables/data_gap_queue.sql`
- Test: MySQL `SHOW CREATE TABLE data_gap_queue;`

- [ ] **Step 1: 创建表结构**

表字段应覆盖：

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
hit_count
last_seen_at
created_at
updated_at
resolved_at
reviewer
review_note
```

- [ ] **Step 2: 设置唯一键**

唯一键：

```sql
UNIQUE KEY uk_gap_key (gap_key)
```

普通索引：

```sql
KEY idx_status_priority (status, priority)
KEY idx_school_major (school_id, major_code)
KEY idx_question_type (question_type)
```

- [ ] **Step 3: 状态默认值**

默认：

```text
status = pending
priority = 2
confidence_level = low
hit_count = 1
```

### Task 5: 实体别名样本

**Files:**

- Create: `data/seeds/entity_aliases.sample.csv`
- Create: `src/major_intel/retrieval/entities.py`
- Test: `tests/test_entity_normalization.py`

- [ ] **Step 1: 建别名样本**

第一版样本包含：

```csv
entity_type,alias,canonical_name,canonical_code,confidence
school,杭电,杭州电子科技大学,,high
school,广工,广东工业大学,,high
school,深大,深圳大学,,high
major,计科,计算机科学与技术,080901,high
major,软工,软件工程,080902,high
major,电气,电气工程及其自动化,080601,medium
major,自动化,自动化,080801,high
```

- [ ] **Step 2: 实现标准化函数**

`entities.py` 提供：

```text
normalize_school_name(input_text)
normalize_major_name(input_text)
```

返回：

```json
{
  "input": "杭电",
  "canonical_name": "杭州电子科技大学",
  "canonical_code": null,
  "confidence": "high"
}
```

### Task 6: 标准上下文包生成

**Files:**

- Create: `src/major_intel/retrieval/context_builder.py`
- Create: `src/major_intel/retrieval/gaps.py`
- Test: `tests/test_context_builder.py`
- Test: `tests/test_gap_detection.py`

- [ ] **Step 1: 定义上下文结构**

输出结构固定为：

```json
{
  "question_type": "school_major_overview",
  "entities": {
    "school": {},
    "major": {},
    "province": null,
    "year": 2025
  },
  "facts": {
    "school": {},
    "major": {},
    "school_major": {},
    "employment": {},
    "admission": {},
    "specialty_group": {}
  },
  "data_gaps": [],
  "warnings": []
}
```

- [ ] **Step 2: 实现缺口检测规则**

规则示例：

```text
如果用户问某校某专业就业，但只有学校级就业数据：
  添加 school_major_employment 缺口
  添加 warning: 当前就业数据为学校级，不代表该校该专业

如果用户问薪资，但只有 edu_major 通用薪资：
  添加 salary_distribution 缺口
  添加 warning: 当前薪资为专业通用参考

如果用户问转专业：
  添加 transfer_policy 缺口

如果用户问专业组分流：
  添加 major_diversion_policy 缺口
```

### Task 7: 最小命令行检索脚本

**Files:**

- Create: `scripts/query_school_major.py`
- Test: 手动运行 5 个样例问题

- [ ] **Step 1: 支持学校和专业参数**

命令形式：

```powershell
python scripts/query_school_major.py --school "杭州电子科技大学" --major "计算机科学与技术"
```

输出：

```text
学校：杭州电子科技大学
专业：计算机科学与技术
是否确认开设：是
学校层次：本科
学校标签：非 985、非 211、双一流状态按库中字段输出
专业门类：工学
专业类：计算机类
学校级就业：有/无
专业通用薪资：有/无
缺失项：专业级就业、薪资分布、Top 企业、转专业政策、分流政策、考公岗位
```

- [ ] **Step 2: 支持 JSON 输出**

命令形式：

```powershell
python scripts/query_school_major.py --school "杭州电子科技大学" --major "计算机科学与技术" --format json
```

输出标准上下文包。

### Task 8: 样例问题和验收

**Files:**

- Create: `data/seeds/sample_questions.csv`

- [ ] **Step 1: 写 20 个样例问题**

第一批问题应覆盖：

```text
学校专业是否开设
学校专业浅层解读
学校就业升学
专业通用就业薪资
专业组风险
历年录取
转专业政策缺口
专业级就业缺口
Top 企业缺口
考公岗位缺口
```

- [ ] **Step 2: 每个问题标记预期结果**

字段：

```csv
id,question,expected_question_type,expected_school,expected_major,should_have_answer,expected_gap_types
```

示例：

```csv
1,杭电计算机怎么样,school_major_overview,杭州电子科技大学,计算机科学与技术,true,"school_major_employment;transfer_policy"
2,广东工业大学自动化能转专业吗,transfer_policy,广东工业大学,自动化,true,"transfer_policy"
```

## 5. 第一阶段验收标准

完成后应能做到：

1. 本地连接只使用 `gaokao_test_local`。
2. 输入学校和专业，能判断是否确认开设。
3. 能返回学校基础信息。
4. 能返回专业基础信息。
5. 能返回学校级就业升学信息。
6. 能返回专业通用就业和薪资信息。
7. 能明确标记专业级就业、薪资分布、Top 企业、转专业政策、专业组分流、考公岗位等缺口。
8. 查不到时不编造，写入或准备写入 `data_gap_queue`。
9. 命令行脚本能输出标准上下文包。
10. 20 个样例问题能用于人工验收。

## 6. 审查重点

你审查这份计划时，建议重点看：

1. 是否同意第一阶段只做本地 SQL-first 检索。
2. 是否同意 `edu_school_major` 作为学校专业主索引来源。
3. 是否接受 `edu_university_department_major` 作为扩展补充来源。
4. 是否同意第一版把专业级就业、转专业、分流比例、Top 企业、考公岗位都标为缺口。
5. 是否希望第一版直接建真实表，还是先全部用视图和检查 SQL。
6. 是否要在第一版就接模型生成自然语言回答。

## 7. 推荐执行顺序

推荐先执行：

```text
Task 1 -> Task 2 -> Task 3 -> Task 4
```

这四步完成后，数据库层就能看清“已有数据”和“缺失数据”。

然后执行：

```text
Task 5 -> Task 6 -> Task 7 -> Task 8
```

这四步完成后，就能用命令行跑通最小检索闭环。

## 8. 与其它文档的关系

本计划依赖以下文档：

- `docs/specs/retrieval-architecture.md`
- `docs/specs/school-major-index.md`
- `docs/specs/data-gap-queue.md`
- `docs/research/2026-05-19-starting-point-research.md`

如果这些文档和本计划冲突，以本计划作为第一阶段执行顺序，以原规格文档作为设计依据。
