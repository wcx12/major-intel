import unittest

from major_intel.volunteer_matching.route_search import (
    DEFAULT_PREDICTION_EXPERT_ROUTE_SPECS,
    RouteSpec,
    apply_route_specs,
    beam_search_route_specs,
    evaluate_route_specs_against_benchmark,
    evaluate_route_specs,
    extract_failed_slice_filters,
    generate_route_candidates,
    quick_score_route_spec,
)
from major_intel.volunteer_matching.metrics import evaluate_predictions, evaluate_predictions_by_group


class RouteSearchTests(unittest.TestCase):
    def test_default_prediction_expert_route_specs_capture_current_v36_routes(self):
        by_name = {spec.name: spec for spec in DEFAULT_PREDICTION_EXPERT_ROUTE_SPECS}

        self.assertEqual(
            by_name["gd_2023_history_vocational_tabicl_score"].filters,
            {
                "target_year": 2023,
                "province_id": "44",
                "opportunity_grain": "school",
                "subject_type": "history",
            },
        )
        self.assertEqual(by_name["gd_2023_history_vocational_tabicl_score"].contains, {"batch": "\u4e13\u79d1"})
        self.assertEqual(by_name["gd_2023_history_vocational_tabicl_score"].score_method, "tabicl_regressor")
        self.assertEqual(
            by_name["gd_2023_vocational_tabicl_rank_blend"].filters,
            {
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
            },
        )
        self.assertEqual(by_name["gd_2023_vocational_tabicl_rank_blend"].rank_method, "tabicl_regressor")
        self.assertEqual(by_name["gd_2023_vocational_tabicl_rank_blend"].rank_weight, 0.4)
        self.assertFalse(by_name["gd_2023_vocational_tabicl_rank_blend"].update_planning_rank)
        self.assertEqual(
            by_name["gd_2024_vocational_best_recent_rank_blend"].filters,
            {
                "target_year": 2024,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
            },
        )
        self.assertEqual(by_name["gd_2024_vocational_best_recent_rank_blend"].rank_method, "best_recent_rank")
        self.assertEqual(by_name["gd_2024_vocational_best_recent_rank_blend"].rank_weight, 0.01)
        self.assertFalse(by_name["gd_2024_vocational_best_recent_rank_blend"].update_planning_rank)
        self.assertEqual(
            by_name["gd_2024_vocational_tabicl_score_blend"].filters,
            {
                "target_year": 2024,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
            },
        )
        self.assertEqual(by_name["gd_2024_vocational_tabicl_score_blend"].score_method, "tabicl_regressor")
        self.assertEqual(by_name["gd_2024_vocational_tabicl_score_blend"].score_weight, 0.75)
        self.assertEqual(
            by_name["gd_2024_vocational_two_year_score_blend"].filters,
            {
                "target_year": 2024,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
            },
        )
        self.assertEqual(by_name["gd_2024_vocational_two_year_score_blend"].score_method, "two_year_mean_rank")
        self.assertEqual(by_name["gd_2024_vocational_two_year_score_blend"].score_weight, 0.4)
        self.assertEqual(by_name["science_ada_boost_score_blend"].filters, {"subject_type": "\u7406\u79d1"})
        self.assertEqual(by_name["science_ada_boost_score_blend"].score_method, "sklearn_ada_boost")
        self.assertEqual(by_name["science_ada_boost_score_blend"].score_weight, 0.2)
        self.assertEqual(by_name["history_extra_trees_rank_blend"].filters, {"subject_type": "history"})
        self.assertEqual(by_name["history_extra_trees_rank_blend"].rank_method, "sklearn_extra_trees")
        self.assertEqual(by_name["history_extra_trees_rank_blend"].rank_weight, 0.2)
        self.assertFalse(by_name["history_extra_trees_rank_blend"].update_planning_rank)
        self.assertEqual(by_name["liberal_arts_ridge_score"].filters, {"subject_type": "\u6587\u79d1"})
        self.assertEqual(by_name["liberal_arts_ridge_score"].score_method, "sklearn_ridge")
        self.assertEqual(by_name["liberal_arts_meta_score_blend"].filters, {"subject_type": "\u6587\u79d1"})
        self.assertEqual(by_name["liberal_arts_meta_score_blend"].score_method, "volunteer_matching_meta_router")
        self.assertEqual(by_name["liberal_arts_meta_score_blend"].score_weight, 0.4)
        route_names = [spec.name for spec in DEFAULT_PREDICTION_EXPERT_ROUTE_SPECS]
        self.assertGreater(
            route_names.index("liberal_arts_meta_score_blend"),
            route_names.index("liberal_arts_ridge_score"),
        )
        self.assertEqual(by_name["vocational_lightgbm_rank_blend"].filters, {"batch": "\u9ad8\u804c\u4e13\u79d1\u6279"})
        self.assertEqual(by_name["vocational_lightgbm_rank_blend"].rank_method, "lightgbm_regressor")
        self.assertEqual(by_name["vocational_lightgbm_rank_blend"].rank_weight, 0.05)
        self.assertFalse(by_name["vocational_lightgbm_rank_blend"].update_planning_rank)
        self.assertEqual(
            by_name["zj_2025_first_segment_ada_score_blend"].filters,
            {
                "target_year": 2025,
                "province_id": "33",
                "batch": "\u4e00\u6bb5",
                "opportunity_grain": "major",
            },
        )
        self.assertEqual(by_name["zj_2025_first_segment_ada_score_blend"].score_method, "sklearn_ada_boost")
        self.assertEqual(by_name["zj_2025_first_segment_ada_score_blend"].score_weight, 0.05)
        self.assertEqual(by_name["physics_meta_rank_blend"].filters, {"subject_type": "physics"})
        self.assertEqual(by_name["physics_meta_rank_blend"].rank_method, "volunteer_matching_meta_router")
        self.assertEqual(by_name["physics_meta_rank_blend"].rank_weight, 0.15)
        self.assertFalse(by_name["physics_meta_rank_blend"].update_planning_rank)
        self.assertEqual(
            by_name["zj_2025_first_segment_lightgbm_score_blend"].filters,
            {
                "target_year": 2025,
                "province_id": "33",
                "batch": "\u4e00\u6bb5",
                "opportunity_grain": "major",
            },
        )
        self.assertEqual(by_name["zj_2025_first_segment_lightgbm_score_blend"].score_method, "lightgbm_regressor")
        self.assertEqual(by_name["zj_2025_first_segment_lightgbm_score_blend"].score_weight, 0.2)
        self.assertGreater(
            route_names.index("zj_2025_first_segment_lightgbm_score_blend"),
            route_names.index("zj_2025_first_segment_ada_score_blend"),
        )
        self.assertEqual(by_name["history_two_year_rank_blend"].filters, {"subject_type": "history"})
        self.assertEqual(by_name["history_two_year_rank_blend"].rank_method, "two_year_mean_rank")
        self.assertEqual(by_name["history_two_year_rank_blend"].rank_weight, 0.01)
        self.assertFalse(by_name["history_two_year_rank_blend"].update_planning_rank)
        self.assertEqual(
            by_name["gd_2023_vocational_elastic_net_score_blend"].filters,
            {
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
            },
        )
        self.assertEqual(by_name["gd_2023_vocational_elastic_net_score_blend"].score_method, "sklearn_elastic_net")
        self.assertEqual(by_name["gd_2023_vocational_elastic_net_score_blend"].score_weight, 0.075)
        self.assertEqual(
            by_name["gd_2023_vocational_ada_boost_score_blend"].filters,
            {
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
            },
        )
        self.assertEqual(by_name["gd_2023_vocational_ada_boost_score_blend"].score_method, "sklearn_ada_boost")
        self.assertEqual(by_name["gd_2023_vocational_ada_boost_score_blend"].score_weight, 0.075)
        self.assertGreater(
            route_names.index("gd_2023_vocational_ada_boost_score_blend"),
            route_names.index("gd_2023_vocational_elastic_net_score_blend"),
        )

    def test_apply_route_specs_routes_matching_score_without_mutating_base(self):
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
                "warnings": ["rank_expert=base"],
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
                "predicted_score": 398.5,
                "warnings": [],
            },
        ]

        result = apply_route_specs(
            predictions,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=[
                RouteSpec(
                    name="gd_2023_history_vocational_tabicl_score",
                    filters={
                        "target_year": 2023,
                        "province_id": "44",
                        "opportunity_grain": "school",
                        "subject_type": "history",
                    },
                    contains={"batch": "\u4e13\u79d1"},
                    score_method="tabicl_regressor",
                )
            ],
        )

        self.assertEqual(len(result.routed_rows), 1)
        self.assertEqual(result.changed_count, 1)
        self.assertEqual(predictions[0]["predicted_score"], 410)
        routed = result.routed_rows[0]
        self.assertEqual(routed["method"], "candidate_router")
        self.assertEqual(routed["predicted_rank"], 10000)
        self.assertEqual(routed["planning_rank"], 9800)
        self.assertEqual(routed["predicted_score"], 398.5)
        self.assertIn("route=gd_2023_history_vocational_tabicl_score:score=tabicl_regressor", routed["warnings"])

    def test_apply_route_specs_routes_rank_and_planning_rank_from_expert(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "zj-first",
                "target_year": 2025,
                "province_id": "33",
                "batch": "\u4e00\u6bb5",
                "opportunity_grain": "major",
                "predicted_rank": 50000,
                "planning_rank": 51000,
                "predicted_score": 590,
                "warnings": [],
            },
            {
                "method": "best_recent_rank",
                "opportunity_key": "zj-first",
                "target_year": 2025,
                "province_id": "33",
                "batch": "\u4e00\u6bb5",
                "opportunity_grain": "major",
                "predicted_rank": 47000,
                "planning_rank": 48000,
                "predicted_score": 592,
                "warnings": [],
            },
        ]

        result = apply_route_specs(
            predictions,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=[
                RouteSpec(
                    name="zhejiang_first_best_recent_rank",
                    filters={"province_id": "33", "opportunity_grain": "major"},
                    contains={"batch": "\u4e00\u6bb5"},
                    rank_method="best_recent_rank",
                )
            ],
        )

        routed = result.routed_rows[0]
        self.assertEqual(result.changed_count, 1)
        self.assertEqual(routed["predicted_rank"], 47000)
        self.assertEqual(routed["planning_rank"], 48000)
        self.assertEqual(routed["predicted_score"], 590)
        self.assertIn("route=zhejiang_first_best_recent_rank:rank=best_recent_rank", routed["warnings"])

    def test_apply_route_specs_can_blend_rank_without_changing_planning_rank(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "gd-voc",
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "predicted_rank": 10000,
                "planning_rank": 9800,
                "predicted_score": 410,
                "warnings": [],
            },
            {
                "method": "tabicl_regressor",
                "opportunity_key": "gd-voc",
                "target_year": 2023,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "predicted_rank": 8000,
                "planning_rank": 8100,
                "predicted_score": 408,
                "warnings": [],
            },
        ]

        result = apply_route_specs(
            predictions,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=[
                RouteSpec(
                    name="gd_2023_vocational_tabicl_rank_blend",
                    filters={
                        "target_year": 2023,
                        "province_id": "44",
                        "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                        "opportunity_grain": "school",
                    },
                    rank_method="tabicl_regressor",
                    rank_weight=0.4,
                    update_planning_rank=False,
                )
            ],
        )

        routed = result.routed_rows[0]
        self.assertEqual(result.changed_count, 1)
        self.assertEqual(routed["predicted_rank"], 9200)
        self.assertEqual(routed["planning_rank"], 9800)
        self.assertIn(
            "route=gd_2023_vocational_tabicl_rank_blend:rank=tabicl_regressor:weight=0.4:planning=base",
            routed["warnings"],
        )

    def test_apply_route_specs_chains_score_blends_in_route_order(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "gd-voc",
                "target_year": 2024,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "predicted_rank": 10000,
                "predicted_score": 430.0,
                "warnings": [],
            },
            {
                "method": "tabicl_regressor",
                "opportunity_key": "gd-voc",
                "target_year": 2024,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "predicted_rank": 10000,
                "predicted_score": 421.67,
                "warnings": [],
            },
            {
                "method": "two_year_mean_rank",
                "opportunity_key": "gd-voc",
                "target_year": 2024,
                "province_id": "44",
                "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
                "opportunity_grain": "school",
                "predicted_rank": 10000,
                "predicted_score": 434.5,
                "warnings": [],
            },
        ]

        result = apply_route_specs(
            predictions,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=[
                RouteSpec(
                    name="first_tabicl_score",
                    filters={"province_id": "44"},
                    score_method="tabicl_regressor",
                    score_weight=0.75,
                ),
                RouteSpec(
                    name="then_two_year_score",
                    filters={"province_id": "44"},
                    score_method="two_year_mean_rank",
                    score_weight=0.4,
                ),
            ],
        )

        routed = result.routed_rows[0]
        self.assertAlmostEqual(routed["predicted_score"], 428.0515)
        self.assertIn("route=first_tabicl_score:score=tabicl_regressor:weight=0.75", routed["warnings"])
        self.assertIn("route=then_two_year_score:score=two_year_mean_rank:weight=0.4", routed["warnings"])

    def test_apply_route_specs_can_force_full_coverage_when_expert_is_missing(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "plain",
                "target_year": 2024,
                "province_id": "61",
                "predicted_rank": 20000,
                "predicted_score": 450,
                "warnings": [],
            }
        ]

        result = apply_route_specs(
            predictions,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=[
                RouteSpec(
                    name="missing_score_expert",
                    filters={"province_id": {"61", "33"}},
                    score_method="sklearn_ridge",
                )
            ],
            force=True,
        )

        self.assertEqual(result.changed_count, 0)
        self.assertEqual(len(result.routed_rows), 1)
        self.assertEqual(result.routed_rows[0]["method"], "candidate_router")
        self.assertEqual(result.routed_rows[0]["predicted_rank"], 20000)
        self.assertEqual(result.routed_rows[0]["predicted_score"], 450)
        self.assertEqual(result.routed_rows[0]["warnings"], [])

    def test_apply_route_specs_omits_candidate_when_no_route_changes_and_not_forced(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "plain",
                "target_year": 2024,
                "province_id": "61",
                "predicted_rank": 20000,
                "predicted_score": 450,
                "warnings": [],
            }
        ]

        result = apply_route_specs(
            predictions,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=[RouteSpec(name="does_not_match", filters={"province_id": "44"}, score_method="sklearn_ridge")],
        )

        self.assertEqual(result.changed_count, 0)
        self.assertEqual(result.routed_rows, [])

    def test_evaluate_route_specs_scores_candidate_as_primary_and_excludes_low_coverage_expert(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "matched",
                "target_year": 2025,
                "province_id": "33",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 10000,
                "predicted_score": 590,
                "warnings": [],
            },
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "plain",
                "target_year": 2025,
                "province_id": "61",
                "actual_rank": 20000,
                "actual_score": 500,
                "predicted_rank": 20000,
                "predicted_score": 490,
                "warnings": [],
            },
            {
                "method": "sklearn_ridge",
                "opportunity_key": "matched",
                "target_year": 2025,
                "province_id": "33",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 10000,
                "predicted_score": 600,
                "warnings": [],
            },
        ]

        result = evaluate_route_specs(
            predictions,
            case_count=2,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=[
                RouteSpec(
                    name="zhejiang_ridge_score",
                    filters={"province_id": "33"},
                    score_method="sklearn_ridge",
                )
            ],
            prediction_metric_directions={
                "mae_score": "asc",
                "within_5_score_points": "desc",
            },
            prediction_metric_tolerances={},
            slice_field_sets=[("province_id",)],
            min_coverage_rate=0.99,
        )

        self.assertEqual(result["route_application"].changed_count, 1)
        self.assertEqual(result["metrics"]["sklearn_ridge"]["coverage_rate"], 0.5)
        self.assertEqual(result["metrics"]["candidate_router"]["coverage_rate"], 1.0)
        self.assertLess(
            result["metrics"]["candidate_router"]["mae_score"],
            result["metrics"]["volunteer_matching_meta_router"]["mae_score"],
        )
        self.assertEqual(result["acceptance_gates"]["prediction_metrics"]["status"], "pass")
        audit_by_metric = {row["metric"]: row for row in result["leadership_audit"]["prediction_metrics"]}
        self.assertIn("sklearn_ridge", audit_by_metric["mae_score"]["excluded_low_coverage_methods"])
        self.assertEqual(audit_by_metric["mae_score"]["primary_method"], "candidate_router")

    def test_evaluate_route_specs_against_benchmark_matches_full_route_evaluation(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "zj-case",
                "target_year": 2025,
                "province_id": "33",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 11000,
                "predicted_score": 590,
                "warnings": [],
            },
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "gd-case",
                "target_year": 2025,
                "province_id": "44",
                "actual_rank": 20000,
                "actual_score": 500,
                "predicted_rank": 21000,
                "predicted_score": 490,
                "warnings": [],
            },
            {
                "method": "sklearn_ridge",
                "opportunity_key": "zj-case",
                "target_year": 2025,
                "province_id": "33",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 10000,
                "predicted_score": 601,
                "warnings": [],
            },
            {
                "method": "sklearn_ridge",
                "opportunity_key": "gd-case",
                "target_year": 2025,
                "province_id": "44",
                "actual_rank": 20000,
                "actual_score": 500,
                "predicted_rank": 20000,
                "predicted_score": 508,
                "warnings": [],
            },
        ]
        benchmark_metrics = evaluate_predictions(predictions)
        for method_metrics in benchmark_metrics.values():
            method_metrics["coverage_rate"] = method_metrics["rank_row_count"] / 2
        benchmark_result = {
            "case_count": 2,
            "predictions": predictions,
            "metrics": benchmark_metrics,
            "group_metrics": {"province_id": evaluate_predictions_by_group(predictions, ["province_id"])},
        }
        route_specs = [
            RouteSpec(
                name="zhejiang_ridge_score",
                filters={"province_id": "33"},
                score_method="sklearn_ridge",
            )
        ]

        full = evaluate_route_specs(
            predictions,
            case_count=2,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=route_specs,
            prediction_metric_directions={"mae_score": "asc", "within_5_score_points": "desc"},
            prediction_metric_tolerances={},
            slice_field_sets=[("province_id",)],
            min_coverage_rate=0.99,
            force=True,
        )
        incremental = evaluate_route_specs_against_benchmark(
            benchmark_result,
            base_method="volunteer_matching_meta_router",
            routed_method="candidate_router",
            route_specs=route_specs,
            prediction_metric_directions={"mae_score": "asc", "within_5_score_points": "desc"},
            prediction_metric_tolerances={},
            slice_field_sets=[("province_id",)],
            min_coverage_rate=0.99,
            force=True,
        )

        self.assertEqual(incremental["route_application"].changed_count, full["route_application"].changed_count)
        self.assertEqual(incremental["metrics"]["candidate_router"], full["metrics"]["candidate_router"])
        self.assertEqual(incremental["acceptance_gates"], full["acceptance_gates"])
        self.assertEqual(incremental["slice_leadership_audit"], full["slice_leadership_audit"])
        self.assertNotIn("candidate_router", benchmark_result["metrics"])

    def test_beam_search_route_specs_returns_best_slice_reducing_route(self):
        predictions = [
            {
                "method": "base",
                "opportunity_key": "zj-case",
                "target_year": 2025,
                "province_id": "33",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 10000,
                "predicted_score": 590,
            },
            {
                "method": "base",
                "opportunity_key": "gd-case",
                "target_year": 2025,
                "province_id": "44",
                "actual_rank": 20000,
                "actual_score": 500,
                "predicted_rank": 20000,
                "predicted_score": 490,
            },
            {
                "method": "comparison",
                "opportunity_key": "zj-case",
                "target_year": 2025,
                "province_id": "33",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 10000,
                "predicted_score": 600,
            },
            {
                "method": "comparison",
                "opportunity_key": "gd-case",
                "target_year": 2025,
                "province_id": "44",
                "actual_rank": 20000,
                "actual_score": 500,
                "predicted_rank": 20000,
                "predicted_score": 500,
            },
            {
                "method": "ridge",
                "opportunity_key": "zj-case",
                "target_year": 2025,
                "province_id": "33",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 10000,
                "predicted_score": 600,
            },
        ]
        benchmark_metrics = evaluate_predictions(predictions)
        for method_metrics in benchmark_metrics.values():
            method_metrics["coverage_rate"] = method_metrics["rank_row_count"] / 2
        benchmark_result = {
            "case_count": 2,
            "predictions": predictions,
            "metrics": benchmark_metrics,
            "group_metrics": {"province_id": evaluate_predictions_by_group(predictions, ["province_id"])},
        }

        results = beam_search_route_specs(
            [benchmark_result],
            [
                RouteSpec(name="no_match", filters={"province_id": "61"}, score_method="ridge"),
                RouteSpec(name="zhejiang_ridge_score", filters={"province_id": "33"}, score_method="ridge"),
            ],
            base_method="base",
            routed_method="candidate_router",
            prediction_metric_directions={"mae_score": "asc"},
            prediction_metric_tolerances={"mae_score": 5},
            slice_field_sets=[("province_id",)],
            min_coverage_rate=0.99,
            max_depth=1,
            beam_width=2,
        )

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0].route_specs[0].name, "zhejiang_ridge_score")
        self.assertEqual(results[0].total_prediction_failures, 0)
        self.assertEqual(results[0].total_slice_failures, 1)
        self.assertEqual(results[0].changed_count, 1)

    def test_extract_failed_slice_filters_parses_groups_without_shell_literals(self):
        benchmark_result = {
            "slice_leadership_audit": {
                "target_year|province_id|batch": {
                    "target_year=2023|province_id=44|batch=\u9ad8\u804c\u4e13\u79d1\u6279": {
                        "failure_count": 9,
                        "primary_rows": 76,
                    },
                    "target_year=2024|province_id=44|batch=\u672c\u79d1\u6279": {
                        "failure_count": 0,
                        "primary_rows": 100,
                    },
                },
                "subject_type": {
                    "subject_type=\u6587\u79d1": {
                        "failure_count": 7,
                        "primary_rows": 50,
                    }
                },
            }
        }

        slices = extract_failed_slice_filters(benchmark_result, limit=2)

        self.assertEqual([item.failure_count for item in slices], [9, 7])
        self.assertEqual(
            slices[0].filters,
            {"target_year": 2023, "province_id": "44", "batch": "\u9ad8\u804c\u4e13\u79d1\u6279"},
        )
        self.assertEqual(slices[0].field, "target_year|province_id|batch")
        self.assertEqual(slices[1].filters, {"subject_type": "\u6587\u79d1"})

    def test_generate_route_candidates_builds_score_rank_and_both_specs(self):
        slices = extract_failed_slice_filters(
            {
                "slice_leadership_audit": {
                    "subject_type": {
                        "subject_type=\u6587\u79d1": {
                            "failure_count": 7,
                            "primary_rows": 50,
                        }
                    }
                }
            }
        )

        specs = generate_route_candidates(
            slices,
            expert_methods=["sklearn_ridge", "tabicl_regressor"],
            modes=("score", "rank", "both"),
        )

        self.assertEqual(len(specs), 6)
        self.assertEqual(specs[0].filters, {"subject_type": "\u6587\u79d1"})
        self.assertEqual(specs[0].score_method, "sklearn_ridge")
        self.assertIsNone(specs[0].rank_method)
        self.assertEqual(specs[1].rank_method, "sklearn_ridge")
        self.assertIsNone(specs[1].score_method)
        self.assertEqual(specs[2].rank_method, "sklearn_ridge")
        self.assertEqual(specs[2].score_method, "sklearn_ridge")

    def test_quick_score_route_spec_scores_only_changed_matching_rows(self):
        predictions = [
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "arts-good",
                "target_year": 2025,
                "subject_type": "\u6587\u79d1",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 12000,
                "predicted_score": 590,
            },
            {
                "method": "volunteer_matching_meta_router",
                "opportunity_key": "science-ignore",
                "target_year": 2025,
                "subject_type": "\u7406\u79d1",
                "actual_rank": 20000,
                "actual_score": 500,
                "predicted_rank": 19000,
                "predicted_score": 498,
            },
            {
                "method": "sklearn_ridge",
                "opportunity_key": "arts-good",
                "target_year": 2025,
                "subject_type": "\u6587\u79d1",
                "actual_rank": 10000,
                "actual_score": 600,
                "predicted_rank": 10500,
                "predicted_score": 602,
            },
        ]

        score = quick_score_route_spec(
            predictions,
            base_method="volunteer_matching_meta_router",
            route_spec=RouteSpec(
                name="arts_ridge_both",
                filters={"subject_type": "\u6587\u79d1"},
                rank_method="sklearn_ridge",
                score_method="sklearn_ridge",
            ),
        )

        self.assertEqual(score.matched_count, 1)
        self.assertEqual(score.changed_count, 1)
        self.assertEqual(score.rank_error_delta, -1500)
        self.assertEqual(score.score_error_delta, -8)
        self.assertEqual(score.improved_metric_count, 2)


if __name__ == "__main__":
    unittest.main()
