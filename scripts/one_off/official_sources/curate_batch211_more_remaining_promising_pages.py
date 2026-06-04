from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch211_more_remaining_promising_pages")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch211_more_remaining_promising_pages_curated")

TONGJI_DENTISTRY_HTML = RAW_DIR / "dent.tongji.edu.cn" / "9a91fbf5cdc02e9d.htm"
TONGJI_DENTISTRY_URL = "https://dent.tongji.edu.cn/info/1191/11811.htm"
TONGJI_DENTISTRY_TITLE = "同济大学口腔医学院2026届本科生推荐免试研究生结果公示"


def _collapse_spaces(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_collapse_spaces(part) for part in parts) if part)


def _html_table_rows(html_path: Path) -> list[list[str]]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows: list[list[str]] = []
    for tr in soup.find_all("tr"):
        cells = [_collapse_spaces(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return rows


def curate_tongji_dentistry_html(html_path: Path = TONGJI_DENTISTRY_HTML) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cells in _html_table_rows(html_path):
        if len(cells) != 6 or cells[0] == "序号":
            continue
        sequence, name, qualification_type, retest_total, admission_status, note = cells
        if admission_status != "拟录取":
            continue
        rows.append(
            crawler._clean_record(
                {
                    "school_name": "同济大学",
                    "year": 2026,
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": name,
                    "college": "口腔医学院",
                    "ranking": sequence,
                    "remarks": _remarks(
                        f"qualification_type {qualification_type}",
                        f"retest_total {retest_total}",
                        f"admission_status {admission_status}",
                        f"note {note}" if note else "",
                    ),
                    "source_url": TONGJI_DENTISTRY_URL,
                    "title": TONGJI_DENTISTRY_TITLE,
                    "needs_review": False,
                }
            )
        )
    rows.sort(key=lambda row: int(str(row.get("ranking") or 0)))
    return rows


def curate_records(*, tongji_dentistry_html: Path = TONGJI_DENTISTRY_HTML) -> list[dict[str, Any]]:
    return curate_tongji_dentistry_html(tongji_dentistry_html)


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch211_more_remaining_promising_pages_curated: normalized Tongji University School of Stomatology 2026 recommendation exemption result table.",
        "NUFE attachment was CAPTCHA-gated; Xidian page retained no static list after public period; ZAFU returned 404; ShanghaiTech and CPU returned 410.",
        f"rows={len(rows)}",
        f"source_page={TONGJI_DENTISTRY_URL}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
