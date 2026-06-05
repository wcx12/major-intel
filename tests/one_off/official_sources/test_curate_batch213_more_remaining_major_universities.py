import unittest
from pathlib import Path


class Batch213MoreRemainingMajorUniversitiesCurationTests(unittest.TestCase):
    def test_curate_whut_pdf_sets_2026_and_keeps_admitted_rows(self):
        from scripts.one_off.official_sources.curate_batch213_more_remaining_major_universities import curate_whut_pdf

        rows = curate_whut_pdf(
            Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch213_more_remaining_major_universities/"
                "stle.whut.edu.cn/1f294b0c26383986.pdf"
            )
        )

        self.assertEqual(len(rows), 89)
        self.assertEqual({row["school_name"] for row in rows}, {"武汉理工大学"})
        self.assertEqual({str(row["year"]) for row in rows}, {"2026"})
        self.assertEqual({row["document_type"] for row in rows}, {"incoming_recommendation_admission_list"})
        self.assertEqual({row["route"] for row in rows}, {"recommendation_exemption"})
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "刘俊杰")
        self.assertEqual(first["college"], "交通与物流工程学院")
        self.assertEqual(first["major"], "082300")
        self.assertEqual(first["admission_major"], "082300 交通运输工程")
        self.assertIn("admission_type 直博生", first["remarks"])
        self.assertIn("list_status 拟录取", first["remarks"])

        last = rows[-1]
        self.assertEqual(last["ranking"], "89")
        self.assertEqual(last["person_name"], "李丽")
        self.assertEqual(last["admission_major"], "125604 物流工程与管理")

        flattened = "\n".join(str(row) for row in rows)
        self.assertNotIn("复试不合格", flattened)
        self.assertNotIn("缺考", flattened)
        self.assertNotIn("候补", flattened)


if __name__ == "__main__":
    unittest.main()
