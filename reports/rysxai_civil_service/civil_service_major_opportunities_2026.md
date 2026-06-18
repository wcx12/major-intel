# RYSXAI Civil-Service Major Opportunity Report

- Input role rows: 20714
- Parsed roles with at least one major match: 20550
- Role-major match rows: 888025
- Major opportunity rows: 1653
- Majors with at least one role match: 1110
- Employment-warning linked majors: 146
- Red/yellow linked majors: 83
- Official-policy linked majors: 560
- AI replacement-risk linked majors: 1613

## Top Majors By Matched Role Count

| Major | Level | Roles | Plans | Weighted ratio | Match level |
|---|---|---:|---:|---:|---|
| 会计学 | 本科 | 7445 | 15538 | 82.11 | very_high |
| 审计学 | 本科 | 7368 | 15460 | 81.66 | very_high |
| 财务管理 | 本科 | 7344 | 15397 | 81.91 | very_high |
| 财政学 | 本科 | 6730 | 14242 | 77.36 | very_high |
| 税收学 | 本科 | 6685 | 14176 | 77.04 | very_high |
| 国际税收 | 本科 | 6639 | 14093 | 77.15 | very_high |
| 资产评估 | 本科 | 6541 | 14285 | 79.74 | very_high |
| 财务会计教育 | 本科 | 6508 | 14216 | 79.91 | very_high |
| 经济学 | 本科 | 6326 | 12980 | 76.89 | very_high |
| 经济统计学 | 本科 | 6000 | 12126 | 77.57 | very_high |
| 数字经济 | 本科 | 5972 | 12094 | 77.49 | very_high |
| 国民经济管理 | 本科 | 5952 | 12065 | 77.58 | very_high |
| 资源与环境经济学 | 本科 | 5943 | 12055 | 77.53 | very_high |
| 经济工程 | 本科 | 5943 | 12053 | 77.57 | very_high |
| 商务经济学 | 本科 | 5942 | 12052 | 77.5 | very_high |
| 能源经济 | 本科 | 5942 | 12052 | 77.51 | very_high |
| 劳动经济学 | 本科 | 5942 | 12052 | 77.49 | very_high |
| 低空经济与管理 | 本科 | 5941 | 12051 | 77.49 | very_high |
| 资源环境审计 | 本科 | 5941 | 12051 | 77.49 | very_high |
| 金融工程 | 本科 | 5165 | 10908 | 71.93 | very_high |

## Outputs

- Major opportunities: `data\processed\rysxai_civil_service\civil_service_major_opportunities_2026.csv`
- Role parse summary: `data\processed\rysxai_civil_service\civil_service_role_match_summary_2026.csv`
- Role-major matches: `data\processed\rysxai_civil_service\civil_service_role_major_matches_2026.csv`
- Unmatched terms: `data\processed\rysxai_civil_service\civil_service_unmatched_profession_terms_2026.csv`
- Manifest: `data\processed\rysxai_civil_service\civil_service_major_opportunities_manifest_2026.json`

## Use Notes

- Source level is `C`: this is a third-party API mirror of civil-service role data.
- Exact matches come from six-digit major codes or exact major names.
- Broad matches come from discipline/category codes, major-class terms, and documented aliases.
- A matched role is evidence of a textual eligibility clue, not a final application eligibility judgment.
