# Raw Source Inventory Dataset

This package is a metadata-only inventory for local raw crawl files and crawl
logs. It is designed to make the crawl corpus auditable without redistributing
large or person-level raw source contents.

## Scope

- Scans `data/raw` and `data/logs`.
- Records file path, source family, suffix, byte size, SHA-256 status, and
  whether the file is already present in an existing zip package.
- By default, SHA-256 is computed for files up to 20 MB; larger files are
  marked `skipped_large_file` to keep the inventory build practical.
- Does not copy raw webpages, PDFs, images, JSON payloads, or crawl logs.

## Primary Files

| File | Description |
|---|---|
| `data/processed/raw_source_inventory/raw_source_file_inventory_2026.csv` | One row per raw/log file with path, source family, suffix, bytes, SHA-256 when computed, hash status, and zip package memberships. |
| `data/processed/raw_source_inventory/raw_source_family_summary_2026.csv` | Rollup by storage layer, source family, and package coverage flag. |
| `data/processed/raw_source_inventory/raw_source_package_summary_2026.csv` | Rollup by zip package membership, including `<not_packaged>` for metadata-only raw/log files. |
| `data/processed/raw_source_inventory/raw_source_inventory_manifest_2026.json` | Build manifest with row counts, checksums, and report path. |

## Current Build Snapshot

| Metric | Count |
|---|---:|
| Raw/log file inventory rows | 31,027 |
| Family summary rows | 942 |
| Package summary rows | 14 |
| Files in any zip package | 24,141 |
| Files not in a zip package | 6,886 |
| Major-risk review-source archive raw/text/metadata files | 483 |
| Major-risk review-source archive files packaged | 483 |

## Packages

| Package | Contents |
|---|---|
| `outputs/raw_source_inventory_dataset_20260612.zip` | Metadata-only raw/log file inventory, summaries, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_source_archive_raw_sources_20260612.zip` | Raw/text/metadata files for the public review-source URL archive; all 483 files are represented in this inventory. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this inventory dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Rebuild

```powershell
python scripts/ingestion/build_raw_source_inventory.py
```
