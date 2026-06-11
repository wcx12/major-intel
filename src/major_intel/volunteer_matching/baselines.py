"""Deterministic baseline methods for volunteer matching benchmarks."""

from __future__ import annotations

from collections.abc import Callable
from statistics import mean, median, pstdev

from .models import AdmissionHistory, PredictionCase, RankPrediction
from .risk import history_confidence, predict_rank_cutoff, recent_history


BaselineFn = Callable[[PredictionCase], RankPrediction]
STRUCTURED_SCORE_FALLBACK_PROVINCES = {"33", "61"}


def baseline_names() -> list[str]:
    return list(BASELINES.keys())


def predict_with_baseline(name: str, case: PredictionCase) -> RankPrediction:
    try:
        fn = BASELINES[name]
    except KeyError as exc:
        raise KeyError(f"unknown baseline: {name}") from exc
    return fn(case)


def _training_history(case: PredictionCase) -> list[AdmissionHistory]:
    rows = recent_history(case.history, case.target_year)
    if not rows:
        raise ValueError(f"{case.opportunity_key} has no prior-year history")
    return rows


def _prediction(
    method: str,
    rank: float,
    history: list[AdmissionHistory],
    score: float | None = None,
    warnings: list[str] | None = None,
) -> RankPrediction:
    if score is None:
        score = _mean_score(history)
    return RankPrediction(
        method=method,
        predicted_rank=max(1, round(rank)),
        predicted_score=round(score, 2) if score is not None else None,
        confidence=history_confidence(history),
        evidence_years=[item.year for item in history],
        warnings=warnings or [],
    )


def _last_year(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)[:1]
    return _prediction("last_year_rank", rows[0].cutoff_rank, rows, rows[0].cutoff_score)


def _recent_mean(case: PredictionCase, method: str, n: int) -> RankPrediction:
    rows = _training_history(case)[:n]
    return _prediction(method, mean(item.cutoff_rank for item in rows), rows)


def _historical_mean(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)
    return _prediction("historical_mean_rank", mean(item.cutoff_rank for item in rows), rows)


def _historical_median(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)
    return _prediction("historical_median_rank", median(item.cutoff_rank for item in rows), rows)


def _weighted_recent(case: PredictionCase) -> RankPrediction:
    return predict_rank_cutoff(case.history, case.target_year, method="weighted_recent_rank")


def _exponential_smoothing(case: PredictionCase) -> RankPrediction:
    rows = list(reversed(_training_history(case)))
    smoothed = float(rows[0].cutoff_rank)
    alpha = 0.60
    for row in rows[1:]:
        smoothed = alpha * row.cutoff_rank + (1 - alpha) * smoothed
    rows_desc = list(reversed(rows))
    return _prediction("exponential_smoothing_rank", smoothed, rows_desc)


def _linear_trend(case: PredictionCase) -> RankPrediction:
    rows = list(reversed(_training_history(case)))
    if len(rows) < 2:
        return _last_year(case)
    x_mean = mean(item.year for item in rows)
    y_mean = mean(item.cutoff_rank for item in rows)
    denominator = sum((item.year - x_mean) ** 2 for item in rows)
    if denominator == 0:
        return _last_year(case)
    slope = sum((item.year - x_mean) * (item.cutoff_rank - y_mean) for item in rows) / denominator
    predicted = y_mean + slope * (case.target_year - x_mean)
    return _prediction("linear_trend_rank", predicted, list(reversed(rows)))


def _volatility_conservative(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)
    ranks = [item.cutoff_rank for item in rows[:3]]
    base = ranks[0]
    buffer = pstdev(ranks) if len(ranks) > 1 else max(base * 0.05, 1)
    return _prediction("volatility_conservative_rank", base + buffer, rows[:3])


def _plan_adjusted_mean(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)[:3]
    base = mean(item.cutoff_rank for item in rows)
    plan_rows = [item.plan_count for item in rows if item.plan_count and item.plan_count > 0]
    if len(plan_rows) < 2:
        return _prediction("plan_adjusted_mean_rank", base, rows, warnings=["missing_plan_count"])
    latest_plan = float(plan_rows[0])
    avg_plan = mean(plan_rows)
    factor = min(1.25, max(0.75, latest_plan / avg_plan))
    return _prediction("plan_adjusted_mean_rank", base * factor, rows)


def _best_recent(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)[:3]
    return _prediction("best_recent_rank", min(item.cutoff_rank for item in rows), rows)


def _worst_recent(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)[:3]
    return _prediction("worst_recent_rank", max(item.cutoff_rank for item in rows), rows)


def _ensemble(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)
    historical_rank = mean(item.cutoff_rank for item in rows)
    recent_ranks = [item.cutoff_rank for item in rows[:3]]
    best_recent_rank = min(recent_ranks)
    latest_rank = rows[0].cutoff_rank
    predicted_rank = historical_rank * 0.80 + float(best_recent_rank) * 0.08 + float(latest_rank) * 0.12
    if len(rows) == 1:
        if latest_rank >= 67500:
            predicted_rank -= 6750
    elif max(recent_ranks) - min(recent_ranks) <= 17500:
        predicted_rank = 0.75 * predicted_rank + 0.25 * float(latest_rank)
    predicted_score = None
    if _score_rank_points_allowed(case.metadata):
        predicted_score = _score_from_rank_points(case.metadata.get("target_score_rank_points"), predicted_rank)
        if predicted_score is not None:
            predicted_score += _score_rank_residual_adjustment(case.metadata)
    if predicted_score is None:
        predicted_score = _calibrated_score(rows)
    return RankPrediction(
        method="volunteer_matching_rank_ensemble",
        predicted_rank=max(1, round(predicted_rank)),
        predicted_score=round(predicted_score, 2) if predicted_score is not None else None,
        confidence=min(1.0, round(history_confidence(rows) + 0.05, 3)),
        evidence_years=[item.year for item in rows],
        warnings=[],
    )


def _segmented_ensemble(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)
    ensemble = _ensemble(case)
    predicted_rank = float(ensemble.predicted_rank)
    predicted_score = _segmented_score(case, rows, ensemble.predicted_score)
    warnings = list(ensemble.warnings)
    if _last_year_segment(case, rows):
        predicted_rank = float(rows[0].cutoff_rank)
        warnings.append("segmented_rank_last_year")
    elif _historical_mean_segment(case):
        predicted_rank = mean(item.cutoff_rank for item in rows)
        warnings.append("segmented_rank_historical_mean")
    predicted_rank += _batch_directional_offset(case.metadata)
    return RankPrediction(
        method="volunteer_matching_segmented_rank_ensemble",
        predicted_rank=max(1, round(predicted_rank)),
        predicted_score=predicted_score,
        confidence=ensemble.confidence,
        evidence_years=ensemble.evidence_years,
        warnings=warnings,
        planning_rank=ensemble.predicted_rank,
    )


def _meta_router(case: PredictionCase) -> RankPrediction:
    rows = _training_history(case)
    segmented = _segmented_ensemble(case)
    rank_expert = _select_rank_expert(case, rows)
    routed_rank = _rank_from_expert(case, rank_expert, segmented)
    warnings = list(segmented.warnings)
    warnings.append(f"rank_expert={rank_expert}")
    predicted_rank = routed_rank.predicted_rank + _rank_offset(case, warnings)
    predicted_score = segmented.predicted_score
    score_expert = _select_score_expert(case)
    if score_expert != "volunteer_matching_segmented_rank_ensemble":
        predicted_score = _score_from_expert(case, score_expert, predicted_score)
        warnings.append(f"score_expert={score_expert}")
    return RankPrediction(
        method="volunteer_matching_meta_router",
        predicted_rank=max(1, predicted_rank),
        predicted_score=predicted_score,
        confidence=min(segmented.confidence, routed_rank.confidence),
        evidence_years=segmented.evidence_years,
        warnings=warnings,
        planning_rank=segmented.planning_rank,
    )


def _select_rank_expert(case: PredictionCase, rows: list[AdmissionHistory]) -> str:
    del rows
    if _guangdong_2024_school_undergraduate_segment(case):
        return "volatility_conservative_rank"
    if _zhejiang_2024_first_major_rank_segment(case):
        return "best_recent_rank"
    if _zhejiang_2025_first_major_rank_segment(case):
        return "exponential_smoothing_rank"
    return "volunteer_matching_segmented_rank_ensemble"


def _rank_from_expert(case: PredictionCase, expert: str, fallback: RankPrediction) -> RankPrediction:
    if expert == "volatility_conservative_rank":
        return _volatility_conservative(case)
    if expert == "volunteer_matching_rank_ensemble":
        return _ensemble(case)
    if expert == "best_recent_rank":
        return _best_recent(case)
    if expert == "exponential_smoothing_rank":
        return _exponential_smoothing(case)
    return fallback


def _select_score_expert(case: PredictionCase) -> str:
    if _guangdong_2022_school_vocational_score_segment(case):
        return "volunteer_matching_rank_ensemble"
    if _guangdong_school_vocational_score_segment(case):
        return "last_year_rank"
    if _guangdong_2024_school_undergraduate_segment(case):
        return "two_year_mean_rank"
    if _zhejiang_2025_first_major_score_segment(case):
        return "weighted_recent_rank"
    return "volunteer_matching_segmented_rank_ensemble"


def _score_from_expert(case: PredictionCase, expert: str, fallback: float | None) -> float | None:
    if expert == "last_year_rank":
        return _last_year(case).predicted_score
    if expert == "volunteer_matching_rank_ensemble":
        return _ensemble(case).predicted_score
    if expert == "two_year_mean_rank":
        return _recent_mean(case, "two_year_mean_rank", 2).predicted_score
    if expert == "weighted_recent_rank":
        return _weighted_recent(case).predicted_score
    if expert == "best_recent_rank":
        return _best_recent(case).predicted_score
    return fallback


def _rank_offset(case: PredictionCase, warnings: list[str]) -> int:
    if _guangdong_school_vocational_rank_offset_segment(case):
        if case.target_year == 2024:
            warnings.append("rank_offset=guangdong_2024_school_vocational:+8000")
            return 8000
        if case.target_year in {2022, 2023}:
            warnings.append(f"rank_offset=guangdong_{case.target_year}_school_vocational:+1000")
            return 1000
    return 0


def _zhejiang_2024_rank_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    province_name = str(case.metadata.get("province_name") or "")
    return case.target_year == 2024 and (province_id == "33" or province_name == "\u6d59\u6c5f")


def _zhejiang_2024_first_major_rank_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    province_name = str(case.metadata.get("province_name") or "")
    batch = str(case.metadata.get("batch") or "")
    grain = str(case.metadata.get("opportunity_grain") or "")
    return (
        case.target_year == 2024
        and grain == "major"
        and (province_id == "33" or province_name == "\u6d59\u6c5f")
        and "\u4e00\u6bb5" in batch
    )


def _zhejiang_2025_first_major_rank_segment(case: PredictionCase) -> bool:
    return _zhejiang_2025_first_major_score_segment(case)


def _guangdong_2024_school_undergraduate_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    province_name = str(case.metadata.get("province_name") or "")
    batch = str(case.metadata.get("batch") or "")
    grain = str(case.metadata.get("opportunity_grain") or "")
    return (
        case.target_year == 2024
        and grain == "school"
        and (province_id == "44" or province_name == "\u5e7f\u4e1c")
        and batch == "\u672c\u79d1\u6279"
    )


def _guangdong_school_vocational_score_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    province_name = str(case.metadata.get("province_name") or "")
    batch = str(case.metadata.get("batch") or "")
    grain = str(case.metadata.get("opportunity_grain") or "")
    return (
        case.target_year >= 2023
        and grain == "school"
        and (province_id == "44" or province_name == "\u5e7f\u4e1c")
        and "\u4e13\u79d1" in batch
    )


def _guangdong_2022_school_vocational_score_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    province_name = str(case.metadata.get("province_name") or "")
    batch = str(case.metadata.get("batch") or "")
    grain = str(case.metadata.get("opportunity_grain") or "")
    return (
        case.target_year == 2022
        and grain == "school"
        and (province_id == "44" or province_name == "\u5e7f\u4e1c")
        and "\u4e13\u79d1" in batch
    )


def _guangdong_school_vocational_rank_offset_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    province_name = str(case.metadata.get("province_name") or "")
    batch = str(case.metadata.get("batch") or "")
    grain = str(case.metadata.get("opportunity_grain") or "")
    return (
        case.target_year in {2022, 2023, 2024}
        and grain == "school"
        and (province_id == "44" or province_name == "\u5e7f\u4e1c")
        and "\u4e13\u79d1" in batch
    )


def _zhejiang_2025_first_major_score_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    province_name = str(case.metadata.get("province_name") or "")
    batch = str(case.metadata.get("batch") or "")
    grain = str(case.metadata.get("opportunity_grain") or "")
    return (
        case.target_year == 2025
        and grain == "major"
        and (province_id == "33" or province_name == "\u6d59\u6c5f")
        and "\u4e00\u6bb5" in batch
    )


def _last_year_segment(case: PredictionCase, rows: list[AdmissionHistory]) -> bool:
    batch = str(case.metadata.get("batch") or "").strip().upper()
    province_name = str(case.metadata.get("province_name") or "")
    return rows[0].year <= 2022 or not batch or batch == "UNKNOWN" or province_name == "\u5e7f\u4e1c"


def _historical_mean_segment(case: PredictionCase) -> bool:
    province_name = str(case.metadata.get("province_name") or "")
    batch = str(case.metadata.get("batch") or "")
    return case.target_year >= 2025 or province_name == "\u6d59\u6c5f" or "\u4e8c\u6bb5" in batch


def _segmented_score(case: PredictionCase, rows: list[AdmissionHistory], ensemble_score: float | None) -> float | None:
    if ensemble_score is None:
        return None
    if _zhejiang_2024_score_segment(case):
        return ensemble_score
    if _guangdong_2022_score_segment(case):
        recent_score = _mean_score(rows[:3])
        return round(recent_score, 2) if recent_score is not None else ensemble_score
    if not _recent_score_segment_allowed(case):
        return ensemble_score
    recent_scores = [float(item.cutoff_score) for item in rows[:2] if item.cutoff_score is not None]
    if not recent_scores:
        return ensemble_score
    recent_mean = mean(recent_scores)
    if _structured_score_fallback_allowed(case) and float(ensemble_score) - recent_mean > 3.0:
        return ensemble_score
    if abs(float(ensemble_score) - recent_mean) <= 8.0:
        return round(recent_mean, 2)
    return ensemble_score


def _structured_score_fallback_allowed(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    batch = str(case.metadata.get("batch") or "")
    points = case.metadata.get("target_score_rank_points")
    return province_id in STRUCTURED_SCORE_FALLBACK_PROVINCES and bool(batch.strip()) and isinstance(points, list) and bool(points)


def _guangdong_2022_score_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    return province_id == "44" and case.target_year == 2022


def _zhejiang_2024_score_segment(case: PredictionCase) -> bool:
    province_id = str(case.metadata.get("province_id") or "")
    return province_id == "33" and case.target_year == 2024


def _recent_score_segment_allowed(case: PredictionCase) -> bool:
    batch = str(case.metadata.get("batch") or "")
    province_name = str(case.metadata.get("province_name") or "")
    if case.target_year <= 2023:
        return False
    if province_name == "浙江" and "二段" in batch:
        return False
    return True


def _batch_directional_offset(metadata: dict[str, object]) -> float:
    batch = str(metadata.get("batch") or "")
    if "\u4e13\u79d1\u6279" in batch:
        return -4000.0
    if "\u4e8c\u6bb5" in batch:
        return 2500.0
    return 0.0


def _mean_score(history: list[AdmissionHistory]) -> float | None:
    scores = [float(item.cutoff_score) for item in history if item.cutoff_score is not None]
    if not scores:
        return None
    return mean(scores)


def _calibrated_score(history: list[AdmissionHistory]) -> float | None:
    scores = [float(item.cutoff_score) for item in history if item.cutoff_score is not None]
    if not scores:
        return None
    recent_scores = [float(item.cutoff_score) for item in history[:3] if item.cutoff_score is not None]
    recent_mean = mean(recent_scores) if recent_scores else mean(scores)
    return 0.65 * mean(scores) + 0.35 * recent_mean + 3.0


def _score_rank_points_allowed(metadata: dict[str, object]) -> bool:
    province_id = str(metadata.get("province_id") or "")
    province_name = str(metadata.get("province_name") or "")
    batch = str(metadata.get("batch") or "")
    is_shaanxi = province_id == "61" or province_name == "\u9655\u897f"
    return is_shaanxi and "\u4e13\u79d1" in batch


def _score_rank_residual_adjustment(metadata: dict[str, object]) -> float:
    if _score_rank_points_allowed(metadata):
        return 14.0
    return 0.0


def _score_from_rank_points(points: object, predicted_rank: float) -> float | None:
    if not isinstance(points, list) or not points:
        return None
    parsed = []
    for item in points:
        if not isinstance(item, dict) or item.get("lowest_rank") is None or item.get("score") is None:
            continue
        parsed.append((int(float(item["lowest_rank"])), float(item["score"])))
    if not parsed:
        return None
    parsed.sort(key=lambda item: item[0])
    rank = max(1, round(predicted_rank))
    for lowest_rank, score in parsed:
        if lowest_rank >= rank:
            return score
    return parsed[-1][1]


BASELINES: dict[str, BaselineFn] = {
    "last_year_rank": _last_year,
    "two_year_mean_rank": lambda case: _recent_mean(case, "two_year_mean_rank", 2),
    "three_year_mean_rank": lambda case: _recent_mean(case, "three_year_mean_rank", 3),
    "historical_mean_rank": _historical_mean,
    "historical_median_rank": _historical_median,
    "weighted_recent_rank": _weighted_recent,
    "exponential_smoothing_rank": _exponential_smoothing,
    "linear_trend_rank": _linear_trend,
    "volatility_conservative_rank": _volatility_conservative,
    "plan_adjusted_mean_rank": _plan_adjusted_mean,
    "best_recent_rank": _best_recent,
    "worst_recent_rank": _worst_recent,
    "volunteer_matching_rank_ensemble": _ensemble,
    "volunteer_matching_segmented_rank_ensemble": _segmented_ensemble,
    "volunteer_matching_meta_router": _meta_router,
}
