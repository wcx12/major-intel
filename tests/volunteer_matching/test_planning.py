import unittest

from major_intel.volunteer_matching.planning import (
    build_rank_plan,
    build_method_rank_plan,
    evaluate_rank_plans,
    synthetic_applicant_ranks,
)


class PlanningTests(unittest.TestCase):
    def test_synthetic_applicant_ranks_use_quantiles_inside_observed_range(self):
        predictions = [
            {"actual_rank": 1000},
            {"actual_rank": 2000},
            {"actual_rank": 3000},
            {"actual_rank": 4000},
            {"actual_rank": 5000},
        ]

        ranks = synthetic_applicant_ranks(predictions, count=3)

        self.assertEqual(ranks, [2000, 3000, 4000])

    def test_build_rank_plan_respects_bucket_quotas_and_scores_close_options_first(self):
        predictions = [
            {"method": "m", "opportunity_key": "reach", "predicted_rank": 9000, "actual_rank": 8500},
            {"method": "m", "opportunity_key": "stable", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "m", "opportunity_key": "safe", "predicted_rank": 15000, "actual_rank": 16000},
            {"method": "m", "opportunity_key": "safe_far", "predicted_rank": 30000, "actual_rank": 32000},
        ]

        plan = build_rank_plan(predictions, applicant_rank=10000, total_slots=3, bucket_quotas={"chong": 1, "wen": 1, "bao": 1})

        self.assertEqual([item["bucket"] for item in plan], ["chong", "wen", "bao"])
        self.assertEqual([item["opportunity_key"] for item in plan], ["reach", "stable", "safe"])

    def test_build_rank_plan_deduplicates_opportunities_before_filling_remaining_slots(self):
        predictions = [
            {"method": "m", "opportunity_key": "same", "predicted_rank": 15000, "actual_rank": 16000},
            {"method": "m", "opportunity_key": "same", "predicted_rank": 15100, "actual_rank": 16100},
            {"method": "m", "opportunity_key": "other", "predicted_rank": 15200, "actual_rank": 16200},
        ]

        plan = build_rank_plan(predictions, applicant_rank=10000, total_slots=3, bucket_quotas={"chong": 0, "wen": 0, "bao": 3})

        self.assertEqual(len(plan), 2)
        self.assertEqual({item["opportunity_key"] for item in plan}, {"same", "other"})

    def test_build_rank_plan_backfills_bucket_quota_after_deduplication(self):
        predictions = [
            {"method": "m", "opportunity_key": "stable", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "m", "opportunity_key": "stable_extra", "predicted_rank": 11100, "actual_rank": 12100},
            {"method": "m", "opportunity_key": "safe_a", "predicted_rank": 18000, "actual_rank": 19000},
            {"method": "m", "opportunity_key": "safe_a", "predicted_rank": 18100, "actual_rank": 19100},
            {"method": "m", "opportunity_key": "safe_b", "predicted_rank": 17500, "actual_rank": 18500},
            {"method": "m", "opportunity_key": "safe_c", "predicted_rank": 17000, "actual_rank": 18000},
        ]

        plan = build_rank_plan(
            predictions,
            applicant_rank=10000,
            total_slots=4,
            bucket_quotas={"chong": 0, "wen": 1, "bao": 3},
        )

        self.assertEqual([item["bucket"] for item in plan].count("wen"), 1)
        self.assertEqual([item["bucket"] for item in plan].count("bao"), 3)
        self.assertEqual({item["opportunity_key"] for item in plan if item["bucket"] == "bao"}, {"safe_a", "safe_b", "safe_c"})

    def test_volunteer_matching_method_uses_safety_first_bucket_mix(self):
        predictions = [
            {"method": "volunteer_matching_rank_ensemble", "opportunity_key": "reach", "predicted_rank": 9000, "actual_rank": 8500},
            {"method": "volunteer_matching_rank_ensemble", "opportunity_key": "stable_a", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "volunteer_matching_rank_ensemble", "opportunity_key": "stable_b", "predicted_rank": 11500, "actual_rank": 12200},
            {"method": "volunteer_matching_rank_ensemble", "opportunity_key": "safe_a", "predicted_rank": 15000, "actual_rank": 16000},
            {"method": "volunteer_matching_rank_ensemble", "opportunity_key": "safe_b", "predicted_rank": 15500, "actual_rank": 16500},
            {"method": "volunteer_matching_rank_ensemble", "opportunity_key": "safe_c", "predicted_rank": 16000, "actual_rank": 17000},
            {"method": "volunteer_matching_rank_ensemble", "opportunity_key": "safe_d", "predicted_rank": 16500, "actual_rank": 17500},
        ]

        plan = build_method_rank_plan("volunteer_matching_rank_ensemble", predictions, applicant_rank=10000, total_slots=5)

        self.assertNotIn("chong", {item["bucket"] for item in plan})
        self.assertEqual(sum(1 for item in plan if item["bucket"] == "wen"), 1)
        self.assertEqual(sum(1 for item in plan if item["bucket"] == "bao"), 4)

    def test_segmented_volunteer_matching_method_uses_safety_first_bucket_mix(self):
        predictions = [
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "reach", "predicted_rank": 9000, "actual_rank": 8500},
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "stable_a", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "stable_b", "predicted_rank": 11500, "actual_rank": 12200},
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "safe_a", "predicted_rank": 15000, "actual_rank": 16000},
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "safe_b", "predicted_rank": 15500, "actual_rank": 16500},
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "safe_c", "predicted_rank": 16000, "actual_rank": 17000},
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "safe_d", "predicted_rank": 16500, "actual_rank": 17500},
        ]

        plan = build_method_rank_plan("volunteer_matching_segmented_rank_ensemble", predictions, applicant_rank=10000, total_slots=5)

        self.assertNotIn("chong", {item["bucket"] for item in plan})
        self.assertEqual(sum(1 for item in plan if item["bucket"] == "wen"), 1)
        self.assertEqual(sum(1 for item in plan if item["bucket"] == "bao"), 4)

    def test_meta_router_method_uses_safety_first_bucket_mix(self):
        predictions = [
            {"method": "volunteer_matching_meta_router", "opportunity_key": "reach", "predicted_rank": 9000, "actual_rank": 8500},
            {"method": "volunteer_matching_meta_router", "opportunity_key": "stable_a", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "volunteer_matching_meta_router", "opportunity_key": "stable_b", "predicted_rank": 11500, "actual_rank": 12200},
            {"method": "volunteer_matching_meta_router", "opportunity_key": "safe_a", "predicted_rank": 15000, "actual_rank": 16000},
            {"method": "volunteer_matching_meta_router", "opportunity_key": "safe_b", "predicted_rank": 15500, "actual_rank": 16500},
            {"method": "volunteer_matching_meta_router", "opportunity_key": "safe_c", "predicted_rank": 16000, "actual_rank": 17000},
            {"method": "volunteer_matching_meta_router", "opportunity_key": "safe_d", "predicted_rank": 16500, "actual_rank": 17500},
        ]

        plan = build_method_rank_plan("volunteer_matching_meta_router", predictions, applicant_rank=10000, total_slots=5)

        self.assertNotIn("chong", {item["bucket"] for item in plan})
        self.assertEqual(sum(1 for item in plan if item["bucket"] == "wen"), 1)
        self.assertEqual(sum(1 for item in plan if item["bucket"] == "bao"), 4)

    def test_segmented_volunteer_matching_prefers_useful_safe_gap_over_far_safe_gap(self):
        predictions = [
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "stable", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "safe_near", "predicted_rank": 14000, "actual_rank": 14000},
            {"method": "volunteer_matching_segmented_rank_ensemble", "opportunity_key": "safe_far", "predicted_rank": 18000, "actual_rank": 18000},
        ]

        plan = build_method_rank_plan("volunteer_matching_segmented_rank_ensemble", predictions, applicant_rank=10000, total_slots=3)

        self.assertEqual([item["opportunity_key"] for item in plan], ["stable", "safe_near", "safe_far"])

    def test_rank_plan_uses_planning_rank_when_available(self):
        predictions = [
            {
                "method": "m",
                "opportunity_key": "display_far_plan_near",
                "predicted_rank": 18000,
                "planning_rank": 14000,
                "actual_rank": 14000,
            },
            {
                "method": "m",
                "opportunity_key": "display_near_plan_far",
                "predicted_rank": 14000,
                "planning_rank": 18000,
                "actual_rank": 18000,
            },
        ]

        plan = build_rank_plan(predictions, applicant_rank=10000, total_slots=2, bucket_quotas={"chong": 0, "wen": 0, "bao": 2}, sort_targets={"bao": 4000})

        self.assertEqual(plan[0]["opportunity_key"], "display_far_plan_near")
        self.assertEqual(plan[0]["predicted_gap"], 4000)

    def test_evaluate_rank_plans_reports_admissibility_and_first_safe_position(self):
        predictions = [
            {"method": "good", "opportunity_key": "a", "predicted_rank": 9000, "actual_rank": 8500},
            {"method": "good", "opportunity_key": "b", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "good", "opportunity_key": "c", "predicted_rank": 15000, "actual_rank": 16000},
            {"method": "bad", "opportunity_key": "a", "predicted_rank": 15000, "actual_rank": 8500},
            {"method": "bad", "opportunity_key": "b", "predicted_rank": 9000, "actual_rank": 8500},
            {"method": "bad", "opportunity_key": "c", "predicted_rank": 11000, "actual_rank": 9000},
        ]

        metrics = evaluate_rank_plans(
            predictions,
            applicant_ranks=[10000],
            total_slots=2,
            bucket_quotas={"chong": 1, "wen": 1, "bao": 0},
        )

        self.assertEqual(metrics["good"]["plan_count"], 1)
        self.assertEqual(metrics["good"]["admissible_rate"], 0.5)
        self.assertEqual(metrics["good"]["first_admissible_position_mean"], 2)
        self.assertGreater(metrics["good"]["ndcg"], metrics["bad"]["ndcg"])

    def test_evaluate_rank_plans_reports_whole_plan_failure_and_utility(self):
        predictions = [
            {"method": "useful", "opportunity_key": "reach", "predicted_rank": 9000, "actual_rank": 8500},
            {"method": "useful", "opportunity_key": "stable", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "useful", "opportunity_key": "best_available", "predicted_rank": 16000, "actual_rank": 13000},
            {"method": "no_offer", "opportunity_key": "miss_a", "predicted_rank": 9000, "actual_rank": 8500},
            {"method": "no_offer", "opportunity_key": "miss_b", "predicted_rank": 9500, "actual_rank": 9000},
        ]

        metrics = evaluate_rank_plans(
            predictions,
            applicant_ranks=[10000],
            total_slots=2,
            bucket_quotas={"chong": 1, "wen": 1, "bao": 0},
        )

        self.assertEqual(metrics["useful"]["no_offer_rate"], 0.0)
        self.assertEqual(metrics["useful"]["expected_utility"], 0.4545)
        self.assertEqual(metrics["useful"]["regret"], 0.0909)
        self.assertIsNone(metrics["useful"]["safety_gated_regret"])
        self.assertEqual(metrics["no_offer"]["no_offer_rate"], 1.0)
        self.assertEqual(metrics["no_offer"]["expected_utility"], 0.0)
        self.assertEqual(metrics["no_offer"]["regret"], 0.0)
        self.assertIsNone(metrics["no_offer"]["safety_gated_regret"])

    def test_safety_gated_regret_ignores_low_regret_unsafe_plans(self):
        predictions = [
            {"method": "safe", "opportunity_key": "safe_a", "predicted_rank": 11000, "actual_rank": 12000},
            {"method": "safe", "opportunity_key": "safe_b", "predicted_rank": 12000, "actual_rank": 12500},
            {"method": "safe", "opportunity_key": "best_available", "predicted_rank": 16000, "actual_rank": 13000},
            {"method": "unsafe", "opportunity_key": "reach", "predicted_rank": 9000, "actual_rank": 9000},
            {"method": "unsafe", "opportunity_key": "best", "predicted_rank": 13000, "actual_rank": 13000},
        ]

        metrics = evaluate_rank_plans(
            predictions,
            applicant_ranks=[10000],
            total_slots=2,
            bucket_quotas={"chong": 1, "wen": 1, "bao": 0},
        )

        self.assertEqual(metrics["safe"]["no_offer_rate"], 0.0)
        self.assertEqual(metrics["safe"]["admissible_rate"], 1.0)
        self.assertIsNotNone(metrics["safe"]["safety_gated_regret"])
        self.assertLess(metrics["unsafe"]["regret"], metrics["safe"]["regret"])
        self.assertIsNone(metrics["unsafe"]["safety_gated_regret"])


if __name__ == "__main__":
    unittest.main()
