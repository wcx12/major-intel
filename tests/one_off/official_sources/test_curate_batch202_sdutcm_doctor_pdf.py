import unittest
from pathlib import Path


class SdutcmBatch202DoctorPdfCurationTests(unittest.TestCase):
    def test_parse_doctor_line_keeps_scores_and_major(self):
        from scripts.one_off.official_sources.curate_batch202_sdutcm_doctor_pdf import parse_doctor_line

        record = parse_doctor_line(
            "1044199518 中医学院 袁顺 100501 中医基础理论 60.00 88.25 79.78",
            source_url="https://example.edu/sdutcm.pdf",
            title="山东中医药大学2026年全日制博士研究生第一批次拟录取名单公示",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "袁顺")
        self.assertEqual(record["student_id"], "1044199518")
        self.assertEqual(record["college"], "中医学院")
        self.assertEqual(record["admission_major"], "100501 中医基础理论")
        self.assertIn("material_score 60.00", record["remarks"])
        self.assertIn("assessment_score 88.25", record["remarks"])
        self.assertIn("final_score 79.78", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_parse_doctor_line_accepts_z_major_code(self):
        from scripts.one_off.official_sources.curate_batch202_sdutcm_doctor_pdf import parse_doctor_line

        record = parse_doctor_line(
            "1044199717 卫生管理学院 王凯正 1005Z3 中医药管理学 69.40 90.10 83.89",
            source_url="https://example.edu/sdutcm.pdf",
            title="山东中医药大学2026年全日制博士研究生第一批次拟录取名单公示",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "王凯正")
        self.assertEqual(record["college"], "卫生管理学院")
        self.assertEqual(record["admission_major"], "1005Z3 中医药管理学")

    def test_curate_records_reparses_all_doctor_rows(self):
        from scripts.one_off.official_sources.curate_batch202_sdutcm_doctor_pdf import SOURCE_URL, curate_records

        rows = curate_records(
            Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch202_sdutcm_doctor_pdf/yjs.sdutcm.edu.cn/cb583ad75967bb89.pdf"
            )
        )

        self.assertEqual(len(rows), 133)
        self.assertEqual({row["source_url"] for row in rows}, {SOURCE_URL})
        self.assertFalse(any(row["person_name"].startswith("第 ") for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))


if __name__ == "__main__":
    unittest.main()
