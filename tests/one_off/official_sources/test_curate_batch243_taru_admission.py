import unittest
from pathlib import Path


class Batch243TaruAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch243_keeps_only_taru_admitted_candidates(self):
        from scripts.one_off.official_sources.curate_batch243_taru_admission import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260529_batch243_taru_admission/yjsb.taru.edu.cn/3b74bf6c52b4cae6.pdf"
            )
        )

        self.assertEqual(len(rows), 371)
        self.assertEqual(sum(row["school_name"] == "塔里木大学" for row in rows), 371)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 371)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 371)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"].isdigit() for row in rows))
        self.assertFalse(any(row["person_name"] == "理论" for row in rows))

        excluded_names = {"高曼玲", "王倩", "逯政要", "张翌", "李宗蓓"}
        self.assertTrue(excluded_names.isdisjoint({row["person_name"] for row in rows}))

        hard_exclude_terms = (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "复试成绩不合格",
            "加试不合格",
            "缺考",
            "候补",
        )
        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))

        first = rows[0]
        self.assertEqual(first["person_name"], "祁德新")
        self.assertEqual(first["student_id"], "107576350900003")
        self.assertEqual(first["college"], "农学院")
        self.assertEqual(first["admission_major"], "作物学")

        self.assertEqual(rows[-1]["person_name"], "努尔加玛丽·喀迪尔")
        self.assertEqual(rows[-1]["college"], "外国语学院")
        self.assertEqual(rows[-1]["admission_major"], "学科教学（英语）")
        self.assertIn("少数民族照顾政策", rows[-1]["remarks"])


if __name__ == "__main__":
    unittest.main()
