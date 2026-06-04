import importlib
import unittest
from pathlib import Path


RAW_TEXT = Path(
    "data/raw/official_site_recommendation_web_visible_dlou_2024_adjustment_second_batch/"
    "dlou_2024_adjustment_second_batch_pdf_text.txt"
)


def _load_curate_text():
    module_name = "scripts.one_off.official_sources.curate_dlou_2024_adjustment_second_batch_web_visible"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name:
            raise AssertionError("DLOU 2024 web-visible adjustment curator is missing") from exc
        raise
    return module.curate_text


class Dlou2024AdjustmentSecondBatchWebVisibleTests(unittest.TestCase):
    def test_curates_all_web_visible_adjustment_admission_rows(self):
        rows = _load_curate_text()(RAW_TEXT.read_text(encoding="utf-8"))

        self.assertEqual(len(rows), 51)
        self.assertTrue(all(row["school_name"] == "大连海洋大学" for row in rows))
        self.assertTrue(all(row["year"] == 2024 for row in rows))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in rows))
        self.assertTrue(all(row["route"] == "postgraduate_exam_or_admission" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "孙佳兵")
        self.assertEqual(first["student_id"], "103074210000584")
        self.assertEqual(first["college"], "水产与生命学院")
        self.assertEqual(first["major"], "095134渔业发展")
        self.assertEqual(first["admission_major"], "095134渔业发展")
        self.assertIn("college_code 001", first["remarks"])
        self.assertIn("research_direction 水产养殖技术", first["remarks"])
        self.assertIn("admission_score 85.38", first["remarks"])
        self.assertIn("admission_type 非定向", first["remarks"])
        self.assertIn("official_web_visible_pdf_text true", first["remarks"])

        minority_plan = rows[13]
        self.assertEqual(minority_plan["person_name"], "王泽旭")
        self.assertIn("admission_type 定向", minority_plan["remarks"])
        self.assertIn("note 少数民族骨干计划", minority_plan["remarks"])

        last = rows[-1]
        self.assertEqual(last["ranking"], "51")
        self.assertEqual(last["person_name"], "于淼")
        self.assertEqual(last["college"], "海洋法律与人文学院")
        self.assertIn("local_pdf_fetch HTTP 404 196_byte_html", last["remarks"])


if __name__ == "__main__":
    unittest.main()
