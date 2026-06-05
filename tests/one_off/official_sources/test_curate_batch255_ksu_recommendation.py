import importlib.util
import unittest
from pathlib import Path


class Batch255KsuRecommendationCurationTests(unittest.TestCase):
    def test_curate_batch255_parses_ksu_scanned_recommendation_pdf(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch255_ksu_recommendation")
        self.assertIsNotNone(spec, "batch255 curation module should exist")

        from scripts.one_off.official_sources.curate_batch255_ksu_recommendation import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch255_ksu_recommendation/"
                "yjsc.ksu.edu.cn/9c7cd0d132eb3846.pdf"
            )
        )

        self.assertEqual(len(rows), 60)
        self.assertEqual(sum(row["school_name"] == "喀什大学" for row in rows), 60)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 60)
        self.assertEqual(sum(row["document_type"] == "recommendation_exemption_list" for row in rows), 60)
        self.assertEqual(sum(row["route"] == "recommendation_exemption" for row in rows), 60)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "张梦馨")
        self.assertEqual(first["student_id"], "622826********1949")
        self.assertEqual(first["college"], "人文学院")
        self.assertEqual(first["major"], "中国少数民族语言文学")
        self.assertEqual(first["admission_major"], "050107 中国少数民族语言文学")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("专项计划", first["remarks"])

        special_plan_last = rows[37]
        self.assertEqual(special_plan_last["person_name"], "刘志雨")
        self.assertEqual(special_plan_last["student_id"], "370883********682X")
        self.assertEqual(special_plan_last["ranking"], "38")
        self.assertIn("专项计划", special_plan_last["remarks"])

        normal_first = rows[38]
        self.assertEqual(normal_first["person_name"], "杨昌钱")
        self.assertEqual(normal_first["college"], "计算机科学与技术学院")
        self.assertEqual(normal_first["admission_major"], "085410 人工智能")
        self.assertEqual(normal_first["ranking"], "39")
        self.assertNotIn("专项计划", normal_first["remarks"])

        corrected_name = next(row for row in rows if row["ranking"] == "46")
        self.assertEqual(corrected_name["person_name"], "姜宁")
        self.assertEqual(corrected_name["admission_major"], "035102 法律（法学）")

        long_name = next(row for row in rows if row["ranking"] == "55")
        self.assertEqual(long_name["person_name"], "穆开代斯·赛买提")
        self.assertEqual(long_name["admission_major"], "045103 学科教学（语文）")

        last = rows[-1]
        self.assertEqual(last["person_name"], "刘荞真")
        self.assertEqual(last["student_id"], "411123********014X")
        self.assertEqual(last["college"], "化学与环境科学学院")
        self.assertEqual(last["major"], "分析化学")
        self.assertEqual(last["admission_major"], "070302 分析化学")
        self.assertEqual(last["ranking"], "60")
        self.assertTrue(last["source_url"].startswith("https://yjsc.ksu.edu.cn/virtual_attach_file.vsb?"))

        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        hard_exclude_terms = (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
            "不合格",
            "名额受限",
            "放弃一志愿录取资格",
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))


if __name__ == "__main__":
    unittest.main()
