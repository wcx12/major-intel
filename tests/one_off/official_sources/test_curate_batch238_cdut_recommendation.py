import unittest
from pathlib import Path


class Batch238CdutRecommendationCurationTests(unittest.TestCase):
    def test_curate_batch238_rebuilds_cdut_recommendation_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch238_cdut_recommendation import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch238_cdut_recommendation"
            )
        )

        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["school_name"] == "成都理工大学" for row in rows), 6)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 6)
        self.assertEqual(sum(row["document_type"] == "recommendation_exemption_list" for row in rows), 6)
        self.assertEqual(sum(row["route"] == "recommendation_exemption" for row in rows), 6)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))
        self.assertFalse(any(row["person_name"] in {"研究生", "支教团"} for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "余宏鑫")
        self.assertEqual(first["college"], "计算机与网络安全学院（示范性软件学院）")
        self.assertEqual(first["admission_major"], "081200 计算机科学与技术")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("reexam_score 88", first["remarks"])
        self.assertIn("degree_category 硕士", first["remarks"])
        self.assertIn("研究生支教团", first["remarks"])

        self.assertEqual(rows[-1]["person_name"], "宇琪琪")
        self.assertEqual(rows[-1]["ranking"], "6")
        self.assertIn("reexam_score 76.6", rows[-1]["remarks"])


if __name__ == "__main__":
    unittest.main()
