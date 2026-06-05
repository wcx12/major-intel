from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EMPLOYMENT_DIR = ROOT / "data/processed/graduate_outcomes_official_employment_reports_remaining15"
REPORT_SOURCES_CSV = EMPLOYMENT_DIR / "report_sources.csv"
REPORT_METRICS_CSV = EMPLOYMENT_DIR / "report_metrics_clean.csv"

SCHOOL_NAME = "\u4e91\u5357\u6c11\u65cf\u5927\u5b66"
REPORT_YEAR_OR_COHORT = "2023-2024"
SOURCE_URL = "https://www.ymu.edu.cn/__local/A/A1/AA/90F5868660743B27277806117B4_73FFDA0B_22C94C.pdf"
SOURCE_TITLE = "\u4e91\u5357\u6c11\u65cf\u5927\u5b662023-2024\u5b66\u5e74\u672c\u79d1\u6559\u5b66\u8d28\u91cf\u62a5\u544a"

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


def build_source_row() -> dict[str, str]:
    return {
        "school_name": SCHOOL_NAME,
        "data_track": "official_employment_or_teaching_quality",
        "report_year_or_cohort": REPORT_YEAR_OR_COHORT,
        "source_title": SOURCE_TITLE,
        "source_url": SOURCE_URL,
        "local_artifact": "",
        "fetch_status": "official_pdf_web_visible",
        "content_type": "application/pdf",
        "extraction_status": "metrics_extracted",
        "notes": (
            "official_pdf_web_visible; local_curl_returned_521_waf"
            "(tmp/employment_ymu_alt_2023_2024_teaching_quality.pdf); "
            "official ymu.edu.cn PDF text layer visible via web retrieval; "
            "local live fetch still returns WAF/JS clearance HTML, so no WAF bypass was attempted"
        ),
    }


def _metric(
    metric_name: str,
    metric_value: str,
    metric_unit: str,
    scope: str,
    evidence_note: str,
) -> dict[str, str]:
    return {
        "school_name": SCHOOL_NAME,
        "report_year_or_cohort": REPORT_YEAR_OR_COHORT,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "metric_unit": metric_unit,
        "scope": scope,
        "source_url": SOURCE_URL,
        "evidence_note": evidence_note,
        "extraction_quality": "high",
    }


def build_metric_rows() -> list[dict[str, str]]:
    graduates = "2024 undergraduate graduates"
    further_study = "2024 undergraduate further-study outcomes"
    initial = "2024 undergraduate initial employment outcomes"
    channels = "2024 undergraduate initial employment channel table"
    employer = "2023-2024 employer feedback section"

    return [
        _metric("total_undergraduate_graduates", "8775", "people", graduates, "Report states 8,775 undergraduate graduates."),
        _metric("undergraduate_graduation_rate", "100.00", "percent", graduates, "Report states undergraduate graduation rate 100.00%."),
        _metric("undergraduate_degree_award_count", "8227", "people", graduates, "Report states 8,227 graduates received bachelor's degrees."),
        _metric("undergraduate_degree_award_rate", "93.75", "percent", graduates, "Report states degree-award rate 93.75%."),
        _metric("undergraduate_further_study_count", "784", "people", further_study, "Report states 784 graduates pursued further study."),
        _metric("domestic_same_school_further_study_count", "459", "people", further_study, "Further-study paragraph states 459 entered Yunnan Minzu University."),
        _metric("domestic_other_school_further_study_count", "155", "people", further_study, "Further-study paragraph states 155 entered other universities."),
        _metric("recommendation_exemption_further_study_count", "115", "people", further_study, "Further-study paragraph states 115 were admitted through recommendation exemption."),
        _metric("overseas_study_count", "38", "people", further_study, "Further-study paragraph states 38 studied abroad."),
        _metric("second_bachelor_degree_count", "17", "people", further_study, "Further-study paragraph states 17 pursued a second bachelor's degree."),
        _metric("undergraduate_further_study_rate", "8.93", "percent", further_study, "Report states further-study share 8.93% of 2024 undergraduate graduates."),
        _metric("initial_undergraduate_employment_rate", "71.16", "percent", initial, "Report states initial undergraduate employment rate 71.16%."),
        _metric("initial_employment_count", "6243", "people", initial, "Report states initial employment count 6,243."),
        _metric("local_region_employment_count", "5184", "people", initial, "Report states 5,184 graduates were employed within Yunnan."),
        _metric("nonlocal_region_employment_count", "1059", "people", initial, "Report states 1,059 graduates were employed outside Yunnan."),
        _metric("signing_agreement_count", "3609", "people", channels, "Employment-channel table lists 3,609 agreement signings."),
        _metric("labor_contract_count", "395", "people", channels, "Employment-channel table lists 395 labor contracts."),
        _metric("other_hiring_form_count", "1223", "people", channels, "Employment-channel table lists 1,223 other hiring forms."),
        _metric("conscription_count", "69", "people", channels, "Employment-channel table lists 69 conscription cases."),
        _metric("freelance_count", "108", "people", channels, "Employment-channel table lists 108 freelance cases."),
        _metric("startup_count", "55", "people", channels, "Employment-channel table lists 55 startups."),
        _metric("enterprise_employment_share", "57.34", "percent", initial, "Report states enterprise employment share 57.34%."),
        _metric("employer_very_satisfied_rate", "46.58", "percent", employer, "Employer feedback section states very-satisfied share 46.58%."),
        _metric("employer_overall_satisfaction_rate", "78.26", "percent", employer, "Employer feedback section states overall satisfaction 78.26%."),
    ]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def upsert_rows(
    path: Path,
    fieldnames: list[str],
    new_rows: list[dict[str, str]],
    key_fields: tuple[str, ...],
) -> int:
    existing_rows = read_csv(path)
    replacement_keys = {tuple(row.get(field, "") for field in key_fields) for row in new_rows}
    kept_rows = [
        row
        for row in existing_rows
        if tuple(row.get(field, "") for field in key_fields) not in replacement_keys
    ]
    write_csv(path, fieldnames, [*kept_rows, *new_rows])
    return len(new_rows)


def main() -> None:
    source_count = upsert_rows(
        REPORT_SOURCES_CSV,
        SOURCE_FIELDS,
        [build_source_row()],
        ("school_name", "report_year_or_cohort", "source_url"),
    )
    metric_count = upsert_rows(
        REPORT_METRICS_CSV,
        METRIC_FIELDS,
        build_metric_rows(),
        ("school_name", "report_year_or_cohort", "source_url", "metric_name"),
    )
    print({"source_rows_upserted": source_count, "metric_rows_upserted": metric_count})


if __name__ == "__main__":
    main()
