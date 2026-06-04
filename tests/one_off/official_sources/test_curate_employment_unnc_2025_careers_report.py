import unittest


class CurateEmploymentUnnc2025CareersReportTest(unittest.TestCase):
    def test_builds_pdf_source_and_high_confidence_metrics(self):
        from scripts.one_off.official_sources.curate_employment_unnc_2025_careers_report import (
            SOURCE_URL,
            build_metric_rows,
            build_source_row,
        )

        school_name = "\u5b81\u6ce2\u8bfa\u4e01\u6c49\u5927\u5b66"
        source = build_source_row()
        self.assertEqual(source["school_name"], school_name)
        self.assertEqual(source["report_year_or_cohort"], "2025\u5c4a")
        self.assertEqual(source["source_url"], SOURCE_URL)
        self.assertEqual(source["fetch_status"], "200_downloaded")
        self.assertEqual(source["content_type"], "application/pdf")
        self.assertEqual(source["extraction_status"], "metrics_extracted")
        self.assertIn("2024-2025", source["source_title"])

        metrics = build_metric_rows()
        by_name = {row["metric_name"]: row for row in metrics}
        self.assertEqual(len(metrics), 62)
        expected_values = {
            "graduate_count": "2715",
            "bachelor_count": "1666",
            "master_count": "903",
            "phd_count": "146",
            "bachelor_employment_rate": "95.2",
            "master_employment_rate": "95.0",
            "phd_employment_rate": "100.0",
            "undergraduate_further_study_rate": "87.4",
            "undergraduate_direct_employment_rate": "7.5",
            "undergraduate_startup_rate": "0.3",
            "undergraduate_overseas_further_study_count": "1364",
            "undergraduate_further_study_count": "1368",
            "direct_employment_top_organization_rate": "90.2",
            "direct_employment_new_quality_productive_force_rate": "70.0",
            "undergraduate_employer_top_org_rate": "84.8",
            "master_direct_employment_rate": "85.1",
            "master_further_study_rate": "6.1",
            "master_startup_rate": "3.9",
            "master_education_industry_rate": "23.5",
            "master_financial_services_rate": "20.2",
            "master_manufacturing_rate": "9.9",
            "master_top_organization_rate": "89.4",
            "master_ningbo_retention_rate": "34.0",
            "master_zhejiang_retention_rate": "50.1",
            "phd_top_organization_rate": "98.45",
            "phd_higher_education_institution_rate": "70.5",
            "phd_enterprise_rate": "7.8",
            "phd_ningbo_retention_rate": "41.1",
            "phd_zhejiang_retention_rate": "51.9",
            "international_hmt_further_study_rate": "15.5",
            "international_hmt_direct_employment_rate": "84.5",
            "international_hmt_mainland_china_rate": "26.2",
            "international_hmt_outside_china_rate": "73.8",
        }
        for metric_name, expected_value in expected_values.items():
            self.assertEqual(by_name[metric_name]["metric_value"], expected_value)

        for row in metrics:
            self.assertEqual(row["school_name"], school_name)
            self.assertEqual(row["report_year_or_cohort"], "2025\u5c4a")
            self.assertEqual(row["source_url"], SOURCE_URL)
            self.assertEqual(row["extraction_quality"], "high")


if __name__ == "__main__":
    unittest.main()
