import unittest
from pathlib import Path


class Batch221EcuplHuelHbucmCurationTests(unittest.TestCase):
    def test_curate_batch221_keeps_official_people_rows_and_drops_pdf_watermark_fragments(self):
        from scripts.one_off.official_sources.curate_batch221_ecupl_huel_hbucm import curate_records

        rows = curate_records(
            ecupl_pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm/"
                "gs.ecupl.edu.cn/c66f3bdcd0d339a0.pdf"
            ),
            huel_html_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm/"
                "yjs.huel.edu.cn/88b89bc9f0ea6a27.htm"
            ),
            hbucm_html_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm/"
                "yjs.hbucm.edu.cn/87386a149c83bf78.htm"
            ),
        )

        self.assertEqual(len(rows), 351)
        self.assertEqual(sum(row["school_name"] == "华东政法大学" for row in rows), 349)
        self.assertEqual(sum(row["school_name"] == "河南财经政法大学" for row in rows), 1)
        self.assertEqual(sum(row["school_name"] == "湖北中医药大学" for row in rows), 1)
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["school_name"], "华东政法大学")
        self.assertEqual(first["person_name"], "闫*冰")
        self.assertEqual(first["undergraduate_school"], "安徽大学")
        self.assertEqual(first["college"], "法律学院")
        self.assertEqual(first["major"], "法学理论")
        self.assertEqual(first["admission_major"], "法学理论 法学理论")
        self.assertIn("interview_score 83", first["remarks"])

        ecupl_retired = next(row for row in rows if row["school_name"] == "华东政法大学" and row["person_name"] == "吴*菲")
        self.assertEqual(ecupl_retired["undergraduate_school"], "宁波大学")
        self.assertEqual(ecupl_retired["college"], "法律学院")
        self.assertIn("退役大学生士兵计划", ecupl_retired["remarks"])

        huel = next(row for row in rows if row["school_name"] == "河南财经政法大学")
        self.assertEqual(huel["person_name"], "杨晶莹")
        self.assertEqual(huel["major"], "125300")
        self.assertEqual(huel["admission_major"], "会计")
        self.assertIn("interview_score 92.5", huel["remarks"])

        hbucm = next(row for row in rows if row["school_name"] == "湖北中医药大学")
        self.assertEqual(hbucm["person_name"], "邓强")
        self.assertEqual(hbucm["student_id"], "105076110000029")
        self.assertEqual(hbucm["major"], "100602")
        self.assertEqual(hbucm["admission_major"], "100602 中西医结合临床")

        flattened = "\n".join(str(row) for row in rows)
        for fragment in ("可 大", "许 法", "经 政", "未 东", "禁 研", "兵计划,"):
            self.assertNotIn(fragment, flattened)


if __name__ == "__main__":
    unittest.main()
