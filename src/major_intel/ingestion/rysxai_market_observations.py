"""Build analytic tables from rysxai major-level market snapshots."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "rysxai_market_observations/v1"
SOURCE_LEVEL = "C"

PROFILE_FIELDS = [
    "market_profile_id",
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "category",
    "subject",
    "degree",
    "limit_year",
    "selection_advice",
    "heat",
    "is_hot",
    "captured_at",
    "industry_distribution_count",
    "region_distribution_count",
    "job_direction_distribution_count",
    "demand_ranking_count",
    "salary_ranking_count",
    "job_posting_sample_total_reported",
    "job_posting_sample_count",
    "job_sample_with_salary_count",
    "salary_sample_min_observed",
    "salary_sample_max_observed",
    "salary_sample_midpoint_avg",
    "salary_reference_national",
    "salary_reference_top_region",
    "salary_reference_top_region_value",
    "demand_count_national",
    "demand_top_region",
    "demand_top_region_count",
    "rank_by_demand_count_national",
    "rank_by_salary_reference_national",
    "rank_by_job_sample_total_reported",
    "market_demand_signal_level",
    "market_salary_signal_level",
    "market_activity_signal_level",
    "top_industries",
    "top_regions",
    "top_job_directions",
    "top_job_titles",
    "top_skills",
    "top_job_cities",
    "top_job_industries",
    "top_company_scales",
    "top_financing_stages",
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
    "has_ai_medium_or_high_risk",
    "civil_service_match_count",
    "civil_service_opportunity_level",
    "civil_service_role_match_count",
    "civil_service_plan_num_sum",
    "civil_service_weighted_competition_ratio",
    "has_civil_service_match",
    "transfer_policy_match_count",
    "transfer_policy_mentioned_in_school_count",
    "transfer_policy_high_difficulty_school_count",
    "has_transfer_policy_mention",
    "source_level",
    "data_scope",
    "info_url",
    "positions_url",
    "source_snapshot_path",
]

JOB_SAMPLE_FIELDS = [
    "job_sample_id",
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "captured_at",
    "source_item_id",
    "job_title",
    "company_name",
    "city",
    "district",
    "industry",
    "salary_raw",
    "monthly_salary_min",
    "monthly_salary_max",
    "monthly_salary_midpoint",
    "education",
    "experience",
    "skills",
    "company_tags",
    "company_scale",
    "financing_stage",
    "source_level",
    "data_scope",
]

CITY_SALARY_FIELDS = [
    "city_salary_id",
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "city",
    "sample_count",
    "monthly_salary_min_observed",
    "monthly_salary_max_observed",
    "monthly_salary_midpoint_avg",
    "source_level",
    "data_scope",
]

DISTRIBUTION_FIELDS = [
    "distribution_id",
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "distribution_type",
    "rank",
    "label",
    "rate_percent",
    "detail_jobs",
    "source_level",
    "data_scope",
]

RANKING_FIELDS = [
    "ranking_id",
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "ranking_type",
    "rank",
    "region",
    "demand_count",
    "monthly_salary_reference",
    "source_level",
    "data_scope",
]

SKILL_FIELDS = [
    "skill_summary_id",
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "skill",
    "job_sample_count",
    "sample_job_titles",
    "sample_cities",
    "sample_industries",
    "source_level",
    "data_scope",
]

SUMMARY_FIELDS = [
    "summary_id",
    "group_type",
    "group_value",
    "profile_count",
    "with_job_samples_count",
    "job_sample_count_sum",
    "job_sample_total_reported_sum",
    "with_salary_reference_count",
    "avg_salary_reference_national",
    "median_salary_reference_national",
    "with_demand_count_count",
    "avg_demand_count_national",
    "median_demand_count_national",
    "employment_high_risk_profile_count",
    "official_policy_linked_profile_count",
    "ai_medium_or_high_profile_count",
    "civil_service_linked_profile_count",
    "transfer_policy_mentioned_profile_count",
]


def build_rysxai_market_observations(
    *,
    snapshots_dir: Path,
    major_seed_csv: Path,
    employment_warnings_csv: Path,
    official_policy_warnings_csv: Path,
    ai_replacement_csv: Path,
    civil_service_major_csv: Path,
    transfer_policy_major_csv: Path,
    output_profiles_csv: Path,
    output_job_samples_csv: Path,
    output_city_salary_csv: Path,
    output_distributions_csv: Path,
    output_rankings_csv: Path,
    output_skill_summary_csv: Path,
    output_summary_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    snapshot_paths = list_snapshot_paths(snapshots_dir)
    major_seed_by_id = load_major_seed_by_id(major_seed_csv)
    employment_by_code, employment_by_name = build_ref_indexes(
        load_employment_warning_refs(employment_warnings_csv)
    )
    policy_by_code, policy_by_name = build_ref_indexes(
        load_policy_warning_refs(official_policy_warnings_csv)
    )
    ai_by_profession_id, ai_by_code, ai_by_name = build_ai_indexes(
        load_ai_replacement_refs(ai_replacement_csv)
    )
    civil_by_code, civil_by_name = build_ref_indexes(
        load_civil_service_refs(civil_service_major_csv)
    )
    transfer_by_code, transfer_by_name = build_ref_indexes(
        load_transfer_policy_refs(transfer_policy_major_csv)
    )

    profile_rows: list[dict[str, Any]] = []
    job_rows: list[dict[str, Any]] = []
    city_salary_rows: list[dict[str, Any]] = []
    distribution_rows: list[dict[str, Any]] = []
    ranking_rows: list[dict[str, Any]] = []
    skill_rows: list[dict[str, Any]] = []
    duplicate_profile_ids = 0
    profile_ids: set[str] = set()

    for snapshot_path in snapshot_paths:
        snapshot = load_json(snapshot_path)
        profile_context = build_profile_context(snapshot, snapshot_path, major_seed_by_id)
        profile = build_profile_row(
            profile_context,
            employment_by_code=employment_by_code,
            employment_by_name=employment_by_name,
            policy_by_code=policy_by_code,
            policy_by_name=policy_by_name,
            ai_by_profession_id=ai_by_profession_id,
            ai_by_code=ai_by_code,
            ai_by_name=ai_by_name,
            civil_by_code=civil_by_code,
            civil_by_name=civil_by_name,
            transfer_by_code=transfer_by_code,
            transfer_by_name=transfer_by_name,
        )
        if profile["market_profile_id"] in profile_ids:
            duplicate_profile_ids += 1
        profile_ids.add(profile["market_profile_id"])
        profile_rows.append(profile)
        job_rows.extend(build_job_sample_rows(profile_context))
        city_salary_rows.extend(build_city_salary_rows(profile_context))
        distribution_rows.extend(build_distribution_rows(profile_context))
        ranking_rows.extend(build_ranking_rows(profile_context))
        skill_rows.extend(build_skill_rows(profile_context))

    add_market_ranks_and_levels(profile_rows)
    summary_rows = build_summary_rows(profile_rows)

    write_csv(output_profiles_csv, profile_rows, PROFILE_FIELDS)
    write_csv(output_job_samples_csv, job_rows, JOB_SAMPLE_FIELDS)
    write_csv(output_city_salary_csv, city_salary_rows, CITY_SALARY_FIELDS)
    write_csv(output_distributions_csv, distribution_rows, DISTRIBUTION_FIELDS)
    write_csv(output_rankings_csv, ranking_rows, RANKING_FIELDS)
    write_csv(output_skill_summary_csv, skill_rows, SKILL_FIELDS)
    write_csv(output_summary_csv, summary_rows, SUMMARY_FIELDS)

    linked_employment = [
        row for row in profile_rows if row["has_employment_high_risk_warning"] == "true"
    ]
    linked_policy = [row for row in profile_rows if row["has_official_policy_warning"] == "true"]
    linked_ai = [row for row in profile_rows if row["has_ai_medium_or_high_risk"] == "true"]
    linked_civil = [row for row in profile_rows if row["has_civil_service_match"] == "true"]
    linked_transfer = [
        row for row in profile_rows if row["has_transfer_policy_mention"] == "true"
    ]

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "source_level": SOURCE_LEVEL,
        "snapshots_dir": str(snapshots_dir),
        "major_seed_csv": str(major_seed_csv),
        "employment_warnings_csv": str(employment_warnings_csv),
        "official_policy_warnings_csv": str(official_policy_warnings_csv),
        "ai_replacement_csv": str(ai_replacement_csv),
        "civil_service_major_csv": str(civil_service_major_csv),
        "transfer_policy_major_csv": str(transfer_policy_major_csv),
        "output_profiles_csv": str(output_profiles_csv),
        "output_job_samples_csv": str(output_job_samples_csv),
        "output_city_salary_csv": str(output_city_salary_csv),
        "output_distributions_csv": str(output_distributions_csv),
        "output_rankings_csv": str(output_rankings_csv),
        "output_skill_summary_csv": str(output_skill_summary_csv),
        "output_summary_csv": str(output_summary_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "snapshot_file_count": len(snapshot_paths),
        "profile_row_count": len(profile_rows),
        "unique_profile_id_count": len(profile_ids),
        "duplicate_profile_id_count": duplicate_profile_ids,
        "job_sample_row_count": len(job_rows),
        "city_salary_row_count": len(city_salary_rows),
        "distribution_row_count": len(distribution_rows),
        "ranking_row_count": len(ranking_rows),
        "skill_summary_row_count": len(skill_rows),
        "summary_row_count": len(summary_rows),
        "linked_high_risk_profile_count": len(linked_employment),
        "linked_policy_profile_count": len(linked_policy),
        "linked_ai_medium_or_high_profile_count": len(linked_ai),
        "linked_civil_service_profile_count": len(linked_civil),
        "linked_transfer_policy_profile_count": len(linked_transfer),
        "level_counts": dict(sorted(Counter(row["level"] for row in profile_rows).items())),
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(output_report_md, manifest, profile_rows)
    return manifest


def build_profile_context(
    snapshot: dict[str, Any],
    snapshot_path: Path,
    major_seed_by_id: dict[str, dict[str, str]],
) -> dict[str, Any]:
    profession = snapshot.get("profession") or {}
    source = snapshot.get("source") or {}
    profession_id = text(profession.get("id"))
    seed = major_seed_by_id.get(profession_id, {})
    major_code = text(profession.get("code")) or text(seed.get("major_code"))
    major_name = text(profession.get("name")) or text(seed.get("major_name"))
    level = text(profession.get("level")) or text(seed.get("level"))
    return {
        "snapshot": snapshot,
        "snapshot_path": snapshot_path,
        "profession_id": profession_id,
        "major_code": major_code,
        "major_name": major_name,
        "level": level,
        "category": text(seed.get("category")),
        "subject": text(seed.get("subject")),
        "degree": text(profession.get("degree")) or text(seed.get("degree")),
        "limit_year": text(profession.get("limit_year")) or text(seed.get("limit_year")),
        "selection_advice": text(profession.get("selection_advice")),
        "heat": text(seed.get("heat")),
        "is_hot": text(seed.get("is_hot")),
        "captured_at": text(snapshot.get("captured_at")),
        "source": source,
    }


def build_profile_row(
    context: dict[str, Any],
    *,
    employment_by_code: dict[str, list[dict[str, str]]],
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_code: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
    ai_by_profession_id: dict[str, list[dict[str, str]]],
    ai_by_code: dict[str, list[dict[str, str]]],
    ai_by_name: dict[str, list[dict[str, str]]],
    civil_by_code: dict[str, list[dict[str, str]]],
    civil_by_name: dict[str, list[dict[str, str]]],
    transfer_by_code: dict[str, list[dict[str, str]]],
    transfer_by_name: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    snapshot = context["snapshot"]
    macro = snapshot.get("macro_employment") or {}
    samples = list(snapshot.get("job_posting_samples") or [])
    salary_midpoints = [
        midpoint(sample.get("monthly_salary_min"), sample.get("monthly_salary_max"))
        for sample in samples
    ]
    salary_midpoints = [value for value in salary_midpoints if value is not None]
    demand_national = ranking_value(snapshot.get("demand_ranking"), "demand_count", "national")
    salary_national = ranking_value(
        snapshot.get("salary_ranking"), "monthly_salary_reference", "national"
    )
    demand_top = top_ranking(snapshot.get("demand_ranking"), "demand_count")
    salary_top = top_ranking(snapshot.get("salary_ranking"), "monthly_salary_reference")

    major_code = context["major_code"]
    major_name = context["major_name"]
    profession_id = context["profession_id"]
    employment_refs, _ = match_refs(
        major_code, major_name, employment_by_code, employment_by_name
    )
    policy_refs, _ = match_refs(major_code, major_name, policy_by_code, policy_by_name)
    ai_refs, _ = match_ai_refs(
        profession_id, major_code, major_name, ai_by_profession_id, ai_by_code, ai_by_name
    )
    civil_refs, _ = match_refs(major_code, major_name, civil_by_code, civil_by_name)
    transfer_refs, _ = match_refs(major_code, major_name, transfer_by_code, transfer_by_name)
    best_ai = best_ai_ref(ai_refs)
    best_civil = best_numeric_ref(civil_refs, "role_match_count")
    best_transfer = best_numeric_ref(transfer_refs, "mentioned_in_school_count")

    return {
        "market_profile_id": market_profile_id(
            profession_id, major_code, major_name, context["level"]
        ),
        "rysxai_profession_id": profession_id,
        "major_code": major_code,
        "major_name": major_name,
        "level": context["level"],
        "category": context["category"],
        "subject": context["subject"],
        "degree": context["degree"],
        "limit_year": context["limit_year"],
        "selection_advice": context["selection_advice"],
        "heat": context["heat"],
        "is_hot": context["is_hot"],
        "captured_at": context["captured_at"],
        "industry_distribution_count": len(macro.get("industry_distribution") or []),
        "region_distribution_count": len(macro.get("region_distribution") or []),
        "job_direction_distribution_count": len(
            macro.get("job_direction_distribution") or []
        ),
        "demand_ranking_count": len(snapshot.get("demand_ranking") or []),
        "salary_ranking_count": len(snapshot.get("salary_ranking") or []),
        "job_posting_sample_total_reported": to_int(
            snapshot.get("job_posting_sample_total_reported")
        ),
        "job_posting_sample_count": to_int(snapshot.get("job_posting_sample_count")),
        "job_sample_with_salary_count": len(salary_midpoints),
        "salary_sample_min_observed": min_or_blank(
            sample.get("monthly_salary_min") for sample in samples
        ),
        "salary_sample_max_observed": max_or_blank(
            sample.get("monthly_salary_max") for sample in samples
        ),
        "salary_sample_midpoint_avg": mean_or_blank(salary_midpoints),
        "salary_reference_national": number_text(salary_national),
        "salary_reference_top_region": salary_top[0],
        "salary_reference_top_region_value": number_text(salary_top[1]),
        "demand_count_national": number_text(demand_national),
        "demand_top_region": demand_top[0],
        "demand_top_region_count": number_text(demand_top[1]),
        "rank_by_demand_count_national": "",
        "rank_by_salary_reference_national": "",
        "rank_by_job_sample_total_reported": "",
        "market_demand_signal_level": "",
        "market_salary_signal_level": "",
        "market_activity_signal_level": "",
        "top_industries": distribution_summary(
            macro.get("industry_distribution") or [], "label", "rate_percent"
        ),
        "top_regions": distribution_summary(
            macro.get("region_distribution") or [], "label", "rate_percent"
        ),
        "top_job_directions": distribution_summary(
            macro.get("job_direction_distribution") or [], "label", "rate_percent"
        ),
        "top_job_titles": counter_summary(
            Counter(text(sample.get("job_title")) for sample in samples)
        ),
        "top_skills": counter_summary(skill_counter(samples)),
        "top_job_cities": counter_summary(Counter(text(sample.get("city")) for sample in samples)),
        "top_job_industries": counter_summary(
            Counter(text(sample.get("industry")) for sample in samples)
        ),
        "top_company_scales": counter_summary(
            Counter(text(sample.get("company_scale")) for sample in samples)
        ),
        "top_financing_stages": counter_summary(
            Counter(text(sample.get("financing_stage")) for sample in samples)
        ),
        **summarize_employment_refs(employment_refs),
        **summarize_policy_refs(policy_refs),
        **summarize_ai_refs(ai_refs, best_ai),
        **summarize_civil_refs(civil_refs, best_civil),
        **summarize_transfer_refs(transfer_refs, best_transfer),
        "source_level": SOURCE_LEVEL,
        "data_scope": "third_party_major_market_observation",
        "info_url": text(context["source"].get("info_url")),
        "positions_url": text(context["source"].get("positions_url")),
        "source_snapshot_path": context["snapshot_path"].as_posix(),
    }


def build_job_sample_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    snapshot = context["snapshot"]
    rows: list[dict[str, Any]] = []
    for index, sample in enumerate(snapshot.get("job_posting_samples") or [], start=1):
        salary_midpoint = midpoint(
            sample.get("monthly_salary_min"), sample.get("monthly_salary_max")
        )
        rows.append(
            {
                "job_sample_id": job_sample_id(context, sample, index),
                "rysxai_profession_id": context["profession_id"],
                "major_code": context["major_code"],
                "major_name": context["major_name"],
                "level": context["level"],
                "captured_at": context["captured_at"],
                "source_item_id": text(sample.get("source_item_id")),
                "job_title": text(sample.get("job_title")),
                "company_name": text(sample.get("company_name")),
                "city": text(sample.get("city")),
                "district": text(sample.get("district")),
                "industry": text(sample.get("industry")),
                "salary_raw": text(sample.get("salary_raw")),
                "monthly_salary_min": number_text(sample.get("monthly_salary_min")),
                "monthly_salary_max": number_text(sample.get("monthly_salary_max")),
                "monthly_salary_midpoint": number_text(salary_midpoint),
                "education": text(sample.get("education")),
                "experience": text(sample.get("experience")),
                "skills": join_list(sample.get("skills")),
                "company_tags": join_list(sample.get("company_tags")),
                "company_scale": text(sample.get("company_scale")),
                "financing_stage": text(sample.get("financing_stage")),
                "source_level": SOURCE_LEVEL,
                "data_scope": "recruiting_market_sample",
            }
        )
    return rows


def build_city_salary_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    snapshot = context["snapshot"]
    rows: list[dict[str, Any]] = []
    city_data = snapshot.get("salary_observations_by_city") or {}
    for city, values in sorted(city_data.items()):
        rows.append(
            {
                "city_salary_id": stable_id(
                    "market_city_salary",
                    context["profession_id"],
                    context["major_code"],
                    city,
                ),
                "rysxai_profession_id": context["profession_id"],
                "major_code": context["major_code"],
                "major_name": context["major_name"],
                "level": context["level"],
                "city": text(city),
                "sample_count": to_int(values.get("sample_count")),
                "monthly_salary_min_observed": number_text(
                    values.get("monthly_salary_min_observed")
                ),
                "monthly_salary_max_observed": number_text(
                    values.get("monthly_salary_max_observed")
                ),
                "monthly_salary_midpoint_avg": number_text(
                    values.get("monthly_salary_midpoint_avg")
                ),
                "source_level": SOURCE_LEVEL,
                "data_scope": "recruiting_market_sample_city_salary",
            }
        )
    return rows


def build_distribution_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    macro = context["snapshot"].get("macro_employment") or {}
    definitions = [
        ("industry", macro.get("industry_distribution") or []),
        ("region", macro.get("region_distribution") or []),
        ("job_direction", macro.get("job_direction_distribution") or []),
    ]
    rows: list[dict[str, Any]] = []
    for distribution_type, values in definitions:
        for index, item in enumerate(values, start=1):
            label = text(item.get("label"))
            rows.append(
                {
                    "distribution_id": stable_id(
                        "market_distribution",
                        context["profession_id"],
                        distribution_type,
                        index,
                        label,
                    ),
                    "rysxai_profession_id": context["profession_id"],
                    "major_code": context["major_code"],
                    "major_name": context["major_name"],
                    "level": context["level"],
                    "distribution_type": distribution_type,
                    "rank": index,
                    "label": label,
                    "rate_percent": number_text(item.get("rate_percent")),
                    "detail_jobs": join_list(item.get("detail_jobs")),
                    "source_level": SOURCE_LEVEL,
                    "data_scope": "third_party_major_market_macro_distribution",
                }
            )
    return rows


def build_ranking_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    snapshot = context["snapshot"]
    rows: list[dict[str, Any]] = []
    for ranking_type, values in [
        ("demand", snapshot.get("demand_ranking") or []),
        ("salary", snapshot.get("salary_ranking") or []),
    ]:
        for index, item in enumerate(values, start=1):
            region = text(item.get("region"))
            rows.append(
                {
                    "ranking_id": stable_id(
                        "market_ranking",
                        context["profession_id"],
                        ranking_type,
                        index,
                        region,
                    ),
                    "rysxai_profession_id": context["profession_id"],
                    "major_code": context["major_code"],
                    "major_name": context["major_name"],
                    "level": context["level"],
                    "ranking_type": ranking_type,
                    "rank": index,
                    "region": region,
                    "demand_count": number_text(item.get("demand_count")),
                    "monthly_salary_reference": number_text(
                        item.get("monthly_salary_reference")
                    ),
                    "source_level": SOURCE_LEVEL,
                    "data_scope": "third_party_major_market_ranking",
                }
            )
    return rows


def build_skill_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    samples = context["snapshot"].get("job_posting_samples") or []
    by_skill: dict[str, dict[str, set[str] | int]] = defaultdict(
        lambda: {"count": 0, "titles": set(), "cities": set(), "industries": set()}
    )
    for sample in samples:
        for skill in as_list(sample.get("skills")):
            skill_text = text(skill)
            if not skill_text:
                continue
            entry = by_skill[skill_text]
            entry["count"] = int(entry["count"]) + 1
            add_if(entry["titles"], sample.get("job_title"))
            add_if(entry["cities"], sample.get("city"))
            add_if(entry["industries"], sample.get("industry"))

    rows: list[dict[str, Any]] = []
    for skill, value in sorted(
        by_skill.items(),
        key=lambda item: (-int(item[1]["count"]), item[0]),
    ):
        rows.append(
            {
                "skill_summary_id": stable_id(
                    "market_skill", context["profession_id"], context["major_code"], skill
                ),
                "rysxai_profession_id": context["profession_id"],
                "major_code": context["major_code"],
                "major_name": context["major_name"],
                "level": context["level"],
                "skill": skill,
                "job_sample_count": int(value["count"]),
                "sample_job_titles": join_sample(value["titles"], limit=8),
                "sample_cities": join_sample(value["cities"], limit=8),
                "sample_industries": join_sample(value["industries"], limit=8),
                "source_level": SOURCE_LEVEL,
                "data_scope": "recruiting_market_sample_skill_summary",
            }
        )
    return rows


def add_market_ranks_and_levels(rows: list[dict[str, Any]]) -> None:
    add_rank(rows, "demand_count_national", "rank_by_demand_count_national")
    add_rank(rows, "salary_reference_national", "rank_by_salary_reference_national")
    add_rank(
        rows,
        "job_posting_sample_total_reported",
        "rank_by_job_sample_total_reported",
    )
    demand_values = numeric_values(rows, "demand_count_national")
    salary_values = numeric_values(rows, "salary_reference_national")
    activity_values = numeric_values(rows, "job_posting_sample_total_reported")
    for row in rows:
        row["market_demand_signal_level"] = percentile_level(
            to_float(row.get("demand_count_national")),
            demand_values,
        )
        row["market_salary_signal_level"] = percentile_level(
            to_float(row.get("salary_reference_national")),
            salary_values,
        )
        row["market_activity_signal_level"] = percentile_level(
            to_float(row.get("job_posting_sample_total_reported")),
            activity_values,
        )


def add_rank(rows: list[dict[str, Any]], value_field: str, rank_field: str) -> None:
    ranked = sorted(
        [row for row in rows if to_float(row.get(value_field)) is not None],
        key=lambda row: (
            -float(to_float(row.get(value_field)) or 0),
            row.get("major_code", ""),
            row.get("major_name", ""),
        ),
    )
    for rank, row in enumerate(ranked, start=1):
        row[rank_field] = rank


def build_summary_rows(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in profile_rows:
        groups[("all", "all")].append(row)
        for group_type, field in [
            ("level", "level"),
            ("category", "category"),
            ("subject", "subject"),
        ]:
            value = text(row.get(field))
            if value:
                groups[(group_type, value)].append(row)
    rows: list[dict[str, Any]] = []
    for (group_type, group_value), group_rows in sorted(groups.items()):
        salary_values = numeric_values(group_rows, "salary_reference_national")
        demand_values = numeric_values(group_rows, "demand_count_national")
        rows.append(
            {
                "summary_id": stable_id("market_summary", group_type, group_value),
                "group_type": group_type,
                "group_value": group_value,
                "profile_count": len(group_rows),
                "with_job_samples_count": count_positive(
                    group_rows, "job_posting_sample_count"
                ),
                "job_sample_count_sum": sum_int(
                    group_rows, "job_posting_sample_count"
                ),
                "job_sample_total_reported_sum": sum_int(
                    group_rows, "job_posting_sample_total_reported"
                ),
                "with_salary_reference_count": len(salary_values),
                "avg_salary_reference_national": mean_or_blank(salary_values),
                "median_salary_reference_national": median_or_blank(salary_values),
                "with_demand_count_count": len(demand_values),
                "avg_demand_count_national": mean_or_blank(demand_values),
                "median_demand_count_national": median_or_blank(demand_values),
                "employment_high_risk_profile_count": count_true(
                    group_rows, "has_employment_high_risk_warning"
                ),
                "official_policy_linked_profile_count": count_true(
                    group_rows, "has_official_policy_warning"
                ),
                "ai_medium_or_high_profile_count": count_true(
                    group_rows, "has_ai_medium_or_high_risk"
                ),
                "civil_service_linked_profile_count": count_true(
                    group_rows, "has_civil_service_match"
                ),
                "transfer_policy_mentioned_profile_count": count_true(
                    group_rows, "has_transfer_policy_mention"
                ),
            }
        )
    return rows


def load_major_seed_by_id(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    result: dict[str, dict[str, str]] = {}
    for row in read_csv_rows(path):
        profession_id = text(row.get("rysxai_profession_id")) or text(
            row.get("profession_id")
        )
        if profession_id:
            result[profession_id] = row
    return result


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


def load_ai_replacement_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in safe_read_csv_rows(path):
        refs.append(
            {
                "id": stable_id(
                    "ai",
                    row.get("profession_id"),
                    row.get("major_code"),
                    row.get("major_name"),
                ),
                "profession_id": text(row.get("profession_id")),
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
                "weighted_competition_ratio": text(
                    row.get("weighted_competition_ratio")
                ),
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
        ref_id = text(ref.get("id")) or stable_id(
            "ref", ref.get("major_code"), ref.get("major_name")
        )
        if text(ref.get("major_code")):
            by_code[text(ref.get("major_code"))][ref_id] = ref
        if text(ref.get("major_name")):
            by_name[text(ref.get("major_name"))][ref_id] = ref
    return (
        {key: sorted(value.values(), key=ref_sort_key) for key, value in by_code.items()},
        {key: sorted(value.values(), key=ref_sort_key) for key, value in by_name.items()},
    )


def build_ai_indexes(
    refs: list[dict[str, str]],
) -> tuple[
    dict[str, list[dict[str, str]]],
    dict[str, list[dict[str, str]]],
    dict[str, list[dict[str, str]]],
]:
    by_profession_id: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    by_code: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    by_name: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for ref in refs:
        ref_id = text(ref.get("id"))
        if text(ref.get("profession_id")):
            by_profession_id[text(ref.get("profession_id"))][ref_id] = ref
        if text(ref.get("major_code")):
            by_code[text(ref.get("major_code"))][ref_id] = ref
        if text(ref.get("major_name")):
            by_name[text(ref.get("major_name"))][ref_id] = ref
    return (
        {key: sorted(value.values(), key=ai_sort_key) for key, value in by_profession_id.items()},
        {key: sorted(value.values(), key=ai_sort_key) for key, value in by_code.items()},
        {key: sorted(value.values(), key=ai_sort_key) for key, value in by_name.items()},
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


def match_ai_refs(
    profession_id: str,
    major_code: str,
    major_name: str,
    by_profession_id: dict[str, list[dict[str, str]]],
    by_code: dict[str, list[dict[str, str]]],
    by_name: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, str]], str]:
    refs_by_id: dict[str, dict[str, str]] = {}
    basis: list[str] = []
    if profession_id and profession_id in by_profession_id:
        basis.append("profession_id")
        for ref in by_profession_id[profession_id]:
            refs_by_id[ref_identity(ref)] = ref
    if major_code and major_code in by_code:
        basis.append("code")
        for ref in by_code[major_code]:
            refs_by_id[ref_identity(ref)] = ref
    if major_name and major_name in by_name:
        basis.append("name")
        for ref in by_name[major_name]:
            refs_by_id[ref_identity(ref)] = ref
    return sorted(refs_by_id.values(), key=ai_sort_key), "+".join(basis)


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
    level = text(best_ai.get("level") if best_ai else "")
    score = to_float(best_ai.get("score") if best_ai else "")
    medium_or_high = level in {"very_high", "high", "medium", "很高", "较高", "中等"}
    if score is not None:
        medium_or_high = medium_or_high or score >= 50
    return {
        "ai_replacement_match_count": len(refs),
        "ai_replacement_rank": text(best_ai.get("rank") if best_ai else ""),
        "ai_replacement_score": text(best_ai.get("score") if best_ai else ""),
        "ai_replacement_level": level,
        "ai_confidence_score": text(best_ai.get("confidence_score") if best_ai else ""),
        "ai_candidate_count": text(best_ai.get("candidate_count") if best_ai else ""),
        "has_ai_medium_or_high_risk": bool_text(bool(refs) and medium_or_high),
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
        "civil_service_weighted_competition_ratio": text(
            best_civil.get("weighted_competition_ratio") if best_civil else ""
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


def write_report(
    path: Path,
    manifest: dict[str, Any],
    profile_rows: list[dict[str, Any]],
) -> None:
    top_demand = sorted(
        profile_rows,
        key=lambda row: (
            -(to_float(row.get("demand_count_national")) or 0),
            row.get("major_code", ""),
        ),
    )[:20]
    top_salary = sorted(
        profile_rows,
        key=lambda row: (
            -(to_float(row.get("salary_reference_national")) or 0),
            row.get("major_code", ""),
        ),
    )[:20]
    lines = [
        "# RYSXAI Major Market Observation Report",
        "",
        f"- Source level: {manifest['source_level']}",
        f"- Snapshot files: {manifest['snapshot_file_count']}",
        f"- Major market profiles: {manifest['profile_row_count']}",
        f"- Job sample rows: {manifest['job_sample_row_count']}",
        f"- City salary rows: {manifest['city_salary_row_count']}",
        f"- Distribution rows: {manifest['distribution_row_count']}",
        f"- Ranking rows: {manifest['ranking_row_count']}",
        f"- Skill summary rows: {manifest['skill_summary_row_count']}",
        f"- Red/yellow employment-warning linked profiles: {manifest['linked_high_risk_profile_count']}",
        f"- Official-policy linked profiles: {manifest['linked_policy_profile_count']}",
        f"- AI medium-or-high linked profiles: {manifest['linked_ai_medium_or_high_profile_count']}",
        "",
        "## Top Demand Signals",
        "",
        "| Major | Level | Demand | Salary ref | Job samples | High-risk | AI risk |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for row in top_demand:
        lines.append(
            "| {major_name} | {level} | {demand_count_national} | "
            "{salary_reference_national} | {job_posting_sample_count} | "
            "{has_employment_high_risk_warning} | {ai_replacement_level} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Top Salary Reference Signals",
            "",
            "| Major | Level | Salary ref | Demand | Job samples | High-risk | AI risk |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in top_salary:
        lines.append(
            "| {major_name} | {level} | {salary_reference_national} | "
            "{demand_count_national} | {job_posting_sample_count} | "
            "{has_employment_high_risk_warning} | {ai_replacement_level} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Profiles: `{manifest['output_profiles_csv']}`",
            f"- Job samples: `{manifest['output_job_samples_csv']}`",
            f"- City salary: `{manifest['output_city_salary_csv']}`",
            f"- Distributions: `{manifest['output_distributions_csv']}`",
            f"- Rankings: `{manifest['output_rankings_csv']}`",
            f"- Skills: `{manifest['output_skill_summary_csv']}`",
            f"- Summary: `{manifest['output_summary_csv']}`",
            f"- Manifest: `{manifest['output_manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- Source level is `C`: this is third-party market observation data, not official graduate outcome evidence.",
            "- Recruiting samples are retained with job/company fields but without recruiter personal fields.",
            "- Salary and demand fields are suitable for screening and retrieval features, not deterministic employment forecasts.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def list_snapshot_paths(snapshots_dir: Path) -> list[Path]:
    return sorted(
        snapshots_dir.glob("profession_*_market_snapshot.json"),
        key=snapshot_sort_key,
    )


def snapshot_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"profession_(\d+)_market_snapshot\.json$", path.name)
    return (int(match.group(1)) if match else 10**9, path.name)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def safe_read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    if not path.exists():
        return iter(())
    return read_csv_rows(path)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def major_name_from_warning(row: dict[str, str]) -> str:
    return text(row.get("standard_major_name")) or text(row.get("reported_major_name"))


def market_profile_id(
    profession_id: str,
    major_code: str,
    major_name: str,
    level: str,
) -> str:
    return stable_id("market_profile", profession_id, major_code, major_name, level)


def job_sample_id(context: dict[str, Any], sample: dict[str, Any], index: int) -> str:
    return stable_id(
        "market_job_sample",
        context["profession_id"],
        sample.get("source_item_id"),
        sample.get("job_title"),
        sample.get("company_name"),
        index,
    )


def stable_id(prefix: str, *parts: Any) -> str:
    key = "|".join(text(part) for part in parts)
    return prefix + ":" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


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


def ai_sort_key(ref: dict[str, str]) -> tuple[int, str, str]:
    return (
        to_int(ref.get("rank"), default=10**9),
        text(ref.get("major_code")),
        text(ref.get("major_name")),
    )


def best_ai_ref(refs: list[dict[str, str]]) -> dict[str, str] | None:
    return min(refs, key=ai_sort_key) if refs else None


def best_numeric_ref(refs: list[dict[str, str]], field: str) -> dict[str, str] | None:
    if not refs:
        return None
    return max(refs, key=lambda ref: (to_float(ref.get(field)) or 0, ref_identity(ref)))


def ranking_value(rows: Any, value_key: str, region_kind: str) -> float | None:
    if not isinstance(rows, list):
        return None
    for row in rows:
        region = text(row.get("region"))
        if region_kind == "national" and region in {"全国", "national", "Nationwide"}:
            return to_float(row.get(value_key))
    return to_float(rows[0].get(value_key)) if rows else None


def top_ranking(rows: Any, value_key: str) -> tuple[str, float | None]:
    if not isinstance(rows, list) or not rows:
        return "", None
    best = max(rows, key=lambda row: to_float(row.get(value_key)) or 0)
    return text(best.get("region")), to_float(best.get(value_key))


def distribution_summary(rows: list[dict[str, Any]], label_key: str, value_key: str) -> str:
    values = []
    for row in rows[:10]:
        label = text(row.get(label_key))
        value = to_float(row.get(value_key))
        if label:
            values.append(f"{label}:{number_text(value)}")
    return "|".join(values)


def counter_summary(counter: Counter[str], limit: int = 10) -> str:
    values = []
    for label, count in counter.most_common(limit):
        if label:
            values.append(f"{label}:{count}")
    return "|".join(values)


def skill_counter(samples: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for sample in samples:
        for skill in as_list(sample.get("skills")):
            skill_text = text(skill)
            if skill_text:
                counter[skill_text] += 1
    return counter


def midpoint(low: Any, high: Any) -> float | None:
    low_value = to_float(low)
    high_value = to_float(high)
    if low_value is None or high_value is None:
        return None
    return round((low_value + high_value) / 2, 2)


def mean_or_blank(values: Any) -> str:
    numeric = [float(value) for value in values if to_float(value) is not None]
    if not numeric:
        return ""
    return number_text(round(sum(numeric) / len(numeric), 2))


def median_or_blank(values: Any) -> str:
    numeric = [float(value) for value in values if to_float(value) is not None]
    if not numeric:
        return ""
    return number_text(round(statistics.median(numeric), 2))


def min_or_blank(values: Any) -> str:
    numeric = [to_float(value) for value in values if to_float(value) is not None]
    return number_text(min(numeric)) if numeric else ""


def max_or_blank(values: Any) -> str:
    numeric = [to_float(value) for value in values if to_float(value) is not None]
    return number_text(max(numeric)) if numeric else ""


def numeric_values(rows: list[dict[str, Any]], field: str) -> list[float]:
    return sorted(
        [float(value) for row in rows if (value := to_float(row.get(field))) is not None]
    )


def percentile_level(value: float | None, values: list[float]) -> str:
    if value is None or not values:
        return "unknown"
    p50 = percentile_nearest(values, 0.50)
    p75 = percentile_nearest(values, 0.75)
    p90 = percentile_nearest(values, 0.90)
    if value >= p90:
        return "very_high"
    if value >= p75:
        return "high"
    if value >= p50:
        return "medium"
    return "limited"


def percentile_nearest(values: list[float], percentile: float) -> float:
    if not values:
        return 0
    index = round((len(values) - 1) * percentile)
    return values[index]


def count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if text(row.get(field)) == "true")


def count_positive(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if to_float(row.get(field)) not in (None, 0))


def sum_int(rows: list[dict[str, Any]], field: str) -> int:
    return sum(to_int(row.get(field)) for row in rows)


def ordered_unique(values: list[str], *, order: list[str] | None = None) -> list[str]:
    seen = {value for value in values if value}
    if order:
        return [value for value in order if value in seen] + sorted(seen - set(order))
    return sorted(seen)


def join_list(value: Any) -> str:
    return "|".join(text(item) for item in as_list(value) if text(item))


def join_sample(values: Any, *, limit: int = 8) -> str:
    return "|".join(sorted(text(value) for value in values if text(value))[:limit])


def add_if(values: Any, value: Any) -> None:
    value_text = text(value)
    if value_text:
        values.add(value_text)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def to_int(value: Any, *, default: int = 0) -> int:
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
        description="Build analytic tables from rysxai market snapshots."
    )
    parser.add_argument(
        "--snapshots-dir",
        type=Path,
        default=Path("data/processed/rysxai"),
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
        default=Path(
            "data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv"
        ),
    )
    parser.add_argument(
        "--ai-replacement-csv",
        type=Path,
        default=Path("data/processed/ai_replacement/major_ai_replacement_ranking.csv"),
    )
    parser.add_argument(
        "--civil-service-major-csv",
        type=Path,
        default=Path(
            "data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv"
        ),
    )
    parser.add_argument(
        "--transfer-policy-major-csv",
        type=Path,
        default=Path(
            "data/processed/rysxai_transfer_policies/transfer_policy_major_mentions_2026.csv"
        ),
    )
    parser.add_argument(
        "--output-profiles-csv",
        type=Path,
        default=Path("data/processed/rysxai_market/market_major_profiles_2026.csv"),
    )
    parser.add_argument(
        "--output-job-samples-csv",
        type=Path,
        default=Path("data/processed/rysxai_market/market_job_samples_2026.csv"),
    )
    parser.add_argument(
        "--output-city-salary-csv",
        type=Path,
        default=Path("data/processed/rysxai_market/market_city_salary_2026.csv"),
    )
    parser.add_argument(
        "--output-distributions-csv",
        type=Path,
        default=Path("data/processed/rysxai_market/market_macro_distributions_2026.csv"),
    )
    parser.add_argument(
        "--output-rankings-csv",
        type=Path,
        default=Path("data/processed/rysxai_market/market_rankings_2026.csv"),
    )
    parser.add_argument(
        "--output-skill-summary-csv",
        type=Path,
        default=Path("data/processed/rysxai_market/market_skill_summary_2026.csv"),
    )
    parser.add_argument(
        "--output-summary-csv",
        type=Path,
        default=Path("data/processed/rysxai_market/market_profile_summary_2026.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/rysxai_market/market_observations_manifest_2026.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/rysxai_market/market_observations_2026.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_rysxai_market_observations(
        snapshots_dir=args.snapshots_dir,
        major_seed_csv=args.major_seed_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        ai_replacement_csv=args.ai_replacement_csv,
        civil_service_major_csv=args.civil_service_major_csv,
        transfer_policy_major_csv=args.transfer_policy_major_csv,
        output_profiles_csv=args.output_profiles_csv,
        output_job_samples_csv=args.output_job_samples_csv,
        output_city_salary_csv=args.output_city_salary_csv,
        output_distributions_csv=args.output_distributions_csv,
        output_rankings_csv=args.output_rankings_csv,
        output_skill_summary_csv=args.output_skill_summary_csv,
        output_summary_csv=args.output_summary_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
