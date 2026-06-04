from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCHOOL = "\u4e2d\u56fd\u533b\u79d1\u5927\u5b66"
SOURCE_TITLE = (
    "\u4e2d\u56fd\u533b\u79d1\u5927\u5b662026\u5e74"
    "\u201c\u5c11\u6570\u6c11\u65cf\u9ad8\u5c42\u6b21\u9aa8\u5e72\u4eba\u624d\u8ba1\u5212"
    "\u201d\u535a\u58eb\u7814\u7a76\u751f\u62df\u5f55\u53d6\u540d\u5355\u516c\u793a"
)
SOURCE_URLS = (
    "https://www.cmu.edu.cn/cmuyjs/zsxx/tkbs.htm; "
    "https://www.cmu.edu.cn/cmuyjs/info/1901/9841.htm"
)
LOCAL_ARTIFACTS = (
    "tmp/cmu_tkbs_list.html; "
    "tmp/cmu_2026_doctor_minority_admission_9841.html; "
    "tmp/cmu_2026_doctor_minority_admission_9841.headers.txt; "
    "data/raw/official_recommendation_cmu_2026_doctor_minority_admission/"
    "cmu_2026_doctor_minority_admission.html; "
    "data/processed/official_recommendation_cmu_2026_doctor_minority_admission/"
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
                "live_status": "HTTP 200 official article with inline row-level table",
                "content_type": "text/html official article table",
                "decision": "ingested",
                "blocker_type": "official_html_table_found",
                "notes": (
                    "2026-06-04 recheck found official CMU doctoral admissions article "
                    "1901/9841 from the tkbs list. The article title states proposed "
                    "admission list publicity and the inline table exposes application "
                    "number, candidate name, college, major code, major, department, "
                    "and total score for 3 proposed-admitted minority-backbone doctoral "
                    "candidates. Cleaned into the official recommendation/admission master."
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
