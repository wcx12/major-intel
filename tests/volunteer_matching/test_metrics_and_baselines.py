import unittest

from major_intel.volunteer_matching.baselines import baseline_names, predict_with_baseline
from major_intel.volunteer_matching.metrics import evaluate_predictions, evaluate_predictions_by_group
from major_intel.volunteer_matching.models import AdmissionHistory, PredictionCase


class MetricsAndBaselineTests(unittest.TestCase):
    def test_registers_at_least_ten_baselines(self):
        names = baseline_names()

        self.assertGreaterEqual(len(names), 10)
        self.assertIn("last_year_rank", names)
        self.assertIn("weighted_recent_rank", names)
        self.assertIn("volunteer_matching_segmented_rank_ensemble", names)

    def test_baselines_predict_without_future_year_leakage(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2023, cutoff_rank=11000, cutoff_score=615, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=620, plan_count=19),
                AdmissionHistory(year=2025, cutoff_rank=9800, cutoff_score=622, plan_count=20),
            ],
        )

        prediction = predict_with_baseline("last_year_rank", case)

        self.assertEqual(prediction.predicted_rank, 10000)
        self.assertEqual(prediction.evidence_years, [2024])

    def test_custom_ensemble_balances_rank_and_calibrates_score_drift(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650, plan_count=19),
            ],
            metadata={"batch": "一段"},
        )

        prediction = predict_with_baseline("volunteer_matching_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 11760)
        self.assertAlmostEqual(prediction.predicted_score, 626.33, places=2)
        self.assertEqual(prediction.evidence_years, [2024, 2023, 2022])

    def test_custom_ensemble_uses_target_year_score_rank_points_when_available(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650, plan_count=19),
            ],
            metadata={
                "province_name": "陕西",
                "batch": "专科批",
                "target_score_rank_points": [{"lowest_rank": 11000, "score": 627}, {"lowest_rank": 12000, "score": 625}],
            },
        )

        prediction = predict_with_baseline("volunteer_matching_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 11760)
        self.assertEqual(prediction.predicted_score, 639)

    def test_custom_ensemble_does_not_use_score_rank_points_for_regular_batches(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650, plan_count=19),
            ],
            metadata={
                "province_name": "浙江",
                "batch": "一段",
                "target_score_rank_points": [{"lowest_rank": 11000, "score": 627}, {"lowest_rank": 12000, "score": 625}],
            },
        )

        prediction = predict_with_baseline("volunteer_matching_rank_ensemble", case)

        self.assertAlmostEqual(prediction.predicted_score, 626.33, places=2)

    def test_custom_ensemble_applies_deep_sparse_history_safety_correction(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2024, cutoff_rank=80000, cutoff_score=550, plan_count=19),
            ],
        )

        prediction = predict_with_baseline("volunteer_matching_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 73250)

    def test_custom_ensemble_leaves_mid_sparse_history_rank_unchanged(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2024, cutoff_rank=50000, cutoff_score=550, plan_count=19),
            ],
        )

        prediction = predict_with_baseline("volunteer_matching_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 50000)

    def test_custom_ensemble_leaves_shallow_sparse_history_rank_unchanged(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2024, cutoff_rank=213, cutoff_score=700, plan_count=2),
            ],
        )

        prediction = predict_with_baseline("volunteer_matching_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 213)

    def test_segmented_rank_ensemble_uses_last_year_for_early_history_slices(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2023,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2020, cutoff_rank=12000, cutoff_score=600),
                AdmissionHistory(year=2021, cutoff_rank=11000, cutoff_score=610),
                AdmissionHistory(year=2022, cutoff_rank=10000, cutoff_score=620),
            ],
        )

        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 10000)

    def test_segmented_rank_ensemble_uses_historical_mean_for_later_volatile_slice(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650, plan_count=19),
            ],
            metadata={"batch": "一段"},
        )

        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 11333)
        self.assertAlmostEqual(prediction.predicted_score, 626.33, places=2)

    def test_segmented_rank_ensemble_keeps_base_rank_for_plan_sorting(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650, plan_count=19),
            ],
            metadata={"batch": "一段"},
        )

        base = predict_with_baseline("volunteer_matching_rank_ensemble", case)
        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 11333)
        self.assertEqual(prediction.planning_rank, base.predicted_rank)

    def test_segmented_rank_ensemble_uses_two_year_score_when_close_to_calibrated_score(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=630, plan_count=19),
            ],
            metadata={"batch": "一段"},
        )

        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(prediction.predicted_score, 625)

    def test_segmented_rank_ensemble_keeps_calibrated_score_when_structured_batch_score_would_drop_too_far(self):
        case = PredictionCase(
            opportunity_key="10336:080901:structured-score",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=626, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=619, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=621, plan_count=19),
            ],
            metadata={
                "province_id": "33",
                "batch": "一段",
                "target_score_rank_points": [{"lowest_rank": 12000, "score": 625}],
            },
        )

        base = predict_with_baseline("volunteer_matching_rank_ensemble", case)
        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(base.predicted_score, 625)
        self.assertEqual(prediction.predicted_score, base.predicted_score)

    def test_segmented_rank_ensemble_keeps_calibrated_score_for_early_score_slices(self):
        case = PredictionCase(
            opportunity_key="10336:080901:guangdong",
            target_year=2023,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2020, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2021, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2022, cutoff_rank=13000, cutoff_score=630, plan_count=19),
            ],
            metadata={"province_name": "广东"},
        )

        base = predict_with_baseline("volunteer_matching_rank_ensemble", case)
        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertAlmostEqual(prediction.predicted_score, base.predicted_score, places=2)

    def test_segmented_rank_ensemble_uses_recent_score_mean_for_guangdong_2022_score_slice(self):
        case = PredictionCase(
            opportunity_key="10336:080901:guangdong-2022",
            target_year=2022,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2018, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2019, cutoff_rank=9000, cutoff_score=640, plan_count=18),
                AdmissionHistory(year=2020, cutoff_rank=13000, cutoff_score=620, plan_count=19),
                AdmissionHistory(year=2021, cutoff_rank=12500, cutoff_score=630, plan_count=19),
            ],
            metadata={"province_id": "44"},
        )

        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(prediction.predicted_score, 630)

    def test_segmented_rank_ensemble_keeps_calibrated_score_for_zhejiang_2024_score_slice(self):
        case = PredictionCase(
            opportunity_key="10336:080901:zhejiang-2024",
            target_year=2024,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2022, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2023, cutoff_rank=13000, cutoff_score=630, plan_count=19),
            ],
            metadata={"province_id": "33", "batch": "一段"},
        )

        base = predict_with_baseline("volunteer_matching_rank_ensemble", case)
        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(prediction.predicted_score, base.predicted_score)

    def test_segmented_rank_ensemble_keeps_calibrated_score_for_second_segment(self):
        case = PredictionCase(
            opportunity_key="10336:080901:zhejiang-second",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=630, plan_count=19),
            ],
            metadata={"province_name": "浙江", "batch": "二段"},
        )

        base = predict_with_baseline("volunteer_matching_rank_ensemble", case)
        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertAlmostEqual(prediction.predicted_score, base.predicted_score, places=2)

    def test_segmented_rank_ensemble_applies_specialty_batch_directional_offset(self):
        case = PredictionCase(
            opportunity_key="10336:080901:陕西:文科:专科批",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650, plan_count=19),
            ],
            metadata={"batch": "专科批"},
        )

        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 7333)

    def test_segmented_rank_ensemble_applies_second_segment_directional_offset(self):
        case = PredictionCase(
            opportunity_key="10336:080901:浙江:综合:二段",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650, plan_count=19),
            ],
            metadata={"batch": "二段"},
        )

        prediction = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)

        self.assertEqual(prediction.predicted_rank, 13833)

    def test_meta_router_keeps_segmented_rank_for_zhejiang_after_major_name_key_fix(self):
        case = PredictionCase(
            opportunity_key="10336:080901:zhejiang-2024",
            target_year=2024,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=18000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2022, cutoff_rank=10000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2023, cutoff_rank=14000, cutoff_score=630, plan_count=19),
            ],
            metadata={"province_id": "33", "province_name": "浙江", "batch": "一段"},
        )

        segmented = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_rank, segmented.predicted_rank)
        self.assertEqual(routed.predicted_score, segmented.predicted_score)
        self.assertIn("rank_expert=volunteer_matching_segmented_rank_ensemble", routed.warnings)

    def test_meta_router_keeps_segmented_rank_for_guangdong_unknown_batch_until_route_is_stable(self):
        case = PredictionCase(
            opportunity_key="10141::44::",
            target_year=2024,
            actual_rank=4705,
            actual_score=670,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=16000, cutoff_score=655, plan_count=20),
                AdmissionHistory(year=2022, cutoff_rank=8000, cutoff_score=665, plan_count=18),
                AdmissionHistory(year=2023, cutoff_rank=10921, cutoff_score=668, plan_count=19),
            ],
            metadata={"province_id": "44", "province_name": "广东", "batch": "UNKNOWN"},
        )

        segmented = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_rank, segmented.predicted_rank)
        self.assertIn("rank_expert=volunteer_matching_segmented_rank_ensemble", routed.warnings)

    def test_meta_router_routes_2024_guangdong_school_undergraduate_to_volatility_expert(self):
        case = PredictionCase(
            opportunity_key="12713::44:physics:本科批",
            target_year=2024,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=16000, cutoff_score=600, plan_count=20),
                AdmissionHistory(year=2022, cutoff_rank=8000, cutoff_score=620, plan_count=18),
                AdmissionHistory(year=2023, cutoff_rank=10921, cutoff_score=630, plan_count=19),
            ],
            metadata={
                "province_id": "44",
                "province_name": "广东",
                "batch": "本科批",
                "opportunity_grain": "school",
            },
        )

        volatility = predict_with_baseline("volatility_conservative_rank", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_rank, volatility.predicted_rank)
        self.assertIn("rank_expert=volatility_conservative_rank", routed.warnings)

    def test_evaluate_predictions_reports_primary_metrics(self):
        rows = [
            {
                "method": "a",
                "actual_rank": 10000,
                "predicted_rank": 9800,
                "actual_score": 620,
                "predicted_score": 621,
            },
            {
                "method": "a",
                "actual_rank": 20000,
                "predicted_rank": 22000,
                "actual_score": 590,
                "predicted_score": 585,
            },
        ]

        metrics = evaluate_predictions(rows)

        self.assertEqual(metrics["a"]["mae_rank"], 1100)
        self.assertEqual(metrics["a"]["mae_score"], 3)
        self.assertEqual(metrics["a"]["within_5_score_points"], 1.0)
        self.assertEqual(metrics["a"]["directional_bias_abs"], 0.0)
        self.assertEqual(metrics["a"]["median_ae_rank"], 1100)
        self.assertGreater(metrics["a"]["rmse_rank"], metrics["a"]["mae_rank"])
        self.assertEqual(metrics["a"]["severe_optimistic_rate"], 0.0)

    def test_evaluate_predictions_reports_severe_optimistic_risk(self):
        rows = [
            {
                "method": "a",
                "actual_rank": 10000,
                "predicted_rank": 14000,
                "actual_score": 620,
                "predicted_score": 610,
            },
            {
                "method": "a",
                "actual_rank": 20000,
                "predicted_rank": 15000,
                "actual_score": 590,
                "predicted_score": 592,
            },
        ]

        metrics = evaluate_predictions(rows)

        self.assertEqual(metrics["a"]["optimistic_error_rate"], 0.5)
        self.assertEqual(metrics["a"]["severe_optimistic_rate"], 0.5)
        self.assertEqual(metrics["a"]["severe_pessimistic_rate"], 0.5)
        self.assertEqual(metrics["a"]["severe_directional_balance_abs"], 0.0)
        self.assertEqual(metrics["a"]["severe_error_rate"], 1.0)

    def test_evaluate_predictions_by_group_keeps_method_metrics_separate(self):
        rows = [
            {
                "method": "a",
                "province_name": "浙江",
                "actual_rank": 10000,
                "predicted_rank": 9800,
                "actual_score": 620,
                "predicted_score": 621,
            },
            {
                "method": "a",
                "province_name": "广东",
                "actual_rank": 20000,
                "predicted_rank": 23000,
                "actual_score": 590,
                "predicted_score": 585,
            },
        ]

        grouped = evaluate_predictions_by_group(rows, ["province_name"])

        self.assertEqual(grouped["province_name=浙江"]["a"]["mae_rank"], 200)
        self.assertEqual(grouped["province_name=广东"]["a"]["mae_rank"], 3000)


    def test_meta_router_offsets_2024_guangdong_school_vocational_rank(self):
        case = PredictionCase(
            opportunity_key="14010::44:history:vocational",
            target_year=2024,
            actual_rank=9800,
            actual_score=227,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=500, plan_count=20),
                AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=460, plan_count=18),
                AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=400, plan_count=19),
            ],
            metadata={
                "province_id": "44",
                "province_name": "\u5e7f\u4e1c",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
            },
        )

        segmented = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_rank, segmented.predicted_rank + 8000)
        self.assertEqual(routed.planning_rank, segmented.planning_rank)
        self.assertIn("rank_offset=guangdong_2024_school_vocational:+8000", routed.warnings)

    def test_meta_router_offsets_guangdong_2022_and_2023_school_vocational_rank(self):
        for target_year, history in (
            (
                2022,
                [AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=500, plan_count=20)],
            ),
            (
                2023,
                [
                    AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=500, plan_count=20),
                    AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=460, plan_count=18),
                ],
            ),
        ):
            case = PredictionCase(
                opportunity_key=f"14010::44:history:vocational:{target_year}",
                target_year=target_year,
                actual_rank=9800,
                actual_score=227,
                history=history,
                metadata={
                    "province_id": "44",
                    "province_name": "\u5e7f\u4e1c",
                    "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                    "opportunity_grain": "school",
                },
            )

            segmented = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)
            routed = predict_with_baseline("volunteer_matching_meta_router", case)

            self.assertEqual(routed.predicted_rank, segmented.predicted_rank + 1000)
            self.assertEqual(routed.planning_rank, segmented.planning_rank)
            self.assertIn(f"rank_offset=guangdong_{target_year}_school_vocational:+1000", routed.warnings)

    def test_meta_router_keeps_segmented_rank_for_2025_zhejiang_second_major(self):
        case = PredictionCase(
            opportunity_key="33010::33:history:second",
            target_year=2025,
            actual_rank=9800,
            actual_score=560,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=550, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=11000, cutoff_score=555, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=558, plan_count=19),
            ],
            metadata={
                "province_id": "33",
                "province_name": "\u6d59\u6c5f",
                "batch": "\u4e8c\u6bb5",
                "opportunity_grain": "major",
            },
        )

        segmented = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_rank, segmented.predicted_rank)
        self.assertEqual(routed.planning_rank, segmented.planning_rank)
        self.assertNotIn("rank_offset=zhejiang_2025_second_major:+1000", routed.warnings)

    def test_meta_router_routes_2024_zhejiang_first_major_rank_to_best_recent(self):
        case = PredictionCase(
            opportunity_key="33010::33:history:first:2024",
            target_year=2024,
            actual_rank=9800,
            actual_score=620,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=12500, cutoff_score=608, plan_count=20),
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=610, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=618, plan_count=19),
            ],
            metadata={
                "province_id": "33",
                "province_name": "\u6d59\u6c5f",
                "batch": "\u4e00\u6bb5",
                "opportunity_grain": "major",
            },
        )

        segmented = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)
        expert = predict_with_baseline("best_recent_rank", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_rank, expert.predicted_rank)
        self.assertEqual(routed.planning_rank, segmented.planning_rank)
        self.assertIn("rank_expert=best_recent_rank", routed.warnings)

    def test_meta_router_routes_2025_zhejiang_first_major_rank_to_exponential_smoothing(self):
        case = PredictionCase(
            opportunity_key="33010::33:history:first:2025",
            target_year=2025,
            actual_rank=9800,
            actual_score=620,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=610, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=11000, cutoff_score=615, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=618, plan_count=19),
            ],
            metadata={
                "province_id": "33",
                "province_name": "\u6d59\u6c5f",
                "batch": "\u4e00\u6bb5",
                "opportunity_grain": "major",
            },
        )

        segmented = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)
        expert = predict_with_baseline("exponential_smoothing_rank", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_rank, expert.predicted_rank)
        self.assertEqual(routed.planning_rank, segmented.planning_rank)
        self.assertIn("rank_expert=exponential_smoothing_rank", routed.warnings)

    def test_meta_router_routes_guangdong_school_vocational_score_to_last_year_score(self):
        case = PredictionCase(
            opportunity_key="14010::44:history:vocational",
            target_year=2024,
            actual_rank=9800,
            actual_score=227,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=500, plan_count=20),
                AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=460, plan_count=18),
                AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=400, plan_count=19),
            ],
            metadata={
                "province_id": "44",
                "province_name": "\u5e7f\u4e1c",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
            },
        )

        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_score, 400)
        self.assertIn("score_expert=last_year_rank", routed.warnings)

    def test_meta_router_routes_guangdong_2022_school_vocational_score_to_rank_ensemble(self):
        case = PredictionCase(
            opportunity_key="14010::44:history:vocational:2022",
            target_year=2022,
            actual_rank=9800,
            actual_score=227,
            history=[
                AdmissionHistory(year=2019, cutoff_rank=15000, cutoff_score=520, plan_count=20),
                AdmissionHistory(year=2020, cutoff_rank=13000, cutoff_score=505, plan_count=20),
                AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=500, plan_count=20),
            ],
            metadata={
                "province_id": "44",
                "province_name": "\u5e7f\u4e1c",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
            },
        )

        expert = predict_with_baseline("volunteer_matching_rank_ensemble", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_score, expert.predicted_score)
        self.assertIn("score_expert=volunteer_matching_rank_ensemble", routed.warnings)

    def test_meta_router_routes_2024_guangdong_undergraduate_score_to_two_year_mean(self):
        case = PredictionCase(
            opportunity_key="14010::44:history:undergraduate",
            target_year=2024,
            actual_rank=9800,
            actual_score=560,
            history=[
                AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=540, plan_count=20),
                AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=550, plan_count=18),
                AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=558, plan_count=19),
            ],
            metadata={
                "province_id": "44",
                "province_name": "\u5e7f\u4e1c",
                "batch": "\u672c\u79d1\u6279",
                "opportunity_grain": "school",
            },
        )

        expert = predict_with_baseline("two_year_mean_rank", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_score, expert.predicted_score)
        self.assertIn("score_expert=two_year_mean_rank", routed.warnings)

    def test_meta_router_routes_2025_zhejiang_first_score_to_weighted_recent(self):
        case = PredictionCase(
            opportunity_key="33010::33:history:first",
            target_year=2025,
            actual_rank=9800,
            actual_score=620,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=610, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=11000, cutoff_score=615, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=618, plan_count=19),
            ],
            metadata={
                "province_id": "33",
                "province_name": "\u6d59\u6c5f",
                "batch": "\u4e00\u6bb5",
                "opportunity_grain": "major",
            },
        )

        expert = predict_with_baseline("weighted_recent_rank", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_score, expert.predicted_score)
        self.assertIn("score_expert=weighted_recent_rank", routed.warnings)

    def test_meta_router_keeps_segmented_score_for_2025_zhejiang_second_major(self):
        case = PredictionCase(
            opportunity_key="33010::33:history:second",
            target_year=2025,
            actual_rank=9800,
            actual_score=560,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=550, plan_count=20),
                AdmissionHistory(year=2023, cutoff_rank=11000, cutoff_score=555, plan_count=18),
                AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=558, plan_count=19),
            ],
            metadata={
                "province_id": "33",
                "province_name": "\u6d59\u6c5f",
                "batch": "\u4e8c\u6bb5",
                "opportunity_grain": "major",
            },
        )

        segmented = predict_with_baseline("volunteer_matching_segmented_rank_ensemble", case)
        routed = predict_with_baseline("volunteer_matching_meta_router", case)

        self.assertEqual(routed.predicted_score, segmented.predicted_score)
        self.assertNotIn("score_expert=best_recent_rank", routed.warnings)


if __name__ == "__main__":
    unittest.main()
