import unittest
from pathlib import Path


class Batch241XidianMathAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch241_rebuilds_xidian_math_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch241_xidian_math_admission import curate_records

        rows = curate_records(
            records_csv=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch241_xidian_math_admission/records.csv"
            )
        )

        self.assertEqual(len(rows), 62)
        self.assertEqual(sum(row["school_name"] == "西安电子科技大学" for row in rows), 62)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 62)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 62)
        self.assertEqual(sum(row["college"] == "数学与统计学院" for row in rows), 62)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
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
        self.assertEqual(first["person_name"], "贺小钟")
        self.assertEqual(first["student_id"], "107015515914372")
        self.assertEqual(first["admission_major"], "数学")

        self.assertEqual(rows[-1]["person_name"], "李阳")
        self.assertEqual(rows[-1]["admission_major"], "数学")


if __name__ == "__main__":
    unittest.main()
