import json
import unittest

from scripts.ingest_rysxai_data import (
    TRANSFER_POLICY_TABLE,
    build_insert_sql,
    build_schema_sql,
    civil_role_record_to_rows,
    ingest_transfer,
    load_transfer_policy_records,
    market_snapshot_to_rows,
    transfer_policy_record_to_row,
)


MARKET_SNAPSHOT = {
    "schema_version": "rysxai_market_snapshot/v1",
    "captured_at": "2026-05-19T21:14:37+08:00",
    "source": {
        "name": "rysxai",
        "source_level": "C",
        "data_scope": "major_level_market_observation",
        "info_url": "https://api.rysxai.cn/api/ry_education/profession/info/?id=270",
        "positions_url": "https://api.rysxai.cn/api/ry_education/profession/positions/?id=270",
    },
    "profession": {
        "id": 270,
        "name": "机械工程",
        "code": "080201",
        "level": "本科",
        "degree": "工学学士",
        "limit_year": "四年",
    },
    "macro_employment": {
        "industry_distribution": [{"label": "机械重工", "rate_percent": 29.61}],
        "region_distribution": [{"label": "上海", "rate_percent": 15.1}],
    },
    "demand_ranking": [{"region": "全国", "demand_count": 61649}],
    "salary_ranking": [{"region": "上海", "monthly_salary_reference": 8945}],
    "job_posting_sample_total_reported": 50,
    "job_posting_sample_count": 1,
    "job_posting_samples": [
        {
            "source_item_id": 50,
            "job_title": "机械工程师",
            "company_name": "励金",
            "city": "无锡",
            "district": "惠山区",
            "industry": "通用设备",
            "salary_raw": "15-20K",
            "monthly_salary_min": 15000,
            "monthly_salary_max": 20000,
            "education": "本科",
            "experience": "5-10年",
            "skills": ["SolidWorks"],
            "company_tags": ["未融资", "0-20人"],
            "company_scale": "0-20人",
            "financing_stage": "未融资",
            "source_level": "C",
            "data_scope": "recruiting_market_sample",
        }
    ],
    "salary_observations_by_city": {
        "无锡": {
            "sample_count": 1,
            "monthly_salary_min_observed": 15000,
            "monthly_salary_max_observed": 20000,
        }
    },
    "salary_observations_by_industry": {},
    "warnings": ["招聘岗位样本不能代表某校某专业毕业生实际薪资。"],
}


CIVIL_ROLE_RECORD = {
    "schema_version": "rysxai_civil_service_role/v1",
    "fetched_at": "2026-05-19T22:41:04+08:00",
    "source": {
        "source_url": "https://api.rysxai.cn/api/ry_education/civil_servant/info/?id=20812"
    },
    "role": {
        "id": 20812,
        "year": 2026,
        "sheet_type": "中央机关",
        "department_code": "2000",
        "department_name": "中央办公厅",
        "sub_department": "老干部局",
        "job_name": "行政后勤岗位",
        "position_code": "100210002005",
        "exam_type": "综合管理类",
        "plan_num": 2,
        "apply_num": 448,
        "ratio": 224.0,
        "profession": "081002建筑环境与能源应用工程、080901计算机科学与技术",
        "education_level": "仅限本科",
        "degree_requirement": "学士",
        "work_location": "北京市",
        "province": "北京",
        "remark": "以官方招录表为准。",
    },
}


def mojibake(text):
    return text.encode("utf-8").decode("gb18030", errors="replace")


TRANSFER_POLICY_RECORD = {
    "schema_version": "rysxai_transfer_policy/v1",
    "fetched_at": "2026-05-20T14:48:04+08:00",
    "source": {
        "name": "rysxai",
        "source_level": "C",
        "source_url": "https://api.rysxai.cn/api/ry_education/university/docs/new/?id=903",
        "data_scope": "school_transfer_major_policy",
    },
    "school": {
        "id": 903,
        "name": mojibake("浙江大学"),
        "province": mojibake("浙江"),
        "city": mojibake("杭州"),
        "town": mojibake("西湖区"),
        "type": mojibake("综合"),
        "property": mojibake("公办"),
        "level": mojibake("本科"),
        "department": mojibake("教育部"),
        "tags": ["985", "211", mojibake("双一流")],
        "rank_list": [{"qs": "47"}],
    },
    "transfer_policy": {
        "change_profession": mojibake("学生申请"),
        "change_profession_by_faculty": [
            {"faculty_name": mojibake("信息学院"), "rows": []}
        ],
        "change_profession_application_condition": mojibake("申请条件文本"),
        "change_profession_admission_requirement": mojibake("准入要求文本"),
        "change_profession_assessment": mojibake("考核方式文本"),
        "is_new_version": True,
    },
    "availability": {
        "has_transfer_policy": True,
        "has_faculty_policy": True,
        "faculty_policy_count": 1,
        "change_profession_chars": 18,
        "application_condition_chars": 6,
        "admission_requirement_chars": 6,
        "assessment_chars": 6,
    },
    "warnings": ["verify against official school notices"],
}


class RysxaiDataIngestionTests(unittest.TestCase):
    def test_market_snapshot_to_rows_preserves_scope_and_job_samples(self):
        snapshot_row, sample_rows = market_snapshot_to_rows(MARKET_SNAPSHOT)

        self.assertEqual(snapshot_row["profession_id"], 270)
        self.assertEqual(snapshot_row["major_code"], "080201")
        self.assertEqual(snapshot_row["major_name"], "机械工程")
        self.assertEqual(snapshot_row["source_level"], "C")
        self.assertEqual(snapshot_row["data_scope"], "major_level_market_observation")
        self.assertEqual(snapshot_row["job_posting_sample_count"], 1)
        self.assertEqual(
            json.loads(snapshot_row["macro_employment_json"])["industry_distribution"][0]["label"],
            "机械重工",
        )
        self.assertEqual(
            json.loads(snapshot_row["raw_snapshot_json"])["schema_version"],
            "rysxai_market_snapshot/v1",
        )

        self.assertEqual(len(sample_rows), 1)
        self.assertEqual(sample_rows[0]["profession_id"], 270)
        self.assertEqual(sample_rows[0]["major_name"], "机械工程")
        self.assertEqual(sample_rows[0]["source_item_id"], "50")
        self.assertEqual(sample_rows[0]["monthly_salary_min"], 15000)
        self.assertEqual(json.loads(sample_rows[0]["skills_json"]), ["SolidWorks"])

    def test_civil_role_record_to_rows_extracts_major_code_candidates(self):
        role_row, candidate_rows = civil_role_record_to_rows(CIVIL_ROLE_RECORD)

        self.assertEqual(role_row["role_id"], 20812)
        self.assertEqual(role_row["year"], 2026)
        self.assertEqual(role_row["department_name"], "中央办公厅")
        self.assertEqual(role_row["profession_text"], "081002建筑环境与能源应用工程、080901计算机科学与技术")
        self.assertEqual(json.loads(role_row["raw_role_json"])["id"], 20812)

        self.assertEqual([row["major_code"] for row in candidate_rows], ["081002", "080901"])
        self.assertEqual(candidate_rows[0]["candidate_type"], "major_code")
        self.assertEqual(candidate_rows[0]["major_name"], "建筑环境与能源应用工程")
        self.assertEqual(candidate_rows[1]["major_name"], "计算机科学与技术")

    def test_civil_role_record_to_rows_keeps_unparsed_profession_text(self):
        record = json.loads(json.dumps(CIVIL_ROLE_RECORD, ensure_ascii=False))
        record["role"]["id"] = 20813
        record["role"]["profession"] = "计算机类、电子信息类及相关专业"

        _, candidate_rows = civil_role_record_to_rows(record)

        self.assertEqual(len(candidate_rows), 1)
        self.assertEqual(candidate_rows[0]["candidate_type"], "raw_profession_text")
        self.assertEqual(candidate_rows[0]["major_code"], "")
        self.assertEqual(candidate_rows[0]["profession_text"], "计算机类、电子信息类及相关专业")

    def test_transfer_policy_record_to_row_preserves_scope_and_repairs_display_text(self):
        row = transfer_policy_record_to_row(TRANSFER_POLICY_RECORD)

        self.assertEqual(row["school_id"], 903)
        self.assertEqual(row["school_name"], "浙江大学")
        self.assertEqual(row["province"], "浙江")
        self.assertEqual(row["school_level"], "本科")
        self.assertEqual(row["source_level"], "C")
        self.assertEqual(row["data_scope"], "school_transfer_major_policy")
        self.assertEqual(row["source_endpoint"], "new")
        self.assertEqual(row["has_transfer_policy"], 1)
        self.assertEqual(row["has_faculty_policy"], 1)
        self.assertEqual(row["faculty_policy_count"], 1)
        self.assertIn("\u5b66\u751f\u7533\u8bf7", row["change_profession"])
        self.assertIn("\u4fe1\u606f\u5b66\u9662", row["change_profession_by_faculty_json"])
        self.assertEqual(
            json.loads(row["raw_policy_json"])["schema_version"],
            "rysxai_transfer_policy/v1",
        )

    def test_transfer_policy_record_to_row_does_not_corrupt_valid_chinese_policy_text(self):
        record = json.loads(json.dumps(TRANSFER_POLICY_RECORD, ensure_ascii=False))
        record["transfer_policy"]["change_profession"] = (
            "## 中国语言文学系\n\n### 转专业申请条件\n\n学生可在规定时间内申请，条件包含面试和成绩排名。"
        )

        row = transfer_policy_record_to_row(record)

        self.assertIn("中国语言文学系", row["change_profession"])
        self.assertIn("转专业申请条件", row["change_profession"])
        self.assertIn("条件包含面试", row["change_profession"])
        self.assertNotIn("�й", row["change_profession"])

    def test_build_schema_sql_contains_tables_and_idempotent_keys(self):
        schema_sql = build_schema_sql()

        self.assertIn("CREATE TABLE IF NOT EXISTS rysxai_major_market_snapshots", schema_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS rysxai_major_job_samples", schema_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS rysxai_civil_service_roles", schema_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS civil_service_major_role_candidates", schema_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS rysxai_transfer_policies", schema_sql)
        self.assertIn("UNIQUE KEY uk_profession_sample", schema_sql)
        self.assertIn("UNIQUE KEY uk_role_candidate", schema_sql)
        self.assertIn("PRIMARY KEY (school_id)", schema_sql)

    def test_build_insert_sql_escapes_values_without_exposing_passwords(self):
        sql = build_insert_sql(
            "rysxai_major_market_snapshots",
            [{"profession_id": 270, "major_name": "机械'工程", "job_posting_sample_count": 1}],
            key_columns=["profession_id"],
        )

        self.assertIn("INSERT INTO rysxai_major_market_snapshots", sql)
        self.assertIn("'机械''工程'", sql)
        self.assertIn("ON DUPLICATE KEY UPDATE", sql)
        self.assertNotIn("MYSQL_PWD", sql)
        self.assertNotIn("GAOKAO_DB_PASSWORD", sql)

    def test_load_transfer_policy_records_reads_jsonl_with_limit(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            jsonl_path = Path(temp_dir) / "transfer.jsonl"
            jsonl_path.write_text(
                json.dumps(TRANSFER_POLICY_RECORD, ensure_ascii=False)
                + "\n"
                + json.dumps(
                    {
                        **TRANSFER_POLICY_RECORD,
                        "school": {**TRANSFER_POLICY_RECORD["school"], "id": 904},
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            records = load_transfer_policy_records(jsonl_path, limit=1)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["school"]["id"], 903)

    def test_ingest_transfer_builds_idempotent_chunks(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        class FakeRunner:
            def __init__(self):
                self.sql_statements = []

            def run(self, sql, capture_output=False):
                self.sql_statements.append(sql)
                return ""

        with TemporaryDirectory() as temp_dir:
            jsonl_path = Path(temp_dir) / "transfer.jsonl"
            records = []
            for school_id in [903, 904, 905]:
                record = json.loads(json.dumps(TRANSFER_POLICY_RECORD, ensure_ascii=False))
                record["school"]["id"] = school_id
                records.append(record)
            jsonl_path.write_text(
                "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
                encoding="utf-8",
            )
            runner = FakeRunner()

            stats = ingest_transfer(runner, jsonl_path, chunk_size=2)

            self.assertEqual(stats, {"policies": 3})
            self.assertEqual(len(runner.sql_statements), 2)
            self.assertTrue(all(TRANSFER_POLICY_TABLE in sql for sql in runner.sql_statements))
            self.assertTrue(all("ON DUPLICATE KEY UPDATE" in sql for sql in runner.sql_statements))


if __name__ == "__main__":
    unittest.main()
