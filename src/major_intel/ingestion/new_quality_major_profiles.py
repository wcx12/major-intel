"""Build packaged new-quality-productivity major support profiles."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "new_quality_major_profiles/v1"
SOURCE_LEVEL = "B/C"

PROFILE_FIELDS = [
    "new_quality_profile_id",
    "major_special_id",
    "major_code",
    "major_name",
    "major_type",
    "major_level2",
    "major_level3",
    "evaluation_label",
    "support_category",
    "is_new_quality_productivity_major",
    "directions",
    "direction_count",
    "confidence",
    "rule_score",
    "rationale",
    "policy_source_count",
    "policy_source_ids",
    "policy_evidence_excerpt",
    "official_major_source",
    "sample_coverage",
    "sample_coverage_count",
    "qingbei_sample",
    "tier_985_sample",
    "tier_211_sample",
    "shuangfei_sample",
    "needs_review",
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
    "market_profile_match_count",
    "market_demand_count_national",
    "market_salary_reference_national",
    "market_demand_signal_level",
    "market_salary_signal_level",
    "market_activity_signal_level",
    "market_job_sample_count",
    "civil_service_match_count",
    "civil_service_opportunity_level",
    "civil_service_role_match_count",
    "civil_service_plan_num_sum",
    "has_civil_service_match",
    "transfer_policy_match_count",
    "transfer_policy_mentioned_in_school_count",
    "transfer_policy_high_difficulty_school_count",
    "has_transfer_policy_mention",
    "opportunity_risk_balance",
    "source_level",
    "data_scope",
]

TIER_SAMPLE_FIELDS = [
    "tier_sample_id",
    "new_quality_profile_id",
    "major_special_id",
    "major_code",
    "major_name",
    "major_type",
    "major_level2",
    "major_level3",
    "school_tier",
    "sample_school_id",
    "sample_school_name",
    "sample_school_rank",
    "sample_school_found",
    "tier_offer_count",
    "evaluation_label",
    "support_category",
    "is_new_quality_productivity_major",
    "directions",
    "confidence",
    "rule_score",
    "rationale",
    "policy_source_ids",
    "policy_evidence_excerpt",
    "official_major_source",
    "school_sample_source",
    "estimation_method",
    "needs_review",
    "source_level",
    "data_scope",
]

POLICY_SOURCE_FIELDS = [
    "policy_source_profile_id",
    "direction",
    "source_id",
    "source_title",
    "source_url",
    "source_year",
    "issuing_org",
    "keyword",
    "evidence_excerpt",
    "source_level",
    "data_scope",
]

SUMMARY_FIELDS = [
    "summary_id",
    "group_type",
    "group_value",
    "profile_count",
    "core_count",
    "related_count",
    "weak_related_count",
    "not_related_count",
    "needs_review_count",
    "high_confidence_count",
    "medium_confidence_count",
    "low_confidence_count",
    "avg_rule_score",
    "policy_source_linked_count",
    "tier_sample_coverage_avg",
    "employment_high_risk_count",
    "official_policy_linked_count",
    "ai_linked_count",
    "market_linked_count",
    "civil_service_linked_count",
    "transfer_policy_linked_count",
]


def build_new_quality_major_profiles(
    *,
    input_summary_csv: Path,
    input_detail_csv: Path,
    input_policy_sources_csv: Path,
    employment_warnings_csv: Path,
    official_policy_warnings_csv: Path,
    ai_replacement_csv: Path,
    market_profiles_csv: Path,
    civil_service_major_csv: Path,
    transfer_policy_major_csv: Path,
    output_profiles_csv: Path,
    output_tier_samples_csv: Path,
    output_policy_sources_csv: Path,
    output_summary_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    summary_source_rows = list(read_csv_rows(input_summary_csv))
    detail_source_rows = list(read_csv_rows(input_detail_csv))
    policy_source_rows = list(read_csv_rows(input_policy_sources_csv))

    employment_by_code, employment_by_name = build_ref_indexes(
        load_employment_warning_refs(employment_warnings_csv)
    )
    policy_by_code, policy_by_name = build_ref_indexes(
        load_policy_warning_refs(official_policy_warnings_csv)
    )
    ai_by_code, ai_by_name = build_ref_indexes(load_ai_refs(ai_replacement_csv))
    market_by_code, market_by_name = build_ref_indexes(load_market_refs(market_profiles_csv))
    civil_by_code, civil_by_name = build_ref_indexes(
        load_civil_service_refs(civil_service_major_csv)
    )
    transfer_by_code, transfer_by_name = build_ref_indexes(
        load_transfer_policy_refs(transfer_policy_major_csv)
    )

    profile_rows: list[dict[str, Any]] = []
    profile_ids: set[str] = set()
    duplicate_profile_ids = 0
    for row in summary_source_rows:
        profile = build_profile_row(
            row,
            employment_by_code=employment_by_code,
            employment_by_name=employment_by_name,
            policy_by_code=policy_by_code,
            policy_by_name=policy_by_name,
            ai_by_code=ai_by_code,
            ai_by_name=ai_by_name,
            market_by_code=market_by_code,
            market_by_name=market_by_name,
            civil_by_code=civil_by_code,
            civil_by_name=civil_by_name,
            transfer_by_code=transfer_by_code,
            transfer_by_name=transfer_by_name,
        )
        if profile["new_quality_profile_id"] in profile_ids:
            duplicate_profile_ids += 1
        profile_ids.add(profile["new_quality_profile_id"])
        profile_rows.append(profile)

    profile_id_by_key = {
        profile_key(row): row["new_quality_profile_id"] for row in profile_rows
    }
    tier_rows = [
        build_tier_sample_row(row, profile_id_by_key) for row in detail_source_rows
    ]
    policy_rows = [build_policy_source_row(row) for row in policy_source_rows]
    grouped_summary_rows = build_summary_rows(profile_rows)

    write_csv(output_profiles_csv, profile_rows, PROFILE_FIELDS)
    write_csv(output_tier_samples_csv, tier_rows, TIER_SAMPLE_FIELDS)
    write_csv(output_policy_sources_csv, policy_rows, POLICY_SOURCE_FIELDS)
    write_csv(output_summary_csv, grouped_summary_rows, SUMMARY_FIELDS)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "source_level": SOURCE_LEVEL,
        "input_summary_csv": str(input_summary_csv),
        "input_detail_csv": str(input_detail_csv),
        "input_policy_sources_csv": str(input_policy_sources_csv),
        "employment_warnings_csv": str(employment_warnings_csv),
        "official_policy_warnings_csv": str(official_policy_warnings_csv),
        "ai_replacement_csv": str(ai_replacement_csv),
        "market_profiles_csv": str(market_profiles_csv),
        "civil_service_major_csv": str(civil_service_major_csv),
        "transfer_policy_major_csv": str(transfer_policy_major_csv),
        "output_profiles_csv": str(output_profiles_csv),
        "output_tier_samples_csv": str(output_tier_samples_csv),
        "output_policy_sources_csv": str(output_policy_sources_csv),
        "output_summary_csv": str(output_summary_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "input_profile_count": len(summary_source_rows),
        "profile_row_count": len(profile_rows),
        "unique_profile_id_count": len(profile_ids),
        "duplicate_profile_id_count": duplicate_profile_ids,
        "tier_sample_row_count": len(tier_rows),
        "policy_source_row_count": len(policy_rows),
        "summary_row_count": len(grouped_summary_rows),
        "support_category_counts": dict(
            sorted(Counter(row["support_category"] for row in profile_rows).items())
        ),
        "confidence_counts": dict(
            sorted(Counter(row["confidence"] for row in profile_rows).items())
        ),
        "direction_counts": direction_counts(profile_rows),
        "linked_high_risk_profile_count": count_true(
            profile_rows, "has_employment_high_risk_warning"
        ),
        "linked_policy_profile_count": count_true(
            profile_rows, "has_official_policy_warning"
        ),
        "linked_ai_profile_count": count_positive(
            profile_rows, "ai_replacement_match_count"
        ),
        "linked_market_profile_count": count_positive(
            profile_rows, "market_profile_match_count"
        ),
        "linked_civil_service_profile_count": count_true(
            profile_rows, "has_civil_service_match"
        ),
        "linked_transfer_policy_profile_count": count_true(
            profile_rows, "has_transfer_policy_mention"
        ),
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(output_report_md, manifest, profile_rows)
    return manifest


def build_profile_row(
    row: dict[str, str],
    *,
    employment_by_code: dict[str, list[dict[str, str]]],
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_code: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
    ai_by_code: dict[str, list[dict[str, str]]],
    ai_by_name: dict[str, list[dict[str, str]]],
    market_by_code: dict[str, list[dict[str, str]]],
    market_by_name: dict[str, list[dict[str, str]]],
    civil_by_code: dict[str, list[dict[str, str]]],
    civil_by_name: dict[str, list[dict[str, str]]],
    transfer_by_code: dict[str, list[dict[str, str]]],
    transfer_by_name: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    major_code = text(row.get("major_code"))
    major_name = text(row.get("major_name"))
    major_type = text(row.get("major_type"))
    major_special_id = text(row.get("major_special_id"))
    profile_id = new_quality_profile_id(major_special_id, major_code, major_name, major_type)
    employment_refs, _ = match_refs(
        major_code, major_name, employment_by_code, employment_by_name
    )
    policy_refs, _ = match_refs(major_code, major_name, policy_by_code, policy_by_name)
    ai_refs, _ = match_refs(major_code, major_name, ai_by_code, ai_by_name)
    market_refs, _ = match_refs(major_code, major_name, market_by_code, market_by_name)
    civil_refs, _ = match_refs(major_code, major_name, civil_by_code, civil_by_name)
    transfer_refs, _ = match_refs(major_code, major_name, transfer_by_code, transfer_by_name)
    best_ai = best_numeric_ref(ai_refs, "rank", reverse=False)
    best_market = best_numeric_ref(market_refs, "demand_count_national")
    best_civil = best_numeric_ref(civil_refs, "role_match_count")
    best_transfer = best_numeric_ref(transfer_refs, "mentioned_in_school_count")
    support_category = normalize_support_category(row.get("evaluation_label"))

    result = {
        "new_quality_profile_id": profile_id,
        "major_special_id": major_special_id,
        "major_code": major_code,
        "major_name": major_name,
        "major_type": major_type,
        "major_level2": text(row.get("major_level2")),
        "major_level3": text(row.get("major_level3")),
        "evaluation_label": text(row.get("evaluation_label")),
        "support_category": support_category,
        "is_new_quality_productivity_major": text(
            row.get("is_new_quality_productivity_major")
        ),
        "directions": text(row.get("directions")),
        "direction_count": len(split_values(row.get("directions"), sep=";")),
        "confidence": text(row.get("confidence")),
        "rule_score": text(row.get("score")),
        "rationale": text(row.get("rationale")),
        "policy_source_count": len(split_values(row.get("policy_source_ids"), sep=";")),
        "policy_source_ids": text(row.get("policy_source_ids")),
        "policy_evidence_excerpt": text(row.get("policy_evidence_excerpt")),
        "official_major_source": text(row.get("official_major_source")),
        "sample_coverage": text(row.get("sample_coverage")),
        "sample_coverage_count": parse_sample_coverage(row.get("sample_coverage")),
        "qingbei_sample": text(row.get("qingbei_sample")),
        "tier_985_sample": text(row.get("tier_985_sample")),
        "tier_211_sample": text(row.get("tier_211_sample")),
        "shuangfei_sample": text(row.get("shuangfei_sample")),
        "needs_review": text(row.get("needs_review")),
        **summarize_employment_refs(employment_refs),
        **summarize_policy_refs(policy_refs),
        **summarize_ai_refs(ai_refs, best_ai),
        **summarize_market_refs(market_refs, best_market),
        **summarize_civil_refs(civil_refs, best_civil),
        **summarize_transfer_refs(transfer_refs, best_transfer),
        "opportunity_risk_balance": "",
        "source_level": SOURCE_LEVEL,
        "data_scope": "new_quality_productivity_major_support_profile",
    }
    result["opportunity_risk_balance"] = opportunity_risk_balance(result)
    return result


def build_tier_sample_row(
    row: dict[str, str],
    profile_id_by_key: dict[str, str],
) -> dict[str, Any]:
    profile_id = profile_id_by_key.get(profile_key(row)) or new_quality_profile_id(
        row.get("major_special_id"),
        row.get("major_code"),
        row.get("major_name"),
        row.get("major_type"),
    )
    return {
        "tier_sample_id": stable_id(
            "new_quality_tier",
            profile_id,
            row.get("school_tier"),
            row.get("sample_school_id"),
        ),
        "new_quality_profile_id": profile_id,
        "major_special_id": text(row.get("major_special_id")),
        "major_code": text(row.get("major_code")),
        "major_name": text(row.get("major_name")),
        "major_type": text(row.get("major_type")),
        "major_level2": text(row.get("major_level2")),
        "major_level3": text(row.get("major_level3")),
        "school_tier": text(row.get("school_tier")),
        "sample_school_id": text(row.get("sample_school_id")),
        "sample_school_name": text(row.get("sample_school_name")),
        "sample_school_rank": text(row.get("sample_school_rank")),
        "sample_school_found": text(row.get("sample_school_found")),
        "tier_offer_count": to_int(row.get("tier_offer_count")),
        "evaluation_label": text(row.get("evaluation_label")),
        "support_category": normalize_support_category(row.get("evaluation_label")),
        "is_new_quality_productivity_major": text(
            row.get("is_new_quality_productivity_major")
        ),
        "directions": text(row.get("directions")),
        "confidence": text(row.get("confidence")),
        "rule_score": text(row.get("score")),
        "rationale": text(row.get("rationale")),
        "policy_source_ids": text(row.get("policy_source_ids")),
        "policy_evidence_excerpt": text(row.get("policy_evidence_excerpt")),
        "official_major_source": text(row.get("official_major_source")),
        "school_sample_source": text(row.get("school_sample_source")),
        "estimation_method": text(row.get("estimation_method")),
        "needs_review": text(row.get("needs_review")),
        "source_level": SOURCE_LEVEL,
        "data_scope": "new_quality_productivity_tier_sample",
    }


def build_policy_source_row(row: dict[str, str]) -> dict[str, Any]:
    return {
        "policy_source_profile_id": stable_id(
            "new_quality_policy_source",
            row.get("direction"),
            row.get("source_id"),
            row.get("keyword"),
        ),
        "direction": text(row.get("direction")),
        "source_id": text(row.get("source_id")),
        "source_title": text(row.get("source_title")),
        "source_url": text(row.get("source_url")),
        "source_year": text(row.get("source_year")),
        "issuing_org": text(row.get("issuing_org")),
        "keyword": text(row.get("keyword")),
        "evidence_excerpt": text(row.get("evidence_excerpt")),
        "source_level": "B",
        "data_scope": "new_quality_productivity_policy_evidence_source",
    }


def build_summary_rows(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in profile_rows:
        groups[("all", "all")].append(row)
        for field, group_type in [
            ("support_category", "support_category"),
            ("evaluation_label", "evaluation_label"),
            ("confidence", "confidence"),
            ("major_type", "major_type"),
            ("major_level2", "major_level2"),
            ("major_level3", "major_level3"),
        ]:
            value = text(row.get(field))
            if value:
                groups[(group_type, value)].append(row)
        for direction in split_values(row.get("directions"), sep=";"):
            groups[("direction", direction)].append(row)

    rows: list[dict[str, Any]] = []
    for (group_type, group_value), group_rows in sorted(groups.items()):
        rule_scores = [
            to_float(row.get("rule_score"))
            for row in group_rows
            if to_float(row.get("rule_score")) is not None
        ]
        coverage = [
            to_float(row.get("sample_coverage_count"))
            for row in group_rows
            if to_float(row.get("sample_coverage_count")) is not None
        ]
        rows.append(
            {
                "summary_id": stable_id("new_quality_summary", group_type, group_value),
                "group_type": group_type,
                "group_value": group_value,
                "profile_count": len(group_rows),
                "core_count": count_equals(group_rows, "support_category", "core"),
                "related_count": count_equals(group_rows, "support_category", "related"),
                "weak_related_count": count_equals(
                    group_rows, "support_category", "weak_related"
                ),
                "not_related_count": count_equals(
                    group_rows, "support_category", "not_related"
                ),
                "needs_review_count": count_equals(
                    group_rows, "support_category", "needs_review"
                ),
                "high_confidence_count": count_equals(group_rows, "confidence", "high"),
                "medium_confidence_count": count_equals(
                    group_rows, "confidence", "medium"
                ),
                "low_confidence_count": count_equals(group_rows, "confidence", "low"),
                "avg_rule_score": mean_text(rule_scores),
                "policy_source_linked_count": count_positive(
                    group_rows, "policy_source_count"
                ),
                "tier_sample_coverage_avg": mean_text(coverage),
                "employment_high_risk_count": count_true(
                    group_rows, "has_employment_high_risk_warning"
                ),
                "official_policy_linked_count": count_true(
                    group_rows, "has_official_policy_warning"
                ),
                "ai_linked_count": count_positive(
                    group_rows, "ai_replacement_match_count"
                ),
                "market_linked_count": count_positive(
                    group_rows, "market_profile_match_count"
                ),
                "civil_service_linked_count": count_true(
                    group_rows, "has_civil_service_match"
                ),
                "transfer_policy_linked_count": count_true(
                    group_rows, "has_transfer_policy_mention"
                ),
            }
        )
    return rows


def load_employment_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in safe_read_csv_rows(path):
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
    for row in safe_read_csv_rows(path):
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


def load_ai_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in safe_read_csv_rows(path):
        refs.append(
            {
                "id": stable_id(
                    "ai", row.get("profession_id"), row.get("major_code"), row.get("major_name")
                ),
                "major_code": text(row.get("major_code")),
                "major_name": text(row.get("major_name")),
                "rank": text(row.get("rank")),
                "score": text(row.get("ai_replacement_score")),
                "level": text(row.get("ai_replacement_level")),
                "confidence_score": text(row.get("confidence_score")),
                "candidate_count": text(row.get("candidate_count")),
            }
        )
    return refs


def load_market_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in safe_read_csv_rows(path):
        refs.append(
            {
                "id": text(row.get("market_profile_id")),
                "major_code": text(row.get("major_code")),
                "major_name": text(row.get("major_name")),
                "demand_count_national": text(row.get("demand_count_national")),
                "salary_reference_national": text(row.get("salary_reference_national")),
                "demand_signal_level": text(row.get("market_demand_signal_level")),
                "salary_signal_level": text(row.get("market_salary_signal_level")),
                "activity_signal_level": text(row.get("market_activity_signal_level")),
                "job_sample_count": text(row.get("job_posting_sample_count")),
            }
        )
    return refs


def load_civil_service_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in safe_read_csv_rows(path):
        refs.append(
            {
                "id": text(row.get("civil_service_major_id")),
                "major_code": text(row.get("major_code")),
                "major_name": text(row.get("major_name")),
                "opportunity_level": text(row.get("opportunity_level")),
                "role_match_count": text(row.get("role_match_count")),
                "plan_num_sum": text(row.get("plan_num_sum")),
            }
        )
    return refs


def load_transfer_policy_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in safe_read_csv_rows(path):
        refs.append(
            {
                "id": text(row.get("transfer_policy_major_id")),
                "major_code": text(row.get("major_code")),
                "major_name": text(row.get("major_name")),
                "mentioned_in_school_count": text(row.get("mentioned_in_school_count")),
                "high_difficulty_school_count": text(
                    row.get("high_difficulty_school_count")
                ),
            }
        )
    return refs


def build_ref_indexes(
    refs: list[dict[str, str]],
) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    by_code: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    by_name: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for ref in refs:
        ref_id = ref_identity(ref)
        if text(ref.get("major_code")):
            by_code[text(ref.get("major_code"))][ref_id] = ref
        if text(ref.get("major_name")):
            by_name[text(ref.get("major_name"))][ref_id] = ref
    return (
        {key: sorted(values.values(), key=ref_sort_key) for key, values in by_code.items()},
        {key: sorted(values.values(), key=ref_sort_key) for key, values in by_name.items()},
    )


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
            refs_by_id[ref_identity(ref)] = ref
    if major_name and major_name in by_name:
        basis.append("name")
        for ref in by_name[major_name]:
            refs_by_id[ref_identity(ref)] = ref
    return sorted(refs_by_id.values(), key=ref_sort_key), "+".join(basis)


def summarize_employment_refs(refs: list[dict[str, str]]) -> dict[str, Any]:
    risk_levels = ordered_unique(
        [ref["risk_level"] for ref in refs], order=["red", "yellow", "green"]
    )
    has_red = "red" in risk_levels
    has_yellow = "yellow" in risk_levels
    has_green = "green" in risk_levels
    return {
        "employment_warning_count": len(refs),
        "employment_risk_levels": "|".join(risk_levels),
        "employment_warning_years": "|".join(ordered_unique([ref["year"] for ref in refs])),
        "employment_warning_record_ids": "|".join(
            ordered_unique([ref["id"] for ref in refs])
        ),
        "has_employment_high_risk_warning": bool_text(has_red or has_yellow),
        "has_employment_red_warning": bool_text(has_red),
        "has_employment_yellow_warning": bool_text(has_yellow),
        "has_employment_green_signal": bool_text(has_green),
    }


def summarize_policy_refs(refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "official_policy_warning_count": len(refs),
        "official_policy_record_types": "|".join(
            ordered_unique([ref["record_type"] for ref in refs])
        ),
        "official_policy_years": "|".join(ordered_unique([ref["year"] for ref in refs])),
        "official_policy_warning_ids": "|".join(
            ordered_unique([ref["id"] for ref in refs])
        ),
        "has_official_policy_warning": bool_text(bool(refs)),
    }


def summarize_ai_refs(
    refs: list[dict[str, str]],
    best_ai: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "ai_replacement_match_count": len(refs),
        "ai_replacement_rank": text(best_ai.get("rank") if best_ai else ""),
        "ai_replacement_score": text(best_ai.get("score") if best_ai else ""),
        "ai_replacement_level": text(best_ai.get("level") if best_ai else ""),
        "ai_confidence_score": text(best_ai.get("confidence_score") if best_ai else ""),
        "ai_candidate_count": text(best_ai.get("candidate_count") if best_ai else ""),
    }


def summarize_market_refs(
    refs: list[dict[str, str]],
    best_market: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "market_profile_match_count": len(refs),
        "market_demand_count_national": text(
            best_market.get("demand_count_national") if best_market else ""
        ),
        "market_salary_reference_national": text(
            best_market.get("salary_reference_national") if best_market else ""
        ),
        "market_demand_signal_level": text(
            best_market.get("demand_signal_level") if best_market else ""
        ),
        "market_salary_signal_level": text(
            best_market.get("salary_signal_level") if best_market else ""
        ),
        "market_activity_signal_level": text(
            best_market.get("activity_signal_level") if best_market else ""
        ),
        "market_job_sample_count": text(
            best_market.get("job_sample_count") if best_market else ""
        ),
    }


def summarize_civil_refs(
    refs: list[dict[str, str]],
    best_civil: dict[str, str] | None,
) -> dict[str, Any]:
    return {
        "civil_service_match_count": len(refs),
        "civil_service_opportunity_level": text(
            best_civil.get("opportunity_level") if best_civil else ""
        ),
        "civil_service_role_match_count": text(
            best_civil.get("role_match_count") if best_civil else ""
        ),
        "civil_service_plan_num_sum": text(
            best_civil.get("plan_num_sum") if best_civil else ""
        ),
        "has_civil_service_match": bool_text(
            best_civil is not None and to_int(best_civil.get("role_match_count")) > 0
        ),
    }


def summarize_transfer_refs(
    refs: list[dict[str, str]],
    best_transfer: dict[str, str] | None,
) -> dict[str, Any]:
    mentioned = to_int(
        best_transfer.get("mentioned_in_school_count") if best_transfer else ""
    )
    return {
        "transfer_policy_match_count": len(refs),
        "transfer_policy_mentioned_in_school_count": text(
            best_transfer.get("mentioned_in_school_count") if best_transfer else ""
        ),
        "transfer_policy_high_difficulty_school_count": text(
            best_transfer.get("high_difficulty_school_count") if best_transfer else ""
        ),
        "has_transfer_policy_mention": bool_text(best_transfer is not None and mentioned > 0),
    }


def opportunity_risk_balance(row: dict[str, Any]) -> str:
    support = text(row.get("support_category"))
    high_employment = text(row.get("has_employment_high_risk_warning")) == "true"
    ai_score = to_float(row.get("ai_replacement_score"))
    ai_high = ai_score is not None and ai_score >= 50
    market_demand = text(row.get("market_demand_signal_level"))
    if support in {"core", "related"} and not high_employment and not ai_high:
        return "policy_supported_lower_observed_risk"
    if support in {"core", "related"} and (high_employment or ai_high):
        return "policy_supported_with_risk_flags"
    if support == "weak_related" and market_demand in {"very_high", "high"}:
        return "weak_policy_match_high_market_signal"
    if high_employment or ai_high:
        return "risk_flags_without_policy_support"
    return "neutral_or_insufficient_signal"


def write_report(
    path: Path,
    manifest: dict[str, Any],
    profile_rows: list[dict[str, Any]],
) -> None:
    top_rows = sorted(
        profile_rows,
        key=lambda row: (
            support_sort_value(row.get("support_category")),
            -to_int(row.get("rule_score")),
            row.get("major_code", ""),
        ),
    )[:30]
    lines = [
        "# New Quality Major Support Profile Report",
        "",
        f"- Source level: {manifest['source_level']}",
        f"- Input profiles: {manifest['input_profile_count']}",
        f"- Output profiles: {manifest['profile_row_count']}",
        f"- Tier sample rows: {manifest['tier_sample_row_count']}",
        f"- Policy source rows: {manifest['policy_source_row_count']}",
        f"- Summary rows: {manifest['summary_row_count']}",
        f"- Red/yellow employment-warning linked profiles: {manifest['linked_high_risk_profile_count']}",
        f"- Official-policy linked profiles: {manifest['linked_policy_profile_count']}",
        f"- AI replacement linked profiles: {manifest['linked_ai_profile_count']}",
        f"- Market-observation linked profiles: {manifest['linked_market_profile_count']}",
        "",
        "## Top Supported Profiles",
        "",
        "| Major | Code | Label | Directions | Confidence | Score | Risk flags |",
        "|---|---|---|---|---|---:|---|",
    ]
    for row in top_rows:
        risk_flags = []
        if row["has_employment_high_risk_warning"] == "true":
            risk_flags.append("employment")
        if row["has_official_policy_warning"] == "true":
            risk_flags.append("policy")
        if to_float(row.get("ai_replacement_score")) and to_float(row.get("ai_replacement_score")) >= 50:
            risk_flags.append("ai")
        lines.append(
            "| {major_name} | {major_code} | {evaluation_label} | {directions} | "
            "{confidence} | {rule_score} | {risk_flags} |".format(
                risk_flags=",".join(risk_flags) or "-",
                **row,
            )
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Profiles: `{manifest['output_profiles_csv']}`",
            f"- Tier samples: `{manifest['output_tier_samples_csv']}`",
            f"- Policy sources: `{manifest['output_policy_sources_csv']}`",
            f"- Summary: `{manifest['output_summary_csv']}`",
            f"- Manifest: `{manifest['output_manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- This is a support/opportunity dataset, not a high-risk warning list.",
            "- Policy/source evidence is source-level B where official policy pages were used; local school offering samples and heuristic labels are support-level evidence.",
            "- Use `opportunity_risk_balance` and linked source IDs to review high-opportunity but still risky majors.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def direction_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        for direction in split_values(row.get("directions"), sep=";"):
            counter[direction] += 1
    return dict(counter.most_common())


def profile_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            text(row.get("major_special_id")),
            text(row.get("major_code")),
            text(row.get("major_name")),
            text(row.get("major_type")),
        ]
    )


def new_quality_profile_id(
    major_special_id: Any,
    major_code: Any,
    major_name: Any,
    major_type: Any,
) -> str:
    return stable_id("new_quality_major", major_special_id, major_code, major_name, major_type)


def stable_id(prefix: str, *parts: Any) -> str:
    key = "|".join(text(part) for part in parts)
    return prefix + ":" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def normalize_support_category(value: Any) -> str:
    label = text(value)
    if label == "是":
        return "core"
    if label == "相关":
        return "related"
    if label == "弱相关":
        return "weak_related"
    if label == "否":
        return "not_related"
    if "复核" in label:
        return "needs_review"
    return "unknown"


def support_sort_value(value: Any) -> int:
    return {
        "core": 0,
        "related": 1,
        "weak_related": 2,
        "needs_review": 3,
        "not_related": 4,
    }.get(text(value), 9)


def parse_sample_coverage(value: Any) -> int:
    coverage = text(value)
    if "/" not in coverage:
        return 0
    return to_int(coverage.split("/", 1)[0])


def split_values(value: Any, *, sep: str = "|") -> list[str]:
    return [part.strip() for part in text(value).split(sep) if part.strip()]


def ref_identity(ref: dict[str, str]) -> str:
    return text(ref.get("id")) or stable_id(
        "ref",
        ref.get("major_code"),
        ref.get("major_name"),
        ref.get("year"),
        ref.get("record_type"),
        ref.get("risk_level"),
    )


def ref_sort_key(ref: dict[str, str]) -> tuple[str, str, str]:
    return (
        text(ref.get("year")),
        text(ref.get("record_type")) or text(ref.get("risk_level")),
        ref_identity(ref),
    )


def best_numeric_ref(
    refs: list[dict[str, str]],
    field: str,
    *,
    reverse: bool = True,
) -> dict[str, str] | None:
    if not refs:
        return None
    if reverse:
        return max(refs, key=lambda ref: (to_float(ref.get(field)) or 0, ref_identity(ref)))
    return min(
        refs,
        key=lambda ref: (
            to_float(ref.get(field)) if to_float(ref.get(field)) is not None else 10**12,
            ref_identity(ref),
        ),
    )


def major_name_from_warning(row: dict[str, str]) -> str:
    return text(row.get("standard_major_name")) or text(row.get("reported_major_name"))


def safe_read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    if not path.exists():
        return iter(())
    return read_csv_rows(path)


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def ordered_unique(values: list[str], *, order: list[str] | None = None) -> list[str]:
    seen = {value for value in values if value}
    if order:
        return [value for value in order if value in seen] + sorted(seen - set(order))
    return sorted(seen)


def count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if text(row.get(field)) == "true")


def count_positive(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if to_float(row.get(field)) not in (None, 0))


def count_equals(rows: list[dict[str, Any]], field: str, value: str) -> int:
    return sum(1 for row in rows if text(row.get(field)) == value)


def mean_text(values: list[float]) -> str:
    if not values:
        return ""
    value = sum(values) / len(values)
    return number_text(round(value, 2))


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


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


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build packaged new-quality-productivity major support profiles."
    )
    parser.add_argument(
        "--input-summary-csv",
        type=Path,
        default=Path("outputs/new_quality_major_eval_20260613/new_quality_major_evaluation_summary.csv"),
    )
    parser.add_argument(
        "--input-detail-csv",
        type=Path,
        default=Path("outputs/new_quality_major_eval_20260613/new_quality_major_evaluation_detail.csv"),
    )
    parser.add_argument(
        "--input-policy-sources-csv",
        type=Path,
        default=Path("outputs/new_quality_major_eval_20260613/new_quality_policy_sources.csv"),
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
        "--market-profiles-csv",
        type=Path,
        default=Path("data/processed/rysxai_market/market_major_profiles_2026.csv"),
    )
    parser.add_argument(
        "--civil-service-major-csv",
        type=Path,
        default=Path("data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv"),
    )
    parser.add_argument(
        "--transfer-policy-major-csv",
        type=Path,
        default=Path("data/processed/rysxai_transfer_policies/transfer_policy_major_mentions_2026.csv"),
    )
    parser.add_argument(
        "--output-profiles-csv",
        type=Path,
        default=Path("data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv"),
    )
    parser.add_argument(
        "--output-tier-samples-csv",
        type=Path,
        default=Path("data/processed/new_quality_major_profiles/new_quality_major_tier_samples_2026.csv"),
    )
    parser.add_argument(
        "--output-policy-sources-csv",
        type=Path,
        default=Path("data/processed/new_quality_major_profiles/new_quality_policy_sources_2026.csv"),
    )
    parser.add_argument(
        "--output-summary-csv",
        type=Path,
        default=Path("data/processed/new_quality_major_profiles/new_quality_major_profile_summary_2026.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/new_quality_major_profiles/new_quality_major_profiles_manifest_2026.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/new_quality_major_profiles/new_quality_major_profiles_2026.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_new_quality_major_profiles(
        input_summary_csv=args.input_summary_csv,
        input_detail_csv=args.input_detail_csv,
        input_policy_sources_csv=args.input_policy_sources_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        ai_replacement_csv=args.ai_replacement_csv,
        market_profiles_csv=args.market_profiles_csv,
        civil_service_major_csv=args.civil_service_major_csv,
        transfer_policy_major_csv=args.transfer_policy_major_csv,
        output_profiles_csv=args.output_profiles_csv,
        output_tier_samples_csv=args.output_tier_samples_csv,
        output_policy_sources_csv=args.output_policy_sources_csv,
        output_summary_csv=args.output_summary_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
