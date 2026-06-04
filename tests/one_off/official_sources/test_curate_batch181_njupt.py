import unittest


class NjuptBatch181CurationTests(unittest.TestCase):
    def test_parse_doctoral_line_keeps_masked_name_and_identity_tail(self):
        from scripts.one_off.official_sources.curate_batch181_njupt import parse_doctoral_line

        line = "35   102936199900039    001X   杨*宇    申请考核    光学工程     电子与光学工程学院、柔性电子（未来技术）学院    光电信息工程"

        record = parse_doctoral_line(
            line,
            source_url="http://example.edu/njupt.pdf",
            title="2026年博士研究生拟录取名单（第一批次）",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "杨*宇")
        self.assertEqual(record["student_id"], "102936199900039")
        self.assertEqual(record["ranking"], "35")
        self.assertEqual(record["major"], "光学工程")
        self.assertEqual(record["college"], "电子与光学工程学院、柔性电子（未来技术）学院")
        self.assertEqual(record["admission_major"], "光电信息工程")
        self.assertIn("identity_tail 001X", record["remarks"])
        self.assertIn("exam_method 申请考核", record["remarks"])
        self.assertFalse(record["needs_review"])

    def test_parse_doctoral_line_keeps_final_note(self):
        from scripts.one_off.official_sources.curate_batch181_njupt import parse_doctoral_line

        line = "212     20269900078      1913   张*海    申请考核    电子信息     计算机学院软件学院网络空间安全学院   电子信息    少民骨干"

        record = parse_doctoral_line(
            line,
            source_url="http://example.edu/njupt.pdf",
            title="2026年博士研究生拟录取名单（第一批次）",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "张*海")
        self.assertEqual(record["student_id"], "20269900078")
        self.assertEqual(record["admission_major"], "电子信息")
        self.assertIn("少民骨干", record["remarks"])

    def test_parse_doctoral_line_rejects_non_rows(self):
        from scripts.one_off.official_sources.curate_batch181_njupt import parse_doctoral_line

        self.assertIsNone(
            parse_doctoral_line(
                "序号   考生编号/学号   身份证号（后四位） 考生姓名",
                source_url="http://example.edu/njupt.pdf",
                title="2026年博士研究生拟录取名单（第一批次）",
            )
        )
        self.assertIsNone(
            parse_doctoral_line(
                "南 京 邮 电 大 学",
                source_url="http://example.edu/njupt.pdf",
                title="2026年博士研究生拟录取名单（第一批次）",
            )
        )


if __name__ == "__main__":
    unittest.main()
