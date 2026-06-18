# Official Catalog And Policy Evidence Dataset

This support package preserves two auxiliary official-source datasets used for
major and policy analysis:

- Official vocational / graduate major catalogs.
- National policy documents and direction-level evidence paragraphs.

## Official Catalog Files

| File | Rows | Purpose |
|---|---:|---|
| `data/processed/official_major_catalog/official_major_catalog_records_official_major_catalog_20260612_v2.csv` | 1,530 | Parsed official catalog rows. |
| `data/processed/official_major_catalog/official_major_catalog_records_official_major_catalog_20260612_v2.jsonl` | 1,530 | Same records in JSON Lines format. |
| `data/processed/official_major_catalog/official_major_catalog_attachments_official_major_catalog_20260612_v2.jsonl` | 2 | Attachment metadata and row counts. |
| `data/logs/official_major_catalog/official_major_catalog_20260612_v2_manifest.json` | 1 | Crawl/build manifest. |
| `reports/official_major_catalog/official_major_catalog_coverage_official_major_catalog_20260612_v2.md` | 1 | Human-readable coverage report. |

Coverage:

- 中等职业教育：358 rows.
- 高等职业教育专科：744 rows.
- 高等职业教育本科：247 rows.
- 研究生教育：181 rows.
- Attachment failures: 0.

## Policy Evidence Files

| File | Rows | Purpose |
|---|---:|---|
| `data/processed/policy_evidence/policy_documents_policy_evidence_seed_20260612_v5.jsonl` | 17 | Policy document metadata, source URLs, text lengths, and mention counts. |
| `data/processed/policy_evidence/policy_mentions_policy_evidence_seed_20260612_v5.csv` | 1,019 | Direction-level evidence paragraph hits. |
| `data/processed/policy_evidence/policy_mentions_policy_evidence_seed_20260612_v5.jsonl` | 1,019 | Same mentions in JSON Lines format. |
| `data/logs/policy_evidence/policy_evidence_seed_20260612_v5_manifest.json` | 1 | Crawl/build manifest. |
| `reports/policy_evidence/policy_evidence_coverage_policy_evidence_seed_20260612_v5.md` | 1 | Human-readable coverage report. |

Direction coverage:

- `advanced_manufacturing`: 198
- `artificial_intelligence`: 331
- `bio_manufacturing`: 127
- `commercial_space`: 17
- `digital_economy`: 93
- `future_industries`: 72
- `green_low_carbon`: 80
- `integrated_circuit`: 26
- `low_altitude_economy`: 31
- `new_materials`: 9
- `quantum_technology`: 35

## Packages

| Package | Purpose |
|---|---|
| `outputs/official_catalog_policy_evidence_dataset_20260612.zip` | Processed catalog and policy-evidence files, reports, docs, and scripts. |
| `outputs/official_catalog_policy_evidence_raw_sources_20260612.zip` | Raw catalog attachments and policy-evidence source pages. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined package with core risk warnings and all support datasets built in this pass. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |
