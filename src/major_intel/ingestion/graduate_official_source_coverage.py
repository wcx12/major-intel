from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/graduate_official_source_coverage"

DEFAULT_SCHOOL_COVERAGE_PATH = ROOT / "data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv"
DEFAULT_CLEAN_SOURCE_ATTEMPTS_PATH = ROOT / "data/cleaned/graduate_outcomes/official_recommendation_source_attempts.csv"
DEFAULT_SCHOOL_YEAR_SUMMARY_PATH = (
    ROOT / "data/processed/graduate_outcomes_official_site_recommendation_master/school_year_summary.csv"
)
DEFAULT_REMAINING_ATTEMPTS_PATH = (
    ROOT / "data/processed/graduate_outcomes_official_recommendation_remaining15/source_attempts.csv"
)
DEFAULT_EMPLOYMENT_SOURCES_PATH = (
    ROOT / "data/processed/graduate_outcomes_official_employment_reports_remaining15/report_sources.csv"
)
DEFAULT_EMPLOYMENT_METRICS_PATH = (
    ROOT / "data/processed/graduate_outcomes_official_employment_reports_remaining15/report_metrics_clean.csv"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _int(value: Any) -> int:
    try:
        return int(float(str(value or "0").replace(",", "")))
    except ValueError:
        return 0


def _float_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        return str(float(text))
    except ValueError:
        return text


def _split_multi(value: str) -> list[str]:
    return [part.strip() for part in str(value or "").split(";") if part.strip()]


def _join(values: Any) -> str:
    return ";".join(str(value) for value in sorted({str(item) for item in values if str(item)}))


def _path_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_artifact_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def _artifact_inventory_rows(source_rows: list[dict[str, str]], *, source_table: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_index, source in enumerate(source_rows, start=1):
        for artifact_index, artifact in enumerate(_split_multi(source.get("local_artifact", "")), start=1):
            path = _resolve_artifact_path(artifact)
            exists = path.is_file()
            info = file_info(path) if exists else {"bytes": "", "sha256": ""}
            rows.append(
                {
                    "artifact_inventory_id": f"{source_table}:{source_index}:{artifact_index}",
                    "source_table": source_table,
                    "school_name": source.get("school_name", ""),
                    "source_title": source.get("source_title", ""),
                    "artifact_path": artifact,
                    "artifact_suffix": path.suffix.lower(),
                    "artifact_exists": str(exists).lower(),
                    "artifact_bytes": info["bytes"],
                    "artifact_sha256": info["sha256"],
                    "included_raw_file_in_package": "false",
                    "raw_file_exclusion_reason": (
                        "metadata_only_raw_public_sources_may_contain_person_level_rows_or_large_original_files"
                    ),
                }
            )
    return rows


def _augment_attempt_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    augmented: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        artifacts = _split_multi(row.get("local_artifact", ""))
        urls = _split_multi(row.get("source_url", ""))
        existing_count = sum(1 for item in artifacts if _resolve_artifact_path(item).is_file())
        output = dict(row)
        output.update(
            {
                "attempt_id": f"graduate_official_recommendation_attempt:{index:04d}",
                "source_url_count": len(urls),
                "local_artifact_count": len(artifacts),
                "local_artifact_existing_count": existing_count,
                "local_artifact_missing_count": max(len(artifacts) - existing_count, 0),
            }
        )
        augmented.append(output)
    return augmented


def _augment_employment_source_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    augmented: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        artifacts = _split_multi(row.get("local_artifact", ""))
        urls = _split_multi(row.get("source_url", ""))
        existing_count = sum(1 for item in artifacts if _resolve_artifact_path(item).is_file())
        output = dict(row)
        output.update(
            {
                "employment_source_id": f"graduate_official_employment_source:{index:04d}",
                "source_url_count": len(urls),
                "local_artifact_count": len(artifacts),
                "local_artifact_existing_count": existing_count,
                "local_artifact_missing_count": max(len(artifacts) - existing_count, 0),
            }
        )
        augmented.append(output)
    return augmented


def _school_year_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        new_row = dict(row)
        new_row["school_year_source_id"] = f"graduate_official_school_year_source:{index:04d}"
        output.append(new_row)
    return output


def _school_coverage_rows(
    coverage_rows: list[dict[str, str]],
    school_year_rows: list[dict[str, Any]],
    attempt_rows: list[dict[str, Any]],
    employment_sources: list[dict[str, Any]],
    employment_metrics: list[dict[str, str]],
) -> list[dict[str, Any]]:
    school_year_by_school: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in school_year_rows:
        school_year_by_school[row.get("school_name", "")].append(row)

    attempts_by_school: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in attempt_rows:
        attempts_by_school[row.get("school_name", "")].append(row)

    employment_sources_by_school: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in employment_sources:
        employment_sources_by_school[row.get("school_name", "")].append(row)

    employment_metrics_by_school: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in employment_metrics:
        employment_metrics_by_school[row.get("school_name", "")].append(row)

    coverage_by_school = {row.get("school_name", ""): row for row in coverage_rows}
    all_schools = sorted(
        set(coverage_by_school)
        | set(school_year_by_school)
        | set(attempts_by_school)
        | set(employment_sources_by_school)
        | set(employment_metrics_by_school)
    )

    output: list[dict[str, Any]] = []
    for school_name in all_schools:
        coverage = coverage_by_school.get(school_name, {})
        source_years = school_year_by_school.get(school_name, [])
        attempts = attempts_by_school.get(school_name, [])
        emp_sources = employment_sources_by_school.get(school_name, [])
        emp_metrics = employment_metrics_by_school.get(school_name, [])
        decision_counts = Counter(row.get("decision", "") for row in attempts)
        extraction_counts = Counter(row.get("extraction_status", "") for row in emp_sources)
        output.append(
            {
                "school_name": school_name,
                "school_id": coverage.get("school_id", ""),
                "province": coverage.get("province", ""),
                "official_url": coverage.get("official_url", ""),
                "has_official_recommendation_records": coverage.get("has_official_recommendation_records", ""),
                "official_recommendation_record_count": _int(
                    coverage.get("official_recommendation_record_count", "")
                ),
                "coverage_note": coverage.get("coverage_note", ""),
                "school_year_summary_rows": len(source_years),
                "school_years_covered": _join(row.get("year", "") for row in source_years),
                "document_types": _join(row.get("document_type", "") for row in source_years),
                "routes": _join(row.get("route", "") for row in source_years),
                "master_summary_record_count": sum(_int(row.get("record_count", "")) for row in source_years),
                "master_summary_unique_person_count": sum(
                    _int(row.get("unique_person_count", "")) for row in source_years
                ),
                "master_summary_needs_review_count": sum(
                    _int(row.get("needs_review_count", "")) for row in source_years
                ),
                "master_summary_source_document_count": sum(
                    _int(row.get("source_document_count", "")) for row in source_years
                ),
                "recommendation_attempt_count": len(attempts),
                "recommendation_ingested_attempt_count": decision_counts["ingested"],
                "recommendation_no_ingest_attempt_count": decision_counts["no_ingest"],
                "recommendation_blocker_types": _join(row.get("blocker_type", "") for row in attempts),
                "recommendation_latest_checked_date": max(
                    (row.get("last_checked_date", "") for row in attempts), default=""
                ),
                "employment_source_count": len(emp_sources),
                "employment_metrics_extracted_source_count": extraction_counts["metrics_extracted"],
                "employment_no_ingest_source_count": extraction_counts["no_ingest"],
                "employment_source_only_count": extraction_counts["source_only"],
                "employment_metric_count": len(emp_metrics),
                "employment_metric_names": _join(row.get("metric_name", "") for row in emp_metrics),
                "employment_report_years": _join(row.get("report_year_or_cohort", "") for row in emp_metrics),
            }
        )
    return output


def build_graduate_official_source_coverage(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    school_coverage_path: Path = DEFAULT_SCHOOL_COVERAGE_PATH,
    clean_source_attempts_path: Path = DEFAULT_CLEAN_SOURCE_ATTEMPTS_PATH,
    school_year_summary_path: Path = DEFAULT_SCHOOL_YEAR_SUMMARY_PATH,
    remaining_attempts_path: Path = DEFAULT_REMAINING_ATTEMPTS_PATH,
    employment_sources_path: Path = DEFAULT_EMPLOYMENT_SOURCES_PATH,
    employment_metrics_path: Path = DEFAULT_EMPLOYMENT_METRICS_PATH,
    generated_at: str | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    coverage_rows = read_csv(Path(school_coverage_path))
    clean_attempts = read_csv(Path(clean_source_attempts_path))
    remaining_attempts = read_csv(Path(remaining_attempts_path))
    school_year_input_rows = read_csv(Path(school_year_summary_path))
    employment_source_input_rows = read_csv(Path(employment_sources_path))
    employment_metric_rows = read_csv(Path(employment_metrics_path))

    attempt_rows = _augment_attempt_rows(remaining_attempts)
    employment_source_rows = _augment_employment_source_rows(employment_source_input_rows)
    school_year_output_rows = _school_year_rows(school_year_input_rows)
    artifact_rows = [
        *_artifact_inventory_rows(attempt_rows, source_table="recommendation_attempts"),
        *_artifact_inventory_rows(employment_source_rows, source_table="employment_sources"),
    ]
    school_coverage_output_rows = _school_coverage_rows(
        coverage_rows,
        school_year_output_rows,
        attempt_rows,
        employment_source_rows,
        employment_metric_rows,
    )

    output_files: dict[str, tuple[list[dict[str, Any]], list[str]]] = {
        "graduate_official_source_school_coverage_2026.csv": (
            school_coverage_output_rows,
            [
                "school_name",
                "school_id",
                "province",
                "official_url",
                "has_official_recommendation_records",
                "official_recommendation_record_count",
                "coverage_note",
                "school_year_summary_rows",
                "school_years_covered",
                "document_types",
                "routes",
                "master_summary_record_count",
                "master_summary_unique_person_count",
                "master_summary_needs_review_count",
                "master_summary_source_document_count",
                "recommendation_attempt_count",
                "recommendation_ingested_attempt_count",
                "recommendation_no_ingest_attempt_count",
                "recommendation_blocker_types",
                "recommendation_latest_checked_date",
                "employment_source_count",
                "employment_metrics_extracted_source_count",
                "employment_no_ingest_source_count",
                "employment_source_only_count",
                "employment_metric_count",
                "employment_metric_names",
                "employment_report_years",
            ],
        ),
        "graduate_official_source_school_year_summary_2026.csv": (
            school_year_output_rows,
            [
                "school_year_source_id",
                "school_name",
                "year",
                "document_type",
                "route",
                "record_count",
                "unique_person_count",
                "needs_review_count",
                "with_undergraduate_school_count",
                "with_admission_major_count",
                "source_document_count",
            ],
        ),
        "graduate_official_recommendation_attempts_2026.csv": (
            attempt_rows,
            [
                "attempt_id",
                "school_name",
                "data_track",
                "source_title",
                "source_url",
                "local_artifact",
                "live_status",
                "content_type",
                "decision",
                "blocker_type",
                "notes",
                "last_checked_date",
                "source_url_count",
                "local_artifact_count",
                "local_artifact_existing_count",
                "local_artifact_missing_count",
            ],
        ),
        "graduate_official_employment_sources_2026.csv": (
            employment_source_rows,
            [
                "employment_source_id",
                "school_name",
                "data_track",
                "report_year_or_cohort",
                "source_title",
                "source_url",
                "local_artifact",
                "fetch_status",
                "content_type",
                "extraction_status",
                "notes",
                "source_url_count",
                "local_artifact_count",
                "local_artifact_existing_count",
                "local_artifact_missing_count",
            ],
        ),
        "graduate_official_employment_metrics_2026.csv": (
            [{**row, "metric_value": _float_text(row.get("metric_value", ""))} for row in employment_metric_rows],
            [
                "school_name",
                "report_year_or_cohort",
                "metric_name",
                "metric_value",
                "metric_unit",
                "scope",
                "source_url",
                "evidence_note",
                "extraction_quality",
            ],
        ),
        "graduate_official_local_artifact_inventory_2026.csv": (
            artifact_rows,
            [
                "artifact_inventory_id",
                "source_table",
                "school_name",
                "source_title",
                "artifact_path",
                "artifact_suffix",
                "artifact_exists",
                "artifact_bytes",
                "artifact_sha256",
                "included_raw_file_in_package",
                "raw_file_exclusion_reason",
            ],
        ),
    }

    for name, (rows, fields) in output_files.items():
        write_csv(output_dir / name, rows, fields)

    manifest = {
        "generated_at": generated_at,
        "dataset": "graduate_official_source_coverage",
        "status": "metadata_and_coverage_no_raw_person_level_files",
        "input_files": [
            _path_key(Path(school_coverage_path)),
            _path_key(Path(clean_source_attempts_path)),
            _path_key(Path(school_year_summary_path)),
            _path_key(Path(remaining_attempts_path)),
            _path_key(Path(employment_sources_path)),
            _path_key(Path(employment_metrics_path)),
        ],
        "row_counts": {
            "school_coverage": len(school_coverage_output_rows),
            "school_year_summary": len(school_year_output_rows),
            "clean_source_attempts": len(clean_attempts),
            "recommendation_attempts": len(attempt_rows),
            "employment_sources": len(employment_source_rows),
            "employment_metrics": len(employment_metric_rows),
            "local_artifact_inventory": len(artifact_rows),
        },
        "distributions": {
            "school_has_official_recommendation_records": dict(
                sorted(Counter(row.get("has_official_recommendation_records", "") for row in coverage_rows).items())
            ),
            "recommendation_attempt_decision": dict(
                sorted(Counter(row.get("decision", "") for row in attempt_rows).items())
            ),
            "recommendation_attempt_blocker_type": dict(
                sorted(Counter(row.get("blocker_type", "") for row in attempt_rows).items())
            ),
            "employment_source_extraction_status": dict(
                sorted(Counter(row.get("extraction_status", "") for row in employment_source_rows).items())
            ),
            "employment_source_fetch_status": dict(
                sorted(Counter(row.get("fetch_status", "") for row in employment_source_rows).items())
            ),
            "artifact_exists": dict(sorted(Counter(row.get("artifact_exists", "") for row in artifact_rows).items())),
        },
        "privacy_and_packaging_notes": [
            "This package contains coverage metadata, source URLs, metrics, and hashes of local artifacts.",
            "Raw official PDFs/HTML/XLSX files are not embedded because many original files may contain public person-level rows.",
            "Use public masked graduate outcome packages for row-level analysis.",
        ],
        "checksums": {
            **{
                f"data/processed/graduate_official_source_coverage/{name}": file_info(output_dir / name)
                for name in output_files
            },
        },
    }
    manifest_path = output_dir / "graduate_official_source_coverage_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build graduate official source coverage tables.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_graduate_official_source_coverage(
        output_dir=args.output_dir,
        generated_at=args.generated_at,
    )
    print(
        json.dumps(
            {
                "dataset": manifest["dataset"],
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
