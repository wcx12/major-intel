from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
RAW_PDF = (
    ROOT
    / "data/raw/official_recommendation_bift_2026_doctor_admission_first/"
    "bift_2026_doctor_admission_first.pdf"
)


def load_curator():
    path = ROOT / "scripts/one_off/official_sources/curate_bift_2026_doctor_admission_first.py"
    if not path.exists():
        raise AssertionError(f"curator script should exist: {path}")
    spec = importlib.util.spec_from_file_location("curate_bift_2026_doctor_admission_first", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load curator script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BiftDoctorAdmissionFirstCuratorTest(unittest.TestCase):
    def test_curate_records_from_official_pdf_keeps_only_final_admitted_rows(self) -> None:
        curator = load_curator()

        records = curator.curate_records(pdf_path=RAW_PDF)

        self.assertEqual(len(records), 35)
        self.assertTrue(all(row["school_name"] == "\u5317\u4eac\u670d\u88c5\u5b66\u9662" for row in records))
        self.assertTrue(all(row["year"] == "2026" for row in records))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in records))
        self.assertTrue(all(row["student_id"].startswith("100126") for row in records))
        self.assertTrue(all("admission_status \u62df\u5f55\u53d6" in row["remarks"] for row in records))
        self.assertFalse(any("\u62df\u4e0d\u5f55\u53d6" in row["remarks"] for row in records))

        by_id = {row["student_id"]: row for row in records}
        self.assertEqual(by_id["100126100000114"]["person_name"], "\u674e\u6cfd\u5947")
        self.assertEqual(by_id["100126100000114"]["admission_major"], "01\u8bbe\u8ba1\u5386\u53f2\u4e0e\u7406\u8bba")
        self.assertIn("material_review_score 84.63", by_id["100126100000114"]["remarks"])
        self.assertIn("comprehensive_assessment_score 87.54", by_id["100126100000114"]["remarks"])
        self.assertIn("total_score 86.67", by_id["100126100000114"]["remarks"])
        self.assertIn("official_pdf_download true", by_id["100126100000114"]["remarks"])


if __name__ == "__main__":
    unittest.main()
