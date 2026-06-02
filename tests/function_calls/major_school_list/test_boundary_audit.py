import unittest

from scripts.major_school_list_oracles import build_oracle_major_school_sql
from scripts.evaluate_major_school_list_boundaries import (
    AuditCase,
    AuditResult,
    DEFAULT_CASES_PATH,
    classify_result,
    load_cases,
    render_markdown_report,
)


class MajorSchoolListBoundaryAuditTests(unittest.TestCase):
    def test_default_cases_load_from_major_school_list_function_call_folder(self):
        cases = load_cases(DEFAULT_CASES_PATH)
        case_ids = {case.case_id for case in cases}

        self.assertIn("tests/function_calls/major_school_list", DEFAULT_CASES_PATH.as_posix())
        self.assertGreaterEqual(len(cases), 24)
        self.assertIn("cs_zhejiang_undergrad_dual_key", case_ids)
        self.assertIn("cs_zhejiang_province_suffix", case_ids)
        self.assertIn("law_beijing_municipality_suffix", case_ids)
        self.assertIn("cs_nationwide_211_flag", case_ids)
        self.assertIn("ecommerce_cross_level_warning", case_ids)
        self.assertIn("ecommerce_zhejiang_suffix_warning", case_ids)
        self.assertIn("limit_float_decimal", case_ids)
        self.assertIn("limit_bool_true", case_ids)
        self.assertIn("limit_text", case_ids)
        self.assertIn("limit_negative", case_ids)

    def test_load_cases_preserves_invalid_limit_values_for_audit(self):
        cases_by_id = {case.case_id: case for case in load_cases(DEFAULT_CASES_PATH)}

        self.assertEqual(cases_by_id["limit_float_decimal"].limit, 1.5)
        self.assertIs(cases_by_id["limit_bool_true"].limit, True)
        self.assertEqual(cases_by_id["limit_text"].limit, "ten")

    def test_oracle_sql_matches_school_code_and_school_id(self):
        major = {"code": "080901", "special_name": "Computer Science"}

        sql = build_oracle_major_school_sql(
            major,
            province_filter="Zhejiang",
            school_level_filter="Undergraduate",
            limit=30,
        )

        self.assertIn("u.code = CAST(sm.school_id AS CHAR)", sql)
        self.assertIn("CAST(u.school_id AS CHAR) = CAST(sm.school_id AS CHAR)", sql)
        self.assertIn("sm.major_code = '080901'", sql)
        self.assertIn("sm.major_name = 'Computer Science'", sql)
        self.assertIn("u.province_name = 'Zhejiang'", sql)
        self.assertIn("u.level_name LIKE '%Undergraduate%'", sql)
        self.assertIn("LIMIT 30", sql)

    def test_classify_result_flags_key_mismatch_when_oracle_has_more_schools(self):
        result = AuditResult(
            case=AuditCase(case_id="cs_zhejiang", major="Computer Science", province_filter="Zhejiang"),
            tool_status="ok",
            tool_school_count=2,
            oracle_school_count=6,
            relation_counts={"matches_code": 2, "matches_school_id": 4, "other": 0},
            missing_school_names=["Zhejiang Gongshang University"],
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "key_mismatch")
        self.assertEqual(classified.verdict, "fail")
        self.assertIn("school_id", classified.reason)

    def test_classify_result_flags_province_normalization_gap(self):
        result = AuditResult(
            case=AuditCase(case_id="zhejiang_suffix", major="Computer Science", province_filter="浙江省"),
            tool_status="not_found",
            tool_school_count=0,
            oracle_school_count=6,
            relation_counts={"matches_code": 2, "matches_school_id": 4, "other": 0},
            missing_school_names=["浙江工业大学"],
            normalized_province_filter="浙江",
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "province_normalization_gap")
        self.assertEqual(classified.verdict, "fail")
        self.assertIn("省份", classified.reason)

    def test_classify_result_flags_missing_expected_warning(self):
        result = AuditResult(
            case=AuditCase(
                case_id="ecommerce",
                major="电子商务",
                expected_warning_substrings=["同名专业存在多个层次"],
            ),
            tool_status="ok",
            tool_school_count=1,
            oracle_school_count=1,
            relation_counts={"matches_code": 1, "matches_school_id": 0, "other": 0},
            missing_school_names=[],
            warnings=[],
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "warning_propagation_gap")
        self.assertEqual(classified.verdict, "fail")
        self.assertIn("warning", classified.reason)

    def test_classify_result_marks_invalid_limit_needs_clarification_as_pass(self):
        result = AuditResult(
            case=AuditCase(case_id="negative_limit", major="Computer Science", limit=-1),
            tool_status="needs_clarification",
            tool_school_count=0,
            oracle_school_count=0,
            relation_counts={},
            missing_school_names=[],
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "pass")
        self.assertEqual(classified.verdict, "pass")

    def test_classify_result_marks_non_integral_limit_needs_clarification_as_pass(self):
        for limit in [True, 1.5, "ten"]:
            with self.subTest(limit=repr(limit)):
                result = AuditResult(
                    case=AuditCase(case_id="invalid_limit", major="Computer Science", limit=limit),
                    tool_status="needs_clarification",
                    tool_school_count=0,
                    oracle_school_count=0,
                    relation_counts={},
                    missing_school_names=[],
                )

                classified = classify_result(result)

                self.assertEqual(classified.classification, "pass")
                self.assertEqual(classified.verdict, "pass")

    def test_classify_result_flags_non_integral_limit_that_reaches_tool_results(self):
        result = AuditResult(
            case=AuditCase(case_id="float_limit", major="Computer Science", limit=1.5),
            tool_status="ok",
            tool_school_count=1,
            oracle_school_count=1,
            relation_counts={"matches_code": 1, "matches_school_id": 0, "other": 0},
            missing_school_names=[],
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "input_validation_gap")
        self.assertEqual(classified.verdict, "fail")

    def test_markdown_report_includes_school_samples_and_classification(self):
        result = classify_result(
            AuditResult(
                case=AuditCase(case_id="mixed_key", major="Computer Science", province_filter="Zhejiang"),
                tool_status="ok",
                tool_school_count=2,
                oracle_school_count=4,
                relation_counts={"matches_code": 2, "matches_school_id": 2, "other": 0},
                missing_school_names=["School A", "School B"],
            )
        )

        markdown = render_markdown_report([result])

        self.assertIn("# major_school_list 边界审计报告", markdown)
        self.assertIn("## 分类汇总", markdown)
        self.assertIn("- 判定：", markdown)
        self.assertIn("- 分类：", markdown)
        self.assertIn("- 原因：", markdown)
        self.assertIn("- 漏召回学校样本：", markdown)
        self.assertIn("mixed_key", markdown)
        self.assertIn("key_mismatch", markdown)
        self.assertIn("School A", markdown)
        self.assertIn("School B", markdown)


if __name__ == "__main__":
    unittest.main()
