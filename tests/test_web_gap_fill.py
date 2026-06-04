import json
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from scripts.retrieval_tools import RetrievalTools


def _enabled_env():
    return {
        "WEB_SEARCH_ENABLED": "true",
        "WEB_SEARCH_PROVIDER": "searxng",
        "SEARXNG_BASE_URL": "http://127.0.0.1:8081",
        "WEB_SEARCH_TIMEOUT_SECONDS": "7",
    }


def _major_school_gap():
    return {
        "gap_key": "major_school_relation",
        "label": "专业开设院校关系",
        "question_type": "major_school_list",
        "missing_fields": ["major_school_relation"],
        "resolvable_by_web": True,
        "preferred_source_types": ["official", "chsi"],
        "evidence_requirements": ["school_name", "major_name_or_code", "source_url", "evidence_snippet"],
        "normalized_slots": {
            "major_name": "人工智能",
            "major_code": "080717T",
            "province_filter": "上海",
            "school_level_filter": "本科",
        },
    }


def test_web_gap_fill_accepts_official_page_evidence_and_rejects_third_party_search_results():
    official_url = "https://zsb.sjtu.edu.cn/major/ai.html"
    third_party_url = "https://example.com/sjtu-ai"
    calls = []

    def fetcher(url, timeout):
        calls.append(url)
        if "/search?" in url:
            query = parse_qs(urlparse(url).query)["q"][0]
            assert "人工智能" in query
            return json.dumps(
                {
                    "results": [
                        {
                            "title": "第三方汇总",
                            "url": third_party_url,
                            "content": "第三方页面说上海交通大学开设人工智能。",
                            "score": 0.99,
                        },
                        {
                            "title": "上海交通大学本科招生专业目录",
                            "url": official_url,
                            "content": "上海交通大学本科招生专业目录包含人工智能。",
                            "score": 0.9,
                        },
                    ]
                },
                ensure_ascii=False,
            ).encode("utf-8")
        if url == official_url:
            return """
            <html><body>
              <h1>上海交通大学本科招生专业目录</h1>
              <p>人工智能专业代码080717T，属于本科招生专业，学制四年，授予工学学士学位。</p>
            </body></html>
            """.encode("utf-8")
        raise AssertionError(f"unexpected fetch url: {url}")

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill(
            [_major_school_gap()],
            question="人工智能专业，上海有哪些本科院校开设？",
            max_rounds=2,
            max_fetches_per_round=3,
        )

    assert result["status"] == "partial"
    assert result["data"]["coverage_status"] == "partial"
    assert result["data"]["unfilled_gaps"][0]["unfilled_reason"] == "list_coverage_incomplete"
    assert result["data"]["filled_items"][0]["school_name"] == "上海交通大学"
    assert result["data"]["accepted_evidence"][0]["source_url"] == official_url
    assert result["data"]["accepted_evidence"][0]["source_type"] == "official"
    assert "人工智能" in result["data"]["accepted_evidence"][0]["evidence_snippet"]
    assert result["data"]["rejected_evidence"][0]["source_url"] == third_party_url
    assert third_party_url not in calls
    assert result["data"]["coverage_summary"]["confirmed_schools"] == [
        result["data"]["filled_items"][0]["school_name"]
    ]


def test_web_gap_fill_returns_not_found_when_only_third_party_results_exist():
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
                            "score": 0.99,
                        }
                    ]
                },
                ensure_ascii=False,
            ).encode("utf-8")
        raise AssertionError("official_only should not fetch third-party pages")

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill([_major_school_gap()], max_rounds=1, max_fetches_per_round=2)

    assert result["status"] == "not_found"
    assert result["data"]["accepted_evidence"] == []
    assert result["data"]["unfilled_gaps"][0]["gap_key"] == "major_school_relation"
    assert result["data"]["unfilled_gaps"][0]["unfilled_reason"] == "no_accepted_official_evidence"
    assert result["data"]["rejected_evidence"][0]["rejection_reason"] == "source_policy_rejected"


def test_web_gap_fill_rejects_unknown_gap_key_before_network_call():
    calls = []

    def fetcher(url, timeout):
        calls.append(url)
        return b'{"results": []}'

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill([{"gap_key": "unknown_gap"}])

    assert result["status"] == "needs_clarification"
    assert result["data"]["unfilled_gaps"][0]["unfilled_reason"] == "unknown_gap_key"
    assert calls == []


def test_web_gap_fill_honors_max_rounds_and_fetches_per_round():
    search_calls = []

    def fetcher(url, timeout):
        if "/search?" in url:
            search_calls.append(url)
            return json.dumps({"results": []}, ensure_ascii=False).encode("utf-8")
        raise AssertionError(f"unexpected fetch url: {url}")

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill([_major_school_gap()], max_rounds=1, max_fetches_per_round=1)

    assert result["status"] == "not_found"
    assert len(search_calls) == 1
    assert len(result["data"]["rounds"]) == 1
    assert len(result["data"]["rounds"][0]["queries"]) == 1


def test_web_gap_fill_continues_regional_major_list_after_first_confirmed_school():
    shu_url = "https://www.shu.edu.cn/ai.html"
    tongji_url = "https://www.tongji.edu.cn/ai.html"
    search_queries = []

    def fetcher(url, timeout):
        if "/search?" in url:
            query = parse_qs(urlparse(url).query)["q"][0]
            search_queries.append(query)
            if len(search_queries) == 1:
                return json.dumps(
                    {
                        "results": [
                            {
                                "title": "上海大学人工智能本科专业",
                                "url": shu_url,
                                "content": "上海大学人工智能本科专业介绍。",
                                "score": 0.95,
                            }
                        ]
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
            if len(search_queries) == 2:
                return json.dumps(
                    {
                        "results": [
                            {
                                "title": "同济大学人工智能本科专业",
                                "url": tongji_url,
                                "content": "同济大学人工智能本科专业介绍。",
                                "score": 0.9,
                            }
                        ]
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
            return json.dumps({"results": []}, ensure_ascii=False).encode("utf-8")
        if url == shu_url:
            return "<html><body><p>上海大学开设人工智能本科专业，专业代码080717T。</p></body></html>".encode("utf-8")
        if url == tongji_url:
            return "<html><body><p>同济大学开设人工智能本科专业，专业代码080717T。</p></body></html>".encode("utf-8")
        raise AssertionError(f"unexpected fetch url: {url}")

    def judge(context):
        url = context["page"]["url"]
        if url == shu_url:
            return {
                "supports_gap": True,
                "confidence": "high",
                "filled_fields": {"school_name": "上海大学", "major_name": "人工智能", "major_code": "080717T", "school_level": "本科"},
                "evidence_quote": "上海大学开设人工智能本科专业，专业代码080717T。",
                "reason": "正文支持。",
                "missing_requirements": [],
                "next_action": "accept",
            }
        if url == tongji_url:
            return {
                "supports_gap": True,
                "confidence": "high",
                "filled_fields": {"school_name": "同济大学", "major_name": "人工智能", "major_code": "080717T", "school_level": "本科"},
                "evidence_quote": "同济大学开设人工智能本科专业，专业代码080717T。",
                "reason": "正文支持。",
                "missing_requirements": [],
                "next_action": "accept",
            }
        raise AssertionError(f"unexpected judge url: {url}")

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher, web_evidence_judge=judge)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill(
            [_major_school_gap()],
            question="人工智能专业，上海有哪些本科院校开设？",
            max_rounds=1,
            max_fetches_per_round=3,
        )

    assert len(search_queries) >= 2
    assert result["status"] == "partial"
    assert result["data"]["coverage_status"] == "partial"
    assert result["data"]["coverage_summary"]["confirmed_schools"] == ["上海大学", "同济大学"]
    assert result["data"]["unfilled_gaps"][0]["unfilled_reason"] == "list_coverage_incomplete"


def test_web_gap_fill_uses_injected_llm_judge_to_accept_body_supported_evidence():
    official_url = "https://zybl.shu.edu.cn/yxshezhi/rgzn.htm"
    body_quote = "人工智能专业代码080717T，属于本科招生专业"
    judge_contexts = []

    def fetcher(url, timeout):
        if "/search?" in url:
            return json.dumps(
                {
                    "results": [
                        {
                            "title": "上海大学人工智能专业介绍",
                            "url": official_url,
                            "content": "上海大学人工智能专业介绍。",
                            "score": 0.95,
                        }
                    ]
                },
                ensure_ascii=False,
            ).encode("utf-8")
        if url == official_url:
            return f"<html><body><p>{body_quote}，学制四年，授予工学学士学位。</p></body></html>".encode("utf-8")
        raise AssertionError(f"unexpected fetch url: {url}")

    def judge(context):
        judge_contexts.append(context)
        assert context["gap_item"]["gap_key"] == "major_school_relation"
        assert body_quote in context["body_text"]
        assert "上海大学人工智能专业介绍" == context["page"]["title"]
        return {
            "supports_gap": True,
            "confidence": "high",
            "filled_fields": {
                "school_name": "上海大学",
                "major_name": "人工智能",
                "major_code": "080717T",
                "school_level": "本科",
            },
            "evidence_quote": body_quote,
            "reason": "正文明确说明上海大学设置人工智能本科专业。",
            "missing_requirements": [],
            "next_action": "accept",
        }

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher, web_evidence_judge=judge)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill([_major_school_gap()], max_rounds=1, max_fetches_per_round=1)

    evidence = result["data"]["accepted_evidence"][0]
    assert result["status"] == "partial"
    assert result["data"]["coverage_status"] == "partial"
    assert result["data"]["unfilled_gaps"][0]["unfilled_reason"] == "list_coverage_incomplete"
    assert evidence["judge_mode"] == "llm"
    assert evidence["judge_quote_verified"] is True
    assert evidence["evidence_snippet"] == body_quote
    assert evidence["school_name"] == "上海大学"
    assert evidence["judge_reason"] == "正文明确说明上海大学设置人工智能本科专业。"
    assert judge_contexts


def test_web_gap_fill_rejects_llm_judge_acceptance_when_quote_is_not_in_body():
    official_url = "https://zsb.sjtu.edu.cn/list.htm"

    def fetcher(url, timeout):
        if "/search?" in url:
            return json.dumps(
                {
                    "results": [
                        {
                            "title": "上海交通大学人工智能学院招生动态",
                            "url": official_url,
                            "content": "上海交通大学人工智能学院招生动态。",
                            "score": 0.91,
                        }
                    ]
                },
                ensure_ascii=False,
            ).encode("utf-8")
        if url == official_url:
            return "<html><body><p>学院新闻列表：本科招生通知、研究生招生通知。</p></body></html>".encode("utf-8")
        raise AssertionError(f"unexpected fetch url: {url}")

    def judge(context):
        return {
            "supports_gap": True,
            "confidence": "high",
            "filled_fields": {"school_name": "上海交通大学", "major_name": "人工智能"},
            "evidence_quote": "人工智能专业代码080717T，属于本科招生专业",
            "reason": "模型声称支持，但引用并不在正文中。",
            "missing_requirements": [],
            "next_action": "accept",
        }

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher, web_evidence_judge=judge)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill([_major_school_gap()], max_rounds=1, max_fetches_per_round=1)

    assert result["status"] == "not_found"
    assert result["data"]["accepted_evidence"] == []
    assert result["data"]["rejected_evidence"][0]["rejection_reason"] == "judge_quote_not_in_body"
    assert result["data"]["rejected_evidence"][0]["judge_mode"] == "llm"
    assert result["data"]["unfilled_gaps"][0]["unfilled_reason"] == "no_accepted_official_evidence"


def test_web_gap_fill_repairs_llm_quote_when_body_contains_equivalent_evidence():
    official_url = "https://zybl.shu.edu.cn/yxshezhi/rgzn.htm"
    body_quote = "人工智能专业为本科招生专业，学制四年，授予工学学士学位。"

    def fetcher(url, timeout):
        if "/search?" in url:
            return json.dumps(
                {
                    "results": [
                        {
                            "title": "上海大学人工智能专业介绍",
                            "url": official_url,
                            "content": "上海大学人工智能专业介绍。",
                            "score": 0.95,
                        }
                    ]
                },
                ensure_ascii=False,
            ).encode("utf-8")
        if url == official_url:
            return f"<html><body><p>{body_quote}</p><p>培养面向智能系统应用的人才。</p></body></html>".encode("utf-8")
        raise AssertionError(f"unexpected fetch url: {url}")

    def judge(context):
        return {
            "supports_gap": True,
            "confidence": "high",
            "filled_fields": {
                "school_name": "上海大学",
                "major_name": "人工智能",
                "major_code": "080717T",
                "school_level": "本科",
            },
            "evidence_quote": "人工智能-上海大学本科招生专业博览网 ... 专业设置 ... 人工智能",
            "reason": "页面支持该缺口，但摘录不是正文逐字原文。",
            "missing_requirements": [],
            "next_action": "accept",
        }

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher, web_evidence_judge=judge)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill([_major_school_gap()], max_rounds=1, max_fetches_per_round=1)

    evidence = result["data"]["accepted_evidence"][0]
    assert result["status"] == "partial"
    assert evidence["judge_quote_verified"] is True
    assert evidence["judge_quote_repaired"] is True
    assert evidence["original_evidence_quote"] == "人工智能-上海大学本科招生专业博览网 ... 专业设置 ... 人工智能"
    assert evidence["evidence_snippet"] == body_quote


def test_web_gap_fill_flattens_nested_llm_judge_filled_fields():
    official_url = "https://zybl.shu.edu.cn/yxshezhi/rgzn.htm"
    body_quote = "上海大学拥有人工智能本科专业"

    def fetcher(url, timeout):
        if "/search?" in url:
            return json.dumps(
                {
                    "results": [
                        {
                            "title": "上海大学人工智能专业介绍",
                            "url": official_url,
                            "content": "上海大学人工智能专业介绍。",
                            "score": 0.95,
                        }
                    ]
                },
                ensure_ascii=False,
            ).encode("utf-8")
        if url == official_url:
            return f"<html><body><p>{body_quote}，专业代码080717T。</p></body></html>".encode("utf-8")
        raise AssertionError(f"unexpected fetch url: {url}")

    def judge(context):
        return {
            "supports_gap": True,
            "confidence": "high",
            "filled_fields": {
                "major_school_relation": {
                    "school_name": "上海大学",
                    "major_name": "人工智能",
                    "major_code": "080717T",
                    "school_level": "本科",
                }
            },
            "evidence_quote": body_quote,
            "reason": "正文支持。",
            "missing_requirements": [],
            "next_action": "accept",
        }

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher, web_evidence_judge=judge)

    with patch.dict("os.environ", _enabled_env(), clear=True):
        result = tools.web_gap_fill([_major_school_gap()], max_rounds=1, max_fetches_per_round=1)

    evidence = result["data"]["accepted_evidence"][0]
    assert evidence["school_name"] == "上海大学"
    assert evidence["major_name"] == "人工智能"
    assert evidence["major_code"] == "080717T"
    assert result["data"]["filled_items"][0]["school_name"] == "上海大学"


def test_web_gap_fill_stops_without_network_when_total_timeout_is_exhausted():
    calls = []

    def fetcher(url, timeout):
        calls.append(url)
        return b'{"results": []}'

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

    with patch.dict("os.environ", _enabled_env(), clear=True), patch(
        "scripts.retrieval_tools.time.monotonic", side_effect=[100.0, 101.0]
    ):
        result = tools.web_gap_fill([_major_school_gap()], max_rounds=2, max_fetches_per_round=2, max_seconds=0.5)

    assert result["status"] == "not_found"
    assert result["data"]["stop_reason"] == "timeout_reached"
    assert result["data"]["unfilled_gaps"][0]["unfilled_reason"] == "timeout_reached"
    assert calls == []
