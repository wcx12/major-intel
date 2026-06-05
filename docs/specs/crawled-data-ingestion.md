# Major Intel 爬取数据接入方案

## 阅读说明

这份文档定义如何把已经爬取到的 rysxai 就业市场数据、考公岗位数据接入本地 MySQL。它的目标不是重新爬取数据，而是把散落在 JSON、JSONL、CSV 文件里的数据规范化为后续 function call 可以稳定查询的表。

需要特别注意：这些爬取数据的价值很高，但它们的证据口径和学校官方数据不同。接入时必须保留来源、抓取时间、数据范围和风险提示，避免后续 agent 把“市场观察样本”误说成“某校某专业真实就业结果”。

## 当前已有数据

| 数据类型 | 本地位置 | 当前用途 | 证据等级 |
|---|---|---|---|
| 专业市场快照 | `data/processed/rysxai/profession_*_market_snapshot.json` | 专业通用就业方向、城市/行业分布、招聘岗位样本、薪资观察 | B |
| 专业市场原始响应 | `data/raw/rysxai/*/profession_*_info.raw.json`、`profession_*_positions.raw.json` | 追溯 rysxai 接口原始返回 | B |
| 考公岗位 JSONL | `data/raw/rysxai_civil_service_2026.jsonl` | 岗位详情、专业要求文本、部门、地点、报录比 | B/C |
| 考公岗位 CSV | `data/processed/rysxai_civil_service_2026.csv` | 岗位详情扁平化文件 | B/C |
| 转专业政策探索数据 | `data/raw/rysxai_transfer_policies.jsonl` | 暂不纳入本轮，后续单独审查 | C |

## 接入后的回答边界

### 就业市场数据能回答

- 某专业通用就业方向。
- 某专业招聘市场常见岗位。
- 某专业招聘样本中的城市、行业、薪资区间。
- 某专业市场热度和需求观察。

### 就业市场数据不能直接回答

- 某学校某专业毕业生真实去了哪些公司。
- 某学校某专业真实薪资分布。
- 某学校某专业就业地域分布。
- 某学校某专业官方就业质量。

这些问题需要学校就业质量报告、学院毕业去向或官方来源。

### 考公岗位数据能回答

- 某专业或专业代码在岗位专业要求文本中出现过哪些岗位样本。
- 岗位所属部门、职位名称、工作地点、学历要求、专业要求文本。
- 某专业方向可关注哪些岗位类别。

### 考公岗位数据不能直接回答

- 某专业一定能报某岗位。
- 某专业完整可报岗位清单。
- 某岗位专业要求的官方最终解释。

这些结论需要把岗位专业要求文本映射到教育部专业代码，并保留招录公告来源。

## 建议新增表

### 1. `rysxai_major_market_snapshots`

保存每个 rysxai 专业的一份市场观察快照。

| 字段 | 类型 | 说明 |
|---|---|---|
| `profession_id` | bigint primary key | rysxai 专业 ID |
| `major_code` | varchar(32) | 专业代码 |
| `major_name` | varchar(200) | 专业名称 |
| `major_level` | varchar(50) | 本科/专科 |
| `degree` | varchar(100) | 学位 |
| `limit_year` | varchar(50) | 学制 |
| `captured_at` | varchar(50) | 抓取时间 |
| `source_name` | varchar(50) | 数据来源，例如 rysxai |
| `source_level` | varchar(10) | 证据等级，当前为 C/B 之间的市场观察 |
| `data_scope` | varchar(100) | 数据口径，例如 `major_level_market_observation` |
| `info_url` | varchar(500) | 专业信息接口 URL |
| `positions_url` | varchar(500) | 招聘样本接口 URL |
| `macro_employment_json` | json | 行业、地区、岗位方向分布 |
| `demand_ranking_json` | json | 需求排行 |
| `salary_ranking_json` | json | 薪资排行 |
| `salary_observations_by_city_json` | json | 招聘样本城市薪资聚合 |
| `salary_observations_by_industry_json` | json | 招聘样本行业薪资聚合 |
| `job_posting_sample_total_reported` | int | 接口声称样本量 |
| `job_posting_sample_count` | int | 实际保存样本量 |
| `warnings_json` | json | 风险提示 |
| `raw_snapshot_json` | json | 原始规范化快照 |

### 2. `rysxai_major_job_samples`

保存专业下的招聘岗位样本。它是市场观察样本，不是毕业生去向。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | bigint auto_increment primary key | 内部 ID |
| `profession_id` | bigint | rysxai 专业 ID |
| `source_item_id` | varchar(64) | rysxai 岗位样本 ID |
| `major_code` | varchar(32) | 专业代码 |
| `major_name` | varchar(200) | 专业名称 |
| `job_title` | varchar(255) | 岗位名称 |
| `company_name` | varchar(255) | 公司名称 |
| `city` | varchar(100) | 城市 |
| `district` | varchar(100) | 区县 |
| `industry` | varchar(255) | 行业 |
| `salary_raw` | varchar(100) | 原始薪资文本 |
| `monthly_salary_min` | int | 月薪下限 |
| `monthly_salary_max` | int | 月薪上限 |
| `education` | varchar(100) | 学历要求 |
| `experience` | varchar(100) | 经验要求 |
| `skills_json` | json | 技能标签 |
| `company_tags_json` | json | 公司标签 |
| `company_scale` | varchar(100) | 公司规模 |
| `financing_stage` | varchar(100) | 融资阶段 |
| `source_level` | varchar(10) | 来源等级 |
| `data_scope` | varchar(100) | 数据口径 |
| `captured_at` | varchar(50) | 快照抓取时间 |

### 3. `rysxai_civil_service_roles`

保存考公岗位详情。

| 字段 | 类型 | 说明 |
|---|---|---|
| `role_id` | bigint primary key | rysxai 岗位 ID |
| `year` | int | 招录年份 |
| `sheet_type` | varchar(255) | 表类型 |
| `department_code` | varchar(64) | 部门代码 |
| `department_name` | varchar(255) | 部门名称 |
| `sub_department` | varchar(255) | 用人司局 |
| `job_name` | varchar(255) | 职位名称 |
| `position_code` | varchar(64) | 职位代码 |
| `exam_type` | varchar(100) | 考试类别 |
| `plan_num` | int | 招录人数 |
| `apply_num` | int | 报名人数 |
| `ratio` | decimal(10,2) | 报录比 |
| `profession_text` | text | 原始专业要求文本 |
| `education_level` | varchar(100) | 学历要求 |
| `degree_requirement` | varchar(100) | 学位要求 |
| `work_location` | varchar(100) | 工作地点 |
| `province` | varchar(100) | 省份 |
| `remark` | text | 备注 |
| `source_url` | varchar(500) | 来源 URL |
| `fetched_at` | varchar(50) | 抓取时间 |
| `raw_role_json` | json | 原始岗位详情 |

### 4. `civil_service_major_role_candidates`

保存从考公岗位专业要求文本里抽取出的专业代码候选或待解析文本。它不是最终可报结论，而是后续映射和人工审核的候选层。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | bigint auto_increment primary key | 内部 ID |
| `role_id` | bigint | 岗位 ID |
| `candidate_type` | varchar(50) | `major_code`、`major_category_code`、`raw_profession_text` |
| `major_code` | varchar(32) | 抽取出的专业代码 |
| `major_name` | varchar(200) | 专业名称候选 |
| `profession_text` | text | 原始专业要求文本 |
| `match_status` | varchar(50) | `candidate`、`matched`、`rejected` |
| `evidence_text` | text | 抽取证据 |

## 第一版入库策略

第一版先做到“可重复、可覆盖、可回滚思路清楚”。

1. 使用 `CREATE TABLE IF NOT EXISTS` 建表，不破坏原始业务表。
2. 使用 `INSERT ... ON DUPLICATE KEY UPDATE`，支持重复执行。
3. 市场快照以 `profession_id` 作为主键覆盖更新。
4. 岗位样本以 `profession_id + source_item_id` 去重。
5. 考公岗位以 `role_id` 作为主键覆盖更新。
6. 考公专业候选可按 `role_id + candidate_type + major_code` 去重；没有专业代码时保留一条 raw 文本候选。
7. 所有入库脚本只从环境变量读取数据库密码，不写入代码和文档。

## 第一版脚本建议

新增脚本：

```text
scripts/ingest_rysxai_data.py
```

真实实现位于 `src/major_intel/ingestion/rysxai_data.py`。`scripts/ingest_rysxai_data.py` 是兼容 CLI wrapper；新的结构化入口是 `scripts/ingestion/ingest_rysxai_data.py`。

建议支持命令：

```text
python scripts/ingest_rysxai_data.py init-schema
python scripts/ingest_rysxai_data.py ingest-market --processed-dir data/processed/rysxai
python scripts/ingest_rysxai_data.py ingest-civil --jsonl data/raw/rysxai_civil_service_2026.jsonl
python scripts/ingest_rysxai_data.py summarize
```

第一版测试重点：

- 市场快照能转成一条 snapshot 行和多条 job sample 行。
- 考公岗位 JSONL 能转成 role 行和专业候选行。
- SQL 建表语句包含必要主键和去重键。
- 空字段、缺字段、非数字薪资不会导致脚本崩溃。
- 入库 SQL 不包含数据库密码。

## 后续 function call 影响

接入后可以把这些 function call 能力前移：

| 工具 | 原阶段 | 接入后建议阶段 | 说明 |
|---|---|---|---|
| `major_market_reference` | 第三阶段 | 第二阶段 | 有规范化市场快照后即可查专业市场参考 |
| `civil_service_role_search` | 未单列 | 第二阶段 | 先做岗位样本检索，不做最终可报断言 |
| `civil_service_mapping` | 第四阶段 | 第三/四阶段 | 需要专业代码映射和人工审核后再提升等级 |
| `source_trace_lookup` | 第三阶段 | 第三阶段 | 入库时保留 source_url、source_level、data_scope 后更好做 |

## 回答口径模板

### 专业市场参考

```text
以下为第三方招聘市场样本和专业市场观察，不代表某学校某专业毕业生真实就业去向或薪资。
```

### 考公岗位样本

```text
以下为岗位专业要求文本命中的考公岗位样本，不等于该专业一定可报。最终可报范围应以当年官方招录公告和岗位表解释为准。
```

## 验收标准

第一版完成时应满足：

- MySQL 中存在四张新增 rysxai 接入表。
- 至少能入库已有市场快照文件。
- 至少能入库已有考公岗位 JSONL。
- 能统计入库专业数、岗位样本数、考公岗位数和专业候选数。
- 入库脚本可重复执行，不产生明显重复记录。
- 单元测试覆盖市场快照转换、考公岗位转换和 DDL 生成。
