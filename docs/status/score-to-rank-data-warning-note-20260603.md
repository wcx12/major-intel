# score_to_rank 数据警告记录

记录时间：2026-06-03

## 当前决定

`same_count_mismatch` 先不作为 `score_to_rank` 工具缺陷处理，保留为数据警告。当前工具返回的本科批次行本身是自洽的；异常主要来自同一精确键下并存的专科批次压缩区间行。

相关评估报告：

- `reports/score_to_rank_boundary_eval_20260603_first.md`
- `reports/score_to_rank_boundary_eval_20260603_after_fix2.md`

最终评估结果：

- Total cases: 52
- Hard failures: 0
- Answer failures: 0
- Data warnings: 31
- Tool statuses: `{"needs_clarification": 2, "not_found": 19, "ok": 31}`

## 触发 same_count_mismatch 的 function call

1. `score_to_rank(province="山西", subject_type="历史", score=750, year=2025)`
2. `score_to_rank(province="山西", subject_type="物理", score=750, year=2025)`

这两个调用同时还会触发 `ambiguous_batch_key` / `ambiguous_exact_key`，因为同一省份、年份、科类、分数下同时存在 `undergraduate` 和 `vocational` 两个批次记录。

## 数据证据

### 山西历史 2025 750 分

| batch_type | score | max_score | min_score | same_count | highest_rank | lowest_rank | rank_span |
|---|---:|---:|---:|---:|---:|---:|---:|
| undergraduate | 750 | 750 | 672 | 8 | 1 | 8 | 8 |
| vocational | 750 | 750 | 443 | 115 | 1 | 3025 | 3025 |

`undergraduate` 行：`same_count = 8`，`lowest_rank - highest_rank + 1 = 8`，自洽。

`vocational` 行：`same_count = 115`，但 `lowest_rank - highest_rank + 1 = 3025`，相差 2910。

对应批次总量复核：

| batch_type | rows_count | sum_same_count | min_highest | max_lowest | missing |
|---|---:|---:|---:|---:|---:|
| undergraduate | 230 | 35877 | 1 | 35877 | 0 |
| vocational | 343 | 49117 | 1 | 52027 | 2910 |

历史专科批次的总量缺口 `52027 - 49117 = 2910`，正好等于顶部压缩行缺口 `3025 - 115 = 2910`。

### 山西物理 2025 750 分

| batch_type | score | max_score | min_score | same_count | highest_rank | lowest_rank | rank_span |
|---|---:|---:|---:|---:|---:|---:|---:|
| undergraduate | 750 | 750 | 705 | 10 | 1 | 10 | 10 |
| vocational | 750 | 750 | 419 | 260 | 1 | 9283 | 9283 |

`undergraduate` 行：`same_count = 10`，`lowest_rank - highest_rank + 1 = 10`，自洽。

`vocational` 行：`same_count = 260`，但 `lowest_rank - highest_rank + 1 = 9283`，相差 9023。

对应批次总量复核：

| batch_type | rows_count | sum_same_count | min_highest | max_lowest | missing |
|---|---:|---:|---:|---:|---:|
| undergraduate | 287 | 120285 | 1 | 120285 | 0 |
| vocational | 317 | 53322 | 1 | 62345 | 9023 |

物理专科批次的总量缺口 `62345 - 53322 = 9023`，正好等于顶部压缩行缺口 `9283 - 260 = 9023`。

## 判断

这不是当前 `score_to_rank` 查询逻辑导致的主问题，而是 `edu_score_rank` 里部分批次记录的建模或导入语义问题：

- 顶部分数行不是普通单分数行，而是压缩区间行，例如历史专科 `443-750`、物理专科 `419-750`。
- `highest_rank` / `lowest_rank` 表示这个压缩区间覆盖的累计位次范围。
- `same_count` 看起来不是整个压缩区间人数，而更像边界分数人数或导入时保留的单点人数。
- 因此 `same_count` 与 `lowest_rank - highest_rank + 1` 不一致。

当前工具排序会优先返回本科批次行；本科批次行的 `same_count` 与位次跨度一致。对于同一精确键下存在多个批次的情况，工具已经通过警告提示用户按本科、专科等批次口径复核。

## 后续可选处理

后续如果要消掉这个数据警告，可以考虑：

1. 在数据层明确压缩区间行语义，新增或标注 `interval_count`，避免把 `same_count` 当成区间人数。
2. 给 `score_to_rank` 增加显式 `batch_type` 参数，让用户可以区分本科、专科批次查询。
3. 在评估器里把 `max_score != min_score` 的压缩区间行单独归类为 `compressed_interval_row`，避免和普通单分数行的数据质量警告混在一起。
