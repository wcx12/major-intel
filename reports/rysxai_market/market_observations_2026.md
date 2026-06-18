# RYSXAI Major Market Observation Report

- Source level: C
- Snapshot files: 1616
- Major market profiles: 1616
- Job sample rows: 6814
- City salary rows: 6459
- Distribution rows: 39659
- Ranking rows: 33414
- Skill summary rows: 28492
- Red/yellow employment-warning linked profiles: 84
- Official-policy linked profiles: 564
- AI medium-or-high linked profiles: 238

## Top Demand Signals

| Major | Level | Demand | Salary ref | Job samples | High-risk | AI risk |
|---|---|---:|---:|---:|---|---|
| 服务科学与工程 | 本科 | 2073828 | 7358 | 5 | false | 较低 |
| 工程软件 | 本科 | 1956418 | 6926 | 0 | false | 较低 |
| 数据科学 | 本科 | 1365652 | 7918 | 5 | false | 较低 |
| 资源环境科学 | 本科 | 1257541 | 8638 | 5 | false | 较低 |
| 资源化学 | 本科 | 1116762 | 8440 | 0 | false | 较低 |
| 资源环境大数据工程 | 本科 | 1004852 | 8651 | 0 | false | 中等 |
| 计算金融 | 本科 | 921367 | 8646 | 5 | false | 较低 |
| 职业卫生工程 | 本科 | 879080 | 7515 | 5 | false | 较低 |
| 旅游管理 | 本科 | 869839 | 7127 | 5 | true | 较低 |
| 旅游管理与服务教育 | 本科 | 869839 | 7127 | 5 | false | 较低 |
| 环境科学与工程 | 本科 | 812729 | 7250 | 5 | false | 较低 |
| 环境科学 | 本科 | 812729 | 7250 | 5 | false | 较低 |
| 国际商务 | 本科 | 684096 | 7668 | 5 | false | 较低 |
| 信息与计算科学 | 本科 | 639567 | 8328 | 5 | true | 较低 |
| 数据计算及应用 | 本科 | 639567 | 8328 | 5 | false | 中等 |
| 新媒体技术 | 本科 | 634881 | 7726 | 5 | false | 中等 |
| 新媒体艺术 | 本科 | 634881 | 7726 | 5 | false | 中等 |
| 工业软件 | 本科 | 628255 | 7578 | 5 | false | 较低 |
| 社会政策 | 本科 | 612855 | 8068 | 5 | false | 较低 |
| 旅游英语 | 专科 | 604582 | 6558 | 5 | false | 较低 |

## Top Salary Reference Signals

| Major | Level | Salary ref | Demand | Job samples | High-risk | AI risk |
|---|---|---:|---:|---:|---|---|
| 萨摩亚语 | 本科 | 20000 | 1 | 0 | false | 中等 |
| 装甲车辆工程 | 本科 | 18777 | 3 | 5 | false | 较低 |
| 生态农业技术 | 专科 | 18518 | 1296 | 0 | false | 较低 |
| 林业技术 | 专科 | 18294 | 827 | 0 | false | 较低 |
| 卢森堡语 | 本科 | 14800 | 5 | 0 | false | 较低 |
| 格鲁吉亚语 | 本科 | 14785 | 7 | 5 | false | 中等 |
| 移民管理 | 本科 | 14047 | 2820 | 5 | false | 较低 |
| 爱尔兰语 | 本科 | 13749 | 12 | 1 | false | 中等 |
| 水生态修复技术 | 专科 | 13742 | 2792 | 5 | false | 较低 |
| 投资学 | 本科 | 13437 | 19096 | 5 | true | 较低 |
| 茨瓦纳语 | 本科 | 13299 | 162 | 0 | false | 较低 |
| 生态修复学 | 本科 | 13058 | 7653 | 5 | false | 较低 |
| 土地科学与技术 | 本科 | 12626 | 15734 | 5 | false | 较低 |
| 土地整治工程 | 本科 | 12485 | 12067 | 5 | false | 较低 |
| 电磁场与无线技术 | 本科 | 12355 | 2990 | 5 | false | 较低 |
| 水声工程 | 本科 | 11990 | 219 | 5 | false | 较低 |
| 核化工与核燃料工程 | 本科 | 11938 | 639 | 5 | false | 较低 |
| 人工智能教育 | 本科 | 11825 | 17926 | 5 | false | 较低 |
| 人工智能 | 本科 | 11825 | 17926 | 5 | false | 较低 |
| 仿生科学与工程 | 本科 | 11753 | 138 | 5 | false | 较低 |

## Outputs

- Profiles: `data\processed\rysxai_market\market_major_profiles_2026.csv`
- Job samples: `data\processed\rysxai_market\market_job_samples_2026.csv`
- City salary: `data\processed\rysxai_market\market_city_salary_2026.csv`
- Distributions: `data\processed\rysxai_market\market_macro_distributions_2026.csv`
- Rankings: `data\processed\rysxai_market\market_rankings_2026.csv`
- Skills: `data\processed\rysxai_market\market_skill_summary_2026.csv`
- Summary: `data\processed\rysxai_market\market_profile_summary_2026.csv`
- Manifest: `data\processed\rysxai_market\market_observations_manifest_2026.json`

## Use Notes

- Source level is `C`: this is third-party market observation data, not official graduate outcome evidence.
- Recruiting samples are retained with job/company fields but without recruiter personal fields.
- Salary and demand fields are suitable for screening and retrieval features, not deterministic employment forecasts.
