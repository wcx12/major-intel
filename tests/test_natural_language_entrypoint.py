import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.retrieval_tools import tool_result


class RecordingDispatcher:
    """Test dispatcher that records tool calls without touching MySQL.

    The natural-language entrypoint should be testable as pure orchestration:
    route a question, extract slots, build a tool plan, and pass arguments to
    the existing function-call dispatcher boundary.  These tests therefore use
    deterministic fake tool results instead of a live database.
    """

    def __init__(self):
        self.calls = []

    def __call__(self, tool_name, arguments):
        self.calls.append((tool_name, arguments))
        status = "partial" if tool_name in {"school_major_profile", "civil_service_role_search"} else "ok"
        return tool_result(
            tool_name,
            status,
            arguments,
            data={"echo": arguments},
            scope_notes=[f"{tool_name} scope"],
            data_gaps=["校专业级就业事实"] if tool_name == "school_major_profile" else [],
            warnings=["考公岗位文本命中不等于正式可报"] if tool_name == "civil_service_role_search" else [],
        )


class NaturalLanguageEntryPointTests(unittest.TestCase):
    def test_routes_score_major_question_to_rank_to_major_match(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run("广东物理 580 想学计算机，有哪些稳一点的学校？")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["intent"], "rank_to_major_match")
        self.assertEqual(result["slots"]["province"], "广东")
        self.assertEqual(result["slots"]["subject_type"], "物理")
        self.assertEqual(result["slots"]["score"], 580)
        self.assertEqual(result["slots"]["major_text"], "计算机")
        self.assertEqual(
            dispatcher.calls,
            [
                (
                    "rank_to_major_match",
                    {
                        "province": "广东",
                        "subject_type": "物理",
                        "score": 580,
                        "major_text": "计算机",
                        "limit": 30,
                    },
                )
            ],
        )

    def test_missing_province_and_subject_returns_clarification_without_tools(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run("45000 位次能冲什么？")

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["intent"], "rank_to_school_match")
        self.assertEqual(result["needs_clarification"], ["province", "subject_type"])
        self.assertEqual(dispatcher.calls, [])
        self.assertIn("省份", result["answer_markdown"])

    def test_score_to_rank_question_does_not_route_to_recommendation(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run("广东物理 580 分对应多少位次？")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["intent"], "score_to_rank")
        self.assertEqual(
            dispatcher.calls,
            [("score_to_rank", {"province": "广东", "subject_type": "物理", "score": 580})],
        )

    def test_major_market_question_routes_to_market_reference(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run("计算机薪资怎么样，主要去哪些公司？")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["intent"], "major_market_reference")
        self.assertEqual(dispatcher.calls, [("major_market_reference", {"major_text": "计算机", "sample_limit": 10})])

    def test_school_major_list_question_routes_to_school_major_list(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run("杭电有哪些专业？")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["intent"], "school_major_list")
        self.assertEqual(dispatcher.calls, [("school_major_list", {"school_text": "杭电", "limit": 50})])

    def test_school_major_profile_uses_multiple_supporting_tools(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run("杭电计算机怎么样？")

        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["intent"], "school_major_profile")
        self.assertEqual(result["slots"]["school_text"], "杭电")
        self.assertEqual(result["slots"]["major_text"], "计算机")
        self.assertEqual(
            [tool_name for tool_name, _ in dispatcher.calls],
            ["school_major_profile", "employment_summary", "admission_history", "data_gap_detection"],
        )
        self.assertEqual(dispatcher.calls[0][1], {"school_text": "杭电", "major_text": "计算机"})
        self.assertIn("校专业级就业事实", result["data_gaps"])

    def test_civil_service_question_uses_sample_search_as_partial_mapping(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run("软件工程适合考公吗？")

        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["intent"], "civil_service_mapping")
        self.assertEqual(dispatcher.calls, [("civil_service_role_search", {"major_text": "软件工程", "limit": 20})])
        self.assertIn("不是正式可报判定", "".join(result["warnings"]))

    def test_specialty_group_risk_without_context_asks_for_precise_slots(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run("这个专业组会不会被调剂到冷门专业？")

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["intent"], "specialty_group_risk")
        self.assertEqual(result["needs_clarification"], ["school_text", "province", "year", "group_code"])
        self.assertEqual(dispatcher.calls, [])

    def test_session_context_can_supply_missing_score_match_slots(self):
        from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint

        dispatcher = RecordingDispatcher()
        entrypoint = NaturalLanguageEntryPoint(dispatcher=dispatcher)

        result = entrypoint.run(
            "想学计科能看哪些学校？",
            session_context={"province": "广东", "subject_type": "物理", "score": 580},
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["intent"], "rank_to_major_match")
        self.assertEqual(result["slots"]["major_text"], "计科")
        self.assertEqual(dispatcher.calls[0][0], "rank_to_major_match")
        self.assertEqual(dispatcher.calls[0][1]["province"], "广东")

    def test_cli_can_plan_without_database(self):
        repo_root = Path(__file__).resolve().parents[1]
        script_path = repo_root / "scripts" / "natural_language_entrypoint.py"

        completed = subprocess.run(
            [sys.executable, str(script_path), "广东物理 580 想学计算机", "--no-execute"],
            cwd=repo_root,
            capture_output=True,
        )

        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr.decode("utf-8", errors="replace")
            + completed.stdout.decode("utf-8", errors="replace"),
        )
        payload = json.loads(completed.stdout.decode("utf-8"))
        self.assertEqual(payload["intent"], "rank_to_major_match")
        self.assertEqual(payload["tool_plan"][0]["tool_name"], "rank_to_major_match")
        self.assertEqual(payload["tool_trace"], [])


if __name__ == "__main__":
    unittest.main()
