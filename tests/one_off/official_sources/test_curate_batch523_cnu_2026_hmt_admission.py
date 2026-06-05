import unittest


class Batch523CnuHmtAdmissionTests(unittest.TestCase):
    def test_curate_pdf_text_extracts_cnu_hmt_admission_row(self):
        from scripts.one_off.official_sources.curate_batch523_cnu_2026_hmt_admission import curate_pdf_text

        text = (
            "考生编号 姓名 初试总成绩 复试总成绩 录取成绩 录取学习方式\n"
            "100282026027001 陈思睿 108 76.96 73.98 全日制\n"
            "首都师范大学2026年面向港澳台地区招收硕士研究生拟录取名单"
        )

        rows = curate_pdf_text(text)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["school_name"], "首都师范大学")
        self.assertEqual(row["year"], 2026)
        self.assertEqual(row["document_type"], "postgraduate_admission_list")
        self.assertEqual(row["route"], "postgraduate_exam_or_admission")
        self.assertEqual(row["student_id"], "100282026027001")
        self.assertEqual(row["person_name"], "陈思睿")
        self.assertIn("initial_score 108", row["remarks"])
        self.assertIn("reexam_score 76.96", row["remarks"])
        self.assertIn("admission_score 73.98", row["remarks"])
        self.assertIn("study_mode 全日制", row["remarks"])


if __name__ == "__main__":
    unittest.main()
