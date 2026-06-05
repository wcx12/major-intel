import unittest
from pathlib import Path


class Batch246LcuRecommendationCurationTests(unittest.TestCase):
    def test_curate_batch246_keeps_lcu_recommendation_records(self):
        from scripts.one_off.official_sources.curate_batch246_lcu_recommendation import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch246_lcu_recommendation/yz.lcu.edu.cn/794a8e58cfad1d8f.pdf"
            )
        )

        self.assertEqual(len(rows), 163)
        self.assertEqual(sum(row["school_name"] == "聊城大学" for row in rows), 163)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 163)
        self.assertEqual(sum(row["document_type"] == "recommendation_exemption_list" for row in rows), 163)
        self.assertEqual(sum(row["route"] == "recommendation_exemption" for row in rows), 163)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertNotIn("姓名", {row["person_name"] for row in rows})
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "杨思雨")
        self.assertEqual(first["college"], "商学院")
        self.assertEqual(first["major"], "020200")
        self.assertEqual(first["admission_major"], "应用经济学")
        self.assertIn("复试成绩: 89.8", first["remarks"])
        self.assertIn("非专项计划", first["remarks"])

        support_plan = next(row for row in rows if row["person_name"] == "李珞璇")
        self.assertEqual(support_plan["college"], "政治与公共管理学院")
        self.assertIn("支教团推免计划", support_plan["remarks"])

        rural_plan = next(row for row in rows if row["person_name"] == "刘家莹")
        self.assertIn("农村师资计划", rural_plan["remarks"])

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
        self.assertEqual(last["person_name"], "孙兆文")
        self.assertEqual(last["college"], "医学院")
        self.assertIn("复试成绩: 86.5", last["remarks"])
        self.assertEqual(last["source_url"], "https://yz.lcu.edu.cn/docs/20241018150049513144.pdf")


if __name__ == "__main__":
    unittest.main()
