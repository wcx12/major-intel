import unittest
from pathlib import Path


class Batch223MucDoctoralAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch223_reads_legacy_xls_bins_and_xlsx_attachments(self):
        from scripts.one_off.official_sources.curate_batch223_muc_doctoral_admission import curate_records

        rows = curate_records(
            documents_jsonl=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch223_muc_doctoral_admission/"
                "documents.jsonl"
            )
        )

        self.assertEqual(len(rows), 540)
        self.assertEqual(sum(row["school_name"] == "中央民族大学" for row in rows), 540)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))

        xls_row = next(row for row in rows if row["student_id"] == "B20261193")
        self.assertEqual(xls_row["person_name"], "王涵")
        self.assertEqual(xls_row["college"], "民族学与社会学学院")
        self.assertEqual(xls_row["admission_major"], "马克思主义民族理论与政策")
        self.assertIn("research_direction 不区分研究方向", xls_row["remarks"])
        self.assertIn("special_plan 无专项计划", xls_row["remarks"])
        self.assertIn("admission_category 非定向", xls_row["remarks"])
        self.assertIn("admission_status 录取", xls_row["remarks"])

        xlsx_row = next(row for row in rows if row["student_id"] == "B20262693")
        self.assertEqual(xlsx_row["person_name"], "丁俊文")
        self.assertEqual(xlsx_row["college"], "美术学院")
        self.assertEqual(xlsx_row["admission_major"], "美术与书法")

        flattened = "\n".join(str(row) for row in rows)
        for bad_fragment in (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
        ):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
