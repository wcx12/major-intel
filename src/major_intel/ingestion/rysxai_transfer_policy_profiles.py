"""Build transfer-major policy profiles from rysxai school policy data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "rysxai_transfer_policy_profiles/v1"

SCHOOL_FIELDS = [
    "transfer_policy_profile_id",
    "school_id",
    "school_name",
    "province",
    "city",
    "school_type",
    "property",
    "level",
    "department",
    "tags",
    "source_url",
    "has_transfer_policy",
    "has_faculty_policy",
    "faculty_policy_count",
    "is_new_version",
    "change_profession_chars",
    "application_condition_chars",
    "admission_requirement_chars",
    "assessment_chars",
    "total_policy_chars",
    "policy_sections_present",
    "has_gpa_requirement",
    "has_rank_requirement",
    "has_exam_requirement",
    "has_interview_requirement",
    "has_quota_limit",
    "has_major_restriction",
    "has_special_enrollment_restriction",
    "has_grade_time_restriction",
    "has_course_requirement",
    "has_physical_requirement",
    "has_penalty_restriction",
    "has_open_transfer_signal",
    "transfer_difficulty_score",
    "transfer_difficulty_level",
    "mentioned_major_count",
    "mentioned_high_risk_major_count",
    "mentioned_policy_risk_major_count",
    "mentioned_ai_risk_major_count",
    "sample_mentioned_majors",
    "sample_high_risk_majors",
    "source_level",
    "data_scope",
]

FACULTY_FIELDS = [
    "transfer_faculty_profile_id",
    "school_id",
    "school_name",
    "province",
    "city",
    "faculty_name",
    "source_url",
    "columns",
    "policy_chars",
    "has_gpa_requirement",
    "has_rank_requirement",
    "has_exam_requirement",
    "has_interview_requirement",
    "has_quota_limit",
    "has_major_restriction",
    "has_special_enrollment_restriction",
    "has_course_requirement",
    "has_physical_requirement",
    "transfer_difficulty_score",
    "transfer_difficulty_level",
    "mentioned_major_count",
    "sample_mentioned_majors",
    "source_level",
    "data_scope",
]

MAJOR_FIELDS = [
    "transfer_policy_major_id",
    "major_code",
    "major_name",
    "major_level",
    "category",
    "subject",
    "mentioned_in_school_count",
    "mentioned_in_faculty_count",
    "high_difficulty_school_count",
    "gpa_requirement_school_count",
    "rank_requirement_school_count",
    "exam_requirement_school_count",
    "quota_limit_school_count",
    "major_restriction_school_count",
    "special_enrollment_restriction_school_count",
    "physical_requirement_school_count",
    "sample_schools",
    "sample_faculties",
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

SUMMARY_FIELDS = [
    "summary_key",
    "group_type",
    "school_count",
    "with_transfer_policy_count",
    "with_faculty_policy_count",
    "avg_difficulty_score",
    "very_restrictive_count",
    "restrictive_count",
    "moderate_count",
    "permissive_count",
    "unknown_count",
    "avg_faculty_policy_count",
    "avg_total_policy_chars",
    "source_level",
    "data_scope",
]


@dataclass(frozen=True)
class MajorRef:
    key: str
    major_code: str
    major_name: str
    level: str
    category: str
    subject: str


KEYWORDS = {
    "gpa": ["GPA", "\u7ee9\u70b9", "\u5e73\u5747\u7ee9\u70b9", "\u5b66\u5206\u7ee9"],
    "rank": ["\u6392\u540d", "\u4e13\u4e1a\u6392\u540d", "\u6210\u7ee9\u6392\u540d", "\u524d10%", "\u524d 10%"],
    "exam": ["\u7b14\u8bd5", "\u8003\u8bd5", "\u6d4b\u8bd5"],
    "interview": ["\u9762\u8bd5", "\u8003\u6838"],
    "quota": ["\u540d\u989d", "\u8ba1\u5212", "\u6bd4\u4f8b", "\u63a5\u6536\u4eba\u6570", "\u9650\u989d", "\u4e0d\u8d85\u8fc7"],
    "major_restriction": [
        "\u4e0d\u5f97\u8f6c\u4e13\u4e1a",
        "\u4e0d\u5141\u8bb8",
        "\u4e0d\u5f97\u7533\u8bf7",
        "\u4e0d\u80fd\u7533\u8bf7",
        "\u4e0d\u63a5\u6536",
        "\u4e0d\u5f97\u8f6c\u5165",
        "\u4e0d\u5f97\u8f6c\u51fa",
        "\u7981\u6b62",
    ],
    "special": [
        "\u5f3a\u57fa",
        "\u5b9a\u5411",
        "\u4e2d\u5916\u5408\u4f5c",
        "\u827a\u672f",
        "\u4f53\u80b2",
        "\u9ad8\u6c34\u5e73",
        "\u56fd\u9632",
        "\u516c\u8d39\u5e08\u8303",
        "\u4fdd\u9001",
    ],
    "grade_time": ["\u5927\u4e00", "\u5927\u4e8c", "\u7b2c\u4e00\u5b66\u5e74", "\u7b2c\u4e8c\u5b66\u5e74", "\u7533\u8bf7\u65f6\u95f4", "\u8f6c\u5165\u65f6\u95f4"],
    "course": ["\u8bfe\u7a0b", "\u4fee\u8bfb", "\u9ad8\u7b49\u6570\u5b66", "\u7269\u7406", "\u5316\u5b66", "\u4e0d\u53ca\u683c", "\u6302\u79d1"],
    "physical": ["\u8272\u76f2", "\u8272\u5f31", "\u4f53\u68c0", "\u8eab\u4f53"],
    "penalty": ["\u5904\u5206", "\u8fdd\u7eaa", "\u4f11\u5b66", "\u9000\u5b66"],
    "open": ["\u96f6\u95e8\u69db", "\u81ea\u7531\u8f6c", "\u4e0d\u8bbe\u9650\u5236", "\u65e0\u95e8\u69db", "\u5747\u53ef", "\u53ef\u7533\u8bf7"],
}


def build_rysxai_transfer_policy_profiles(
    *,
    transfer_policies_csv: Path,
    major_seed_csv: Path,
    employment_warnings_csv: Path,
    official_policy_warnings_csv: Path,
    ai_replacement_csv: Path,
    output_school_profiles_csv: Path,
    output_faculty_profiles_csv: Path,
    output_major_mentions_csv: Path,
    output_summary_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    majors = load_major_refs(major_seed_csv)
    employment_by_name = build_warning_name_index(load_employment_warning_refs(employment_warnings_csv))
    policy_by_name = build_warning_name_index(load_policy_warning_refs(official_policy_warnings_csv))
    ai_by_name = build_ai_name_index(load_ai_replacement_refs(ai_replacement_csv))

    school_rows: list[dict[str, Any]] = []
    faculty_rows: list[dict[str, Any]] = []
    major_mentions: dict[str, dict[str, Any]] = defaultdict(new_major_mention_aggregate)

    input_school_count = 0
    for row in read_csv_rows(transfer_policies_csv):
        input_school_count += 1
        text_blob = policy_text_blob(row)
        mentioned = find_mentioned_majors(text_blob, majors)
        school_profile = build_school_profile(row, mentioned, employment_by_name, policy_by_name, ai_by_name)
        school_rows.append(school_profile)
        update_major_mention_aggregates(major_mentions, mentioned, school_profile)
        for faculty_index, faculty in enumerate(parse_faculty_rows(row), start=1):
            faculty_text = faculty_text_blob(faculty)
            faculty_mentioned = find_mentioned_majors(faculty_text, majors)
            faculty_profile = build_faculty_profile(row, faculty, faculty_index, faculty_text, faculty_mentioned)
            faculty_rows.append(faculty_profile)
            update_faculty_major_mentions(major_mentions, faculty_mentioned, faculty_profile)

    major_rows = build_major_mention_rows(
        majors,
        major_mentions,
        employment_by_name=employment_by_name,
        policy_by_name=policy_by_name,
        ai_by_name=ai_by_name,
    )
    summary_rows = build_summary_rows(school_rows)

    write_csv(output_school_profiles_csv, school_rows, SCHOOL_FIELDS)
    write_csv(output_faculty_profiles_csv, faculty_rows, FACULTY_FIELDS)
    write_csv(output_major_mentions_csv, major_rows, MAJOR_FIELDS)
    write_csv(output_summary_csv, summary_rows, SUMMARY_FIELDS)

    mentioned_major_rows = [row for row in major_rows if int(row["mentioned_in_school_count"])]
    linked_high_risk = [row for row in mentioned_major_rows if row["has_employment_high_risk_warning"] == "true"]
    linked_policy = [row for row in mentioned_major_rows if int(row["official_policy_warning_count"])]
    linked_ai = [row for row in mentioned_major_rows if int(row["ai_replacement_match_count"])]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "transfer_policies_csv": str(transfer_policies_csv),
        "major_seed_csv": str(major_seed_csv),
        "employment_warnings_csv": str(employment_warnings_csv),
        "official_policy_warnings_csv": str(official_policy_warnings_csv),
        "ai_replacement_csv": str(ai_replacement_csv),
        "output_school_profiles_csv": str(output_school_profiles_csv),
        "output_faculty_profiles_csv": str(output_faculty_profiles_csv),
        "output_major_mentions_csv": str(output_major_mentions_csv),
        "output_summary_csv": str(output_summary_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "input_school_count": input_school_count,
        "school_profile_count": len(school_rows),
        "faculty_profile_count": len(faculty_rows),
        "major_seed_count": len(majors),
        "major_mention_row_count": len(major_rows),
        "mentioned_major_count": len(mentioned_major_rows),
        "summary_row_count": len(summary_rows),
        "linked_high_risk_major_count": len(linked_high_risk),
        "linked_policy_major_count": len(linked_policy),
        "linked_ai_replacement_major_count": len(linked_ai),
        "source_level": "C",
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(output_report_md, manifest, school_rows, major_rows)
    return manifest


def build_school_profile(
    row: dict[str, str],
    mentioned: list[MajorRef],
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
    ai_by_name: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    text_blob = policy_text_blob(row)
    flags = keyword_flags(text_blob)
    score, level = difficulty_score(flags, total_chars=to_int(row.get("change_profession_chars")) + to_int(row.get("application_condition_chars")) + to_int(row.get("admission_requirement_chars")) + to_int(row.get("assessment_chars")), faculty_count=to_int(row.get("faculty_policy_count")), has_policy=row_bool(row.get("has_transfer_policy")))
    high_risk = [major for major in mentioned if has_high_risk(major.major_name, employment_by_name)]
    policy_risk = [major for major in mentioned if policy_by_name.get(major.major_name)]
    ai_risk = [major for major in mentioned if ai_by_name.get(major.major_name)]
    return {
        "transfer_policy_profile_id": school_profile_id(text(row.get("school_id")), text(row.get("school_name"))),
        "school_id": text(row.get("school_id")),
        "school_name": text(row.get("school_name")),
        "province": text(row.get("province")),
        "city": text(row.get("city")),
        "school_type": text(row.get("type")),
        "property": text(row.get("property")),
        "level": text(row.get("level")),
        "department": text(row.get("department")),
        "tags": "|".join(parse_tags(row.get("tags_json"))),
        "source_url": text(row.get("source_url")),
        "has_transfer_policy": lower_bool_text(row.get("has_transfer_policy")),
        "has_faculty_policy": lower_bool_text(row.get("has_faculty_policy")),
        "faculty_policy_count": to_int(row.get("faculty_policy_count")),
        "is_new_version": lower_bool_text(row.get("is_new_version")),
        "change_profession_chars": to_int(row.get("change_profession_chars")),
        "application_condition_chars": to_int(row.get("application_condition_chars")),
        "admission_requirement_chars": to_int(row.get("admission_requirement_chars")),
        "assessment_chars": to_int(row.get("assessment_chars")),
        "total_policy_chars": len(text_blob),
        "policy_sections_present": policy_sections_present(row),
        **flags_to_output(flags),
        "transfer_difficulty_score": score,
        "transfer_difficulty_level": level,
        "mentioned_major_count": len(mentioned),
        "mentioned_high_risk_major_count": len({major.key for major in high_risk}),
        "mentioned_policy_risk_major_count": len({major.key for major in policy_risk}),
        "mentioned_ai_risk_major_count": len({major.key for major in ai_risk}),
        "sample_mentioned_majors": join_sample([major.major_name for major in mentioned], limit=20),
        "sample_high_risk_majors": join_sample([major.major_name for major in high_risk], limit=20),
        "source_level": "C",
        "data_scope": "rysxai_transfer_policy_school_profile",
    }


def build_faculty_profile(
    school_row: dict[str, str],
    faculty: dict[str, Any],
    faculty_index: int,
    faculty_text: str,
    mentioned: list[MajorRef],
) -> dict[str, Any]:
    flags = keyword_flags(faculty_text)
    score, level = difficulty_score(
        flags,
        total_chars=len(faculty_text),
        faculty_count=0,
        has_policy=bool(faculty_text),
    )
    return {
        "transfer_faculty_profile_id": faculty_profile_id(text(school_row.get("school_id")), faculty_index, text(faculty.get("faculty_name"))),
        "school_id": text(school_row.get("school_id")),
        "school_name": text(school_row.get("school_name")),
        "province": text(school_row.get("province")),
        "city": text(school_row.get("city")),
        "faculty_name": text(faculty.get("faculty_name")),
        "source_url": text(school_row.get("source_url")),
        "columns": "|".join(column_titles(faculty)),
        "policy_chars": len(faculty_text),
        **faculty_flags_to_output(flags),
        "transfer_difficulty_score": score,
        "transfer_difficulty_level": level,
        "mentioned_major_count": len(mentioned),
        "sample_mentioned_majors": join_sample([major.major_name for major in mentioned], limit=20),
        "source_level": "C",
        "data_scope": "rysxai_transfer_policy_faculty_profile",
    }


def build_major_mention_rows(
    majors: list[MajorRef],
    aggregates: dict[str, dict[str, Any]],
    *,
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
    ai_by_name: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for major in sorted(majors, key=lambda item: (item.level, item.major_code, item.major_name)):
        aggregate = aggregates.get(major.key, new_major_mention_aggregate())
        employment_refs = employment_by_name.get(major.major_name, [])
        policy_refs = policy_by_name.get(major.major_name, [])
        ai_refs = ai_by_name.get(major.major_name, [])
        best_ai = min(ai_refs, key=ai_sort_key) if ai_refs else None
        rows.append(
            {
                "transfer_policy_major_id": major_mention_id(major.key),
                "major_code": major.major_code,
                "major_name": major.major_name,
                "major_level": major.level,
                "category": major.category,
                "subject": major.subject,
                "mentioned_in_school_count": len(aggregate["schools"]),
                "mentioned_in_faculty_count": len(aggregate["faculties"]),
                "high_difficulty_school_count": len(aggregate["high_difficulty_schools"]),
                "gpa_requirement_school_count": len(aggregate["gpa_schools"]),
                "rank_requirement_school_count": len(aggregate["rank_schools"]),
                "exam_requirement_school_count": len(aggregate["exam_schools"]),
                "quota_limit_school_count": len(aggregate["quota_schools"]),
                "major_restriction_school_count": len(aggregate["major_restriction_schools"]),
                "special_enrollment_restriction_school_count": len(aggregate["special_schools"]),
                "physical_requirement_school_count": len(aggregate["physical_schools"]),
                "sample_schools": join_sample(aggregate["schools"], limit=20),
                "sample_faculties": join_sample(aggregate["faculties"], limit=20),
                **summarize_employment_refs(employment_refs),
                **summarize_policy_refs(policy_refs),
                **summarize_ai_refs(ai_refs, best_ai),
                "source_level": "C",
                "data_scope": "rysxai_transfer_policy_major_mention",
            }
        )
    return rows


def build_summary_rows(school_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [summary_row("ALL", "all", school_rows)]
    for field, group_type in [("province", "province"), ("school_type", "school_type"), ("property", "property"), ("level", "level")]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in school_rows:
            key = text(row.get(field)) or "UNKNOWN"
            grouped[key].append(row)
        rows.extend(summary_row(key, group_type, items) for key, items in sorted(grouped.items()))
    return rows


def summary_row(key: str, group_type: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [to_float(row.get("transfer_difficulty_score")) for row in rows if to_float(row.get("transfer_difficulty_score")) is not None]
    return {
        "summary_key": key,
        "group_type": group_type,
        "school_count": len(rows),
        "with_transfer_policy_count": sum(1 for row in rows if row["has_transfer_policy"] == "true"),
        "with_faculty_policy_count": sum(1 for row in rows if row["has_faculty_policy"] == "true"),
        "avg_difficulty_score": number_text(sum(scores) / len(scores) if scores else None),
        "very_restrictive_count": count_level(rows, "very_restrictive"),
        "restrictive_count": count_level(rows, "restrictive"),
        "moderate_count": count_level(rows, "moderate"),
        "permissive_count": count_level(rows, "permissive"),
        "unknown_count": count_level(rows, "unknown"),
        "avg_faculty_policy_count": number_text(sum(to_int(row.get("faculty_policy_count")) for row in rows) / len(rows) if rows else None),
        "avg_total_policy_chars": number_text(sum(to_int(row.get("total_policy_chars")) for row in rows) / len(rows) if rows else None),
        "source_level": "C",
        "data_scope": "rysxai_transfer_policy_profile_summary",
    }


def new_major_mention_aggregate() -> dict[str, Any]:
    return {
        "schools": set(),
        "faculties": set(),
        "high_difficulty_schools": set(),
        "gpa_schools": set(),
        "rank_schools": set(),
        "exam_schools": set(),
        "quota_schools": set(),
        "major_restriction_schools": set(),
        "special_schools": set(),
        "physical_schools": set(),
    }


def update_major_mention_aggregates(
    aggregates: dict[str, dict[str, Any]],
    mentioned: list[MajorRef],
    school_profile: dict[str, Any],
) -> None:
    for major in mentioned:
        aggregate = aggregates[major.key]
        add_if(aggregate["schools"], school_profile["school_name"])
        if school_profile["transfer_difficulty_level"] in {"restrictive", "very_restrictive"}:
            add_if(aggregate["high_difficulty_schools"], school_profile["school_name"])
        if school_profile["has_gpa_requirement"] == "true":
            add_if(aggregate["gpa_schools"], school_profile["school_name"])
        if school_profile["has_rank_requirement"] == "true":
            add_if(aggregate["rank_schools"], school_profile["school_name"])
        if school_profile["has_exam_requirement"] == "true" or school_profile["has_interview_requirement"] == "true":
            add_if(aggregate["exam_schools"], school_profile["school_name"])
        if school_profile["has_quota_limit"] == "true":
            add_if(aggregate["quota_schools"], school_profile["school_name"])
        if school_profile["has_major_restriction"] == "true":
            add_if(aggregate["major_restriction_schools"], school_profile["school_name"])
        if school_profile["has_special_enrollment_restriction"] == "true":
            add_if(aggregate["special_schools"], school_profile["school_name"])
        if school_profile["has_physical_requirement"] == "true":
            add_if(aggregate["physical_schools"], school_profile["school_name"])


def update_faculty_major_mentions(
    aggregates: dict[str, dict[str, Any]],
    mentioned: list[MajorRef],
    faculty_profile: dict[str, Any],
) -> None:
    for major in mentioned:
        add_if(
            aggregates[major.key]["faculties"],
            f"{faculty_profile['school_name']}:{faculty_profile['faculty_name']}",
        )


def keyword_flags(value: str) -> dict[str, bool]:
    return {name: any(keyword in value for keyword in keywords) for name, keywords in KEYWORDS.items()}


def difficulty_score(
    flags: dict[str, bool],
    *,
    total_chars: int,
    faculty_count: int,
    has_policy: bool,
) -> tuple[str, str]:
    if not has_policy:
        return "", "unknown"
    score = 10
    score += min(total_chars // 2500, 20)
    score += min(faculty_count, 15)
    weights = {
        "gpa": 9,
        "rank": 8,
        "exam": 8,
        "interview": 5,
        "quota": 8,
        "major_restriction": 12,
        "special": 8,
        "grade_time": 4,
        "course": 5,
        "physical": 4,
        "penalty": 4,
    }
    for key, weight in weights.items():
        if flags.get(key):
            score += weight
    if flags.get("open"):
        score -= 8
    score = max(0, min(100, score))
    if score > 75:
        level = "very_restrictive"
    elif score > 50:
        level = "restrictive"
    elif score > 25:
        level = "moderate"
    else:
        level = "permissive"
    return str(score), level


def flags_to_output(flags: dict[str, bool]) -> dict[str, str]:
    return {
        "has_gpa_requirement": bool_text(flags.get("gpa", False)),
        "has_rank_requirement": bool_text(flags.get("rank", False)),
        "has_exam_requirement": bool_text(flags.get("exam", False)),
        "has_interview_requirement": bool_text(flags.get("interview", False)),
        "has_quota_limit": bool_text(flags.get("quota", False)),
        "has_major_restriction": bool_text(flags.get("major_restriction", False)),
        "has_special_enrollment_restriction": bool_text(flags.get("special", False)),
        "has_grade_time_restriction": bool_text(flags.get("grade_time", False)),
        "has_course_requirement": bool_text(flags.get("course", False)),
        "has_physical_requirement": bool_text(flags.get("physical", False)),
        "has_penalty_restriction": bool_text(flags.get("penalty", False)),
        "has_open_transfer_signal": bool_text(flags.get("open", False)),
    }


def faculty_flags_to_output(flags: dict[str, bool]) -> dict[str, str]:
    output = flags_to_output(flags)
    return {key: output[key] for key in FACULTY_FIELDS if key in output}


def find_mentioned_majors(value: str, majors: list[MajorRef]) -> list[MajorRef]:
    mentioned: list[MajorRef] = []
    for major in sorted(majors, key=lambda item: len(item.major_name), reverse=True):
        if major_name_occurs(value, major.major_name):
            mentioned.append(major)
    return mentioned


def major_name_occurs(value: str, name: str) -> bool:
    if not name or len(name) < 2:
        return False
    start = 0
    while True:
        index = value.find(name, start)
        if index < 0:
            return False
        next_index = index + len(name)
        if next_index >= len(value) or value[next_index] != "\u7c7b":
            return True
        start = next_index


def parse_faculty_rows(row: dict[str, str]) -> list[dict[str, Any]]:
    raw = text(row.get("change_profession_by_faculty_json"))
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def faculty_text_blob(faculty: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in faculty.items():
        if key == "columns":
            continue
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, (dict, list)):
            parts.append(json.dumps(value, ensure_ascii=False))
    return "\n".join(parts)


def policy_text_blob(row: dict[str, str]) -> str:
    return "\n".join(
        [
            text(row.get("change_profession")),
            text(row.get("change_profession_application_condition")),
            text(row.get("change_profession_admission_requirement")),
            text(row.get("change_profession_assessment")),
            text(row.get("change_profession_by_faculty_json")),
        ]
    )


def policy_sections_present(row: dict[str, str]) -> str:
    sections = []
    for field, label in [
        ("change_profession", "policy_text"),
        ("change_profession_application_condition", "application_condition"),
        ("change_profession_admission_requirement", "admission_requirement"),
        ("change_profession_assessment", "assessment"),
        ("change_profession_by_faculty_json", "faculty_json"),
    ]:
        if text(row.get(field)) and text(row.get(field)) != "[]":
            sections.append(label)
    return "|".join(sections)


def column_titles(faculty: dict[str, Any]) -> list[str]:
    raw = faculty.get("columns")
    if not isinstance(raw, list):
        return []
    titles = []
    for item in raw:
        if isinstance(item, dict):
            titles.append(text(item.get("title")) or text(item.get("key")))
    return [title for title in titles if title]


def parse_tags(value: Any) -> list[str]:
    try:
        data = json.loads(text(value))
    except json.JSONDecodeError:
        return []
    return [text(item) for item in data if text(item)] if isinstance(data, list) else []


def load_major_refs(path: Path) -> list[MajorRef]:
    refs: list[MajorRef] = []
    for row in read_csv_rows(path):
        code = text(row.get("major_code"))
        name = text(row.get("major_name"))
        level = text(row.get("level"))
        if code and name:
            refs.append(
                MajorRef(
                    key=major_key(code, name, level),
                    major_code=code,
                    major_name=name,
                    level=level,
                    category=text(row.get("category")),
                    subject=text(row.get("subject")),
                )
            )
    return refs


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
    school_rows: list[dict[str, Any]],
    major_rows: list[dict[str, Any]],
) -> None:
    top_schools = sorted(
        [row for row in school_rows if row["transfer_difficulty_score"]],
        key=lambda row: (-to_int(row["transfer_difficulty_score"]), row["school_name"]),
    )[:20]
    top_majors = sorted(
        major_rows,
        key=lambda row: (-to_int(row["mentioned_in_school_count"]), row["major_code"]),
    )[:20]
    lines = [
        "# RYSXAI Transfer Policy Profile Report",
        "",
        f"- Input schools: {manifest['input_school_count']}",
        f"- School profiles: {manifest['school_profile_count']}",
        f"- Faculty profiles: {manifest['faculty_profile_count']}",
        f"- Major mention rows: {manifest['major_mention_row_count']}",
        f"- Mentioned majors: {manifest['mentioned_major_count']}",
        f"- Mentioned red/yellow majors: {manifest['linked_high_risk_major_count']}",
        f"- Mentioned official-policy risk majors: {manifest['linked_policy_major_count']}",
        f"- Mentioned AI replacement-risk majors: {manifest['linked_ai_replacement_major_count']}",
        "",
        "## Highest Heuristic Difficulty Schools",
        "",
        "| School | Province | Score | Level | Faculty policies | Mentioned majors |",
        "|---|---|---:|---|---:|---:|",
    ]
    for row in top_schools:
        lines.append(
            "| {school_name} | {province} | {transfer_difficulty_score} | "
            "{transfer_difficulty_level} | {faculty_policy_count} | {mentioned_major_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Most Mentioned Majors",
            "",
            "| Major | Level | Schools | Faculty rows | Red/yellow | AI risk |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    for row in top_majors:
        lines.append(
            "| {major_name} | {major_level} | {mentioned_in_school_count} | "
            "{mentioned_in_faculty_count} | {has_employment_high_risk_warning} | {ai_replacement_level} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- School profiles: `{manifest['output_school_profiles_csv']}`",
            f"- Faculty profiles: `{manifest['output_faculty_profiles_csv']}`",
            f"- Major mentions: `{manifest['output_major_mentions_csv']}`",
            f"- Summary: `{manifest['output_summary_csv']}`",
            f"- Manifest: `{manifest['output_manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- Source level is `C`: this is third-party compiled policy text.",
            "- Difficulty score is a transparent heuristic from policy length and keyword flags.",
            "- Major mentions are text matches, not official school-major eligibility records.",
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


def has_high_risk(major_name: str, employment_by_name: dict[str, list[dict[str, str]]]) -> bool:
    return any(ref["risk_level"] in {"red", "yellow"} for ref in employment_by_name.get(major_name, []))


def count_level(rows: list[dict[str, Any]], level: str) -> int:
    return sum(1 for row in rows if row.get("transfer_difficulty_level") == level)


def school_profile_id(school_id: str, school_name: str) -> str:
    return "transfer_school:" + hashlib.sha256(f"{school_id}|{school_name}".encode("utf-8")).hexdigest()[:24]


def faculty_profile_id(school_id: str, index: int, faculty_name: str) -> str:
    return "transfer_faculty:" + hashlib.sha256(f"{school_id}|{index}|{faculty_name}".encode("utf-8")).hexdigest()[:24]


def major_mention_id(key: str) -> str:
    return "transfer_major:" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def major_key(code: str, name: str, level: str) -> str:
    return f"{code}|{name}|{level}"


def ai_sort_key(ref: dict[str, str]) -> tuple[int, str]:
    return (to_int(ref.get("rank"), default=10**9), ref.get("major_name", ""))


def ordered_unique(values: list[str], *, order: list[str] | None = None) -> list[str]:
    seen = {value for value in values if value}
    if order:
        return [value for value in order if value in seen] + sorted(seen - set(order))
    return sorted(seen)


def join_sample(values: Any, *, limit: int = 8) -> str:
    return "|".join(sorted(text(value) for value in values if text(value))[:limit])


def add_if(values: set[str], value: Any) -> None:
    value_text = text(value)
    if value_text:
        values.add(value_text)


def to_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def to_float(value: Any) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def number_text(value: float | None) -> str:
    if value is None:
        return ""
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def row_bool(value: Any) -> bool:
    return text(value).lower() == "true"


def lower_bool_text(value: Any) -> str:
    value_text = text(value)
    if not value_text:
        return ""
    if value_text.lower() in {"true", "1", "yes", "y"}:
        return "true"
    if value_text.lower() in {"false", "0", "no", "n"}:
        return "false"
    return value_text


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build transfer-major policy profiles from rysxai school policy data."
    )
    parser.add_argument(
        "--transfer-policies-csv",
        type=Path,
        default=Path("data/processed/rysxai_transfer_policies.csv"),
    )
    parser.add_argument(
        "--major-seed-csv",
        type=Path,
        default=Path("data/seeds/rysxai_professions.full.csv"),
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
        "--output-school-profiles-csv",
        type=Path,
        default=Path("data/processed/rysxai_transfer_policies/transfer_policy_school_profiles_2026.csv"),
    )
    parser.add_argument(
        "--output-faculty-profiles-csv",
        type=Path,
        default=Path("data/processed/rysxai_transfer_policies/transfer_policy_faculty_profiles_2026.csv"),
    )
    parser.add_argument(
        "--output-major-mentions-csv",
        type=Path,
        default=Path("data/processed/rysxai_transfer_policies/transfer_policy_major_mentions_2026.csv"),
    )
    parser.add_argument(
        "--output-summary-csv",
        type=Path,
        default=Path("data/processed/rysxai_transfer_policies/transfer_policy_profile_summary_2026.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/rysxai_transfer_policies/transfer_policy_profiles_manifest_2026.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/rysxai_transfer_policies/transfer_policy_profiles_2026.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_rysxai_transfer_policy_profiles(
        transfer_policies_csv=args.transfer_policies_csv,
        major_seed_csv=args.major_seed_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        ai_replacement_csv=args.ai_replacement_csv,
        output_school_profiles_csv=args.output_school_profiles_csv,
        output_faculty_profiles_csv=args.output_faculty_profiles_csv,
        output_major_mentions_csv=args.output_major_mentions_csv,
        output_summary_csv=args.output_summary_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
