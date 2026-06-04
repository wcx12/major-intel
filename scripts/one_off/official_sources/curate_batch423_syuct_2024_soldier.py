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
    "data/raw/official_site_recommendation_websearch_web_20260602_batch423_syuct_2024_master_pdf/"
    "zbhk-new.lnyun.com.cn/1d7604f89f164ea8.pdf"
)
OUT_DIR = Path("data/processed/official_site_recommendation_websearch_web_20260602_batch423_syuct_2024_soldier_curated")
SOURCE_URL = "https://zbhk-new.lnyun.com.cn/www/hgdxyjsy/pdf/202404/630116749978637260.pdf"
TITLE = "沈阳化工大学2024年硕士研究生招生“退役大学生士兵计划”一志愿考生拟录取结果公示"
SCHOOL_NAME = "沈阳化工大学"
YEAR = 2024
DOCUMENT_TYPE = "master_admission_list"
ROUTE = "postgraduate_exam_or_admission"


def parse_segment_tokens(tokens: list[str], *, ranking: int | None = None) -> dict[str, Any] | None:
    tokens = [_clean(token) for token in tokens if _clean(token)]
    if len(tokens) < 7:
        return None

    first = tokens[0].split(maxsplit=1)
    if not first or not re.fullmatch(r"\d{15}", first[0]):
        return None
    student_id = first[0]
    if len(first) > 1:
        person_name = first[1]
        details_index = 1
    else:
        if len(tokens) < 8:
            return None
        person_name = tokens[1]
        details_index = 2

    details_match = re.fullmatch(r"(.+?)\s+(\d{6})\s+(.+)", tokens[details_index])
    if details_match:
        college, major_code, major_name = details_match.groups()
        rest = tokens[details_index + 1 :]
    elif details_index + 1 < len(tokens):
        major_match = re.fullmatch(r"(\d{6})\s+(.+)", tokens[details_index + 1])
        if not major_match:
            return None
        college = tokens[details_index]
        major_code, major_name = major_match.groups()
        rest = tokens[details_index + 2 :]
    else:
        return None
    study_mode = next((token for token in rest if token in {"全日制", "非全日制"}), "")
    numbers = [token for token in rest if _looks_like_number(token)]
    status = next((token for token in rest if token in {"拟录取", "不予录取", "待递补录取"}), "")
    if status != "拟录取":
        return None
    if len(numbers) < 3:
        return None

    initial_score, reexam_score, total_score = numbers[:3]
    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": student_id,
        "college": college,
        "major": major_code,
        "admission_major": major_name,
        "ranking": str(ranking or ""),
        "remarks": _remarks(
            [
                ("source_plan", "退役大学生士兵计划"),
                ("major_code", major_code),
                ("study_mode", study_mode),
                ("initial_score", initial_score),
                ("reexam_score", reexam_score),
                ("total_score", total_score),
                ("official_admission_status", status),
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
        if re.match(r"^\d{15}(?:\s+.+)?$", line)
    ]
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
                "batch423_syuct_2024_soldier_curated: parsed official Shenyang University of Chemical Technology 2024 retired-college-soldier plan PDF.",
                "Only attachment roster rows whose official status is 拟录取 were retained; policy text containing 不予录取 was ignored.",
                f"rows={len(rows)}",
                f"source_pdf={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(clean_path)})


if __name__ == "__main__":
    main()
