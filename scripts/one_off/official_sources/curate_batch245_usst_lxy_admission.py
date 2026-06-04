from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch245_usst_lxy_admission/lxy.usst.edu.cn/dc2af7cc9b8d5d67.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch245_usst_lxy_admission_curated"
)

SCHOOL_NAME = "上海理工大学"
YEAR = 2026
COLLEGE = "理学院"
SOURCE_URL = (
    "https://lxy.usst.edu.cn/_upload/article/files/88/d2/23dc2812494e8d088def5148c24d/"
    "7193cd58-d41f-42a9-902d-041d09138d7a.pdf"
)
TITLE = "上海理工大学理学院2026年硕士研究生招生考试一志愿拟录取名单公示"

ROW_RE = re.compile(
    r"^\s*(?P<rank>\d+)\s+"
    r"(?P<student_id>\d{15})\s+"
    r"(?P<name>[\u4e00-\u9fff·]+)\s+"
    r"(?P<initial>\d+(?:\.\d+)?)\s+"
    r"(?P<interview>\d+(?:\.\d+)?)\s+"
    r"(?P<total>\d+(?:\.\d+)?)\s+"
    r"(?P<status>.+?)\s*$"
)


def _extract_major(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and stripped not in {"理学院2026年硕士研究生一志愿复试录取结果公示"}:
            if stripped not in {"序号        考生编号          考生姓名 初试成绩 复试成绩        总成绩        备注"}:
                return stripped
    return "物理学"


def _status_text(raw_status: str) -> str:
    if "大学生士兵专" in raw_status:
        return "拟录取（退役大学生士兵专项计划)"
    return raw_status.strip()


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    major = _extract_major(text)
    records: list[dict[str, Any]] = []

    for line in text.splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        status = _status_text(match.group("status"))
        if "拟录取" not in status:
            continue
        remarks = [
            f"初试成绩: {match.group('initial')}",
            f"复试成绩: {match.group('interview')}",
            f"总成绩: {match.group('total')}",
            f"录取状态: {status}",
        ]
        record = {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": COLLEGE,
            "major": major,
            "admission_major": major,
            "ranking": match.group("rank"),
            "remarks": "; ".join(remarks),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
        records.append(crawler._clean_record(record))

    return records


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
