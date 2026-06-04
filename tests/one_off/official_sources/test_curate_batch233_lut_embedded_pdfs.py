import unittest
from pathlib import Path


class Batch233LutEmbeddedPdfsCurationTests(unittest.TestCase):
    def test_curate_batch233_rebuilds_lut_embedded_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch233_lut_embedded_pdfs import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch233_lut_embedded_pdfs"
            )
        )

        self.assertEqual(len(rows), 12)
        self.assertEqual(sum(row["school_name"] == "兰州理工大学" for row in rows), 12)
        self.assertEqual(len({row["student_id"] for row in rows}), 12)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "黄宪雨")
        self.assertEqual(first["student_id"], "107316371704595")
        self.assertEqual(first["college"], "微电子现代产业学院")
        self.assertEqual(first["admission_major"], "仪器仪表工程")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("initial_score 270", first["remarks"])
        self.assertIn("total_score 63.61", first["remarks"])

        special = next(row for row in rows if row["student_id"] == "1073116107310007")
        self.assertEqual(special["person_name"], "戴蓬")
        self.assertEqual(special["college"], "机电工程学院")
        self.assertEqual(special["admission_major"], "机械制造及其自动化")
        self.assertIn("立功表彰退役军人免初试专项计划", special["remarks"])


if __name__ == "__main__":
    unittest.main()
