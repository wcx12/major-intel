from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
RAW_PDF = (
    ROOT
    / "data/raw/official_recommendation_nwnu_jykxxy_2025_master_first_choice/"
    "nwnu_jykxxy_2025_master_first_choice.pdf"
)


def load_curator():
    path = ROOT / "scripts/one_off/official_sources/curate_nwnu_jykxxy_2025_master_first_choice.py"
    if not path.exists():
        raise AssertionError(f"curator script should exist: {path}")
    spec = importlib.util.spec_from_file_location("curate_nwnu_jykxxy_2025", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load curator script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NwnuJykxxyCuratorTest(unittest.TestCase):
    def test_parse_pdf_line_keeps_admitted_row_and_rejects_not_admitted_row(self) -> None:
        curator = load_curator()

        admitted = curator.parse_pdf_line(
            "1    107365030001273   马若楠   040101    教育学原理   "
            "374   81.16   0.3   76.71    拟录取      全日制"
        )
        self.assertIsNotNone(admitted)
        self.assertEqual(admitted["ranking"], "1")
        self.assertEqual(admitted["student_id"], "107365030001273")
        self.assertEqual(admitted["person_name"], "马若楠")
        self.assertEqual(admitted["admission_major"], "教育学原理")
        self.assertIn("initial_score 374", admitted["remarks"])
        self.assertIn("study_mode 全日制", admitted["remarks"])

        not_admitted = curator.parse_pdf_line(
            "17   107365030001289   周婷婷   040101   教育学原理    "
            "332   70.20   0.3   67.54   不予录取      全日制     复试面试不合格"
        )
        self.assertIsNone(not_admitted)

    def test_curate_records_from_pdf_counts_only_final_admitted_rows(self) -> None:
        curator = load_curator()

        records = curator.curate_records(pdf_path=RAW_PDF)

        self.assertEqual(len(records), 106)
        self.assertTrue(all(row["school_name"] == "西北师范大学" for row in records))
        self.assertTrue(all(row["college"] == "教育科学学院" for row in records))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in records))
        self.assertTrue(all("not_admitted_excluded" not in row["remarks"] for row in records))
        self.assertTrue(
            any(
                row["student_id"] == "107365030001215"
                and "享受少数民族照顾政策" in row["remarks"]
                for row in records
            )
        )
        self.assertTrue(
            any(
                row["student_id"] == "107365030001639"
                and "特岗教师初试加10分" in row["remarks"]
                for row in records
            )
        )


if __name__ == "__main__":
    unittest.main()
