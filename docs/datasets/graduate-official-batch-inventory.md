# Graduate Official Batch Inventory Dataset

This package is a metadata-only inventory of the local graduate official-site
batch outputs created during source discovery and extraction. Many batch record
files contain direct person identifiers, so the package does not redistribute
those records. It keeps enough file-level and document-level metadata to audit
coverage, hashes, row counts, and provenance.

## Scope

- Scans `data/processed/graduate_outcomes_official_site*` and
  `data/processed/official_site_recommendation_websearch*` batch directories.
- Publishes batch directory inventory, file hash inventory, public document-page
  metadata, document-type coverage, and privacy classification summaries.
- Does not copy `records.csv`, `records.jsonl`, `records_clean.csv`,
  `records_public.csv`, or curated person-level record files from the scanned
  batch directories.

## Primary Files

| File | Description |
|---|---|
| `data/processed/graduate_official_batch_inventory/graduate_official_batch_directories_2026.csv` | One row per scanned batch directory with file counts, bytes, document counts, row-count rollups, source years, document types, and person-field file counts. |
| `data/processed/graduate_official_batch_inventory/graduate_official_batch_files_2026.csv` | One row per batch file with path, name, suffix, byte size, SHA-256, row count, field names, and publication/privacy level. |
| `data/processed/graduate_official_batch_inventory/graduate_official_batch_documents_2026.csv` | Public official document metadata from batch `documents.jsonl` files, including school, URL, title, year, type, parse status, and source raw path. |
| `data/processed/graduate_official_batch_inventory/graduate_official_batch_document_summary_2026.csv` | Rollup by year, document type, and parse status. |
| `data/processed/graduate_official_batch_inventory/graduate_official_batch_privacy_summary_2026.csv` | File-name level privacy classification counts. |
| `data/processed/graduate_official_batch_inventory/graduate_official_batch_inventory_manifest_2026.json` | Build manifest with row counts, checksums, and privacy policy notes. |

## Privacy Handling

- Direct identifier fields such as `person_name` and `student_id` are detected
  at the file-inventory level.
- Files containing person-level fields are marked `inventory_only_*` and are
  not copied into this package.
- Public masked graduate-outcome record tables are delivered separately in the
  graduate outcome and CHSI public-source packages.

## Packages

| Package | Contents |
|---|---|
| `outputs/graduate_official_batch_inventory_dataset_20260612.zip` | Metadata-only batch directory/file/document inventory, privacy summaries, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this inventory dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Rebuild

```powershell
python scripts/ingestion/build_graduate_official_batch_inventory.py
```
