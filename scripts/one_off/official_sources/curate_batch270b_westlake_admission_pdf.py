from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch270b_westlake_admission_pdf/"
    "www.westlake.edu.cn/8f090f22e4a1ff52.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch270b_westlake_admission_pdf_curated"
)

SCHOOL_NAME = "西湖大学"
YEAR = 2026
SOURCE_URL = "https://www.westlake.edu.cn/admissions/graduate/information/announcements/202605/P020260507325813095887.pdf"
TITLE = "西湖大学2026级博士生拟录取名单公示-4月批次.pdf"

LINE_RE = re.compile(
    r"^(?P<application>\*{3}\d{3})\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<id>\d{2}……[\dX]{3})\s+"
    r"(?P<college>\S+)\s+"
    r"(?P<major>.+?)\s+"
    r"(?P<score>\d{2,3}\.\d{2})\s+"
    r"(?P<duration>[45])(?:\s+(?P<note>.+))?$"
)


def _remarks(score: str, duration: str, note: str = "") -> str:
    parts = [f"面试成绩: {score}", f"学制: {duration}"]
    if note:
        parts.append(note)
    return "; ".join(parts)


def _record_from_line(line: str) -> dict[str, Any] | None:
    match = LINE_RE.match(line.strip())
    if not match:
        return None
    data = match.groupdict(default="")
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": data["name"],
            "student_id": data["id"],
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": data["college"],
            "major": data["major"].strip(),
            "admission_major": data["major"].strip(),
            "ranking": data["application"],
            "remarks": _remarks(data["score"], data["duration"], data["note"].strip()),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
    )


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    records = []
    for line in text.splitlines():
        record = _record_from_line(line)
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
