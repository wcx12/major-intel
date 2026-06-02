import json
import unittest
from pathlib import Path


CASES_PATH = Path(__file__).with_name("boundary_cases.json")


class MajorSchoolListBoundaryCasesManifestTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        self.cases = self.payload["cases"]

    def test_cases_have_unique_ids_and_required_fields(self):
        case_ids = [case["case_id"] for case in self.cases]

        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertGreaterEqual(len(self.cases), 12)
        for case in self.cases:
            self.assertIn("major", case)
            self.assertIn("limit", case)
            self.assertIn("note", case)
            self.assertIsInstance(case["case_id"], str)
            self.assertTrue(case["case_id"].strip())
            self.assertIsInstance(case["major"], str)
            self.assertTrue(case["major"].strip())
            self.assertIsInstance(case["limit"], int)

    def test_cases_cover_known_major_school_list_risk_classes(self):
        case_ids = {case["case_id"] for case in self.cases}

        required_case_ids = {
            "cs_zhejiang_undergrad_dual_key",
            "cs_nationwide_undergrad_dual_key",
            "cs_zhejiang_province_suffix",
            "alias_jike_zhejiang_undergrad",
            "broad_computer_needs_clarification",
            "major_not_found",
            "ecommerce_cross_level_warning",
            "cs_zhejiang_985_empty",
            "limit_zero",
            "limit_negative",
        }
        self.assertTrue(required_case_ids.issubset(case_ids))

    def test_known_contract_cases_are_marked_explicitly(self):
        cases_by_id = {case["case_id"]: case for case in self.cases}

        self.assertEqual(cases_by_id["broad_computer_needs_clarification"].get("expected_status"), "needs_clarification")
        self.assertEqual(cases_by_id["major_not_found"].get("expected_status"), "not_found")
        self.assertEqual(cases_by_id["limit_zero"].get("expected_status"), "needs_clarification")
        self.assertIn("正整数", cases_by_id["limit_zero"]["note"])
        self.assertEqual(cases_by_id["limit_negative"].get("expected_status"), "needs_clarification")
        self.assertIn("正整数", cases_by_id["limit_negative"]["note"])
        self.assertIn("同名专业存在多个层次", cases_by_id["ecommerce_cross_level_warning"]["expected_warning_substrings"])


if __name__ == "__main__":
    unittest.main()
