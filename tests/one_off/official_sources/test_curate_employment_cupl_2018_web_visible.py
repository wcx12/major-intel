import unittest


class CurateEmploymentCupl2018WebVisibleTest(unittest.TestCase):
    def test_builds_web_visible_source_and_high_confidence_metrics(self):
        from scripts.one_off.official_sources.curate_employment_cupl_2018_web_visible import (
            SOURCE_URL,
            build_metric_rows,
            build_source_row,
        )

        school_name = "\u4e2d\u56fd\u653f\u6cd5\u5927\u5b66"
        source = build_source_row()
        self.assertEqual(source["school_name"], school_name)
        self.assertEqual(source["report_year_or_cohort"], "2018\u5c4a")
        self.assertEqual(source["source_url"], SOURCE_URL)
        self.assertEqual(source["fetch_status"], "official_page_web_visible")
        self.assertEqual(source["content_type"], "text/html")
        self.assertEqual(source["extraction_status"], "metrics_extracted")
        self.assertEqual(source["local_artifact"], "")
        self.assertIn("local_curl_dynamic_challenge", source["notes"])

        metrics = build_metric_rows()
        by_name = {row["metric_name"]: row for row in metrics}
        self.assertEqual(len(metrics), 14)
        self.assertEqual(by_name["graduate_count"]["metric_value"], "4063")
        self.assertEqual(by_name["undergraduate_count"]["metric_value"], "2092")
        self.assertEqual(by_name["graduate_student_count"]["metric_value"], "1971")
        self.assertEqual(by_name["employment_implementation_count"]["metric_value"], "3989")
        self.assertEqual(by_name["overall_employment_rate"]["metric_value"], "98.18")
        self.assertEqual(by_name["undergraduate_employment_rate"]["metric_value"], "98.80")
        self.assertEqual(by_name["master_employment_rate"]["metric_value"], "97.54")
        self.assertEqual(by_name["doctoral_employment_rate"]["metric_value"], "97.24")
        self.assertEqual(by_name["further_study_count"]["metric_value"], "1441")
        self.assertEqual(by_name["further_study_rate"]["metric_value"], "35.47")
        self.assertEqual(by_name["undergraduate_further_study_count"]["metric_value"], "1313")
        self.assertEqual(by_name["undergraduate_further_study_rate"]["metric_value"], "62.76")
        self.assertEqual(by_name["signing_count"]["metric_value"], "3021")
        self.assertEqual(by_name["signing_rate"]["metric_value"], "74.35")
        for row in metrics:
            self.assertEqual(row["school_name"], school_name)
            self.assertEqual(row["report_year_or_cohort"], "2018\u5c4a")
            self.assertEqual(row["source_url"], SOURCE_URL)
            self.assertEqual(row["extraction_quality"], "high")


if __name__ == "__main__":
    unittest.main()
