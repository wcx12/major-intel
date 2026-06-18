# Major AI Replacement Risk Dataset

This support dataset adds a non-official market-risk dimension to the major-risk
data package. It uses already crawled rysxai Chinese recruiting-market snapshots
and transparent heuristic scoring to rank majors by AI replacement exposure.

It is intentionally separate from the official red/yellow/green employment
warnings and official policy controls. Its `source_level` is `C`.

## Source

- Source snapshots: `data/processed/rysxai/*.json`
- Raw API payloads: `data/raw/rysxai/`
- Full market crawl manifests:
  - `data/logs/rysxai/full_benke_20260519_manifest.json`
  - `data/logs/rysxai/full_zhuanke_20260519_manifest.json`
- Rebuild script: `python scripts/datasets/build_ai_replacement_dataset.py`

The source crawl covers 845 undergraduate professions and 771 specialist /
associate professions. The final normalized input directory contains 1,616
market snapshots.

## Files

| File | Rows | Purpose |
|---|---:|---|
| `data/processed/ai_replacement/major_ai_replacement_ranking.csv` | 1,612 | Major-level AI replacement risk ranking. |
| `data/processed/ai_replacement/major_ai_replacement_top100.csv` | 100 | Top 100 higher-risk majors. |
| `data/processed/ai_replacement/risk_level_summary.csv` | 15 | Risk-level counts by major level. |
| `data/processed/ai_replacement/major_ai_replacement_ranking.jsonl` | 1,612 | Ranking with nested job evidence. |
| `data/processed/ai_replacement/major_job_candidates.csv` | 65,473 | Major-job candidate evidence and job-level risk scores. |
| `data/processed/ai_replacement/job_ai_risk_seed.csv` | 18,248 | Normalized job-title AI risk seed scores. |
| `data/processed/ai_replacement/manifest.json` | 1 | Build manifest. |
| `reports/ai_replacement/major_ai_replacement_summary.md` | 1 | Human-readable ranking summary. |

## Risk Distribution

| Risk level | Majors |
|---|---:|
| 很高 | 0 |
| 较高 | 10 |
| 中等 | 221 |
| 较低 | 1,325 |
| 低 | 56 |

By major level:

- 本科：844
- 专科：768

## Main Fields

| Field | Meaning |
|---|---|
| `rank` | Rank by `ai_replacement_score`, descending. |
| `major_code` / `major_name` / `level` | Major identity and level. |
| `ai_replacement_score` | Aggregated major-level AI replacement risk score. |
| `ai_replacement_level` | Risk bucket: `很高`, `较高`, `中等`, `较低`, or `低`. |
| `ai_exposure_score` | How much common work is exposed to AI assistance/automation. |
| `automation_score` | Likelihood that common tasks can be independently automated. |
| `human_barrier_score` | Maximum of physical, license, trust, and liability barriers. |
| `ai_assist_value_score` | Value of AI as an assistant, independent of full replacement risk. |
| `confidence_score` | Confidence from candidate coverage, evidence count, scoring rules, and source fields. |
| `top_risky_jobs` | Job titles contributing most to risk score. |
| `top_resilient_jobs` | Job titles with lower replacement risk or stronger barriers. |
| `main_reasons` | Human-readable risk rationale. |
| `source_level` | `C`, third-party recruiting-market observation. |
| `warning` | Required usage caveat. |

## Scoring Scope

The scoring model is rule-based and transparent:

```text
major AI replacement risk = weighted average(job risk)
job risk = automation_score * (1 - 0.0065 * max_barrier_score) + ai_exposure_score * 0.15
max_barrier_score = max(physical_barrier, license_barrier, trust_barrier, liability_barrier)
```

Use this dataset for ranking, sampling, and follow-up review. Do not use it as
an official employment outcome, school-major employment guarantee, or
deterministic career prediction.

## Packages

| Package | Purpose |
|---|---|
| `outputs/major_ai_replacement_dataset_20260612.zip` | Processed AI replacement-risk files, report, docs, and script. |
| `outputs/major_ai_replacement_source_snapshots_20260612.zip` | rysxai raw API payloads, normalized market snapshots, and crawl logs. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined package with core risk warnings and all support datasets built in this pass. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |
