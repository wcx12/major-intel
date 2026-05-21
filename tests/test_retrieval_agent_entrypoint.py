import unittest


class FakeRuleEntryPoint:
    """Small rule-router fake for testing the hybrid entrypoint boundary.

    These tests should not touch MySQL or a real LLM.  The production rule
    router already has its own tests, so this fake only records whether the
    hybrid layer asks the rule router to plan/execute a question.
    """

    def __init__(self, result):
        self.result = result
        self.calls = []

    def run(self, question, session_context=None, *, execute=True):
        self.calls.append((question, session_context or {}, execute))
        return self.result


class TwoPhaseRuleEntryPoint:
    """Rule fake that returns a preflight plan first and a full result later."""

    def __init__(self, preflight_result, executed_result):
        self.preflight_result = preflight_result
        self.executed_result = executed_result
        self.calls = []

    def run(self, question, session_context=None, *, execute=True):
        self.calls.append((question, session_context or {}, execute))
        return self.executed_result if execute else self.preflight_result


class FakeDeepSeekAgent:
    """LLM-agent fake that exposes the same tiny surface as DeepSeekRetrievalAgent."""

    def __init__(self, answer="DeepSeek answer"):
        self.answer = answer
        self.calls = []
        self.tool_trace = [
            {
                "tool_name": "school_lookup",
                "arguments": {"school_text": "杭电"},
                "result": {"status": "ok", "warnings": [], "scope_notes": [], "data_gaps": []},
            }
        ]

    def run(self, question):
        self.calls.append(question)
        return self.answer


class MemoryAgentStorage:
    """In-memory cache/log store used to test entrypoint persistence behavior."""

    def __init__(self):
        self.cache = {}
        self.cache_writes = []
        self.logs = []
        self.traces = []
        self.gaps = []

    def get_cached_result(self, cache_key):
        return self.cache.get(cache_key)

    def save_cached_result(self, cache_key, cache_source, result, ttl_seconds=None):
        self.cache[cache_key] = result
        self.cache_writes.append((cache_key, cache_source, result, ttl_seconds))

    def write_query_log(self, record):
        query_log_id = f"log_{len(self.logs) + 1}"
        self.logs.append(record | {"id": query_log_id})
        return query_log_id

    def write_tool_traces(self, query_log_id, tool_trace):
        for index, trace in enumerate(tool_trace):
            self.traces.append((query_log_id, index, trace))

    def write_data_gap_items(self, items):
        self.gaps.extend(items)


class HybridRetrievalEntryPointTests(unittest.TestCase):
    def test_auto_mode_returns_rule_result_for_high_confidence_question(self):
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        rule_result = {
            "status": "ok",
            "intent": "rank_to_major_match",
            "tool_plan": [{"tool_name": "rank_to_major_match", "arguments": {"score": 580}}],
            "tool_trace": [],
            "answer_markdown": "规则入口结果",
        }
        rule_entrypoint = FakeRuleEntryPoint(rule_result)
        deepseek_factory_calls = []

        def deepseek_factory():  # pragma: no cover - should not be called
            deepseek_factory_calls.append(True)
            return FakeDeepSeekAgent()

        result = HybridRetrievalEntryPoint(
            rule_entrypoint=rule_entrypoint,
            deepseek_agent_factory=deepseek_factory,
        ).run("广东物理 580 想学计算机")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["route"], "rules")
        self.assertEqual(result["intent"], "rank_to_major_match")
        self.assertEqual(result["answer_markdown"], "规则入口结果")
        self.assertEqual(rule_entrypoint.calls, [("广东物理 580 想学计算机", {}, True)])
        self.assertEqual(deepseek_factory_calls, [])

    def test_auto_mode_returns_rule_clarification_without_calling_llm(self):
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        rule_result = {
            "status": "needs_clarification",
            "intent": "rank_to_school_match",
            "needs_clarification": ["province", "subject_type"],
            "tool_plan": [],
            "tool_trace": [],
            "answer_markdown": "还需要补充省份、科类。",
        }
        deepseek_factory_calls = []

        result = HybridRetrievalEntryPoint(
            rule_entrypoint=FakeRuleEntryPoint(rule_result),
            deepseek_agent_factory=lambda: deepseek_factory_calls.append(True),
        ).run("45000 位次能冲什么？")

        self.assertEqual(result["route"], "rules")
        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["needs_clarification"], ["province", "subject_type"])
        self.assertEqual(deepseek_factory_calls, [])

    def test_auto_mode_falls_back_to_deepseek_for_unknown_or_complex_question(self):
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        rule_result = {
            "status": "needs_clarification",
            "intent": "unknown",
            "needs_clarification": ["intent"],
            "tool_plan": [],
            "tool_trace": [],
            "answer_markdown": "这个问题还需要补充具体意图。",
        }
        agent = FakeDeepSeekAgent(answer="我会先帮你拆成可检索问题。")

        result = HybridRetrievalEntryPoint(
            rule_entrypoint=FakeRuleEntryPoint(rule_result),
            deepseek_agent_factory=lambda: agent,
        ).run("我有点迷茫，不知道怎么选城市和专业")

        self.assertEqual(result["route"], "deepseek")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["answer_markdown"], "我会先帮你拆成可检索问题。")
        self.assertEqual(result["rule_preflight"]["intent"], "unknown")
        self.assertEqual(result["tool_trace"], agent.tool_trace)
        self.assertEqual(agent.calls, ["我有点迷茫，不知道怎么选城市和专业"])

    def test_deepseek_mode_skips_rule_preflight(self):
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        rule_entrypoint = FakeRuleEntryPoint({"status": "ok", "intent": "school_profile"})
        agent = FakeDeepSeekAgent(answer="直接使用 DeepSeek。")

        result = HybridRetrievalEntryPoint(
            rule_entrypoint=rule_entrypoint,
            deepseek_agent_factory=lambda: agent,
        ).run("杭电怎么样？", mode="deepseek")

        self.assertEqual(result["route"], "deepseek")
        self.assertEqual(result["rule_preflight"], None)
        self.assertEqual(rule_entrypoint.calls, [])

    def test_rules_mode_never_calls_deepseek(self):
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        rule_result = {
            "status": "ok",
            "intent": "comparison_query",
            "tool_plan": [{"tool_name": "comparison_query", "arguments": {"target_type": "school", "target_texts": ["杭电", "浙大"]}}],
            "tool_trace": [],
            "answer_markdown": "结构化对比结果。",
        }
        result = HybridRetrievalEntryPoint(
            rule_entrypoint=FakeRuleEntryPoint(rule_result),
            deepseek_agent_factory=lambda: (_ for _ in ()).throw(AssertionError("should not call DeepSeek")),
        ).run("杭电和浙大怎么选？", mode="rules")

        self.assertEqual(result["route"], "rules")
        self.assertEqual(result["intent"], "comparison_query")

    def test_auto_mode_keeps_implemented_comparison_query_in_rules(self):
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        rule_result = {
            "status": "ok",
            "intent": "comparison_query",
            "tool_plan": [{"tool_name": "comparison_query", "arguments": {"target_type": "school", "target_texts": ["杭电", "浙大"]}}],
            "tool_trace": [
                {
                    "tool_name": "comparison_query",
                    "arguments": {"target_type": "school", "target_texts": ["杭电", "浙大"]},
                    "result": {"status": "ok", "warnings": [], "scope_notes": [], "data_gaps": []},
                }
            ],
            "answer_markdown": "结构化对比结果。",
        }

        result = HybridRetrievalEntryPoint(
            rule_entrypoint=FakeRuleEntryPoint(rule_result),
            deepseek_agent_factory=lambda: (_ for _ in ()).throw(AssertionError("should not call DeepSeek")),
        ).run("杭电和浙大怎么选？")

        self.assertEqual(result["route"], "rules")
        self.assertEqual(result["intent"], "comparison_query")
        self.assertEqual(result["answer_markdown"], "结构化对比结果。")

    def test_storage_records_cache_logs_and_tool_traces_on_miss(self):
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        preflight = {
            "status": "planned",
            "intent": "rank_to_major_match",
            "slots": {"province": "广东", "subject_type": "物理", "score": 580, "major_text": "计算机"},
            "tool_plan": [{"tool_name": "rank_to_major_match", "arguments": {"score": 580}}],
            "tool_trace": [],
            "answer_markdown": "计划",
        }
        executed = {
            **preflight,
            "status": "ok",
            "tool_trace": [
                {
                    "tool_name": "rank_to_major_match",
                    "arguments": {"score": 580},
                    "result": {"status": "ok", "warnings": [], "scope_notes": [], "data_gaps": []},
                }
            ],
            "answer_markdown": "执行结果",
        }
        storage = MemoryAgentStorage()
        rule_entrypoint = TwoPhaseRuleEntryPoint(preflight, executed)

        result = HybridRetrievalEntryPoint(rule_entrypoint=rule_entrypoint, storage=storage).run(
            "广东物理 580 想学计算机",
            session_id="s1",
        )

        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["cache_hit"])
        self.assertEqual(rule_entrypoint.calls[-1], ("广东物理 580 想学计算机", {}, True))
        self.assertEqual(len(storage.cache_writes), 1)
        self.assertEqual(storage.logs[0]["session_id"], "s1")
        self.assertEqual(storage.logs[0]["cache_hit"], False)
        self.assertEqual(storage.logs[0]["result"]["answer_markdown"], "执行结果")
        self.assertEqual(storage.traces[0][2]["tool_name"], "rank_to_major_match")
        self.assertEqual(storage.gaps, [])

    def test_storage_writes_data_gap_queue_items_when_result_has_gaps(self):
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        preflight = {
            "status": "planned",
            "intent": "rank_to_major_match",
            "slots": {"province": "广东", "subject_type": "物理", "score": 580, "major_text": "计算机"},
            "tool_plan": [{"tool_name": "rank_to_major_match", "arguments": {"score": 580}}],
            "tool_trace": [],
            "answer_markdown": "计划",
        }
        executed = {
            **preflight,
            "status": "not_found",
            "data_gaps": ["本地专业录取历史"],
            "warnings": ["缺 2025 年广东物理计算机方向样本。"],
            "answer_markdown": "本地库暂时没有足够数据。",
        }
        storage = MemoryAgentStorage()

        result = HybridRetrievalEntryPoint(
            rule_entrypoint=TwoPhaseRuleEntryPoint(preflight, executed),
            storage=storage,
        ).run("广东物理 580 想学计算机", session_id="s_gap")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(len(storage.gaps), 1)
        self.assertEqual(storage.gaps[0]["query_log_id"], "log_1")
        self.assertEqual(storage.gaps[0]["session_id"], "s_gap")
        self.assertEqual(storage.gaps[0]["question_type"], "rank_to_major_match")
        self.assertEqual(storage.gaps[0]["missing_fields"], ["本地专业录取历史"])
        self.assertEqual(storage.gaps[0]["status"], "pending")

    def test_storage_cache_hit_returns_cached_result_without_full_execution(self):
        from scripts.agent_query_storage import build_cache_identity
        from scripts.retrieval_agent_entrypoint import HybridRetrievalEntryPoint

        preflight = {
            "status": "planned",
            "intent": "rank_to_major_match",
            "slots": {"province": "广东", "subject_type": "物理", "score": 580, "major_text": "计算机"},
            "tool_plan": [{"tool_name": "rank_to_major_match", "arguments": {"score": 580}}],
            "tool_trace": [],
            "answer_markdown": "计划",
        }
        cache_key, _ = build_cache_identity(
            question="广东物理 580 想学计算机",
            mode="auto",
            route="rules",
            intent="rank_to_major_match",
            slots=preflight["slots"],
            tool_plan=preflight["tool_plan"],
        )
        storage = MemoryAgentStorage()
        storage.cache[cache_key] = {
            "status": "ok",
            "route": "rules",
            "intent": "rank_to_major_match",
            "slots": preflight["slots"],
            "tool_plan": preflight["tool_plan"],
            "tool_trace": [],
            "answer_markdown": "缓存结果",
        }
        rule_entrypoint = TwoPhaseRuleEntryPoint(preflight, {"status": "ok", "answer_markdown": "不应执行"})

        result = HybridRetrievalEntryPoint(rule_entrypoint=rule_entrypoint, storage=storage).run(
            "广东物理 580 想学计算机",
            session_id="s2",
        )

        self.assertEqual(result["answer_markdown"], "缓存结果")
        self.assertTrue(result["cache_hit"])
        self.assertEqual(rule_entrypoint.calls, [("广东物理 580 想学计算机", {}, False)])
        self.assertEqual(storage.logs[0]["cache_hit"], True)
        self.assertEqual(storage.cache_writes, [])


if __name__ == "__main__":
    unittest.main()
