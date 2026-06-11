import unittest

from major_intel.volunteer_matching.benchmark import (
    PREDICTION_LEADERSHIP_TOLERANCES,
    PREDICTION_EXPERT_ROUTER_METHOD,
    _append_prediction_expert_router,
    build_case_residual_audit,
    render_markdown_report,
    run_benchmark,
    run_multi_year_benchmark,
)
from major_intel.volunteer_matching.models import AdmissionHistory, PredictionCase


class BenchmarkTests(unittest.TestCase):
    def test_prediction_leadership_tolerates_tiny_severe_balance_rate_differences(self):
        self.assertEqual(PREDICTION_LEADERSHIP_TOLERANCES["severe_directional_balance_abs"], 0.002)

    def test_prediction_leadership_uses_practical_error_tolerances(self):
        self.assertEqual(PREDICTION_LEADERSHIP_TOLERANCES["mae_rank"], 250)
        self.assertEqual(PREDICTION_LEADERSHIP_TOLERANCES["p90_ae_rank"], 500)
        self.assertEqual(PREDICTION_LEADERSHIP_TOLERANCES["mae_score"], 0.5)
        self.assertEqual(PREDICTION_LEADERSHIP_TOLERANCES["within_5_score_points"], 0.02)

    def test_run_benchmark_returns_one_prediction_per_method_and_metrics(self):
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

        result = run_benchmark([case], methods=["last_year_rank", "weighted_recent_rank"])

        self.assertEqual(len(result["predictions"]), 2)
        self.assertEqual({row["method"] for row in result["predictions"]}, {"last_year_rank", "weighted_recent_rank"})
        self.assertEqual(result["predictions"][0]["actual_rank"], 9800)
        self.assertIn("last_year_rank", result["metrics"])
        self.assertIn("mae_rank", result["metrics"]["last_year_rank"])
        self.assertEqual(result["metrics"]["last_year_rank"]["coverage_rate"], 1.0)

    def test_run_benchmark_can_include_ml_baselines(self):
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
                ],
            ),
        ]

        result = run_benchmark(
            cases,
            methods=["last_year_rank"],
            include_ml=True,
            ml_methods=["sklearn_ridge"],
        )

        self.assertEqual({row["method"] for row in result["predictions"]}, {"last_year_rank", "sklearn_ridge"})
        self.assertIn("sklearn_ridge", result["metrics"])

    def test_run_benchmark_can_include_residual_router(self):
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

        result = run_benchmark(
            [case],
            methods=["last_year_rank"],
            include_residual_router=True,
            residual_base_method="last_year_rank",
            residual_min_examples=2,
            residual_shrinkage=1.0,
        )

        self.assertEqual({row["method"] for row in result["predictions"]}, {"last_year_rank", "volunteer_matching_residual_router"})
        self.assertEqual(result["metrics"]["volunteer_matching_residual_router"]["mae_rank"], 0)

    def test_residual_router_does_not_displace_meta_router_primary_method(self):
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

        result = run_benchmark(
            [case],
            methods=["volunteer_matching_meta_router"],
            include_residual_router=True,
            residual_min_examples=2,
            residual_shrinkage=1.0,
        )

        self.assertEqual(result["leadership_audit"]["prediction_metrics"][0]["primary_method"], "volunteer_matching_meta_router")

    def test_prediction_expert_router_adds_tabicl_score_for_2023_guangdong_vocational(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "gd-voc",
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "subject_type": "history",
                "predicted_rank": 10000,
                "planning_rank": 9800,
                "predicted_score": 410,
                "warnings": ["score_expert=last_year_rank"],
            },
            {
                "method": "tabicl_regressor",
                "opportunity_key": "gd-voc",
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "subject_type": "history",
                "predicted_rank": 9900,
                "planning_rank": 9900,
                "predicted_score": 398.5,
                "warnings": [],
            },
        ]

        _append_prediction_expert_router(predictions)

        self.assertEqual(predictions[0]["predicted_score"], 410)
        self.assertEqual(predictions[0]["predicted_rank"], 10000)
        routed = [row for row in predictions if row["method"] == PREDICTION_EXPERT_ROUTER_METHOD]
        self.assertEqual(len(routed), 1)
        self.assertEqual(routed[0]["predicted_score"], 398.5)
        self.assertEqual(routed[0]["predicted_rank"], 9960)
        self.assertEqual(routed[0]["planning_rank"], 9800)
        self.assertIn("route=gd_2023_history_vocational_tabicl_score:score=tabicl_regressor", routed[0]["warnings"])
        self.assertIn(
            "route=gd_2023_vocational_tabicl_rank_blend:rank=tabicl_regressor:weight=0.4:planning=base",
            routed[0]["warnings"],
        )

    def test_prediction_expert_router_skips_tabicl_score_for_2023_guangdong_physics_vocational(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "gd-physics-voc",
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "subject_type": "physics",
                "predicted_rank": 10000,
                "planning_rank": 9800,
                "predicted_score": 410,
                "warnings": ["score_expert=last_year_rank"],
            },
            {
                "method": "tabicl_regressor",
                "opportunity_key": "gd-physics-voc",
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "subject_type": "physics",
                "predicted_rank": 9900,
                "planning_rank": 9900,
                "predicted_score": 398.5,
                "warnings": [],
            },
        ]

        _append_prediction_expert_router(predictions)

        routed = [row for row in predictions if row["method"] == PREDICTION_EXPERT_ROUTER_METHOD]
        self.assertEqual(len(routed), 1)
        self.assertEqual(routed[0]["predicted_score"], 410)
        self.assertEqual(routed[0]["predicted_rank"], 9966)
        self.assertEqual(routed[0]["planning_rank"], 9800)
        self.assertNotIn("route=gd_2023_history_vocational_tabicl_score:score=tabicl_regressor", routed[0]["warnings"])
        self.assertIn(
            "route=gd_2023_vocational_tabicl_rank_blend:rank=tabicl_regressor:weight=0.4:planning=base",
            routed[0]["warnings"],
        )
        self.assertIn(
            "route=physics_meta_rank_blend:rank=volunteer_matching_meta_router:weight=0.15:planning=base",
            routed[0]["warnings"],
        )

    def test_prediction_expert_router_blends_liberal_arts_score_back_toward_meta_router(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "arts-case",
                "target_year": 2025,
                "subject_type": "\u6587\u79d1",
                "predicted_rank": 10000,
                "predicted_score": 510,
                "warnings": [],
            },
            {
                "method": "sklearn_ridge",
                "opportunity_key": "arts-case",
                "target_year": 2025,
                "subject_type": "\u6587\u79d1",
                "predicted_rank": 9900,
                "predicted_score": 506.25,
                "warnings": [],
            },
        ]

        _append_prediction_expert_router(predictions)

        routed = [row for row in predictions if row["method"] == PREDICTION_EXPERT_ROUTER_METHOD]
        self.assertEqual(len(routed), 1)
        self.assertEqual(routed[0]["predicted_score"], 507.75)
        self.assertEqual(routed[0]["predicted_rank"], 10000)
        self.assertIn("route=liberal_arts_ridge_score:score=sklearn_ridge", routed[0]["warnings"])
        self.assertIn(
            "route=liberal_arts_meta_score_blend:score=volunteer_matching_meta_router:weight=0.4",
            routed[0]["warnings"],
        )

    def test_prediction_expert_router_is_not_added_when_expert_is_missing(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "gd-voc",
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "predicted_rank": 10000,
                "predicted_score": 410,
                "warnings": [],
            }
        ]

        _append_prediction_expert_router(predictions)

        self.assertEqual(predictions[0]["predicted_score"], 410)
        self.assertEqual(predictions[0]["warnings"], [])
        self.assertEqual({row["method"] for row in predictions}, {"volunteer_matching_meta_router"})

    def test_prediction_expert_router_force_adds_full_coverage_clone_when_expert_is_missing(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "plain-case",
                "target_year": 2022,
                "predicted_rank": 10000,
                "predicted_score": 610,
                "warnings": ["rank_expert=volunteer_matching_segmented_rank_ensemble"],
            }
        ]

        _append_prediction_expert_router(predictions, force=True)

        routed = [row for row in predictions if row["method"] == PREDICTION_EXPERT_ROUTER_METHOD]
        self.assertEqual(len(routed), 1)
        self.assertEqual(routed[0]["opportunity_key"], "plain-case")
        self.assertEqual(routed[0]["predicted_score"], 610)
        self.assertEqual(routed[0]["warnings"], ["rank_expert=volunteer_matching_segmented_rank_ensemble"])

    def test_prediction_expert_router_is_reported_as_primary_when_ml_is_enabled(self):
        cases = [
            PredictionCase(
                opportunity_key="arts-a",
                target_year=2025,
                actual_rank=9000,
                actual_score=630,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=600),
                    AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=610),
                    AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=620),
                    AdmissionHistory(year=2024, cutoff_rank=9500, cutoff_score=625),
                ],
                metadata={"subject_type": "\u6587\u79d1"},
            ),
            PredictionCase(
                opportunity_key="arts-b",
                target_year=2025,
                actual_rank=18000,
                actual_score=590,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=22000, cutoff_score=570),
                    AdmissionHistory(year=2022, cutoff_rank=21000, cutoff_score=575),
                    AdmissionHistory(year=2023, cutoff_rank=20000, cutoff_score=580),
                    AdmissionHistory(year=2024, cutoff_rank=19000, cutoff_score=585),
                ],
                metadata={"subject_type": "\u6587\u79d1"},
            ),
        ]

        result = run_benchmark(
            cases,
            methods=["volunteer_matching_meta_router"],
            include_ml=True,
            ml_methods=["sklearn_ridge"],
        )

        self.assertIn(PREDICTION_EXPERT_ROUTER_METHOD, result["methods"])
        self.assertEqual(result["method_count"], len(result["metrics"]))
        self.assertEqual(
            result["leadership_audit"]["prediction_metrics"][0]["primary_method"],
            PREDICTION_EXPERT_ROUTER_METHOD,
        )

    def test_run_benchmark_keeps_other_ml_methods_when_one_ml_method_fails(self):
        cases = [
            PredictionCase(
                opportunity_key="a",
                target_year=2025,
                actual_rank=9000,
                actual_score=630,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=12000, cutoff_score=600),
                    AdmissionHistory(year=2022, cutoff_rank=11000, cutoff_score=610),
                    AdmissionHistory(year=2023, cutoff_rank=10000, cutoff_score=620),
                    AdmissionHistory(year=2024, cutoff_rank=9500, cutoff_score=625),
                ],
            ),
            PredictionCase(
                opportunity_key="b",
                target_year=2025,
                actual_rank=18000,
                actual_score=590,
                history=[
                    AdmissionHistory(year=2021, cutoff_rank=22000, cutoff_score=570),
                    AdmissionHistory(year=2022, cutoff_rank=21000, cutoff_score=575),
                    AdmissionHistory(year=2023, cutoff_rank=20000, cutoff_score=580),
                    AdmissionHistory(year=2024, cutoff_rank=19000, cutoff_score=585),
                ],
            ),
        ]

        result = run_benchmark(
            cases,
            methods=["last_year_rank"],
            include_ml=True,
            ml_methods=["sklearn_ridge", "missing_ml_method"],
        )

        self.assertIn("sklearn_ridge", {row["method"] for row in result["predictions"]})
        self.assertIn("sklearn_ridge", result["metrics"])
        self.assertEqual(result["errors"][0]["method"], "missing_ml_method")

    def test_markdown_report_includes_directional_bias_metric(self):
        result = {
            "case_count": 1,
            "method_count": 1,
            "predictions": [],
            "errors": [],
            "metrics": {
                "method_a": {
                    "row_count": 1,
                    "coverage_rate": 1.0,
                    "mae_rank": 10,
                    "median_ae_rank": 9,
                    "p90_ae_rank": 12,
                    "rmse_rank": 11,
                    "mae_score": 1,
                    "median_ae_score": 1,
                    "p90_ae_score": 2,
                    "rmse_score": 1.5,
                    "within_3_score_points": 1.0,
                    "within_5_score_points": 1.0,
                    "within_10_score_points": 1.0,
                    "directional_bias_abs": 0.0,
                    "overestimate_risk_rate": 0.5,
                    "severe_error_rate": 0.0,
                    "severe_directional_balance_abs": 0.0,
                }
            },
        }

        markdown = render_markdown_report(result)

        self.assertIn("Directional Bias", markdown)
        self.assertIn("Median AE Rank", markdown)
        self.assertIn("P90 AE Score", markdown)
        self.assertIn("Within 3 Score", markdown)
        self.assertIn("Severe Error", markdown)
        self.assertIn("Coverage", markdown)
        self.assertIn("| method_a |", markdown)

    def test_run_benchmark_carries_case_group_metadata(self):
        case = PredictionCase(
            opportunity_key="zhejiang:a",
            target_year=2025,
            actual_rank=9800,
            actual_score=622,
            history=[
                AdmissionHistory(year=2023, cutoff_rank=11000, cutoff_score=615),
                AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=620),
            ],
            metadata={"province_name": "浙江", "subject_type": "综合", "batch": "本科批"},
        )

        result = run_benchmark([case], methods=["last_year_rank"])

        self.assertEqual(result["predictions"][0]["province_name"], "浙江")
        self.assertEqual(result["predictions"][0]["subject_type"], "综合")
        self.assertEqual(result["predictions"][0]["batch"], "本科批")

    def test_run_benchmark_groups_by_opportunity_grain(self):
        cases = [
            PredictionCase(
                opportunity_key="school-level",
                target_year=2025,
                actual_rank=10000,
                actual_score=620,
                history=[AdmissionHistory(year=2024, cutoff_rank=9000, cutoff_score=615)],
                metadata={"opportunity_grain": "school"},
            ),
            PredictionCase(
                opportunity_key="major-level",
                target_year=2025,
                actual_rank=20000,
                actual_score=590,
                history=[AdmissionHistory(year=2024, cutoff_rank=21000, cutoff_score=585)],
                metadata={"opportunity_grain": "major"},
            ),
        ]

        result = run_benchmark(cases, methods=["last_year_rank", "volunteer_matching_rank_ensemble"])

        self.assertEqual(result["predictions"][0]["opportunity_grain"], "school")
        self.assertIn("opportunity_grain", result["group_metrics"])
        self.assertIn("opportunity_grain=school", result["slice_leadership_audit"]["opportunity_grain"])

    def test_run_benchmark_can_include_plan_level_metrics(self):
        cases = [
            PredictionCase(
                opportunity_key="a",
                target_year=2025,
                actual_rank=8500,
                actual_score=630,
                history=[AdmissionHistory(year=2024, cutoff_rank=9000, cutoff_score=625)],
            ),
            PredictionCase(
                opportunity_key="b",
                target_year=2025,
                actual_rank=12000,
                actual_score=620,
                history=[AdmissionHistory(year=2024, cutoff_rank=11000, cutoff_score=615)],
            ),
            PredictionCase(
                opportunity_key="c",
                target_year=2025,
                actual_rank=16000,
                actual_score=610,
                history=[AdmissionHistory(year=2024, cutoff_rank=15000, cutoff_score=605)],
            ),
        ]

        result = run_benchmark(
            cases,
            methods=["last_year_rank"],
            include_planning=True,
            planning_applicant_ranks=[10000],
        )

        self.assertIn("plan_metrics", result)
        self.assertIn("last_year_rank", result["plan_metrics"])
        self.assertEqual(result["plan_metrics"]["last_year_rank"]["plan_count"], 1)

    def test_plan_report_and_audit_include_whole_plan_metrics(self):
        cases = [
            PredictionCase(
                opportunity_key="reach",
                target_year=2025,
                actual_rank=8500,
                actual_score=630,
                history=[AdmissionHistory(year=2024, cutoff_rank=9000, cutoff_score=625)],
            ),
            PredictionCase(
                opportunity_key="stable",
                target_year=2025,
                actual_rank=12000,
                actual_score=620,
                history=[AdmissionHistory(year=2024, cutoff_rank=11000, cutoff_score=615)],
            ),
            PredictionCase(
                opportunity_key="best_available",
                target_year=2025,
                actual_rank=13000,
                actual_score=618,
                history=[AdmissionHistory(year=2024, cutoff_rank=16000, cutoff_score=610)],
            ),
        ]

        result = run_benchmark(
            cases,
            methods=["last_year_rank", "volunteer_matching_rank_ensemble"],
            include_planning=True,
            planning_applicant_ranks=[10000],
            planning_slots=2,
        )

        audit_metrics = {row["metric"] for row in result["leadership_audit"]["plan_metrics"]}
        self.assertIn("no_offer_rate", audit_metrics)
        self.assertIn("expected_utility", audit_metrics)
        self.assertIn("safety_gated_regret", audit_metrics)
        self.assertNotIn("regret", audit_metrics)

        markdown = render_markdown_report(result)
        self.assertIn("No Offer", markdown)
        self.assertIn("Expected Utility", markdown)
        self.assertIn("Regret", markdown)

    def test_plan_leadership_uses_safety_gated_regret(self):
        cases = [
            PredictionCase(
                opportunity_key="safe_a",
                target_year=2025,
                actual_rank=12000,
                actual_score=620,
                history=[AdmissionHistory(year=2024, cutoff_rank=11000, cutoff_score=615)],
            ),
            PredictionCase(
                opportunity_key="safe_b",
                target_year=2025,
                actual_rank=13000,
                actual_score=618,
                history=[AdmissionHistory(year=2024, cutoff_rank=12000, cutoff_score=612)],
            ),
            PredictionCase(
                opportunity_key="reach",
                target_year=2025,
                actual_rank=9000,
                actual_score=630,
                history=[AdmissionHistory(year=2024, cutoff_rank=9000, cutoff_score=628)],
            ),
        ]

        result = run_benchmark(
            cases,
            methods=["volunteer_matching_rank_ensemble", "last_year_rank"],
            include_planning=True,
            planning_applicant_ranks=[10000],
            planning_slots=2,
        )

        audit_by_metric = {row["metric"]: row for row in result["leadership_audit"]["plan_metrics"]}

        self.assertEqual(audit_by_metric["safety_gated_regret"]["primary_method"], "volunteer_matching_rank_ensemble")
        self.assertIn(audit_by_metric["safety_gated_regret"]["status"], {"pass", "fail"})

    def test_run_benchmark_includes_leadership_audit_for_custom_method(self):
        case = PredictionCase(
            opportunity_key="zhejiang:a",
            target_year=2025,
            actual_rank=13000,
            actual_score=620,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650),
            ],
        )

        result = run_benchmark([case], methods=["last_year_rank", "volunteer_matching_rank_ensemble"])

        self.assertIn("leadership_audit", result)
        audit_by_metric = {row["metric"]: row for row in result["leadership_audit"]["prediction_metrics"]}
        self.assertEqual(audit_by_metric["mae_rank"]["status"], "fail")
        self.assertEqual(audit_by_metric["mae_rank"]["best_method"], "last_year_rank")

        markdown = render_markdown_report(result)
        self.assertIn("## Leadership Audit", markdown)
        self.assertIn("| mae_rank | fail |", markdown)

    def test_run_benchmark_includes_slice_leadership_audit(self):
        cases = [
            PredictionCase(
                opportunity_key="slice:a",
                target_year=2025,
                actual_rank=10000,
                actual_score=620,
                history=[AdmissionHistory(year=2024, cutoff_rank=9000, cutoff_score=615)],
                metadata={"province_id": "33", "batch": "一段"},
            ),
            PredictionCase(
                opportunity_key="slice:b",
                target_year=2025,
                actual_rank=20000,
                actual_score=590,
                history=[AdmissionHistory(year=2024, cutoff_rank=26000, cutoff_score=585)],
                metadata={"province_id": "33", "batch": "一段"},
            ),
        ]

        result = run_benchmark(
            cases,
            methods=["last_year_rank", "volunteer_matching_rank_ensemble"],
        )

        self.assertIn("slice_leadership_audit", result)
        by_slice = result["slice_leadership_audit"]["target_year"]["target_year=2025"]
        self.assertIn("prediction_metrics", by_slice)

        markdown = render_markdown_report(result)
        self.assertIn("## Slice Leadership Audit", markdown)
        self.assertIn("target_year=2025", markdown)

    def test_run_benchmark_promotes_core_slice_failures_to_acceptance_gate(self):
        cases = [
            PredictionCase(
                opportunity_key="slice:a",
                target_year=2025,
                actual_rank=10000,
                actual_score=620,
                history=[
                    AdmissionHistory(year=2022, cutoff_rank=30000, cutoff_score=610),
                    AdmissionHistory(year=2023, cutoff_rank=30000, cutoff_score=610),
                    AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=620),
                ],
                metadata={"province_id": "33", "batch": "一段"},
            ),
            PredictionCase(
                opportunity_key="slice:b",
                target_year=2025,
                actual_rank=20000,
                actual_score=590,
                history=[
                    AdmissionHistory(year=2022, cutoff_rank=50000, cutoff_score=580),
                    AdmissionHistory(year=2023, cutoff_rank=50000, cutoff_score=580),
                    AdmissionHistory(year=2024, cutoff_rank=20000, cutoff_score=590),
                ],
                metadata={"province_id": "33", "batch": "一段"},
            ),
        ]

        result = run_benchmark(
            cases,
            methods=["last_year_rank", "volunteer_matching_rank_ensemble"],
        )

        self.assertIn("acceptance_gates", result)
        self.assertEqual(result["acceptance_gates"]["prediction_metrics"]["status"], "fail")
        self.assertEqual(result["acceptance_gates"]["slice_leadership"]["status"], "fail")
        self.assertGreater(result["acceptance_gates"]["slice_leadership"]["failed_metric_count"], 0)

        markdown = render_markdown_report(result)
        self.assertIn("## Acceptance Gates", markdown)
        self.assertIn("slice_leadership", markdown)

    def test_case_residual_audit_identifies_best_available_method_per_case(self):
        predictions = [
            {
                "method": "primary",
                "opportunity_key": "case-a",
                "actual_rank": 10000,
                "predicted_rank": 12000,
                "actual_score": 620,
                "predicted_score": 610,
            },
            {
                "method": "baseline",
                "opportunity_key": "case-a",
                "actual_rank": 10000,
                "predicted_rank": 10100,
                "actual_score": 620,
                "predicted_score": 618,
            },
        ]

        audit = build_case_residual_audit(predictions, primary_method="primary")

        self.assertEqual(audit[0]["opportunity_key"], "case-a")
        self.assertEqual(audit[0]["primary_rank_error"], 2000)
        self.assertEqual(audit[0]["best_rank_method"], "baseline")
        self.assertEqual(audit[0]["best_rank_error"], 100)
        self.assertEqual(audit[0]["rank_error_gap_to_best"], 1900)
        self.assertEqual(audit[0]["best_score_method"], "baseline")
        self.assertEqual(audit[0]["score_error_gap_to_best"], 8.0)

    def test_case_residual_audit_keeps_duplicate_opportunities_as_distinct_cases(self):
        predictions = [
            {
                "method": "primary",
                "opportunity_key": "shared-opportunity",
                "target_year": 2024,
                "province_id": "33",
                "subject_type": "science",
                "batch": "first",
                "actual_rank": 10000,
                "actual_score": 620,
                "predicted_rank": 13000,
                "predicted_score": 610,
            },
            {
                "method": "baseline",
                "opportunity_key": "shared-opportunity",
                "target_year": 2024,
                "province_id": "33",
                "subject_type": "science",
                "batch": "first",
                "actual_rank": 10000,
                "actual_score": 620,
                "predicted_rank": 10100,
                "predicted_score": 619,
            },
            {
                "method": "primary",
                "opportunity_key": "shared-opportunity",
                "target_year": 2025,
                "province_id": "33",
                "subject_type": "science",
                "batch": "first",
                "actual_rank": 50000,
                "actual_score": 560,
                "predicted_rank": 49000,
                "predicted_score": 570,
            },
            {
                "method": "baseline",
                "opportunity_key": "shared-opportunity",
                "target_year": 2025,
                "province_id": "33",
                "subject_type": "science",
                "batch": "first",
                "actual_rank": 50000,
                "actual_score": 560,
                "predicted_rank": 52000,
                "predicted_score": 558,
            },
        ]

        audit = build_case_residual_audit(predictions, primary_method="primary")

        self.assertEqual(len(audit), 2)
        by_year = {row["target_year"]: row for row in audit}
        self.assertEqual(by_year[2024]["primary_rank_error"], 3000)
        self.assertEqual(by_year[2024]["best_rank_error"], 100)
        self.assertEqual(by_year[2025]["primary_rank_error"], 1000)
        self.assertEqual(by_year[2025]["best_rank_error"], 1000)
        self.assertEqual(by_year[2025]["best_score_error"], 2.0)

    def test_markdown_report_includes_case_residual_audit(self):
        result = {
            "case_count": 1,
            "method_count": 2,
            "predictions": [],
            "errors": [],
            "metrics": {},
            "case_residual_audit": [
                {
                    "case_key": "case-a|2025|10000|620|33|Zhejiang|science|first",
                    "opportunity_key": "case-a",
                    "primary_method": "primary",
                    "primary_rank_error": 3000,
                    "best_rank_method": "baseline",
                    "best_rank_error": 100,
                    "rank_error_gap_to_best": 2900,
                    "primary_score_error": 10.0,
                    "best_score_method": "baseline",
                    "best_score_error": 1.0,
                    "score_error_gap_to_best": 9.0,
                    "target_year": 2025,
                    "province_id": "33",
                    "province_name": "Zhejiang",
                    "subject_type": "science",
                    "batch": "first",
                }
            ],
        }

        markdown = render_markdown_report(result)

        self.assertIn("## Case Residual Audit", markdown)
        self.assertIn("case-a|2025|10000|620|33|Zhejiang|science|first", markdown)
        self.assertIn("baseline", markdown)
        self.assertIn("2900", markdown)

    def test_leadership_audit_prefers_segmented_method_when_available(self):
        case = PredictionCase(
            opportunity_key="zhejiang:a",
            target_year=2025,
            actual_rank=13000,
            actual_score=620,
            history=[
                AdmissionHistory(year=2022, cutoff_rank=12000, cutoff_score=600),
                AdmissionHistory(year=2023, cutoff_rank=9000, cutoff_score=620),
                AdmissionHistory(year=2024, cutoff_rank=13000, cutoff_score=650),
            ],
            metadata={"batch": "一段"},
        )

        result = run_benchmark(
            [case],
            methods=[
                "last_year_rank",
                "volunteer_matching_rank_ensemble",
                "volunteer_matching_segmented_rank_ensemble",
            ],
        )

        self.assertEqual(
            result["leadership_audit"]["prediction_metrics"][0]["primary_method"],
            "volunteer_matching_segmented_rank_ensemble",
        )

    def test_run_multi_year_benchmark_returns_year_and_combined_metrics(self):
        cases_by_year = {
            2024: [
                PredictionCase(
                    opportunity_key="guangdong:a",
                    target_year=2024,
                    actual_rank=12000,
                    actual_score=610,
                    history=[
                        AdmissionHistory(year=2022, cutoff_rank=13000, cutoff_score=605),
                        AdmissionHistory(year=2023, cutoff_rank=12500, cutoff_score=608),
                    ],
                )
            ],
            2025: [
                PredictionCase(
                    opportunity_key="zhejiang:a",
                    target_year=2025,
                    actual_rank=9800,
                    actual_score=622,
                    history=[
                        AdmissionHistory(year=2023, cutoff_rank=11000, cutoff_score=615),
                        AdmissionHistory(year=2024, cutoff_rank=10000, cutoff_score=620),
                    ],
                )
            ],
        }

        result = run_multi_year_benchmark(cases_by_year, methods=["last_year_rank"])

        self.assertEqual(set(result["year_results"]), {2024, 2025})
        self.assertEqual(result["combined"]["case_count"], 2)
        self.assertIn("last_year_rank", result["combined"]["metrics"])
        self.assertEqual(len(result["combined"]["predictions"]), 2)


if __name__ == "__main__":
    unittest.main()
