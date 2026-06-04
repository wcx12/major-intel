import unittest
from pathlib import Path


class SicnuBatch192CurationTests(unittest.TestCase):
    def test_should_drop_misparsed_third_batch_noise(self):
        from scripts.one_off.official_sources.curate_batch192_sicnu import curate_records

        rows = curate_records(
            Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch192_sicnu/records.csv")
        )

        self.assertEqual(len(rows), 1033)
        self.assertFalse(any(row["person_name"] == "209 242.8 451.8" for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

    def test_should_keep_first_and_second_batch_sources(self):
        from scripts.one_off.official_sources.curate_batch192_sicnu import curate_records

        rows = curate_records(
            Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch192_sicnu/records.csv")
        )
        sources = {row["source_url"] for row in rows}

        self.assertEqual(
            sources,
            {
                "https://yjsc.sicnu.edu.cn/files/yjs/news/639111969476232211_d.pdf",
                "https://yjsc.sicnu.edu.cn/files/yjs/news/639119533275173333_d.pdf",
            },
        )


if __name__ == "__main__":
    unittest.main()
