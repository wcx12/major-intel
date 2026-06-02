import unittest

from scripts.school_major_list_oracles import build_oracle_school_major_sql
from scripts.evaluate_school_major_list_boundaries import (
    AuditCase,
    AuditResult,
    DEFAULT_CASES_PATH,
    classify_result,
    load_cases,
    render_markdown_report,
)


class SchoolMajorListBoundaryAuditTests(unittest.TestCase):
    def test_default_cases_load_from_school_major_list_function_call_folder(self):
        cases = load_cases(DEFAULT_CASES_PATH)
        case_ids = {case.case_id for case in cases}

        self.assertIn("tests/function_calls/school_major_list", DEFAULT_CASES_PATH.as_posix())
        self.assertGreaterEqual(len(cases), 30)
        self.assertIn("hdu_cs", case_ids)
        self.assertIn("hdu_vocational_category_noise", case_ids)
        self.assertIn("uestc_cs", case_ids)
        self.assertIn("cupl_limit_negative", case_ids)

    def test_oracle_sql_matches_both_school_code_and_school_id(self):
        school = {
            "name": "Example University",
            "code": "CODE100",
            "school_id": "SID200",
            "school_site": "https://www.example.edu.cn/",
        }

        sql = build_oracle_school_major_sql(school, major_category="Computer")

        self.assertIn("sm.school_id IN ('CODE100', 'SID200')", sql)
        self.assertIn("sm.school_name = 'Example University'", sql)
        self.assertIn("FROM edu_university_department_major dm", sql)
        self.assertIn("JOIN edu_university_department d ON d.id = dm.dept_id", sql)
        self.assertIn("d.school_id = 'SID200'", sql)
        self.assertIn("d.website_url LIKE '%example.edu.cn%'", sql)
        self.assertIn("sm.menlei_name LIKE '%Computer%'", sql)
        self.assertIn("sm.level3_name LIKE '%Computer%'", sql)
        self.assertIn("sm.xueke_name LIKE '%Computer%'", sql)
        self.assertIn("sm.major_name LIKE '%Computer%'", sql)
        self.assertIn("FROM edu_major m", sql)
        self.assertIn("REPLACE(REPLACE(", sql)
        self.assertIn("sm.major_code IS NULL OR sm.major_code = ''", sql)
        self.assertIn("dm.major_code IS NULL OR dm.major_code = ''", sql)
        self.assertIn("m.special_name", sql)
        self.assertIn("m.level2_name LIKE '%Computer%'", sql)
        self.assertIn("m.level3_name LIKE '%Computer%'", sql)
        self.assertIn("m.special_name LIKE '%Computer%'", sql)

    def test_classify_result_flags_key_mismatch_when_oracle_has_more_rows(self):
        result = AuditResult(
            case=AuditCase(case_id="cqupt_cs", school="CQUpt", major_category="Computer"),
            tool_status="not_found",
            tool_major_count=0,
            oracle_major_count=5,
            oracle_all_major_count=18,
            relation_counts={"matches_code": 2, "matches_school_id": 16, "other": 0},
            missing_major_names=["Computer Science"],
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "key_mismatch")
        self.assertEqual(classified.verdict, "fail")
        self.assertIn("school_id", classified.reason)

    def test_classify_result_marks_zero_category_match_as_pass_when_oracle_agrees(self):
        result = AuditResult(
            case=AuditCase(case_id="hdu_engineering", school="HDU", major_category="Engineering"),
            tool_status="not_found",
            tool_major_count=0,
            oracle_major_count=0,
            oracle_all_major_count=8,
            relation_counts={"matches_code": 8, "matches_school_id": 0, "other": 0},
            missing_major_names=[],
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "pass")
        self.assertEqual(classified.verdict, "pass")

    def test_classify_result_marks_invalid_limit_needs_clarification_as_pass(self):
        result = AuditResult(
            case=AuditCase(case_id="negative_limit", school="CUPL", limit=-1),
            tool_status="needs_clarification",
            tool_major_count=0,
            oracle_major_count=0,
            oracle_all_major_count=0,
            relation_counts={},
            missing_major_names=[],
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "pass")
        self.assertEqual(classified.verdict, "pass")

    def test_classify_result_marks_positive_limit_truncation_before_key_mismatch(self):
        result = AuditResult(
            case=AuditCase(case_id="limit_one", school="CUPL", limit=1),
            tool_status="ok",
            tool_major_count=1,
            oracle_major_count=24,
            oracle_all_major_count=24,
            relation_counts={"matches_code": 21, "matches_school_id": 3, "other": 0},
            missing_major_names=["Law", "Sociology"],
        )

        classified = classify_result(result)

        self.assertEqual(classified.classification, "limit_truncated")
        self.assertEqual(classified.verdict, "pass")

    def test_markdown_report_includes_missing_majors_and_classification(self):
        result = classify_result(
            AuditResult(
                case=AuditCase(case_id="mixed_key", school="Mixed Key University"),
                tool_status="ok",
                tool_major_count=2,
                oracle_major_count=4,
                oracle_all_major_count=4,
                relation_counts={"matches_code": 2, "matches_school_id": 2, "other": 0},
                missing_major_names=["Software Engineering", "Network Security"],
            )
        )

        markdown = render_markdown_report([result])

        self.assertIn("# school_major_list 边界审计报告", markdown)
        self.assertIn("## 分类汇总", markdown)
        self.assertIn("- 判定：", markdown)
        self.assertIn("- 分类：", markdown)
        self.assertIn("- 原因：", markdown)
        self.assertIn("- 漏召回专业样本：", markdown)
        self.assertIn("mixed_key", markdown)
        self.assertIn("key_mismatch", markdown)
        self.assertIn("Software Engineering", markdown)
        self.assertIn("Network Security", markdown)


if __name__ == "__main__":
    unittest.main()
