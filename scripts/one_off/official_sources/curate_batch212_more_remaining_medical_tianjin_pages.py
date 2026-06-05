from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch212_more_remaining_medical_tianjin_pages")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch212_more_remaining_medical_tianjin_pages_curated")

STDU_PDF = RAW_DIR / "yjs.stdu.edu.cn" / "01505ff283ae7d9a.pdf"
STDU_PAGE_URL = "https://yjs.stdu.edu.cn/enrollment/masters-degree-admission/3747-202604020003"
STDU_SOURCE_URL = (
    "https://yjs.stdu.edu.cn/sitedata/yjs/files/zhaosheng/2026/2shuoshi/fushi/"
    "石家庄铁道大学2026年硕士研究生第一志愿复试成绩和拟录取名单第一批正式稿2.pdf"
)
STDU_TITLE = "石家庄铁道大学2026年硕士研究生复试成绩和拟录取名单（第一志愿）"

ADMITTED_STATUS = "拟录取"
STATUS_TERMS = ("拟录取", "复试不合格", "不予录取", "放弃复试", "复试缺考", "缺考", "未录取", "加试不合格")
STDU_ROW_RE = re.compile(
    r"^(?P<student_id>\d{15})\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<college_code>\d{3})\s+"
    r"(?P<college>.+?)\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<major_name>.+?)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<scores>.*?)\s+"
    r"(?P<status>" + "|".join(re.escape(term) for term in STATUS_TERMS) + r")"
    r"(?:\s+(?P<note>.+))?$"
)

SCORE_LABELS = (
    "initial_total",
    "english_or_politics_score",
    "retest_subject_score",
    "interview_score",
    "retest_score",
    "total_score",
)


def _collapse_spaces(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_collapse_spaces(part) for part in parts) if part)


def _extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_stdu_line(
    line: str,
    *,
    ranking: int,
    source_url: str = STDU_SOURCE_URL,
    title: str = STDU_TITLE,
) -> dict[str, Any] | None:
    match = STDU_ROW_RE.match(_collapse_spaces(line))
    if not match or match.group("status") != ADMITTED_STATUS:
        return None

    scores = _collapse_spaces(match.group("scores")).split()
    score_parts: list[str] = []
    if len(scores) >= len(SCORE_LABELS):
        score_parts.extend(f"{label} {value}" for label, value in zip(SCORE_LABELS, scores[: len(SCORE_LABELS)]))
        if len(scores) > len(SCORE_LABELS):
            score_parts.append(f"extra_score_tokens {' '.join(scores[len(SCORE_LABELS):])}")
    elif scores:
        score_parts.append(f"raw_scores {' '.join(scores)}")

    major_code = match.group("major_code")
    major_name = match.group("major_name")
    note = _collapse_spaces(match.group("note"))
    return crawler._clean_record(
        {
            "school_name": "石家庄铁道大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "college": match.group("college"),
            "major": major_code,
            "admission_major": f"{major_code} {major_name}",
            "ranking": str(ranking),
            "remarks": _remarks(
                f"college_code {match.group('college_code')}",
                f"study_mode {match.group('study_mode')}",
                *score_parts,
                f"list_status {match.group('status')}",
                f"note {note}" if note else "",
            ),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _iter_candidate_lines(pdf_path: Path) -> list[str]:
    return [
        _collapse_spaces(line)
        for line in _extract_pdf_text(pdf_path).splitlines()
        if re.match(r"^\d{15}\s+", _collapse_spaces(line))
    ]


def summarize_stdu_pdf_lines(pdf_path: Path = STDU_PDF) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for line in _iter_candidate_lines(pdf_path):
        match = STDU_ROW_RE.match(line)
        if match:
            counts[match.group("status")] += 1
        else:
            counts["blank_or_unparsed_status"] += 1
    return dict(counts)


def curate_stdu_pdf(pdf_path: Path = STDU_PDF) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in _iter_candidate_lines(pdf_path):
        record = parse_stdu_line(line, ranking=len(rows) + 1)
        if record is not None:
            rows.append(record)
    return rows


def curate_records(*, stdu_pdf: Path = STDU_PDF) -> list[dict[str, Any]]:
    return curate_stdu_pdf(stdu_pdf)


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    status_counts = summarize_stdu_pdf_lines()
    notes = [
        "batch212_more_remaining_medical_tianjin_pages_curated: normalized Shijiazhuang Tiedao University 2026 first-choice postgraduate admission PDF.",
        "STDU: kept only rows with explicit status 拟录取; excluded blank-status rows, 缺考 rows, and 复试不合格 rows from the same score table.",
        "SXTUCM attachment was CAPTCHA-gated; TUST was a self-redirecting 302 loop; YNUCM and TUTE returned 404.",
        f"rows={len(rows)}",
        f"status_counts={status_counts}",
        f"stdu_page={STDU_PAGE_URL}",
        f"stdu_pdf={STDU_SOURCE_URL}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv"), "status_counts": status_counts})


if __name__ == "__main__":
    main()
