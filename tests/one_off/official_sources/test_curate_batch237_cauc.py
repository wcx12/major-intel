import re
import unittest
from pathlib import Path


class Batch237CaucCurationTests(unittest.TestCase):
    def test_curate_batch237_rebuilds_cauc_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch237_cauc import curate_records

        rows = curate_records(
            raw_dir=Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch237_cauc")
        )

        self.assertEqual(len(rows), 1439)
        self.assertEqual(sum(row["school_name"] == "中国民航大学" for row in rows), 1439)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 1439)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 1422)
        self.assertEqual(sum(row["document_type"] == "incoming_recommendation_admission_list" for row in rows), 17)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))
        self.assertFalse(
            any(
                re.search(
                    "进入复试名单|拟不录取|不予录取|是否拟录取[:：]?\\s*否|放弃复试|复试不合格|缺考|候补",
                    " ".join(str(value) for value in row.values()),
                )
                for row in rows
            )
        )

        admission_rows = [row for row in rows if row["document_type"] == "postgraduate_admission_list"]
        recommendation_rows = [
            row for row in rows if row["document_type"] == "incoming_recommendation_admission_list"
        ]
        self.assertEqual(len({(row["source_url"], row["ranking"], row["person_name"]) for row in rows}), 1439)

        first = admission_rows[0]
        self.assertEqual(first["person_name"], "肖芯蕊")
        self.assertEqual(first["student_id"], "100595100590015")
        self.assertEqual(first["college"], "001")
        self.assertEqual(first["admission_major"], "083700")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("admission_status 拟录取", first["remarks"])
        self.assertIn("study_mode 全日制", first["remarks"])
        self.assertIn("reexam_score 91.50", first["remarks"])
        self.assertIn("total_score 91.50", first["remarks"])

        soldier_plan = [row for row in admission_rows if row["ranking"] == "119"][0]
        self.assertEqual(soldier_plan["person_name"], "朱永昌")
        self.assertIn("退役大学生士兵计划", soldier_plan["remarks"])

        first_recommendation = recommendation_rows[0]
        self.assertEqual(first_recommendation["person_name"], "肖芯蕊")
        self.assertEqual(first_recommendation["student_id"], "1401**********482X")
        self.assertEqual(first_recommendation["undergraduate_school"], "中国民航大学")
        self.assertEqual(first_recommendation["college"], "001【安全科学与工程学院】")
        self.assertEqual(first_recommendation["admission_major"], "083700【安全科学与工程】")
        self.assertEqual(first_recommendation["ranking"], "1")
        self.assertIn("reexam_score 91.50", first_recommendation["remarks"])

        last = recommendation_rows[-1]
        self.assertEqual(last["person_name"], "唐羚棋")
        self.assertEqual(last["admission_major"], "055100【翻译】")


if __name__ == "__main__":
    unittest.main()
