import unittest
from pathlib import Path


class WmuBatch197CurationTests(unittest.TestCase):
    def test_parse_pdf_line_keeps_scores_and_study_mode(self):
        from scripts.one_off.official_sources.curate_batch197_wmu import parse_pdf_line

        record = parse_pdf_line(
            "03099 匡梦轩 045400 应用心理 不区分研究方向 393 86.893 81.92 全日制",
            source_url="https://example.edu/wmu-first.pdf",
            title="温州医科大学2025年硕士研究生第一批拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "匡梦轩")
        self.assertEqual(record["student_id"], "03099")
        self.assertEqual(record["admission_major"], "045400 应用心理 不区分研究方向")
        self.assertIn("initial_total 393", record["remarks"])
        self.assertIn("retest_score 86.893", record["remarks"])
        self.assertIn("final_score 81.92", record["remarks"])
        self.assertIn("study_mode 全日制", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_parse_pdf_line_keeps_special_plan_note(self):
        from scripts.one_off.official_sources.curate_batch197_wmu import parse_pdf_line

        record = parse_pdf_line(
            "02959 张宾 105101 内科学 不区分研究方向 323 78.880 70.31 全日制 退役大学生士兵",
            source_url="https://example.edu/wmu-second.pdf",
            title="温州医科大学2025年硕士研究生第二批拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "张宾")
        self.assertEqual(record["admission_major"], "105101 内科学 不区分研究方向")
        self.assertIn("note 退役大学生士兵", record["remarks"])

    def test_parse_pdf_line_accepts_alphanumeric_major_code(self):
        from scripts.one_off.official_sources.curate_batch197_wmu import parse_pdf_line

        record = parse_pdf_line(
            "00122 付文俭 1001Z2 医学生物化学与分子生物学 不区分研究方向 325 82.600 72.04 全日制",
            source_url="https://example.edu/wmu-second.pdf",
            title="温州医科大学2025年硕士研究生第二批拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["admission_major"], "1001Z2 医学生物化学与分子生物学 不区分研究方向")

    def test_logical_rows_join_split_ethnic_name(self):
        from scripts.one_off.official_sources.curate_batch197_wmu import iter_logical_pdf_rows

        rows = list(
            iter_logical_pdf_rows(
                [
                    "01384 李彦蓉 100201 内科学 不区分研究方向 339 89.000 76.28 全日制",
                    "21735 卡德礼亚",
                    "·艾尼瓦 100201 内科学 不区分研究方向 337 89.600 76.28 全日制",
                    "00174 凡元圆 100201 内科学 不区分研究方向 341 86.200 75.40 全日制",
                ]
            )
        )

        self.assertEqual(
            rows[1],
            "21735 卡德礼亚·艾尼瓦 100201 内科学 不区分研究方向 337 89.600 76.28 全日制",
        )

    def test_curate_records_reparses_wmu_pdfs(self):
        from scripts.one_off.official_sources.curate_batch197_wmu import FIRST_PDF_SOURCE_URL, SECOND_PDF_SOURCE_URL, curate_records

        rows = curate_records(
            pdf_paths=[
                Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch197_direct_pdfs/yjsy.wmu.edu.cn/39b18c6a617113e4.pdf"
                ),
                Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch197_direct_pdfs/yjsy.wmu.edu.cn/f9b72ea4d8b98022.pdf"
                ),
            ]
        )

        self.assertEqual(len(rows), 2309)
        self.assertEqual(sum(row["source_url"] == FIRST_PDF_SOURCE_URL for row in rows), 1422)
        self.assertEqual(sum(row["source_url"] == SECOND_PDF_SOURCE_URL for row in rows), 887)
        self.assertFalse(any(row["person_name"] in {"号后五", "位", "示"} for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))


if __name__ == "__main__":
    unittest.main()
