import unittest

from major_intel.volunteer_matching.models import AdmissionHistory, PredictionCase
from major_intel.volunteer_matching.residual_router import predict_residual_router


class ResidualRouterTests(unittest.TestCase):
    def test_residual_router_learns_segment_residual_from_pseudo_history(self):
        case = PredictionCase(
            opportunity_key="stable-growth",
            target_year=2025,
            actual_rank=5400,
            actual_score=540,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=1000, cutoff_score=500),
                AdmissionHistory(year=2022, cutoff_rank=2100, cutoff_score=510),
                AdmissionHistory(year=2023, cutoff_rank=3200, cutoff_score=520),
                AdmissionHistory(year=2024, cutoff_rank=4300, cutoff_score=530),
                AdmissionHistory(year=2025, cutoff_rank=5400, cutoff_score=540),
            ],
            metadata={"province_id": "44", "batch": "高职专科批", "opportunity_grain": "school"},
        )

        rows = predict_residual_router(
            [case],
            base_method="last_year_rank",
            min_examples=2,
            shrinkage=1.0,
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["method"], "volunteer_matching_residual_router")
        self.assertEqual(rows[0]["predicted_rank"], 5400)
        self.assertEqual(rows[0]["predicted_score"], 540)
        self.assertEqual(rows[0]["evidence_years"], [2024])
        self.assertIn("residual_router_key=province_id|batch|opportunity_grain", rows[0]["warnings"])
        self.assertIn("residual_examples=3", rows[0]["warnings"])


if __name__ == "__main__":
    unittest.main()
