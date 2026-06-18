# Major Risk Master Index Dataset

This package builds a unified per-major screening index from the processed
major-risk corpus. It is designed for downstream filtering: one row per
major-code/level pair where possible, with official policy warnings, public
employment warning lists, and third-party market signals kept in separate
columns.

## Scope

- Integrates 9 source families: RYSXAI major seed, employment-warning summary,
  official policy warning rows, AI replacement ranking, market observations,
  civil-service opportunity profiles, new-quality-productivity profiles,
  official emerging-major candidates, and high-vocational register summaries.
- Produces 4,028 major index rows: 1,978 undergraduate rows and 2,050 associate
  / higher-vocational rows.
- Assigns each row to an `overall_review_bucket` for screening, not for
  deterministic admissions or employment decisions.
- Keeps `source_presence_flags` and `source_level_mix` so official A-level
  evidence can be separated from B/C-level public or third-party signals.

## Primary Files

| File | Description |
|---|---|
| `data/processed/major_risk_master_index/major_risk_master_index_2026.csv` | Wide per-major index with risk signals, opportunity signals, source coverage, and review buckets. |
| `data/processed/major_risk_master_index/major_risk_master_index_summary_2026.csv` | Rollup by all rows, review bucket, level, category, source coverage count, risk-signal count, and opportunity-signal count. |
| `data/processed/major_risk_master_index/major_risk_master_index_source_coverage_2026.csv` | Source-family coverage and linked risk/opportunity counts. |
| `data/processed/major_risk_master_index/major_risk_master_index_manifest_2026.json` | Build manifest with inputs, output paths, row counts, checksums, and bucket counts. |
| `reports/major_risk_master_index/major_risk_master_index_2026.md` | Human-readable build report and sample high-risk rows. |

## Review Buckets

| Bucket | Meaning |
|---|---|
| `high_risk_review` | Employment or official policy risk is combined with another risk signal, or official policy risk combines with AI/market/civil-service weakness. |
| `employment_or_policy_warning_review` | Red/yellow employment warning or official professional-setting warning appears without additional negative signals. |
| `ai_market_risk_review` | AI replacement risk combines with weak market or civil-service opportunity. |
| `multi_signal_risk_review` | Two or more non-employment risk signals appear. |
| `opportunity_with_risk_flags` | At least one opportunity signal and at least one risk signal appear. |
| `single_signal_watch` | One risk signal appears. |
| `opportunity_watch` | Two or more opportunity signals appear and no risk signal appears. |
| `opportunity_signal_reference` | One opportunity signal appears and no risk signal appears. |
| `baseline_reference` | No current risk or opportunity signal was attached from the available sources. |

## Current Build Snapshot

| Metric | Count |
|---|---:|
| Master index rows | 4,028 |
| High-risk review rows | 657 |
| Employment red/yellow linked rows | 174 |
| Official policy warning linked rows | 945 |
| AI high-signal rows | 45 |
| Market-limited rows | 1,722 |
| Civil-service-limited rows | 1,087 |
| New-quality supported rows | 1,133 |
| Official emerging-major signal rows | 1,163 |

## Core Fields

| Field | Meaning |
|---|---|
| `major_master_id` | Stable row ID from major code, name, and level. |
| `major_code`, `major_name`, `major_level` | Canonical major identity used for joins. |
| `source_presence_flags` | Pipe-delimited source families present for the row. |
| `source_level_mix` | Evidence-level mix observed across source families: A, B, and/or C. |
| `risk_signal_count` | Count of negative screening signals attached to the row. |
| `opportunity_signal_count` | Count of positive/opportunity signals attached to the row. |
| `overall_review_bucket` | Derived screening bucket. |
| `primary_risk_reasons` | Pipe-delimited reasons behind the risk count. |
| `primary_opportunity_reasons` | Pipe-delimited reasons behind the opportunity count. |
| `needs_review`, `review_notes` | Flags for non-major names, missing major codes, or missing levels. |

## Rebuild

```powershell
python scripts/ingestion/build_major_risk_master_index.py --generated-at 2026-06-14
```

## Packages

| Package | Contents |
|---|---|
| `outputs/major_risk_master_index_dataset_20260612.zip` | Master index outputs, report, docs, source module, CLI wrapper, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this master index. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Related Evidence Layer

Use `docs/datasets/major-risk-evidence-profiles.md` and
`data/processed/major_risk_evidence_profiles/major_risk_evidence_records_2026.csv`
when a row needs source-level traceability. The master index is optimized for
screening and filtering; the evidence layer is optimized for showing which
specific warning row, policy record, URL, or market/opportunity profile supports
each signal.
