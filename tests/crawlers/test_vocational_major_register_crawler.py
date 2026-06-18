import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.crawlers.vocational_major_register_crawler import (
    build_unique_major_rows,
    normalize_register_item,
    read_failure_pages,
    register_url,
    repair_vocational_major_register_run,
)


class VocationalMajorRegisterCrawlerTests(unittest.TestCase):
    def test_register_url_includes_year_page_and_optional_province(self):
        url = register_url(year="2026", page=2, page_size=50, province="BJ")

        self.assertIn("year=2026", url)
        self.assertIn("page=2", url)
        self.assertIn("pageSize=50", url)
        self.assertIn("province=BJ", url)

    def test_normalize_register_item_preserves_official_scope(self):
        row = normalize_register_item(
            {
                "prov_name": "北京市",
                "major_code": "510111",
                "major_name": "低空安全与技术",
                "school_code": "4111010853",
                "school_name": "北京工业职业技术学院",
                "school_system": "3",
                "remark": None,
            },
            year="2026",
            source_url="https://zwfw.moe.gov.cn/eduSearch/api/major-register?year=2026&page=1&pageSize=50",
            captured_at="2026-06-12T00:00:00+08:00",
        )

        self.assertTrue(row["record_id"].startswith("vocational_major:"))
        self.assertEqual(row["major_level"], "高职专科")
        self.assertEqual(row["source_level"], "A")
        self.assertEqual(row["major_code"], "510111")
        self.assertEqual(row["major_name"], "低空安全与技术")
        self.assertEqual(row["remark"], "")

    def test_build_unique_major_rows_deduplicates_by_year_code_name(self):
        records = [
            {
                "year": "2026",
                "province_name": "北京市",
                "major_code": "510111",
                "major_name": "低空安全与技术",
                "school_name": "北京工业职业技术学院",
            },
            {
                "year": "2026",
                "province_name": "河北省",
                "major_code": "510111",
                "major_name": "低空安全与技术",
                "school_name": "河北样例职业学院",
            },
        ]

        rows = build_unique_major_rows(records)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["record_count"], 2)
        self.assertEqual(rows[0]["province_count"], 2)
        self.assertEqual(rows[0]["school_count"], 2)
        self.assertIn("北京工业职业技术学院", rows[0]["sample_schools"])

    def test_read_failure_pages_deduplicates_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "failures.jsonl"
            path.write_text('{"page": 3, "error": "x"}\n{"page": 3, "error": "y"}\n{"page": 5}\n', encoding="utf-8")

            self.assertEqual(read_failure_pages(path), [3, 5])

    def test_repair_vocational_major_register_run_merges_failed_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            raw_dir = root / "raw"
            processed_dir = root / "processed"
            logs_dir = root / "logs"
            reports_dir = root / "reports"
            processed_dir.mkdir()
            logs_dir.mkdir()
            base_run_id = "base"
            base_record = normalize_register_item(
                {
                    "prov_name": "北京市",
                    "major_code": "510111",
                    "major_name": "低空安全与技术",
                    "school_code": "4111010853",
                    "school_name": "北京工业职业技术学院",
                    "school_system": "3",
                },
                year="2026",
                source_url=register_url(year="2026", page=1, page_size=50),
                captured_at="2026-06-12T00:00:00+08:00",
            )
            (processed_dir / f"vocational_major_records_{base_run_id}.jsonl").write_text(
                json.dumps(base_record, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (logs_dir / f"{base_run_id}_manifest.json").write_text(
                json.dumps({"total_reported": 2, "page_count": 2}, ensure_ascii=False),
                encoding="utf-8",
            )

            def fake_fetch_register_page(**kwargs):
                self.assertEqual(kwargs["page"], 2)
                return {
                    "success": True,
                    "data": {
                        "list": [
                            {
                                "prov_name": "河北省",
                                "major_code": "510111",
                                "major_name": "低空安全与技术",
                                "school_code": "4113010000",
                                "school_name": "河北样例职业学院",
                                "school_system": "3",
                                "remark": None,
                            }
                        ]
                    },
                }

            with patch("major_intel.crawlers.vocational_major_register_crawler.fetch_register_page", fake_fetch_register_page):
                manifest = repair_vocational_major_register_run(
                    year="2026",
                    base_run_id=base_run_id,
                    raw_dir=raw_dir,
                    processed_dir=processed_dir,
                    logs_dir=logs_dir,
                    reports_dir=reports_dir,
                    run_id="repaired",
                    pages=[2],
                )

            self.assertEqual(manifest["record_count"], 2)
            self.assertEqual(manifest["failure_count"], 0)
            output_path = processed_dir / "vocational_major_records_repaired.jsonl"
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual({row["province_name"] for row in rows}, {"北京市", "河北省"})


if __name__ == "__main__":
    unittest.main()
