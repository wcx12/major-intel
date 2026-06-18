# Emerging Major Candidate Details Dataset

## Scope

This dataset preserves the detailed official Ministry policy/catalog candidate
rows behind the undergraduate official event tables. It adds the missing JSON
Lines representation to the packaged outputs so downstream code can consume
typed fields such as `schema_version` and `warnings` without reparsing CSV
strings.

The data comes from official Ministry catalog and filing/approval documents. It
contains no person-level records.

## Current Counts

| Asset | Rows |
|---|---:|
| Candidate JSONL rows | 33,981 |
| Candidate CSV rows | 33,981 |
| Unique major rows | 1,280 |
| Coverage rows | 14 |
| Candidate distribution rows | 20 |
| Source document summary rows | 14 |
| Warning summary rows | 1 |
| Normalized official event rows | 33,173 |
| Official event summary rows | 1,081 |
| Rejected candidate rows | 808 |

## Candidate Distribution

| Field | Distribution |
|---|---|
| `event_type` | `catalog_added`: 5,435; `filing_added`: 28,546 |
| `candidate_status` | `catalog_confirmed`: 33,973; `catalog_candidate`: 8 |
| `major_level` | `本科`: 33,981 |
| `source_level` | `A`: 33,981 |
| `parsed_from` | `pdf`: 12,674; `docx`: 10,345; `doc`: 5,143; `pdf_ocr`: 2,948; `xls`: 2,871 |

Rows cover source years 2012-2024 and 2026. The 2025 undergraduate catalog is
represented through the 2024 annual filing/approval notice that published the
2025 catalog.

## Files

| File | Purpose |
|---|---|
| `data/processed/emerging_major_candidate_details/emerging_major_candidates_2026.jsonl` | Full candidate rows in JSON Lines format with typed `warnings` arrays and schema version. |
| `data/processed/emerging_major_candidate_details/emerging_major_candidates_2026.csv` | Full candidate rows in CSV format. |
| `data/processed/emerging_major_candidate_details/emerging_major_unique_majors_2026.csv` | Deduplicated major-level rollup. |
| `data/processed/emerging_major_candidate_details/emerging_major_coverage_2026.csv` | Attachment/source-year coverage summary. |
| `data/processed/emerging_major_candidate_details/emerging_major_candidate_distribution_2026.csv` | Distribution by year, event type, status, level, source level, and parser. |
| `data/processed/emerging_major_candidate_details/emerging_major_source_document_summary_2026.csv` | Source document rollup with attachment URLs and candidate counts. |
| `data/processed/emerging_major_candidate_details/emerging_major_warning_summary_2026.csv` | Warning-array distribution. |
| `data/processed/emerging_major_candidate_details/undergraduate_major_official_events_20260612_v5.csv` | Normalized undergraduate official event table joined to risk warning signals. |
| `data/processed/emerging_major_candidate_details/undergraduate_major_official_event_summary_20260612_v5.csv` | Event summary by normalized major. |
| `data/processed/emerging_major_candidate_details/undergraduate_major_official_events_rejected_20260612_v5.csv` | Rejected candidate rows and reasons. |
| `data/processed/emerging_major_candidate_details/emerging_major_candidate_details_manifest_2026.json` | Row counts, distributions, checksums, and usage notes. |

## Relationship To Existing Packages

The existing full package already included the candidate CSV and normalized
official event tables under `data/processed/policy_documents/`. This package
adds the JSONL detail file and small summary indexes as a dedicated delivery
unit.

## Rebuild

```powershell
python scripts/ingestion/build_emerging_major_candidate_details.py --generated-at 2026-06-14
```

## Packages

| Package | Purpose |
|---|---|
| `outputs/emerging_major_candidate_details_dataset_20260612.zip` | Candidate JSONL/CSV detail, unique major rollup, coverage, source document summaries, normalized official event tables, docs, report, script, source module, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this detailed support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- Candidate rows are official policy/catalog extraction rows, not direct labor
  market risk labels.
- The normalized official event files should be used for joins to risk-warning,
  AI, market, civil-service, and transfer-policy support datasets.
- Some candidate rows from older catalog documents are rejected downstream when
  the undergraduate major code is missing or invalid; those rows remain in the
  detailed candidate file for traceability.
