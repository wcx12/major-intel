import csv
from pathlib import Path

from scripts.ingestion.build_graduate_official_source_coverage import (
    build_graduate_official_source_coverage,
)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_graduate_official_source_coverage_outputs_metadata(tmp_path):
    raw_file = tmp_path / "source.pdf"
    raw_file.write_bytes(b"pdf")
    output_dir = tmp_path / "out"

    school_coverage = tmp_path / "coverage.csv"
    write_csv(
        school_coverage,
        [
            {
                "school_id": "1001",
                "school_name": "测试大学",
                "province": "测试省",
                "official_url": "https://example.edu",
                "has_official_recommendation_records": "True",
                "official_recommendation_record_count": "10",
                "coverage_note": "matched",
            }
        ],
        [
            "school_id",
            "school_name",
            "province",
            "official_url",
            "has_official_recommendation_records",
            "official_recommendation_record_count",
            "coverage_note",
        ],
    )
    attempts = tmp_path / "attempts.csv"
    write_csv(
        attempts,
        [
            {
                "school_name": "测试大学",
                "data_track": "official_recommendation_admission",
                "source_title": "测试名单",
                "source_url": "https://example.edu/a",
                "local_artifact": str(raw_file),
                "live_status": "HTTP 200",
                "content_type": "application/pdf",
                "decision": "ingested",
                "blocker_type": "official_pdf_access_restored",
                "notes": "ok",
                "last_checked_date": "2026-06-14",
            }
        ],
        [
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
        ],
    )
    school_year = tmp_path / "school_year.csv"
    write_csv(
        school_year,
        [
            {
                "school_name": "测试大学",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "record_count": "10",
                "unique_person_count": "10",
                "needs_review_count": "1",
                "with_undergraduate_school_count": "2",
                "with_admission_major_count": "9",
                "source_document_count": "1",
            }
        ],
        [
            "school_name",
            "year",
            "document_type",
            "route",
            "record_count",
            "unique_person_count",
            "needs_review_count",
            "with_undergraduate_school_count",
            "with_admission_major_count",
            "source_document_count",
        ],
    )
    employment_sources = tmp_path / "employment_sources.csv"
    write_csv(
        employment_sources,
        [
            {
                "school_name": "测试大学",
                "data_track": "official_employment_or_teaching_quality",
                "report_year_or_cohort": "2024",
                "source_title": "就业报告",
                "source_url": "https://example.edu/report",
                "local_artifact": str(raw_file),
                "fetch_status": "200_downloaded",
                "content_type": "application/pdf",
                "extraction_status": "metrics_extracted",
                "notes": "ok",
            }
        ],
        [
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
        ],
    )
    employment_metrics = tmp_path / "employment_metrics.csv"
    write_csv(
        employment_metrics,
        [
            {
                "school_name": "测试大学",
                "report_year_or_cohort": "2024",
                "metric_name": "overall_employment_rate",
                "metric_value": "95",
                "metric_unit": "percent",
                "scope": "本科",
                "source_url": "https://example.edu/report",
                "evidence_note": "report",
                "extraction_quality": "high",
            }
        ],
        [
            "school_name",
            "report_year_or_cohort",
            "metric_name",
            "metric_value",
            "metric_unit",
            "scope",
            "source_url",
            "evidence_note",
            "extraction_quality",
        ],
    )

    manifest = build_graduate_official_source_coverage(
        output_dir=output_dir,
        school_coverage_path=school_coverage,
        clean_source_attempts_path=attempts,
        school_year_summary_path=school_year,
        remaining_attempts_path=attempts,
        employment_sources_path=employment_sources,
        employment_metrics_path=employment_metrics,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["school_coverage"] == 1
    assert manifest["row_counts"]["local_artifact_inventory"] == 2
    assert (output_dir / "graduate_official_source_school_coverage_2026.csv").exists()
    artifact_rows = list(
        csv.DictReader(
            (output_dir / "graduate_official_local_artifact_inventory_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    assert artifact_rows[0]["artifact_exists"] == "true"
    assert artifact_rows[0]["included_raw_file_in_package"] == "false"
