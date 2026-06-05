import unittest

from scripts.one_off.official_sources.curate_batch354_sust_admission import parse_row_tokens, curate_records


class CurateBatch354SustAdmissionTests(unittest.TestCase):
    def test_parse_exam_record_row(self):
        record = parse_row_tokens(
            [
                "曹晓雄",
                "101455000002258",
                "轻工科学与工程学院",
                "001",
                "080700",
                "动力工程及工程热物理",
                "全日制",
                "285",
                "75.33",
                "62.50",
            ],
            ranking=1,
        )

        self.assertEqual(record["person_name"], "曹晓雄")
        self.assertEqual(record["student_id"], "101455000002258")
        self.assertEqual(record["college"], "轻工科学与工程学院")
        self.assertEqual(record["major"], "080700")
        self.assertEqual(record["admission_major"], "动力工程及工程热物理")
        self.assertIn("college_code: 001", record["remarks"])
        self.assertIn("initial_score: 285", record["remarks"])
        self.assertIn("study_mode: 全日制", record["remarks"])

    def test_parse_recommendation_record_row_without_initial_score(self):
        record = parse_row_tokens(
            [
                "常希雨",
                "107085107080036",
                "轻工科学与工程学院",
                "001",
                "082200",
                "轻工技术与工程",
                "全日制",
                "85.26",
                "推免",
            ],
            ranking=11,
        )

        self.assertEqual(record["student_id"], "107085107080036")
        self.assertEqual(record["admission_major"], "轻工技术与工程")
        self.assertIn("total_score: 85.26", record["remarks"])
        self.assertIn("source_remark: 推免", record["remarks"])

    def test_curate_records_extracts_full_pdf(self):
        rows = curate_records()

        self.assertEqual(len(rows), 1959)
        self.assertEqual(rows[0]["person_name"], "曹晓雄")
        self.assertEqual(rows[0]["student_id"], "101455000002258")
        self.assertEqual(rows[-1]["person_name"], "朱子鑫")
        self.assertEqual(rows[-1]["student_id"], "107085414204872")
        self.assertEqual(rows[-1]["college"], "数学与数据科学学院")
        self.assertEqual(rows[-1]["admission_major"], "数学")


if __name__ == "__main__":
    unittest.main()
