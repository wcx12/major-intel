"""Build a unified per-major risk and opportunity index."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/major_risk_master_index"
DEFAULT_REPORT_DIR = ROOT / "reports/major_risk_master_index"
SOURCE_LEVEL = "A/B/C"
SCHEMA_VERSION = "major_risk_master_index/v1"

MASTER_FIELDS = [
    "major_master_id",
    "major_code",
    "major_name",
    "major_level",
    "category",
    "subject",
    "degree",
    "source_presence_flags",
    "source_presence_count",
    "source_level_mix",
    "needs_review",
    "review_notes",
    "risk_signal_count",
    "opportunity_signal_count",
    "overall_review_bucket",
    "primary_risk_reasons",
    "primary_opportunity_reasons",
    "employment_warning_count",
    "employment_red_count",
    "employment_yellow_count",
    "employment_green_count",
    "employment_latest_risk_level",
    "employment_latest_report_year",
    "employment_red_years",
    "employment_yellow_years",
    "employment_green_years",
    "has_employment_high_risk_warning",
    "has_employment_red_warning",
    "has_employment_yellow_warning",
    "has_employment_green_signal",
    "official_policy_warning_count",
    "official_policy_record_types",
    "official_policy_years",
    "has_official_policy_warning",
    "ai_replacement_rank",
    "ai_replacement_score",
    "ai_replacement_level",
    "ai_confidence_score",
    "ai_candidate_count",
    "market_demand_count_national",
    "market_salary_reference_national",
    "market_job_sample_count",
    "market_demand_signal_level",
    "market_salary_signal_level",
    "market_activity_signal_level",
    "market_top_industries",
    "market_top_job_titles",
    "market_top_skills",
    "civil_service_opportunity_level",
    "civil_service_role_match_count",
    "civil_service_plan_num_sum",
    "civil_service_weighted_competition_ratio",
    "has_civil_service_match",
    "new_quality_support_category",
    "is_new_quality_productivity_major",
    "new_quality_directions",
    "new_quality_confidence",
    "new_quality_rule_score",
    "new_quality_policy_source_count",
    "new_quality_opportunity_risk_balance",
    "emerging_first_event_year",
    "emerging_latest_event_year",
    "emerging_event_types",
    "emerging_candidate_statuses",
    "emerging_source_count",
    "emerging_attachment_count",
    "emerging_evidence_count",
    "vocational_first_year",
    "vocational_latest_year",
    "vocational_years",
    "vocational_record_count",
    "vocational_province_count",
    "vocational_school_count",
    "vocational_latest_year_record_count",
    "vocational_latest_year_school_count",
    "rysxai_profession_ids",
]

SUMMARY_FIELDS = [
    "summary_id",
    "group_type",
    "group_value",
    "major_count",
    "high_risk_review_count",
    "employment_high_risk_count",
    "official_policy_warning_count",
    "ai_high_risk_count",
    "market_limited_count",
    "civil_limited_count",
    "opportunity_supported_count",
    "emerging_signal_count",
    "avg_risk_signal_count",
    "avg_opportunity_signal_count",
]

COVERAGE_FIELDS = [
    "source_presence_flag",
    "major_count",
    "high_risk_review_count",
    "employment_high_risk_count",
    "official_policy_warning_count",
    "ai_high_risk_count",
    "market_limited_count",
    "civil_limited_count",
    "opportunity_supported_count",
]

SOURCE_LEVEL_BY_FLAG = {
    "rysxai_seed": "C",
    "employment_warning": "B",
    "official_policy_warning": "A",
    "ai_replacement": "C",
    "market_observation": "C",
    "civil_service": "C",
    "new_quality": "B/C",
    "emerging_major": "A",
    "vocational_register": "A",
}

NON_MAJOR_NAMES = {
    "",
    "\u5907\u6ce8",
    "\u5408\u8ba1",
    "\u5c0f\u8ba1",
    "\u603b\u8ba1",
    "\u4e13\u4e1a\u540d\u79f0",
}


def build_major_risk_master_index(
    *,
    major_seed_csv: Path = ROOT / "data/seeds/rysxai_professions.full.csv",
    employment_summary_csv: Path = ROOT
    / "data/processed/major_risk_warnings/major_risk_warning_major_summary.csv",
    official_policy_warnings_csv: Path = ROOT
    / "data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv",
    ai_replacement_csv: Path = ROOT
    / "data/processed/ai_replacement/major_ai_replacement_ranking.csv",
    market_profiles_csv: Path = ROOT
    / "data/processed/rysxai_market/market_major_profiles_2026.csv",
    civil_service_major_csv: Path = ROOT
    / "data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv",
    new_quality_profiles_csv: Path = ROOT
    / "data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv",
    emerging_majors_csv: Path = ROOT
    / "data/processed/emerging_major_candidate_details/emerging_major_unique_majors_2026.csv",
    vocational_summary_csv: Path = ROOT
    / "data/processed/vocational_major_register/vocational_major_risk_link_summary_2013_2026.csv",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or date.today().isoformat()
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records: dict[str, dict[str, Any]] = {}
    source_counts = {
        "rysxai_seed": load_rysxai_seed(records, major_seed_csv),
        "employment_warning": load_employment_summary(records, employment_summary_csv),
        "official_policy_warning": load_official_policy_warnings(
            records, official_policy_warnings_csv
        ),
        "ai_replacement": load_ai_replacement(records, ai_replacement_csv),
        "market_observation": load_market_profiles(records, market_profiles_csv),
        "civil_service": load_civil_service(records, civil_service_major_csv),
        "new_quality": load_new_quality_profiles(records, new_quality_profiles_csv),
        "emerging_major": load_emerging_majors(records, emerging_majors_csv),
        "vocational_register": load_vocational_summary(records, vocational_summary_csv),
    }

    master_rows = finalize_rows(records.values())
    summary_rows = build_summary_rows(master_rows)
    coverage_rows = build_source_coverage_rows(master_rows)

    master_csv = output_dir / "major_risk_master_index_2026.csv"
    summary_csv = output_dir / "major_risk_master_index_summary_2026.csv"
    coverage_csv = output_dir / "major_risk_master_index_source_coverage_2026.csv"
    manifest_json = output_dir / "major_risk_master_index_manifest_2026.json"
    report_md = report_dir / "major_risk_master_index_2026.md"

    write_csv(master_csv, master_rows, MASTER_FIELDS)
    write_csv(summary_csv, summary_rows, SUMMARY_FIELDS)
    write_csv(coverage_csv, coverage_rows, COVERAGE_FIELDS)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "generated_at": generated_at,
        "source_level": SOURCE_LEVEL,
        "inputs": {
            "major_seed_csv": path_key(major_seed_csv),
            "employment_summary_csv": path_key(employment_summary_csv),
            "official_policy_warnings_csv": path_key(official_policy_warnings_csv),
            "ai_replacement_csv": path_key(ai_replacement_csv),
            "market_profiles_csv": path_key(market_profiles_csv),
            "civil_service_major_csv": path_key(civil_service_major_csv),
            "new_quality_profiles_csv": path_key(new_quality_profiles_csv),
            "emerging_majors_csv": path_key(emerging_majors_csv),
            "vocational_summary_csv": path_key(vocational_summary_csv),
        },
        "outputs": {
            "master_csv": path_key(master_csv),
            "summary_csv": path_key(summary_csv),
            "coverage_csv": path_key(coverage_csv),
            "manifest_json": path_key(manifest_json),
            "report_md": path_key(report_md),
        },
        "source_input_row_counts": source_counts,
        "row_counts": {
            "master_index": len(master_rows),
            "summary": len(summary_rows),
            "source_coverage": len(coverage_rows),
        },
        "overall_review_bucket_counts": dict(
            sorted(Counter(row["overall_review_bucket"] for row in master_rows).items())
        ),
        "major_level_counts": dict(
            sorted(Counter(row["major_level"] for row in master_rows).items())
        ),
        "risk_summary": {
            "high_risk_review_count": count_bucket(master_rows, "high_risk_review"),
            "employment_high_risk_count": count_true(
                master_rows, "has_employment_high_risk_warning"
            ),
            "official_policy_warning_count": count_true(
                master_rows, "has_official_policy_warning"
            ),
            "ai_high_risk_count": sum(1 for row in master_rows if has_ai_risk(row)),
            "market_limited_count": sum(1 for row in master_rows if has_market_limited(row)),
            "civil_limited_count": sum(1 for row in master_rows if has_civil_limited(row)),
            "opportunity_supported_count": sum(
                1 for row in master_rows if has_new_quality_opportunity(row)
            ),
            "emerging_signal_count": sum(1 for row in master_rows if has_emerging_signal(row)),
        },
        "checksums": {
            path_key(master_csv): file_info(master_csv),
            path_key(summary_csv): file_info(summary_csv),
            path_key(coverage_csv): file_info(coverage_csv),
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
    write_report(report_md, manifest, master_rows, coverage_rows)
    return manifest


def load_rysxai_seed(records: dict[str, dict[str, Any]], path: Path) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        record = ensure_record(
            records,
            row.get("major_code"),
            row.get("major_name"),
            row.get("level"),
            category=row.get("category"),
            subject=row.get("subject"),
            degree=row.get("degree"),
        )
        add_source(record, "rysxai_seed")
        add_unique(record, "rysxai_profession_ids", row.get("rysxai_profession_id"))
    return count


def load_employment_summary(records: dict[str, dict[str, Any]], path: Path) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        record = ensure_record(
            records,
            row.get("major_code"),
            row.get("standard_major_name"),
            row.get("education_level"),
            category=row.get("discipline"),
            subject=row.get("major_category"),
        )
        add_source(record, "employment_warning")
        set_max_number(record, "employment_red_count", row.get("red_count"))
        set_max_number(record, "employment_yellow_count", row.get("yellow_count"))
        set_max_number(record, "employment_green_count", row.get("green_count"))
        set_text_if_empty(record, "employment_latest_risk_level", row.get("latest_risk_level"))
        set_max_text(record, "employment_latest_report_year", row.get("latest_report_year"))
        set_text_if_empty(record, "employment_red_years", row.get("red_years"))
        set_text_if_empty(record, "employment_yellow_years", row.get("yellow_years"))
        set_text_if_empty(record, "employment_green_years", row.get("green_years"))
        if to_int(row.get("red_count")) or to_int(row.get("yellow_count")):
            record["has_employment_high_risk_warning"] = "true"
        if to_int(row.get("red_count")):
            record["has_employment_red_warning"] = "true"
        if to_int(row.get("yellow_count")):
            record["has_employment_yellow_warning"] = "true"
        if to_int(row.get("green_count")):
            record["has_employment_green_signal"] = "true"
    return count


def load_official_policy_warnings(
    records: dict[str, dict[str, Any]],
    path: Path,
) -> int:
    grouped: dict[str, dict[str, Any]] = {}
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        name = text(row.get("standard_major_name")) or text(row.get("reported_major_name"))
        if not text(row.get("major_code")) and name in NON_MAJOR_NAMES:
            continue
        key = master_key(row.get("major_code"), name, row.get("education_level"))
        item = grouped.setdefault(
            key,
            {
                "major_code": text(row.get("major_code")),
                "major_name": name,
                "major_level": normalize_level(row.get("education_level")),
                "category": text(row.get("discipline")),
                "subject": text(row.get("major_category")),
                "count": 0,
                "record_types": set(),
                "years": set(),
            },
        )
        item["count"] += 1
        add_if(item["record_types"], row.get("record_type"))
        add_if(item["years"], row.get("policy_year"))
    for item in grouped.values():
        record = ensure_record(
            records,
            item["major_code"],
            item["major_name"],
            item["major_level"],
            category=item["category"],
            subject=item["subject"],
        )
        add_source(record, "official_policy_warning")
        set_max_number(record, "official_policy_warning_count", item["count"])
        merge_delimited(record, "official_policy_record_types", item["record_types"])
        merge_delimited(record, "official_policy_years", item["years"])
        record["has_official_policy_warning"] = "true"
    return count


def load_ai_replacement(records: dict[str, dict[str, Any]], path: Path) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        record = ensure_record(
            records,
            row.get("major_code"),
            row.get("major_name"),
            row.get("level"),
        )
        add_source(record, "ai_replacement")
        set_best_rank(record, "ai_replacement_rank", row.get("rank"))
        set_best_ai_value(record, "ai_replacement_score", row.get("ai_replacement_score"))
        set_text_if_empty(record, "ai_replacement_level", row.get("ai_replacement_level"))
        set_best_ai_value(record, "ai_confidence_score", row.get("confidence_score"))
        set_max_number(record, "ai_candidate_count", row.get("candidate_count"))
    return count


def load_market_profiles(records: dict[str, dict[str, Any]], path: Path) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        record = ensure_record(
            records,
            row.get("major_code"),
            row.get("major_name"),
            row.get("level"),
            category=row.get("category"),
            subject=row.get("subject"),
            degree=row.get("degree"),
        )
        add_source(record, "market_observation")
        set_max_number(record, "market_demand_count_national", row.get("demand_count_national"))
        set_max_number(
            record, "market_salary_reference_national", row.get("salary_reference_national")
        )
        set_max_number(record, "market_job_sample_count", row.get("job_posting_sample_count"))
        set_text_if_empty(record, "market_demand_signal_level", row.get("market_demand_signal_level"))
        set_text_if_empty(record, "market_salary_signal_level", row.get("market_salary_signal_level"))
        set_text_if_empty(record, "market_activity_signal_level", row.get("market_activity_signal_level"))
        set_text_if_empty(record, "market_top_industries", row.get("top_industries"))
        set_text_if_empty(record, "market_top_job_titles", row.get("top_job_titles"))
        set_text_if_empty(record, "market_top_skills", row.get("top_skills"))
        copy_linked_flags(record, row)
    return count


def load_civil_service(records: dict[str, dict[str, Any]], path: Path) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        record = ensure_record(
            records,
            row.get("major_code"),
            row.get("major_name"),
            row.get("major_level"),
            category=row.get("category"),
            subject=row.get("subject"),
        )
        add_source(record, "civil_service")
        set_text_if_empty(record, "civil_service_opportunity_level", row.get("opportunity_level"))
        set_max_number(record, "civil_service_role_match_count", row.get("role_match_count"))
        set_max_number(record, "civil_service_plan_num_sum", row.get("plan_num_sum"))
        set_max_number(
            record,
            "civil_service_weighted_competition_ratio",
            row.get("weighted_competition_ratio"),
        )
        if true_text(row.get("has_civil_service_match")) or to_int(row.get("role_match_count")) > 0:
            record["has_civil_service_match"] = "true"
        copy_linked_flags(record, row)
    return count


def load_new_quality_profiles(records: dict[str, dict[str, Any]], path: Path) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        level = level_from_new_quality_type(row.get("major_type"))
        record = ensure_record(
            records,
            row.get("major_code"),
            row.get("major_name"),
            level,
            category=row.get("major_level2"),
            subject=row.get("major_level3"),
        )
        add_source(record, "new_quality")
        set_text_if_empty(record, "new_quality_support_category", row.get("support_category"))
        set_text_if_empty(
            record,
            "is_new_quality_productivity_major",
            row.get("is_new_quality_productivity_major"),
        )
        set_text_if_empty(record, "new_quality_directions", row.get("directions"))
        set_text_if_empty(record, "new_quality_confidence", row.get("confidence"))
        set_best_ai_value(record, "new_quality_rule_score", row.get("rule_score"))
        set_max_number(record, "new_quality_policy_source_count", row.get("policy_source_count"))
        set_text_if_empty(
            record,
            "new_quality_opportunity_risk_balance",
            row.get("opportunity_risk_balance"),
        )
        copy_linked_flags(record, row)
        copy_ai_fields(record, row)
        copy_market_fields(record, row)
        copy_civil_fields(record, row)
    return count


def load_emerging_majors(records: dict[str, dict[str, Any]], path: Path) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        record = ensure_record(
            records,
            row.get("major_code"),
            row.get("major_name"),
            row.get("major_level"),
            category=row.get("discipline_category"),
            subject=row.get("major_class"),
        )
        add_source(record, "emerging_major")
        set_max_text(record, "emerging_first_event_year", row.get("first_event_year"), reverse=False)
        set_max_text(record, "emerging_latest_event_year", row.get("latest_event_year"))
        set_text_if_empty(record, "emerging_event_types", row.get("event_types"))
        set_text_if_empty(record, "emerging_candidate_statuses", row.get("candidate_statuses"))
        set_max_number(record, "emerging_source_count", row.get("source_count"))
        set_max_number(record, "emerging_attachment_count", row.get("attachment_count"))
        set_max_number(record, "emerging_evidence_count", row.get("evidence_count"))
    return count


def load_vocational_summary(records: dict[str, dict[str, Any]], path: Path) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        record = ensure_record(
            records,
            row.get("major_code"),
            row.get("major_name"),
            "\u4e13\u79d1",
        )
        add_source(record, "vocational_register")
        set_max_text(record, "vocational_first_year", row.get("first_year"), reverse=False)
        set_max_text(record, "vocational_latest_year", row.get("latest_year"))
        set_text_if_empty(record, "vocational_years", row.get("years"))
        set_max_number(record, "vocational_record_count", row.get("record_count"))
        set_max_number(record, "vocational_province_count", row.get("province_count"))
        set_max_number(record, "vocational_school_count", row.get("school_count"))
        set_max_number(
            record,
            "vocational_latest_year_record_count",
            row.get("latest_year_record_count"),
        )
        set_max_number(
            record,
            "vocational_latest_year_school_count",
            row.get("latest_year_school_count"),
        )
        copy_linked_flags(record, row)
    return count


def ensure_record(
    records: dict[str, dict[str, Any]],
    major_code: Any,
    major_name: Any,
    major_level: Any,
    *,
    category: Any = "",
    subject: Any = "",
    degree: Any = "",
) -> dict[str, Any]:
    code = text(major_code)
    name = text(major_name)
    level = normalize_level(major_level)
    key = master_key(code, name, level)
    record = records.setdefault(key, empty_record(code, name, level))
    set_text_if_empty(record, "major_code", code)
    set_text_if_empty(record, "major_name", name)
    set_text_if_empty(record, "major_level", level)
    set_text_if_empty(record, "category", category)
    set_text_if_empty(record, "subject", subject)
    set_text_if_empty(record, "degree", degree)
    return record


def empty_record(major_code: str, major_name: str, major_level: str) -> dict[str, Any]:
    row = {field: "" for field in MASTER_FIELDS}
    row.update(
        {
            "major_master_id": stable_id("major_master", major_code, major_name, major_level),
            "major_code": major_code,
            "major_name": major_name,
            "major_level": major_level,
            "source_presence_flags": set(),
            "source_level_mix": set(),
            "needs_review": "false",
            "employment_warning_count": 0,
            "employment_red_count": 0,
            "employment_yellow_count": 0,
            "employment_green_count": 0,
            "has_employment_high_risk_warning": "false",
            "has_employment_red_warning": "false",
            "has_employment_yellow_warning": "false",
            "has_employment_green_signal": "false",
            "official_policy_warning_count": 0,
            "has_official_policy_warning": "false",
            "has_civil_service_match": "false",
            "risk_signal_count": 0,
            "opportunity_signal_count": 0,
            "rysxai_profession_ids": set(),
        }
    )
    return row


def finalize_rows(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        record["employment_warning_count"] = (
            to_int(record.get("employment_red_count"))
            + to_int(record.get("employment_yellow_count"))
            + to_int(record.get("employment_green_count"))
        )
        risk_reasons = risk_reasons_for(record)
        opportunity_reasons = opportunity_reasons_for(record)
        review_notes = review_notes_for(record)
        source_flags = sorted(record.get("source_presence_flags") or [])
        source_levels = sorted(record.get("source_level_mix") or [])
        profession_ids = sorted(record.get("rysxai_profession_ids") or [], key=natural_text_key)
        record["source_presence_flags"] = "|".join(source_flags)
        record["source_presence_count"] = len(source_flags)
        record["source_level_mix"] = "|".join(source_levels)
        record["risk_signal_count"] = len(risk_reasons)
        record["opportunity_signal_count"] = len(opportunity_reasons)
        record["overall_review_bucket"] = overall_review_bucket(record, risk_reasons, opportunity_reasons)
        record["primary_risk_reasons"] = "|".join(risk_reasons)
        record["primary_opportunity_reasons"] = "|".join(opportunity_reasons)
        record["needs_review"] = bool_text(bool(review_notes))
        record["review_notes"] = "|".join(review_notes)
        record["rysxai_profession_ids"] = "|".join(profession_ids)
        for field in [
            "employment_warning_count",
            "employment_red_count",
            "employment_yellow_count",
            "employment_green_count",
            "official_policy_warning_count",
            "source_presence_count",
            "risk_signal_count",
            "opportunity_signal_count",
        ]:
            record[field] = str(to_int(record.get(field)))
        rows.append({field: record.get(field, "") for field in MASTER_FIELDS})
    return sorted(rows, key=master_sort_key)


def risk_reasons_for(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if true_text(row.get("has_employment_high_risk_warning")):
        reasons.append("employment_red_or_yellow_warning")
    if true_text(row.get("has_official_policy_warning")):
        reasons.append("official_policy_setting_warning")
    if has_ai_risk(row):
        reasons.append("ai_replacement_high_signal")
    if has_market_limited(row):
        reasons.append("limited_market_signal")
    if has_civil_limited(row):
        reasons.append("weak_civil_service_opportunity")
    return reasons


def opportunity_reasons_for(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if has_new_quality_opportunity(row):
        reasons.append("new_quality_policy_support")
    if has_market_opportunity(row):
        reasons.append("strong_market_signal")
    if has_civil_opportunity(row):
        reasons.append("civil_service_role_opportunity")
    if has_emerging_signal(row):
        reasons.append("official_emerging_major_signal")
    return reasons


def overall_review_bucket(
    row: dict[str, Any],
    risk_reasons: list[str],
    opportunity_reasons: list[str],
) -> str:
    employment = true_text(row.get("has_employment_high_risk_warning"))
    official_policy = true_text(row.get("has_official_policy_warning"))
    ai_risk = has_ai_risk(row)
    market_limited = has_market_limited(row)
    civil_limited = has_civil_limited(row)
    risk_count = len(risk_reasons)
    opportunity_count = len(opportunity_reasons)
    if employment and (official_policy or ai_risk or market_limited or civil_limited):
        return "high_risk_review"
    if official_policy and (ai_risk or market_limited or civil_limited):
        return "high_risk_review"
    if employment or official_policy:
        return "employment_or_policy_warning_review"
    if ai_risk and (market_limited or civil_limited):
        return "ai_market_risk_review"
    if risk_count >= 2:
        return "multi_signal_risk_review"
    if risk_count >= 1 and opportunity_count >= 1:
        return "opportunity_with_risk_flags"
    if risk_count >= 1:
        return "single_signal_watch"
    if opportunity_count >= 2:
        return "opportunity_watch"
    if opportunity_count == 1:
        return "opportunity_signal_reference"
    return "baseline_reference"


def review_notes_for(row: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    if text(row.get("major_name")) in NON_MAJOR_NAMES:
        notes.append("non_major_or_table_note_name")
    if not text(row.get("major_code")):
        notes.append("missing_major_code")
    if not text(row.get("major_level")):
        notes.append("missing_major_level")
    if text(row.get("major_name")) and len(text(row.get("major_name"))) <= 1:
        notes.append("very_short_major_name")
    return notes


def build_summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[("all", "all")].append(row)
        for field, group_type in [
            ("overall_review_bucket", "overall_review_bucket"),
            ("major_level", "major_level"),
            ("category", "category"),
            ("source_presence_count", "source_presence_count"),
            ("risk_signal_count", "risk_signal_count"),
            ("opportunity_signal_count", "opportunity_signal_count"),
        ]:
            value = text(row.get(field)) or "<blank>"
            groups[(group_type, value)].append(row)
    result: list[dict[str, Any]] = []
    for (group_type, group_value), group_rows in sorted(groups.items()):
        result.append(summary_row(group_type, group_value, group_rows))
    return result


def build_source_coverage_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for flag in sorted(SOURCE_LEVEL_BY_FLAG):
        group_rows = [
            row for row in rows if flag in split_values(row.get("source_presence_flags"))
        ]
        result.append(
            {
                "source_presence_flag": flag,
                "major_count": len(group_rows),
                "high_risk_review_count": count_bucket(group_rows, "high_risk_review"),
                "employment_high_risk_count": count_true(
                    group_rows, "has_employment_high_risk_warning"
                ),
                "official_policy_warning_count": count_true(
                    group_rows, "has_official_policy_warning"
                ),
                "ai_high_risk_count": sum(1 for row in group_rows if has_ai_risk(row)),
                "market_limited_count": sum(1 for row in group_rows if has_market_limited(row)),
                "civil_limited_count": sum(1 for row in group_rows if has_civil_limited(row)),
                "opportunity_supported_count": sum(
                    1 for row in group_rows if has_new_quality_opportunity(row)
                ),
            }
        )
    return result


def summary_row(group_type: str, group_value: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary_id": stable_id("major_risk_summary", group_type, group_value),
        "group_type": group_type,
        "group_value": group_value,
        "major_count": len(rows),
        "high_risk_review_count": count_bucket(rows, "high_risk_review"),
        "employment_high_risk_count": count_true(rows, "has_employment_high_risk_warning"),
        "official_policy_warning_count": count_true(rows, "has_official_policy_warning"),
        "ai_high_risk_count": sum(1 for row in rows if has_ai_risk(row)),
        "market_limited_count": sum(1 for row in rows if has_market_limited(row)),
        "civil_limited_count": sum(1 for row in rows if has_civil_limited(row)),
        "opportunity_supported_count": sum(1 for row in rows if has_new_quality_opportunity(row)),
        "emerging_signal_count": sum(1 for row in rows if has_emerging_signal(row)),
        "avg_risk_signal_count": mean_text([to_float(row.get("risk_signal_count")) for row in rows]),
        "avg_opportunity_signal_count": mean_text(
            [to_float(row.get("opportunity_signal_count")) for row in rows]
        ),
    }


def write_report(
    path: Path,
    manifest: dict[str, Any],
    rows: list[dict[str, Any]],
    coverage_rows: list[dict[str, Any]],
) -> None:
    bucket_counts = Counter(row["overall_review_bucket"] for row in rows)
    high_risk_rows = [
        row
        for row in rows
        if row["overall_review_bucket"] in {"high_risk_review", "ai_market_risk_review"}
    ][:30]
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Major Risk Master Index",
        "",
        f"- Built at: {manifest['generated_at']}",
        f"- Master index rows: {manifest['row_counts']['master_index']}",
        f"- Source level mix: {manifest['source_level']}",
        f"- High-risk review rows: {manifest['risk_summary']['high_risk_review_count']}",
        f"- Employment red/yellow linked rows: {manifest['risk_summary']['employment_high_risk_count']}",
        f"- Official policy warning linked rows: {manifest['risk_summary']['official_policy_warning_count']}",
        f"- AI high-signal rows: {manifest['risk_summary']['ai_high_risk_count']}",
        f"- New-quality supported rows: {manifest['risk_summary']['opportunity_supported_count']}",
        "",
        "## Review Buckets",
        "",
        "| bucket | rows |",
        "|---|---:|",
    ]
    for bucket, count in sorted(bucket_counts.items()):
        lines.append(f"| {bucket} | {count} |")
    lines.extend(
        [
            "",
            "## Source Coverage",
            "",
            "| source flag | majors | high-risk review | employment high-risk | official policy |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in coverage_rows:
        lines.append(
            "| {source_presence_flag} | {major_count} | {high_risk_review_count} | "
            "{employment_high_risk_count} | {official_policy_warning_count} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Sample High-Risk Rows",
            "",
            "| major | code | level | bucket | risk reasons | opportunity reasons |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in high_risk_rows:
        lines.append(
            "| {major_name} | {major_code} | {major_level} | {overall_review_bucket} | "
            "{primary_risk_reasons} | {primary_opportunity_reasons} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Master index: `{manifest['outputs']['master_csv']}`",
            f"- Summary: `{manifest['outputs']['summary_csv']}`",
            f"- Source coverage: `{manifest['outputs']['coverage_csv']}`",
            f"- Manifest: `{manifest['outputs']['manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- This is an integrated review index. It keeps official records, public warning lists, and third-party market signals in separate columns.",
            "- `overall_review_bucket` is a screening label, not an admissions recommendation or deterministic employment forecast.",
            "- Use `source_presence_flags`, `source_level_mix`, and the source-specific fields before making a judgment about any single major.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def copy_linked_flags(record: dict[str, Any], row: dict[str, str]) -> None:
    set_max_number(record, "official_policy_warning_count", row.get("official_policy_warning_count"))
    merge_delimited(record, "official_policy_record_types", split_values(row.get("official_policy_record_types")))
    merge_delimited(record, "official_policy_years", split_values(row.get("official_policy_years")))
    if true_text(row.get("has_official_policy_warning")):
        record["has_official_policy_warning"] = "true"
    if true_text(row.get("has_employment_high_risk_warning")):
        record["has_employment_high_risk_warning"] = "true"
    if true_text(row.get("has_employment_red_warning")):
        record["has_employment_red_warning"] = "true"
    if true_text(row.get("has_employment_yellow_warning")):
        record["has_employment_yellow_warning"] = "true"
    if true_text(row.get("has_employment_green_signal")):
        record["has_employment_green_signal"] = "true"


def copy_ai_fields(record: dict[str, Any], row: dict[str, str]) -> None:
    set_best_rank(record, "ai_replacement_rank", row.get("ai_replacement_rank"))
    set_best_ai_value(record, "ai_replacement_score", row.get("ai_replacement_score"))
    set_text_if_empty(record, "ai_replacement_level", row.get("ai_replacement_level"))
    set_best_ai_value(record, "ai_confidence_score", row.get("ai_confidence_score"))
    set_max_number(record, "ai_candidate_count", row.get("ai_candidate_count"))


def copy_market_fields(record: dict[str, Any], row: dict[str, str]) -> None:
    set_max_number(record, "market_demand_count_national", row.get("market_demand_count_national"))
    set_max_number(record, "market_salary_reference_national", row.get("market_salary_reference_national"))
    set_max_number(record, "market_job_sample_count", row.get("market_job_sample_count"))
    set_text_if_empty(record, "market_demand_signal_level", row.get("market_demand_signal_level"))
    set_text_if_empty(record, "market_salary_signal_level", row.get("market_salary_signal_level"))
    set_text_if_empty(record, "market_activity_signal_level", row.get("market_activity_signal_level"))


def copy_civil_fields(record: dict[str, Any], row: dict[str, str]) -> None:
    set_text_if_empty(record, "civil_service_opportunity_level", row.get("civil_service_opportunity_level"))
    set_max_number(record, "civil_service_role_match_count", row.get("civil_service_role_match_count"))
    set_max_number(record, "civil_service_plan_num_sum", row.get("civil_service_plan_num_sum"))
    if true_text(row.get("has_civil_service_match")):
        record["has_civil_service_match"] = "true"


def add_source(record: dict[str, Any], flag: str) -> None:
    record.setdefault("source_presence_flags", set()).add(flag)
    for level in SOURCE_LEVEL_BY_FLAG.get(flag, "").split("/"):
        if level:
            record.setdefault("source_level_mix", set()).add(level)


def add_unique(record: dict[str, Any], field: str, value: Any) -> None:
    value_text = text(value)
    if value_text:
        record.setdefault(field, set()).add(value_text)


def set_text_if_empty(record: dict[str, Any], field: str, value: Any) -> None:
    value_text = text(value)
    if value_text and not text(record.get(field)):
        record[field] = value_text


def set_max_text(
    record: dict[str, Any],
    field: str,
    value: Any,
    *,
    reverse: bool = True,
) -> None:
    value_text = text(value)
    current = text(record.get(field))
    if not value_text:
        return
    if not current:
        record[field] = value_text
        return
    if (value_text > current) == reverse:
        record[field] = value_text


def set_max_number(record: dict[str, Any], field: str, value: Any) -> None:
    numeric = to_float(value)
    if numeric is None:
        return
    current = to_float(record.get(field))
    if current is None or numeric > current:
        record[field] = number_text(numeric)


def set_best_rank(record: dict[str, Any], field: str, value: Any) -> None:
    numeric = to_float(value)
    if numeric is None:
        return
    current = to_float(record.get(field))
    if current is None or numeric < current:
        record[field] = number_text(numeric)


def set_best_ai_value(record: dict[str, Any], field: str, value: Any) -> None:
    numeric = to_float(value)
    if numeric is None:
        return
    current = to_float(record.get(field))
    if current is None or numeric > current:
        record[field] = number_text(numeric)


def merge_delimited(record: dict[str, Any], field: str, values: Iterable[Any]) -> None:
    current = set(split_values(record.get(field)))
    for value in values:
        value_text = text(value)
        if value_text:
            current.add(value_text)
    record[field] = "|".join(sorted(current))


def has_ai_risk(row: dict[str, Any]) -> bool:
    level = text(row.get("ai_replacement_level")).lower()
    score = to_float(row.get("ai_replacement_score"))
    high_labels = {
        "high",
        "very_high",
        "\u9ad8",
        "\u8f83\u9ad8",
        "\u5f88\u9ad8",
    }
    return level in high_labels or (score is not None and score >= 60)


def has_market_limited(row: dict[str, Any]) -> bool:
    values = {
        text(row.get("market_demand_signal_level")).lower(),
        text(row.get("market_salary_signal_level")).lower(),
        text(row.get("market_activity_signal_level")).lower(),
    }
    return "limited" in values


def has_civil_limited(row: dict[str, Any]) -> bool:
    level = text(row.get("civil_service_opportunity_level")).lower()
    return level in {"none", "limited"} and "civil_service" in source_flags(row)


def has_new_quality_opportunity(row: dict[str, Any]) -> bool:
    support = text(row.get("new_quality_support_category"))
    label = text(row.get("is_new_quality_productivity_major"))
    return support in {"core", "related"} or label in {
        "\u662f",
        "\u76f8\u5173",
        "yes",
        "related",
    }


def has_market_opportunity(row: dict[str, Any]) -> bool:
    values = {
        text(row.get("market_demand_signal_level")).lower(),
        text(row.get("market_salary_signal_level")).lower(),
    }
    return bool(values & {"high", "very_high"})


def has_civil_opportunity(row: dict[str, Any]) -> bool:
    level = text(row.get("civil_service_opportunity_level")).lower()
    return level in {"medium", "high", "very_high"} and to_int(
        row.get("civil_service_role_match_count")
    ) > 0


def has_emerging_signal(row: dict[str, Any]) -> bool:
    return to_int(row.get("emerging_source_count")) > 0 or bool(
        text(row.get("emerging_event_types"))
    )


def level_from_new_quality_type(value: Any) -> str:
    value_text = text(value)
    if value_text == "1":
        return "\u672c\u79d1"
    if value_text == "2":
        return "\u4e13\u79d1"
    return normalize_level(value_text)


def normalize_level(value: Any) -> str:
    value_text = text(value)
    if not value_text:
        return ""
    if "\u7814\u7a76\u751f" in value_text or "\u7855" in value_text or "\u535a" in value_text:
        return "\u7814\u7a76\u751f"
    if "\u4e13\u79d1" in value_text or "\u9ad8\u804c" in value_text or "\u9ad8\u4e13" in value_text:
        return "\u4e13\u79d1"
    if "\u672c\u79d1" in value_text or "\u5b66\u58eb" in value_text:
        return "\u672c\u79d1"
    return value_text


def master_key(major_code: Any, major_name: Any, major_level: Any) -> str:
    code = text(major_code)
    name = text(major_name)
    level = normalize_level(major_level)
    if code:
        return f"code:{code}|level:{level}"
    return f"name:{name}|level:{level}"


def stable_id(prefix: str, *parts: Any) -> str:
    key = "|".join(text(part) for part in parts)
    return prefix + ":" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def master_sort_key(row: dict[str, Any]) -> tuple[int, str, str, str]:
    bucket_order = {
        "high_risk_review": 0,
        "employment_or_policy_warning_review": 1,
        "ai_market_risk_review": 2,
        "multi_signal_risk_review": 3,
        "opportunity_with_risk_flags": 4,
        "single_signal_watch": 5,
        "opportunity_watch": 6,
        "opportunity_signal_reference": 7,
        "baseline_reference": 8,
    }
    return (
        bucket_order.get(text(row.get("overall_review_bucket")), 99),
        f"{999 - to_int(row.get('risk_signal_count')):03d}",
        text(row.get("major_code")),
        text(row.get("major_name")),
    )


def natural_text_key(value: Any) -> tuple[int, str]:
    value_text = text(value)
    return (to_int(value_text, default=10**9), value_text)


def safe_read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    if not Path(path).exists():
        return iter(())
    return read_csv_rows(Path(path))


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def path_key(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def split_values(value: Any) -> list[str]:
    return [part.strip() for part in text(value).split("|") if part.strip()]


def source_flags(row: dict[str, Any]) -> set[str]:
    value = row.get("source_presence_flags")
    if isinstance(value, set):
        return {text(item) for item in value if text(item)}
    if isinstance(value, (list, tuple)):
        return {text(item) for item in value if text(item)}
    return set(split_values(value))


def add_if(values: set[str], value: Any) -> None:
    value_text = text(value)
    if value_text:
        values.add(value_text)


def count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if true_text(row.get(field)))


def count_bucket(rows: list[dict[str, Any]], bucket: str) -> int:
    return sum(1 for row in rows if text(row.get("overall_review_bucket")) == bucket)


def mean_text(values: list[float | None]) -> str:
    numeric = [value for value in values if value is not None]
    if not numeric:
        return ""
    return number_text(sum(numeric) / len(numeric))


def to_int(value: Any, *, default: int = 0) -> int:
    number = to_float(value)
    return int(number) if number is not None else default


def to_float(value: Any) -> float | None:
    try:
        value_text = text(value)
        if not value_text:
            return None
        return float(value_text)
    except (TypeError, ValueError):
        return None


def number_text(value: Any) -> str:
    number = to_float(value)
    if number is None:
        return ""
    if number.is_integer():
        return str(int(number))
    return f"{number:.2f}".rstrip("0").rstrip(".")


def true_text(value: Any) -> bool:
    return text(value).lower() == "true"


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the unified major risk master index.")
    parser.add_argument("--major-seed-csv", type=Path, default=ROOT / "data/seeds/rysxai_professions.full.csv")
    parser.add_argument(
        "--employment-summary-csv",
        type=Path,
        default=ROOT / "data/processed/major_risk_warnings/major_risk_warning_major_summary.csv",
    )
    parser.add_argument(
        "--official-policy-warnings-csv",
        type=Path,
        default=ROOT
        / "data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv",
    )
    parser.add_argument(
        "--ai-replacement-csv",
        type=Path,
        default=ROOT / "data/processed/ai_replacement/major_ai_replacement_ranking.csv",
    )
    parser.add_argument(
        "--market-profiles-csv",
        type=Path,
        default=ROOT / "data/processed/rysxai_market/market_major_profiles_2026.csv",
    )
    parser.add_argument(
        "--civil-service-major-csv",
        type=Path,
        default=ROOT
        / "data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv",
    )
    parser.add_argument(
        "--new-quality-profiles-csv",
        type=Path,
        default=ROOT
        / "data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv",
    )
    parser.add_argument(
        "--emerging-majors-csv",
        type=Path,
        default=ROOT
        / "data/processed/emerging_major_candidate_details/emerging_major_unique_majors_2026.csv",
    )
    parser.add_argument(
        "--vocational-summary-csv",
        type=Path,
        default=ROOT
        / "data/processed/vocational_major_register/vocational_major_risk_link_summary_2013_2026.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_major_risk_master_index(
        major_seed_csv=args.major_seed_csv,
        employment_summary_csv=args.employment_summary_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        ai_replacement_csv=args.ai_replacement_csv,
        market_profiles_csv=args.market_profiles_csv,
        civil_service_major_csv=args.civil_service_major_csv,
        new_quality_profiles_csv=args.new_quality_profiles_csv,
        emerging_majors_csv=args.emerging_majors_csv,
        vocational_summary_csv=args.vocational_summary_csv,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        generated_at=args.generated_at,
    )
    print(
        json.dumps(
            {
                "dataset": "major_risk_master_index",
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
                "risk_summary": manifest["risk_summary"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
