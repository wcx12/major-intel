import csv
import tempfile
import unittest
from pathlib import Path

from scripts.one_off.official_sources.curate_batch394_hust_recommendation_pdf import curate_clean_rows, is_page_number_name


class CurateBatch394HustRecommendationPdfTests(unittest.TestCase):
    def test_is_page_number_name_detects_pdf_footers_only(self):
        self.assertTrue(is_page_number_name("1/99"))
        self.assertTrue(is_page_number_name(" 99 / 99 "))
        self.assertFalse(is_page_number_name("丁世豪"))
        self.assertFalse(is_page_number_name("张三丰"))

    def test_curate_clean_rows_drops_page_number_pseudo_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "records_clean.csv"
            fieldnames = ["person_name", "school_name", "year"]
            with path.open("w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({"person_name": "丁世豪", "school_name": "华中科技大学", "year": "2024"})
                writer.writerow({"person_name": "1/99", "school_name": "华中科技大学", "year": "2024"})
                writer.writerow({"person_name": "张三丰", "school_name": "华中科技大学", "year": "2024"})

            rows = curate_clean_rows(path)

        self.assertEqual([row["person_name"] for row in rows], ["丁世豪", "张三丰"])


if __name__ == "__main__":
    unittest.main()
