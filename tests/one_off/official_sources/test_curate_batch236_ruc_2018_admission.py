import unittest
from pathlib import Path


class Batch236RucAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch236_rebuilds_ruc_2018_admission_records(self):
        from scripts.one_off.official_sources.curate_batch236_ruc_2018_admission import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch236_ruc_2018_admission"
            )
        )

        self.assertEqual(len(rows), 2804)
        self.assertEqual(sum(row["school_name"] == "中国人民大学" for row in rows), 2804)
        self.assertEqual(sum(row["year"] == 2018 for row in rows), 2804)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 2804)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 2804)
        self.assertFalse(any(row["document_type"] == "recommendation_exemption_list" for row in rows))
        self.assertEqual(len({(row["source_url"], row["student_id"], row["person_name"]) for row in rows}), 2804)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        first_batch = [
            row for row in rows if row["source_url"] == "https://grs.ruc.edu.cn/info/1083/1273.htm"
        ]
        second_batch = [
            row for row in rows if row["source_url"] == "https://grs.ruc.edu.cn/info/1083/1348.htm"
        ]
        self.assertEqual(len(first_batch), 2530)
        self.assertEqual(len(second_batch), 274)

        first = rows[0]
        self.assertEqual(first["person_name"], "曹一飞")
        self.assertEqual(first["student_id"], "100028110001651")
        self.assertEqual(first["college"], "哲学院")
        self.assertEqual(first["admission_major"], "马克思主义哲学")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("research_direction 不区分研究方向", first["remarks"])
        self.assertIn("study_mode 全日制", first["remarks"])
        self.assertIn("initial_score 408", first["remarks"])
        self.assertIn("weighted_score 83.82", first["remarks"])

        second_first = second_batch[0]
        self.assertEqual(second_first["person_name"], "周润秋")
        self.assertEqual(second_first["college"], "财政金融学院（EMBA）")
        self.assertEqual(second_first["admission_major"], "工商管理（专业学位）")
        self.assertIn("study_mode 非全日制", second_first["remarks"])

        last = rows[-1]
        self.assertEqual(last["person_name"], "苟晓莉")
        self.assertEqual(last["student_id"], "100028512922969")
        self.assertIn("research_direction 新疆定向", last["remarks"])
        self.assertIn("少数民族骨干计划", last["remarks"])


if __name__ == "__main__":
    unittest.main()
