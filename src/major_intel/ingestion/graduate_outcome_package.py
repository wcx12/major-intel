from __future__ import annotations

import csv
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

from major_intel.crawlers import graduate_outcome_crawler as crawler

CHSI_CLEAN = ROOT / "data/processed/graduate_outcomes_chsi/master_records_clean.csv"
OFFICIAL_CLEAN = (
    ROOT / "data/processed/graduate_outcomes_official_site_recommendation_master/records_clean.csv"
)
EXTRA_OFFICIAL_CLEAN_FILES = [
    ROOT
    / "data/processed/official_site_recommendation_web_visible_cupl_2016_recommendation/"
    "records_clean_curated.csv",
    ROOT
    / "data/processed/official_site_recommendation_websearch_web_20260603_nufe_2026_doctor_supp_image/"
    "records_clean_curated.csv",
    ROOT
    / "data/processed/official_site_recommendation_web_visible_ymu_2025_recommendation/"
    "records_clean_curated.csv",
    ROOT
    / "data/processed/official_site_recommendation_web_visible_dlou_2024_adjustment_second_batch/"
    "records_clean_curated.csv",
    ROOT
    / "data/processed/official_recommendation_zcmu_2025_master_admission_current/"
    "records_clean_curated.csv",
    ROOT
    / "data/processed/official_recommendation_nwnu_jykxxy_2025_master_first_choice/"
    "records_clean_curated.csv",
    ROOT
    / "data/processed/official_recommendation_cmu_2026_doctor_minority_admission/"
    "records_clean_curated.csv",
    ROOT
    / "data/processed/official_recommendation_bift_2026_doctor_admission_first/"
    "records_clean_curated.csv",
]
OUTPUT_DIR = ROOT / "data/cleaned/graduate_outcomes"
EMPLOYMENT_REPORTS_DIR = (
    ROOT / "data/processed/graduate_outcomes_official_employment_reports_remaining15"
)
RECOMMENDATION_SOURCE_ATTEMPTS = (
    ROOT
    / "data/processed/graduate_outcomes_official_recommendation_remaining15/source_attempts.csv"
)
NON_FINAL_ROW_LEVEL_FILES = [
    ROOT / "data/processed/official_non_final_row_level_xza_2025_adjustment_score/records_clean.csv",
    ROOT / "data/processed/official_non_final_row_level_bift_2026_doctor_second_assessment/records_clean.csv",
    ROOT / "data/processed/official_non_final_row_level_bfa_2026_recommendation_candidate_numbers/records_clean.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: crawler._csv_value(row.get(field)) for field in fieldnames})


def with_source_dataset(rows: list[dict[str, str]], source_dataset: str) -> list[dict[str, str]]:
    return [{"source_dataset": source_dataset, **row} for row in rows]


def read_official_clean_rows() -> list[dict[str, str]]:
    rows = read_csv(OFFICIAL_CLEAN)
    for path in EXTRA_OFFICIAL_CLEAN_FILES:
        if path.exists():
            rows.extend(read_csv(path))
    return rows


def public_rows(clean_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows = []
    for row in clean_rows:
        public = {
            field: row.get(field, "")
            for field in crawler.PUBLIC_RECORD_CSV_FIELDS
            if field != "public_record_id"
        }
        public["source_dataset"] = row.get("source_dataset", "")
        public["public_record_id"] = crawler._public_record_id(row)
        rows.append(public)
    return rows


def build_summary_rows(clean_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clean_rows:
        grouped[
            (
                row.get("source_dataset", ""),
                row.get("school_name", ""),
                row.get("year", ""),
                row.get("document_type", ""),
                row.get("route", ""),
            )
        ].append(row)

    summary_rows = []
    for (source_dataset, school_name, year, document_type, route), rows in sorted(grouped.items()):
        unique_people = {
            row.get("student_id") or row.get("person_name") or row.get("record_id") or ""
            for row in rows
        }
        summary_rows.append(
            {
                "source_dataset": source_dataset,
                "school_name": school_name,
                "year": year,
                "document_type": document_type,
                "route": route,
                "record_count": len(rows),
                "unique_person_count": len(unique_people),
                "needs_review_count": sum(1 for row in rows if row.get("needs_review") == "true"),
                "with_undergraduate_school_count": sum(
                    1 for row in rows if row.get("undergraduate_school")
                ),
                "with_admission_major_count": sum(1 for row in rows if row.get("admission_major")),
                "source_document_count": len({row.get("source_url", "") for row in rows if row.get("source_url")}),
            }
        )
    return summary_rows


def build_undergraduate_source_outcome_rows(clean_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clean_rows:
        undergraduate_school = row.get("undergraduate_school", "").strip()
        if not undergraduate_school:
            continue
        grouped[
            (
                undergraduate_school,
                row.get("year", ""),
                row.get("source_dataset", ""),
                row.get("school_name", ""),
                row.get("document_type", ""),
                row.get("route", ""),
            )
        ].append(row)

    summary_rows = []
    for (
        undergraduate_school,
        year,
        source_dataset,
        destination_school,
        document_type,
        route,
    ), rows in sorted(grouped.items()):
        unique_people = {
            row.get("student_id") or row.get("person_name") or row.get("record_id") or ""
            for row in rows
        }
        summary_rows.append(
            {
                "undergraduate_school": undergraduate_school,
                "year": year,
                "source_dataset": source_dataset,
                "destination_school": destination_school,
                "document_type": document_type,
                "route": route,
                "record_count": len(rows),
                "unique_person_count": len(unique_people),
                "with_student_id_count": sum(1 for row in rows if row.get("student_id")),
                "with_admission_major_count": sum(1 for row in rows if row.get("admission_major")),
                "source_document_count": len({row.get("source_url", "") for row in rows if row.get("source_url")}),
            }
        )
    return summary_rows


def build_coverage_rows(coverage_base: list[dict[str, str]], official_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    counts: dict[str, int] = defaultdict(int)
    for row in official_rows:
        school_name = row.get("school_name", "")
        if school_name:
            counts[school_name] += 1

    rows = []
    for row in coverage_base:
        count = counts.get(row.get("school_name", ""), 0)
        updated = dict(row)
        updated["has_official_recommendation_records"] = "True" if count else "False"
        updated["official_recommendation_record_count"] = count
        updated["coverage_note"] = "matched_by_school_name" if count else "no_exact_school_name_match_yet"
        rows.append(updated)
    return rows


def publish_employment_report_tables() -> dict[str, int]:
    outputs = {
        "report_sources.csv": OUTPUT_DIR / "official_employment_report_sources.csv",
        "report_metrics_clean.csv": OUTPUT_DIR / "official_employment_report_metrics.csv",
    }
    counts: dict[str, int] = {}
    for source_name, target_path in outputs.items():
        source_path = EMPLOYMENT_REPORTS_DIR / source_name
        if not source_path.exists():
            counts[source_name] = 0
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_path)
        counts[source_name] = len(read_csv(target_path))
    return counts


def publish_recommendation_source_attempts() -> int:
    target_path = OUTPUT_DIR / "official_recommendation_source_attempts.csv"
    if not RECOMMENDATION_SOURCE_ATTEMPTS.exists():
        return 0
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RECOMMENDATION_SOURCE_ATTEMPTS, target_path)
    return len(read_csv(target_path))


def publish_non_final_row_level_records() -> int:
    target_path = OUTPUT_DIR / "official_non_final_row_level_records.csv"
    rows: list[dict[str, str]] = []
    fieldnames: list[str] = []
    for source_path in NON_FINAL_ROW_LEVEL_FILES:
        if not source_path.exists():
            continue
        source_rows = read_csv(source_path)
        if not source_rows:
            continue
        for field in source_rows[0].keys():
            if field not in fieldnames:
                fieldnames.append(field)
        rows.extend(source_rows)
    if not rows:
        return 0
    write_csv(target_path, fieldnames, rows)
    return len(rows)


def main() -> None:
    chsi_rows = with_source_dataset(read_csv(CHSI_CLEAN), "chsi_yanzhao")
    official_rows = with_source_dataset(read_official_clean_rows(), "official_site_recommendation")
    clean_rows = chsi_rows + official_rows

    clean_fields = ["source_dataset", *crawler.CLEAN_RECORD_CSV_FIELDS]
    public_fields = ["source_dataset", *crawler.PUBLIC_RECORD_CSV_FIELDS]
    summary_fields = [
        "source_dataset",
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
    ]
    undergraduate_source_summary_fields = [
        "undergraduate_school",
        "year",
        "source_dataset",
        "destination_school",
        "document_type",
        "route",
        "record_count",
        "unique_person_count",
        "with_student_id_count",
        "with_admission_major_count",
        "source_document_count",
    ]
    coverage_fields = [
        "school_id",
        "school_name",
        "province",
        "official_url",
        "has_official_recommendation_records",
        "official_recommendation_record_count",
        "coverage_note",
    ]

    coverage_base = read_csv(OUTPUT_DIR / "official_recommendation_school_coverage.csv")
    coverage_rows = build_coverage_rows(coverage_base, official_rows)

    write_csv(OUTPUT_DIR / "master_records_clean.csv", clean_fields, clean_rows)
    write_csv(OUTPUT_DIR / "master_records_public.csv", public_fields, public_rows(clean_rows))
    write_csv(
        OUTPUT_DIR / "school_year_source_summary.csv",
        summary_fields,
        build_summary_rows(clean_rows),
    )
    undergraduate_source_summary_rows = build_undergraduate_source_outcome_rows(clean_rows)
    write_csv(
        OUTPUT_DIR / "undergraduate_school_outcome_summary.csv",
        undergraduate_source_summary_fields,
        undergraduate_source_summary_rows,
    )
    write_csv(
        OUTPUT_DIR / "official_recommendation_school_coverage.csv",
        coverage_fields,
        coverage_rows,
    )
    employment_report_counts = publish_employment_report_tables()
    recommendation_source_attempt_rows = publish_recommendation_source_attempts()
    non_final_row_level_rows = publish_non_final_row_level_records()
    matched = sum(1 for row in coverage_rows if row["official_recommendation_record_count"])
    print(
        {
            "chsi_rows": len(chsi_rows),
            "official_rows": len(official_rows),
            "total_rows": len(clean_rows),
            "summary_rows": len(build_summary_rows(clean_rows)),
            "undergraduate_source_summary_rows": len(undergraduate_source_summary_rows),
            "coverage_rows": len(coverage_rows),
            "coverage_matched": matched,
            "employment_report_rows": employment_report_counts,
            "recommendation_source_attempt_rows": recommendation_source_attempt_rows,
            "non_final_row_level_rows": non_final_row_level_rows,
        }
    )


if __name__ == "__main__":
    main()
