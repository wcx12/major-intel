# Major Risk Evidence Profiles Dataset

This package is the long-form evidence layer behind the unified major risk
master index. It keeps each employment warning, official policy row, and
derived market/opportunity signal as a separate row, with source IDs, titles,
URLs, source paths, evidence text, and signal direction.

## Scope

- Builds from the current processed corpus rather than recrawling source pages.
- Covers all 4,028 rows in `major_risk_master_index_2026.csv`.
- Produces 20,664 evidence records and 4,028 per-major evidence summaries.
- Preserves source-level separation: official policy/emerging/register evidence
  (`A`), public employment-warning summaries (`B`), and third-party market or
  heuristic signals (`C`).
- Resolves all 1,616 RYSXAI market-observation evidence rows to paired local
  raw JSON paths for the `profession/info` and `profession/positions` API
  sources when those archives are present.

## Primary Files

| File | Description |
|---|---|
| `data/processed/major_risk_evidence_profiles/major_risk_evidence_records_2026.csv` | Long-form evidence table with one row per source-backed or profile-derived signal. |
| `data/processed/major_risk_evidence_profiles/major_risk_evidence_major_summary_2026.csv` | Per-major evidence rollup with family counts, signal-direction counts, source URL counts, and source samples. |
| `data/processed/major_risk_evidence_profiles/major_risk_evidence_source_summary_2026.csv` | Evidence-family/source-level rollup by signal direction and source table. |
| `data/processed/major_risk_evidence_profiles/major_risk_evidence_profiles_manifest_2026.json` | Build manifest with inputs, row counts, family counts, direction counts, and checksums. |
| `reports/major_risk_evidence_profiles/major_risk_evidence_profiles_2026.md` | Human-readable report with family counts, source summary, and high-risk evidence coverage samples. |

## Current Build Snapshot

| Evidence family | Records |
|---|---:|
| `official_policy_warning` | 9,143 |
| `vocational_register` | 2,737 |
| `new_quality` | 2,053 |
| `civil_service` | 1,653 |
| `market_observation` | 1,616 |
| `ai_replacement` | 1,612 |
| `emerging_major` | 1,280 |
| `employment_warning` | 570 |

| Signal direction | Records |
|---|---:|
| `risk` | 10,779 |
| `reference` | 4,956 |
| `opportunity` | 3,548 |
| `mixed` | 1,381 |

## Core Fields

| Field | Meaning |
|---|---|
| `evidence_id` | Stable evidence-row ID. |
| `major_master_id` | Join key back to `major_risk_master_index_2026.csv`. |
| `evidence_family` | Source family such as `employment_warning`, `official_policy_warning`, `market_observation`, or `new_quality`. |
| `signal_direction` | `risk`, `opportunity`, `reference`, or `mixed`. |
| `source_level` | Evidence/source level: A, B, C, or a mix. |
| `source_table` | Processed input table that produced the evidence row. |
| `source_record_id` | Row ID from the source table when available. |
| `source_ids` | Source IDs or linked warning IDs carried by the source row. |
| `source_titles`, `source_urls`, `source_publishers`, `source_paths` | Resolved provenance metadata where available. URL and path ordering is preserved when a source row carries paired URLs and local files. |
| `evidence_text` | Source-backed excerpt or profile-derived evidence summary. |
| `source_note` | Additional context such as criterion text, table row number, top jobs, or sample schools. |

## Rebuild

```powershell
python scripts/ingestion/build_major_risk_evidence_profiles.py --generated-at 2026-06-14
```

## Packages

| Package | Contents |
|---|---|
| `outputs/major_risk_evidence_profiles_dataset_20260612.zip` | Evidence records, per-major summary, source summary, manifest, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this evidence layer. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Related Review Release

Use `docs/datasets/major-risk-review-release.md` for the analyst-facing
shortlist and unified source-document index built from this evidence layer. The
evidence records are optimized for row-level traceability; the review release is
optimized for sorting review work and browsing sources.
