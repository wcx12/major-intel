from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch329_bhu_admission/"
    "yjszsxxw.bhu.edu.cn"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch329_bhu_admission_curated"
)

PDF_PATH = RAW_DIR / "9e4def14d27ef94a.pdf"
SOURCE_URL = "https://yjszsxxw.bhu.edu.cn/engine/upload/engine/2025-04/20250425164722875P.pdf"
TITLE = "渤海大学2025年全国硕士研究生招生拟录取名单公示"
SCHOOL_NAME = "渤海大学"
YEAR = 2025
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"

EMPLOYMENT_TYPES = {"非定向就业", "定向就业"}
STUDY_MODES = {"全日制", "非全日制"}
PERSON_LINE_RE = re.compile(r"^\s*\d{15}\s+")


def parse_record_line(line: str, *, ranking: int | None = None) -> dict[str, Any] | None:
    parts = _clean(line).split()
    if len(parts) < 9 or not re.fullmatch(r"\d{15}", parts[0]):
        return None

    employment_index = next(
        (index for index, value in enumerate(parts) if value in EMPLOYMENT_TYPES),
        None,
    )
    if employment_index is None or employment_index < 4:
        return None

    after_employment = parts[employment_index + 1 :]
    if len(after_employment) < 4:
        return None
    if after_employment[3] not in STUDY_MODES:
        return None
    if not all(_looks_like_number(value) for value in after_employment[:3]):
        return None

    college_major_tokens = parts[2:employment_index]
    if len(college_major_tokens) < 2:
        return None

    student_id = parts[0]
    person_name = parts[1]
    college = college_major_tokens[0]
    admission_major = " ".join(college_major_tokens[1:])
    source_remark = " ".join(after_employment[4:])

    remarks = _remarks(
        [
            ("admission_category", parts[employment_index]),
            ("initial_score", after_employment[0]),
            ("interview_score", after_employment[1]),
            ("total_score", after_employment[2]),
            ("study_mode", after_employment[3]),
            ("official_admission_status", "拟录取"),
            ("source_remark", source_remark),
        ]
    )

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": student_id,
        "college": college,
        "major": admission_major,
        "admission_major": admission_major,
        "ranking": str(ranking or ""),
        "remarks": remarks,
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def parse_records_from_text(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        if not PERSON_LINE_RE.match(line):
            continue
        record = parse_record_line(line, ranking=len(rows) + 1)
        if record:
            rows.append(record)
    return rows


def curate_records() -> list[dict[str, Any]]:
    return parse_records_from_text(_extract_pdf_raw_text(PDF_PATH))


def _extract_pdf_raw_text(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["pdftotext", "-raw", str(path), "-"],
            capture_output=True,
            text=False,
            timeout=60,
            check=False,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    return crawler._decode_pdftotext_output(completed.stdout)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\x0c", " ")).strip()


def _looks_like_number(value: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:\.\d+)?", value or ""))


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key}: {_clean(value)}" for key, value in parts if _clean(value))


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch329_bhu_admission_curated: parsed Bohai University 2025 postgraduate admission PDF.",
                "Only 15-digit candidate-id rows with admission_category, three scores, and study_mode were retained.",
                f"rows={len(rows)}",
                f"source_pdf={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
