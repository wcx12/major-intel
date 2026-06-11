import unittest
from math import isnan

from major_intel.volunteer_matching.ml_baselines import (
    build_ml_examples,
    ml_baseline_names,
    predict_ml_baselines,
)
from major_intel.volunteer_matching.models import AdmissionHistory, PredictionCase


class MlBaselineTests(unittest.TestCase):
    def test_registers_at_least_ten_strong_ml_baselines(self):
        names = ml_baseline_names()

        self.assertGreaterEqual(len(names), 10)
        self.assertIn("sklearn_random_forest", names)
        self.assertIn("sklearn_hist_gradient_boosting", names)
        self.assertIn("sklearn_ridge", names)
        self.assertIn("xgboost_regressor", names)
        self.assertIn("lightgbm_regressor", names)
        self.assertIn("catboost_regressor", names)
        self.assertIn("tabicl_regressor", names)

    def test_predict_ml_baselines_returns_rows_without_target_year_leakage(self):
        cases = [
            PredictionCase(
                opportunity_key="a",
                target_year=2025,
                actual_rank=9000,
                actual_score=630,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                    AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=610, plan_count=20),
                    AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=620, plan_count=22),
                    AdmissionHistory(year=2024, cutoff_rank=9500, cutoff_score=625, plan_count=22),
                    AdmissionHistory(year=2025, cutoff_rank=9000, cutoff_score=630, plan_count=22),
                ],
            ),
            PredictionCase(
                opportunity_key="b",
                target_year=2025,
                actual_rank=18000,
                actual_score=590,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=22000, cutoff_score=570, plan_count=30),
                    AdmissionHistory(year=2022, cutoff_rank=21000, cutoff_score=575, plan_count=32),
                    AdmissionHistory(year=2023, cutoff_rank=20000, cutoff_score=580, plan_count=34),
                    AdmissionHistory(year=2024, cutoff_rank=19000, cutoff_score=585, plan_count=36),
                    AdmissionHistory(year=2025, cutoff_rank=18000, cutoff_score=590, plan_count=38),
                ],
            ),
        ]

        rows = predict_ml_baselines(cases, methods=["sklearn_ridge", "sklearn_random_forest"])

        self.assertEqual(len(rows), 4)
        self.assertEqual({row["method"] for row in rows}, {"sklearn_ridge", "sklearn_random_forest"})
        self.assertTrue(all(row["target_year"] == 2025 for row in rows))
        self.assertTrue(all(max(row["evidence_years"]) < 2025 for row in rows))
        self.assertTrue(all(row["predicted_rank"] > 0 for row in rows))

    def test_predict_ml_baselines_carries_opportunity_grain_metadata(self):
        cases = [
            PredictionCase(
                opportunity_key="school:a",
                target_year=2025,
                actual_rank=9000,
                actual_score=630,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                    AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=610, plan_count=20),
                    AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=620, plan_count=22),
                    AdmissionHistory(year=2024, cutoff_rank=9500, cutoff_score=625, plan_count=22),
                ],
                metadata={
                    "province_id": "44",
                    "province_name": "广东",
                    "subject_type": "physics",
                    "batch": "本科批",
                    "opportunity_grain": "school",
                },
            ),
            PredictionCase(
                opportunity_key="major:b",
                target_year=2025,
                actual_rank=18000,
                actual_score=590,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=22000, cutoff_score=570, plan_count=30),
                    AdmissionHistory(year=2022, cutoff_rank=21000, cutoff_score=575, plan_count=32),
                    AdmissionHistory(year=2023, cutoff_rank=20000, cutoff_score=580, plan_count=34),
                    AdmissionHistory(year=2024, cutoff_rank=19000, cutoff_score=585, plan_count=36),
                ],
                metadata={
                    "province_id": "33",
                    "province_name": "浙江",
                    "subject_type": "comprehensive",
                    "batch": "一段",
                    "opportunity_grain": "major",
                },
            ),
        ]

        rows = predict_ml_baselines(cases, methods=["sklearn_ridge"])

        by_key = {row["opportunity_key"]: row for row in rows}
        self.assertEqual(by_key["school:a"]["opportunity_grain"], "school")
        self.assertEqual(by_key["major:b"]["opportunity_grain"], "major")

    def test_ml_features_include_case_metadata(self):
        history = [
            AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=600, plan_count=20),
            AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=610, plan_count=20),
            AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=620, plan_count=22),
            AdmissionHistory(year=2024, cutoff_rank=9500, cutoff_score=625, plan_count=22),
        ]
        cases = [
            PredictionCase(
                opportunity_key="school:a",
                target_year=2025,
                actual_rank=9000,
                actual_score=630,
                history=history,
                metadata={
                    "province_id": "44",
                    "subject_type": "physics",
                    "batch": "本科批",
                    "opportunity_grain": "school",
                },
            ),
            PredictionCase(
                opportunity_key="major:a",
                target_year=2025,
                actual_rank=9000,
                actual_score=630,
                history=history,
                metadata={
                    "province_id": "33",
                    "subject_type": "comprehensive",
                    "batch": "一段",
                    "opportunity_grain": "major",
                },
            ),
        ]

        _, targets = build_ml_examples(cases)

        self.assertEqual(len(targets), 2)
        self.assertNotEqual(targets[0].features, targets[1].features)

    def test_ml_features_do_not_emit_nan_for_missing_plan_counts(self):
        cases = [
            PredictionCase(
                opportunity_key="a",
                target_year=2025,
                actual_rank=9000,
                actual_score=630,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=600, plan_count=None),
                    AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=610, plan_count=None),
                    AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=620, plan_count=None),
                    AdmissionHistory(year=2024, cutoff_rank=9500, cutoff_score=625, plan_count=None),
                ],
            )
        ]

        training, targets = build_ml_examples(cases)

        all_features = [item.features for item in training] + [item.features for item in targets]
        self.assertTrue(all_features)
        self.assertFalse(any(isnan(value) for features in all_features for value in features))


if __name__ == "__main__":
    unittest.main()
