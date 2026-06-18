"""Build risk-linkable profiles from rysxai major introduction snapshots."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "rysxai_major_intro_risk_profiles/v1"
SOURCE_LEVEL = "C"

PROFILE_FIELDS = [
    "profile_id",
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "degree",
    "limit_year",
    "selection_advice",
    "enrollment_scale",
    "univ_count",
    "apply_plan_ratio",
    "has_major_detail",
    "has_major_course",
    "has_undergraduate_to_graduate",
    "has_similar_majors",
    "major_detail_chars",
    "major_course_chars",
    "undergraduate_to_graduate_chars",
    "similar_majors_chars",
    "content_sha256",
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
    "ai_replacement_match_count",
    "ai_replacement_match_basis",
    "ai_replacement_rank",
    "ai_replacement_score",
    "ai_replacement_level",
    "ai_confidence_score",
    "ai_candidate_count",
    "ai_top_risky_jobs",
    "source_level",
    "data_scope",
    "info_url",
    "captured_at",
    "source_snapshot_path",
    "raw_source_path",
]

SUMMARY_FIELDS = [
    "level",
    "profile_count",
    "with_major_detail_count",
    "with_major_course_count",
    "with_undergraduate_to_graduate_count",
    "with_similar_majors_count",
    "employment_linked_profile_count",
    "employment_high_risk_profile_count",
    "employment_red_profile_count",
    "employment_yellow_profile_count",
    "employment_green_profile_count",
    "official_policy_linked_profile_count",
    "ai_linked_profile_count",
    "avg_ai_replacement_score",
    "max_ai_replacement_score",
]


def build_rysxai_major_intro_risk_profiles(
    *,
    major_introductions_csv: Path,
    employment_warnings_csv: Path,
    official_policy_warnings_csv: Path,
    ai_replacement_csv: Path,
    output_profiles_csv: Path,
    output_summary_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    intro_rows = list(read_csv_rows(major_introductions_csv))
    employment_refs = load_employment_warning_refs(employment_warnings_csv)
    policy_refs = load_policy_warning_refs(official_policy_warnings_csv)
    ai_refs = load_ai_replacement_refs(ai_replacement_csv)
    employment_by_code, employment_by_name = build_ref_indexes(employment_refs)
    policy_by_code, policy_by_name = build_ref_indexes(policy_refs)
    ai_by_profession_id, ai_by_code, ai_by_name = build_ai_indexes(ai_refs)

    profile_rows: list[dict[str, Any]] = []
    profile_ids: set[str] = set()
    duplicate_profile_ids = 0
    missing_sections: Counter[str] = Counter()
    linked_employment = 0
    linked_high_risk = 0
    linked_policy = 0
    linked_ai = 0

    for row in intro_rows:
        profile = build_profile_row(
            row,
            employment_by_code=employment_by_code,
            employment_by_name=employment_by_name,
            policy_by_code=policy_by_code,
            policy_by_name=policy_by_name,
            ai_by_profession_id=ai_by_profession_id,
            ai_by_code=ai_by_code,
            ai_by_name=ai_by_name,
        )
        if profile["profile_id"] in profile_ids:
            duplicate_profile_ids += 1
        profile_ids.add(profile["profile_id"])
        for key in (
            "has_major_detail",
            "has_major_course",
            "has_undergraduate_to_graduate",
            "has_similar_majors",
        ):
            if profile[key] == "false":
                missing_sections[key.removeprefix("has_")] += 1
        if int(profile["employment_warning_count"]):
            linked_employment += 1
        if profile["has_employment_high_risk_warning"] == "true":
            linked_high_risk += 1
        if int(profile["official_policy_warning_count"]):
            linked_policy += 1
        if int(profile["ai_replacement_match_count"]):
            linked_ai += 1
        profile_rows.append(profile)

    write_csv(output_profiles_csv, profile_rows, PROFILE_FIELDS)
    summary_rows = build_summary_rows(profile_rows)
    write_csv(output_summary_csv, summary_rows, SUMMARY_FIELDS)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "source_level": SOURCE_LEVEL,
        "major_introductions_csv": str(major_introductions_csv),
        "employment_warnings_csv": str(employment_warnings_csv),
        "official_policy_warnings_csv": str(official_policy_warnings_csv),
        "ai_replacement_csv": str(ai_replacement_csv),
        "output_profiles_csv": str(output_profiles_csv),
        "output_summary_csv": str(output_summary_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "input_profile_count": len(intro_rows),
        "output_profile_count": len(profile_rows),
        "unique_profile_id_count": len(profile_ids),
        "duplicate_profile_id_count": duplicate_profile_ids,
        "level_counts": dict(sorted(Counter(row["level"] for row in profile_rows).items())),
        "missing_section_counts": dict(sorted(missing_sections.items())),
        "linked_employment_profile_count": linked_employment,
        "linked_high_risk_profile_count": linked_high_risk,
        "linked_policy_profile_count": linked_policy,
        "linked_ai_replacement_profile_count": linked_ai,
        "summary_row_count": len(summary_rows),
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(output_report_md, manifest, summary_rows)
    return manifest


def build_profile_row(
    row: dict[str, str],
    *,
    employment_by_code: dict[str, list[dict[str, str]]],
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_code: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
    ai_by_profession_id: dict[str, list[dict[str, str]]],
    ai_by_code: dict[str, list[dict[str, str]]],
    ai_by_name: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    profession_id = text(row.get("rysxai_profession_id"))
    major_code = text(row.get("major_code"))
    major_name = text(row.get("major_name"))
    level = text(row.get("level"))
    profile_id = major_profile_id(profession_id, major_code, major_name, level)
    sections = {
        "major_detail": text(row.get("major_detail")),
        "major_course": text(row.get("major_course")),
        "undergraduate_to_graduate": text(row.get("undergraduate_to_graduate")),
        "similar_majors": text(row.get("similar_majors")),
    }
    employment_refs, employment_basis = match_refs(
        major_code,
        major_name,
        employment_by_code,
        employment_by_name,
    )
    policy_refs, policy_basis = match_refs(
        major_code,
        major_name,
        policy_by_code,
        policy_by_name,
    )
    ai_refs, ai_basis = match_ai_refs(
        profession_id,
        major_code,
        major_name,
        ai_by_profession_id,
        ai_by_code,
        ai_by_name,
    )
    best_ai = best_ai_ref(ai_refs)
    return {
        "profile_id": profile_id,
        "rysxai_profession_id": profession_id,
        "major_code": major_code,
        "major_name": major_name,
        "level": level,
        "degree": text(row.get("degree")),
        "limit_year": text(row.get("limit_year")),
        "selection_advice": text(row.get("selection_advice")),
        "enrollment_scale": text(row.get("enrollment_scale")),
        "univ_count": text(row.get("univ_count")),
        "apply_plan_ratio": text(row.get("apply_plan_ratio")),
        "has_major_detail": bool_text(bool(sections["major_detail"])),
        "has_major_course": bool_text(bool(sections["major_course"])),
        "has_undergraduate_to_graduate": bool_text(bool(sections["undergraduate_to_graduate"])),
        "has_similar_majors": bool_text(bool(sections["similar_majors"])),
        "major_detail_chars": len(sections["major_detail"]),
        "major_course_chars": len(sections["major_course"]),
        "undergraduate_to_graduate_chars": len(sections["undergraduate_to_graduate"]),
        "similar_majors_chars": len(sections["similar_majors"]),
        "content_sha256": content_digest(sections),
        **summarize_employment_refs(employment_refs, employment_basis),
        **summarize_policy_refs(policy_refs, policy_basis),
        **summarize_ai_refs(ai_refs, ai_basis, best_ai),
        "source_level": SOURCE_LEVEL,
        "data_scope": "third_party_major_introduction_text",
        "info_url": text(row.get("info_url")),
        "captured_at": text(row.get("captured_at")),
        "source_snapshot_path": source_snapshot_path(profession_id),
        "raw_source_path": raw_source_path(profession_id),
    }


def build_summary_rows(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in profile_rows:
        grouped[text(row.get("level"))].append(row)

    summary_rows: list[dict[str, Any]] = []
    for level, rows in sorted(grouped.items()):
        ai_scores = [
            float(row["ai_replacement_score"])
            for row in rows
            if text(row.get("ai_replacement_score"))
        ]
        summary_rows.append(
            {
                "level": level,
                "profile_count": len(rows),
                "with_major_detail_count": count_true(rows, "has_major_detail"),
                "with_major_course_count": count_true(rows, "has_major_course"),
                "with_undergraduate_to_graduate_count": count_true(
                    rows, "has_undergraduate_to_graduate"
                ),
                "with_similar_majors_count": count_true(rows, "has_similar_majors"),
                "employment_linked_profile_count": count_positive(
                    rows, "employment_warning_count"
                ),
                "employment_high_risk_profile_count": count_true(
                    rows, "has_employment_high_risk_warning"
                ),
                "employment_red_profile_count": count_true(
                    rows, "has_employment_red_warning"
                ),
                "employment_yellow_profile_count": count_true(
                    rows, "has_employment_yellow_warning"
                ),
                "employment_green_profile_count": count_true(
                    rows, "has_employment_green_signal"
                ),
                "official_policy_linked_profile_count": count_positive(
                    rows, "official_policy_warning_count"
                ),
                "ai_linked_profile_count": count_positive(
                    rows, "ai_replacement_match_count"
                ),
                "avg_ai_replacement_score": (
                    round(sum(ai_scores) / len(ai_scores), 2) if ai_scores else ""
                ),
                "max_ai_replacement_score": round(max(ai_scores), 2) if ai_scores else "",
            }
        )
    return summary_rows


def load_employment_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
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


def load_ai_replacement_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        refs.append(
            {
                "profession_id": text(row.get("profession_id")),
                "major_code": text(row.get("major_code")),
                "major_name": text(row.get("major_name")),
                "rank": text(row.get("rank")),
                "score": text(row.get("ai_replacement_score")),
                "level": text(row.get("ai_replacement_level")),
                "confidence_score": text(row.get("confidence_score")),
                "candidate_count": text(row.get("candidate_count")),
                "top_risky_jobs": text(row.get("top_risky_jobs")),
            }
        )
    return refs


def build_ref_indexes(
    refs: list[dict[str, str]],
) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for ref in refs:
        if ref["major_code"]:
            by_code[ref["major_code"]].append(ref)
        if ref["major_name"]:
            by_name[ref["major_name"]].append(ref)
    return by_code, by_name


def build_ai_indexes(
    refs: list[dict[str, str]],
) -> tuple[
    dict[str, list[dict[str, str]]],
    dict[str, list[dict[str, str]]],
    dict[str, list[dict[str, str]]],
]:
    by_profession_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for ref in refs:
        if ref["profession_id"]:
            by_profession_id[ref["profession_id"]].append(ref)
        if ref["major_code"]:
            by_code[ref["major_code"]].append(ref)
        if ref["major_name"]:
            by_name[ref["major_name"]].append(ref)
    return by_profession_id, by_code, by_name


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


def match_ai_refs(
    profession_id: str,
    major_code: str,
    major_name: str,
    by_profession_id: dict[str, list[dict[str, str]]],
    by_code: dict[str, list[dict[str, str]]],
    by_name: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, str]], str]:
    refs_by_key: dict[str, dict[str, str]] = {}
    basis: list[str] = []
    if profession_id and profession_id in by_profession_id:
        basis.append("profession_id")
        for ref in by_profession_id[profession_id]:
            refs_by_key[ai_ref_key(ref)] = ref
    if major_code and major_code in by_code:
        basis.append("code")
        for ref in by_code[major_code]:
            refs_by_key[ai_ref_key(ref)] = ref
    if major_name and major_name in by_name:
        basis.append("name")
        for ref in by_name[major_name]:
            refs_by_key[ai_ref_key(ref)] = ref
    refs = sorted(refs_by_key.values(), key=ai_sort_key)
    return refs, "+".join(basis)


def summarize_employment_refs(
    refs: list[dict[str, str]],
    basis: str,
) -> dict[str, Any]:
    risk_levels = ordered_unique([ref["risk_level"] for ref in refs], order=["red", "yellow", "green"])
    years = ordered_unique([ref["year"] for ref in refs])
    ids = ordered_unique([ref["id"] for ref in refs])
    has_red = "red" in risk_levels
    has_yellow = "yellow" in risk_levels
    has_green = "green" in risk_levels
    return {
        "employment_warning_count": len(refs),
        "employment_risk_levels": "|".join(risk_levels),
        "employment_warning_years": "|".join(years),
        "employment_warning_match_basis": basis,
        "employment_warning_record_ids": "|".join(ids),
        "has_employment_high_risk_warning": bool_text(has_red or has_yellow),
        "has_employment_red_warning": bool_text(has_red),
        "has_employment_yellow_warning": bool_text(has_yellow),
        "has_employment_green_signal": bool_text(has_green),
    }


def summarize_policy_refs(refs: list[dict[str, str]], basis: str) -> dict[str, Any]:
    record_types = ordered_unique([ref["record_type"] for ref in refs])
    years = ordered_unique([ref["year"] for ref in refs])
    ids = ordered_unique([ref["id"] for ref in refs])
    return {
        "official_policy_warning_count": len(refs),
        "official_policy_record_types": "|".join(record_types),
        "official_policy_years": "|".join(years),
        "official_policy_match_basis": basis,
        "official_policy_warning_ids": "|".join(ids),
        "has_official_policy_warning": bool_text(bool(refs)),
    }


def summarize_ai_refs(
    refs: list[dict[str, str]],
    basis: str,
    best_ai: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "ai_replacement_match_count": len(refs),
        "ai_replacement_match_basis": basis,
        "ai_replacement_rank": text(best_ai.get("rank") if best_ai else ""),
        "ai_replacement_score": text(best_ai.get("score") if best_ai else ""),
        "ai_replacement_level": text(best_ai.get("level") if best_ai else ""),
        "ai_confidence_score": text(best_ai.get("confidence_score") if best_ai else ""),
        "ai_candidate_count": text(best_ai.get("candidate_count") if best_ai else ""),
        "ai_top_risky_jobs": text(best_ai.get("top_risky_jobs") if best_ai else ""),
    }


def best_ai_ref(refs: list[dict[str, str]]) -> dict[str, str] | None:
    return min(refs, key=ai_sort_key) if refs else None


def ai_sort_key(ref: dict[str, str]) -> tuple[int, str, str]:
    return (to_int(ref.get("rank"), default=10**9), ref.get("major_code", ""), ref.get("major_name", ""))


def ai_ref_key(ref: dict[str, str]) -> str:
    return "|".join([ref.get("profession_id", ""), ref.get("major_code", ""), ref.get("major_name", "")])


def write_report(
    path: Path,
    manifest: dict[str, Any],
    summary_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Rysxai Major Introduction Risk-Link Report",
        "",
        f"- Source level: {manifest['source_level']}",
        f"- Input profile rows: {manifest['input_profile_count']}",
        f"- Output profile rows: {manifest['output_profile_count']}",
        f"- Duplicate profile IDs: {manifest['duplicate_profile_id_count']}",
        f"- Employment-warning linked profiles: {manifest['linked_employment_profile_count']}",
        f"- Red/yellow linked profiles: {manifest['linked_high_risk_profile_count']}",
        f"- Official-policy linked profiles: {manifest['linked_policy_profile_count']}",
        f"- AI replacement-risk linked profiles: {manifest['linked_ai_replacement_profile_count']}",
        "",
        "## Level Summary",
        "",
        "| Level | Profiles | Red/yellow linked | Policy linked | AI linked | Avg AI score |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            "| {level} | {profile_count} | {employment_high_risk_profile_count} | "
            "{official_policy_linked_profile_count} | {ai_linked_profile_count} | "
            "{avg_ai_replacement_score} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Profiles: `{manifest['output_profiles_csv']}`",
            f"- Summary: `{manifest['output_summary_csv']}`",
            f"- Manifest: `{manifest['output_manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- This is a source-level C support dataset. It is suitable for retrieval, feature extraction, and review sampling.",
            "- It must not be interpreted as an official employment warning, official professional-setting decision, or deterministic AI-risk prediction.",
            "- Risk linkage is exact by major code/name where available and keeps matched source IDs for audit.",
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


def source_snapshot_path(profession_id: str) -> str:
    if not profession_id:
        return ""
    return f"data/processed/rysxai_major_intros/profession_{profession_id}_major_intro_snapshot.json"


def raw_source_path(profession_id: str) -> str:
    if not profession_id:
        return ""
    preferred = Path(
        f"data/raw/rysxai_major_intros/full_20260611_intro/profession_{profession_id}_info.raw.json"
    )
    if preferred.exists():
        return preferred.as_posix()
    matches = sorted(
        Path("data/raw/rysxai_major_intros").glob(f"*/profession_{profession_id}_info.raw.json")
    )
    return matches[0].as_posix() if matches else preferred.as_posix()


def content_digest(sections: dict[str, str]) -> str:
    payload = json.dumps(sections, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def major_profile_id(
    profession_id: str,
    major_code: str,
    major_name: str,
    level: str,
) -> str:
    key = "|".join([profession_id, major_code, major_name, level])
    return "major_intro:" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if text(row.get(field)) == "true")


def count_positive(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if to_int(row.get(field), default=0) > 0)


def ordered_unique(values: list[str], *, order: list[str] | None = None) -> list[str]:
    seen = {value for value in values if value}
    if order:
        return [value for value in order if value in seen] + sorted(seen - set(order))
    return sorted(seen)


def to_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build risk-linkable rysxai major introduction profiles."
    )
    parser.add_argument(
        "--major-introductions-csv",
        type=Path,
        default=Path("data/processed/rysxai_major_intros/major_introductions_full_20260611_intro.csv"),
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
        "--output-profiles-csv",
        type=Path,
        default=Path("data/processed/rysxai_major_intros/major_intro_risk_profiles_20260611.csv"),
    )
    parser.add_argument(
        "--output-summary-csv",
        type=Path,
        default=Path("data/processed/rysxai_major_intros/major_intro_risk_profile_summary_20260611.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/rysxai_major_intros/major_intro_risk_profiles_manifest_20260611.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/rysxai_major_intros/major_intro_risk_profiles_20260611.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_rysxai_major_intro_risk_profiles(
        major_introductions_csv=args.major_introductions_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        ai_replacement_csv=args.ai_replacement_csv,
        output_profiles_csv=args.output_profiles_csv,
        output_summary_csv=args.output_summary_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
