import unittest


SAMPLE_TEXT = """
长春师范大学2026年硕士研究生招生考试
一志愿考生成绩及拟录取结果
考生姓名 考生编号 学习方式
报考学院名
称
报考专业名
称
初试
总成绩
是否
拟录取
专项计划 备注
于巾栩 102056210101065 全日制
马克思主义学
院
马克思主义理
论
441
14.80
63.00
77.00
154.80
83.88
是
成佳冉 102056210100064 全日制
马克思主义学
院
马克思主义理
论
416
13.00
54.20
67.00
134.20
76.76
否
王瑞鑫 102056210202607 全日制 教育学院 教育学 385 17.00 69.00 85.00 171.00 80.40 是
张普凡 102056210201184 全日制 教育学院 现代教育技术 388 18.00 73.00 80.00 171.00 80.76 是 退役大学生计划
"""


class Batch312CcsfuAdmissionCurationTests(unittest.TestCase):
    def test_curates_only_yes_admission_rows_from_mixed_pdf_text(self):
        from scripts.one_off.official_sources.curate_batch312_ccsfu_admission import curate_records

        rows = curate_records(raw_text=SAMPLE_TEXT)

        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["school_name"] == "长春师范大学" for row in rows))
        self.assertTrue(all(row["year"] == 2026 for row in rows))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in rows))
        self.assertTrue(all(row["route"] == "postgraduate_exam_or_admission" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertNotIn("102056210100064", {row["student_id"] for row in rows})

        broken = rows[0]
        self.assertEqual(broken["person_name"], "于巾栩")
        self.assertEqual(broken["student_id"], "102056210101065")
        self.assertEqual(broken["college"], "马克思主义学院")
        self.assertEqual(broken["admission_major"], "马克思主义理论")
        self.assertIn("admission_status: 是", broken["remarks"])
        self.assertIn("initial_score: 441", broken["remarks"])
        self.assertIn("composite_score: 83.88", broken["remarks"])

        one_line = rows[1]
        self.assertEqual(one_line["person_name"], "王瑞鑫")
        self.assertEqual(one_line["college"], "教育学院")
        self.assertEqual(one_line["admission_major"], "教育学")

        plan = rows[2]
        self.assertEqual(plan["person_name"], "张普凡")
        self.assertEqual(plan["admission_major"], "现代教育技术")
        self.assertIn("专项计划: 退役大学生计划", plan["remarks"])

        flattened = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("remarks", "quality_flags"))
            for row in rows
        )
        for bad_fragment in ("未录取", "admission_status: 否", "拟不录取", "不予录取", "候补"):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
