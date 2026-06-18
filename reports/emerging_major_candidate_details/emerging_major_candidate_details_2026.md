# Emerging Major Candidate Details Report

Generated: 2026-06-14

## Summary

This package adds a dedicated detailed delivery unit for official Ministry
undergraduate catalog and filing/approval candidate rows. It preserves the JSONL
candidate representation that was not previously included in the combined
package and adds small distribution/source-summary indexes for easier review.

## Coverage

| Metric | Count |
|---|---:|
| Candidate JSONL rows | 33,981 |
| Candidate CSV rows | 33,981 |
| Unique major rows | 1,280 |
| Source coverage rows | 14 |
| Source document summary rows | 14 |
| Normalized official event rows | 33,173 |
| Official event summary rows | 1,081 |
| Rejected candidate rows | 808 |

## Candidate Mix

| Event type | Rows |
|---|---:|
| `filing_added` | 28,546 |
| `catalog_added` | 5,435 |

| Parser/source format | Rows |
|---|---:|
| `pdf` | 12,674 |
| `docx` | 10,345 |
| `doc` | 5,143 |
| `pdf_ocr` | 2,948 |
| `xls` | 2,871 |

## Notes

- All candidate rows are source level `A`.
- The JSONL file contains no person-level records.
- The detailed candidate rows are source extraction rows; use normalized
  official event tables for downstream major-level joins.
