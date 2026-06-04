# web_gap_fill

## 1. 工具原理

`web_gap_fill` 是面向 Agent 的网页缺口补全工具。它接收结构化 `gap_items`，围绕每个缺口生成有限轮次搜索查询，调用 `web_evidence_fetch` 搜索并抓取网页正文，然后判断正文是否真的能填补当前缺口。

当前证据判断有两种模式：

- 默认模式：使用确定性规则评估正文证据，保持本地测试和离线运行兼容。
- LLM judge 模式：设置 `WEB_GAP_JUDGE_ENABLED=true` 后，工具会把缺口、证据契约、网页来源信息和正文片段交给 OpenAI-compatible 模型判断。模型只能返回结构化 JSON，且 `evidence_quote` 必须能在抓取正文中原文找到；如果模型判断支持但摘录不是逐字原文，工具只允许从抓取正文中按学校、专业、代码、层级等字段重新定位一段真实原文，定位不到仍会拒绝。

`source_policy=official_only` 时只接受学校官网、考试院、政府域名、阳光高考等可信来源。第三方结果只作为线索进入 `rejected_evidence`，不能写成事实。

对于 `major_school_list` 这类“某地区有哪些学校开设某专业”的列表型缺口，`web_gap_fill` 不会因为确认了一个学校就把缺口标记为完整。它会继续在预算内搜索其它候选学校；如果只确认到部分学校，会返回 `partial`、`coverage_status=partial` 和 `unfilled_reason=list_coverage_incomplete`。

## 2. 输入与输出

主要输入：

- `gap_items`：结构化缺口数组，通常来自 `data_gap_detection` 或本地工具结果缺口识别。
- `question`：用户原始问题，用于生成更完整的搜索 query。
- `max_rounds`：最多搜索补全轮数。
- `max_fetches_per_round`：每轮最多抓取页面数。
- `max_seconds`：整个工具最大运行秒数，超时返回 `stop_reason=timeout_reached`。
- `source_policy`：来源策略，支持 `official_only`、`trusted_first`、`official_first`、`any`。

关键输出：

- `data.filled_items`：已被证据填补出的结构化字段。
- `data.accepted_evidence`：通过证据评估的网页正文证据。
- `data.rejected_evidence`：被拒绝的网页或搜索结果，包含拒绝原因。
- `data.unfilled_gaps`：仍未填补的缺口。
- `data.rounds`：每轮搜索、抓取、接受/拒绝数量。
- `data.stop_reason`：停止原因，例如 `all_gaps_filled`、`timeout_reached`、`no_accepted_evidence`。
- `data.coverage_summary`：列表型缺口的覆盖摘要，包含 `confirmed_schools`、`candidate_schools`、`unknown_schools` 和 `rejected_schools`。

## 3. 状态语义

- `ok`：所有可网页补全的缺口都找到了已抓取、已评估通过的可信正文证据。
- `partial`：部分缺口补全成功，仍有缺口保留在 `unfilled_gaps`。
- `not_found`：输入缺口可尝试补全，但没有找到任何通过评估的可信网页正文证据。
- `needs_clarification`：`gap_items` 缺失或为空、数值参数非法、`source_policy` 非法，或出现未知 `gap_key`。
- `data.stop_reason`：说明工具为什么停止，例如 `all_gaps_filled`、`timeout_reached`、`no_accepted_evidence`。
- 列表型缺口即使有 `accepted_evidence`，只要不能证明列表完整，也返回 `partial`，不能写成“只有这些学校”。

## 4. 测试范围

- 官方网页正文能支持 `major_school_relation` 时进入 `accepted_evidence`。
- 第三方结果在 `official_only` 下不被抓取或接受。
- 只有第三方结果时返回 `not_found`，并保留 `unfilled_gaps`。
- 未知 `gap_key` 在网络调用前返回 `needs_clarification`。
- `max_rounds` 和 `max_fetches_per_round` 生效，避免无限搜索。
- 注入式 LLM judge 可以接受正文支持的证据。
- LLM judge 声称支持但引用不在正文中时，工具返回 `judge_quote_not_in_body`。
- LLM judge 声称支持但引用不精确时，如果正文中存在等价可定位证据，工具会修复为正文原文并标记 `judge_quote_repaired=true`。
- `max_seconds` 耗尽时不继续发起网络请求，返回 `stop_reason=timeout_reached`。
- 地区专业院校列表确认一个学校后仍继续检索其它候选学校，并返回 `coverage_status=partial`。
- registry schema、dispatcher 和 DeepSeek Agent 自动 fallback 优先调用 `web_gap_fill`。

## 5. 测试结果

- 最近运行日期：2026-06-04
- 专项测试：`python -m pytest tests/test_web_gap_fill.py -q`
- 专项结果：`10 passed`

## 6. 已知风险与待改善

- LLM judge 依赖网页正文质量；如果页面是图片、复杂 JS 渲染、扫描 PDF 或被 403/412 拦截，仍可能无法确认。
- 当前 judge 使用正文片段和受限 `body_text`，不是无限制全文输入；极长页面可能需要后续做段落级切片和多段裁判。
- 第三方页面目前只作为线索，后续可以提取候选学校后再自动查官方站详情页。
- 学校实体归一化仍需后续接入，避免“上海交通大学人工智能学院”这类学院名被当成学校名。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- Schema：[scripts/retrieval_function_registry.py](../../../scripts/retrieval_function_registry.py)
- Agent 接入：[scripts/deepseek_retrieval_agent.py](../../../scripts/deepseek_retrieval_agent.py)
- 专项测试：[tests/test_web_gap_fill.py](../../test_web_gap_fill.py)
- 配置示例：[.env.example](../../../.env.example)
