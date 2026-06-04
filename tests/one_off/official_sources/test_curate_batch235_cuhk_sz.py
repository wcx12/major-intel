import unittest
from pathlib import Path


class Batch235CuhkSzCurationTests(unittest.TestCase):
    def test_curate_batch235_rebuilds_cuhk_sz_sds_records(self):
        from scripts.one_off.official_sources.curate_batch235_cuhk_sz import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch235_cuhk_sz"
            )
        )

        self.assertEqual(len(rows), 38)
        self.assertEqual(sum(row["school_name"] == "香港中文大学（深圳）" for row in rows), 38)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 9)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 29)
        self.assertEqual(sum(row["document_type"] == "recommendation_exemption_list" for row in rows), 9)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 29)
        self.assertEqual(sum(row["college"] == "数据科学学院" for row in rows), 38)
        self.assertEqual(len({(row["source_url"], row["ranking"], row["person_name"]) for row in rows}), 38)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))
        self.assertFalse(any(row["source_url"].endswith("/article/2309") for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "Aaron")
        self.assertEqual(first["student_id"], "121040033")
        self.assertEqual(first["major"], "数据科学与大数据技术")
        self.assertEqual(first["admission_major"], "数据科学理学硕士项目")
        self.assertEqual(first["ranking"], "1")

        normalized = [row for row in rows if row["person_name"] == "蒋飞弘"][0]
        self.assertEqual(normalized["major"], "金融学")
        self.assertEqual(normalized["student_id"], "121090230")

        xlsx_rows = [row for row in rows if row["year"] == 2026]
        self.assertEqual(xlsx_rows[0]["person_name"], "张驰")
        self.assertEqual(xlsx_rows[0]["student_id"], "")
        self.assertEqual(xlsx_rows[0]["major"], "数据科学与大数据技术")
        self.assertEqual(xlsx_rows[0]["admission_major"], "人工智能与机器人理学硕士项目")
        self.assertIn("2026年秋季入学", xlsx_rows[0]["title"])
        self.assertEqual(xlsx_rows[-1]["person_name"], "姚天扬")
        self.assertEqual(xlsx_rows[-1]["ranking"], "29")
        self.assertEqual(xlsx_rows[-1]["admission_major"], "计算机科学理学硕士")


if __name__ == "__main__":
    unittest.main()
