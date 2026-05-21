# Major Intel 考生问题地图与检索能力设计

## 阅读说明

这份文档用于设计后续的“检索总入口”。它不直接定义页面或接口细节，而是先回答一个更上游的问题：一个高考考生、家长或志愿咨询老师，可能会围绕学校、专业、分数、位次、城市、就业和风险提出哪些问题。

后续所有检索能力都应从这份问题地图出发，而不是只写几个孤立接口。检索总入口的目标是让用户自然提问，系统自动识别意图、抽取槽位、调用本地数据库、标注数据口径，并在本地数据不足时进入缺口队列。

## 能力分级

本文把问题分成三档：

| 等级 | 含义 | 处理策略 |
|---|---|---|
| A | 本地库已有核心数据，第一版可以直接做 | 直接查本地 MySQL，输出结构化结果 |
| B | 本地库有部分数据，但不能覆盖完整结论 | 输出已有部分，并明确数据口径和缺失项 |
| C | 本地库缺核心数据，不能可靠回答 | 不生成确定结论，写入缺口队列，后续由联网 agent 或人工补充 |

## 通用输入槽位

检索总入口需要识别这些槽位。不是每个问题都需要全部槽位，但每个意图必须知道自己依赖哪些槽位。

| 槽位 | 示例 | 说明 |
|---|---|---|
| `school_name` | 杭州电子科技大学 | 学校名、简称、旧名、分校区名 |
| `major_name` | 计算机科学与技术 | 专业名、简称、专业代码、专业大类 |
| `province` | 广东、浙江、河南 | 考生所在省份或招生省份 |
| `subject_type` | 物理、历史、综合、理科、文科 | 新高考/传统高考科类 |
| `score` | 580 | 高考分数 |
| `rank` | 45000 | 省内位次，优先级高于分数 |
| `year` | 2025 | 数据年份，默认使用本地库最新年份 |
| `city_preference` | 上海、杭州、珠三角 | 城市或地域偏好 |
| `school_level_preference` | 211、双一流、公办、本科 | 学校层次偏好 |
| `major_preference` | 计算机、电气、医学 | 专业偏好，可为专业、专业类、方向 |
| `risk_preference` | 冲、稳、保 | 志愿风险偏好 |
| `budget_constraint` | 学费低、中外合作可接受 | 费用偏好 |
| `career_preference` | 考公、就业、读研、稳定 | 职业目标 |
| `personal_constraint` | 不想离家太远、数学不好 | 个性化约束 |
| `comparison_targets` | A 学校和 B 学校 | 对比对象 |

## 底层检索能力清单

上层用户问题可以非常多，但底层检索能力应尽量稳定。后续代码不要给每种自然语言问法都写一个独立查询，而应先归一成这些底层能力。

| 能力名 | 作用 | 当前支持 |
|---|---|---|
| `school_lookup` | 解析学校实体，返回学校基础信息 | A |
| `school_profile` | 学校概况、层次、地区、标签、官网 | A |
| `school_major_list` | 给学校查开设专业 | A |
| `school_department_major_list` | 给学校查院系和院系下专业 | A |
| `major_lookup` | 解析专业实体，返回专业基础信息 | A |
| `major_profile` | 专业介绍、学制、学位、通用薪资、就业方向 | A/B |
| `major_school_list` | 给专业查开设学校 | A |
| `school_major_profile` | 学校 + 专业组合解读 | A/B，已做 MVP |
| `subject_eval_lookup` | 学科评估查询 | A |
| `dual_class_lookup` | 双一流学科查询 | A |
| `employment_summary` | 学校级就业/升学数据 | B |
| `major_market_reference` | 专业通用市场和薪资参考 | B |
| `score_to_rank` | 分数转省内位次 | A |
| `rank_to_score` | 位次转分数区间 | A |
| `rank_to_school_match` | 按位次匹配可报学校 | A/B |
| `rank_to_major_match` | 按位次和专业匹配学校专业 | A/B |
| `admission_history` | 学校/专业历年录取分和位次 | A |
| `plan_history` | 学校/专业招生计划数 | A |
| `specialty_group_lookup` | 专业组、组内专业、选科要求 | A |
| `specialty_group_risk` | 专业组调剂风险初筛 | B |
| `subject_requirement_lookup` | 选科要求查询 | A/B |
| `comparison_query` | 学校、专业、学校专业组合对比 | B |
| `data_gap_detection` | 识别缺失数据并入队 | A，需要新增缺口表增强 |
| `source_trace_lookup` | 查证据来源、官网链接、报告来源 | B/C |
| `civil_service_mapping` | 专业到考公岗位映射 | C |
| `transfer_policy_lookup` | 转专业政策 | C |
| `fee_and_campus_lookup` | 学费线索、校区字段缺口 | B/C |
| `major_streaming_policy_lookup` | 大类分流政策和比例 | C |
| `policy_rule_lookup` | 招生政策、批次规则、特殊限制 | C |

## 当前实现状态

截至 2026-05-20，已有 23 个底层能力进入正式 function call 注册表，可以由后续 agent 自动调用：

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

其中：

- `rank_to_major_match` 已完成第一版，可以支撑“某省某科类某分数/位次想学某专业，能看哪些学校专业”的问题。
- `major_market_reference` 和 `civil_service_role_search` 属于提前完成能力，能读取已接入的市场样本和考公岗位样本，但仍必须保留数据口径提示。
- `specialty_group_lookup`、`subject_requirement_lookup`、`school_department_major_list`、`plan_history` 已经补齐，能覆盖专业组、选科、院系专业和招生计划类问题。
- `employment_summary`、`transfer_policy_lookup`、`fee_and_campus_lookup`、`specialty_group_risk` 已经进入正式工具层，但仍会在校专业级就业、官方转专业复核、稳定校区字段、真实分流比例处标注缺口。
- `civil_service_mapping` 仍处于部分完成状态：当前只有 `civil_service_role_search` 样本检索，正式可报判定、人工确认和政策解释还没有完成。
- 自然语言 agent 的离线规则入口、DeepSeek function-call agent 和统一入口已完成第一版，可以把高频中文问题自动归一到 intent、slots 和工具计划，也能把复杂问题交给 LLM 自动选择工具。
- 缺口队列 `data_gap_queue` 已完成第一版，统一入口遇到本地缺口时可以去重入队。
- 下一批主要剩 `comparison_query`、`major_streaming_policy_lookup`、`policy_rule_lookup`，以及让动态 RAG 和人工复核流程消费缺口队列。

## 考生问题总分类

### 1. 学校认知类

| 项目 | 内容 |
|---|---|
| 典型问法 | “这个学校怎么样？”、“杭州电子科技大学是什么层次？”、“这个学校是不是 211/双一流？”、“这个学校在本省认可度怎么样？” |
| 必填槽位 | `school_name` |
| 可选槽位 | `province`、`city_preference`、`career_preference` |
| 底层能力 | `school_lookup`、`school_profile`、`subject_eval_lookup`、`dual_class_lookup`、`employment_summary` |
| 本地支持 | A/B |
| 主要表 | `edu_university`、`edu_dual_class`、`edu_university_subject_eval`、`edu_university_employment` |
| 回答口径 | 学校基础属性可直接说；就业升学是学校级数据，不代表某个专业；本地库没有“本省认可度”的直接字段，只能通过地区、录取、就业数据辅助判断 |
| 缺口处理 | 本省认可度、行业口碑、校友评价进入缺口队列 |
| MVP 优先级 | 高 |

### 2. 学校专业列表类

| 项目 | 内容 |
|---|---|
| 典型问法 | “这个学校有哪些专业？”、“这个学校计算机类有哪些专业？”、“这个学校有哪些一流本科专业？”、“这个学校有哪些冷门专业？” |
| 必填槽位 | `school_name` |
| 可选槽位 | `major_preference`、`subject_type`、`province`、`year` |
| 底层能力 | `school_major_list`、`school_department_major_list`、`subject_eval_lookup` |
| 本地支持 | A/B |
| 主要表 | `edu_university`、`edu_school_major`、`edu_university_department`、`edu_university_department_major`、`edu_major` |
| 回答口径 | 可回答“本地库记录的开设专业”；如果带省份和年份，应切换到招生计划口径，不能把学校所有开设专业等同于某省当年招生专业 |
| 缺口处理 | “冷门专业”若没有明确定义，只能用录取位次、计划数、专业认知做风险提示，不能直接给死结论 |
| MVP 优先级 | 高 |

### 3. 专业认知类

| 项目 | 内容 |
|---|---|
| 典型问法 | “计算机科学与技术学什么？”、“机械专业就业怎么样？”、“这个专业适合女生吗？”、“这个专业是不是天坑？” |
| 必填槽位 | `major_name` |
| 可选槽位 | `career_preference`、`personal_constraint` |
| 底层能力 | `major_lookup`、`major_profile`、`major_market_reference` |
| 本地支持 | A/B |
| 主要表 | `edu_major` |
| 回答口径 | 专业介绍、学制、学位、通用就业方向可回答；薪资是专业通用参考，不代表某校某专业；“天坑”属于判断性表达，必须拆成就业面、薪资、学习难度、读研依赖、地域适配等维度 |
| 缺口处理 | 专业学习难度、适合人群、真实行业去向若无来源，进入缺口队列或给出低置信度提示 |
| MVP 优先级 | 高 |

### 4. 专业找学校类

| 项目 | 内容 |
|---|---|
| 典型问法 | “想学计算机有哪些学校？”、“电气工程哪些学校比较强？”、“中等分数能读哪些软件工程学校？” |
| 必填槽位 | `major_name` |
| 可选槽位 | `province`、`subject_type`、`score`、`rank`、`school_level_preference`、`city_preference` |
| 底层能力 | `major_school_list`、`subject_eval_lookup`、`rank_to_major_match` |
| 本地支持 | A/B |
| 主要表 | `edu_school_major`、`edu_university_department_major`、`edu_university_subject_eval`、`edu_school_admission_stats` |
| 回答口径 | 不带分数时回答“开设学校/学科实力”；带分数位次时回答“在某省某科类可报可能性” |
| 缺口处理 | 学校专业真实就业质量不足时列为缺口 |
| MVP 优先级 | 高 |

### 5. 学校 + 专业深度类

| 项目 | 内容 |
|---|---|
| 典型问法 | “杭州电子科技大学计算机怎么样？”、“广东工业大学自动化值得报吗？”、“某校某专业就业好吗？” |
| 必填槽位 | `school_name`、`major_name` |
| 可选槽位 | `province`、`subject_type`、`score`、`rank`、`year` |
| 底层能力 | `school_major_profile`、`admission_history`、`subject_eval_lookup`、`employment_summary`、`specialty_group_lookup`、`data_gap_detection` |
| 本地支持 | A/B，基础 MVP 已实现 |
| 主要表 | `edu_university`、`edu_major`、`edu_school_major`、`edu_university_subject_eval`、`edu_university_employment`、`edu_school_admission_stats`、`edu_college_specialty_group`、`edu_specialty_group_major` |
| 回答口径 | 必须区分校专业组合、学校级就业、专业通用薪资、招生专业组四种口径 |
| 缺口处理 | 校专业级薪资、Top 公司、官网专业介绍、转专业政策进入缺口队列 |
| MVP 优先级 | 高 |

### 6. 分数/位次匹配类

| 项目 | 内容 |
|---|---|
| 典型问法 | “广东物理 580 能上哪些学校？”、“河南理科 45000 位次能报哪些专业？”、“这个分数能不能上杭电？” |
| 必填槽位 | `province`、`subject_type`，以及 `score` 或 `rank` |
| 可选槽位 | `major_name`、`school_name`、`city_preference`、`school_level_preference`、`risk_preference`、`year` |
| 底层能力 | `score_to_rank`、`rank_to_school_match`、`rank_to_major_match`、`admission_history` |
| 本地支持 | A/B |
| 主要表 | `edu_score_rank`、`edu_school_admission_stats`、`edu_university_score_config`、`edu_university_score_group`、`edu_university_score_special` |
| 回答口径 | 位次优先于分数；如果只给分数，先转成对应省份科类位次；跨年份比较必须以位次为主；推荐结果是基于历史录取统计的风险分层，不是录取保证 |
| 缺口处理 | 缺省份、科类、分数/位次时需要追问；缺当年数据时回退到最近年份并说明 |
| MVP 优先级 | 最高 |

### 7. 冲稳保志愿策略类

| 项目 | 内容 |
|---|---|
| 典型问法 | “我这个分数怎么填志愿？”、“哪些学校适合冲？”、“哪些专业稳一点？”、“保底怎么选？” |
| 必填槽位 | `province`、`subject_type`，以及 `score` 或 `rank` |
| 可选槽位 | `major_preference`、`city_preference`、`school_level_preference`、`risk_preference` |
| 底层能力 | `score_to_rank`、`rank_to_school_match`、`rank_to_major_match`、`admission_history`、`specialty_group_risk` |
| 本地支持 | A/B |
| 主要表 | `edu_school_admission_stats`、`edu_score_rank`、`edu_college_specialty_group`、`edu_specialty_group_major` |
| 回答口径 | “冲稳保”应基于历史位次差、计划数、专业组构成和用户偏好；不能承诺录取；专业组调剂风险只能做初筛 |
| 缺口处理 | 真实调剂概率、院校当年政策变化进入缺口队列 |
| MVP 优先级 | 最高 |

### 8. 录取数据类

| 项目 | 内容 |
|---|---|
| 典型问法 | “某校历年录取分是多少？”、“某专业最低位次是多少？”、“这个专业分数线涨了吗？”、“招生人数有没有变化？” |
| 必填槽位 | 至少包含 `school_name` 或 `major_name`；如果问具体可报性，还需 `province`、`subject_type` |
| 可选槽位 | `year`、`batch` |
| 底层能力 | `admission_history`、`plan_history` |
| 本地支持 | A |
| 主要表 | `edu_school_admission_stats`、`edu_university_score_config`、`edu_university_score_group`、`edu_university_score_special`、`edu_university_plan_config`、`edu_university_plan_special_group`、`edu_university_plan_special` |
| 回答口径 | 历史分数必须带年份、省份、科类、批次；趋势判断应优先用位次，不只看分数 |
| 缺口处理 | 数据缺年份时列出已命中年份，不补写缺失年份 |
| MVP 优先级 | 高 |

### 9. 专业组风险类

| 项目 | 内容 |
|---|---|
| 典型问法 | “这个专业组里有哪些专业？”、“会不会被调剂到冷门专业？”、“专业组风险大不大？”、“这个组适不适合冲？” |
| 必填槽位 | `school_name` 或专业组标识；如果按报考场景，还需 `province`、`subject_type`、`year` |
| 可选槽位 | `major_name`、`score`、`rank`、`risk_preference` |
| 底层能力 | `specialty_group_lookup`、`specialty_group_risk`、`admission_history` |
| 本地支持 | A/B |
| 主要表 | `edu_college_specialty_group`、`edu_specialty_group_major`、`edu_university_plan_special_group`、`edu_university_plan_special`、`edu_university_score_group`、`edu_university_score_special` |
| 回答口径 | 可回答专业组构成、选科要求、计划数、历史最低分位次；“冷门风险”只能作为初筛标签，不等于真实分流或调剂概率 |
| 缺口处理 | 冷门定义、真实调剂比例、学校转专业兜底政策进入缺口队列 |
| MVP 优先级 | 高 |

### 10. 转专业与大类分流类

| 项目 | 内容 |
|---|---|
| 典型问法 | “入学后能不能转专业？”、“转专业难不难？”、“大类招生怎么分流？”、“会不会被分到冷门专业？” |
| 必填槽位 | `school_name` |
| 可选槽位 | `major_name`、`province`、`year` |
| 底层能力 | `transfer_policy_lookup`、`major_streaming_policy_lookup`、`data_gap_detection` |
| 本地支持 | C |
| 主要表 | 当前本地核心表不足，需要后续新增政策来源表 |
| 回答口径 | 不能凭经验回答某校转专业难度；必须有学校教务处、招生章程、培养方案或官方问答来源 |
| 缺口处理 | 直接进入缺口队列，联网 agent 抓学校官网或人工核验 |
| MVP 优先级 | 中高 |

### 11. 就业类

| 项目 | 内容 |
|---|---|
| 典型问法 | “这个专业毕业去哪里？”、“某校某专业去哪些公司？”、“工资分布怎么样？”、“适合考公吗？” |
| 必填槽位 | `major_name` 或 `school_name` + `major_name` |
| 可选槽位 | `city_preference`、`career_preference` |
| 底层能力 | `employment_summary`、`major_market_reference`、`civil_service_mapping`、`data_gap_detection` |
| 本地支持 | B/C |
| 主要表 | `edu_major`、`edu_university_employment`；考公和校专业级就业需要新增数据表 |
| 回答口径 | 学校就业数据是学校级；专业薪资是通用级；校专业级薪资、地域分布、Top 公司没有证据时不能写成事实 |
| 缺口处理 | 校专业级就业地域、薪资分布、Top 公司、考公岗位进入缺口队列 |
| MVP 优先级 | 中高 |

### 12. 升学深造类

| 项目 | 内容 |
|---|---|
| 典型问法 | “这个学校保研率怎么样？”、“这个专业适合考研吗？”、“升学率如何？”、“读研方向有哪些？” |
| 必填槽位 | `school_name` 或 `major_name` |
| 可选槽位 | `career_preference` |
| 底层能力 | `employment_summary`、`major_profile`、`subject_eval_lookup` |
| 本地支持 | B/C |
| 主要表 | `edu_university_employment`、`edu_major`、`edu_university_subject_eval` |
| 回答口径 | 学校升学率可回答学校级数据；专业是否适合读研可以结合专业性质和学科评估做解释，但不能伪造保研率 |
| 缺口处理 | 校专业保研率、考研去向、升学院校名单进入缺口队列 |
| MVP 优先级 | 中 |

### 13. 城市与地域选择类

| 项目 | 内容 |
|---|---|
| 典型问法 | “同分数去哪个城市更好？”、“想留在广东就业怎么选？”、“学校城市重要还是专业重要？” |
| 必填槽位 | 视问题而定，通常需要 `province`、`score` 或 `rank`、`city_preference` |
| 可选槽位 | `major_preference`、`career_preference` |
| 底层能力 | `rank_to_school_match`、`rank_to_major_match`、`employment_summary`、`comparison_query` |
| 本地支持 | B |
| 主要表 | `edu_university`、`edu_school_admission_stats`、`edu_university_employment` |
| 回答口径 | 城市建议属于决策建议，需要明确是基于录取可达性、城市产业、学校层次、专业适配综合判断；不能声称有完整当地就业认可度数据 |
| 缺口处理 | 城市产业岗位、校友就业地域、当地企业认可度进入缺口队列 |
| MVP 优先级 | 中 |

### 14. 费用与生活类

| 项目 | 内容 |
|---|---|
| 典型问法 | “学费多少？”、“中外合作值不值？”、“校区在哪里？”、“住宿条件怎么样？”、“生活成本高不高？” |
| 必填槽位 | `school_name`，有时需要 `major_name` |
| 可选槽位 | `budget_constraint`、`city_preference` |
| 底层能力 | `school_profile`、`plan_history`、`data_gap_detection` |
| 本地支持 | B/C |
| 主要表 | `edu_university`、`edu_university_plan_special`、`edu_specialty_group_major` |
| 回答口径 | 学费字段可作为招生计划口径；住宿、校区、生活成本需要官方或可靠来源 |
| 缺口处理 | 住宿条件、校区分布、生活成本、中外合作培养质量进入缺口队列 |
| MVP 优先级 | 中 |

### 15. 特殊限制与选科类

| 项目 | 内容 |
|---|---|
| 典型问法 | “色弱能不能报？”、“物化生能报哪些专业？”、“历史类能不能报计算机？”、“单科成绩有没有要求？” |
| 必填槽位 | `province`、`subject_type` 或具体选科组合；如果问某校某专业，还需 `school_name`、`major_name` |
| 可选槽位 | `year` |
| 底层能力 | `subject_requirement_lookup`、`specialty_group_lookup`、`plan_history` |
| 本地支持 | B/C |
| 主要表 | `edu_college_specialty_group`、`edu_specialty_group_major`、`edu_university_plan_special_group`、`edu_university_plan_special` |
| 回答口径 | 选科要求可从招生计划/专业组表回答；身体限制、单科要求必须以招生章程或专业备注为准 |
| 缺口处理 | 身体条件、单科成绩、语种限制进入缺口队列 |
| MVP 优先级 | 中高 |

### 16. 院校/专业/方案对比类

| 项目 | 内容 |
|---|---|
| 典型问法 | “A 学校和 B 学校怎么选？”、“杭电计算机和广工自动化哪个好？”、“选学校还是选专业？” |
| 必填槽位 | `comparison_targets` |
| 可选槽位 | `score`、`rank`、`province`、`subject_type`、`career_preference` |
| 底层能力 | `comparison_query`、`school_profile`、`major_profile`、`school_major_profile`、`admission_history` |
| 本地支持 | B |
| 主要表 | 对比对象对应的所有基础表和录取表 |
| 回答口径 | 对比必须拆成可解释维度：录取风险、学校层次、专业实力、城市、就业、升学、费用；不能输出单一绝对结论 |
| 缺口处理 | 缺就业、转专业、分流等关键证据时列出不确定项 |
| MVP 优先级 | 中 |

### 17. 个性化决策类

| 项目 | 内容 |
|---|---|
| 典型问法 | “我数学不好适合什么专业？”、“想稳定就业怎么选？”、“想考公怎么选专业？”、“不想离家太远怎么报？” |
| 必填槽位 | 至少一个个人偏好或约束 |
| 可选槽位 | `province`、`score`、`rank`、`subject_type`、`career_preference`、`city_preference` |
| 底层能力 | `rank_to_major_match`、`major_profile`、`comparison_query`、`civil_service_mapping` |
| 本地支持 | B/C |
| 主要表 | `edu_major`、`edu_school_admission_stats`、后续职业/考公映射表 |
| 回答口径 | 个性化建议必须把偏好翻译成筛选条件和风险权重；不能根据一句“数学不好”直接排除全部工科 |
| 缺口处理 | 职业倾向测评、学习能力画像、家庭约束长期保存需要用户档案表 |
| MVP 优先级 | 中 |

### 18. 数据可信度与来源类

| 项目 | 内容 |
|---|---|
| 典型问法 | “这些数据来自哪里？”、“这个薪资可信吗？”、“没查到是不是代表没有？”、“为什么结果和官网不一样？” |
| 必填槽位 | 用户正在查看的回答或实体 |
| 可选槽位 | `school_name`、`major_name`、`year` |
| 底层能力 | `source_trace_lookup`、`data_gap_detection` |
| 本地支持 | B/C |
| 主要表 | 当前需要依赖原始表字段；后续应新增 `source_documents` 或同类证据表 |
| 回答口径 | 必须区分“本地库未命中”和“事实不存在”；薪资、就业、录取都需要说明年份、来源、样本口径 |
| 缺口处理 | 没有来源链接的字段标记低证据等级，进入证据补全队列 |
| MVP 优先级 | 高 |

### 19. 政策与批次规则类

| 项目 | 内容 |
|---|---|
| 典型问法 | “平行志愿怎么录取？”、“专业服从调剂是什么意思？”、“提前批能不能报？”、“地方专项有什么限制？” |
| 必填槽位 | `province`，有时需要 `year` |
| 可选槽位 | `school_name`、`major_name`、`subject_type` |
| 底层能力 | `data_gap_detection`、后续政策检索能力 |
| 本地支持 | C |
| 主要表 | 当前核心库不足，需要省考试院政策、招生章程、批次规则来源表 |
| 回答口径 | 这类问题高风险，必须引用当年省考试院或招生章程；不能只给通用解释后替用户做政策判断 |
| 缺口处理 | 进入政策资料抓取和人工核验队列 |
| MVP 优先级 | 中 |

### 20. 兜底追问类

| 项目 | 内容 |
|---|---|
| 典型问法 | “我该怎么选？”、“帮我推荐一下”、“这个专业好不好？” |
| 必填槽位 | 取决于追问目标，通常需要补齐省份、科类、分数/位次、专业/城市/职业偏好 |
| 可选槽位 | 所有通用槽位 |
| 底层能力 | `data_gap_detection`、意图澄清、槽位追问 |
| 本地支持 | A，作为流程能力 |
| 主要表 | 不直接查表，先补槽位 |
| 回答口径 | 当关键信息不足时，先问 1 到 3 个最关键问题；不要在信息不足时直接给志愿推荐 |
| 缺口处理 | 用户拒绝补充时，只能给通用分析框架 |
| MVP 优先级 | 高 |

## 高频自然语言问法归一

同一个底层能力会对应很多用户问法。检索总入口需要做归一，而不是为每句话单独写逻辑。

| 用户问法 | 归一意图 | 关键槽位 |
|---|---|---|
| “杭电有什么专业？” | `school_major_list` | `school_name` |
| “杭电计算机怎么样？” | `school_major_profile` | `school_name`、`major_name` |
| “计算机哪些学校强？” | `major_school_list` + `subject_eval_lookup` | `major_name` |
| “广东物理 580 想学计算机” | `rank_to_major_match` | `province`、`subject_type`、`score`、`major_name` |
| “45000 位次能冲什么？” | `rank_to_school_match` | `rank`，需要追问 `province`、`subject_type` |
| “这个专业组风险大吗？” | `specialty_group_risk` | 专业组标识，通常还需 `province`、`year` |
| “能不能转专业？” | `transfer_policy_lookup` | `school_name` |
| “适合考公吗？” | `civil_service_mapping` | `major_name` |
| “A 和 B 怎么选？” | `comparison_query` | `comparison_targets` |
| “数据靠谱吗？” | `source_trace_lookup` | 当前回答上下文 |

## 本地库现有表与可支撑问题

| 表 | 可支撑能力 |
|---|---|
| `edu_university` | 学校解析、学校基础信息、学校层次、地区、官网 |
| `edu_major` | 专业解析、专业介绍、学制、学位、通用薪资和就业方向 |
| `edu_school_major` | 学校开设专业、专业开设学校、校专业组合初筛 |
| `edu_university_department` | 院系信息、院系官网、院系结构 |
| `edu_university_department_major` | 学校院系下专业、专业一流/特色/学科评估字段 |
| `edu_dual_class` | 双一流学科 |
| `edu_university_subject_eval` | 教育部学科评估 |
| `edu_university_employment` | 学校级就业率、升学率、就业行业/地区/雇主字段 |
| `edu_score_rank` | 分数与位次互转 |
| `edu_school_admission_stats` | 专业级录取统计、冲稳保分数位次、计划数 |
| `edu_university_score_config` | 学校录取配置入口 |
| `edu_university_score_group` | 专业组录取分和位次 |
| `edu_university_score_special` | 专业录取分和位次 |
| `edu_university_plan_config` | 招生计划配置入口 |
| `edu_university_plan_special_group` | 招生专业组和选科 |
| `edu_university_plan_special` | 专业招生计划和学费 |
| `edu_college_specialty_group` | 专业组样本、计划数、分数、位次 |
| `edu_specialty_group_major` | 专业组内专业、选科、备注 |

## 需要新增或强化的数据表

这些表不是所有功能开始前都必须建，但要做成可靠产品时会逐步需要。

| 表 | 必要性 | 用途 |
|---|---|---|
| `query_logs` | 高 | 记录用户原始问题、解析出的槽位、命中的意图、命中的实体 |
| `retrieval_cache` | 高 | 缓存同类问题结果，减少重复查库和重复生成 |
| `data_gap_queue` | 高 | 记录本地库缺失的数据，供联网 agent 或人工处理 |
| `entity_aliases` | 高 | 存放已确认的学校/专业/地区/专业组别名 |
| `entity_alias_candidates` | 高 | 存放自动发现但待确认的别名 |
| `source_documents` | 中高 | 存证据来源、URL、抓取时间、证据等级 |
| `school_major_evidence` | 中高 | 存某校某专业官网介绍、培养方案、学院页面 |
| `transfer_policy_sources` | 中高 | 存转专业政策来源、年份、摘要、适用范围 |
| `major_streaming_sources` | 中高 | 存大类分流政策、分流规则、比例证据 |
| `civil_service_major_roles` | 中 | 专业代码到考公岗位、岗位大类、限制条件的映射 |
| `candidate_profiles` | 中 | 如果做登录或长期跟踪，用于保存考生省份、科类、分数、偏好 |

## 检索总入口建议

详细设计已经落到 `docs/specs/natural-language-entrypoint.md`。本节保留为问题地图里的总入口摘要；实现时以后者为准。

总入口不应让用户手动选择模式，而应自动完成以下流程。

```text
用户问题
  -> 文本清洗
  -> 实体识别：学校、专业、省份、城市、分数、位次、科类、年份
  -> 意图识别：学校、专业、分数匹配、录取、专业组、就业、对比等
  -> 槽位完整性检查
  -> 必要时追问
  -> 调用一个或多个底层检索能力
  -> 合并结构化结果
  -> 标注数据口径
  -> 识别缺失项
  -> 输出回答或写入缺口队列
```

总入口的输出建议同时包含结构化 JSON 和可读 Markdown。

```text
{
  "intent": "rank_to_major_match",
  "slots": {
    "province": "广东",
    "subject_type": "物理",
    "score": 580,
    "major_name": "计算机"
  },
  "retrieval_calls": [
    "score_to_rank",
    "rank_to_major_match",
    "admission_history",
    "data_gap_detection"
  ],
  "answer_markdown": "...",
  "data_gaps": [...],
  "source_scope_notes": [...]
}
```

## 第一批建议实现范围

为了尽快覆盖考生高频问题，第一批检索总入口建议实现以下 10 类能力。

| 顺序 | 能力 | 原因 |
|---:|---|---|
| 1 | 给学校查学校概况和专业列表 | 高频、数据完整、实现成本低 |
| 2 | 给专业查专业概况和开设学校 | 高频、数据完整、可复用专业解析 |
| 3 | 学校 + 专业深度解读 | 已有 MVP，可继续增强 |
| 4 | 分数转位次 | 志愿推荐基础能力 |
| 5 | 位次匹配学校 | 把录取数据变成可用推荐 |
| 6 | 位次 + 专业匹配学校专业 | 最接近考生真实问题 |
| 7 | 历年录取查询 | 所有推荐都需要证据 |
| 8 | 专业组构成查询 | 新高考志愿风险核心 |
| 9 | 数据缺口检测和入队 | 防止模型瞎编 |
| 10 | 基础对比能力 | 覆盖家长常见决策问题 |

## 回答原则

1. 能查到的事实必须带数据口径，例如学校级、专业通用级、校专业级、专业组级。
2. 没查到不等于不存在，必须表达为“本地库暂未命中”。
3. 分数推荐优先使用位次，跨年份比较不能只看分数。
4. 就业和薪资不能用一个单点数字下结论，必须说明样本来源和适用范围。
5. 专业组风险不能等同于真实分流比例，除非有学校官方政策或历史数据。
6. 转专业、身体限制、单科要求、招生政策属于高风险问题，必须有官方来源。
7. 个性化建议要把用户偏好翻译成筛选条件和风险权重，而不是直接给主观结论。

## 下一步实施建议

检索总入口第一批能力已经落到 `scripts/natural_language_entrypoint.py`。后续继续演进时，仍建议保持轻量命令行或 API 层的输出结构稳定，输入自然语言或结构化参数，输出：

```text
intent
slots
retrieval_calls
structured_result
answer_markdown
data_gaps
scope_notes
```

在实现之前，先为每个底层能力写测试，尤其覆盖：

- 学校名和专业名能正确解析。
- 缺省份、科类、分数时会追问。
- 只给分数时会尝试转位次。
- 查不到数据时不会生成确定结论。
- 学校级、专业通用级、校专业级、专业组级口径不会混用。
