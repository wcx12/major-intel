import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook


class Batch522CpuHmtAdmissionTests(unittest.TestCase):
    def test_curate_workbook_preserves_cpu_hmt_admission_fields(self):
        from scripts.one_off.official_sources.curate_batch522_cpu_2026_hmt_admission import curate_workbook

        workbook_path = Path(tempfile.gettempdir()) / "cpu_hmt_admission_test.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.append(["中国药科大学2026年面向香港、澳门、台湾地区招收研究生拟录取名单"])
        ws.append(
            [
                "考生编号",
                "姓名",
                "拟攻读学位",
                "院系所代码",
                "院系所名称",
                "专业代码",
                "专业名称",
                "学习方式",
                "初试成绩",
                "复试成绩",
                "录取总成绩",
            ]
        )
        ws.append(
            [
                "103162026000001",
                "孙毓曼",
                "硕士",
                "001",
                "药学院",
                "100701",
                "药物化学",
                "全日制",
                "124",
                "109.4",
                "233.4",
            ]
        )
        wb.save(workbook_path)

        rows = curate_workbook(workbook_path)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["school_name"], "中国药科大学")
        self.assertEqual(row["year"], 2026)
        self.assertEqual(row["document_type"], "postgraduate_admission_list")
        self.assertEqual(row["route"], "postgraduate_exam_or_admission")
        self.assertEqual(row["person_name"], "孙毓曼")
        self.assertEqual(row["student_id"], "103162026000001")
        self.assertEqual(row["college"], "药学院")
        self.assertEqual(row["major"], "药物化学")
        self.assertEqual(row["admission_major"], "药物化学")
        self.assertIn("degree 硕士", row["remarks"])
        self.assertIn("college_code 001", row["remarks"])
        self.assertIn("major_code 100701", row["remarks"])
        self.assertIn("study_mode 全日制", row["remarks"])
        self.assertIn("initial_score 124", row["remarks"])
        self.assertIn("reexam_score 109.4", row["remarks"])
        self.assertIn("total_score 233.4", row["remarks"])


if __name__ == "__main__":
    unittest.main()
