import unittest
from pathlib import Path


class Batch209RemainingPromisingPagesCurationTests(unittest.TestCase):
    def test_parse_hlju_record_handles_wrapped_long_name(self):
        from scripts.one_off.official_sources.curate_batch209_remaining_promising_pages import parse_hlju_record

        record = parse_hlju_record(
            "2260027 艾则提约麦尔·麦麦提图尔荪 102126102120027 003.法学院 "
            "030100.法学 00.不区分研究方向 全日制 免试 88.7 88.7 非定向 推免生"
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["school_name"], "黑龙江大学")
        self.assertEqual(record["person_name"], "艾则提约麦尔·麦麦提图尔荪")
        self.assertEqual(record["student_id"], "102126102120027")
        self.assertEqual(record["college"], "003.法学院")
        self.assertEqual(record["major"], "030100.法学")
        self.assertEqual(record["admission_major"], "030100.法学 00.不区分研究方向")
        self.assertIn("school_record_no 2260027", record["remarks"])
        self.assertIn("final_score 88.7", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_parse_cqnu_regular_and_support_rows(self):
        from scripts.one_off.official_sources.curate_batch209_remaining_promising_pages import parse_cqnu_ranked_line, parse_cqnu_support_line

        regular = parse_cqnu_ranked_line("1 马克思主义学院 思想政治教育 罗欣悦 1", category="普通类")
        support = parse_cqnu_support_line("历史与社会学院 历史学（师范） 崔靖宇 1")

        self.assertIsNotNone(regular)
        self.assertEqual(regular["school_name"], "重庆师范大学")
        self.assertEqual(regular["person_name"], "罗欣悦")
        self.assertEqual(regular["college"], "马克思主义学院")
        self.assertEqual(regular["major"], "思想政治教育")
        self.assertEqual(regular["ranking"], "1")
        self.assertIn("category 普通类", regular["remarks"])
        self.assertIsNotNone(support)
        self.assertEqual(support["person_name"], "崔靖宇")
        self.assertIn("category 研究生支教团", support["remarks"])

    def test_curate_records_reparses_clean_sources_and_drops_noise(self):
        from scripts.one_off.official_sources.curate_batch209_remaining_promising_pages import curate_records

        rows = curate_records(
            hlj_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages/yjsy.hlju.edu.cn/461b15ecfd01f1ec.pdf"
            ),
            cqnu_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages/jwc.cqnu.edu.cn/8c281b25ccf76a48.pdf"
            ),
            wtu_html=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages/fashion.wtu.edu.cn/d647428c0b6553a1.htm"
            ),
            whsu_html=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages/jtxy.whsu.edu.cn/56217fa14bad29d6.htm"
            ),
        )

        counts = {}
        for row in rows:
            counts[row["school_name"]] = counts.get(row["school_name"], 0) + 1

        self.assertEqual(
            counts,
            {"重庆师范大学": 313, "武汉体育学院": 8, "武汉纺织大学": 7, "黑龙江大学": 219},
        )
        self.assertEqual(len(rows), 547)
        self.assertFalse(any(row["person_name"] in {"免试", "赛事名称"} for row in rows))
        self.assertFalse(any("候补" in row["remarks"] for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))


if __name__ == "__main__":
    unittest.main()
