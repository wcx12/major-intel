import csv
import json
from pathlib import Path

from scripts.ingestion.build_major_risk_evidence_profiles import (
    build_major_risk_evidence_profiles,
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


def test_build_major_risk_evidence_profiles_links_sources_and_summarizes(tmp_path):
    master = tmp_path / "master.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    sources = tmp_path / "sources.csv"
    ai = tmp_path / "ai.csv"
    market = tmp_path / "market.csv"
    civil = tmp_path / "civil.csv"
    new_quality = tmp_path / "new_quality.csv"
    nq_sources = tmp_path / "nq_sources.csv"
    emerging = tmp_path / "emerging.csv"
    vocational = tmp_path / "vocational.csv"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "report"

    write_csv(
        master,
        [
            {
                "major_master_id": "major_master:test",
                "major_code": "050201",
                "major_name": "英语",
                "major_level": "本科",
                "overall_review_bucket": "high_risk_review",
                "risk_signal_count": "3",
                "opportunity_signal_count": "1",
                "needs_review": "false",
            }
        ],
        [
            "major_master_id",
            "major_code",
            "major_name",
            "major_level",
            "overall_review_bucket",
            "risk_signal_count",
            "opportunity_signal_count",
            "needs_review",
        ],
    )
    write_csv(
        sources,
        [
            {
                "source_id": "src1",
                "title": "就业预警来源",
                "url": "https://example.test/warn",
                "publisher": "publisher",
                "raw_path": "raw.html",
                "text_path": "raw.txt",
            }
        ],
        ["source_id", "title", "url", "publisher", "raw_path", "text_path"],
    )
    write_csv(
        employment,
        [
            {
                "record_id": "e1",
                "report_year": "2025",
                "education_level": "本科",
                "risk_level": "red",
                "reported_major_name": "英语",
                "standard_major_name": "英语",
                "major_code": "050201",
                "source_ids": "src1",
                "evidence_type": "table",
                "evidence_text": "红牌专业包括英语。",
                "confidence": "high",
                "notes": "note",
            }
        ],
        [
            "record_id",
            "report_year",
            "education_level",
            "risk_level",
            "reported_major_name",
            "standard_major_name",
            "major_code",
            "source_ids",
            "evidence_type",
            "evidence_text",
            "confidence",
            "notes",
        ],
    )
    write_csv(
        policy,
        [
            {
                "warning_id": "p1",
                "policy_year": "2024",
                "education_level": "本科",
                "record_type": "major_cancel",
                "warning_label": "撤销",
                "reported_major_name": "英语",
                "standard_major_name": "英语",
                "major_code": "050201",
                "policy_action": "撤销",
                "criterion_text": "source criterion",
                "source_row_no": "1",
                "source_ids": "src1",
                "evidence_text": "表格列出英语。",
                "confidence": "high",
            }
        ],
        [
            "warning_id",
            "policy_year",
            "education_level",
            "record_type",
            "warning_label",
            "reported_major_name",
            "standard_major_name",
            "major_code",
            "policy_action",
            "criterion_text",
            "source_row_no",
            "source_ids",
            "evidence_text",
            "confidence",
        ],
    )
    write_csv(
        ai,
        [
            {
                "profession_id": "1",
                "major_code": "050201",
                "major_name": "英语",
                "level": "本科",
                "rank": "2",
                "ai_replacement_score": "66",
                "ai_replacement_level": "较高",
                "confidence_score": "90",
                "source_fields": "jobs",
                "top_risky_jobs": "翻译",
                "top_resilient_jobs": "教师",
                "main_reasons": "文本任务可自动化",
                "data_scope": "test_ai",
            }
        ],
        [
            "profession_id",
            "major_code",
            "major_name",
            "level",
            "rank",
            "ai_replacement_score",
            "ai_replacement_level",
            "confidence_score",
            "source_fields",
            "top_risky_jobs",
            "top_resilient_jobs",
            "main_reasons",
            "data_scope",
        ],
    )
    write_csv(
        market,
        [
            {
                "market_profile_id": "m1",
                "major_code": "050201",
                "major_name": "英语",
                "level": "本科",
                "market_demand_signal_level": "limited",
                "market_salary_signal_level": "medium",
                "market_activity_signal_level": "limited",
                "demand_count_national": "100",
                "salary_reference_national": "7000",
                "job_posting_sample_count": "5",
                "top_industries": "教育:3",
                "top_job_titles": "教师:2",
                "top_skills": "英语:5",
                "info_url": "https://example.test/info",
                "positions_url": "https://example.test/jobs",
                "source_snapshot_path": "snapshot.json",
                "data_scope": "market",
            }
        ],
        [
            "market_profile_id",
            "major_code",
            "major_name",
            "level",
            "market_demand_signal_level",
            "market_salary_signal_level",
            "market_activity_signal_level",
            "demand_count_national",
            "salary_reference_national",
            "job_posting_sample_count",
            "top_industries",
            "top_job_titles",
            "top_skills",
            "info_url",
            "positions_url",
            "source_snapshot_path",
            "data_scope",
        ],
    )
    write_csv(civil, [], ["major_code", "major_name", "major_level"])
    write_csv(
        nq_sources,
        [
            {
                "source_id": "nq1",
                "source_title": "AI政策",
                "source_url": "https://example.test/policy",
                "issuing_org": "gov",
            }
        ],
        ["source_id", "source_title", "source_url", "issuing_org"],
    )
    write_csv(
        new_quality,
        [
            {
                "new_quality_profile_id": "nq_profile",
                "major_code": "050201",
                "major_name": "英语",
                "major_type": "1",
                "support_category": "related",
                "is_new_quality_productivity_major": "相关",
                "directions": "digital_economy",
                "confidence": "medium",
                "rule_score": "3",
                "policy_source_ids": "nq1",
                "rationale": "命中方向",
                "policy_evidence_excerpt": "政策证据",
                "official_major_source": "catalog",
                "opportunity_risk_balance": "policy_supported_with_risk_flags",
                "source_level": "B/C",
                "data_scope": "nq",
            }
        ],
        [
            "new_quality_profile_id",
            "major_code",
            "major_name",
            "major_type",
            "support_category",
            "is_new_quality_productivity_major",
            "directions",
            "confidence",
            "rule_score",
            "policy_source_ids",
            "rationale",
            "policy_evidence_excerpt",
            "official_major_source",
            "opportunity_risk_balance",
            "source_level",
            "data_scope",
        ],
    )
    write_csv(emerging, [], ["major_code", "major_name", "major_level"])
    write_csv(vocational, [], ["major_code", "major_name", "major_key", "record_count"])

    manifest = build_major_risk_evidence_profiles(
        master_index_csv=master,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        warning_sources_csv=sources,
        ai_replacement_csv=ai,
        market_profiles_csv=market,
        civil_service_major_csv=civil,
        new_quality_profiles_csv=new_quality,
        new_quality_policy_sources_csv=nq_sources,
        emerging_majors_csv=emerging,
        vocational_summary_csv=vocational,
        output_dir=output_dir,
        report_dir=report_dir,
        generated_at="2026-06-14",
    )

    evidence_rows = read_rows(output_dir / "major_risk_evidence_records_2026.csv")
    summary_rows = read_rows(output_dir / "major_risk_evidence_major_summary_2026.csv")
    manifest_data = json.loads(
        (output_dir / "major_risk_evidence_profiles_manifest_2026.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["row_counts"]["evidence_records"] == 5
    assert {row["evidence_family"] for row in evidence_rows} == {
        "employment_warning",
        "official_policy_warning",
        "ai_replacement",
        "market_observation",
        "new_quality",
    }
    employment_row = next(row for row in evidence_rows if row["evidence_family"] == "employment_warning")
    assert employment_row["source_urls"] == "https://example.test/warn"
    ai_row = next(row for row in evidence_rows if row["evidence_family"] == "ai_replacement")
    assert ai_row["signal_direction"] == "risk"
    market_row = next(row for row in evidence_rows if row["evidence_family"] == "market_observation")
    assert market_row["source_urls"] == "https://example.test/info|https://example.test/jobs"
    assert market_row["source_paths"] == "snapshot.json"
    nq_row = next(row for row in evidence_rows if row["evidence_family"] == "new_quality")
    assert nq_row["source_titles"] == "AI政策"
    assert summary_rows[0]["evidence_record_count"] == "5"
    assert summary_rows[0]["source_url_count"] == "4"
    assert manifest_data["major_counts"]["high_risk_review_majors_with_evidence"] == 1
    assert (report_dir / "major_risk_evidence_profiles_2026.md").exists()
