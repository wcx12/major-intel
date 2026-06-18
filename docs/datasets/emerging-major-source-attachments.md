# Emerging Major Source Attachments Dataset

This package indexes the official Ministry policy pages and downloadable
attachments used by the detailed emerging-major candidate dataset. It is a
provenance layer: use it to trace candidate majors back to source pages,
attachment URLs, local raw files, and parse outcomes.

## Scope

- Source family: Ministry undergraduate catalog and annual filing/approval
  notices in `data/processed/policy_documents/*_v5.*`.
- Public data only: source-page metadata, attachment metadata, local raw-file
  hashes, parse status, row counts, and candidate-major counts.
- No person-level records are included.

## Primary Files

| File | Description |
|---|---|
| `data/processed/emerging_major_source_attachments/emerging_major_source_documents_2026.csv` | Official policy page index with source IDs, URLs, publication dates, source years, source types, raw paths, page hashes, and attachment counts. |
| `data/processed/emerging_major_source_attachments/emerging_major_source_documents_2026.jsonl` | Typed JSONL version of the same source-page records. |
| `data/processed/emerging_major_source_attachments/emerging_major_source_attachments_2026.csv` | Attachment index with parent source page, attachment URL/title/type, parse status, row count, candidate-major count, raw path, and warnings JSON. |
| `data/processed/emerging_major_source_attachments/emerging_major_source_attachments_2026.jsonl` | Typed JSONL attachment records retaining warning arrays. |
| `data/processed/emerging_major_source_attachments/emerging_major_source_year_summary_2026.csv` | Coverage rollup by source year and source type. |
| `data/processed/emerging_major_source_attachments/emerging_major_attachment_parse_summary_2026.csv` | Parse-status rollup by source year, file type, and status. |
| `data/processed/emerging_major_source_attachments/emerging_major_source_raw_file_inventory_2026.csv` | Local raw-file existence, byte size, and SHA-256 inventory for source pages and attachments. |
| `data/processed/emerging_major_source_attachments/emerging_major_source_attachments_manifest_2026.json` | Build manifest with row counts, checksums, and usage notes. |

## Join Keys

- Join `emerging_major_source_attachments_2026.attachment_url` to
  `emerging_major_candidate_details/emerging_major_candidates_2026.attachment_url`.
- Join `emerging_major_source_documents_2026.doc_id` to
  `emerging_major_source_attachments_2026.parent_doc_id`.
- Use `raw_path` plus `sha256` in the raw-file inventory for byte-level source
  traceability.

## Packages

| Package | Contents |
|---|---|
| `outputs/emerging_major_source_attachments_dataset_20260612.zip` | Source-page index, attachment index, coverage summaries, raw-file inventory, crawl manifest/failure log, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this provenance dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Rebuild

```powershell
python scripts/ingestion/build_emerging_major_source_attachments.py
```
