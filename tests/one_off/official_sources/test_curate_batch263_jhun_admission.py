import importlib.util
import unittest
from pathlib import Path


class Batch263JhunAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch263_parses_jhun_master_and_doctor_pdfs(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch263_jhun_admission")
        self.assertIsNotNone(spec, "batch263 curation module should exist")

        from scripts.one_off.official_sources.curate_batch263_jhun_admission import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch263_jhun_admission/"
                "gs.jhun.edu.cn"
            )
        )

        self.assertEqual(len(rows), 1088)
        self.assertEqual(sum(row["school_name"] == "江汉大学" for row in rows), 1088)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 1088)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 1088)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 1088)

        master_rows = [row for row in rows if "硕士研究生招生拟录取名单" in row["title"]]
        doctor_rows = [row for row in rows if "博士研究生招生拟录取名单" in row["title"]]
        self.assertEqual(len(master_rows), 1050)
        self.assertEqual(len(doctor_rows), 38)

        first = master_rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "廖怡菲")
        self.assertEqual(first["student_id"], "110726000001877")
        self.assertEqual(first["college"], "光电材料与技术学院")
        self.assertEqual(first["major"], "化学工程与技术")
        self.assertEqual(first["admission_major"], "化学工程与技术")
        self.assertIn("初试成绩: 340", first["remarks"])
        self.assertIn("复试成绩: 87.2", first["remarks"])
        self.assertIn("录取成绩: 75.68", first["remarks"])

        split_college = next(row for row in master_rows if row["ranking"] == "982")
        self.assertEqual(split_college["person_name"], "冯宇阳")
        self.assertEqual(split_college["student_id"], "104976100302681")
        self.assertEqual(split_college["college"], "数字建造与爆破工程学院")
        self.assertEqual(split_college["major"], "土木水利")

        special = master_rows[-1]
        self.assertEqual(special["ranking"], "1050")
        self.assertEqual(special["person_name"], "翟世豪")
        self.assertEqual(special["college"], "人工智能学院")
        self.assertEqual(special["major"], "管理科学与工程")
        self.assertIn("立功表彰退役军人", special["remarks"])
        self.assertTrue(special["needs_review"])

        doctor_first = doctor_rows[0]
        self.assertEqual(doctor_first["ranking"], "普通招考类-1")
        self.assertEqual(doctor_first["person_name"], "王慧敏")
        self.assertEqual(doctor_first["student_id"], "110722026081719")
        self.assertEqual(doctor_first["college"], "环境与健康学院")
        self.assertEqual(doctor_first["major"], "化学工程与技术")

        doctor_split = next(row for row in doctor_rows if row["person_name"] == "陈泽曦")
        self.assertEqual(doctor_split["ranking"], "申请-考核制-2")
        self.assertEqual(doctor_split["student_id"], "110722026081734")
        self.assertEqual(doctor_split["college"], "数字建造与爆破工程学院")

        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("person_name", "college", "major", "admission_major", "remarks"))
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
