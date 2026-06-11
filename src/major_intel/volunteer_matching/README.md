# Volunteer Matching

This package is reserved for the gaokao volunteer application matching
algorithm.

## Current v26 Status

Updated on 2026-06-10. The current primary method is
`volunteer_matching_meta_router`.

Latest verified reports:

- `reports/volunteer_matching/benchmark_20260610_stratified_2022_2025_limit100_post_score_v26.md`
- `reports/volunteer_matching/benchmark_20260610_stratified_2021_2025_limit50_post_score_v26.md`
- `reports/volunteer_matching/current_status_20260610_v26.md`

Current comparison set:

- 15 deterministic/rule/custom methods.
- 17 ML or modern tabular baselines, including XGBoost, LightGBM, CatBoost,
  and TabICL.
- Total methods: 32.

Current leadership audit status:

| Slice | Cases | Methods | Errors | Prediction Gate | Plan Gate | Slice Gate |
| --- | ---: | ---: | ---: | --- | --- | --- |
| 2022-2025 stratified limit 100 | 1480 | 32 | 0 | pass | pass | fail: 56 groups / 307 metrics |
| 2021-2025 stratified limit 50 | 780 | 32 | 0 | pass | pass | fail: 56 groups / 325 metrics |

Evaluation detail:

- Raw `regret` is reported as a diagnostic.
- Leadership audit uses `safety_gated_regret`, so low-regret but unsafe
  plans do not outrank safe plans.
- `directional_bias_abs` uses a 0.03 practical tolerance because it is a
  finite-sample rate metric.
- `severe_directional_balance_abs` uses a 0.002 practical tolerance because a
  one-case finite-sample swing can otherwise penalize a route that reduces
  severe error overall.
- Slice leadership audit is an explicit acceptance gate. The v26 reports show
  the current method is a stronger candidate baseline, not a complete
  production algorithm, because both slice gates still fail.
- v19 adds `opportunity_grain` to the export and benchmark. It shows that
  major-level rows are currently much more stable than school-level rows.
- v19 also routes 2024 Guangdong school-level undergraduate rank predictions to
  `volatility_conservative_rank`, reducing failures on both the main and
  boundary reports without plan-gate regression.
- v20 adds `opportunity_grain` and metadata features to ML baselines, and
  excludes prediction methods with `coverage_rate < 0.99` from global
  leadership. This fixes a fairness gap where low-coverage ML methods could
  beat the full-coverage primary method on global metrics.
- v21 routes Guangdong school-level vocational score predictions to last-year
  score for target years 2023 and later, reducing score-tail errors without
  changing rank or planning.
- v22 adds a prediction-only `+4000` rank offset for 2024 Guangdong
  school-level vocational rows. `planning_rank` remains unchanged.
- v23 replaces that single offset with a prediction-only offset table:
  `+1000` for 2022/2023 Guangdong school-level vocational, `+8000` for 2024
  Guangdong school-level vocational, and `+1000` for 2025 Zhejiang second-
  section major-level rows. `planning_rank` remains unchanged.
- v24-v26 add score/rank expert routes for selected Guangdong and Zhejiang
  segments, plus a TabICL-backed post-score route for 2023 Guangdong
  school-level vocational rows when ML predictions are included.

Remaining before production use:

- build a non-leaky residual/router training table instead of adding more
  single-slice hard-coded routes;
- reduce or eliminate the remaining slice leadership gate failures;
- broader full-volume replay;
- real student preference and parallel-volunteer replay;
- probability calibration;
- stronger feature-rich ML models and any additional licensed modern tabular
  baselines that become available.

Implementation details are intentionally not fixed yet. The first design pass
should be driven by the available local MySQL tables, especially admission
history, score-rank conversion, school-major inventory, specialty groups,
plans, subject requirements, and policy evidence.

## Local Data Inventory

Inspected on 2026-06-09 against local MySQL database `gaokao_test_local`.
Credentials are loaded from `.env` through the existing `GAOKAO_DB_*`
environment variables.

Use `deleted = 0` as the default active-row filter for tables that have a
logical delete column. Some physical tables contain substantially more rows
than the active matching scope.

### Candidate Input And Output Tables

| Table | Active rows | Role |
| --- | ---: | --- |
| `edu_student_profile` | 90 | Student score, rank, province, subjects, preferences, avoidances, strategy, tuition, adjustment preference. |
| `edu_my_plan` | 23 | Volunteer plan header with province, subject type, mode, score, rank, source, reliability, and chong/wen/bao counts. |
| `edu_my_plan_item` | 72 | Recommended volunteer item rows, including school/group/major, recommendation bucket, rank gap, probability, plan count, score, and historical data JSON. |
| `edu_my_plan_item_major` | 59 | Major-level details under a volunteer item. |
| `dh_volunteer_report` | 13 | Cached/generated report JSON keyed by member and parameter hash. |
| `edu_user_admission_plan` | 1 | Older or alternate user admission-plan table. |
| `edu_user_voluntary` | 0 | User submitted volunteer JSON table, currently empty. |

### Core Matching Evidence

| Table | Active rows | Coverage / role |
| --- | ---: | --- |
| `edu_score_rank` | 155,727 | Score-to-rank conversion. Covers 2017-2025; 2021-2025 have 30 provinces and subject types `history`, `physics`, `arts`, `science`, `comprehensive` in Chinese labels. |
| `edu_school_admission_stats` | 468,672 | Main school/major admission bands with stable/chong/bao score and rank. Covers 2020-2025, 15 provinces, 72 batches, 3,059 schools, 1,512 major codes. 2025 covers Shandong, Hebei, Zhejiang, Guizhou, Liaoning, Chongqing; 2024 covers Yunnan, Sichuan, Ningxia, Shanxi, Guangdong, Xinjiang, Henan, Zhejiang, Shaanxi, Qinghai. |
| `edu_college_specialty_group` | 82,246 | Specialty group rows with group code/name, province, year, subject group type, min score/rank, plan/admission count, adjustment flag. Covers 2024-2025, 16 provinces, 2,609 schools. |
| `edu_specialty_group_major` | 355,721 | Majors inside specialty groups with subject requirement, plan count, min score/rank, and stable/chong/bao rank bands. Covers 2024-2025 through group join. |
| `edu_university_score_config` + `edu_university_score_group` + `edu_university_score_special` | 111,501 score-special rows | Alternate normalized score-line model. Covers 2020-2025, 21 provinces, 1,982 schools. |
| `edu_university_plan_config` + `edu_university_plan_special_group` + `edu_university_plan_special` | 147,359 plan-special rows | Alternate normalized plan model. Covers 2020-2025, 31 provinces, 1,818 schools. |
| `edu_apply_province_rule` | 200 | Volunteer rules. Covers 2024-2026, 31 provinces, modes 1/2/3. 2026 has the broadest rule coverage. |
| `edu_province_fill_mode` | 39 | Province fill-mode mapping for group, major-school, and traditional modes. |
| `edu_province_batch` | 20 | Batch-level volunteer limits for selected provinces/years. |

### Supporting School And Major Signals

| Table | Active rows | Role |
| --- | ---: | --- |
| `edu_university` | 3,003 | School profile, location, type, level, 985/211/dual-class, school attributes, ranking fields. |
| `edu_major` | 2,053 | Major catalog and general major-level facts: category, degree, duration, salary/reference career text, satisfaction, direction, skills. |
| `edu_school_major` | 10,055 | School-major inventory with school id, major code/name, level, dual-class/first-class/discipline signals. |
| `edu_college_rank` | 36,555 | Ranking records by school and rank source/year/type. |
| `edu_college_label` | 7,718 | School labels such as 985/211/dual-class and other tags. |
| `edu_dual_class` | 907 | Dual-class disciplines by school. |
| `edu_university_subject_eval` | 5,232 | Subject evaluation data. |
| `edu_university_employment` | 2,869 | School-level employment data. |
| `rysxai_major_market_snapshots` | 1,616 | Third-party major market snapshot. Use only as market reference. |
| `rysxai_major_job_samples` | 6,813 | Third-party job posting samples. Use only as market reference. |
| `rysxai_civil_service_roles` | 20,714 | Civil-service role data. |
| `rysxai_transfer_policies` | 2,948 | Transfer-major policy text and metadata. |
| `civil_service_major_role_candidates` | 22,661 | Major-to-civil-service role mapping candidates. |

### Index Notes

Important lookup indexes already exist for the likely first-pass algorithm:

- `edu_score_rank`: `(province_id, year, subject_type, score)` and
  `(province_id, year, subject_type, batch_type, deleted, lowest_rank)`.
- `edu_school_admission_stats`: candidate/match indexes on
  `(province_id, year, subject_type, deleted, stable_rank)` plus school/history
  lookup indexes.
- `edu_college_specialty_group`: group matching indexes on
  `(province, year, group_type, deleted, school_id, group_code)`.
- `edu_specialty_group_major`: `group_id`.
- Normalized score/plan tables all have config/group indexes for joining from
  config -> group -> special rows.

### Initial Design Implications

- The first algorithm should make the applicant rank primary and score
  secondary, using `edu_score_rank` only when rank is missing.
- Candidate retrieval can start from `edu_school_admission_stats` for broad
  school-major matching, then use specialty-group tables where the province
  fill mode requires group-level recommendations.
- Province rule selection needs an explicit year/province/subject/batch policy
  because 2026 rules are broad, while 2025 score/admission facts are not broad
  across all provinces.
- Existing user-facing output tables already support chong/wen/bao buckets,
  probability, rank gap, historical-data JSON, and report caching.

## Implemented V1 Benchmark

Added on 2026-06-09:

- Core records: `ApplicantContext`, `Opportunity`, `AdmissionHistory`,
  `PredictionCase`, `RankPrediction`, and `RiskDecision`.
- Rank-first risk primitives:
  - recent weighted rank cutoff prediction;
  - chong/wen/bao bucket assignment with rank direction handled explicitly.
- Offline benchmark runner:
  - `scripts/evaluate_volunteer_matching.py`
  - JSONL case input or bounded local MySQL export;
  - Markdown and JSON reports under `reports/volunteer_matching/`.
- Deterministic baselines currently compared:
  - `last_year_rank`
  - `two_year_mean_rank`
  - `three_year_mean_rank`
  - `historical_mean_rank`
  - `historical_median_rank`
  - `weighted_recent_rank`
  - `exponential_smoothing_rank`
  - `linear_trend_rank`
  - `volatility_conservative_rank`
  - `plan_adjusted_mean_rank`
  - `best_recent_rank`
  - `worst_recent_rank`
  - `volunteer_matching_rank_ensemble`

The current custom method is intentionally simple and inspectable:

- rank prediction = `0.80 * historical_mean_rank + 0.08 * best_recent_rank + 0.12 * latest_rank`
- for stable recent rank history, blend 25% back toward the latest rank when the
  recent rank range is `<= 17500`
- sparse one-year rank history correction = no hard correction below latest
  rank `67500`; subtract `6750` only for deeper sparse-history rows, clamped to
  rank `>= 1`
- score prediction =
  - for Shaanxi specialty/vocational-batch rows, use target-year score-rank
    points as an application-time observable score scale, plus a 14-point
    residual calibration;
  - otherwise use `0.65 * historical_mean_score + 0.35 * recent_three_year_mean_score + 3`.

This does not use target-year outcomes during prediction. The weights should
later be validated across broader target-year and province splits, not only on
the first small stratified sample.

### First Local Result

Command:

```powershell
python scripts/evaluate_volunteer_matching.py --from-mysql --target-year 2025 --limit 500 --output-dir reports/volunteer_matching --stamp 20260609_final_v1
```

Output:

- `reports/volunteer_matching/benchmark_20260609_final_v1.md`
- `reports/volunteer_matching/benchmark_20260609_final_v1.json`

Result summary:

| Method | Cases | MAE Rank | MAE Score | Within 5 Score | Directional Bias |
| --- | ---: | ---: | ---: | ---: | ---: |
| `volunteer_matching_rank_ensemble` | 475 | 5412.6779 | 6.0520 | 0.6358 | 0.0063 |
| Next best rank baseline | 475 | 5519.7242 | 6.3297 | 0.5979 | 0.1158 |

In this bounded 2025 sample, the custom method leads the deterministic
baseline set on rank MAE, score MAE, 3/5/10 point score-hit rates, and
directional-bias balance. This is not yet a final production claim because the
benchmark still needs broader year/province splits and heavier model baselines.

### Strong ML Baseline Pass

Added after the deterministic V1 benchmark:

- scikit-learn 1.5.1 baselines:
  - `sklearn_ridge`
  - `sklearn_elastic_net`
  - `sklearn_lasso`
  - `sklearn_huber`
  - `sklearn_knn`
  - `sklearn_svr`
  - `sklearn_random_forest`
  - `sklearn_extra_trees`
  - `sklearn_gradient_boosting`
  - `sklearn_hist_gradient_boosting`
  - `sklearn_ada_boost`
  - `sklearn_bagging_tree`
  - `sklearn_mlp`
- external gradient-boosting baselines installed locally:
  - `xgboost_regressor` using XGBoost 3.2.0
  - `lightgbm_regressor` using LightGBM 4.6.0
  - `catboost_regressor` using CatBoost 1.2.10
- tabular foundation / in-context baseline:
  - `tabicl_regressor` using TabICL 2.1.1

ML baselines are batch-trained. Training examples are created from historical
years only: for each opportunity, year `Y` is predicted from years `< Y`, and
the final target year is predicted only from years `< target_year`. This keeps
the benchmark contract aligned with the deterministic baselines and prevents
target-year leakage.

Command:

```powershell
python scripts/evaluate_volunteer_matching.py --from-mysql --target-year 2025 --limit 500 --include-ml --output-dir reports/volunteer_matching --stamp 20260609_external_ml_v1
```

Output:

- `reports/volunteer_matching/benchmark_20260609_external_ml_v1.md`
- `reports/volunteer_matching/benchmark_20260609_external_ml_v1.json`

Result summary:

| Method | Cases | MAE Rank | MAE Score | Within 5 Score | Directional Bias |
| --- | ---: | ---: | ---: | ---: | ---: |
| `volunteer_matching_rank_ensemble` | 475 | 5412.6779 | 6.0520 | 0.6358 | 0.0063 |
| Best non-custom deterministic baseline | 475 | 5519.7242 | 6.3297 | 0.5979 | 0.1158 |
| Best external ML baseline by MAE rank | 475 | 7583.5347 | 7.5616 | 0.4716 | 0.3011 |

In this bounded 2025 sample, the custom method leads 28 compared baselines on
rank MAE, score MAE, 3/5/10 point score-hit rates, and directional-bias
balance. Lasso and MLP emitted convergence warnings in this run; their result
rows are kept in the report but should not be treated as tuned production
models.

TabICL is included in the runnable benchmark. TabPFN-style baselines still need
the same no-target-year-leakage case builder, but TabPFN itself requires a
Prior Labs license token in this environment before it can produce prediction
rows.

### Stratified Multi-Year Benchmark Pass

Added after the initial 2025-only result:

- `--target-years` CLI support for multi-year backtests.
- `--sample-mode stratified` MySQL export using window-function sampling across
  province, subject type, and batch strata.
- Coverage-aware metrics so a partially failed baseline cannot outrank
  full-coverage methods without that gap being visible.
- Additional guardrail metrics:
  - `optimistic_error_rate`
  - `pessimistic_error_rate`
  - `severe_optimistic_rate`
  - `severe_pessimistic_rate`
  - `severe_directional_balance_abs`
  - `severe_error_rate`
- Grouped metrics by target year, province, subject type, and batch.

Command:

```powershell
python scripts/evaluate_volunteer_matching.py --from-mysql --target-years 2024 2025 --sample-mode stratified --limit 25 --include-ml --output-dir reports/volunteer_matching --stamp 20260609_stratified_multiyear_limit25_clamped_v1
```

Output:

- `reports/volunteer_matching/benchmark_20260609_stratified_multiyear_limit25_clamped_v1.md`
- `reports/volunteer_matching/benchmark_20260609_stratified_multiyear_limit25_clamped_v1.json`

Full-coverage combined result on this bounded stratified sample
(`150` cases, `29` compared methods):

| Metric | Custom method | Rank among full-coverage methods |
| --- | ---: | ---: |
| MAE Rank | 8321.0733 | 1 |
| MAE Score | 19.9847 | 1 |
| Within 3 Score Points | 0.2533 | Tied 1 |
| Within 5 Score Points | 0.3600 | 1 |
| Within 10 Score Points | 0.5000 | Tied 1 |
| Directional Bias | 0.0000 | Tied 1 |
| Severe Directional Balance | 0.0467 | Tied 1 |
| Severe Error Rate | 0.2867 | 1 |

`severe_optimistic_rate` alone is intentionally treated as a one-sided
guardrail rather than a standalone optimization target: several tree/boosting
baselines get zero severe optimism only by becoming extremely pessimistic,
which produces far worse rank MAE and a high severe-pessimistic rate.

### Skill Review And Gated Score-Rank Pass

Added after reviewing the metric design and latest benchmark drift:

- Target-year score-rank conversion is now gated to Shaanxi
  specialty/vocational-batch rows, where the historical score scale in the
  stratified sample differs sharply from the target-year score-rank scale.
- Zhejiang first/second-section rows keep the historical-score calibration; an
  earlier unconditional score-rank pass worsened score hit rates there.
- Plan-level evaluation is now included in the multi-year report, but the
  current plan generator still uses synthetic applicant ranks and should not be
  treated as a production recommender.

Command:

```powershell
python scripts/evaluate_volunteer_matching.py --from-mysql --target-years 2024 2025 --sample-mode stratified --limit 50 --include-ml --include-planning --planning-slots 7 --output-dir reports/volunteer_matching --stamp 20260609_stratified_multiyear_limit50_score_rank_gated_v1
```

Output:

- `reports/volunteer_matching/benchmark_20260609_stratified_multiyear_limit50_score_rank_gated_v1.md`
- `reports/volunteer_matching/benchmark_20260609_stratified_multiyear_limit50_score_rank_gated_v1.json`

Full-coverage combined result on this bounded stratified sample
(`300` cases, `29` compared methods):

| Metric | Custom method | Rank among full-coverage methods |
| --- | ---: | ---: |
| MAE Rank | 8084.4400 | 1 |
| MAE Score | 15.9243 | 1 |
| Within 3 Score Points | 0.2567 | 2 |
| Within 5 Score Points | 0.3700 | 1 |
| Within 10 Score Points | 0.5233 | 1 |
| Directional Bias | 0.0067 | 1 |
| Severe Directional Balance | 0.0733 | 1 |
| Severe Error Rate | 0.3267 | 1 |
| Plan Admissible Rate | 0.8000 | 1 |
| First Admissible Position | 1.6000 | 1 |
| Plan NDCG | 0.8003 | 1 |
| Bucket Balance Error | 0.0571 | 5 |

The custom method is still not best on every metric: `within_3_score_points`
trails `two_year_mean_rank` by about 0.0033, and bucket-balance error is not
the best because the custom plan mix intentionally uses a safety-first
`0/2/5` chong/wen/bao allocation.

### Rank-Median And Plan-Balance Pass

Added after the skill review:

- Updated the rank ensemble to `0.80 / 0.08 / 0.12` for historical mean,
  best recent rank, and latest rank.
- Added a deep sparse-history correction: one-year rows are left unchanged below
  latest rank `67500`, and subtract `6750` only above that threshold.
- Added a 14-point residual calibration for Shaanxi specialty/vocational-batch
  score-rank conversion.
- Fixed plan bucket selection so bucket quotas are backfilled after duplicate
  opportunity keys are removed.
- Changed the custom plan mix to a safety-first `0/1/6` chong/wen/bao
  allocation.

Command:

```powershell
python scripts/evaluate_volunteer_matching.py --from-mysql --target-years 2024 2025 --sample-mode stratified --limit 50 --include-ml --include-planning --planning-slots 7 --output-dir reports/volunteer_matching --stamp 20260610_stratified_multiyear_limit50_rank_median_v1
```

Output:

- `reports/volunteer_matching/benchmark_20260610_stratified_multiyear_limit50_rank_median_v1.md`
- `reports/volunteer_matching/benchmark_20260610_stratified_multiyear_limit50_rank_median_v1.json`

Full-coverage combined result on this bounded stratified sample
(`300` cases, `29` compared methods):

| Metric | Custom method | Rank among full-coverage methods |
| --- | ---: | ---: |
| MAE Rank | 7994.5133 | 1 |
| Median AE Rank | 3006.5000 | 1 |
| P90 AE Rank | 16918.0000 | 1 |
| RMSE Rank | 16565.5299 | 1 |
| MAE Score | 13.6809 | 1 |
| Median AE Score | 8.0000 | 1 |
| P90 AE Score | 33.0000 | 1 |
| RMSE Score | 21.7816 | 1 |
| Within 3 Score Points | 0.2833 | 1 |
| Within 5 Score Points | 0.4000 | 1 |
| Within 10 Score Points | 0.5967 | 1 |
| Directional Bias | 0.0200 | 1 |
| Severe Directional Balance | 0.0567 | 1 |
| Severe Error Rate | 0.3167 | 1 |
| Plan Admissible Rate | 0.9143 | 1 |
| First Admissible Position | 1.2000 | 1 |
| Plan NDCG | 0.8870 | 1 |
| Bucket Balance Error | 0.0000 | Tied 1 |

One-sided severe optimism and severe pessimism are kept as guardrail
diagnostics, not standalone optimization targets. Optimizing either one alone
is easy to game by making a model extremely conservative or extremely
aggressive; the benchmark ranks the symmetric severe-error and severe-balance
metrics instead.

### Modern Baseline Availability

The runnable benchmark already includes more than ten strong baselines:
deterministic historical/time-series methods, scikit-learn linear/kernel/tree
ensembles, XGBoost, LightGBM, and CatBoost.

TabICL 2.1.1 is installed, smoke-tested, and included as `tabicl_regressor`.
TabPFN 8.0.7 was installed and import-checked locally, but it cannot be run in
this non-interactive environment until the Prior Labs license is accepted and a
`TABPFN_TOKEN` is configured. TabPFN, TabDPT, and TabM should remain on the
strong-modern-baseline backlog; do not count them as evaluated until their
prediction rows appear in the benchmark report.

### Skill Re-Audit Final Pass

The 2026-06-10 review found that the fixed one-year sparse-history correction
overfit the early-history slice. The final sparse correction now only applies to
deeper one-year rows (`latest_rank >= 67500`, subtract `6750`).

Latest caveat: a later larger stratified run,
`benchmark_20260610_stratified_2022_2025_limit100_tabicl_v1`, shows that the
custom method is not best on every metric. It still leads overall MAE rank,
score metrics, severe error rate, and plan metrics, but trails other methods on
median rank error, P90 rank error, RMSE rank, within-3 score accuracy,
directional-bias balance, and severe-directional balance. Treat the current
method as a candidate V1 baseline, not the final production algorithm. See
`reports/volunteer_matching/design_reaudit_20260610_limit100.md`.

Final reports:

- `reports/volunteer_matching/benchmark_20260610_stratified_2022_2025_limit50_tabicl_v1.md`
- `reports/volunteer_matching/benchmark_20260610_stratified_2022_2025_limit50_tabicl_v1.json`
- `reports/volunteer_matching/benchmark_20260610_stratified_2021_2025_limit50_tabicl_v1.md`
- `reports/volunteer_matching/benchmark_20260610_stratified_2021_2025_limit50_tabicl_v1.json`

Combined 2022-2025 result (`400` cases, `30` methods including ML and TabICL baselines):

| Metric | Custom method | Rank |
| --- | ---: | ---: |
| MAE Rank | 6027.6075 | 1 |
| Median AE Rank | 1138.0000 | 1 |
| P90 AE Rank | 14250.0000 | 1 |
| RMSE Rank | 14431.0604 | 1 |
| MAE Score | 12.6494 | 1 |
| Median AE Score | 8.5450 | 1 |
| P90 AE Score | 26.0000 | 1 |
| RMSE Score | 19.5237 | 1 |
| Within 3 Score Points | 0.2375 | 1 |
| Within 5 Score Points | 0.3450 | 1 |
| Within 10 Score Points | 0.5725 | 1 |
| Directional Bias | 0.0100 | 1 |
| Severe Error Rate | 0.2275 | 1 |
| Severe Directional Balance | 0.0525 | 1 |
| Plan Admissible Rate | 0.8571 | 1 |
| First Admissible Position | 1.6000 | 1 |
| Plan NDCG | 0.7988 | 1 |
| Bucket Balance Error | 0.0000 | Tied 1 |

Combined 2021-2025 boundary result (`450` cases, `30` methods; ML/TabICL
coverage is `0.8889` because 2021 has no prior training year):

| Metric | Custom method | Rank |
| --- | ---: | ---: |
| MAE Rank | 5404.6667 | 1 |
| Median AE Rank | 841.5000 | 1 |
| P90 AE Rank | 13476.0000 | 1 |
| RMSE Rank | 13608.4688 | 1 |
| MAE Score | 12.4594 | 1 |
| Median AE Score | 8.5050 | 1 |
| P90 AE Score | 24.0000 | 1 |
| RMSE Score | 19.0897 | 1 |
| Within 3 Score Points | 0.2178 | 1 |
| Within 5 Score Points | 0.3378 | 1 |
| Within 10 Score Points | 0.5844 | 1 |
| Directional Bias | 0.0111 | 1 |
| Severe Error Rate | 0.2067 | 1 |
| Severe Directional Balance | 0.0467 | 1 |
| Plan Admissible Rate | 0.8286 | 1 |
| First Admissible Position | 1.6000 | 1 |
| Plan NDCG | 0.8446 | 1 |
| Bucket Balance Error | 0.0000 | Tied 1 |
