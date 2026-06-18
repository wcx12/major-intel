import csv
import json

from scripts.ingestion.build_rysxai_major_intro_risk_profiles import (
    build_rysxai_major_intro_risk_profiles,
)


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


def test_build_rysxai_major_intro_risk_profiles_links_sources(tmp_path):
    intros = tmp_path / "intros.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    ai = tmp_path / "ai.csv"
    profiles = tmp_path / "profiles.csv"
    summary = tmp_path / "summary.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    intro_fields = [
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
        "major_detail",
        "major_course",
        "undergraduate_to_graduate",
        "similar_majors",
        "captured_at",
        "info_url",
    ]
    write_csv(
        intros,
        [
            {
                "rysxai_profession_id": "270",
                "major_code": "080201",
                "major_name": "Mechanical Engineering",
                "level": "undergraduate",
                "degree": "BE",
                "limit_year": "4",
                "selection_advice": "physics",
                "enrollment_scale": "100",
                "univ_count": "10",
                "apply_plan_ratio": "120",
                "major_detail": "detail",
                "major_course": "course",
                "undergraduate_to_graduate": "graduate",
                "similar_majors": "similar",
                "captured_at": "2026-06-11T00:00:00+08:00",
                "info_url": "https://example.test/info?id=270",
            }
        ],
        intro_fields,
    )
    write_csv(
        employment,
        [
            {
                "record_id": "risk1",
                "report_year": "2025",
                "risk_level": "red",
                "reported_major_name": "Mechanical Engineering",
                "standard_major_name": "Mechanical Engineering",
                "major_code": "080201",
            }
        ],
        [
            "record_id",
            "report_year",
            "risk_level",
            "reported_major_name",
            "standard_major_name",
            "major_code",
        ],
    )
    write_csv(
        policy,
        [
            {
                "warning_id": "policy1",
                "policy_year": "2024",
                "record_type": "major_cancel",
                "reported_major_name": "Mechanical Engineering",
                "standard_major_name": "Mechanical Engineering",
                "major_code": "080201",
            }
        ],
        [
            "warning_id",
            "policy_year",
            "record_type",
            "reported_major_name",
            "standard_major_name",
            "major_code",
        ],
    )
    write_csv(
        ai,
        [
            {
                "profession_id": "270",
                "major_code": "080201",
                "major_name": "Mechanical Engineering",
                "rank": "7",
                "ai_replacement_score": "61.5",
                "ai_replacement_level": "medium",
                "confidence_score": "80",
                "candidate_count": "12",
                "top_risky_jobs": "drafting",
            }
        ],
        [
            "profession_id",
            "major_code",
            "major_name",
            "rank",
            "ai_replacement_score",
            "ai_replacement_level",
            "confidence_score",
            "candidate_count",
            "top_risky_jobs",
        ],
    )

    result = build_rysxai_major_intro_risk_profiles(
        major_introductions_csv=intros,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        ai_replacement_csv=ai,
        output_profiles_csv=profiles,
        output_summary_csv=summary,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    rows = read_rows(profiles)
    assert result["output_profile_count"] == 1
    assert result["linked_high_risk_profile_count"] == 1
    assert result["linked_policy_profile_count"] == 1
    assert result["linked_ai_replacement_profile_count"] == 1
    assert rows[0]["has_employment_red_warning"] == "true"
    assert rows[0]["has_official_policy_warning"] == "true"
    assert rows[0]["ai_replacement_score"] == "61.5"
    assert rows[0]["has_major_course"] == "true"
    assert json.loads(manifest.read_text(encoding="utf-8"))["summary_row_count"] == 1
