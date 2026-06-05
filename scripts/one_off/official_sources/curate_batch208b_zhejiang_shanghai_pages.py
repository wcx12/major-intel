from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_RECORDS_CSV = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch208b_zhejiang_shanghai_pages/records.csv"
)
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch208b_zhejiang_shanghai_pages_curated")

HZNU_SOURCE_URL = "https://lcyxy.hznu.edu.cn/upload/resources/file/2025/09/24/7899961.xls"
HZNU_PAGE_URL = "https://lcyxy.hznu.edu.cn/c/2025-09-24/3111521.shtml"
HZNU_TITLE = "杭州师范大学2026年临床医学专业学位硕士研究生招生拟录取名单公示（推免生）"
HZNU_COLLEGE = "临床医学院（口腔医学院）"


def _collapse_spaces(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def normalize_hznu_row(row: dict[str, Any]) -> dict[str, Any]:
    code = _collapse_spaces(row.get("major"))
    name = _collapse_spaces(row.get("admission_major"))
    return crawler._clean_record(
        {
            "school_name": "杭州师范大学",
            "year": 2026,
            "document_type": "incoming_recommendation_admission_list",
            "route": "recommendation_exemption",
            "person_name": _collapse_spaces(row.get("person_name")),
            "college": HZNU_COLLEGE,
            "major": code,
            "admission_major": _collapse_spaces(f"{code} {name}"),
            "ranking": _collapse_spaces(row.get("ranking")),
            "remarks": f"study_mode {_collapse_spaces(row.get('remarks'))}",
            "source_url": _collapse_spaces(row.get("source_url")) or HZNU_SOURCE_URL,
            "title": _collapse_spaces(row.get("title")) or HZNU_TITLE,
            "needs_review": False,
        }
    )


def curate_records(*, records_csv: Path = RAW_RECORDS_CSV) -> list[dict[str, Any]]:
    with records_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    curated = [
        normalize_hznu_row(row)
        for row in rows
        if _collapse_spaces(row.get("school_name")) == "杭州师范大学"
        and "推免生" in _collapse_spaces(row.get("title"))
    ]
    curated.sort(key=lambda row: (str(row.get("college") or ""), str(row.get("major") or ""), str(row.get("person_name") or "")))
    return curated


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch208b_zhejiang_shanghai_pages_curated: normalized HZNU clinical medicine 2026 recommendation-exemption admission XLS records.",
        "Corrected the crawler's attachment-date year 2025 to the title year 2026 and mapped the route to recommendation_exemption.",
        "USST pages returned site hint pages, ZAFU returned 404, and no records were merged from those sources.",
        f"rows={len(rows)}",
        f"source_page={HZNU_PAGE_URL}",
        f"source_attachment={HZNU_SOURCE_URL}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
