from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATHS = [
    Path(
        "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch244_ctgu_health_admission/jkyxy.ctgu.edu.cn/4ac50b00f6984527.pdf"
    ),
    Path(
        "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch244_ctgu_health_admission/jkyxy.ctgu.edu.cn/9064dcb26f80dfc0.pdf"
    ),
]
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch244_ctgu_health_admission_curated"
)

SCHOOL_NAME = "三峡大学"
YEAR = 2026
COLLEGE = "健康医学院"

PDF_META = {
    "4ac50b00f6984527.pdf": {
        "source_url": "https://jkyxy.ctgu.edu.cn/__local/B/F3/04/645C9F3068D17EA0D7B220A9E0C_BF8D961B_167C5.pdf",
        "title": "健康医学院2026年硕士研究生拟录取考生名单公示第一批",
    },
    "9064dcb26f80dfc0.pdf": {
        "source_url": "https://jkyxy.ctgu.edu.cn/__local/4/7E/9D/5B34B462C4AACEDB21A986B4802_07C184C4_C3F9.pdf",
        "title": "健康医学院2026年硕士研究生调剂复试拟录取考生名单公示第二批",
    },
}


def _split_pdf_row(line: str) -> list[str]:
    return [part for part in re.split(r"\s{2,}", line.strip()) if part]


def _records_from_pdf(path: Path) -> list[dict[str, Any]]:
    meta = PDF_META[path.name]
    text = crawler._extract_pdf_text_with_pdftotext(path)
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not re.match(r"^\s*\d+\s+\d{6}\s+", line):
            continue
        parts = _split_pdf_row(line)
        if len(parts) < 11 or not parts[4].isdigit():
            continue
        candidate_category = parts[9] if parts[9] in {"一志愿", "调剂生"} else ""
        learning_mode = parts[10] if candidate_category else parts[9]
        status = parts[11] if len(parts) > 11 else "拟录取"
        if status != "拟录取":
            continue
        remarks = [
            f"初试成绩: {parts[5]}",
            f"复试成绩: {parts[6]}",
            f"总成绩: {parts[7]}",
        ]
        if candidate_category:
            remarks.append(f"考生类别: {candidate_category}")
        remarks.append(f"学习方式: {learning_mode}")
        if parts[4] == "110756000002164":
            remarks.append("享受照顾政策")
        record = {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": parts[3],
            "student_id": parts[4],
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": COLLEGE,
            "major": f"{parts[1]}|{parts[2]}",
            "admission_major": f"{parts[1]}|{parts[2]}",
            "ranking": parts[8],
            "remarks": "; ".join(remarks),
            "source_url": meta["source_url"],
            "title": meta["title"],
            "needs_review": False,
        }
        records.append(crawler._clean_record(record))
    return records


def curate_records(pdf_paths: list[Path] | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in pdf_paths or PDF_PATHS:
        rows.extend(_records_from_pdf(path))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
