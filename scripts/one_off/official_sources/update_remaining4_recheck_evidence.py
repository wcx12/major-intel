from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ATTEMPTS = (
    ROOT
    / "data/processed/graduate_outcomes_official_recommendation_remaining15/source_attempts.csv"
)

BIFT = "\u5317\u4eac\u670d\u88c5\u5b66\u9662"
CDSU = "\u6210\u90fd\u4f53\u80b2\u5b66\u9662"
UNNC = "\u5b81\u6ce2\u8bfa\u4e01\u6c49\u5927\u5b66"
XZA = "\u897f\u85cf\u519c\u7267\u5927\u5b66"


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_unique(existing: str, additions: list[str], separator: str = "; ") -> str:
    parts = [part.strip() for part in existing.split(separator) if part.strip()]
    for addition in additions:
        if addition and addition not in parts:
            parts.append(addition)
    return separator.join(parts)


def append_note(existing: str, addition: str) -> str:
    if addition in existing:
        return existing
    if not existing:
        return addition
    return existing.rstrip() + "; " + addition


UPDATES = {
    BIFT: {
        "live_status": (
            "HTTP 302 to custom404; HTTP 200 current non-row-level notice; "
            "HTTP 200 doctoral assessment PDF"
        ),
        "content_type": "HTML custom404 and official article; application/pdf auxiliary",
        "urls": [],
        "note": (
            "2026-06-04 recheck: official 2025/2026 final-list candidate pages "
            "remain custom404 or non-row-level notices; the readable 7e8 page is "
            "a logistics/material collection notice and exposes no public person-level "
            "final list."
        ),
    },
    CDSU: {
        "live_status": "HTTP 200 Safeline WAF HTML",
        "content_type": "HTML Safeline challenge",
        "urls": [
            "https://yjs.cdsu.edu.cn/info/1004/6518.htm",
            "https://yjs.cdsu.edu.cn/info/1004/4966.htm",
        ],
        "note": (
            "2026-06-04 recheck: official PDF candidate URL returned text/html "
            "with safeline_bot_challenge cookies rather than application/pdf; "
            "official row-level body remains unreachable without bypassing WAF."
        ),
    },
    UNNC: {
        "live_status": "HTTP 200 official pages with no row-level list",
        "content_type": "HTML portal/news/admission information",
        "urls": [
            "https://www.nottingham.edu.cn/cn/study-with-us/hmt-recruitment/postgraduate/how-to-apply.aspx",
        ],
        "note": (
            "2026-06-04 recheck: official application pages are reachable and "
            "describe application/conditional-offer workflows, but no public "
            "person-level recommendation or admission final list was found."
        ),
    },
    XZA: {
        "live_status": (
            "known official score table is non-final; current public final-list "
            "body not accessible"
        ),
        "content_type": "HTML score table/non-final auxiliary; unavailable final list",
        "urls": [
            "https://yz.chsi.com.cn/sch/schoolInfo--schId-2107935185.dhtml",
        ],
        "note": (
            "2026-06-04 recheck: no accessible official final admitted-list body "
            "was found; known score-table evidence remains non-final auxiliary "
            "material and CHSI school page does not expose person-level final rows."
        ),
    },
}


def main() -> None:
    rows, fieldnames = read_csv(SOURCE_ATTEMPTS)
    updated: list[str] = []

    for row in rows:
        update = UPDATES.get(row.get("school_name", ""))
        if not update:
            continue

        row["source_url"] = append_unique(row.get("source_url", ""), update["urls"])
        row["live_status"] = update["live_status"]
        row["content_type"] = update["content_type"]
        row["notes"] = append_note(row.get("notes", ""), update["note"])
        row["last_checked_date"] = "2026-06-04"
        updated.append(row["school_name"])

    write_csv(SOURCE_ATTEMPTS, rows, fieldnames)
    print({"updated_count": len(updated), "updated_schools": updated})


if __name__ == "__main__":
    main()
