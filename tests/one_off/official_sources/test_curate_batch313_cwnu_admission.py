import unittest


PDF_SAMPLE_TEXT = """
                 西华师范大学2025年硕士研究生拟录取名单公示
学院名称   专业代码 专业名称      研究方向   学习方式      考生编号           姓名 初试成绩 复试成绩 总成绩 录取类别              备注

教育学院   040100   教育学      教育学原理   全日制    106385040100065   季*妃   352   87.2   77.12 非定向

历史文化学
      045109   学科教学（历史）   不区分研究方向   全日制    106375206006283   陈*姗   366   76.8    75    非定向
  院

历史文化学                 秦汉至宋元明考
      060100   考古学              全日制    106385060100003   胡*彦   365   78.5   75.75 非定向
  院                      古

地理科学学        水土保持与荒漠化防
      091000           不区分研究方向   全日制    106385091000015   刘*飞   379   86.33   80.01 非定向
  院             治学

管理学院   125200   公共管理 不区分研究方向 非全日制   106385125200283   李*    153   80.5   65.75   定向   退役大学生士兵计划
"""


DOCTOR_HTML_SAMPLE = """
<html><body>
<table>
<tr><td>序号</td><td>姓名</td><td>拟录取专业</td><td>拟录取研究方向</td><td>报考导师</td><td>材料审核成绩</td><td>综合考核成绩</td><td>总成绩</td><td>考生类别</td></tr>
<tr><td>1</td><td>王雨洁</td><td>生态学</td><td>植物生态学</td><td>李明</td><td>75.00</td><td>79.32</td><td>78.03</td><td>硕博-普通</td></tr>
</table>
</body></html>
"""


class Batch313CwnuAdmissionCurationTests(unittest.TestCase):
    def test_curates_pdf_rows_across_layout_wrapping(self):
        from scripts.one_off.official_sources.curate_batch313_cwnu_admission import PDF_SOURCES, curate_pdf_records

        rows = curate_pdf_records(PDF_SAMPLE_TEXT, PDF_SOURCES[0])

        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row["school_name"] == "西华师范大学" for row in rows))
        self.assertTrue(all(row["year"] == 2025 for row in rows))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in rows))
        self.assertTrue(all(row["route"] == "postgraduate_exam_or_admission" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "季*妃")
        self.assertEqual(first["student_id"], "106385040100065")
        self.assertEqual(first["college"], "教育学院")
        self.assertEqual(first["admission_major"], "教育学")
        self.assertIn("research_direction: 教育学原理", first["remarks"])
        self.assertIn("learning_mode: 全日制", first["remarks"])
        self.assertIn("total_score: 77.12", first["remarks"])

        split_college = rows[1]
        self.assertEqual(split_college["college"], "历史文化学院")
        self.assertEqual(split_college["admission_major"], "学科教学（历史）")
        self.assertIn("research_direction: 不区分研究方向", split_college["remarks"])

        split_direction = rows[2]
        self.assertEqual(split_direction["college"], "历史文化学院")
        self.assertEqual(split_direction["admission_major"], "考古学")
        self.assertIn("research_direction: 秦汉至宋元明考古", split_direction["remarks"])

        split_major = rows[3]
        self.assertEqual(split_major["college"], "地理科学学院")
        self.assertEqual(split_major["admission_major"], "水土保持与荒漠化防治学")
        self.assertIn("research_direction: 不区分研究方向", split_major["remarks"])

        second_batch_note = rows[4]
        self.assertEqual(second_batch_note["person_name"], "李*")
        self.assertEqual(second_batch_note["college"], "管理学院")
        self.assertIn("learning_mode: 非全日制", second_batch_note["remarks"])
        self.assertIn("note: 退役大学生士兵计划", second_batch_note["remarks"])

    def test_curates_doctor_html_table(self):
        from scripts.one_off.official_sources.curate_batch313_cwnu_admission import curate_doctor_html_records

        rows = curate_doctor_html_records(DOCTOR_HTML_SAMPLE)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["school_name"], "西华师范大学")
        self.assertEqual(row["year"], 2025)
        self.assertEqual(row["person_name"], "王雨洁")
        self.assertEqual(row["admission_major"], "生态学")
        self.assertEqual(row["ranking"], "1")
        self.assertIn("research_direction: 植物生态学", row["remarks"])
        self.assertIn("advisor: 李明", row["remarks"])
        self.assertIn("total_score: 78.03", row["remarks"])

        flattened = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("remarks", "quality_flags"))
            for row in rows
        )
        for bad_fragment in ("进入复试名单", "拟不录取", "不予录取", "admission_status: 否", "候补"):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
