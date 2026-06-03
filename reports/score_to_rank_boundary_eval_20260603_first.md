# score_to_rank Boundary Evaluation

- JSONL: `reports/score_to_rank_boundary_eval_20260603_first.jsonl`
- Total cases: 52
- Hard failures: 1
- Answer failures: 133
- Data warnings: 31
- Tool statuses: `{"error": 1, "not_found": 19, "ok": 32}`

## Top Failures

- `manual_zhejiang_2025_comprehensive_620_ok` [happy_path] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `manual_zhejiang_comprehensive_620_latest_year` [latest_year_fallback] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, ambiguous_exact_key, ambiguous_year_key
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `manual_zhejiang_2025_comprehensive_268_min` [min_score] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `manual_zhejiang_2025_comprehensive_750_max` [max_score] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `manual_henan_2025_science_465_alias` [legacy_subject_alias] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。 注意：输入科类为“理科”，已按本地一分一段表命中的科类“物理”返回；请结合该省当年新高考/传统文理科口径复核。。
- `manual_henan_science_465_latest_subject_priority` [latest_year_subject_priority] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, ambiguous_exact_key, ambiguous_subject_key, ambiguous_year_key
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `manual_beijing_2021_comprehensive_119_duplicate_batch` [duplicate_batch_key] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, ambiguous_batch_key, ambiguous_exact_key
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `manual_zhejiang_2025_comprehensive_decimal` [invalid_score] status=ok codes=tool_accepts_invalid_score, answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, non_integral_score
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `manual_zhejiang_2025_comprehensive_chinese_score` [invalid_score] status=error codes=answer_missing_score_to_rank_trace, nonnumeric_score
  answer: 这个问题还需要补充：你想查询的具体问题。补齐后我再调用本地检索工具，避免猜测。
- `auto_11_综合_2025_min_109` [auto_min] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_11_综合_2025_max_750` [auto_max] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_12_综合_2025_min_100` [auto_min] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_12_综合_2025_below_min_99` [auto_below_min] status=not_found codes=answer_missing_score_to_rank_trace
  answer: 这个问题还需要补充：你想查询的具体问题。补齐后我再调用本地检索工具，避免猜测。
- `auto_12_综合_2025_max_750` [auto_max] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_13_历史_2025_min_140` [auto_min] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_13_历史_2025_max_750` [auto_max] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_13_物理_2025_min_140` [auto_min] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_13_物理_2025_max_750` [auto_max] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_14_历史_2025_min_101` [auto_min] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_14_历史_2025_max_750` [auto_max] status=ok codes=tool_missing_ambiguity_warning, answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, ambiguous_batch_key, ambiguous_exact_key, same_count_mismatch
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_14_物理_2025_min_100` [auto_min] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_14_物理_2025_below_min_99` [auto_below_min] status=not_found codes=answer_missing_score_to_rank_trace
  answer: 这个问题还需要补充：你想查询的具体问题。补齐后我再调用本地检索工具，避免猜测。
- `auto_14_物理_2025_max_750` [auto_max] status=ok codes=tool_missing_ambiguity_warning, answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, ambiguous_batch_key, ambiguous_exact_key, same_count_mismatch
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_15_历史_2025_min_200` [auto_min] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_15_历史_2025_max_750` [auto_max] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_15_物理_2025_min_200` [auto_min] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_15_物理_2025_max_750` [auto_max] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_ambiguous_11_综合_2025_119` [auto_ambiguous_exact_key] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, ambiguous_batch_key, ambiguous_exact_key
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_ambiguous_11_综合_2025_129` [auto_ambiguous_exact_key] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, ambiguous_batch_key, ambiguous_exact_key
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。
- `auto_ambiguous_11_综合_2025_139` [auto_ambiguous_exact_key] status=ok codes=answer_missing_rank_range, answer_missing_year, answer_missing_same_count, answer_missing_scope_note, ambiguous_batch_key, ambiguous_exact_key
  answer: 已按 `score_to_rank` 处理，调用工具：score_to_rank。

## Interpretation

- `hard_fail`: tool output disagrees with the local oracle or accepts invalid input.
- `answer_fail`: structured retrieval succeeded or failed correctly, but the user-facing answer omitted required facts or warnings.
- `data_warning`: local `edu_score_rank` data has ambiguity or quality issues the tool may need to surface.
