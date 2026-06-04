import unittest


class Batch325ImunDoctorPngCurationTests(unittest.TestCase):
    def test_curates_only_official_yes_rows_from_png_transcription(self):
        from scripts.one_off.official_sources.curate_batch325_imun_doctor_png import curate_records

        rows = curate_records()

        self.assertEqual(len(rows), 22)
        self.assertTrue(all(row["school_name"] == "内蒙古民族大学" for row in rows))
        self.assertTrue(all(row["year"] == 2026 for row in rows))
        self.assertTrue(all(row["route"] == "postgraduate_exam_or_admission" for row in rows))
        self.assertTrue(all(row["admission_major"] == "中药学" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "吴峰")
        self.assertEqual(first["student_id"], "1013699965")
        self.assertIn("degree_level: 博士", first["remarks"])
        self.assertIn("official_admission_status: 是", first["remarks"])

        excluded_names = {row["person_name"] for row in rows}
        self.assertNotIn("曹明未", excluded_names)
        self.assertNotIn("娜琴", excluded_names)
        self.assertNotIn("朱江", excluded_names)

        flattened_status_fields = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("remarks", "quality_flags"))
            for row in rows
        )
        for bad_fragment in ("是否拟录取: 否", "admission_status: 否", "放弃", "拟不录取", "不予录取"):
            self.assertNotIn(bad_fragment, flattened_status_fields)


if __name__ == "__main__":
    unittest.main()
