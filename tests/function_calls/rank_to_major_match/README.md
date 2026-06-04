# rank_to_major_match

## 1. 工具原理

`rank_to_major_match` 根据位次或分数查询学校专业层面的历史录取匹配。它会解析专业，并结合学校录取统计和专业录取统计返回候选。

## 2. 输入与输出

- 主要输入：`major_text`、省份、科类、年份、位次或分数。
- 可选输入：学校过滤、冲稳保策略、limit。
- 关键输出：候选学校专业、历史分数、历史位次、风险标签。

## 3. 状态语义

- `ok`：返回专业匹配候选。
- `not_found`：没有匹配记录或专业未命中。
- `needs_clarification`：缺少专业、位次或分数等必要槽位。
- `partial`：部分上下文不足或上游转换有限。

## 4. 测试范围

已补充专属边界评估集和真实库 evaluator，覆盖：

- 专业解析：全称、代码、短别名、宽泛词、多候选歧义、大类/试验班、同名跨层次。
- 分数/位次：分数转位次、直接位次、极高分、极低分、缺科类、缺位次/分数。
- 科类口径：3+3 省份选考科目映射综合、3+1+2 省份缺首选科目、传统文理与物理/历史别名。
- 录取匹配：年份回退、限定 reference_years、地区过滤、学校层次过滤、limit、去重、冲/稳/保阈值。
- 入口与答案：自然语言路由是否调用 `rank_to_major_match`，答案是否包含学校、专业、位次、参考年份、冲稳保和历史参考限制。

## 5. 测试结果

- 最近运行日期：2026-06-03。
- 单元测试命令：

```powershell
python -m pytest tests/test_rank_to_major_match_boundary_evaluator.py -q
python -m pytest tests/test_retrieval_tools.py -k rank_to_major_match -q
```

- 单元测试结果：
  - `tests/test_rank_to_major_match_boundary_evaluator.py`：6 passed。
  - `tests/test_retrieval_tools.py -k rank_to_major_match`：3 passed。

- 真实库边界评估命令：

```powershell
python scripts/evaluate_rank_to_major_match_boundaries.py --manual-only --stamp 20260603_manual_after_oracle_fix
```

- 真实库边界评估结果：
  - 手工 case：41 个。
  - 工具层 hard fail：0。
  - 工具状态：`ok` 22、`not_found` 13、`needs_clarification` 6。
  - 入口层 call fail：11，主要是部分专业代码、直接位次、大类试验班被误路由到 `rank_to_school_match`、`comparison_query` 或 `source_trace_lookup`。
  - 答案层 answer fail：119，主要是当前入口答案仍偏占位，未展开学校名、专业名、位次、参考年份、冲稳保标签和历史参考限制。
  - 数据 warning：23，主要是同名跨层次专业、传统文理与物理/历史别名、3+3 综合口径映射、分数位次重复批次等。

- 报告文件：
  - [rank_to_major_match_boundary_eval_20260603_manual_after_oracle_fix.md](../../../reports/rank_to_major_match_boundary_eval_20260603_manual_after_oracle_fix.md)
  - [rank_to_major_match_boundary_eval_20260603_manual_after_oracle_fix.jsonl](../../../reports/rank_to_major_match_boundary_eval_20260603_manual_after_oracle_fix.jsonl)

## 6. 已知风险与待改善

- 历史专业录取不代表未来录取保证。
- `major_lookup` 对宽泛词会保守返回澄清或 not_found；入口答案需要把这种状态解释成“请补全专业全称/代码”，而不是只输出工具名。
- 入口路由对“专业代码”“数据科学与大数据技术”“口腔医学直接位次”“工科试验班/医学试验班”等表达仍不稳。
- 答案生成层需要消费结构化 buckets，输出学校-专业行、冲稳保标签、考生位次、参考年份和空桶说明。
- 传统文理与物理/历史切换年份会导致一分一段科类和历史录取科类不一致，需要在答案中明确提示。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 边界 case：[boundary_cases.json](boundary_cases.json)
- 边界 evaluator：[scripts/evaluate_rank_to_major_match_boundaries.py](../../../scripts/evaluate_rank_to_major_match_boundaries.py)
- 独立 oracle：[scripts/rank_to_major_match_oracles.py](../../../scripts/rank_to_major_match_oracles.py)
- 上游工具：`score_to_rank`、`major_lookup`

## 8. 扩展工具层边界集

新增 `extended_boundary_cases.json`，用于只压测 direct `rank_to_major_match` + oracle，不混入固定自然语言路由和答案生成层。

运行命令：

```powershell
python scripts/evaluate_rank_to_major_match_boundaries.py --cases tests/function_calls/rank_to_major_match/extended_boundary_cases.json --manual-only --tool-only --stamp 20260603_extended_tool_only_after_input_validation
```

本轮覆盖 41 个扩展 case：

- 跨层级专业解析：临床医学、口腔医学、护理学、软件工程等。
- 输入合法性边界：0 位次、负位次、超大位次、字符串分数、小数分数、负分、rank 与 score 同时存在。
- 年份边界：未来年份、reference_years 交叉/重复/老年份/缺省年份。
- 过滤交叉：未知地区、重复地区、985/211/双一流/本科、地区与层次强交集为空。
- 阈值微边界：保、稳、冲阈值附近的等于和差 1 位。
- limit 契约：0、负数、2、3、100、字符串数字。

最新结果：

- total：41
- direct tool hard fail：0
- data warning：9
- tool statuses：`ok` 27、`not_found` 9、`needs_clarification` 5
- `rank=0`、`rank=-1` 会返回 `needs_clarification=["rank"]`。
- `limit=0`、`limit=-5` 会返回 `needs_clarification=["limit"]`。
- `limit` 以字符串 `"5"` 传入时会规范化为整数 `5`，并稳定返回 5 条候选。

报告：

- [rank_to_major_match_boundary_eval_20260603_extended_tool_only_after_input_validation.md](../../../reports/rank_to_major_match_boundary_eval_20260603_extended_tool_only_after_input_validation.md)
- [rank_to_major_match_boundary_eval_20260603_extended_tool_only_after_input_validation.jsonl](../../../reports/rank_to_major_match_boundary_eval_20260603_extended_tool_only_after_input_validation.jsonl)
