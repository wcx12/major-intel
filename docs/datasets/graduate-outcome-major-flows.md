# Graduate Outcome Major Flow Support Dataset

This support dataset aggregates public, masked official-source graduate outcome
records into major-level flow rows and links those rows to the major-risk
warning dataset.

It is not a direct employment-warning dataset. It is useful as supplementary
evidence for observed recommendation-exemption, postgraduate admission, and
further-study flows exposed by official school or CHSI pages.

## Scope

The input public row-level table contains 285,608 masked records from the
graduate outcome clean package verified on 2026-06-04. The derived major-flow
table uses two major roles:

- `undergraduate_major`: the source student's undergraduate major when an
  official row exposes it;
- `admission_major`: the destination recommended/admitted postgraduate major or
  programme name.

Leading programme codes such as `125100 工商管理` and `(010100)哲学` are
normalized for matching, while the original reported strings are retained in
`reported_major_names`.

## Outputs

| File | Purpose |
|---|---|
| `data/processed/graduate_outcomes/major_outcome_flow_summary_20260604.csv` | Major-role flow summary with official row counts, quality stats, source samples, and risk links. |
| `data/processed/graduate_outcomes/major_outcome_flow_role_summary_20260604.csv` | Role-level summary for undergraduate-major and admission-major rows. |
| `data/processed/graduate_outcomes/major_outcome_flows_manifest_20260604.json` | Build manifest with row counts and linkage counts. |
| `reports/graduate_outcomes/major_outcome_flows_20260604.md` | Human-readable build report. |
| `data/cleaned/graduate_outcomes/master_records_public.csv` | Public masked row-level source table used for aggregation. |
| `data/cleaned/graduate_outcomes/official_employment_report_metrics.csv` | Official employment/further-study metrics extracted from school reports. |
| `data/processed/graduate_outcomes/graduate_outcome_school_year_profiles_20260604.csv` | Related school-year profile table combining public sample counts with official report metrics. |
| `outputs/graduate_outcomes/graduate_outcomes_clean_data_package.xlsx` | Existing workbook package with public records, coverage, source attempts, and metrics. |

## Current Counts

| Metric | Count |
|---|---:|
| Public masked row-level input records | 285,608 |
| Rows with undergraduate major | 3,494 |
| Rows with admission major | 253,584 |
| Major-flow summary rows after normalization | 4,534 |
| Admission-major flow rows | 4,124 |
| Undergraduate-major flow rows | 410 |
| Major-flow rows linked to employment warnings | 143 |
| Major-flow rows linked to red/yellow employment warnings | 85 |
| Major-flow rows linked to official policy risk rows | 424 |
| Major-flow rows linked to AI replacement-risk rows | 493 |

## Key Fields

| Field | Meaning |
|---|---|
| `major_flow_id` | Stable hash ID for role and normalized major name. |
| `major_role` | `undergraduate_major` or `admission_major`. |
| `major_name` | Normalized major/programme name used for matching. |
| `reported_major_names` | Up to 25 source strings that were merged into the normalized name. |
| `record_count` | Number of public masked official-source rows in this flow. |
| `destination_school_count` | Distinct destination schools in the flow. |
| `undergraduate_school_count` | Distinct source undergraduate schools in the flow. |
| `source_document_count` | Distinct source URLs behind the flow. |
| `needs_review_count`, `avg_quality_score`, `low_quality_record_count` | Quality indicators inherited from the public row-level package. |
| `employment_warning_*` | Exact normalized-name matches to red/yellow/green warning rows. |
| `official_policy_*` | Exact normalized-name matches to official cancellation, stop-enrollment, warning-list, or controlled-major rows. |
| `ai_replacement_*` | Exact normalized-name matches to source-level C AI replacement-risk rows. |

## Packaging

| Package | Purpose |
|---|---|
| `outputs/graduate_outcomes_major_flows_dataset_20260612.zip` | Derived major-flow tables, public masked source tables, employment metrics, workbook package, reports, docs, scripts, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- Flow counts are official-source row counts, not employment rates and not
  per-major employment-quality conclusions.
- `admission_major` often describes graduate programme names; not every value
  is an undergraduate major.
- Public records are masked. The internal unmasked clean table is not included
  in this support package.
- Source URLs and quality fields should be preserved for downstream audit.
