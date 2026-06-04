import unittest
from pathlib import Path


class Batch222MinzuUniversitiesCurationTests(unittest.TestCase):
    def test_curate_batch222_repairs_xbmu_pdf_rows_and_keeps_nmu_rows(self):
        from scripts.one_off.official_sources.curate_batch222_minzu_universities import curate_records

        rows = curate_records(
            nmu_clean_csv=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities/"
                "records_clean.csv"
            ),
            xbmu_pdf_paths={
                "ordinary": Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities/"
                    "www.xbmu.edu.cn/7e85a7d3965e71aa.pdf"
                ),
                "minority_backbone": Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities/"
                    "www.xbmu.edu.cn/4d88ffd34d963f64.pdf"
                ),
                "retired_soldier": Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities/"
                    "www.xbmu.edu.cn/3cfe555dc68509a0.pdf"
                ),
            },
        )

        self.assertEqual(len(rows), 1515)
        self.assertEqual(sum(row["school_name"] == "北方民族大学" for row in rows), 1025)
        self.assertEqual(sum(row["school_name"] == "西北民族大学" for row in rows), 490)
        self.assertFalse(any(row["needs_review"] for row in rows))

        first_xbmu = next(row for row in rows if row["school_name"] == "西北民族大学")
        self.assertEqual(first_xbmu["person_name"], "陈丹阳")
        self.assertEqual(first_xbmu["student_id"], "107426123450003")
        self.assertEqual(first_xbmu["college"], "经济学院")
        self.assertEqual(first_xbmu["major"], "025100")
        self.assertEqual(first_xbmu["admission_major"], "025100 金融")
        self.assertEqual(first_xbmu["ranking"], "1")
        self.assertIn("research_direction 不区分研究方向", first_xbmu["remarks"])
        self.assertIn("initial_score 372.00", first_xbmu["remarks"])
        self.assertIn("retest_score 81.95", first_xbmu["remarks"])
        self.assertIn("total_score 76.67", first_xbmu["remarks"])
        self.assertIn("plan_type 普通计划含照顾政策", first_xbmu["remarks"])

        minority = next(row for row in rows if row["student_id"] == "107426123450100")
        self.assertEqual(minority["person_name"], "毕文锦")
        self.assertEqual(minority["major"], "035102")
        self.assertEqual(minority["admission_major"], "035102 法律（法学）")
        self.assertIn("plan_type 少数民族高层次骨干人才计划", minority["remarks"])
        self.assertIn("source_province 青海省", minority["remarks"])

        soldier = next(row for row in rows if row["student_id"] == "107426123450066")
        self.assertEqual(soldier["person_name"], "郭鹏飞")
        self.assertEqual(soldier["college"], "法学院")
        self.assertEqual(soldier["major"], "035101")
        self.assertIn("plan_type 退役大学生士兵专项计划", soldier["remarks"])
        self.assertIn("initial_converted_score 88.42", soldier["remarks"])

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

        for row in rows:
            self.assertNotEqual(row["person_name"], "麻醉学")
            self.assertNotEqual(row["student_id"], "00")


if __name__ == "__main__":
    unittest.main()
