from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


INPUT_CSV = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch190_swust/records.csv")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch190_swust_curated")
PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch190_swust/gs.swust.edu.cn/bcce9edb59effe25.pdf"
)
PDF_SOURCE_URL = "https://gs.swust.edu.cn/_upload/article/files/c5/a8/47903d32491cbaedf86ee1dad05e/e8a0424a-f45b-448c-9f79-270eeb383e7a.pdf"
PDF_TITLE = "西南科技大学2026年拟录取硕士研究生（统考生、立功表彰退役军人免试生）名单.pdf"

MOTTO_NAMES = {"学科为首", "学生为本", "学者为基", "学术为要"}

PDF_ROW_PATTERN = re.compile(
    r"^\s*(?P<student_id>\d{12,15})\s+"
    r"(?P<name>.+?)\s+"
    r"(?P<college>\d{3}\|.+?)\s+"
    r"(?P<major>[0-9A-Z]{6}\|.+?)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<category>非定向|定向)\s+"
    r"(?P<subject1>\d+)\s+"
    r"(?P<subject2>\d+)\s+"
    r"(?P<subject3>\d+)\s+"
    r"(?P<subject4>\d+)\s+"
    r"(?P<initial_total>\d+)\s+"
    r"(?P<retest>\d+(?:\.\d+)?)\s+"
    r"(?P<final>\d+(?:\.\d+)?)(?:\s+(?P<note>.*?))?\s*$"
)


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _remarks(parts: list[str]) -> str:
    return "; ".join(part for part in (_collapse_spaces(p) for p in parts) if part)


def _clean(row: dict[str, object]) -> dict[str, Any]:
    return crawler._clean_record(row)


def parse_pdf_admission_line(
    line: str,
    *,
    source_url: str = PDF_SOURCE_URL,
    title: str = PDF_TITLE,
) -> dict[str, Any] | None:
    match = PDF_ROW_PATTERN.match(line)
    if not match:
        return None

    note = _collapse_spaces(match.group("note") or "")
    remarks = _remarks(
        [
            f"study_mode {match.group('study_mode')}",
            f"admission_category {match.group('category')}",
            f"subject1 {match.group('subject1')}",
            f"subject2 {match.group('subject2')}",
            f"subject3 {match.group('subject3')}",
            f"subject4 {match.group('subject4')}",
            f"initial_total {match.group('initial_total')}",
            f"retest_score {match.group('retest')}",
            f"final_score {match.group('final')}",
            f"note {note}" if note else "",
        ]
    )
    return _clean(
        {
            "school_name": "西南科技大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": _collapse_spaces(match.group("name")),
            "student_id": match.group("student_id"),
            "college": _collapse_spaces(match.group("college")),
            "admission_major": _collapse_spaces(match.group("major")),
            "remarks": remarks,
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _is_motto_row(row: dict[str, str]) -> bool:
    return row.get("person_name") in MOTTO_NAMES and row.get("major") == "特别说明"


def _parse_pdf_records(pdf_path: Path) -> list[dict[str, Any]]:
    text = crawler._extract_pdf_text_with_pdftotext(pdf_path)
    rows: list[dict[str, Any]] = []
    unparsed: list[str] = []
    for line in text.splitlines():
        if not re.match(r"^\s*\d{12,15}\s+", line):
            continue
        record = parse_pdf_admission_line(line)
        if record is None:
            unparsed.append(line)
            continue
        rows.append(record)
    if unparsed:
        raise ValueError(f"Unparsed SWUST PDF admission rows: {len(unparsed)}")
    return rows


def _clean_html_record(row: dict[str, str]) -> dict[str, Any] | None:
    if _is_motto_row(row):
        return None
    if row.get("source_url") == PDF_SOURCE_URL:
        return None
    cleaned = _clean(row)
    if (
        cleaned.get("route") == "recommendation_exemption"
        and cleaned.get("person_name")
        and cleaned.get("college")
        and cleaned.get("admission_major")
    ):
        cleaned["needs_review"] = False
        flags = [
            flag
            for flag in str(cleaned.get("quality_flags") or "").split(";")
            if flag and flag not in {"missing_student_id", "missing_undergraduate_school", "needs_review"}
        ]
        cleaned["quality_flags"] = ";".join(flags)
        if not flags:
            cleaned["quality_score"] = 100
    elif cleaned.get("needs_review"):
        return None
    return cleaned


def curate_records(
    *,
    input_csv: Path = INPUT_CSV,
    pdf_path: Path = PDF_PATH,
) -> list[dict[str, Any]]:
    rows = [record for row in _read_csv(input_csv) if (record := _clean_html_record(row))]
    rows.extend(_parse_pdf_records(pdf_path))
    rows.sort(
        key=lambda row: (
            str(row.get("source_url") or ""),
            str(row.get("route") or ""),
            str(row.get("college") or ""),
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
    summary = [
        "batch190_swust_curated: reparsed official SWUST 2026 master admission PDF and retained recommendation rows from the official HTML page.",
        "Dropped page footer motto rows and repeated PDF table headers from the generic extraction.",
        f"rows={len(rows)}",
        f"pdf_rows={sum(row.get('source_url') == PDF_SOURCE_URL for row in rows)}",
        f"recommendation_rows={sum(row.get('route') == 'recommendation_exemption' for row in rows)}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
