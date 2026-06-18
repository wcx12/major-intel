import csv
import json

from scripts.ingestion.build_rysxai_market_observations import (
    build_rysxai_market_observations,
)


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


def write_snapshot(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_build_rysxai_market_observations_outputs_linked_tables(tmp_path):
    snapshots_dir = tmp_path / "snapshots"
    seed = tmp_path / "seed.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    ai = tmp_path / "ai.csv"
    civil = tmp_path / "civil.csv"
    transfer = tmp_path / "transfer.csv"

    profiles = tmp_path / "profiles.csv"
    jobs = tmp_path / "jobs.csv"
    city_salary = tmp_path / "city_salary.csv"
    distributions = tmp_path / "distributions.csv"
    rankings = tmp_path / "rankings.csv"
    skills = tmp_path / "skills.csv"
    summary = tmp_path / "summary.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    write_csv(
        seed,
        [
            {
                "rysxai_profession_id": "270",
                "major_code": "080201",
                "major_name": "Mechanical Engineering",
                "level": "undergraduate",
                "category": "engineering",
                "subject": "mechanical",
                "degree": "BE",
                "limit_year": "4",
                "heat": "100",
                "is_hot": "true",
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
            "limit_year",
            "heat",
            "is_hot",
        ],
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
                "rank": "8",
                "ai_replacement_score": "63.5",
                "ai_replacement_level": "medium",
                "confidence_score": "88",
                "candidate_count": "12",
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
        ],
    )
    write_csv(
        civil,
        [
            {
                "civil_service_major_id": "civil1",
                "major_code": "080201",
                "major_name": "Mechanical Engineering",
                "opportunity_level": "high",
                "role_match_count": "21",
                "plan_num_sum": "34",
                "weighted_competition_ratio": "65.2",
            }
        ],
        [
            "civil_service_major_id",
            "major_code",
            "major_name",
            "opportunity_level",
            "role_match_count",
            "plan_num_sum",
            "weighted_competition_ratio",
        ],
    )
    write_csv(
        transfer,
        [
            {
                "transfer_policy_major_id": "transfer1",
                "major_code": "080201",
                "major_name": "Mechanical Engineering",
                "mentioned_in_school_count": "12",
                "high_difficulty_school_count": "3",
            }
        ],
        [
            "transfer_policy_major_id",
            "major_code",
            "major_name",
            "mentioned_in_school_count",
            "high_difficulty_school_count",
        ],
    )

    write_snapshot(
        snapshots_dir / "profession_270_market_snapshot.json",
        {
            "schema_version": "rysxai_market_snapshot/v1",
            "captured_at": "2026-05-19T16:52:42+08:00",
            "source": {
                "name": "rysxai",
                "source_level": "C",
                "info_url": "https://example.test/info?id=270",
                "positions_url": "https://example.test/positions?id=270",
            },
            "profession": {
                "id": 270,
                "name": "Mechanical Engineering",
                "code": "080201",
                "level": "undergraduate",
                "degree": "BE",
                "limit_year": "4",
                "selection_advice": "physics",
            },
            "macro_employment": {
                "industry_distribution": [
                    {"label": "machinery", "rate_percent": 29.61}
                ],
                "region_distribution": [
                    {"label": "Shanghai", "rate_percent": 15.1}
                ],
                "job_direction_distribution": [
                    {
                        "label": "mechanical design",
                        "rate_percent": 21,
                        "detail_jobs": ["design engineer"],
                    }
                ],
            },
            "demand_ranking": [
                {"region": "全国", "demand_count": 61649},
                {"region": "Shanghai", "demand_count": 9396},
            ],
            "salary_ranking": [
                {"region": "全国", "monthly_salary_reference": 7516},
                {"region": "Shanghai", "monthly_salary_reference": 8945},
            ],
            "job_posting_sample_total_reported": 2,
            "job_posting_sample_count": 2,
            "job_posting_samples": [
                {
                    "source_item_id": 50,
                    "job_title": "Mechanical Engineer",
                    "company_name": "Alpha",
                    "city": "Wuxi",
                    "district": "Huishan",
                    "industry": "equipment",
                    "salary_raw": "15-20K",
                    "monthly_salary_min": 15000,
                    "monthly_salary_max": 20000,
                    "education": "bachelor",
                    "experience": "5-10 years",
                    "skills": ["CAD", "design"],
                    "company_tags": ["equipment"],
                    "company_scale": "20-99",
                    "financing_stage": "",
                    "bossName": "drop me",
                },
                {
                    "source_item_id": 47,
                    "job_title": "Mechanical Engineer",
                    "company_name": "Beta",
                    "city": "Shanghai",
                    "district": "Fengxian",
                    "industry": "instrument",
                    "salary_raw": "9-14K",
                    "monthly_salary_min": 9000,
                    "monthly_salary_max": 14000,
                    "education": "bachelor",
                    "experience": "3-5 years",
                    "skills": ["CAD"],
                    "company_tags": ["instrument"],
                    "company_scale": "100-499",
                    "financing_stage": "",
                },
            ],
            "salary_observations_by_city": {
                "Wuxi": {
                    "sample_count": 1,
                    "monthly_salary_min_observed": 15000,
                    "monthly_salary_max_observed": 20000,
                    "monthly_salary_midpoint_avg": 17500,
                }
            },
        },
    )

    result = build_rysxai_market_observations(
        snapshots_dir=snapshots_dir,
        major_seed_csv=seed,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        ai_replacement_csv=ai,
        civil_service_major_csv=civil,
        transfer_policy_major_csv=transfer,
        output_profiles_csv=profiles,
        output_job_samples_csv=jobs,
        output_city_salary_csv=city_salary,
        output_distributions_csv=distributions,
        output_rankings_csv=rankings,
        output_skill_summary_csv=skills,
        output_summary_csv=summary,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    profile_rows = read_rows(profiles)
    job_rows = read_rows(jobs)
    skill_rows = read_rows(skills)
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))

    assert result["profile_row_count"] == 1
    assert result["job_sample_row_count"] == 2
    assert result["distribution_row_count"] == 3
    assert result["ranking_row_count"] == 4
    assert result["skill_summary_row_count"] == 2
    assert profile_rows[0]["salary_sample_midpoint_avg"] == "14500"
    assert profile_rows[0]["salary_reference_national"] == "7516"
    assert profile_rows[0]["demand_count_national"] == "61649"
    assert profile_rows[0]["has_employment_red_warning"] == "true"
    assert profile_rows[0]["has_official_policy_warning"] == "true"
    assert profile_rows[0]["has_ai_medium_or_high_risk"] == "true"
    assert profile_rows[0]["has_civil_service_match"] == "true"
    assert profile_rows[0]["has_transfer_policy_mention"] == "true"
    assert "bossName" not in job_rows[0]
    assert job_rows[0]["monthly_salary_midpoint"] == "17500"
    assert skill_rows[0]["skill"] == "CAD"
    assert manifest_data["summary_row_count"] >= 3
