"""Build clean undergraduate major official event tables and risk links."""

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


SCHEMA_VERSION = "undergraduate_major_official_events/v1"
SOURCE_CANDIDATE_SCHEMA = "emerging_major_candidate/v1"
VALID_UNDERGRAD_CODE_RE = re.compile(r"^\d{6}[A-Z]{0,2}$")

EVENT_FIELDS = [
    "event_record_id",
    "source_candidate_id",
    "major_code",
    "major_name",
    "major_level",
    "normalized_event_type",
    "source_event_type",
    "event_year",
    "school_name",
    "is_school_level_event",
    "discipline_category",
    "major_class",
    "degree",
    "study_years",
    "candidate_status",
    "source_title",
    "source_url",
    "attachment_url",
    "source_level",
    "evidence_text",
    "raw_path",
    "parsed_from",
    "captured_at",
    "warnings_json",
    "employment_warning_count",
    "employment_risk_levels",
    "employment_warning_years",
    "employment_warning_match_basis",
    "has_employment_high_risk_warning",
    "has_employment_red_warning",
    "has_employment_yellow_warning",
    "has_employment_green_signal",
    "official_policy_warning_count",
    "official_policy_record_types",
    "official_policy_years",
    "official_policy_match_basis",
    "has_official_policy_warning",
]

SUMMARY_FIELDS = [
    "major_key",
    "major_code",
    "major_name",
    "major_level",
    "first_event_year",
    "latest_event_year",
    "normalized_event_types",
    "candidate_statuses",
    "event_count",
    "catalog_entry_count",
    "filing_added_count",
    "school_count",
    "sample_schools",
    "source_count",
    "attachment_count",
    "parsed_from",
    "employment_warning_count",
    "employment_risk_levels",
    "employment_warning_years",
    "employment_warning_match_basis",
    "employment_warning_record_ids",
    "has_employment_high_risk_warning",
    "has_employment_red_warning",
    "has_employment_yellow_warning",
    "has_employment_green_signal",
    "official_policy_warning_count",
    "official_policy_record_types",
    "official_policy_years",
    "official_policy_match_basis",
    "official_policy_warning_ids",
    "has_official_policy_warning",
]

REJECTED_FIELDS = [
    "source_candidate_id",
    "major_code",
    "major_name",
    "major_level",
    "source_event_type",
    "event_year",
    "candidate_status",
    "reject_reason",
    "source_title",
    "source_url",
    "attachment_url",
    "evidence_text",
    "raw_path",
    "parsed_from",
    "captured_at",
    "warnings_json",
]


def build_undergraduate_major_official_events(
    *,
    candidates_csv: Path,
    employment_warnings_csv: Path,
    official_policy_warnings_csv: Path,
    output_events_csv: Path,
    output_summary_csv: Path,
    output_rejected_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    candidate_rows = list(read_csv_rows(candidates_csv))
    canonical_major_names = build_canonical_major_names(candidate_rows)
    employment_refs = load_employment_warning_refs(employment_warnings_csv)
    policy_refs = load_policy_warning_refs(official_policy_warnings_csv)
    employment_by_code, employment_by_name = build_ref_indexes(employment_refs)
    policy_by_code, policy_by_name = build_ref_indexes(policy_refs)

    source_candidate_counts = Counter(text(row.get("candidate_id")) for row in candidate_rows)
    source_candidate_occurrences: Counter[str] = Counter()
    source_total = 0
    accepted_total = 0
    rejected_total = 0
    duplicate_event_ids = 0
    event_ids: set[str] = set()
    rejected_reason_counts: Counter[str] = Counter()
    event_type_counts: Counter[str] = Counter()
    event_year_counts: Counter[str] = Counter()
    linked_employment_rows = 0
    linked_policy_rows = 0
    normalized_major_name_count = 0
    missing_school_name_filing_count = 0
    summary_groups: dict[tuple[str, str], dict[str, Any]] = {}

    output_events_csv.parent.mkdir(parents=True, exist_ok=True)
    output_rejected_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_events_csv.open("w", encoding="utf-8-sig", newline="") as event_handle, output_rejected_csv.open(
        "w", encoding="utf-8-sig", newline=""
    ) as rejected_handle:
        event_writer = csv.DictWriter(event_handle, fieldnames=EVENT_FIELDS, extrasaction="ignore")
        rejected_writer = csv.DictWriter(rejected_handle, fieldnames=REJECTED_FIELDS, extrasaction="ignore")
        event_writer.writeheader()
        rejected_writer.writeheader()
        for row in candidate_rows:
            source_total += 1
            source_candidate_id = text(row.get("candidate_id"))
            source_candidate_occurrences[source_candidate_id] += 1
            reject_reason = reject_reason_for(row)
            if reject_reason:
                rejected_total += 1
                rejected_reason_counts[reject_reason] += 1
                rejected_writer.writerow(build_rejected_row(row, reject_reason=reject_reason))
                continue

            event_row = build_event_row(
                row,
                source_candidate_count=source_candidate_counts[source_candidate_id],
                source_candidate_ordinal=source_candidate_occurrences[source_candidate_id],
                canonical_major_names=canonical_major_names,
                employment_by_code=employment_by_code,
                employment_by_name=employment_by_name,
                policy_by_code=policy_by_code,
                policy_by_name=policy_by_name,
            )
            if event_row["event_record_id"] in event_ids:
                duplicate_event_ids += 1
            event_ids.add(event_row["event_record_id"])
            accepted_total += 1
            event_type_counts[event_row["normalized_event_type"]] += 1
            event_year_counts[event_row["event_year"]] += 1
            if int(event_row["employment_warning_count"]):
                linked_employment_rows += 1
            if int(event_row["official_policy_warning_count"]):
                linked_policy_rows += 1
            if text(row.get("major_name")) != event_row["major_name"]:
                normalized_major_name_count += 1
            if (
                event_row["normalized_event_type"] == "undergraduate_filing_or_approval_added"
                and not event_row["school_name"]
            ):
                missing_school_name_filing_count += 1
            update_summary_group(summary_groups, event_row)
            event_writer.writerow(event_row)

    summary_rows = build_summary_rows(
        summary_groups,
        employment_by_code=employment_by_code,
        employment_by_name=employment_by_name,
        policy_by_code=policy_by_code,
        policy_by_name=policy_by_name,
    )
    write_csv(output_summary_csv, summary_rows, SUMMARY_FIELDS)

    linked_high_risk_majors = [row for row in summary_rows if row["has_employment_high_risk_warning"] == "true"]
    linked_policy_majors = [row for row in summary_rows if row["has_official_policy_warning"] == "true"]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source_schema_version": SOURCE_CANDIDATE_SCHEMA,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "candidates_csv": str(candidates_csv),
        "employment_warnings_csv": str(employment_warnings_csv),
        "official_policy_warnings_csv": str(official_policy_warnings_csv),
        "output_events_csv": str(output_events_csv),
        "output_summary_csv": str(output_summary_csv),
        "output_rejected_csv": str(output_rejected_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "source_candidate_count": source_total,
        "accepted_event_count": accepted_total,
        "rejected_candidate_count": rejected_total,
        "duplicate_source_candidate_id_count": sum(count - 1 for count in source_candidate_counts.values() if count > 1),
        "duplicate_event_record_id_count": duplicate_event_ids,
        "unique_major_count": len(summary_rows),
        "event_type_counts": dict(sorted(event_type_counts.items())),
        "event_year_counts": dict(sorted(event_year_counts.items())),
        "rejected_reason_counts": dict(sorted(rejected_reason_counts.items())),
        "linked_employment_row_count": linked_employment_rows,
        "linked_policy_row_count": linked_policy_rows,
        "linked_high_risk_major_count": len(linked_high_risk_majors),
        "linked_policy_major_count": len(linked_policy_majors),
        "normalized_major_name_count": normalized_major_name_count,
        "missing_school_name_filing_count": missing_school_name_filing_count,
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(output_report_md, manifest)
    return manifest


def reject_reason_for(row: dict[str, str]) -> str:
    major_code = text(row.get("major_code"))
    major_name = text(row.get("major_name"))
    major_level = text(row.get("major_level"))
    if major_level and major_level != "本科":
        return "not_undergraduate_level"
    if not VALID_UNDERGRAD_CODE_RE.fullmatch(major_code):
        return "invalid_or_missing_undergraduate_major_code"
    if not major_name:
        return "missing_major_name"
    if major_name in {"备注", "序 号"}:
        return "table_header_or_note"
    return ""


def build_event_row(
    row: dict[str, str],
    *,
    source_candidate_count: int,
    source_candidate_ordinal: int,
    canonical_major_names: dict[str, str],
    employment_by_code: dict[str, list[dict[str, str]]],
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_code: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    major_code = text(row.get("major_code"))
    source_major_name = text(row.get("major_name"))
    source_candidate_id = text(row.get("candidate_id"))
    event_record_id = source_candidate_id
    if source_candidate_count > 1:
        event_record_id = f"{source_candidate_id}:{source_candidate_ordinal:03d}"
    normalized_event_type = normalize_event_type(row.get("event_type"))
    major_name = normalize_major_name(
        row,
        normalized_event_type=normalized_event_type,
        canonical_major_name=canonical_major_names.get(major_code, ""),
    )
    employment_refs, employment_basis = match_refs(major_code, major_name, employment_by_code, employment_by_name)
    policy_refs, policy_basis = match_refs(major_code, major_name, policy_by_code, policy_by_name)
    school_name = parse_school_name(
        row,
        normalized_event_type=normalized_event_type,
        canonical_major_name=canonical_major_names.get(major_code, ""),
        normalized_major_name=major_name,
    )
    return {
        "event_record_id": event_record_id,
        "source_candidate_id": source_candidate_id,
        "major_code": major_code,
        "major_name": major_name,
        "major_level": text(row.get("major_level")) or "本科",
        "normalized_event_type": normalized_event_type,
        "source_event_type": text(row.get("event_type")),
        "event_year": text(row.get("event_year")),
        "school_name": school_name,
        "is_school_level_event": bool_text(bool(school_name)),
        "discipline_category": text(row.get("discipline_category")),
        "major_class": text(row.get("major_class")),
        "degree": text(row.get("degree")),
        "study_years": text(row.get("study_years")),
        "candidate_status": text(row.get("candidate_status")),
        "source_title": text(row.get("source_title")),
        "source_url": text(row.get("source_url")),
        "attachment_url": text(row.get("attachment_url")),
        "source_level": text(row.get("source_level")),
        "evidence_text": text(row.get("evidence_text")),
        "raw_path": text(row.get("raw_path")),
        "parsed_from": text(row.get("parsed_from")),
        "captured_at": text(row.get("captured_at")),
        "warnings_json": text(row.get("warnings_json")) or "[]",
        **summarize_employment_refs(employment_refs, employment_basis),
        **summarize_policy_refs(policy_refs, policy_basis),
    }


def build_rejected_row(row: dict[str, str], *, reject_reason: str) -> dict[str, Any]:
    return {
        "source_candidate_id": text(row.get("candidate_id")),
        "major_code": text(row.get("major_code")),
        "major_name": text(row.get("major_name")),
        "major_level": text(row.get("major_level")),
        "source_event_type": text(row.get("event_type")),
        "event_year": text(row.get("event_year")),
        "candidate_status": text(row.get("candidate_status")),
        "reject_reason": reject_reason,
        "source_title": text(row.get("source_title")),
        "source_url": text(row.get("source_url")),
        "attachment_url": text(row.get("attachment_url")),
        "evidence_text": text(row.get("evidence_text")),
        "raw_path": text(row.get("raw_path")),
        "parsed_from": text(row.get("parsed_from")),
        "captured_at": text(row.get("captured_at")),
        "warnings_json": text(row.get("warnings_json")) or "[]",
    }


def normalize_event_type(event_type: Any) -> str:
    value = text(event_type)
    if value == "catalog_added":
        return "undergraduate_catalog_entry"
    if value == "filing_added":
        return "undergraduate_filing_or_approval_added"
    return value or "unknown"


def normalize_major_name(row: dict[str, str], *, normalized_event_type: str, canonical_major_name: str = "") -> str:
    source_major_name = text(row.get("major_name"))
    if normalized_event_type != "undergraduate_filing_or_approval_added" or not canonical_major_name:
        return source_major_name
    if source_major_name == canonical_major_name:
        return source_major_name
    if source_major_name.endswith(canonical_major_name):
        return canonical_major_name
    before_code = text_before_major_code(row)
    if before_code == source_major_name and looks_like_school_name(source_major_name):
        return canonical_major_name
    return source_major_name


def parse_school_name(
    row: dict[str, str],
    *,
    normalized_event_type: str,
    canonical_major_name: str = "",
    normalized_major_name: str = "",
) -> str:
    if normalized_event_type != "undergraduate_filing_or_approval_added":
        return ""
    evidence_text = text(row.get("evidence_text"))
    major_code = text(row.get("major_code"))
    source_major_name = text(row.get("major_name"))
    split_major_name = canonical_major_name or normalized_major_name or source_major_name
    if "|" in evidence_text:
        parts = [part.strip() for part in evidence_text.split("|")]
        if parts and parts[0].isdigit():
            parts = parts[1:]
        if parts and len(parts) >= 2:
            if major_code in parts:
                idx = parts.index(major_code)
                before_code_parts = parts[:idx]
                if not before_code_parts:
                    return ""
                last = before_code_parts[-1]
                if split_major_name and last.endswith(split_major_name):
                    prefix = last[: -len(split_major_name)].strip()
                    return "".join(before_code_parts[:-1] + ([prefix] if prefix else [])).strip()
                if normalized_major_name and last == normalized_major_name:
                    return "".join(before_code_parts[:-1]).strip()
                return "".join(before_code_parts).strip()
            return parts[0]
    tokens = evidence_text.split()
    if tokens and tokens[0].isdigit():
        tokens = tokens[1:]
    if major_code in tokens:
        idx = tokens.index(major_code)
        before = "".join(tokens[:idx])
        if split_major_name and before.endswith(split_major_name):
            return before[: -len(split_major_name)].strip()
        if normalized_major_name and normalized_major_name in tokens[:idx]:
            name_idx = tokens[:idx].index(normalized_major_name)
            return "".join(tokens[:name_idx]).strip()
        if canonical_major_name and before == source_major_name and looks_like_school_name(source_major_name):
            return before
    return ""


def text_before_major_code(row: dict[str, str]) -> str:
    evidence_text = text(row.get("evidence_text"))
    major_code = text(row.get("major_code"))
    if not evidence_text or not major_code:
        return ""
    if "|" in evidence_text:
        parts = [part.strip() for part in evidence_text.split("|")]
        if parts and parts[0].isdigit():
            parts = parts[1:]
        if major_code in parts:
            return "".join(parts[: parts.index(major_code)]).strip()
    tokens = evidence_text.split()
    if tokens and tokens[0].isdigit():
        tokens = tokens[1:]
    if major_code in tokens:
        return "".join(tokens[: tokens.index(major_code)]).strip()
    return ""


def looks_like_school_name(value: str) -> bool:
    return any(marker in value for marker in ("大学", "学院", "学校", "高等专科学校", "职业技术大学"))


def build_canonical_major_names(rows: list[dict[str, str]]) -> dict[str, str]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        if normalize_event_type(row.get("event_type")) != "undergraduate_catalog_entry":
            continue
        major_code = text(row.get("major_code"))
        major_name = text(row.get("major_name"))
        if not VALID_UNDERGRAD_CODE_RE.fullmatch(major_code):
            continue
        if not major_name or major_name in {"备注", "序 号"} or looks_like_degree_word(major_name):
            continue
        grouped[major_code][major_name] += 1
    canonical: dict[str, str] = {}
    for major_code, names in grouped.items():
        canonical[major_code] = sorted(names.items(), key=lambda item: (-item[1], "（注" in item[0], len(item[0]), item[0]))[0][0]
    return canonical


def looks_like_degree_word(value: str) -> bool:
    return value in {"哲学", "经济学", "法学", "教育学", "文学", "历史学", "理学", "工学", "农学", "医学", "管理学", "艺术学"}


def update_summary_group(groups: dict[tuple[str, str], dict[str, Any]], event_row: dict[str, Any]) -> None:
    key = (event_row["major_code"], event_row["major_name"])
    group = groups.setdefault(
        key,
        {
            "major_code": event_row["major_code"],
            "major_name": event_row["major_name"],
            "major_level": event_row["major_level"],
            "event_years": set(),
            "normalized_event_types": Counter(),
            "candidate_statuses": set(),
            "event_count": 0,
            "schools": set(),
            "sources": set(),
            "attachments": set(),
            "parsed_from": set(),
        },
    )
    group["event_count"] += 1
    if event_row["event_year"]:
        group["event_years"].add(event_row["event_year"])
    group["normalized_event_types"][event_row["normalized_event_type"]] += 1
    if event_row["candidate_status"]:
        group["candidate_statuses"].add(event_row["candidate_status"])
    if event_row["school_name"]:
        group["schools"].add(event_row["school_name"])
    if event_row["source_url"]:
        group["sources"].add(event_row["source_url"])
    if event_row["attachment_url"]:
        group["attachments"].add(event_row["attachment_url"])
    if event_row["parsed_from"]:
        group["parsed_from"].add(event_row["parsed_from"])


def build_summary_rows(
    groups: dict[tuple[str, str], dict[str, Any]],
    *,
    employment_by_code: dict[str, list[dict[str, str]]],
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_code: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (major_code, major_name), group in groups.items():
        event_years = sorted(group["event_years"])
        event_type_counts: Counter[str] = group["normalized_event_types"]
        employment_refs, employment_basis = match_refs(major_code, major_name, employment_by_code, employment_by_name)
        policy_refs, policy_basis = match_refs(major_code, major_name, policy_by_code, policy_by_name)
        rows.append(
            {
                "major_key": major_key(major_code, major_name),
                "major_code": major_code,
                "major_name": major_name,
                "major_level": group["major_level"],
                "first_event_year": event_years[0] if event_years else "",
                "latest_event_year": event_years[-1] if event_years else "",
                "normalized_event_types": "|".join(sorted(event_type_counts)),
                "candidate_statuses": "|".join(sorted(group["candidate_statuses"])),
                "event_count": group["event_count"],
                "catalog_entry_count": event_type_counts.get("undergraduate_catalog_entry", 0),
                "filing_added_count": event_type_counts.get("undergraduate_filing_or_approval_added", 0),
                "school_count": len(group["schools"]),
                "sample_schools": "、".join(sorted(group["schools"])[:8]),
                "source_count": len(group["sources"]),
                "attachment_count": len(group["attachments"]),
                "parsed_from": "|".join(sorted(group["parsed_from"])),
                **summarize_employment_refs(employment_refs, employment_basis, include_ids=True),
                **summarize_policy_refs(policy_refs, policy_basis, include_ids=True),
            }
        )
    return sorted(rows, key=lambda item: (item["major_code"], item["major_name"]))


def load_employment_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        if not is_undergraduate_level(row.get("education_level")):
            continue
        refs.append(
            {
                "id": text(row.get("record_id")),
                "major_code": text(row.get("major_code")),
                "major_name": major_name_from_warning(row),
                "year": text(row.get("report_year")),
                "risk_level": text(row.get("risk_level")),
            }
        )
    return refs


def load_policy_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        if not is_undergraduate_level(row.get("education_level")):
            continue
        refs.append(
            {
                "id": text(row.get("warning_id")),
                "major_code": text(row.get("major_code")),
                "major_name": major_name_from_warning(row),
                "year": text(row.get("policy_year")),
                "record_type": text(row.get("record_type")),
            }
        )
    return refs


def build_ref_indexes(refs: list[dict[str, str]]) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for ref in refs:
        if ref["major_code"]:
            by_code[ref["major_code"]].append(ref)
        if ref["major_name"]:
            by_name[ref["major_name"]].append(ref)
    return by_code, by_name


def match_refs(
    major_code: str,
    major_name: str,
    by_code: dict[str, list[dict[str, str]]],
    by_name: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, str]], str]:
    refs_by_id: dict[str, dict[str, str]] = {}
    basis: list[str] = []
    if major_code and major_code in by_code:
        basis.append("code")
        for ref in by_code[major_code]:
            refs_by_id[ref["id"]] = ref
    if major_name and major_name in by_name:
        basis.append("name")
        for ref in by_name[major_name]:
            refs_by_id[ref["id"]] = ref
    refs = sorted(refs_by_id.values(), key=lambda item: (item.get("year", ""), item.get("id", "")))
    return refs, "+".join(basis)


def summarize_employment_refs(refs: list[dict[str, str]], basis: str, *, include_ids: bool = False) -> dict[str, Any]:
    risk_levels = ordered_unique([ref["risk_level"] for ref in refs], order=["red", "yellow", "green"])
    years = ordered_unique([ref["year"] for ref in refs])
    has_red = "red" in risk_levels
    has_yellow = "yellow" in risk_levels
    has_green = "green" in risk_levels
    summary: dict[str, Any] = {
        "employment_warning_count": len(refs),
        "employment_risk_levels": "|".join(risk_levels),
        "employment_warning_years": "|".join(years),
        "employment_warning_match_basis": basis,
        "has_employment_high_risk_warning": bool_text(has_red or has_yellow),
        "has_employment_red_warning": bool_text(has_red),
        "has_employment_yellow_warning": bool_text(has_yellow),
        "has_employment_green_signal": bool_text(has_green),
    }
    if include_ids:
        summary["employment_warning_record_ids"] = "|".join(ordered_unique([ref["id"] for ref in refs]))
    return summary


def summarize_policy_refs(refs: list[dict[str, str]], basis: str, *, include_ids: bool = False) -> dict[str, Any]:
    record_types = ordered_unique([ref["record_type"] for ref in refs])
    years = ordered_unique([ref["year"] for ref in refs])
    summary: dict[str, Any] = {
        "official_policy_warning_count": len(refs),
        "official_policy_record_types": "|".join(record_types),
        "official_policy_years": "|".join(years),
        "official_policy_match_basis": basis,
        "has_official_policy_warning": bool_text(bool(refs)),
    }
    if include_ids:
        summary["official_policy_warning_ids"] = "|".join(ordered_unique([ref["id"] for ref in refs]))
    return summary


def write_report(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# 本科专业目录/备案审批事件清洗与风险关联报告",
        "",
        f"- 来源候选行数：{manifest['source_candidate_count']}",
        f"- 清洗后有效本科专业事件：{manifest['accepted_event_count']}",
        f"- 拒收噪声/非标准行：{manifest['rejected_candidate_count']}",
        f"- 重复来源 candidate_id 超额数：{manifest['duplicate_source_candidate_id_count']}",
        f"- 输出事件表重复 event_record_id：{manifest['duplicate_event_record_id_count']}",
        f"- 去重专业代码/名称数：{manifest['unique_major_count']}",
        f"- 通过目录标准名修复的专业名行数：{manifest['normalized_major_name_count']}",
        f"- 备案/审批新增事件中仍无法可靠推断学校名的行数：{manifest['missing_school_name_filing_count']}",
        f"- 可关联红/黄就业预警的本科专业数：{manifest['linked_high_risk_major_count']}",
        f"- 可关联官方政策风险记录的本科专业数：{manifest['linked_policy_major_count']}",
        f"- 行级就业预警关联数：{manifest['linked_employment_row_count']}",
        f"- 行级官方政策关联数：{manifest['linked_policy_row_count']}",
        "",
        "## 事件类型",
        "",
    ]
    for event_type, count in manifest["event_type_counts"].items():
        lines.append(f"- `{event_type}`: {count}")
    lines.extend(["", "## 年份覆盖", ""])
    for year, count in manifest["event_year_counts"].items():
        lines.append(f"- {year}: {count}")
    lines.extend(["", "## 拒收原因", ""])
    for reason, count in manifest["rejected_reason_counts"].items():
        lines.append(f"- `{reason}`: {count}")
    lines.extend(
        [
            "",
            "## 输出文件",
            "",
            f"- 清洗事件表：`{manifest['output_events_csv']}`",
            f"- 专业级汇总：`{manifest['output_summary_csv']}`",
            f"- 拒收行表：`{manifest['output_rejected_csv']}`",
            f"- Manifest：`{manifest['output_manifest_json']}`",
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


def major_key(major_code: str, major_name: str) -> str:
    return hashlib.sha256(f"{major_code}|{major_name}".encode("utf-8")).hexdigest()[:24]


def ordered_unique(values: list[str], *, order: list[str] | None = None) -> list[str]:
    seen = {value for value in values if value}
    if order:
        return [value for value in order if value in seen] + sorted(seen - set(order))
    return sorted(seen)


def is_undergraduate_level(value: Any) -> bool:
    level = text(value)
    return "本科" in level or level == "高等教育"


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build clean undergraduate official major-event outputs.")
    parser.add_argument(
        "--candidates-csv",
        type=Path,
        default=Path("data/processed/policy_documents/emerging_major_candidates_emerging_major_seed_20260612_v5.csv"),
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
        "--output-events-csv",
        type=Path,
        default=Path("data/processed/policy_documents/undergraduate_major_official_events_20260612_v5.csv"),
    )
    parser.add_argument(
        "--output-summary-csv",
        type=Path,
        default=Path("data/processed/policy_documents/undergraduate_major_official_event_summary_20260612_v5.csv"),
    )
    parser.add_argument(
        "--output-rejected-csv",
        type=Path,
        default=Path("data/processed/policy_documents/undergraduate_major_official_events_rejected_20260612_v5.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/policy_documents/undergraduate_major_official_events_manifest_20260612_v5.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/policy_documents/undergraduate_major_official_events_20260612_v5.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_undergraduate_major_official_events(
        candidates_csv=args.candidates_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        output_events_csv=args.output_events_csv,
        output_summary_csv=args.output_summary_csv,
        output_rejected_csv=args.output_rejected_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
