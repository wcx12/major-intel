import unittest
from pathlib import Path


class Batch208BZhejiangShanghaiCurationTests(unittest.TestCase):
    def test_normalize_hznu_row_corrects_year_route_and_admission_major(self):
        from scripts.one_off.official_sources.curate_batch208b_zhejiang_shanghai_pages import normalize_hznu_row

        record = normalize_hznu_row(
            {
                "school_name": "杭州师范大学",
                "year": "2025",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name": "陈佳林",
                "major": "105116",
                "admission_major": "眼科学",
                "ranking": "1",
                "remarks": "全日制",
                "source_url": "https://lcyxy.hznu.edu.cn/upload/resources/file/2025/09/24/7899961.xls",
                "title": "杭州师范大学2026年临床医学专业学位硕士研究生招生拟录取名单公示（推免生）",
                "needs_review": "false",
            }
        )

        self.assertEqual(record["year"], 2026)
        self.assertEqual(record["document_type"], "incoming_recommendation_admission_list")
        self.assertEqual(record["route"], "recommendation_exemption")
        self.assertEqual(record["college"], "临床医学院（口腔医学院）")
        self.assertEqual(record["major"], "105116")
        self.assertEqual(record["admission_major"], "105116 眼科学")
        self.assertEqual(record["remarks"], "study_mode 全日制")
        self.assertFalse(record["needs_review"])

    def test_curate_records_keeps_two_hznu_people(self):
        from scripts.one_off.official_sources.curate_batch208b_zhejiang_shanghai_pages import curate_records

        rows = curate_records(
            records_csv=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch208b_zhejiang_shanghai_pages/records.csv"
            )
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual({row["school_name"] for row in rows}, {"杭州师范大学"})
        self.assertEqual({row["year"] for row in rows}, {2026})
        self.assertEqual({row["route"] for row in rows}, {"recommendation_exemption"})
        self.assertEqual({row["person_name"] for row in rows}, {"陈佳林", "徐州琳"})
        self.assertFalse(any(row["needs_review"] for row in rows))


if __name__ == "__main__":
    unittest.main()
