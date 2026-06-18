import csv
import json
from pathlib import Path

from scripts.ingestion.build_major_risk_master_index import (
    build_major_risk_master_index,
)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_build_major_risk_master_index_merges_risk_and_opportunity_signals(tmp_path):
    seed = tmp_path / "seeds.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    ai = tmp_path / "ai.csv"
    market = tmp_path / "market.csv"
    civil = tmp_path / "civil.csv"
    new_quality = tmp_path / "new_quality.csv"
    emerging = tmp_path / "emerging.csv"
    vocational = tmp_path / "vocational.csv"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "reports"

    write_csv(
        seed,
        [
            {
                "rysxai_profession_id": "1",
                "major_code": "080717T",
                "major_name": "人工智能",
                "level": "本科",
                "category": "工学",
                "subject": "电子信息类",
                "degree": "工学学士",
            }
        ],
        [
            "rysxai_profession_id",
            "major_code",
            "major_name",
            "level",
            "category",
            "subject",
            "degree",
        ],
    )
    write_csv(
        employment,
        [
            {
                "education_level": "本科",
                "standard_major_name": "人工智能",
                "major_code": "080717T",
                "discipline": "工学",
                "major_category": "电子信息类",
                "red_count": "1",
                "yellow_count": "0",
                "green_count": "0",
                "latest_risk_level": "red",
                "latest_report_year": "2026",
            }
        ],
        [
            "education_level",
            "standard_major_name",
            "major_code",
            "discipline",
            "major_category",
            "red_count",
            "yellow_count",
            "green_count",
            "latest_risk_level",
            "latest_report_year",
        ],
    )
    write_csv(
        policy,
        [
            {
                "warning_id": "p1",
                "policy_year": "2025",
                "education_level": "本科",
                "record_type": "major_stop_enrollment",
                "standard_major_name": "人工智能",
                "reported_major_name": "人工智能",
                "major_code": "080717T",
                "discipline": "工学",
                "major_category": "电子信息类",
            }
        ],
        [
            "warning_id",
            "policy_year",
            "education_level",
            "record_type",
            "standard_major_name",
            "reported_major_name",
            "major_code",
            "discipline",
            "major_category",
        ],
    )
    write_csv(
        ai,
        [
            {
                "rank": "5",
                "major_code": "080717T",
                "major_name": "人工智能",
                "level": "本科",
                "ai_replacement_score": "66.5",
                "ai_replacement_level": "较高",
                "confidence_score": "91",
                "candidate_count": "20",
            }
        ],
        [
            "rank",
            "major_code",
            "major_name",
            "level",
            "ai_replacement_score",
            "ai_replacement_level",
            "confidence_score",
            "candidate_count",
        ],
    )
    write_csv(
        market,
        [
            {
                "major_code": "080717T",
                "major_name": "人工智能",
                "level": "本科",
                "category": "工学",
                "subject": "电子信息类",
                "demand_count_national": "1000",
                "salary_reference_national": "12000",
                "job_posting_sample_count": "8",
                "market_demand_signal_level": "high",
                "market_salary_signal_level": "high",
                "market_activity_signal_level": "very_high",
                "top_industries": "互联网:3",
                "top_job_titles": "算法工程师:3",
                "top_skills": "Python:4",
            }
        ],
        [
            "major_code",
            "major_name",
            "level",
            "category",
            "subject",
            "demand_count_national",
            "salary_reference_national",
            "job_posting_sample_count",
            "market_demand_signal_level",
            "market_salary_signal_level",
            "market_activity_signal_level",
            "top_industries",
            "top_job_titles",
            "top_skills",
        ],
    )
    write_csv(
        civil,
        [
            {
                "major_code": "080717T",
                "major_name": "人工智能",
                "major_level": "本科",
                "opportunity_level": "medium",
                "role_match_count": "10",
                "plan_num_sum": "12",
                "weighted_competition_ratio": "80",
                "has_civil_service_match": "true",
            }
        ],
        [
            "major_code",
            "major_name",
            "major_level",
            "opportunity_level",
            "role_match_count",
            "plan_num_sum",
            "weighted_competition_ratio",
            "has_civil_service_match",
        ],
    )
    write_csv(
        new_quality,
        [
            {
                "major_code": "080717T",
                "major_name": "人工智能",
                "major_type": "本科(普通)",
                "major_level2": "工学",
                "major_level3": "电子信息类",
                "support_category": "core",
                "is_new_quality_productivity_major": "是",
                "directions": "artificial_intelligence",
                "confidence": "high",
                "rule_score": "8",
                "policy_source_count": "2",
                "opportunity_risk_balance": "policy_supported_with_risk_flags",
            }
        ],
        [
            "major_code",
            "major_name",
            "major_type",
            "major_level2",
            "major_level3",
            "support_category",
            "is_new_quality_productivity_major",
            "directions",
            "confidence",
            "rule_score",
            "policy_source_count",
            "opportunity_risk_balance",
        ],
    )
    write_csv(
        emerging,
        [
            {
                "major_code": "080717T",
                "major_name": "人工智能",
                "major_level": "本科",
                "discipline_category": "工学",
                "major_class": "电子信息类",
                "first_event_year": "2018",
                "latest_event_year": "2026",
                "event_types": "catalog_added",
                "candidate_statuses": "catalog_confirmed",
                "source_count": "2",
                "attachment_count": "1",
                "evidence_count": "3",
            },
            {
                "major_code": "",
                "major_name": "备注",
                "major_level": "本科",
                "discipline_category": "",
                "major_class": "",
                "first_event_year": "2012",
                "latest_event_year": "2012",
                "event_types": "catalog_added",
                "candidate_statuses": "catalog_candidate",
                "source_count": "1",
                "attachment_count": "1",
                "evidence_count": "1",
            },
        ],
        [
            "major_code",
            "major_name",
            "major_level",
            "discipline_category",
            "major_class",
            "first_event_year",
            "latest_event_year",
            "event_types",
            "candidate_statuses",
            "source_count",
            "attachment_count",
            "evidence_count",
        ],
    )
    write_csv(
        vocational,
        [],
        [
            "major_code",
            "major_name",
            "first_year",
            "latest_year",
            "years",
            "record_count",
            "province_count",
            "school_count",
            "latest_year_record_count",
            "latest_year_school_count",
        ],
    )

    manifest = build_major_risk_master_index(
        major_seed_csv=seed,
        employment_summary_csv=employment,
        official_policy_warnings_csv=policy,
        ai_replacement_csv=ai,
        market_profiles_csv=market,
        civil_service_major_csv=civil,
        new_quality_profiles_csv=new_quality,
        emerging_majors_csv=emerging,
        vocational_summary_csv=vocational,
        output_dir=output_dir,
        report_dir=report_dir,
        generated_at="2026-06-14",
    )

    rows = read_rows(output_dir / "major_risk_master_index_2026.csv")
    target = next(row for row in rows if row["major_code"] == "080717T")
    note = next(row for row in rows if row["major_name"] == "备注")
    manifest_data = json.loads(
        (output_dir / "major_risk_master_index_manifest_2026.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["row_counts"]["master_index"] == 2
    assert target["overall_review_bucket"] == "high_risk_review"
    assert target["risk_signal_count"] == "3"
    assert target["opportunity_signal_count"] == "4"
    assert target["has_official_policy_warning"] == "true"
    assert "employment_red_or_yellow_warning" in target["primary_risk_reasons"]
    assert "new_quality_policy_support" in target["primary_opportunity_reasons"]
    assert note["needs_review"] == "true"
    assert "non_major_or_table_note_name" in note["review_notes"]
    assert manifest_data["risk_summary"]["high_risk_review_count"] == 1
    assert (report_dir / "major_risk_master_index_2026.md").exists()
