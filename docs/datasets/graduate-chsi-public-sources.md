# Graduate CHSI Public Sources Support Dataset

## Scope

This support dataset packages the CHSI / China Graduate Admissions Information
Network public-source subset used by the graduate outcome clean package. It
contains masked public rows plus source metadata for CHSI school index pages,
bulletin seeds, captured document metadata, and crawl-batch summaries.

It does not include unmasked CHSI record files. CHSI person-level source rows
are represented through `chsi_public_records_2026.csv`, where person and
student identifiers are masked.

## Current Counts

| Asset | Rows |
|---|---:|
| Masked CHSI public records | 5,710 |
| CHSI school-year summary rows | 152 |
| CHSI school-index inventory rows | 939 |
| CHSI bulletin seed inventory rows | 244 |
| CHSI document inventory rows | 249 |
| CHSI crawl-batch summary rows | 11 |
| CHSI source-file manifest rows | 123 |

## Public Record Distributions

| Route | Rows |
|---|---:|
| `postgraduate_exam_or_admission` | 4,970 |
| `recommendation_exemption` | 740 |

| Document type | Rows |
|---|---:|
| `postgraduate_admission_list` | 4,971 |
| `incoming_recommendation_admission_list` | 651 |
| `recommendation_exemption_list` | 88 |

Top years by public record count:

| Year | Rows |
|---|---:|
| 2026 | 1,063 |
| 2022 | 782 |
| 2025 | 683 |
| 2008 | 552 |
| 2018 | 523 |
| 2015 | 432 |
| 2009 | 344 |
| 2024 | 341 |
| 2021 | 307 |
| 2011 | 168 |

The manifest preserves the extracted year distribution as-is. Rare implausible
years such as `2095` should be treated as extraction noise and reviewed against
the linked CHSI source URL before use in analysis.

## Files

| File | Purpose |
|---|---|
| `data/processed/graduate_chsi_public_sources/chsi_public_records_2026.csv` | Masked CHSI public person-level rows. |
| `data/processed/graduate_chsi_public_sources/chsi_school_year_summary_2026.csv` | CHSI source school/year/document/route counts. |
| `data/processed/graduate_chsi_public_sources/chsi_school_index_inventory_2026.csv` | Deduplicated CHSI school index rows and source-file provenance. |
| `data/processed/graduate_chsi_public_sources/chsi_bulletin_seed_inventory_2026.csv` | Deduplicated CHSI bulletin seed URLs and discovery metadata. |
| `data/processed/graduate_chsi_public_sources/chsi_document_inventory_2026.csv` | Captured CHSI document metadata without raw page body text. |
| `data/processed/graduate_chsi_public_sources/chsi_crawl_batch_summary_2026.csv` | Per-batch row counts and sensitive-file exclusion flags. |
| `data/processed/graduate_chsi_public_sources/chsi_source_file_manifest_2026.csv` | Input/output file hashes with unmasked-file exclusion labels. |
| `data/processed/graduate_chsi_public_sources/graduate_chsi_public_sources_manifest_2026.json` | Row counts, distributions, checksums, and privacy notes. |

## Relationship To Graduate Outcome Master

The CHSI records are also integrated into
`data/cleaned/graduate_outcomes/master_records_public.csv` with
`source_dataset=chsi_yanzhao`. This package keeps the CHSI subset separately
available for source audit and provenance review.

## Rebuild

```powershell
python scripts/ingestion/build_graduate_chsi_public_sources.py --generated-at 2026-06-14
```

## Packages

| Package | Purpose |
|---|---|
| `outputs/graduate_chsi_public_sources_dataset_20260612.zip` | Masked CHSI public records, source inventories, crawl-batch summaries, report, docs, script, source module, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- Unmasked `master_records_clean.csv`, per-batch `records.jsonl`,
  `records.csv`, and `records_clean.csv` files are excluded.
- CHSI rows are public-source samples, not admission-rate denominators.
- Use `source_url`, `title`, and document inventory fields for source review
  before drawing year-specific or school-specific conclusions.
