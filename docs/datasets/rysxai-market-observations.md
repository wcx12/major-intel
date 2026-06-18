# RYSXAI Major Market Observation Support Dataset

This support dataset structures local rysxai major-market snapshots into
analysis-ready tables for major risk screening, retrieval, and feature
engineering.

The source is a third-party public API snapshot and is marked `source_level=C`.
It is useful for market observation, but it is not official school-major
graduate outcome evidence.

## Scope

The build uses:

- 1,616 local normalized market snapshots from `data/processed/rysxai`;
- 3,242 raw rysxai API payloads under `data/raw/rysxai`;
- the local rysxai profession seed table for category/subject metadata;
- major-risk employment warning and official policy-warning tables;
- AI replacement-risk profiles;
- civil-service opportunity profiles;
- transfer-policy major-mention profiles.

The derived tables preserve source-level caveats and keep the recruiting sample
fields limited to job/company/market attributes. Recruiter personal fields are
not included.

## Outputs

| File | Purpose |
|---|---|
| `data/processed/rysxai_market/market_major_profiles_2026.csv` | One row per crawled major with demand, salary, job-sample, distribution, risk-link, civil-service, and transfer-policy features. |
| `data/processed/rysxai_market/market_job_samples_2026.csv` | Safe recruiting job samples with job title, company, city, industry, salary range, education, experience, skills, and company tags. |
| `data/processed/rysxai_market/market_city_salary_2026.csv` | Per-major city salary aggregates derived from job samples. |
| `data/processed/rysxai_market/market_macro_distributions_2026.csv` | Long table for industry, region, and job-direction distributions. |
| `data/processed/rysxai_market/market_rankings_2026.csv` | Long table for demand and salary ranking observations. |
| `data/processed/rysxai_market/market_skill_summary_2026.csv` | Per-major skill frequency summaries from job samples. |
| `data/processed/rysxai_market/market_profile_summary_2026.csv` | Summary by all, level, category, and subject. |
| `data/processed/rysxai_market/market_observations_manifest_2026.json` | Build manifest with row counts and linkage coverage. |
| `reports/rysxai_market/market_observations_2026.md` | Human-readable build report. |

## Current Counts

| Metric | Count |
|---|---:|
| Snapshot files | 1,616 |
| Major market profiles | 1,616 |
| Job sample rows | 6,814 |
| City salary rows | 6,459 |
| Macro distribution rows | 39,659 |
| Ranking rows | 33,414 |
| Skill summary rows | 28,492 |
| Summary rows | 214 |
| Profiles linked to red/yellow employment warnings | 84 |
| Profiles linked to official policy risk rows | 564 |
| Profiles linked to medium-or-higher AI risk | 238 |
| Profiles linked to civil-service opportunity rows | 1,090 |
| Profiles linked to transfer-policy mentions | 806 |

## Key Fields

| Field | Meaning |
|---|---|
| `market_profile_id` | Stable hash ID for profession id, code, name, and level. |
| `rysxai_profession_id` | Source profession id used to locate raw API payloads and normalized snapshots. |
| `major_code`, `major_name`, `level`, `category`, `subject` | Major identity fields. |
| `demand_count_national`, `salary_reference_national` | Source ranking signals for national demand and salary reference where present. |
| `job_posting_sample_*` | Reported and retained recruiting sample counts. |
| `salary_sample_*` | Salary range summaries derived from retained recruiting samples. |
| `market_*_signal_level` | Percentile-based labels within this snapshot set: `very_high`, `high`, `medium`, `limited`, or `unknown`. |
| `top_industries`, `top_regions`, `top_job_directions` | Compact top macro distribution labels and rates. |
| `top_job_titles`, `top_skills`, `top_job_cities` | Compact top recruiting-sample features. |
| `employment_warning_*` | Links to red/yellow/green employment-warning rows. |
| `official_policy_*` | Links to official professional-setting risk rows. |
| `ai_replacement_*` | Matched source-level C AI replacement-risk score and rank. |
| `civil_service_*` | Matched civil-service opportunity signals. |
| `transfer_policy_*` | Matched transfer-policy text-mention signals. |
| `source_snapshot_path` | Local normalized snapshot path for audit. |

## Packaging

| Package | Purpose |
|---|---|
| `outputs/rysxai_market_observations_dataset_20260612.zip` | Processed market tables, report, docs, source module, CLI wrapper, crawler/report modules, and tests. |
| `outputs/rysxai_market_raw_sources_20260612.zip` | Raw rysxai market API payloads, normalized per-major snapshots, crawl logs, and market crawler spec. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- `source_level=C` means the dataset is a non-official support source.
- Demand, salary, and job samples are market observations, not official graduate
  destination or salary facts for any specific school-major combination.
- Company names and job attributes are retained for market analysis; recruiter
  personal fields are excluded.
- Percentile signal labels are relative to the crawled snapshot set and should
  not be interpreted as external national rankings.
