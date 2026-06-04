from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch246_lcu_recommendation/yz.lcu.edu.cn/794a8e58cfad1d8f.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch246_lcu_recommendation_curated"
)

SCHOOL_NAME = "聊城大学"
YEAR = 2025
SOURCE_URL = "https://yz.lcu.edu.cn/docs/20241018150049513144.pdf"
TITLE = "聊城大学2025年推荐免试硕士研究生拟录取名单"


def _split_pdf_row(line: str) -> list[str]:
    return [part for part in re.split(r"\s{2,}", line.strip()) if part]


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not re.match(r"^\s*\d+\s+", line):
            continue
        parts = _split_pdf_row(line)
        if len(parts) != 7 or not parts[0].isdigit() or not re.fullmatch(r"\d{6}", parts[3]):
            continue
        ranking, name, college, major_code, major_name, score, plan_note = parts
        record = {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": name,
            "student_id": "",
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": college,
            "major": major_code,
            "admission_major": major_name,
            "ranking": ranking,
            "remarks": f"复试成绩: {score}; {plan_note}",
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
