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
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch354_sust_admission/"
    "yjszs.sust.edu.cn"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch354_sust_admission_curated"
)

PDF_PATH = RAW_DIR / "a50ba7b4c84b3faa.pdf"
SOURCE_URL = (
    "https://yjszs.sust.edu.cn/system/_content/download.jsp?"
    "urltype=news.DownloadAttachUrl&owner=1276705140&wbfileid=D57A0CEF4D463A6B1590A67CC8146F6A"
)
TITLE = "陕西科技大学2025年硕士研究生拟录取名单"
SCHOOL_NAME = "陕西科技大学"
YEAR = 2025
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"
STUDY_MODES = {"全日制", "非全日制"}


def parse_row_tokens(tokens: list[str], *, ranking: int | None = None) -> dict[str, Any] | None:
    tokens = [_clean(token) for token in tokens if _clean(token)]
    if len(tokens) < 9:
        return None
    if tokens[0] in {"姓名", "第"}:
        return None

    person_name, student_id, college, college_code, major_code = tokens[:5]
    if not re.fullmatch(r"\d{12,15}", student_id or ""):
        return None
    if college_code and not re.fullmatch(r"\d{3}", college_code):
        return None
    if not re.fullmatch(r"[0-9A-Z]{6}", major_code or ""):
        return None

    study_index = next((index for index, value in enumerate(tokens[5:], start=5) if value in STUDY_MODES), None)
    if study_index is None:
        return None

    admission_major = _clean("".join(tokens[5:study_index]))
    tail = tokens[study_index + 1 :]
    initial_score = ""
    interview_score = ""
    total_score = ""
    source_remark = ""
    if not admission_major:
        major_tail: list[str] = []
        retained_tail: list[str] = []
        for value in tail:
            if _looks_like_number(value) or value == "推免":
                retained_tail.append(value)
            else:
                major_tail.append(value)
        admission_major = _clean("".join(major_tail))
        tail = retained_tail
    if not admission_major:
        return None

    if len(tail) >= 3 and all(_looks_like_number(value) for value in tail[:3]):
        initial_score, interview_score, total_score = tail[:3]
        source_remark = " ".join(tail[3:])
    elif len(tail) >= 2 and tail[0] == "推免" and _looks_like_number(tail[-1]):
        total_score = tail[-1]
        source_remark = " ".join(tail[:-1])
    elif tail and _looks_like_number(tail[0]):
        total_score = tail[0]
        source_remark = " ".join(tail[1:])
    elif tail and tail[0] == "推免":
        source_remark = " ".join(tail)
    else:
        return None

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": student_id,
        "college": college,
        "major": major_code,
        "admission_major": admission_major,
        "ranking": str(ranking or ""),
        "remarks": _remarks(
            [
                ("college_code", college_code),
                ("initial_score", initial_score),
                ("interview_score", interview_score),
                ("total_score", total_score),
                ("study_mode", tokens[study_index]),
                ("source_remark", source_remark),
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
    with fitz.open(path) as document:
        for page in document:
            for tokens in _page_record_tokens(page):
                record = parse_row_tokens(tokens, ranking=len(rows) + 1)
                if record:
                    rows.append(record)
    return rows


def _page_record_tokens(page: Any) -> list[list[str]]:
    records: list[list[str]] = []
    current: list[str] | None = None
    for tokens in _page_line_tokens(page):
        if len(tokens) > 1 and re.fullmatch(r"\d{12,15}", tokens[1]):
            if current:
                records.append(current)
            current = list(tokens)
            continue
        if current and not _is_header_or_footer(tokens):
            current.extend(tokens)
    if current:
        records.append(current)
    return records


def _is_header_or_footer(tokens: list[str]) -> bool:
    if not tokens:
        return True
    joined = "".join(tokens)
    return "姓名准考证号" in joined or (tokens[0] == "第" and "页" in joined)


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
                "batch354_sust_admission_curated: parsed Shaanxi University of Science and Technology 2025 postgraduate admission PDF.",
                "Rows were reconstructed from PyMuPDF word coordinates to retain candidate id, college code, major code, scores, study mode, and remarks.",
                f"rows={len(rows)}",
                f"source_pdf={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(clean_path)})


if __name__ == "__main__":
    main()
