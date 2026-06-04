import unittest


class CurateEmploymentCqupt20162017Test(unittest.TestCase):
    def test_builds_source_and_high_confidence_metrics(self):
        from scripts.one_off.official_sources.curate_employment_cqupt_2016_2017 import (
            SOURCE_URL,
            build_metric_rows,
            build_source_row,
        )

        source = build_source_row()
        self.assertEqual(source["school_name"], "重庆邮电大学")
        self.assertEqual(source["report_year_or_cohort"], "2016-2017")
        self.assertEqual(source["source_url"], SOURCE_URL)
        self.assertEqual(source["fetch_status"], "200_downloaded")
        self.assertEqual(source["content_type"], "application/pdf")
        self.assertEqual(source["extraction_status"], "metrics_extracted")

        metrics = build_metric_rows()
        by_name = {row["metric_name"]: row for row in metrics}
        self.assertEqual(len(metrics), 6)
        self.assertEqual(by_name["undergraduate_graduation_rate"]["metric_value"], "95.93")
        self.assertEqual(by_name["undergraduate_degree_award_rate"]["metric_value"], "99.16")
        self.assertEqual(by_name["initial_employment_rate"]["metric_value"], "94.64")
        self.assertEqual(by_name["initial_employment_rate_2016"]["metric_value"], "92.18")
        self.assertEqual(by_name["year_end_employment_rate_2016"]["metric_value"], "93.97")
        self.assertEqual(by_name["employer_satisfaction_rate"]["metric_value"], "92.00")
        for row in metrics:
            self.assertEqual(row["school_name"], "重庆邮电大学")
            self.assertEqual(row["report_year_or_cohort"], "2016-2017")
            self.assertEqual(row["source_url"], SOURCE_URL)
            self.assertEqual(row["metric_unit"], "percent")
            self.assertEqual(row["extraction_quality"], "high")


if __name__ == "__main__":
    unittest.main()
