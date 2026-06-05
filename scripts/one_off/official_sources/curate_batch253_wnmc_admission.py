from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch253_wnmc_recommendation/www.wnmc.edu.cn/17cb42ea25f79920.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch253_wnmc_admission_curated"
)

SCHOOL_NAME = "皖南医学院"
YEAR = 2025
SOURCE_URL = "https://www.wnmc.edu.cn/__local/A/C6/DA/A19EA1BD793B172B18AD6C3E700_229104C8_44124.pdf"
TITLE = "皖南医学院2025年硕士研究生招生拟录取名单"

ROW_RE = re.compile(
    r"^(\d{1,4})\s+(\d{15})\s+(\S+)\s+([男女])\s+([0-9A-Z]{6})\s+(.+?)\s+(.+?)\s+"
    r"(一志愿|调剂)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)(?:\s+(.+))?$"
)


def _parse_line(line: str) -> dict[str, Any] | None:
    match = ROW_RE.match(line.strip())
    if not match:
        return None
    (
        ranking,
        student_id,
        person_name,
        gender,
        major_code,
        major_name,
        direction,
        category,
        initial_score,
        retest_score,
        admission_score,
        note,
    ) = match.groups()
    remark_parts = [
        f"性别: {gender}",
        f"研究方向: {direction}",
        f"类别: {category}",
        f"初试总分: {initial_score}",
        f"复试总分: {retest_score}",
        f"录取总分: {admission_score}",
    ]
    if note:
        remark_parts.append(f"备注: {note}")

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


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        record = _parse_line(line)
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
