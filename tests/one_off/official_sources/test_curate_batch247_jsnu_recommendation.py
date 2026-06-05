import unittest
from pathlib import Path


class Batch247JsnuRecommendationCurationTests(unittest.TestCase):
    def test_curate_batch247_keeps_jsnu_recommendation_records(self):
        from scripts.one_off.official_sources.curate_batch247_jsnu_recommendation import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch247_jsnu_recommendation/yjsy.jsnu.edu.cn/ad453d0fffcc59fc.pdf"
            )
        )

        self.assertEqual(len(rows), 113)
        self.assertEqual(sum(row["school_name"] == "江苏师范大学" for row in rows), 113)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 113)
        self.assertEqual(sum(row["document_type"] == "recommendation_exemption_list" for row in rows), 113)
        self.assertEqual(sum(row["route"] == "recommendation_exemption" for row in rows), 113)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "张彭菲")
        self.assertEqual(first["student_id"], "3203**********5527")
        self.assertEqual(first["college"], "公共管理与社会学院")
        self.assertEqual(first["major"], "120401")
        self.assertEqual(first["admission_major"], "行政管理")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("拟录取学院代码: 001", first["remarks"])
        self.assertIn("推免类型: 普通计划", first["remarks"])

        wrapped_college = next(row for row in rows if row["person_name"] == "陈亘烨")
        self.assertEqual(wrapped_college["college"], "智慧教育学院（计算机科学与技术学院）")
        self.assertEqual(wrapped_college["major"], "045114")
        self.assertEqual(wrapped_college["admission_major"], "现代教育技术")
        self.assertIn("推免类型: 农村学校教育硕士师资培养计划", wrapped_college["remarks"])

        support_plan = next(row for row in rows if row["person_name"] == "陈佳濠")
        self.assertEqual(support_plan["admission_major"], "金融")
        self.assertIn("推免类型: 研究生支教团", support_plan["remarks"])

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
        self.assertEqual(last["person_name"], "郝雨甜")
        self.assertEqual(last["student_id"], "3203**********3049")
        self.assertEqual(last["college"], "美术学院")
        self.assertEqual(last["major"], "140300")
        self.assertEqual(last["admission_major"], "设计学")
        self.assertEqual(
            last["source_url"],
            "http://yjsy.jsnu.edu.cn/_upload/article/files/ca/08/ec9ecd2d4c2daa9bb3a54722897c/0baf68fa-b026-4a15-a7e3-2b00b68a4728.pdf",
        )


if __name__ == "__main__":
    unittest.main()
