# Major Risk Source Archive Dataset

This package archives public source URLs from the major-risk review-release
source index that did not already have a local raw/text path. It is the
traceability layer for source pages, PDFs, office documents, images, and
download-handler responses behind the analyst-facing review tables.

## Scope

- Starts from `major_risk_source_document_index_2026.csv`.
- Targets URL rows with `source_path_status = no_local_path`, plus URLs already
  present in a previous archive CSV so the archive can be rebuilt from cache.
- Archives 161 unique public URLs covering 166 review-release source-index rows.
- Stores fetched bytes for every archived URL and a text/metadata companion file
  for every archived URL. Binary fallbacks extract legacy Office strings, ZIP
  member text, image metadata, and scanned-PDF metadata when full text is not
  machine-readable.
- Uses cached files on reruns and records crawl status in a reproducible CSV.

## Primary Files

| File | Description |
|---|---|
| `data/processed/major_risk_source_archive/major_risk_review_source_archive_2026.csv` | One row per archived public URL with source context, crawl status, raw path, text path, content metadata, and checksum. |
| `data/processed/major_risk_source_archive/major_risk_source_archive_manifest_2026.json` | Build manifest with inputs, outputs, row counts, domain counts, status counts, content-type counts, and checksums. |
| `reports/major_risk_source_archive/major_risk_source_archive_2026.md` | Human-readable archive report with crawl status and top domains. |
| `data/raw/major_risk_review_source_archive/20260614/` | Raw bytes, extracted text, and per-URL metadata JSON files for archived public sources. |
| `data/processed/major_risk_source_content_index/` | Searchable document, snippet, and keyword-summary tables derived from the archived text/metadata files. |

## Current Build Snapshot

| Metric | Count |
|---|---:|
| Unique archived URL rows | 161 |
| Source-index rows covered | 166 |
| Successful or cached raw downloads | 161 |
| Failed downloads | 0 |
| URLs with text or metadata file | 161 |
| URL rows joined back into review release | 161 |
| Path references joined back into review release | 322 |

## Core Fields

| Field | Meaning |
|---|---|
| `archive_id` | Stable URL archive ID. |
| `source_url`, `final_url`, `source_domain` | Original URL, final URL after redirects, and normalized domain. |
| `source_title_sample`, `source_publishers`, `evidence_families`, `source_tables` | Source context inherited from the review-release source index. |
| `crawl_status`, `http_status`, `content_type`, `content_length` | Fetch status and response metadata. |
| `raw_path`, `text_path` | Local raw bytes and extracted text/metadata path. Current build populates `text_path` for every archived URL; scanned PDFs and images receive metadata when content text is not machine-readable. |
| `sha256` | SHA-256 hash of the fetched raw bytes. |
| `error` | Fetch error when a URL cannot be archived. Current build has no failed URL rows. |

## Rebuild

```powershell
python scripts/ingestion/build_major_risk_source_archive.py --generated-at 2026-06-14 --run-id 20260614 --timeout-seconds 8 --sleep-seconds 0
python scripts/ingestion/build_major_risk_source_content_index.py --generated-at 2026-06-14
python scripts/ingestion/build_major_risk_review_release.py --generated-at 2026-06-14
```

## Packages

| Package | Contents |
|---|---|
| `outputs/major_risk_source_archive_dataset_20260612.zip` | Archive CSV, manifest, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_source_content_index_dataset_20260612.zip` | Searchable document, snippet, and keyword-summary tables derived from archived source text/metadata files. |
| `outputs/major_risk_source_archive_raw_sources_20260612.zip` | Raw bytes, extracted text, and per-URL metadata JSON files from `data/raw/major_risk_review_source_archive/20260614/`. |
| `outputs/major_risk_review_release_dataset_20260612.zip` | Review source index that joins these archive paths back onto URL rows. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including the archive metadata dataset. |
