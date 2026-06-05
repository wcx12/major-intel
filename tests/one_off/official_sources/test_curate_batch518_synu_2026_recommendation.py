import unittest


class Batch518SynuRecommendationTests(unittest.TestCase):
    def test_pdf_positive_row_extracts_name_without_identity_number(self):
        from scripts.one_off.official_sources.curate_batch518_synu_2026_recommendation import curate_rows

        rows = curate_rows(
            [
                {
                    "school_name": "沈阳师范大学",
                    "year": "2026",
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": "211121200403111826 王艺霖 女",
                    "student_id": "22011108",
                    "college": "015",
                    "major": "化学化工学院",
                    "admission_major": "070301",
                    "ranking": "正选",
                    "remarks": "",
                    "source_url": "https://hxhg.synu.edu.cn/example.pdf",
                    "title": "化学化工学院2026年推免情况汇总表",
                    "needs_review": "false",
                }
            ]
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["person_name"], "王艺霖")
        self.assertEqual(rows[0]["student_id"], "22011108")
        self.assertEqual(rows[0]["college"], "化学化工学院")
        self.assertEqual(rows[0]["admission_major"], "070301")
        self.assertIn("selection_status 正选", rows[0]["remarks"])
        self.assertNotIn("211121200403111826", " ".join(str(value) for value in rows[0].values()))

    def test_pdf_header_and_substitute_rows_are_skipped(self):
        from scripts.one_off.official_sources.curate_batch518_synu_2026_recommendation import curate_rows

        rows = curate_rows(
            [
                {
                    "school_name": "沈阳师范大学",
                    "person_name": "",
                    "student_id": "",
                    "college": "替补） （院系/",
                    "major": "成绩",
                    "admission_major": "名次",
                    "ranking": "",
                    "source_url": "https://hxhg.synu.edu.cn/example.pdf",
                },
                {
                    "school_name": "沈阳师范大学",
                    "person_name": "211121200403111826 王艺霖 女",
                    "student_id": "22011108",
                    "college": "015",
                    "major": "化学化工学院",
                    "admission_major": "070301",
                    "ranking": "替补",
                    "source_url": "https://hxhg.synu.edu.cn/example.pdf",
                },
            ]
        )

        self.assertEqual(rows, [])

    def test_wxy_html_rows_keep_plain_names_and_add_college(self):
        from scripts.one_off.official_sources.curate_batch518_synu_2026_recommendation import curate_rows

        rows = curate_rows(
            [
                {
                    "school_name": "沈阳师范大学",
                    "year": "2026",
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": "高阳",
                    "major": "秘书",
                    "source_url": "https://wxy.synu.edu.cn/2025/0914/c2696a106945/page.htm",
                    "title": "关于文学院2026年推荐优秀应届本科毕业生免试攻读研究生名单的公示",
                }
            ]
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["person_name"], "高阳")
        self.assertEqual(rows[0]["college"], "文学院")
        self.assertEqual(rows[0]["major"], "秘书")


if __name__ == "__main__":
    unittest.main()
