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
    "data/raw/official_site_recommendation_websearch_web_20260602_batch397_ppsuc_2014_admission_pdf/"
    "yzb.ppsuc.edu.cn/c057b72d942ad202.pdf"
)
OUT_DIR = Path("data/processed/official_site_recommendation_websearch_web_20260602_batch397_ppsuc_2014_admission_pdf_curated")
SOURCE_URL = "https://yzb.ppsuc.edu.cn/__local/9/4F/D1/6028C1BCA976E6639F8E94AF1A4_4303F51F_97DED.pdf?e=.pdf"
TITLE = "中国人民公安大学2014年硕士研究生招生复试情况及拟录取名单（不含校外调剂）"
SCHOOL_NAME = "中国人民公安大学"
YEAR = 2014
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"


def parse_segment_tokens(tokens: list[str], *, ranking: int | None = None) -> dict[str, Any] | None:
    tokens = [_clean(token) for token in tokens if _clean(token)]
    if len(tokens) < 12 or not re.fullmatch(r"100414\d{9}", tokens[0]):
        return None

    status_index = next((index for index, value in enumerate(tokens) if _status_value(value)), None)
    if status_index is None:
        return None
    status_token = tokens[status_index]
    status = _status_value(status_token)
    if status != "是":
        return None

    status_prefix = status_token[: -len(status)].strip()
    direction_tokens = tokens[status_index + 1 :]
    admission_major = direction_tokens[0] if direction_tokens else ""
    source_remark = " ".join(direction_tokens[1:])
    student_id, gender = tokens[:2]
    score_tokens = tokens[2:status_index]

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": "",
        "student_id": student_id,
        "college": "",
        "major": "",
        "admission_major": admission_major,
        "ranking": str(ranking or ""),
        "remarks": _remarks(
            [
                ("gender", gender),
                ("initial_score", score_tokens[0] if len(score_tokens) > 0 else ""),
                ("reexam_english_score", score_tokens[1] if len(score_tokens) > 1 else ""),
                ("total_score", score_tokens[-1] if score_tokens else ""),
                ("official_admission_status", status),
                ("status_prefix", status_prefix),
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
    starts = [index for index, line in enumerate(lines) if re.fullmatch(r"100414\d{9}", line)]
    segments: list[list[str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        segments.append(lines[start:end])
    return segments


def _pdf_lines(path: Path) -> list[str]:
    lines: list[str] = []
    with fitz.open(path) as document:
        for page in document:
            lines.extend(_clean(line) for line in page.get_text().splitlines() if _clean(line))
    return lines


def _status_value(value: str) -> str:
    value = _clean(value)
    if value in {"是", "否"}:
        return value
    if value.endswith("是"):
        return "是"
    if value.endswith("否"):
        return "否"
    return ""


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
                "batch397_ppsuc_2014_admission_pdf_curated: parsed official China People's Public Security University 2014 master admission PDF.",
                "Only rows with official_admission_status 是 were retained; rows with 否 were excluded.",
                f"rows={len(rows)}",
                f"source_pdf={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(clean_path)})


if __name__ == "__main__":
    main()
