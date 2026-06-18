# Processed Asset Inventory Dataset

This package is a metadata-only catalog for processed, cleaned, report, and
dataset-document assets. It is intended to make the local data corpus auditable
without redistributing personal-level extracted records, oversized intermediate
files, or non-crawl evaluation artifacts.

## Scope

- Scans `data/processed`, `data/cleaned`, `reports`, and `docs/datasets`.
- Records file path, root, asset group, suffix, byte size, hash status, row
  count status, fields, privacy flags, package memberships, and publication
  level.
- Does not copy unbundled source data files; it only publishes metadata.

## Primary Files

| File | Description |
|---|---|
| `data/processed/processed_asset_inventory/processed_asset_file_inventory_2026.csv` | One row per scanned file with metadata, privacy flags, and package memberships. |
| `data/processed/processed_asset_inventory/processed_asset_group_summary_2026.csv` | Rollup by root, asset group, package coverage, and publication level. |
| `data/processed/processed_asset_inventory/processed_asset_privacy_summary_2026.csv` | Privacy/publication-level file counts by root. |
| `data/processed/processed_asset_inventory/processed_asset_inventory_manifest_2026.json` | Build manifest with row counts, scan roots, thresholds, checksums, and report path. |

## Current Build Snapshot

| Metric | Count |
|---|---:|
| Processed/cleaned/report/docs inventory rows | 6,828 |
| Group summary rows | 1,649 |
| Privacy summary rows | 14 |
| Files in any zip package | 3,504 |
| Files not in a zip package | 3,324 |

## Publication Levels

- `packaged_content_available`: content is already present in one or more zip
  packages.
- `metadata_only_direct_person_fields_present`: file headers/keys indicate
  direct person identifiers such as `person_name` or `student_id`; content is
  not redistributed here.
- `metadata_only_masked_person_fields_present`: file contains masked person
  fields and remains metadata-only in this package.
- `metadata_only_non_crawl_eval_artifact`: local evaluation/report artifacts
  outside the crawl source corpus.
- `metadata_only_unpackaged_intermediate_or_legacy`: intermediate, old-version,
  or otherwise unbundled data represented by metadata only.

## Packages

| Package | Contents |
|---|---|
| `outputs/processed_asset_inventory_dataset_20260612.zip` | Metadata-only processed/cleaned/report/docs inventory, summaries, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this inventory dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Rebuild

```powershell
python scripts/ingestion/build_processed_asset_inventory.py
```
