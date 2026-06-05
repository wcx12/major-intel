from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCHOOL = "\u5317\u4eac\u670d\u88c5\u5b66\u9662"
SOURCE_TITLE = (
    "\u5317\u4eac\u670d\u88c5\u5b66\u96622026\u5e74"
    "\u535a\u58eb\u7814\u7a76\u751f\u62db\u751f\u8003\u8bd5"
    "\u62df\u5f55\u53d6\u7ed3\u679c\u516c\u793a\uff08\u7b2c\u4e00\u6279\uff09"
)
SOURCE_URLS = (
    "https://yjs.bift.edu.cn/zsgz/zsxx/592661e0e6f74dac8942679a9dfe0882.htm; "
    "https://yjs.bift.edu.cn/docs//2026-06/85b36649ec7b43d79acd889705f02a2d.pdf"
)
LOCAL_ARTIFACTS = (
    "tmp/bift_zsxx_index.html; "
    "tmp/bift_2026_doctor_admission_first_5926.html; "
    "tmp/bift_2026_doctor_admission_first_5926.headers.txt; "
    "tmp/bift_2026_doctor_admission_first.pdf; "
    "tmp/bift_2026_doctor_admission_first_pdf.headers.txt; "
    "data/raw/official_recommendation_bift_2026_doctor_admission_first/"
    "bift_2026_doctor_admission_first.pdf; "
    "data/raw/official_recommendation_bift_2026_doctor_admission_first/"
    "bift_2026_doctor_admission_first_page.html; "
    "data/processed/official_recommendation_bift_2026_doctor_admission_first/"
    "records_clean_curated.csv"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_source_attempts() -> int:
    path = ROOT / "data/processed/graduate_outcomes_official_recommendation_remaining15/source_attempts.csv"
    rows = read_csv(path)
    fieldnames = list(rows[0].keys())
    updated = 0
    for row in rows:
        if row.get("school_name") != SCHOOL:
            continue
        row.update(
            {
                "source_title": SOURCE_TITLE,
                "source_url": SOURCE_URLS,
                "local_artifact": LOCAL_ARTIFACTS,
                "live_status": "HTTP 200 official article and application/pdf attachment",
                "content_type": "text/html official article; application/pdf",
                "decision": "ingested",
                "blocker_type": "official_pdf_access_restored",
                "notes": (
                    "2026-06-04 recheck found a newly published official BIFT doctoral "
                    "proposed-admission result article in the admissions-information list. "
                    "The PDF attachment is application/pdf and contains 64 candidate rows "
                    "with candidate number, name, material-review score, comprehensive "
                    "assessment score, total score, and admission status. Cleaned only the "
                    "35 rows marked proposed admitted and excluded 29 proposed-not-admitted rows."
                ),
                "last_checked_date": "2026-06-04",
            }
        )
        updated += 1
    write_csv(path, rows, fieldnames)
    return updated


def remove_from_remaining(path: Path) -> int:
    rows = read_csv(path)
    fieldnames = list(rows[0].keys())
    kept = [row for row in rows if row.get("school_name") != SCHOOL]
    write_csv(path, kept, fieldnames)
    return len(rows) - len(kept)


def main() -> None:
    result = {
        "source_attempts_updated": update_source_attempts(),
        "remaining_tracker_removed": remove_from_remaining(
            ROOT / "outputs/graduate_outcomes/remaining_uncovered_schools.csv"
        ),
        "latest_recheck_removed": remove_from_remaining(
            ROOT / "outputs/graduate_outcomes/remaining_uncovered_recheck_2026-06-04.csv"
        ),
    }
    print(result)


if __name__ == "__main__":
    main()
