import json
import unittest
from unittest.mock import patch


class WebEvidenceSearchTests(unittest.TestCase):
    def test_requires_enabled_searxng_configuration_before_network_call(self):
        from scripts.retrieval_tools import RetrievalTools

        calls = []

        def fetcher(url, timeout):
            calls.append((url, timeout))
            return b'{"results": []}'

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict("os.environ", {}, clear=True):
            result = tools.web_evidence_search("杭州电子科技大学 招生章程 单科限制")

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["needs_clarification"], ["WEB_SEARCH_ENABLED", "SEARXNG_BASE_URL"])
        self.assertEqual(calls, [])
        self.assertIn("SearXNG", result["warnings"][0])

    def test_queries_searxng_json_and_normalizes_results(self):
        from scripts.retrieval_tools import RetrievalTools

        captured_urls = []

        def fetcher(url, timeout):
            captured_urls.append(url)
            payload = {
                "results": [
                    {
                        "title": "杭州电子科技大学2025年普通高校招生章程",
                        "url": "https://zhaosheng.hdu.edu.cn/2025/notice.html",
                        "content": "杭州电子科技大学发布2025年普通高校招生章程。",
                        "score": 0.92,
                        "category": "general",
                    },
                    {
                        "title": "第三方汇总页",
                        "url": "https://example.com/hdu",
                        "content": "非官方转载信息。",
                    },
                ]
            }
            return json.dumps(payload, ensure_ascii=False).encode("utf-8")

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict(
            "os.environ",
            {
                "WEB_SEARCH_ENABLED": "true",
                "WEB_SEARCH_PROVIDER": "searxng",
                "SEARXNG_BASE_URL": "http://127.0.0.1:8080",
                "WEB_SEARCH_TIMEOUT_SECONDS": "7",
            },
            clear=True,
        ):
            result = tools.web_evidence_search(
                "杭州电子科技大学 招生章程 单科限制",
                search_scope="official",
                domains=["hdu.edu.cn"],
                limit=2,
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["normalized_slots"]["provider"], "searxng")
        self.assertEqual(result["normalized_slots"]["limit"], 2)
        self.assertEqual(len(result["data"]["results"]), 2)
        first = result["data"]["results"][0]
        self.assertEqual(first["title"], "杭州电子科技大学2025年普通高校招生章程")
        self.assertEqual(first["source_type"], "official")
        self.assertEqual(first["confidence"], "high")
        self.assertEqual(captured_urls[0].split("?", 1)[0], "http://127.0.0.1:8080/search")
        self.assertIn("format=json", captured_urls[0])
        self.assertIn("site%3Ahdu.edu.cn", captured_urls[0])

    def test_returns_not_found_when_searxng_has_no_results(self):
        from scripts.retrieval_tools import RetrievalTools

        def fetcher(url, timeout):
            return b'{"results": []}'

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict(
            "os.environ",
            {
                "WEB_SEARCH_ENABLED": "true",
                "WEB_SEARCH_PROVIDER": "searxng",
                "SEARXNG_BASE_URL": "http://127.0.0.1:8080",
            },
            clear=True,
        ):
            result = tools.web_evidence_search("不存在的查询", limit=3)

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["data"]["results"], [])
        self.assertEqual(result["data_gaps"], ["external_web_evidence"])

    def test_rejects_invalid_limit_before_network_call(self):
        from scripts.retrieval_tools import RetrievalTools

        calls = []

        def fetcher(url, timeout):
            calls.append(url)
            return b'{"results": []}'

        tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

        with patch.dict(
            "os.environ",
            {
                "WEB_SEARCH_ENABLED": "true",
                "WEB_SEARCH_PROVIDER": "searxng",
                "SEARXNG_BASE_URL": "http://127.0.0.1:8080",
            },
            clear=True,
        ):
            result = tools.web_evidence_search("杭州电子科技大学", limit=0)

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["needs_clarification"], ["limit"])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
