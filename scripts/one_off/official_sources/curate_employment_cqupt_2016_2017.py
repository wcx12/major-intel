from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EMPLOYMENT_DIR = ROOT / "data/processed/graduate_outcomes_official_employment_reports_remaining15"
REPORT_SOURCES_CSV = EMPLOYMENT_DIR / "report_sources.csv"
REPORT_METRICS_CSV = EMPLOYMENT_DIR / "report_metrics_clean.csv"

SOURCE_URL = (
    "https://www.cqupt.edu.cn/__local/6/77/35/"
    "030BC5BB3EB8D927D67ABDA31ED_023C1745_1C0152.pdf?e=.pdf"
)
LOCAL_ARTIFACT = (
    "data/raw/official_employment_report_20260603_cqupt_2016_2017/"
    "www.cqupt.edu.cn/2016-2017_teaching_quality.pdf"
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
        "school_name": "重庆邮电大学",
        "data_track": "official_employment_or_teaching_quality",
        "report_year_or_cohort": "2016-2017",
        "source_title": "重庆邮电大学2016-2017学年本科教学质量报告",
        "source_url": SOURCE_URL,
        "local_artifact": LOCAL_ARTIFACT,
        "fetch_status": "200_downloaded",
        "content_type": "application/pdf",
        "extraction_status": "metrics_extracted",
        "notes": "官方本科教学质量报告PDF直链可达；支撑数据目录含毕业率、学位授予率、初次就业率和用人单位满意度",
    }


def _metric(metric_name: str, metric_value: str, scope: str, evidence_note: str) -> dict[str, str]:
    return {
        "school_name": "重庆邮电大学",
        "report_year_or_cohort": "2016-2017",
        "metric_name": metric_name,
        "metric_value": metric_value,
        "metric_unit": "percent",
        "scope": scope,
        "source_url": SOURCE_URL,
        "evidence_note": evidence_note,
        "extraction_quality": "high",
    }


def build_metric_rows() -> list[dict[str, str]]:
    return [
        _metric(
            "undergraduate_graduation_rate",
            "95.93",
            "2017届应届本科生",
            "支撑数据目录第19项披露应届本科生毕业率",
        ),
        _metric(
            "undergraduate_degree_award_rate",
            "99.16",
            "2017届应届本科生",
            "支撑数据目录第20项披露应届本科生学位授予率",
        ),
        _metric(
            "initial_employment_rate",
            "94.64",
            "2017届毕业生初次就业率",
            "表5.5和支撑数据目录第21项披露2017年初次就业率",
        ),
        _metric(
            "initial_employment_rate_2016",
            "92.18",
            "2016届毕业生初次就业率",
            "表5.5近三年毕业生初次、年终就业率统计表",
        ),
        _metric(
            "year_end_employment_rate_2016",
            "93.97",
            "2016届毕业生年终就业率",
            "表5.5近三年毕业生初次、年终就业率统计表",
        ),
        _metric(
            "employer_satisfaction_rate",
            "92.00",
            "用人单位对毕业生满意度",
            "支撑数据目录第24项披露第三方机构调查的用人单位满意度",
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
