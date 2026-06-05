import unittest
from pathlib import Path


class Batch240SwpuAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch240_rebuilds_swpu_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch240_swpu_admission_pdfs import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch240_swpu_admission_pdfs"
            )
        )

        self.assertEqual(len(rows), 25)
        self.assertEqual(sum(row["school_name"] == "西南石油大学" for row in rows), 25)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 25)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 25)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        petro = [row for row in rows if row["college"] == "石油与天然气工程学院"]
        civil = [row for row in rows if row["college"] == "土木工程与测绘学院"]
        self.assertEqual(len(petro), 4)
        self.assertEqual(len(civil), 21)

        first = petro[0]
        self.assertEqual(first["person_name"], "辜新航")
        self.assertEqual(first["student_id"], "1061550820****2")
        self.assertEqual(first["admission_major"], "082000-油气储运工程")
        self.assertEqual(first["ranking"], "450")
        self.assertIn("initial_score 283", first["remarks"])
        self.assertIn("reexam_score 74.51", first["remarks"])
        self.assertIn("total_score 65.56", first["remarks"])

        civil_first = civil[0]
        self.assertEqual(civil_first["person_name"], "喻岭")
        self.assertEqual(civil_first["student_id"], "1021350000****7")
        self.assertEqual(civil_first["admission_major"], "081400 土木工程")
        self.assertEqual(civil_first["ranking"], "1")
        self.assertIn("study_mode 全日制", civil_first["remarks"])

        self.assertEqual(civil[-1]["person_name"], "彭豪")
        self.assertEqual(civil[-1]["admission_major"], "081600 测绘科学与技术")


if __name__ == "__main__":
    unittest.main()
