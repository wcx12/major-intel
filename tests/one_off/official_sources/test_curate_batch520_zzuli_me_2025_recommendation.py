import unittest


class Batch520ZzuliMeRecommendationTests(unittest.TestCase):
    def test_extract_approved_rows_keeps_only_agreed_recommendations(self):
        from scripts.one_off.official_sources.curate_batch520_zzuli_me_2025_recommendation import (
            extract_approved_rows_from_text,
        )

        text = """
一、申请推免名单公示
       542202010718 王佳音    1    85.61   89.8   6    6         同意推免
       542202010720 吴俊豪    11   79.62   83.6   4    4
车辆工程
       542202080119 孙雪婷    1    83.435 87.3    10   10        同意推免
二、科研成果、竞赛获奖公示
542202010718 王佳音                                             8
"""

        rows = extract_approved_rows_from_text(
            text,
            source_url="https://me.zzuli.edu.cn/example.pdf",
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual([row["person_name"] for row in rows], ["王佳音", "孙雪婷"])
        self.assertEqual(rows[0]["major"], "机械设计制造及其自动化")
        self.assertEqual(rows[1]["major"], "车辆工程")
        self.assertEqual(rows[0]["ranking"], "1")
        self.assertIn("recommendation_status 同意推免", rows[0]["remarks"])
        self.assertNotIn("吴俊豪", [row["person_name"] for row in rows])


if __name__ == "__main__":
    unittest.main()
