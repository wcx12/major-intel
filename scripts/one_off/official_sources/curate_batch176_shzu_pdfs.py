from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch176_shzu_curated")
PDF_DOCUMENTS_JSONL = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch176b_shzu_pdfs/documents.jsonl"
)
ZFXY_HTML = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch176_shzu/"
    "zfxy.shzu.edu.cn/bd0ec18115f3aecd.htm"
)
ZFXY_SOURCE_URL = "https://zfxy.shzu.edu.cn/2026/0417/c12845a231298/page.htm"
ZFXY_TITLE = "石河子大学法学院2026年硕士研究生调剂复试情况公示（第二批次）"

SCHOOL_NAME = "石河子大学"
ADMIT_STATUS = "拟录取"
REJECT_STATUS_TERMS = ("拟不录取", "不予录取")

PDF_ROW_PATTERN = re.compile(
    r"^\s*(?P<rank>\d{1,3})\s+"
    r"(?P<student_id>\d{15})\s+"
    r"(?P<name>[\u4e00-\u9fff·]{2,24})\s+"
    r"(?P<major_code>[0-9A-Z]{6})\s+"
    r"(?P<major_name>[\u4e00-\u9fffA-Za-z0-9（）()·]+)\s+"
    r"(?P<tail>.+)$"
)


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _is_explicit_admission(value: str) -> bool:
    return ADMIT_STATUS in value and not any(term in value for term in REJECT_STATUS_TERMS)


def _clean(row: dict[str, object]) -> dict[str, Any]:
    return crawler._clean_record(row)


def parse_pdf_line(
    line: str,
    *,
    school_name: str,
    college: str,
    source_url: str,
    title: str,
) -> dict[str, Any] | None:
    """Parse one pdftotext layout row, keeping only explicit admission rows."""
    if not _is_explicit_admission(line):
        return None

    match = PDF_ROW_PATTERN.match(line)
    if not match:
        return None

    tail = _collapse_spaces(match.group("tail"))
    return _clean(
        {
            "school_name": school_name,
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "college": college,
            "major": match.group("major_code"),
            "admission_major": f"{match.group('major_code')} {match.group('major_name')}",
            "ranking": match.group("rank"),
            "remarks": _collapse_spaces(f"{ADMIT_STATUS}; {tail}"),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def parse_zfxy_row(
    cells: list[str],
    *,
    source_url: str,
    title: str,
    table_title: str,
) -> dict[str, Any] | None:
    """Parse one law-school HTML table row using the college-opinion column."""
    if len(cells) < 20:
        return None

    opinion = cells[19].strip()
    if opinion != ADMIT_STATUS:
        return None

    ranking = cells[13].strip() or cells[0].strip()
    remarks_parts = [
        table_title,
        f"initial_score {cells[10].strip()}",
        f"reexam_score {cells[11].strip()}",
        f"total_score {cells[12].strip()}",
        f"moral_assessment {cells[18].strip()}",
        f"college_opinion {opinion}",
    ]
    if cells[5].strip():
        remarks_parts.append(f"research_direction {cells[5].strip()}")
    if len(cells) > 20 and cells[20].strip():
        remarks_parts.append(f"notes {cells[20].strip()}")

    return _clean(
        {
            "school_name": SCHOOL_NAME,
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": cells[2].strip(),
            "student_id": cells[1].strip(),
            "college": "法学院",
            "major": cells[3].strip(),
            "admission_major": _collapse_spaces(f"{cells[3].strip()} {cells[4].strip()}"),
            "ranking": ranking,
            "remarks": "; ".join(part for part in remarks_parts if part),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _college_for_document(document: dict[str, Any]) -> str:
    source_url = str(document.get("source_url") or "")
    title = str(document.get("title") or "")
    if "cs.shzu.edu.cn" in source_url:
        return "信息科学与技术学院"
    if "wyxy.shzu.edu.cn" in source_url:
        return "外国语学院"
    if "yaoxy.shzu.edu.cn" in source_url or "药学院" in title:
        return "药学院"
    return ""


def _load_pdf_documents() -> list[dict[str, Any]]:
    documents = []
    with PDF_DOCUMENTS_JSONL.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                documents.append(json.loads(line))
    return documents


def add_pdf_records(rows: list[dict[str, Any]], notes: list[str]) -> None:
    for document in _load_pdf_documents():
        raw_path = Path(str(document.get("raw_path") or ""))
        college = _college_for_document(document)
        title = str(document.get("title") or "")
        source_url = str(document.get("source_url") or "")
        text = crawler._extract_pdf_text_with_pdftotext(raw_path)
        before = len(rows)
        candidate_lines = 0
        for line in text.splitlines():
            if not re.match(r"^\s*\d{1,3}\s+\d{15}\s+", line):
                continue
            candidate_lines += 1
            record = parse_pdf_line(
                line,
                school_name=SCHOOL_NAME,
                college=college,
                source_url=source_url,
                title=title,
            )
            if record is not None:
                rows.append(record)
        notes.append(
            f"{title}: candidate_rows={candidate_lines}, kept_explicit_admission={len(rows) - before}"
        )


def add_zfxy_records(rows: list[dict[str, Any]], notes: list[str]) -> None:
    soup = BeautifulSoup(ZFXY_HTML.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    before_all = len(rows)
    for table in soup.find_all("table"):
        table_rows = []
        for tr in table.find_all("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
            if cells:
                table_rows.append(cells)
        if len(table_rows) < 3:
            continue

        table_title = _collapse_spaces(table_rows[0][0])
        before = len(rows)
        for cells in table_rows[2:]:
            record = parse_zfxy_row(
                cells,
                source_url=ZFXY_SOURCE_URL,
                title=ZFXY_TITLE,
                table_title=table_title,
            )
            if record is not None:
                rows.append(record)
        notes.append(f"{table_title}: kept_explicit_admission={len(rows) - before}")
    notes.append(f"{ZFXY_TITLE}: kept_explicit_admission={len(rows) - before_all}")


def _ranking_sort_value(value: object) -> int:
    text = str(value or "")
    return int(text) if text.isdigit() else 0


def _dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped = []
    seen = set()
    for row in rows:
        key = (
            row.get("school_name") or "",
            row.get("year") or "",
            row.get("document_type") or "",
            row.get("route") or "",
            row.get("person_name") or "",
            row.get("student_id") or "",
            row.get("source_url") or "",
            row.get("admission_major") or "",
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def main() -> None:
    rows: list[dict[str, Any]] = []
    notes: list[str] = [
        "batch176_shzu_curated: keep only rows whose row-level PDF text or HTML college-opinion cell explicitly says 拟录取.",
        "Rows containing 拟不录取 or 不予录取 are excluded even when the page title contains admission keywords.",
    ]
    add_pdf_records(rows, notes)
    add_zfxy_records(rows, notes)
    rows = _dedupe(rows)
    rows.sort(
        key=lambda row: (
            str(row.get("college") or ""),
            str(row.get("source_url") or ""),
            _ranking_sort_value(row.get("ranking")),
            str(row.get("student_id") or ""),
        )
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(rows)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join([*notes, f"total_rows={len(rows)}", f"summary_rows={summary_rows}"]),
        encoding="utf-8",
    )
    print({"rows": len(rows), "summary": summary_rows})


if __name__ == "__main__":
    main()
