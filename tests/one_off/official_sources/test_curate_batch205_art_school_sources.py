import unittest
from pathlib import Path


class Batch205ArtSchoolCurationTests(unittest.TestCase):
    def test_parse_cafa_recommendation_line_maps_departments_and_direction(self):
        from scripts.one_off.official_sources.curate_batch205_art_school_sources import parse_cafa_recommendation_line

        record = parse_cafa_recommendation_line(
            "1 袁艺萌 中国画学院 中国画学院 02水墨人物画研究",
            source_url="https://example.edu/cafa_tm.pdf",
            title="中央美术学院2026年接收推荐免试攻读硕士学位研究生拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "袁艺萌")
        self.assertEqual(record["undergraduate_school"], "中国画学院")
        self.assertEqual(record["college"], "中国画学院")
        self.assertEqual(record["admission_major"], "02水墨人物画研究")
        self.assertFalse(record["needs_review"])

    def test_parse_cafa_master_line_keeps_candidate_id_and_remark(self):
        from scripts.one_off.official_sources.curate_batch205_art_school_sources import parse_cafa_master_line

        record = parse_cafa_master_line(
            "艾尔盼·爱尔肯 100476010042024 南疆计划",
            source_url="https://example.edu/cafa_master.pdf",
            title="中央美术学院2026年硕士研究生招生考试拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "艾尔盼·爱尔肯")
        self.assertEqual(record["student_id"], "100476010042024")
        self.assertEqual(record["remarks"], "南疆计划")
        self.assertFalse(record["needs_review"])

    def test_parse_xafa_row_preserves_direction_scores_and_recommendation_type(self):
        from scripts.one_off.official_sources.curate_batch205_art_school_sources import parse_xafa_cells

        record = parse_xafa_cells(
            ["秦云鹤", "艺术人文学院", "艺术学", "艺术管理与美育研究", "81.19", "86.5", "83.85", "研究生支教团 - 全日制学术学位"],
            source_url="https://example.edu/xafa.htm",
            title="西安美术学院2026年优秀应届本科毕业生免试攻读硕士学位研究生拟录取名单公示",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "秦云鹤")
        self.assertEqual(record["college"], "艺术人文学院")
        self.assertEqual(record["major"], "艺术学")
        self.assertEqual(record["admission_major"], "艺术学 艺术管理与美育研究")
        self.assertIn("recommendation_score 81.19", record["remarks"])
        self.assertIn("final_score 83.85", record["remarks"])
        self.assertIn("研究生支教团 - 全日制学术学位", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_curate_records_reparses_all_art_school_sources(self):
        from scripts.one_off.official_sources.curate_batch205_art_school_sources import curate_records

        rows = curate_records(
            cafa_recommendation_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources/www.cafa.edu.cn/c4f2340b429dfb98.pdf"
            ),
            cafa_master_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources/www.cafa.edu.cn/430b61e6cffc3b1c.pdf"
            ),
            xafa_html=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources/zhshch.xafa.edu.cn/9c4d79113c45a308.htm"
            ),
        )

        counts = {}
        for row in rows:
            key = (row["school_name"], row["document_type"])
            counts[key] = counts.get(key, 0) + 1

        self.assertEqual(
            counts,
            {
                ("中央美术学院", "recommendation_exemption_list"): 205,
                ("中央美术学院", "postgraduate_admission_list"): 488,
                ("西安美术学院", "incoming_recommendation_admission_list"): 83,
            },
        )
        self.assertEqual(len(rows), 776)
        self.assertFalse(any(row["person_name"] == "姓名" for row in rows))
        self.assertFalse(any(row["person_name"] == "序号" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))


if __name__ == "__main__":
    unittest.main()
