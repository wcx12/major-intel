import unittest
from pathlib import Path

from scripts.evaluate_rank_to_major_match_boundaries import (
    answer_failures,
    classify_oracle,
    evaluate_case,
    load_manual_cases,
    summarize_records,
    tool_failures,
)
from scripts.rank_to_major_match_oracles import selected_oracle_rows


class RankToMajorMatchBoundaryEvaluatorTests(unittest.TestCase):
    def test_selected_oracle_rows_deduplicates_school_major_batch(self):
        rows = [
            {
                "school_id": "10001",
                "school_name": "冲刺大学",
                "major_code": "080901",
                "major_name": "计算机科学与技术",
                "batch": "本科批",
                "year": "2024",
                "stable_rank": "43000",
                "chong_rank": "56000",
                "bao_rank": "30000",
            },
            {
                "school_id": "10001",
                "school_name": "冲刺大学",
                "major_code": "080901",
                "major_name": "计算机科学与技术",
                "batch": "本科批",
                "year": "2023",
                "stable_rank": "44000",
                "chong_rank": "57000",
                "bao_rank": "31000",
            },
            {
                "school_id": "10001",
                "school_name": "冲刺大学",
                "major_code": "080902",
                "major_name": "软件工程",
                "batch": "本科批",
                "year": "2024",
                "stable_rank": "59000",
                "chong_rank": "68000",
                "bao_rank": "51000",
            },
        ]

        buckets, selected = selected_oracle_rows(rows, applicant_rank=50000, limit=10)

        self.assertEqual(len(selected), 2)
        self.assertEqual(buckets["rush"][0]["major_name"], "计算机科学与技术")
        self.assertEqual(buckets["safe"][0]["major_name"], "软件工程")

    def test_classify_oracle_builds_major_row_buckets_and_fallback(self):
        oracle = classify_oracle(
            [
                {
                    "school_id": "10001",
                    "school_name": "冲刺大学",
                    "major_code": "080901",
                    "major_name": "计算机科学与技术",
                    "subject_type": "物理",
                    "year": "2024",
                    "stable_rank": "43000",
                    "chong_rank": "56000",
                    "bao_rank": "30000",
                    "batch": "本科批",
                },
                {
                    "school_id": "10002",
                    "school_name": "稳妥大学",
                    "major_code": "080901",
                    "major_name": "计算机科学与技术",
                    "subject_type": "物理",
                    "year": "2024",
                    "stable_rank": "52000",
                    "chong_rank": "65000",
                    "bao_rank": "42000",
                    "batch": "本科批",
                },
                {
                    "school_id": "10003",
                    "school_name": "保底大学",
                    "major_code": "080901",
                    "major_name": "计算机科学与技术",
                    "subject_type": "",
                    "year": "2024",
                    "stable_rank": "70000",
                    "chong_rank": "90000",
                    "bao_rank": "56000",
                    "batch": "本科批",
                },
            ],
            applicant_rank=50000,
            requested_year=2025,
            limit=10,
        )

        self.assertEqual(oracle["expected_status"], "ok")
        self.assertTrue(oracle["history_fallback"])
        self.assertEqual(oracle["bucket_counts"], {"rush": 1, "stable": 1, "safe": 1})
        self.assertEqual(oracle["returned_major_rows"], 3)
        self.assertEqual(oracle["required_major_rows_by_bucket"]["rush"], ["冲刺大学|计算机科学与技术|本科批"])
        self.assertIn("subject_unknown_rows", oracle["issue_codes"])

    def test_tool_failures_detect_major_row_count_and_name_mismatch(self):
        oracle = {
            "expected_status": "ok",
            "returned_major_rows": 2,
            "reference_years": [2024],
            "history_fallback": True,
            "bucket_counts": {"rush": 1, "stable": 1, "safe": 0},
            "required_major_rows_by_bucket": {
                "rush": ["冲刺大学|计算机科学与技术|本科批"],
                "stable": ["稳妥大学|计算机科学与技术|本科批"],
                "safe": [],
            },
            "empty_buckets": ["safe"],
        }
        result = {
            "status": "ok",
            "data": {
                "reference": {"reference_years": [2024], "history_fallback": True},
                "coverage": {"candidate_rows": 3, "returned_major_rows": 1},
                "buckets": {
                    "rush": [{"school_name": "冲刺大学", "major_name": "计算机科学与技术", "batch": "本科批"}],
                    "stable": [],
                    "safe": [],
                },
            },
        }

        failures = tool_failures({"id": "case"}, oracle, result)
        codes = {failure["code"] for failure in failures}

        self.assertIn("tool_returned_major_rows_mismatch", codes)
        self.assertIn("tool_bucket_count_mismatch", codes)
        self.assertIn("tool_missing_expected_major_row", codes)

    def test_tool_failures_require_cross_level_resolution_metadata(self):
        oracle = {
            "expected_status": "ok",
            "returned_major_rows": 0,
            "reference_years": [],
            "history_fallback": False,
            "bucket_counts": {"rush": 0, "stable": 0, "safe": 0},
            "required_major_rows_by_bucket": {"rush": [], "stable": [], "safe": []},
            "issue_codes": ["major_cross_level_candidates"],
        }
        result = {
            "status": "ok",
            "data": {
                "reference": {"reference_years": [], "history_fallback": False},
                "coverage": {"returned_major_rows": 0},
                "buckets": {"rush": [], "stable": [], "safe": []},
            },
        }

        failures = tool_failures({"id": "case"}, oracle, result)
        codes = {failure["code"] for failure in failures}

        self.assertIn("tool_missing_cross_level_major_resolution", codes)

    def test_tool_failures_accept_cross_level_candidate_summary_without_level_rank_split(self):
        oracle = {
            "expected_status": "ok",
            "returned_major_rows": 0,
            "reference_years": [],
            "history_fallback": False,
            "bucket_counts": {"rush": 0, "stable": 0, "safe": 0},
            "required_major_rows_by_bucket": {"rush": [], "stable": [], "safe": []},
            "issue_codes": ["major_cross_level_candidates"],
        }
        result = {
            "status": "ok",
            "data": {
                "reference": {"reference_years": [], "history_fallback": False},
                "coverage": {"returned_major_rows": 0},
                "buckets": {"rush": [], "stable": [], "safe": []},
                "major_resolution": {
                    "candidate_count": 4,
                    "cross_level_candidates": False,
                    "candidate_level_summary": [
                        {"level_rank": 0, "level2_name": "工学", "count": 1},
                        {"level_rank": 0, "level2_name": "电子与信息大类", "count": 2},
                    ],
                },
            },
        }

        failures = tool_failures({"id": "case"}, oracle, result)
        codes = {failure["code"] for failure in failures}

        self.assertNotIn("tool_missing_cross_level_major_resolution", codes)

    def test_answer_failures_require_major_school_rank_scope_and_empty_bucket_notes(self):
        entry_result = {
            "status": "ok",
            "answer_markdown": "已按 rank_to_major_match 处理。",
            "tool_trace": [
                {
                    "tool_name": "rank_to_major_match",
                    "result": {
                        "status": "ok",
                        "data": {
                            "applicant": {"rank": 50000, "rank_source": "score_to_rank"},
                            "reference": {"reference_years": [2024], "history_fallback": True},
                            "buckets": {
                                "rush": [
                                    {
                                        "school_name": "冲刺大学",
                                        "major_name": "计算机科学与技术",
                                        "risk_label": "冲",
                                        "reference_year": 2024,
                                    }
                                ],
                                "stable": [],
                                "safe": [],
                            },
                        },
                        "warnings": ["本地库缺少请求年份的专业录取结果，已使用最近可用历史年份作为参考。"],
                        "scope_notes": ["本工具使用历史专业录取位次做学校-专业行参考，不代表未来录取保证。"],
                    },
                }
            ],
        }

        failures = answer_failures({"id": "case"}, entry_result)
        codes = {failure["code"] for failure in failures}

        self.assertIn("answer_missing_school_names", codes)
        self.assertIn("answer_missing_major_names", codes)
        self.assertIn("answer_missing_rank", codes)
        self.assertIn("answer_missing_reference_year", codes)
        self.assertIn("answer_missing_scope_note", codes)
        self.assertIn("answer_missing_empty_bucket_note", codes)

    def test_manifest_has_broad_manual_boundary_coverage(self):
        cases = load_manual_cases(Path("tests/function_calls/rank_to_major_match/boundary_cases.json"))
        categories = {case["category"] for case in cases}

        self.assertGreaterEqual(len(cases), 36)
        self.assertIn("major_resolution_ambiguous", categories)
        self.assertIn("major_resolution_alias", categories)
        self.assertIn("score_rank_extreme", categories)
        self.assertIn("subject_mode_boundary", categories)
        self.assertIn("strict_filter_not_found", categories)
        self.assertIn("category_or_broad_major", categories)

    def test_extended_manifest_has_deeper_tool_boundary_coverage(self):
        cases = load_manual_cases(Path("tests/function_calls/rank_to_major_match/extended_boundary_cases.json"))
        categories = {case["category"] for case in cases}
        ids = {case["id"] for case in cases}

        self.assertGreaterEqual(len(cases), 36)
        self.assertEqual(len(ids), len(cases))
        self.assertIn("cross_level_resolution", categories)
        self.assertIn("input_validation_boundary", categories)
        self.assertIn("reference_year_edge", categories)
        self.assertIn("filter_intersection_boundary", categories)
        self.assertIn("bucket_threshold_micro", categories)
        self.assertIn("limit_contract_boundary", categories)

    def test_evaluate_case_can_skip_entrypoint_for_tool_only_runs(self):
        case = {
            "id": "tool_only_probe",
            "category": "unit",
            "major_text": "",
            "expected_intent": "rank_to_major_match",
        }

        record = evaluate_case(case, client=None, tools=None, entrypoint=None, include_entrypoint=False)

        self.assertEqual(record["entry_result"]["status"], "skipped")
        self.assertEqual(record["entry_result"]["intent"], "skipped")
        self.assertEqual(record["call_failures"], [])
        self.assertEqual(record["answer_failures"], [])

    def test_summarize_records_counts_all_failure_groups(self):
        summary = summarize_records(
            [
                {
                    "call_failures": [{"severity": "call_fail"}],
                    "tool_failures": [{"severity": "hard_fail"}],
                    "answer_failures": [],
                    "data_warnings": [],
                },
                {
                    "call_failures": [],
                    "tool_failures": [],
                    "answer_failures": [{"severity": "answer_fail"}],
                    "data_warnings": [{"severity": "data_warning"}],
                },
            ]
        )

        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["call_fail"], 1)
        self.assertEqual(summary["hard_fail"], 1)
        self.assertEqual(summary["answer_fail"], 1)
        self.assertEqual(summary["data_warning"], 1)


if __name__ == "__main__":
    unittest.main()
