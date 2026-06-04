import csv
import tempfile
import unittest
from pathlib import Path


class CurateCupl2016RecommendationWebVisibleTest(unittest.TestCase):
    def test_extract_records_from_web_visible_pdf_text(self):
        from scripts.one_off.official_sources.curate_cupl_2016_recommendation_web_visible import (
            SOURCE_URL,
            extract_records_from_text,
        )

        text = """
中国政法大学2016年推免生拟录取名单
序号 姓名 证件号码 拟录取学院 拟录取专业 复试成绩
1 **燕 110108********3422 法学院 法学理论 79.6
2 **蕾 230206********1140 民商经济法学院 民商法学 78.6
"""

        rows = extract_records_from_text(text)

        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertEqual(first["school_name"], "中国政法大学")
        self.assertEqual(first["year"], 2016)
        self.assertEqual(first["document_type"], "incoming_recommendation_admission_list")
        self.assertEqual(first["route"], "recommendation_exemption")
        self.assertEqual(first["person_name"], "**燕")
        self.assertEqual(first["student_id"], "110108********3422")
        self.assertEqual(first["college"], "法学院")
        self.assertEqual(first["major"], "法学理论")
        self.assertEqual(first["admission_major"], "法学理论")
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["source_url"], SOURCE_URL)
        self.assertIn("复试成绩 79.6", first["remarks"])
        self.assertIn("official_web_visible_pdf_text", first["remarks"])

    def test_write_outputs_produces_clean_summary_and_public_rows(self):
        from scripts.one_off.official_sources.curate_cupl_2016_recommendation_web_visible import write_outputs

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            raw_text = tmp / "cupl.txt"
            output_dir = tmp / "out"
            raw_text.write_text(
                "\n".join(
                    [
                        "中国政法大学2016年推免生拟录取名单",
                        "序号 姓名 证件号码 拟录取学院 拟录取专业 复试成绩",
                        "1 **燕 110108********3422 法学院 法学理论 79.6",
                        "2 **蕾 230206********1140 民商经济法学院 民商法学 78.6",
                    ]
                ),
                encoding="utf-8",
            )

            result = write_outputs(raw_text_path=raw_text, output_dir=output_dir)

            self.assertEqual(result["curated"], 2)
            with (output_dir / "records_clean_curated.csv").open(
                "r", encoding="utf-8-sig", newline=""
            ) as handle:
                clean_rows = list(csv.DictReader(handle))
            with (output_dir / "school_year_summary_curated.csv").open(
                "r", encoding="utf-8-sig", newline=""
            ) as handle:
                summary_rows = list(csv.DictReader(handle))
            with (output_dir / "records_public_curated.csv").open(
                "r", encoding="utf-8-sig", newline=""
            ) as handle:
                public_rows = list(csv.DictReader(handle))

            self.assertEqual(len(clean_rows), 2)
            self.assertEqual(clean_rows[0]["person_name"], "**燕")
            self.assertEqual(clean_rows[0]["student_id_masked"], "1101**************")
            self.assertEqual(summary_rows[0]["record_count"], "2")
            self.assertEqual(len(public_rows), 2)


if __name__ == "__main__":
    unittest.main()
