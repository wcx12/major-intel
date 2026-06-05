import unittest
from pathlib import Path


class Batch244CtguHealthAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch244_rebuilds_ctgu_health_pdf_records(self):
        from scripts.one_off.official_sources.curate_batch244_ctgu_health_admission import curate_records

        rows = curate_records(
            pdf_paths=[
                Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch244_ctgu_health_admission/jkyxy.ctgu.edu.cn/4ac50b00f6984527.pdf"
                ),
                Path(
                    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch244_ctgu_health_admission/jkyxy.ctgu.edu.cn/9064dcb26f80dfc0.pdf"
                ),
            ]
        )

        self.assertEqual(len(rows), 102)
        self.assertEqual(sum(row["school_name"] == "三峡大学" for row in rows), 102)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 102)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 102)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"].isdigit() for row in rows))
        self.assertFalse(any(row["college"] != "健康医学院" for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))

        source_counts = {}
        for row in rows:
            source_counts[row["source_url"]] = source_counts.get(row["source_url"], 0) + 1
        self.assertEqual(
            source_counts[
                "https://jkyxy.ctgu.edu.cn/__local/B/F3/04/645C9F3068D17EA0D7B220A9E0C_BF8D961B_167C5.pdf"
            ],
            87,
        )
        self.assertEqual(
            source_counts[
                "https://jkyxy.ctgu.edu.cn/__local/4/7E/9D/5B34B462C4AACEDB21A986B4802_07C184C4_C3F9.pdf"
            ],
            15,
        )

        hard_exclude_terms = (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
        )
        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))

        first = rows[0]
        self.assertEqual(first["person_name"], "彭派派")
        self.assertEqual(first["student_id"], "110756000008127")
        self.assertEqual(first["admission_major"], "105500|药学")
        self.assertIn("考生类别: 一志愿", first["remarks"])

        self.assertEqual(rows[33]["person_name"], "任巧玲")
        self.assertEqual(rows[33]["student_id"], "110756000002164")
        self.assertIn("享受照顾政策", rows[33]["remarks"])

        second_batch_first = rows[87]
        self.assertEqual(second_batch_first["person_name"], "高远霞")
        self.assertEqual(second_batch_first["student_id"], "102856210020993")
        self.assertIn("考生类别: 调剂生", second_batch_first["remarks"])

        self.assertEqual(rows[-1]["person_name"], "耿静")
        self.assertEqual(rows[-1]["student_id"], "104236371708644")


if __name__ == "__main__":
    unittest.main()
