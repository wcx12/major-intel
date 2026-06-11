"""Metric leadership audit helpers for volunteer matching benchmarks."""

from __future__ import annotations

from typing import Any


MetricDirections = dict[str, str]
MetricTolerances = dict[str, float]


def audit_metric_leadership(
    metrics: dict[str, dict[str, Any]],
    *,
    primary_method: str,
    metric_directions: MetricDirections,
    metric_tolerances: MetricTolerances | None = None,
    min_coverage_rate: float | None = None,
) -> list[dict[str, Any]]:
    """Report whether the primary method leads each requested metric."""
    primary_metrics = metrics.get(primary_method, {})
    tolerances = metric_tolerances or {}
    rows: list[dict[str, Any]] = []
    for metric, direction in metric_directions.items():
        primary_value = primary_metrics.get(metric)
        tolerance = tolerances.get(metric, 0.0)
        candidates, excluded_low_coverage_methods = _candidate_values(
            metrics,
            metric,
            min_coverage_rate=min_coverage_rate,
        )
        if primary_value is None:
            best_method, best_value = candidates[0] if candidates else (None, None)
            rows.append(
                {
                    "metric": metric,
                    "direction": direction,
                    "status": "fail",
                    "reason": "missing_primary_value",
                    "primary_method": primary_method,
                    "primary_value": None,
                    "best_method": best_method,
                    "best_value": best_value,
                    "excluded_low_coverage_methods": excluded_low_coverage_methods,
                }
            )
            continue
        if _below_min_coverage(primary_metrics, min_coverage_rate):
            candidates.sort(key=lambda item: item[1], reverse=direction == "desc")
            best_method, best_value = candidates[0] if candidates else (None, None)
            rows.append(
                {
                    "metric": metric,
                    "direction": direction,
                    "status": "fail",
                    "reason": "primary_coverage_below_threshold",
                    "primary_method": primary_method,
                    "primary_value": primary_value,
                    "best_method": best_method,
                    "best_value": best_value,
                    "excluded_low_coverage_methods": excluded_low_coverage_methods,
                }
            )
            continue
        if not candidates:
            rows.append(
                {
                    "metric": metric,
                    "direction": direction,
                    "status": "fail",
                    "reason": "missing_comparison_values",
                    "primary_method": primary_method,
                    "primary_value": primary_value,
                    "best_method": None,
                    "best_value": None,
                    "excluded_low_coverage_methods": excluded_low_coverage_methods,
                }
            )
            continue
        candidates.sort(key=lambda item: item[1], reverse=direction == "desc")
        best_method, best_value = candidates[0]
        is_within_tolerance = _within_tolerance(primary_value, best_value, direction, tolerance)
        is_leader = best_method == primary_method or is_within_tolerance
        reason = "leader" if best_method == primary_method else "within_tolerance" if is_within_tolerance else "not_best"
        rows.append(
            {
                "metric": metric,
                "direction": direction,
                "status": "pass" if is_leader else "fail",
                "reason": reason,
                "primary_method": primary_method,
                "primary_value": primary_value,
                "best_method": best_method,
                "best_value": best_value,
                "excluded_low_coverage_methods": excluded_low_coverage_methods,
            }
        )
    return rows


def _candidate_values(
    metrics: dict[str, dict[str, Any]],
    metric: str,
    *,
    min_coverage_rate: float | None = None,
) -> tuple[list[tuple[str, float]], list[str]]:
    values = []
    excluded_low_coverage_methods = []
    for method, method_metrics in metrics.items():
        if _below_min_coverage(method_metrics, min_coverage_rate):
            excluded_low_coverage_methods.append(method)
            continue
        value = method_metrics.get(metric)
        if value is None:
            continue
        values.append((method, float(value)))
    return values, sorted(excluded_low_coverage_methods)


def _below_min_coverage(method_metrics: dict[str, Any], min_coverage_rate: float | None) -> bool:
    if min_coverage_rate is None:
        return False
    coverage = method_metrics.get("coverage_rate")
    if coverage is None:
        return True
    return float(coverage) < min_coverage_rate


def _within_tolerance(left: Any, right: Any, direction: str, tolerance: float) -> bool:
    left_value = float(left)
    right_value = float(right)
    if direction == "desc":
        return left_value >= right_value - max(0.0, tolerance)
    return left_value <= right_value + max(0.0, tolerance)
