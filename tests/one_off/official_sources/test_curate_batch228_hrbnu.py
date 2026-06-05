import unittest
from pathlib import Path


class Batch228HrbnuCurationTests(unittest.TestCase):
    def test_curate_batch228_rebuilds_hrbnu_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch228_hrbnu import curate_records

        rows = curate_records(
            raw_pdf=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch228_hrbnu/"
                "yjsxy.hrbnu.edu.cn/6edae7b26bf65f7b.pdf"
            )
        )

        self.assertEqual(len(rows), 1665)
        self.assertEqual(sum(row["school_name"] == "哈尔滨师范大学" for row in rows), 1665)
        self.assertEqual(len({row["student_id"] for row in rows}), 1665)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = next(row for row in rows if row["student_id"] == "102316045103095")
        self.assertEqual(first["person_name"], "张思琦")
        self.assertEqual(first["college"], "文学院")
        self.assertEqual(first["major"], "045103")
        self.assertEqual(first["admission_major"], "学科教学（语文）")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("study_mode 非全日制", first["remarks"])
        self.assertIn("total_score 539", first["remarks"])

        special_policy = next(row for row in rows if row["student_id"] == "102316045103077")
        self.assertEqual(special_policy["person_name"], "乌音嘎")
        self.assertIn("少数民族照顾政策", special_policy["remarks"])

        last = rows[-1]
        self.assertEqual(last["person_name"], "丛山峰")
        self.assertEqual(last["student_id"], "102316070304001")
        self.assertEqual(last["admission_major"], "物理化学")

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
