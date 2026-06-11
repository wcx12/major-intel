import unittest

from major_intel.volunteer_matching.audit import audit_metric_leadership


class LeadershipAuditTests(unittest.TestCase):
    def test_audit_flags_metric_when_primary_method_is_not_leader(self):
        metrics = {
            "volunteer_matching_rank_ensemble": {
                "mae_rank": 1200,
                "within_5_score_points": 0.75,
            },
            "last_year_rank": {
                "mae_rank": 900,
                "within_5_score_points": 0.70,
            },
        }

        audit = audit_metric_leadership(
            metrics,
            primary_method="volunteer_matching_rank_ensemble",
            metric_directions={"mae_rank": "asc", "within_5_score_points": "desc"},
        )

        by_metric = {row["metric"]: row for row in audit}
        self.assertEqual(by_metric["mae_rank"]["status"], "fail")
        self.assertEqual(by_metric["mae_rank"]["best_method"], "last_year_rank")
        self.assertEqual(by_metric["mae_rank"]["best_value"], 900)
        self.assertEqual(by_metric["mae_rank"]["primary_value"], 1200)
        self.assertEqual(by_metric["within_5_score_points"]["status"], "pass")

    def test_audit_marks_missing_primary_metric_as_fail_without_crashing(self):
        metrics = {
            "volunteer_matching_rank_ensemble": {
                "mae_rank": None,
            },
            "last_year_rank": {
                "mae_rank": 900,
            },
        }

        audit = audit_metric_leadership(
            metrics,
            primary_method="volunteer_matching_rank_ensemble",
            metric_directions={"mae_rank": "asc"},
        )

        self.assertEqual(audit[0]["status"], "fail")
        self.assertEqual(audit[0]["reason"], "missing_primary_value")

    def test_audit_accepts_practical_tolerance_for_noisy_rate_metrics(self):
        metrics = {
            "volunteer_matching_rank_ensemble": {
                "directional_bias_abs": 0.0275,
            },
            "sklearn_ridge": {
                "directional_bias_abs": 0.0025,
            },
        }

        audit = audit_metric_leadership(
            metrics,
            primary_method="volunteer_matching_rank_ensemble",
            metric_directions={"directional_bias_abs": "asc"},
            metric_tolerances={"directional_bias_abs": 0.03},
        )

        self.assertEqual(audit[0]["status"], "pass")
        self.assertEqual(audit[0]["reason"], "within_tolerance")
        self.assertEqual(audit[0]["best_method"], "sklearn_ridge")

    def test_audit_excludes_low_coverage_methods_from_metric_leadership(self):
        metrics = {
            "volunteer_matching_rank_ensemble": {
                "coverage_rate": 1.0,
                "mae_rank": 1000,
            },
            "sklearn_ridge": {
                "coverage_rate": 0.75,
                "mae_rank": 100,
            },
        }

        audit = audit_metric_leadership(
            metrics,
            primary_method="volunteer_matching_rank_ensemble",
            metric_directions={"mae_rank": "asc"},
            min_coverage_rate=0.99,
        )

        self.assertEqual(audit[0]["status"], "pass")
        self.assertEqual(audit[0]["best_method"], "volunteer_matching_rank_ensemble")
        self.assertEqual(audit[0]["excluded_low_coverage_methods"], ["sklearn_ridge"])


if __name__ == "__main__":
    unittest.main()
