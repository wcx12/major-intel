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
    "data/raw/official_site_recommendation_websearch_web_20260602_batch410_fjnu_life_2024_result/"
    "life.fjnu.edu.cn/3363bd542ae8d9af.pdf"
)
OUT_DIR = Path("data/processed/official_site_recommendation_websearch_web_20260602_batch410_fjnu_life_2024_result_curated")
SOURCE_URL = "https://life.fjnu.edu.cn/_upload/article/files/1c/75/429798164f80a01743a8f27b70c0/d450bf92-3d86-426c-b470-9d177b6666f9.pdf"
TITLE = "福建师范大学生命科学学院2024年硕士研究生招生复试结果公布（一志愿）.pdf"
SCHOOL_NAME = "福建师范大学"
YEAR = 2024
DOCUMENT_TYPE = "master_admission_list"
ROUTE = "postgraduate_exam_or_admission"


def parse_segment_tokens(tokens: list[str], *, ranking: int | None = None) -> dict[str, Any] | None:
    tokens = [_clean(token) for token in tokens if _clean(token)]
    if len(tokens) < 10:
        return None
    if not re.fullmatch(r"\d{1,3}", tokens[0] or ""):
        return None
    if not re.fullmatch(r"\d{15}", tokens[1] or ""):
        return None
    if not re.fullmatch(r"\d{6}", tokens[3] or ""):
        return None
    if not _looks_like_number(tokens[5]) or not _looks_like_number(tokens[8]):
        return None

    status = tokens[9] if len(tokens) > 9 else ""
    if status != "建议录取":
        return None

    serial = tokens[0]
    student_id = tokens[1]
    person_name = tokens[2]
    major_code = tokens[3]
    major_name = tokens[4]
    initial_score = tokens[5]
    reexam_score = tokens[6]
    reexam_weight = tokens[7]
    total_score = tokens[8]
    study_mode = tokens[10] if len(tokens) > 10 else ""
    source_remark = " ".join(tokens[11:])

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": student_id,
        "college": "生命科学学院",
        "major": major_code,
        "admission_major": major_name,
        "ranking": str(ranking or serial),
        "remarks": _remarks(
            [
                ("serial", serial),
                ("major_code", major_code),
                ("reexam_major", major_name),
                ("initial_score_percent", initial_score),
                ("reexam_score", reexam_score),
                ("reexam_weight", reexam_weight),
                ("total_score", total_score),
                ("official_admission_status", status),
                ("study_mode", study_mode),
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
        if re.fullmatch(r"\d{1,3}", line or "")
        and index + 1 < len(lines)
        and re.fullmatch(r"\d{15}", lines[index + 1] or "")
    ]
    segments: list[list[str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        segments.append(_trim_segment(lines[start:end]))
    return segments


def _trim_segment(lines: list[str]) -> list[str]:
    stop_prefixes = ("备注：", "学院咨询电话：", "学院监督电话：")
    trimmed: list[str] = []
    for line in lines:
        if any(line.startswith(prefix) for prefix in stop_prefixes):
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
                "batch410_fjnu_life_2024_result_curated: parsed official Fujian Normal University Life Sciences College 2024 first-choice master re-exam result PDF.",
                "Only rows whose official status is 建议录取 were retained; blank status, 不予录取, and 放弃复试 rows were excluded.",
                f"rows={len(rows)}",
                f"source_pdf={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(clean_path)})


if __name__ == "__main__":
    main()
