# New Quality Major Support Profile Dataset

This dataset packages the local new-quality-productivity major evaluation into
analysis-ready support tables and links each major back to the risk, policy,
AI, market, civil-service, and transfer-policy datasets built in this project.

It is an opportunity/support dataset, not a high-risk warning list. Official
policy evidence is treated as source-level B. The local rule labels, school
offering samples, and third-party market links are support-level evidence and
must remain auditable.

## Scope

The build uses:

- 2,053 local `edu_major` evaluation rows already exported to
  `outputs/new_quality_major_eval_20260613`;
- 8,212 tier-sample rows, one row per major per school tier where available;
- 33 policy source rows derived from the policy-evidence crawl;
- the major-risk warning, official policy-warning, AI replacement, rysxai
  market, civil-service, and transfer-policy support tables.

The source evaluation classifies majors as `core`, `related`, `weak_related`,
or `not_related` for new-quality-productivity policy relevance. This build adds
stable IDs, source-level fields, linked risk/opportunity dimensions, and group
summaries.

## Outputs

| File | Purpose |
|---|---|
| `data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv` | One row per local major with support label, policy directions, tier samples, and risk/opportunity linkage fields. |
| `data/processed/new_quality_major_profiles/new_quality_major_tier_samples_2026.csv` | Four-tier school sample rows for 清北, 985, 211, and 双非 where available. |
| `data/processed/new_quality_major_profiles/new_quality_policy_sources_2026.csv` | Policy source rows used by the new-quality-productivity direction rules. |
| `data/processed/new_quality_major_profiles/new_quality_major_profile_summary_2026.csv` | Summary by all, support category, label, confidence, major type/class, and direction. |
| `data/processed/new_quality_major_profiles/new_quality_major_profiles_manifest_2026.json` | Build manifest with counts and linkage coverage. |
| `reports/new_quality_major_profiles/new_quality_major_profiles_2026.md` | Human-readable build report. |
| `outputs/new_quality_major_eval_20260613/new_quality_major_evaluation.xlsx` | Existing reviewed workbook output retained in the package. |

## Current Counts

| Metric | Count |
|---|---:|
| Major profiles | 2,053 |
| Tier sample rows | 8,212 |
| Policy source rows | 33 |
| Summary rows | 238 |
| Core new-quality majors | 263 |
| Related majors | 400 |
| Weak-related majors | 470 |
| Not-related majors | 920 |
| High-confidence profiles | 263 |
| Medium-confidence profiles | 678 |
| Low-confidence profiles | 1,112 |
| Profiles linked to red/yellow employment warnings | 106 |
| Profiles linked to official policy risk rows | 634 |
| Profiles linked to AI replacement profiles | 1,779 |
| Profiles linked to rysxai market profiles | 1,783 |
| Profiles linked to civil-service opportunity rows | 1,233 |
| Profiles linked to transfer-policy mentions | 922 |

## Direction Coverage

| Direction | Profiles |
|---|---:|
| `artificial_intelligence` | 520 |
| `digital_economy` | 496 |
| `advanced_manufacturing` | 269 |
| `green_low_carbon` | 177 |
| `bio_manufacturing` | 158 |
| `commercial_space` | 148 |
| `low_altitude_economy` | 114 |
| `new_materials` | 110 |
| `integrated_circuit` | 68 |
| `future_industries` | 31 |
| `quantum_technology` | 24 |

## Key Fields

| Field | Meaning |
|---|---|
| `new_quality_profile_id` | Stable hash ID for local special id, code, name, and major type. |
| `support_category` | Normalized support label: `core`, `related`, `weak_related`, `not_related`, or `needs_review`. |
| `directions` | Semicolon-separated policy directions matched by the rule system. |
| `rule_score`, `confidence`, `rationale` | Auditable heuristic score, confidence label, and rule rationale. |
| `policy_source_ids`, `policy_evidence_excerpt` | Policy evidence links and short excerpts. |
| `sample_coverage` | Number of school-tier samples found out of four tiers. |
| `employment_warning_*` | Links to red/yellow/green employment-warning rows. |
| `official_policy_*` | Links to official professional-setting risk rows. |
| `ai_replacement_*` | Matched source-level C AI replacement-risk score and rank. |
| `market_*` | Matched rysxai market demand, salary, and activity signals. |
| `civil_service_*` | Matched civil-service opportunity signals. |
| `transfer_policy_*` | Matched transfer-policy text-mention signals. |
| `opportunity_risk_balance` | Compact review bucket for policy support versus observed risk flags. |

## Packaging

| Package | Purpose |
|---|---|
| `outputs/new_quality_major_profiles_dataset_20260612.zip` | Processed profiles, tier samples, policy sources, summary, manifest, report, docs, workbook, source scripts, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- This dataset should be used as an opportunity and policy-support dimension,
  not as an employment outcome or admission recommendation.
- A major can be policy-supported and still carry employment, official-policy,
  or AI-risk flags. Use the linked fields and source IDs for review.
- School-tier samples come from the local `edu_school_major` and
  `edu_university` database export used to create the source workbook; missing
  samples mean no local sample was found in that export.
- Direction labels are rule-based and should be reviewed before public-facing
  deterministic claims.
