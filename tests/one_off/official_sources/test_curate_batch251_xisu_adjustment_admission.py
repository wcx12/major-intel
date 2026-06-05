import importlib.util
import unittest
from pathlib import Path


class Batch251XisuAdjustmentAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch251_preserves_xisu_html_table_fields(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch251_xisu_adjustment_admission")
        self.assertIsNotNone(spec, "batch251 curation module should exist")

        from scripts.one_off.official_sources.curate_batch251_xisu_adjustment_admission import curate_records

        rows = curate_records(
            html_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch251_xisu_adjustment_admission/yzw.xisu.edu.cn/33396b4b85311a14.htm"
            )
        )

        self.assertEqual(len(rows), 158)
        self.assertEqual(sum(row["school_name"] == "西安外国语大学" for row in rows), 158)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 158)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 158)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 158)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "张佳琪")
        self.assertEqual(first["student_id"], "107106614310644")
        self.assertEqual(first["major"], "030500")
        self.assertEqual(first["admission_major"], "马克思主义理论")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("初试总分: 347", first["remarks"])
        self.assertIn("复试总分: 109.67", first["remarks"])
        self.assertIn("总成绩: 78.2", first["remarks"])
        self.assertIn("特殊说明: 士兵计划", first["remarks"])

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
        self.assertNotIn("吕老师", {row["person_name"] for row in rows})

        last = rows[-1]
        self.assertEqual(last["person_name"], "徐思")
        self.assertEqual(last["student_id"], "102706210008506")
        self.assertEqual(last["major"], "045300")
        self.assertEqual(last["admission_major"], "国际中文教育")
        self.assertEqual(last["ranking"], "158")
        self.assertEqual(
            last["source_url"],
            "https://yzw.xisu.edu.cn/info/1080/4622.htm",
        )


if __name__ == "__main__":
    unittest.main()
