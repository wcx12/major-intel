import unittest
from pathlib import Path


class Batch206ArtMusicCurationTests(unittest.TestCase):
    def test_parse_lumei_row_keeps_major_direction_and_scores(self):
        from scripts.one_off.official_sources.curate_batch206_art_music_sources import parse_lumei_row

        record = parse_lumei_row(
            ("1", "徐英奇", "101786000100013", "美术史论研究", "396", "81.33", "79.84", "全日制", "非定向就业", None),
            current_major="艺术学（130100）",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "徐英奇")
        self.assertEqual(record["student_id"], "101786000100013")
        self.assertEqual(record["major"], "艺术学（130100）")
        self.assertEqual(record["admission_major"], "美术史论研究")
        self.assertEqual(record["ranking"], "1")
        self.assertIn("initial_score 396", record["remarks"])
        self.assertIn("admission_category 非定向就业", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_parse_caa_cells_moves_scores_out_of_major(self):
        from scripts.one_off.official_sources.curate_batch206_art_music_sources import parse_caa_cells

        record = parse_caa_cells(
            ["博士", "103552026006003", "许莺", "手工艺术学院", "设计", "手工艺术创作", "83", "88", "84.33", "172.33", "70.75", "澳门"]
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "许莺")
        self.assertEqual(record["student_id"], "103552026006003")
        self.assertEqual(record["college"], "手工艺术学院")
        self.assertEqual(record["major"], "设计")
        self.assertEqual(record["admission_major"], "设计 手工艺术创作")
        self.assertIn("application_type 博士", record["remarks"])
        self.assertIn("composite_score 70.75", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_parse_sccm_chunks_reuses_college_for_wrapped_rows(self):
        from scripts.one_off.official_sources.curate_batch206_art_music_sources import records_from_sccm_lines

        rows = records_from_sccm_lines(
            [
                "1",
                "管弦系",
                "谢佳宇 20220410060 女 音乐表演（小提琴演奏）",
                "92",
                "89.6 62.72 10 3 65.72 1 合格 无",
                "2 张逢瑜 20220410085 女 音乐表演（中提琴演奏） 88.68 62.08 10 3 65.08 2 合格 无",
            ]
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["college"], "管弦系")
        self.assertEqual(rows[0]["person_name"], "谢佳宇")
        self.assertEqual(rows[0]["major"], "音乐表演（小提琴演奏）")
        self.assertEqual(rows[1]["college"], "管弦系")
        self.assertEqual(rows[1]["person_name"], "张逢瑜")
        self.assertEqual(rows[1]["ranking"], "2")

    def test_curate_records_reparses_batch206_sources(self):
        from scripts.one_off.official_sources.curate_batch206_art_music_sources import curate_records

        rows = curate_records(
            lumei_xlsx=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch206_art_music_sources/www.lumei.edu.cn/79cd0fb1f2abecdf.xlsx"
            ),
            caa_html=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch206_art_music_sources/zb.caa.edu.cn/8e90fca12f1f8882.htm"
            ),
            sccm_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch206_art_music_sources/www.sccm.edu.cn/83e73544fc2f63fb.pdf"
            ),
            jmu_xlsx=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch206_art_music_sources/arts.jmu.edu.cn/617dc24c4d992173.xlsx"
            ),
        )

        counts = {}
        for row in rows:
            counts[row["school_name"]] = counts.get(row["school_name"], 0) + 1

        self.assertEqual(
            counts,
            {
                "鲁迅美术学院": 361,
                "中国美术学院": 9,
                "四川音乐学院": 52,
                "集美大学": 11,
            },
        )
        self.assertEqual(len(rows), 433)
        self.assertFalse(any(row["person_name"] in {"特此公示", "川美招生", "计30%"} for row in rows))
        self.assertFalse(any("备选" in row["remarks"] for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))


if __name__ == "__main__":
    unittest.main()
