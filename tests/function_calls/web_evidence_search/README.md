# web_evidence_search

## 1. 工具原理

`web_evidence_search` 是面向 agent 的外部网页证据检索工具。它不查询本地 MySQL 表，而是通过已配置的免费 SearXNG 服务调用 `/search?format=json`，把搜索结果归一化为统一 function-call envelope。

设计边界：本地数据库工具仍然优先。只有本地结果为 `not_found`、`partial`、存在 `data_gaps`，或用户明确询问最新、官网、招生章程、政策、选科、学费、校区等时效信息时，才应调用该工具。返回结果只能作为外部候选证据，不能直接当作本地库事实。

## 2. 输入与输出

- 主要输入：`query`、`search_scope`、`domains`、`limit`。
- 关键输出：`data.results`，包含 `title`、`url`、`snippet`、`source_type`、`confidence`、`rank`。
- 重要字段：`source_type` 用于区分 `official`、`exam_authority`、`chsi`、`third_party`；`confidence` 用于提示证据可信度。

## 3. 状态语义

- `ok`：SearXNG 返回至少 1 条可用网页结果。
- `partial`：当前工具暂不主动返回该状态；后续如果加入正文抓取或多 provider 聚合，可用于表示部分 provider 成功。
- `not_found`：SearXNG 调用成功，但没有返回可用结果。
- `needs_clarification`：缺少 `query`、`limit` 非正整数、未开启 `WEB_SEARCH_ENABLED`、未配置 `SEARXNG_BASE_URL`，或 provider 不是 `searxng`。
- `error`：SearXNG 请求、JSON 解析或外部网络调用失败。

## 4. 测试范围

当前专属测试覆盖：

- 未启用 `WEB_SEARCH_ENABLED` 或缺少 `SEARXNG_BASE_URL` 时，不发起网络请求并返回 `needs_clarification`。
- 使用 fake fetcher 模拟 SearXNG JSON 返回，验证结果归一化、官方来源识别、置信度、URL 参数。
- SearXNG 无结果时返回 `not_found` 和 `external_web_evidence` 缺口。
- `limit=0` 时在网络调用前返回 `needs_clarification`。
- registry schema 注册、required slot、dispatcher 可调用性。

## 5. 测试结果

- 最近运行日期：2026-06-03
- 运行命令：`python -m pytest tests/test_web_evidence_search.py tests/test_retrieval_function_registry.py -q`
- 运行结果：`13 passed in 0.55s`
- 真实 SearXNG smoke：本地 Docker 容器 `major-intel-searxng` 运行在 `http://127.0.0.1:8081`，已开启 JSON 输出。
- 真实工具调用：`python scripts\retrieval_tools.py web_evidence_search --query "杭州电子科技大学 招生章程" --search-scope official --domain zhaosheng.hdu.edu.cn --limit 5`
- 真实调用结果：`status=ok`，命中 `https://zhaosheng.hdu.edu.cn/art.php?aid=2339` 等官方来源。

## 6. 已知风险与待改善

- 该工具依赖自托管 SearXNG；公共实例通常不稳定，且可能关闭 JSON 输出。
- SearXNG 免费但受上游搜索引擎限流影响，需要后续补缓存和限流策略。
- 当前只返回搜索结果摘要，不抓取网页正文；如果要严谨核验招生章程/PDF，需要后续增加 `web_page_extract`。
- 第三方网页只能作为线索，最终高风险结论应优先使用学校官网、省考试院、阳光高考等官方来源。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- Schema：[scripts/retrieval_function_registry.py](../../../scripts/retrieval_function_registry.py)
- 专属测试：[tests/test_web_evidence_search.py](../../test_web_evidence_search.py)
- Registry 测试：[tests/test_retrieval_function_registry.py](../../test_retrieval_function_registry.py)
- 配置示例：[.env.example](../../../.env.example)
