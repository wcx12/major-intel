import unittest
from pathlib import Path


class Batch210RemainingPromisingPagesCurationTests(unittest.TestCase):
    def test_curate_gznu_keeps_only_sheet1_proposed_recommendations(self):
        from scripts.one_off.official_sources.curate_batch210_remaining_promising_pages import curate_gznu_workbook

        rows = curate_gznu_workbook(
            Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch210_remaining_promising_pages/"
                "jwc.gznu.edu.cn/9f0c97d758546d21.xlsx"
            )
        )

        self.assertEqual(len(rows), 209)
        self.assertEqual({row["school_name"] for row in rows}, {"贵州师范大学"})
        self.assertEqual({row["document_type"] for row in rows}, {"recommendation_exemption_list"})
        self.assertEqual({row["route"] for row in rows}, {"recommendation_exemption"})
        self.assertFalse(any("候补" in row["remarks"] for row in rows))
        self.assertFalse(any(row["person_name"] == "刘雪杨" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))
        first = rows[0]
        self.assertEqual(first["person_name"], "蹇志颖")
        self.assertEqual(first["student_id"], "221107050017")
        self.assertEqual(first["college"], "文学院")
        self.assertEqual(first["major"], "汉语言文学")

    def test_parse_ccucm_record_handles_wrapped_direct_phd_direction(self):
        from scripts.one_off.official_sources.curate_batch210_remaining_promising_pages import parse_ccucm_record

        record = parse_ccucm_record(
            "70 直博生 李佳南 22018320******5245 1006Z2 中西医结合药学 中西医结合药物的 "
            "制剂与递送系统的研究 82.60 金叶"
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["school_name"], "长春中医药大学")
        self.assertEqual(record["person_name"], "李佳南")
        self.assertEqual(record["major"], "1006Z2")
        self.assertEqual(record["admission_major"], "1006Z2 中西医结合药学")
        self.assertIn("applicant_type 直博生", record["remarks"])
        self.assertIn("direction 中西医结合药物的 制剂与递送系统的研究", record["remarks"])
        self.assertIn("total_score 82.60", record["remarks"])
        self.assertIn("advisor 金叶", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_curate_records_counts_clean_sources_and_drops_noisy_rows(self):
        from scripts.one_off.official_sources.curate_batch210_remaining_promising_pages import curate_records

        rows = curate_records(
            gznu_xlsx=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch210_remaining_promising_pages/"
                "jwc.gznu.edu.cn/9f0c97d758546d21.xlsx"
            ),
            ccucm_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch210_remaining_promising_pages/"
                "y.ccucm.edu.cn/9fb669f338a13013.pdf"
            ),
        )

        counts = {}
        for row in rows:
            counts[row["school_name"]] = counts.get(row["school_name"], 0) + 1

        self.assertEqual(counts, {"内蒙古农业大学": 22, "贵州师范大学": 209, "长春中医药大学": 70})
        self.assertEqual(len(rows), 301)
        self.assertFalse(any(row["person_name"] in {"105400", "1006Z2", "中西医结合药学"} for row in rows))
        self.assertFalse(any("候补" in row["remarks"] for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        imau_last = [row for row in rows if row["school_name"] == "内蒙古农业大学"][-1]
        self.assertEqual(imau_last["person_name"], "朝都必力格")
        self.assertEqual(imau_last["student_id"], "2022122013255")
        self.assertEqual(imau_last["major"], "马业科学")
        self.assertIn("recommendation_type 蒙授理科", imau_last["remarks"])


if __name__ == "__main__":
    unittest.main()
