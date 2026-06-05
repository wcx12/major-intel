import unittest
from pathlib import Path


class Batch303HquDoctoralAdmissionCurationTests(unittest.TestCase):
    def test_curates_hqu_doctoral_pdf_rows_and_multiline_notes(self):
        from scripts.one_off.official_sources.curate_batch303_hqu_doctoral_admission import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch303_hqu_admission/"
                "grs.hqu.edu.cn/hqu_2026_doctoral_admission_second_batch.pdf"
            )
        )

        self.assertEqual(len(rows), 146)
        self.assertTrue(all(row["school_name"] == "华侨大学" for row in rows))
        self.assertTrue(all(row["year"] == 2026 for row in rows))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in rows))
        self.assertTrue(all(row["route"] == "postgraduate_exam_or_admission" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "曹佐相")
        self.assertEqual(first["student_id"], "1038599819")
        self.assertEqual(first["college"], "哲学与社会发展学院")
        self.assertEqual(first["admission_major"], "哲学")
        self.assertIn("supervisor: 许斗斗", first["remarks"])
        self.assertIn("interview_score: 86.68", first["remarks"])
        self.assertIn("exam_method: 申请审核", first["remarks"])

        multiline_major = next(row for row in rows if row["ranking"] == "18")
        self.assertEqual(multiline_major["admission_major"], "华侨华人与区域国别研究")
        self.assertEqual(multiline_major["person_name"], "杨雯旭")
        self.assertIn("research_direction: 不区分研究方向", multiline_major["remarks"])

        multiline_note = next(row for row in rows if row["ranking"] == "92")
        self.assertEqual(multiline_note["person_name"], "万妍君")
        self.assertEqual(multiline_note["student_id"], "1038599660")
        self.assertIn("note: 国际产学研用联培博士计划", multiline_note["remarks"])

        last = rows[-1]
        self.assertEqual(last["ranking"], "146")
        self.assertEqual(last["person_name"], "郁航")
        self.assertEqual(last["admission_major"], "旅游管理")

        flattened = "\n".join(str(row) for row in rows)
        for bad_fragment in (
            "第 1 页",
            "学院代码",
            "录取考",
            "生姓名",
            "拟不录取",
            "不予录取",
            "候补",
            "放弃拟录取",
        ):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
