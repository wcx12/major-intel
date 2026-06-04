from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


HTML_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch251_xisu_adjustment_admission/yzw.xisu.edu.cn/33396b4b85311a14.htm"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch251_xisu_adjustment_admission_curated"
)

SCHOOL_NAME = "西安外国语大学"
YEAR = 2026
SOURCE_URL = "https://yzw.xisu.edu.cn/info/1080/4622.htm"
TITLE = "西安外国语大学2026年硕士研究生招生考试调剂考生拟录取名单公示"


def _split_name_note(raw_name: str) -> tuple[str, str]:
    match = re.match(r"^(.+?)\s*[（(](.+?)[）)]$", raw_name.strip())
    if not match:
        return raw_name.strip(), ""
    return match.group(1).strip(), match.group(2).strip()


def _record_from_cells(cells: list[str]) -> dict[str, Any] | None:
    if len(cells) != 8 or not cells[0].isdigit():
        return None
    ranking, raw_name, student_id, major_code, major_name, initial_score, retest_score, total_score = cells
    if not (raw_name and student_id and major_code and major_name):
        return None

    person_name, name_note = _split_name_note(raw_name)
    remark_parts = [
        f"初试总分: {initial_score}",
        f"复试总分: {retest_score}",
        f"总成绩: {total_score}",
    ]
    if name_note:
        remark_parts.append(f"特殊说明: {name_note}")

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "person_name": person_name,
        "student_id": student_id,
        "undergraduate_school": "",
        "undergraduate_major": "",
        "college": "",
        "major": major_code,
        "admission_major": major_name,
        "ranking": ranking,
        "remarks": "; ".join(remark_parts),
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def curate_records(html_path: Path | None = None) -> list[dict[str, Any]]:
    path = html_path or HTML_PATH
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    records: list[dict[str, Any]] = []
    for table_row in soup.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in table_row.find_all(["td", "th"])]
        record = _record_from_cells(cells)
        if record:
            records.append(record)
    return records


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
