import json
import unittest
from unittest.mock import patch


class WebEvidenceFetchTests(unittest.TestCase):
    def _enabled_env(self):
        return {
            "WEB_SEARCH_ENABLED": "true",
            "WEB_SEARCH_PROVIDER": "searxng",
            "SEARXNG_BASE_URL": "http://127.0.0.1:8081",
            "WEB_SEARCH_TIMEOUT_SECONDS": "7",
        }

    def test_fetches_official_html_and_extracts_query_matched_evidence(self):
        from scripts.retrieval_tools import RetrievalTools

        official_url = "https://zsb.sjtu.edu.cn/article/ai.html"
        third_party_url = "https://example.com/sjtu-ai"
        calls = []

        def fetcher(url, timeout):
            calls.append(url)
            if "/search?" in url:
                return json.dumps(
                    {
                        "results": [
                            {
                                "title": "第三方汇总",
                                "url": third_party_url,
                                "content": "第三方页面说上海交通大学开设人工智能。",
                                "score": 0.95,
                            },
                            {
                                "title": "上海交通大学招生专业介绍",
                                "url": official_url,
                                "content": "上海交通大学招生网发布人工智能本科专业介绍。",
                                "score": 0.9,
                            },
                        ]
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
            if url == official_url:
                return """
                <html>
                  <head><title>上海交通大学招生专业介绍</title></head>
                  <body>
                    <nav>首页 导航</nav>
                    <script>console.log("noise")</script>
                    <main>
                      <h1>上海交通大学招生专业介绍</h1>
                      <p>电子信息类包含人工智能方向，面向本科生培养。</p>
                      <p>招生专业目录以学校招生网发布的信息为准。</p>
                    </main>
                  </body>
                </html>
                """.encode("utf-8")
            raise AssertionError(f"unexpected fetch url: {url}")

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict("os.environ", self._enabled_env(), clear=True):
            result = tools.web_evidence_fetch(
                "上海交通大学 人工智能 本科专业",
                search_scope="official",
                domains=["sjtu.edu.cn"],
                limit=5,
                fetch_limit=2,
                evidence_limit=3,
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data_gaps"], [])
        self.assertEqual(len(result["data"]["search_results"]), 1)
        self.assertEqual(result["data"]["rejected_search_results"][0]["url"], third_party_url)
        self.assertEqual(len(result["data"]["pages"]), 1)

        page = result["data"]["pages"][0]
        self.assertEqual(page["url"], official_url)
        self.assertEqual(page["source_type"], "official")
        self.assertEqual(page["fetch_status"], "ok")
        self.assertGreater(page["content_length"], 30)
        self.assertIn("招生专业", page["text_excerpt"])
        self.assertNotIn("console.log", page["text_excerpt"])
        self.assertTrue(any("人工智能" in snippet["text"] for snippet in page["evidence_snippets"]))
        self.assertTrue(any("本科" in snippet["text"] for snippet in page["evidence_snippets"]))
        self.assertNotIn(third_party_url, calls)
        self.assertTrue(
            any("search_results 只能作为候选" in note for note in result["scope_notes"]),
            result["scope_notes"],
        )
        self.assertTrue(
            any("pages.evidence_snippets" in note for note in result["scope_notes"]),
            result["scope_notes"],
        )

    def test_returns_partial_when_candidate_pages_cannot_be_fetched(self):
        from scripts.retrieval_tools import RetrievalTools

        official_url = "https://zsb.sjtu.edu.cn/article/ai.html"

        def fetcher(url, timeout):
            if "/search?" in url:
                return json.dumps(
                    {
                        "results": [
                            {
                                "title": "上海交通大学招生专业介绍",
                                "url": official_url,
                                "content": "上海交通大学招生网发布人工智能本科专业介绍。",
                                "score": 0.9,
                            }
                        ]
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
            raise RuntimeError("network blocked")

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict("os.environ", self._enabled_env(), clear=True):
            result = tools.web_evidence_fetch("上海交通大学 人工智能 本科专业", limit=3)

        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["data_gaps"], ["web_page_content"])
        self.assertEqual(result["data"]["pages"][0]["fetch_status"], "error")
        self.assertIn("RuntimeError", result["data"]["pages"][0]["warnings"][0])

    def test_official_only_returns_not_found_without_fetching_third_party_pages(self):
        from scripts.retrieval_tools import RetrievalTools

        third_party_url = "https://example.com/sjtu-ai"
        calls = []

        def fetcher(url, timeout):
            calls.append(url)
            if "/search?" in url:
                return json.dumps(
                    {
                        "results": [
                            {
                                "title": "第三方汇总",
                                "url": third_party_url,
                                "content": "第三方页面说上海交通大学开设人工智能。",
                                "score": 0.95,
                            }
                        ]
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
            raise AssertionError("official_only should not fetch third-party pages")

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict("os.environ", self._enabled_env(), clear=True):
            result = tools.web_evidence_fetch("上海交通大学 人工智能 本科专业")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["data_gaps"], ["official_web_evidence"])
        self.assertEqual(result["data"]["search_results"], [])
        self.assertEqual(result["data"]["rejected_search_results"][0]["url"], third_party_url)
        self.assertEqual(result["data"]["pages"], [])
        self.assertEqual(calls, ["http://127.0.0.1:8081/search?q=%E4%B8%8A%E6%B5%B7%E4%BA%A4%E9%80%9A%E5%A4%A7%E5%AD%A6+%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD+%E6%9C%AC%E7%A7%91%E4%B8%93%E4%B8%9A&format=json&language=zh-CN&safesearch=0&pageno=1&count=5"])

    def test_source_policy_any_allows_third_party_but_marks_low_confidence(self):
        from scripts.retrieval_tools import RetrievalTools

        third_party_url = "https://example.com/sjtu-ai"

        def fetcher(url, timeout):
            if "/search?" in url:
                return json.dumps(
                    {
                        "results": [
                            {
                                "title": "第三方汇总",
                                "url": third_party_url,
                                "content": "第三方页面说上海交通大学开设人工智能。",
                                "score": 0.5,
                            }
                        ]
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
            if url == third_party_url:
                return "<html><body>上海交通大学 人工智能 本科 招生 线索。</body></html>".encode("utf-8")
            raise AssertionError(f"unexpected fetch url: {url}")

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict("os.environ", self._enabled_env(), clear=True):
            result = tools.web_evidence_fetch(
                "上海交通大学 人工智能 本科专业",
                source_policy="any",
            )

        self.assertEqual(result["status"], "ok")
        page = result["data"]["pages"][0]
        self.assertEqual(page["source_type"], "third_party")
        self.assertEqual(page["confidence"], "low")
        self.assertIn("第三方来源只能作为线索", result["scope_notes"][1])

    def test_rejects_invalid_fetch_limit_before_network_call(self):
        from scripts.retrieval_tools import RetrievalTools

        calls = []

        def fetcher(url, timeout):
            calls.append(url)
            return b'{"results": []}'

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict("os.environ", self._enabled_env(), clear=True):
            result = tools.web_evidence_fetch("上海交通大学 人工智能", fetch_limit=0)

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["needs_clarification"], ["fetch_limit"])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
