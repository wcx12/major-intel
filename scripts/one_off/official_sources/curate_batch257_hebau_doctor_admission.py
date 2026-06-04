from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch257_hebau_doctor_admission/"
    "yanjiusheng.hebau.edu.cn/0e22121dee46236a.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch257_hebau_doctor_admission_curated"
)

SCHOOL_NAME = "河北农业大学"
YEAR = 2026
SOURCE_URL = "https://yanjiusheng.hebau.edu.cn/__local/B/8A/32/0EF1F4B72A57F5B93FA41D72EF8_926A5724_1C059.pdf"
TITLE = "河北农业大学2026级硕博连读研究生拟录取名单公示"

SCORE_RE = re.compile(r"^\d{2,3}\.\d{2}$")


def _compact(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _is_data_tokens(tokens: list[str]) -> bool:
    return (
        len(tokens) >= 7
        and tokens[0].isdigit()
        and tokens[1].isdigit()
        and SCORE_RE.match(tokens[-2]) is not None
    )


def _is_college_prefix(line: str) -> bool:
    compact = _compact(line)
    return bool(
        compact
        and len(compact) <= 12
        and not compact.startswith("（")
        and compact.endswith("学院")
    )


def _remarks(advisors: list[str], score: str, category: str) -> str:
    parts = []
    if advisors:
        parts.append(f"第一导师: {advisors[0]}")
    if len(advisors) > 1:
        parts.append(f"第二导师: {advisors[1]}")
    if len(advisors) > 2:
        parts.append(f"其他导师: {'、'.join(advisors[2:])}")
    parts.append(f"考核成绩: {score}")
    parts.append(f"拟录取类别: {category}")
    return "; ".join(parts)


def _record_from_line(line: str, pending_college: str, suffix: str = "") -> dict[str, Any] | None:
    tokens = line.split()
    if not _is_data_tokens(tokens):
        return None

    ranking, student_id, person_name = tokens[:3]
    score = tokens[-2]
    category = tokens[-1]
    middle = tokens[3:-2]
    if pending_college:
        if len(middle) < 2:
            return None
        college = f"{pending_college}{suffix}"
        admission_major = middle[0]
        advisors = middle[1:]
    else:
        if len(middle) < 3:
            return None
        college = middle[0]
        admission_major = middle[1]
        advisors = middle[2:]

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
        "major": admission_major,
        "admission_major": admission_major,
        "ranking": ranking,
        "remarks": _remarks(advisors, score, category),
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    lines = [line for line in text.splitlines() if line.strip()]
    records: list[dict[str, Any]] = []
    pending_college = ""
    index = 0
    while index < len(lines):
        line = lines[index]
        tokens = line.split()
        if _is_college_prefix(line) and not _is_data_tokens(tokens):
            pending_college = _compact(line)
            index += 1
            continue

        suffix = ""
        skip_next = False
        if pending_college and index + 1 < len(lines):
            next_compact = _compact(lines[index + 1])
            if next_compact.startswith("（") and next_compact.endswith("）"):
                suffix = next_compact
                skip_next = True

        record = _record_from_line(line, pending_college, suffix)
        if record:
            records.append(record)
            pending_college = ""
            index += 2 if skip_next else 1
            continue

        index += 1
    return records


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
