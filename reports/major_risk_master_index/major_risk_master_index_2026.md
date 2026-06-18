# Major Risk Master Index

- Built at: 2026-06-14
- Master index rows: 4028
- Source level mix: A/B/C
- High-risk review rows: 657
- Employment red/yellow linked rows: 174
- Official policy warning linked rows: 945
- AI high-signal rows: 45
- New-quality supported rows: 1133

## Review Buckets

| bucket | rows |
|---|---:|
| ai_market_risk_review | 34 |
| baseline_reference | 1172 |
| employment_or_policy_warning_review | 356 |
| high_risk_review | 657 |
| multi_signal_risk_review | 688 |
| opportunity_signal_reference | 422 |
| opportunity_watch | 167 |
| opportunity_with_risk_flags | 488 |
| single_signal_watch | 44 |

## Source Coverage

| source flag | majors | high-risk review | employment high-risk | official policy |
|---|---:|---:|---:|---:|
| ai_replacement | 1612 | 477 | 88 | 580 |
| civil_service | 1653 | 477 | 88 | 580 |
| emerging_major | 1163 | 334 | 46 | 501 |
| employment_warning | 141 | 89 | 81 | 92 |
| market_observation | 1616 | 477 | 88 | 580 |
| new_quality | 2053 | 521 | 110 | 650 |
| official_policy_warning | 643 | 431 | 64 | 643 |
| rysxai_seed | 1653 | 477 | 88 | 580 |
| vocational_register | 2010 | 151 | 93 | 184 |

## Sample High-Risk Rows

| major | code | level | bucket | risk reasons | opportunity reasons |
|---|---|---|---|---|---|
| 乌尔都语 | 050221 | 本科 | high_risk_review | official_policy_setting_warning|ai_replacement_high_signal|limited_market_signal|weak_civil_service_opportunity | official_emerging_major_signal |
| 世界语 | 050241 | 本科 | high_risk_review | official_policy_setting_warning|ai_replacement_high_signal|limited_market_signal|weak_civil_service_opportunity | strong_market_signal|official_emerging_major_signal |
| 翻译 | 050261 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | official_emerging_major_signal |
| 历史学 | 060101 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | official_emerging_major_signal |
| 中医学 | 100501 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | strong_market_signal |
| 音乐表演 | 130201 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | official_emerging_major_signal |
| 广播电视编导 | 130305 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | official_emerging_major_signal |
| 美术学 | 130401 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | strong_market_signal|official_emerging_major_signal |
| 绘画 | 130402 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | official_emerging_major_signal |
| 食品检验检测技术 | 490104 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | strong_market_signal |
| 中医学 | 520401 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity |  |
| 国际经济与贸易 | 530501 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | new_quality_policy_support |
| 旅游管理 | 540101 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | new_quality_policy_support|strong_market_signal |
| 导游 | 540102 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | new_quality_policy_support |
| 音乐表演 | 550201 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity |  |
| 出版策划与编辑 | 560103 | 专科 | high_risk_review | official_policy_setting_warning|ai_replacement_high_signal|limited_market_signal|weak_civil_service_opportunity | new_quality_policy_support |
| 数字出版 | 560105 | 专科 | high_risk_review | official_policy_setting_warning|ai_replacement_high_signal|limited_market_signal|weak_civil_service_opportunity | new_quality_policy_support |
| 学前教育 | 570102 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity |  |
| 小学教育 | 570103 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity |  |
| 运动训练 | 570303 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | strong_market_signal |
| 刑事科学技术 | 580201 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity |  |
| 社会工作 | 590101 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity |  |
| 党务工作 | 590102 | 专科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | new_quality_policy_support |
| 投资学 | 020304 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal | strong_market_signal|civil_service_role_opportunity|official_emerging_major_signal |
| 国际经济与贸易 | 020401 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal | new_quality_policy_support|civil_service_role_opportunity|official_emerging_major_signal |
| 民族学 | 030401 | 本科 | high_risk_review | official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity | official_emerging_major_signal |
| 学前教育 | 040106 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|limited_market_signal | civil_service_role_opportunity|official_emerging_major_signal |
| 体育教育 | 040201 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|weak_civil_service_opportunity | strong_market_signal|official_emerging_major_signal |
| 运动训练 | 040202 | 本科 | high_risk_review | employment_red_or_yellow_warning|official_policy_setting_warning|weak_civil_service_opportunity | strong_market_signal |
| 武术与民族传统体育 | 040204 | 本科 | high_risk_review | official_policy_setting_warning|limited_market_signal|weak_civil_service_opportunity |  |

## Outputs

- Master index: `data/processed/major_risk_master_index/major_risk_master_index_2026.csv`
- Summary: `data/processed/major_risk_master_index/major_risk_master_index_summary_2026.csv`
- Source coverage: `data/processed/major_risk_master_index/major_risk_master_index_source_coverage_2026.csv`
- Manifest: `data/processed/major_risk_master_index/major_risk_master_index_manifest_2026.json`

## Use Notes

- This is an integrated review index. It keeps official records, public warning lists, and third-party market signals in separate columns.
- `overall_review_bucket` is a screening label, not an admissions recommendation or deterministic employment forecast.
- Use `source_presence_flags`, `source_level_mix`, and the source-specific fields before making a judgment about any single major.
