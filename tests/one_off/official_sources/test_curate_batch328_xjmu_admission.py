import unittest


SAMPLE_TEXT = """
新疆医科大学2023年硕士研究生一志愿考生拟录取名单（不含推免生和本硕生）
序号 考生编号 考生姓名 民族 报考院系名称 学位 类型 专业 代码 专业名称 研究 方向 码 研究方向名称 学习方式 初试 成绩 复试 成绩 加试1 成绩 加试2 成绩 总成绩 拟录取情况 备注
1 107603123454560 刘千熙 汉族 001基础医学院 学术学位 071003 生理学 00 不区分研究方向 全日制 369 241.20 76.44 拟录取
2 107603123450021 克朗·木尔扎汗 哈萨克族 001基础医学院 学术学位 071003 生理学 00 不区分研究方向 全日制 310 162.00 58.80
复试成绩不合
格，不予拟录取
38 107603123454448
迪丽达尔·沙哈提
别克
哈萨克族 001基础医学院 学术学位 100103 病原生物学 00 不区分研究方向 全日制 303 203.60 66.63 拟录取 享受少数民族照顾政策
42 107603123454449
热孜瓦古力·居麦
克
维吾尔族 001基础医学院 学术学位 100103 病原生物学 00 不区分研究方向 全日制 265 206.60 62.47
计划受限，不予
拟录取
4 121213000001628 陈勇强 汉族 001基础医学院 学术学位 071003 生理学 00 不区分研究方向 全日制 358 0.00 42.96 放弃
"""


class Batch328XjmuAdmissionCurationTests(unittest.TestCase):
    def test_curates_only_final_admission_rows_from_raw_pdf_text(self):
        from scripts.one_off.official_sources.curate_batch328_xjmu_admission import PDF_SOURCES, curate_pdf_records

        rows = curate_pdf_records(SAMPLE_TEXT, PDF_SOURCES[0])

        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["school_name"] == "新疆医科大学" for row in rows))
        self.assertTrue(all(row["year"] == 2023 for row in rows))
        self.assertTrue(all(row["route"] == "postgraduate_exam_or_admission" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "刘千熙")
        self.assertEqual(first["student_id"], "107603123454560")
        self.assertEqual(first["college"], "001基础医学院")
        self.assertEqual(first["admission_major"], "生理学")
        self.assertIn("major_code: 071003", first["remarks"])
        self.assertIn("total_score: 76.44", first["remarks"])
        self.assertIn("official_admission_status: 拟录取", first["remarks"])

        split_name = rows[1]
        self.assertEqual(split_name["person_name"], "迪丽达尔·沙哈提别克")
        self.assertEqual(split_name["student_id"], "107603123454448")
        self.assertEqual(split_name["admission_major"], "病原生物学")
        self.assertIn("note: 享受少数民族照顾政策", split_name["remarks"])

        flattened_status_fields = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("remarks", "quality_flags"))
            for row in rows
        )
        for bad_fragment in (
            "不予拟录取",
            "拟不录取",
            "不予录取",
            "放弃",
            "计划受限",
            "不予复试",
            "复试成绩不合",
        ):
            self.assertNotIn(bad_fragment, flattened_status_fields)


if __name__ == "__main__":
    unittest.main()
