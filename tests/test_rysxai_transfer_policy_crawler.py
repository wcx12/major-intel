import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.rysxai_transfer_policy_crawler import (
    FetchError,
    _json_body_from_query,
    crawl_transfer_policies,
    list_universities_from_api,
    normalize_transfer_policy,
    read_completed_school_ids,
    write_csv_from_jsonl,
)


SCHOOL = {
    "id": 903,
    "name": "浙江大学",
    "province": "浙江",
    "city": "杭州市",
    "type": "综合",
    "property": "公办",
    "level": "本科",
    "department": "教育部",
    "tags": ["985", "211"],
}


DOCS_PAYLOAD = {
    "code": "SUCCESS",
    "detail": "成功",
    "data": {
        "change_profession": "## 转专业政策\n学生可在规定时间内申请。",
        "change_profession_by_faculty": [
            {
                "faculty_name": "信息与电子工程学院",
                "columns": [{"key": "condition", "title": "申请条件"}],
                "rows": [{"condition": "GPA 不低于 3.5"}],
            }
        ],
        "change_profession_application_condition": "申请条件文本",
        "change_profession_admission_requirement": "准入要求文本",
        "change_profession_assessment": "考核方式文本",
        "is_new_version": True,
    },
}


class RysxaiTransferPolicyCrawlerTests(unittest.TestCase):
    def test_normalize_transfer_policy_keeps_policy_fields_and_metadata(self):
        record = normalize_transfer_policy(
            SCHOOL,
            DOCS_PAYLOAD,
            fetched_at="2026-05-20T12:00:00+08:00",
            source_url="https://api.rysxai.cn/api/ry_education/university/docs/new/?id=903",
        )

        self.assertEqual(record["schema_version"], "rysxai_transfer_policy/v1")
        self.assertEqual(record["school"]["id"], 903)
        self.assertEqual(record["school"]["name"], "浙江大学")
        self.assertTrue(record["availability"]["has_transfer_policy"])
        self.assertTrue(record["availability"]["has_faculty_policy"])
        self.assertEqual(record["availability"]["faculty_policy_count"], 1)
        self.assertIn("学生可在规定时间内申请", record["transfer_policy"]["change_profession"])
        self.assertEqual(
            record["transfer_policy"]["change_profession_by_faculty"][0]["faculty_name"],
            "信息与电子工程学院",
        )

    def test_list_universities_from_api_pages_until_total_and_deduplicates(self):
        calls = []

        def fake_fetch(url, method="GET", timeout_seconds=20):
            calls.append(url)
            page = 1 if "page_flag=1" in url else 2
            if page == 1:
                return {
                    "code": "SUCCESS",
                    "data": {
                        "total": 3,
                        "items": [
                            SCHOOL,
                            {"id": 1, "name": "北京大学", "province": "北京"},
                        ],
                    },
                }
            return {
                "code": "SUCCESS",
                "data": {
                    "total": 3,
                    "items": [
                        {"id": 1, "name": "北京大学", "province": "北京"},
                        {"id": 3, "name": "清华大学", "province": "北京"},
                    ],
                },
            }

        schools = list_universities_from_api(
            fetcher=fake_fetch,
            page_size=2,
            delay_seconds=0,
            sleeper=lambda seconds: None,
        )

        self.assertEqual([school["id"] for school in schools], [903, 1, 3])
        self.assertEqual(len(calls), 2)

    def test_list_universities_from_api_retries_transient_fetch_errors(self):
        calls = []

        def fake_fetch(url, method="GET", timeout_seconds=20):
            calls.append(url)
            if len(calls) == 1:
                raise FetchError("temporary", status_code=None)
            return {"code": "SUCCESS", "data": {"total": 1, "items": [SCHOOL]}}

        schools = list_universities_from_api(
            fetcher=fake_fetch,
            page_size=10,
            delay_seconds=0,
            retry_base_seconds=0,
            sleeper=lambda seconds: None,
        )

        self.assertEqual([school["id"] for school in schools], [903])
        self.assertEqual(len(calls), 2)

    def test_read_completed_school_ids_ignores_invalid_lines(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "policies.jsonl"
            output_path.write_text(
                "\n"
                + json.dumps({"school": {"id": 903}}, ensure_ascii=False)
                + "\nnot-json\n"
                + json.dumps({"school": {"id": 1}}, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )

            self.assertEqual(read_completed_school_ids(output_path), {1, 903})

    def test_crawl_transfer_policies_skips_existing_and_logs_failures(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "policies.jsonl"
            failures_path = Path(temp_dir) / "failures.jsonl"
            output_path.write_text(
                json.dumps({"school": {"id": 903}}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            calls = []

            def fake_fetch(url, method="GET", timeout_seconds=20):
                calls.append(url)
                if "id=3" in url:
                    raise FetchError("server busy", status_code=503)
                return DOCS_PAYLOAD

            summary = crawl_transfer_policies(
                schools=[
                    SCHOOL,
                    {"id": 1, "name": "北京大学", "province": "北京"},
                    {"id": 3, "name": "清华大学", "province": "北京"},
                ],
                output_path=output_path,
                failures_path=failures_path,
                delay_seconds=0,
                jitter_seconds=0,
                fetcher=fake_fetch,
                sleeper=lambda seconds: None,
            )

            self.assertEqual(len(calls), 2)
            self.assertEqual(summary.requested_schools, 3)
            self.assertEqual(summary.skipped_existing, 1)
            self.assertEqual(summary.fetched, 1)
            self.assertEqual(summary.failed, 1)
            self.assertEqual(read_completed_school_ids(output_path), {1, 903})

            failure = json.loads(failures_path.read_text(encoding="utf-8").strip())
            self.assertEqual(failure["school_id"], 3)
            self.assertEqual(failure["status_code"], 503)

    def test_crawl_transfer_policies_falls_back_to_legacy_docs_after_404(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "policies.jsonl"
            failures_path = Path(temp_dir) / "failures.jsonl"
            calls = []

            def fake_fetch(url, method="GET", timeout_seconds=20):
                calls.append(url)
                if "/docs/new/" in url:
                    raise FetchError("not found", status_code=404)
                return {
                    "code": "SUCCESS",
                    "data": {"change_profession": "旧接口转专业政策"},
                }

            summary = crawl_transfer_policies(
                schools=[SCHOOL],
                output_path=output_path,
                failures_path=failures_path,
                delay_seconds=0,
                jitter_seconds=0,
                fetcher=fake_fetch,
                sleeper=lambda seconds: None,
            )

            self.assertEqual(summary.fetched, 1)
            self.assertEqual(summary.failed, 0)
            self.assertIn("/docs/new/", calls[0])
            self.assertIn("/docs/", calls[1])
            record = json.loads(output_path.read_text(encoding="utf-8").strip())
            self.assertEqual(record["transfer_policy"]["change_profession"], "旧接口转专业政策")
            self.assertTrue(record["source"]["source_url"].endswith("/docs/?id=903"))

    def test_crawl_transfer_policies_can_run_with_worker_pool(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "policies.jsonl"
            failures_path = Path(temp_dir) / "failures.jsonl"

            def fake_fetch(url, method="GET", timeout_seconds=20):
                payload = json.loads(json.dumps(DOCS_PAYLOAD, ensure_ascii=False))
                payload["data"]["change_profession"] = f"policy from {url.split('id=')[1]}"
                return payload

            summary = crawl_transfer_policies(
                schools=[
                    SCHOOL,
                    {"id": 1, "name": "北京大学", "province": "北京"},
                ],
                output_path=output_path,
                failures_path=failures_path,
                delay_seconds=0,
                jitter_seconds=0,
                fetcher=fake_fetch,
                sleeper=lambda seconds: None,
                workers=2,
            )

            self.assertEqual(summary.fetched, 2)
            records = [
                json.loads(line)
                for line in output_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual({record["school"]["id"] for record in records}, {1, 903})

    def test_json_body_from_query_keeps_post_pagination_params(self):
        body = _json_body_from_query(
            "https://api.rysxai.cn/api/ry_education/university/search/v2/?page_model=page&page_flag=2&page_size=10"
        )

        self.assertEqual(
            json.loads(body.decode("utf-8")),
            {"page_model": "page", "page_flag": "2", "page_size": "10"},
        )

    def test_write_csv_from_jsonl_flattens_summary_and_json_fields(self):
        with TemporaryDirectory() as temp_dir:
            jsonl_path = Path(temp_dir) / "policies.jsonl"
            csv_path = Path(temp_dir) / "policies.csv"
            record = normalize_transfer_policy(
                SCHOOL,
                DOCS_PAYLOAD,
                fetched_at="2026-05-20T12:00:00+08:00",
                source_url="https://api.rysxai.cn/api/ry_education/university/docs/new/?id=903",
            )
            jsonl_path.write_text(
                json.dumps(record, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            count = write_csv_from_jsonl(jsonl_path, csv_path)

            self.assertEqual(count, 1)
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["school_id"], "903")
            self.assertEqual(rows[0]["school_name"], "浙江大学")
            self.assertEqual(rows[0]["has_transfer_policy"], "true")
            self.assertIn("信息与电子工程学院", rows[0]["change_profession_by_faculty_json"])


if __name__ == "__main__":
    unittest.main()
