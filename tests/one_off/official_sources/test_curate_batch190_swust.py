import unittest
from pathlib import Path


class SwustBatch190CurationTests(unittest.TestCase):
    def test_parse_pdf_admission_line_keeps_scores_and_major(self):
        from scripts.one_off.official_sources.curate_batch190_swust import parse_pdf_admission_line

        line = "106196025103974 曹力         109|经济管理学院   025100|金融         全日制   非定向    60   60    107   138   365   83.00   76.00"

        record = parse_pdf_admission_line(
            line,
            source_url="https://example.edu/swust.pdf",
            title="西南科技大学2026年拟录取硕士研究生名单.pdf",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "曹力")
        self.assertEqual(record["student_id"], "106196025103974")
        self.assertEqual(record["college"], "109|经济管理学院")
        self.assertEqual(record["admission_major"], "025100|金融")
        self.assertIn("study_mode 全日制", record["remarks"])
        self.assertIn("initial_total 365", record["remarks"])
        self.assertIn("final_score 76.00", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_parse_pdf_admission_line_keeps_long_ethnic_name(self):
        from scripts.one_off.official_sources.curate_batch190_swust import parse_pdf_admission_line

        line = "145966008000175 阿迪莱·阿卜力克木 109|经济管理学院    025100|金融         全日制   非定向    52   69    95    131   347   89.76   75.51"

        record = parse_pdf_admission_line(
            line,
            source_url="https://example.edu/swust.pdf",
            title="西南科技大学2026年拟录取硕士研究生名单.pdf",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "阿迪莱·阿卜力克木")
        self.assertEqual(record["college"], "109|经济管理学院")
        self.assertEqual(record["admission_major"], "025100|金融")
        self.assertIn("subject1 52", record["remarks"])

    def test_parse_pdf_admission_line_keeps_special_plan_note(self):
        from scripts.one_off.official_sources.curate_batch190_swust import parse_pdf_admission_line

        line = "106196000009962 夏海波        109|经济管理学院   125100|工商管理     非全日制   定向     0    0      0     0     0    74.72   74.72   立功表彰退役军人免初试"

        record = parse_pdf_admission_line(
            line,
            source_url="https://example.edu/swust.pdf",
            title="西南科技大学2026年拟录取硕士研究生名单.pdf",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "夏海波")
        self.assertIn("study_mode 非全日制", record["remarks"])
        self.assertIn("admission_category 定向", record["remarks"])
        self.assertIn("note 立功表彰退役军人免初试", record["remarks"])

    def test_curate_records_reparses_pdf_and_drops_page_mottos(self):
        from scripts.one_off.official_sources.curate_batch190_swust import PDF_SOURCE_URL, curate_records

        rows = curate_records(
            input_csv=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch190_swust/records.csv"
            ),
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch190_swust/gs.swust.edu.cn/bcce9edb59effe25.pdf"
            ),
        )

        self.assertEqual(len(rows), 2274)
        self.assertEqual(sum(row["source_url"] == PDF_SOURCE_URL for row in rows), 2237)
        self.assertEqual(
            sum(row["route"] == "recommendation_exemption" for row in rows),
            37,
        )
        self.assertFalse(any(row["person_name"] in {"学科为首", "学生为本", "学者为基", "学术为要"} for row in rows))
        self.assertFalse(any(row["person_name"] in {"总成绩", "入学考试", ""} for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))


if __name__ == "__main__":
    unittest.main()
