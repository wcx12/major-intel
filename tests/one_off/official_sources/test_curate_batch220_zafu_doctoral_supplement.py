import unittest
from pathlib import Path


class Batch220ZafuDoctoralSupplementCurationTests(unittest.TestCase):
    def test_curate_zafu_html_tables_keeps_candidate_ids_scores_and_research_direction(self):
        from scripts.one_off.official_sources.curate_batch220_zafu_doctoral_supplement import curate_records

        rows = curate_records(
            html_paths=[
                Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch220_zafu_doctoral_supplement/"
                    "yjszs.zafu.edu.cn/8414edbb79258d73.htm"
                ),
                Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch220_zafu_doctoral_supplement/"
                    "yjszs.zafu.edu.cn/ff61cc3ef777664c.htm"
                ),
            ]
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual({row["school_name"] for row in rows}, {"\u6d59\u6c5f\u519c\u6797\u5927\u5b66"})
        self.assertEqual({str(row["year"]) for row in rows}, {"2026"})
        self.assertEqual({row["document_type"] for row in rows}, {"postgraduate_admission_list"})
        self.assertEqual({row["route"] for row in rows}, {"postgraduate_exam_or_admission"})
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "\u4e01\u5fd7\u6210")
        self.assertEqual(first["student_id"], "103416199666017")
        self.assertEqual(first["college"], "\u73b0\u4ee3\u519c\u5b66\u9662")
        self.assertEqual(first["major"], "090100")
        self.assertEqual(first["admission_major"], "090100 \u4f5c\u7269\u5b66")
        self.assertIn("research_direction \u7279\u8272\u4f5c\u7269\u751f\u4ea7\u4e0e\u7efc\u5408\u5229\u7528", first["remarks"])
        self.assertIn("composite_score 75.04", first["remarks"])
        self.assertIn("admission_method \u7533\u8bf7\u8003\u6838", first["remarks"])
        self.assertEqual(first["source_url"], "https://yjszs.zafu.edu.cn/info/1109/3307.htm")

        second = rows[1]
        self.assertEqual(second["person_name"], "\u51af\u5b97\u82b9")
        self.assertEqual(second["student_id"], "103416199666006")
        self.assertIn("research_direction \u4f5c\u7269\u4f18\u5f02\u79cd\u8d28\u521b\u5236\u4e0e\u5229\u7528", second["remarks"])
        self.assertIn("composite_score 76.88", second["remarks"])
        self.assertEqual(second["source_url"], "https://yjszs.zafu.edu.cn/info/1109/3304.htm")


if __name__ == "__main__":
    unittest.main()
