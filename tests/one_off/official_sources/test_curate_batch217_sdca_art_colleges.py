import unittest
from pathlib import Path


class Batch217SdcaArtCollegesCurationTests(unittest.TestCase):
    def test_curate_msxy_pdf_drops_headers_and_keeps_recommended_rows(self):
        from scripts.one_off.official_sources.curate_batch217_sdca_art_colleges import curate_msxy_pdf

        rows = curate_msxy_pdf(
            Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch217_sdca_art_colleges/"
                "msxy.sdca.edu.cn/5e6220db16b839ae.pdf"
            )
        )

        self.assertEqual(len(rows), 15)
        self.assertEqual({row["school_name"] for row in rows}, {"山东艺术学院"})
        self.assertEqual({str(row["year"]) for row in rows}, {"2026"})
        self.assertEqual({row["document_type"] for row in rows}, {"recommendation_exemption_list"})
        self.assertEqual({row["route"] for row in rows}, {"recommendation_exemption"})
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["student_id"], "202202031")
        self.assertEqual(first["person_name"], "臧晓宇")
        self.assertEqual(first["college"], "美术学院")
        self.assertEqual(first["undergraduate_major"], "130402 绘画")
        self.assertIn("recommendation_status 是", first["remarks"])
        self.assertIn("major_group 油画第一工作室", first["remarks"])

        last = rows[-1]
        self.assertEqual(last["ranking"], "15")
        self.assertEqual(last["person_name"], "田欣乐")
        self.assertEqual(last["undergraduate_major"], "130401 美术学")

        flattened = "\n".join(str(row) for row in rows)
        self.assertNotIn("是否推荐", flattened)
        self.assertNotIn("实验艺术, 员", flattened)
        self.assertNotIn("候补", flattened)


if __name__ == "__main__":
    unittest.main()
