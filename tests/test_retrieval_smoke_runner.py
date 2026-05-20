import json
import unittest
from pathlib import Path

from scripts.run_retrieval_smoke_cases import (
    DEFAULT_CASES_PATH,
    build_command,
    load_cases,
    summarize_results,
    validate_payload,
)


class RetrievalSmokeRunnerTests(unittest.TestCase):
    def test_load_cases_accepts_metadata_wrapped_case_file(self):
        case_file = Path(self._testMethodName + ".json")
        self.addCleanup(lambda: case_file.unlink(missing_ok=True))
        case_file.write_text(
            json.dumps(
                {
                    "metadata": {"version": 1},
                    "cases": [
                        {
                            "id": "school_lookup_exact",
                            "tool": "school_lookup",
                            "category": "happy_path",
                            "args": {"school": "杭州电子科技大学"},
                            "allowed_statuses": ["ok"],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        cases = load_cases(case_file)

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]["id"], "school_lookup_exact")
        self.assertEqual(cases[0]["args"]["school"], "杭州电子科技大学")

    def test_build_command_converts_case_args_to_cli_flags(self):
        case = {
            "tool": "admission_history",
            "args": {
                "school": "杭州电子科技大学",
                "major": "计算机科学与技术",
                "province": "广东",
                "subject_type": "物理",
                "years": [2023, 2024, 2025],
                "limit": 5,
                "unused_none": None,
            },
        }

        command = build_command("python", Path("scripts/retrieval_tools.py"), case)

        self.assertEqual(
            command,
            [
                "python",
                "scripts/retrieval_tools.py",
                "admission_history",
                "--school",
                "杭州电子科技大学",
                "--major",
                "计算机科学与技术",
                "--province",
                "广东",
                "--subject-type",
                "物理",
                "--years",
                "2023",
                "2024",
                "2025",
                "--limit",
                "5",
            ],
        )

    def test_validate_payload_checks_envelope_status_and_expected_data_keys(self):
        case = {
            "id": "major_lookup_cs",
            "tool": "major_lookup",
            "allowed_statuses": ["ok"],
            "target_status": "ok",
            "expected_data_keys": ["selected_major", "candidates"],
        }
        payload = {
            "tool_name": "major_lookup",
            "status": "ok",
            "input": {},
            "normalized_slots": {},
            "data": {"selected_major": {}, "candidates": []},
            "scope_notes": [],
            "data_gaps": [],
            "needs_clarification": [],
            "source_tables": [],
            "warnings": [],
        }

        errors, quality_misses = validate_payload(case, payload)

        self.assertEqual(errors, [])
        self.assertEqual(quality_misses, [])

    def test_validate_payload_reports_quality_miss_without_structural_error(self):
        case = {
            "id": "school_profile_hdu",
            "tool": "school_profile",
            "allowed_statuses": ["ok", "not_found"],
            "target_status": "ok",
        }
        payload = {
            "tool_name": "school_profile",
            "status": "not_found",
            "input": {},
            "normalized_slots": {},
            "data": {},
            "scope_notes": [],
            "data_gaps": [],
            "needs_clarification": [],
            "source_tables": [],
            "warnings": [],
        }

        errors, quality_misses = validate_payload(case, payload)

        self.assertEqual(errors, [])
        self.assertEqual(quality_misses, ["expected target status ok, got not_found"])

    def test_summarize_results_groups_by_tool_status_and_quality(self):
        results = [
            {"tool": "school_lookup", "status": "ok", "ok": True, "quality_misses": []},
            {"tool": "school_lookup", "status": "not_found", "ok": True, "quality_misses": ["miss"]},
            {"tool": "major_lookup", "status": "error", "ok": False, "quality_misses": []},
        ]

        summary = summarize_results(results)

        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["quality_misses"], 1)
        self.assertEqual(summary["by_tool"]["school_lookup"]["ok"], 1)
        self.assertEqual(summary["by_tool"]["school_lookup"]["not_found"], 1)
        self.assertEqual(summary["by_tool"]["major_lookup"]["error"], 1)

    def test_default_case_file_is_large_and_covers_every_retrieval_entry(self):
        cases = load_cases(DEFAULT_CASES_PATH)
        tools = {case["tool"] for case in cases}

        self.assertGreaterEqual(len(cases), 150)
        self.assertEqual(
            tools,
            {
                "school_lookup",
                "major_lookup",
                "school_profile",
                "major_profile",
                "school_major_list",
                "major_school_list",
                "school_major_profile",
                "score_to_rank",
                "rank_to_school_match",
                "admission_history",
                "major_market_reference",
                "civil_service_role_search",
                "data_gap_detection",
            },
        )


if __name__ == "__main__":
    unittest.main()
