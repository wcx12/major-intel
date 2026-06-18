# High-Vocational Major Register Dataset

This support dataset preserves the publicly fetchable high-vocational specialty
registration query data from the Ministry of Education government service
platform and links it back to the major-risk warning dataset.

## Source

- Query page: https://zwfw.moe.gov.cn/zyyxzy/
- API base: https://zwfw.moe.gov.cn/eduSearch/api
- Main endpoint: `/major-register?year=<year>&page=<page>&pageSize=50`
- Auxiliary endpoints: `/years`, `/provinces`

The live API currently exposes 14 years: 2013-2026. The 2026 endpoint reports
69,414 specialty-point rows.

## Files

| File | Rows | Purpose |
|---|---:|---|
| `data/processed/vocational_major_register/vocational_major_records_2013_2026.csv` | 814,328 | Direct normalized Ministry API rows. |
| `data/processed/vocational_major_register/vocational_major_unique_2013_2026.csv` | 2,737 | Cross-year unique `major_code`/`major_name` summary. |
| `data/processed/vocational_major_register/vocational_major_records_2013_2026_annotated.csv` | 814,328 | Row-level table with unique IDs, duplicate flags, and risk/policy linkage fields. |
| `data/processed/vocational_major_register/vocational_major_risk_link_summary_2013_2026.csv` | 2,737 | Major-level coverage and risk/policy linkage summary. |
| `data/processed/vocational_major_register/vocational_major_risk_links_manifest_2013_2026.json` | 1 | Build manifest and validation counts. |
| `reports/vocational_major_register/vocational_major_register_coverage_2013_2026.md` | 1 | Year-level coverage report. |
| `reports/vocational_major_register/vocational_major_risk_links_2013_2026.md` | 1 | Risk-link report. |

## Coverage

| Year | Rows |
|---|---:|
| 2013 | 47,619 |
| 2014 | 49,179 |
| 2015 | 47,077 |
| 2016 | 50,810 |
| 2017 | 52,901 |
| 2018 | 54,840 |
| 2019 | 57,788 |
| 2020 | 59,536 |
| 2021 | 62,024 |
| 2022 | 64,038 |
| 2023 | 64,861 |
| 2024 | 65,998 |
| 2025 | 68,243 |
| 2026 | 69,414 |

Every year covers 32 province-level regions returned by the API.

## Annotated Row Fields

| Field | Meaning |
|---|---|
| `record_id` | Unique row ID for analysis. Duplicate API natural keys receive `:001`, `:002`, etc. |
| `source_record_id` | Original natural-key hash from the normalized API row. This may repeat when the API returns duplicate rows. |
| `year` | Registration/result year. |
| `province_name` | Province-level region. |
| `major_code` | Specialty code returned by the API. |
| `major_name` | Specialty name returned by the API. |
| `school_code` | School code when returned by the API. |
| `school_name` | School name returned by the API. |
| `school_system` | Schooling length/system field returned by the API. |
| `remark` | API remark field. Usually blank. |
| `source_level` | Source quality label. `A` means direct Ministry platform API. |
| `source_url` | API page URL used for the row. |
| `captured_at` | Crawl timestamp. |
| `duplicate_group_size` | Number of identical API natural-key rows. |
| `duplicate_ordinal` | Row ordinal within the duplicate natural-key group. |
| `is_duplicate_api_row` | `true` when `duplicate_group_size > 1`. |
| `employment_warning_count` | Count of linked high-vocational employment-warning records. |
| `employment_risk_levels` | Linked warning labels, such as `red|yellow`. |
| `employment_warning_years` | Years where the specialty appears in high-vocational warning records. |
| `employment_warning_match_basis` | `code`, `name`, or `code+name`. |
| `has_employment_high_risk_warning` | `true` if linked red or yellow warning exists. |
| `has_employment_red_warning` | `true` if linked red warning exists. |
| `has_employment_yellow_warning` | `true` if linked yellow warning exists. |
| `has_employment_green_signal` | `true` if linked green-list record exists. |
| `official_policy_warning_count` | Count of linked official policy warning/control records. |
| `official_policy_record_types` | Linked policy record types. |
| `official_policy_years` | Years of linked policy records. |
| `official_policy_match_basis` | `code`, `name`, or `code+name`. |
| `has_official_policy_warning` | `true` if any high-vocational official policy row is linked. |

## Validation Snapshot

- Normalized official rows: 814,328
- Annotated rows: 814,328
- Duplicate annotated `record_id`: 0
- API duplicate natural-key groups: 125
- API duplicate excess rows: 125
- Cross-year major-code/name pairs: 2,737
- Major-code/name pairs linked to red/yellow high-vocational employment warning: 121
- Major-code/name pairs linked to official high-vocational policy records: 196

## Build

```powershell
python scripts/crawlers/vocational_major_register_crawler.py --year 2026
python scripts/ingestion/build_vocational_major_register_index.py --input-jsonl <one-or-more-year-jsonl-files>
python scripts/ingestion/build_vocational_major_risk_links.py
```

The checked-in workspace already contains the 2013-2026 combined outputs. The
raw API page JSON files are stored under `data/raw/vocational_major_register/`.

## Packages

| Package | Purpose |
|---|---|
| `outputs/vocational_major_register_dataset_20260612.zip` | Processed high-vocational register files, risk-link summaries, reports, docs, and scripts. |
| `outputs/vocational_major_register_raw_pages_20260612.zip` | Raw Ministry API JSON pages and crawl logs. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined package with the core major-risk warning dataset and this high-vocational register support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |
