# Reference Seed Inventory Dataset

This package preserves the project seed files used to reproduce crawls and
joins for high-risk-major analysis. It keeps the original `data/seeds` files
and adds normalized indexes for official-site seeds, policy sources, and
RYSXAI profession/university dimensions.

## Scope

- `data/seeds/rysxai_professions.full.csv` and sample profession dimensions.
- `data/seeds/rysxai_universities.csv` school dimensions.
- Policy source seed files used for Ministry catalog/policy evidence crawls.
- Graduate official-site discovery seed CSVs.
- CHSI and graduate outcome sample seed files.

## Primary Files

| File | Description |
|---|---|
| `data/processed/reference_seed_inventory/reference_seed_file_manifest_2026.csv` | File-level manifest for every seed file, including family, suffix, row count, bytes, SHA-256, and CSV fields. |
| `data/processed/reference_seed_inventory/reference_seed_official_site_sources_2026.csv` | Concatenated graduate official-site seed rows with school, URL, domain, year, document type, discovery query, title, and rank. |
| `data/processed/reference_seed_inventory/reference_seed_official_site_unique_sources_2026.csv` | Deduplicated school/source URL table with seed-file counts and merged metadata. |
| `data/processed/reference_seed_inventory/reference_seed_rysxai_profession_summary_2026.csv` | RYSXAI profession seed rollup by level, category, subject, and hot flag. |
| `data/processed/reference_seed_inventory/reference_seed_rysxai_university_summary_2026.csv` | RYSXAI university seed rollup by province/type/property/level and tag counts. |
| `data/processed/reference_seed_inventory/reference_seed_policy_sources_2026.csv` | Combined policy document and policy evidence source seeds. |
| `data/processed/reference_seed_inventory/reference_seed_policy_source_summary_2026.csv` | Policy-source rollup by seed family, source type, source level, and source year. |
| `data/processed/reference_seed_inventory/reference_seed_inventory_manifest_2026.json` | Build manifest with row counts, checksums, and report path. |

## Packages

| Package | Contents |
|---|---|
| `outputs/reference_seed_inventory_dataset_20260612.zip` | All original `data/seeds` files, normalized seed indexes, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this reference seed dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Rebuild

```powershell
python scripts/ingestion/build_reference_seed_inventory.py
```
