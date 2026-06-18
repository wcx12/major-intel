"""Build analyst-facing review shortlists and source document indexes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/major_risk_review_release"
DEFAULT_REPORT_DIR = ROOT / "reports/major_risk_review_release"
DEFAULT_SOURCE_ARCHIVE_CSV = (
    ROOT / "data/processed/major_risk_source_archive/major_risk_review_source_archive_2026.csv"
)
SCHEMA_VERSION = "major_risk_review_release/v1"

LOCAL_PROFILE_SOURCE_PATHS = {
    "civil_service_major_opportunities_2026.csv": (
        "data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv"
    ),
    "major_ai_replacement_ranking.csv": (
        "data/processed/ai_replacement/major_ai_replacement_ranking.csv"
    ),
    "new_quality_major_profiles_2026.csv": (
        "data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv"
    ),
    "vocational_major_risk_link_summary_2013_2026.csv": (
        "data/processed/vocational_major_register/vocational_major_risk_link_summary_2013_2026.csv"
    ),
}

SHORTLIST_FIELDS = [
    "review_rank",
    "review_tier",
    "review_priority_score",
    "major_master_id",
    "major_code",
    "major_name",
    "major_level",
    "category",
    "subject",
    "overall_review_bucket",
    "risk_signal_count",
    "opportunity_signal_count",
    "primary_risk_reasons",
    "primary_opportunity_reasons",
    "evidence_record_count",
    "risk_evidence_count",
    "opportunity_evidence_count",
    "source_url_count",
    "source_title_sample",
    "source_url_sample",
    "employment_warning_count",
    "employment_red_count",
    "employment_yellow_count",
    "employment_latest_risk_level",
    "employment_latest_report_year",
    "official_policy_warning_count",
    "official_policy_record_types",
    "official_policy_years",
    "ai_replacement_score",
    "ai_replacement_level",
    "market_demand_signal_level",
    "market_salary_signal_level",
    "market_activity_signal_level",
    "civil_service_opportunity_level",
    "new_quality_support_category",
    "is_new_quality_productivity_major",
    "source_presence_flags",
    "source_level_mix",
    "needs_review",
    "review_notes",
    "recommended_review_action",
]

SOURCE_DOCUMENT_FIELDS = [
    "source_document_id",
    "source_kind",
    "source_url",
    "source_title",
    "source_publisher",
    "source_path",
    "source_path_count",
    "existing_source_path_count",
    "missing_source_path_count",
    "source_path_status",
    "source_ids",
    "source_level_mix",
    "evidence_families",
    "signal_directions",
    "source_tables",
    "evidence_record_count",
    "major_count",
    "high_risk_major_count",
    "risk_evidence_count",
    "opportunity_evidence_count",
    "mixed_evidence_count",
    "reference_evidence_count",
    "sample_majors",
    "sample_evidence_text",
]

SUMMARY_FIELDS = [
    "summary_id",
    "group_type",
    "group_value",
    "row_count",
    "tier_1_count",
    "tier_2_count",
    "tier_3_count",
    "tier_4_count",
    "tier_5_count",
    "avg_review_priority_score",
    "avg_evidence_record_count",
    "source_url_count_sum",
]


def build_major_risk_review_release(
    *,
    master_index_csv: Path = ROOT
    / "data/processed/major_risk_master_index/major_risk_master_index_2026.csv",
    evidence_major_summary_csv: Path = ROOT
    / "data/processed/major_risk_evidence_profiles/major_risk_evidence_major_summary_2026.csv",
    evidence_records_csv: Path = ROOT
    / "data/processed/major_risk_evidence_profiles/major_risk_evidence_records_2026.csv",
    source_archive_csv: Path | None = DEFAULT_SOURCE_ARCHIVE_CSV,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or date.today().isoformat()
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    master_rows = list(read_csv_rows(master_index_csv))
    evidence_summaries = {
        row["major_master_id"]: row for row in read_csv_rows(evidence_major_summary_csv)
    }
    evidence_rows = list(read_csv_rows(evidence_records_csv))
    source_archive_paths = load_source_archive_paths(source_archive_csv)

    shortlist_rows = build_shortlist_rows(master_rows, evidence_summaries)
    source_document_rows = build_source_document_rows(evidence_rows, source_archive_paths)
    summary_rows = build_summary_rows(shortlist_rows)

    shortlist_csv = output_dir / "major_risk_high_risk_shortlist_2026.csv"
    source_index_csv = output_dir / "major_risk_source_document_index_2026.csv"
    summary_csv = output_dir / "major_risk_review_release_summary_2026.csv"
    manifest_json = output_dir / "major_risk_review_release_manifest_2026.json"
    report_md = report_dir / "major_risk_review_release_2026.md"

    write_csv(shortlist_csv, shortlist_rows, SHORTLIST_FIELDS)
    write_csv(source_index_csv, source_document_rows, SOURCE_DOCUMENT_FIELDS)
    write_csv(summary_csv, summary_rows, SUMMARY_FIELDS)

    manifest = {
        "dataset": "major_risk_review_release",
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "generated_at": generated_at,
        "inputs": {
            "master_index_csv": path_key(master_index_csv),
            "evidence_major_summary_csv": path_key(evidence_major_summary_csv),
            "evidence_records_csv": path_key(evidence_records_csv),
            "source_archive_csv": path_key(source_archive_csv) if source_archive_csv else "",
        },
        "outputs": {
            "shortlist_csv": path_key(shortlist_csv),
            "source_index_csv": path_key(source_index_csv),
            "summary_csv": path_key(summary_csv),
            "manifest_json": path_key(manifest_json),
            "report_md": path_key(report_md),
        },
        "row_counts": {
            "shortlist": len(shortlist_rows),
            "source_document_index": len(source_document_rows),
            "summary": len(summary_rows),
        },
        "shortlist_tier_counts": dict(
            sorted(Counter(row["review_tier"] for row in shortlist_rows).items())
        ),
        "source_kind_counts": dict(
            sorted(Counter(row["source_kind"] for row in source_document_rows).items())
        ),
        "source_path_status_counts": dict(
            sorted(Counter(row["source_path_status"] for row in source_document_rows).items())
        ),
        "source_archive": {
            "url_count": len(source_archive_paths),
            "path_count": sum(len(paths) for paths in source_archive_paths.values()),
        },
        "checksums": {
            path_key(shortlist_csv): file_info(shortlist_csv),
            path_key(source_index_csv): file_info(source_index_csv),
            path_key(summary_csv): file_info(summary_csv),
        },
    }
    manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest["checksums"][path_key(manifest_json)] = file_info(manifest_json)
    manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(report_md, manifest, shortlist_rows, source_document_rows, summary_rows)
    return manifest


def build_shortlist_rows(
    master_rows: list[dict[str, str]],
    evidence_summaries: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in master_rows:
        if to_int(row.get("risk_signal_count")) <= 0:
            continue
        summary = evidence_summaries.get(row["major_master_id"], {})
        score = review_priority_score(row, summary)
        tier = review_tier(row)
        rows.append(
            {
                "review_rank": 0,
                "review_tier": tier,
                "review_priority_score": number_text(score),
                "major_master_id": row.get("major_master_id", ""),
                "major_code": row.get("major_code", ""),
                "major_name": row.get("major_name", ""),
                "major_level": row.get("major_level", ""),
                "category": row.get("category", ""),
                "subject": row.get("subject", ""),
                "overall_review_bucket": row.get("overall_review_bucket", ""),
                "risk_signal_count": row.get("risk_signal_count", ""),
                "opportunity_signal_count": row.get("opportunity_signal_count", ""),
                "primary_risk_reasons": row.get("primary_risk_reasons", ""),
                "primary_opportunity_reasons": row.get("primary_opportunity_reasons", ""),
                "evidence_record_count": summary.get("evidence_record_count", ""),
                "risk_evidence_count": summary.get("risk_evidence_count", ""),
                "opportunity_evidence_count": summary.get("opportunity_evidence_count", ""),
                "source_url_count": summary.get("source_url_count", ""),
                "source_title_sample": summary.get("source_title_sample", ""),
                "source_url_sample": summary.get("source_url_sample", ""),
                "employment_warning_count": row.get("employment_warning_count", ""),
                "employment_red_count": row.get("employment_red_count", ""),
                "employment_yellow_count": row.get("employment_yellow_count", ""),
                "employment_latest_risk_level": row.get("employment_latest_risk_level", ""),
                "employment_latest_report_year": row.get("employment_latest_report_year", ""),
                "official_policy_warning_count": row.get("official_policy_warning_count", ""),
                "official_policy_record_types": row.get("official_policy_record_types", ""),
                "official_policy_years": row.get("official_policy_years", ""),
                "ai_replacement_score": row.get("ai_replacement_score", ""),
                "ai_replacement_level": row.get("ai_replacement_level", ""),
                "market_demand_signal_level": row.get("market_demand_signal_level", ""),
                "market_salary_signal_level": row.get("market_salary_signal_level", ""),
                "market_activity_signal_level": row.get("market_activity_signal_level", ""),
                "civil_service_opportunity_level": row.get("civil_service_opportunity_level", ""),
                "new_quality_support_category": row.get("new_quality_support_category", ""),
                "is_new_quality_productivity_major": row.get("is_new_quality_productivity_major", ""),
                "source_presence_flags": row.get("source_presence_flags", ""),
                "source_level_mix": row.get("source_level_mix", ""),
                "needs_review": row.get("needs_review", ""),
                "review_notes": row.get("review_notes", ""),
                "recommended_review_action": recommended_review_action(row, summary),
            }
        )
    rows.sort(key=shortlist_sort_key)
    for index, row in enumerate(rows, start=1):
        row["review_rank"] = index
    return rows


def build_source_document_rows(
    evidence_rows: list[dict[str, str]],
    source_archive_paths: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    source_archive_paths = source_archive_paths or {}
    docs: dict[str, dict[str, Any]] = {}
    for row in evidence_rows:
        for doc in document_refs_for(row):
            key = source_document_key(doc)
            item = docs.setdefault(
                key,
                {
                    "source_kind": doc["source_kind"],
                    "source_url": doc["source_url"],
                    "source_title": doc["source_title"],
                    "source_publisher": doc["source_publisher"],
                    "source_paths": set(),
                    "source_ids": set(),
                    "source_level_mix": set(),
                    "evidence_families": set(),
                    "signal_directions": set(),
                    "source_tables": set(),
                    "evidence_record_count": 0,
                    "majors": set(),
                    "high_risk_majors": set(),
                    "risk_evidence_count": 0,
                    "opportunity_evidence_count": 0,
                    "mixed_evidence_count": 0,
                    "reference_evidence_count": 0,
                    "sample_majors": set(),
                    "sample_evidence": set(),
                },
            )
            item["evidence_record_count"] += 1
            item["source_paths"].update(split_values(doc.get("source_path")))
            item["source_ids"].update(split_values(row.get("source_ids")))
            item["source_level_mix"].update(split_values(row.get("source_level")))
            item["evidence_families"].add(row.get("evidence_family", ""))
            item["signal_directions"].add(row.get("signal_direction", ""))
            item["source_tables"].add(row.get("source_table", ""))
            major_id = row.get("major_master_id", "")
            if major_id:
                item["majors"].add(major_id)
                if row.get("overall_review_bucket") == "high_risk_review":
                    item["high_risk_majors"].add(major_id)
            direction = row.get("signal_direction")
            if direction == "risk":
                item["risk_evidence_count"] += 1
            elif direction == "opportunity":
                item["opportunity_evidence_count"] += 1
            elif direction == "mixed":
                item["mixed_evidence_count"] += 1
            elif direction == "reference":
                item["reference_evidence_count"] += 1
            major_label = join_nonempty([row.get("major_code"), row.get("major_name"), row.get("major_level")], sep=" ")
            if major_label:
                item["sample_majors"].add(major_label)
            if row.get("evidence_text"):
                item["sample_evidence"].add(row.get("evidence_text", ""))

    rows: list[dict[str, Any]] = []
    for item in docs.values():
        if item["source_kind"] == "url":
            item["source_paths"].update(source_archive_paths.get(item["source_url"], []))
        source_paths = sorted(item["source_paths"])
        existing_path_count = sum(1 for path in source_paths if local_path_exists(path))
        missing_path_count = len(source_paths) - existing_path_count
        rows.append(
            {
                "source_document_id": stable_id(
                    "risk_source_doc",
                    item["source_kind"],
                    item["source_url"],
                    "|".join(source_paths),
                    item["source_title"],
                ),
                "source_kind": item["source_kind"],
                "source_url": item["source_url"],
                "source_title": item["source_title"],
                "source_publisher": item["source_publisher"],
                "source_path": "|".join(source_paths),
                "source_path_count": len(source_paths),
                "existing_source_path_count": existing_path_count,
                "missing_source_path_count": missing_path_count,
                "source_path_status": source_path_status(len(source_paths), existing_path_count),
                "source_ids": join_sorted(item["source_ids"]),
                "source_level_mix": join_sorted(item["source_level_mix"]),
                "evidence_families": join_sorted(item["evidence_families"]),
                "signal_directions": join_sorted(item["signal_directions"]),
                "source_tables": join_sorted(item["source_tables"]),
                "evidence_record_count": item["evidence_record_count"],
                "major_count": len(item["majors"]),
                "high_risk_major_count": len(item["high_risk_majors"]),
                "risk_evidence_count": item["risk_evidence_count"],
                "opportunity_evidence_count": item["opportunity_evidence_count"],
                "mixed_evidence_count": item["mixed_evidence_count"],
                "reference_evidence_count": item["reference_evidence_count"],
                "sample_majors": join_sample(item["sample_majors"], limit=10),
                "sample_evidence_text": join_sample(item["sample_evidence"], limit=3),
            }
        )
    return sorted(rows, key=source_document_sort_key)


def build_summary_rows(shortlist_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in shortlist_rows:
        add_group(groups, "all", "all", row)
        for field, group_type in [
            ("review_tier", "review_tier"),
            ("overall_review_bucket", "overall_review_bucket"),
            ("major_level", "major_level"),
            ("category", "category"),
            ("risk_signal_count", "risk_signal_count"),
        ]:
            add_group(groups, group_type, row.get(field, "") or "<blank>", row)
    result = []
    for (group_type, group_value), rows in sorted(groups.items()):
        result.append(
            {
                "summary_id": stable_id("risk_review_summary", group_type, group_value),
                "group_type": group_type,
                "group_value": group_value,
                "row_count": len(rows),
                "tier_1_count": count_tier(rows, "tier_1_high_risk_review"),
                "tier_2_count": count_tier(rows, "tier_2_employment_or_policy_warning"),
                "tier_3_count": count_tier(rows, "tier_3_ai_or_multi_signal_risk"),
                "tier_4_count": count_tier(rows, "tier_4_opportunity_with_risk_flags"),
                "tier_5_count": count_tier(rows, "tier_5_single_signal_watch"),
                "avg_review_priority_score": mean_text(
                    [to_float(row.get("review_priority_score")) for row in rows]
                ),
                "avg_evidence_record_count": mean_text(
                    [to_float(row.get("evidence_record_count")) for row in rows]
                ),
                "source_url_count_sum": sum(to_int(row.get("source_url_count")) for row in rows),
            }
        )
    return result


def review_tier(row: dict[str, str]) -> str:
    bucket = row.get("overall_review_bucket", "")
    if bucket == "high_risk_review":
        return "tier_1_high_risk_review"
    if bucket == "employment_or_policy_warning_review":
        return "tier_2_employment_or_policy_warning"
    if bucket in {"ai_market_risk_review", "multi_signal_risk_review"}:
        return "tier_3_ai_or_multi_signal_risk"
    if bucket == "opportunity_with_risk_flags":
        return "tier_4_opportunity_with_risk_flags"
    return "tier_5_single_signal_watch"


def review_priority_score(row: dict[str, str], summary: dict[str, str]) -> float:
    bucket_points = {
        "high_risk_review": 40,
        "employment_or_policy_warning_review": 32,
        "ai_market_risk_review": 28,
        "multi_signal_risk_review": 26,
        "opportunity_with_risk_flags": 20,
        "single_signal_watch": 12,
    }
    score = float(bucket_points.get(row.get("overall_review_bucket", ""), 0))
    score += min(to_int(row.get("risk_signal_count")) * 6, 30)
    score += min(to_int(row.get("official_policy_warning_count")), 20) * 0.8
    score += min(to_int(row.get("employment_red_count")) * 4, 16)
    score += min(to_int(row.get("employment_yellow_count")) * 2, 12)
    if ai_high(row):
        score += 8
    if market_limited(row):
        score += 5
    if civil_limited(row):
        score += 4
    score += min(to_int(summary.get("risk_evidence_count")), 30) * 0.25
    score += min(to_int(summary.get("source_url_count")), 25) * 0.15
    if row.get("needs_review") == "true":
        score += 1
    return round(score, 2)


def recommended_review_action(row: dict[str, str], summary: dict[str, str]) -> str:
    actions = []
    if to_int(row.get("official_policy_warning_count")):
        actions.append("verify_official_policy_rows")
    if to_int(row.get("employment_red_count")) or to_int(row.get("employment_yellow_count")):
        actions.append("compare_employment_warning_years")
    if ai_high(row):
        actions.append("inspect_ai_replacement_evidence")
    if market_limited(row):
        actions.append("check_market_demand_and_salary")
    if civil_limited(row):
        actions.append("check_public_exam_opportunity_limits")
    if row.get("needs_review") == "true":
        actions.append("resolve_major_code_or_name_review_note")
    if not actions and to_int(summary.get("risk_evidence_count")):
        actions.append("inspect_evidence_records")
    return "|".join(actions)


def document_refs_for(row: dict[str, str]) -> list[dict[str, str]]:
    urls = split_values(row.get("source_urls"))
    titles = split_values(row.get("source_titles"))
    publishers = split_values(row.get("source_publishers"))
    paths = split_values(row.get("source_paths"))
    refs = []
    if urls:
        has_one_to_one_paths = len(paths) == len(urls)
        source_path = "|".join(paths) if len(urls) == 1 else ""
        for index, url in enumerate(urls):
            refs.append(
                {
                    "source_kind": "url",
                    "source_url": url,
                    "source_title": value_at(titles, index) or value_at(titles, 0),
                    "source_publisher": value_at(publishers, index) or value_at(publishers, 0),
                    "source_path": value_at(paths, index) if has_one_to_one_paths else source_path,
                }
            )
        if len(urls) > 1 and not has_one_to_one_paths:
            refs.extend(local_path_refs(paths, titles, publishers))
        return refs
    if paths:
        return local_path_refs(paths, titles, publishers)
    return [
        {
            "source_kind": "local_profile",
            "source_url": "",
            "source_title": row.get("source_table", ""),
            "source_publisher": row.get("evidence_family", ""),
            "source_path": local_profile_source_path(row.get("source_table", "")),
        }
    ]


def local_path_refs(
    paths: list[str],
    titles: list[str],
    publishers: list[str],
) -> list[dict[str, str]]:
    refs = []
    for index, path in enumerate(paths):
        refs.append(
            {
                "source_kind": "local_path",
                "source_url": "",
                "source_title": value_at(titles, index) or value_at(titles, 0),
                "source_publisher": value_at(publishers, index) or value_at(publishers, 0),
                "source_path": path,
            }
        )
    return refs


def source_document_key(doc: dict[str, str]) -> str:
    if doc["source_kind"] == "url":
        return "|".join([doc["source_kind"], doc["source_url"], doc["source_title"]])
    return "|".join([doc["source_kind"], doc["source_path"], doc["source_title"]])


def local_profile_source_path(source_table: str) -> str:
    value = text(source_table)
    return LOCAL_PROFILE_SOURCE_PATHS.get(value, value)


def local_path_exists(path: str) -> bool:
    path_text = text(path)
    if not path_text:
        return False
    return (ROOT / Path(path_text.replace("\\", "/"))).exists()


def source_path_status(path_count: int, existing_count: int) -> str:
    if path_count == 0:
        return "no_local_path"
    if existing_count == path_count:
        return "all_paths_available"
    if existing_count:
        return "partial_paths_available"
    return "all_paths_missing"


def write_report(
    path: Path,
    manifest: dict[str, Any],
    shortlist_rows: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
) -> None:
    top_rows = shortlist_rows[:30]
    source_kind_counts = Counter(row["source_kind"] for row in source_rows)
    source_path_status_counts = Counter(row["source_path_status"] for row in source_rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Major Risk Review Release",
        "",
        f"- Built at: {manifest['generated_at']}",
        f"- High-risk / risk-watch shortlist rows: {manifest['row_counts']['shortlist']}",
        f"- Unified source-document index rows: {manifest['row_counts']['source_document_index']}",
        f"- Summary rows: {manifest['row_counts']['summary']}",
        "",
        "## Shortlist Tiers",
        "",
        "| tier | rows |",
        "|---|---:|",
    ]
    for tier, count in sorted(Counter(row["review_tier"] for row in shortlist_rows).items()):
        lines.append(f"| {tier} | {count} |")
    lines.extend(["", "## Source Kinds", "", "| kind | rows |", "|---|---:|"])
    for kind, count in sorted(source_kind_counts.items()):
        lines.append(f"| {kind} | {count} |")
    lines.extend(["", "## Source Path Status", "", "| status | rows |", "|---|---:|"])
    for status, count in sorted(source_path_status_counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(
        [
            "",
            "## Top Review Rows",
            "",
            "| rank | major | code | level | tier | score | risk reasons | evidence | urls |",
            "|---:|---|---|---|---|---:|---|---:|---:|",
        ]
    )
    for row in top_rows:
        lines.append(
            "| {review_rank} | {major_name} | {major_code} | {major_level} | {review_tier} | "
            "{review_priority_score} | {primary_risk_reasons} | {evidence_record_count} | "
            "{source_url_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Shortlist: `{manifest['outputs']['shortlist_csv']}`",
            f"- Source-document index: `{manifest['outputs']['source_index_csv']}`",
            f"- Summary: `{manifest['outputs']['summary_csv']}`",
            f"- Manifest: `{manifest['outputs']['manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- The shortlist includes every major with at least one risk signal from the master index.",
            "- `review_priority_score` is a transparent triage score for sorting review work, not a statistical probability.",
            "- The source-document index includes public URLs when available, raw/text local paths when available, and a local-profile placeholder for derived profile tables.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def shortlist_sort_key(row: dict[str, Any]) -> tuple[float, str, str]:
    return (-to_float(row.get("review_priority_score"), default=0), row.get("major_level", ""), row.get("major_code", ""))


def source_document_sort_key(row: dict[str, Any]) -> tuple[int, str, str]:
    return (-to_int(row.get("evidence_record_count")), row.get("source_kind", ""), row.get("source_url", "") or row.get("source_path", ""))


def add_group(groups: dict[tuple[str, str], list[dict[str, Any]]], group_type: str, group_value: str, row: dict[str, Any]) -> None:
    groups.setdefault((group_type, group_value), []).append(row)


def count_tier(rows: list[dict[str, Any]], tier: str) -> int:
    return sum(1 for row in rows if row.get("review_tier") == tier)


def ai_high(row: dict[str, str]) -> bool:
    score = to_float(row.get("ai_replacement_score"))
    return row.get("ai_replacement_level") in {"\u8f83\u9ad8", "\u9ad8", "\u5f88\u9ad8", "high", "very_high"} or (
        score is not None and score >= 60
    )


def market_limited(row: dict[str, str]) -> bool:
    return "limited" in {
        text(row.get("market_demand_signal_level")).lower(),
        text(row.get("market_salary_signal_level")).lower(),
        text(row.get("market_activity_signal_level")).lower(),
    }


def civil_limited(row: dict[str, str]) -> bool:
    return text(row.get("civil_service_opportunity_level")).lower() in {"none", "limited"}


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def load_source_archive_paths(path: Path | None) -> dict[str, list[str]]:
    if not path or not Path(path).exists():
        return {}
    result: dict[str, list[str]] = {}
    for row in read_csv_rows(Path(path)):
        if row.get("crawl_status") not in {"ok", "cached"}:
            continue
        source_url = text(row.get("source_url"))
        if not source_url:
            continue
        paths = [path for path in [text(row.get("raw_path")), text(row.get("text_path"))] if path]
        if paths:
            result.setdefault(source_url, [])
            for source_path in paths:
                if source_path not in result[source_url]:
                    result[source_url].append(source_path)
    return result


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_values(value: Any) -> list[str]:
    return [part.strip() for part in text(value).split("|") if part.strip()]


def value_at(values: list[str], index: int) -> str:
    return values[index] if 0 <= index < len(values) else ""


def join_sorted(values: Iterable[Any]) -> str:
    return "|".join(sorted({text(value) for value in values if text(value)}))


def join_sample(values: Iterable[Any], *, limit: int) -> str:
    return "|".join(sorted({text(value) for value in values if text(value)})[:limit])


def join_nonempty(values: Iterable[Any], *, sep: str = "|") -> str:
    return sep.join(text(value) for value in values if text(value))


def mean_text(values: list[float | None]) -> str:
    numeric = [value for value in values if value is not None]
    if not numeric:
        return ""
    return number_text(sum(numeric) / len(numeric))


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def stable_id(prefix: str, *parts: Any) -> str:
    key = "|".join(text(part) for part in parts)
    return prefix + ":" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def path_key(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def to_int(value: Any, *, default: int = 0) -> int:
    number = to_float(value)
    return int(number) if number is not None else default


def to_float(value: Any, *, default: float | None = None) -> float | None:
    try:
        value_text = text(value)
        if not value_text:
            return default
        return float(value_text)
    except (TypeError, ValueError):
        return default


def number_text(value: Any) -> str:
    number = to_float(value)
    if number is None:
        return ""
    if number.is_integer():
        return str(int(number))
    return f"{number:.2f}".rstrip("0").rstrip(".")


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build major risk review shortlist and source index.")
    parser.add_argument("--master-index-csv", type=Path, default=ROOT / "data/processed/major_risk_master_index/major_risk_master_index_2026.csv")
    parser.add_argument("--evidence-major-summary-csv", type=Path, default=ROOT / "data/processed/major_risk_evidence_profiles/major_risk_evidence_major_summary_2026.csv")
    parser.add_argument("--evidence-records-csv", type=Path, default=ROOT / "data/processed/major_risk_evidence_profiles/major_risk_evidence_records_2026.csv")
    parser.add_argument("--source-archive-csv", type=Path, default=DEFAULT_SOURCE_ARCHIVE_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_major_risk_review_release(
        master_index_csv=args.master_index_csv,
        evidence_major_summary_csv=args.evidence_major_summary_csv,
        evidence_records_csv=args.evidence_records_csv,
        source_archive_csv=args.source_archive_csv,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        generated_at=args.generated_at,
    )
    print(
        json.dumps(
            {
                "dataset": "major_risk_review_release",
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
                "shortlist_tier_counts": manifest["shortlist_tier_counts"],
                "source_kind_counts": manifest["source_kind_counts"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
