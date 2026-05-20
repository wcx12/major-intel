# Major Intel 当前状态快照

更新时间：2026-05-20

## 已完成的主干能力

### 1. 本地检索与 function call 层

当前已落地 13 个可调用检索入口：

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

本轮新增整理点：

- 修复 MySQL CLI TSV 解析：长文本字段中的换行不再被拆成假结果行。
- `major_lookup` 已加入第一版内置常用简称保护，例如“计科”优先命中“计算机科学与技术”；完整别名表、候选沉淀和人工确认流程仍待落地。

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

## 下一步建议

1. 将 `major_lookup` 的内置简称升级为正式专业别名表，继续避免短词 `LIKE` 误命中。
2. 把转专业政策数据接入正式检索表，并实现 `transfer_policy_lookup`。
3. 增加 `source_trace_lookup`，让每个回答能解释来源表、字段和可信等级。
4. 把 smoke case 输出沉淀为可读汇总，而不是提交临时 JSON 运行结果。
