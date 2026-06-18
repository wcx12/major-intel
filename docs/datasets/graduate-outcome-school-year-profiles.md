# Graduate Outcome School-Year Profile Support Dataset

This support dataset combines public, masked official-source graduate outcome
records with official employment/teaching-quality report metrics at the
school-year level.

It is not a direct major-risk warning table. It is a school-level evidence
base for comparing official further-study, recommendation/admission samples,
and employment-quality report metrics.

## Scope

The build uses the graduate outcome clean package verified on 2026-06-04:

- 285,608 public masked recommendation/admission records;
- 326 official employment or teaching-quality report metric rows;
- 74 official employment or teaching-quality report source rows;
- 430 school-level recommendation-coverage rows;
- 15 source-attempt audit rows.

Public record counts are official-source sample counts. Official percentage
fields come only from extracted official employment or teaching-quality report
metrics.

## Outputs

| File | Purpose |
|---|---|
| `data/processed/graduate_outcomes/graduate_outcome_school_year_profiles_20260604.csv` | One school-year profile per school/year with public row counts, source samples, official metric fields, coverage fields, and source-attempt counts. |
| `data/processed/graduate_outcomes/graduate_outcome_school_summary_20260604.csv` | School-level rollup across all profile years plus coverage-only schools. |
| `data/processed/graduate_outcomes/graduate_outcome_school_year_profiles_manifest_20260604.json` | Build manifest with row counts and source counts. |
| `reports/graduate_outcomes/school_year_profiles_20260604.md` | Human-readable build report. |

## Current Counts

| Metric | Count |
|---|---:|
| Public masked row-level input records | 285,608 |
| Destination-school public records | 285,608 |
| Undergraduate-source public records | 2,181 |
| Official metric rows | 326 |
| Official report source rows | 74 |
| School-year profile rows | 860 |
| School summary rows | 524 |
| Profiles with public records | 795 |
| Profiles with official metrics | 28 |
| Coverage schools | 430 |
| Source-attempt schools | 15 |

## Key Fields

| Field | Meaning |
|---|---|
| `school_year_profile_id` | Stable hash ID for school and normalized year. |
| `school_name`, `year` | School-year key. Ranges such as `2023-2024` normalize to the ending year. |
| `public_record_count` | Sum of rows where the school appears as destination school or undergraduate source school. |
| `as_destination_record_count` | Public rows where `school_name` is the destination/admitting school. |
| `as_undergraduate_source_record_count` | Public rows where the school appears in `undergraduate_school`. |
| `unique_public_record_count` | Distinct public masked record IDs in the profile. |
| `destination_school_count`, `undergraduate_source_school_count` | Counterparty school counts. |
| `admission_major_count`, `undergraduate_major_count` | Distinct exposed major/programme names in public rows. |
| `needs_review_count`, `avg_quality_score`, `low_quality_record_count` | Quality indicators inherited from the public clean package. |
| `official_metric_count`, `official_report_source_count` | Counts of linked official report metric/source rows. |
| `official_*_rate` fields | Rate metrics extracted from official reports, when available. |
| `official_lowest_employment_like_rate` | Lowest employment/destination-implementation style percentage found in the profile year. |
| `official_highest_further_study_like_rate` | Highest further-study style percentage found in the profile year. |
| `coverage_*` fields | School-level recommendation/admission coverage metadata. |
| `source_attempt_*` fields | Source-attempt and blocker audit summary. |

## Packaging

| Package | Purpose |
|---|---|
| `outputs/graduate_outcomes_school_year_profiles_dataset_20260612.zip` | Derived school-year profile tables, public/official source tables, report, docs, scripts, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- Public list counts are not true school-level admission, employment, or
  further-study rates.
- `official_*` percentage fields should be read with each metric's original
  source URL, scope, and extraction quality.
- Undergraduate-source coverage is sparse because many public admission lists
  do not expose the undergraduate school.
- Coverage-only schools appear in the school summary table even when they have
  no school-year profile row.
