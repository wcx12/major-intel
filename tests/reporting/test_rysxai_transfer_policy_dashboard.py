import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.build_rysxai_transfer_policy_dashboard import (
    build_dashboard_model,
    repair_mojibake,
    render_dashboard,
    write_dashboard,
)


def mojibake(text):
    return text.encode("utf-8").decode("gb18030", errors="replace")


def sample_record(
    school_id,
    name,
    province,
    level,
    source_url,
    has_policy=True,
    faculty_count=0,
    change_chars=0,
):
    return {
        "schema_version": "rysxai_transfer_policy/v1",
        "fetched_at": "2026-05-20T14:48:04+08:00",
        "source": {"source_url": source_url},
        "school": {
            "id": school_id,
            "name": mojibake(name),
            "province": mojibake(province),
            "city": mojibake(province),
            "type": mojibake("综合"),
            "property": mojibake("公办"),
            "level": mojibake(level),
            "department": mojibake("教育部"),
            "tags": ["985", "211"],
        },
        "transfer_policy": {
            "change_profession": mojibake("学生可在规定时间内申请转专业。") if has_policy else "",
            "change_profession_by_faculty": [{} for _ in range(faculty_count)],
            "is_new_version": "/docs/new/" in source_url,
        },
        "availability": {
            "has_transfer_policy": has_policy,
            "has_faculty_policy": faculty_count > 0,
            "faculty_policy_count": faculty_count,
            "change_profession_chars": change_chars,
            "application_condition_chars": 0,
            "admission_requirement_chars": 0,
            "assessment_chars": 0,
        },
    }


class RysxaiTransferPolicyDashboardTests(unittest.TestCase):
    def test_repair_mojibake_restores_common_school_labels(self):
        self.assertEqual(repair_mojibake(mojibake("复旦大学")), "复旦大学")
        self.assertEqual(repair_mojibake(mojibake("本科")), "本科")
        self.assertEqual(repair_mojibake("985"), "985")

    def test_build_dashboard_model_aggregates_transfer_policy_records(self):
        records = [
            sample_record(
                1,
                "浙江大学",
                "浙江",
                "本科",
                "https://api.rysxai.cn/api/ry_education/university/docs/new/?id=1",
                has_policy=True,
                faculty_count=2,
                change_chars=1200,
            ),
            sample_record(
                2,
                "南京职业技术大学",
                "江苏",
                "专科",
                "https://api.rysxai.cn/api/ry_education/university/docs/?id=2",
                has_policy=True,
                faculty_count=0,
                change_chars=80,
            ),
            sample_record(
                3,
                "上海样例学院",
                "上海",
                "本科",
                "https://api.rysxai.cn/api/ry_education/university/docs/?id=3",
                has_policy=False,
                faculty_count=0,
                change_chars=0,
            ),
        ]

        model = build_dashboard_model(records)

        self.assertEqual(model["summary"]["totalSchools"], 3)
        self.assertEqual(model["summary"]["schoolsWithPolicy"], 2)
        self.assertEqual(model["summary"]["emptyPolicySchools"], 1)
        self.assertEqual(model["summary"]["schoolsWithFacultyPolicy"], 1)
        self.assertEqual(model["records"][0]["schoolName"], "浙江大学")

        endpoints = {item["label"]: item["value"] for item in model["charts"]["endpointCounts"]}
        self.assertEqual(endpoints, {"旧接口": 2, "新接口": 1})

        buckets = {item["label"]: item["value"] for item in model["charts"]["lengthBuckets"]}
        self.assertEqual(buckets["空白"], 1)
        self.assertEqual(buckets["1-999字"], 1)
        self.assertEqual(buckets["1000-4999字"], 1)

    def test_render_dashboard_embeds_payload_and_ui_shell(self):
        model = build_dashboard_model(
            [
                sample_record(
                    1,
                    "浙江大学",
                    "浙江",
                    "本科",
                    "https://api.rysxai.cn/api/ry_education/university/docs/new/?id=1",
                    has_policy=True,
                    faculty_count=1,
                    change_chars=100,
                )
            ]
        )

        html = render_dashboard(model)

        self.assertIn("转专业政策可视化", html)
        self.assertIn('<script id="payload" type="application/json">', html)
        self.assertIn("浙江大学", html)

    def test_write_dashboard_reads_jsonl_and_writes_html(self):
        with TemporaryDirectory() as temp_dir:
            jsonl_path = Path(temp_dir) / "policies.jsonl"
            output_path = Path(temp_dir) / "dashboard.html"
            record = sample_record(
                1,
                "浙江大学",
                "浙江",
                "本科",
                "https://api.rysxai.cn/api/ry_education/university/docs/new/?id=1",
                has_policy=True,
                faculty_count=1,
                change_chars=100,
            )
            jsonl_path.write_text(
                json.dumps(record, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            written = write_dashboard(jsonl_path, output_path)

            self.assertEqual(written, output_path)
            self.assertIn("转专业政策可视化", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
