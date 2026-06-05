from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import fitz

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_PDF = Path(
    "data/raw/official_site_recommendation_websearch_web_20260602_batch401_gsau_life_2024_admission/"
    "smkx.gsau.edu.cn/4f3ffcf5404c4c41.pdf"
)
OUT_DIR = Path("data/processed/official_site_recommendation_websearch_web_20260602_batch401_gsau_life_2024_admission_curated")
SOURCE_URL = (
    "http://smkx.gsau.edu.cn/system/_content/download.jsp?"
    "urltype=news.DownloadAttachUrl&owner=1058947186&wbfileid=C60A7EB8CE87B56AB2C64DD8D54FC201"
)
TITLE = "生命科学技术学院2024年硕士研究生招生拟录取名单（一志愿）公示.pdf"
SCHOOL_NAME = "甘肃农业大学"
YEAR = 2024
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"


def parse_segment_tokens(tokens: list[str], *, ranking: int | None = None) -> dict[str, Any] | None:
    tokens = [_clean(token) for token in tokens if _clean(token)]
    if len(tokens) < 16:
        return None
    if not re.fullmatch(r"\d+", tokens[0] or "") or not re.fullmatch(r"\d{15}", tokens[2] or ""):
        return None
    if not re.fullmatch(r"\d{6}", tokens[3] or "") or not re.fullmatch(r"\d{6}", tokens[5] or ""):
        return None
    if not all(_looks_like_number(value) for value in tokens[7:11]):
        return None

    serial = tokens[0]
    person_name = tokens[1]
    student_id = tokens[2]
    first_major_code = tokens[3]
    first_major_name = tokens[4]
    admission_major_code = tokens[5]
    admission_major_name = tokens[6]
    total_score, written_score, interview_score, reexam_score = tokens[7:11]
    is_recommended = tokens[11]
    is_adjustment = tokens[12]
    is_equivalent = tokens[13]
    admission_category = tokens[14]
    study_mode = tokens[15]
    source_remark = " ".join(tokens[16:])

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": student_id,
        "college": "生命科学技术学院",
        "major": first_major_code,
        "admission_major": admission_major_name,
        "ranking": str(ranking or serial),
        "remarks": _remarks(
            [
                ("serial", serial),
                ("first_choice_major", f"{first_major_code}|{first_major_name}"),
                ("admission_major_code", admission_major_code),
                ("total_score", total_score),
                ("written_score", written_score),
                ("interview_score", interview_score),
                ("reexam_score", reexam_score),
                ("is_recommendation", is_recommended),
                ("is_adjustment", is_adjustment),
                ("is_equivalent_academic_ability", is_equivalent),
                ("admission_category", admission_category),
                ("study_mode", study_mode),
                ("official_admission_status", "拟录取"),
                ("source_remark", source_remark),
            ]
        ),
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def curate_records(path: Path = RAW_PDF) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for segment in _record_segments(path):
        record = parse_segment_tokens(segment, ranking=len(records) + 1)
        if record:
            records.append(record)
    return records


def _record_segments(path: Path) -> list[list[str]]:
    lines = _pdf_lines(path)
    starts = [
        index
        for index, line in enumerate(lines)
        if re.fullmatch(r"\d{1,3}", line)
        and index + 2 < len(lines)
        and re.fullmatch(r"\d{15}", lines[index + 2])
    ]
    segments: list[list[str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        segment = _trim_segment(lines[start:end])
        if segment:
            segments.append(segment)
    return segments


def _trim_segment(lines: list[str]) -> list[str]:
    stop_markers = {"专业课笔", "加试", "是否", "序", "如有异议请联系韩老师：0931-7631875", "注：总成绩=[（初试科目成绩之和）/5]×70%+复试成绩×30%"}
    trimmed: list[str] = []
    for line in lines:
        if line in stop_markers or line.startswith("生命科学技术学院"):
            break
        trimmed.append(line)
    return trimmed


def _pdf_lines(path: Path) -> list[str]:
    lines: list[str] = []
    with fitz.open(path) as document:
        for page in document:
            lines.extend(_clean(line) for line in page.get_text().splitlines() if _clean(line))
    return lines


def _looks_like_number(value: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:\.\d+)?", value or ""))


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\x0c", " ")).strip()


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key}: {_clean(value)}" for key, value in parts if _clean(value))


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_path = OUT_DIR / "records_clean_curated.csv"
    public_path = OUT_DIR / "records_public_curated.csv"
    summary_path = OUT_DIR / "school_year_summary_curated.csv"
    crawler._write_clean_records_csv(rows, clean_path)
    crawler.export_public_records_csv(clean_path, public_path)
    crawler._write_summary_csv(crawler._build_summary_rows(rows), summary_path)
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch401_gsau_life_2024_admission_curated: parsed official Gansu Agricultural University Life Science and Technology College 2024 first-choice master admission PDF.",
                "Rows are split by serial number plus 15-digit candidate id. The repeated 否 columns are recommendation/adjustment/equivalent-academic-ability flags, not admission rejection flags.",
                f"rows={len(rows)}",
                f"source_pdf={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(clean_path)})


if __name__ == "__main__":
    main()
