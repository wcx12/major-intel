import unittest
from pathlib import Path


class Batch302HebcmRecommendationCurationTests(unittest.TestCase):
    def test_curates_only_waiting_admission_recommendation_rows(self):
        from scripts.one_off.official_sources.curate_batch302_hebcm_recommendation import curate_records

        rows = curate_records(xls_path=Path("tmp/hebcm_reco_batch1.xls"))

        self.assertEqual(len(rows), 16)
        self.assertTrue(all(row["school_name"] == "河北中医药大学" for row in rows))
        self.assertTrue(all(row["year"] == 2026 for row in rows))
        self.assertTrue(
            all(row["document_type"] == "incoming_recommendation_admission_list" for row in rows)
        )
        self.assertTrue(all(row["route"] == "recommendation_exemption" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "李茎丹")
        self.assertEqual(first["college"], "中医学院")
        self.assertEqual(first["admission_major"], "中医医史文献")
        self.assertIn("admission_status: 待录取", first["remarks"])

        direct_doctor = next(row for row in rows if row["person_name"] == "郭丹丹")
        self.assertEqual(direct_doctor["admission_major"], "中西医结合基础")
        self.assertIn("待录取（直博生）", direct_doctor["remarks"])

        flattened = "\n".join(str(row) for row in rows)
        for bad_fragment in (
            "未参加复试",
            "放弃待录取通知",
            "拒绝待录取通知",
            "拒绝复试通知",
            "已被其他院校录取",
        ):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
