import unittest
from pathlib import Path


class Batch227TustCurationTests(unittest.TestCase):
    def test_curate_batch227_rebuilds_tust_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch227_tust import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch227_tust_sdut_qut/"
                "yjs.tust.edu.cn"
            )
        )

        self.assertEqual(len(rows), 2090)
        self.assertEqual(sum(row["school_name"] == "天津科技大学" for row in rows), 2090)
        self.assertEqual(
            sum(row["document_type"] == "postgraduate_admission_list" for row in rows),
            2062,
        )
        self.assertEqual(
            sum(row["document_type"] == "incoming_recommendation_admission_list" for row in rows),
            28,
        )
        self.assertEqual(len({(row["person_name"], row["student_id"], row["ranking"], row["source_url"]) for row in rows}), 2090)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first_choice = next(row for row in rows if row["student_id"] == "100576011120132")
        self.assertEqual(first_choice["person_name"], "庄芸鉴")
        self.assertEqual(first_choice["document_type"], "postgraduate_admission_list")
        self.assertEqual(first_choice["route"], "postgraduate_exam_or_admission")
        self.assertEqual(first_choice["college"], "机械工程学院")
        self.assertEqual(first_choice["major"], "080200")
        self.assertEqual(first_choice["admission_major"], "机械工程")
        self.assertEqual(first_choice["ranking"], "1")
        self.assertIn("batch 一志愿第一批", first_choice["remarks"])
        self.assertIn("initial_score 265", first_choice["remarks"])
        self.assertIn("composite_score 61.26", first_choice["remarks"])

        transfer = next(row for row in rows if row["student_id"] == "106986123306881")
        self.assertEqual(transfer["person_name"], "张蕊")
        self.assertEqual(transfer["college"], "化工与材料学院")
        self.assertEqual(transfer["major"], "080500")
        self.assertEqual(transfer["admission_major"], "材料科学与工程")
        self.assertIn("batch 调剂第一批", transfer["remarks"])
        self.assertIn("research_direction 材料物理与化学", transfer["remarks"])

        recommendation = next(row for row in rows if row["person_name"] == "高润凡")
        self.assertEqual(recommendation["document_type"], "incoming_recommendation_admission_list")
        self.assertEqual(recommendation["route"], "recommendation_exemption")
        self.assertEqual(recommendation["college"], "电子信息与自动化学院")
        self.assertEqual(recommendation["student_id"], "")
        self.assertEqual(recommendation["undergraduate_school"], "河北农业大学")
        self.assertEqual(recommendation["undergraduate_major"], "智慧农业")
        self.assertEqual(recommendation["admission_major"], "电子信息")
        self.assertIn("gender 女", recommendation["remarks"])
        self.assertIn("assessment_score 93.20", recommendation["remarks"])

        flattened = "\n".join(str(row) for row in rows)
        for bad_fragment in (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
        ):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
