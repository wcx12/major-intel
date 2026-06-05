import importlib
import unittest


def _load_curate_records():
    module_name = "scripts.one_off.official_sources.curate_nufe_2026_doctor_supp_image"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name:
            raise AssertionError("NUFE 2026 doctoral supplement image curator is missing") from exc
        raise
    return module.curate_records


class Nufe2026DoctorSupplementImageTests(unittest.TestCase):
    def test_curates_only_official_admitted_row_from_png_transcription(self):
        rows = _load_curate_records()()

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["school_name"], "南京财经大学")
        self.assertEqual(row["year"], 2026)
        self.assertEqual(row["document_type"], "postgraduate_admission_list")
        self.assertEqual(row["route"], "postgraduate_exam_or_admission")
        self.assertEqual(row["person_name"], "周*帆")
        self.assertEqual(row["student_id"], "10327*******062")
        self.assertEqual(row["ranking"], "2")
        self.assertEqual(row["source_url"], "https://yjsc.nufe.edu.cn/__local/A/C7/31/38635DF087259669397CAD93EEC_C1C13246_111C3.png")
        self.assertFalse(row["needs_review"])

        self.assertIn("degree_level 博士", row["remarks"])
        self.assertIn("admission_method 普通招考递补", row["remarks"])
        self.assertIn("initial_score 214.5", row["remarks"])
        self.assertIn("reexam_score 88.8", row["remarks"])
        self.assertIn("composite_score 76.690", row["remarks"])
        self.assertIn("official_admission_status 拟录取", row["remarks"])
        self.assertIn("source_image_transcribed true", row["remarks"])

        flattened = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("person_name", "student_id", "remarks"))
            for row in rows
        )
        self.assertNotIn("李*林", flattened)
        self.assertNotIn("放弃拟录取", flattened)


if __name__ == "__main__":
    unittest.main()
