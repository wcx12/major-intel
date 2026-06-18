# Reference Seed Inventory

- Built at: 2026-06-14
- Seed files: 593
- Official-site seed rows: 2835
- Unique official-site source URLs: 2050
- Policy source rows: 33

## Seed Families

| seed_family | files |
|---|---:|
| chsi_source_seed | 3 |
| emerging_major_source_query_seed | 1 |
| graduate_official_site_gap_seed | 1 |
| graduate_official_site_seed | 4 |
| graduate_official_site_websearch_seed | 577 |
| graduate_outcome_sample_seed | 2 |
| policy_document_source_seed | 1 |
| policy_evidence_source_seed | 1 |
| rysxai_profession_seed | 2 |
| rysxai_university_seed | 1 |

## Official-Site Seed Years

| year | seed_rows |
|---|---:|
|  | 3 |
| 2014 | 1 |
| 2017 | 5 |
| 2018 | 3 |
| 2019 | 1 |
| 2020 | 4 |
| 2021 | 5 |
| 2022 | 4 |
| 2023 | 9 |
| 2024 | 47 |
| 2025 | 283 |
| 2026 | 2470 |

## Outputs

- `data/processed/reference_seed_inventory/reference_seed_file_manifest_2026.csv`
- `data/processed/reference_seed_inventory/reference_seed_official_site_sources_2026.csv`
- `data/processed/reference_seed_inventory/reference_seed_official_site_unique_sources_2026.csv`
- `data/processed/reference_seed_inventory/reference_seed_rysxai_profession_summary_2026.csv`
- `data/processed/reference_seed_inventory/reference_seed_rysxai_university_summary_2026.csv`
- `data/processed/reference_seed_inventory/reference_seed_policy_sources_2026.csv`
- `data/processed/reference_seed_inventory/reference_seed_policy_source_summary_2026.csv`

## Notes

- This package preserves all `data/seeds` files and adds normalized inventories for reproducible crawling.
- Official-site seed rows are source URLs and metadata only; person-level extracted records are not included here.
- RYSXAI profession and university seeds are third-party entity dimensions used for joins and should not be treated as official Ministry catalog truth.
