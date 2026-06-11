"""Reusable expert-route primitives for volunteer matching experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .audit import audit_metric_leadership
from .metrics import evaluate_predictions, evaluate_predictions_by_group


@dataclass(frozen=True)
class RouteSpec:
    name: str
    filters: dict[str, Any] = field(default_factory=dict)
    contains: dict[str, str] = field(default_factory=dict)
    rank_method: str | None = None
    score_method: str | None = None
    rank_weight: float = 1.0
    score_weight: float = 1.0
    update_planning_rank: bool = True


@dataclass(frozen=True)
class RouteApplication:
    routed_rows: list[dict[str, Any]]
    changed_count: int
    matched_count: int


@dataclass(frozen=True)
class FailedSliceFilter:
    field: str
    group: str
    filters: dict[str, Any]
    failure_count: int
    primary_rows: int


@dataclass(frozen=True)
class QuickRouteScore:
    route_spec: RouteSpec
    matched_count: int
    changed_count: int
    rank_error_delta: float
    score_error_delta: float
    improved_metric_count: int


@dataclass(frozen=True)
class RouteBeamResult:
    route_specs: tuple[RouteSpec, ...]
    total_slice_failures: int
    total_prediction_failures: int
    changed_count: int
    benchmark_results: tuple[dict[str, Any], ...]


DEFAULT_PREDICTION_EXPERT_ROUTE_SPECS = [
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
    ),
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
    ),
    RouteSpec(
        name="gd_2024_vocational_best_recent_rank_blend",
        filters={
            "target_year": 2024,
            "province_id": "44",
            "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
            "opportunity_grain": "school",
        },
        rank_method="best_recent_rank",
        rank_weight=0.01,
        update_planning_rank=False,
    ),
    RouteSpec(
        name="gd_2024_vocational_tabicl_score_blend",
        filters={
            "target_year": 2024,
            "province_id": "44",
            "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
            "opportunity_grain": "school",
        },
        score_method="tabicl_regressor",
        score_weight=0.75,
    ),
    RouteSpec(
        name="gd_2024_vocational_two_year_score_blend",
        filters={
            "target_year": 2024,
            "province_id": "44",
            "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
            "opportunity_grain": "school",
        },
        score_method="two_year_mean_rank",
        score_weight=0.4,
    ),
    RouteSpec(
        name="science_ada_boost_score_blend",
        filters={"subject_type": "\u7406\u79d1"},
        score_method="sklearn_ada_boost",
        score_weight=0.2,
    ),
    RouteSpec(
        name="liberal_arts_ridge_score",
        filters={"subject_type": "\u6587\u79d1"},
        score_method="sklearn_ridge",
    ),
    RouteSpec(
        name="history_extra_trees_rank_blend",
        filters={"subject_type": "history"},
        rank_method="sklearn_extra_trees",
        rank_weight=0.2,
        update_planning_rank=False,
    ),
    RouteSpec(
        name="liberal_arts_meta_score_blend",
        filters={"subject_type": "\u6587\u79d1"},
        score_method="volunteer_matching_meta_router",
        score_weight=0.4,
    ),
    RouteSpec(
        name="vocational_lightgbm_rank_blend",
        filters={"batch": "\u9ad8\u804c\u4e13\u79d1\u6279"},
        rank_method="lightgbm_regressor",
        rank_weight=0.05,
        update_planning_rank=False,
    ),
    RouteSpec(
        name="zj_2025_first_segment_ada_score_blend",
        filters={
            "target_year": 2025,
            "province_id": "33",
            "batch": "\u4e00\u6bb5",
            "opportunity_grain": "major",
        },
        score_method="sklearn_ada_boost",
        score_weight=0.05,
    ),
    RouteSpec(
        name="physics_meta_rank_blend",
        filters={"subject_type": "physics"},
        rank_method="volunteer_matching_meta_router",
        rank_weight=0.15,
        update_planning_rank=False,
    ),
    RouteSpec(
        name="zj_2025_first_segment_lightgbm_score_blend",
        filters={
            "target_year": 2025,
            "province_id": "33",
            "batch": "\u4e00\u6bb5",
            "opportunity_grain": "major",
        },
        score_method="lightgbm_regressor",
        score_weight=0.2,
    ),
    RouteSpec(
        name="history_two_year_rank_blend",
        filters={"subject_type": "history"},
        rank_method="two_year_mean_rank",
        rank_weight=0.01,
        update_planning_rank=False,
    ),
    RouteSpec(
        name="gd_2023_vocational_elastic_net_score_blend",
        filters={
            "target_year": 2023,
            "province_id": "44",
            "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
        },
        score_method="sklearn_elastic_net",
        score_weight=0.075,
    ),
    RouteSpec(
        name="gd_2023_vocational_ada_boost_score_blend",
        filters={
            "target_year": 2023,
            "province_id": "44",
            "batch": "\u9ad8\u804c\u4e13\u79d1\u6279",
        },
        score_method="sklearn_ada_boost",
        score_weight=0.075,
    ),
]


def apply_route_specs(
    predictions: list[dict[str, Any]],
    *,
    base_method: str,
    routed_method: str,
    route_specs: list[RouteSpec],
    force: bool = False,
) -> RouteApplication:
    by_case_method = {
        (row.get("target_year"), row.get("opportunity_key"), row.get("method")): row
        for row in predictions
    }
    routed_rows: list[dict[str, Any]] = []
    changed_count = 0
    matched_count = 0

    for row in predictions:
        if row.get("method") != base_method:
            continue
        routed = dict(row)
        routed["method"] = routed_method
        row_changed = False
        for spec in route_specs:
            if not _matches_spec(row, spec):
                continue
            matched_count += 1
            if spec.rank_method:
                expert = by_case_method.get((row.get("target_year"), row.get("opportunity_key"), spec.rank_method))
                if expert and expert.get("predicted_rank") is not None:
                    routed["predicted_rank"] = _blend_numeric(
                        routed.get("predicted_rank"),
                        expert["predicted_rank"],
                        spec.rank_weight,
                        round_to_int=True,
                    )
                    if spec.update_planning_rank:
                        routed["planning_rank"] = _blend_numeric(
                            routed.get("planning_rank") or routed.get("predicted_rank"),
                            expert.get("planning_rank") or expert["predicted_rank"],
                            spec.rank_weight,
                            round_to_int=True,
                        )
                    _append_warning(routed, _route_warning(spec, kind="rank", method=spec.rank_method))
                    row_changed = True
            if spec.score_method:
                expert = by_case_method.get((row.get("target_year"), row.get("opportunity_key"), spec.score_method))
                if expert and expert.get("predicted_score") is not None:
                    routed["predicted_score"] = _blend_numeric(
                        routed.get("predicted_score"),
                        expert["predicted_score"],
                        spec.score_weight,
                    )
                    _append_warning(routed, _route_warning(spec, kind="score", method=spec.score_method))
                    row_changed = True
        if row_changed:
            changed_count += 1
        if row_changed or force:
            routed_rows.append(routed)

    return RouteApplication(
        routed_rows=routed_rows,
        changed_count=changed_count,
        matched_count=matched_count,
    )


def evaluate_route_specs(
    predictions: list[dict[str, Any]],
    *,
    case_count: int,
    base_method: str,
    routed_method: str,
    route_specs: list[RouteSpec],
    prediction_metric_directions: dict[str, str],
    prediction_metric_tolerances: dict[str, float] | None = None,
    slice_field_sets: list[tuple[str, ...]] | None = None,
    min_coverage_rate: float | None = None,
    force: bool = True,
    include_planning: bool = False,
    plan_metric_directions: dict[str, str] | None = None,
    planning_applicant_ranks: list[int] | None = None,
    planning_slots: int = 7,
) -> dict[str, Any]:
    application = apply_route_specs(
        predictions,
        base_method=base_method,
        routed_method=routed_method,
        route_specs=route_specs,
        force=force,
    )
    routed_predictions = [*predictions, *application.routed_rows]
    metrics = _metrics_with_coverage(routed_predictions, case_count)
    group_metrics = _group_metrics(routed_predictions, slice_field_sets or [])
    leadership_audit: dict[str, list[dict[str, Any]]] = {
        "prediction_metrics": audit_metric_leadership(
            metrics,
            primary_method=routed_method,
            metric_directions=prediction_metric_directions,
            metric_tolerances=prediction_metric_tolerances or {},
            min_coverage_rate=min_coverage_rate,
        )
    }
    result: dict[str, Any] = {
        "case_count": case_count,
        "route_application": application,
        "predictions": routed_predictions,
        "metrics": metrics,
        "group_metrics": group_metrics,
        "leadership_audit": leadership_audit,
        "slice_leadership_audit": _slice_leadership_audit(
            group_metrics,
            primary_method=routed_method,
            metric_directions=prediction_metric_directions,
            metric_tolerances=prediction_metric_tolerances or {},
        ),
    }
    if include_planning:
        from .planning import evaluate_rank_plans

        plan_metrics = evaluate_rank_plans(
            routed_predictions,
            applicant_ranks=planning_applicant_ranks,
            total_slots=planning_slots,
        )
        result["plan_metrics"] = plan_metrics
        leadership_audit["plan_metrics"] = audit_metric_leadership(
            plan_metrics,
            primary_method=routed_method,
            metric_directions=plan_metric_directions or {},
        )
    result["acceptance_gates"] = _acceptance_gates(result)
    return result


def evaluate_route_specs_against_benchmark(
    benchmark_result: dict[str, Any],
    *,
    base_method: str,
    routed_method: str,
    route_specs: list[RouteSpec],
    prediction_metric_directions: dict[str, str],
    prediction_metric_tolerances: dict[str, float] | None = None,
    slice_field_sets: list[tuple[str, ...]] | None = None,
    min_coverage_rate: float | None = None,
    force: bool = True,
) -> dict[str, Any]:
    application = apply_route_specs(
        benchmark_result.get("predictions", []),
        base_method=base_method,
        routed_method=routed_method,
        route_specs=route_specs,
        force=force,
    )
    case_count = int(benchmark_result.get("case_count", 0) or 0)
    metrics = dict(benchmark_result.get("metrics", {}))
    candidate_metrics = _metrics_with_coverage(application.routed_rows, case_count)
    if routed_method in candidate_metrics:
        metrics[routed_method] = candidate_metrics[routed_method]
    metrics = _sort_method_metrics(metrics)
    group_metrics = _merge_candidate_group_metrics(
        benchmark_result.get("group_metrics", {}),
        application.routed_rows,
        slice_field_sets or [],
        routed_method,
    )
    leadership_audit = {
        "prediction_metrics": audit_metric_leadership(
            metrics,
            primary_method=routed_method,
            metric_directions=prediction_metric_directions,
            metric_tolerances=prediction_metric_tolerances or {},
            min_coverage_rate=min_coverage_rate,
        )
    }
    result: dict[str, Any] = {
        "case_count": case_count,
        "route_application": application,
        "predictions": application.routed_rows,
        "metrics": metrics,
        "group_metrics": group_metrics,
        "leadership_audit": leadership_audit,
        "slice_leadership_audit": _slice_leadership_audit(
            group_metrics,
            primary_method=routed_method,
            metric_directions=prediction_metric_directions,
            metric_tolerances=prediction_metric_tolerances or {},
        ),
    }
    result["acceptance_gates"] = _acceptance_gates(result)
    return result


def beam_search_route_specs(
    benchmark_results: list[dict[str, Any]],
    candidate_specs: list[RouteSpec],
    *,
    base_method: str,
    routed_method: str,
    prediction_metric_directions: dict[str, str],
    prediction_metric_tolerances: dict[str, float] | None = None,
    slice_field_sets: list[tuple[str, ...]] | None = None,
    min_coverage_rate: float | None = None,
    max_depth: int = 1,
    beam_width: int = 10,
    max_prediction_failures: int = 0,
) -> list[RouteBeamResult]:
    frontier: list[tuple[RouteSpec, ...]] = [()]
    results: list[RouteBeamResult] = []

    for _depth in range(max(0, max_depth)):
        expanded: list[RouteBeamResult] = []
        for current_specs in frontier:
            current_keys = {_route_spec_key(spec) for spec in current_specs}
            for candidate in candidate_specs:
                if _route_spec_key(candidate) in current_keys:
                    continue
                route_specs = (*current_specs, candidate)
                benchmark_evaluations = tuple(
                    evaluate_route_specs_against_benchmark(
                        benchmark_result,
                        base_method=base_method,
                        routed_method=routed_method,
                        route_specs=list(route_specs),
                        prediction_metric_directions=prediction_metric_directions,
                        prediction_metric_tolerances=prediction_metric_tolerances or {},
                        slice_field_sets=slice_field_sets or [],
                        min_coverage_rate=min_coverage_rate,
                        force=True,
                    )
                    for benchmark_result in benchmark_results
                )
                changed_count = sum(
                    evaluation["route_application"].changed_count
                    for evaluation in benchmark_evaluations
                )
                if not changed_count:
                    continue
                total_prediction_failures = sum(
                    evaluation["acceptance_gates"]["prediction_metrics"]["failure_count"]
                    for evaluation in benchmark_evaluations
                )
                if total_prediction_failures > max_prediction_failures:
                    continue
                total_slice_failures = sum(
                    evaluation["acceptance_gates"]["slice_leadership"]["failure_count"]
                    for evaluation in benchmark_evaluations
                )
                expanded.append(
                    RouteBeamResult(
                        route_specs=route_specs,
                        total_slice_failures=total_slice_failures,
                        total_prediction_failures=total_prediction_failures,
                        changed_count=changed_count,
                        benchmark_results=benchmark_evaluations,
                    )
                )
        expanded.sort(key=_route_beam_sort_key)
        results.extend(expanded)
        frontier = [result.route_specs for result in expanded[: max(1, beam_width)]]
        if not frontier:
            break

    results.sort(key=_route_beam_sort_key)
    return results


def extract_failed_slice_filters(
    benchmark_result: dict[str, Any],
    *,
    limit: int | None = None,
    min_failure_count: int = 1,
) -> list[FailedSliceFilter]:
    slices: list[FailedSliceFilter] = []
    for field, groups in benchmark_result.get("slice_leadership_audit", {}).items():
        for group, audit in groups.items():
            failure_count = int(audit.get("failure_count", 0) or 0)
            if failure_count < min_failure_count:
                continue
            filters = _parse_slice_group(group)
            if not filters:
                continue
            slices.append(
                FailedSliceFilter(
                    field=field,
                    group=group,
                    filters=filters,
                    failure_count=failure_count,
                    primary_rows=int(audit.get("primary_rows", 0) or 0),
                )
            )
    slices.sort(key=lambda item: (-item.failure_count, -item.primary_rows, item.field, item.group))
    return slices[:limit] if limit is not None else slices


def generate_route_candidates(
    failed_slices: list[FailedSliceFilter],
    *,
    expert_methods: list[str],
    modes: tuple[str, ...] = ("score", "rank", "both"),
) -> list[RouteSpec]:
    specs: list[RouteSpec] = []
    seen: set[tuple[Any, ...]] = set()
    for failed_slice in failed_slices:
        for method in expert_methods:
            for mode in modes:
                rank_method = method if mode in {"rank", "both"} else None
                score_method = method if mode in {"score", "both"} else None
                key = (tuple(sorted(failed_slice.filters.items())), rank_method, score_method)
                if key in seen:
                    continue
                seen.add(key)
                specs.append(
                    RouteSpec(
                        name=_route_candidate_name(failed_slice, method, mode),
                        filters=dict(failed_slice.filters),
                        rank_method=rank_method,
                        score_method=score_method,
                    )
                )
    return specs


def quick_score_route_spec(
    predictions: list[dict[str, Any]],
    *,
    base_method: str,
    route_spec: RouteSpec,
) -> QuickRouteScore:
    by_case_method = {
        (row.get("target_year"), row.get("opportunity_key"), row.get("method")): row
        for row in predictions
    }
    matched_count = 0
    changed_count = 0
    rank_error_delta = 0.0
    score_error_delta = 0.0

    for row in predictions:
        if row.get("method") != base_method or not _matches_spec(row, route_spec):
            continue
        matched_count += 1
        changed = False
        if route_spec.rank_method:
            expert = by_case_method.get((row.get("target_year"), row.get("opportunity_key"), route_spec.rank_method))
            if expert and expert.get("predicted_rank") is not None:
                candidate_rank = _blend_numeric(
                    row.get("predicted_rank"),
                    expert.get("predicted_rank"),
                    route_spec.rank_weight,
                    round_to_int=True,
                )
                delta = _absolute_error(candidate_rank, row.get("actual_rank")) - _absolute_error(
                    row.get("predicted_rank"),
                    row.get("actual_rank"),
                )
                if delta is not None:
                    rank_error_delta += delta
                    changed = True
        if route_spec.score_method:
            expert = by_case_method.get((row.get("target_year"), row.get("opportunity_key"), route_spec.score_method))
            if expert and expert.get("predicted_score") is not None:
                candidate_score = _blend_numeric(
                    row.get("predicted_score"),
                    expert.get("predicted_score"),
                    route_spec.score_weight,
                )
                delta = _absolute_error(candidate_score, row.get("actual_score")) - _absolute_error(
                    row.get("predicted_score"),
                    row.get("actual_score"),
                )
                if delta is not None:
                    score_error_delta += delta
                    changed = True
        if changed:
            changed_count += 1

    improved_metric_count = int(rank_error_delta < 0) + int(score_error_delta < 0)
    return QuickRouteScore(
        route_spec=route_spec,
        matched_count=matched_count,
        changed_count=changed_count,
        rank_error_delta=rank_error_delta,
        score_error_delta=score_error_delta,
        improved_metric_count=improved_metric_count,
    )


def _matches_spec(row: dict[str, Any], spec: RouteSpec) -> bool:
    for field, expected in spec.filters.items():
        if not _matches_value(row.get(field), expected):
            return False
    for field, needle in spec.contains.items():
        if str(needle) not in str(row.get(field) or ""):
            return False
    return True


def _matches_value(actual: Any, expected: Any) -> bool:
    if isinstance(expected, (set, tuple, list, frozenset)):
        return any(_matches_value(actual, item) for item in expected)
    return actual == expected


def _append_warning(row: dict[str, Any], warning: str) -> None:
    row["warnings"] = [*(row.get("warnings") or []), warning]


def _route_warning(spec: RouteSpec, *, kind: str, method: str) -> str:
    weight = spec.rank_weight if kind == "rank" else spec.score_weight
    warning = f"route={spec.name}:{kind}={method}"
    if weight != 1.0:
        warning = f"{warning}:weight={weight:g}"
    if kind == "rank" and not spec.update_planning_rank:
        warning = f"{warning}:planning=base"
    return warning


def _blend_numeric(base_value: Any, expert_value: Any, weight: float, *, round_to_int: bool = False) -> float | int:
    if base_value is None or weight >= 1.0:
        blended = float(expert_value)
    else:
        blended = (float(base_value) * (1.0 - weight)) + (float(expert_value) * weight)
    if round_to_int:
        return round(blended)
    return blended


def _parse_slice_group(group: str) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    for part in group.split("|"):
        if "=" not in part:
            return {}
        field, value = part.split("=", 1)
        filters[field] = _parse_filter_value(field, value)
    return filters


def _parse_filter_value(field: str, value: str) -> Any:
    if field == "target_year":
        try:
            return int(value)
        except ValueError:
            return value
    return value


def _route_candidate_name(failed_slice: FailedSliceFilter, method: str, mode: str) -> str:
    normalized_group = (
        failed_slice.group.replace("|", "__")
        .replace("=", "-")
        .replace(" ", "_")
        .replace("/", "_")
    )
    return f"{failed_slice.field}:{normalized_group}:{method}:{mode}"


def _route_spec_key(spec: RouteSpec) -> tuple[Any, ...]:
    return (
        spec.name,
        tuple(sorted(spec.filters.items())),
        tuple(sorted(spec.contains.items())),
        spec.rank_method,
        spec.score_method,
        spec.rank_weight,
        spec.score_weight,
        spec.update_planning_rank,
    )


def _route_beam_sort_key(result: RouteBeamResult) -> tuple[Any, ...]:
    return (
        result.total_prediction_failures,
        result.total_slice_failures,
        -result.changed_count,
        tuple(spec.name for spec in result.route_specs),
    )


def _absolute_error(predicted: Any, actual: Any) -> float | None:
    if predicted is None or actual is None:
        return None
    return abs(float(predicted) - float(actual))


def _metrics_with_coverage(predictions: list[dict[str, Any]], case_count: int) -> dict[str, dict[str, Any]]:
    metrics = evaluate_predictions(predictions)
    denominator = case_count or 1
    for method_metrics in metrics.values():
        method_metrics["coverage_rate"] = round(float(method_metrics.get("rank_row_count", 0)) / denominator, 4)
    return metrics


def _group_metrics(
    predictions: list[dict[str, Any]],
    slice_field_sets: list[tuple[str, ...]],
) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    return {
        "|".join(fields): evaluate_predictions_by_group(predictions, list(fields))
        for fields in slice_field_sets
    }


def _merge_candidate_group_metrics(
    existing_group_metrics: dict[str, Any],
    candidate_predictions: list[dict[str, Any]],
    slice_field_sets: list[tuple[str, ...]],
    routed_method: str,
) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    merged = {
        field: {group: dict(method_metrics) for group, method_metrics in groups.items()}
        for field, groups in existing_group_metrics.items()
    }
    candidate_group_metrics = _group_metrics(candidate_predictions, slice_field_sets)
    for field, groups in candidate_group_metrics.items():
        field_groups = merged.setdefault(field, {})
        for group, candidate_metrics in groups.items():
            group_methods = dict(field_groups.get(group, {}))
            if routed_method in candidate_metrics:
                group_methods[routed_method] = candidate_metrics[routed_method]
            field_groups[group] = _sort_method_metrics(group_methods)
    return merged


def _sort_method_metrics(metrics: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {method: metrics[method] for method in sorted(metrics)}


def _slice_leadership_audit(
    group_metrics: dict[str, dict[str, dict[str, dict[str, Any]]]],
    *,
    primary_method: str,
    metric_directions: dict[str, str],
    metric_tolerances: dict[str, float],
) -> dict[str, dict[str, Any]]:
    audits: dict[str, dict[str, Any]] = {}
    for field, groups in group_metrics.items():
        field_audits: dict[str, Any] = {}
        for group, metrics in groups.items():
            if primary_method not in metrics:
                continue
            rows = audit_metric_leadership(
                metrics,
                primary_method=primary_method,
                metric_directions=metric_directions,
                metric_tolerances=metric_tolerances,
            )
            field_audits[group] = {
                "primary_method": primary_method,
                "primary_rows": metrics.get(primary_method, {}).get("row_count", 0),
                "failure_count": sum(1 for row in rows if row["status"] == "fail"),
                "prediction_metrics": rows,
            }
        if field_audits:
            audits[field] = field_audits
    return audits


def _acceptance_gates(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    leadership = result.get("leadership_audit", {})
    prediction_failures = sum(1 for row in leadership.get("prediction_metrics", []) if row.get("status") == "fail")
    plan_failures = sum(1 for row in leadership.get("plan_metrics", []) if row.get("status") == "fail")
    slice_failed_groups = 0
    slice_failed_metrics = 0
    for groups in result.get("slice_leadership_audit", {}).values():
        for group_audit in groups.values():
            failures = int(group_audit.get("failure_count", 0) or 0)
            if failures:
                slice_failed_groups += 1
                slice_failed_metrics += failures
    return {
        "prediction_metrics": {
            "status": "fail" if prediction_failures else "pass",
            "failure_count": prediction_failures,
        },
        "plan_metrics": {
            "status": "fail" if plan_failures else "pass",
            "failure_count": plan_failures,
        },
        "slice_leadership": {
            "status": "fail" if slice_failed_metrics else "pass",
            "failure_count": slice_failed_metrics,
            "failed_group_count": slice_failed_groups,
            "failed_metric_count": slice_failed_metrics,
        },
    }
