# Major Intel 当前状态快照

更新时间：2026-05-20

## 已完成的主干能力

### 1. 本地检索与 function call 层

当前已落地 14 个正式可调用检索入口：

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
admission_history
major_market_reference
civil_service_role_search
data_gap_detection
```

配套能力：

- `scripts/retrieval_tools.py`：标准工具层。
- `scripts/retrieval_function_registry.py`：function schema 注册与 dispatcher。
- `scripts/run_retrieval_smoke_cases.py`：本地 smoke case runner。
- `scripts/local_retrieval_mvp.py`：面向本地 MySQL 的 CLI MVP。
- `scripts/setup_entity_aliases.py`：创建和维护 `entity_aliases`、`entity_alias_candidates`。

已经完成的关键修复和增强：

- 修复 MySQL CLI TSV 解析：长文本字段中的换行不再被拆成假结果行。
- 修复录取历史表与学校表的关联键：`edu_school_admission_stats.school_id` 应按 `edu_university.code + name` 关联，不能按内部 `edu_university.school_id` 关联。
- `major_lookup` 的常用简称已经从代码内置迁入数据库确认别名表 `entity_aliases`，例如“计科”优先命中“计算机科学与技术”；短简称不再直接走危险模糊匹配。
- `rank_to_school_match` 已能按分数或位次返回学校层面的冲/稳/保参考。
- `rank_to_major_match` 已能按分数或位次 + 专业偏好返回学校-专业行层面的冲/稳/保参考。

### 1.1 工具完成状态

正式已完成：

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
admission_history
data_gap_detection
```

提前完成：

```text
major_market_reference
civil_service_role_search
```

部分完成，但还不是正式结论型工具：

```text
transfer_policy_lookup
civil_service_mapping
```

仍待制作：

```text
specialty_group_lookup
plan_history
subject_requirement_lookup
school_department_major_list
specialty_group_risk
comparison_query
employment_summary
source_trace_lookup
major_streaming_policy_lookup
fee_and_campus_lookup
policy_rule_lookup
```

当前验证：

- 单元测试：`python -m unittest discover -s tests` 最近一次为 79 个测试通过。
- 烟测矩阵：覆盖 14 个工具入口。
- 真实库抽样：`major_lookup`、`rank_to_school_match`、`rank_to_major_match` 已验证过可跑通。

### 2. rysxai 专业市场数据

已完成：

- 专业列表 seed：`data/seeds/rysxai_professions.full.csv`。
- 市场样本 crawler：`scripts/rysxai_market_crawler.py`。
- Markdown 报告渲染：`scripts/rysxai_market_report.py`。
- 市场概览与 dashboard 构建：`scripts/build_rysxai_overview.py`、`scripts/build_rysxai_dashboards.py`。
- 单元测试：`tests/test_rysxai_market_crawler.py`、`tests/test_rysxai_market_report.py`。

边界：

- 该数据是第三方专业市场观察，只能用于专业通用就业方向、招聘样本、城市/行业/薪资观察。
- 不能直接回答某校某专业真实就业去向、真实薪资或官方就业质量。

### 3. rysxai 公考岗位数据

已完成：

- 2026 公考岗位详情 crawler：`scripts/rysxai_civil_service_crawler.py`。
- JSONL 到 CSV 展平能力。
- 本地检索工具 `civil_service_role_search` 已能读取已接入样本。
- 单元测试：`tests/test_rysxai_civil_service_crawler.py`。

边界：

- 当前只能说明岗位文本命中过某些专业样本。
- 不能声明某专业一定可报某岗位；最终可报范围仍要以当年官方岗位表和招录公告为准。

### 4. rysxai 转专业政策数据

本轮新增：

- 学校列表 seed：`data/seeds/rysxai_universities.csv`。
- 转专业政策 crawler：`scripts/rysxai_transfer_policy_crawler.py`。
- 转专业政策静态 dashboard：`scripts/build_rysxai_transfer_policy_dashboard.py`。
- 单元测试：`tests/test_rysxai_transfer_policy_crawler.py`、`tests/test_rysxai_transfer_policy_dashboard.py`。

边界：

- rysxai 转专业文本按 C 级第三方线索处理。
- 高风险使用前必须回到学校官网、教务处通知或招生章程复核。
- 接口空白不等于学校无转专业政策，只能说明抓取时第三方接口未暴露相关字段。

## 当前未纳入版本历史的本地产物

以下内容保留在本地，但默认忽略，不提交：

- `data/raw/`、`data/processed/`、`data/logs/`
- `reports/rysxai/`
- `reports/retrieval_smoke*.json`
- `gaokao_test_*.sql`
- `gaokao-zhiyuan-projects/`
- `docs/superpowers/`

当前工作区还存在未提交的实验性文件，暂未纳入主干状态：

- `.env.example`
- `scripts/deepseek_retrieval_agent.py`
- `tests/test_deepseek_retrieval_agent.py`

## 下一步建议

1. 先实现 `specialty_group_lookup`：查询专业组、组内专业、选科要求、计划数和调剂口径。
2. 再实现 `subject_requirement_lookup`：把选科要求从专业组/招生计划中抽成独立工具。
3. 再实现 `specialty_group_risk`：基于组内专业构成做调剂风险初筛，但不声称真实分流比例。
4. 然后实现 `transfer_policy_lookup`：把已入库的 rysxai 转专业线索接入正式检索工具，并明确第三方线索口径。
5. 最后审查未提交的 DeepSeek agent 草稿，再决定是否纳入主干自然语言总入口。
