import unittest
from pathlib import Path


class Batch216XatuRecommendationCurationTests(unittest.TestCase):
    def test_curate_xatu_html_table_keeps_full_recommendation_fields(self):
        from scripts.one_off.official_sources.curate_batch216_xatu_recommendation import curate_xatu_html

        rows = curate_xatu_html(
            Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch216_xatu_recommendation/"
                "grs.xatu.edu.cn/c0f20c9791623b5a.htm"
            )
        )

        self.assertEqual(len(rows), 230)
        self.assertEqual({row["school_name"] for row in rows}, {"西安工业大学"})
        self.assertEqual({str(row["year"]) for row in rows}, {"2026"})
        self.assertEqual({row["document_type"] for row in rows}, {"recommendation_exemption_list"})
        self.assertEqual({row["route"] for row in rows}, {"recommendation_exemption"})
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["student_id"], "2022030082")
        self.assertEqual(first["person_name"], "宗璟熠")
        self.assertEqual(first["college"], "光电工程学院")
        self.assertEqual(first["undergraduate_major"], "080301 测控技术与仪器")
        self.assertEqual(first["major"], "测控技术与仪器")
        self.assertIn("undergraduate_major_code 080301", first["remarks"])
        self.assertIn("recommendation_status 拟推荐", first["remarks"])

        last = rows[-1]
        self.assertEqual(last["ranking"], "230")
        self.assertEqual(last["person_name"], "罗颖超")
        self.assertEqual(last["college"], "兵器科学与技术学院")

        flattened = "\n".join(str(row) for row in rows)
        self.assertNotIn("候补", flattened)
        self.assertNotIn("复试不合格", flattened)


if __name__ == "__main__":
    unittest.main()
