# Major Risk Review Release Dataset

This package is the analyst-facing release layer for the major-risk corpus. It
turns the master index and evidence profiles into two directly usable tables:
a sortable high-risk / risk-watch major shortlist and a unified source-document
index.

## Scope

- Includes every major with at least one risk signal from
  `major_risk_master_index_2026.csv`.
- Adds a transparent `review_priority_score` for triage and a five-tier
  `review_tier`.
- Builds a source-document index from the evidence table, including public URLs,
  local raw/text source paths, and local processed-profile placeholders where a
  signal comes from derived profile tables.
- Resolves paired RYSXAI `profession/info` and `profession/positions` API URLs
  back to existing local raw JSON archives where those files are already present.
- Joins `major_risk_review_source_archive_2026.csv` so remaining public URLs are
  linked to locally archived raw/text files.

## Primary Files

| File | Description |
|---|---|
| `data/processed/major_risk_review_release/major_risk_high_risk_shortlist_2026.csv` | Sortable risk-review shortlist with rank, tier, priority score, evidence counts, source URL samples, and recommended review actions. |
| `data/processed/major_risk_review_release/major_risk_source_document_index_2026.csv` | Unified source-document index grouped by URL, local raw/text path, or local profile source. |
| `data/processed/major_risk_review_release/major_risk_review_release_summary_2026.csv` | Rollup by all rows, review tier, review bucket, level, category, and risk-signal count. |
| `data/processed/major_risk_review_release/major_risk_review_release_manifest_2026.json` | Build manifest with inputs, outputs, row counts, tier counts, source-kind counts, and checksums. |
| `reports/major_risk_review_release/major_risk_review_release_2026.md` | Human-readable report with tier counts, source-kind counts, and top ranked review rows. |

## Current Build Snapshot

| Metric | Count |
|---|---:|
| Shortlist rows | 2,267 |
| Source-document index rows | 4,428 |
| Summary rows | 51 |
| Public/source URL rows | 3,660 |
| Local raw/text path rows | 764 |
| Local derived-profile rows | 4 |
| Source rows with available local paths | 4,428 |
| Source rows with no local path | 0 |
| Source rows with missing local profile path | 0 |
| RYSXAI API URL rows resolved to local raw JSON | 3,232 |
| Review-source archive unique URL rows | 161 |
| Review-source archive path references | 322 |

## Review Tiers

| Tier | Rows | Meaning |
|---|---:|---|
| `tier_1_high_risk_review` | 657 | Multi-source high-risk bucket from the master index. |
| `tier_2_employment_or_policy_warning` | 356 | Employment red/yellow or official policy warning without additional negative signals. |
| `tier_3_ai_or_multi_signal_risk` | 722 | AI/market/civil-service multi-signal risk or non-employment multi-signal risk. |
| `tier_4_opportunity_with_risk_flags` | 488 | Opportunity-supported rows that still carry at least one risk flag. |
| `tier_5_single_signal_watch` | 44 | Single-signal risk-watch rows. |

## Core Fields

| Field | Meaning |
|---|---|
| `review_rank` | Sort order by descending `review_priority_score`. |
| `review_tier` | Coarse review tier derived from the master-index bucket. |
| `review_priority_score` | Transparent triage score using risk bucket, signal count, employment warnings, official policy count, AI/market/civil-service signals, evidence count, and URL count. |
| `recommended_review_action` | Pipe-delimited review actions such as verifying official policy rows or checking market weakness. |
| `source_title_sample`, `source_url_sample` | Source examples inherited from the evidence summary. |
| `source_document_id` | Stable ID for a URL, local source path, or local derived-profile placeholder in the source index. |
| `source_kind` | `url`, `local_path`, or `local_profile`. |
| `source_path`, `source_path_count` | Pipe-delimited local raw/text path references and their count. Multi-URL evidence rows are represented conservatively with separate `local_path` rows. |
| `existing_source_path_count`, `missing_source_path_count`, `source_path_status` | Local path availability checks: `all_paths_available`, `all_paths_missing`, or `no_local_path`. In the current build, all 4,428 source-document rows resolve to available local paths, including the four local-profile rows for derived processed tables. |
| `evidence_families`, `signal_directions` | Evidence families and signal directions attached to the source document. |

## Rebuild

```powershell
python scripts/ingestion/build_major_risk_review_release.py --generated-at 2026-06-14
```

## Packages

| Package | Contents |
|---|---|
| `outputs/major_risk_review_release_dataset_20260612.zip` | Review shortlist, source-document index, summary, manifest, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_source_archive_dataset_20260612.zip` | URL archive metadata, manifest, report, docs, source module, CLI wrapper, and tests for public source URLs that previously lacked local paths. |
| `outputs/major_risk_source_archive_raw_sources_20260612.zip` | Raw/text files archived from the remaining review-release public source URLs. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this review release. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |
