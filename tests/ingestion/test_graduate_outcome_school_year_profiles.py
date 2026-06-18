import csv
import json

from scripts.ingestion.build_graduate_outcome_school_year_profiles import (
    build_graduate_outcome_school_year_profiles,
)


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


PUBLIC_FIELDS = [
    "source_dataset",
    "public_record_id",
    "school_name",
    "year",
    "document_type",
    "route",
    "undergraduate_school",
    "undergraduate_major",
    "major",
    "admission_major",
    "source_url",
    "needs_review",
    "quality_score",
]

METRIC_FIELDS = [
    "school_name",
    "report_year_or_cohort",
    "metric_name",
    "metric_value",
    "metric_unit",
    "scope",
    "source_url",
    "evidence_note",
    "extraction_quality",
]

SOURCE_FIELDS = [
    "school_name",
    "data_track",
    "report_year_or_cohort",
    "source_title",
    "source_url",
    "local_artifact",
    "fetch_status",
    "content_type",
    "extraction_status",
    "notes",
]

COVERAGE_FIELDS = [
    "school_id",
    "school_name",
    "province",
    "official_url",
    "has_official_recommendation_records",
    "official_recommendation_record_count",
    "coverage_note",
]

ATTEMPT_FIELDS = [
    "school_name",
    "data_track",
    "source_title",
    "source_url",
    "local_artifact",
    "live_status",
    "content_type",
    "decision",
    "blocker_type",
    "notes",
    "last_checked_date",
]


def test_build_school_year_profiles_combines_public_rows_metrics_and_coverage(tmp_path):
    public_records = tmp_path / "public.csv"
    metrics = tmp_path / "metrics.csv"
    report_sources = tmp_path / "sources.csv"
    coverage = tmp_path / "coverage.csv"
    attempts = tmp_path / "attempts.csv"
    profiles = tmp_path / "profiles.csv"
    summary = tmp_path / "summary.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    write_csv(
        public_records,
        [
            {
                "source_dataset": "official_site_recommendation",
                "public_record_id": "r1",
                "school_name": "Target University",
                "year": "2024",
                "document_type": "recommendation_exemption_list",
                "route": "recommendation_exemption",
                "undergraduate_school": "Source College",
                "undergraduate_major": "Law",
                "major": "",
                "admission_major": "Civil Law",
                "source_url": "https://example.test/list",
                "needs_review": "false",
                "quality_score": "90",
            },
            {
                "source_dataset": "chsi_yanzhao",
                "public_record_id": "r2",
                "school_name": "Target University",
                "year": "2024",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "undergraduate_school": "",
                "undergraduate_major": "",
                "major": "",
                "admission_major": "Civil Law",
                "source_url": "https://example.test/chsi",
                "needs_review": "true",
                "quality_score": "55",
            },
        ],
        PUBLIC_FIELDS,
    )
    write_csv(
        metrics,
        [
            {
                "school_name": "Target University",
                "report_year_or_cohort": "2023-2024",
                "metric_name": "overall_undergraduate_employment_rate",
                "metric_value": "91.5",
                "metric_unit": "percent",
                "scope": "undergraduate",
                "source_url": "https://example.test/report.pdf",
                "evidence_note": "official rate",
                "extraction_quality": "high",
            },
            {
                "school_name": "Target University",
                "report_year_or_cohort": "2023-2024",
                "metric_name": "undergraduate_further_study_rate",
                "metric_value": "42.20",
                "metric_unit": "percent",
                "scope": "undergraduate",
                "source_url": "https://example.test/report.pdf",
                "evidence_note": "official rate",
                "extraction_quality": "high",
            },
        ],
        METRIC_FIELDS,
    )
    write_csv(
        report_sources,
        [
            {
                "school_name": "Target University",
                "data_track": "official_employment_or_teaching_quality",
                "report_year_or_cohort": "2023-2024",
                "source_title": "Target University Teaching Quality Report",
                "source_url": "https://example.test/report.pdf",
                "local_artifact": "tmp/report.pdf",
                "fetch_status": "200_downloaded",
                "content_type": "application/pdf",
                "extraction_status": "metrics_extracted",
                "notes": "",
            }
        ],
        SOURCE_FIELDS,
    )
    write_csv(
        coverage,
        [
            {
                "school_id": "1001",
                "school_name": "Target University",
                "province": "Test",
                "official_url": "https://target.example",
                "has_official_recommendation_records": "True",
                "official_recommendation_record_count": "2",
                "coverage_note": "matched_by_school_name",
            },
            {
                "school_id": "1002",
                "school_name": "Coverage Only University",
                "province": "Test",
                "official_url": "https://coverage.example",
                "has_official_recommendation_records": "False",
                "official_recommendation_record_count": "0",
                "coverage_note": "not_found",
            },
        ],
        COVERAGE_FIELDS,
    )
    write_csv(
        attempts,
        [
            {
                "school_name": "Target University",
                "data_track": "official_recommendation_admission",
                "source_title": "candidate",
                "source_url": "https://target.example/candidate",
                "local_artifact": "",
                "live_status": "HTTP 200",
                "content_type": "text/html",
                "decision": "ingested",
                "blocker_type": "",
                "notes": "",
                "last_checked_date": "2026-06-04",
            },
            {
                "school_name": "Coverage Only University",
                "data_track": "official_recommendation_admission",
                "source_title": "blocked",
                "source_url": "https://coverage.example/blocked",
                "local_artifact": "",
                "live_status": "HTTP 412",
                "content_type": "text/html",
                "decision": "no_ingest",
                "blocker_type": "js_challenge",
                "notes": "",
                "last_checked_date": "2026-06-04",
            },
        ],
        ATTEMPT_FIELDS,
    )

    result = build_graduate_outcome_school_year_profiles(
        public_records_csv=public_records,
        official_metrics_csv=metrics,
        official_report_sources_csv=report_sources,
        recommendation_coverage_csv=coverage,
        source_attempts_csv=attempts,
        output_profiles_csv=profiles,
        output_school_summary_csv=summary,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    profile_rows = read_rows(profiles)
    by_school_year = {(row["school_name"], row["year"]): row for row in profile_rows}
    target = by_school_year[("Target University", "2024")]
    source = by_school_year[("Source College", "2024")]
    assert result["public_record_input_count"] == 2
    assert result["school_year_profile_count"] == 2
    assert target["as_destination_record_count"] == "2"
    assert target["unique_public_record_count"] == "2"
    assert target["needs_review_count"] == "1"
    assert target["low_quality_record_count"] == "1"
    assert target["official_metric_count"] == "2"
    assert target["official_report_source_count"] == "1"
    assert target["official_overall_undergraduate_employment_rate"] == "91.5"
    assert target["official_undergraduate_further_study_rate"] == "42.2"
    assert target["coverage_school_id"] == "1001"
    assert target["has_official_recommendation_records"] == "true"
    assert target["ingested_attempt_count"] == "1"
    assert source["as_undergraduate_source_record_count"] == "1"
    assert source["destination_school_count"] == "1"

    summary_rows = read_rows(summary)
    by_school = {row["school_name"]: row for row in summary_rows}
    assert by_school["Coverage Only University"]["year_profile_count"] == "0"
    assert by_school["Coverage Only University"]["blocked_attempt_count"] == "1"
    assert by_school["Coverage Only University"]["source_attempt_blocker_types"] == "js_challenge"
    assert json.loads(manifest.read_text(encoding="utf-8"))["school_summary_row_count"] == 3
