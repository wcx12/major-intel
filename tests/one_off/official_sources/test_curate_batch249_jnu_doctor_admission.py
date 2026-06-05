import importlib.util
import unittest
from pathlib import Path


class Batch249JnuDoctorAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch249_preserves_jnu_doctor_excel_fields(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch249_jnu_doctor_admission")
        self.assertIsNotNone(spec, "batch249 curation module should exist")

        from scripts.one_off.official_sources.curate_batch249_jnu_doctor_admission import curate_records

        rows = curate_records(
            xlsx_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch249_jnu_doctor_admission/yz.jnu.edu.cn/e4b19b8e5a05e00b.xlsx"
            )
        )

        self.assertEqual(len(rows), 228)
        self.assertEqual(sum(row["school_name"] == "暨南大学" for row in rows), 228)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 228)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 228)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 228)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "梁滨雁")
        self.assertEqual(first["student_id"], "105596126002005")
        self.assertEqual(first["college"], "经济学院")
        self.assertEqual(first["major"], "020104")
        self.assertEqual(first["admission_major"], "西方经济学")
        self.assertIn("院系代码: 001", first["remarks"])
        self.assertIn("录取类别: 非定向", first["remarks"])
        self.assertIn("考试方式: 申请考核", first["remarks"])
        self.assertIn("初试总分: 271.4", first["remarks"])
        self.assertIn("复试总分: 252.8", first["remarks"])
        self.assertIn("总成绩: 262.1", first["remarks"])

        directed = next(row for row in rows if row["person_name"] == "李芳容")
        self.assertEqual(directed["college"], "马克思主义学院")
        self.assertEqual(directed["major"], "0305J2")
        self.assertEqual(directed["admission_major"], "中华民族共同体学")
        self.assertIn("拟录取研究方向名称: 中华民族共同体基础理论", directed["remarks"])

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
        self.assertEqual(last["person_name"], "孙榕")
        self.assertEqual(last["student_id"], "105596105740442")
        self.assertEqual(last["college"], "网络空间安全学院")
        self.assertEqual(last["major"], "083900")
        self.assertEqual(last["admission_major"], "网络空间安全")
        self.assertIn("考试方式: 直博生", last["remarks"])
        self.assertIn("备注: 直博生", last["remarks"])
        self.assertEqual(
            last["source_url"],
            "https://yz.jnu.edu.cn/_upload/article/files/99/b1/1fb265f14ab3a02802f00c1b0d79/c7235e9d-63f1-4efc-8781-7d1090e91a28.xlsx",
        )


if __name__ == "__main__":
    unittest.main()
