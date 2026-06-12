# 数据清单与需求覆盖状态（2026-06-12）

本文档记录当前项目已经具备的数据资产、核心字段、使用边界，以及它们对专业解读需求的支撑程度。

## 1. 存放原则

项目数据分三层管理：

| 层级 | 存放方式 | 说明 |
| --- | --- | --- |
| Git 仓库 | 小体积、可公开、可审查的数据样本与 seed | 例如 `data/seeds/`、对话数据集、评测用例 |
| GitHub Release | 大体积爬取数据、清洗数据、报告产物 | 例如 `data/raw/`、`data/processed/`、`data/cleaned/`、`outputs/graduate_outcomes/` |
| 本地 MySQL | 核心高考数据库 | 不上传公开仓库；检索工具本地查询使用 |

当前明确不上传：

- 核心 MySQL dump。
- `.env`、密码、API Key。
- `reports/volunteer_matching/` 志愿匹配实验和论文产物。
- 依赖缓存、虚拟环境、外部工具缓存。

## 2. 已有数据集清单

### 2.1 RYSXAI 专业目录 seed

路径：

- `data/seeds/rysxai_professions.full.csv`
- `data/seeds/rysxai_professions.sample.csv`

规模：

- full：1653 行。

字段：

| 字段 | 含义 |
| --- | --- |
| `rysxai_profession_id` | 第三方 RYSXAI 专业 ID |
| `major_code` | 专业代码，含 `T`、`TK` 等国标码后缀 |
| `major_name` | 专业名称 |
| `level` | 层次，例如本科 |
| `category` | 学科门类，例如工学、经济学 |
| `subject` | 专业类，例如计算机类、金融学类 |
| `degree` | 授予学位 |
| `limit_year` | 学制 |
| `heat` | 第三方热度值 |
| `is_hot` | 是否为热门专业标记 |

用途：

- 专业实体识别。
- 新增专业、`T/TK` 专业初筛。
- 专业介绍、薪资、考公、升学等外部数据的 join key。

边界：

- 来源是第三方结构化专业表，不等同于教育部官方专业目录。
- 用于产品初筛可以，正式“教育部新增专业”判断仍需接入教育部专业目录或官方公告。

### 2.2 RYSXAI 院校 seed

路径：

- `data/seeds/rysxai_universities.csv`

规模：

- 2948 行。

字段：

| 字段 | 含义 |
| --- | --- |
| `id` | 第三方院校 ID |
| `name` | 院校名称 |
| `province` | 省份 |
| `city` | 城市 |
| `town` | 区县/辖区 |
| `type` | 院校类型 |
| `property` | 办学性质 |
| `level` | 办学层次 |
| `department` | 主管部门 |
| `tags` | 院校标签，例如双一流、211 等 |

用途：

- 第三方院校实体映射。
- 转专业政策、专业介绍、市场数据等 RYSXAI 数据的学校维度补充。

边界：

- 学校 ID 与本地 `edu_university` ID 不是同一口径，不能直接强行外键关联。

### 2.3 RYSXAI 专业介绍数据

路径：

- `data/raw/rysxai_major_intros/`
- `data/processed/rysxai_major_intros/`
- `data/logs/rysxai_major_intros/`

核心文件：

- `data/processed/rysxai_major_intros/major_introductions_full_20260611_intro.csv`
- `data/processed/rysxai_major_intros/major_introductions_full_20260611_intro.jsonl`

规模：

- raw：1658 个文件，约 90 MB。
- processed：1661 个文件，约 94.39 MB。
- aggregate CSV：1653 行。

字段：

| 字段 | 含义 |
| --- | --- |
| `rysxai_profession_id` | RYSXAI 专业 ID |
| `major_code` | 专业代码 |
| `major_name` | 专业名称 |
| `level` | 专业层次 |
| `degree` | 学位 |
| `limit_year` | 学制 |
| `selection_advice` | 选科建议 |
| `enrollment_scale` | 招生规模描述 |
| `univ_count` | 开设院校数量 |
| `apply_plan_ratio` | 报考/计划相关比例字段，第三方口径 |
| `major_detail` | 专业详情、培养目标、就业方向等长文本 |
| `major_course` | 专业课程分析 |
| `undergraduate_to_graduate` | 本研衔接、考研方向等 |
| `similar_majors` | 相似专业 |
| `captured_at` | 抓取时间 |
| `info_url` | 来源接口 URL |

用途：

- 专业浅层解读。
- 核心课程说明。
- 专业学习内容、就业方向、本研衔接解释。
- 学科能力标签的初步抽取来源。
- 新增专业、低空经济、半导体、智能计算等新专业的基础介绍。

边界：

- 这是专业通用介绍，不是学校官网的某校某专业培养方案。
- 不应替代学校官网专业介绍证据链。

### 2.4 RYSXAI 专业市场与薪资数据

路径：

- `data/raw/rysxai/`
- `data/processed/rysxai/`

核心文件形态：

- `data/processed/rysxai/profession_{id}_market_snapshot.json`

规模：

- processed 快照约 1616 个专业。

主要结构：

| 字段/对象 | 含义 |
| --- | --- |
| `profession` | 专业 ID、名称、代码、学制、学位等 |
| `macro_employment.industry_distribution` | 行业分布 |
| `macro_employment.region_distribution` | 地域分布 |
| `macro_employment.job_direction_distribution` | 就业方向分布 |
| `demand_ranking` | 地区需求排行 |
| `salary_ranking` | 地区薪资参考排行 |
| `job_posting_samples` | 招聘样本，含岗位、公司、城市、行业、薪资、学历、经验等 |
| `salary_observations_by_city` | 城市维度薪资观测 |
| `salary_observations_by_industry` | 行业维度薪资观测 |
| `warnings` | 抓取或解析警告 |

用途：

- 专业薪资参考。
- 专业就业方向、行业分布、地域分布。
- 对口企业/岗位样本。
- AI 替代性、行业风险等后续模型的辅助特征。

边界：

- 第三方招聘样本，不是官方就业质量报告。
- 可以做“参考/样本口径”，不能做绝对就业承诺。
- Top 5% 月薪目前只能用样本分位估算，尚不是稳定官方字段。

### 2.5 RYSXAI 考公岗位数据

路径：

- `data/raw/rysxai_civil_service_2026.jsonl`
- `data/processed/rysxai_civil_service_2026.csv`

规模：

- 20714 行。

字段：

| 字段 | 含义 |
| --- | --- |
| `id` | 岗位记录 ID |
| `sheet_type` | 表类型 |
| `year` | 年份 |
| `department_code` | 部门代码 |
| `department_name` | 部门名称 |
| `sub_department` | 用人司局/下级部门 |
| `department_property` | 部门属性 |
| `job_name` | 岗位名称 |
| `job_property` | 岗位属性 |
| `job_area` | 岗位地区 |
| `job_intro` | 岗位简介 |
| `position_code` | 职位代码 |
| `department_level` | 部门层级 |
| `exam_type` | 考试类型 |
| `plan_num` | 招录人数 |
| `apply_num` | 报名人数 |
| `ratio` | 竞争比 |
| `profession` | 专业要求文本 |
| `education_level` | 学历要求 |
| `degree_requirement` | 学位要求 |
| `identity` | 身份要求 |
| `work_year` | 基层/工作年限要求 |
| `work_experience` | 工作经历要求 |
| `need_test` | 是否组织专业测试 |
| `work_location` | 工作地点 |
| `province` | 省份 |
| `residence_location` | 户籍/生源限制 |
| `remark` | 备注 |
| `is_new_graduate` | 应届要求 |
| `department_website` | 部门网站 |
| `phone` | 咨询电话 |
| `wuweitu` / `wuwei_table` | 第三方无位/岗位表相关字段 |

用途：

- 专业到考公岗位的文本匹配。
- 三不限/对口岗位线索。
- 岗位层级、地区、竞争比分析。
- `civil_service_role_search`、`civil_service_mapping` 的底层数据。

边界：

- 当前是“岗位文本命中/映射线索”，不是最终可报岗位判定。
- 正式可报判断还需要官方职位表、专业目录、限制条件和年份口径复核。

### 2.6 RYSXAI 转专业政策数据

路径：

- `data/processed/rysxai_transfer_policies.csv`

规模：

- 2948 行。

字段：

| 字段 | 含义 |
| --- | --- |
| `school_id` | 第三方学校 ID |
| `school_name` | 学校名称 |
| `province` / `city` | 地区 |
| `type` / `property` / `level` | 学校属性 |
| `department` | 主管部门 |
| `tags_json` | 学校标签 |
| `source_url` | 来源接口 |
| `has_transfer_policy` | 是否有校级转专业政策文本 |
| `has_faculty_policy` | 是否有院系级政策 |
| `faculty_policy_count` | 院系政策数量 |
| `change_profession_chars` | 转专业政策文本长度 |
| `application_condition_chars` | 申请条件文本长度 |
| `admission_requirement_chars` | 接收要求文本长度 |
| `assessment_chars` | 考核办法文本长度 |
| `is_new_version` | 是否新版本 |
| `change_profession` | 转专业政策正文 |
| `change_profession_application_condition` | 申请条件正文 |
| `change_profession_admission_requirement` | 接收要求正文 |
| `change_profession_assessment` | 考核办法正文 |
| `change_profession_by_faculty_json` | 院系级政策 JSON |

用途：

- 转专业政策问答。
- 转专业门槛、考核方式、院系差异的初筛。

边界：

- 来源是第三方接口，未逐条对照学校官网。
- 对考生输出时需要标注为“第三方转专业政策线索”，不能等同官方实时政策。

### 2.7 升学/保研去向数据

路径：

- `data/cleaned/graduate_outcomes/`
- `outputs/graduate_outcomes/`

核心文件：

- `master_records_public.csv`
- `undergraduate_school_outcome_summary.csv`
- `official_employment_report_metrics.csv`
- `official_recommendation_school_coverage.csv`
- `graduate_outcomes_clean_data_package.xlsx`

主要文件与字段：

| 文件 | 行数 | 核心字段 | 含义 |
| --- | ---: | --- | --- |
| `master_records_public.csv` | 285608 | `school_name`, `year`, `route`, `undergraduate_school`, `undergraduate_major`, `admission_major`, `source_url`, `quality_score` | 脱敏人员级升学/推免/拟录取公开记录 |
| `undergraduate_school_outcome_summary.csv` | 642 | `undergraduate_school`, `destination_school`, `year`, `route`, `record_count`, `unique_person_count` | 本科来源学校到升学去向学校的聚合 |
| `official_employment_report_metrics.csv` | 326 | `school_name`, `metric_name`, `metric_value`, `metric_unit`, `source_url` | 官方就业/教学质量报告中的就业率、升学率、出国率等指标 |
| `official_recommendation_school_coverage.csv` | 430 | `school_name`, `has_official_recommendation_records`, `official_recommendation_record_count` | 目标院校升学/推免记录覆盖状态 |
| `official_recommendation_source_attempts.csv` | 15 | `school_name`, `decision`, `blocker_type`, `notes` | 未覆盖学校的来源尝试和阻塞原因 |

用途：

- 升学去向、保研/考研公开名单样本。
- “最好的学长学姐去了哪里”。
- 去清北、C9、985、211、双一流数量的样本统计。
- 学校级升学率/出国率/推免人数的官方报告指标。

边界：

- `master_records_public.csv` 是公开名单样本，不能直接推导真实升学率。
- 升学率、保研率、考研率必须优先用 `official_employment_report_metrics.csv`，但该表目前覆盖有限：326 条指标、26 所学校，其中升学相关指标约 128 条、22 所学校。

### 2.8 高考志愿对话数据集

路径：

- `datasets/dialogue/claude_full/`

核心文件：

| 文件 | 行数/用途 | 主要字段 |
| --- | --- | --- |
| `question_bank.jsonl` | 152 条问题 | `question_raw`, `question_normalized`, `question_family`, `slots`, `expected_tools`, `quality_label` |
| `function_call_eval_cases.jsonl` | 152 条 function-call 评测用例 | `user_question`, `expected_intent`, `expected_tools`, `required_slots`, `should_clarify` |
| `llm_cleaned_dialogues.jsonl` | 清洗后的对话样本 | `question_*`, `slots`, `mentor_strategy`, `quality_score` |
| `usable_question_bank.jsonl` | 可用问题子集 | 同问题库字段 |
| `usable_function_call_eval_cases.jsonl` | 可用 function-call 子集 | 同评测用例字段 |
| `asr_question_candidates.jsonl` | ASR 候选问题 | 原始候选、来源、清洗状态 |
| `review_queue.jsonl` | 人工复核队列 | 待复核样本与质量标记 |
| `mentor_strategy_bank.jsonl` | 回答策略库 | 策略名称、适用意图 |

用途：

- Agent 问题理解和 function-call 选择评测。
- 常见考生问题覆盖设计。
- 对话风格和导师策略参考。

边界：

- 这是问题/对话数据，不是事实库。
- 不能直接回答学校、专业、政策事实，只能辅助路由和表达。

### 2.9 本地 MySQL `gaokao_test`

状态：

- 已导入本地。
- 不上传公开仓库，也不上传 GitHub Release。

主要用途：

- 学校基础信息。
- 专业基础信息。
- 学校开设专业。
- 招生计划。
- 录取历史。
- 位次换算。
- 专业组、选科、学费、校区等结构化检索。
- 已接入 function-call 工具层和 SQL-first agent。

边界：

- 具体字段以本地库 schema 为准。
- 公开仓库只记录工具、文档和测试，不公开核心数据库 dump。

## 3. 需求覆盖对照

| 需求 | 当前数据支撑 | 结论 | 说明 |
| --- | --- | --- | --- |
| 核心课程：选取三个代表性学校 | `rysxai_major_intros.major_course` | 部分支撑 | 能支撑“专业通用核心课程”。不能支撑“某专业在三个代表性学校的官网课程方案”，后者需要学校官网培养方案/课程体系补采。 |
| AI 替代性 | RYSXAI 岗位样本、就业方向、行业分布 | 部分支撑 | 可以作为模型特征，但没有现成“AI 替代性”标签。需要新增规则、LLM 标注或外部职业自动化风险数据。 |
| 新质生产力专业：AI、低空经济等，抓取政府工作报告等文献判断 | 新增专业 seed、专业介绍、低空经济与管理、低空技术与工程等专业记录 | 部分支撑 | 专业侧已有初筛数据；政府工作报告、产业政策文献尚未系统抓取。 |
| 新增专业（教育部专业目录，特别是国标码带 T 的专业） | `rysxai_professions.full.csv`、`rysxai_major_intros` | 部分支撑 | 可按 `major_code` 中 `T/TK` 初筛新增/特设/控制布点专业；还缺教育部官方目录作为权威来源。 |
| 高危专业（教育部红牌专业，近年裁撤缩招较多的专业） | 本地招生计划/录取历史、RYSXAI 热度与市场数据 | 部分支撑 | 可做“缩招/低热/低薪/就业弱”风险特征，但没有官方红牌专业库和裁撤专业库。 |
| 学科适合度：数学、物理、化学、生物、读写、英语能力要求 | 选科要求工具、本地招生计划选科字段、`major_course`、`major_detail` | 部分支撑 | 可以抽取能力标签，但目前还没有稳定的结构化学科能力 tag 表。 |
| MBTI 适配度 | 当前仓库未发现 `MBTI匹配度.md` 或结构化 MBTI 表 | 暂不支撑 | 需要把已有 MBTI 文档放入仓库，或转成结构化 `major_mbti_fit` 表。 |
| 薪资分布：毕业月薪参考、top 5%月薪参考、毕业5年后月薪 | 本地 `edu_major` 薪资字段、RYSXAI 市场薪资样本 | 可支撑基础版 | 毕业月薪、五年薪资、城市/行业薪资样本可支撑；Top 5% 目前只能从招聘样本分位估算，需标注样本口径。 |
| 考公适配度：岗位、三不限/对口、国考/省市县比例、平均竞争比 | `rysxai_civil_service_2026.csv` | 部分支撑 | 有岗位、专业要求、层级、地区、招录人数、报名人数、竞争比。三不限/对口和层级比例可计算，但仍是文本命中线索，不是最终可报判定。 |
| 升学适配度：平均保研考研率、最好去向、平均每年去清北/985/211/双一流多少个 | 升学公开名单、去向汇总、官方报告指标 | 部分支撑 | 最好去向和去向层次可由名单样本统计；官方升学率/保研率覆盖有限，不能对所有学校稳定计算真实平均率。 |
| 扩招提示（依据当期 2026 数据，接口先留着） | 本地招生计划/录取历史、部分 2026 计划数据 | 部分支撑 | 可以留接口并用计划历史做趋势；还缺标准化扩招标签和当期官方计划差分表。 |

## 4. 建议的下一步数据表优先级

1. `graduate_outcome_school_year_profile`：升学画像表，聚合公开名单和官方报告指标。
2. `major_subject_ability_tags`：学科能力要求标签表。
3. `major_emerging_policy_evidence`：新质生产力/政策文献证据表。
4. `major_risk_tags`：高危、缩招、低热、低薪等风险标签表。
5. `major_ai_substitution_tags`：AI 替代性标签表。

第一阶段应优先做第 1 和第 2 张，因为它们直接服务考生决策，而且已有数据基础相对明确。
