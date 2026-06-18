# RYSXAI Civil-Service Major Opportunity Support Dataset

This support dataset turns the crawled 2026 civil-service role table into
major-level opportunity and competition profiles.

The source is a rysxai third-party API mirror of civil-service role details.
It is marked `source_level=C`. The derived tables are useful for screening and
ranking, but a matched row is only a textual eligibility clue. Final
application eligibility still requires the official role table and current
exam notice.

## Scope

The build uses:

- 20,714 crawled 2026 role rows from `data/processed/rysxai_civil_service_2026.csv`;
- 1,653 local rysxai major seed rows;
- the major-risk warning tables for red/yellow/green and official policy links;
- the AI replacement-risk support table for non-official AI-risk links.

Professional requirements are parsed conservatively:

- six-digit major codes and exact major names are marked `exact`;
- four-digit/two-digit code prefixes, major-class names, and documented aliases
  are marked `broad`;
- unmatched professional terms are kept in a review table.

## Outputs

| File | Purpose |
|---|---|
| `data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv` | One row per local major seed with role counts, plan counts, competition ratios, restriction counts, region/department samples, and risk links. |
| `data/processed/rysxai_civil_service/civil_service_role_match_summary_2026.csv` | One row per civil-service role with parsed major count, matched categories/subjects, restriction flags, and unmatched terms. |
| `data/processed/rysxai_civil_service/civil_service_role_major_matches_2026.csv` | Role-major bridge table with exact/broad match scope and matched terms. |
| `data/processed/rysxai_civil_service/civil_service_unmatched_profession_terms_2026.csv` | Unmatched professional requirement terms ranked by role count. |
| `data/processed/rysxai_civil_service/civil_service_major_opportunities_manifest_2026.json` | Build manifest with row counts and linkage counts. |
| `reports/rysxai_civil_service/civil_service_major_opportunities_2026.md` | Human-readable build report. |

## Current Counts

| Metric | Count |
|---|---:|
| Input role rows | 20,714 |
| Roles with at least one major match | 20,550 |
| Unmatched role rows | 164 |
| Local major seed rows | 1,653 |
| Major opportunity rows | 1,653 |
| Majors with at least one role match | 1,110 |
| Role-major match rows | 888,025 |
| Unmatched professional terms | 1,003 |
| Majors linked to employment warnings | 146 |
| Majors linked to red/yellow employment warnings | 83 |
| Majors linked to official policy rows | 560 |
| Majors linked to AI replacement-risk rows | 1,613 |

## Key Fields

| Field | Meaning |
|---|---|
| `role_match_count` | Number of civil-service role rows matched to the major. |
| `exact_role_match_count` | Matches from exact six-digit major code or exact major name. |
| `broad_role_match_count` | Matches from code prefix, major-class term, or documented alias. |
| `plan_num_sum`, `apply_num_sum` | Summed planned hires and applicants over matched roles. |
| `weighted_competition_ratio` | `apply_num_sum / plan_num_sum` when planned hires are available. |
| `avg_competition_ratio`, `median_competition_ratio` | Role-level competition-ratio summaries. |
| `low_restriction_role_count` | Roles where identity, work-year, and service-project experience fields are all unrestricted in the source table. |
| `central_role_count`, `provincial_role_count`, `city_role_count`, `county_or_below_role_count` | Department-level distribution. |
| `need_test_role_count`, `party_member_role_count`, `new_graduate_role_count` | Restriction and applicant-type indicators. |
| `employment_warning_*`, `official_policy_*`, `ai_replacement_*` | Exact major-name links back to the broader risk-warning support tables. |

## Packaging

| Package | Purpose |
|---|---|
| `outputs/rysxai_civil_service_major_opportunities_dataset_20260612.zip` | Processed source table, derived opportunity tables, report, docs, scripts, and tests. |
| `outputs/rysxai_civil_service_raw_sources_20260612.zip` | Raw rysxai civil-service JSONL crawl and failure log if present. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |

## Caveats

- This is not an official eligibility engine.
- Graduate major codes in role text may not have a matching undergraduate or
  vocational seed row; unmatched terms are retained for review.
- Broad matches can intentionally expand one role into many majors.
- Competition ratios reflect the crawled source table at capture time and may
  change if the source updates.
