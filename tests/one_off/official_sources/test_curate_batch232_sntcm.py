import unittest
from pathlib import Path


class Batch232SntcmCurationTests(unittest.TestCase):
    def test_curate_batch232_rebuilds_sntcm_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch232_sntcm import curate_records

        rows = curate_records(
            raw_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch232_sntcm/"
                "img.sntcm.edu.cn/9e1e9668227c91d4.pdf"
            )
        )

        self.assertEqual(len(rows), 769)
        self.assertEqual(sum(row["school_name"] == "陕西中医药大学" for row in rows), 769)
        self.assertEqual(len({row["student_id"] for row in rows}), 769)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "李祥瑞")
        self.assertEqual(first["student_id"], "107166161400130")
        self.assertEqual(first["major"], "100501")
        self.assertEqual(first["ranking"], "001")
        self.assertIn("initial_score 329", first["remarks"])
        self.assertIn("composite_score 71.46", first["remarks"])

        soldier_plan = next(row for row in rows if row["student_id"] == "107166113103137")
        self.assertEqual(soldier_plan["person_name"], "龙涛")
        self.assertEqual(soldier_plan["ranking"], "120")
        self.assertIn("退役大学生士兵计划", soldier_plan["remarks"])

        grassroots_plan = next(row for row in rows if row["student_id"] == "107166165154539")
        self.assertEqual(grassroots_plan["person_name"], "吴驳")
        self.assertIn("三支一扶计划", grassroots_plan["remarks"])

        last = rows[-1]
        self.assertEqual(last["person_name"], "侯易洁")
        self.assertEqual(last["student_id"], "107166136013636")
        self.assertEqual(last["ranking"], "886")


if __name__ == "__main__":
    unittest.main()
