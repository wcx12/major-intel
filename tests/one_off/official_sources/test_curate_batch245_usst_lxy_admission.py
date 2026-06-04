import unittest
from pathlib import Path


class Batch245UsstLxyAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch245_rebuilds_usst_lxy_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch245_usst_lxy_admission import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch245_usst_lxy_admission/lxy.usst.edu.cn/dc2af7cc9b8d5d67.pdf"
            )
        )

        self.assertEqual(len(rows), 33)
        self.assertEqual(sum(row["school_name"] == "上海理工大学" for row in rows), 33)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 33)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 33)
        self.assertEqual(sum(row["college"] == "理学院" for row in rows), 33)
        self.assertEqual(sum(row["admission_major"] == "物理学" for row in rows), 33)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"].isdigit() for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "杜泽雨")
        self.assertEqual(first["student_id"], "102526210000006")
        self.assertIn("初试成绩: 309.0", first["remarks"])
        self.assertIn("复试成绩: 75.8", first["remarks"])
        self.assertIn("总成绩: 68.1", first["remarks"])

        soldier_plan = rows[5]
        self.assertEqual(soldier_plan["person_name"], "曹鑫培")
        self.assertEqual(soldier_plan["student_id"], "102526210000834")
        self.assertIn("退役大学生士兵专项计划", soldier_plan["remarks"])

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

        last = rows[-1]
        self.assertEqual(last["person_name"], "周翔")
        self.assertEqual(last["student_id"], "102526210008547")


if __name__ == "__main__":
    unittest.main()
