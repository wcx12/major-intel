from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CLEANED_ATTEMPTS = ROOT / "data/cleaned/graduate_outcomes/official_recommendation_source_attempts.csv"
PROCESSED_ATTEMPTS = (
    ROOT
    / "data/processed/graduate_outcomes_official_recommendation_remaining15/source_attempts.csv"
)
RECHECK = ROOT / "outputs/graduate_outcomes/remaining_uncovered_recheck_2026-06-04.csv"
TRACKER = ROOT / "outputs/graduate_outcomes/remaining_uncovered_schools.csv"

CQUPT = "\u91cd\u5e86\u90ae\u7535\u5927\u5b66"

NEW_URLS = [
    "https://yjs.cqupt.edu.cn/info/1179/14574.htm",
    "https://yjs.cqupt.edu.cn/info/1179/14564.htm",
]

NEW_ARTIFACTS = [
    "tmp/cqupt_2026_doctor_second_batch_14574.html",
    "tmp/cqupt_2026_doctor_second_batch_14574.headers.txt",
    "tmp/cqupt_2026_doctor_common_14564.html",
    "tmp/cqupt_2026_doctor_common_14564.headers.txt",
]

NOTE = (
    "2026-06-04 additional recheck: official graduate-school homepage publicly lists "
    "2026 doctoral proposed-admission notices at 1179/14574 and 1179/14564, but both "
    "detail URLs return HTTP 412 Precondition Failed challenge pages from direct public "
    "fetch, so no official row-level article body or attachment is ingestible."
)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_unique(existing: str, additions: list[str], separator: str) -> str:
    parts = [part.strip() for part in existing.split(separator) if part.strip()]
    for addition in additions:
        if addition not in parts:
            parts.append(addition)
    return separator.join(parts)


def append_note(existing: str, addition: str) -> str:
    if addition in existing:
        return existing
    if not existing:
        return addition
    return existing.rstrip() + "; " + addition


def update_attempts(path: Path) -> int:
    rows, fieldnames = read_csv(path)
    updated = 0
    for row in rows:
        if row.get("school_name") != CQUPT:
            continue
        row["source_url"] = append_unique(row.get("source_url", ""), NEW_URLS, "; ")
        row["local_artifact"] = append_unique(row.get("local_artifact", ""), NEW_ARTIFACTS, "; ")
        row["live_status"] = (
            "Homepage HTTP 200; graduate-school, doctoral, and ECCS detail pages HTTP 412"
        )
        row["content_type"] = "HTML homepage link list; HTML JavaScript challenge"
        row["notes"] = append_note(row.get("notes", ""), NOTE)
        row["last_checked_date"] = "2026-06-04"
        updated += 1
    write_csv(path, rows, fieldnames)
    return updated


def update_recheck() -> int:
    rows, fieldnames = read_csv(RECHECK)
    updated = 0
    for row in rows:
        if row.get("school_name") != CQUPT:
            continue
        row["official_evidence_urls"] = append_unique(
            row.get("official_evidence_urls", ""), NEW_URLS, "|"
        )
        row["recheck_result"] = (
            "official homepage is readable and exact 2026 direct-doctoral/"
            "recommendation-exempt candidate URL is known; graduate-school detail "
            "fetch still returns HTTP 412; ECCS subsite 2026/2025/2024 candidate "
            "detail pages also return HTTP 412; additional 2026 doctoral proposed-"
            "admission detail URLs 1179/14574 and 1179/14564 also return HTTP 412"
        )
        row["notes"] = append_note(row.get("notes", ""), NOTE)
        updated += 1
    write_csv(RECHECK, rows, fieldnames)
    return updated


def update_tracker() -> int:
    rows, fieldnames = read_csv(TRACKER)
    updated = 0
    for row in rows:
        if row.get("school_name") != CQUPT:
            continue
        row["official_candidate_urls"] = append_unique(
            row.get("official_candidate_urls", ""), NEW_URLS, "|"
        )
        row["current_status"] = (
            "homepage is visible but graduate-school, doctoral, and ECCS official "
            "detail pages return HTTP 412 challenge"
        )
        updated += 1
    write_csv(TRACKER, rows, fieldnames)
    return updated


def main() -> None:
    result = {
        "processed_attempts_updated": update_attempts(PROCESSED_ATTEMPTS),
        "cleaned_attempts_updated": update_attempts(CLEANED_ATTEMPTS),
        "recheck_updated": update_recheck(),
        "tracker_updated": update_tracker(),
    }
    print(result)


if __name__ == "__main__":
    main()
