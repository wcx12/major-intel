import json
import tempfile
import unittest
from pathlib import Path


def _profile_result(
    *,
    status="partial",
    has_catalog=True,
    has_admission_or_plan=False,
    data_gaps=None,
    warnings=None,
    evidence=None,
):
    return {
        "tool_name": "school_major_profile",
        "status": status,
        "input": {},
        "normalized_slots": {},
        "data": {
            "evidence_summary": {
                "has_department_catalog": has_catalog,
                "has_admission_or_plan": has_admission_or_plan,
                "evidence_count": len(evidence or []),
                "source_tables": [],
            },
            "evidence_gaps": [] if has_admission_or_plan else ["招生/录取证据"],
            "school_major_evidence": evidence or [],
        },
        "scope_notes": [],
        "data_gaps": data_gaps
        or [
            "校专业级工作地域分布",
            "校专业级薪资分布",
            "校专业级Top对口公司",
        ],
        "needs_clarification": [],
        "source_tables": [],
        "warnings": warnings if warnings is not None else ["已命中院系专业目录证据，但未命中该省份/科类/年份招生或录取证据。"],
    }


class SchoolMajorProfileAnswerEvalTests(unittest.TestCase):
    def test_tool_expectations_check_status_warning_and_evidence_summary(self):
        from scripts.evaluate_school_major_profile_answers import evaluate_tool_expectations

        case = {
            "expected_tool": {
                "status": "partial",
                "evidence_summary": {"has_department_catalog": True, "has_admission_or_plan": False},
                "must_have_evidence_gaps": ["招生/录取证据"],
                "must_have_warning_contains": ["未命中该省份/科类/年份招生或录取证据"],
            }
        }

        findings = evaluate_tool_expectations(case, _profile_result())

        self.assertEqual(findings, [])

    def test_answer_fails_when_partial_result_has_no_caveat(self):
        from scripts.evaluate_school_major_profile_answers import evaluate_answer

        case = {"risk_checks": ["partial_caveat"]}
        answer = "杭电计算机很强，浙江物理2025可以直接参考。"

        findings = evaluate_answer(case, answer, _profile_result())

        self.assertTrue(any(f["kind"] == "missing_partial_caveat" for f in findings))

    def test_answer_fails_when_school_level_employment_is_used_as_major_fact(self):
        from scripts.evaluate_school_major_profile_answers import evaluate_answer

        case = {"risk_checks": ["employment_scope"]}
        answer = "杭电计算机专业就业率很高，专业薪资在杭州也不错。"

        findings = evaluate_answer(case, answer, _profile_result())

        self.assertTrue(any(f["kind"] == "unsafe_school_major_employment_claim" for f in findings))

    def test_answer_fails_when_specialty_group_line_is_called_major_line(self):
        from scripts.evaluate_school_major_profile_answers import evaluate_answer

        case = {"risk_checks": ["admission_scope"]}
        profile = _profile_result(
            status="ok",
            has_admission_or_plan=True,
            evidence=[
                {
                    "source_type": "specialty_group",
                    "source_table": "edu_specialty_group_major",
                    "major_name": "计算机科学与技术",
                    "year": "2025",
                    "province": "32",
                    "subject_type": "物理",
                }
            ],
        )
        answer = "这个专业2025年在江苏物理的专业录取线是620分。"

        findings = evaluate_answer(case, answer, profile)

        self.assertTrue(any(f["kind"] == "specialty_group_as_major_line" for f in findings))

    def test_answer_fails_when_subject_context_mismatch_is_not_disclosed(self):
        from scripts.evaluate_school_major_profile_answers import evaluate_answer

        case = {
            "tool_args": {
                "province": "广东",
                "subject_type": "火星科",
                "year": 2025,
            },
            "risk_checks": ["context_mismatch"],
        }
        profile = _profile_result(
            status="ok",
            has_admission_or_plan=True,
            evidence=[
                {
                    "source_type": "plan",
                    "source_table": "edu_university_plan_special",
                    "major_name": "计算机科学与技术",
                    "year": "2025",
                    "province": "44",
                    "subject_type": "2073",
                }
            ],
        )
        answer = "广东2025年有招生计划，可以放心参考。"

        findings = evaluate_answer(case, answer, profile)

        self.assertTrue(any(f["kind"] == "undisclosed_context_mismatch" for f in findings))

    def test_load_cases_accepts_metadata_wrapper(self):
        from scripts.evaluate_school_major_profile_answers import load_cases

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "cases.json"
            path.write_text(
                json.dumps(
                    {
                        "metadata": {"version": 1},
                        "cases": [
                            {
                                "id": "hdu_cs",
                                "question": "杭电计算机怎么样？",
                                "tool_args": {
                                    "school_text": "杭州电子科技大学",
                                    "major_text": "计算机科学与技术",
                                },
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            cases = load_cases(path)

        self.assertEqual(cases[0]["id"], "hdu_cs")
        self.assertEqual(cases[0]["tool_args"]["school_text"], "杭州电子科技大学")

    def test_default_case_file_covers_core_boundary_families(self):
        from scripts.evaluate_school_major_profile_answers import DEFAULT_CASES_PATH, load_cases

        cases = load_cases(DEFAULT_CASES_PATH)
        case_ids = {case["id"] for case in cases}

        self.assertGreaterEqual(len(cases), 8)
        self.assertIn("hdu_cs_zj_physics_2025_partial", case_ids)
        self.assertIn("hdu_cs_zj_comprehensive_2025_ok", case_ids)
        self.assertIn("hdu_cs_gd_invalid_subject_2025_context_mismatch", case_ids)
        self.assertIn("hdu_nursing_unsafe_combo", case_ids)

    def test_markdown_report_includes_tool_trace_arguments(self):
        from scripts.evaluate_school_major_profile_answers import summarize_results, write_markdown_report

        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "report.md"
            results = [
                {
                    "id": "agent_case",
                    "question": "浙江物理2025年，杭电计算机怎么样？",
                    "ok": False,
                    "findings": [{"kind": "tool_status_mismatch", "message": "expected partial", "level": "error"}],
                    "answer": "回答",
                    "profile_result": _profile_result(),
                    "tool_trace": [
                        {
                            "tool_name": "school_major_profile",
                            "arguments": {"school_text": "杭州电子科技大学", "major_text": "计算机"},
                            "result": {"status": "needs_clarification"},
                        }
                    ],
                }
            ]

            write_markdown_report(report_path, results, summarize_results(results))
            report = report_path.read_text(encoding="utf-8")

        self.assertIn("Tool trace:", report)
        self.assertIn("school_major_profile", report)
        self.assertIn("计算机", report)

    def test_strong_oracle_passes_confirmed_catalog_and_context_absence(self):
        from scripts.evaluate_school_major_profile_answers import evaluate_strong_oracle

        case = {
            "strong_oracle": {
                "expected_status": "partial",
                "canonical": {"school_name": "杭州电子科技大学", "major_name": "计算机科学与技术"},
                "evidence": {"required_source_types": ["catalog"], "forbidden_context_source_types": ["admission_history"]},
                "context": {
                    "province": "浙江",
                    "subject_type": "物理",
                    "year": 2025,
                    "expected_match": "no_strict_context_match",
                },
            }
        }
        profile = _profile_result(
            status="partial",
            evidence=[
                {
                    "source_type": "catalog",
                    "source_table": "edu_university_department_major",
                    "major_name": "计算机科学与技术",
                }
            ],
        )
        profile["normalized_slots"] = {"school_name": "杭州电子科技大学", "major_name": "计算机科学与技术"}

        findings = evaluate_strong_oracle(case, profile)

        self.assertEqual(findings, [])

    def test_strong_oracle_fails_context_mismatch_without_required_warning(self):
        from scripts.evaluate_school_major_profile_answers import evaluate_strong_oracle

        case = {
            "strong_oracle": {
                "expected_status": "partial",
                "context": {
                    "province": "广东",
                    "subject_type": "火星科",
                    "year": 2025,
                    "expected_match": "no_strict_context_match",
                    "required_warning_contains": ["科类"],
                },
            }
        }
        profile = _profile_result(
            status="ok",
            has_admission_or_plan=True,
            warnings=[],
            evidence=[
                {
                    "source_type": "plan",
                    "source_table": "edu_university_plan_special",
                    "year": "2025",
                    "province": "44",
                    "subject_type": "2073",
                }
            ],
        )

        findings = evaluate_strong_oracle(case, profile)

        self.assertTrue(any(f["kind"] == "oracle_status_mismatch" for f in findings))
        self.assertTrue(any(f["kind"] == "oracle_missing_warning" for f in findings))

    def test_strong_oracle_requires_default_oracle_case_file(self):
        from scripts.evaluate_school_major_profile_answers import DEFAULT_STRONG_ORACLE_PATH, load_cases

        cases = load_cases(DEFAULT_STRONG_ORACLE_PATH)
        case_ids = {case["id"] for case in cases}

        self.assertGreaterEqual(len(cases), 8)
        self.assertTrue(all(case.get("strong_oracle") for case in cases))
        self.assertIn("oracle_hdu_cs_zj_physics_2025", case_ids)
        self.assertIn("oracle_hdu_cs_gd_invalid_subject_2025", case_ids)


if __name__ == "__main__":
    unittest.main()
