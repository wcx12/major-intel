import unittest
from pathlib import Path


class Batch231SxnuDoctorCurationTests(unittest.TestCase):
    def test_curate_batch231_rebuilds_sxnu_doctor_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch231_sxnu_doctor import curate_records

        rows = curate_records(
            raw_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch231_sxnu_doctor/"
                "grc.sxnu.edu.cn/93e5100ec3f18af1.pdf"
            )
        )

        self.assertEqual(len(rows), 82)
        self.assertEqual(sum(row["school_name"] == "山西师范大学" for row in rows), 82)
        self.assertEqual(len({row["student_id"] for row in rows}), 82)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))
        self.assertNotIn("业务二", {row["person_name"] for row in rows})

        first = rows[0]
        self.assertEqual(first["person_name"], "邓林霜")
        self.assertEqual(first["student_id"], "101186100211002")
        self.assertEqual(first["major"], "130100")
        self.assertEqual(first["admission_major"], "艺术学")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("degree 博士", first["remarks"])
        self.assertIn("weighted_score 88.80", first["remarks"])

        spaced_name = next(row for row in rows if row["student_id"] == "101186101811028")
        self.assertEqual(spaced_name["person_name"], "李霞")
        self.assertEqual(spaced_name["admission_major"], "马克思主义理论")

        last = rows[-1]
        self.assertEqual(last["person_name"], "任艳裂")
        self.assertEqual(last["student_id"], "101186101811039")
        self.assertEqual(last["ranking"], "82")


if __name__ == "__main__":
    unittest.main()
