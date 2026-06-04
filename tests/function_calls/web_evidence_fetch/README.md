# web_evidence_fetch

<!-- legacy-section: ## 1. 宸ュ叿鍘熺悊 -->
## 1. 工具原理

`web_evidence_fetch` 是严谨版外部网页证据工具。它不查询本地 MySQL 表，而是复用免费 SearXNG 搜索服务，先获得候选网页，再按来源策略筛选候选页，抓取网页正文，清洗 HTML/PDF 文本，并抽取命中查询关键词的 `evidence_snippets`。

默认 `source_policy=official_only`，只采纳学校官网、`.edu.cn`、省级考试院、政府域名、阳光高考等高可信来源。`trusted_first` / `official_first` 会优先抓取高可信来源，再按候选顺序补足；如果显式使用 `source_policy=any`，第三方页面也会抓取，但必须在回答中标注为线索。

`data.search_results` 只能作为候选页面列表，不能写成事实。高风险事实（学校是否开设某专业、分省招生计划、招生章程限制、录取分数/位次等）必须由 `data.pages[].evidence_snippets` 中的正文片段直接支撑；如果已有结构化本地缺口，Agent 会优先改用 `web_gap_fill` 做多轮搜索、正文抓取和证据评估。

<!-- legacy-section: ## 2. 杈撳叆涓庤緭鍑? -->
## 2. 输入与输出

- 主要输入：`query`、`search_scope`、`domains`、`limit`、`fetch_limit`、`evidence_limit`、`source_policy`。
- 关键输出：`data.search_results`、`data.pages`、`data.evidence_pages`。
- 重要字段：`page.url`、`page.source_type`、`page.confidence`、`page.fetch_status`、`page.text_excerpt`、`page.evidence_snippets`。

<!-- legacy-section: ## 3. 鐘舵€佽涔? -->
## 3. 状态语义

- `ok`：至少一个候选页成功抓取正文，并抽取到证据片段。
- `partial`：搜索到了候选页，但正文抓取失败，或正文没有命中查询关键词。
- `not_found`：没有搜索结果，或在 `official_only` 策略下没有高可信候选来源。
- `needs_clarification`：缺少 `query`，或 `limit` / `fetch_limit` / `evidence_limit` 非正整数，或 `source_policy` 不合法，或 SearXNG 未启用/未配置。
- `error`：SearXNG 搜索请求或 JSON 解析失败。

<!-- legacy-section: ## 4. 娴嬭瘯鑼冨洿 -->
## 4. 测试范围

- 使用 fake fetcher 验证 SearXNG 搜索 JSON 归一化后，会继续抓取官方 HTML 正文。
- 验证 HTML 清洗会移除 `script`、`nav` 等噪声，并返回 `text_excerpt`。
- 验证 `evidence_snippets` 只从正文中抽取，而不是直接使用搜索摘要。
- 验证 `scope_notes` 明确要求 `search_results` 只能作为候选，事实必须来自 `pages.evidence_snippets`。
- 验证 `official_only` 不抓取第三方页面，并返回 `not_found + official_web_evidence`。
- 验证 `source_policy=any` 可以抓取第三方页面，但置信度保持较低；`trusted_first` 与 `official_first` 兼容。
- 验证候选页抓取失败时返回 `partial + web_page_content`。
- 验证 registry schema、dispatcher、agent 自动 fallback 在没有结构化缺口时可调用 `web_evidence_fetch`；如果已有结构化缺口，优先改用 `web_gap_fill`。

<!-- legacy-section: ## 5. 娴嬭瘯缁撴灉 -->
## 5. 测试结果

- 最近运行日期：2026-06-04
- 运行命令：`python -m pytest tests/test_gap_detection_registry.py tests/test_retrieval_function_registry.py tests/test_deepseek_retrieval_agent.py tests/test_web_gap_fill.py tests/test_web_evidence_fetch.py tests/test_web_evidence_search.py tests/test_function_call_readmes.py -q`
- 运行结果：`58 passed in 0.72s`
- 真实工具 smoke：`python scripts\retrieval_tools.py web_evidence_fetch --query "杭州电子科技大学 招生章程" --search-scope official --domain zhaosheng.hdu.edu.cn --limit 5 --fetch-limit 2 --evidence-limit 3 --source-policy official_only`
- 真实工具结果：`status=ok`，成功抓取 `https://zhaosheng.hdu.edu.cn/art.php?aid=2339` 正文，并抽取到“杭州电子科技大学2025年普通高校招生章程”等 `evidence_snippets`。
- 真实 agent smoke：`人工智能专业，上海有哪些本科院校开设？`
- 真实 agent 结果：结构化专业院校缺口优先调用 `major_school_list -> web_gap_fill`；`web_evidence_fetch` 不再承担列表完整性判断。

<!-- legacy-section: ## 6. 宸茬煡椋庨櫓涓庡緟鏀瑰杽 -->
## 6. 已知风险与待改善

- 当前 HTML 正文抽取是通用清洗，不保证能处理所有招生网站的异步渲染页面。
- PDF 仅尝试 `pypdf` 文本提取；扫描版 PDF 仍需要 OCR 能力。
- 官方来源识别仍是启发式规则，后续应该维护学校招生网、省考试院、阳光高考等白名单。
- 自动 fallback 默认 `official_only`，因此宁可返回未核验，也不会自动使用第三方页面当作事实。
- `web_evidence_fetch` 不做完整缺口覆盖判断；涉及结构化缺口时应使用 `web_gap_fill`。

<!-- legacy-section: ## 7. 鍏宠仈鏂囦欢 -->
## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- Schema：[scripts/retrieval_function_registry.py](../../../scripts/retrieval_function_registry.py)
- Agent 接入：[scripts/deepseek_retrieval_agent.py](../../../scripts/deepseek_retrieval_agent.py)
- 专属测试：[tests/test_web_evidence_fetch.py](../../test_web_evidence_fetch.py)
- 配置示例：[.env.example](../../../.env.example)
