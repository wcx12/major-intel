# score_to_rank Boundary Evaluation

- JSONL: `reports/score_to_rank_boundary_eval_20260603_after_fix2.jsonl`
- Total cases: 52
- Hard failures: 0
- Answer failures: 0
- Data warnings: 31
- Tool statuses: `{"needs_clarification": 2, "not_found": 19, "ok": 31}`

## Top Failures

- `manual_zhejiang_comprehensive_620_latest_year` [latest_year_fallback] status=ok codes=ambiguous_exact_key, ambiguous_year_key
  answer: 2025年浙江综合620分，对应位次区间约为 31222-32114 名，同分人数 893 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 你没有指定年份，这里按本地库命中的 2025 年返回。 注意：未提供年份，已按本地库命中的年份 2025 返回；分数位次请优先按目标高考年份复核。。
- `manual_henan_science_465_latest_subject_priority` [latest_year_subject_priority] status=ok codes=ambiguous_exact_key, ambiguous_subject_key, ambiguous_year_key
  answer: 2025年河南物理465分，对应位次区间约为 275962-277938 名，同分人数 1977 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 你没有指定年份，这里按本地库命中的 2025 年返回。 注意：输入科类为“理科”，已按本地一分一段表命中的科类“物理”返回；请结合该省当年新高考/传统文理科口径复核。；未提供年份，已按本地库命中的年份 2025 返回；分数位次请优先按目标高考年份复核。。
- `manual_beijing_2021_comprehensive_119_duplicate_batch` [duplicate_batch_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2021年北京综合119分，对应位次区间约为 42032-42032 名，同分人数 1 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `manual_zhejiang_2025_comprehensive_decimal` [invalid_score] status=needs_clarification codes=non_integral_score
  answer: 这个问题还需要补充：分数。补齐后我再调用本地检索工具，避免猜测。
- `manual_zhejiang_2025_comprehensive_chinese_score` [invalid_score] status=needs_clarification codes=nonnumeric_score
  answer: 这个问题还需要补充：分数。补齐后我再调用本地检索工具，避免猜测。
- `auto_14_历史_2025_max_750` [auto_max] status=ok codes=ambiguous_batch_key, ambiguous_exact_key, same_count_mismatch
  answer: 2025年山西历史750分，对应位次区间约为 1-8 名，同分人数 8 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_14_物理_2025_max_750` [auto_max] status=ok codes=ambiguous_batch_key, ambiguous_exact_key, same_count_mismatch
  answer: 2025年山西物理750分，对应位次区间约为 1-10 名，同分人数 10 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_ambiguous_11_综合_2025_119` [auto_ambiguous_exact_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2025年北京综合119分，对应位次区间约为 65401-65410 名，同分人数 10 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_ambiguous_11_综合_2025_129` [auto_ambiguous_exact_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2025年北京综合129分，对应位次区间约为 65393-65400 名，同分人数 8 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_ambiguous_11_综合_2025_139` [auto_ambiguous_exact_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2025年北京综合139分，对应位次区间约为 65381-65392 名，同分人数 12 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_ambiguous_11_综合_2025_149` [auto_ambiguous_exact_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2025年北京综合149分，对应位次区间约为 65372-65380 名，同分人数 9 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_ambiguous_11_综合_2025_159` [auto_ambiguous_exact_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2025年北京综合159分，对应位次区间约为 65355-65371 名，同分人数 17 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_ambiguous_11_综合_2025_169` [auto_ambiguous_exact_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2025年北京综合169分，对应位次区间约为 65342-65354 名，同分人数 13 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_ambiguous_11_综合_2025_179` [auto_ambiguous_exact_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2025年北京综合179分，对应位次区间约为 65321-65341 名，同分人数 21 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。
- `auto_ambiguous_11_综合_2025_189` [auto_ambiguous_exact_key] status=ok codes=ambiguous_batch_key, ambiguous_exact_key
  answer: 2025年北京综合189分，对应位次区间约为 65302-65320 名，同分人数 19 人。 这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。 注意：本地一分一段表同一省份/科类/年份/分数存在多条记录；当前返回排序后的第一条，请结合本科/专科等批次口径复核。。

## Interpretation

- `hard_fail`: tool output disagrees with the local oracle or accepts invalid input.
- `answer_fail`: structured retrieval succeeded or failed correctly, but the user-facing answer omitted required facts or warnings.
- `data_warning`: local `edu_score_rank` data has ambiguity or quality issues the tool may need to surface.
