import unittest
from pathlib import Path


class Batch239WhpuAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch239_rebuilds_whpu_admission_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch239_whpu_admission import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch239_whpu_admission"
            )
        )

        self.assertEqual(len(rows), 1293)
        self.assertEqual(sum(row["school_name"] == "武汉轻工大学" for row in rows), 1293)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 1293)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 1293)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "艾春艳")
        self.assertEqual(first["student_id"], "103075211505634")
        self.assertEqual(first["college"], "外国语学院")
        self.assertEqual(first["major"], "055101")
        self.assertEqual(first["admission_major"], "英语笔译")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("initial_score 383", first["remarks"])
        self.assertIn("reexam_score 205.6", first["remarks"])
        self.assertIn("total_score 73.37", first["remarks"])

        soldier_plan = [row for row in rows if row["person_name"] == "常江涛"][0]
        self.assertEqual(soldier_plan["admission_major"], "土木水利")
        self.assertIn("退役大学生士兵计划", soldier_plan["remarks"])

        self.assertEqual(rows[-1]["person_name"], "邹云飞")
        self.assertEqual(rows[-1]["admission_major"], "农业管理")


if __name__ == "__main__":
    unittest.main()
