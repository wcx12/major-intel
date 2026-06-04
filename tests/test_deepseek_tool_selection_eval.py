import unittest

from scripts.retrieval_function_registry import RETRIEVAL_FUNCTION_NAMES


class DeepSeekToolSelectionEvalTests(unittest.TestCase):
    def test_eval_cases_reference_registered_tools(self):
        from scripts.evaluate_deepseek_tool_selection import load_cases

        cases = load_cases()
        registered = set(RETRIEVAL_FUNCTION_NAMES)

        self.assertGreaterEqual(len(cases), 6)
        for case in cases:
            self.assertIsInstance(case["id"], str)
            self.assertIsInstance(case["prompt"], str)
            self.assertGreater(len(case["prompt"]), 4)
            self.assertGreater(case["max_executed_tool_calls"], 0)
            expected = set(case["expected_answer_tools"])
            allowed = set(case.get("allowed_support_tools", []))
            forbidden = set(case.get("forbidden_tools", []))
            self.assertTrue(expected)
            self.assertTrue(expected <= registered)
            self.assertTrue(allowed <= registered)
            self.assertTrue(forbidden <= registered)
            self.assertFalse((expected | allowed) & forbidden)

    def test_validate_trace_accepts_allowed_lookup_then_expected_tool(self):
        from scripts.evaluate_deepseek_tool_selection import validate_trace

        case = {
            "id": "school_major_list",
            "prompt": "杭电有哪些专业？",
            "expected_answer_tools": ["school_major_list"],
            "allowed_support_tools": ["school_lookup"],
            "forbidden_tools": [],
            "max_executed_tool_calls": 3,
        }
        trace = [
            {"tool_name": "school_lookup", "result": {"status": "ok"}},
            {"tool_name": "school_major_list", "result": {"status": "ok"}},
        ]

        self.assertEqual(validate_trace(case, trace), [])

    def test_validate_trace_flags_missing_forbidden_and_excess_tools(self):
        from scripts.evaluate_deepseek_tool_selection import validate_trace

        case = {
            "id": "rank_to_school",
            "prompt": "浙江物理580分，能上哪些学校？",
            "expected_answer_tools": ["rank_to_school_match"],
            "allowed_support_tools": ["score_to_rank"],
            "forbidden_tools": ["admission_history"],
            "max_executed_tool_calls": 2,
        }
        trace = [
            {"tool_name": "score_to_rank", "result": {"status": "not_found"}},
            {"tool_name": "admission_history", "result": {"status": "needs_clarification"}},
            {"tool_name": "source_trace_lookup", "result": {"status": "ok"}},
        ]

        errors = validate_trace(case, trace)

        self.assertIn("missing expected answer tool: rank_to_school_match", errors)
        self.assertIn("forbidden tool called: admission_history", errors)
        self.assertIn("tool call count 3 exceeds max_executed_tool_calls 2", errors)
        self.assertIn("unexpected tool called: source_trace_lookup", errors)

    def test_validate_trace_allows_blocking_stop_before_expected_tool(self):
        from scripts.evaluate_deepseek_tool_selection import validate_trace

        case = {
            "id": "streaming_policy",
            "prompt": "杭电计算机大类分流风险大吗？",
            "expected_answer_tools": ["major_streaming_policy_lookup"],
            "allowed_support_tools": ["school_lookup", "major_lookup"],
            "forbidden_tools": [],
            "max_executed_tool_calls": 4,
            "allow_blocking_stop_before_expected": True,
        }
        trace = [
            {"tool_name": "school_lookup", "result": {"status": "ok"}},
            {"tool_name": "major_lookup", "result": {"status": "not_found"}},
        ]

        self.assertEqual(validate_trace(case, trace), [])


if __name__ == "__main__":
    unittest.main()
