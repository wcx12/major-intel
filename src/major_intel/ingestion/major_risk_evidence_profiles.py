"""Build long-form evidence records behind the major risk master index."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Iterator

from .major_risk_master_index import normalize_level


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/major_risk_evidence_profiles"
DEFAULT_REPORT_DIR = ROOT / "reports/major_risk_evidence_profiles"
SCHEMA_VERSION = "major_risk_evidence_profiles/v1"
SOURCE_LEVEL = "A/B/C"

EVIDENCE_FIELDS = [
    "evidence_id",
    "major_master_id",
    "major_code",
    "major_name",
    "major_level",
    "overall_review_bucket",
    "evidence_family",
    "signal_direction",
    "source_level",
    "source_table",
    "source_record_id",
    "record_year",
    "record_type",
    "signal_label",
    "signal_value",
    "confidence",
    "source_ids",
    "source_titles",
    "source_urls",
    "source_publishers",
    "source_paths",
    "evidence_text",
    "source_note",
    "data_scope",
    "needs_review",
]

MAJOR_SUMMARY_FIELDS = [
    "major_master_id",
    "major_code",
    "major_name",
    "major_level",
    "overall_review_bucket",
    "risk_signal_count",
    "opportunity_signal_count",
    "evidence_record_count",
    "risk_evidence_count",
    "opportunity_evidence_count",
    "reference_evidence_count",
    "mixed_evidence_count",
    "employment_warning_evidence_count",
    "official_policy_evidence_count",
    "ai_replacement_evidence_count",
    "market_observation_evidence_count",
    "civil_service_evidence_count",
    "new_quality_evidence_count",
    "emerging_major_evidence_count",
    "vocational_register_evidence_count",
    "source_id_count",
    "source_url_count",
    "source_title_sample",
    "source_url_sample",
    "evidence_family_flags",
]

SOURCE_SUMMARY_FIELDS = [
    "summary_id",
    "evidence_family",
    "signal_direction",
    "source_level",
    "source_table",
    "evidence_record_count",
    "major_count",
    "source_id_count",
    "source_url_count",
    "high_risk_review_major_count",
]


def build_major_risk_evidence_profiles(
    *,
    master_index_csv: Path = ROOT
    / "data/processed/major_risk_master_index/major_risk_master_index_2026.csv",
    employment_warnings_csv: Path = ROOT
    / "data/processed/major_risk_warnings/major_risk_warning_records.csv",
    official_policy_warnings_csv: Path = ROOT
    / "data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv",
    warning_sources_csv: Path = ROOT
    / "data/processed/major_risk_warnings/major_risk_warning_sources.csv",
    ai_replacement_csv: Path = ROOT
    / "data/processed/ai_replacement/major_ai_replacement_ranking.csv",
    market_profiles_csv: Path = ROOT
    / "data/processed/rysxai_market/market_major_profiles_2026.csv",
    civil_service_major_csv: Path = ROOT
    / "data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv",
    new_quality_profiles_csv: Path = ROOT
    / "data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv",
    new_quality_policy_sources_csv: Path = ROOT
    / "data/processed/new_quality_major_profiles/new_quality_policy_sources_2026.csv",
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

    master_rows = load_master_rows(master_index_csv)
    warning_sources = load_warning_sources(warning_sources_csv)
    new_quality_sources = load_new_quality_sources(new_quality_policy_sources_csv)

    evidence_rows: list[dict[str, Any]] = []
    source_counts = {
        "employment_warning": add_employment_warning_rows(
            evidence_rows, employment_warnings_csv, master_rows, warning_sources
        ),
        "official_policy_warning": add_official_policy_rows(
            evidence_rows, official_policy_warnings_csv, master_rows, warning_sources
        ),
        "ai_replacement": add_ai_rows(evidence_rows, ai_replacement_csv, master_rows),
        "market_observation": add_market_rows(evidence_rows, market_profiles_csv, master_rows),
        "civil_service": add_civil_rows(evidence_rows, civil_service_major_csv, master_rows),
        "new_quality": add_new_quality_rows(
            evidence_rows, new_quality_profiles_csv, master_rows, new_quality_sources
        ),
        "emerging_major": add_emerging_rows(evidence_rows, emerging_majors_csv, master_rows),
        "vocational_register": add_vocational_rows(
            evidence_rows, vocational_summary_csv, master_rows
        ),
    }
    evidence_rows = sorted(evidence_rows, key=evidence_sort_key)
    major_summary_rows = build_major_summary_rows(evidence_rows, master_rows)
    source_summary_rows = build_source_summary_rows(evidence_rows)

    evidence_csv = output_dir / "major_risk_evidence_records_2026.csv"
    major_summary_csv = output_dir / "major_risk_evidence_major_summary_2026.csv"
    source_summary_csv = output_dir / "major_risk_evidence_source_summary_2026.csv"
    manifest_json = output_dir / "major_risk_evidence_profiles_manifest_2026.json"
    report_md = report_dir / "major_risk_evidence_profiles_2026.md"

    write_csv(evidence_csv, evidence_rows, EVIDENCE_FIELDS)
    write_csv(major_summary_csv, major_summary_rows, MAJOR_SUMMARY_FIELDS)
    write_csv(source_summary_csv, source_summary_rows, SOURCE_SUMMARY_FIELDS)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "generated_at": generated_at,
        "source_level": SOURCE_LEVEL,
        "inputs": {
            "master_index_csv": path_key(master_index_csv),
            "employment_warnings_csv": path_key(employment_warnings_csv),
            "official_policy_warnings_csv": path_key(official_policy_warnings_csv),
            "warning_sources_csv": path_key(warning_sources_csv),
            "ai_replacement_csv": path_key(ai_replacement_csv),
            "market_profiles_csv": path_key(market_profiles_csv),
            "civil_service_major_csv": path_key(civil_service_major_csv),
            "new_quality_profiles_csv": path_key(new_quality_profiles_csv),
            "new_quality_policy_sources_csv": path_key(new_quality_policy_sources_csv),
            "emerging_majors_csv": path_key(emerging_majors_csv),
            "vocational_summary_csv": path_key(vocational_summary_csv),
        },
        "outputs": {
            "evidence_csv": path_key(evidence_csv),
            "major_summary_csv": path_key(major_summary_csv),
            "source_summary_csv": path_key(source_summary_csv),
            "manifest_json": path_key(manifest_json),
            "report_md": path_key(report_md),
        },
        "source_input_row_counts": source_counts,
        "row_counts": {
            "evidence_records": len(evidence_rows),
            "major_summary": len(major_summary_rows),
            "source_summary": len(source_summary_rows),
        },
        "evidence_family_counts": dict(
            sorted(Counter(row["evidence_family"] for row in evidence_rows).items())
        ),
        "signal_direction_counts": dict(
            sorted(Counter(row["signal_direction"] for row in evidence_rows).items())
        ),
        "major_counts": {
            "majors_with_evidence": len(
                {row["major_master_id"] for row in evidence_rows if row["major_master_id"]}
            ),
            "high_risk_review_majors_with_evidence": len(
                {
                    row["major_master_id"]
                    for row in evidence_rows
                    if row["overall_review_bucket"] == "high_risk_review"
                }
            ),
        },
        "checksums": {
            path_key(evidence_csv): file_info(evidence_csv),
            path_key(major_summary_csv): file_info(major_summary_csv),
            path_key(source_summary_csv): file_info(source_summary_csv),
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
    write_report(report_md, manifest, evidence_rows, major_summary_rows, source_summary_rows)
    return manifest


def add_employment_warning_rows(
    output: list[dict[str, Any]],
    path: Path,
    master_rows: dict[str, dict[str, str]],
    source_map: dict[str, dict[str, str]],
) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        source_ids = split_ids(row.get("source_ids"))
        output.append(
            evidence_row(
                row,
                master_rows,
                evidence_family="employment_warning",
                signal_direction="opportunity" if text(row.get("risk_level")) == "green" else "risk",
                source_level="B",
                source_table="major_risk_warning_records.csv",
                source_record_id=row.get("record_id"),
                record_year=row.get("report_year"),
                record_type=row.get("risk_level"),
                signal_label="employment_warning_risk_level",
                signal_value=row.get("risk_level"),
                confidence=row.get("confidence"),
                source_ids=source_ids,
                source_info=source_info_for(source_ids, source_map),
                evidence_text=row.get("evidence_text"),
                source_note=join_nonempty([row.get("evidence_type"), row.get("notes")]),
                data_scope="public_employment_warning_record",
            )
        )
    return count


def add_official_policy_rows(
    output: list[dict[str, Any]],
    path: Path,
    master_rows: dict[str, dict[str, str]],
    source_map: dict[str, dict[str, str]],
) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        if not text(row.get("major_code")) and not (
            text(row.get("standard_major_name")) or text(row.get("reported_major_name"))
        ):
            continue
        source_ids = split_ids(row.get("source_ids"))
        output.append(
            evidence_row(
                row,
                master_rows,
                evidence_family="official_policy_warning",
                signal_direction="risk",
                source_level="A/B",
                source_table="major_risk_warning_official_policy_warnings.csv",
                source_record_id=row.get("warning_id"),
                record_year=row.get("policy_year"),
                record_type=row.get("record_type"),
                signal_label=text(row.get("policy_action")) or text(row.get("warning_label")),
                signal_value=join_nonempty([row.get("record_type"), row.get("region")]),
                confidence=row.get("confidence"),
                source_ids=source_ids,
                source_info=source_info_for(source_ids, source_map),
                evidence_text=row.get("evidence_text"),
                source_note=join_nonempty(
                    [row.get("warning_label"), row.get("criterion_text"), row.get("source_row_no")]
                ),
                data_scope="official_professional_setting_warning_record",
            )
        )
    return count


def add_ai_rows(
    output: list[dict[str, Any]],
    path: Path,
    master_rows: dict[str, dict[str, str]],
) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        output.append(
            evidence_row(
                row,
                master_rows,
                evidence_family="ai_replacement",
                signal_direction="risk" if ai_high(row) else "reference",
                source_level="C",
                source_table="major_ai_replacement_ranking.csv",
                source_record_id=row.get("profession_id"),
                record_year="2026",
                record_type="ai_replacement_score",
                signal_label=row.get("ai_replacement_level"),
                signal_value=join_nonempty(
                    [
                        f"rank={text(row.get('rank'))}",
                        f"score={text(row.get('ai_replacement_score'))}",
                        f"confidence={text(row.get('confidence_score'))}",
                    ]
                ),
                confidence=row.get("confidence_score"),
                source_ids=[],
                source_info={},
                evidence_text=row.get("main_reasons"),
                source_note=join_nonempty(
                    [row.get("source_fields"), row.get("top_risky_jobs"), row.get("top_resilient_jobs")]
                ),
                data_scope=text(row.get("data_scope")) or "third_party_ai_replacement_screening",
            )
        )
    return count


def add_market_rows(
    output: list[dict[str, Any]],
    path: Path,
    master_rows: dict[str, dict[str, str]],
) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        source_info = {
            "titles": ["RYSXAI major info API", "RYSXAI major positions API"],
            "urls": [url for url in [text(row.get("info_url")), text(row.get("positions_url"))] if url],
            "publishers": ["RYSXAI", "RYSXAI"],
            "paths": market_source_paths(row),
        }
        output.append(
            evidence_row(
                row,
                master_rows,
                evidence_family="market_observation",
                signal_direction=market_direction(row),
                source_level="C",
                source_table="market_major_profiles_2026.csv",
                source_record_id=row.get("market_profile_id"),
                record_year="2026",
                record_type="market_profile",
                signal_label=join_nonempty(
                    [
                        f"demand={text(row.get('market_demand_signal_level'))}",
                        f"salary={text(row.get('market_salary_signal_level'))}",
                        f"activity={text(row.get('market_activity_signal_level'))}",
                    ]
                ),
                signal_value=join_nonempty(
                    [
                        f"demand_count={text(row.get('demand_count_national'))}",
                        f"salary_ref={text(row.get('salary_reference_national'))}",
                        f"job_samples={text(row.get('job_posting_sample_count'))}",
                    ]
                ),
                confidence="",
                source_ids=[],
                source_info=source_info,
                evidence_text=join_nonempty([row.get("top_industries"), row.get("top_job_titles"), row.get("top_skills")]),
                source_note=join_nonempty([row.get("top_regions"), row.get("top_job_directions")]),
                data_scope=text(row.get("data_scope")) or "third_party_major_market_observation",
            )
        )
    return count


def add_civil_rows(
    output: list[dict[str, Any]],
    path: Path,
    master_rows: dict[str, dict[str, str]],
) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        output.append(
            evidence_row(
                row,
                master_rows,
                evidence_family="civil_service",
                signal_direction=civil_direction(row),
                source_level="C",
                source_table="civil_service_major_opportunities_2026.csv",
                source_record_id=row.get("civil_service_major_id"),
                record_year="2026",
                record_type="civil_service_opportunity",
                signal_label=row.get("opportunity_level"),
                signal_value=join_nonempty(
                    [
                        f"role_matches={text(row.get('role_match_count'))}",
                        f"plans={text(row.get('plan_num_sum'))}",
                        f"weighted_competition={text(row.get('weighted_competition_ratio'))}",
                    ]
                ),
                confidence="",
                source_ids=[],
                source_info={},
                evidence_text=join_nonempty([row.get("sample_job_names"), row.get("sample_profession_texts")]),
                source_note=join_nonempty([row.get("sample_provinces"), row.get("sample_departments")]),
                data_scope=text(row.get("data_scope")) or "rysxai_civil_service_major_opportunity",
            )
        )
    return count


def add_new_quality_rows(
    output: list[dict[str, Any]],
    path: Path,
    master_rows: dict[str, dict[str, str]],
    source_map: dict[str, dict[str, str]],
) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        source_ids = split_ids(row.get("policy_source_ids"))
        output.append(
            evidence_row(
                row,
                master_rows,
                evidence_family="new_quality",
                signal_direction="opportunity" if new_quality_positive(row) else "reference",
                source_level=text(row.get("source_level")) or "B/C",
                source_table="new_quality_major_profiles_2026.csv",
                source_record_id=row.get("new_quality_profile_id"),
                record_year="2026",
                record_type="new_quality_productivity_profile",
                signal_label=row.get("support_category"),
                signal_value=join_nonempty(
                    [
                        f"is_new_quality={text(row.get('is_new_quality_productivity_major'))}",
                        f"score={text(row.get('rule_score'))}",
                        f"directions={text(row.get('directions'))}",
                    ]
                ),
                confidence=row.get("confidence"),
                source_ids=source_ids,
                source_info=source_info_for(source_ids, source_map),
                evidence_text=join_nonempty([row.get("rationale"), row.get("policy_evidence_excerpt")]),
                source_note=join_nonempty([row.get("official_major_source"), row.get("opportunity_risk_balance")]),
                data_scope=text(row.get("data_scope")) or "new_quality_productivity_major_support_profile",
            )
        )
    return count


def add_emerging_rows(
    output: list[dict[str, Any]],
    path: Path,
    master_rows: dict[str, dict[str, str]],
) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        source_info = {
            "titles": [text(row.get("first_source_title"))] if text(row.get("first_source_title")) else [],
            "urls": [text(row.get("first_source_url"))] if text(row.get("first_source_url")) else [],
            "publishers": ["Ministry of Education"] if text(row.get("first_source_url")) else [],
            "paths": [],
        }
        output.append(
            evidence_row(
                row,
                master_rows,
                evidence_family="emerging_major",
                signal_direction="opportunity",
                source_level=text(row.get("source_levels")) or "A",
                source_table="emerging_major_unique_majors_2026.csv",
                source_record_id=row.get("major_key"),
                record_year=row.get("latest_event_year"),
                record_type=row.get("event_types"),
                signal_label=row.get("candidate_statuses"),
                signal_value=join_nonempty(
                    [
                        f"first_event={text(row.get('first_event_year'))}",
                        f"sources={text(row.get('source_count'))}",
                        f"attachments={text(row.get('attachment_count'))}",
                    ]
                ),
                confidence="",
                source_ids=[],
                source_info=source_info,
                evidence_text=row.get("sample_evidence_text"),
                source_note=row.get("first_source_title"),
                data_scope="official_emerging_major_candidate_summary",
            )
        )
    return count


def add_vocational_rows(
    output: list[dict[str, Any]],
    path: Path,
    master_rows: dict[str, dict[str, str]],
) -> int:
    count = 0
    for row in safe_read_csv_rows(path):
        count += 1
        output.append(
            evidence_row(
                row,
                master_rows,
                evidence_family="vocational_register",
                signal_direction="mixed" if vocational_has_risk(row) else "reference",
                source_level="A",
                source_table="vocational_major_risk_link_summary_2013_2026.csv",
                source_record_id=row.get("major_key"),
                record_year=row.get("latest_year"),
                record_type="vocational_major_register_summary",
                signal_label=join_nonempty(
                    [row.get("employment_risk_levels"), row.get("official_policy_record_types")]
                ),
                signal_value=join_nonempty(
                    [
                        f"records={text(row.get('record_count'))}",
                        f"schools={text(row.get('school_count'))}",
                        f"latest_year_records={text(row.get('latest_year_record_count'))}",
                    ]
                ),
                confidence="",
                source_ids=split_ids(
                    join_nonempty(
                        [
                            row.get("employment_warning_record_ids"),
                            row.get("official_policy_warning_ids"),
                        ]
                    )
                ),
                source_info={},
                evidence_text=row.get("sample_schools_latest_year"),
                source_note=join_nonempty([row.get("years"), row.get("employment_warning_match_basis"), row.get("official_policy_match_basis")]),
                data_scope="official_vocational_major_register_summary",
            )
        )
    return count


def evidence_row(
    source_row: dict[str, str],
    master_rows: dict[str, dict[str, str]],
    *,
    evidence_family: str,
    signal_direction: str,
    source_level: str,
    source_table: str,
    source_record_id: Any,
    record_year: Any,
    record_type: Any,
    signal_label: Any,
    signal_value: Any,
    confidence: Any,
    source_ids: list[str],
    source_info: dict[str, list[str]],
    evidence_text: Any,
    source_note: Any,
    data_scope: Any,
) -> dict[str, Any]:
    major_code = text(source_row.get("major_code"))
    major_name = (
        text(source_row.get("standard_major_name"))
        or text(source_row.get("major_name"))
        or text(source_row.get("reported_major_name"))
    )
    major_level = normalize_source_level(source_row)
    master = find_master_row(master_rows, major_code, major_name, major_level)
    major_master_id = text(master.get("major_master_id")) if master else stable_id(
        "major_master", major_code, major_name, major_level
    )
    source_ids_text = "|".join(source_ids)
    evidence_id = stable_id(
        "major_evidence",
        evidence_family,
        source_table,
        source_record_id,
        major_code,
        major_name,
        major_level,
    )
    return {
        "evidence_id": evidence_id,
        "major_master_id": major_master_id,
        "major_code": major_code,
        "major_name": major_name,
        "major_level": major_level,
        "overall_review_bucket": text(master.get("overall_review_bucket")) if master else "",
        "evidence_family": evidence_family,
        "signal_direction": signal_direction,
        "source_level": source_level,
        "source_table": source_table,
        "source_record_id": text(source_record_id),
        "record_year": text(record_year),
        "record_type": text(record_type),
        "signal_label": text(signal_label),
        "signal_value": text(signal_value),
        "confidence": text(confidence),
        "source_ids": source_ids_text,
        "source_titles": join_unique_preserve_order(source_info.get("titles", [])),
        "source_urls": join_unique_preserve_order(source_info.get("urls", [])),
        "source_publishers": join_unique_preserve_order(source_info.get("publishers", [])),
        "source_paths": join_unique_preserve_order(source_info.get("paths", [])),
        "evidence_text": text(evidence_text),
        "source_note": text(source_note),
        "data_scope": text(data_scope),
        "needs_review": text(master.get("needs_review")) if master else "true",
    }


def build_major_summary_rows(
    evidence_rows: list[dict[str, Any]],
    master_rows: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in evidence_rows:
        grouped[row["major_master_id"]].append(row)
    summaries: list[dict[str, Any]] = []
    for major_master_id, rows in grouped.items():
        first = rows[0]
        master = find_master_by_id(master_rows, major_master_id) or {}
        family_counter = Counter(row["evidence_family"] for row in rows)
        source_ids = set()
        source_urls = set()
        source_titles = set()
        for row in rows:
            source_ids.update(split_ids(row.get("source_ids")))
            source_urls.update(split_ids(row.get("source_urls")))
            source_titles.update(split_ids(row.get("source_titles")))
        summaries.append(
            {
                "major_master_id": major_master_id,
                "major_code": first["major_code"],
                "major_name": first["major_name"],
                "major_level": first["major_level"],
                "overall_review_bucket": first["overall_review_bucket"],
                "risk_signal_count": text(master.get("risk_signal_count")),
                "opportunity_signal_count": text(master.get("opportunity_signal_count")),
                "evidence_record_count": len(rows),
                "risk_evidence_count": count_direction(rows, "risk"),
                "opportunity_evidence_count": count_direction(rows, "opportunity"),
                "reference_evidence_count": count_direction(rows, "reference"),
                "mixed_evidence_count": count_direction(rows, "mixed"),
                "employment_warning_evidence_count": family_counter["employment_warning"],
                "official_policy_evidence_count": family_counter["official_policy_warning"],
                "ai_replacement_evidence_count": family_counter["ai_replacement"],
                "market_observation_evidence_count": family_counter["market_observation"],
                "civil_service_evidence_count": family_counter["civil_service"],
                "new_quality_evidence_count": family_counter["new_quality"],
                "emerging_major_evidence_count": family_counter["emerging_major"],
                "vocational_register_evidence_count": family_counter["vocational_register"],
                "source_id_count": len(source_ids),
                "source_url_count": len(source_urls),
                "source_title_sample": join_sample(source_titles, limit=8),
                "source_url_sample": join_sample(source_urls, limit=8),
                "evidence_family_flags": "|".join(sorted(family_counter)),
            }
        )
    return sorted(summaries, key=summary_sort_key)


def build_source_summary_rows(evidence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in evidence_rows:
        key = (
            row["evidence_family"],
            row["signal_direction"],
            row["source_level"],
            row["source_table"],
        )
        groups[key].append(row)
    result: list[dict[str, Any]] = []
    for (family, direction, source_level, source_table), rows in sorted(groups.items()):
        source_ids: set[str] = set()
        source_urls: set[str] = set()
        high_risk_majors: set[str] = set()
        for row in rows:
            source_ids.update(split_ids(row.get("source_ids")))
            source_urls.update(split_ids(row.get("source_urls")))
            if row.get("overall_review_bucket") == "high_risk_review":
                high_risk_majors.add(row["major_master_id"])
        result.append(
            {
                "summary_id": stable_id("evidence_source_summary", family, direction, source_level, source_table),
                "evidence_family": family,
                "signal_direction": direction,
                "source_level": source_level,
                "source_table": source_table,
                "evidence_record_count": len(rows),
                "major_count": len({row["major_master_id"] for row in rows}),
                "source_id_count": len(source_ids),
                "source_url_count": len(source_urls),
                "high_risk_review_major_count": len(high_risk_majors),
            }
        )
    return result


def write_report(
    path: Path,
    manifest: dict[str, Any],
    evidence_rows: list[dict[str, Any]],
    major_summary_rows: list[dict[str, Any]],
    source_summary_rows: list[dict[str, Any]],
) -> None:
    family_counts = Counter(row["evidence_family"] for row in evidence_rows)
    direction_counts = Counter(row["signal_direction"] for row in evidence_rows)
    top_high_risk = [
        row
        for row in major_summary_rows
        if row["overall_review_bucket"] == "high_risk_review"
    ][:25]
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Major Risk Evidence Profiles",
        "",
        f"- Built at: {manifest['generated_at']}",
        f"- Evidence records: {manifest['row_counts']['evidence_records']}",
        f"- Major summaries: {manifest['row_counts']['major_summary']}",
        f"- Source summaries: {manifest['row_counts']['source_summary']}",
        f"- Majors with evidence: {manifest['major_counts']['majors_with_evidence']}",
        f"- High-risk review majors with evidence: {manifest['major_counts']['high_risk_review_majors_with_evidence']}",
        "",
        "## Evidence Families",
        "",
        "| family | records |",
        "|---|---:|",
    ]
    for family, count in sorted(family_counts.items()):
        lines.append(f"| {family} | {count} |")
    lines.extend(["", "## Signal Directions", "", "| direction | records |", "|---|---:|"])
    for direction, count in sorted(direction_counts.items()):
        lines.append(f"| {direction} | {count} |")
    lines.extend(
        [
            "",
            "## Source Summary",
            "",
            "| family | direction | source level | records | majors | urls |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in source_summary_rows:
        lines.append(
            "| {evidence_family} | {signal_direction} | {source_level} | "
            "{evidence_record_count} | {major_count} | {source_url_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Sample High-Risk Major Evidence Coverage",
            "",
            "| major | code | level | evidence records | risk | opportunity | source urls | families |",
            "|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in top_high_risk:
        lines.append(
            "| {major_name} | {major_code} | {major_level} | {evidence_record_count} | "
            "{risk_evidence_count} | {opportunity_evidence_count} | {source_url_count} | "
            "{evidence_family_flags} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Evidence records: `{manifest['outputs']['evidence_csv']}`",
            f"- Major summary: `{manifest['outputs']['major_summary_csv']}`",
            f"- Source summary: `{manifest['outputs']['source_summary_csv']}`",
            f"- Manifest: `{manifest['outputs']['manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- This is a long-form evidence table behind the master index. It keeps official, public warning, and third-party signals separate.",
            "- `source_urls` may be empty for derived third-party profile tables where the source is a local processed snapshot rather than a public document row.",
            "- `signal_direction` is a screening direction, not an admissions recommendation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def load_master_rows(path: Path) -> dict[str, dict[str, str]]:
    rows = list(safe_read_csv_rows(path))
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        code = text(row.get("major_code"))
        name = text(row.get("major_name"))
        level = normalize_level(row.get("major_level"))
        indexed[master_key(code, name, level)] = row
        if code:
            indexed.setdefault(master_key(code, "", level), row)
        if name:
            indexed.setdefault(master_key("", name, level), row)
        indexed.setdefault(f"id:{text(row.get('major_master_id'))}", row)
    return indexed


def find_master_row(
    master_rows: dict[str, dict[str, str]],
    major_code: str,
    major_name: str,
    major_level: str,
) -> dict[str, str] | None:
    level = normalize_level(major_level)
    for key in [
        master_key(major_code, major_name, level),
        master_key(major_code, "", level),
        master_key("", major_name, level),
    ]:
        if key in master_rows:
            return master_rows[key]
    return None


def find_master_by_id(
    master_rows: dict[str, dict[str, str]],
    major_master_id: str,
) -> dict[str, str] | None:
    return master_rows.get(f"id:{major_master_id}")


def load_warning_sources(path: Path) -> dict[str, dict[str, str]]:
    result = {}
    for row in safe_read_csv_rows(path):
        source_id = text(row.get("source_id"))
        if source_id:
            result[source_id] = row
    return result


def load_new_quality_sources(path: Path) -> dict[str, dict[str, str]]:
    result = {}
    for row in safe_read_csv_rows(path):
        source_id = text(row.get("source_id"))
        if source_id:
            result[source_id] = {
                "title": text(row.get("source_title")),
                "url": text(row.get("source_url")),
                "publisher": text(row.get("issuing_org")),
                "raw_path": "",
                "text_path": "",
            }
    return result


def source_info_for(
    source_ids: list[str],
    source_map: dict[str, dict[str, str]],
) -> dict[str, list[str]]:
    titles: list[str] = []
    urls: list[str] = []
    publishers: list[str] = []
    paths: list[str] = []
    for source_id in source_ids:
        source = source_map.get(source_id, {})
        add_if(titles, source.get("title"))
        add_if(urls, source.get("url"))
        add_if(publishers, source.get("publisher"))
        add_if(paths, source.get("raw_path"))
        add_if(paths, source.get("text_path"))
    return {"titles": titles, "urls": urls, "publishers": publishers, "paths": paths}


def market_source_paths(row: dict[str, str]) -> list[str]:
    profession_id = text(row.get("rysxai_profession_id"))
    paths: list[str] = []
    if text(row.get("info_url")):
        add_if(paths, rysxai_raw_source_path(profession_id, "info"))
    if text(row.get("positions_url")):
        add_if(paths, rysxai_raw_source_path(profession_id, "positions"))
    if paths:
        return paths
    fallback = text(row.get("source_snapshot_path"))
    return [fallback] if fallback else []


@lru_cache(maxsize=None)
def rysxai_raw_source_path(profession_id: str, endpoint: str) -> str:
    profession_id = text(profession_id)
    endpoint = text(endpoint)
    if not profession_id or endpoint not in {"info", "positions"}:
        return ""
    file_name = f"profession_{profession_id}_{endpoint}.raw.json"
    search_dirs = (
        [ROOT / "data/raw/rysxai_major_intros", ROOT / "data/raw/rysxai"]
        if endpoint == "info"
        else [ROOT / "data/raw/rysxai"]
    )
    for root_dir in search_dirs:
        if not root_dir.exists():
            continue
        matches = sorted(root_dir.glob(f"*/{file_name}"))
        if matches:
            return relative_path(matches[0])
    return ""


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_source_level(row: dict[str, str]) -> str:
    value = (
        row.get("education_level")
        or row.get("level")
        or row.get("major_level")
        or level_from_new_quality_type(row.get("major_type"))
    )
    if not text(value) and row.get("major_key") and text(row.get("record_count")):
        value = "\u4e13\u79d1"
    return normalize_level(value)


def level_from_new_quality_type(value: Any) -> str:
    value_text = text(value)
    if value_text == "1":
        return "\u672c\u79d1"
    if value_text == "2":
        return "\u4e13\u79d1"
    return value_text


def ai_high(row: dict[str, str]) -> bool:
    score = to_float(row.get("ai_replacement_score"))
    level = text(row.get("ai_replacement_level"))
    return level in {"\u8f83\u9ad8", "\u9ad8", "\u5f88\u9ad8", "high", "very_high"} or (
        score is not None and score >= 60
    )


def market_direction(row: dict[str, str]) -> str:
    values = {
        text(row.get("market_demand_signal_level")).lower(),
        text(row.get("market_salary_signal_level")).lower(),
        text(row.get("market_activity_signal_level")).lower(),
    }
    has_limited = "limited" in values
    has_high = bool(values & {"high", "very_high"})
    if has_limited and has_high:
        return "mixed"
    if has_limited:
        return "risk"
    if has_high:
        return "opportunity"
    return "reference"


def civil_direction(row: dict[str, str]) -> str:
    level = text(row.get("opportunity_level")).lower()
    if level in {"none", "limited"}:
        return "risk"
    if level in {"medium", "high", "very_high"} and to_int(row.get("role_match_count")) > 0:
        return "opportunity"
    return "reference"


def new_quality_positive(row: dict[str, str]) -> bool:
    return text(row.get("support_category")) in {"core", "related"} or text(
        row.get("is_new_quality_productivity_major")
    ) in {"\u662f", "\u76f8\u5173", "yes", "related"}


def vocational_has_risk(row: dict[str, str]) -> bool:
    return (
        text(row.get("has_employment_high_risk_warning")) == "true"
        or text(row.get("has_official_policy_warning")) == "true"
    )


def evidence_sort_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        text(row.get("major_level")),
        text(row.get("major_code")),
        text(row.get("major_name")),
        text(row.get("evidence_family")),
        text(row.get("record_year")),
    )


def summary_sort_key(row: dict[str, Any]) -> tuple[int, str, str]:
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
        text(row.get("major_code")),
        text(row.get("major_name")),
    )


def master_key(major_code: Any, major_name: Any, major_level: Any) -> str:
    return f"{text(major_code)}|{text(major_name)}|{normalize_level(major_level)}"


def split_ids(value: Any) -> list[str]:
    parts = re.split(r"[|;；,，]+", text(value))
    return [part.strip() for part in parts if part.strip()]


def join_nonempty(values: Iterable[Any]) -> str:
    return "|".join(text(value) for value in values if text(value))


def join_unique(values: Iterable[Any]) -> str:
    return "|".join(sorted({text(value) for value in values if text(value)}))


def join_unique_preserve_order(values: Iterable[Any]) -> str:
    seen = set()
    result = []
    for value in values:
        value_text = text(value)
        if value_text and value_text not in seen:
            seen.add(value_text)
            result.append(value_text)
    return "|".join(result)


def join_sample(values: Iterable[Any], *, limit: int) -> str:
    return "|".join(sorted({text(value) for value in values if text(value)})[:limit])


def count_direction(rows: list[dict[str, Any]], direction: str) -> int:
    return sum(1 for row in rows if row.get("signal_direction") == direction)


def add_if(values: list[str], value: Any) -> None:
    value_text = text(value)
    if value_text:
        values.append(value_text)


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


def to_float(value: Any) -> float | None:
    try:
        value_text = text(value)
        if not value_text:
            return None
        return float(value_text)
    except (TypeError, ValueError):
        return None


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build long-form major risk evidence profiles.")
    parser.add_argument("--master-index-csv", type=Path, default=ROOT / "data/processed/major_risk_master_index/major_risk_master_index_2026.csv")
    parser.add_argument("--employment-warnings-csv", type=Path, default=ROOT / "data/processed/major_risk_warnings/major_risk_warning_records.csv")
    parser.add_argument("--official-policy-warnings-csv", type=Path, default=ROOT / "data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv")
    parser.add_argument("--warning-sources-csv", type=Path, default=ROOT / "data/processed/major_risk_warnings/major_risk_warning_sources.csv")
    parser.add_argument("--ai-replacement-csv", type=Path, default=ROOT / "data/processed/ai_replacement/major_ai_replacement_ranking.csv")
    parser.add_argument("--market-profiles-csv", type=Path, default=ROOT / "data/processed/rysxai_market/market_major_profiles_2026.csv")
    parser.add_argument("--civil-service-major-csv", type=Path, default=ROOT / "data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv")
    parser.add_argument("--new-quality-profiles-csv", type=Path, default=ROOT / "data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv")
    parser.add_argument("--new-quality-policy-sources-csv", type=Path, default=ROOT / "data/processed/new_quality_major_profiles/new_quality_policy_sources_2026.csv")
    parser.add_argument("--emerging-majors-csv", type=Path, default=ROOT / "data/processed/emerging_major_candidate_details/emerging_major_unique_majors_2026.csv")
    parser.add_argument("--vocational-summary-csv", type=Path, default=ROOT / "data/processed/vocational_major_register/vocational_major_risk_link_summary_2013_2026.csv")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_major_risk_evidence_profiles(
        master_index_csv=args.master_index_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        warning_sources_csv=args.warning_sources_csv,
        ai_replacement_csv=args.ai_replacement_csv,
        market_profiles_csv=args.market_profiles_csv,
        civil_service_major_csv=args.civil_service_major_csv,
        new_quality_profiles_csv=args.new_quality_profiles_csv,
        new_quality_policy_sources_csv=args.new_quality_policy_sources_csv,
        emerging_majors_csv=args.emerging_majors_csv,
        vocational_summary_csv=args.vocational_summary_csv,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        generated_at=args.generated_at,
    )
    print(
        json.dumps(
            {
                "dataset": "major_risk_evidence_profiles",
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
                "evidence_family_counts": manifest["evidence_family_counts"],
                "signal_direction_counts": manifest["signal_direction_counts"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
