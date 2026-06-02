import json
import unittest
from pathlib import Path


CASES_PATH = Path(__file__).with_name("boundary_cases.json")


class SchoolMajorListBoundaryCasesManifestTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        self.cases = self.payload["cases"]

    def test_cases_have_unique_ids_and_required_fields(self):
        case_ids = [case["case_id"] for case in self.cases]

        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertGreaterEqual(len(self.cases), 30)
        for case in self.cases:
            self.assertIn("school", case)
            self.assertIn("limit", case)
            self.assertIn("note", case)
            self.assertIsInstance(case["case_id"], str)
            self.assertTrue(case["case_id"].strip())
            self.assertIsInstance(case["school"], str)
            self.assertTrue(case["school"].strip())
            self.assertIsInstance(case["limit"], int)

    def test_cases_cover_known_school_major_list_risk_classes(self):
        case_ids = {case["case_id"] for case in self.cases}

        required_case_ids = {
            "hdu_cs",
            "hdu_digital_media",
            "hdu_vocational_category_noise",
            "cqupt_cs",
            "nuaa_aerospace",
            "uestc_cs",
            "jlu_cs",
            "taizhou_cs",
            "xinzhou_cs",
            "nanda_alias",
            "jiaoda_alias",
            "huada_alias",
            "cupl_limit_0",
            "cupl_limit_negative",
        }
        self.assertTrue(required_case_ids.issubset(case_ids))

    def test_expected_failure_cases_are_marked_explicitly(self):
        cases_by_id = {case["case_id"]: case for case in self.cases}

        self.assertEqual(cases_by_id["huada_alias"].get("expected_status"), "needs_clarification")
        self.assertIn("暂不修", cases_by_id["huada_alias"]["note"])
        self.assertIn("暂不修", cases_by_id["cupl_limit_0"]["note"])
        self.assertIn("暂不修", cases_by_id["cupl_limit_negative"]["note"])


if __name__ == "__main__":
    unittest.main()
