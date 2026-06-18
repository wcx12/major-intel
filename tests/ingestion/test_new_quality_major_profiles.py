import csv
import json

from scripts.ingestion.build_new_quality_major_profiles import (
    build_new_quality_major_profiles,
)


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


def test_build_new_quality_major_profiles_links_support_and_risk_sources(tmp_path):
    source_summary = tmp_path / "source_summary.csv"
    source_detail = tmp_path / "source_detail.csv"
    policy_sources = tmp_path / "policy_sources.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    ai = tmp_path / "ai.csv"
    market = tmp_path / "market.csv"
    civil = tmp_path / "civil.csv"
    transfer = tmp_path / "transfer.csv"
    profiles = tmp_path / "profiles.csv"
    tiers = tmp_path / "tiers.csv"
    policy_out = tmp_path / "policy_out.csv"
    summary = tmp_path / "summary.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    summary_fields = [
        "major_special_id",
        "major_code",
        "major_name",
        "major_type",
        "major_level2",
        "major_level3",
        "evaluation_label",
        "is_new_quality_productivity_major",
        "directions",
        "confidence",
        "score",
        "rationale",
        "policy_source_ids",
        "policy_evidence_excerpt",
        "official_major_source",
        "qingbei_sample",
        "tier_985_sample",
        "tier_211_sample",
        "shuangfei_sample",
        "sample_coverage",
        "needs_review",
    ]
    write_csv(
        source_summary,
        [
            {
                "major_special_id": "080717T",
                "major_code": "080717T",
                "major_name": "人工智能",
                "major_type": "1",
                "major_level2": "工学",
                "major_level3": "电子信息类",
                "evaluation_label": "是",
                "is_new_quality_productivity_major": "是",
                "directions": "artificial_intelligence;digital_economy",
                "confidence": "high",
                "score": "8",
                "rationale": "专业名称直接命中人工智能",
                "policy_source_ids": "policy_ai",
                "policy_evidence_excerpt": "AI policy evidence",
                "official_major_source": "official catalog",
                "qingbei_sample": "清华大学，排名1；同层次样本数1",
                "tier_985_sample": "浙江大学，排名3；同层次样本数3",
                "tier_211_sample": "北京邮电大学，排名40；同层次样本数5",
                "shuangfei_sample": "深圳大学，排名60；同层次样本数8",
                "sample_coverage": "4/4",
                "needs_review": "否",
            }
        ],
        summary_fields,
    )

    detail_fields = [
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
        "is_new_quality_productivity_major",
        "directions",
        "confidence",
        "score",
        "rationale",
        "policy_source_ids",
        "policy_evidence_excerpt",
        "official_major_source",
        "school_sample_source",
        "estimation_method",
        "needs_review",
    ]
    write_csv(
        source_detail,
        [
            {
                "major_special_id": "080717T",
                "major_code": "080717T",
                "major_name": "人工智能",
                "major_type": "1",
                "major_level2": "工学",
                "major_level3": "电子信息类",
                "school_tier": "985",
                "sample_school_id": "10335",
                "sample_school_name": "浙江大学",
                "sample_school_rank": "3",
                "sample_school_found": "是",
                "tier_offer_count": "3",
                "evaluation_label": "是",
                "is_new_quality_productivity_major": "是",
                "directions": "artificial_intelligence",
                "confidence": "high",
                "score": "8",
                "rationale": "专业名称直接命中人工智能",
                "policy_source_ids": "policy_ai",
                "policy_evidence_excerpt": "AI policy evidence",
                "official_major_source": "official catalog",
                "school_sample_source": "local db",
                "estimation_method": "rule",
                "needs_review": "否",
            }
        ],
        detail_fields,
    )
    write_csv(
        policy_sources,
        [
            {
                "direction": "artificial_intelligence",
                "source_id": "policy_ai",
                "source_title": "AI policy",
                "source_url": "https://example.test/ai",
                "source_year": "2025",
                "issuing_org": "gov",
                "keyword": "人工智能",
                "evidence_excerpt": "support AI",
            }
        ],
        [
            "direction",
            "source_id",
            "source_title",
            "source_url",
            "source_year",
            "issuing_org",
            "keyword",
            "evidence_excerpt",
        ],
    )
    write_csv(
        employment,
        [
            {
                "record_id": "risk1",
                "report_year": "2025",
                "risk_level": "yellow",
                "reported_major_name": "人工智能",
                "standard_major_name": "人工智能",
                "major_code": "080717T",
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
                "warning_id": "official1",
                "policy_year": "2024",
                "record_type": "major_warning_list",
                "reported_major_name": "人工智能",
                "standard_major_name": "人工智能",
                "major_code": "080717T",
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
                "major_code": "080717T",
                "major_name": "人工智能",
                "rank": "4",
                "ai_replacement_score": "58",
                "ai_replacement_level": "medium",
                "confidence_score": "90",
                "candidate_count": "20",
            }
        ],
        [
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
        market,
        [
            {
                "market_profile_id": "market1",
                "major_code": "080717T",
                "major_name": "人工智能",
                "demand_count_national": "100000",
                "salary_reference_national": "11825",
                "market_demand_signal_level": "high",
                "market_salary_signal_level": "high",
                "market_activity_signal_level": "high",
                "job_posting_sample_count": "5",
            }
        ],
        [
            "market_profile_id",
            "major_code",
            "major_name",
            "demand_count_national",
            "salary_reference_national",
            "market_demand_signal_level",
            "market_salary_signal_level",
            "market_activity_signal_level",
            "job_posting_sample_count",
        ],
    )
    write_csv(
        civil,
        [
            {
                "civil_service_major_id": "civil1",
                "major_code": "080717T",
                "major_name": "人工智能",
                "opportunity_level": "high",
                "role_match_count": "10",
                "plan_num_sum": "15",
            }
        ],
        [
            "civil_service_major_id",
            "major_code",
            "major_name",
            "opportunity_level",
            "role_match_count",
            "plan_num_sum",
        ],
    )
    write_csv(
        transfer,
        [
            {
                "transfer_policy_major_id": "transfer1",
                "major_code": "080717T",
                "major_name": "人工智能",
                "mentioned_in_school_count": "8",
                "high_difficulty_school_count": "2",
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

    result = build_new_quality_major_profiles(
        input_summary_csv=source_summary,
        input_detail_csv=source_detail,
        input_policy_sources_csv=policy_sources,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        ai_replacement_csv=ai,
        market_profiles_csv=market,
        civil_service_major_csv=civil,
        transfer_policy_major_csv=transfer,
        output_profiles_csv=profiles,
        output_tier_samples_csv=tiers,
        output_policy_sources_csv=policy_out,
        output_summary_csv=summary,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    profile_rows = read_rows(profiles)
    tier_rows = read_rows(tiers)
    policy_rows = read_rows(policy_out)
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))

    assert result["profile_row_count"] == 1
    assert result["tier_sample_row_count"] == 1
    assert result["policy_source_row_count"] == 1
    assert profile_rows[0]["support_category"] == "core"
    assert profile_rows[0]["direction_count"] == "2"
    assert profile_rows[0]["has_employment_yellow_warning"] == "true"
    assert profile_rows[0]["has_official_policy_warning"] == "true"
    assert profile_rows[0]["ai_replacement_score"] == "58"
    assert profile_rows[0]["market_demand_signal_level"] == "high"
    assert profile_rows[0]["has_civil_service_match"] == "true"
    assert profile_rows[0]["has_transfer_policy_mention"] == "true"
    assert profile_rows[0]["opportunity_risk_balance"] == "policy_supported_with_risk_flags"
    assert tier_rows[0]["support_category"] == "core"
    assert policy_rows[0]["source_level"] == "B"
    assert manifest_data["support_category_counts"]["core"] == 1
