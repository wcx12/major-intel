from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch205_art_school_sources_curated")

CAFA_RECOMMENDATION_PDF = RAW_DIR / "www.cafa.edu.cn" / "c4f2340b429dfb98.pdf"
CAFA_MASTER_PDF = RAW_DIR / "www.cafa.edu.cn" / "430b61e6cffc3b1c.pdf"
XAFA_HTML = RAW_DIR / "zhshch.xafa.edu.cn" / "9c4d79113c45a308.htm"

CAFA_RECOMMENDATION_SOURCE_URL = "https://www.cafa.edu.cn/library/dynamic.images/info/2025926135710903.pdf"
CAFA_MASTER_SOURCE_URL = "https://www.cafa.edu.cn/library/dynamic.images/info/202642152347107.pdf"
XAFA_SOURCE_URL = "https://zhshch.xafa.edu.cn/info/1012/4216.htm"

CAFA_RECOMMENDATION_TITLE = "中央美术学院2026年接收推荐免试攻读硕士学位研究生拟录取名单"
CAFA_MASTER_TITLE = "中央美术学院2026年硕士研究生招生考试拟录取名单"
XAFA_TITLE = "西安美术学院2026年优秀应届本科毕业生免试攻读硕士学位研究生拟录取名单公示"

CAFA_RECOMMENDATION_ROW = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<recommendation_unit>\S+)\s+"
    r"(?P<admission_college>\S+)\s+"
    r"(?P<direction>.+?)\s*$"
)
CAFA_MASTER_ROW = re.compile(r"^\s*(?P<name>.+?)\s+(?P<student_id>100476\d{9})(?:\s+(?P<remark>.+?))?\s*$")


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_collapse_spaces(part) for part in parts) if part)


def _extract_pdf_lines(pdf_path: Path) -> list[str]:
    lines: list[str] = []
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        lines.extend((page.extract_text() or "").splitlines())
    return lines


def parse_cafa_recommendation_line(
    line: str,
    *,
    source_url: str = CAFA_RECOMMENDATION_SOURCE_URL,
    title: str = CAFA_RECOMMENDATION_TITLE,
) -> dict[str, Any] | None:
    match = CAFA_RECOMMENDATION_ROW.match(_collapse_spaces(line))
    if not match:
        return None
    return crawler._clean_record(
        {
            "school_name": "中央美术学院",
            "year": 2026,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "undergraduate_school": match.group("recommendation_unit"),
            "college": match.group("admission_college"),
            "admission_major": _collapse_spaces(match.group("direction")),
            "ranking": match.group("ranking"),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def parse_cafa_master_line(
    line: str,
    *,
    source_url: str = CAFA_MASTER_SOURCE_URL,
    title: str = CAFA_MASTER_TITLE,
) -> dict[str, Any] | None:
    match = CAFA_MASTER_ROW.match(_collapse_spaces(line))
    if not match:
        return None
    return crawler._clean_record(
        {
            "school_name": "中央美术学院",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": _collapse_spaces(match.group("name")),
            "student_id": match.group("student_id"),
            "remarks": _collapse_spaces(match.group("remark") or ""),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def parse_xafa_cells(
    cells: list[str],
    *,
    source_url: str = XAFA_SOURCE_URL,
    title: str = XAFA_TITLE,
) -> dict[str, Any] | None:
    if len(cells) != 8 or cells[0] == "姓名":
        return None
    name, college, major, direction, recommendation_score, interview_score, final_score, recommendation_type = (
        _collapse_spaces(cell) for cell in cells
    )
    if not name:
        return None
    return crawler._clean_record(
        {
            "school_name": "西安美术学院",
            "year": 2026,
            "document_type": "incoming_recommendation_admission_list",
            "route": "recommendation_exemption",
            "person_name": name,
            "college": college,
            "major": major,
            "admission_major": _collapse_spaces(f"{major} {direction}"),
            "remarks": _remarks(
                f"recommendation_score {recommendation_score}",
                f"interview_score {interview_score}",
                f"final_score {final_score}",
                recommendation_type,
            ),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _curate_cafa_recommendation(pdf_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    unparsed: list[str] = []
    for line in _extract_pdf_lines(pdf_path):
        if not re.match(r"^\s*\d+\s+", line):
            continue
        record = parse_cafa_recommendation_line(line)
        if record is None:
            unparsed.append(line)
            continue
        rows.append(record)
    if unparsed:
        raise ValueError(f"Unparsed CAFA recommendation rows: {len(unparsed)}")
    return rows


def _curate_cafa_master(pdf_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    unparsed: list[str] = []
    for line in _extract_pdf_lines(pdf_path):
        if "100476" not in line:
            continue
        record = parse_cafa_master_line(line)
        if record is None:
            unparsed.append(line)
            continue
        rows.append(record)
    if unparsed:
        raise ValueError(f"Unparsed CAFA master rows: {len(unparsed)}")
    return rows


def _extract_xafa_rows(html_path: Path) -> list[list[str]]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows: list[list[str]] = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [_collapse_spaces(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
    return rows


def _curate_xafa(html_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    unparsed: list[list[str]] = []
    for cells in _extract_xafa_rows(html_path):
        if cells and cells[0] == "姓名":
            continue
        record = parse_xafa_cells(cells)
        if record is None:
            unparsed.append(cells)
            continue
        rows.append(record)
    if unparsed:
        raise ValueError(f"Unparsed XAFA rows: {len(unparsed)}")
    return rows


def curate_records(
    *,
    cafa_recommendation_pdf: Path = CAFA_RECOMMENDATION_PDF,
    cafa_master_pdf: Path = CAFA_MASTER_PDF,
    xafa_html: Path = XAFA_HTML,
) -> list[dict[str, Any]]:
    rows = [
        *_curate_cafa_recommendation(cafa_recommendation_pdf),
        *_curate_cafa_master(cafa_master_pdf),
        *_curate_xafa(xafa_html),
    ]
    rows.sort(
        key=lambda row: (
            str(row.get("school_name") or ""),
            str(row.get("document_type") or ""),
            str(row.get("source_url") or ""),
            str(row.get("college") or ""),
            str(row.get("ranking") or ""),
            str(row.get("person_name") or ""),
            str(row.get("student_id") or ""),
        )
    )
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    counts: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (str(row.get("school_name") or ""), str(row.get("document_type") or ""))
        counts[key] = counts.get(key, 0) + 1
    notes = [
        "batch205_art_school_sources_curated: reparsed official CAFA PDFs and XAFA HTML table.",
        "Removed repeated CAFA PDF header rows and preserved CAFA recommendation direction, candidate ids, XAFA directions, scores, and recommendation types.",
        f"rows={len(rows)}",
        f"counts={counts}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv"), "counts": counts})


if __name__ == "__main__":
    main()
