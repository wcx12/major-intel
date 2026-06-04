from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch181_njupt_curated")
PDF = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch181_njupt/"
    "yzb.njupt.edu.cn/a39bfaebe4f0665a.pdf"
)
SOURCE_URL = (
    "http://yzb.njupt.edu.cn/_upload/article/files/0c/78/"
    "68d6839f485bba868e143392ce53/e542a67a-aa12-4aa3-a677-661a9f53feb7.pdf"
)
TITLE = "2026年博士研究生拟录取名单（第一批次）"
EXAM_METHODS = {"硕博连读", "直博", "申请考核"}


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _clean(row: dict[str, object]) -> dict[str, Any]:
    return crawler._clean_record(row)


def parse_doctoral_line(
    line: str,
    *,
    source_url: str,
    title: str,
) -> dict[str, Any] | None:
    values = [_collapse_spaces(value) for value in re.split(r"\s{2,}", line.strip()) if value.strip()]
    if len(values) < 8:
        return None

    sequence, student_id, identity_tail, person_name, exam_method = values[:5]
    first_level_discipline = values[5]
    college = values[6]
    admission_major = values[7]
    notes = " ".join(values[8:])

    if not sequence.isdigit():
        return None
    if not re.fullmatch(r"[A-Za-z0-9]{8,15}", student_id):
        return None
    if not re.fullmatch(r"[0-9Xx]{4}", identity_tail):
        return None
    if not re.fullmatch(r"[\u4e00-\u9fff*]{2,6}", person_name) or not re.search(
        r"[\u4e00-\u9fff]", person_name
    ):
        return None
    if exam_method not in EXAM_METHODS:
        return None

    remarks = [f"identity_tail {identity_tail.upper()}", f"exam_method {exam_method}"]
    if notes:
        remarks.append(notes)

    return _clean(
        {
            "school_name": "南京邮电大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": person_name,
            "student_id": student_id,
            "college": college,
            "major": first_level_discipline,
            "admission_major": admission_major,
            "ranking": sequence,
            "remarks": "; ".join(remarks),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _parse_pdf(path: Path, source_url: str, title: str) -> tuple[list[dict[str, Any]], int, int]:
    text = crawler._extract_pdf_text_with_pdftotext(path)
    records: list[dict[str, Any]] = []
    candidates = 0
    skipped = 0
    for line in text.splitlines():
        if not re.match(r"^\s*\d{1,3}\s+", line):
            continue
        candidates += 1
        record = parse_doctoral_line(line, source_url=source_url, title=title)
        if record is None:
            skipped += 1
            continue
        records.append(record)
    return records, candidates, skipped


def main() -> None:
    rows, candidates, skipped = _parse_pdf(PDF, SOURCE_URL, TITLE)
    rows.sort(
        key=lambda row: (
            int(str(row.get("ranking") or "0")),
            str(row.get("person_name") or ""),
            str(row.get("student_id") or ""),
        )
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(rows)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    notes = [
        "batch181_njupt_curated: parsed Nanjing University of Posts and Telecommunications official doctoral admission PDF.",
        "The generic parser shifted the identity-tail column into person_name for masked official rows; this parser keeps the official masked name.",
        f"candidate_lines={candidates}",
        f"kept={len(rows)}",
        f"skipped={skipped}",
        f"summary_rows={summary_rows}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes), encoding="utf-8")
    print({"rows": len(rows), "candidates": candidates, "skipped": skipped, "summary": summary_rows})


if __name__ == "__main__":
    main()
