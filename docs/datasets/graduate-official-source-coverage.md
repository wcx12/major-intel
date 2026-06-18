# Graduate Official Source Coverage Support Dataset

## Scope

This support dataset packages official-source coverage metadata for graduate
outcome evidence. It complements the public masked graduate-outcome row tables
by documenting which official school pages, PDFs, images, spreadsheets, and
employment or teaching-quality reports were found, ingested, blocked, or
excluded.

It does not include raw official PDF/HTML/XLSX files. Many original source
files may contain public person-level candidate rows, so this package ships
metadata, counts, metrics, source URLs, and local artifact hashes only.

## Current Counts

| Asset | Rows |
|---|---:|
| School coverage rows | 430 |
| School-year official list summary rows | 471 |
| Clean source-attempt audit rows | 15 |
| Remaining-school recommendation attempts | 15 |
| Employment/teaching-quality report sources | 74 |
| Employment/teaching-quality report metrics | 326 |
| Local artifact metadata rows | 174 |

## Key Findings

| Metric | Count |
|---|---:|
| Schools with official recommendation/admission records | 425 |
| Schools still without public official recommendation/admission rows | 5 |
| Remaining-school recommendation attempts ingested | 10 |
| Remaining-school recommendation attempts not ingested | 5 |
| Employment/report sources with metrics extracted | 28 |
| Employment/report sources not ingested | 40 |
| Employment/report sources retained as source-only | 6 |
| Local artifacts currently present | 73 |
| Local artifacts referenced but not present | 101 |

## Files

| File | Purpose |
|---|---|
| `data/processed/graduate_official_source_coverage/graduate_official_source_school_coverage_2026.csv` | School-level rollup joining recommendation coverage, school-year official list summaries, remaining-source attempts, employment sources, and metrics. |
| `data/processed/graduate_official_source_coverage/graduate_official_source_school_year_summary_2026.csv` | Official-source school/year/document summary without person-level rows. |
| `data/processed/graduate_official_source_coverage/graduate_official_recommendation_attempts_2026.csv` | Remaining-school official recommendation/admission source attempts with decisions and blockers. |
| `data/processed/graduate_official_source_coverage/graduate_official_employment_sources_2026.csv` | Official employment or teaching-quality report source inventory with extraction status. |
| `data/processed/graduate_official_source_coverage/graduate_official_employment_metrics_2026.csv` | Extracted official employment, further-study, and related metric rows. |
| `data/processed/graduate_official_source_coverage/graduate_official_local_artifact_inventory_2026.csv` | Metadata and hashes for referenced local source artifacts; raw files are not embedded. |
| `data/processed/graduate_official_source_coverage/graduate_official_source_coverage_manifest_2026.json` | Row counts, distributions, checksums, and packaging notes. |

## Important Fields

| Field | Meaning |
|---|---|
| `has_official_recommendation_records` | Whether the school has public official recommendation/admission row evidence in the cleaned coverage table. |
| `school_years_covered` | Years represented in the official list summary for the school. |
| `document_types`, `routes` | Types of public official lists and admission routes found. |
| `master_summary_record_count` | Count of public masked rows summarized from official list sources; not an admission-rate denominator. |
| `recommendation_*_attempt_count` | Counts of remaining-school source attempts by ingest decision. |
| `recommendation_blocker_types` | Access or suitability blockers such as WAF, JavaScript challenge, login requirement, wrong document type, or no row-level source. |
| `employment_*_source_count` | Counts of employment or teaching-quality report sources by extraction status. |
| `employment_metric_names` | Metric names extracted from official reports for the school. |
| `artifact_sha256` | Hash of a referenced local artifact when the file exists locally. |
| `included_raw_file_in_package` | Always `false` for this package. |

## Rebuild

```powershell
python scripts/ingestion/build_graduate_official_source_coverage.py --generated-at 2026-06-14
```

## Packages

| Package | Purpose |
|---|---|
| `outputs/graduate_official_source_coverage_dataset_20260612.zip` | Source coverage metadata, official metrics, artifact hash inventory, report, docs, script, source module, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- Raw official files are intentionally omitted from this package.
- Public list counts are sample/source counts, not school-level rates.
- Use `master_records_public.csv` from the graduate outcome packages for
  public masked row-level analysis.
- Use `artifact_sha256` and source URLs to trace local evidence without
  redistributing raw person-level source documents.
