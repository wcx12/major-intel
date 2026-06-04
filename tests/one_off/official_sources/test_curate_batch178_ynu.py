import unittest


class YnuBatch178CurationTests(unittest.TestCase):
    def test_parse_application_line_keeps_complete_candidate_row(self):
        from scripts.one_off.official_sources.curate_batch178_ynu import parse_application_line

        line = "001      经济学院   020100   理论经济学             人口与劳动力市场问题    99956   马鹏    86.93"

        record = parse_application_line(
            line,
            source_url="https://example.edu/application.pdf",
            title="云南大学2026年博士研究生“申请-考核”制（第一批次）拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "马鹏")
        self.assertEqual(record["student_id"], "99956")
        self.assertEqual(record["college"], "001 经济学院")
        self.assertEqual(record["admission_major"], "020100 理论经济学")
        self.assertIn("人口与劳动力市场问题", record["remarks"])

    def test_parse_application_line_rejects_wrapped_fragment(self):
        from scripts.one_off.official_sources.curate_batch178_ynu import parse_application_line

        line = "009   国际关系研究院·南亚东南亚研究院   0302Z2   区域国别研究                安全与发展"

        self.assertIsNone(
            parse_application_line(
                line,
                source_url="https://example.edu/application.pdf",
                title="云南大学2026年博士研究生“申请-考核”制（第一批次）拟录取名单",
            )
        )

    def test_parse_master_phd_line_keeps_major_code_with_letter(self):
        from scripts.one_off.official_sources.curate_batch178_ynu import parse_master_phd_line

        line = "028         农学院            付汉涛 12023128007        作物学            0710Z2     保护生物学      黄斌全    77.26"

        record = parse_master_phd_line(
            line,
            source_url="https://example.edu/master-phd.pdf",
            title="云南大学2026年硕博连读拟录取名单",
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "付汉涛")
        self.assertEqual(record["student_id"], "12023128007")
        self.assertEqual(record["college"], "028 农学院")
        self.assertEqual(record["undergraduate_major"], "作物学")
        self.assertEqual(record["admission_major"], "0710Z2 保护生物学")


if __name__ == "__main__":
    unittest.main()
