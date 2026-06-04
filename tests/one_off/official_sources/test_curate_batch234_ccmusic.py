import unittest
from pathlib import Path


class Batch234CcmusicCurationTests(unittest.TestCase):
    def test_curate_batch234_rebuilds_ccmusic_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch234_ccmusic import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch234_ccmusic"
            )
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(sum(row["school_name"] == "中国音乐学院" for row in rows), 2)
        self.assertEqual(len({row["student_id"] for row in rows}), 2)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(row["person_name"] == "研究生院" for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "林威仪")
        self.assertEqual(first["student_id"], "100462026205001")
        self.assertEqual(first["college"], "国乐系")
        self.assertEqual(first["admission_major"], "音乐（筝演奏）")
        self.assertIn("degree_level 硕士", first["remarks"])
        self.assertIn("total_score 81.02", first["remarks"])
        self.assertIn("admission_category 非定向", first["remarks"])

        second = rows[1]
        self.assertEqual(second["person_name"], "蔡东篱")
        self.assertEqual(second["student_id"], "100462026101001")
        self.assertEqual(second["college"], "音乐学系")
        self.assertEqual(second["admission_major"], "艺术学（音乐学）")
        self.assertIn("degree_level 博士", second["remarks"])
        self.assertIn("课题类型：一般课题", second["remarks"])


if __name__ == "__main__":
    unittest.main()
