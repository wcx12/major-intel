import unittest

import pandas as pd

from scripts.reports.build_civil_service_major_fit_by_tier import (
    _build_direct_metrics,
    _major_match_key,
)


class CivilServiceMajorFitByTierTests(unittest.TestCase):
    def test_major_match_key_bridges_catalog_suffixes(self):
        self.assertEqual(
            _major_match_key("030101K", "\u6cd5\u5b66", "\u672c\u79d1"),
            _major_match_key("030101", "\u6cd5\u5b66", "\u672c\u79d1"),
        )
        self.assertNotEqual(
            _major_match_key("530302", "\u5927\u6570\u636e\u4e0e\u4f1a\u8ba1", "\u4e13\u79d1"),
            _major_match_key("530302", "\u5927\u6570\u636e\u4e0e\u4f1a\u8ba1", "\u672c\u79d1"),
        )

    def test_build_direct_metrics_splits_exact_broad_unlimited_and_level_ratios(self):
        matches = pd.DataFrame(
            [
                {
                    "role_id": "1",
                    "major_code": "030101",
                    "education_level": "本科及以上",
                    "plan_num": 2,
                    "apply_num": 20,
                    "competition_ratio": 10,
                    "match_scope": "exact",
                    "department_level": "中央",
                    "department_name": "最高人民法院",
                    "job_name": "法务岗位一级主任科员及以下",
                    "profession_text": "法学",
                    "is_low_restriction_role": True,
                },
                {
                    "role_id": "2",
                    "major_code": "030101",
                    "education_level": "本科及以上",
                    "plan_num": 1,
                    "apply_num": 100,
                    "competition_ratio": 100,
                    "match_scope": "broad",
                    "department_level": "市（地）级",
                    "department_name": "国家税务总局某市税务局",
                    "job_name": "一级行政执法员",
                    "profession_text": "不限",
                    "is_low_restriction_role": True,
                },
                {
                    "role_id": "3",
                    "major_code": "030101",
                    "education_level": "大专及以上",
                    "plan_num": 3,
                    "apply_num": 90,
                    "competition_ratio": 30,
                    "match_scope": "exact",
                    "department_level": "县（区）级及以下",
                    "department_name": "某县公安局",
                    "job_name": "基层民警",
                    "profession_text": "不限",
                    "is_low_restriction_role": True,
                },
            ]
        )

        metrics = _build_direct_metrics(matches).set_index("major_code")
        row = metrics.loc["030101"]

        self.assertEqual(row["undergrad_role_count"], 2)
        self.assertEqual(row["undergrad_exact_role_count"], 1)
        self.assertEqual(row["undergrad_broad_role_count"], 1)
        self.assertEqual(row["undergrad_no_major_limit_role_count"], 1)
        self.assertEqual(row["undergrad_quasi_three_unlimited_role_count"], 1)
        self.assertEqual(row["undergrad_central_role_count"], 1)
        self.assertEqual(row["undergrad_city_role_count"], 1)
        self.assertEqual(row["undergrad_central_avg_competition_ratio"], 10)
        self.assertEqual(row["undergrad_city_avg_competition_ratio"], 100)
        self.assertEqual(row["college_role_count"], 1)
        self.assertEqual(row["college_no_major_limit_role_count"], 1)
        self.assertIn("税务系统", row["undergrad_suitable_role_types"])
        self.assertIn("法院/检察/司法", row["undergrad_suitable_role_types"])


if __name__ == "__main__":
    unittest.main()
