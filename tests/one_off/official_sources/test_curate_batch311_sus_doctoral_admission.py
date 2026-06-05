import unittest


SAMPLE_TEXT = """
报名号 姓名 性
别
报考专
业名称
英语水
平
20190001 于常晓 男
运动人
体科学 六级 437
A comparative biomechanical analysis of the performance level.
非定向
就业 88 67.5 78.4 75.1 20190007 马越斐
女
体育管 理
六级 456
全民网球赛事品牌形象与品牌忠诚。
定向就 业
85 67.5 84.6 79.5
健将
20190038 刘庆生 男
体育管
理
在重要岗位从事新闻宣传工作，实践经验丰富。
定向就
业
75 70 86.8 81.8
"""


class Batch311SusDoctoralAdmissionCurationTests(unittest.TestCase):
    def test_curates_sus_doctoral_pdf_text_rows(self):
        from scripts.one_off.official_sources.curate_batch311_sus_doctoral_admission import curate_records

        rows = curate_records(raw_text=SAMPLE_TEXT)

        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["school_name"] == "上海体育大学" for row in rows))
        self.assertTrue(all(row["year"] == 2020 for row in rows))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in rows))
        self.assertTrue(all(row["route"] == "postgraduate_exam_or_admission" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["student_id"], "20190001")
        self.assertEqual(first["person_name"], "于常晓")
        self.assertEqual(first["admission_major"], "运动人体科学")
        self.assertIn("gender: 男", first["remarks"])
        self.assertIn("english_level: 六级 437", first["remarks"])
        self.assertIn("composite_score: 75.1", first["remarks"])

        cross_page = rows[1]
        self.assertEqual(cross_page["student_id"], "20190007")
        self.assertEqual(cross_page["person_name"], "马越斐")
        self.assertEqual(cross_page["admission_major"], "体育管理")
        self.assertIn("admission_category: 定向就业", cross_page["remarks"])
        self.assertIn("note: 健将", cross_page["remarks"])

        special = rows[2]
        self.assertEqual(special["student_id"], "20190038")
        self.assertEqual(special["person_name"], "刘庆生")
        self.assertEqual(special["admission_major"], "体育管理")
        self.assertIn("official_source_school_name: 上海体育学院", special["remarks"])
        self.assertIn("written_score: 70", special["remarks"])

        flattened = "\n".join(str(row) for row in rows)
        for bad_fragment in ("进入复试", "拟不录取", "不予录取", "候补", "放弃", "未参加复试"):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
