import unittest
from pathlib import Path


class Batch248CqjtuAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch248_keeps_only_cqjtu_admitted_rows(self):
        from scripts.one_off.official_sources.curate_batch248_cqjtu_admission import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch248_cqjtu_admission/yjszs.cqjtu.edu.cn/ab9261a571302314.pdf"
            )
        )

        self.assertEqual(len(rows), 1813)
        self.assertEqual(sum(row["school_name"] == "重庆交通大学" for row in rows), 1813)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 1813)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 1813)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 1813)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "刘超")
        self.assertEqual(first["student_id"], "106185201000025")
        self.assertEqual(first["college"], "土木工程学院")
        self.assertEqual(first["major"], "080100")
        self.assertEqual(first["admission_major"], "力学")
        self.assertIn("学院代码: 001", first["remarks"])
        self.assertIn("初试总分: 360", first["remarks"])
        self.assertIn("复试笔试: 90", first["remarks"])
        self.assertIn("复试面试: 81", first["remarks"])
        self.assertIn("综合成绩: 77.400", first["remarks"])

        names = {row["person_name"] for row in rows}
        self.assertNotIn("张晓民", names)
        self.assertNotIn("王晨茂", names)

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
        self.assertEqual(last["person_name"], "陈娟")
        self.assertEqual(last["student_id"], "106185217006234")
        self.assertEqual(last["college"], "智慧城市学院")
        self.assertEqual(last["major"], "085700")
        self.assertEqual(last["admission_major"], "资源与环境")
        self.assertIn("综合成绩: 61.696", last["remarks"])
        self.assertEqual(
            last["source_url"],
            "https://yjszs.cqjtu.edu.cn/__local/E/EB/D8/88DAF14D0F7C9C26C90E97E6BF5_FE0B182C_A1952.pdf",
        )


if __name__ == "__main__":
    unittest.main()
