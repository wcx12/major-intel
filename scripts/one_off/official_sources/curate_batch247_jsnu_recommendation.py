from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch247_jsnu_recommendation/yjsy.jsnu.edu.cn/ad453d0fffcc59fc.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch247_jsnu_recommendation_curated"
)

SCHOOL_NAME = "江苏师范大学"
YEAR = 2026
SOURCE_URL = (
    "http://yjsy.jsnu.edu.cn/_upload/article/files/ca/08/ec9ecd2d4c2daa9bb3a54722897c/"
    "0baf68fa-b026-4a15-a7e3-2b00b68a4728.pdf"
)
TITLE = "江苏师范大学2026年推荐免试硕士研究生拟录取名单.pdf"

ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<name>[\u4e00-\u9fff·]{2,8})\s+"
    r"(?P<student_id>\d{4}\*{10}\d{3}[\dXx])\s+"
    r"(?P<college_code>\d{3})\s+"
    r"(?P<college>.+?)\s*"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<major_name>.+?)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<recommendation_type>.+?)\s*$"
)


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    records: list[dict[str, Any]] = []

    for line in text.splitlines():
        match = ROW_RE.match(line.strip())
        if not match:
            continue
        remarks = [
            f"拟录取学院代码: {match.group('college_code')}",
            f"学习形式: {match.group('study_mode')}",
            f"推免类型: {match.group('recommendation_type')}",
        ]
        record = {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": match.group("college").strip(),
            "major": match.group("major_code"),
            "admission_major": match.group("major_name").strip(),
            "ranking": match.group("ranking"),
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
