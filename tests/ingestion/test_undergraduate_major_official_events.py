import csv
import json

from scripts.ingestion.build_undergraduate_major_official_events import (
    build_undergraduate_major_official_events,
    parse_school_name,
    reject_reason_for,
)


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_parse_school_name_handles_space_and_pipe_formats():
    assert (
        parse_school_name(
            {
                "event_type": "filing_added",
                "major_code": "080910T",
                "major_name": "数据科学与大数据技术",
                "evidence_text": "8 北京交通大学 数据科学与大数据技术 080910T 工学 四年",
            },
            normalized_event_type="undergraduate_filing_or_approval_added",
        )
        == "北京交通大学"
    )
    assert (
        parse_school_name(
            {
                "major_code": "050204",
                "major_name": "法语",
                "evidence_text": "武汉大学珞珈学院 | 050204 | 法语 | 四年 | 文学",
            },
            normalized_event_type="undergraduate_filing_or_approval_added",
        )
        == "武汉大学珞珈学院"
    )
    assert (
        parse_school_name(
            {
                "major_code": "080301",
                "major_name": "学院测控技术与仪器",
                "evidence_text": "71 | 长春工业大学人文信息 | 学院测控技术与仪器 | 080301 | 工学 | 四年",
            },
            normalized_event_type="undergraduate_filing_or_approval_added",
            canonical_major_name="测控技术与仪器",
            normalized_major_name="测控技术与仪器",
        )
        == "长春工业大学人文信息学院"
    )


def test_reject_reason_accepts_tk_undergraduate_codes():
    assert reject_reason_for({"major_level": "本科", "major_code": "020110TK", "major_name": "低空经济与管理"}) == ""
    assert reject_reason_for({"major_level": "本科", "major_code": "", "major_name": "备注"}) == "invalid_or_missing_undergraduate_major_code"


def test_build_undergraduate_major_official_events_links_and_rejects(tmp_path):
    candidates = tmp_path / "candidates.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    events = tmp_path / "events.csv"
    summary = tmp_path / "summary.csv"
    rejected = tmp_path / "rejected.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    candidate_fields = [
        "candidate_id",
        "major_code",
        "major_name",
        "major_level",
        "discipline_category",
        "major_class",
        "degree",
        "study_years",
        "event_type",
        "event_year",
        "candidate_status",
        "source_title",
        "source_url",
        "attachment_url",
        "source_level",
        "evidence_text",
        "raw_path",
        "parsed_from",
        "captured_at",
        "warnings_json",
    ]
    write_csv(
        candidates,
        [
            {
                "candidate_id": "c1",
                "major_code": "080910T",
                "major_name": "数据科学与大数据技术",
                "major_level": "本科",
                "degree": "工学",
                "study_years": "四年",
                "event_type": "filing_added",
                "event_year": "2024",
                "candidate_status": "catalog_confirmed",
                "source_title": "教育部通知",
                "source_url": "https://example.test/page",
                "attachment_url": "https://example.test/file.pdf",
                "source_level": "A",
                "evidence_text": "8 北京交通大学 数据科学与大数据技术 080910T 工学 四年",
                "parsed_from": "pdf",
                "warnings_json": "[]",
            },
            {
                "candidate_id": "c2",
                "major_code": "",
                "major_name": "备注",
                "major_level": "本科",
                "event_type": "catalog_added",
                "event_year": "2012",
                "candidate_status": "catalog_candidate",
                "source_title": "教育部目录",
                "source_url": "https://example.test/catalog",
                "evidence_text": "备注",
                "warnings_json": "[]",
            },
        ],
        candidate_fields,
    )
    write_csv(
        employment,
        [
            {
                "record_id": "risk1",
                "report_year": "2025",
                "education_level": "本科",
                "risk_level": "red",
                "reported_major_name": "数据科学与大数据技术",
                "standard_major_name": "数据科学与大数据技术",
                "major_code": "080910T",
            }
        ],
        ["record_id", "report_year", "education_level", "risk_level", "reported_major_name", "standard_major_name", "major_code"],
    )
    write_csv(
        policy,
        [
            {
                "warning_id": "policy1",
                "policy_year": "2024",
                "education_level": "本科",
                "record_type": "major_cancel",
                "reported_major_name": "数据科学与大数据技术",
                "standard_major_name": "数据科学与大数据技术",
                "major_code": "080910T",
            }
        ],
        [
            "warning_id",
            "policy_year",
            "education_level",
            "record_type",
            "reported_major_name",
            "standard_major_name",
            "major_code",
        ],
    )

    result = build_undergraduate_major_official_events(
        candidates_csv=candidates,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        output_events_csv=events,
        output_summary_csv=summary,
        output_rejected_csv=rejected,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    assert result["accepted_event_count"] == 1
    assert result["rejected_candidate_count"] == 1
    event_rows = list(csv.DictReader(events.open(encoding="utf-8-sig", newline="")))
    assert event_rows[0]["school_name"] == "北京交通大学"
    assert event_rows[0]["has_employment_red_warning"] == "true"
    assert event_rows[0]["has_official_policy_warning"] == "true"
    rejected_rows = list(csv.DictReader(rejected.open(encoding="utf-8-sig", newline="")))
    assert rejected_rows[0]["reject_reason"] == "invalid_or_missing_undergraduate_major_code"
    assert json.loads(manifest.read_text(encoding="utf-8"))["unique_major_count"] == 1
