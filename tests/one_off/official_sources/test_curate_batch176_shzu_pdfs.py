import unittest


class ShzuBatch176CurationTests(unittest.TestCase):
    def test_parse_pdf_line_keeps_explicit_admission_row(self):
        from scripts.one_off.official_sources.curate_batch176_shzu_pdfs import parse_pdf_line

        line = (
            "1    107596000000928   马瑞珣   085400   电子信息   不区分研究方向   "
            "67   74   144   95    380   156.29   76.86   1     61    "
            "数据库系统原理    71   软件工程     合格            拟录取"
        )

        record = parse_pdf_line(
            line,
            school_name="石河子大学",
            college="信息科学与技术学院",
            source_url="https://example.edu/a.pdf",
            title="信息科学与技术学院电子信息全日制普通计划复试情况汇总表",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "马瑞珣")
        self.assertEqual(record["student_id"], "107596000000928")
        self.assertEqual(record["admission_major"], "085400 电子信息")

    def test_parse_pdf_line_rejects_not_admitted_row(self):
        from scripts.one_off.official_sources.curate_batch176_shzu_pdfs import parse_pdf_line

        line = (
            "62   107596000002042   石义帅   085400   电子信息   不区分研究方向   "
            "58   71   88    52    269   155.57   63.39   62      "
            "合格            按总成绩排名，拟不录取"
        )

        record = parse_pdf_line(
            line,
            school_name="石河子大学",
            college="信息科学与技术学院",
            source_url="https://example.edu/a.pdf",
            title="信息科学与技术学院电子信息全日制普通计划复试情况汇总表",
        )

        self.assertIsNone(record)

    def test_parse_zfxy_row_uses_college_opinion(self):
        from scripts.one_off.official_sources.curate_batch176_shzu_pdfs import parse_zfxy_row

        row = [
            "1",
            "105206666609143",
            "李穹翮",
            "030300",
            "社会学",
            "",
            "63",
            "55",
            "108",
            "122",
            "348",
            "168.4",
            "75.44",
            "1",
            "64",
            "社会学概论",
            "78",
            "社会政策",
            "合格",
            "拟录取",
            "",
        ]

        record = parse_zfxy_row(
            row,
            source_url="https://example.edu/zfxy.htm",
            title="石河子大学法学院2026年硕士研究生调剂复试情况公示（第二批次）",
            table_title="石河子大学法学院 2026 年硕士研究生复试情况汇总表（学术学位）",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "李穹翮")
        self.assertEqual(record["admission_major"], "030300 社会学")

        row[19] = "不予录取"
        self.assertIsNone(
            parse_zfxy_row(
                row,
                source_url="https://example.edu/zfxy.htm",
                title="石河子大学法学院2026年硕士研究生调剂复试情况公示（第二批次）",
                table_title="石河子大学法学院 2026 年硕士研究生复试情况汇总表（学术学位）",
            )
        )


if __name__ == "__main__":
    unittest.main()
