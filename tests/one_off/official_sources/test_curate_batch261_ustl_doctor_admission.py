import importlib.util
import unittest
from pathlib import Path


class Batch261UstlDoctorAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch261_filters_repeated_pdf_header_rows(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch261_ustl_doctor_admission")
        self.assertIsNotNone(spec, "batch261 curation module should exist")

        from scripts.one_off.official_sources.curate_batch261_ustl_doctor_admission import curate_records

        rows = curate_records(
            input_csv=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch261_ustl_doctor_admission/"
                "records.csv"
            )
        )

        self.assertEqual(len(rows), 69)
        self.assertEqual(sum(row["school_name"] == "辽宁科技大学" for row in rows), 69)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 69)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 69)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 69)
        self.assertFalse(any(row["person_name"] == "考生姓名 性别 导师编号 导师姓名" for row in rows))
        self.assertFalse(any(row["student_id"] == "考生编号" for row in rows))
        self.assertFalse(any(row["college"] == "学院" for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "董*玮")
        self.assertEqual(first["student_id"], "101466101460069")
        self.assertEqual(first["college"], "材料与冶金学院")
        self.assertEqual(first["major"], "材料科学与工程")

        last = rows[-1]
        self.assertEqual(last["ranking"], "69")
        self.assertEqual(last["person_name"], "李*阳")
        self.assertEqual(last["student_id"], "101466111006058")
        self.assertEqual(last["college"], "化学工程学院")
        self.assertEqual(last["major"], "低碳技术与工程")


if __name__ == "__main__":
    unittest.main()
