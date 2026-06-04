import unittest

from scripts.evaluate_score_to_rank_boundaries import (
    answer_failures,
    classify_oracle,
    summarize_records,
    tool_failures,
)


class ScoreToRankBoundaryEvaluatorTests(unittest.TestCase):
    def test_classify_oracle_marks_unique_exact_match_as_ok(self):
        oracle = classify_oracle(
            [
                {
                    "province_id": "33",
                    "subject_type": "综合",
                    "year": "2025",
                    "score": "620",
                    "same_count": "893",
                    "highest_rank": "31222",
                    "lowest_rank": "32114",
                    "batch_type": "undergraduate_vocational",
                }
            ]
        )

        self.assertEqual(oracle["expected_status"], "ok")
        self.assertEqual(oracle["expected_data"]["rank_range"]["highest_rank"], 31222)
        self.assertEqual(oracle["expected_data"]["rank_range"]["lowest_rank"], 32114)
        self.assertEqual(oracle["issue_codes"], [])

    def test_classify_oracle_marks_multiple_rows_as_ambiguous(self):
        oracle = classify_oracle(
            [
                {
                    "year": "2021",
                    "subject_type": "综合",
                    "score": "119",
                    "same_count": "1",
                    "highest_rank": "42032",
                    "lowest_rank": "42032",
                    "batch_type": "undergraduate",
                },
                {
                    "year": "2021",
                    "subject_type": "综合",
                    "score": "119",
                    "same_count": "976",
                    "highest_rank": "2633",
                    "lowest_rank": "3608",
                    "batch_type": "vocational",
                },
            ]
        )

        self.assertEqual(oracle["expected_status"], "ambiguous")
        self.assertIn("ambiguous_batch_key", oracle["issue_codes"])
        self.assertEqual(set(oracle["batch_types"]), {"undergraduate", "vocational"})

    def test_classify_oracle_marks_missing_subject_as_invalid_input(self):
        oracle = classify_oracle([], ["missing_subject_type"])

        self.assertEqual(oracle["expected_status"], "invalid_input")
        self.assertIn("missing_subject_type", oracle["issue_codes"])

    def test_classify_oracle_marks_invalid_subject_as_invalid_input(self):
        oracle = classify_oracle([], ["invalid_subject_type"])

        self.assertEqual(oracle["expected_status"], "invalid_input")
        self.assertIn("invalid_subject_type", oracle["issue_codes"])

    def test_tool_failures_check_status_and_rank_values(self):
        case = {"id": "zhejiang_620", "allow_ambiguous_ok": False}
        oracle = {
            "expected_status": "ok",
            "expected_data": {
                "score": 620,
                "same_count": 893,
                "rank_range": {"highest_rank": 31222, "lowest_rank": 32114},
            },
            "expected_year": "2025",
            "expected_subject_type": "综合",
            "issue_codes": [],
        }
        result = {
            "status": "ok",
            "normalized_slots": {"year": "2025", "matched_subject_type": "综合"},
            "data": {"score": 620, "same_count": 893, "rank_range": {"highest_rank": 31222, "lowest_rank": 32115}},
        }

        failures = tool_failures(case, oracle, result)

        self.assertEqual(failures[0]["code"], "tool_rank_range_mismatch")

    def test_answer_failures_require_rank_range_year_and_scope_for_ok_result(self):
        case = {"id": "zhejiang_620", "question": "浙江综合620分对应多少位次？"}
        entry_result = {
            "status": "ok",
            "answer_markdown": "已按 `score_to_rank` 处理，调用工具：score_to_rank。",
            "tool_trace": [
                {
                    "tool_name": "score_to_rank",
                    "result": {
                        "status": "ok",
                        "normalized_slots": {"year": "2025", "matched_subject_type": "综合", "subject_type": "综合"},
                        "data": {
                            "score": 620,
                            "same_count": 893,
                            "rank_range": {"highest_rank": 31222, "lowest_rank": 32114},
                        },
                        "warnings": [],
                        "scope_notes": ["位次优先于分数；分数转位次只在同省、同科类、同年份内有效。"],
                    },
                }
            ],
        }

        failures = answer_failures(case, entry_result)
        codes = {failure["code"] for failure in failures}

        self.assertIn("answer_missing_rank_range", codes)
        self.assertIn("answer_missing_year", codes)
        self.assertIn("answer_missing_scope_note", codes)

    def test_answer_failures_reject_invented_rank_when_not_found(self):
        case = {"id": "zhejiang_history_620", "question": "浙江历史620分对应多少位次？"}
        entry_result = {
            "status": "not_found",
            "answer_markdown": "大概是 31222 到 32114 名。",
            "tool_trace": [{"tool_name": "score_to_rank", "result": {"status": "not_found", "data": {}, "warnings": ["本地库未命中对应一分一段记录。"]}}],
        }

        failures = answer_failures(case, entry_result)
        codes = {failure["code"] for failure in failures}

        self.assertIn("answer_missing_not_found", codes)
        self.assertIn("answer_invents_rank_for_not_found", codes)

    def test_answer_failures_accept_score_clarification_without_tool_trace(self):
        case = {"id": "zhejiang_chinese_score", "question": "浙江综合六百二十分对应多少位次？"}
        entry_result = {
            "status": "needs_clarification",
            "intent": "score_to_rank",
            "needs_clarification": ["score"],
            "answer_markdown": "这个问题还需要补充：分数。",
            "tool_trace": [],
        }

        self.assertEqual(answer_failures(case, entry_result), [])

    def test_summarize_records_counts_failure_severities(self):
        summary = summarize_records(
            [
                {"tool_failures": [{"severity": "hard_fail"}], "answer_failures": [], "data_warnings": []},
                {"tool_failures": [], "answer_failures": [{"severity": "answer_fail"}], "data_warnings": [{"severity": "data_warning"}]},
            ]
        )

        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["hard_fail"], 1)
        self.assertEqual(summary["answer_fail"], 1)
        self.assertEqual(summary["data_warning"], 1)


if __name__ == "__main__":
    unittest.main()
