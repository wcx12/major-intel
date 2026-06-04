import unittest

from scripts.evaluate_rank_to_school_match_boundaries import (
    answer_failures,
    call_failures,
    classify_oracle,
    summarize_records,
    tool_failures,
)


class RankToSchoolMatchBoundaryEvaluatorTests(unittest.TestCase):
    def test_classify_oracle_builds_expected_buckets_and_fallback(self):
        oracle = classify_oracle(
            [
                {
                    "province_name": "浙江",
                    "school_id": "10001",
                    "school_name": "冲刺大学",
                    "school_province_name": "浙江",
                    "subject_type": "综合",
                    "year": "2024",
                    "stable_rank": "62000",
                    "chong_rank": "70000",
                    "bao_rank": "58000",
                },
                {
                    "province_name": "浙江",
                    "school_id": "10002",
                    "school_name": "稳妥大学",
                    "school_province_name": "浙江",
                    "subject_type": "综合",
                    "year": "2024",
                    "stable_rank": "66000",
                    "chong_rank": "73000",
                    "bao_rank": "61000",
                },
                {
                    "province_name": "浙江",
                    "school_id": "10003",
                    "school_name": "保底大学",
                    "school_province_name": "浙江",
                    "subject_type": "综合",
                    "year": "2024",
                    "stable_rank": "70000",
                    "chong_rank": "76000",
                    "bao_rank": "68000",
                },
            ],
            applicant_rank=63956,
            requested_year=2025,
            limit=30,
        )

        self.assertEqual(oracle["expected_status"], "ok")
        self.assertTrue(oracle["history_fallback"])
        self.assertEqual(oracle["bucket_counts"], {"rush": 1, "stable": 1, "safe": 1})
        self.assertEqual(oracle["required_school_names_by_bucket"]["rush"], ["冲刺大学"])
        self.assertEqual(oracle["required_school_names_by_bucket"]["stable"], ["稳妥大学"])
        self.assertEqual(oracle["required_school_names_by_bucket"]["safe"], ["保底大学"])

    def test_tool_failures_detect_bucket_count_and_school_name_mismatch(self):
        oracle = {
            "expected_status": "ok",
            "candidate_rows": 3,
            "returned_schools": 3,
            "reference_years": [2024],
            "history_fallback": True,
            "bucket_counts": {"rush": 1, "stable": 1, "safe": 1},
            "required_school_names_by_bucket": {
                "rush": ["冲刺大学"],
                "stable": ["稳妥大学"],
                "safe": ["保底大学"],
            },
            "empty_buckets": [],
        }
        result = {
            "status": "ok",
            "data": {
                "reference": {"reference_years": [2024], "history_fallback": True},
                "coverage": {"candidate_rows": 3, "returned_schools": 2},
                "buckets": {
                    "rush": [{"school_name": "冲刺大学"}],
                    "stable": [{"school_name": "别的大学"}],
                    "safe": [],
                },
            },
        }

        failures = tool_failures({"id": "case"}, oracle, result)
        codes = {failure["code"] for failure in failures}

        self.assertIn("tool_returned_schools_mismatch", codes)
        self.assertIn("tool_bucket_count_mismatch", codes)
        self.assertIn("tool_missing_expected_school", codes)

    def test_answer_failures_require_school_names_buckets_scope_and_fallback(self):
        entry_result = {
            "status": "ok",
            "answer_markdown": "已按 `rank_to_school_match` 处理，调用工具：rank_to_school_match。",
            "tool_trace": [
                {
                    "tool_name": "rank_to_school_match",
                    "result": {
                        "status": "ok",
                        "data": {
                            "applicant": {"rank": 63956, "rank_source": "score_to_rank"},
                            "reference": {"reference_years": [2024], "history_fallback": True},
                            "buckets": {
                                "rush": [{"school_name": "冲刺大学", "risk_label": "冲", "reference_year": 2024}],
                                "stable": [{"school_name": "稳妥大学", "risk_label": "稳", "reference_year": 2024}],
                                "safe": [],
                            },
                        },
                        "warnings": ["本地库缺少请求年份的录取结果，已使用最近可用历史年份作为参考。"],
                        "scope_notes": ["学校匹配不等于专业录取保证。"],
                    },
                }
            ],
        }

        failures = answer_failures({"id": "case"}, entry_result)
        codes = {failure["code"] for failure in failures}

        self.assertIn("answer_missing_school_names", codes)
        self.assertIn("answer_missing_bucket_labels", codes)
        self.assertIn("answer_missing_rank", codes)
        self.assertIn("answer_missing_reference_year", codes)
        self.assertIn("answer_missing_fallback_warning", codes)
        self.assertIn("answer_missing_scope_note", codes)
        self.assertIn("answer_missing_empty_bucket_note", codes)

    def test_answer_failures_reject_overpromised_admission(self):
        entry_result = {
            "status": "ok",
            "answer_markdown": "保底大学稳上，保证录取。",
            "tool_trace": [
                {
                    "tool_name": "rank_to_school_match",
                    "result": {
                        "status": "ok",
                        "data": {
                            "applicant": {"rank": 63956},
                            "reference": {"reference_years": [2025], "history_fallback": False},
                            "buckets": {"rush": [], "stable": [], "safe": [{"school_name": "保底大学"}]},
                        },
                        "warnings": [],
                        "scope_notes": ["本工具使用历史录取位次做学校层面参考，不代表未来录取保证。"],
                    },
                }
            ],
        }

        failures = answer_failures({"id": "case"}, entry_result)

        self.assertIn("answer_overpromises_admission", {failure["code"] for failure in failures})

    def test_call_failures_detect_wrong_intent_and_wrong_slot(self):
        case = {
            "id": "multi_region",
            "expected_intent": "rank_to_school_match",
            "expected_slots": {"province": "河南", "subject_type": "理科", "score": 465},
        }
        entry_result = {
            "intent": "rank_to_school_match",
            "slots": {"province": "河北", "subject_type": "理科", "score": 465},
            "tool_plan": [{"tool_name": "rank_to_school_match", "arguments": {"province": "河北", "subject_type": "理科", "score": 465}}],
        }

        failures = call_failures(case, entry_result)

        self.assertEqual(failures[0]["code"], "call_slot_mismatch")
        self.assertIn("province", failures[0]["message"])

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
