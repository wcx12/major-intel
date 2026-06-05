import unittest
from pathlib import Path


class Batch270bWestlakeAdmissionPdfCurationTests(unittest.TestCase):
    def test_curate_batch270b_splits_westlake_pdf_columns(self):
        from scripts.one_off.official_sources.curate_batch270b_westlake_admission_pdf import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch270b_westlake_admission_pdf/"
                "www.westlake.edu.cn/8f090f22e4a1ff52.pdf"
            )
        )

        self.assertEqual(len(rows), 168)
        self.assertEqual(sum(row["school_name"] == "西湖大学" for row in rows), 168)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 168)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 168)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 168)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(" " in row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "***277")
        self.assertEqual(first["person_name"], "郭*源")
        self.assertEqual(first["student_id"], "41……018")
        self.assertEqual(first["college"], "工学院")
        self.assertEqual(first["admission_major"], "材料科学与工程")
        self.assertIn("面试成绩: 90.20", first["remarks"])
        self.assertIn("学制: 4", first["remarks"])

        remark_row = next(row for row in rows if row["ranking"] == "***020")
        self.assertEqual(remark_row["person_name"], "林*傲")
        self.assertIn("改本科起点", remark_row["remarks"])

        last = rows[-1]
        self.assertEqual(last["person_name"], "潘*泽")
        self.assertEqual(last["student_id"], "33……072")
        self.assertEqual(last["college"], "医学院")
        self.assertEqual(last["admission_major"], "生物学")

        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("person_name", "student_id", "remarks", "admission_major"))
            for row in rows
        )
        hard_exclude_terms = ("拟不录取", "不予录取", "不合格", "候补", "缺考", "放弃", "未录取")
        self.assertFalse(any(term in joined for term in hard_exclude_terms))


if __name__ == "__main__":
    unittest.main()
