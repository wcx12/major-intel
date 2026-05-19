# Major Intel 汇总版设计文档

## 阅读说明

这是一份给当前阶段审查用的汇总版文档。后续你可以优先只审这份，之前拆开的几份文档作为附录或历史材料保留。

当前阶段目标不是做完整产品，而是先基于本地 MySQL `gaokao_test_local` 跑通一个可检索、可解释、可标记缺口的学校专业情报 MVP。

## 一句话方案

先做 SQL-first 的结构化检索系统，用已有数据库回答能回答的问题；对现有库缺失的专业级就业、转专业、专业分流、Top 企业、考公岗位等内容，先记录为数据缺口，后续再交给联网 agent 补数据。

```text
用户问题
  -> 实体识别
  -> 问题类型判断
  -> 本地 MySQL 结构化检索
  -> 标准上下文包
  -> 缺口识别
  -> 回答生成
  -> 缺口队列，等待后续 agent 补数
```

## 当前数据库约定

后续所有开发默认只使用本地数据库：

```text
host: 127.0.0.1
port: 3306
database: gaokao_test_local
user: root
```

密码不写入仓库，不写入文档，不写入代码。

当前已确认本地库中有这些核心表：

```text
edu_university
edu_major
edu_school_major
edu_university_department
edu_university_department_major
edu_dual_class
edu_university_subject_eval
edu_university_employment
edu_college_specialty_group
edu_specialty_group_major
edu_university_plan_config
edu_university_plan_special
edu_university_plan_special_group
edu_university_score_config
edu_university_score_group
edu_university_score_special
edu_school_admission_stats
edu_score_rank
```

这些表已经足够支撑第一版本地检索 MVP。

## 回答你的三个疑惑

### 1. 为什么要创建新视图？

视图的意义不是“新增一份数据”，而是给问答系统建立一个稳定的只读检索入口。

现在原始表是业务表，分散表达不同事实：

- `edu_university`: 学校基础信息
- `edu_major`: 专业基础信息
- `edu_school_major`: 学校开设专业
- `edu_university_employment`: 学校级就业升学
- `edu_dual_class`: 双一流学科
- `edu_university_subject_eval`: 学科评估
- `edu_college_specialty_group`: 专业组
- `edu_specialty_group_major`: 专业组内专业

如果每次用户提问都临时 JOIN 这些表，会出现三个问题：

1. 查询逻辑重复，后续很难维护。
2. 不同接口可能拼出不同口径，答案不一致。
3. 很难统一判断“哪些字段已有，哪些字段缺失”。

所以视图的作用是建立一个 read model：

```text
原始业务表
  -> 统一检索视图
  -> 检索接口
  -> 标准上下文包
  -> 回答
```

建议第一版只创建只读视图，不改原始表：

```text
v_school_major_index
v_school_major_data_status
```

它们的价值分别是：

- `v_school_major_index`: 统一学校、专业、学校专业组合的基础字段。
- `v_school_major_data_status`: 标记这个学校专业组合有哪些数据、缺哪些数据。

如果你担心视图增加复杂度，也可以先用 SQL 文件或 Python 查询函数实现同样逻辑。也就是说，视图不是唯一实现方式，但“统一检索入口”这件事必须有。

我的建议是：

```text
第一版：用视图，低成本、只读、可快速验证。
第二版：如果性能不够，再改成物化表或缓存表。
```

### 2. 实体别名不可能全手工，怎么处理？

你说得对，实体别名不能全部靠手工建立。

正确做法是“自动候选 + 置信度 + 人工确认”，而不是纯手工穷举。

第一版实体识别分四层：

```text
第 1 层：精确匹配
第 2 层：数据库已有别名和字段生成
第 3 层：模糊匹配和相似度候选
第 4 层：LLM 辅助候选，但必须回查数据库确认
```

#### 第 1 层：精确匹配

直接匹配：

- 学校全称：`edu_university.name`
- 专业全称：`edu_major.special_name`
- 专业代码：`edu_major.code`
- 学校代码：`edu_university.school_id` 或 `edu_university.code`

例如：

```text
杭州电子科技大学
计算机科学与技术
080901
```

这类命中可以给高置信度。

#### 第 2 层：从已有字段自动生成别名

从数据库中自动抽取候选别名：

- `edu_university.short`
- `edu_university.old_name`
- 学校名称中的括号变体
- 学校名称去掉“大学”“学院”后的简称候选
- 专业名称中的常见括号方向
- 专业名称去括号后的标准名

例如：

```text
哈尔滨工业大学(威海) -> 哈工大威海、哈工威海、哈尔滨工业大学威海
广东工业大学 -> 广工
计算机科学与技术 -> 计科、计算机
软件工程 -> 软工
电气工程及其自动化 -> 电气
```

这些自动别名不能全部直接变成高置信度。建议先进入候选别名表：

```text
entity_alias_candidates
```

人工确认后再进入正式别名表：

```text
entity_aliases
```

#### 第 3 层：模糊匹配

当用户输入没有精确命中时，做候选召回：

- `LIKE`
- 拼音或首字母
- 编辑距离
- 中文分词
- n-gram
- 学校所在省市辅助过滤
- 专业门类辅助过滤

例如用户输入：

```text
上工程机械
```

系统可以召回：

```text
上海工程技术大学 + 机械工程
上海工程技术大学 + 机械设计制造及其自动化
```

如果候选只有一个且分数足够高，可以自动采用；如果候选多个，应该让用户确认或在回答中说明“可能指的是”。

#### 第 4 层：LLM 辅助候选

LLM 可以帮忙猜用户说法，例如：

```text
杭电 -> 杭州电子科技大学
广工 -> 广东工业大学
软工 -> 软件工程
计科 -> 计算机科学与技术
```

但规则是：

```text
LLM 只能提出候选，不能直接作为事实。
候选必须回查数据库，命中后才能进入检索。
```

如果 LLM 猜到了一个数据库里没有的学校或专业，不能继续编答。

#### 使用日志反哺别名

每次用户问题解析失败，都记录：

```text
user_query
unresolved_text
candidate_school
candidate_major
created_at
status
```

高频失败项进入人工确认，确认后加入正式别名表。

所以别名不是一开始就建全，而是随着真实用户问题逐步扩充。

### 3. 为什么合成一份汇总文档？

之前拆了多份文档，是为了分别思考检索架构、学校专业索引、数据缺口队列。但你现在要审方案，分散文档会增加审查成本。

后续以本汇总文档为第一阶段主审文档。旧文档暂时保留，作为细节附录，不要求你逐篇审。

## 第一阶段 MVP 范围

第一阶段只做本地结构化检索，不做联网补数。

要支持的问题：

1. 某学校是否开设某专业。
2. 某学校某专业的浅层解读。
3. 某学校就业和升学概况。
4. 某专业通用就业方向和薪资参考。
5. 某专业组的录取和调剂风险初筛。
6. 某学校某专业的历年录取、计划、位次。
7. 当前数据库缺哪些数据。

第一阶段明确不保证回答：

1. 某校某专业精确就业地域分布。
2. 某校某专业薪资分布。
3. 某校某专业 Top 10 对口公司。
4. 某校真实转专业成功率。
5. 某专业组真实大类分流比例。
6. 专业对口考公岗位完整清单。

这些进入缺口队列，后续由联网 agent 或人工补。

## 数据分层

### A. 已有结构化事实

来自本地 MySQL。

可直接用于第一版回答：

- 学校基础信息
- 专业基础信息
- 学校是否开设专业
- 学校专业关联
- 学科评估
- 双一流
- 学校级就业升学
- 专业通用介绍、学习内容、就业方向
- 专业通用薪资参考
- 专业组构成
- 招生计划
- 录取分数和位次

### B. 可参考但必须加提示的数据

这类数据可以回答，但必须说明口径：

- `edu_major` 里的薪资：专业通用参考，不代表某校某专业。
- `edu_major` 里的就业方向：专业通用方向，不代表某校就业去向。
- `edu_university_employment`：学校级就业，不代表某个专业。
- 专业组构成：录取志愿维度，不代表入学后分流结果。

### C. 当前缺失数据

第一版应标记为缺失：

- 学校官网专业介绍证据链
- 某校某专业就业地域分布
- 某校某专业薪资分布
- 某校某专业重点就业单位
- 转专业政策
- 大类分流政策
- 冷门专业真实分流比例
- 考公岗位映射
- 字段级来源证据

## 核心组件设计

### 1. 学校专业统一索引

名称建议：

```text
v_school_major_index
```

它的职责是回答：

```text
某学校 + 某专业是否存在？
它关联到了哪些学校字段和专业字段？
这个组合的置信度如何？
```

主来源：

```text
edu_school_major
```

补充来源：

```text
edu_university_department_major
edu_university_plan_special
edu_specialty_group_major
```

第一版建议只用 `edu_school_major` 做主索引，把扩展来源作为后续补充，不急着全部混进去。

核心字段：

```text
school_id
school_name
province_name
city_name
school_level
school_type_name
school_nature_name
is_985
is_211
is_dual_class_school
school_site

major_code
major_name
special_id
degree_level
major_level_name
limit_year
degree
level2_name
level3_name

is_dual_class_major
is_national_first_class
subject_eval_level

source_table
source_priority
confidence_level
```

### 2. 数据状态视图

名称建议：

```text
v_school_major_data_status
```

它的职责是回答：

```text
这个学校专业组合有哪些数据？
哪些数据缺失？
回答时需要提示什么？
```

核心状态字段：

```text
has_school_basic_info
has_major_basic_info
has_major_intro
has_major_job_info
has_major_general_salary
has_subject_eval
has_dual_class_info
has_school_employment
has_employment_report_links

missing_school_major_official_intro
missing_school_major_employment
missing_salary_distribution
missing_top_employers
missing_transfer_policy
missing_major_diversion_policy
missing_civil_service_positions
```

第一版里，以下字段应默认缺失：

```text
missing_school_major_employment
missing_salary_distribution
missing_top_employers
missing_transfer_policy
missing_major_diversion_policy
missing_civil_service_positions
```

原因是当前库不足以精确支持这些问题。

### 3. 实体识别模块

职责：

```text
把用户输入中的学校、专业、省份、年份、批次解析成数据库可查询实体。
```

识别顺序：

```text
精确匹配
  -> 正式别名表
  -> 自动候选别名
  -> 模糊匹配
  -> LLM 候选
  -> 用户确认或进入缺口
```

正式别名表只放高频、已确认的别名，不追求一开始覆盖全部。

建议正式别名表字段：

```text
id
entity_type
alias
canonical_name
canonical_code
source
confidence
status
created_at
updated_at
```

建议候选别名表字段：

```text
id
entity_type
alias
candidate_name
candidate_code
evidence
hit_count
status
created_at
updated_at
```

### 4. 标准上下文包

所有检索结果整理成统一 JSON，再交给模型或模板生成回答。

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

这个结构的意义是：

- 让模型只组织语言，不临时发明事实。
- 让缺失数据显式暴露。
- 后续可以缓存。
- 后续可以生成评测集。

### 5. 数据缺口队列

名称建议：

```text
data_gap_queue
```

职责：

```text
记录当前库无法可靠回答的问题，后续交给联网 agent 或人工补数。
```

核心字段：

```text
gap_key
question_type
school_id
school_name
major_code
major_name
province_id
province_name
year
missing_fields
available_fields
user_question
priority
status
confidence_level
reason
hit_count
last_seen_at
```

缺口类型：

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

## 检索流程

### 用户问“某学校某专业怎么样”

流程：

```text
1. 解析学校和专业
2. 查 v_school_major_index
3. 查 v_school_major_data_status
4. 查 edu_university_employment
5. 查 edu_major 的通用介绍、就业、薪资
6. 查双一流和学科评估
7. 汇总标准上下文包
8. 标记缺失数据
9. 生成回答
```

回答必须包含：

- 是否确认开设
- 学校基础信息
- 专业基础信息
- 学科/双一流情况
- 学校级就业升学
- 专业通用就业和薪资
- 当前缺失项

### 用户问“就业怎么样”

如果只有学校级就业：

```text
可以回答学校级就业升学情况。
必须提示不是该专业单独就业数据。
创建 school_major_employment 缺口。
```

### 用户问“薪资怎么样”

如果只有 `edu_major` 通用薪资：

```text
可以给专业通用薪资参考。
必须提示不是该校该专业薪资。
创建 salary_distribution 缺口。
```

### 用户问“能不能转专业”

当前库没有转专业政策表：

```text
不能直接回答具体规则。
可以提示当前缺转专业政策。
创建 transfer_policy 缺口。
```

### 用户问“会不会分流到冷门专业”

如果只有招生专业组：

```text
可以列出专业组构成、计划人数、最低分、位次。
只能做风险初筛。
不能输出真实分流比例。
创建 major_diversion_policy 缺口。
```

## 回答规则

第一版回答建议固定为四段：

```text
1. 已确认的信息
2. 可参考的数据
3. 当前缺失的信息
4. 后续可补充方向
```

示例：

```text
目前数据库确认，某校开设某专业，专业代码为 XXXX，属于 XX 类。

可参考数据方面，该专业通用就业方向包括 A、B、C；学校级就业率为 XX%，升学率为 XX%。注意，这里学校级就业数据不等于该专业单独就业数据。

当前缺少该校该专业单独就业地域分布、薪资分布、重点就业单位和转专业政策，因此不能给出这些结论。

这些缺口后续可由联网 agent 优先检索学校就业质量报告、学院官网、教务处文件和招生章程补齐。
```

## 实施顺序

### 阶段 1：本地库检查

目标：

```text
确认本地 gaokao_test_local 可用。
确认核心表存在。
确认核心表数据量合理。
```

产物：

```text
scripts/check_local_db.py
```

### 阶段 2：学校专业索引

目标：

```text
建立 v_school_major_index。
```

产物：

```text
sql/views/v_school_major_index.sql
sql/checks/school_major_index_quality.sql
```

### 阶段 3：数据状态视图

目标：

```text
建立 v_school_major_data_status。
```

产物：

```text
sql/views/v_school_major_data_status.sql
sql/checks/data_status_summary.sql
```

### 阶段 4：缺口队列

目标：

```text
建立 data_gap_queue。
```

产物：

```text
sql/tables/data_gap_queue.sql
```

### 阶段 5：实体识别

目标：

```text
支持学校和专业的精确匹配、别名匹配、模糊匹配和候选召回。
```

产物：

```text
entity_aliases
entity_alias_candidates
src/major_intel/retrieval/entities.py
```

### 阶段 6：最小检索脚本

目标：

```text
输入学校 + 专业，输出标准上下文包。
```

产物：

```text
scripts/query_school_major.py
```

### 阶段 7：样例问题评测

目标：

```text
用 20 个真实问题检查命中率、缺口标记和回答口径。
```

产物：

```text
data/seeds/sample_questions.csv
reports/local_retrieval_eval.md
```

## 第一阶段验收标准

完成后应能做到：

1. 只使用本地 `gaokao_test_local`。
2. 输入学校和专业，能判断是否确认开设。
3. 能返回学校基础信息。
4. 能返回专业基础信息。
5. 能返回学校级就业升学信息。
6. 能返回专业通用就业和薪资信息。
7. 能返回专业组和录取相关信息。
8. 能明确标记专业级就业、薪资分布、Top 企业、转专业政策、专业分流、考公岗位等缺口。
9. 对缺失信息不编造。
10. 能把缺口写入或准备写入 `data_gap_queue`。

## 后续联网 Agent 怎么接

联网 agent 不直接回答用户，而是消费缺口队列。

后续流程：

```text
data_gap_queue.pending
  -> SourceDiscoveryAgent 找官网、就业报告、政策文件
  -> CrawlerAgent 抓取网页或 PDF
  -> ExtractorAgent 抽取结构化字段
  -> VerifierAgent 校验来源、年份和冲突
  -> WriterAgent 写回数据库
  -> data_gap_queue.resolved 或 needs_review
```

这样用户问答链路保持稳定，联网搜索作为后台补数能力，而不是每次问答都临时上网。

## 当前你需要审查的决策点

请重点审查这些问题：

1. 是否同意第一阶段只做本地 SQL-first 检索？
2. 是否同意先用只读视图做统一检索入口？
3. 是否同意 `edu_school_major` 作为第一版学校专业主索引？
4. 是否同意 `edu_university_department_major` 暂时作为补充来源，不直接混进第一版主索引？
5. 是否同意实体别名采用“自动候选 + 置信度 + 人工确认”，而不是纯手工？
6. 是否同意第一版把专业级就业、转专业、分流比例、Top 企业、考公岗位先标为缺口？
7. 是否需要第一版就接大模型生成自然语言回答，还是先只输出标准上下文包？

## 文档关系

后续你优先审查这份文档：

```text
docs/specs/major-intel-consolidated-design.md
```

其它文档作为附录保留：

```text
docs/specs/retrieval-architecture.md
docs/specs/school-major-index.md
docs/specs/data-gap-queue.md
docs/specs/local-retrieval-mvp-plan.md
docs/research/2026-05-19-starting-point-research.md
```

如果旧文档和本汇总文档冲突，以本汇总文档作为第一阶段审查依据。
