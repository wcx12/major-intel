"""Plan-level volunteer recommendation metrics."""

from __future__ import annotations

from collections import defaultdict
from math import log2
from statistics import mean
from typing import Any


DEFAULT_BUCKET_QUOTAS = {"chong": 2, "wen": 3, "bao": 2}
VOLUNTEER_MATCHING_BUCKET_QUOTAS = {"chong": 0, "wen": 1, "bao": 6}
VOLUNTEER_MATCHING_SORT_TARGETS = {"chong": -1500, "wen": 5000, "bao": 4000}
VOLUNTEER_MATCHING_METHODS = {
    "volunteer_matching_prediction_expert_router",
    "volunteer_matching_meta_router",
    "volunteer_matching_rank_ensemble",
    "volunteer_matching_segmented_rank_ensemble",
}
SAFETY_GATED_REGRET_MIN_ADMISSIBLE_RATE = 0.80
SAFETY_GATED_REGRET_MAX_FIRST_POSITION = 2.0


def synthetic_applicant_ranks(predictions: list[dict[str, Any]], count: int = 5) -> list[int]:
    ranks = sorted({int(row["actual_rank"]) for row in predictions if row.get("actual_rank") is not None})
    if not ranks or count <= 0:
        return []
    return [
        ranks[min(len(ranks) - 1, max(0, round((len(ranks) - 1) * ((index + 1) / (count + 1)))))]
        for index in range(count)
    ]


def build_rank_plan(
    predictions: list[dict[str, Any]],
    applicant_rank: int,
    total_slots: int = 7,
    bucket_quotas: dict[str, int] | None = None,
    sort_targets: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    quotas = bucket_quotas or DEFAULT_BUCKET_QUOTAS
    candidates = [
        _annotate_candidate(row, applicant_rank, sort_targets)
        for row in predictions
        if row.get("predicted_rank") is not None
    ]
    by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_bucket[str(candidate["bucket"])].append(candidate)
    for rows in by_bucket.values():
        rows.sort(key=lambda row: (row["sort_distance"], row["predicted_rank"], row["opportunity_key"]))

    plan: list[dict[str, Any]] = []
    used_keys: set[str] = set()
    for bucket in ("chong", "wen", "bao"):
        selected_in_bucket = 0
        bucket_quota = max(0, quotas.get(bucket, 0))
        for candidate in by_bucket.get(bucket, []):
            if selected_in_bucket >= bucket_quota:
                break
            if candidate["opportunity_key"] not in used_keys:
                plan.append(candidate)
                used_keys.add(str(candidate["opportunity_key"]))
                selected_in_bucket += 1

    if len(plan) < total_slots:
        remaining = [candidate for candidate in candidates if candidate["opportunity_key"] not in used_keys]
        remaining.sort(key=lambda row: (row["bucket_order"], row["sort_distance"], row["predicted_rank"], row["opportunity_key"]))
        plan.extend(remaining[: total_slots - len(plan)])

    return plan[:total_slots]


def build_method_rank_plan(
    method: str,
    predictions: list[dict[str, Any]],
    applicant_rank: int,
    total_slots: int = 7,
    bucket_quotas: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    quotas = bucket_quotas
    sort_targets = None
    if quotas is None and method in VOLUNTEER_MATCHING_METHODS:
        quotas = VOLUNTEER_MATCHING_BUCKET_QUOTAS
        sort_targets = VOLUNTEER_MATCHING_SORT_TARGETS
    return build_rank_plan(predictions, applicant_rank, total_slots, quotas or DEFAULT_BUCKET_QUOTAS, sort_targets)


def evaluate_rank_plans(
    predictions: list[dict[str, Any]],
    applicant_ranks: list[int] | None = None,
    total_slots: int = 7,
    bucket_quotas: dict[str, int] | None = None,
) -> dict[str, dict[str, float | int]]:
    rows_by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in predictions:
        rows_by_method[str(row["method"])].append(row)
    ranks = applicant_ranks or synthetic_applicant_ranks(predictions)

    return {
        method: _evaluate_method_plans(method, method_rows, ranks, total_slots, bucket_quotas or DEFAULT_BUCKET_QUOTAS)
        for method, method_rows in sorted(rows_by_method.items())
    }


def _evaluate_method_plans(
    method: str,
    predictions: list[dict[str, Any]],
    applicant_ranks: list[int],
    total_slots: int,
    bucket_quotas: dict[str, int],
) -> dict[str, float | int]:
    method_quotas = None if method in VOLUNTEER_MATCHING_METHODS else bucket_quotas
    plan_pairs = [
        (rank, build_method_rank_plan(method, predictions, rank, total_slots, method_quotas))
        for rank in applicant_ranks
    ]
    plan_pairs = [(rank, plan) for rank, plan in plan_pairs if plan]
    if not plan_pairs:
        return {
            "plan_count": 0,
            "recommendation_count": 0,
            "admissible_rate": 0.0,
            "first_admissible_position_mean": 0.0,
            "bucket_balance_error": 1.0,
            "ndcg": 0.0,
            "no_offer_rate": 1.0,
            "expected_utility": 0.0,
            "regret": 0.0,
            "safety_gated_regret": None,
        }

    admissible_rates = []
    first_positions = []
    balance_errors = []
    ndcgs = []
    no_offer_flags = []
    utilities = []
    regrets = []
    for applicant_rank, plan in plan_pairs:
        admissible = [1 if int(item["actual_rank"]) >= applicant_rank else 0 for item in plan]
        admissible_rates.append(sum(admissible) / len(plan))
        first_positions.append(_first_position(admissible))
        balance_errors.append(_bucket_balance_error(plan, method_quotas or VOLUNTEER_MATCHING_BUCKET_QUOTAS))
        ndcgs.append(_ndcg(plan, applicant_rank))
        no_offer_flags.append(0 if any(admissible) else 1)
        utilities.append(_expected_utility(plan, applicant_rank))
        regrets.append(_regret(predictions, plan, applicant_rank))

    metrics = {
        "plan_count": len(plan_pairs),
        "recommendation_count": sum(len(plan) for _, plan in plan_pairs),
        "admissible_rate": _rounded_mean(admissible_rates),
        "first_admissible_position_mean": _rounded_mean(first_positions),
        "bucket_balance_error": _rounded_mean(balance_errors),
        "ndcg": _rounded_mean(ndcgs),
        "no_offer_rate": _rounded_mean(no_offer_flags),
        "expected_utility": _rounded_mean(utilities),
        "regret": _rounded_mean(regrets),
    }
    metrics["safety_gated_regret"] = _safety_gated_regret(metrics)
    return metrics


def _annotate_candidate(row: dict[str, Any], applicant_rank: int, sort_targets: dict[str, int] | None = None) -> dict[str, Any]:
    predicted_rank = int(row["predicted_rank"])
    planning_rank = int(row.get("planning_rank") or predicted_rank)
    predicted_gap = planning_rank - int(applicant_rank)
    bucket = _bucket_from_gap(predicted_gap, planning_rank)
    annotated = dict(row)
    annotated.update(
        {
            "planning_rank": planning_rank,
            "bucket": bucket,
            "predicted_gap": predicted_gap,
            "actual_gap": int(row["actual_rank"]) - int(applicant_rank),
            "sort_distance": _sort_distance(bucket, predicted_gap, sort_targets),
            "bucket_order": {"wen": 0, "bao": 1, "chong": 2}.get(bucket, 3),
        }
    )
    return annotated


def _bucket_from_gap(predicted_gap: int, predicted_rank: int) -> str:
    denominator = max(abs(predicted_rank), 1)
    ratio = predicted_gap / denominator
    if ratio < 0.03:
        return "chong"
    if ratio >= 0.18:
        return "bao"
    return "wen"


def _sort_distance(bucket: str, predicted_gap: int, sort_targets: dict[str, int] | None = None) -> float:
    targets = sort_targets or {"chong": -1500, "wen": 2500, "bao": 8000}
    return abs(predicted_gap - targets.get(bucket, 0))


def _first_position(flags: list[int]) -> int:
    for index, flag in enumerate(flags, start=1):
        if flag:
            return index
    return len(flags) + 1


def _bucket_balance_error(plan: list[dict[str, Any]], quotas: dict[str, int]) -> float:
    if not plan:
        return 1.0
    desired_total = sum(max(0, value) for value in quotas.values()) or len(plan)
    actual_counts = defaultdict(int)
    for item in plan:
        actual_counts[str(item["bucket"])] += 1
    buckets = set(quotas) | set(actual_counts)
    return sum(abs(actual_counts[bucket] / len(plan) - max(0, quotas.get(bucket, 0)) / desired_total) for bucket in buckets) / 2


def _ndcg(plan: list[dict[str, Any]], applicant_rank: int) -> float:
    gains = [_relevance(item, applicant_rank) for item in plan]
    dcg = sum(gain / log2(index + 2) for index, gain in enumerate(gains))
    ideal = sorted(gains, reverse=True)
    idcg = sum(gain / log2(index + 2) for index, gain in enumerate(ideal))
    if idcg <= 0:
        return 0.0
    return dcg / idcg


def _expected_utility(plan: list[dict[str, Any]], applicant_rank: int) -> float:
    if not plan:
        return 0.0
    return mean(_relevance(item, applicant_rank) for item in plan)


def _regret(predictions: list[dict[str, Any]], plan: list[dict[str, Any]], applicant_rank: int) -> float:
    best_available = max((_relevance(item, applicant_rank) for item in predictions), default=0.0)
    best_selected = max((_relevance(item, applicant_rank) for item in plan), default=0.0)
    return max(0.0, best_available - best_selected)


def _safety_gated_regret(metrics: dict[str, float | int | None]) -> float | None:
    if (metrics.get("no_offer_rate") or 0.0) > 0:
        return None
    if float(metrics.get("admissible_rate") or 0.0) < SAFETY_GATED_REGRET_MIN_ADMISSIBLE_RATE:
        return None
    if float(metrics.get("first_admissible_position_mean") or 0.0) > SAFETY_GATED_REGRET_MAX_FIRST_POSITION:
        return None
    regret = metrics.get("regret")
    return float(regret) if regret is not None else None


def _relevance(item: dict[str, Any], applicant_rank: int) -> float:
    actual_gap = int(item["actual_rank"]) - int(applicant_rank)
    if actual_gap < 0:
        return 0.0
    return 1.0 / (1.0 + abs(actual_gap - 3000) / 10000.0)


def _rounded_mean(values: list[float | int]) -> float:
    return round(mean(values), 4) if values else 0.0
