import unittest

from scripts.one_off.official_sources.curate_batch350_bisu_admission import parse_row_tokens, curate_records


class CurateBatch350BisuAdmissionTests(unittest.TestCase):
    def test_parse_row_tokens_handles_split_name_and_candidate_id(self):
        record = parse_row_tokens(
            ["汤*", "100315050201113", "414", "95.55", "87.90", "英语学院", "英语语言文学"],
            ranking=1,
        )

        self.assertEqual(record["person_name"], "汤*")
        self.assertEqual(record["student_id"], "100315050201113")
        self.assertEqual(record["college"], "英语学院")
        self.assertEqual(record["admission_major"], "英语语言文学")
        self.assertIn("initial_score: 414", record["remarks"])
        self.assertIn("official_admission_status: 拟录取", record["remarks"])

    def test_parse_row_tokens_handles_merged_name_and_candidate_id(self):
        record = parse_row_tokens(
            ["闫*宇100315050201062", "418", "89.54", "85.98", "英语学院", "英语语言文学"],
            ranking=3,
        )

        self.assertEqual(record["person_name"], "闫*宇")
        self.assertEqual(record["student_id"], "100315050201062")
        self.assertEqual(record["college"], "英语学院")
        self.assertEqual(record["admission_major"], "英语语言文学")

    def test_curate_records_extracts_full_pdf_and_special_plan(self):
        rows = curate_records()

        self.assertEqual(len(rows), 428)
        self.assertEqual(rows[0]["person_name"], "汤*")
        self.assertEqual(rows[0]["student_id"], "100315050201113")
        self.assertEqual(rows[-1]["person_name"], "史*同")
        self.assertEqual(rows[-1]["student_id"], "100315025100001")
        self.assertEqual(rows[-1]["college"], "经济学院")
        self.assertEqual(rows[-1]["admission_major"], "金融")
        self.assertIn("special_plan: 退役大学生士兵专项计划", rows[-1]["remarks"])


if __name__ == "__main__":
    unittest.main()
