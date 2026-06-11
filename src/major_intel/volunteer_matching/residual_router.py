"""Non-leaky residual routing for batch volunteer matching benchmarks."""

from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any

from .baselines import predict_with_baseline
from .models import AdmissionHistory, PredictionCase


RESIDUAL_ROUTER_METHOD = "volunteer_matching_residual_router"
DEFAULT_BASE_METHOD = "volunteer_matching_meta_router"
DEFAULT_MIN_EXAMPLES = 12
DEFAULT_SHRINKAGE = 0.35
SEGMENT_KEY_LEVELS: tuple[tuple[str, ...], ...] = (
    ("province_id", "batch", "opportunity_grain", "subject_type"),
    ("province_id", "batch", "opportunity_grain"),
    ("province_id", "batch"),
    ("province_id", "opportunity_grain"),
    ("batch", "opportunity_grain"),
    ("province_id",),
    ("batch",),
    ("opportunity_grain",),
    tuple(),
)


def predict_residual_router(
    cases: list[PredictionCase],
    *,
    base_method: str = DEFAULT_BASE_METHOD,
    min_examples: int = DEFAULT_MIN_EXAMPLES,
    shrinkage: float = DEFAULT_SHRINKAGE,
) -> list[dict[str, Any]]:
    """Predict with a base method plus median residuals learned from prior years.

    Training examples are pseudo-backtests: each historical year Y is predicted
    only from rows earlier than Y. Target-year outcomes are never used to build
    residual tables for that target-year prediction.
    """
    tables = _build_residual_tables(cases, base_method=base_method)
    rows: list[dict[str, Any]] = []
    for case in cases:
        try:
            base = predict_with_baseline(base_method, case)
        except Exception:  # noqa: BLE001 - benchmark methods should skip invalid cases.
            continue
        residual = _select_residual(case, tables, min_examples=min_examples)
        rank_adjustment = _shrunk(residual["rank_residual"], shrinkage) if residual else 0.0
        score_adjustment = _shrunk(residual["score_residual"], shrinkage) if residual else None
        predicted_score = base.predicted_score
        if predicted_score is not None and score_adjustment is not None:
            predicted_score = round(float(predicted_score) + score_adjustment, 2)
        warnings = list(base.warnings)
        if residual:
            warnings.extend(
                [
                    f"residual_router_key={residual['key_name']}",
                    f"residual_examples={residual['count']}",
                    f"rank_residual={round(rank_adjustment, 4)}",
                ]
            )
            if score_adjustment is not None:
                warnings.append(f"score_residual={round(score_adjustment, 4)}")
        else:
            warnings.append("residual_router_key=none")
        rows.append(
            {
                "method": RESIDUAL_ROUTER_METHOD,
                "opportunity_key": case.opportunity_key,
                "target_year": case.target_year,
                "actual_rank": case.actual_rank,
                "actual_score": case.actual_score,
                "predicted_rank": max(1, round(float(base.predicted_rank) + rank_adjustment)),
                "planning_rank": base.planning_rank,
                "predicted_score": predicted_score,
                "confidence": base.confidence,
                "evidence_years": base.evidence_years,
                "warnings": warnings,
                "province_id": case.metadata.get("province_id"),
                "province_name": case.metadata.get("province_name"),
                "subject_type": case.metadata.get("subject_type"),
                "batch": case.metadata.get("batch"),
                "opportunity_grain": case.metadata.get("opportunity_grain"),
            }
        )
    return rows


def _build_residual_tables(
    cases: list[PredictionCase],
    *,
    base_method: str,
) -> dict[tuple[str, tuple[Any, ...]], dict[str, list[float]]]:
    tables: dict[tuple[str, tuple[Any, ...]], dict[str, list[float]]] = defaultdict(
        lambda: {"rank": [], "score": []}
    )
    for case in cases:
        history = sorted([row for row in case.history if row.cutoff_rank > 0], key=lambda row: row.year)
        for actual in history:
            if actual.year >= case.target_year:
                continue
            prior = [row for row in history if row.year < actual.year]
            if not prior:
                continue
            pseudo = PredictionCase(
                opportunity_key=case.opportunity_key,
                target_year=actual.year,
                actual_rank=actual.cutoff_rank,
                actual_score=actual.cutoff_score,
                history=prior,
                metadata=case.metadata,
            )
            try:
                prediction = predict_with_baseline(base_method, pseudo)
            except Exception:  # noqa: BLE001 - one invalid pseudo sample should not discard the batch.
                continue
            rank_residual = float(actual.cutoff_rank) - float(prediction.predicted_rank)
            score_residual = None
            if actual.cutoff_score is not None and prediction.predicted_score is not None:
                score_residual = float(actual.cutoff_score) - float(prediction.predicted_score)
            for fields in SEGMENT_KEY_LEVELS:
                segment_key = _key(case.metadata, fields)
                if segment_key is None:
                    continue
                table = tables[(_key_name(fields), segment_key)]
                table["rank"].append(rank_residual)
                if score_residual is not None:
                    table["score"].append(score_residual)
    return tables


def _select_residual(
    case: PredictionCase,
    tables: dict[tuple[str, tuple[Any, ...]], dict[str, list[float]]],
    *,
    min_examples: int,
) -> dict[str, Any] | None:
    for fields in SEGMENT_KEY_LEVELS:
        key_name = _key_name(fields)
        segment_key = _key(case.metadata, fields)
        if segment_key is None:
            continue
        table = tables.get((key_name, segment_key))
        if not table or len(table["rank"]) < min_examples:
            continue
        score_values = table["score"]
        return {
            "key_name": key_name,
            "count": len(table["rank"]),
            "rank_residual": float(median(table["rank"])),
            "score_residual": float(median(score_values)) if score_values else None,
        }
    return None


def _key(metadata: dict[str, Any], fields: tuple[str, ...]) -> tuple[Any, ...] | None:
    values = tuple(metadata.get(field) for field in fields)
    if any(value in (None, "") for value in values):
        return None
    return values


def _key_name(fields: tuple[str, ...]) -> str:
    return "|".join(fields) if fields else "global"


def _shrunk(value: float | None, shrinkage: float) -> float | None:
    if value is None:
        return None
    return float(value) * max(0.0, min(1.0, float(shrinkage)))
