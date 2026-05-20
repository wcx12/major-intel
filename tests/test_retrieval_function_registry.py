import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.retrieval_tools import tool_result


EXPECTED_FUNCTION_NAMES = {
    "school_lookup",
    "major_lookup",
    "school_profile",
    "major_profile",
    "school_major_list",
    "major_school_list",
    "school_major_profile",
    "score_to_rank",
    "admission_history",
    "major_market_reference",
    "civil_service_role_search",
    "data_gap_detection",
}


class FakeRetrievalTools:
    """Small dispatcher double that records which retrieval method was called.

    The function registry should not know anything about SQL or MySQL.  These
    tests verify the agent-facing dispatch boundary by injecting a fake tools
    object with the same public methods as `RetrievalTools`.
    """

    def __init__(self):
        self.calls = []

    def school_lookup(self, school_text, limit=5):
        self.calls.append(("school_lookup", {"school_text": school_text, "limit": limit}))
        return tool_result(
            "school_lookup",
            "ok",
            {"school_text": school_text, "limit": limit},
            data={"selected_school": {"name": school_text}},
        )

    def score_to_rank(self, province, subject_type, score, year=None):
        self.calls.append(
            (
                "score_to_rank",
                {"province": province, "subject_type": subject_type, "score": score, "year": year},
            )
        )
        return tool_result(
            "score_to_rank",
            "ok",
            {"province": province, "subject_type": subject_type, "score": score, "year": year},
            data={"rank_range": {"highest_rank": 1000, "lowest_rank": 1200}},
        )


class RetrievalFunctionRegistryTests(unittest.TestCase):
    def test_schema_exports_every_first_batch_retrieval_function(self):
        from scripts.retrieval_function_registry import get_function_schemas

        schemas = get_function_schemas()
        names = {schema["function"]["name"] for schema in schemas}

        self.assertEqual(names, EXPECTED_FUNCTION_NAMES)
        for schema in schemas:
            self.assertEqual(schema["type"], "function")
            self.assertEqual(schema["function"]["parameters"]["type"], "object")
            self.assertFalse(schema["function"]["parameters"]["additionalProperties"])

    def test_schema_documents_required_slots_for_high_risk_tools(self):
        from scripts.retrieval_function_registry import schema_for_tool

        score_schema = schema_for_tool("score_to_rank")["function"]["parameters"]
        profile_schema = schema_for_tool("school_major_profile")["function"]["parameters"]

        self.assertEqual(score_schema["required"], ["province", "subject_type", "score"])
        self.assertEqual(profile_schema["required"], ["school_text", "major_text"])

    def test_dispatcher_calls_named_tool_with_arguments(self):
        from scripts.retrieval_function_registry import call_retrieval_function

        fake_tools = FakeRetrievalTools()
        result = call_retrieval_function(
            "school_lookup",
            {"school_text": "HDU", "limit": 2},
            tools=fake_tools,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["selected_school"]["name"], "HDU")
        self.assertEqual(fake_tools.calls, [("school_lookup", {"school_text": "HDU", "limit": 2})])

    def test_dispatcher_keeps_error_inside_common_envelope(self):
        from scripts.retrieval_function_registry import call_retrieval_function

        result = call_retrieval_function("unknown_tool", {}, tools=FakeRetrievalTools())

        self.assertEqual(result["tool_name"], "unknown_tool")
        self.assertEqual(result["status"], "error")
        self.assertIn("unknown_tool", result["warnings"][0])

    def test_dispatcher_rejects_non_object_arguments_before_tool_call(self):
        from scripts.retrieval_function_registry import call_retrieval_function

        fake_tools = FakeRetrievalTools()
        result = call_retrieval_function("school_lookup", ["bad"], tools=fake_tools)

        self.assertEqual(result["status"], "error")
        self.assertEqual(fake_tools.calls, [])
        self.assertIn("arguments", result["warnings"][0])

    def test_cli_exports_schema_json_without_database(self):
        repo_root = Path(__file__).resolve().parents[1]
        script_path = repo_root / "scripts" / "retrieval_function_registry.py"

        completed = subprocess.run(
            [sys.executable, str(script_path), "list-schemas"],
            cwd=repo_root,
            capture_output=True,
        )

        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr.decode("utf-8", errors="replace")
            + completed.stdout.decode("utf-8", errors="replace"),
        )
        schemas = json.loads(completed.stdout.decode("utf-8"))
        self.assertEqual({schema["function"]["name"] for schema in schemas}, EXPECTED_FUNCTION_NAMES)


if __name__ == "__main__":
    unittest.main()
