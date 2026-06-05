import importlib.util
import unittest
from pathlib import Path


class Batch250SdauAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch250_parses_sdau_pdf_table_rows(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch250_sdau_admission")
        self.assertIsNotNone(spec, "batch250 curation module should exist")

        from scripts.one_off.official_sources.curate_batch250_sdau_admission import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch250_sdau_admission/yjsc.sdau.edu.cn/c1907eda81bf9a1b.pdf"
            )
        )

        self.assertEqual(len(rows), 2266)
        self.assertEqual(sum(row["school_name"] == "山东农业大学" for row in rows), 2266)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 2266)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 2266)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 2266)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "张亚军")
        self.assertEqual(first["student_id"], "104345202500661")
        self.assertEqual(first["college"], "农学院")
        self.assertEqual(first["major"], "090100")
        self.assertEqual(first["admission_major"], "作物学")
        self.assertIn("院系代码: 001", first["remarks"])
        self.assertIn("初试成绩: 375.00", first["remarks"])
        self.assertIn("复试成绩: 280.06", first["remarks"])
        self.assertIn("总成绩: 83.26", first["remarks"])

        hard_exclude_terms = (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
            "不合格",
            "名额受限",
        )
        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))

        last = rows[-1]
        self.assertEqual(last["person_name"], "李之恩")
        self.assertEqual(last["student_id"], "104345202505140")
        self.assertEqual(last["college"], "动物医学院")
        self.assertEqual(last["major"], "095200")
        self.assertEqual(last["admission_major"], "兽医")
        self.assertIn("院系代码: 021", last["remarks"])
        self.assertIn("总成绩: 60.36", last["remarks"])
        self.assertEqual(
            last["source_url"],
            "https://yjsc.sdau.edu.cn/cms/viewPdf/f7887010dce34b0a9fc8589e584200ed",
        )


if __name__ == "__main__":
    unittest.main()
