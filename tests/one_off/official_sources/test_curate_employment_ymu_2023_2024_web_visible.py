import unittest


class CurateEmploymentYmu20232024WebVisibleTest(unittest.TestCase):
    def test_builds_web_visible_pdf_source_and_high_confidence_metrics(self):
        from scripts.one_off.official_sources.curate_employment_ymu_2023_2024_web_visible import (
            SOURCE_URL,
            build_metric_rows,
            build_source_row,
        )

        school_name = "\u4e91\u5357\u6c11\u65cf\u5927\u5b66"
        source = build_source_row()
        self.assertEqual(source["school_name"], school_name)
        self.assertEqual(source["report_year_or_cohort"], "2023-2024")
        self.assertEqual(source["source_url"], SOURCE_URL)
        self.assertEqual(source["fetch_status"], "official_pdf_web_visible")
        self.assertEqual(source["content_type"], "application/pdf")
        self.assertEqual(source["extraction_status"], "metrics_extracted")
        self.assertIn("local_curl_returned_521_waf", source["notes"])

        metrics = build_metric_rows()
        by_name = {row["metric_name"]: row for row in metrics}
        self.assertEqual(len(metrics), 24)
        expected_values = {
            "total_undergraduate_graduates": "8775",
            "undergraduate_graduation_rate": "100.00",
            "undergraduate_degree_award_count": "8227",
            "undergraduate_degree_award_rate": "93.75",
            "undergraduate_further_study_count": "784",
            "domestic_same_school_further_study_count": "459",
            "domestic_other_school_further_study_count": "155",
            "recommendation_exemption_further_study_count": "115",
            "overseas_study_count": "38",
            "second_bachelor_degree_count": "17",
            "undergraduate_further_study_rate": "8.93",
            "initial_undergraduate_employment_rate": "71.16",
            "initial_employment_count": "6243",
            "local_region_employment_count": "5184",
            "nonlocal_region_employment_count": "1059",
            "signing_agreement_count": "3609",
            "labor_contract_count": "395",
            "other_hiring_form_count": "1223",
            "conscription_count": "69",
            "freelance_count": "108",
            "startup_count": "55",
            "enterprise_employment_share": "57.34",
            "employer_very_satisfied_rate": "46.58",
            "employer_overall_satisfaction_rate": "78.26",
        }
        for metric_name, expected_value in expected_values.items():
            self.assertEqual(by_name[metric_name]["metric_value"], expected_value)

        for row in metrics:
            self.assertEqual(row["school_name"], school_name)
            self.assertEqual(row["report_year_or_cohort"], "2023-2024")
            self.assertEqual(row["source_url"], SOURCE_URL)
            self.assertEqual(row["extraction_quality"], "high")


if __name__ == "__main__":
    unittest.main()
