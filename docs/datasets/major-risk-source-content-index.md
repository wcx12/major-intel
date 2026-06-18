# Major Risk Source Content Index Dataset

This support dataset turns the archived public review-release sources into
searchable document, snippet, and keyword-summary tables. It is designed for
audit work: analysts can find the original source lines that mention
professional-setting risk signals such as cancellation, stopped enrollment,
red/yellow cards, official filing/approval language, employment signals, and
policy-supported opportunity directions.

## Scope

- Starts from
  `data/processed/major_risk_source_archive/major_risk_review_source_archive_2026.csv`.
- Reads the archived text/metadata companion files for 161 public URLs.
- Produces one document row per archived URL, one keyword-snippet row per
  matched snippet/keyword pair, and one keyword summary row per configured
  keyword.
- Keeps risk-adjustment, official-policy, employment-signal, and
  opportunity-signal keywords in separate groups so downstream review can
  distinguish negative risk evidence from positive policy-support evidence.

## Primary Files

| File | Description |
|---|---|
| `data/processed/major_risk_source_content_index/major_risk_source_content_documents_2026.csv` | One row per archived source URL with source metadata, text size, paragraph count, keyword hit counts, matched keyword list, per-group hit counts, and a short snippet sample. |
| `data/processed/major_risk_source_content_index/major_risk_source_content_snippets_2026.csv` | One row per source-snippet keyword match with source URL, title sample, evidence family, keyword group, keyword, character offsets, snippet text, and local raw/text paths. |
| `data/processed/major_risk_source_content_index/major_risk_source_content_keyword_summary_2026.csv` | Keyword-level document counts, snippet counts, total hits, and sample titles/URLs. |
| `data/processed/major_risk_source_content_index/major_risk_source_content_index_manifest_2026.json` | Build manifest with inputs, outputs, row counts, keyword-group counts, coverage counts, and file checksums. |
| `reports/major_risk_source_content_index/major_risk_source_content_index_2026.md` | Human-readable report with keyword groups, top keywords, and top source documents. |

## Current Build Snapshot

| Metric | Count |
|---|---:|
| Archived source document rows | 161 |
| Documents with keyword hits | 147 |
| Keyword-snippet rows | 5,076 |
| Keyword summary rows | 32 |
| Risk-adjustment snippet rows | 865 |
| Official-policy snippet rows | 2,267 |
| Employment-signal snippet rows | 858 |
| Opportunity-signal snippet rows | 1,086 |

Top keyword hits in the current build are `本科专业` (925 hits), `就业`
(509), `专业设置` (489), `撤销` (482), `人工智能` (409), `新增` (384), `低空`
(356), `普通高等学校` (340), `毕业生` (320), and `停招` (267).

## Core Fields

| Field | Meaning |
|---|---|
| `archive_id` | Stable source archive ID inherited from the source-archive dataset. |
| `source_url`, `source_domain`, `source_title_sample` | Public URL, normalized domain, and representative title/context text. |
| `source_publishers`, `evidence_families`, `source_tables` | Source provenance inherited from the review-release source index. |
| `text_char_count`, `paragraph_count` | Text/metadata companion-file size and searchable unit count. |
| `keyword_hit_count`, `matched_keyword_count`, `matched_keywords` | Document-level keyword coverage metrics. |
| `risk_adjustment_hits`, `official_policy_hits`, `employment_signal_hits`, `opportunity_signal_hits` | Document-level hit counts by keyword group. |
| `keyword_group`, `keyword`, `snippet_text` | Snippet-table fields identifying why the source line was retained. |
| `raw_path`, `text_path` | Local paths back to archived raw bytes and extracted text/metadata. |

## Rebuild

```powershell
python scripts/ingestion/build_major_risk_source_archive.py --generated-at 2026-06-14 --run-id 20260614 --timeout-seconds 8 --sleep-seconds 0
python scripts/ingestion/build_major_risk_source_content_index.py --generated-at 2026-06-14
```

## Packages

| Package | Contents |
|---|---|
| `outputs/major_risk_source_content_index_dataset_20260612.zip` | Document, snippet, keyword-summary, manifest, report, docs, source module, CLI wrapper, and tests for the archived source content index. |
| `outputs/major_risk_source_archive_dataset_20260612.zip` | Source archive metadata and local raw/text path inventory used as the content-index input. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this content-index dataset. |
