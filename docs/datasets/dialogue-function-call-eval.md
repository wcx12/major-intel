# Dialogue Function-Call Eval Support Dataset

## Scope

This support dataset packages the committed `datasets/dialogue/claude_full`
snapshot and derived summary tables for evaluating admission-consulting
question understanding, slot coverage, and function-call routing.

It is not an official admissions, employment, salary, policy, or school-major
fact source. The source dialogue material is public-ASR-derived and should be
used as an evaluation and retrieval-support corpus only.

## Snapshot Counts

| Asset | Rows |
|---|---:|
| ASR question candidates | 152 |
| Claude-cleaned dialogue records | 152 |
| Full question bank | 152 |
| Usable question bank | 34 |
| Function-call eval cases | 152 |
| Usable function-call eval cases | 34 |
| Mentor strategy records | 5 |
| Review queue records | 148 |
| Source inventory records | 6 |
| Question-family summary rows | 11 |
| Quality summary rows | 4 |
| Expected-tool summary rows | 17 |
| Source-inventory summary rows | 6 |

## Key Distributions

| Question family | Questions | Usable | Eval cases | Should clarify |
|---|---:|---:|---:|---:|
| `rank_to_school_match` | 36 | 6 | 36 | 35 |
| `major_profile` | 34 | 9 | 34 | 30 |
| `school_major_profile` | 19 | 4 | 19 | 19 |
| `employment_summary` | 19 | 1 | 19 | 19 |
| `comparison_query` | 16 | 6 | 16 | 16 |
| `transfer_policy_lookup` | 11 | 2 | 11 | 10 |
| `rank_to_major_match` | 6 | 2 | 6 | 5 |
| `major_market_reference` | 4 | 1 | 4 | 3 |
| `subject_requirement_lookup` | 3 | 2 | 3 | 2 |
| `score_to_rank` | 3 | 1 | 3 | 3 |
| `civil_service_role_search` | 1 | 0 | 1 | 1 |

Quality labels in the full question bank:

| Label | Questions | Usable | Average score |
|---|---:|---:|---:|
| A | 4 | 4 | 0.8500 |
| B | 30 | 30 | 0.6967 |
| C | 51 | 0 | 0.4771 |
| D | 67 | 0 | 0.2204 |

## Files

Formal snapshot files:

| File | Purpose |
|---|---|
| `datasets/dialogue/claude_full/asr_question_candidates.jsonl` | Raw public-ASR question candidates and response snippets. |
| `datasets/dialogue/claude_full/llm_cleaned_dialogues.jsonl` | Full cleaned dialogue records with question family, slots, tools, strategy, and quality labels. |
| `datasets/dialogue/claude_full/question_bank.jsonl` | Full 152-row evaluation question bank. |
| `datasets/dialogue/claude_full/usable_question_bank.jsonl` | 34 higher-confidence questions suitable for direct regression tests. |
| `datasets/dialogue/claude_full/function_call_eval_cases.jsonl` | Full function-call routing eval cases. |
| `datasets/dialogue/claude_full/usable_function_call_eval_cases.jsonl` | Higher-confidence eval-case subset. |
| `datasets/dialogue/claude_full/mentor_strategy_bank.jsonl` | Strategy summaries for response planning; not ground-truth facts. |
| `datasets/dialogue/claude_full/source_inventory.json` | Source repository, license, and usage-boundary inventory. |
| `datasets/dialogue/claude_full/review_queue.jsonl` | Records needing human review before product-facing use. |

Derived summary files:

| File | Purpose |
|---|---|
| `data/processed/dialogue_function_call_eval/dialogue_question_family_summary_2026.csv` | Counts by question family, usable subset, eval cases, and clarification expectation. |
| `data/processed/dialogue_function_call_eval/dialogue_quality_summary_2026.csv` | Counts by quality label. |
| `data/processed/dialogue_function_call_eval/dialogue_expected_tool_summary_2026.csv` | Expected tool coverage across questions and eval cases. |
| `data/processed/dialogue_function_call_eval/dialogue_source_inventory_summary_2026.csv` | Flat source inventory for package review. |
| `data/processed/dialogue_function_call_eval/dialogue_eval_manifest_2026.json` | Row counts, distributions, checksums, and usage limits. |

## Source Boundaries

The main dialogue source is the public `Xue-Feng-Skill` ASR transcript corpus.
Additional community repositories are used only as strategy or style references
and are marked in `source_inventory.json`.

Do not use this dataset to assert factual claims about:

- school admission probability
- score lines or rank thresholds
- employment outcomes or salary levels
- official major setup, withdrawal, or policy changes
- civil-service recruitment eligibility

For those claims, use the official and market evidence packages in this
repository and retain source attribution.

## Rebuild

Regenerate the formal dialogue snapshot:

```powershell
python scripts/datasets/build_dialogue_assets.py --output-dir datasets/dialogue/claude_full
```

Regenerate the derived summaries:

```powershell
python scripts/datasets/build_dialogue_eval_summary.py --generated-at 2026-06-14
```

## Packages

| Package | Purpose |
|---|---|
| `outputs/dialogue_function_call_eval_dataset_20260612.zip` | Dialogue snapshot, derived summary tables, docs, report, scripts, source module, and tests. |
| `outputs/major_risk_warnings_full_dataset_20260612.zip` | Combined processed package including this support dataset. |
| `outputs/major_risk_warnings_package_manifest_20260612.json` | Package sizes, SHA-256 checksums, zip entry counts, and zip validation status. |
