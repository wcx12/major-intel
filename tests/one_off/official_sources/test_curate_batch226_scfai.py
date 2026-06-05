import unittest
from pathlib import Path


class Batch226ScfaiCurationTests(unittest.TestCase):
    def test_curate_batch226_rebuilds_scfai_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch226_scfai import curate_records

        rows = curate_records(
            documents_jsonl=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch226_scfai/"
                "documents.jsonl"
            )
        )

        self.assertEqual(len(rows), 590)
        self.assertEqual(sum(row["school_name"] == "四川美术学院" for row in rows), 590)
        self.assertEqual(len({(row["person_name"], row["student_id"], row["source_url"]) for row in rows}), 590)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first_choice = next(row for row in rows if row["student_id"] == "106556201000002")
        self.assertEqual(first_choice["person_name"], "钱伟霖")
        self.assertEqual(first_choice["document_type"], "postgraduate_admission_list")
        self.assertEqual(first_choice["route"], "postgraduate_exam_or_admission")
        self.assertEqual(first_choice["college"], "中国画与书法艺术学院")
        self.assertEqual(first_choice["major"], "135600")
        self.assertEqual(first_choice["admission_major"], "135600 美术与书法")
        self.assertIn("research_direction 51书法篆刻艺术", first_choice["remarks"])
        self.assertIn("special_plan 无", first_choice["remarks"])
        self.assertIn("admission_category 非定向就业", first_choice["remarks"])

        special_plan = next(row for row in rows if row["student_id"] == "106556201000083")
        self.assertEqual(special_plan["person_name"], "王小璐")
        self.assertIn("special_plan 少数民族骨干计划", special_plan["remarks"])
        self.assertIn("admission_category 定向就业", special_plan["remarks"])

        transfer = next(row for row in rows if row["student_id"] == "100036080108511")
        self.assertEqual(transfer["person_name"], "刘珂姌")
        self.assertEqual(transfer["college"], "马克思主义学院")
        self.assertEqual(transfer["admission_major"], "130100 艺术学")
        self.assertIn("research_direction 06马克思主义文艺理论中国化", transfer["remarks"])

        recommendation = next(row for row in rows if row["student_id"] == "106556106550003")
        self.assertEqual(recommendation["person_name"], "李卓然")
        self.assertEqual(recommendation["document_type"], "recommendation_exemption_list")
        self.assertEqual(recommendation["route"], "recommendation_exemption")
        self.assertEqual(recommendation["undergraduate_school"], "四川美术学院")
        self.assertEqual(recommendation["college"], "中国画与书法艺术学院")
        self.assertEqual(recommendation["admission_major"], "美术与书法")
        self.assertIn("research_direction 中国画艺术", recommendation["remarks"])
        self.assertIn("assessment_score 90.17", recommendation["remarks"])

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
            "复试成绩",
            "口语听力",
        ):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
