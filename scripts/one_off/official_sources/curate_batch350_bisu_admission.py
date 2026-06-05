from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import fitz

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch350_beijing_admission_cluster/"
    "www.bisu.edu.cn"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch350_bisu_admission_curated"
)

PDF_PATH = RAW_DIR / "d5f8adaff32a14fc.pdf"
SOURCE_URL = "https://www.bisu.edu.cn/bucketeducation/67eca8b8e4b078dee86ea4c3.pdf"
TITLE = "北京第二外国语学院2025年研究生招生考试一志愿拟录取名单"
SCHOOL_NAME = "北京第二外国语学院"
YEAR = 2025
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"


def parse_row_tokens(
    tokens: list[str],
    *,
    ranking: int | None = None,
    special_plan: str = "",
) -> dict[str, Any] | None:
    tokens = [_clean(token) for token in tokens if _clean(token)]
    if len(tokens) < 6:
        return None

    name_parts: list[str] = []
    after_id: list[str] = []
    student_id = ""
    for index, token in enumerate(tokens):
        match = re.search(r"\d{14,15}", token)
        if not match:
            continue
        student_id = match.group(0)
        prefix = token[: match.start()].strip()
        suffix = token[match.end() :].strip()
        name_parts.extend(tokens[:index])
        if prefix:
            name_parts.append(prefix)
        if suffix:
            after_id.append(suffix)
        after_id.extend(tokens[index + 1 :])
        break

    person_name = _clean("".join(name_parts))
    if not student_id or not person_name or len(after_id) < 5:
        return None

    initial_score, interview_score, total_score = after_id[:3]
    if not all(_looks_like_number(value) for value in (initial_score, interview_score, total_score)):
        return None

    college = after_id[3]
    admission_major = _clean("".join(after_id[4:]))
    if not college or not admission_major:
        return None

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": student_id,
        "college": college,
        "admission_major": admission_major,
        "ranking": str(ranking or ""),
        "remarks": _remarks(
            [
                ("initial_score", initial_score),
                ("interview_score", interview_score),
                ("total_score", total_score),
                ("special_plan", special_plan),
                ("official_admission_status", "拟录取"),
            ]
        ),
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def curate_records() -> list[dict[str, Any]]:
    return parse_records_from_pdf(PDF_PATH)


def parse_records_from_pdf(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_plan = ""
    with fitz.open(path) as document:
        for page in document:
            for tokens in _page_line_tokens(page):
                line_text = "".join(tokens)
                if "退役大学生士兵专项计划" in line_text:
                    current_plan = "退役大学生士兵专项计划"
                    continue
                record = parse_row_tokens(tokens, ranking=len(rows) + 1, special_plan=current_plan)
                if record:
                    rows.append(record)
    return rows


def _page_line_tokens(page: Any) -> list[list[str]]:
    grouped: list[tuple[float, list[tuple[float, str]]]] = []
    for word in page.get_text("words"):
        x0, y0, _x1, _y1, text, *_rest = word
        y = float(y0)
        for anchor_y, words in grouped:
            if abs(anchor_y - y) <= 3:
                words.append((float(x0), str(text)))
                break
        else:
            grouped.append((y, [(float(x0), str(text))]))
    return [[text for _x, text in sorted(words, key=lambda item: item[0])] for _y, words in grouped]


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
    crawler._write_clean_records_csv(rows, clean_path)
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch350_bisu_admission_curated: parsed Beijing International Studies University 2025 first-choice postgraduate admission PDF.",
                "Rows were reconstructed from PyMuPDF word coordinates because the table has merged name/candidate-id cells in some rows.",
                f"rows={len(rows)}",
                f"source_pdf={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(clean_path)})


if __name__ == "__main__":
    main()
