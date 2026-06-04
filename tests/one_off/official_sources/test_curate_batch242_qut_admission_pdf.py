import unittest
from pathlib import Path


class Batch242QutAdmissionPdfCurationTests(unittest.TestCase):
    def test_curate_batch242_rebuilds_qut_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch242_qut_admission_pdf import curate_records

        rows = curate_records(
            records_csv=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch242_qut_admission_pdf/records.csv"
            )
        )

        self.assertEqual(len(rows), 1509)
        self.assertEqual(sum(row["school_name"] == "青岛理工大学" for row in rows), 1509)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 1509)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 1509)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        hard_exclude_terms = (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
        )
        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))

        first = rows[0]
        self.assertEqual(first["person_name"], "宋*")
        self.assertEqual(first["student_id"], "102875210110440")
        self.assertEqual(first["college"], "001土木工程学院")
        self.assertEqual(first["admission_major"], "080100|力学")

        self.assertEqual(rows[-1]["person_name"], "戴*欣")
        self.assertEqual(rows[-1]["college"], "011马克思主义学院")
        self.assertEqual(rows[-1]["admission_major"], "030500|马克思主义理论")


if __name__ == "__main__":
    unittest.main()
