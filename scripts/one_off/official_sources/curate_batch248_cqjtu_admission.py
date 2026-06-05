from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch248_cqjtu_admission/yjszs.cqjtu.edu.cn/ab9261a571302314.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch248_cqjtu_admission_curated"
)

SCHOOL_NAME = "重庆交通大学"
YEAR = 2025
SOURCE_URL = "https://yjszs.cqjtu.edu.cn/__local/E/EB/D8/88DAF14D0F7C9C26C90E97E6BF5_FE0B182C_A1952.pdf"
TITLE = "重庆交通大学2025年硕士招生成绩及拟录取结果公示（一志愿）"
ADMITTED_STATUS = "拟录取"


def _score_remarks(college_code: str, scores: list[str]) -> str:
    labels = ["初试总分", "复试笔试", "复试面试", "综合成绩"]
    if len(scores) == 5:
        labels = ["初试总分", "复试笔试", "复试面试", "复试政治", "综合成绩"]
    parts = [f"学院代码: {college_code}"]
    parts.extend(f"{label}: {value}" for label, value in zip(labels, scores))
    return "; ".join(parts)


def _parse_line(line: str) -> dict[str, Any] | None:
    tokens = line.strip().split()
    if len(tokens) < 9 or not re.fullmatch(r"\d{3}", tokens[0]):
        return None
    try:
        student_index = next(index for index, token in enumerate(tokens) if re.fullmatch(r"\d{15}", token))
    except StopIteration:
        return None
    if student_index <= 4 or tokens[-1] != ADMITTED_STATUS:
        return None

    scores = tokens[student_index + 1 : -1]
    if len(scores) not in {4, 5}:
        return None

    college_code, college, major_code, major_name = tokens[:4]
    name = "".join(tokens[4:student_index])
    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "person_name": name,
        "student_id": tokens[student_index],
        "undergraduate_school": "",
        "undergraduate_major": "",
        "college": college,
        "major": major_code,
        "admission_major": major_name,
        "ranking": "",
        "remarks": _score_remarks(college_code, scores),
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
