"""Batch-trained scikit-learn baselines for volunteer matching benchmarks."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from statistics import mean, median, pstdev
from typing import Any

from .models import AdmissionHistory, PredictionCase


@dataclass(frozen=True)
class TrainingExample:
    features: list[float]
    rank_label: float
    score_label: float | None


@dataclass(frozen=True)
class TargetExample:
    case: PredictionCase
    features: list[float]
    evidence_years: list[int]


def ml_baseline_names() -> list[str]:
    return list(ML_BASELINES.keys())


def predict_ml_baselines(
    cases: list[PredictionCase],
    methods: list[str] | None = None,
) -> list[dict[str, Any]]:
    selected_methods = methods or ml_baseline_names()
    training, targets = build_ml_examples(cases)
    if not training or not targets:
        return []

    rows: list[dict[str, Any]] = []
    for method in selected_methods:
        rank_predictions, score_predictions = _predict_one_method(method, training, targets)
        for target, rank_prediction, score_prediction in zip(targets, rank_predictions, score_predictions):
            rows.append(
                {
                    "method": method,
                    "opportunity_key": target.case.opportunity_key,
                    "target_year": target.case.target_year,
                    "actual_rank": target.case.actual_rank,
                    "actual_score": target.case.actual_score,
                    "predicted_rank": max(1, round(float(rank_prediction))),
                    "planning_rank": None,
                    "predicted_score": round(float(score_prediction), 2) if score_prediction is not None else None,
                    "confidence": min(1.0, 0.35 + 0.05 * len(target.evidence_years)),
                    "evidence_years": target.evidence_years,
                    "warnings": [],
                    "province_id": target.case.metadata.get("province_id"),
                    "province_name": target.case.metadata.get("province_name"),
                    "subject_type": target.case.metadata.get("subject_type"),
                    "batch": target.case.metadata.get("batch"),
                    "opportunity_grain": target.case.metadata.get("opportunity_grain"),
                }
            )
    return rows


def build_ml_examples(cases: list[PredictionCase]) -> tuple[list[TrainingExample], list[TargetExample]]:
    training: list[TrainingExample] = []
    targets: list[TargetExample] = []
    for case in cases:
        history = sorted([row for row in case.history if row.cutoff_rank > 0], key=lambda row: row.year)
        for actual in history:
            if actual.year >= case.target_year:
                continue
            prior = [row for row in history if row.year < actual.year]
            if not prior:
                continue
            training.append(
                TrainingExample(
                    features=_features(prior, actual.year, case.metadata),
                    rank_label=float(actual.cutoff_rank),
                    score_label=float(actual.cutoff_score) if actual.cutoff_score is not None else None,
                )
            )

        prediction_prior = [row for row in history if row.year < case.target_year]
        if prediction_prior:
            targets.append(
                TargetExample(
                    case=case,
                    features=_features(prediction_prior, case.target_year, case.metadata),
                    evidence_years=[row.year for row in sorted(prediction_prior, key=lambda row: row.year, reverse=True)],
                )
            )
    return training, targets


def _predict_one_method(
    method: str,
    training: list[TrainingExample],
    targets: list[TargetExample],
) -> tuple[list[float], list[float | None]]:
    try:
        factory = ML_BASELINES[method]
    except KeyError as exc:
        raise KeyError(f"unknown ML baseline: {method}") from exc

    rank_model = factory()
    x_train = [row.features for row in training]
    y_rank = [row.rank_label for row in training]
    x_target = [row.features for row in targets]
    rank_model.fit(x_train, y_rank)
    rank_predictions = [float(value) for value in rank_model.predict(x_target)]

    score_training = [row for row in training if row.score_label is not None]
    if not score_training:
        return rank_predictions, [None for _ in targets]
    score_model = factory()
    score_model.fit([row.features for row in score_training], [float(row.score_label) for row in score_training])
    score_predictions = [float(value) for value in score_model.predict(x_target)]
    return rank_predictions, score_predictions


def _features(history: list[AdmissionHistory], target_year: int, metadata: dict[str, Any] | None = None) -> list[float]:
    rows = sorted(history, key=lambda row: row.year)
    ranks = [float(row.cutoff_rank) for row in rows]
    scores = [float(row.cutoff_score) for row in rows if row.cutoff_score is not None]
    plans = [float(row.plan_count) for row in rows if row.plan_count and row.plan_count > 0]
    latest = rows[-1]
    previous = rows[-2] if len(rows) >= 2 else rows[-1]

    return [
        float(target_year),
        float(len(rows)),
        float(target_year - latest.year),
        float(latest.cutoff_rank),
        float(previous.cutoff_rank),
        mean(ranks),
        median(ranks),
        min(ranks),
        max(ranks),
        pstdev(ranks) if len(ranks) > 1 else 0.0,
        float(latest.cutoff_rank - previous.cutoff_rank),
        _slope(rows, "rank"),
        float(latest.cutoff_score) if latest.cutoff_score is not None else _nan(),
        mean(scores) if scores else _nan(),
        median(scores) if scores else _nan(),
        float(latest.plan_count) if latest.plan_count else 0.0,
        mean(plans) if plans else 0.0,
        float(latest.plan_count - previous.plan_count)
        if latest.plan_count is not None and previous.plan_count is not None
        else 0.0,
        1.0 if latest.plan_count is not None else 0.0,
        float(len(plans)) / float(len(rows)),
    ] + _metadata_features(metadata)


def _metadata_features(metadata: dict[str, Any] | None) -> list[float]:
    metadata = metadata or {}
    province_id = str(metadata.get("province_id") or "")
    subject_type = str(metadata.get("subject_type") or "")
    batch = str(metadata.get("batch") or "")
    grain = str(metadata.get("opportunity_grain") or "")
    return [
        _stable_bucket(province_id, 100),
        _stable_bucket(subject_type, 100),
        _stable_bucket(batch, 200),
        _stable_bucket(grain, 10),
        1.0 if grain == "school" else 0.0,
        1.0 if grain == "major" else 0.0,
        1.0 if province_id == "44" else 0.0,
        1.0 if province_id == "33" else 0.0,
        1.0 if subject_type == "physics" else 0.0,
        1.0 if subject_type == "history" else 0.0,
        1.0 if subject_type == "comprehensive" else 0.0,
        1.0 if "\u672c\u79d1" in batch else 0.0,
        1.0 if "\u4e13\u79d1" in batch else 0.0,
        1.0 if "\u4e00\u6bb5" in batch else 0.0,
        1.0 if "\u4e8c\u6bb5" in batch else 0.0,
    ]


def _stable_bucket(value: str, modulo: int) -> float:
    if not value:
        return 0.0
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return float(int(digest[:8], 16) % modulo) / float(modulo)


def _slope(rows: list[AdmissionHistory], value_type: str) -> float:
    if len(rows) < 2:
        return 0.0
    xs = [float(row.year) for row in rows]
    if value_type == "rank":
        ys = [float(row.cutoff_rank) for row in rows]
    else:
        ys = [float(row.cutoff_score or 0.0) for row in rows]
    x_bar = mean(xs)
    y_bar = mean(ys)
    denominator = sum((x - x_bar) ** 2 for x in xs)
    if denominator == 0:
        return 0.0
    return sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denominator


def _nan() -> float:
    return float("nan")


def _pipeline(model: Any, *, scale: bool) -> Any:
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if scale:
        return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), model)
    return make_pipeline(SimpleImputer(strategy="median"), model)


def _ridge() -> Any:
    from sklearn.linear_model import Ridge

    return _pipeline(Ridge(alpha=1.0), scale=True)


def _elastic_net() -> Any:
    from sklearn.linear_model import ElasticNet

    return _pipeline(ElasticNet(alpha=0.01, l1_ratio=0.2, max_iter=5000), scale=True)


def _lasso() -> Any:
    from sklearn.linear_model import Lasso

    return _pipeline(Lasso(alpha=0.01, max_iter=5000), scale=True)


def _huber() -> Any:
    from sklearn.linear_model import HuberRegressor

    return _pipeline(HuberRegressor(max_iter=500), scale=True)


def _knn() -> Any:
    from sklearn.neighbors import KNeighborsRegressor

    return _pipeline(KNeighborsRegressor(n_neighbors=5, weights="distance"), scale=True)


def _svr() -> Any:
    from sklearn.svm import SVR

    return _pipeline(SVR(C=10.0, epsilon=0.1, gamma="scale"), scale=True)


def _random_forest() -> Any:
    from sklearn.ensemble import RandomForestRegressor

    return _pipeline(RandomForestRegressor(n_estimators=80, min_samples_leaf=2, random_state=42, n_jobs=-1), scale=False)


def _extra_trees() -> Any:
    from sklearn.ensemble import ExtraTreesRegressor

    return _pipeline(ExtraTreesRegressor(n_estimators=80, min_samples_leaf=2, random_state=42, n_jobs=-1), scale=False)


def _gradient_boosting() -> Any:
    from sklearn.ensemble import GradientBoostingRegressor

    return _pipeline(GradientBoostingRegressor(random_state=42, n_estimators=120, learning_rate=0.05, max_depth=3), scale=False)


def _hist_gradient_boosting() -> Any:
    from sklearn.ensemble import HistGradientBoostingRegressor

    return _pipeline(HistGradientBoostingRegressor(random_state=42, max_iter=120, learning_rate=0.05), scale=False)


def _ada_boost() -> Any:
    from sklearn.ensemble import AdaBoostRegressor

    return _pipeline(AdaBoostRegressor(random_state=42, n_estimators=120, learning_rate=0.05), scale=False)


def _bagging() -> Any:
    from sklearn.ensemble import BaggingRegressor
    from sklearn.tree import DecisionTreeRegressor

    return _pipeline(
        BaggingRegressor(
            estimator=DecisionTreeRegressor(min_samples_leaf=2, random_state=42),
            n_estimators=80,
            random_state=42,
            n_jobs=-1,
        ),
        scale=False,
    )


def _mlp() -> Any:
    from sklearn.neural_network import MLPRegressor

    return _pipeline(MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42), scale=True)


def _xgboost() -> Any:
    from xgboost import XGBRegressor

    return _pipeline(
        XGBRegressor(
            objective="reg:squarederror",
            n_estimators=160,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=-1,
            verbosity=0,
        ),
        scale=False,
    )


def _lightgbm() -> Any:
    from lightgbm import LGBMRegressor

    return _pipeline(
        LGBMRegressor(
            n_estimators=160,
            learning_rate=0.05,
            num_leaves=31,
            min_child_samples=10,
            random_state=42,
            n_jobs=-1,
            verbose=-1,
        ),
        scale=False,
    )


def _catboost() -> Any:
    from catboost import CatBoostRegressor

    return _pipeline(
        CatBoostRegressor(
            iterations=160,
            depth=4,
            learning_rate=0.05,
            loss_function="RMSE",
            random_seed=42,
            verbose=False,
            allow_writing_files=False,
        ),
        scale=False,
    )


def _tabicl() -> Any:
    from tabicl import TabICLRegressor

    return _pipeline(
        TabICLRegressor(
            n_estimators=1,
            batch_size=8,
            device="cpu",
            random_state=42,
            verbose=False,
        ),
        scale=True,
    )


ML_BASELINES: dict[str, Callable[[], Any]] = {
    "sklearn_ridge": _ridge,
    "sklearn_elastic_net": _elastic_net,
    "sklearn_lasso": _lasso,
    "sklearn_huber": _huber,
    "sklearn_knn": _knn,
    "sklearn_svr": _svr,
    "sklearn_random_forest": _random_forest,
    "sklearn_extra_trees": _extra_trees,
    "sklearn_gradient_boosting": _gradient_boosting,
    "sklearn_hist_gradient_boosting": _hist_gradient_boosting,
    "sklearn_ada_boost": _ada_boost,
    "sklearn_bagging_tree": _bagging,
    "sklearn_mlp": _mlp,
    "xgboost_regressor": _xgboost,
    "lightgbm_regressor": _lightgbm,
    "catboost_regressor": _catboost,
    "tabicl_regressor": _tabicl,
}
