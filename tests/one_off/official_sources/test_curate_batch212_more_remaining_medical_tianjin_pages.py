import unittest
from pathlib import Path


class Batch212MoreRemainingMedicalTianjinPagesCurationTests(unittest.TestCase):
    def test_curate_stdu_pdf_keeps_only_proposed_admitted_rows(self):
        from scripts.one_off.official_sources.curate_batch212_more_remaining_medical_tianjin_pages import curate_stdu_pdf

        rows = curate_stdu_pdf(
            Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch212_more_remaining_medical_tianjin_pages/"
                "yjs.stdu.edu.cn/01505ff283ae7d9a.pdf"
            )
        )

        self.assertEqual(len(rows), 1016)
        self.assertEqual({row["school_name"] for row in rows}, {"石家庄铁道大学"})
        self.assertEqual({row["document_type"] for row in rows}, {"postgraduate_admission_list"})
        self.assertEqual({row["route"] for row in rows}, {"postgraduate_exam_or_admission"})
        self.assertFalse(any(row["needs_review"] for row in rows))

        flattened = "\n".join(str(row) for row in rows)
        self.assertNotIn("复试不合格", flattened)
        self.assertNotIn("缺考", flattened)
        self.assertNotIn("放弃复试", flattened)
        self.assertNotIn("不予录取", flattened)

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["student_id"], "101076022010015")
        self.assertEqual(first["person_name"], "李炳兴")
        self.assertEqual(first["college"], "土木工程学院")
        self.assertEqual(first["major"], "081400")
        self.assertEqual(first["admission_major"], "081400 土木工程")
        self.assertIn("list_status 拟录取", first["remarks"])
        self.assertIn("total_score 76.920", first["remarks"])

        soldier_plan = [row for row in rows if row["person_name"] == "张晓博"][0]
        self.assertEqual(soldier_plan["student_id"], "101076022100574")
        self.assertEqual(soldier_plan["admission_major"], "085404 计算机技术")
        self.assertIn("note 退役大学生士兵计划", soldier_plan["remarks"])


if __name__ == "__main__":
    unittest.main()
