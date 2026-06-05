from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None  # type: ignore[assignment]

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


HTML_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch256_hnmu_recommendation/"
    "www.xxmu.edu.cn/084916d104b22a9e.htm"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch256_hnmu_recommendation_curated"
)

SCHOOL_NAME = "河南医药大学"
YEAR = 2026
DOCUMENT_TYPE = "recommendation_exemption_list"
ROUTE = "recommendation_exemption"
SOURCE_URL = "https://www.xxmu.edu.cn/yjsc/info/1013/4466.htm"
TITLE = "河南医药大学2026年推荐免试攻读硕士研究生拟录取名单公示"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _table_rows(html: str) -> list[list[str]]:
    if BeautifulSoup is None:
        raise RuntimeError("BeautifulSoup is required for HNMU HTML table curation")
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        raise ValueError("No HNMU recommendation table found")
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = [_clean_text(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return rows


def _record_from_cells(cells: list[str], ranking: int) -> dict[str, Any]:
    if len(cells) < 7:
        raise ValueError(f"Unexpected HNMU table row shape: {cells}")
    college_code, college, person_name, identity, major_code, major_name, degree_type = cells[:7]
    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": identity,
        "undergraduate_school": "",
        "undergraduate_major": "",
        "college": college,
        "major": major_name,
        "admission_major": f"{major_code} {major_name}".strip(),
        "ranking": str(ranking),
        "remarks": f"院系所代码: {college_code}; 学位类型: {degree_type}",
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def curate_records(html_path: Path | None = None) -> list[dict[str, Any]]:
    path = html_path or HTML_PATH
    html = path.read_text(encoding="utf-8")
    rows = _table_rows(html)
    data_rows = rows[1:]
    return [_record_from_cells(cells, index) for index, cells in enumerate(data_rows, start=1)]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
