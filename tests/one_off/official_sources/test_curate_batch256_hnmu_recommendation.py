import importlib.util
import unittest
from pathlib import Path


class Batch256HnmuRecommendationCurationTests(unittest.TestCase):
    def test_curate_batch256_keeps_hnmu_recommendation_table_fields(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch256_hnmu_recommendation")
        self.assertIsNotNone(spec, "batch256 curation module should exist")

        from scripts.one_off.official_sources.curate_batch256_hnmu_recommendation import curate_records

        rows = curate_records(
            html_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch256_hnmu_recommendation/"
                "www.xxmu.edu.cn/084916d104b22a9e.htm"
            )
        )

        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(row["school_name"] == "河南医药大学" for row in rows), 4)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 4)
        self.assertEqual(sum(row["document_type"] == "recommendation_exemption_list" for row in rows), 4)
        self.assertEqual(sum(row["route"] == "recommendation_exemption" for row in rows), 4)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "宋克强")
        self.assertEqual(first["student_id"], "410326********7537")
        self.assertEqual(first["college"], "药学学部")
        self.assertEqual(first["major"], "药学")
        self.assertEqual(first["admission_major"], "105500 药学")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("院系所代码: 015", first["remarks"])
        self.assertIn("学位类型: 专业学位", first["remarks"])

        second = rows[1]
        self.assertEqual(second["person_name"], "张圣洋")
        self.assertEqual(second["college"], "河南医药大学第一临床学院")
        self.assertEqual(second["admission_major"], "105100 临床医学")

        last = rows[-1]
        self.assertEqual(last["person_name"], "刘松叶")
        self.assertEqual(last["student_id"], "411322********4943")
        self.assertEqual(last["college"], "河南医药大学第三临床学院")
        self.assertEqual(last["admission_major"], "100200 临床医学")
        self.assertIn("学位类型: 学术学位", last["remarks"])

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
