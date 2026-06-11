import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from major_intel.volunteer_matching.mysql_export import build_actual_sql, build_history_sql, build_score_rank_sql, export_cases, load_env_file


class MysqlExportSqlTests(unittest.TestCase):
    def test_actual_sql_filters_active_target_rows_with_rank(self):
        sql = build_actual_sql(target_year=2025, limit=100)

        self.assertIn("deleted = 0", sql)
        self.assertIn("COALESCE(NULLIF(major_code, ''), NULLIF(major_name, ''), '')", sql)
        self.assertIn("AS opportunity_grain", sql)
        self.assertIn("CASE WHEN remark LIKE", sql)
        self.assertIn("THEN 'history'", sql)
        self.assertIn("THEN 'physics'", sql)
        self.assertIn("SUBSTRING_INDEX(remark, '/', -1)", sql)
        self.assertIn("year = 2025", sql)
        self.assertIn("stable_rank IS NOT NULL", sql)
        self.assertIn("stable_rank > 0", sql)
        self.assertIn("LIMIT 100", sql)

    def test_history_sql_excludes_target_year_from_training_history(self):
        sql = build_history_sql(target_year=2025)

        self.assertIn("deleted = 0", sql)
        self.assertIn("COALESCE(NULLIF(major_code, ''), NULLIF(major_name, ''), '')", sql)
        self.assertIn("CASE WHEN remark LIKE", sql)
        self.assertIn("THEN 'history'", sql)
        self.assertIn("THEN 'physics'", sql)
        self.assertIn("SUBSTRING_INDEX(remark, '/', -1)", sql)
        self.assertIn("year < 2025", sql)
        self.assertNotIn("year <= 2025", sql)
        self.assertIn("stable_rank IS NOT NULL", sql)

    def test_score_rank_sql_loads_target_year_rank_to_score_points(self):
        sql = build_score_rank_sql(target_year=2025)

        self.assertIn("FROM edu_score_rank", sql)
        self.assertIn("year = 2025", sql)
        self.assertIn("lowest_rank IS NOT NULL", sql)
        self.assertIn("ORDER BY province_id, subject_type, lowest_rank", sql)

    def test_stratified_actual_sql_balances_backtestable_rows(self):
        sql = build_actual_sql(target_year=2024, limit=25, sample_mode="stratified")

        self.assertIn("ROW_NUMBER() OVER", sql)
        self.assertIn("opportunity_grain", sql)
        self.assertIn("PARTITION BY t.province_id", sql)
        self.assertIn("CASE WHEN t.remark LIKE", sql)
        self.assertIn("SUBSTRING_INDEX(t.remark, '/', -1)", sql)
        self.assertIn("stratum_row_number <= 25", sql)
        self.assertIn("EXISTS", sql)
        self.assertIn("h.year < 2024", sql)
        self.assertIn("COALESCE(NULLIF(t.major_code, ''), NULLIF(t.major_name, ''), '')", sql)
        self.assertIn("COALESCE(NULLIF(h.major_code, ''), NULLIF(h.major_name, ''), '')=COALESCE(NULLIF(t.major_code, ''), NULLIF(t.major_name, ''), '')", sql)
        self.assertIn("CASE WHEN h.remark LIKE", sql)
        self.assertIn("SUBSTRING_INDEX(h.remark, '/', -1)", sql)

    def test_load_env_file_sets_missing_values_without_overriding(self):
        with TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "GAOKAO_DB_HOST=127.0.0.1\n"
                "GAOKAO_DB_PASSWORD=secret\n"
                "EXISTING=from_file\n",
                encoding="utf-8",
            )
            environ = {"EXISTING": "from_process"}

            load_env_file(env_path, environ)

            self.assertEqual(environ["GAOKAO_DB_HOST"], "127.0.0.1")
        self.assertEqual(environ["GAOKAO_DB_PASSWORD"], "secret")
        self.assertEqual(environ["EXISTING"], "from_process")

    def test_export_cases_labels_school_level_rows_when_major_key_is_missing(self):
        class FakeClient:
            def query(self, sql):
                if "stable_rank AS actual_rank" in sql:
                    return [
                        {
                            "opportunity_key": "12713::44:history:高职专科批",
                            "year": "2024",
                            "actual_rank": "247960",
                            "actual_score": "266",
                            "school_id": "12713",
                            "school_name": "School A",
                            "major_code": None,
                            "major_name": "",
                            "opportunity_grain": "school",
                            "province_id": "44",
                            "province_name": "广东",
                            "subject_type": "history",
                            "batch": "高职专科批",
                        }
                    ]
                if "stable_rank AS cutoff_rank" in sql:
                    return [
                        {
                            "opportunity_key": "12713::44:history:高职专科批",
                            "year": "2023",
                            "cutoff_rank": "220000",
                            "cutoff_score": "290",
                            "plan_count": "10",
                        }
                    ]
                if "FROM edu_score_rank" in sql:
                    return [{"province_id": "44", "subject_type": "history", "score": "266", "lowest_rank": "247960"}]
                return []

        cases = export_cases(FakeClient(), target_year=2024, limit=10)

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].metadata["opportunity_grain"], "school")


if __name__ == "__main__":
    unittest.main()
