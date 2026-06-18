import csv
import json

from scripts.ingestion.build_graduate_outcome_major_flows import (
    build_graduate_outcome_major_flows,
)


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


def test_build_graduate_outcome_major_flows_links_risk_sources(tmp_path):
    public_records = tmp_path / "public.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    ai = tmp_path / "ai.csv"
    flows = tmp_path / "flows.csv"
    role_summary = tmp_path / "role_summary.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    write_csv(
        public_records,
        [
            {
                "source_dataset": "official_site_recommendation",
                "public_record_id": "r1",
                "school_name": "Dest A",
                "year": "2026",
                "document_type": "recommendation_exemption_list",
                "route": "recommendation_exemption",
                "undergraduate_school": "Source A",
                "undergraduate_major": "Data Science",
                "admission_major": "Computer Science",
                "source_url": "https://example.test/a",
                "needs_review": "false",
                "quality_score": "90",
            },
            {
                "source_dataset": "official_site_recommendation",
                "public_record_id": "r2",
                "school_name": "Dest B",
                "year": "2025",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "undergraduate_school": "Source B",
                "undergraduate_major": "Data Science",
                "admission_major": "Computer Science",
                "source_url": "https://example.test/b",
                "needs_review": "true",
                "quality_score": "55",
            },
        ],
        [
            "source_dataset",
            "public_record_id",
            "school_name",
            "year",
            "document_type",
            "route",
            "undergraduate_school",
            "undergraduate_major",
            "admission_major",
            "source_url",
            "needs_review",
            "quality_score",
        ],
    )
    write_csv(
        employment,
        [
            {
                "record_id": "risk1",
                "report_year": "2025",
                "risk_level": "yellow",
                "reported_major_name": "Data Science",
                "standard_major_name": "Data Science",
            }
        ],
        ["record_id", "report_year", "risk_level", "reported_major_name", "standard_major_name"],
    )
    write_csv(
        policy,
        [
            {
                "warning_id": "policy1",
                "policy_year": "2024",
                "record_type": "major_cancel",
                "reported_major_name": "Data Science",
                "standard_major_name": "Data Science",
            }
        ],
        ["warning_id", "policy_year", "record_type", "reported_major_name", "standard_major_name"],
    )
    write_csv(
        ai,
        [
            {
                "major_name": "Data Science",
                "rank": "3",
                "ai_replacement_score": "65.5",
                "ai_replacement_level": "medium",
                "confidence_score": "80",
                "candidate_count": "12",
            }
        ],
        [
            "major_name",
            "rank",
            "ai_replacement_score",
            "ai_replacement_level",
            "confidence_score",
            "candidate_count",
        ],
    )

    result = build_graduate_outcome_major_flows(
        public_records_csv=public_records,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        ai_replacement_csv=ai,
        output_flows_csv=flows,
        output_role_summary_csv=role_summary,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    rows = read_rows(flows)
    by_role = {row["major_role"]: row for row in rows if row["major_name"] == "Data Science"}
    assert result["public_record_count"] == 2
    assert result["major_flow_count"] == 2
    assert by_role["undergraduate_major"]["record_count"] == "2"
    assert by_role["undergraduate_major"]["needs_review_count"] == "1"
    assert by_role["undergraduate_major"]["low_quality_record_count"] == "1"
    assert by_role["undergraduate_major"]["has_employment_yellow_warning"] == "true"
    assert by_role["undergraduate_major"]["has_official_policy_warning"] == "true"
    assert by_role["undergraduate_major"]["ai_replacement_score"] == "65.5"
    assert json.loads(manifest.read_text(encoding="utf-8"))["role_summary_row_count"] == 2


def test_build_graduate_outcome_major_flows_normalizes_leading_codes(tmp_path):
    public_records = tmp_path / "public.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    ai = tmp_path / "ai.csv"
    flows = tmp_path / "flows.csv"
    role_summary = tmp_path / "role_summary.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    write_csv(
        public_records,
        [
            {
                "source_dataset": "official_site_recommendation",
                "public_record_id": "r1",
                "school_name": "Dest A",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "undergraduate_school": "",
                "undergraduate_major": "",
                "admission_major": "(010100)Philosophy",
                "source_url": "https://example.test/a",
                "needs_review": "false",
                "quality_score": "90",
            },
            {
                "source_dataset": "official_site_recommendation",
                "public_record_id": "r2",
                "school_name": "Dest B",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "undergraduate_school": "",
                "undergraduate_major": "",
                "admission_major": "010100 Philosophy",
                "source_url": "https://example.test/b",
                "needs_review": "false",
                "quality_score": "90",
            },
        ],
        [
            "source_dataset",
            "public_record_id",
            "school_name",
            "year",
            "document_type",
            "route",
            "undergraduate_school",
            "undergraduate_major",
            "admission_major",
            "source_url",
            "needs_review",
            "quality_score",
        ],
    )
    write_csv(
        employment,
        [
            {
                "record_id": "risk1",
                "report_year": "2025",
                "risk_level": "red",
                "reported_major_name": "Philosophy",
                "standard_major_name": "Philosophy",
            }
        ],
        ["record_id", "report_year", "risk_level", "reported_major_name", "standard_major_name"],
    )
    write_csv(policy, [], ["warning_id", "policy_year", "record_type", "reported_major_name", "standard_major_name"])
    write_csv(ai, [], ["major_name", "rank", "ai_replacement_score", "ai_replacement_level", "confidence_score", "candidate_count"])

    build_graduate_outcome_major_flows(
        public_records_csv=public_records,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        ai_replacement_csv=ai,
        output_flows_csv=flows,
        output_role_summary_csv=role_summary,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    rows = read_rows(flows)
    assert len(rows) == 1
    assert rows[0]["major_name"] == "Philosophy"
    assert rows[0]["normalized_major_name"] == "Philosophy"
    assert rows[0]["record_count"] == "2"
    assert rows[0]["has_employment_red_warning"] == "true"
