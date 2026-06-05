# 对话数据质量报告

ASR 问题候选数：152
LLM 清洗记录数：152
问题记录数：152
可直接使用问题数：34
Function-call 评测用例数：152
导师策略记录数：5

## 问题族统计
- civil_service_role_search: 1
- comparison_query: 16
- employment_summary: 19
- major_market_reference: 4
- major_profile: 34
- rank_to_major_match: 6
- rank_to_school_match: 36
- school_major_profile: 19
- score_to_rank: 3
- subject_requirement_lookup: 3
- transfer_policy_lookup: 11

## 质量标签统计
- A: 4
- B: 30
- C: 51
- D: 67

## 来源类型统计
- public_asr: 152

## 使用规则

- `question_bank.jsonl` 用于检索/function-call 覆盖分析。
- `function_call_eval_cases.jsonl` 用于 expected intent 和 expected tools 测试。
- `mentor_strategy_bank.jsonl` 是策略指导，不是事实标准答案。
- `question_colloquial_clean` 保留用户口语风格，适合测试真实问法鲁棒性。
- 模拟内容不能混入真实对话数据。
- 公开视频 ASR 内容在产品中引用前需要人工复核。
