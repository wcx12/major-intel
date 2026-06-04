import unittest


class Batch519GdpuRecommendationTests(unittest.TestCase):
    def test_curate_rows_keeps_only_formal_recommendation_prefix(self):
        from scripts.one_off.official_sources.curate_batch519_gdpu_2026_recommendation import curate_rows

        records = [
            {
                "school_name": "广东药科大学",
                "year": "2026",
                "document_type": "recommendation_exemption_list",
                "route": "recommendation_exemption",
                "person_name": f"正式{i}",
                "major": "临床医学",
                "source_url": "https://www.gy120.net/m/newsshow.asp?articleid=8312",
                "title": "广东药科大学第一临床医学院推荐2026届优秀本科毕业生免试攻读硕士学位研究生名单公示",
            }
            for i in range(12)
        ]
        records.append(
            {
                "school_name": "广东药科大学",
                "year": "2026",
                "document_type": "recommendation_exemption_list",
                "route": "recommendation_exemption",
                "person_name": "递补0",
                "major": "临床医学",
                "source_url": "https://www.gy120.net/m/newsshow.asp?articleid=8312",
                "title": "广东药科大学第一临床医学院推荐2026届优秀本科毕业生免试攻读硕士学位研究生名单公示",
            }
        )

        rows = curate_rows(records)

        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[-1]["person_name"], "正式11")
        self.assertEqual(rows[0]["college"], "第一临床医学院")
        self.assertEqual(rows[0]["remarks"], "recommendation_status 正式推荐")
        self.assertNotIn("递补0", [row["person_name"] for row in rows])


if __name__ == "__main__":
    unittest.main()
