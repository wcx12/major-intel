"""Evaluation metrics for admission prediction benchmarks."""

from __future__ import annotations

from collections import defaultdict
from math import sqrt
from statistics import median
from typing import Any


def evaluate_predictions(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["method"])].append(row)

    return {method: _evaluate_group(method_rows) for method, method_rows in sorted(grouped.items())}


def evaluate_predictions_by_group(
    rows: list[dict[str, Any]],
    group_fields: list[str],
) -> dict[str, dict[str, dict[str, float | int]]]:
    grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = "|".join(f"{field}={row.get(field) or 'UNKNOWN'}" for field in group_fields)
        grouped_rows[key].append(row)
    return {group: evaluate_predictions(group_rows) for group, group_rows in sorted(grouped_rows.items())}


def _evaluate_group(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    rank_errors = [
        abs(int(row["predicted_rank"]) - int(row["actual_rank"]))
        for row in rows
        if row.get("predicted_rank") is not None and row.get("actual_rank") is not None
    ]
    score_errors = [
        abs(float(row["predicted_score"]) - float(row["actual_score"]))
        for row in rows
        if row.get("predicted_score") is not None and row.get("actual_score") is not None
    ]
    directional_rows = [
        row
        for row in rows
        if row.get("predicted_rank") is not None and row.get("actual_rank") is not None
    ]

    over_rate = _direction_rate(directional_rows, "over")
    under_rate = _direction_rate(directional_rows, "under")
    severe_optimistic_rate, severe_pessimistic_rate = _severe_direction_rates(directional_rows)
    signed_rank_errors = [
        int(row["predicted_rank"]) - int(row["actual_rank"])
        for row in directional_rows
    ]
    metrics: dict[str, float | int] = {
        "row_count": len(rows),
        "rank_row_count": len(rank_errors),
        "score_row_count": len(score_errors),
        "mae_rank": _maybe_int(_mean(rank_errors)),
        "median_ae_rank": _maybe_int(median(rank_errors) if rank_errors else None),
        "p90_ae_rank": _maybe_int(_percentile(rank_errors, 0.90)),
        "rmse_rank": _maybe_int(_rmse(rank_errors)),
        "mean_signed_rank_error": _maybe_int(_mean(signed_rank_errors)),
        "mae_score": _maybe_int(_mean(score_errors)),
        "median_ae_score": _maybe_int(median(score_errors) if score_errors else None),
        "p90_ae_score": _maybe_int(_percentile(score_errors, 0.90)),
        "rmse_score": _maybe_int(_rmse(score_errors)),
        "within_3_score_points": _within(score_errors, 3),
        "within_5_score_points": _within(score_errors, 5),
        "within_10_score_points": _within(score_errors, 10),
        "overestimate_risk_rate": over_rate,
        "underestimate_risk_rate": under_rate,
        "optimistic_error_rate": over_rate,
        "pessimistic_error_rate": under_rate,
        "severe_optimistic_rate": severe_optimistic_rate,
        "severe_pessimistic_rate": severe_pessimistic_rate,
        "severe_directional_balance_abs": _directional_bias_abs(severe_optimistic_rate, severe_pessimistic_rate),
        "severe_error_rate": _sum_rates(severe_optimistic_rate, severe_pessimistic_rate),
        "directional_bias_abs": _directional_bias_abs(over_rate, under_rate),
    }
    return metrics


def _mean(values: list[float | int]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _within(errors: list[float], threshold: float) -> float | None:
    if not errors:
        return None
    return sum(1 for error in errors if error <= threshold) / len(errors)


def _rmse(errors: list[float | int]) -> float | None:
    if not errors:
        return None
    return sqrt(sum(float(error) ** 2 for error in errors) / len(errors))


def _percentile(values: list[float | int], percentile: float) -> float | None:
    if not values:
        return None
    sorted_values = sorted(float(value) for value in values)
    index = min(len(sorted_values) - 1, max(0, round((len(sorted_values) - 1) * percentile)))
    return sorted_values[index]


def _direction_rate(rows: list[dict[str, Any]], direction: str) -> float | None:
    if not rows:
        return None
    if direction == "over":
        count = sum(1 for row in rows if int(row["predicted_rank"]) > int(row["actual_rank"]))
    else:
        count = sum(1 for row in rows if int(row["predicted_rank"]) < int(row["actual_rank"]))
    return count / len(rows)


def _directional_bias_abs(over_rate: float | None, under_rate: float | None) -> float | None:
    if over_rate is None or under_rate is None:
        return None
    return abs(over_rate - under_rate)


def _severe_direction_rates(rows: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    if not rows:
        return None, None
    severe_optimistic = 0
    severe_pessimistic = 0
    for row in rows:
        actual = int(row["actual_rank"])
        predicted = int(row["predicted_rank"])
        threshold = max(3000, actual * 0.10)
        if predicted - actual >= threshold:
            severe_optimistic += 1
        if actual - predicted >= threshold:
            severe_pessimistic += 1
    return severe_optimistic / len(rows), severe_pessimistic / len(rows)


def _sum_rates(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left + right


def _maybe_int(value: float | None) -> float | int | None:
    if value is None:
        return None
    if float(value).is_integer():
        return int(value)
    return round(value, 4)
