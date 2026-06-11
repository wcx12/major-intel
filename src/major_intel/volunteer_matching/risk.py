"""Rank-first risk prediction primitives."""

from __future__ import annotations

from statistics import pstdev

from .models import AdmissionHistory, ApplicantContext, Opportunity, RankPrediction, RiskDecision


RECENT_WEIGHTS = (0.55, 0.30, 0.15)


def predict_rank_cutoff(
    history: list[AdmissionHistory],
    target_year: int,
    method: str = "weighted_recent_rank",
) -> RankPrediction:
    usable = recent_history(history, target_year, limit=len(RECENT_WEIGHTS))
    if not usable:
        raise ValueError("at least one prior admission history row is required")

    weights = RECENT_WEIGHTS[: len(usable)]
    weight_sum = sum(weights)
    rank = round(sum(item.cutoff_rank * weight for item, weight in zip(usable, weights)) / weight_sum)
    score = _weighted_score(usable, weights, weight_sum)
    return RankPrediction(
        method=method,
        predicted_rank=rank,
        predicted_score=score,
        confidence=history_confidence(usable),
        evidence_years=[item.year for item in usable],
    )


def recent_history(
    history: list[AdmissionHistory],
    target_year: int,
    limit: int | None = None,
) -> list[AdmissionHistory]:
    rows = [item for item in history if item.year < target_year and item.cutoff_rank > 0]
    rows.sort(key=lambda item: item.year, reverse=True)
    if limit is not None:
        return rows[:limit]
    return rows


def history_confidence(history: list[AdmissionHistory]) -> float:
    if not history:
        return 0.0
    base = min(1.0, 0.35 + 0.20 * len(history))
    ranks = [item.cutoff_rank for item in history if item.cutoff_rank > 0]
    if len(ranks) < 2:
        return round(base * 0.75, 3)
    mean_rank = sum(ranks) / len(ranks)
    volatility = pstdev(ranks) / mean_rank if mean_rank else 1.0
    penalty = max(0.30, 1.0 - volatility * 3.0)
    return round(max(0.05, min(1.0, base * penalty)), 3)


def risk_bucket(
    applicant: ApplicantContext,
    opportunity: Opportunity,
    predicted_rank: int,
    confidence: float,
) -> RiskDecision:
    del opportunity
    rank_gap = int(predicted_rank) - int(applicant.rank)
    is_admissible_reference = rank_gap >= 0
    denominator = max(abs(int(predicted_rank)), 1)
    gap_ratio = rank_gap / denominator

    if gap_ratio < 0.03:
        bucket = "chong"
    elif gap_ratio >= 0.18 and confidence >= 0.45:
        bucket = "bao"
    else:
        bucket = "wen"

    warnings: list[str] = []
    if confidence < 0.4:
        warnings.append("low_confidence_history")

    return RiskDecision(
        bucket=bucket,
        rank_gap=rank_gap,
        is_admissible_reference=is_admissible_reference,
        confidence=confidence,
        warnings=warnings,
    )


def _weighted_score(
    history: list[AdmissionHistory],
    weights: tuple[float, ...],
    weight_sum: float,
) -> float | None:
    score_rows = [(item, weight) for item, weight in zip(history, weights) if item.cutoff_score is not None]
    if not score_rows:
        return None
    score_weight_sum = sum(weight for _, weight in score_rows) or weight_sum
    return round(sum(float(item.cutoff_score) * weight for item, weight in score_rows) / score_weight_sum, 2)
