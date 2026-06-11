"""Offline benchmark runner for volunteer matching prediction methods."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .audit import audit_metric_leadership
from .baselines import baseline_names, predict_with_baseline
from .metrics import evaluate_predictions, evaluate_predictions_by_group
from .models import PredictionCase, case_from_dict, case_to_dict
from .route_search import DEFAULT_PREDICTION_EXPERT_ROUTE_SPECS, apply_route_specs


PREDICTION_EXPERT_ROUTER_METHOD = "volunteer_matching_prediction_expert_router"
PRIMARY_METHODS = (
    PREDICTION_EXPERT_ROUTER_METHOD,
    "volunteer_matching_meta_router",
    "volunteer_matching_residual_router",
    "volunteer_matching_segmented_rank_ensemble",
    "volunteer_matching_rank_ensemble",
)
PREDICTION_LEADERSHIP_MIN_COVERAGE = 0.99
PREDICTION_LEADERSHIP_METRICS = {
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
    "directional_bias_abs": "asc",
    "severe_error_rate": "asc",
    "severe_directional_balance_abs": "asc",
}
PREDICTION_LEADERSHIP_TOLERANCES = {
    "mae_rank": 250,
    "median_ae_rank": 250,
    "p90_ae_rank": 500,
    "rmse_rank": 500,
    "mae_score": 0.5,
    "median_ae_score": 0.5,
    "p90_ae_score": 1.0,
    "rmse_score": 1.0,
    "within_3_score_points": 0.02,
    "within_5_score_points": 0.02,
    "within_10_score_points": 0.02,
    "directional_bias_abs": 0.03,
    "severe_error_rate": 0.02,
    "severe_directional_balance_abs": 0.002,
}
PLAN_LEADERSHIP_METRICS = {
    "admissible_rate": "desc",
    "first_admissible_position_mean": "asc",
    "bucket_balance_error": "asc",
    "ndcg": "desc",
    "no_offer_rate": "asc",
    "expected_utility": "desc",
    "safety_gated_regret": "asc",
}
SLICE_AUDIT_FIELD_SETS = [
    ("target_year",),
    ("opportunity_grain",),
    ("province_id",),
    ("province_name",),
    ("subject_type",),
    ("batch",),
    ("target_year", "province_id"),
    ("target_year", "opportunity_grain"),
    ("province_id", "opportunity_grain"),
    ("target_year", "province_id", "batch"),
    ("target_year", "province_id", "batch", "opportunity_grain"),
]


def run_benchmark(
    cases: list[PredictionCase],
    methods: list[str] | None = None,
    *,
    include_ml: bool = False,
    ml_methods: list[str] | None = None,
    include_residual_router: bool = False,
    residual_base_method: str = "volunteer_matching_meta_router",
    residual_min_examples: int = 12,
    residual_shrinkage: float = 0.35,
    include_planning: bool = False,
    planning_applicant_ranks: list[int] | None = None,
    planning_slots: int = 7,
) -> dict[str, Any]:
    selected_methods = methods or baseline_names()
    predictions: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for case in cases:
        for method in selected_methods:
            try:
                prediction = predict_with_baseline(method, case)
            except Exception as exc:  # noqa: BLE001 - benchmark should keep other methods running.
                errors.append(
                    {
                        "method": method,
                        "opportunity_key": case.opportunity_key,
                        "error": str(exc),
                    }
                )
                continue
            predictions.append(
                {
                    "method": method,
                    "opportunity_key": case.opportunity_key,
                    "target_year": case.target_year,
                    "actual_rank": case.actual_rank,
                    "actual_score": case.actual_score,
                    "predicted_rank": prediction.predicted_rank,
                    "planning_rank": prediction.planning_rank,
                    "predicted_score": prediction.predicted_score,
                    "confidence": prediction.confidence,
                    "evidence_years": prediction.evidence_years,
                    "warnings": prediction.warnings,
                    **_case_group_fields(case),
                }
            )

    selected_ml_methods: list[str] = []
    if include_ml:
        from .ml_baselines import ml_baseline_names, predict_ml_baselines

        selected_ml_methods = ml_methods or ml_baseline_names()
        for method in selected_ml_methods:
            try:
                predictions.extend(predict_ml_baselines(cases, methods=[method]))
            except Exception as exc:  # noqa: BLE001 - keep other methods available.
                errors.append({"method": method, "opportunity_key": "*", "error": str(exc)})

    _append_prediction_expert_router(predictions, force=include_ml)

    if include_residual_router:
        from .residual_router import RESIDUAL_ROUTER_METHOD, predict_residual_router

        try:
            predictions.extend(
                predict_residual_router(
                    cases,
                    base_method=residual_base_method,
                    min_examples=residual_min_examples,
                    shrinkage=residual_shrinkage,
                )
            )
            selected_methods = [*selected_methods, RESIDUAL_ROUTER_METHOD]
        except Exception as exc:  # noqa: BLE001 - keep the rest of the benchmark inspectable.
            errors.append({"method": RESIDUAL_ROUTER_METHOD, "opportunity_key": "*", "error": str(exc)})

    metrics = _metrics_with_coverage(predictions, len(cases))
    reported_methods = _prediction_methods(predictions)
    result = {
        "case_count": len(cases),
        "method_count": len(reported_methods),
        "methods": reported_methods,
        "predictions": predictions,
        "metrics": metrics,
        "group_metrics": _group_metrics(predictions),
        "errors": errors,
    }
    if include_planning:
        from .planning import evaluate_rank_plans

        result["plan_metrics"] = evaluate_rank_plans(
            predictions,
            applicant_ranks=planning_applicant_ranks,
            total_slots=planning_slots,
        )
    result["leadership_audit"] = _leadership_audit(result)
    result["slice_leadership_audit"] = _slice_leadership_audit(result)
    result["acceptance_gates"] = _acceptance_gates(result)
    result["case_residual_audit"] = build_case_residual_audit(predictions, _primary_method(metrics))
    return result


def run_multi_year_benchmark(
    cases_by_year: dict[int, list[PredictionCase]],
    methods: list[str] | None = None,
    *,
    include_ml: bool = False,
    ml_methods: list[str] | None = None,
    include_residual_router: bool = False,
    residual_base_method: str = "volunteer_matching_meta_router",
    residual_min_examples: int = 12,
    residual_shrinkage: float = 0.35,
    include_planning: bool = False,
    planning_applicant_ranks: list[int] | None = None,
    planning_slots: int = 7,
) -> dict[str, Any]:
    year_results: dict[int, dict[str, Any]] = {}
    combined_predictions: list[dict[str, Any]] = []
    combined_errors: list[dict[str, Any]] = []

    for year, cases in sorted(cases_by_year.items()):
        result = run_benchmark(
            cases,
            methods=methods,
            include_ml=include_ml,
            ml_methods=ml_methods,
            include_residual_router=include_residual_router,
            residual_base_method=residual_base_method,
            residual_min_examples=residual_min_examples,
            residual_shrinkage=residual_shrinkage,
            include_planning=include_planning,
            planning_applicant_ranks=planning_applicant_ranks,
            planning_slots=planning_slots,
        )
        year_results[year] = result
        combined_predictions.extend(result["predictions"])
        for error in result["errors"]:
            combined_errors.append({"target_year": year, **error})

    combined = {
        "case_count": sum(len(cases) for cases in cases_by_year.values()),
        "method_count": len(_prediction_methods(combined_predictions)),
        "methods": _prediction_methods(combined_predictions),
        "predictions": combined_predictions,
        "metrics": _metrics_with_coverage(combined_predictions, sum(len(cases) for cases in cases_by_year.values())),
        "group_metrics": _group_metrics(combined_predictions),
        "errors": combined_errors,
    }
    if include_planning:
        from .planning import evaluate_rank_plans

        combined["plan_metrics"] = evaluate_rank_plans(
            combined_predictions,
            applicant_ranks=planning_applicant_ranks,
            total_slots=planning_slots,
        )
    combined["leadership_audit"] = _leadership_audit(combined)
    combined["slice_leadership_audit"] = _slice_leadership_audit(combined)
    combined["acceptance_gates"] = _acceptance_gates(combined)
    combined["case_residual_audit"] = build_case_residual_audit(combined_predictions, _primary_method(combined["metrics"]))

    return {
        "year_results": year_results,
        "combined": combined,
    }


def load_cases_jsonl(path: Path) -> list[PredictionCase]:
    cases = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                cases.append(case_from_dict(json.loads(line)))
    return cases


def write_cases_jsonl(cases: list[PredictionCase], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(case_to_dict(case), ensure_ascii=False, sort_keys=True) + "\n")


def render_markdown_report(result: dict[str, Any]) -> str:
    if "combined" in result and "year_results" in result:
        return render_multi_year_markdown_report(result)

    lines = [
        "# Volunteer Matching Benchmark",
        "",
        f"- Cases: {result['case_count']}",
        f"- Methods: {result['method_count']}",
        f"- Prediction rows: {len(result['predictions'])}",
        f"- Errors: {len(result['errors'])}",
        "",
        "## Metrics",
        "",
        "| Method | Rows | Coverage | MAE Rank | Median AE Rank | P90 AE Rank | RMSE Rank | MAE Score | Median AE Score | P90 AE Score | RMSE Score | Within 3 Score | Within 5 Score | Within 10 Score | Directional Bias | Severe Error | Severe Balance |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method, metrics in sorted(
        result["metrics"].items(),
        key=lambda item: (
            (item[1].get("coverage_rate", 1.0) or 0.0) < 1.0,
            item[1].get("mae_rank") is None,
            item[1].get("mae_rank") if item[1].get("mae_rank") is not None else float("inf"),
        ),
    ):
        lines.append(
            "| {method} | {rows} | {coverage} | {mae_rank} | {median_rank} | {p90_rank} | {rmse_rank} | {mae_score} | {median_score} | {p90_score} | {rmse_score} | {within3} | {within5} | {within10} | {bias} | {severe_error} | {severe_balance} |".format(
                method=method,
                rows=metrics.get("row_count"),
                coverage=_fmt(metrics.get("coverage_rate")),
                mae_rank=_fmt(metrics.get("mae_rank")),
                median_rank=_fmt(metrics.get("median_ae_rank")),
                p90_rank=_fmt(metrics.get("p90_ae_rank")),
                rmse_rank=_fmt(metrics.get("rmse_rank")),
                mae_score=_fmt(metrics.get("mae_score")),
                median_score=_fmt(metrics.get("median_ae_score")),
                p90_score=_fmt(metrics.get("p90_ae_score")),
                rmse_score=_fmt(metrics.get("rmse_score")),
                within3=_fmt(metrics.get("within_3_score_points")),
                within5=_fmt(metrics.get("within_5_score_points")),
                within10=_fmt(metrics.get("within_10_score_points")),
                bias=_fmt(metrics.get("directional_bias_abs")),
                severe_error=_fmt(metrics.get("severe_error_rate")),
                severe_balance=_fmt(metrics.get("severe_directional_balance_abs")),
            )
        )

    if result["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in result["errors"][:20]:
            lines.append(f"- `{error['method']}` {error['opportunity_key']}: {error['error']}")

    if result.get("plan_metrics"):
        lines.extend(
            [
                "",
                "## Plan Metrics",
                "",
                "| Method | Plans | Admissible Rate | First Admissible | No Offer | Expected Utility | Regret | Safety-Gated Regret | Bucket Error | NDCG |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for method, metrics in sorted(
            result["plan_metrics"].items(),
            key=lambda item: (
                -(item[1].get("admissible_rate") or 0),
                item[1].get("no_offer_rate") or float("inf"),
                item[1].get("first_admissible_position_mean") or float("inf"),
                item[1].get("regret") or float("inf"),
                item[1].get("bucket_balance_error") or float("inf"),
            ),
        ):
            lines.append(
                "| {method} | {plans} | {admissible} | {first} | {no_offer} | {utility} | {regret} | {safety_gated_regret} | {bucket_error} | {ndcg} |".format(
                    method=method,
                    plans=metrics.get("plan_count"),
                    admissible=_fmt(metrics.get("admissible_rate")),
                    first=_fmt(metrics.get("first_admissible_position_mean")),
                    no_offer=_fmt(metrics.get("no_offer_rate")),
                    utility=_fmt(metrics.get("expected_utility")),
                    regret=_fmt(metrics.get("regret")),
                    safety_gated_regret=_fmt(metrics.get("safety_gated_regret")),
                    bucket_error=_fmt(metrics.get("bucket_balance_error")),
                    ndcg=_fmt(metrics.get("ndcg")),
                )
            )

    audit = result.get("leadership_audit")
    if audit and (audit.get("prediction_metrics") or audit.get("plan_metrics")):
        lines.extend(["", "## Leadership Audit", ""])
        if audit.get("prediction_metrics"):
            lines.extend(
                [
                    "### Prediction Metrics",
                    "",
                    "| Metric | Status | Primary Value | Best Method | Best Value |",
                    "| --- | --- | ---: | --- | ---: |",
                ]
            )
            for row in audit["prediction_metrics"]:
                lines.append(
                    "| {metric} | {status} | {primary_value} | {best_method} | {best_value} |".format(
                        metric=row["metric"],
                        status=row["status"],
                        primary_value=_fmt(row.get("primary_value")),
                        best_method=row.get("best_method") or "-",
                        best_value=_fmt(row.get("best_value")),
                    )
                )
        if audit.get("plan_metrics"):
            lines.extend(
                [
                    "",
                    "### Plan Metrics",
                    "",
                    "| Metric | Status | Primary Value | Best Method | Best Value |",
                    "| --- | --- | ---: | --- | ---: |",
                ]
            )
            for row in audit["plan_metrics"]:
                lines.append(
                    "| {metric} | {status} | {primary_value} | {best_method} | {best_value} |".format(
                        metric=row["metric"],
                        status=row["status"],
                        primary_value=_fmt(row.get("primary_value")),
                        best_method=row.get("best_method") or "-",
                        best_value=_fmt(row.get("best_value")),
                    )
                )

    gates = result.get("acceptance_gates")
    if gates:
        lines.extend(
            [
                "",
                "## Acceptance Gates",
                "",
                "| Gate | Status | Failures | Details |",
                "| --- | --- | ---: | --- |",
            ]
        )
        for gate, gate_result in gates.items():
            details = ", ".join(
                f"{key}={value}"
                for key, value in gate_result.items()
                if key not in {"status", "failure_count"} and value is not None
            )
            lines.append(
                "| {gate} | {status} | {failures} | {details} |".format(
                    gate=gate,
                    status=gate_result.get("status"),
                    failures=gate_result.get("failure_count", 0),
                    details=details or "-",
                )
            )

    slice_audit = result.get("slice_leadership_audit")
    if slice_audit:
        lines.extend(
            [
                "",
                "## Slice Leadership Audit",
                "",
                "| Field | Slice | Primary Rows | Failures |",
                "| --- | --- | ---: | ---: |",
            ]
        )
        for field, groups in sorted(slice_audit.items()):
            for group, audit_result in sorted(groups.items()):
                lines.append(
                    "| {field} | {group} | {rows} | {failures} |".format(
                        field=field,
                        group=group,
                        rows=audit_result.get("primary_rows"),
                        failures=audit_result.get("failure_count"),
                    )
                )

    case_residual_audit = result.get("case_residual_audit")
    if case_residual_audit:
        lines.extend(["", "## Case Residual Audit", ""])
        for row in case_residual_audit[:20]:
            group = " / ".join(
                str(value)
                for value in (row.get("target_year"), row.get("province_id"), row.get("batch"))
                if value is not None
            )
            lines.append(
                "- `{case_key}` ({group}): rank gap {rank_gap} vs `{best_rank_method}`; score gap {score_gap} vs `{best_score_method}`.".format(
                    case_key=row.get("case_key") or row.get("opportunity_key"),
                    group=group or "-",
                    rank_gap=_fmt(row.get("rank_error_gap_to_best")),
                    best_rank_method=row.get("best_rank_method") or "-",
                    score_gap=_fmt(row.get("score_error_gap_to_best")),
                    best_score_method=row.get("best_score_method") or "-",
                )
            )

    return "\n".join(lines).rstrip() + "\n"


def render_multi_year_markdown_report(result: dict[str, Any]) -> str:
    combined = result["combined"]
    lines = [
        "# Volunteer Matching Benchmark",
        "",
        "## Combined Metrics",
        "",
        render_markdown_report(combined).strip(),
    ]
    for year, year_result in sorted(result["year_results"].items()):
        lines.extend(["", f"## {year} Metrics", "", render_markdown_report(year_result).strip()])
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate volunteer matching baselines.")
    parser.add_argument("--cases", type=Path, help="Prediction cases JSONL path.")
    parser.add_argument("--from-mysql", action="store_true", help="Export prediction cases from local MySQL.")
    parser.add_argument("--target-year", type=int, default=2025)
    parser.add_argument("--target-years", nargs="*", type=int, default=None)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--sample-mode", choices=["sequential", "stratified"], default="sequential")
    parser.add_argument("--methods", nargs="*", default=None)
    parser.add_argument("--include-ml", action="store_true", help="Add scikit-learn batch-trained baselines.")
    parser.add_argument("--ml-methods", nargs="*", default=None)
    parser.add_argument("--include-residual-router", action="store_true", help="Add non-leaky residual-router method.")
    parser.add_argument("--residual-base-method", default="volunteer_matching_meta_router")
    parser.add_argument("--residual-min-examples", type=int, default=12)
    parser.add_argument("--residual-shrinkage", type=float, default=0.35)
    parser.add_argument("--include-planning", action="store_true", help="Add plan-level recommendation metrics.")
    parser.add_argument("--planning-ranks", nargs="*", type=int, default=None)
    parser.add_argument("--planning-slots", type=int, default=7)
    parser.add_argument("--output-dir", type=Path, default=Path("reports/volunteer_matching"))
    parser.add_argument("--stamp", default="latest")
    args = parser.parse_args(argv)

    if args.from_mysql:
        from .mysql_export import export_cases_from_env

        target_years = args.target_years or [args.target_year]
        if len(target_years) > 1:
            cases_by_year = {
                year: export_cases_from_env(target_year=year, limit=args.limit, sample_mode=args.sample_mode)
                for year in target_years
            }
            result = run_multi_year_benchmark(
                cases_by_year,
                methods=args.methods,
                include_ml=args.include_ml,
                ml_methods=args.ml_methods,
                include_residual_router=args.include_residual_router,
                residual_base_method=args.residual_base_method,
                residual_min_examples=args.residual_min_examples,
                residual_shrinkage=args.residual_shrinkage,
                include_planning=args.include_planning,
                planning_applicant_ranks=args.planning_ranks,
                planning_slots=args.planning_slots,
            )
            return _write_result(result, args.output_dir, args.stamp)
        cases = export_cases_from_env(target_year=target_years[0], limit=args.limit, sample_mode=args.sample_mode)
    elif args.cases:
        cases = load_cases_jsonl(args.cases)
    else:
        parser.error("provide --cases or --from-mysql")

    result = run_benchmark(
        cases,
        methods=args.methods,
        include_ml=args.include_ml,
        ml_methods=args.ml_methods,
        include_residual_router=args.include_residual_router,
        residual_base_method=args.residual_base_method,
        residual_min_examples=args.residual_min_examples,
        residual_shrinkage=args.residual_shrinkage,
        include_planning=args.include_planning,
        planning_applicant_ranks=args.planning_ranks,
        planning_slots=args.planning_slots,
    )
    return _write_result(result, args.output_dir, args.stamp)


def _write_result(result: dict[str, Any], output_dir: Path, stamp: str) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"benchmark_{stamp}.json"
    md_path = output_dir / f"benchmark_{stamp}.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_markdown_report(result), encoding="utf-8")
    print(str(md_path))
    print(str(json_path))
    return 0


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def _case_group_fields(case: PredictionCase) -> dict[str, Any]:
    return {
        "province_id": case.metadata.get("province_id"),
        "province_name": case.metadata.get("province_name"),
        "subject_type": case.metadata.get("subject_type"),
        "batch": case.metadata.get("batch"),
        "opportunity_grain": case.metadata.get("opportunity_grain"),
    }


def _append_prediction_expert_router(predictions: list[dict[str, Any]], *, force: bool = False) -> None:
    application = apply_route_specs(
        predictions,
        base_method="volunteer_matching_meta_router",
        routed_method=PREDICTION_EXPERT_ROUTER_METHOD,
        route_specs=DEFAULT_PREDICTION_EXPERT_ROUTE_SPECS,
        force=force,
    )
    predictions.extend(application.routed_rows)


def _prediction_methods(predictions: list[dict[str, Any]]) -> list[str]:
    methods: list[str] = []
    seen: set[str] = set()
    for row in predictions:
        method = str(row.get("method"))
        if method not in seen:
            methods.append(method)
            seen.add(method)
    return methods


def _group_metrics(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    return {_field_set_name(fields): evaluate_predictions_by_group(predictions, list(fields)) for fields in SLICE_AUDIT_FIELD_SETS}


def _metrics_with_coverage(predictions: list[dict[str, Any]], case_count: int) -> dict[str, dict[str, Any]]:
    metrics = evaluate_predictions(predictions)
    denominator = case_count or 1
    for method_metrics in metrics.values():
        method_metrics["coverage_rate"] = round(float(method_metrics.get("rank_row_count", 0)) / denominator, 4)
    return metrics


def _leadership_audit(result: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    metrics = result.get("metrics", {})
    plan_metrics = result.get("plan_metrics", {})
    prediction_primary = _primary_method(metrics)
    plan_primary = _primary_method(plan_metrics)
    return {
        "prediction_metrics": audit_metric_leadership(
            metrics,
            primary_method=prediction_primary,
            metric_directions=PREDICTION_LEADERSHIP_METRICS,
            metric_tolerances=PREDICTION_LEADERSHIP_TOLERANCES,
            min_coverage_rate=PREDICTION_LEADERSHIP_MIN_COVERAGE,
        )
        if prediction_primary
        else [],
        "plan_metrics": audit_metric_leadership(
            plan_metrics,
            primary_method=plan_primary,
            metric_directions=PLAN_LEADERSHIP_METRICS,
        )
        if plan_primary
        else [],
    }


def _slice_leadership_audit(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    audits: dict[str, dict[str, Any]] = {}
    for field, groups in result.get("group_metrics", {}).items():
        field_audits: dict[str, Any] = {}
        for group, metrics in groups.items():
            primary = _primary_method(metrics)
            if not primary:
                continue
            rows = audit_metric_leadership(
                metrics,
                primary_method=primary,
                metric_directions=PREDICTION_LEADERSHIP_METRICS,
                metric_tolerances=PREDICTION_LEADERSHIP_TOLERANCES,
            )
            field_audits[group] = {
                "primary_method": primary,
                "primary_rows": metrics.get(primary, {}).get("row_count", 0),
                "failure_count": sum(1 for row in rows if row["status"] == "fail"),
                "prediction_metrics": rows,
            }
        if field_audits:
            audits[field] = field_audits
    return audits


def _acceptance_gates(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    audit = result.get("leadership_audit", {})
    prediction_failures = sum(1 for row in audit.get("prediction_metrics", []) if row.get("status") == "fail")
    plan_failures = sum(1 for row in audit.get("plan_metrics", []) if row.get("status") == "fail")
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


def build_case_residual_audit(predictions: list[dict[str, Any]], primary_method: str | None) -> list[dict[str, Any]]:
    if not primary_method:
        return []
    by_key: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in predictions:
        by_key.setdefault(_case_residual_key(row), []).append(row)

    audits: list[dict[str, Any]] = []
    for case_key, rows in sorted(by_key.items(), key=lambda item: tuple(str(value) for value in item[0])):
        primary_rows = [row for row in rows if row.get("method") == primary_method]
        if not primary_rows:
            continue
        primary = primary_rows[0]
        opportunity_key = str(primary.get("opportunity_key"))
        primary_rank_error = _rank_error(primary)
        primary_score_error = _score_error(primary)
        best_rank = min((row for row in rows if _rank_error(row) is not None), key=lambda row: _rank_error(row), default=None)
        best_score = min((row for row in rows if _score_error(row) is not None), key=lambda row: _score_error(row), default=None)
        best_rank_error = _rank_error(best_rank) if best_rank else None
        best_score_error = _score_error(best_score) if best_score else None
        audits.append(
            {
                "opportunity_key": opportunity_key,
                "primary_method": primary_method,
                "primary_rank_error": primary_rank_error,
                "best_rank_method": best_rank.get("method") if best_rank else None,
                "best_rank_error": best_rank_error,
                "rank_error_gap_to_best": _error_gap(primary_rank_error, best_rank_error),
                "primary_score_error": primary_score_error,
                "best_score_method": best_score.get("method") if best_score else None,
                "best_score_error": best_score_error,
                "score_error_gap_to_best": _error_gap(primary_score_error, best_score_error),
                "target_year": primary.get("target_year"),
                "province_id": primary.get("province_id"),
                "province_name": primary.get("province_name"),
                "subject_type": primary.get("subject_type"),
                "batch": primary.get("batch"),
                "opportunity_grain": primary.get("opportunity_grain"),
                "case_key": _render_case_residual_key(case_key),
            }
        )
    audits.sort(
        key=lambda row: (
            row.get("rank_error_gap_to_best") is None,
            -(float(row.get("rank_error_gap_to_best") or 0.0)),
            row["opportunity_key"],
        )
    )
    return audits


def _case_residual_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("opportunity_key"),
        row.get("target_year"),
        row.get("actual_rank"),
        row.get("actual_score"),
        row.get("province_id"),
        row.get("province_name"),
        row.get("subject_type"),
        row.get("batch"),
    )


def _render_case_residual_key(case_key: tuple[Any, ...]) -> str:
    return "|".join("" if value is None else str(value) for value in case_key)


def _rank_error(row: dict[str, Any] | None) -> int | None:
    if not row or row.get("predicted_rank") is None or row.get("actual_rank") is None:
        return None
    return abs(int(row["predicted_rank"]) - int(row["actual_rank"]))


def _score_error(row: dict[str, Any] | None) -> float | None:
    if not row or row.get("predicted_score") is None or row.get("actual_score") is None:
        return None
    return abs(float(row["predicted_score"]) - float(row["actual_score"]))


def _error_gap(primary_error: float | int | None, best_error: float | int | None) -> float | int | None:
    if primary_error is None or best_error is None:
        return None
    return primary_error - best_error


def _primary_method(metrics: dict[str, Any]) -> str | None:
    for method in PRIMARY_METHODS:
        if method in metrics:
            return method
    return None


def _field_set_name(fields: tuple[str, ...]) -> str:
    return "|".join(fields)


if __name__ == "__main__":
    raise SystemExit(main())
