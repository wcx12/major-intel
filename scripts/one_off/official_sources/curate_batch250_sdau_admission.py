from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch250_sdau_admission/yjsc.sdau.edu.cn/c1907eda81bf9a1b.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch250_sdau_admission_curated"
)

SCHOOL_NAME = "山东农业大学"
YEAR = 2025
SOURCE_URL = "https://yjsc.sdau.edu.cn/cms/viewPdf/f7887010dce34b0a9fc8589e584200ed"
TITLE = "山东农业大学2025年硕士研究生拟录取名单公示"

ROW_RE = re.compile(
    r"^(\d{15})\s+(\S+)\s+(\d{3})\s+(.+?)\s+([0-9A-Z]{6})\s+(.+?)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)$"
)


def _parse_line(line: str) -> dict[str, Any] | None:
    match = ROW_RE.match(line.strip())
    if not match:
        return None
    (
        student_id,
        person_name,
        college_code,
        college,
        major_code,
        major_name,
        initial_score,
        retest_score,
        total_score,
    ) = match.groups()
    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "person_name": person_name,
        "student_id": student_id,
        "undergraduate_school": "",
        "undergraduate_major": "",
        "college": college,
        "major": major_code,
        "admission_major": major_name,
        "ranking": "",
        "remarks": (
            f"院系代码: {college_code}; 初试成绩: {initial_score}; "
            f"复试成绩: {retest_score}; 总成绩: {total_score}"
        ),
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
