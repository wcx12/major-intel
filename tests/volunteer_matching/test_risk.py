import unittest

from major_intel.volunteer_matching.models import (
    AdmissionHistory,
    ApplicantContext,
    Opportunity,
)
from major_intel.volunteer_matching.risk import predict_rank_cutoff, risk_bucket


class VolunteerRiskTests(unittest.TestCase):
    def test_predict_rank_cutoff_uses_recent_weighted_history(self):
        history = [
            AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=610, plan_count=20),
            AdmissionHistory(year=2023, cutoff_rank=11000, cutoff_score=615, plan_count=18),
            AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=620, plan_count=19),
        ]

        prediction = predict_rank_cutoff(history, target_year=2025)

        self.assertEqual(prediction.predicted_rank, 10600)
        self.assertEqual(prediction.evidence_years, [2024, 2023, 2022])
        self.assertGreater(prediction.confidence, 0)
        self.assertLessEqual(prediction.confidence, 1)

    def test_risk_bucket_respects_rank_direction(self):
        applicant = ApplicantContext(
            province="浙江",
            subject_type="综合",
            year=2025,
            rank=9500,
            score=625,
            preferred_majors=["计算机科学与技术"],
        )
        opportunity = Opportunity(
            school_id="10336",
            school_name="杭州电子科技大学",
            major_code="080901",
            major_name="计算机科学与技术",
            province="浙江",
            subject_type="综合",
            batch="本科批",
            plan_count=20,
        )

        decision = risk_bucket(applicant, opportunity, predicted_rank=10000, confidence=0.8)

        self.assertEqual(decision.bucket, "wen")
        self.assertEqual(decision.rank_gap, 500)
        self.assertTrue(decision.is_admissible_reference)


if __name__ == "__main__":
    unittest.main()
