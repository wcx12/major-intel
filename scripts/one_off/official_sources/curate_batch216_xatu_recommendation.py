from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch216_xatu_recommendation")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch216_xatu_recommendation_curated")

XATU_HTML = RAW_DIR / "grs.xatu.edu.cn" / "c0f20c9791623b5a.htm"
XATU_SOURCE_URL = "https://grs.xatu.edu.cn/info/1024/4652.htm"
XATU_TITLE = "西安工业大学2026年推荐优秀应届本科毕业生免试攻读研究生名单公示-西安工业大学研究生院"


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


def curate_xatu_html(html_path: Path = XATU_HTML) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cells in _html_table_rows(html_path):
        if len(cells) != 6 or cells[0] == "序号" or not cells[0].isdigit():
            continue
        sequence, student_id, name, college, major_code, major_name = cells
        rows.append(
            crawler._clean_record(
                {
                    "school_name": "西安工业大学",
                    "year": 2026,
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": name,
                    "student_id": student_id,
                    "undergraduate_major": f"{major_code} {major_name}",
                    "college": college,
                    "major": major_name,
                    "ranking": sequence,
                    "remarks": _remarks(
                        f"undergraduate_major_code {major_code}",
                        "recommendation_status 拟推荐",
                    ),
                    "source_url": XATU_SOURCE_URL,
                    "title": XATU_TITLE,
                    "needs_review": False,
                }
            )
        )
    rows.sort(key=lambda row: int(str(row.get("ranking") or 0)))
    return rows


def curate_records(*, xatu_html: Path = XATU_HTML) -> list[dict[str, Any]]:
    return curate_xatu_html(xatu_html)


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch216_xatu_recommendation_curated: normalized XATU university-level 2026 recommendation exemption table.",
        "The generic parser captured 230 people but marked all for review; this curation preserves sequence, student id, college, major code, and major name from the HTML table.",
        f"rows={len(rows)}",
        f"xatu_page={XATU_SOURCE_URL}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
