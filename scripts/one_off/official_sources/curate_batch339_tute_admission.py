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
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch339_tute_admission/"
    "yjsh.tute.edu.cn"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch339_tute_admission_curated"
)

PDF_PATH = RAW_DIR / "48a7a99a2042e26f.pdf"
SOURCE_URL = "https://yjsh.tute.edu.cn/__local/C/8A/6E/B9219C8F5C980B9B37E7A8F165F_C99922C3_54DC6.pdf"
TITLE = "天津职业技术师范大学2025年硕士研究生拟录取名单"
SCHOOL_NAME = "天津职业技术师范大学"
YEAR = 2025
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"

STUDY_MODES = {"全日制", "非全日制"}


def parse_record_line(line: str, *, ranking: int | None = None) -> dict[str, Any] | None:
    parts = _clean(line).split()
    if len(parts) < 6:
        return None

    student_id = ""
    person_name = ""
    offset = 0
    if re.fullmatch(r"\d{15}", parts[0]):
        if len(parts) < 8:
            return None
        student_id = parts[0]
        person_name = parts[1]
        offset = 2
    elif re.fullmatch(r"\d{6}", parts[1] if len(parts) > 1 else ""):
        person_name = parts[0]
        offset = 1
    else:
        return None

    major_code = parts[offset]
    if not re.fullmatch(r"\d{6}", major_code):
        return None

    study_index = next((index for index, value in enumerate(parts) if value in STUDY_MODES), None)
    if study_index is None or study_index <= offset + 1:
        return None

    before_study = parts[offset + 1 : study_index]
    if len(before_study) < 2:
        return None
    scores: list[str]
    if len(before_study) >= 4 and all(_looks_like_number(value) for value in before_study[-3:]):
        admission_major = " ".join(before_study[:-3])
        scores = before_study[-3:]
        initial_score, interview_score, total_score = scores
    elif len(before_study) >= 2 and _looks_like_number(before_study[-1]):
        admission_major = " ".join(before_study[:-1])
        initial_score = ""
        interview_score = ""
        total_score = before_study[-1]
    else:
        return None
    if not admission_major:
        return None

    source_remark = " ".join(parts[study_index + 1 :])
    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": student_id,
        "major": major_code,
        "admission_major": admission_major,
        "ranking": str(ranking or ""),
        "remarks": _remarks(
            [
                ("major_code", major_code),
                ("initial_score", initial_score),
                ("interview_score", interview_score),
                ("total_score", total_score),
                ("study_mode", parts[study_index]),
                ("official_admission_status", "拟录取"),
                ("source_remark", source_remark),
            ]
        ),
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def parse_records_from_text(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
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
                "batch339_tute_admission_curated: parsed Tianjin University of Technology and Education 2025 postgraduate admission PDF.",
                "Rows with 15-digit candidate ids and one official no-initial-exam row without candidate id were retained.",
                f"rows={len(rows)}",
                f"source_pdf={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
