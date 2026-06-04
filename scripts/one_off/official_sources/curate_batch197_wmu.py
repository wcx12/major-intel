from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch197_direct_pdfs/yjsy.wmu.edu.cn")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch197_wmu_curated")

FIRST_PDF_PATH = RAW_DIR / "39b18c6a617113e4.pdf"
SECOND_PDF_PATH = RAW_DIR / "f9b72ea4d8b98022.pdf"
FIRST_PDF_SOURCE_URL = "https://yjsy.wmu.edu.cn/__local/7/37/B7/FE9C98AACCA77F365E9E1FFEF3E_3CC368F6_D989A.pdf"
SECOND_PDF_SOURCE_URL = "https://yjsy.wmu.edu.cn/__local/1/19/A9/D49C9A4BC1536107F46B238B538_C5F6557A_9AED5.pdf"
PDF_METADATA = {
    FIRST_PDF_PATH.name: (
        FIRST_PDF_SOURCE_URL,
        "温州医科大学2025年硕士研究生第一批拟录取名单",
    ),
    SECOND_PDF_PATH.name: (
        SECOND_PDF_SOURCE_URL,
        "温州医科大学2025年硕士研究生第二批拟录取名单",
    ),
}

PDF_ROW_PATTERN = re.compile(
    r"^\s*(?P<student_id>\d{5})\s+"
    r"(?P<name>.+?)\s+"
    r"(?P<major_code>[0-9A-Z]{6})\s+"
    r"(?P<body>.+?)\s+"
    r"(?P<initial_total>\d{2,3})\s+"
    r"(?P<retest>\d+(?:\.\d+)?)\s+"
    r"(?P<final>\d+(?:\.\d+)?)\s+"
    r"(?P<study_mode>全日制|非全日制)"
    r"(?:\s+(?P<note>.*?))?\s*$"
)
EMBEDDED_ROW_PATTERN = re.compile(r"(\d{5}\s+\S+\s+[0-9A-Z]{6}\s+.+)")
WATERMARK_TERMS = ("公示专用", "第 ", "页，共", "温州医科大学2025年硕士研究生")


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _remarks(parts: Iterable[str]) -> str:
    return "; ".join(part for part in (_collapse_spaces(str(p)) for p in parts) if part)


def _is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if any(term in stripped for term in WATERMARK_TERMS):
        return True
    return stripped in {"考生编", "号后五", "位", "姓名", "专业代码", "专业名称", "研究方向", "备注", "专", "用", "示"}


def _extract_embedded_row(line: str) -> str:
    match = EMBEDDED_ROW_PATTERN.search(line)
    return match.group(1) if match else ""


def iter_logical_pdf_rows(lines: Iterable[str]) -> Iterable[str]:
    buffer = ""
    for raw_line in lines:
        line = _collapse_spaces(raw_line)
        if _is_noise_line(line):
            continue
        embedded = "" if re.match(r"^\d{5}\s+", line) else _extract_embedded_row(line)
        if embedded:
            line = embedded

        if re.match(r"^\d{5}\s+", line):
            if buffer and PDF_ROW_PATTERN.match(buffer):
                yield buffer
            buffer = line
        elif buffer:
            joiner = "" if line.startswith("·") else " "
            buffer = f"{buffer}{joiner}{line}"
        else:
            continue

        if PDF_ROW_PATTERN.match(buffer):
            yield buffer
            buffer = ""
    if buffer and PDF_ROW_PATTERN.match(buffer):
        yield buffer


def parse_pdf_line(line: str, *, source_url: str, title: str) -> dict[str, Any] | None:
    match = PDF_ROW_PATTERN.match(_collapse_spaces(line))
    if not match:
        return None
    admission_major = _collapse_spaces(f"{match.group('major_code')} {match.group('body')}")
    remarks = _remarks(
        [
            f"initial_total {match.group('initial_total')}",
            f"retest_score {match.group('retest')}",
            f"final_score {match.group('final')}",
            f"study_mode {match.group('study_mode')}",
            f"note {match.group('note')}" if match.group("note") else "",
        ]
    )
    return crawler._clean_record(
        {
            "school_name": "温州医科大学",
            "year": 2025,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": _collapse_spaces(match.group("name")),
            "student_id": match.group("student_id"),
            "admission_major": admission_major,
            "remarks": remarks,
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _extract_pdf_lines(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    lines: list[str] = []
    for page in reader.pages:
        lines.extend((page.extract_text() or "").splitlines())
    return lines


def _parse_pdf_records(pdf_path: Path) -> list[dict[str, Any]]:
    source_url, title = PDF_METADATA[pdf_path.name]
    rows: list[dict[str, Any]] = []
    unparsed: list[str] = []
    for line in iter_logical_pdf_rows(_extract_pdf_lines(pdf_path)):
        record = parse_pdf_line(line, source_url=source_url, title=title)
        if record is None:
            unparsed.append(line)
            continue
        rows.append(record)
    if unparsed:
        raise ValueError(f"Unparsed WMU PDF rows in {pdf_path.name}: {len(unparsed)}")
    return rows


def curate_records(pdf_paths: list[Path] | None = None) -> list[dict[str, Any]]:
    paths = pdf_paths or [FIRST_PDF_PATH, SECOND_PDF_PATH]
    rows: list[dict[str, Any]] = []
    for pdf_path in paths:
        rows.extend(_parse_pdf_records(pdf_path))
    rows.sort(
        key=lambda row: (
            str(row.get("source_url") or ""),
            str(row.get("admission_major") or ""),
            str(row.get("person_name") or ""),
            str(row.get("student_id") or ""),
        )
    )
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch197_wmu_curated: reparsed official WMU 2025 first and second batch master admission PDFs from text rows.",
        "Replaced generic extraction noise rows caused by split PDF table headers, watermarks, and wrapped names.",
        f"rows={len(rows)}",
        f"first_batch_rows={sum(row.get('source_url') == FIRST_PDF_SOURCE_URL for row in rows)}",
        f"second_batch_rows={sum(row.get('source_url') == SECOND_PDF_SOURCE_URL for row in rows)}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
