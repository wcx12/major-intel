# 高考志愿对话清洗结果说明

## 产出概览

- 原始 ASR 问题候选：152 条
- Claude Code 清洗完成：152 条
- 可直接用于高质量检索 / function-call 覆盖测试的问题：34 条
- Function-call 评测用例：152 条
- 导师回复策略记录：5 条
- 数据来源：已拉取的高考志愿相关 GitHub 项目中的公开视频 ASR 转写与资料片段。
- 数据性质：真实公开语料衍生的清洗数据，不是模拟问答，不是官方招生数据。

## 生成命令

```bash
python scripts/datasets/build_dialogue_assets.py \
  --cleaner claude \
  --claude-batch-size 1 \
  --claude-timeout-seconds 360 \
  --no-rule-fallback \
  --output-dir datasets/dialogue/claude_full
```

清洗过程中使用了缓存续跑。最终产物已重新生成，`llm_cleaned_dialogues.jsonl`、`question_bank.jsonl`、`function_call_eval_cases.jsonl` 均为 152 条全量结果。

## 核心文件

- `README.md`：当前说明文件。
- `SOURCES.md`：第三方仓库来源引用、许可证和署名说明。
- `asr_question_candidates.jsonl`：从 ASR 里抽取的原始问题候选及导师回复片段。
- `llm_cleaned_dialogues.jsonl`：Claude Code 清洗后的全量对话记录。
- `question_bank.jsonl`：问题库，全量 152 条，适合做检索覆盖、intent 分类、function-call 覆盖分析。
- `usable_question_bank.jsonl`：质量较高、可直接用于评测的 34 条问题。
- `function_call_eval_cases.jsonl`：全量 function-call 评测用例。
- `usable_function_call_eval_cases.jsonl`：高质量 function-call 评测用例。
- `mentor_strategy_bank.jsonl`：导师回复策略摘要，不是事实标准答案。
- `mentor_reply_strategies.md`：导师策略的人类可读汇总。
- `student_common_questions.md`：学生 / 家长常问问题的人类可读汇总。
- `source_inventory.json`：源项目清单与数据类型。
- `dialogue_quality_report.md`：数量、问题族、质量标签统计。
- `review_queue.jsonl`：需要人工复核的记录。

## 字段口径

- `question_raw`：原始 ASR 问题，不做事实修正。
- `question_colloquial_clean`：轻清洗口语版，保留考生 / 家长真实问法风格，只去掉明显重复、断裂和 ASR 噪声。
- `question_formal_clean`：书面表达版，用于后续更标准的查询、摘要或训练对照；不新增省份、分数、位次、学校、专业等事实。
- `question_normalized`：用于检索 / function-call 测试的规范化问题，统一以中文问号结尾。
- `question_family`：问题族，用于 intent 覆盖分析。
- `slots`：只抽取原文中明确出现的事实。
- `missing_slots`：当前问题缺失但通常影响志愿判断的槽位。
- `expected_tools`：该问题理论上需要调用的工具集合。
- `mentor_strategy`：从导师回复中抽取的策略摘要，不引用原话，不作为事实标准答案。
- `quality_label` / `quality_score`：对问题完整性、可测试性、ASR 噪声程度的质量判断。

## 质量分层

- A：问题信息较完整，口语噪声少，可直接进入评测。
- B：主体意图清楚，但缺少少量关键槽位或有轻微 ASR 噪声。
- C：能识别大致意图，但缺槽较多、表达断裂或上下文依赖较强。
- D：ASR 噪声明显、问题不完整、话题断裂或更像泛化观点；仍可用于测试模型的数据缺口识别能力。

`usable_question_bank.jsonl` 只保留较适合直接回归测试的子集；`question_bank.jsonl` 保留全量真实分布。

## 清洗方式

1. 先从公开视频 ASR 中抽取考生 / 家长问题候选及其后续导师回复片段。
2. 每条候选都把 `question_raw` 和完整 `response_candidate_raw` 直接传给本地 Claude Code；未做本地截断、摘要或压缩。
3. Claude Code 需要同时输出口语轻清洗版和书面版，并抽取问题族、槽位、缺失槽位、expected tools、导师策略、风格特征和质量标签。
4. 脚本只做确定性校验和规范化：
   - 解析 Claude Code 的 JSON event wrapper、`result` 字段、单条 record object 和批次输出文件。
   - 将少量工具名误填的问题族规范到 canonical family，例如 `school_profile -> school_major_profile`、`specialty_group_lookup -> specialty_group_risk`。
   - 兼容 `question_colformal_clean` 这类明显字段拼写错误。
   - 强制 `question_normalized` 以中文问号结尾。
   - 拒绝未知工具、缺失必填字段、非对象记录、非当前批次 candidate_id。
5. 对 Claude 未按 JSON 输出、漏 candidate、字段错误的样本，用缓存续跑重试，直到 152 条全部成功。

## 未提交的中间文件

清洗过程中产生过 `_claude_batch_output_*.json`、`_claude_cleaned_cache.jsonl`、`_claude_failures_cache.jsonl` 等中间文件。这些文件只用于断点续跑、失败排查和批次兜底，不是面向下游使用的数据集，因此不应作为正式数据接口依赖。

## 验证结果

- 单测：`python -m pytest tests/test_build_dialogue_assets.py -q`，28 passed。
- JSONL 校验：
  - `llm_cleaned_dialogues.jsonl`：152 条
  - `question_bank.jsonl`：152 条
  - `function_call_eval_cases.jsonl`：152 条
  - `usable_question_bank.jsonl`：34 条
  - `mentor_strategy_bank.jsonl`：5 条
  - `review_queue.jsonl`：148 条
- 校验项包括：152 个唯一 `source_candidate_id`、双版本问题字段非空、`question_normalized` 以中文问号结尾、`mentor_strategy` 为数组。

## 使用建议

- 后续测试模型检索 / function-call 覆盖时，优先用 `question_bank.jsonl` 全量覆盖，再用 `usable_question_bank.jsonl` 做高置信回归集。
- `question_colloquial_clean` 用来测真实口语问法鲁棒性；`question_formal_clean` 用来测标准问法覆盖。
- `mentor_strategy` 适合沉淀为回复策略或 RAG 参考，不建议作为逐字答案。
- D 级样本仍有价值，主要用于测试模型面对 ASR 噪声、信息缺失和话题断裂时能否识别缺口并请求补充信息。

## 使用边界

- 这批数据来自公开材料和 ASR 转写，存在识别错误、断句错误、上下文丢失和口误。
- `mentor_strategy` 是策略抽取，不应直接展示为导师原话。
- 涉及院校、专业、录取概率、分数线、位次等事实判断时，必须接入官方数据源或项目内检索工具二次核验。
- 若用于产品侧展示，建议先对 `review_queue.jsonl` 做人工复核。
- 继续分发或引用本目录数据时，应同时保留 `SOURCES.md` 和 `source_inventory.json`。
