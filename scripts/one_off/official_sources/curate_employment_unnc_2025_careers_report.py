from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EMPLOYMENT_DIR = ROOT / "data/processed/graduate_outcomes_official_employment_reports_remaining15"
REPORT_SOURCES_CSV = EMPLOYMENT_DIR / "report_sources.csv"
REPORT_METRICS_CSV = EMPLOYMENT_DIR / "report_metrics_clean.csv"

SCHOOL_NAME = "\u5b81\u6ce2\u8bfa\u4e01\u6c49\u5927\u5b66"
REPORT_YEAR_OR_COHORT = "2025\u5c4a"
SOURCE_URL = "https://www.nottingham.edu.cn/en/careers/documents/202425/2025-annual-report.pdf"
SOURCE_TITLE = (
    "University of Nottingham Ningbo China 2024-2025 Academic Year "
    "Careers and Employability Annual Report"
)
LOCAL_ARTIFACT = (
    "data/raw/official_employment_report_20260603_unnc_2025_careers/"
    "www.nottingham.edu.cn/2025_annual_report.pdf"
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
        "local_artifact": LOCAL_ARTIFACT,
        "fetch_status": "200_downloaded",
        "content_type": "application/pdf",
        "extraction_status": "metrics_extracted",
        "notes": (
            "Official careers PDF downloaded from nottingham.edu.cn; "
            "English report text layer extracted with pdftotext; "
            "metrics include cohort scale, bachelor/master/PhD outcomes, "
            "further-study quality, employment sectors, employer types, and regions."
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
    all_graduates = "Class of 2025 all graduates"
    bachelors = "Class of 2025 bachelors / domestic undergraduate section"
    overseas_study = "Class of 2025 undergraduate further-study destinations"
    direct_employment = "Class of 2025 graduates directly entering employment"
    undergraduate_work = "Class of 2025 undergraduate graduates directly entering employment"
    masters = "Class of 2025 domestic masters graduates"
    masters_work = "Class of 2025 domestic masters directly entering employment"
    phd = "Class of 2025 domestic PhD graduates"
    international_hmt = "Class of 2025 international, Hong Kong, Macau, and Taiwan graduates"

    return [
        _metric("graduate_count", "2715", "people", all_graduates, "Breakdown of Graduates states total 2025 graduates."),
        _metric("bachelor_count", "1666", "people", all_graduates, "Breakdown of Graduates states 1,666 bachelors."),
        _metric("master_count", "903", "people", all_graduates, "Breakdown of Graduates states 903 masters."),
        _metric("phd_count", "146", "people", all_graduates, "Breakdown of Graduates states 146 PhDs."),
        _metric("bachelor_employment_rate", "95.2", "percent", bachelors, "Highlights employment rate table gives Bachelors 95.2%."),
        _metric("master_employment_rate", "95.0", "percent", masters, "Highlights employment rate table gives Masters 95.0%."),
        _metric("phd_employment_rate", "100.0", "percent", phd, "Highlights employment rate table gives PhD graduates 100.0%."),
        _metric("undergraduate_further_study_rate", "87.4", "percent", bachelors, "Undergraduate comprehensive outcomes panel gives further study 87.4%."),
        _metric("undergraduate_direct_employment_rate", "7.5", "percent", bachelors, "Undergraduate comprehensive outcomes panel gives direct entry into employment 7.5%."),
        _metric("undergraduate_startup_rate", "0.3", "percent", bachelors, "Undergraduate comprehensive outcomes panel gives start-ups 0.3%."),
        _metric("undergraduate_overseas_further_study_count", "1364", "people", overseas_study, "Report states 1,364 graduates went abroad for further studies."),
        _metric("undergraduate_further_study_count", "1368", "people", overseas_study, "Report states the further-study graduates total 1,368."),
        _metric("undergraduate_top10_offer_rate", "47.7", "percent", overseas_study, "Further-study quality panel gives top-10 offer rate."),
        _metric("undergraduate_top50_offer_rate", "86.7", "percent", overseas_study, "Further-study quality panel gives top-50 offer rate."),
        _metric("undergraduate_top100_offer_rate", "97.8", "percent", overseas_study, "Further-study quality panel gives top-100 offer rate."),
        _metric("undergraduate_top10_enrolled_rate", "38.1", "percent", overseas_study, "Further-study quality panel gives top-10 entered rate."),
        _metric("undergraduate_top50_enrolled_rate", "82.1", "percent", overseas_study, "Further-study quality panel gives top-50 entered rate."),
        _metric("undergraduate_top100_enrolled_rate", "96.8", "percent", overseas_study, "Further-study quality panel gives top-100 entered rate."),
        _metric("undergraduate_uk_study_destination_rate", "44.3", "percent", overseas_study, "Destination country/region breakdown gives United Kingdom share."),
        _metric("undergraduate_us_study_destination_rate", "21.7", "percent", overseas_study, "Destination country/region breakdown gives United States share."),
        _metric("undergraduate_australia_study_destination_rate", "11.8", "percent", overseas_study, "Destination country/region breakdown gives Australia share."),
        _metric("undergraduate_mainland_china_study_destination_rate", "6.9", "percent", overseas_study, "Destination country/region breakdown gives Mainland China share."),
        _metric("undergraduate_singapore_study_destination_rate", "6.2", "percent", overseas_study, "Destination country/region breakdown gives Singapore share."),
        _metric("undergraduate_hk_study_destination_rate", "5.6", "percent", overseas_study, "Destination country/region breakdown gives Hong Kong SAR share."),
        _metric("direct_employment_top_organization_rate", "90.2", "percent", direct_employment, "Highlights state direct-employment graduates joining top organizations."),
        _metric("direct_employment_new_quality_productive_force_rate", "70.0", "percent", direct_employment, "Highlights state direct-employment graduates in new-quality productive-force sectors."),
        _metric("undergraduate_employer_top_org_rate", "84.8", "percent", undergraduate_work, "Undergraduate high-quality employment section gives employer profile rate."),
        _metric("undergraduate_employment_yangtze_region_rate", "67.5", "percent", undergraduate_work, "Undergraduate geographical distribution gives Yangtze River Economic Belt share."),
        _metric("undergraduate_employment_jingjinji_region_rate", "10.6", "percent", undergraduate_work, "Undergraduate geographical distribution gives Beijing-Tianjin-Hebei share."),
        _metric("undergraduate_employment_gba_region_rate", "8.1", "percent", undergraduate_work, "Undergraduate geographical distribution gives Greater Bay Area share."),
        _metric("master_direct_employment_rate", "85.1", "percent", masters, "Domestic masters outcomes panel gives direct employment rate."),
        _metric("master_further_study_rate", "6.1", "percent", masters, "Domestic masters outcomes panel gives further-study rate."),
        _metric("master_startup_rate", "3.9", "percent", masters, "Domestic masters outcomes panel gives self-start-up rate."),
        _metric("master_education_industry_rate", "23.5", "percent", masters_work, "Domestic masters industry distribution gives education share."),
        _metric("master_financial_services_rate", "20.2", "percent", masters_work, "Domestic masters industry distribution gives financial services share."),
        _metric("master_manufacturing_rate", "9.9", "percent", masters_work, "Domestic masters industry distribution gives manufacturing share."),
        _metric("master_private_enterprise_rate", "37.5", "percent", masters_work, "Domestic masters company-type panel gives private enterprise share."),
        _metric("master_government_state_owned_rate", "30.4", "percent", masters_work, "Domestic masters company-type panel gives government/SOE share."),
        _metric("master_education_public_institutions_rate", "23.8", "percent", masters_work, "Domestic masters company-type panel gives education/public institutions share."),
        _metric("master_foreign_joint_venture_rate", "8.3", "percent", masters_work, "Domestic masters company-type panel gives foreign joint venture share."),
        _metric("master_top_organization_rate", "89.4", "percent", masters_work, "Domestic masters company-type panel gives top organization share."),
        _metric("master_yangtze_region_rate", "69.9", "percent", masters_work, "Domestic masters location panel gives Yangtze River Economic Belt share."),
        _metric("master_jingjinji_region_rate", "8.1", "percent", masters_work, "Domestic masters location panel gives Beijing-Tianjin-Hebei share."),
        _metric("master_gba_region_rate", "5.9", "percent", masters_work, "Domestic masters location panel gives Greater Bay Area share."),
        _metric("master_overseas_position_rate", "1.2", "percent", masters_work, "Domestic masters location panel gives overseas position share."),
        _metric("master_ningbo_retention_rate", "34.0", "percent", masters_work, "Domestic masters location panel gives Ningbo retention rate."),
        _metric("master_zhejiang_retention_rate", "50.1", "percent", masters_work, "Domestic masters location panel gives Zhejiang retention rate."),
        _metric("phd_top_organization_rate", "98.45", "percent", phd, "Domestic PhD global/employer panel gives top organization share."),
        _metric("phd_higher_education_institution_rate", "70.5", "percent", phd, "Domestic PhD employer panel gives higher-education institution share."),
        _metric("phd_public_research_medical_other_institution_rate", "19.4", "percent", phd, "Domestic PhD employer panel gives scientific research/medical/other public institution share."),
        _metric("phd_enterprise_rate", "7.8", "percent", phd, "Domestic PhD employer panel gives enterprise share."),
        _metric("phd_yangtze_region_rate", "76.0", "percent", phd, "Domestic PhD geographical distribution gives Yangtze River Economic Belt share."),
        _metric("phd_jingjinji_region_rate", "4.7", "percent", phd, "Domestic PhD geographical distribution gives Beijing-Tianjin-Hebei share."),
        _metric("phd_gba_region_rate", "11.6", "percent", phd, "Domestic PhD geographical distribution gives Greater Bay Area share."),
        _metric("phd_overseas_university_teaching_research_rate", "3.9", "percent", phd, "Domestic PhD geographical distribution gives overseas teaching/research share."),
        _metric("phd_ningbo_retention_rate", "41.1", "percent", phd, "Domestic PhD location paragraph gives Ningbo retention rate."),
        _metric("phd_zhejiang_retention_rate", "51.9", "percent", phd, "Domestic PhD location paragraph gives Zhejiang retention rate."),
        _metric("international_hmt_further_study_rate", "15.5", "percent", international_hmt, "International/HMT overview gives further-study rate."),
        _metric("international_hmt_direct_employment_rate", "84.5", "percent", international_hmt, "International/HMT overview gives direct employment rate."),
        _metric("international_hmt_phd_employment_rate", "100.0", "percent", international_hmt, "International/HMT overview gives PhD employment rate."),
        _metric("international_hmt_mainland_china_rate", "26.2", "percent", international_hmt, "International/HMT employment location gives Mainland China share."),
        _metric("international_hmt_outside_china_rate", "73.8", "percent", international_hmt, "International/HMT employment location gives outside-China share."),
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
