from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EMPLOYMENT_DIR = ROOT / "data/processed/graduate_outcomes_official_employment_reports_remaining15"
REPORT_SOURCES_CSV = EMPLOYMENT_DIR / "report_sources.csv"
REPORT_METRICS_CSV = EMPLOYMENT_DIR / "report_metrics_clean.csv"

SOURCE_URL = "https://xxgk.cupl.edu.cn/info/1064/2494.htm"
SCHOOL_NAME = "\u4e2d\u56fd\u653f\u6cd5\u5927\u5b66"
REPORT_YEAR_OR_COHORT = "2018\u5c4a"
SOURCE_TITLE = (
    "\u4e2d\u56fd\u653f\u6cd5\u5927\u5b662018\u5c4a\u6bd5\u4e1a\u751f\u7684"
    "\u89c4\u6a21\u3001\u7ed3\u6784\u3001\u5c31\u4e1a\u7387\u3001\u5c31\u4e1a\u6d41\u5411"
)

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
        "fetch_status": "official_page_web_visible",
        "content_type": "text/html",
        "extraction_status": "metrics_extracted",
        "notes": (
            "official_page_web_visible; local_curl_dynamic_challenge"
            "(tmp/employment_cupl_2018_outcomes_2494_ua.html); "
            "\u5b98\u65b9\u4fe1\u606f\u516c\u5f00\u9875\u6b63\u6587\u53ef\u89c1"
            "\uff0c\u672c\u5730curl\u4ec5\u8fd4\u56dedynamic_challenge\u58f3"
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
    total_scope = "2018\u5c4a\u5168\u6821\u6bd5\u4e1a\u751f"
    undergrad_scope = "2018\u5c4a\u672c\u79d1\u6bd5\u4e1a\u751f"
    graduate_scope = "2018\u5c4a\u7814\u7a76\u751f\u6bd5\u4e1a\u751f"
    return [
        _metric(
            "graduate_count",
            "4063",
            "people",
            total_scope,
            "\u6b63\u6587\u62ab\u97322018\u5c4a\u6bd5\u4e1a\u751f\u51714063\u4eba",
        ),
        _metric(
            "undergraduate_count",
            "2092",
            "people",
            undergrad_scope,
            "\u6b63\u6587\u62ab\u9732\u672c\u79d1\u6bd5\u4e1a\u751f2092\u4eba",
        ),
        _metric(
            "graduate_student_count",
            "1971",
            "people",
            graduate_scope,
            "\u6b63\u6587\u62ab\u9732\u7814\u7a76\u751f\u6bd5\u4e1a\u751f1971\u4eba",
        ),
        _metric(
            "employment_implementation_count",
            "3989",
            "people",
            total_scope,
            "\u6b63\u6587\u62ab\u9732\u843d\u5b9e\u5c31\u4e1a\u5355\u4f4d\u4eba\u65703989\u4eba",
        ),
        _metric(
            "overall_employment_rate",
            "98.18",
            "percent",
            total_scope,
            "\u6b63\u6587\u62ab\u9732\u603b\u4f53\u5c31\u4e1a\u738798.18%",
        ),
        _metric(
            "undergraduate_employment_rate",
            "98.80",
            "percent",
            undergrad_scope,
            "\u6b63\u6587\u62ab\u9732\u672c\u79d1\u751f\u5c31\u4e1a\u738798.80%",
        ),
        _metric(
            "master_employment_rate",
            "97.54",
            "percent",
            "2018\u5c4a\u7855\u58eb\u6bd5\u4e1a\u751f",
            "\u6b63\u6587\u62ab\u9732\u7855\u58eb\u7814\u7a76\u751f\u5c31\u4e1a\u738797.54%",
        ),
        _metric(
            "doctoral_employment_rate",
            "97.24",
            "percent",
            "2018\u5c4a\u535a\u58eb\u6bd5\u4e1a\u751f",
            "\u6b63\u6587\u62ab\u9732\u535a\u58eb\u7814\u7a76\u751f\u5c31\u4e1a\u738797.24%",
        ),
        _metric(
            "further_study_count",
            "1441",
            "people",
            total_scope,
            "\u6b63\u6587\u62ab\u9732\u7ee7\u7eed\u6df1\u9020\u4eba\u65701441\u4eba",
        ),
        _metric(
            "further_study_rate",
            "35.47",
            "percent",
            total_scope,
            "\u6b63\u6587\u62ab\u9732\u7ee7\u7eed\u6df1\u9020\u6bd4\u4f8b35.47%",
        ),
        _metric(
            "undergraduate_further_study_count",
            "1313",
            "people",
            undergrad_scope,
            "\u6b63\u6587\u62ab\u9732\u672c\u79d1\u7ee7\u7eed\u6df1\u9020\u4eba\u65701313\u4eba",
        ),
        _metric(
            "undergraduate_further_study_rate",
            "62.76",
            "percent",
            undergrad_scope,
            "\u6b63\u6587\u62ab\u9732\u672c\u79d1\u7ee7\u7eed\u6df1\u9020\u6bd4\u4f8b62.76%",
        ),
        _metric(
            "signing_count",
            "3021",
            "people",
            total_scope,
            "\u6b63\u6587\u62ab\u9732\u5168\u6821\u7b7e\u7ea6\u5c31\u4e1a3021\u4eba",
        ),
        _metric(
            "signing_rate",
            "74.35",
            "percent",
            total_scope,
            "\u6b63\u6587\u62ab\u9732\u5168\u6821\u7b7e\u7ea6\u738774.35%",
        ),
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
