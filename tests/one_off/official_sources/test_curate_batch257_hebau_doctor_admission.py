import importlib.util
import unittest
from pathlib import Path


class Batch257HebauDoctorAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch257_parses_hebau_doctoral_admission_pdf_rows(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch257_hebau_doctor_admission")
        self.assertIsNotNone(spec, "batch257 curation module should exist")

        from scripts.one_off.official_sources.curate_batch257_hebau_doctor_admission import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch257_hebau_doctor_admission/"
                "yanjiusheng.hebau.edu.cn/0e22121dee46236a.pdf"
            )
        )

        self.assertEqual(len(rows), 42)
        self.assertEqual(sum(row["school_name"] == "河北农业大学" for row in rows), 42)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 42)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 42)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 42)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["student_id"], "20242050090")
        self.assertEqual(first["person_name"], "周静怡")
        self.assertEqual(first["college"], "生命科学学院")
        self.assertEqual(first["admission_major"], "生物学")
        self.assertIn("第一导师: 赵锦", first["remarks"])
        self.assertIn("考核成绩: 91.00", first["remarks"])
        self.assertIn("拟录取类别: 非定向就业", first["remarks"])

        two_advisors = rows[4]
        self.assertEqual(two_advisors["ranking"], "5")
        self.assertEqual(two_advisors["person_name"], "彭程")
        self.assertEqual(two_advisors["college"], "食品科技学院")
        self.assertEqual(two_advisors["admission_major"], "食品科学与工程")
        self.assertIn("第一导师: 张伟", two_advisors["remarks"])
        self.assertIn("第二导师: 李晨", two_advisors["remarks"])

        wrapped_college = next(row for row in rows if row["ranking"] == "27")
        self.assertEqual(wrapped_college["person_name"], "周鑫源")
        self.assertEqual(wrapped_college["college"], "资源与环境科学学院（国土资源学院）")
        self.assertEqual(wrapped_college["admission_major"], "农业资源与环境")
        self.assertIn("第一导师: 薛澄", wrapped_college["remarks"])

        wrapped_linyuan = next(row for row in rows if row["ranking"] == "36")
        self.assertEqual(wrapped_linyuan["person_name"], "胡秋硕")
        self.assertEqual(wrapped_linyuan["college"], "林学院（园林与旅游学院）")
        self.assertEqual(wrapped_linyuan["admission_major"], "林学")

        last = rows[-1]
        self.assertEqual(last["ranking"], "42")
        self.assertEqual(last["student_id"], "20257201802")
        self.assertEqual(last["person_name"], "李霄")
        self.assertEqual(last["college"], "动物医学院（中兽医学院）")
        self.assertEqual(last["admission_major"], "兽医")
        self.assertTrue(last["source_url"].startswith("https://yanjiusheng.hebau.edu.cn/__local/"))

        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
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
            "放弃一志愿录取资格",
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))


if __name__ == "__main__":
    unittest.main()
