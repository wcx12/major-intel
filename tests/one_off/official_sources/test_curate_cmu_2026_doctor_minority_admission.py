from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
RAW_HTML = (
    ROOT
    / "data/raw/official_recommendation_cmu_2026_doctor_minority_admission/"
    "cmu_2026_doctor_minority_admission.html"
)


def load_curator():
    path = ROOT / "scripts/one_off/official_sources/curate_cmu_2026_doctor_minority_admission.py"
    if not path.exists():
        raise AssertionError(f"curator script should exist: {path}")
    spec = importlib.util.spec_from_file_location("curate_cmu_2026_doctor_minority", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load curator script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CmuDoctorMinorityAdmissionCuratorTest(unittest.TestCase):
    def test_curate_records_from_official_html_table(self) -> None:
        curator = load_curator()

        records = curator.curate_records(html_path=RAW_HTML)

        self.assertEqual(len(records), 3)
        self.assertTrue(all(row["school_name"] == "\u4e2d\u56fd\u533b\u79d1\u5927\u5b66" for row in records))
        self.assertTrue(all(row["year"] == "2026" for row in records))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in records))
        self.assertTrue(all(row["route"] == "postgraduate_exam_or_admission" for row in records))
        self.assertTrue(all(row["student_id"].startswith("10159999") for row in records))
        self.assertTrue(all("official_html_table true" in row["remarks"] for row in records))
        self.assertTrue(all("minority_backbone_plan true" in row["remarks"] for row in records))

        by_id = {row["student_id"]: row for row in records}
        self.assertEqual(by_id["1015999980"]["person_name"], "\u5b8b\u6d77\u5b81")
        self.assertEqual(by_id["1015999980"]["college"], "\u7b2c\u4e00\u4e34\u5e8a\u5b66\u9662")
        self.assertEqual(by_id["1015999980"]["major"], "\u5185\u79d1\u5b66")
        self.assertIn("major_code 105101", by_id["1015999980"]["remarks"])
        self.assertIn("department \u98ce\u6e7f\u514d\u75ab\u79d1", by_id["1015999980"]["remarks"])
        self.assertIn("total_score 86", by_id["1015999980"]["remarks"])


if __name__ == "__main__":
    unittest.main()
