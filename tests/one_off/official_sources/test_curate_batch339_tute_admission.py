import unittest

from scripts.one_off.official_sources.curate_batch339_tute_admission import parse_record_line, parse_records_from_text


class CurateBatch339TuteAdmissionTests(unittest.TestCase):
    def test_parse_numbered_record_line(self):
        record = parse_record_line(
            "100665132310085 蔡茗涵 040100 教育学 367 84.45 76.72 全日制"
        )

        self.assertEqual(record["student_id"], "100665132310085")
        self.assertEqual(record["person_name"], "蔡茗涵")
        self.assertEqual(record["major"], "040100")
        self.assertEqual(record["admission_major"], "教育学")
        self.assertEqual(record["remarks"], "major_code: 040100; initial_score: 367; interview_score: 84.45; total_score: 76.72; study_mode: 全日制; official_admission_status: 拟录取")

    def test_parse_exempt_record_without_student_id(self):
        record = parse_record_line("叶宗波 085502 车辆工程 72.64 全日制 免初试")

        self.assertEqual(record["student_id"], "")
        self.assertEqual(record["person_name"], "叶宗波")
        self.assertEqual(record["admission_major"], "车辆工程")
        self.assertIn("total_score: 72.64", record["remarks"])
        self.assertIn("source_remark: 免初试", record["remarks"])

    def test_parse_records_from_text_ignores_headers_and_footers(self):
        text = """
天津职业技术师范大学2025年硕士研究生拟录取名单
考生编号 姓名 专业代码 拟录取专业 初试成绩 复试成绩 总成绩 学习形式 备注
100665132310085 蔡茗涵 040100 教育学 367 84.45 76.72 全日制
第１０页，共１４页
叶宗波 085502 车辆工程 72.64 全日制 免初试
"""

        records = parse_records_from_text(text)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["person_name"], "蔡茗涵")
        self.assertEqual(records[1]["person_name"], "叶宗波")


if __name__ == "__main__":
    unittest.main()
