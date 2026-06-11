"""Build tables and figures for the volunteer matching LaTeX paper."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from major_intel.volunteer_matching.route_search import (  # noqa: E402
    DEFAULT_PREDICTION_EXPERT_ROUTE_SPECS,
)


PRIMARY = "volunteer_matching_prediction_expert_router"
META = "volunteer_matching_meta_router"

REPORT_DIR = ROOT / "reports" / "volunteer_matching" / "paper_v50"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"
DATA_DIR = REPORT_DIR / "data"

MAIN_JSON = (
    ROOT
    / "reports"
    / "volunteer_matching"
    / "benchmark_20260610_stratified_2022_2025_limit100_route_specs_v50.json"
)
BOUNDARY_JSON = (
    ROOT
    / "reports"
    / "volunteer_matching"
    / "benchmark_20260610_stratified_2021_2025_limit50_route_specs_v50.json"
)

VALIDATION_SETS = [
    ("Main", "2022-2025 stratified limit100", MAIN_JSON),
    ("Boundary", "2021-2025 stratified limit50", BOUNDARY_JSON),
]

CORE_PREDICTION_METRICS = {
    "mae_rank": "asc",
    "median_ae_rank": "asc",
    "p90_ae_rank": "asc",
    "rmse_rank": "asc",
    "mae_score": "asc",
    "median_ae_score": "asc",
    "p90_ae_score": "asc",
    "rmse_score": "asc",
    "within_3_score_points": "desc",
    "within_5_score_points": "desc",
    "within_10_score_points": "desc",
}

METRIC_LABELS = {
    "mae_rank": "MAE rank",
    "median_ae_rank": "Median AE rank",
    "p90_ae_rank": "P90 AE rank",
    "rmse_rank": "RMSE rank",
    "mae_score": "MAE score",
    "median_ae_score": "Median AE score",
    "p90_ae_score": "P90 AE score",
    "rmse_score": "RMSE score",
    "within_3_score_points": "Hit <=3",
    "within_5_score_points": "Hit <=5",
    "within_10_score_points": "Hit <=10",
    "admissible_rate": "Admissible rate",
    "ndcg": "NDCG",
    "expected_utility": "Expected utility",
    "safety_gated_regret": "Safety-gated regret",
}

METHOD_LABELS = {
    PRIMARY: "Expert router",
    META: "Meta router",
    "volunteer_matching_rank_ensemble": "Rank ensemble",
    "volunteer_matching_segmented_rank_ensemble": "Segmented ensemble",
    "last_year_rank": "Last year",
    "two_year_mean_rank": "Two-year mean",
    "three_year_mean_rank": "Three-year mean",
    "historical_mean_rank": "Historical mean",
    "historical_median_rank": "Historical median",
    "weighted_recent_rank": "Weighted recent",
    "exponential_smoothing_rank": "Exp. smoothing",
    "linear_trend_rank": "Linear trend",
    "volatility_conservative_rank": "Volatility conservative",
    "plan_adjusted_mean_rank": "Plan adjusted",
    "best_recent_rank": "Best recent",
    "worst_recent_rank": "Worst recent",
    "sklearn_ridge": "Ridge",
    "sklearn_lasso": "Lasso",
    "sklearn_elastic_net": "Elastic Net",
    "sklearn_huber": "Huber",
    "sklearn_random_forest": "Random forest",
    "sklearn_extra_trees": "Extra Trees",
    "sklearn_gradient_boosting": "Gradient boosting",
    "sklearn_hist_gradient_boosting": "Hist. gradient boost",
    "sklearn_ada_boost": "AdaBoost",
    "sklearn_bagging_tree": "Bagging tree",
    "lightgbm_regressor": "LightGBM",
    "xgboost_regressor": "XGBoost",
    "catboost_regressor": "CatBoost",
    "sklearn_knn": "KNN",
    "sklearn_svr": "SVR",
    "sklearn_mlp": "MLP",
    "tabicl_regressor": "TabICL",
}

PROVINCE_LABELS = {"33": "Zhejiang", "44": "Guangdong", "61": "Shaanxi"}
BATCH_LABELS = {
    "本科批": "Undergraduate",
    "专科批": "Junior college",
    "高职专科批": "Vocational",
    "一段": "First segment",
    "二段": "Second segment",
}
DIMENSION_LABELS = {
    "batch": "Batch",
    "opportunity_grain": "Grain",
    "province_id": "Province",
    "province_id|opportunity_grain": "Province x grain",
    "province_name": "Province name",
    "subject_type": "Subject",
    "target_year": "Year",
    "target_year|opportunity_grain": "Year x grain",
    "target_year|province_id": "Year x province",
    "target_year|province_id|batch": "Year x province x batch",
    "target_year|province_id|batch|opportunity_grain": "Year x province x batch x grain",
    "target_year|subject_type": "Year x subject",
}


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "figure.dpi": 140,
            "savefig.dpi": 220,
        }
    )

    payloads = load_payloads()
    metrics_df = build_metrics_frame(payloads)
    plan_df = build_plan_frame(payloads)
    predictions_df = build_predictions_frame(payloads)
    summary_df = build_overall_summary(metrics_df)
    categories_df = build_category_frame(metrics_df)
    routes_df = build_routes_frame()
    evolution_df = build_evolution_frame()
    slice_df = build_slice_frame(payloads)
    dataset_df = build_dataset_frame(predictions_df)

    write_tables(
        metrics_df,
        plan_df,
        predictions_df,
        summary_df,
        categories_df,
        routes_df,
        evolution_df,
        slice_df,
        dataset_df,
        payloads,
    )
    build_figures(
        metrics_df,
        plan_df,
        predictions_df,
        categories_df,
        evolution_df,
        slice_df,
        dataset_df,
    )
    write_summary_json(payloads, metrics_df, plan_df, summary_df, evolution_df)

    print(f"Wrote paper assets to {REPORT_DIR}")


def load_payloads() -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for short_name, label, path in VALIDATION_SETS:
        payloads[short_name] = {
            "label": label,
            "path": str(path.relative_to(ROOT)),
            "data": json.loads(path.read_text(encoding="utf-8"))["combined"],
        }
    return payloads


def build_metrics_frame(payloads: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for set_name, payload in payloads.items():
        data = payload["data"]
        for method, metrics in data["metrics"].items():
            row = {
                "validation_set": set_name,
                "validation_label": payload["label"],
                "method": method,
                "method_label": label_method(method),
                "category": categorize_method(method),
                "case_count": data["case_count"],
                "method_count": data["method_count"],
                "errors": len(data.get("errors") or []),
            }
            row.update(metrics)
            rows.append(row)
    return pd.DataFrame(rows)


def build_plan_frame(payloads: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for set_name, payload in payloads.items():
        for method, metrics in payload["data"]["plan_metrics"].items():
            row = {
                "validation_set": set_name,
                "validation_label": payload["label"],
                "method": method,
                "method_label": label_method(method),
                "category": categorize_method(method),
            }
            row.update(metrics)
            rows.append(row)
    return pd.DataFrame(rows)


def build_predictions_frame(payloads: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for set_name, payload in payloads.items():
        for row in payload["data"]["predictions"]:
            copied = dict(row)
            copied["validation_set"] = set_name
            copied["validation_label"] = payload["label"]
            copied["method_label"] = label_method(str(row["method"]))
            copied["category"] = categorize_method(str(row["method"]))
            if copied.get("predicted_rank") is not None and copied.get("actual_rank") is not None:
                copied["ae_rank"] = abs(int(copied["predicted_rank"]) - int(copied["actual_rank"]))
                copied["log10_ae_rank_plus1"] = np.log10(copied["ae_rank"] + 1)
            if copied.get("predicted_score") is not None and copied.get("actual_score") is not None:
                copied["ae_score"] = abs(float(copied["predicted_score"]) - float(copied["actual_score"]))
            rows.append(copied)
    return pd.DataFrame(rows)


def build_overall_summary(metrics_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    comparable = metrics_df[(metrics_df["coverage_rate"].fillna(0) >= 0.95)]
    for set_name in ["Main", "Boundary"]:
        set_df = comparable[comparable["validation_set"] == set_name]
        primary = set_df[set_df["method"] == PRIMARY].iloc[0]
        for metric, direction in CORE_PREDICTION_METRICS.items():
            baselines = set_df[set_df["method"] != PRIMARY].dropna(subset=[metric])
            if direction == "asc":
                best = baselines.sort_values(metric, ascending=True).iloc[0]
                rel = (float(best[metric]) - float(primary[metric])) / max(abs(float(best[metric])), 1e-9)
            else:
                best = baselines.sort_values(metric, ascending=False).iloc[0]
                rel = (float(primary[metric]) - float(best[metric])) / max(abs(float(best[metric])), 1e-9)
            rows.append(
                {
                    "validation_set": set_name,
                    "metric": metric,
                    "metric_label": METRIC_LABELS[metric],
                    "direction": "lower is better" if direction == "asc" else "higher is better",
                    "primary_value": primary[metric],
                    "best_baseline": best["method"],
                    "best_baseline_label": best["method_label"],
                    "best_baseline_value": best[metric],
                    "relative_improvement": rel,
                    "primary_rank_among_coverage_methods": rank_method(set_df, metric, direction, PRIMARY),
                }
            )
    return pd.DataFrame(rows)


def build_category_frame(metrics_df: pd.DataFrame) -> pd.DataFrame:
    method_rows = metrics_df[metrics_df["validation_set"] == "Main"][
        ["method", "method_label", "category"]
    ].drop_duplicates()
    grouped = (
        method_rows.groupby("category")
        .agg(method_count=("method", "count"), methods=("method_label", lambda x: "; ".join(sorted(x))))
        .reset_index()
        .sort_values(["method_count", "category"], ascending=[False, True])
    )
    return grouped


def build_routes_frame() -> pd.DataFrame:
    rows = []
    for spec in DEFAULT_PREDICTION_EXPERT_ROUTE_SPECS:
        item = asdict(spec)
        item["filter_text"] = filters_to_text(item["filters"], item["contains"])
        item["rank_method_label"] = label_method(item["rank_method"]) if item["rank_method"] else ""
        item["score_method_label"] = label_method(item["score_method"]) if item["score_method"] else ""
        rows.append(item)
    return pd.DataFrame(rows)


def build_evolution_frame() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    patterns = [
        ("Main", "2022_2025_limit100"),
        ("Boundary", "2021_2025_limit50"),
    ]
    for set_name, fragment in patterns:
        for path in sorted((ROOT / "reports" / "volunteer_matching").glob(f"benchmark_20260610_stratified_{fragment}_route_specs_v*.json")):
            match = re.search(r"_v(\d+)\.json$", path.name)
            if not match:
                continue
            version = int(match.group(1))
            if version < 37 or version > 50:
                continue
            data = json.loads(path.read_text(encoding="utf-8"))["combined"]
            if PRIMARY not in data["metrics"]:
                continue
            metric = data["metrics"][PRIMARY]
            gate = data.get("acceptance_gates", {}).get("slice_leadership", {})
            rows.append(
                {
                    "validation_set": set_name,
                    "version": version,
                    "mae_rank": metric.get("mae_rank"),
                    "mae_score": metric.get("mae_score"),
                    "within_10_score_points": metric.get("within_10_score_points"),
                    "slice_failures": gate.get("failure_count") or gate.get("failed_metric_count"),
                    "case_count": data.get("case_count"),
                    "method_count": data.get("method_count"),
                }
            )
    return pd.DataFrame(rows).sort_values(["validation_set", "version"])


def build_slice_frame(payloads: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for set_name, payload in payloads.items():
        audit = payload["data"]["slice_leadership_audit"]
        for dimension, groups in audit.items():
            for group_name, group_result in groups.items():
                failure_count = int(group_result.get("failure_count") or 0)
                rows.append(
                    {
                        "validation_set": set_name,
                        "dimension": dimension,
                        "dimension_label": DIMENSION_LABELS.get(dimension, dimension),
                        "group": group_name,
                        "failure_count": failure_count,
                        "primary_rows": group_result.get("primary_rows"),
                    }
                )
    return pd.DataFrame(rows)


def build_dataset_frame(predictions_df: pd.DataFrame) -> pd.DataFrame:
    primary = predictions_df[predictions_df["method"] == PRIMARY].copy()
    primary["province_label"] = primary["province_id"].astype(str).map(PROVINCE_LABELS).fillna(primary["province_id"].astype(str))
    primary["batch_label"] = primary["batch"].map(BATCH_LABELS).fillna(primary["batch"])
    group_cols = [
        "validation_set",
        "target_year",
        "province_id",
        "province_label",
        "batch",
        "batch_label",
        "subject_type",
        "opportunity_grain",
    ]
    return primary.groupby(group_cols).size().reset_index(name="case_count")


def write_tables(
    metrics_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    categories_df: pd.DataFrame,
    routes_df: pd.DataFrame,
    evolution_df: pd.DataFrame,
    slice_df: pd.DataFrame,
    dataset_df: pd.DataFrame,
    payloads: dict[str, dict[str, Any]],
) -> None:
    metrics_df.to_csv(TABLE_DIR / "all_prediction_metrics.csv", index=False, encoding="utf-8-sig")
    plan_df.to_csv(TABLE_DIR / "all_planning_metrics.csv", index=False, encoding="utf-8-sig")
    summary_df.to_csv(TABLE_DIR / "overall_prediction_summary.csv", index=False, encoding="utf-8-sig")
    categories_df.to_csv(TABLE_DIR / "baseline_categories.csv", index=False, encoding="utf-8-sig")
    routes_df.to_csv(TABLE_DIR / "expert_route_specs.csv", index=False, encoding="utf-8-sig")
    evolution_df.to_csv(TABLE_DIR / "route_evolution_v37_v50.csv", index=False, encoding="utf-8-sig")
    slice_df.to_csv(TABLE_DIR / "slice_failures.csv", index=False, encoding="utf-8-sig")
    dataset_df.to_csv(TABLE_DIR / "dataset_distribution.csv", index=False, encoding="utf-8-sig")

    dataset_overview = []
    for set_name, payload in payloads.items():
        data = payload["data"]
        gates = data["acceptance_gates"]
        dataset_overview.append(
            {
                "validation_set": set_name,
                "label": payload["label"],
                "source_file": payload["path"],
                "cases": data["case_count"],
                "methods": data["method_count"],
                "errors": len(data.get("errors") or []),
                "prediction_gate": gates["prediction_metrics"]["status"],
                "plan_gate": gates["plan_metrics"]["status"],
                "slice_gate": gates["slice_leadership"]["status"],
                "slice_failure_count": gates["slice_leadership"].get("failure_count"),
            }
        )
    pd.DataFrame(dataset_overview).to_csv(TABLE_DIR / "dataset_overview.csv", index=False, encoding="utf-8-sig")

    small_predictions = predictions_df[predictions_df["method"].isin([PRIMARY, META, "last_year_rank", "weighted_recent_rank"])]
    small_predictions.to_parquet(DATA_DIR / "selected_predictions.parquet", index=False)


def build_figures(
    metrics_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
    categories_df: pd.DataFrame,
    evolution_df: pd.DataFrame,
    slice_df: pd.DataFrame,
    dataset_df: pd.DataFrame,
) -> None:
    fig_pipeline()
    fig_aris_protocol()
    fig_dataset_distribution(dataset_df)
    fig_baseline_taxonomy(categories_df)
    fig_leaderboard(metrics_df, "mae_rank", "fig_rank_mae_leaderboard.png", "Lower MAE rank is better")
    fig_leaderboard(metrics_df, "mae_score", "fig_score_mae_leaderboard.png", "Lower MAE score is better")
    fig_hit_rates(metrics_df)
    fig_error_distribution(predictions_df)
    fig_evolution(evolution_df)
    fig_slice_heatmap(slice_df)
    fig_planning_metrics(plan_df)


def fig_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(16, 2.8))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    boxes = [
        ("Local data", "admission lines\nrank-score map"),
        ("Replay", "held-out year\nprior history only"),
        ("Baselines", "heuristics\nML regressors\nensembles"),
        ("Meta router", "scenario-aware\nbase prediction"),
        ("Expert routes", "16 corrections\nrank/score blend"),
        ("Planning", "7 slots\nrisk buckets"),
        ("Evaluation", "prediction\nplanning\nslice diagnostics"),
    ]
    colors = ["#E7EEF8", "#EAF4EA", "#FEF3D5", "#E8E1F1", "#FCE5D8", "#E5F3F0", "#F0F0F0"]
    x_positions = np.linspace(0.09, 0.91, len(boxes))
    for i, ((title, subtitle), x) in enumerate(zip(boxes, x_positions)):
        ax.text(
            x,
            0.55,
            f"{title}\n{subtitle}",
            ha="center",
            va="center",
            fontsize=9.2,
            linespacing=1.35,
            bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.08", fc=colors[i], ec="#4B5563", lw=1.0),
        )
        if i < len(boxes) - 1:
            ax.annotate(
                "",
                xy=(x_positions[i + 1] - 0.055, 0.55),
                xytext=(x + 0.055, 0.55),
                arrowprops=dict(arrowstyle="->", color="#374151", lw=1.4),
            )
    ax.set_title("Volunteer matching prediction and planning workflow", fontsize=14, pad=8)
    savefig(fig, "fig_method_pipeline.png")


def fig_aris_protocol() -> None:
    fig, ax = plt.subplots(figsize=(15, 3.2))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    boxes = [
        ("Narrative report", "claims\nexperiments\nresults"),
        ("Paper plan", "claims-evidence\nsection outline"),
        ("Paper figures", "JSON/CSV-driven\nplots and tables"),
        ("LaTeX writing", "section draft\ncitations"),
        ("Compile", "PDF build\nformat check"),
        ("Improve loop", "review\naudit\nrevise"),
    ]
    colors = ["#E7EEF8", "#FEF3D5", "#E5F3F0", "#E8E1F1", "#F0F0F0", "#FCE5D8"]
    x_positions = np.linspace(0.10, 0.90, len(boxes))
    for i, ((title, subtitle), x) in enumerate(zip(boxes, x_positions)):
        ax.text(
            x,
            0.55,
            f"{title}\n{subtitle}",
            ha="center",
            va="center",
            fontsize=9.2,
            linespacing=1.25,
            bbox=dict(boxstyle="round,pad=0.42,rounding_size=0.08", fc=colors[i], ec="#4B5563", lw=1.0),
        )
        if i < len(boxes) - 1:
            ax.annotate(
                "",
                xy=(x_positions[i + 1] - 0.065, 0.55),
                xytext=(x + 0.065, 0.55),
                arrowprops=dict(arrowstyle="->", color="#374151", lw=1.35),
            )
    ax.annotate(
        "",
        xy=(x_positions[1] - 0.025, 0.28),
        xytext=(x_positions[-1] + 0.015, 0.28),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.20", color="#B45309", lw=1.3),
    )
    ax.text(0.52, 0.13, "review findings feed back into plan, figures, and text", ha="center", fontsize=9, color="#92400E")
    ax.set_title("ARIS-inspired paper writing protocol used for this report", fontsize=14, pad=6)
    savefig(fig, "fig_aris_writing_protocol.png")


def fig_dataset_distribution(dataset_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8), gridspec_kw={"width_ratios": [1.0, 1.3]})
    year_counts = dataset_df.groupby(["validation_set", "target_year"], as_index=False)["case_count"].sum()
    sns.barplot(data=year_counts, x="target_year", y="case_count", hue="validation_set", palette=set_palette(), ax=axes[0])
    axes[0].set_title("Cases by target year")
    axes[0].set_xlabel("Target year")
    axes[0].set_ylabel("Cases")
    axes[0].legend(title="")

    main = dataset_df[dataset_df["validation_set"] == "Main"]
    province_batch = (
        main.groupby(["province_label", "batch_label"], as_index=False)["case_count"].sum().sort_values("case_count", ascending=False)
    )
    sns.barplot(
        data=province_batch,
        y="province_label",
        x="case_count",
        hue="batch_label",
        palette="Set2",
        ax=axes[1],
    )
    axes[1].set_title("Main set coverage by province and batch")
    axes[1].set_xlabel("Cases")
    axes[1].set_ylabel("")
    axes[1].legend(title="Batch", bbox_to_anchor=(1.02, 1.0), loc="upper left")
    fig.tight_layout()
    savefig(fig, "fig_dataset_distribution.png")


def fig_baseline_taxonomy(categories_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    data = categories_df.sort_values("method_count", ascending=True)
    sns.barplot(data=data, y="category", x="method_count", palette="Set3", ax=ax)
    ax.set_title("Benchmark method taxonomy")
    ax.set_xlabel("Number of methods")
    ax.set_ylabel("")
    for container in ax.containers:
        ax.bar_label(container, padding=3, fontsize=9)
    fig.tight_layout()
    savefig(fig, "fig_baseline_taxonomy.png")


def fig_leaderboard(metrics_df: pd.DataFrame, metric: str, filename: str, subtitle: str) -> None:
    comparable = metrics_df[metrics_df["coverage_rate"].fillna(0) >= 0.95].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4), sharex=False)
    for ax, set_name in zip(axes, ["Main", "Boundary"]):
        data = comparable[comparable["validation_set"] == set_name].sort_values(metric, ascending=True).head(10)
        data = data.sort_values(metric, ascending=False)
        colors = ["#2563EB" if m == PRIMARY else "#94A3B8" for m in data["method"]]
        ax.barh(data["method_label"], data[metric], color=colors)
        ax.set_title(f"{set_name} set")
        ax.set_xlabel(METRIC_LABELS[metric])
        ax.set_ylabel("")
        ax.grid(axis="x", alpha=0.3)
    fig.suptitle(f"{METRIC_LABELS[metric]} leaderboard among high-coverage methods\n{subtitle}", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    savefig(fig, filename)


def fig_hit_rates(metrics_df: pd.DataFrame) -> None:
    comparable = metrics_df[metrics_df["coverage_rate"].fillna(0) >= 0.95].copy()
    selected_methods = [PRIMARY, META, "last_year_rank", "weighted_recent_rank", "best_recent_rank"]
    data = comparable[comparable["method"].isin(selected_methods)]
    melted = data.melt(
        id_vars=["validation_set", "method", "method_label"],
        value_vars=["within_3_score_points", "within_5_score_points", "within_10_score_points"],
        var_name="metric",
        value_name="hit_rate",
    )
    melted["metric_label"] = melted["metric"].map(METRIC_LABELS)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2), sharey=True)
    for ax, set_name in zip(axes, ["Main", "Boundary"]):
        subset = melted[melted["validation_set"] == set_name]
        sns.barplot(data=subset, x="metric_label", y="hit_rate", hue="method_label", palette=set_palette(), ax=ax)
        ax.set_title(f"{set_name} score hit rates")
        ax.set_xlabel("")
        ax.set_ylabel("Hit rate")
        ax.set_ylim(0, 0.65)
        ax.legend(title="", fontsize=8)
    fig.tight_layout()
    savefig(fig, "fig_score_hit_rates.png")


def fig_error_distribution(predictions_df: pd.DataFrame) -> None:
    selected = [PRIMARY, META, "last_year_rank", "weighted_recent_rank"]
    main = predictions_df[
        (predictions_df["validation_set"] == "Main")
        & (predictions_df["method"].isin(selected))
        & predictions_df["ae_rank"].notna()
        & predictions_df["ae_score"].notna()
    ].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    sns.boxplot(
        data=main,
        x="method_label",
        y="log10_ae_rank_plus1",
        palette=set_palette(),
        showfliers=False,
        ax=axes[0],
    )
    axes[0].set_title("Main set rank-error distribution")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("log10(abs rank error + 1)")
    axes[0].tick_params(axis="x", rotation=20)

    sns.boxplot(
        data=main,
        x="method_label",
        y="ae_score",
        palette=set_palette(),
        showfliers=False,
        ax=axes[1],
    )
    axes[1].set_title("Main set score-error distribution")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Absolute score error")
    axes[1].tick_params(axis="x", rotation=20)
    fig.tight_layout()
    savefig(fig, "fig_error_distribution.png")


def fig_evolution(evolution_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.7))
    line_specs = [
        ("mae_rank", "MAE rank", "lower is better"),
        ("mae_score", "MAE score", "lower is better"),
        ("slice_failures", "Slice failures", "diagnostic, lower is better"),
    ]
    for ax, (metric, label, subtitle) in zip(axes, line_specs):
        sns.lineplot(
            data=evolution_df,
            x="version",
            y=metric,
            hue="validation_set",
            marker="o",
            palette=set_palette(),
            ax=ax,
        )
        ax.set_title(f"{label}\n{subtitle}", fontsize=11)
        ax.set_xlabel("Route-spec version")
        ax.set_ylabel(label)
        ax.grid(True, alpha=0.3)
        ax.legend(title="")
    fig.tight_layout()
    savefig(fig, "fig_v37_v50_trajectory.png")


def fig_slice_heatmap(slice_df: pd.DataFrame) -> None:
    dimension_counts = (
        slice_df.groupby(["validation_set", "dimension_label"], as_index=False)["failure_count"].sum()
    )
    pivot = dimension_counts.pivot(index="dimension_label", columns="validation_set", values="failure_count").fillna(0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(8.5, 7.2))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, cbar_kws={"label": "Failed metric count"}, ax=ax)
    ax.set_title("Diagnostic slice-leadership failures by slice dimension")
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    savefig(fig, "fig_slice_failure_heatmap.png")


def fig_planning_metrics(plan_df: pd.DataFrame) -> None:
    selected = [
        PRIMARY,
        META,
        "volunteer_matching_rank_ensemble",
        "volunteer_matching_segmented_rank_ensemble",
        "best_recent_rank",
    ]
    data = plan_df[plan_df["method"].isin(selected)].copy()
    quality = data.melt(
        id_vars=["validation_set", "method", "method_label"],
        value_vars=["admissible_rate", "ndcg", "expected_utility"],
        var_name="metric",
        value_name="value",
    )
    quality["metric_label"] = quality["metric"].map(METRIC_LABELS)
    regret = data[["validation_set", "method_label", "safety_gated_regret"]].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    sns.barplot(data=quality, x="metric_label", y="value", hue="method_label", palette=set_palette(), ax=axes[0])
    axes[0].set_title("Planning quality metrics")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Value")
    axes[0].set_ylim(0, 1.0)
    axes[0].legend(title="", fontsize=8)

    sns.barplot(data=regret, x="validation_set", y="safety_gated_regret", hue="method_label", palette=set_palette(), ax=axes[1])
    axes[1].set_title("Safety-gated regret")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Regret, lower is better")
    axes[1].legend(title="", fontsize=8)
    fig.tight_layout()
    savefig(fig, "fig_planning_metrics.png")


def write_summary_json(
    payloads: dict[str, dict[str, Any]],
    metrics_df: pd.DataFrame,
    plan_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    evolution_df: pd.DataFrame,
) -> None:
    primary_metrics = {}
    primary_plan = {}
    for set_name in ["Main", "Boundary"]:
        primary_metrics[set_name] = (
            metrics_df[(metrics_df["validation_set"] == set_name) & (metrics_df["method"] == PRIMARY)]
            .iloc[0]
            .replace({np.nan: None})
            .to_dict()
        )
        primary_plan[set_name] = (
            plan_df[(plan_df["validation_set"] == set_name) & (plan_df["method"] == PRIMARY)]
            .iloc[0]
            .replace({np.nan: None})
            .to_dict()
        )
    summary = {
        "primary_method": PRIMARY,
        "validation_sets": {
            name: {
                "label": payload["label"],
                "source": payload["path"],
                "case_count": payload["data"]["case_count"],
                "method_count": payload["data"]["method_count"],
                "errors": len(payload["data"].get("errors") or []),
                "gates": payload["data"]["acceptance_gates"],
            }
            for name, payload in payloads.items()
        },
        "primary_metrics": primary_metrics,
        "primary_plan_metrics": primary_plan,
        "core_summary": summary_df.replace({np.nan: None}).to_dict(orient="records"),
        "latest_evolution": evolution_df.groupby("validation_set").tail(1).replace({np.nan: None}).to_dict(orient="records"),
    }
    (DATA_DIR / "paper_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def rank_method(df: pd.DataFrame, metric: str, direction: str, method: str) -> int:
    sorted_df = df.dropna(subset=[metric]).sort_values(metric, ascending=(direction == "asc")).reset_index(drop=True)
    matches = sorted_df.index[sorted_df["method"] == method].tolist()
    return int(matches[0] + 1) if matches else -1


def categorize_method(method: str) -> str:
    historical = {
        "last_year_rank",
        "two_year_mean_rank",
        "three_year_mean_rank",
        "historical_mean_rank",
        "historical_median_rank",
        "weighted_recent_rank",
        "exponential_smoothing_rank",
        "linear_trend_rank",
        "volatility_conservative_rank",
        "plan_adjusted_mean_rank",
        "best_recent_rank",
        "worst_recent_rank",
    }
    volunteer = {
        "volunteer_matching_rank_ensemble",
        "volunteer_matching_segmented_rank_ensemble",
        "volunteer_matching_meta_router",
        PRIMARY,
    }
    linear = {"sklearn_ridge", "sklearn_lasso", "sklearn_elastic_net", "sklearn_huber"}
    tree = {
        "sklearn_random_forest",
        "sklearn_extra_trees",
        "sklearn_gradient_boosting",
        "sklearn_hist_gradient_boosting",
        "sklearn_ada_boost",
        "sklearn_bagging_tree",
        "xgboost_regressor",
        "lightgbm_regressor",
        "catboost_regressor",
    }
    if method in historical:
        return "Historical rank heuristics"
    if method in volunteer:
        return "Volunteer matching routers and ensembles"
    if method in linear:
        return "Linear and robust regressors"
    if method in tree:
        return "Tree and boosting regressors"
    return "Other ML regressors"


def label_method(method: str | None) -> str:
    if not method:
        return ""
    return METHOD_LABELS.get(method, method.replace("_", " "))


def filters_to_text(filters: dict[str, Any], contains: dict[str, str]) -> str:
    parts = [f"{key}={value}" for key, value in filters.items()]
    parts.extend(f"{key} contains {value}" for key, value in contains.items())
    return "; ".join(parts)


def set_palette() -> list[str]:
    return ["#2563EB", "#D97706", "#059669", "#DB2777", "#7C3AED", "#64748B"]


def savefig(fig: plt.Figure, filename: str) -> None:
    fig.savefig(FIG_DIR / filename, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
