import importlib.util
import unittest
from pathlib import Path


class Batch262NcstRecommendationCurationTests(unittest.TestCase):
    def test_curate_batch262_keeps_only_admitted_recommendation_rows(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch262_ncst_recommendation")
        self.assertIsNotNone(spec, "batch262 curation module should exist")

        from scripts.one_off.official_sources.curate_batch262_ncst_recommendation import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch262_ncst_recommendation/"
                "yjsxy.ncst.edu.cn/bc696a7d17f86a25.pdf"
            )
        )

        self.assertEqual(len(rows), 16)
        self.assertEqual(sum(row["school_name"] == "华北理工大学" for row in rows), 16)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 16)
        self.assertEqual(sum(row["document_type"] == "incoming_recommendation_admission_list" for row in rows), 16)
        self.assertEqual(sum(row["route"] == "recommendation_exemption" for row in rows), 16)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))
        self.assertFalse(any(not row["undergraduate_school"] for row in rows))
        self.assertFalse(any(not row["undergraduate_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "范祎锋")
        self.assertEqual(first["admission_major"], "085801 电气工程")
        self.assertEqual(first["major"], "电气工程")
        self.assertEqual(first["undergraduate_school"], "河北师范大学")
        self.assertEqual(first["undergraduate_major"], "电气工程及其自动化")
        self.assertIn("综合考核成绩: 84.2", first["remarks"])
        self.assertIn("录取状态: 拟录取", first["remarks"])

        page_break_row = next(row for row in rows if row["ranking"] == "25")
        self.assertEqual(page_break_row["person_name"], "尹畅")
        self.assertEqual(page_break_row["admission_major"], "101100 护理学")
        self.assertEqual(page_break_row["undergraduate_major"], "护理学")

        last = rows[-1]
        self.assertEqual(last["ranking"], "30")
        self.assertEqual(last["person_name"], "赵晨宇")
        self.assertEqual(last["admission_major"], "105200 口腔医学")
        self.assertEqual(last["undergraduate_school"], "河北北方学院")
        self.assertEqual(last["source_url"], "https://yjsxy.ncst.edu.cn/atm/7/20250926144423420.pdf")

        names = {row["person_name"] for row in rows}
        self.assertNotIn("张帆", names)
        self.assertNotIn("王春雨", names)
        self.assertNotIn("刘幸", names)
        self.assertNotIn("梁思彤", names)
        self.assertNotIn("陈艺茜", names)

        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        excluded_terms = (
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
            "放弃一志愿录取资格",
            "拒绝待录取",
            "因差额未录取",
            "被其他学校待录取",
        )
        self.assertFalse(any(term in joined for term in excluded_terms))


if __name__ == "__main__":
    unittest.main()
