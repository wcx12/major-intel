# Graduate CHSI Public Sources Report

Generated: 2026-06-14

## Summary

This dataset isolates the CHSI public-source subset behind the graduate outcome
clean package. It provides masked public records and source metadata for CHSI
school index pages, bulletin seeds, captured document metadata, and crawl-batch
coverage.

Unmasked record files are excluded from the package. The source-file manifest
labels those files explicitly so the package remains useful for audit without
redistributing unmasked person-level rows.

## Coverage

| Metric | Count |
|---|---:|
| Masked CHSI public records | 5,710 |
| School-year summary rows | 152 |
| School-index inventory rows | 939 |
| Bulletin seed inventory rows | 244 |
| Document inventory rows | 249 |
| Crawl-batch summary rows | 11 |
| Source-file manifest rows | 123 |

## Public Record Mix

| Route | Rows |
|---|---:|
| `postgraduate_exam_or_admission` | 4,970 |
| `recommendation_exemption` | 740 |

| Document type | Rows |
|---|---:|
| `postgraduate_admission_list` | 4,971 |
| `incoming_recommendation_admission_list` | 651 |
| `recommendation_exemption_list` | 88 |

## Packaging Notes

- `chsi_public_records_2026.csv` contains masked person and student identifiers.
- Unmasked master and per-batch record files are not packaged.
- `chsi_document_inventory_2026.csv` includes source URLs and metadata, not raw
  page body text.
- Implausible extracted years should be reviewed against the source URL before
  downstream use.
