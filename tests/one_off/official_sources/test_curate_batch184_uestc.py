import unittest


class UestcBatch184CurationTests(unittest.TestCase):
    def test_parse_master_line_keeps_major_scores_and_modes(self):
        from scripts.one_off.official_sources.curate_batch184_uestc import parse_master_line

        line = "106146085406211   周威     421    160       73       147     380     80.1   新一代电子信息技术（含量子技术等）    01     非全日制   定向就业"

        record = parse_master_line(
            line,
            college="信息与通信工程学院",
            source_url="https://example.edu/sice.pdf",
            title="信息与通信工程学院2026年硕士研究生招生拟录取名单（调剂）.pdf",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "周威")
        self.assertEqual(record["student_id"], "106146085406211")
        self.assertEqual(record["college"], "信息与通信工程学院")
        self.assertEqual(record["admission_major"], "新一代电子信息技术（含量子技术等）")
        self.assertIn("initial_score 421", record["remarks"])
        self.assertIn("weighted_score 80.1", record["remarks"])
        self.assertIn("direction_code 01", record["remarks"])
        self.assertIn("study_mode 非全日制", record["remarks"])
        self.assertIn("admission_category 定向就业", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_parse_master_line_keeps_optional_note(self):
        from scripts.one_off.official_sources.curate_batch184_uestc import parse_master_line

        line = "106146125212784   舒劲民   187   38   38   173   249   72.67   公共管理   01   非全日制   定向就业     退役大学生计划"

        record = parse_master_line(
            line,
            college="公共管理学院",
            source_url="https://example.edu/mpa.pdf",
            title="公共管理学院2026年MPA硕士研究生招生拟录取名单.pdf",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "舒劲民")
        self.assertEqual(record["admission_major"], "公共管理")
        self.assertIn("退役大学生计划", record["remarks"])

    def test_parse_doctor_line_keeps_major_and_category(self):
        from scripts.one_off.official_sources.curate_batch184_uestc import parse_doctor_line

        line = "106146110011124 龚应豪      申请考核    165.00   78.43   243.43   081000 信息与通信工程   不区分招生方向   11 非定向       无"

        record = parse_doctor_line(
            line,
            college="信息与通信工程学院",
            source_url="https://example.edu/doctor.pdf",
            title="2026年电子科技大学信息与通信工程学院博士研究生招生拟录取名单.pdf",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "龚应豪")
        self.assertEqual(record["student_id"], "106146110011124")
        self.assertEqual(record["admission_major"], "081000 信息与通信工程")
        self.assertIn("exam_method 申请考核", record["remarks"])
        self.assertIn("direction 不区分招生方向", record["remarks"])
        self.assertIn("admission_category 11 非定向", record["remarks"])

    def test_parse_master_line_rejects_headers(self):
        from scripts.one_off.official_sources.curate_batch184_uestc import parse_master_line

        self.assertIsNone(
            parse_master_line(
                "考生编号 姓名 初试总成绩 加权总成绩 拟录取专业名称",
                college="信息与通信工程学院",
                source_url="https://example.edu/sice.pdf",
                title="信息与通信工程学院2026年硕士研究生招生拟录取名单（调剂）.pdf",
            )
        )


if __name__ == "__main__":
    unittest.main()
