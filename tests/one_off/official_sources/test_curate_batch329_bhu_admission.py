import unittest

from scripts.one_off.official_sources.curate_batch329_bhu_admission import parse_record_line, parse_records_from_text


class CurateBatch329BhuAdmissionTests(unittest.TestCase):
    def test_parse_record_line_keeps_major_separate_from_college(self):
        record = parse_record_line(
            "103195211301456 丁* 物理科学与技术学院 凝聚态物理 非定向就业 304 93 73.68 全日制"
        )

        self.assertEqual(record["student_id"], "103195211301456")
        self.assertEqual(record["person_name"], "丁*")
        self.assertEqual(record["college"], "物理科学与技术学院")
        self.assertEqual(record["admission_major"], "凝聚态物理")
        self.assertEqual(record["remarks"], "admission_category: 非定向就业; initial_score: 304; interview_score: 93; total_score: 73.68; study_mode: 全日制; official_admission_status: 拟录取")

    def test_parse_record_line_preserves_optional_source_remark(self):
        record = parse_record_line(
            "103575210019567 袁* 教育科学学院 教育学原理 非定向就业 312 85 71.44 全日制 退役士兵计划"
        )

        self.assertEqual(record["college"], "教育科学学院")
        self.assertEqual(record["admission_major"], "教育学原理")
        self.assertIn("source_remark: 退役士兵计划", record["remarks"])

    def test_parse_records_from_text_ignores_header_and_page_noise(self):
        text = """
考生编号 考生姓名 拟录取院系 拟录取专业 拟录取类别
初试
成绩
103575210019567 袁* 教育科学学院 教育学原理 非定向就业 312 85 71.44 全日制 退役士兵计划
渤
海
大
学
103195211301456 丁* 物理科学与技术学院 凝聚态物理 非定向就业 304 93 73.68 全日制
"""

        records = parse_records_from_text(text)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["admission_major"], "教育学原理")
        self.assertEqual(records[1]["admission_major"], "凝聚态物理")


if __name__ == "__main__":
    unittest.main()
