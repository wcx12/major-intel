# 专业 AI 可替代性数据方案

## 阅读说明

本文档把“专业 AI 可替代性”从一个主观判断问题，落成 Major Intel 项目内可以逐步实现、可追溯、可复核的数据产品方案。

本文档日期：2026-06-12。

本文档默认中国口径优先。国外数据源只作为任务拆解或方法参考，不作为中国就业行情的主结论。

## 一句话方案

不要直接判断“某专业会不会被 AI 取代”，而是建立这条链路：

```text
专业
  -> 中国招聘市场中的岗位候选
  -> 中国职业分类标准化
  -> 岗位任务拆解
  -> 任务级 AI 暴露度和自动化替代度
  -> 线下、资质、监管、人际信任等中国本地阻力修正
  -> 专业级 AI 可替代性画像
```

最终输出不应该只有一个分数，而应该至少包含：

- `ai_exposure_score`: AI 暴露度，表示相关岗位有多少任务会被 AI 影响。
- `automation_risk_score`: 自动化替代风险，表示相关任务被 AI 独立完成的可能性。
- `ai_assist_value_score`: AI 增效价值，表示 AI 作为工具能提升多少效率。
- `human_barrier_score`: 人类、线下、资质、信任阻力。
- `confidence_score`: 数据置信度。
- `top_risk_jobs`: 高风险岗位方向。
- `top_resilient_jobs`: 相对抗替代岗位方向。
- `evidence_summary`: 可追溯证据摘要。

## 目标和非目标

### 目标

1. 为本科和专科专业建立“中国行情优先”的专业 AI 可替代性画像。
2. 复用项目已爬取的 rysxai 专业市场快照，先跑通第一版专业到岗位映射。
3. 使用中国职业分类体系和国家职业标准，逐步把岗位映射到标准职业和任务。
4. 在输出中清楚区分“官方事实”“第三方市场样本”“模型评分”。
5. 支持后续新增 function call，例如 `major_ai_substitutability`。

### 非目标

1. 不把第三方招聘样本包装成官方毕业生就业去向。
2. 不承诺预测某专业未来一定会消失或保留。
3. 不把学校级就业率套用到某个具体专业。
4. 不用单一大模型直接给专业拍分。
5. 不把美国 O*NET 或论文里的职业暴露度直接当成中国结论。

## 现有本地数据结论

### 可直接复用的数据

本项目已经有一套可直接作为第一版底座的专业市场数据：

```text
data/processed/rysxai/
```

本地核验结果：

- 专业市场快照文件：1616 个。
- 含可用市场字段的快照：1612 个。
- 覆盖字段包括：
  - `macro_employment.industry_distribution`
  - `macro_employment.region_distribution`
  - `macro_employment.job_direction_distribution`
  - `job_posting_samples`
  - `salary_observations_by_city`
  - `salary_observations_by_industry`

对应处理代码：

```text
src/major_intel/crawlers/rysxai_market_crawler.py
src/major_intel/ingestion/rysxai_data.py
src/major_intel/reporting/rysxai_market_report.py
```

这部分数据可以用来生成第一版 `专业 -> 岗位候选`，但数据等级必须保持为第三方市场观察。

### 只能辅助使用的数据

```text
data/cleaned/graduate_outcomes/master_records_public.csv
data/cleaned/graduate_outcomes/master_records_clean.csv
```

这两张表主要来自考研、推免、录取名单链路，字段包括：

- `undergraduate_school`
- `undergraduate_major`
- `major`
- `admission_major`
- `route`
- `document_type`

抽样前 200000 行的本地核验结果：

- `undergraduate_major` 非空约 0.9%。
- `major` 非空约 39.3%。
- `admission_major` 非空约 86.2%。
- 数据主语偏读研/推免/录取去向，不是毕业就业岗位。

因此它们适合用于“升学流向”补充，不适合作为“就业岗位流向”主数据。

### 官方就业报告数据

```text
data/cleaned/graduate_outcomes/official_employment_report_metrics.csv
data/cleaned/graduate_outcomes/official_employment_report_sources.csv
data/cleaned/graduate_outcomes/undergraduate_school_outcome_summary.csv
```

这些数据主要是学校级或报告级指标，例如：

- 本科毕业去向落实率
- 升学率
- 出国境率
- 灵活就业率
- 官方报告来源 URL

这部分只能用于学校级就业背景和质量校验，不能直接代表某校某专业的岗位去向。

### 专业基础表

```text
data/seeds/rysxai_professions.full.csv
```

本地核验结果：

- 专业记录：1653 条。
- 字段包括：
  - `rysxai_profession_id`
  - `major_code`
  - `major_name`
  - `level`
  - `category`
  - `subject`
  - `degree`
  - `limit_year`
  - `heat`
  - `is_hot`

这张表可以做专业种子表，但最终应与教育部专业目录对齐。

## 中国口径优先的数据源

### 专业目录

优先级：

1. 教育部《普通高等学校本科专业目录》。
2. 教育部职业教育专业目录。
3. 项目本地 `edu_major`、`rysxai_professions.full.csv` 作为已入库或第三方补充。

说明：

- 本科专业目录用于本科专业代码、专业名称、门类、专业类标准化。
- 职业教育专业目录用于专科专业标准化。
- 如果第三方专业名称和教育部目录不一致，应以教育部目录为准，第三方名称进入 alias 表。

参考：

- 教育部 2025 年本科专业目录发布页：`https://www.moe.gov.cn/srcsite/A08/moe_1034/s4930/202504/t20250422_1188239.html`
- 阳光高考专业库：`https://gaokao.chsi.com.cn/`

### 职业分类

优先级：

1. 《中华人民共和国职业分类大典（2022年版）》。
2. 技能人才评价工作网的职业分类系统和职业标准系统。
3. 人社部新职业发布和国家职业标准更新。

用途：

- 把招聘岗位、岗位方向、行业词映射到标准职业。
- 解决同义岗位问题，例如“Java 开发”“后端工程师”“软件开发工程师”应归到更稳定的职业或职业族。
- 给职业任务拆解提供标准入口。

参考：

- 中国人力资源市场网关于 2022 版职业分类大典的报道：`https://chrm.mohrss.gov.cn/%E6%96%B0%E7%89%88%E8%81%8C%E4%B8%9A%E5%88%86%E7%B1%BB%E5%A4%A7%E5%85%B8%E5%87%80%E5%A2%9E158%E4%B8%AA%E6%96%B0%E8%81%8C%E4%B8%9A/`
- 技能人才评价工作网国家职业标准查询：`https://www.osta.org.cn/skillStandard`

### 招聘市场数据

可使用：

- rysxai 已爬快照。
- 合规授权的招聘平台数据。
- 国家大学生就业服务平台公开岗位信息。
- 学校就业信息网公开招聘岗位。

注意：

- 招聘数据只能代表市场需求样本。
- 招聘数据不能代表毕业生实际就业去向。
- 招聘 JD 中的岗位职责、技能要求比岗位标题更有价值。

### 学校就业数据

可使用：

- 官方毕业生就业质量年度报告。
- 本科教学质量报告中的就业去向章节。
- 学院或专业培养质量报告。
- 学校就业信息网和官方新闻中的典型去向。

注意：

- 学校级指标只用于背景。
- 专业级就业去向必须保留来源和粒度。
- 不同学校、不同年份、不同学历层次不能直接混合。

## 数据等级约定

建议沿用项目已有 `source_level` 思路，增加 AI 可替代性专用分级。

| 等级 | 含义 | 可用于最终结论吗 |
|---|---|---|
| A | 国家部委、教育部目录、人社部职业分类、国家职业标准 | 可以作为基准事实 |
| B | 学校官方就业质量报告、教学质量报告、学院官方材料 | 可以作为学校或专业证据 |
| C | rysxai、招聘平台、第三方市场样本 | 只能作为市场观察 |
| D | 模型抽取、模型映射、模型评分 | 必须带置信度和复核状态 |
| E | 未核验文本、论坛、经验帖、短视频口播 | 默认不进入正式分数 |

## 数据模型设计

### 专业到岗位候选表

表名建议：

```text
ai_major_job_candidates
```

字段：

```text
id
major_code
major_name
major_level
profession_id
raw_job_text
normalized_job_title
job_group
industry_label
rate_percent
sample_count
source_name
source_level
source_field
evidence_json
captured_at
confidence_score
review_status
created_at
updated_at
```

抽取规则：

1. 优先抽 `job_direction_distribution.detail_jobs`。
2. 其次抽 `job_direction_distribution.label`。
3. 再抽 `job_posting_samples.job_title`。
4. 最后抽 `industry_distribution.label`，但标记为行业或方向，不直接当岗位。

过滤规则：

- 过滤 `其他`、空值、明显乱码。
- 过滤过泛行业词，例如“互联网”“房地产”“金融投资”，除非只有行业粒度。
- 对“销售业务”“艺术设计”“机械设计/制造”等岗位族保留，但 `job_type` 标为 `job_group`。
- 对“Java 开发工程师”“后端开发”“软件工程师”等做同义归并。

### 岗位到中国职业映射表

表名建议：

```text
ai_job_occupation_mapping
```

字段：

```text
id
raw_job_text
normalized_job_title
occupation_code
occupation_name
occupation_category_l1
occupation_category_l2
occupation_category_l3
mapping_method
mapping_confidence
evidence_text
source_level
review_status
created_at
updated_at
```

映射方法：

1. 精确词典匹配。
2. 同义词和别名匹配。
3. 中文 embedding 召回。
4. LLM 辅助判定。
5. 高频岗位人工复核。

`mapping_method` 可取值：

```text
exact_catalog
alias_dictionary
embedding_candidate
llm_candidate
manual_verified
manual_rejected
```

### 职业任务表

表名建议：

```text
ai_occupation_tasks
```

字段：

```text
id
occupation_code
occupation_name
task_name
task_description
task_type
task_weight
source_name
source_level
source_url
evidence_text
confidence_score
created_at
updated_at
```

任务来源优先级：

1. 国家职业标准中的职业功能、工作内容、技能要求。
2. 中国招聘 JD 中的岗位职责和技能要求。
3. 高校培养方案中的培养目标和就业方向。
4. O*NET、ESCO 等国外任务库，仅作补充。

任务类型建议：

```text
text_document
data_analysis
software_coding
design_creation
customer_communication
sales_business
onsite_operation
equipment_maintenance
quality_inspection
medical_legal_education
management_decision
research_development
```

### 任务级 AI 评分表

表名建议：

```text
ai_task_substitutability_scores
```

字段：

```text
id
task_id
model_version
scoring_run_id
ai_assist_score
ai_automation_score
physical_barrier_score
license_barrier_score
human_trust_barrier_score
liability_barrier_score
china_local_modifier
final_task_risk_score
final_task_assist_score
rationale
evidence_json
review_status
created_at
updated_at
```

评分范围建议统一为 0 到 100。

含义：

- `ai_assist_score`: AI 辅助价值。
- `ai_automation_score`: AI 独立完成可能性。
- `physical_barrier_score`: 线下、设备、现场操作阻力。
- `license_barrier_score`: 执业资格、监管、准入阻力。
- `human_trust_barrier_score`: 信任、关系、情绪劳动、人际判断阻力。
- `liability_barrier_score`: 责任签字、事故责任、法律后果阻力。
- `china_local_modifier`: 中国市场、本地监管、组织形态修正。

建议公式：

```text
barrier = max(
  physical_barrier_score,
  license_barrier_score,
  human_trust_barrier_score,
  liability_barrier_score
)

final_task_risk_score =
  ai_automation_score * (1 - barrier / 100) * china_local_modifier

final_task_assist_score =
  ai_assist_score * china_local_modifier
```

`china_local_modifier` 默认 1.0，可在 0.7 到 1.2 之间调整。

示例：

- 公务员岗位：AI 辅助可能高，但自动化替代风险应受编制、流程、责任约束下调。
- 医生岗位：文书和影像辅助暴露高，但诊疗责任和资质阻力强。
- 软件开发初级岗位：自动化暴露高，但复杂系统设计、业务沟通、责任归属会降低完全替代判断。
- 设备维修岗位：AI 可辅助诊断，但现场操作阻力高。

### 专业级画像表

表名建议：

```text
ai_major_substitutability_profiles
```

字段：

```text
id
major_code
major_name
major_level
scoring_run_id
ai_exposure_score
automation_risk_score
ai_assist_value_score
human_barrier_score
confidence_score
risk_level
assist_level
top_risk_jobs_json
top_resilient_jobs_json
evidence_summary_json
warnings_json
created_at
updated_at
```

风险等级建议：

| 分数 | 等级 |
|---|---|
| 0-20 | 很低 |
| 20-40 | 较低 |
| 40-60 | 中等 |
| 60-80 | 较高 |
| 80-100 | 很高 |

输出时必须同时展示置信度。如果 `confidence_score < 60`，页面或回答中必须提示“数据不足，仅作初筛”。

### 评分运行元数据表

表名建议：

```text
ai_scoring_runs
```

字段：

```text
scoring_run_id
run_name
model_name
model_version
prompt_version
data_snapshot_version
created_by
created_at
notes
```

用途：

- 记录每次评分使用的数据快照和模型版本。
- 支持后续重新评分和回溯。
- 避免同一专业不同时间分数不可解释。

## 核心算法

### 第一步：专业岗位池抽取

输入：

```text
data/processed/rysxai/profession_*_market_snapshot.json
```

抽取逻辑：

```text
for each snapshot:
  read profession.id / code / name / level
  extract job_direction_distribution.detail_jobs
  extract job_direction_distribution.label
  extract job_posting_samples.job_title
  extract industry_distribution.label as fallback
  normalize text
  deduplicate
  assign preliminary weight
  write ai_major_job_candidates
```

候选权重建议：

```text
weight = normalized_rate_percent * source_quality_weight * field_quality_weight
```

`field_quality_weight` 建议：

| 字段来源 | 权重 |
|---|---|
| `job_direction_distribution.detail_jobs` | 1.00 |
| `job_direction_distribution.label` | 0.85 |
| `job_posting_samples.job_title` | 0.70 |
| `industry_distribution.label` | 0.45 |

`source_quality_weight`：

```text
rysxai_market_snapshot = 0.75
official_professional_report = 1.00
official_school_report_major_level = 0.95
job_posting_authorized_sample = 0.80
llm_inferred = 0.40
```

### 第二步：岗位标准化

目标：

```text
raw_job_text -> normalized_job_title -> occupation_code
```

处理顺序：

1. 清洗标点、空格、括号、地区、薪资、年限。
2. 同义归一，例如：
   - `Java开发`、`后端开发工程师`、`软件开发工程师`
   - `机械制图员`、`CAD制图员`
   - `新媒体运营`、`内容运营`
3. 匹配中国职业分类或职业族。
4. 对匹配置信度低于 70 的进入人工复核队列。

人工优先复核对象：

- 出现频次最高的前 500 个岗位。
- 权重最高的前 300 个专业-岗位组合。
- 医学、法学、教育、工程、金融等高风险解释专业。

### 第三步：职业任务拆解

任务拆解不要只靠招聘标题。

优先从国家职业标准抽：

```text
职业功能
工作内容
技能要求
相关知识要求
```

如果国家职业标准缺失，再从招聘 JD 和高校培养方案抽：

```text
岗位职责
任职要求
工具技能
交付物
工作场景
```

任务权重可来自：

- 职业标准中的层级结构。
- JD 中出现频次。
- 专家规则。
- 人工复核。

### 第四步：任务级 AI 评分

建议先做规则 + LLM 的混合评分。

基础规则：

| 任务类型 | AI 辅助 | 自动化替代 | 阻力 |
|---|---:|---:|---:|
| 文本撰写、总结、翻译 | 高 | 中高 | 低 |
| 数据整理、报表、基础分析 | 高 | 中高 | 低 |
| 代码生成、脚本、测试 | 高 | 中高 | 中 |
| 视觉设计、营销物料 | 高 | 中 | 中 |
| 销售沟通、客户关系 | 中高 | 中低 | 高 |
| 医疗诊断、法律意见、教学评价 | 高 | 低到中 | 很高 |
| 设备操作、施工、护理、维修 | 中 | 低 | 很高 |
| 管理决策、组织协调 | 中高 | 低到中 | 高 |

LLM 评分提示词必须要求输出：

```text
score fields:
  ai_assist_score
  ai_automation_score
  physical_barrier_score
  license_barrier_score
  human_trust_barrier_score
  liability_barrier_score
  china_local_modifier
  rationale
  uncertainty
```

禁止让模型只输出一个总分。

### 第五步：专业级聚合

每个专业的岗位权重先归一化：

```text
job_weight_i = raw_job_weight_i / sum(raw_job_weight)
```

岗位风险：

```text
job_automation_risk =
  sum(task_weight * final_task_risk_score)
```

专业风险：

```text
major_automation_risk =
  sum(job_weight * job_automation_risk)
```

专业 AI 暴露度：

```text
major_ai_exposure =
  sum(job_weight * sum(task_weight * ai_assist_score))
```

人类阻力：

```text
major_human_barrier =
  sum(job_weight * sum(task_weight * barrier))
```

置信度：

```text
confidence =
  data_coverage_score
  * mapping_confidence_score
  * task_source_quality_score
  * review_status_score
```

其中：

- `data_coverage_score`: 该专业岗位样本是否充足。
- `mapping_confidence_score`: 岗位到职业映射是否可靠。
- `task_source_quality_score`: 任务是否来自国家职业标准或高质量 JD。
- `review_status_score`: 是否经过人工复核。

## 中国本地修正规则

### 资质和监管

这些专业相关岗位不能只按任务文本高低判断：

- 临床医学
- 口腔医学
- 护理学
- 法学
- 会计学、审计学
- 教育学、师范类
- 土木工程、建筑学、城乡规划
- 电气工程、自动化、机械工程中的安全责任岗位

修正规则：

```text
if occupation requires license or professional qualification:
  license_barrier_score >= 70
```

### 编制、国企、公共部门

考公、事业单位、国企岗位存在强组织流程和责任边界。

修正规则：

```text
if job route is civil_service_or_public_sector:
  automation_risk_score downweight
  ai_assist_value_score can remain high
```

### 线下交付

制造、护理、维修、施工、检测、实验、物流等岗位需要现场操作。

修正规则：

```text
if task_type in onsite_operation/equipment_maintenance/quality_inspection:
  physical_barrier_score >= 60
```

### 初级岗位和高级岗位区分

同一专业内部，初级岗位更容易受 AI 影响，高级岗位更偏 AI 增效。

示例：

- 初级文案、资料整理、基础客服：替代风险较高。
- 高级品牌策略、复杂客户管理、组织协调：替代风险降低。
- 初级代码实现：暴露度高。
- 架构设计、复杂业务建模、跨团队协作：替代风险降低。

## 第一版 MVP 实施计划

### P0：离线数据集生成

目标：

基于已有 rysxai 快照生成 `专业 -> 岗位候选` CSV 或 JSONL。

产物：

```text
data/processed/ai_substitutability/major_job_candidates.csv
data/processed/ai_substitutability/major_job_candidates.review_sample.csv
```

验收：

- 覆盖不少于 1500 个专业。
- 每个有数据专业至少保留 3 个岗位或岗位方向。
- 高频岗位完成初步归一。
- 明确保留 `source_level=C` 和来源字段。

### P1：数据库入库

目标：

新增 AI 可替代性相关表，至少入库：

- `ai_major_job_candidates`
- `ai_job_occupation_mapping`
- `ai_scoring_runs`

验收：

- 支持按 `major_code` 和 `major_name` 查询候选岗位。
- 支持查看每个岗位候选的来源字段和证据。
- 不污染已有招生、就业、专业主表。

### P2：职业映射

目标：

把高频岗位映射到中国职业分类或职业族。

产物：

```text
data/processed/ai_substitutability/job_occupation_mapping.csv
data/processed/ai_substitutability/job_occupation_mapping_review_queue.csv
```

验收：

- 高频前 500 个岗位完成映射。
- 映射置信度低于 70 的进入复核队列。
- 医学、法学、教育、工程、金融类重点岗位人工抽检。

### P3：任务库和评分

目标：

先为前 100 个高频职业或职业族建立任务库和任务级 AI 评分。

产物：

```text
data/processed/ai_substitutability/occupation_tasks.csv
data/processed/ai_substitutability/task_ai_scores.csv
```

验收：

- 每个职业至少 5 个任务。
- 每个任务同时有辅助分、自动化分、阻力分和解释。
- 评分输出可复现，记录 prompt 和模型版本。

### P4：专业画像生成

目标：

生成专业级 AI 可替代性画像。

产物：

```text
data/processed/ai_substitutability/major_ai_profiles.csv
reports/ai_substitutability/major_ai_profile_samples.md
```

验收：

- 每个专业输出 5 个核心指标。
- 每个专业输出高风险岗位和低风险岗位。
- 置信度低的专业必须提示数据不足。

### P5：function call 接入

目标：

新增工具：

```text
major_ai_substitutability
```

输入：

```json
{
  "major": "计算机科学与技术",
  "level": "本科",
  "province": "浙江",
  "school": "可选"
}
```

输出：

```text
专业 AI 可替代性画像
AI 暴露度
自动化替代风险
AI 增效价值
主要受影响岗位
相对抗替代岗位
中国本地修正说明
证据来源和置信度
口径提醒
```

验收：

- 工具输出不能只给一个分数。
- 工具必须展示来源等级。
- 工具必须区分“市场样本”和“官方就业事实”。
- 无数据时返回缺口，不编造。

## 验证方案

### 抽样专业

建议至少人工审查 60 个专业：

高风险候选：

- 电子商务
- 市场营销
- 新闻学
- 广告学
- 汉语言文学
- 秘书学
- 信息管理与信息系统
- 数字媒体技术
- 视觉传达设计
- 会计学

中等风险候选：

- 计算机科学与技术
- 软件工程
- 金融学
- 法学
- 工商管理
- 人力资源管理
- 工业设计
- 机械工程
- 自动化
- 电子信息工程

低风险或高阻力候选：

- 临床医学
- 口腔医学
- 护理学
- 动物医学
- 土木工程
- 建筑学
- 电气工程及其自动化
- 车辆工程
- 食品质量与安全
- 应急技术与管理

### 人工审查问题

每个专业审查：

1. 岗位池是否符合中国就业市场常识。
2. 是否把行业词误当成岗位。
3. 是否遗漏关键岗位。
4. 是否过度依赖第三方样本。
5. 职业映射是否合理。
6. 任务拆解是否贴近真实工作。
7. AI 替代风险是否被资质、现场、人际因素正确修正。

### 自动化测试

建议新增测试：

```text
tests/ai_substitutability/test_major_job_candidate_extraction.py
tests/ai_substitutability/test_job_occupation_mapping.py
tests/ai_substitutability/test_task_score_formula.py
tests/ai_substitutability/test_major_profile_generation.py
```

关键测试：

- `其他` 不应进入岗位候选。
- `industry_distribution` 只能作为低权重兜底。
- 医学、法律、教师等任务必须有较高资质阻力。
- 低置信度映射不能直接进入正式画像。
- 无数据专业必须返回缺口。

## 输出示例

以“计算机科学与技术”为例，最终回答应类似：

```text
计算机科学与技术的 AI 暴露度较高，自动化替代风险中高，AI 增效价值很高。

主要受影响岗位：
- 初级软件开发
- 测试开发
- 数据处理和报表分析
- 技术文档和运维脚本

相对抗替代岗位：
- 系统架构
- 复杂业务系统设计
- 安全攻防
- 大型工程协作和技术管理

中国本地修正：
- 互联网和软件外包市场中，初级编码任务更容易被 AI 压缩。
- 但复杂业务理解、系统责任、工程协同和客户交付仍有明显人类阻力。
- 考公、国企、事业单位相关岗位受组织流程影响，不能简单按任务可自动化程度判断。

口径：
- 岗位池来自第三方招聘市场样本和专业市场快照，不代表某校某专业官方就业去向。
- 分数为任务级模型评分聚合结果，需要结合年份和地区更新。
```

## 风险和注意事项

### 数据风险

- rysxai 数据是第三方市场样本，不能代表官方就业结论。
- 招聘岗位标题存在噪声，可能混入行业、岗位族、公司自定义名称。
- 不同专业名称在本科、专科、研究生层次可能含义不同。
- 医学、法学、教育等专业不能只按文本任务判断。

### 算法风险

- LLM 容易高估文本类工作的替代风险。
- LLM 容易低估线下操作、组织责任、监管合规的阻力。
- 如果岗位映射错误，专业分数会系统性偏差。
- 如果只输出总分，会误导用户。

### 产品风险

- 面向高考志愿场景时，必须避免“劝退式结论”。
- 应优先解释“哪些岗位受影响、该专业如何调整能力结构”。
- 结论要区分“替代风险”和“AI 工具价值”。很多专业不是更差，而是工作方式改变。

## 推荐落地顺序

最务实的顺序：

1. 先从 `data/processed/rysxai/` 生成 `major_job_candidates.csv`。
2. 对高频岗位做归一和人工抽检。
3. 引入中国职业分类大典映射。
4. 为前 100 个职业族构建任务和评分。
5. 生成第一版 `major_ai_profiles.csv`。
6. 抽样 60 个专业人工审查。
7. 再接入 `major_ai_substitutability` function call。

不要一开始就追求全自动和全覆盖。第一版最重要的是：

- 数据口径清楚。
- 证据能追溯。
- 分数能解释。
- 低置信度会提示。
- 中国本地阻力不会被忽略。

## 与现有系统的关系

已有工具和表可以复用：

- `major_lookup`: 专业解析。
- `major_market_reference`: 现有 rysxai 市场样本查询。
- `employment_summary`: 学校级就业摘要。
- `civil_service_mapping`: 考公映射线索。
- `source_trace_lookup`: 数据来源和可信度解释。
- `data_gap_detection`: 缺口检测。

新增能力不应替代这些工具，而是组合它们形成新画像：

```text
major_lookup
  -> major_market_reference
  -> ai_major_job_candidates
  -> ai_job_occupation_mapping
  -> ai_occupation_tasks
  -> ai_task_substitutability_scores
  -> ai_major_substitutability_profiles
  -> major_ai_substitutability
```

## 后续可扩展方向

1. 按省份修正岗位市场，例如长三角、珠三角、京津冀、成渝。
2. 按学校层次修正，例如双一流、行业强校、地方本科、高职。
3. 按学历层次区分本科、专科、硕士。
4. 引入时间序列，观察岗位需求和 AI 风险变化。
5. 建立“专业能力升级建议”，从风险判断升级为报考和学习建议。
6. 把“AI 替代风险”拆成学生可行动的能力清单，例如：
   - 更应该学什么工具。
   - 哪些岗位方向更稳。
   - 哪些低阶任务会快速贬值。
   - 哪些证书或实践能提高抗替代性。
