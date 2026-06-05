import importlib.util
import unittest
from pathlib import Path


class Batch253WnmcAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch253_parses_wnmc_pdf_table_rows(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch253_wnmc_admission")
        self.assertIsNotNone(spec, "batch253 curation module should exist")

        from scripts.one_off.official_sources.curate_batch253_wnmc_admission import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch253_wnmc_recommendation/www.wnmc.edu.cn/17cb42ea25f79920.pdf"
            )
        )

        self.assertEqual(len(rows), 768)
        self.assertEqual(sum(row["school_name"] == "皖南医学院" for row in rows), 768)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 768)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 768)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 768)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "王诗雅")
        self.assertEqual(first["student_id"], "102985211402915")
        self.assertEqual(first["major"], "030500")
        self.assertEqual(first["admission_major"], "马克思主义理论")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("性别: 女", first["remarks"])
        self.assertIn("研究方向: 马克思主义基本原理", first["remarks"])
        self.assertIn("类别: 调剂", first["remarks"])
        self.assertIn("初试总分: 358", first["remarks"])
        self.assertIn("复试总分: 91.57", first["remarks"])
        self.assertIn("录取总分: 77.59", first["remarks"])

        hard_exclude_terms = (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
            "不合格",
            "名额受限",
        )
        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))

        last = rows[-1]
        self.assertEqual(last["person_name"], "王天楠")
        self.assertEqual(last["student_id"], "103685210002269")
        self.assertEqual(last["major"], "105500")
        self.assertEqual(last["admission_major"], "药学")
        self.assertEqual(last["ranking"], "768")
        self.assertIn("类别: 一志愿", last["remarks"])
        self.assertEqual(
            last["source_url"],
            "https://www.wnmc.edu.cn/__local/A/C6/DA/A19EA1BD793B172B18AD6C3E700_229104C8_44124.pdf",
        )


if __name__ == "__main__":
    unittest.main()
