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
    "rank_to_school_match",
    "rank_to_major_match",
    "specialty_group_lookup",
    "subject_requirement_lookup",
    "school_department_major_list",
    "plan_history",
    "employment_summary",
    "source_trace_lookup",
    "transfer_policy_lookup",
    "fee_and_campus_lookup",
    "specialty_group_risk",
    "comparison_query",
    "major_streaming_policy_lookup",
    "civil_service_mapping",
    "policy_rule_lookup",
    "admission_history",
    "major_market_reference",
    "civil_service_role_search",
    "data_gap_detection",
    "web_evidence_search",
    "web_evidence_fetch",
    "web_gap_fill",
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

    def score_to_rank(self, province, score, subject_type=None, year=None):
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

    def rank_to_school_match(
        self,
        province,
        subject_type=None,
        score=None,
        rank=None,
        year=None,
        reference_years=None,
        preferred_regions=None,
        school_level_filter=None,
        limit=30,
    ):
        # This fake mirrors the public method shape so the registry test stays
        # focused on function-call dispatch rather than SQL or MySQL behavior.
        self.calls.append(
            (
                "rank_to_school_match",
                {
                    "province": province,
                    "subject_type": subject_type,
                    "score": score,
                    "rank": rank,
                    "year": year,
                    "reference_years": reference_years,
                    "preferred_regions": preferred_regions,
                    "school_level_filter": school_level_filter,
                    "limit": limit,
                },
            )
        )
        return tool_result(
            "rank_to_school_match",
            "ok",
            {
                "province": province,
                "subject_type": subject_type,
                "score": score,
                "rank": rank,
                "year": year,
                "reference_years": reference_years,
                "preferred_regions": preferred_regions,
                "school_level_filter": school_level_filter,
                "limit": limit,
            },
            data={"buckets": {"rush": [], "stable": [], "safe": []}},
        )

    def rank_to_major_match(
        self,
        province,
        major_text,
        subject_type=None,
        score=None,
        rank=None,
        year=None,
        reference_years=None,
        preferred_regions=None,
        school_level_filter=None,
        limit=30,
    ):
        self.calls.append(
            (
                "rank_to_major_match",
                {
                    "province": province,
                    "major_text": major_text,
                    "subject_type": subject_type,
                    "score": score,
                    "rank": rank,
                    "year": year,
                    "reference_years": reference_years,
                    "preferred_regions": preferred_regions,
                    "school_level_filter": school_level_filter,
                    "limit": limit,
                },
            )
        )
        return tool_result(
            "rank_to_major_match",
            "ok",
            {
                "province": province,
                "major_text": major_text,
                "subject_type": subject_type,
                "score": score,
                "rank": rank,
                "year": year,
                "reference_years": reference_years,
                "preferred_regions": preferred_regions,
                "school_level_filter": school_level_filter,
                "limit": limit,
            },
            data={"buckets": {"rush": [], "stable": [], "safe": []}},
        )

    def comparison_query(
        self,
        target_type,
        target_texts,
        major_text=None,
        province=None,
        subject_type=None,
        score=None,
        rank=None,
        year=None,
        dimensions=None,
        limit=10,
    ):
        self.calls.append(
            (
                "comparison_query",
                {
                    "target_type": target_type,
                    "target_texts": target_texts,
                    "major_text": major_text,
                    "province": province,
                    "subject_type": subject_type,
                    "score": score,
                    "rank": rank,
                    "year": year,
                    "dimensions": dimensions,
                    "limit": limit,
                },
            )
        )
        return tool_result(
            "comparison_query",
            "ok",
            {"target_type": target_type, "target_texts": target_texts},
            data={"targets": [{"target_text": text} for text in target_texts]},
        )

    def major_streaming_policy_lookup(
        self,
        school_text,
        major_text=None,
        province=None,
        year=None,
        limit=10,
    ):
        self.calls.append(
            (
                "major_streaming_policy_lookup",
                {
                    "school_text": school_text,
                    "major_text": major_text,
                    "province": province,
                    "year": year,
                    "limit": limit,
                },
            )
        )
        return tool_result(
            "major_streaming_policy_lookup",
            "partial",
            {"school_text": school_text},
            data_gaps=["官方大类分流政策", "真实分流比例"],
        )

    def civil_service_mapping(self, major_text, year=None, province=None, limit=20):
        self.calls.append(
            (
                "civil_service_mapping",
                {"major_text": major_text, "year": year, "province": province, "limit": limit},
            )
        )
        return tool_result(
            "civil_service_mapping",
            "partial",
            {"major_text": major_text},
            data_gaps=["正式可报条件判定"],
        )

    def policy_rule_lookup(self, school_text, policy_type=None, province=None, year=None):
        self.calls.append(
            (
                "policy_rule_lookup",
                {"school_text": school_text, "policy_type": policy_type, "province": province, "year": year},
            )
        )
        return tool_result(
            "policy_rule_lookup",
            "partial",
            {"school_text": school_text},
            data_gaps=["官方招生章程原文"],
        )

    def web_evidence_search(self, query, search_scope=None, domains=None, limit=5):
        self.calls.append(
            (
                "web_evidence_search",
                {"query": query, "search_scope": search_scope, "domains": domains, "limit": limit},
            )
        )
        return tool_result(
            "web_evidence_search",
            "ok",
            {"query": query, "search_scope": search_scope, "domains": domains, "limit": limit},
            data={"results": [{"title": "招生章程", "url": "https://zsb.example.edu.cn/news"}]},
        )
    def web_evidence_fetch(
        self,
        query,
        search_scope=None,
        domains=None,
        limit=5,
        fetch_limit=3,
        evidence_limit=5,
        source_policy="official_only",
    ):
        self.calls.append(
            (
                "web_evidence_fetch",
                {
                    "query": query,
                    "search_scope": search_scope,
                    "domains": domains,
                    "limit": limit,
                    "fetch_limit": fetch_limit,
                    "evidence_limit": evidence_limit,
                    "source_policy": source_policy,
                },
            )
        )
        return tool_result(
            "web_evidence_fetch",
            "ok",
            {
                "query": query,
                "search_scope": search_scope,
                "domains": domains,
                "limit": limit,
                "fetch_limit": fetch_limit,
                "evidence_limit": evidence_limit,
                "source_policy": source_policy,
            },
            data={
                "pages": [
                    {
                        "title": "official page",
                        "url": "https://zsb.example.edu.cn/news",
                        "evidence_snippets": [{"text": "正文证据"}],
                    }
                ]
            },
        )

    def web_gap_fill(
        self,
        gap_items,
        question=None,
        max_rounds=3,
        max_fetches_per_round=5,
        source_policy="official_only",
        max_seconds=None,
    ):
        self.calls.append(
            (
                "web_gap_fill",
                {
                    "gap_items": gap_items,
                    "question": question,
                    "max_rounds": max_rounds,
                    "max_fetches_per_round": max_fetches_per_round,
                    "source_policy": source_policy,
                    "max_seconds": max_seconds,
                },
            )
        )
        return tool_result(
            "web_gap_fill",
            "ok",
            {
                "gap_items": gap_items,
                "question": question,
                "max_rounds": max_rounds,
                "max_fetches_per_round": max_fetches_per_round,
                "source_policy": source_policy,
                "max_seconds": max_seconds,
            },
            data={"filled_items": [], "accepted_evidence": [], "unfilled_gaps": []},
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

    def test_source_trace_registry_covers_every_registered_function(self):
        from scripts.retrieval_tools import _SOURCE_TRACE_REGISTRY

        self.assertEqual(set(_SOURCE_TRACE_REGISTRY), EXPECTED_FUNCTION_NAMES)
        for tool_name, trace in _SOURCE_TRACE_REGISTRY.items():
            self.assertIn("source_tables", trace, tool_name)
            self.assertIn("scope_notes", trace, tool_name)
            self.assertIn("reliability", trace, tool_name)

    def test_schema_documents_required_slots_for_high_risk_tools(self):
        from scripts.retrieval_function_registry import schema_for_tool

        score_schema = schema_for_tool("score_to_rank")["function"]["parameters"]
        match_schema = schema_for_tool("rank_to_school_match")["function"]["parameters"]
        major_match_schema = schema_for_tool("rank_to_major_match")["function"]["parameters"]
        group_schema = schema_for_tool("specialty_group_lookup")["function"]["parameters"]
        transfer_schema = schema_for_tool("transfer_policy_lookup")["function"]["parameters"]
        profile_schema = schema_for_tool("school_major_profile")["function"]["parameters"]
        comparison_schema = schema_for_tool("comparison_query")["function"]["parameters"]
        streaming_schema = schema_for_tool("major_streaming_policy_lookup")["function"]["parameters"]
        mapping_schema = schema_for_tool("civil_service_mapping")["function"]["parameters"]
        policy_schema = schema_for_tool("policy_rule_lookup")["function"]["parameters"]
        web_schema = schema_for_tool("web_evidence_search")["function"]["parameters"]
        web_fetch_schema = schema_for_tool("web_evidence_fetch")["function"]["parameters"]
        web_gap_fill_schema = schema_for_tool("web_gap_fill")["function"]["parameters"]

        self.assertEqual(score_schema["required"], ["province", "score"])
        self.assertEqual(match_schema["required"], ["province"])
        self.assertEqual(major_match_schema["required"], ["province", "major_text"])
        self.assertEqual(group_schema["required"], ["school_text"])
        self.assertEqual(transfer_schema["required"], ["school_text"])
        self.assertEqual(profile_schema["required"], ["school_text", "major_text"])
        self.assertEqual(comparison_schema["required"], ["target_type", "target_texts"])
        self.assertEqual(streaming_schema["required"], ["school_text"])
        self.assertEqual(mapping_schema["required"], ["major_text"])
        self.assertEqual(policy_schema["required"], ["school_text"])
        self.assertEqual(web_schema["required"], ["query"])
        self.assertEqual(web_fetch_schema["required"], ["query"])
        self.assertEqual(web_gap_fill_schema["required"], ["gap_items"])
        self.assertIn("max_rounds", web_gap_fill_schema["properties"])
        self.assertIn("source_policy", web_gap_fill_schema["properties"])
        self.assertIn("max_seconds", web_gap_fill_schema["properties"])

    def test_school_major_list_schema_warns_not_to_pass_major_text(self):
        from scripts.retrieval_function_registry import schema_for_tool

        schema = schema_for_tool("school_major_list")["function"]
        parameters = schema["parameters"]

        self.assertNotIn("major_text", parameters["properties"])
        self.assertIn("不要传 major_text", schema["description"])
        self.assertIn("school_major_profile", schema["description"])
        self.assertIn("major_school_list", schema["description"])

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

    def test_dispatcher_allows_score_to_rank_without_subject_type(self):
        from scripts.retrieval_function_registry import call_retrieval_function

        fake_tools = FakeRetrievalTools()
        result = call_retrieval_function(
            "score_to_rank",
            {"province": "浙江", "score": 620},
            tools=fake_tools,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            fake_tools.calls,
            [("score_to_rank", {"province": "浙江", "subject_type": None, "score": 620, "year": None})],
        )

    def test_dispatcher_calls_web_evidence_search_with_optional_filters(self):
        from scripts.retrieval_function_registry import call_retrieval_function

        fake_tools = FakeRetrievalTools()
        result = call_retrieval_function(
            "web_evidence_search",
            {
                "query": "杭州电子科技大学 招生章程 单科限制",
                "search_scope": "official",
                "domains": ["hdu.edu.cn"],
                "limit": 3,
            },
            tools=fake_tools,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            fake_tools.calls,
            [
                (
                    "web_evidence_search",
                    {
                        "query": "杭州电子科技大学 招生章程 单科限制",
                        "search_scope": "official",
                        "domains": ["hdu.edu.cn"],
                        "limit": 3,
                    },
                )
            ],
        )

    def test_dispatcher_calls_web_evidence_fetch_with_fetch_controls(self):
        from scripts.retrieval_function_registry import call_retrieval_function

        fake_tools = FakeRetrievalTools()
        result = call_retrieval_function(
            "web_evidence_fetch",
            {
                "query": "上海交通大学 人工智能 本科专业",
                "search_scope": "official",
                "domains": ["sjtu.edu.cn"],
                "limit": 5,
                "fetch_limit": 2,
                "evidence_limit": 4,
                "source_policy": "official_only",
            },
            tools=fake_tools,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            fake_tools.calls,
            [
                (
                    "web_evidence_fetch",
                    {
                        "query": "上海交通大学 人工智能 本科专业",
                        "search_scope": "official",
                        "domains": ["sjtu.edu.cn"],
                        "limit": 5,
                        "fetch_limit": 2,
                        "evidence_limit": 4,
                        "source_policy": "official_only",
                    },
                )
            ],
        )

    def test_dispatcher_calls_web_gap_fill_with_gap_items(self):
        from scripts.retrieval_function_registry import call_retrieval_function

        fake_tools = FakeRetrievalTools()
        gap_items = [
            {
                "gap_key": "major_school_relation",
                "label": "专业开设院校关系",
                "normalized_slots": {"major_name": "人工智能", "province_filter": "上海"},
            }
        ]
        result = call_retrieval_function(
            "web_gap_fill",
            {
                "gap_items": gap_items,
                "question": "人工智能专业，上海有哪些本科院校开设？",
                "max_rounds": 2,
                "max_fetches_per_round": 3,
                "source_policy": "official_only",
                "max_seconds": 12,
            },
            tools=fake_tools,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            fake_tools.calls,
            [
                (
                    "web_gap_fill",
                    {
                        "gap_items": gap_items,
                        "question": "人工智能专业，上海有哪些本科院校开设？",
                        "max_rounds": 2,
                        "max_fetches_per_round": 3,
                        "source_policy": "official_only",
                        "max_seconds": 12,
                    },
                )
            ],
        )

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
        repo_root = Path(__file__).resolve().parents[2]
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
