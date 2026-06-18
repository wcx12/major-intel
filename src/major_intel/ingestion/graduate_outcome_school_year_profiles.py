"""Build school-year profiles from public graduate outcome assets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "graduate_outcome_school_year_profiles/v1"

PROFILE_FIELDS = [
    "school_year_profile_id",
    "school_name",
    "year",
    "source_types",
    "source_datasets",
    "routes",
    "document_types",
    "public_record_count",
    "as_destination_record_count",
    "as_undergraduate_source_record_count",
    "unique_public_record_count",
    "destination_school_count",
    "undergraduate_source_school_count",
    "admission_major_count",
    "undergraduate_major_count",
    "source_document_count",
    "needs_review_count",
    "avg_quality_score",
    "low_quality_record_count",
    "sample_destination_schools",
    "sample_undergraduate_source_schools",
    "sample_admission_majors",
    "sample_undergraduate_majors",
    "sample_source_urls",
    "official_metric_count",
    "official_report_source_count",
    "official_metric_names",
    "official_report_titles",
    "official_report_urls",
    "official_overall_undergraduate_employment_rate",
    "official_undergraduate_employment_rate",
    "official_initial_undergraduate_employment_rate",
    "official_undergraduate_destination_implementation_rate",
    "official_total_destination_implementation_rate",
    "official_further_study_rate",
    "official_undergraduate_further_study_rate",
    "official_overseas_study_rate",
    "official_flexible_employment_rate",
    "official_total_undergraduate_graduates",
    "official_employer_satisfaction_rate",
    "official_lowest_employment_like_rate",
    "official_highest_further_study_like_rate",
    "metric_extraction_qualities",
    "coverage_school_id",
    "province",
    "official_url",
    "has_official_recommendation_records",
    "official_recommendation_record_count",
    "coverage_note",
    "source_attempt_count",
    "ingested_attempt_count",
    "blocked_attempt_count",
    "source_attempt_blocker_types",
    "data_scope",
    "source_level",
]

SCHOOL_SUMMARY_FIELDS = [
    "school_profile_id",
    "school_name",
    "first_year",
    "latest_year",
    "years",
    "year_profile_count",
    "public_record_count",
    "as_destination_record_count",
    "as_undergraduate_source_record_count",
    "unique_public_record_count",
    "official_metric_count",
    "official_report_source_count",
    "official_year_count",
    "has_public_records",
    "has_official_metrics",
    "coverage_school_id",
    "province",
    "official_url",
    "has_official_recommendation_records",
    "official_recommendation_record_count",
    "coverage_note",
    "source_attempt_count",
    "ingested_attempt_count",
    "blocked_attempt_count",
    "source_attempt_blocker_types",
    "latest_official_undergraduate_employment_rate",
    "latest_official_further_study_rate",
    "sample_year_profile_ids",
    "data_scope",
    "source_level",
]

CANONICAL_METRICS = {
    "official_overall_undergraduate_employment_rate": [
        "overall_undergraduate_employment_rate",
    ],
    "official_undergraduate_employment_rate": [
        "undergraduate_employment_rate",
        "bachelor_employment_rate",
    ],
    "official_initial_undergraduate_employment_rate": [
        "initial_undergraduate_employment_rate",
        "initial_undergraduate_destination_implementation_rate",
        "initial_destination_implementation_rate",
    ],
    "official_undergraduate_destination_implementation_rate": [
        "undergraduate_destination_implementation_rate",
        "destination_implementation_rate",
    ],
    "official_total_destination_implementation_rate": [
        "total_destination_implementation_rate",
        "overall_destination_implementation_rate",
    ],
    "official_further_study_rate": [
        "further_study_rate",
        "overall_further_study_rate",
    ],
    "official_undergraduate_further_study_rate": [
        "undergraduate_further_study_rate",
        "undergraduate_further_study_rate_including_second_bachelor",
        "undergraduate_further_study_rate_qualitative",
    ],
    "official_overseas_study_rate": [
        "overseas_study_rate",
        "undergraduate_overseas_study_rate",
    ],
    "official_flexible_employment_rate": [
        "flexible_employment_rate",
    ],
    "official_total_undergraduate_graduates": [
        "total_undergraduate_graduates",
        "actual_undergraduate_graduates",
        "total_undergraduate_graduates_for_employment_statistics",
        "undergraduate_count",
        "bachelor_count",
    ],
    "official_employer_satisfaction_rate": [
        "employer_satisfaction_rate",
        "employer_overall_satisfaction_rate",
        "employer_very_satisfied_rate",
    ],
}


def build_graduate_outcome_school_year_profiles(
    *,
    public_records_csv: Path,
    official_metrics_csv: Path,
    official_report_sources_csv: Path,
    recommendation_coverage_csv: Path,
    source_attempts_csv: Path,
    output_profiles_csv: Path,
    output_school_summary_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    coverage_by_school = load_coverage(recommendation_coverage_csv)
    attempts_by_school = load_attempts(source_attempts_csv)
    groups: dict[tuple[str, str], dict[str, Any]] = {}

    public_row_count = 0
    destination_public_rows = 0
    undergraduate_source_public_rows = 0
    for row in read_csv_rows(public_records_csv):
        public_row_count += 1
        year = normalize_year_key(row.get("year"))
        destination_school = text(row.get("school_name"))
        undergraduate_school = text(row.get("undergraduate_school"))
        if destination_school and year:
            destination_public_rows += 1
            update_public_group(
                get_group(groups, destination_school, year),
                row,
                profile_role="destination",
            )
        if undergraduate_school and year:
            undergraduate_source_public_rows += 1
            update_public_group(
                get_group(groups, undergraduate_school, year),
                row,
                profile_role="undergraduate_source",
            )

    official_metric_row_count = 0
    for row in read_csv_rows(official_metrics_csv):
        school_name = text(row.get("school_name"))
        year = normalize_year_key(row.get("report_year_or_cohort"))
        if not school_name or not year:
            continue
        official_metric_row_count += 1
        update_metric_group(get_group(groups, school_name, year), row)

    official_report_source_row_count = 0
    for row in read_csv_rows(official_report_sources_csv):
        school_name = text(row.get("school_name"))
        year = normalize_year_key(row.get("report_year_or_cohort"))
        if not school_name or not year:
            continue
        official_report_source_row_count += 1
        update_report_source_group(get_group(groups, school_name, year), row)

    profile_rows = [
        build_profile_row(key, group, coverage_by_school, attempts_by_school)
        for key, group in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1]))
    ]
    write_csv(output_profiles_csv, profile_rows, PROFILE_FIELDS)

    school_summary_rows = build_school_summary_rows(profile_rows, coverage_by_school, attempts_by_school)
    write_csv(output_school_summary_csv, school_summary_rows, SCHOOL_SUMMARY_FIELDS)

    profile_with_public = [row for row in profile_rows if int(row["public_record_count"])]
    profile_with_metrics = [row for row in profile_rows if int(row["official_metric_count"])]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "public_records_csv": str(public_records_csv),
        "official_metrics_csv": str(official_metrics_csv),
        "official_report_sources_csv": str(official_report_sources_csv),
        "recommendation_coverage_csv": str(recommendation_coverage_csv),
        "source_attempts_csv": str(source_attempts_csv),
        "output_profiles_csv": str(output_profiles_csv),
        "output_school_summary_csv": str(output_school_summary_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "public_record_input_count": public_row_count,
        "destination_public_record_count": destination_public_rows,
        "undergraduate_source_public_record_count": undergraduate_source_public_rows,
        "official_metric_input_count": official_metric_row_count,
        "official_report_source_input_count": official_report_source_row_count,
        "school_year_profile_count": len(profile_rows),
        "school_summary_row_count": len(school_summary_rows),
        "profiles_with_public_records": len(profile_with_public),
        "profiles_with_official_metrics": len(profile_with_metrics),
        "coverage_school_count": len(coverage_by_school),
        "source_attempt_school_count": len(attempts_by_school),
        "source_type_counts": dict(sorted(count_source_types(profile_rows).items())),
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(output_report_md, manifest)
    return manifest


def get_group(groups: dict[tuple[str, str], dict[str, Any]], school_name: str, year: str) -> dict[str, Any]:
    key = (school_name, year)
    return groups.setdefault(
        key,
        {
            "school_name": school_name,
            "year": year,
            "source_types": set(),
            "source_datasets": set(),
            "routes": set(),
            "document_types": set(),
            "public_record_ids": set(),
            "destination_schools": set(),
            "undergraduate_source_schools": set(),
            "admission_majors": set(),
            "undergraduate_majors": set(),
            "source_urls": set(),
            "destination_record_count": 0,
            "undergraduate_source_record_count": 0,
            "needs_review_count": 0,
            "quality_scores": [],
            "low_quality_record_count": 0,
            "metrics": [],
            "report_sources": [],
        },
    )


def update_public_group(group: dict[str, Any], row: dict[str, str], *, profile_role: str) -> None:
    group["source_types"].add("public_record")
    add_if(group["source_datasets"], row.get("source_dataset"))
    add_if(group["routes"], row.get("route"))
    add_if(group["document_types"], row.get("document_type"))
    add_if(group["public_record_ids"], row.get("public_record_id"))
    add_if(group["source_urls"], row.get("source_url"))
    add_if(group["admission_majors"], row.get("admission_major") or row.get("major"))
    add_if(group["undergraduate_majors"], row.get("undergraduate_major"))
    if profile_role == "destination":
        group["destination_record_count"] += 1
        add_if(group["undergraduate_source_schools"], row.get("undergraduate_school"))
    elif profile_role == "undergraduate_source":
        group["undergraduate_source_record_count"] += 1
        add_if(group["destination_schools"], row.get("school_name"))
    else:
        raise ValueError(f"Unknown public profile role: {profile_role}")
    if text(row.get("needs_review")).lower() == "true":
        group["needs_review_count"] += 1
    score = to_float(row.get("quality_score"))
    if score is not None:
        group["quality_scores"].append(score)
        if score < 60:
            group["low_quality_record_count"] += 1


def update_metric_group(group: dict[str, Any], row: dict[str, str]) -> None:
    group["source_types"].add("official_report_metric")
    group["metrics"].append(
        {
            "metric_name": text(row.get("metric_name")),
            "metric_value": text(row.get("metric_value")),
            "metric_unit": text(row.get("metric_unit")),
            "scope": text(row.get("scope")),
            "source_url": text(row.get("source_url")),
            "evidence_note": text(row.get("evidence_note")),
            "extraction_quality": text(row.get("extraction_quality")),
        }
    )
    add_if(group["source_urls"], row.get("source_url"))


def update_report_source_group(group: dict[str, Any], row: dict[str, str]) -> None:
    group["source_types"].add("official_report_source")
    group["report_sources"].append(
        {
            "source_title": text(row.get("source_title")),
            "source_url": text(row.get("source_url")),
            "local_artifact": text(row.get("local_artifact")),
            "fetch_status": text(row.get("fetch_status")),
            "content_type": text(row.get("content_type")),
            "extraction_status": text(row.get("extraction_status")),
        }
    )
    add_if(group["source_urls"], row.get("source_url"))


def build_profile_row(
    key: tuple[str, str],
    group: dict[str, Any],
    coverage_by_school: dict[str, dict[str, str]],
    attempts_by_school: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    school_name, year = key
    quality_scores = group["quality_scores"]
    metrics = group["metrics"]
    report_sources = group["report_sources"]
    coverage = coverage_by_school.get(school_name, {})
    attempts = attempts_by_school.get(school_name, {})
    canonical_values = select_canonical_metric_values(metrics)
    return {
        "school_year_profile_id": school_year_profile_id(school_name, year),
        "school_name": school_name,
        "year": year,
        "source_types": join_sorted(group["source_types"]),
        "source_datasets": join_sorted(group["source_datasets"]),
        "routes": join_sorted(group["routes"]),
        "document_types": join_sorted(group["document_types"]),
        "public_record_count": group["destination_record_count"] + group["undergraduate_source_record_count"],
        "as_destination_record_count": group["destination_record_count"],
        "as_undergraduate_source_record_count": group["undergraduate_source_record_count"],
        "unique_public_record_count": len(group["public_record_ids"]),
        "destination_school_count": len(group["destination_schools"]),
        "undergraduate_source_school_count": len(group["undergraduate_source_schools"]),
        "admission_major_count": len(group["admission_majors"]),
        "undergraduate_major_count": len(group["undergraduate_majors"]),
        "source_document_count": len(group["source_urls"]),
        "needs_review_count": group["needs_review_count"],
        "avg_quality_score": round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else "",
        "low_quality_record_count": group["low_quality_record_count"],
        "sample_destination_schools": join_sample(group["destination_schools"]),
        "sample_undergraduate_source_schools": join_sample(group["undergraduate_source_schools"]),
        "sample_admission_majors": join_sample(group["admission_majors"]),
        "sample_undergraduate_majors": join_sample(group["undergraduate_majors"]),
        "sample_source_urls": join_sample(group["source_urls"], separator="|"),
        "official_metric_count": len(metrics),
        "official_report_source_count": len(report_sources),
        "official_metric_names": join_sorted({metric["metric_name"] for metric in metrics}),
        "official_report_titles": join_sample({source["source_title"] for source in report_sources}),
        "official_report_urls": join_sample({source["source_url"] for source in report_sources}, separator="|"),
        **canonical_values,
        "official_lowest_employment_like_rate": lowest_employment_like_rate(metrics),
        "official_highest_further_study_like_rate": highest_further_study_like_rate(metrics),
        "metric_extraction_qualities": join_sorted({metric["extraction_quality"] for metric in metrics}),
        **coverage_fields(coverage),
        **attempt_fields(attempts),
        "data_scope": "official_public_graduate_outcome_school_year_profile",
        "source_level": "A/B",
    }


def build_school_summary_rows(
    profile_rows: list[dict[str, Any]],
    coverage_by_school: dict[str, dict[str, str]],
    attempts_by_school: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in profile_rows:
        grouped[row["school_name"]].append(row)
    school_names = set(grouped) | set(coverage_by_school) | set(attempts_by_school)
    rows: list[dict[str, Any]] = []
    for school_name in sorted(school_names):
        profiles = sorted(grouped.get(school_name, []), key=lambda row: row["year"])
        years = [row["year"] for row in profiles if row["year"]]
        coverage = coverage_by_school.get(school_name, {})
        attempts = attempts_by_school.get(school_name, {})
        public_record_count = sum(to_int(row["public_record_count"]) for row in profiles)
        metric_count = sum(to_int(row["official_metric_count"]) for row in profiles)
        latest_profile = profiles[-1] if profiles else {}
        rows.append(
            {
                "school_profile_id": school_profile_id(school_name),
                "school_name": school_name,
                "first_year": years[0] if years else "",
                "latest_year": years[-1] if years else "",
                "years": "|".join(years),
                "year_profile_count": len(profiles),
                "public_record_count": public_record_count,
                "as_destination_record_count": sum(to_int(row["as_destination_record_count"]) for row in profiles),
                "as_undergraduate_source_record_count": sum(to_int(row["as_undergraduate_source_record_count"]) for row in profiles),
                "unique_public_record_count": sum(to_int(row["unique_public_record_count"]) for row in profiles),
                "official_metric_count": metric_count,
                "official_report_source_count": sum(to_int(row["official_report_source_count"]) for row in profiles),
                "official_year_count": sum(1 for row in profiles if to_int(row["official_metric_count"]) > 0),
                "has_public_records": bool_text(public_record_count > 0),
                "has_official_metrics": bool_text(metric_count > 0),
                **coverage_fields(coverage),
                **attempt_fields(attempts),
                "latest_official_undergraduate_employment_rate": first_text(
                    latest_profile.get("official_undergraduate_employment_rate"),
                    latest_profile.get("official_overall_undergraduate_employment_rate"),
                    latest_profile.get("official_initial_undergraduate_employment_rate"),
                    latest_profile.get("official_undergraduate_destination_implementation_rate"),
                ),
                "latest_official_further_study_rate": first_text(
                    latest_profile.get("official_undergraduate_further_study_rate"),
                    latest_profile.get("official_further_study_rate"),
                ),
                "sample_year_profile_ids": "|".join(row["school_year_profile_id"] for row in profiles[-5:]),
                "data_scope": "official_public_graduate_outcome_school_summary",
                "source_level": "A/B",
            }
        )
    return rows


def select_canonical_metric_values(metrics: list[dict[str, str]]) -> dict[str, str]:
    values: dict[str, str] = {}
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for metric in metrics:
        by_name[metric["metric_name"]].append(metric)
    for output_field, metric_names in CANONICAL_METRICS.items():
        selected = ""
        for metric_name in metric_names:
            for metric in by_name.get(metric_name, []):
                selected = metric_value_for_output(metric)
                if selected:
                    break
            if selected:
                break
        values[output_field] = selected
    return values


def lowest_employment_like_rate(metrics: list[dict[str, str]]) -> str:
    values = []
    for metric in metrics:
        name = metric["metric_name"]
        unit = metric["metric_unit"]
        if "satisfaction" in name:
            continue
        if unit.startswith("percent") and (
            "employment_rate" in name
            or "destination_implementation_rate" in name
            or name in {"employed_rate", "unit_employment_rate"}
        ):
            value = metric_numeric_value(metric)
            if value is not None:
                values.append(value)
    return format_number(min(values)) if values else ""


def highest_further_study_like_rate(metrics: list[dict[str, str]]) -> str:
    values = []
    for metric in metrics:
        name = metric["metric_name"]
        unit = metric["metric_unit"]
        if unit.startswith("percent") and (
            "further_study_rate" in name
            or "postgraduate_study_rate" in name
            or "overseas_study_rate" in name
        ):
            value = metric_numeric_value(metric)
            if value is not None:
                values.append(value)
    return format_number(max(values)) if values else ""


def metric_value_for_output(metric: dict[str, str]) -> str:
    value = metric_numeric_value(metric)
    return format_number(value) if value is not None else text(metric.get("metric_value"))


def metric_numeric_value(metric: dict[str, str]) -> float | None:
    return numeric_prefix(metric.get("metric_value"))


def load_coverage(path: Path) -> dict[str, dict[str, str]]:
    coverage: dict[str, dict[str, str]] = {}
    for row in read_csv_rows(path):
        school_name = text(row.get("school_name"))
        if school_name:
            coverage[school_name] = row
    return coverage


def load_attempts(path: Path) -> dict[str, dict[str, Any]]:
    attempts: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "source_attempt_count": 0,
            "ingested_attempt_count": 0,
            "blocked_attempt_count": 0,
            "source_attempt_blocker_types": set(),
        }
    )
    for row in read_csv_rows(path):
        school_name = text(row.get("school_name"))
        if not school_name:
            continue
        attempt = attempts[school_name]
        attempt["source_attempt_count"] += 1
        decision = text(row.get("decision")).lower()
        if decision == "ingested":
            attempt["ingested_attempt_count"] += 1
        elif decision:
            attempt["blocked_attempt_count"] += 1
        add_if(attempt["source_attempt_blocker_types"], row.get("blocker_type"))
    return dict(attempts)


def coverage_fields(coverage: dict[str, str]) -> dict[str, str]:
    return {
        "coverage_school_id": text(coverage.get("school_id")),
        "province": text(coverage.get("province")),
        "official_url": text(coverage.get("official_url")),
        "has_official_recommendation_records": lower_bool_text(coverage.get("has_official_recommendation_records")),
        "official_recommendation_record_count": text(coverage.get("official_recommendation_record_count")),
        "coverage_note": text(coverage.get("coverage_note")),
    }


def attempt_fields(attempts: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_attempt_count": attempts.get("source_attempt_count", 0),
        "ingested_attempt_count": attempts.get("ingested_attempt_count", 0),
        "blocked_attempt_count": attempts.get("blocked_attempt_count", 0),
        "source_attempt_blocker_types": join_sorted(attempts.get("source_attempt_blocker_types", set())),
    }


def write_report(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# Graduate Outcome School-Year Profile Report",
        "",
        f"- Public row-level input records: {manifest['public_record_input_count']}",
        f"- Destination-school public records: {manifest['destination_public_record_count']}",
        f"- Undergraduate-source public records: {manifest['undergraduate_source_public_record_count']}",
        f"- Official metric rows: {manifest['official_metric_input_count']}",
        f"- Official report source rows: {manifest['official_report_source_input_count']}",
        f"- School-year profiles: {manifest['school_year_profile_count']}",
        f"- School summary rows: {manifest['school_summary_row_count']}",
        f"- Profiles with public records: {manifest['profiles_with_public_records']}",
        f"- Profiles with official metrics: {manifest['profiles_with_official_metrics']}",
        "",
        "## Outputs",
        "",
        f"- School-year profiles: `{manifest['output_profiles_csv']}`",
        f"- School summary: `{manifest['output_school_summary_csv']}`",
        f"- Manifest: `{manifest['output_manifest_json']}`",
        "",
        "## Use Notes",
        "",
        "- Public record counts are counts of public, masked official-source rows.",
        "- `official_*` fields come from official employment or teaching-quality report metrics.",
        "- Do not interpret public list sample counts as true school-level employment or further-study rates.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def count_source_types(profile_rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in profile_rows:
        for source_type in text(row.get("source_types")).split("|"):
            if source_type:
                counts[source_type] += 1
    return counts


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


YEAR_RANGE_RE = re.compile(r"(20\d{2})\s*[-/]\s*(?:20)?(\d{2})")
YEAR_RE = re.compile(r"(20\d{2})")
NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")


def normalize_year_key(value: Any) -> str:
    raw = text(value)
    if not raw:
        return ""
    match = YEAR_RANGE_RE.search(raw)
    if match:
        start_year = int(match.group(1))
        end_part = match.group(2)
        end_year = int(f"{str(start_year)[:2]}{end_part}")
        if end_year < start_year:
            end_year += 100
        return str(end_year)
    match = YEAR_RE.search(raw)
    return match.group(1) if match else raw


def school_year_profile_id(school_name: str, year: str) -> str:
    return "graduate_school_year:" + hashlib.sha256(f"{school_name}|{year}".encode("utf-8")).hexdigest()[:24]


def school_profile_id(school_name: str) -> str:
    return "graduate_school:" + hashlib.sha256(school_name.encode("utf-8")).hexdigest()[:24]


def add_if(values: set[str], value: Any) -> None:
    value_text = text(value)
    if value_text:
        values.add(value_text)


def join_sorted(values: Any, *, separator: str = "|") -> str:
    return separator.join(sorted(text(value) for value in values if text(value)))


def join_sample(values: Any, *, limit: int = 8, separator: str = "; ") -> str:
    return separator.join(sorted(text(value) for value in values if text(value))[:limit])


def first_text(*values: Any) -> str:
    for value in values:
        value_text = text(value)
        if value_text:
            return value_text
    return ""


def to_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def to_float(value: Any) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def numeric_prefix(value: Any) -> float | None:
    match = NUMBER_RE.search(text(value))
    return float(match.group(0)) if match else None


def format_number(value: float | None) -> str:
    if value is None:
        return ""
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def lower_bool_text(value: Any) -> str:
    value_text = text(value)
    if not value_text:
        return ""
    if value_text.lower() in {"true", "1", "yes", "y"}:
        return "true"
    if value_text.lower() in {"false", "0", "no", "n"}:
        return "false"
    return value_text


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build school-year profiles from public graduate outcome assets."
    )
    parser.add_argument(
        "--public-records-csv",
        type=Path,
        default=Path("data/cleaned/graduate_outcomes/master_records_public.csv"),
    )
    parser.add_argument(
        "--official-metrics-csv",
        type=Path,
        default=Path("data/cleaned/graduate_outcomes/official_employment_report_metrics.csv"),
    )
    parser.add_argument(
        "--official-report-sources-csv",
        type=Path,
        default=Path("data/cleaned/graduate_outcomes/official_employment_report_sources.csv"),
    )
    parser.add_argument(
        "--recommendation-coverage-csv",
        type=Path,
        default=Path("data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv"),
    )
    parser.add_argument(
        "--source-attempts-csv",
        type=Path,
        default=Path("data/cleaned/graduate_outcomes/official_recommendation_source_attempts.csv"),
    )
    parser.add_argument(
        "--output-profiles-csv",
        type=Path,
        default=Path("data/processed/graduate_outcomes/graduate_outcome_school_year_profiles_20260604.csv"),
    )
    parser.add_argument(
        "--output-school-summary-csv",
        type=Path,
        default=Path("data/processed/graduate_outcomes/graduate_outcome_school_summary_20260604.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/graduate_outcomes/graduate_outcome_school_year_profiles_manifest_20260604.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/graduate_outcomes/school_year_profiles_20260604.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_graduate_outcome_school_year_profiles(
        public_records_csv=args.public_records_csv,
        official_metrics_csv=args.official_metrics_csv,
        official_report_sources_csv=args.official_report_sources_csv,
        recommendation_coverage_csv=args.recommendation_coverage_csv,
        source_attempts_csv=args.source_attempts_csv,
        output_profiles_csv=args.output_profiles_csv,
        output_school_summary_csv=args.output_school_summary_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
