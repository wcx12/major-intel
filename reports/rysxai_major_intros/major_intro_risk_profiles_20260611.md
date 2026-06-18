# Rysxai Major Introduction Risk-Link Report

- Source level: C
- Input profile rows: 1653
- Output profile rows: 1653
- Duplicate profile IDs: 0
- Employment-warning linked profiles: 147
- Red/yellow linked profiles: 84
- Official-policy linked profiles: 564
- AI replacement-risk linked profiles: 1613

## Level Summary

| Level | Profiles | Red/yellow linked | Policy linked | AI linked | Avg AI score |
|---|---:|---:|---:|---:|---:|
| 专科 | 771 | 38 | 101 | 768 | 43.57 |
| 本科 | 882 | 46 | 463 | 845 | 46.09 |

## Outputs

- Profiles: `data\processed\rysxai_major_intros\major_intro_risk_profiles_20260611.csv`
- Summary: `data\processed\rysxai_major_intros\major_intro_risk_profile_summary_20260611.csv`
- Manifest: `data\processed\rysxai_major_intros\major_intro_risk_profiles_manifest_20260611.json`

## Use Notes

- This is a source-level C support dataset. It is suitable for retrieval, feature extraction, and review sampling.
- It must not be interpreted as an official employment warning, official professional-setting decision, or deterministic AI-risk prediction.
- Risk linkage is exact by major code/name where available and keeps matched source IDs for audit.
