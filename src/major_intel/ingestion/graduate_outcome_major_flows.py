"""Build major-level flow summaries from public graduate outcome records."""

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


SCHEMA_VERSION = "graduate_outcome_major_flows/v1"

FLOW_FIELDS = [
    "major_flow_id",
    "major_role",
    "major_name",
    "normalized_major_name",
    "reported_major_names",
    "first_year",
    "latest_year",
    "years",
    "source_datasets",
    "routes",
    "document_types",
    "record_count",
    "unique_public_record_count",
    "destination_school_count",
    "undergraduate_school_count",
    "source_document_count",
    "needs_review_count",
    "avg_quality_score",
    "low_quality_record_count",
    "sample_destination_schools",
    "sample_undergraduate_schools",
    "sample_source_urls",
    "employment_warning_count",
    "employment_risk_levels",
    "employment_warning_years",
    "employment_warning_record_ids",
    "has_employment_high_risk_warning",
    "has_employment_red_warning",
    "has_employment_yellow_warning",
    "has_employment_green_signal",
    "official_policy_warning_count",
    "official_policy_record_types",
    "official_policy_years",
    "official_policy_warning_ids",
    "has_official_policy_warning",
    "ai_replacement_match_count",
    "ai_replacement_rank",
    "ai_replacement_score",
    "ai_replacement_level",
    "ai_confidence_score",
    "ai_candidate_count",
    "source_level",
    "data_scope",
]

ROLE_SUMMARY_FIELDS = [
    "major_role",
    "major_count",
    "record_count",
    "employment_linked_major_count",
    "employment_high_risk_major_count",
    "official_policy_linked_major_count",
    "ai_linked_major_count",
    "avg_ai_replacement_score",
]


def build_graduate_outcome_major_flows(
    *,
    public_records_csv: Path,
    employment_warnings_csv: Path,
    official_policy_warnings_csv: Path,
    ai_replacement_csv: Path,
    output_flows_csv: Path,
    output_role_summary_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    employment_by_name = build_warning_name_index(load_employment_warning_refs(employment_warnings_csv))
    policy_by_name = build_warning_name_index(load_policy_warning_refs(official_policy_warnings_csv))
    ai_by_name = build_ai_name_index(load_ai_replacement_refs(ai_replacement_csv))

    groups: dict[tuple[str, str], dict[str, Any]] = {}
    public_row_count = 0
    rows_with_undergraduate_major = 0
    rows_with_admission_major = 0
    for row in read_csv_rows(public_records_csv):
        public_row_count += 1
        if text(row.get("undergraduate_major")):
            rows_with_undergraduate_major += 1
            update_group(groups, row, major_role="undergraduate_major", major_name=text(row.get("undergraduate_major")))
        if text(row.get("admission_major")):
            rows_with_admission_major += 1
            update_group(groups, row, major_role="admission_major", major_name=text(row.get("admission_major")))

    flow_rows = [
        build_flow_row(
            key,
            group,
            employment_by_name=employment_by_name,
            policy_by_name=policy_by_name,
            ai_by_name=ai_by_name,
        )
        for key, group in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1]))
    ]
    write_csv(output_flows_csv, flow_rows, FLOW_FIELDS)
    role_summary_rows = build_role_summary_rows(flow_rows)
    write_csv(output_role_summary_csv, role_summary_rows, ROLE_SUMMARY_FIELDS)

    linked_employment = [row for row in flow_rows if int(row["employment_warning_count"])]
    linked_high_risk = [row for row in flow_rows if row["has_employment_high_risk_warning"] == "true"]
    linked_policy = [row for row in flow_rows if int(row["official_policy_warning_count"])]
    linked_ai = [row for row in flow_rows if int(row["ai_replacement_match_count"])]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "public_records_csv": str(public_records_csv),
        "employment_warnings_csv": str(employment_warnings_csv),
        "official_policy_warnings_csv": str(official_policy_warnings_csv),
        "ai_replacement_csv": str(ai_replacement_csv),
        "output_flows_csv": str(output_flows_csv),
        "output_role_summary_csv": str(output_role_summary_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "public_record_count": public_row_count,
        "rows_with_undergraduate_major": rows_with_undergraduate_major,
        "rows_with_admission_major": rows_with_admission_major,
        "major_flow_count": len(flow_rows),
        "linked_employment_major_flow_count": len(linked_employment),
        "linked_high_risk_major_flow_count": len(linked_high_risk),
        "linked_policy_major_flow_count": len(linked_policy),
        "linked_ai_replacement_major_flow_count": len(linked_ai),
        "role_counts": dict(sorted(Counter(row["major_role"] for row in flow_rows).items())),
        "role_summary_row_count": len(role_summary_rows),
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(output_report_md, manifest, role_summary_rows)
    return manifest


def update_group(
    groups: dict[tuple[str, str], dict[str, Any]],
    row: dict[str, str],
    *,
    major_role: str,
    major_name: str,
) -> None:
    normalized_major_name = normalize_major_name(major_name)
    key = (major_role, normalized_major_name or major_name)
    group = groups.setdefault(
        key,
        {
            "major_role": major_role,
            "major_name": normalized_major_name or major_name,
            "normalized_major_name": normalized_major_name,
            "reported_major_names": set(),
            "years": set(),
            "source_datasets": set(),
            "routes": set(),
            "document_types": set(),
            "public_record_ids": set(),
            "destination_schools": set(),
            "undergraduate_schools": set(),
            "source_urls": set(),
            "record_count": 0,
            "needs_review_count": 0,
            "quality_scores": [],
            "low_quality_record_count": 0,
        },
    )
    group["record_count"] += 1
    add_if(group["reported_major_names"], major_name)
    add_if(group["years"], row.get("year"))
    add_if(group["source_datasets"], row.get("source_dataset"))
    add_if(group["routes"], row.get("route"))
    add_if(group["document_types"], row.get("document_type"))
    add_if(group["public_record_ids"], row.get("public_record_id"))
    add_if(group["destination_schools"], row.get("school_name"))
    add_if(group["undergraduate_schools"], row.get("undergraduate_school"))
    add_if(group["source_urls"], row.get("source_url"))
    if text(row.get("needs_review")).lower() == "true":
        group["needs_review_count"] += 1
    score = to_float(row.get("quality_score"))
    if score is not None:
        group["quality_scores"].append(score)
        if score < 60:
            group["low_quality_record_count"] += 1


def build_flow_row(
    key: tuple[str, str],
    group: dict[str, Any],
    *,
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
    ai_by_name: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    major_role, normalized_key_name = key
    normalized_major_name = group["normalized_major_name"] or normalized_key_name
    employment_refs = employment_by_name.get(normalized_major_name, [])
    policy_refs = policy_by_name.get(normalized_major_name, [])
    ai_refs = ai_by_name.get(normalized_major_name, [])
    best_ai = min(ai_refs, key=ai_sort_key) if ai_refs else None
    years = sorted(group["years"])
    quality_scores = group["quality_scores"]
    return {
        "major_flow_id": major_flow_id(major_role, normalized_major_name),
        "major_role": major_role,
        "major_name": group["major_name"],
        "normalized_major_name": normalized_major_name,
        "reported_major_names": "|".join(sorted(group["reported_major_names"])[:25]),
        "first_year": years[0] if years else "",
        "latest_year": years[-1] if years else "",
        "years": "|".join(years),
        "source_datasets": "|".join(sorted(group["source_datasets"])),
        "routes": "|".join(sorted(group["routes"])),
        "document_types": "|".join(sorted(group["document_types"])),
        "record_count": group["record_count"],
        "unique_public_record_count": len(group["public_record_ids"]),
        "destination_school_count": len(group["destination_schools"]),
        "undergraduate_school_count": len(group["undergraduate_schools"]),
        "source_document_count": len(group["source_urls"]),
        "needs_review_count": group["needs_review_count"],
        "avg_quality_score": round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else "",
        "low_quality_record_count": group["low_quality_record_count"],
        "sample_destination_schools": "、".join(sorted(group["destination_schools"])[:8]),
        "sample_undergraduate_schools": "、".join(sorted(group["undergraduate_schools"])[:8]),
        "sample_source_urls": "|".join(sorted(group["source_urls"])[:5]),
        **summarize_employment_refs(employment_refs),
        **summarize_policy_refs(policy_refs),
        **summarize_ai_refs(ai_refs, best_ai),
        "source_level": "A/B",
        "data_scope": "official_public_graduate_recommendation_or_admission_major_flow",
    }


def build_role_summary_rows(flow_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in flow_rows:
        grouped[row["major_role"]].append(row)
    rows: list[dict[str, Any]] = []
    for role, items in sorted(grouped.items()):
        ai_scores = [
            float(item["ai_replacement_score"])
            for item in items
            if text(item.get("ai_replacement_score"))
        ]
        rows.append(
            {
                "major_role": role,
                "major_count": len(items),
                "record_count": sum(int(item["record_count"]) for item in items),
                "employment_linked_major_count": count_positive(items, "employment_warning_count"),
                "employment_high_risk_major_count": count_true(items, "has_employment_high_risk_warning"),
                "official_policy_linked_major_count": count_positive(items, "official_policy_warning_count"),
                "ai_linked_major_count": count_positive(items, "ai_replacement_match_count"),
                "avg_ai_replacement_score": round(sum(ai_scores) / len(ai_scores), 2) if ai_scores else "",
            }
        )
    return rows


def load_employment_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        refs.append(
            {
                "id": text(row.get("record_id")),
                "major_name": major_name_from_warning(row),
                "year": text(row.get("report_year")),
                "risk_level": text(row.get("risk_level")),
            }
        )
    return refs


def load_policy_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        refs.append(
            {
                "id": text(row.get("warning_id")),
                "major_name": major_name_from_warning(row),
                "year": text(row.get("policy_year")),
                "record_type": text(row.get("record_type")),
            }
        )
    return refs


def load_ai_replacement_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        refs.append(
            {
                "major_name": text(row.get("major_name")),
                "rank": text(row.get("rank")),
                "score": text(row.get("ai_replacement_score")),
                "level": text(row.get("ai_replacement_level")),
                "confidence_score": text(row.get("confidence_score")),
                "candidate_count": text(row.get("candidate_count")),
            }
        )
    return refs


def build_warning_name_index(refs: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    by_name: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for ref in refs:
        if ref["major_name"]:
            by_name[ref["major_name"]][ref["id"]] = ref
    return {
        name: sorted(items.values(), key=lambda item: (item.get("year", ""), item.get("id", "")))
        for name, items in by_name.items()
    }


def build_ai_name_index(refs: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for ref in refs:
        if ref["major_name"]:
            by_name[ref["major_name"]].append(ref)
    return {name: sorted(items, key=ai_sort_key) for name, items in by_name.items()}


def summarize_employment_refs(refs: list[dict[str, str]]) -> dict[str, Any]:
    risk_levels = ordered_unique([ref["risk_level"] for ref in refs], order=["red", "yellow", "green"])
    has_red = "red" in risk_levels
    has_yellow = "yellow" in risk_levels
    has_green = "green" in risk_levels
    return {
        "employment_warning_count": len(refs),
        "employment_risk_levels": "|".join(risk_levels),
        "employment_warning_years": "|".join(ordered_unique([ref["year"] for ref in refs])),
        "employment_warning_record_ids": "|".join(ordered_unique([ref["id"] for ref in refs])),
        "has_employment_high_risk_warning": bool_text(has_red or has_yellow),
        "has_employment_red_warning": bool_text(has_red),
        "has_employment_yellow_warning": bool_text(has_yellow),
        "has_employment_green_signal": bool_text(has_green),
    }


def summarize_policy_refs(refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "official_policy_warning_count": len(refs),
        "official_policy_record_types": "|".join(ordered_unique([ref["record_type"] for ref in refs])),
        "official_policy_years": "|".join(ordered_unique([ref["year"] for ref in refs])),
        "official_policy_warning_ids": "|".join(ordered_unique([ref["id"] for ref in refs])),
        "has_official_policy_warning": bool_text(bool(refs)),
    }


def summarize_ai_refs(refs: list[dict[str, str]], best_ai: dict[str, str] | None) -> dict[str, Any]:
    return {
        "ai_replacement_match_count": len(refs),
        "ai_replacement_rank": text(best_ai.get("rank") if best_ai else ""),
        "ai_replacement_score": text(best_ai.get("score") if best_ai else ""),
        "ai_replacement_level": text(best_ai.get("level") if best_ai else ""),
        "ai_confidence_score": text(best_ai.get("confidence_score") if best_ai else ""),
        "ai_candidate_count": text(best_ai.get("candidate_count") if best_ai else ""),
    }


def write_report(
    path: Path,
    manifest: dict[str, Any],
    role_summary_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Graduate Outcome Major Flow Risk-Link Report",
        "",
        f"- Public row-level input records: {manifest['public_record_count']}",
        f"- Rows with undergraduate major: {manifest['rows_with_undergraduate_major']}",
        f"- Rows with admission major: {manifest['rows_with_admission_major']}",
        f"- Major flow rows: {manifest['major_flow_count']}",
        f"- Employment-warning linked major flows: {manifest['linked_employment_major_flow_count']}",
        f"- Red/yellow linked major flows: {manifest['linked_high_risk_major_flow_count']}",
        f"- Official-policy linked major flows: {manifest['linked_policy_major_flow_count']}",
        f"- AI replacement-risk linked major flows: {manifest['linked_ai_replacement_major_flow_count']}",
        "",
        "## Role Summary",
        "",
        "| Role | Majors | Records | Red/yellow linked | Policy linked | AI linked | Avg AI score |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in role_summary_rows:
        lines.append(
            "| {major_role} | {major_count} | {record_count} | "
            "{employment_high_risk_major_count} | {official_policy_linked_major_count} | "
            "{ai_linked_major_count} | {avg_ai_replacement_score} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Major flows: `{manifest['output_flows_csv']}`",
            f"- Role summary: `{manifest['output_role_summary_csv']}`",
            f"- Manifest: `{manifest['output_manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- `undergraduate_major` means the source student's undergraduate major when the official row exposes it.",
            "- `admission_major` means the destination admitted/recommended postgraduate major or programme name.",
            "- Counts are public, masked official-source row counts; they are not employment rates and must not be used as per-major employment-quality conclusions.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def major_name_from_warning(row: dict[str, str]) -> str:
    return text(row.get("standard_major_name")) or text(row.get("reported_major_name"))


def major_flow_id(role: str, major_name: str) -> str:
    return "graduate_flow:" + hashlib.sha256(f"{role}|{major_name}".encode("utf-8")).hexdigest()[:24]


LEADING_MAJOR_CODE_RE = re.compile(r"^[（(]?\s*\d{4,6}[A-Z]{0,2}\s*[）)]?\s*")


def normalize_major_name(value: str) -> str:
    name = text(value)
    if not name:
        return ""
    stripped = LEADING_MAJOR_CODE_RE.sub("", name).strip()
    return stripped or name


def ai_sort_key(ref: dict[str, str]) -> tuple[int, str]:
    return (to_int(ref.get("rank"), default=10**9), ref.get("major_name", ""))


def ordered_unique(values: list[str], *, order: list[str] | None = None) -> list[str]:
    seen = {value for value in values if value}
    if order:
        return [value for value in order if value in seen] + sorted(seen - set(order))
    return sorted(seen)


def count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if text(row.get(field)) == "true")


def count_positive(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if to_int(row.get(field), default=0) > 0)


def add_if(values: set[str], value: Any) -> None:
    value_text = text(value)
    if value_text:
        values.add(value_text)


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


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build major-level flow summaries from public graduate outcome records."
    )
    parser.add_argument(
        "--public-records-csv",
        type=Path,
        default=Path("data/cleaned/graduate_outcomes/master_records_public.csv"),
    )
    parser.add_argument(
        "--employment-warnings-csv",
        type=Path,
        default=Path("data/processed/major_risk_warnings/major_risk_warning_records.csv"),
    )
    parser.add_argument(
        "--official-policy-warnings-csv",
        type=Path,
        default=Path("data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv"),
    )
    parser.add_argument(
        "--ai-replacement-csv",
        type=Path,
        default=Path("data/processed/ai_replacement/major_ai_replacement_ranking.csv"),
    )
    parser.add_argument(
        "--output-flows-csv",
        type=Path,
        default=Path("data/processed/graduate_outcomes/major_outcome_flow_summary_20260604.csv"),
    )
    parser.add_argument(
        "--output-role-summary-csv",
        type=Path,
        default=Path("data/processed/graduate_outcomes/major_outcome_flow_role_summary_20260604.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/graduate_outcomes/major_outcome_flows_manifest_20260604.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/graduate_outcomes/major_outcome_flows_20260604.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_graduate_outcome_major_flows(
        public_records_csv=args.public_records_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        ai_replacement_csv=args.ai_replacement_csv,
        output_flows_csv=args.output_flows_csv,
        output_role_summary_csv=args.output_role_summary_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
