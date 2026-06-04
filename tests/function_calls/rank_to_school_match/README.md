# rank_to_school_match

## 1. 工具原理

`rank_to_school_match` 根据位次或分数推算学校层面的历史录取匹配。分数输入会先复用 `score_to_rank` 转换位次，再查询学校录取历史。

## 2. 输入与输出

- 主要输入：省份、科类、年份、位次或分数。
- 可选输入：学校层级过滤、冲稳保策略、limit。
- 关键输出：候选学校、历史位次、匹配风险分层。

## 3. 状态语义

- `ok`：返回学校匹配候选。
- `not_found`：没有匹配记录。
- `needs_clarification`：缺少必要位次或分数、缺省份或科类。
- `partial`：部分上下文不足或上游转换结果有限。

## 4. 测试范围

专属边界评估器覆盖四层：

- 自然语言 function call：intent、槽位、工具参数是否正确，尤其是多省份偏好、`省内`、学校层级过滤。
- 数据库 oracle：独立 SQL 从本地 `edu_score_rank`、`edu_school_admission_stats`、`edu_university` 复算候选、年份回退和冲稳保分桶。
- 工具 envelope：直接调用 `rank_to_school_match` 后，对比状态、参考年份、返回数量、bucket count、学校名。
- 用户答案：检查最终回答是否列出学校、冲稳保、位次、参考年份、空 bucket、历史参考/专业录取限制，并拒绝“保证录取”等越界表述。

## 5. 测试结果

- 最近运行日期：2026-06-03。
- 快速单元测试：`python -m pytest tests/test_rank_to_school_match_boundary_evaluator.py -q`
- 人工边界集：`python scripts/evaluate_rank_to_school_match_boundaries.py --manual-only --stamp 20260603_manual_after_fix`
- 完整边界集：`python scripts/evaluate_rank_to_school_match_boundaries.py --stamp 20260603_full --auto-groups 10 --threshold-cases 5`
- 最新完整报告：`reports/rank_to_school_match_boundary_eval_20260603_full.md`
- 最新完整 JSONL：`reports/rank_to_school_match_boundary_eval_20260603_full.jsonl`

最新完整评估：38 条 case，工具层 hard fail 为 0；function-call fail 为 7；answer fail 为 198。主要失败集中在当前自然语言入口没有为 `rank_to_school_match` 渲染推荐答案，只返回“已调用工具”的摘要。

## 6. 已知风险与待改善

- 学校匹配不等于专业录取保证。
- 需要补充批次、年份、招生口径差异的风险提示测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 上游工具：`score_to_rank`
