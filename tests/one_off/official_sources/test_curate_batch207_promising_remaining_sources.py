import unittest
from pathlib import Path


class Batch207PromisingRemainingSourcesCurationTests(unittest.TestCase):
    def test_parse_xsyu_pdf_line_keeps_final_school_level_fields(self):
        from scripts.one_off.official_sources.curate_batch207_promising_remaining_sources import parse_xsyu_pdf_line

        record = parse_xsyu_pdf_line("蔡新如 经济管理学院 020204 金融学")

        self.assertIsNotNone(record)
        self.assertEqual(record["school_name"], "西安石油大学")
        self.assertEqual(record["person_name"], "蔡新如")
        self.assertEqual(record["college"], "经济管理学院")
        self.assertEqual(record["major"], "020204")
        self.assertEqual(record["admission_major"], "020204 金融学")
        self.assertEqual(record["remarks"], "")
        self.assertFalse(record["needs_review"])

    def test_parse_xsyu_pdf_line_keeps_special_route_remark(self):
        from scripts.one_off.official_sources.curate_batch207_promising_remaining_sources import parse_xsyu_pdf_line

        record = parse_xsyu_pdf_line("虞茗荃 石油工程学院 082000 石油与天然气工程 支教团")

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "虞茗荃")
        self.assertEqual(record["college"], "石油工程学院")
        self.assertEqual(record["admission_major"], "082000 石油与天然气工程")
        self.assertEqual(record["remarks"], "支教团")
        self.assertFalse(record["needs_review"])

    def test_curate_records_uses_school_level_final_pdf_without_preliminary_college_rows(self):
        from scripts.one_off.official_sources.curate_batch207_promising_remaining_sources import curate_records

        rows = curate_records(
            xsyu_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch207_promising_remaining_sources/yjszs.xsyu.edu.cn/cd195ee12b216126.pdf"
            )
        )

        self.assertEqual(len(rows), 54)
        self.assertEqual({row["school_name"] for row in rows}, {"西安石油大学"})
        self.assertEqual(sum(row["remarks"] == "直博生" for row in rows), 6)
        self.assertEqual(sum(row["remarks"] == "支教团" for row in rows), 8)
        self.assertFalse(any(row["person_name"] == "姓名" for row in rows))
        self.assertFalse(any(row["person_name"] in {"温家怡", "郭亚冰", "许景芮"} for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))


if __name__ == "__main__":
    unittest.main()
