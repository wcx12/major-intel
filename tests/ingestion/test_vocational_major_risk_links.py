import csv
import json

from scripts.ingestion.build_vocational_major_risk_links import build_vocational_major_risk_links


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_build_vocational_major_risk_links_marks_duplicates_and_links(tmp_path):
    vocational = tmp_path / "vocational.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    annotated = tmp_path / "annotated.csv"
    summary = tmp_path / "summary.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    write_csv(
        vocational,
        [
            {
                "record_id": "vocational_major:abc",
                "year": "2026",
                "province_name": "北京市",
                "major_code": "510201",
                "major_name": "计算机应用技术",
                "school_code": "10001",
                "school_name": "样例职业学院",
                "school_system": "3",
                "remark": "",
                "source_level": "A",
                "source_url": "https://example.test/1",
                "captured_at": "2026-06-12T00:00:00+08:00",
            },
            {
                "record_id": "vocational_major:abc",
                "year": "2026",
                "province_name": "北京市",
                "major_code": "510201",
                "major_name": "计算机应用技术",
                "school_code": "10001",
                "school_name": "样例职业学院",
                "school_system": "3",
                "remark": "",
                "source_level": "A",
                "source_url": "https://example.test/1",
                "captured_at": "2026-06-12T00:00:00+08:00",
            },
        ],
        [
            "record_id",
            "year",
            "province_name",
            "major_code",
            "major_name",
            "school_code",
            "school_name",
            "school_system",
            "remark",
            "source_level",
            "source_url",
            "captured_at",
        ],
    )
    write_csv(
        employment,
        [
            {
                "record_id": "risk1",
                "report_year": "2026",
                "education_level": "高职高专",
                "risk_level": "red",
                "reported_major_name": "计算机应用技术",
                "standard_major_name": "计算机应用技术",
                "major_code": "510201",
            }
        ],
        ["record_id", "report_year", "education_level", "risk_level", "reported_major_name", "standard_major_name", "major_code"],
    )
    write_csv(
        policy,
        [
            {
                "warning_id": "policy1",
                "policy_year": "2026",
                "education_level": "高职高专",
                "record_type": "major_stop_enrollment",
                "reported_major_name": "计算机应用技术",
                "standard_major_name": "计算机应用技术",
                "major_code": "510201",
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

    result = build_vocational_major_risk_links(
        vocational_records_csv=vocational,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        output_annotated_csv=annotated,
        output_summary_csv=summary,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    assert result["record_count"] == 2
    assert result["duplicate_group_count"] == 1
    assert result["duplicate_excess_row_count"] == 1
    rows = list(csv.DictReader(annotated.open(encoding="utf-8-sig", newline="")))
    assert [row["record_id"] for row in rows] == ["vocational_major:abc:001", "vocational_major:abc:002"]
    assert rows[0]["has_employment_red_warning"] == "true"
    assert rows[0]["has_official_policy_warning"] == "true"
    summary_rows = list(csv.DictReader(summary.open(encoding="utf-8-sig", newline="")))
    assert summary_rows[0]["employment_warning_record_ids"] == "risk1"
    assert summary_rows[0]["official_policy_warning_ids"] == "policy1"
    assert json.loads(manifest.read_text(encoding="utf-8"))["annotated_duplicate_record_id_count"] == 0
