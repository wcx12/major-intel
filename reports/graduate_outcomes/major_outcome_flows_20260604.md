# Graduate Outcome Major Flow Risk-Link Report

- Public row-level input records: 285608
- Rows with undergraduate major: 3494
- Rows with admission major: 253584
- Major flow rows: 4534
- Employment-warning linked major flows: 143
- Red/yellow linked major flows: 85
- Official-policy linked major flows: 424
- AI replacement-risk linked major flows: 493

## Role Summary

| Role | Majors | Records | Red/yellow linked | Policy linked | AI linked | Avg AI score |
|---|---:|---:|---:|---:|---:|---:|
| admission_major | 4124 | 253584 | 41 | 202 | 249 | 45.65 |
| undergraduate_major | 410 | 3494 | 44 | 222 | 244 | 45.75 |

## Outputs

- Major flows: `data\processed\graduate_outcomes\major_outcome_flow_summary_20260604.csv`
- Role summary: `data\processed\graduate_outcomes\major_outcome_flow_role_summary_20260604.csv`
- Manifest: `data\processed\graduate_outcomes\major_outcome_flows_manifest_20260604.json`

## Use Notes

- `undergraduate_major` means the source student's undergraduate major when the official row exposes it.
- `admission_major` means the destination admitted/recommended postgraduate major or programme name.
- Counts are public, masked official-source row counts; they are not employment rates and must not be used as per-major employment-quality conclusions.
