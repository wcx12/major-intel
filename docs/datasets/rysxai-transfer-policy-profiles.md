# RYSXAI Transfer Policy Profile Support Dataset

This support dataset structures the crawled rysxai school transfer-major policy
table into school, faculty, and major-mention profiles.

The source is a third-party compiled policy dataset and is marked
`source_level=C`. It is useful for screening transfer-major flexibility,
restrictions, and review targets. It should not replace current official school
policy notices for high-stakes decisions.

## Scope

The build uses:

- 2,948 school policy rows from `data/processed/rysxai_transfer_policies.csv`;
- 1,653 local rysxai major seed rows;
- the major-risk warning tables for red/yellow/green and official policy links;
- the AI replacement-risk support table for non-official AI-risk links.

The source keeps the original long policy text and faculty-policy JSON. The
derived tables extract keyword flags and text mentions while preserving
source-level caveats.

## Outputs

| File | Purpose |
|---|---|
| `data/processed/rysxai_transfer_policies/transfer_policy_school_profiles_2026.csv` | One row per school with policy availability, section lengths, keyword flags, heuristic difficulty score, major-mention counts, and risk links. |
| `data/processed/rysxai_transfer_policies/transfer_policy_faculty_profiles_2026.csv` | One row per faculty/department policy block exposed by the source JSON. |
| `data/processed/rysxai_transfer_policies/transfer_policy_major_mentions_2026.csv` | One row per local major seed summarizing school/faculty policy-text mentions and risk links. |
| `data/processed/rysxai_transfer_policies/transfer_policy_profile_summary_2026.csv` | Summary by all schools, province, school type, property, and level. |
| `data/processed/rysxai_transfer_policies/transfer_policy_profiles_manifest_2026.json` | Build manifest with row counts and linkage counts. |
| `reports/rysxai_transfer_policies/transfer_policy_profiles_2026.md` | Human-readable build report. |

## Current Counts

| Metric | Count |
|---|---:|
| Input school rows | 2,948 |
| School profile rows | 2,948 |
| Faculty profile rows | 2,386 |
| Local major seed rows | 1,653 |
| Major mention rows | 1,653 |
| Mentioned majors | 815 |
| Summary rows | 55 |
| Mentioned majors linked to red/yellow employment warnings | 76 |
| Mentioned majors linked to official policy rows | 468 |
| Mentioned majors linked to AI replacement-risk rows | 805 |

## Key Fields

| Field | Meaning |
|---|---|
| `has_transfer_policy`, `has_faculty_policy` | Whether the source exposed school-level or faculty-level policy text. |
| `faculty_policy_count` | Number of faculty blocks in the source JSON. |
| `*_chars`, `total_policy_chars` | Text-length indicators for source sections. |
| `has_gpa_requirement`, `has_rank_requirement` | Whether policy text contains GPA/ranking-style requirements. |
| `has_exam_requirement`, `has_interview_requirement` | Whether policy text contains written-test/interview/assessment signals. |
| `has_quota_limit` | Whether policy text contains quota, plan, or proportion limit signals. |
| `has_major_restriction`, `has_special_enrollment_restriction` | Whether policy text contains no-transfer/special-enrollment restriction signals. |
| `has_physical_requirement`, `has_penalty_restriction` | Whether policy text contains physical-condition or discipline-status signals. |
| `transfer_difficulty_score` | Transparent heuristic score from policy length, faculty-policy count, and keyword flags. |
| `transfer_difficulty_level` | `permissive`, `moderate`, `restrictive`, `very_restrictive`, or `unknown`. |
| `mentioned_*` fields | Text-mention counts for local major names and linked risk dimensions. |

## Packaging

| Package | Purpose |
|---|---|
| `outputs/rysxai_transfer_policy_profiles_dataset_20260612.zip` | Processed source table, school/faculty/major profiles, report, docs, scripts, and tests. |
| `outputs/rysxai_transfer_policy_raw_sources_20260612.zip` | Raw rysxai transfer-policy JSONL crawl and failure log if present. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |

## Caveats

- Difficulty score is heuristic and should be used for screening, not as an
  official school ranking.
- Major mentions are text matches. They do not prove that a major is open or
  closed for transfer at a specific school.
- Short major names such as chemistry can appear frequently in course or
  requirement descriptions; use samples and source text for review.
- Empty source fields mean the third-party API did not expose that section at
  crawl time, not that the official school has no policy.
