import unittest
from pathlib import Path


class Batch199PromisingPagesCurationTests(unittest.TestCase):
    def test_curate_records_drops_hrbcu_page_headers(self):
        from scripts.one_off.official_sources.curate_batch199_promising_pages import curate_records

        rows = curate_records(
            Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch199_promising_pages/records.csv")
        )

        self.assertEqual(len(rows), 2956)
        self.assertFalse(any(row["person_name"].startswith("第 ") and "页，共" in row["person_name"] for row in rows))
        self.assertFalse(any("哈尔滨商业大学2026年硕士研究生招生考试一志愿拟录取名单" in row["person_name"] for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

    def test_curate_records_keeps_four_official_pdf_sources(self):
        from scripts.one_off.official_sources.curate_batch199_promising_pages import curate_records

        rows = curate_records(
            Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch199_promising_pages/records.csv")
        )
        counts = {}
        for row in rows:
            counts[row["school_name"]] = counts.get(row["school_name"], 0) + 1

        self.assertEqual(
            counts,
            {
                "山西财经大学": 1380,
                "佳木斯大学": 519,
                "哈尔滨商业大学": 579,
                "青海民族大学": 478,
            },
        )


if __name__ == "__main__":
    unittest.main()
