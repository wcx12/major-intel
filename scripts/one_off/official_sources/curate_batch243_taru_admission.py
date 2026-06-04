from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260529_batch243_taru_admission/yjsb.taru.edu.cn/3b74bf6c52b4cae6.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260529_batch243_taru_admission_curated"
)

SCHOOL_NAME = "塔里木大学"
YEAR = 2026
SOURCE_URL = "https://yjsb.taru.edu.cn/__local/3/9F/D4/8F60D02C5578C92BD23BF082ADE_9B5FB6D3_40612.pdf"
TITLE = "塔里木大学2026年硕士研究生招生第一批次一志愿考生复试成绩及录取结果公示"


def _split_pdf_row(line: str) -> list[str]:
    return [part for part in re.split(r"\s{2,}", line.strip()) if part]


def _final_admission_flag(parts: list[str]) -> tuple[str, int]:
    flag_positions = [index for index, part in enumerate(parts) if part in {"是", "否"}]
    if not flag_positions:
        return "", -1
    index = flag_positions[-1]
    return parts[index], index


def _remarks_from_parts(parts: list[str], flag_index: int) -> str:
    remarks: list[str] = []
    if len(parts) > 5 and parts[5] != "不区分研究方向":
        remarks.append(f"研究方向: {parts[5]}")
    if len(parts) > 6:
        remarks.append(f"学习方式: {parts[6]}")
    tail = " ".join(parts[flag_index + 1 :]).strip()
    if tail:
        remarks.append(tail)
    return "; ".join(remarks)


def curate_records(pdf_path: Path = PDF_PATH) -> list[dict[str, Any]]:
    text = crawler._extract_pdf_text_with_pdftotext(pdf_path)
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not re.match(r"^\s*\d+\s+\d{15}\s+", line):
            continue
        parts = _split_pdf_row(line)
        if len(parts) < 8:
            continue
        admission_flag, flag_index = _final_admission_flag(parts)
        if admission_flag != "是":
            continue
        record = {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": parts[2],
            "student_id": parts[1],
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": parts[3],
            "major": parts[4],
            "admission_major": parts[4],
            "ranking": parts[0],
            "remarks": _remarks_from_parts(parts, flag_index),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
        rows.append(crawler._clean_record(record))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
