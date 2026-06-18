# RYSXAI Transfer Policy Profile Report

- Input schools: 2948
- School profiles: 2948
- Faculty profiles: 2386
- Major mention rows: 1653
- Mentioned majors: 815
- Mentioned red/yellow majors: 76
- Mentioned official-policy risk majors: 468
- Mentioned AI replacement-risk majors: 805

## Highest Heuristic Difficulty Schools

| School | Province | Score | Level | Faculty policies | Mentioned majors |
|---|---|---:|---|---:|---:|
| 上海大学 | 上海 | 100 | very_restrictive | 23 | 55 |
| 东北农业大学 | 黑龙江 | 100 | very_restrictive | 16 | 87 |
| 东北大学 | 辽宁 | 100 | very_restrictive | 16 | 64 |
| 东北林业大学 | 黑龙江 | 100 | very_restrictive | 16 | 71 |
| 中国人民大学 | 北京 | 100 | very_restrictive | 28 | 72 |
| 中国传媒大学 | 北京 | 100 | very_restrictive | 17 | 61 |
| 中国农业大学 | 北京 | 100 | very_restrictive | 19 | 33 |
| 中国地质大学（武汉） | 湖北 | 100 | very_restrictive | 22 | 50 |
| 中央财经大学 | 北京 | 100 | very_restrictive | 16 | 57 |
| 中山大学 | 广东 | 100 | very_restrictive | 63 | 74 |
| 云南大学 | 云南 | 100 | very_restrictive | 27 | 45 |
| 兰州大学 | 甘肃 | 100 | very_restrictive | 33 | 67 |
| 内蒙古大学 | 内蒙古 | 100 | very_restrictive | 18 | 52 |
| 北京工业大学 | 北京 | 100 | very_restrictive | 16 | 62 |
| 北京师范大学 | 北京 | 100 | very_restrictive | 22 | 43 |
| 华中农业大学 | 湖北 | 100 | very_restrictive | 15 | 49 |
| 华中师范大学 | 湖北 | 100 | very_restrictive | 17 | 23 |
| 华中科技大学 | 湖北 | 100 | very_restrictive | 40 | 118 |
| 华南师范大学 | 广东 | 100 | very_restrictive | 31 | 85 |
| 华南理工大学 | 广东 | 100 | very_restrictive | 34 | 104 |

## Most Mentioned Majors

| Major | Level | Schools | Faculty rows | Red/yellow | AI risk |
|---|---|---:|---:|---|---|
| 化学 | 本科 | 953 | 408 | true | 较低 |
| 护理 | 专科 | 376 | 88 | true | 较低 |
| 数字经济 | 本科 | 249 | 18 | false | 中等 |
| 药学 | 本科 | 247 | 53 | false | 较低 |
| 药学 | 专科 | 247 | 53 | false | 较低 |
| 学前教育 | 本科 | 246 | 5 | true | 较低 |
| 学前教育 | 专科 | 246 | 5 | true | 较低 |
| 法学 | 本科 | 207 | 203 | true | 较低 |
| 经济学 | 本科 | 198 | 148 | false | 中等 |
| 教育学 | 本科 | 198 | 132 | false | 较低 |
| 英语 | 本科 | 193 | 686 | true | 较低 |
| 艺术设计 | 专科 | 189 | 10 | false | 中等 |
| 临床医学 | 本科 | 175 | 136 | true | 较低 |
| 临床医学 | 专科 | 175 | 136 | true | 较低 |
| 人工智能 | 本科 | 174 | 107 | false | 较低 |
| 电子商务 | 本科 | 155 | 17 | true | 较低 |
| 电子商务 | 专科 | 155 | 17 | true | 较低 |
| 自动化 | 本科 | 143 | 150 | false | 较低 |
| 旅游管理 | 本科 | 141 | 16 | true | 较低 |
| 旅游管理 | 专科 | 141 | 16 | true | 较低 |

## Outputs

- School profiles: `data\processed\rysxai_transfer_policies\transfer_policy_school_profiles_2026.csv`
- Faculty profiles: `data\processed\rysxai_transfer_policies\transfer_policy_faculty_profiles_2026.csv`
- Major mentions: `data\processed\rysxai_transfer_policies\transfer_policy_major_mentions_2026.csv`
- Summary: `data\processed\rysxai_transfer_policies\transfer_policy_profile_summary_2026.csv`
- Manifest: `data\processed\rysxai_transfer_policies\transfer_policy_profiles_manifest_2026.json`

## Use Notes

- Source level is `C`: this is third-party compiled policy text.
- Difficulty score is a transparent heuristic from policy length and keyword flags.
- Major mentions are text matches, not official school-major eligibility records.
