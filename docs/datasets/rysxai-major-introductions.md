# Rysxai Major Introduction Support Dataset

This support dataset turns the full rysxai major-introduction crawl into
risk-linkable profile rows. It is a source-level C dataset and is kept separate
from official employment-warning and official professional-setting records.

## Scope

The source crawl covers 1,653 major profiles captured from the rysxai
`profession/info` public API on 2026-06-11. Each profile keeps major code,
major name, education level, degree, study duration, selection advice,
enrollment scale, university count, application-plan ratio, major introduction
text, course text, undergraduate-to-graduate transition text, and similar-major
text.

The derived risk-link profile table adds exact links to:

- red/yellow/green employment-warning records;
- official professional-setting risk records, including cancellation and
  stop-enrollment rows;
- the source-level C AI replacement-risk ranking.

## Outputs

| File | Purpose |
|---|---|
| `data/processed/rysxai_major_intros/major_introductions_full_20260611_intro.csv` | Flat source-level profile text table from the full crawl. |
| `data/processed/rysxai_major_intros/major_introductions_full_20260611_intro.jsonl` | Same source profiles with nested source metadata and section labels. |
| `data/processed/rysxai_major_intros/major_intro_risk_profiles_20260611.csv` | Risk-linkable profile table with section completeness, source digests, warning/policy links, and AI-risk links. |
| `data/processed/rysxai_major_intros/major_intro_risk_profile_summary_20260611.csv` | Level-level summary for profile coverage and risk linkage. |
| `data/processed/rysxai_major_intros/major_intro_risk_profiles_manifest_20260611.json` | Build manifest with counts and linkage coverage. |
| `reports/rysxai_major_intros/major_intro_risk_profiles_20260611.md` | Human-readable build report. |

## Current Counts

| Metric | Count |
|---|---:|
| Input/output profiles | 1,653 |
| Undergraduate profiles | 882 |
| Associate/vocational profiles | 771 |
| Profiles linked to employment warnings | 147 |
| Profiles linked to red/yellow employment warnings | 84 |
| Profiles linked to official policy risk rows | 564 |
| Profiles linked to AI replacement-risk profiles | 1,613 |
| Missing major-detail sections | 1 |
| Missing course sections | 1 |
| Missing undergraduate-to-graduate sections | 114 |

## Key Fields

| Field | Meaning |
|---|---|
| `profile_id` | Stable hash ID for profession id, code, name, and level. |
| `rysxai_profession_id` | Source profession id used for raw API and snapshot lookup. |
| `major_code`, `major_name`, `level` | Source major identity fields. |
| `has_major_detail`, `has_major_course`, `has_undergraduate_to_graduate`, `has_similar_majors` | Section completeness flags. |
| `content_sha256` | Digest of the four long text sections for change tracking. |
| `employment_warning_*` | Exact code/name matches to red/yellow/green employment-warning rows. |
| `official_policy_*` | Exact code/name matches to official cancellation, stop-enrollment, warning-list, or controlled-major policy rows. |
| `ai_replacement_*` | Matched source-level C AI replacement-risk score and rank. |
| `source_snapshot_path`, `raw_source_path` | Local paths for normalized snapshot and raw API payload verification. |

## Packaging

| Package | Purpose |
|---|---|
| `outputs/rysxai_major_introductions_dataset_20260612.zip` | Processed profile files, report, docs, source module, CLI wrapper, and tests. |
| `outputs/rysxai_major_introductions_raw_sources_20260612.zip` | Raw rysxai introduction API payloads, normalized per-major snapshots, aggregate source files, and crawl logs. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |

## Caveats

- `source_level=C` means this is a non-official support source. It is suitable
  for retrieval, text feature extraction, review sampling, and context
  enrichment.
- It must not be used as official employment-warning evidence, an official
  Ministry professional-setting decision, or a deterministic prediction.
- Long text fields can be large. Use the risk-link profile table for analytics
  and the JSONL/snapshot files for detailed retrieval.
