# 检索工具问题拆分与更正待办

生成时间：2026-05-21

依据：

- 测试命令集：`docs/status/retrieval-tool-broad-test-command-dataset.md`
- 全量运行记录：`reports/retrieval_broad_dataset_run_20260521_163348.jsonl`
- 问题报告：`reports/retrieval_broad_dataset_issues_20260521_163348.md`

本文件只记录问题拆分和后续修改建议，不代表已经修改代码或数据。

## 总体结论

530 条广覆盖检索命令全部执行完成，运行层没有崩溃、超时或 JSON 解析失败。当前主要问题不是 CLI 不稳定，而是：

1. 部分工具状态语义不准确，存在“核心结果为空但返回 ok”的情况。
2. 学校-专业证据分散在多张表里，`school_major_profile` 只依赖部分证据，导致常见组合被误判为缺开设关系。
3. 专业组、选科、分流风险、政策规则、学费校区等志愿填报关键证据链缺口明显。
4. 测试集里正例、边界例和覆盖探测例混在一起，后续需要给每条用例标注预期状态。

## 问题来源工具索引

说明：

- “直接来源 tools”指这条问题最直接暴露或需要修改的 `scripts/retrieval_tools.py` CLI 子命令。
- “关联 tools / 脚本”指复现、交叉验证或后续可能受影响的工具、脚本、测试集。
- “主要实现入口”给出建议优先查看的函数或辅助 SQL 构造函数；在对应文件中搜索函数名即可定位实现。

| 问题编号 | 问题主题 | 直接来源 tools | 关联 tools / 脚本 | 主要实现入口 |
|---|---|---|---|---|
| 1 | 空核心结果却返回 `ok` | `school_major_list`、`major_school_list`、`admission_history`、`data_gap_detection` | `scripts/retrieval_tools.py` CLI；`tests/test_retrieval_tools.py` | `RetrievalTools.school_major_list`、`RetrievalTools.major_school_list`、`RetrievalTools.admission_history`、`RetrievalTools.data_gap_detection`；辅助函数：`_school_major_list_sql`、`_major_school_list_sql`、`_admission_history_sql` |
| 2 | `data_gap_detection` 未知问题类型 | `data_gap_detection` | 自然语言入口会调用缺口检测：`scripts/natural_language_entrypoint.py` | `RetrievalTools.data_gap_detection` |
| 3 | 学校-专业统一证据链 | `school_major_profile`、`school_department_major_list` | `admission_history`、`rank_to_major_match`、`plan_history`、`specialty_group_lookup`；真实库验证命令来自 `docs/status/retrieval-tool-broad-test-command-dataset.md` | `RetrievalTools.school_major_profile`、`RetrievalTools.school_department_major_list`；辅助函数：`_school_major_evidence_sqls`、`_school_major_evidence_summary`、`_school_department_major_list_sql`、`_admission_history_sql`、`_rank_to_major_match_sql`、`_plan_history_sql`、`_specialty_group_lookup_sql` |
| 4 | 改造 `school_major_profile` 输出结构和状态 | `school_major_profile` | `admission_history`、`plan_history`、`specialty_group_lookup`、`data_gap_detection` | `RetrievalTools.school_major_profile`；辅助函数：`_school_major_profile_status`、`_school_major_profile_warnings`、`_school_major_evidence_gaps`、`_raw_admission_major`、`_major_query_clause` |
| 5 | 核心测试集增加预期状态 | 不是单个 retrieval tool；覆盖全部工具 | `scripts/run_retrieval_smoke_cases.py`、`data/retrieval_smoke_cases.json`、`tests/test_retrieval_smoke_runner.py`、`docs/status/retrieval-tool-broad-test-command-dataset.md` | `load_cases`、`run_case`、`main`；用例字段：`id`、`category`、`expected_status`、`reason` |
| 6 | 专业组查询学校 ID 口径 | `specialty_group_lookup`、`subject_requirement_lookup`、`specialty_group_risk`、`major_streaming_policy_lookup` | `school_major_profile` 的证据链也会读取专业组证据 | `RetrievalTools.specialty_group_lookup`、`RetrievalTools.subject_requirement_lookup`、`RetrievalTools.specialty_group_risk`、`RetrievalTools.major_streaming_policy_lookup`；辅助函数：`_specialty_group_lookup_sql`、`_subject_requirement_lookup_sql`、`_specialty_group_sql` |
| 7 | 选科要求 fallback | `subject_requirement_lookup` | `admission_history`、`plan_history`、`school_major_profile` | `RetrievalTools.subject_requirement_lookup`；候选 fallback 来源实现可参考 `_admission_history_sql`、`_plan_history_sql`、`_school_major_evidence_sqls` |
| 8 | 专业组风险 fallback | `specialty_group_risk` | `specialty_group_lookup`、`admission_history`、`plan_history` | `RetrievalTools.specialty_group_risk`；辅助函数：`_specialty_group_risk_payload`、`_specialty_group_lookup_sql`、`_admission_history_sql`、`_plan_history_sql` |
| 9 | `edu_qjjh_plan.deleted=1` 语义审计 | `plan_history` | 数据审计 SQL；后续可能影响 `school_major_profile` 的计划证据 | `RetrievalTools.plan_history`、`_plan_history_sql`；证据链入口：`_school_major_evidence_sqls` |
| 10 | `plan_history` 增加备用数据源 | `plan_history` | `school_major_profile`、`fee_and_campus_lookup`、`admission_history` | `RetrievalTools.plan_history`、`_plan_history_sql`；备用来源可参考 `_school_major_evidence_sqls` 中的 `edu_university_plan_special`、`edu_school_admission_stats` 分支 |
| 11 | 学费/校区工具改造 | `fee_and_campus_lookup` | `plan_history`、`school_major_profile` | `RetrievalTools.fee_and_campus_lookup`、`_fee_and_campus_lookup_sql`；文本线索可复用计划表字段 `special_name`、`remark`、`tuition_fee` |
| 12 | 学校/专业别名补充 | `school_lookup`、`major_lookup` | 所有依赖实体解析的工具；别名导入脚本 `scripts/setup_entity_aliases.py` | `RetrievalTools.school_lookup`、`RetrievalTools.major_lookup`；底层解析函数在 `scripts/local_retrieval_mvp.py`：`resolve_school_sql`、`resolve_major_sql` |
| 13 | `policy_rule_lookup` 升级为证据工具 | `policy_rule_lookup` | `transfer_policy_lookup`、`fee_and_campus_lookup`、`source_trace_lookup` | `RetrievalTools.policy_rule_lookup`；后续新增政策表后需补 SQL helper |
| 14 | 考公映射证据等级 | `civil_service_mapping`、`civil_service_role_search` | `major_lookup`；数据表 `civil_service_major_role_candidates`、`rysxai_civil_service_roles` | `RetrievalTools.civil_service_mapping`、`RetrievalTools.civil_service_role_search`、`_civil_service_role_search_sql`、`_catalog_major_code_variants` |
| 15 | 科类口径提示 | `score_to_rank`、`rank_to_school_match`、`rank_to_major_match` | `admission_history` 也使用 `subject_type` 过滤 | `RetrievalTools.score_to_rank`、`RetrievalTools.rank_to_school_match`、`RetrievalTools.rank_to_major_match`；辅助函数：`_subject_type_candidates`、`_score_to_rank_sql`、`_rank_to_school_match_sql`、`_rank_to_major_match_sql` |
| 16 | 数据覆盖率报告 | 不是单个 retrieval tool；覆盖全部工具和数据表 | `source_trace_lookup`、`scripts/run_retrieval_smoke_cases.py`、`reports/retrieval_broad_dataset_run_20260521_163348.jsonl`、`reports/retrieval_broad_dataset_issues_20260521_163348.md` | `RetrievalTools.source_trace_lookup`、`_SOURCE_TRACE_REGISTRY`；报告生成可基于 smoke runner 输出和各工具 `source_tables` |

## P0 待办

### 1. 修正“空结果却返回 ok”的状态语义

状态：已完成（2026-05-21）

问题：

- `school_major_list` 在 `majors=[]` 时仍返回 `ok`。
- `major_school_list` 在 `schools=[]` 时仍返回 `ok`。
- `admission_history` 在 `records=[]` 时仍返回 `ok`。
- `data_gap_detection --question-type unknown_question_type` 返回 `ok` 且 `missing_items=[]`。

影响：

- 上层 agent 会把“查询成功但无数据”误解成“数据完整且无问题”。
- 测试报告会低估真实缺口。

建议修改：

- 核心列表为空时返回 `not_found`。
- 如果是缺少必要槽位，返回 `needs_clarification`。
- 如果是未知问题类型，返回 `needs_clarification`，并附带支持的问题类型列表。

验收标准：

- 空核心列表不再返回 `ok`。
- `unknown_question_type` 不再返回 `ok + missing_items=[]`。
- 对应测试用例能明确区分“查不到数据”和“查询成功”。

验收记录：

- 新增回归测试覆盖 `school_major_list`、`major_school_list`、`admission_history` 空核心列表。
- `python -m pytest tests/test_retrieval_tools.py`：39 passed。
- `python -m pytest tests`：137 passed。

补充验收记录（2026-06-02，`major_school_list` 专项）：

- 建立 `tests/function_calls/major_school_list/boundary_cases.json`、`test_boundary_cases_manifest.py`、`test_boundary_audit.py`。
- 建立 `scripts/evaluate_major_school_list_boundaries.py` 和独立 oracle `scripts/major_school_list_oracles.py`，真实库对照工具输出和 `code OR school_id` 双键召回结果。
- 修复 `major_school_list` 的学校关联键漏召回、省份后缀归一化、`major_lookup` warning 传播、`limit<=0` 参数校验。
- `python scripts/evaluate_major_school_list_boundaries.py --jsonl-report reports/major_school_list_boundary_eval_20260602.jsonl --markdown-report reports/major_school_list_boundary_eval_20260602.md`：16/16 通过。
- `python -m pytest tests\function_calls\major_school_list tests\test_retrieval_tools.py -q`：78 passed。

### 2. 修正 `data_gap_detection` 未知问题类型处理

状态：已完成（2026-05-21）

问题：

- 未知 `question_type` 当前返回空缺口，容易被理解为“不缺数据”。

建议修改：

- 为 `data_gap_detection` 增加支持类型校验。
- 未知类型返回：
  - `status = needs_clarification`
  - `needs_clarification = ["question_type"]`
  - `data.supported_question_types = [...]`

验收标准：

- `python scripts/retrieval_tools.py data_gap_detection --question-type unknown_question_type` 不再返回 `ok`。

验收记录：

- 目标命令返回 `status = needs_clarification`。
- `needs_clarification = ["question_type"]`。
- `data.supported_question_types` 返回 7 个已支持问题类型。
- `python -m pytest tests/test_retrieval_tools.py -k "data_gap_detection_rejects_unknown_question_type or data_gap_detection_lists_school_major_gaps"`：2 passed。

### 3. 建立学校-专业统一证据链

状态：已完成（2026-05-21）。

最新口径调整（2026-05-21）：

- `school_major_profile` 暂时禁用 `edu_school_major` 作为学校-专业证据来源。
- 当前目录类证据以 `edu_university_department` + `edu_university_department_major` 为准。
- `edu_school_major` 暂不参与 `school_major_profile` 的 `status`、`school_major_evidence`、`source_tables` 和 `evidence_gaps` 判断，避免主表脏数据把可疑组合误判为 `ok`。

问题：

- `edu_school_major` 缺少很多常见学校-专业关系。
- 例如“杭州电子科技大学-计算机科学与技术”：
  - `admission_history` 能查到 2025 浙江录取记录。
  - `rank_to_major_match` 能返回该组合。
  - 但 `school_major_profile` 因 `edu_school_major` 未命中而提示“不能直接认定已开设”。
- 复核后确认：`edu_university_department_major` 才是该类学校-专业目录的重要补充来源。
- 同时发现原 `school_department_major_list` 对院系表错误地同时使用 `school_id` 和 `code` 查询，导致杭电 `code=10336` 误命中 `school_id=10336` 的台州学院院系数据。

建议修改：

- 建立统一证据逻辑或视图，例如 `school_major_evidence`。
- 合并以下来源：
  - `edu_university_department`
  - `edu_university_department_major`
  - `edu_school_admission_stats`
  - `edu_qjjh_plan`
  - `edu_university_plan_config`
  - `edu_university_plan_special_group`
  - `edu_university_plan_special`
  - `edu_college_specialty_group`
  - `edu_specialty_group_major`
- 每条证据标注：
  - `source_type`: `catalog` / `admission_history` / `plan` / `specialty_group`
  - `source_table`
  - `year`
  - `province`
  - `subject_type`
  - `confidence`
- 按表区分学校键口径：
  - `edu_university_department` / `edu_university_department_major`：只使用 `edu_university.school_id`，不能用院校 `code` 混查。
  - `edu_college_specialty_group` / `edu_specialty_group_major`：只使用内部 `school_id`。
  - `edu_university_plan_config` / `edu_university_plan_special`：使用内部 `school_id`。
  - `edu_school_admission_stats`：录取统计里的 `school_id` 是院校代码口径，需结合 `school_name` 精确匹配。
  - `edu_school_major`：当前暂不用于 `school_major_profile` 证据链；后续需完成数据质量审计后再决定是否恢复。

验收标准：

- 高频组合如“杭电-计算机”能返回院系目录证据，并在有上下文时返回招生或录取证据。
- 工具能区分“院系目录证据”和“招生/录取证据”。

验收记录：

- `school_department_major_list --school "杭州电子科技大学" --major "计算机科学与技术"` 只返回杭电内部 `school_id=10124` 下的“杭州电子科技大学圣光机联合学院”和“计算机学院”，不再误返回台州学院“人工智能学院”。
- `school_major_profile --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025` 返回 `status=ok`。
- 上述画像结果的 `school_major_evidence` 返回 5 条证据：2 条 `edu_university_department_major` 院系专业目录证据，3 条 `edu_school_admission_stats` 2025 浙江综合录取历史证据。
- `evidence_summary.has_department_catalog=true`，`evidence_summary.has_admission_history=true`，`evidence_gaps=[]`。
- `school_major_profile --school "杭州电子科技大学" --major "护理学" --province "浙江" --subject-type "综合" --year 2025` 不再因 `edu_school_major` 主表脏数据返回 `ok`，当前返回 `partial`。
- 新增回归测试覆盖院系专业表只用内部 `school_id`、`school_major_profile` 使用院系专业目录证据、`school_major_profile` 不再查询 `edu_school_major`。
- `python -m pytest tests/test_retrieval_tools.py`：42 passed。

### 4. 改造 `school_major_profile`

状态：已完成第一版（2026-05-21）。

问题：

- 当前 `school_major_profile` 对学校-专业关系过度依赖 `edu_school_major`。
- 即使录取历史表有证据，也仍返回“未命中明确学校-专业开设关系”。

建议修改：

- 接入学校-专业统一证据链。
- 返回结构增加：
  - `school_major_evidence`
  - `evidence_summary`
  - `evidence_gaps`
- 如果只有录取或招生证据，状态可以是 `partial`，但说明应改为：
  - “有招生/录取证据”
  - “缺院系专业目录证据”

验收标准：

- “杭州电子科技大学-计算机科学与技术-浙江-综合-2025”不再只给负面提示。
- 输出能明确说明已有证据来自录取历史或招生计划。

验收记录：

- 已增加 `data.school_major_evidence`、`data.evidence_summary`、`data.evidence_gaps`。
- 当前不再使用 `edu_school_major`。若命中 `edu_university_department_major` 这类目录证据，`school_major_profile` 可返回 `ok`；若只有招生/录取/计划/专业组推断证据，仍保持 `partial` 口径。
- 当 `major_lookup` 未能映射到 `edu_major` 标准专业库时，`school_major_profile` 不再直接中断；会进入 `raw_admission_name` 模式，继续从招生计划、录取历史、专业组等表查原始招生名称证据。
- 带 `province` / `subject_type` / `year` 上下文时，如果只命中院系目录、没有命中招生/录取/计划/专业组证据，状态降为 `partial`，并提示“已命中院系专业目录证据，但未命中该省份/科类/年份招生或录取证据。”
- `python -m pytest tests/test_retrieval_tools.py`：44 passed。
- `python -m pytest tests`：142 passed。

### 5. 给核心测试集增加预期状态

问题：

- 当前测试集覆盖很广，但正例、边界例、缺口探测例混在一起。
- 后续无法快速判断 `not_found` 是预期边界，还是数据/逻辑问题。

建议修改：

- 将测试命令拆成三类：
  - `positive_core`: 应稳定返回 `ok` 或可接受的 `partial`
  - `boundary_expected`: 预期返回 `not_found` 或 `needs_clarification`
  - `coverage_probe`: 用于探测数据覆盖缺口
- 为每条命令增加：
  - `case_id`
  - `category`
  - `expected_status`
  - `reason`

验收标准：

- 后续运行报告能区分“预期失败”和“非预期失败”。

## P1 待办

### 6. 复核专业组查询的学校 ID 口径

问题：

- 早期判断认为专业组相关表里可能同时存在 `edu_university.school_id` 和 `edu_university.code` 两种学校标识口径。
- P0-3 复核时发现不能盲目同时兼容两种键：杭电 `code=10336` 会误命中 `edu_college_specialty_group.school_id=10336` 的台州学院专业组样本。
- 当前更安全的判断是：`edu_college_specialty_group` / `edu_specialty_group_major` 应优先按内部 `school_id` 查询；是否存在例外需要单独数据审计。

建议修改：

- `specialty_group_lookup`
- `subject_requirement_lookup`
- `specialty_group_risk`
- `major_streaming_policy_lookup`

这些工具不要直接改成 `school.school_id OR school.code`，应先抽样核对专业组表 `school_id` 的真实口径。

验收标准：

- 对已有专业组样本的学校，不因 ID 口径不同而漏查。
- 不因院校 `code` 与其他学校内部 `school_id` 重号而误查。

### 7. 给选科要求增加 fallback

问题：

- `subject_requirement_lookup` 依赖专业组样本。
- 当专业组表缺省份/年份样本时，直接 `not_found`。
- 但 `edu_school_admission_stats.subject_requirement` 里可能已有选科要求。

建议修改：

- 查询顺序：
  1. 专业组表。
  2. 录取历史表 `subject_requirement`。
  3. 招生计划表相关字段。
  4. 返回缺口。

验收标准：

- “杭电-计算机-浙江-综合-2025”即使专业组表缺浙江样本，也能返回录取历史中的 `物理,化学` 线索。

### 8. 给专业组风险增加 fallback

问题：

- 专业组风险工具在专业组表缺样本时只能 `not_found`。
- 但用户仍需要知道“缺什么”和“还能用哪些替代证据判断风险”。

建议修改：

- 专业组缺失时返回 `partial`，并附：
  - 录取历史中的专业名称、备注、选科要求。
  - 招生计划中的专业组或专业名称线索。
  - 明确 `data_gaps = ["专业组样本", "真实分流比例"]`。

验收标准：

- 没有专业组样本时，不直接结束为普通 `not_found`，而是给出可解释的风险缺口。

### 9. 检查 `edu_qjjh_plan.deleted=1` 的数据语义

问题：

- `plan_history` 大量 `not_found`。
- 抽查发现 `edu_qjjh_plan` 中部分记录存在，但 `deleted=1`，被工具过滤掉。

待确认：

- `deleted=1` 是否表示真正废弃？
- 是否是导入阶段误标？
- 是否存在全表或批次级误删标记？

建议修改：

- 先做数据审计，不直接改查询条件。
- 输出按学校、省份、年份统计：
  - `deleted=0` 数量
  - `deleted=1` 数量

验收标准：

- 明确 `deleted=1` 的业务含义。
- 决定是修数据，还是调整工具查询逻辑。

### 10. 给 `plan_history` 增加备用数据源

问题：

- `edu_qjjh_plan` 覆盖不足或被 `deleted` 标记影响。
- 其他表中仍可能有计划数，例如：
  - `edu_university_plan_special.plan_count`
  - `edu_school_admission_stats.plan_count`

建议修改：

- `plan_history` 主查 `edu_qjjh_plan`。
- 查不到时 fallback 到：
  1. `edu_university_plan_special`
  2. `edu_school_admission_stats.plan_count`
- 返回时标注来源和可靠性。

验收标准：

- 高频学校-专业组合能返回至少一类计划线索。

### 11. 改造学费/校区工具

问题：

- `fee_and_campus_lookup` 经常查不到。
- 即使命中，也固定返回 `campus_items=[]`。
- 但校区线索常存在于 `special_name` 或 `remark` 文本里。

建议修改：

- 从文本中抽取：
  - `下沙校区`
  - `粤海校区`
  - `校本部`
  - `主校区`
  - `中外合作办学`
  - `本科学术互认课程项目`
- 新增字段：
  - `campus_clues`
  - `fee_clues`
  - `cooperation_program_clues`
- 明确标注“文本线索，需官方复核”。

验收标准：

- 深圳大学计算机相关用例能返回学费和校区文本线索。
- 杭电计算机在浙江缺计划表时，能说明缺省份计划数据，而不是模糊 `not_found`。

### 12. 补充常见学校/专业别名

问题：

- 部分常见简称未命中：
  - `上交`
  - `成电`
  - `北工大`
  - `重邮`
  - `网安`
- `河大` 有歧义，不应强行绑定。

建议修改：

- 在 `entity_aliases` 中补明确别名：
  - `上交` -> `上海交通大学`
  - `成电` -> `电子科技大学`
  - `北工大` -> `北京工业大学`
  - `重邮` -> `重庆邮电大学`
  - `网安` -> `网络空间安全`
- 对歧义别名：
  - `河大` 返回候选或 `needs_clarification`。

验收标准：

- 明确简称能正常归一。
- 歧义简称不乱猜。

## P2 待办

### 13. 将 `policy_rule_lookup` 从缺口提示器升级为证据工具

问题：

- 当前 28 条政策规则测试全部 `partial`。
- 工具主要告诉用户缺什么，但不能返回官方政策证据。

建议修改：

- 新建或补充政策规则表，字段包括：
  - `school_id`
  - `school_name`
  - `year`
  - `province`
  - `policy_type`
  - `original_text`
  - `source_url`
  - `single_subject_limit`
  - `physical_exam_limit`
  - `language_limit`
  - `adjustment_rule`
  - `cooperation_program_rule`
  - `campus_rule`

验收标准：

- 查询招生章程、体检、语种、调剂、中外合作时，能返回官方来源和结构化摘要。

### 14. 考公映射增加证据等级

问题：

- `civil_service_mapping` 目前基本都是 `partial`。
- 它能提供岗位文本命中线索，但不能判断正式可报。

建议修改：

- 增加：
  - `official_role_table_source`
  - `manual_major_mapping`
  - `eligibility_rules`
  - `match_confidence`
- 区分：
  - 文本命中
  - 专业代码命中
  - 人工确认匹配
  - 正式可报仍需复核

验收标准：

- 输出不只说“命中岗位文本”，还能说明证据等级。

### 15. 优化科类口径提示

问题：

- 部分传统文理输入会映射到新高考 `物理/历史`。
- 当前有 warning，但后续回答层需要更明确地解释。

建议修改：

- 对 `理科 -> 物理`、`文科 -> 历史` 的情况输出更强提示。
- 标注：
  - “这是本地表口径兼容，不代表所有省份严格等价。”

验收标准：

- 传统文理省份查询结果不会被误解为严格新高考口径。

### 16. 生成数据覆盖率报告

问题：

- 当前只能从测试结果反推缺口。
- 缺少系统性覆盖率视图。

建议修改：

- 按以下维度统计覆盖率：
  - 省份
  - 年份
  - 学校
  - 专业
  - 工具
  - 数据表
- 重点统计：
  - 实体覆盖
  - 学校-专业关系覆盖
  - 招生计划覆盖
  - 录取历史覆盖
  - 专业组覆盖
  - 选科要求覆盖
  - 政策规则覆盖
  - 学费校区覆盖

验收标准：

- 能明确回答“哪些省份/学校/专业最缺数据”。

## 建议执行顺序

1. P0-1：修正空结果状态语义。
2. P0-2：修正未知 `question_type`。
3. P0-3：建立学校-专业统一证据链。
4. P0-4：改造 `school_major_profile`。
5. P0-5：给测试集加预期状态。
6. P1-6 到 P1-8：修专业组、选科、风险 fallback。
7. P1-9 到 P1-10：审计并修招生计划数据源。
8. P1-11：改造学费/校区文本线索。
9. P1-12：补别名和歧义处理。
10. P2-13 到 P2-16：补政策、考公、科类提示和覆盖率报告。

## 当前优先建议

建议先从 P0-1 开始。理由：

- 改动范围小。
- 最容易验证。
- 能立即提高测试报告可信度。
- 不修这个问题，后续所有统计都会继续混淆“查询成功”和“查无数据”。
