import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.rysxai_civil_service_crawler import (
    FetchError,
    RequestsDetailFetcher,
    crawl_id_range,
    normalize_role,
    read_completed_ids,
    write_csv_from_jsonl,
)


DETAIL_PAYLOAD = {
    "code": "SUCCESS",
    "detail": "成功",
    "data": {
        "id": 41524,
        "sheet_type": "中央国家行政机关参照公务员法管理事业单位",
        "year": 2026,
        "department_code": "116112",
        "department_name": "生态环境部西北核与辐射安全监督站",
        "job_name": "核与辐射安全监督岗位一级主任科员及以下",
        "position_code": "400110112001",
        "plan_num": 1,
        "apply_num": 132,
        "ratio": 132.0,
        "profession": "核工程类、核物理、放射化学、核电技术与控制工程及其他相关专业。",
        "education_level": "本科及以上",
        "phone": ["0931-8682811"],
        "wuwei_table": [
            {"name": "岗位质量", "value": 4.1, "avg": 4.02, "percent": 69}
        ],
    },
}


class RysxaiCivilServiceCrawlerTests(unittest.TestCase):
    def test_normalize_role_keeps_detail_fields_and_source_metadata(self):
        record = normalize_role(
            DETAIL_PAYLOAD,
            fetched_at="2026-05-19T18:00:00+08:00",
            source_url="https://api.rysxai.cn/api/ry_education/civil_servant/info/?id=41524",
        )

        self.assertEqual(record["schema_version"], "rysxai_civil_service_role/v1")
        self.assertEqual(record["fetched_at"], "2026-05-19T18:00:00+08:00")
        self.assertEqual(record["source"]["source_url"].split("?id=")[1], "41524")
        self.assertEqual(record["role"]["id"], 41524)
        self.assertEqual(record["role"]["year"], 2026)
        self.assertEqual(record["role"]["department_name"], "生态环境部西北核与辐射安全监督站")
        self.assertEqual(record["role"]["phone"], ["0931-8682811"])

    def test_read_completed_ids_ignores_blank_and_invalid_lines(self):
        with TemporaryDirectory() as temp_dir:
            jsonl_path = Path(temp_dir) / "roles.jsonl"
            jsonl_path.write_text(
                "\n"
                + json.dumps({"role": {"id": 1}}, ensure_ascii=False)
                + "\nnot-json\n"
                + json.dumps({"role": {"id": 2}}, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )

            self.assertEqual(read_completed_ids(jsonl_path), {1, 2})

    def test_crawl_id_range_skips_existing_records_and_logs_failures(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "roles.jsonl"
            failures_path = Path(temp_dir) / "failures.jsonl"
            output_path.write_text(
                json.dumps({"role": {"id": 10}}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            calls = []

            def fake_fetch(role_id, timeout_seconds=20):
                calls.append(role_id)
                if role_id == 12:
                    raise FetchError("boom", status_code=500)
                payload = json.loads(json.dumps(DETAIL_PAYLOAD))
                payload["data"]["id"] = role_id
                return payload

            summary = crawl_id_range(
                start_id=10,
                end_id=13,
                output_path=output_path,
                failures_path=failures_path,
                delay_seconds=0,
                jitter_seconds=0,
                fetcher=fake_fetch,
                sleeper=lambda seconds: None,
            )

            self.assertEqual(calls, [11, 12, 13])
            self.assertEqual(summary.requested_ids, 4)
            self.assertEqual(summary.skipped_existing, 1)
            self.assertEqual(summary.fetched, 2)
            self.assertEqual(summary.failed, 1)
            self.assertEqual(read_completed_ids(output_path), {10, 11, 13})

            failure = json.loads(failures_path.read_text(encoding="utf-8").strip())
            self.assertEqual(failure["id"], 12)
            self.assertEqual(failure["status_code"], 500)

    def test_write_csv_from_jsonl_flattens_role_fields(self):
        with TemporaryDirectory() as temp_dir:
            jsonl_path = Path(temp_dir) / "roles.jsonl"
            csv_path = Path(temp_dir) / "roles.csv"
            record = normalize_role(
                DETAIL_PAYLOAD,
                fetched_at="2026-05-19T18:00:00+08:00",
                source_url="https://api.rysxai.cn/api/ry_education/civil_servant/info/?id=41524",
            )
            jsonl_path.write_text(
                json.dumps(record, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            row_count = write_csv_from_jsonl(jsonl_path, csv_path)

            self.assertEqual(row_count, 1)
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["id"], "41524")
            self.assertEqual(rows[0]["phone"], "0931-8682811")
            self.assertIn("岗位质量", rows[0]["wuwei_table"])

    def test_requests_detail_fetcher_reuses_session_and_maps_http_errors(self):
        class FakeResponse:
            status_code = 200

            def json(self):
                return DETAIL_PAYLOAD

        class FakeSession:
            def __init__(self):
                self.calls = []

            def get(self, url, timeout, headers):
                self.calls.append((url, timeout, headers))
                return FakeResponse()

        session = FakeSession()
        fetcher = RequestsDetailFetcher(session=session)

        payload = fetcher(41524, timeout_seconds=11)

        self.assertEqual(payload["data"]["id"], 41524)
        self.assertIn("id=41524", session.calls[0][0])
        self.assertEqual(session.calls[0][1], 11)
        self.assertIn("User-Agent", session.calls[0][2])

        class ErrorResponse:
            status_code = 500
            text = "server error"

            def json(self):
                return {}

        session.get = lambda url, timeout, headers: ErrorResponse()
        with self.assertRaises(FetchError) as context:
            fetcher(41525)
        self.assertEqual(context.exception.status_code, 500)


if __name__ == "__main__":
    unittest.main()
