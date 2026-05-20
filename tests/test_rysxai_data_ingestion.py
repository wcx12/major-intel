import json
import unittest

from scripts.ingest_rysxai_data import (
    build_insert_sql,
    build_schema_sql,
    civil_role_record_to_rows,
    market_snapshot_to_rows,
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

    def test_build_schema_sql_contains_tables_and_idempotent_keys(self):
        schema_sql = build_schema_sql()

        self.assertIn("CREATE TABLE IF NOT EXISTS rysxai_major_market_snapshots", schema_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS rysxai_major_job_samples", schema_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS rysxai_civil_service_roles", schema_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS civil_service_major_role_candidates", schema_sql)
        self.assertIn("UNIQUE KEY uk_profession_sample", schema_sql)
        self.assertIn("UNIQUE KEY uk_role_candidate", schema_sql)

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


if __name__ == "__main__":
    unittest.main()
