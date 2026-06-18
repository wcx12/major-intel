# Graduate Source Discovery Queue Support Dataset

## Scope

This support dataset packages the graduate-outcome source discovery queues used
to drive later official-site and CHSI crawling. It is a crawler-planning and
provenance dataset: it contains search tasks, official-homepage candidates,
probe search results, seed URLs, failure summaries, and derived queue summaries.

It does not contain person-level graduate outcome rows and should not be treated
as evidence that a specific official source exists. Rows marked `pending` still
need live crawling and human/source validation.

## Current Counts

| Asset | Rows |
|---|---:|
| Full 2024-2026 discovery tasks | 26,532 |
| Recommended-undergraduate priority discovery tasks | 1,350 |
| Official-site discovery queue rows | 450 |
| School official-site URL rows | 430 |
| Discovery task summary rows | 576 |
| School-level discovery summary rows | 2,948 |
| Search probe result rows | 370 |
| Search result domain summary rows | 95 |
| Probe seed inventory rows | 13 |
| Official-site seed failure rows | 150 |
| Source file manifest rows | 39 |

## Task Coverage

The full task queue spans three years and three source/document tracks:

| Dimension | Values |
|---|---|
| Years | 2024, 2025, 2026 |
| Source types | `recommendation_exemption`, `incoming_recommendation`, `postgraduate_admission` |
| Document types | `recommendation_exemption_list`, `incoming_recommendation_admission_list`, `postgraduate_admission_list` |
| Status | all 26,532 rows are `pending` |

The queue contains 8,844 rows for each year, source type, and document type
because it was generated as a systematic school/year/document search matrix.

## Files

| File | Purpose |
|---|---|
| `data/processed/graduate_source_discovery/graduate_discovery_tasks_2024_2026.csv` | Full school/year/source/document search task matrix. |
| `data/processed/graduate_source_discovery/graduate_recommendation_discovery_tasks_2024_2026.csv` | Smaller priority queue for undergraduate recommendation-exemption qualification lists. |
| `data/processed/graduate_source_discovery/graduate_official_site_discovery_queue_2026.csv` | Schools needing official homepage resolution for recommendation-exemption discovery. |
| `data/processed/graduate_source_discovery/graduate_school_official_sites_2026.csv` | School official-site URL candidates from the local official-site source. |
| `data/processed/graduate_source_discovery/graduate_discovery_task_summary_2026.csv` | Province/level/year/source/document/status task counts. |
| `data/processed/graduate_source_discovery/graduate_discovery_school_summary_2026.csv` | School-level task coverage and official URL availability. |
| `data/processed/graduate_source_discovery/graduate_search_results_probe_2026.csv` | Combined search-probe results with host classification. |
| `data/processed/graduate_source_discovery/graduate_search_result_domain_summary_2026.csv` | Result counts by provider, host, and school/official-likeness. |
| `data/processed/graduate_source_discovery/graduate_probe_seed_inventory_2026.csv` | Probe seed URL inventory. |
| `data/processed/graduate_source_discovery/graduate_official_site_seed_failures_2026.csv` | Combined official-site seed crawl failures. |
| `data/processed/graduate_source_discovery/graduate_source_discovery_file_manifest_2026.csv` | Checksums and row counts for source and derived files. |
| `data/processed/graduate_source_discovery/graduate_source_discovery_manifest_2026.json` | Row counts, distributions, checksums, and usage notes. |

## Search Probe Quality

The search probe result set is intentionally retained for audit even though it
contains search-engine noise. In the current run:

| Host class | Rows |
|---|---:|
| Likely official school or CHSI host | 12 |
| Other host | 358 |

The probe rows should be filtered by `likely_official_or_school_host`,
`result_host`, and manual review before becoming crawl seeds.

## Rebuild

```powershell
python scripts/ingestion/build_graduate_source_discovery.py --generated-at 2026-06-14
```

## Packages

| Package | Purpose |
|---|---|
| `outputs/graduate_source_discovery_dataset_20260612.zip` | Discovery task queues, official URL candidates, search probe results, seed/failure inventories, summaries, docs, report, script, source module, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- `pending` queue rows are not successful crawls.
- Search probe results include irrelevant public web results and should not be
  used as source evidence without review.
- This package is useful for continuing source discovery and explaining crawl
  coverage gaps, not for final factual claims about a school, major, or person.
