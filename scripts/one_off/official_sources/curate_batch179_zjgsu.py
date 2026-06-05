from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch179_zjgsu_curated")
PDFS = [
    (
        Path(
            "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch179_zjgsu/"
            "yjszs.zjgsu.edu.cn/3250162b78ab6fe9.pdf"
        ),
        "https://yjszs.zjgsu.edu.cn/_upload/article/files/45/8a/c9d72c20400aa85f9baea3e0124c/13e52e06-fbc4-4368-9e81-3fb8c907048f.pdf",
        "浙江工商大学2026年“申请-考核”制博士研究生拟录取名单（第一批）",
    ),
    (
        Path(
            "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch179_zjgsu/"
            "yjszs.zjgsu.edu.cn/22d1b9ccb8c64717.pdf"
        ),
        "https://yjszs.zjgsu.edu.cn/_upload/article/files/45/8a/c9d72c20400aa85f9baea3e0124c/8dc16439-8987-4c80-bd5c-9f0b7fa295c1.pdf",
        "浙江工商大学2026年“申请-考核”制博士研究生拟录取名单（第二批）",
    ),
]

DOCTORAL_ROW_PATTERN = re.compile(
    r"^\s*(?P<rank>\d{1,3})\s+"
    r"(?P<discipline>.+?)\s+"
    r"(?P<college>.+?)\s+"
    r"(?P<major_code>[0-9A-Z]{6})\s+"
    r"(?P<major_name>.+?)\s+"
    r"(?P<student_id>\d{10})\s+"
    r"(?P<name>[\u4e00-\u9fff·]{1,12})\s+"
    r"(?P<category>非定向|定向)\s+"
    r"(?P<score>[0-9.]+)\s*"
    r"(?P<notes>.*)$"
)


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
    match = DOCTORAL_ROW_PATTERN.match(line)
    if not match:
        return None

    notes = _collapse_spaces(match.group("notes"))
    remarks = [
        "admission_method application_assessment",
        f"first_level_discipline {_collapse_spaces(match.group('discipline'))}",
        f"admission_category {match.group('category')}",
        f"total_score {match.group('score')}",
    ]
    if notes:
        remarks.append(notes)

    return _clean(
        {
            "school_name": "浙江工商大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "college": _collapse_spaces(match.group("college")),
            "major": _collapse_spaces(match.group("discipline")),
            "admission_major": f"{match.group('major_code')} {_collapse_spaces(match.group('major_name'))}",
            "ranking": match.group("rank"),
            "remarks": "; ".join(remarks),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _parse_pdf(path: Path, source_url: str, title: str) -> tuple[list[dict[str, Any]], int, int]:
    text = crawler._extract_pdf_text_with_pdftotext(path)
    records = []
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
    rows: list[dict[str, Any]] = []
    notes = [
        "batch179_zjgsu_curated: parsed Zhejiang Gongshang University official doctoral admission PDFs.",
        "The generic parser produced no rows because this PDF table layout is not covered by the shared rules.",
    ]
    for path, source_url, title in PDFS:
        parsed, candidates, skipped = _parse_pdf(path, source_url, title)
        rows.extend(parsed)
        notes.append(f"{title}: candidate_lines={candidates}, kept={len(parsed)}, skipped={skipped}")

    rows.sort(
        key=lambda row: (
            str(row.get("source_url") or ""),
            int(str(row.get("ranking") or "0")),
            str(row.get("person_name") or ""),
        )
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(rows)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    notes.extend([f"total_rows={len(rows)}", f"summary_rows={summary_rows}"])
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes), encoding="utf-8")
    print({"rows": len(rows), "summary": summary_rows, "notes": notes[2:]})


if __name__ == "__main__":
    main()
