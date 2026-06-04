import unittest


class ZjgsuBatch179CurationTests(unittest.TestCase):
    def test_parse_doctoral_line_keeps_pdf_table_row(self):
        from scripts.one_off.official_sources.curate_batch179_zjgsu import parse_doctoral_line

        line = "1    工商管理学    工商管理学院（MBA学院）    120202    企业管理         1035399933   刘文利   非定向    91.55"

        record = parse_doctoral_line(
            line,
            source_url="https://example.edu/zjgsu.pdf",
            title="浙江工商大学2026年申请考核制博士研究生拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "刘文利")
        self.assertEqual(record["student_id"], "1035399933")
        self.assertEqual(record["college"], "工商管理学院（MBA学院）")
        self.assertEqual(record["admission_major"], "120202 企业管理")
        self.assertIn("first_level_discipline 工商管理学", record["remarks"])

    def test_parse_doctoral_line_keeps_notes(self):
        from scripts.one_off.official_sources.curate_batch179_zjgsu import parse_doctoral_line

        line = "5     工商管理学     工商管理学院（MBA学院）    120202     企业管理        1035399685   唐鹏展   非定向    75.40   中外合作专项；补录"

        record = parse_doctoral_line(
            line,
            source_url="https://example.edu/zjgsu.pdf",
            title="浙江工商大学2026年申请考核制博士研究生拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "唐鹏展")
        self.assertIn("中外合作专项；补录", record["remarks"])

    def test_parse_doctoral_line_rejects_header(self):
        from scripts.one_off.official_sources.curate_batch179_zjgsu import parse_doctoral_line

        self.assertIsNone(
            parse_doctoral_line(
                "序号   一级学科         招生学院        录取专业代码                   报名号         姓名    录取类别   总成绩      备注",
                source_url="https://example.edu/zjgsu.pdf",
                title="浙江工商大学2026年申请考核制博士研究生拟录取名单",
            )
        )


if __name__ == "__main__":
    unittest.main()
