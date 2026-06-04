import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


def _message(content=None, tool_calls=None):
    return SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls or [])


def _tool_call(call_id, name, arguments):
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(name=name, arguments=arguments),
    )


def _response(message):
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeCompletions:
    def __init__(self, messages):
        self._messages = list(messages)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _response(self._messages.pop(0))


class FakeClient:
    def __init__(self, messages):
        self.completions = FakeCompletions(messages)
        self.chat = SimpleNamespace(completions=self.completions)


class DeepSeekRetrievalAgentTests(unittest.TestCase):
    def test_registers_tools_and_disables_thinking_for_first_pass(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        client = FakeClient([_message(content="最终回答")])
        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "school_lookup"}}],
        )

        result = agent.run("杭电怎么样？")

        self.assertEqual(result, "最终回答")
        call = client.completions.calls[0]
        self.assertEqual(call["model"], "deepseek-v4-pro")
        self.assertEqual(call["tools"][0]["function"]["name"], "school_lookup")
        self.assertEqual(call["tool_choice"], "auto")
        self.assertEqual(call["extra_body"], {"thinking": {"type": "disabled"}})
        self.assertEqual(call["temperature"], 0.1)
        self.assertIn("不要使用 emoji", call["messages"][0]["content"])
        self.assertIn("Markdown", call["messages"][0]["content"])
        self.assertIn("---", call["messages"][0]["content"])
        self.assertIn("志愿填报小导师", call["messages"][0]["content"])
        self.assertIn("先给明确判断", call["messages"][0]["content"])
        self.assertIn("适合什么样的考生", call["messages"][0]["content"])
        self.assertIn("下一步建议", call["messages"][0]["content"])
        self.assertIn("自然、清晰、有人味", call["messages"][0]["content"])
        self.assertIn("帮他收窄选择", call["messages"][0]["content"])
        self.assertIn("直接指出风险", call["messages"][0]["content"])
        self.assertIn("不要长篇解释", call["messages"][0]["content"])
        self.assertIn("不能攻击用户", call["messages"][0]["content"])

        self.assertIn("not_found", call["messages"][0]["content"])
        self.assertIn("needs_clarification", call["messages"][0]["content"])
        self.assertIn("\u4e0d\u8981\u731c\u6d4b\u65b0\u7684\u5b66\u6821\u3001\u4e13\u4e1a\u3001\u5206\u6570\u3001\u4f4d\u6b21\u6216\u5e74\u4efd", call["messages"][0]["content"])
        self.assertIn("school_major_list 不接受 major_text", call["messages"][0]["content"])
        self.assertIn("学校+专业", call["messages"][0]["content"])
        self.assertIn("school_major_profile", call["messages"][0]["content"])
        self.assertIn("major_school_list", call["messages"][0]["content"])
        self.assertIn("web_evidence_fetch 的 search_results", call["messages"][0]["content"])
        self.assertIn("只能使用 pages.evidence_snippets", call["messages"][0]["content"])

    def test_forces_final_answer_after_needs_clarification_without_more_tools(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        tool_call = _tool_call(
            "call_1",
            "major_profile",
            json.dumps({"major_text": "\u8ba1\u7b97\u673a"}, ensure_ascii=False),
        )
        client = FakeClient([
            _message(tool_calls=[tool_call]),
            _message(content="\u8bf7\u5148\u786e\u8ba4\u4f60\u8bf4\u7684\u662f\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f\u3001\u8f6f\u4ef6\u5de5\u7a0b\uff0c\u8fd8\u662f\u8ba1\u7b97\u673a\u7c7b\u3002"),
        ])
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            return {
                "tool_name": name,
                "status": "needs_clarification",
                "needs_clarification": ["major_text"],
                "data": {"candidates": [{"special_name": "\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f"}]},
                "warnings": ["\u4e13\u4e1a\u8f93\u5165\u547d\u4e2d\u591a\u4e2a\u5019\u9009\uff0c\u8bf7\u63d0\u4f9b\u4e13\u4e1a\u5168\u79f0\u6216\u4e13\u4e1a\u4ee3\u7801\u540e\u518d\u67e5\u8be2\u3002"],
                "scope_notes": [],
            }

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "major_profile"}}],
            dispatcher=dispatch,
        )

        result = agent.run("\u676d\u7535\u8ba1\u7b97\u673a\u600e\u4e48\u6837\uff1f")

        self.assertEqual(result, "\u8bf7\u5148\u786e\u8ba4\u4f60\u8bf4\u7684\u662f\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f\u3001\u8f6f\u4ef6\u5de5\u7a0b\uff0c\u8fd8\u662f\u8ba1\u7b97\u673a\u7c7b\u3002")
        self.assertEqual(dispatcher_calls, [("major_profile", {"major_text": "\u8ba1\u7b97\u673a"})])
        self.assertNotIn("tools", client.completions.calls[1])
        self.assertEqual(client.completions.calls[1]["tool_choice"], "none")

    def test_forces_final_answer_after_not_found_without_guessing_new_arguments(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        first_call = _tool_call(
            "call_1",
            "rank_to_school_match",
            json.dumps({"province": "\u6d59\u6c5f", "subject_type": "\u7269\u7406", "score": 580}, ensure_ascii=False),
        )
        client = FakeClient([
            _message(tool_calls=[first_call]),
            _message(content="\u5f53\u524d\u5e93\u6ca1\u6709\u547d\u4e2d\u6d59\u6c5f\u7269\u7406580\u5206\u5bf9\u5e94\u7684\u4e00\u5206\u4e00\u6bb5\u8bb0\u5f55\uff0c\u4e0d\u80fd\u636e\u6b64\u7ed9\u51b2\u7a33\u4fdd\u5b66\u6821\u3002"),
        ])
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            return {
                "tool_name": name,
                "status": "not_found",
                "data": {},
                "warnings": ["\u672c\u5730\u5e93\u672a\u547d\u4e2d\u5bf9\u5e94\u4e00\u5206\u4e00\u6bb5\u8bb0\u5f55\u3002"],
                "scope_notes": [],
                "needs_clarification": [],
            }

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "rank_to_school_match"}}],
            dispatcher=dispatch,
        )

        with patch.dict("os.environ", {"WEB_SEARCH_ENABLED": "false"}, clear=False):
            result = agent.run("\u6d59\u6c5f\u7269\u7406580\u5206\uff0c\u80fd\u4e0a\u54ea\u4e9b\u5b66\u6821\uff1f")

        self.assertIn("\u4e0d\u80fd\u636e\u6b64\u7ed9\u51b2\u7a33\u4fdd\u5b66\u6821", result)
        self.assertEqual(dispatcher_calls, [("rank_to_school_match", {"province": "\u6d59\u6c5f", "subject_type": "\u7269\u7406", "score": 580})])
        self.assertNotIn("tools", client.completions.calls[1])

    def test_auto_runs_web_evidence_search_after_local_not_found_when_enabled(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        first_call = _tool_call(
            "call_1",
            "major_school_list",
            json.dumps({"major_text": "\u4eba\u5de5\u667a\u80fd", "province_filter": "\u4e0a\u6d77"}, ensure_ascii=False),
        )
        client = FakeClient([
            _message(tool_calls=[first_call]),
            _message(content="\u672c\u5730\u5e93\u6ca1\u6709\u547d\u4e2d\uff0c\u4f46\u7f51\u9875\u8bc1\u636e\u663e\u793a\u4e0a\u6d77\u4ea4\u901a\u5927\u5b66\u62db\u751f\u7f51\u6709\u4eba\u5de5\u667a\u80fd\u76f8\u5173\u4fe1\u606f\u3002"),
        ])
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            if name == "major_school_list":
                return {
                    "tool_name": name,
                    "status": "not_found",
                    "input": arguments,
                    "data": {"schools": []},
                    "warnings": ["\u672c\u5730\u5e93\u672a\u547d\u4e2d\u5f00\u8bbe\u8be5\u4e13\u4e1a\u7684\u5b66\u6821\u8bb0\u5f55\u3002"],
                    "scope_notes": ["\u5f00\u8bbe\u5b66\u6821\u5217\u8868\u662f\u672c\u5730\u5b66\u6821\u4e13\u4e1a\u5173\u7cfb\u53e3\u5f84\u3002"],
                    "data_gaps": ["\u5f00\u8bbe\u8be5\u4e13\u4e1a\u7684\u5b66\u6821\u8bb0\u5f55"],
                    "needs_clarification": [],
                    "normalized_slots": {"major_name": "\u4eba\u5de5\u667a\u80fd", "province_filter": "\u4e0a\u6d77"},
                }
            if name == "web_evidence_search":
                return {
                    "tool_name": name,
                    "status": "ok",
                    "input": arguments,
                    "data": {
                        "results": [
                            {
                                "title": "\u4e0a\u6d77\u4ea4\u901a\u5927\u5b66\u4eba\u5de5\u667a\u80fd",
                                "url": "https://zsb.sjtu.edu.cn/example",
                                "source_type": "official",
                                "confidence": "high",
                            }
                        ]
                    },
                    "warnings": [],
                    "scope_notes": ["\u7f51\u9875\u641c\u7d22\u7ed3\u679c\u662f\u5916\u90e8\u5019\u9009\u8bc1\u636e\u3002"],
                    "needs_clarification": [],
                    "data_gaps": [],
                }
            raise AssertionError(f"unexpected tool: {name}")

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[
                {"type": "function", "function": {"name": "major_school_list"}},
                {"type": "function", "function": {"name": "web_evidence_search"}},
            ],
            dispatcher=dispatch,
        )

        with patch.dict(
            "os.environ",
            {
                "WEB_SEARCH_ENABLED": "true",
                "WEB_SEARCH_PROVIDER": "searxng",
                "SEARXNG_BASE_URL": "http://127.0.0.1:8081",
            },
            clear=False,
        ):
            result = agent.run("\u4eba\u5de5\u667a\u80fd\u4e13\u4e1a\uff0c\u4e0a\u6d77\u6709\u54ea\u4e9b\u672c\u79d1\u9662\u6821\u5f00\u8bbe\uff1f")

        self.assertIn("\u7f51\u9875\u8bc1\u636e", result)
        self.assertEqual(dispatcher_calls[0], ("major_school_list", {"major_text": "\u4eba\u5de5\u667a\u80fd", "province_filter": "\u4e0a\u6d77"}))
        self.assertEqual(dispatcher_calls[1][0], "web_evidence_search")
        self.assertIn("\u4eba\u5de5\u667a\u80fd", dispatcher_calls[1][1]["query"])
        self.assertIn("\u4e0a\u6d77", dispatcher_calls[1][1]["query"])
        self.assertEqual(agent.tool_trace[-1]["tool_name"], "web_evidence_search")
        self.assertNotIn("tools", client.completions.calls[1])
        final_messages = client.completions.calls[1]["messages"]
        self.assertTrue(any("https://zsb.sjtu.edu.cn/example" in str(message.get("content")) for message in final_messages))

    def test_auto_runs_web_evidence_fetch_before_search_when_registered(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        first_call = _tool_call(
            "call_1",
            "major_school_list",
            json.dumps({"major_text": "\u4eba\u5de5\u667a\u80fd", "province_filter": "\u4e0a\u6d77"}, ensure_ascii=False),
        )
        client = FakeClient([
            _message(tool_calls=[first_call]),
            _message(content="\u672c\u5730\u5e93\u6ca1\u6709\u547d\u4e2d\uff0c\u5df2\u4f7f\u7528\u5b98\u65b9\u7f51\u9875\u6b63\u6587\u8bc1\u636e\u8865\u5145\u3002"),
        ])
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            if name == "major_school_list":
                return {
                    "tool_name": name,
                    "status": "not_found",
                    "input": arguments,
                    "data": {"schools": []},
                    "warnings": ["\u672c\u5730\u5e93\u672a\u547d\u4e2d\u5f00\u8bbe\u8be5\u4e13\u4e1a\u7684\u5b66\u6821\u8bb0\u5f55\u3002"],
                    "scope_notes": [],
                    "data_gaps": ["\u5f00\u8bbe\u8be5\u4e13\u4e1a\u7684\u5b66\u6821\u8bb0\u5f55"],
                    "needs_clarification": [],
                    "normalized_slots": {"major_name": "\u4eba\u5de5\u667a\u80fd", "province_filter": "\u4e0a\u6d77"},
                }
            if name == "web_evidence_fetch":
                return {
                    "tool_name": name,
                    "status": "ok",
                    "input": arguments,
                    "data": {
                        "pages": [
                            {
                                "title": "\u4e0a\u6d77\u4ea4\u901a\u5927\u5b66\u672c\u79d1\u62db\u751f\u4e13\u4e1a",
                                "url": "https://zsb.sjtu.edu.cn/ai.html",
                                "source_type": "official",
                                "confidence": "high",
                                "evidence_snippets": [
                                    {"text": "\u4eba\u5de5\u667a\u80fd\u65b9\u5411\u9762\u5411\u672c\u79d1\u751f\u57f9\u517b\u3002"}
                                ],
                            }
                        ]
                    },
                    "warnings": [],
                    "scope_notes": ["\u5df2\u6293\u53d6\u7f51\u9875\u6b63\u6587\u5e76\u62bd\u53d6\u8bc1\u636e\u7247\u6bb5\u3002"],
                    "needs_clarification": [],
                    "data_gaps": [],
                }
            raise AssertionError(f"unexpected tool: {name}")

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[
                {"type": "function", "function": {"name": "major_school_list"}},
                {"type": "function", "function": {"name": "web_evidence_search"}},
                {"type": "function", "function": {"name": "web_evidence_fetch"}},
            ],
            dispatcher=dispatch,
        )

        with patch.dict(
            "os.environ",
            {
                "WEB_SEARCH_ENABLED": "true",
                "WEB_SEARCH_PROVIDER": "searxng",
                "SEARXNG_BASE_URL": "http://127.0.0.1:8081",
            },
            clear=False,
        ):
            result = agent.run("\u4eba\u5de5\u667a\u80fd\u4e13\u4e1a\uff0c\u4e0a\u6d77\u6709\u54ea\u4e9b\u672c\u79d1\u9662\u6821\u5f00\u8bbe\uff1f")

        self.assertIn("\u5b98\u65b9\u7f51\u9875\u6b63\u6587\u8bc1\u636e", result)
        self.assertEqual(dispatcher_calls[1][0], "web_evidence_fetch")
        self.assertEqual(dispatcher_calls[1][1]["source_policy"], "official_only")
        self.assertEqual(agent.tool_trace[-1]["tool_name"], "web_evidence_fetch")
        final_messages = client.completions.calls[1]["messages"]
        self.assertTrue(any("https://zsb.sjtu.edu.cn/ai.html" in str(message.get("content")) for message in final_messages))

    def test_auto_runs_web_gap_fill_before_fetch_when_registered(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        first_call = _tool_call(
            "call_1",
            "major_school_list",
            json.dumps({"major_text": "人工智能", "province_filter": "上海"}, ensure_ascii=False),
        )
        client = FakeClient(
            [
                _message(tool_calls=[first_call]),
                _message(content="本地库没有命中，已使用官方网页证据补全已确认部分。"),
            ]
        )
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            if name == "major_school_list":
                return {
                    "tool_name": name,
                    "status": "not_found",
                    "input": arguments,
                    "data": {"major": {"special_name": "人工智能", "code": "080717T"}, "schools": []},
                    "warnings": ["本地库未命中开设该专业的学校记录。"],
                    "scope_notes": [],
                    "data_gaps": ["开设该专业的学校记录"],
                    "needs_clarification": [],
                    "normalized_slots": {
                        "major_name": "人工智能",
                        "major_code": "080717T",
                        "province_filter": "上海",
                        "school_level_filter": "本科",
                    },
                }
            if name == "web_gap_fill":
                return {
                    "tool_name": name,
                    "status": "ok",
                    "input": arguments,
                    "data": {
                        "filled_items": [
                            {
                                "school_name": "上海交通大学",
                                "major_name": "人工智能",
                                "source_url": "https://zsb.sjtu.edu.cn/ai.html",
                            }
                        ],
                        "accepted_evidence": [
                            {
                                "school_name": "上海交通大学",
                                "major_name": "人工智能",
                                "source_url": "https://zsb.sjtu.edu.cn/ai.html",
                                "source_type": "official",
                                "evidence_snippet": "人工智能专业代码080717T，属于本科招生专业。",
                            }
                        ],
                        "rejected_evidence": [],
                        "unfilled_gaps": [],
                    },
                    "warnings": [],
                    "scope_notes": ["网页缺口补全只接受抓取正文后通过证据评估的页面。"],
                    "needs_clarification": [],
                    "data_gaps": [],
                }
            raise AssertionError(f"unexpected tool: {name}")

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[
                {"type": "function", "function": {"name": "major_school_list"}},
                {"type": "function", "function": {"name": "web_evidence_search"}},
                {"type": "function", "function": {"name": "web_evidence_fetch"}},
                {"type": "function", "function": {"name": "web_gap_fill"}},
            ],
            dispatcher=dispatch,
        )

        with patch.dict(
            "os.environ",
            {
                "WEB_SEARCH_ENABLED": "true",
                "WEB_SEARCH_PROVIDER": "searxng",
                "SEARXNG_BASE_URL": "http://127.0.0.1:8081",
            },
            clear=False,
        ):
            result = agent.run("人工智能专业，上海有哪些本科院校开设？")

        self.assertIn("官方网页证据", result)
        self.assertEqual(dispatcher_calls[1][0], "web_gap_fill")
        self.assertEqual(dispatcher_calls[1][1]["source_policy"], "official_only")
        self.assertEqual(dispatcher_calls[1][1]["gap_items"][0]["gap_key"], "major_school_relation")
        self.assertEqual(dispatcher_calls[1][1]["gap_items"][0]["normalized_slots"]["province_filter"], "上海")
        self.assertEqual(agent.tool_trace[-1]["tool_name"], "web_gap_fill")
        final_messages = client.completions.calls[1]["messages"]
        self.assertTrue(any("accepted_evidence" in str(message.get("content")) for message in final_messages))

    def test_direct_web_fetch_after_structured_gap_is_redirected_to_web_gap_fill(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        local_call = _tool_call(
            "call_1",
            "major_school_list",
            json.dumps({"major_text": "人工智能", "province_filter": "上海"}, ensure_ascii=False),
        )
        fetch_call = _tool_call(
            "call_2",
            "web_evidence_fetch",
            json.dumps({"query": "人工智能 上海 本科 开设", "source_policy": "official_only"}, ensure_ascii=False),
        )
        client = FakeClient(
            [
                _message(tool_calls=[local_call, fetch_call]),
                _message(content="已改用结构化网页缺口补全。"),
            ]
        )
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            if name == "major_school_list":
                return {
                    "tool_name": name,
                    "status": "not_found",
                    "input": arguments,
                    "data": {"major": {"special_name": "人工智能", "code": "080717T"}, "schools": []},
                    "warnings": ["本地库未命中开设该专业的学校记录。"],
                    "scope_notes": [],
                    "data_gaps": ["开设该专业的学校记录"],
                    "needs_clarification": [],
                    "normalized_slots": {
                        "major_name": "人工智能",
                        "major_code": "080717T",
                        "province_filter": "上海",
                        "school_level_filter": "本科",
                    },
                }
            if name == "web_gap_fill":
                return {
                    "tool_name": name,
                    "status": "partial",
                    "input": arguments,
                    "data": {
                        "filled_items": [],
                        "accepted_evidence": [],
                        "rejected_evidence": [],
                        "unfilled_gaps": [
                            {
                                "gap_key": "major_school_relation",
                                "unfilled_reason": "list_coverage_incomplete",
                            }
                        ],
                        "coverage_status": "partial",
                    },
                    "warnings": [],
                    "scope_notes": ["网页缺口补全只接受抓取正文后通过证据评估的页面。"],
                    "needs_clarification": [],
                    "data_gaps": ["专业开设院校关系"],
                }
            raise AssertionError(f"unexpected tool: {name}")

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[
                {"type": "function", "function": {"name": "major_school_list"}},
                {"type": "function", "function": {"name": "web_evidence_fetch"}},
                {"type": "function", "function": {"name": "web_gap_fill"}},
            ],
            dispatcher=dispatch,
        )

        with patch.dict(
            "os.environ",
            {
                "WEB_SEARCH_ENABLED": "true",
                "WEB_SEARCH_PROVIDER": "searxng",
                "SEARXNG_BASE_URL": "http://127.0.0.1:8081",
            },
            clear=False,
        ):
            result = agent.run("人工智能专业，上海有哪些本科院校开设？")

        self.assertIn("结构化网页缺口补全", result)
        self.assertEqual(dispatcher_calls[1][0], "web_gap_fill")
        self.assertEqual(dispatcher_calls[1][1]["source_policy"], "official_only")
        self.assertEqual(dispatcher_calls[1][1]["gap_items"][0]["gap_key"], "major_school_relation")
        self.assertEqual(agent.tool_trace[1]["tool_name"], "web_gap_fill")
        self.assertEqual(agent.tool_trace[1]["redirected_from"], "web_evidence_fetch")

    def test_partial_web_gap_fill_answer_does_not_claim_complete_school_list(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        first_call = _tool_call(
            "call_1",
            "major_school_list",
            json.dumps({"major_text": "人工智能", "province_filter": "上海"}, ensure_ascii=False),
        )
        client = FakeClient(
            [
                _message(tool_calls=[first_call]),
                _message(content="目前能确认的上海本科层次开设人工智能专业的高校只有一所：上海大学。"),
            ]
        )
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            if name == "major_school_list":
                return {
                    "tool_name": name,
                    "status": "not_found",
                    "input": arguments,
                    "data": {"major": {"special_name": "人工智能", "code": "080717T"}, "schools": []},
                    "warnings": ["本地库未命中开设该专业的学校记录。"],
                    "scope_notes": [],
                    "data_gaps": ["开设该专业的学校记录"],
                    "needs_clarification": [],
                    "normalized_slots": {
                        "major_name": "人工智能",
                        "major_code": "080717T",
                        "province_filter": "上海",
                        "school_level_filter": "本科",
                    },
                }
            if name == "web_gap_fill":
                return {
                    "tool_name": name,
                    "status": "partial",
                    "input": arguments,
                    "data": {
                        "filled_items": [
                            {
                                "school_name": "上海大学",
                                "major_name": "人工智能",
                                "source_url": "https://zybl.shu.edu.cn/rgzn.htm",
                            }
                        ],
                        "accepted_evidence": [
                            {
                                "school_name": "上海大学",
                                "major_name": "人工智能",
                                "source_url": "https://zybl.shu.edu.cn/rgzn.htm",
                                "source_type": "official",
                                "evidence_snippet": "人工智能-上海大学本科招生专业博览网",
                            }
                        ],
                        "rejected_evidence": [],
                        "unfilled_gaps": [
                            {
                                "gap_key": "major_school_relation",
                                "unfilled_reason": "list_coverage_incomplete",
                            }
                        ],
                        "coverage_status": "partial",
                        "coverage_summary": {"confirmed_schools": ["上海大学"]},
                    },
                    "warnings": [],
                    "scope_notes": ["网页缺口补全只接受抓取正文后通过证据评估的页面。"],
                    "needs_clarification": [],
                    "data_gaps": ["专业开设院校关系"],
                }
            raise AssertionError(f"unexpected tool: {name}")

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[
                {"type": "function", "function": {"name": "major_school_list"}},
                {"type": "function", "function": {"name": "web_gap_fill"}},
            ],
            dispatcher=dispatch,
        )

        with patch.dict(
            "os.environ",
            {
                "WEB_SEARCH_ENABLED": "true",
                "WEB_SEARCH_PROVIDER": "searxng",
                "SEARXNG_BASE_URL": "http://127.0.0.1:8081",
            },
            clear=False,
        ):
            result = agent.run("人工智能专业，上海有哪些本科院校开设？")

        self.assertIn("本轮只确认到一所", result)
        self.assertNotIn("只有一所", result)
        self.assertIn("不代表完整名单", result)
        self.assertEqual(dispatcher_calls[1][0], "web_gap_fill")
        final_instruction = client.completions.calls[1]["messages"][-1]["content"]
        self.assertIn("coverage_status", final_instruction)
        self.assertIn("list_coverage_incomplete", final_instruction)

    def test_unfilled_web_gap_labels_are_disclaimed_in_final_answer(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        first_call = _tool_call(
            "call_1",
            "web_gap_fill",
            json.dumps(
                {
                    "gap_items": [
                        {
                            "gap_key": "language_limit",
                            "label": "外语语种限制",
                            "question_type": "policy_rule_lookup",
                            "missing_fields": ["language_limit"],
                        }
                    ],
                    "question": "浙江大学2025年本科招生章程里，对外语语种有没有限制？",
                },
                ensure_ascii=False,
            ),
        )
        client = FakeClient(
            [
                _message(tool_calls=[first_call]),
                _message(content="浙江大学2025年没有外语语种限制。"),
            ]
        )

        def dispatch(name, arguments):
            return {
                "tool_name": name,
                "status": "partial",
                "input": arguments,
                "data": {
                    "filled_items": [
                        {
                            "gap_key": "official_admission_rule",
                            "label": "官方招生章程原文",
                            "source_url": "https://zdzsc.zju.edu.cn/rule.htm",
                        }
                    ],
                    "accepted_evidence": [],
                    "rejected_evidence": [],
                    "unfilled_gaps": [
                        {
                            "gap_key": "language_limit",
                            "label": "外语语种限制",
                            "unfilled_reason": "no_accepted_official_evidence",
                        }
                    ],
                },
                "warnings": [],
                "scope_notes": [],
                "needs_clarification": [],
                "data_gaps": ["外语语种限制"],
            }

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "web_gap_fill"}}],
            dispatcher=dispatch,
        )

        result = agent.run("浙江大学2025年本科招生章程里，对外语语种有没有限制？")

        self.assertIn("外语语种限制", result)
        self.assertIn("不能作为已核验结论", result)

    def test_forces_final_answer_after_answer_tool_succeeds(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        tool_call = _tool_call(
            "call_1",
            "major_school_list",
            json.dumps({"major_text": "\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f", "province_filter": "\u6d59\u6c5f"}, ensure_ascii=False),
        )
        client = FakeClient([
            _message(tool_calls=[tool_call]),
            _message(content="\u6d59\u6c5f\u5f00\u8bbe\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f\u7684\u5b66\u6821\u5df2\u6309\u672c\u5730\u5e93\u6574\u7406\u3002"),
        ])

        def dispatch(name, arguments):
            return {
                "tool_name": name,
                "status": "ok",
                "data": {"schools": [{"name": "\u6d59\u6c5f\u5de5\u4e1a\u5927\u5b66"}]},
                "warnings": [],
                "scope_notes": [],
                "needs_clarification": [],
            }

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "major_school_list"}}],
            dispatcher=dispatch,
        )

        result = agent.run("\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f\uff0c\u6d59\u6c5f\u6709\u54ea\u4e9b\u5b66\u6821\u5f00\u8bbe\uff1f")

        self.assertEqual(result, "\u6d59\u6c5f\u5f00\u8bbe\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f\u7684\u5b66\u6821\u5df2\u6309\u672c\u5730\u5e93\u6574\u7406\u3002")
        self.assertNotIn("tools", client.completions.calls[1])

    def test_lookup_only_success_can_continue_to_answer_tool(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        lookup_call = _tool_call("call_1", "school_lookup", json.dumps({"school_text": "\u676d\u7535"}, ensure_ascii=False))
        list_call = _tool_call(
            "call_2",
            "school_major_list",
            json.dumps({"school_text": "\u676d\u5dde\u7535\u5b50\u79d1\u6280\u5927\u5b66"}, ensure_ascii=False),
        )
        client = FakeClient([
            _message(tool_calls=[lookup_call]),
            _message(tool_calls=[list_call]),
            _message(content="\u676d\u7535\u5f00\u8bbe\u4e13\u4e1a\u5217\u8868\u5df2\u6574\u7406\u3002"),
        ])
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            status_data = {
                "school_lookup": {"selected_school": {"name": "\u676d\u5dde\u7535\u5b50\u79d1\u6280\u5927\u5b66"}},
                "school_major_list": {"majors": [{"major_name": "\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f"}]},
            }
            return {
                "tool_name": name,
                "status": "ok",
                "data": status_data[name],
                "warnings": [],
                "scope_notes": [],
                "needs_clarification": [],
            }

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[
                {"type": "function", "function": {"name": "school_lookup"}},
                {"type": "function", "function": {"name": "school_major_list"}},
            ],
            dispatcher=dispatch,
        )

        result = agent.run("\u676d\u7535\u6709\u54ea\u4e9b\u4e13\u4e1a\uff1f")

        self.assertEqual(result, "\u676d\u7535\u5f00\u8bbe\u4e13\u4e1a\u5217\u8868\u5df2\u6574\u7406\u3002")
        self.assertEqual(
            dispatcher_calls,
            [
                ("school_lookup", {"school_text": "\u676d\u7535"}),
                ("school_major_list", {"school_text": "\u676d\u5dde\u7535\u5b50\u79d1\u6280\u5927\u5b66"}),
            ],
        )
        self.assertIn("tools", client.completions.calls[1])
        self.assertNotIn("tools", client.completions.calls[2])

    def test_skips_excess_tool_calls_in_one_model_round(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        tool_calls = [
            _tool_call("call_1", "school_lookup", json.dumps({"school_text": "\u676d\u7535"}, ensure_ascii=False)),
            _tool_call("call_2", "major_lookup", json.dumps({"major_text": "\u8ba1\u7b97\u673a"}, ensure_ascii=False)),
            _tool_call("call_3", "school_major_list", json.dumps({"school_text": "\u676d\u7535"}, ensure_ascii=False)),
        ]
        client = FakeClient([
            _message(tool_calls=tool_calls),
            _message(content="\u5de5\u5177\u8bf7\u6c42\u8fc7\u591a\uff0c\u5df2\u57fa\u4e8e\u5df2\u6709\u7ed3\u679c\u6536\u53e3\u3002"),
        ])
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            return {
                "tool_name": name,
                "status": "ok",
                "data": {},
                "warnings": [],
                "scope_notes": [],
                "needs_clarification": [],
            }

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[
                {"type": "function", "function": {"name": "school_lookup"}},
                {"type": "function", "function": {"name": "major_lookup"}},
                {"type": "function", "function": {"name": "school_major_list"}},
            ],
            dispatcher=dispatch,
            max_tool_calls_per_round=1,
        )

        result = agent.run("\u676d\u7535\u8ba1\u7b97\u673a\u5927\u7c7b\u5206\u6d41\u98ce\u9669\u5927\u5417\uff1f")

        self.assertIn("\u5df2\u57fa\u4e8e\u5df2\u6709\u7ed3\u679c\u6536\u53e3", result)
        self.assertEqual(dispatcher_calls, [("school_lookup", {"school_text": "\u676d\u7535"})])
        self.assertEqual([item["result"]["status"] for item in agent.tool_trace], ["ok", "skipped", "skipped"])
        self.assertNotIn("tools", client.completions.calls[1])

    def test_temperature_can_be_overridden_for_style_experiments(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        client = FakeClient([_message(content="最终回答")])
        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "school_lookup"}}],
            temperature=0.0,
        )

        agent.run("杭电怎么样？")

        self.assertEqual(client.completions.calls[0]["temperature"], 0.0)

    def test_executes_tool_call_and_sends_tool_result_back_to_model(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        tool_call = _tool_call(
            "call_1",
            "school_lookup",
            json.dumps({"school_text": "杭电"}, ensure_ascii=False),
        )
        client = FakeClient([
            _message(tool_calls=[tool_call]),
            _message(content="杭电的工具结果已经整理好了。"),
        ])
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            return {
                "tool_name": name,
                "status": "ok",
                "data": {"selected_school": {"name": "杭州电子科技大学"}},
                "warnings": [],
                "scope_notes": [],
            }

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "school_lookup"}}],
            dispatcher=dispatch,
        )

        result = agent.run("杭电怎么样？")

        self.assertEqual(result, "杭电的工具结果已经整理好了。")
        self.assertEqual(dispatcher_calls, [("school_lookup", {"school_text": "杭电"})])
        second_messages = client.completions.calls[1]["messages"]
        tool_messages = [message for message in second_messages if message.get("role") == "tool"]
        self.assertEqual(tool_messages[0]["tool_call_id"], "call_1")
        payload = json.loads(tool_messages[0]["content"])
        self.assertEqual(payload["data"]["selected_school"]["name"], "杭州电子科技大学")

    def test_invalid_tool_arguments_are_returned_as_tool_error_without_dispatching(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        tool_call = _tool_call("call_bad", "school_lookup", "{bad json")
        client = FakeClient([
            _message(tool_calls=[tool_call]),
            _message(content="我需要你重新提供学校名称。"),
        ])

        def dispatch(name, arguments):  # pragma: no cover - should not be called
            raise AssertionError("dispatcher should not receive invalid JSON arguments")

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "school_lookup"}}],
            dispatcher=dispatch,
        )

        result = agent.run("查一下")

        self.assertEqual(result, "我需要你重新提供学校名称。")
        tool_message = [
            message for message in client.completions.calls[1]["messages"] if message.get("role") == "tool"
        ][0]
        payload = json.loads(tool_message["content"])
        self.assertEqual(payload["tool_name"], "school_lookup")
        self.assertEqual(payload["status"], "error")
        self.assertIn("not valid JSON", payload["warnings"][0])

    def test_load_env_file_reads_deepseek_api_key_placeholder_location(self):
        from scripts.deepseek_retrieval_agent import load_env_file

        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text('DEEPSEEK_API_KEY="sk-test"\nOTHER=value\n', encoding="utf-8")

            values = load_env_file(env_path)

        self.assertEqual(values["DEEPSEEK_API_KEY"], "sk-test")
        self.assertEqual(values["OTHER"], "value")

    def test_placeholder_api_key_is_not_accepted_as_configured(self):
        from scripts.deepseek_retrieval_agent import resolve_deepseek_api_key

        with self.assertRaisesRegex(RuntimeError, "fill in DEEPSEEK_API_KEY"):
            resolve_deepseek_api_key("your_deepseek_api_key_here")

    def test_configure_utf8_stdio_reconfigures_print_streams(self):
        from scripts.deepseek_retrieval_agent import configure_utf8_stdio

        class FakeStream:
            def __init__(self):
                self.calls = []

            def reconfigure(self, **kwargs):
                self.calls.append(kwargs)

        stdout = FakeStream()
        stderr = FakeStream()

        configure_utf8_stdio(stdout=stdout, stderr=stderr)

        self.assertEqual(stdout.calls, [{"encoding": "utf-8"}])
        self.assertEqual(stderr.calls, [{"encoding": "utf-8"}])

    def test_clean_answer_text_removes_decorative_markdown_and_emoji(self):
        from scripts.deepseek_retrieval_agent import clean_answer_text

        raw = "## 🏫 学校定位\n\n---\n\n杭电**计算机**不错。\n"

        self.assertEqual(clean_answer_text(raw), "学校定位\n\n杭电计算机不错。")


if __name__ == "__main__":
    unittest.main()
