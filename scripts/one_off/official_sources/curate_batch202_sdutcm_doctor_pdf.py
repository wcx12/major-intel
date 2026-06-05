from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch202_sdutcm_doctor_pdf/yjs.sdutcm.edu.cn/cb583ad75967bb89.pdf"
)
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch202_sdutcm_doctor_pdf_curated")
SOURCE_URL = "https://yjs.sdutcm.edu.cn/__local/8/82/E8/08B98A973B57AE574FEE8244163_76DB338B_5BA11.pdf"
TITLE = "山东中医药大学2026年全日制博士研究生第一批次拟录取名单公示"

DOCTOR_ROW_PATTERN = re.compile(
    r"^\s*(?P<student_id>104419\d{4})\s+"
    r"(?P<college>\S+学院|\S+研究院)\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<major_code>[0-9A-Z]{6})\s+"
    r"(?P<major_name>.+?)\s+"
    r"(?P<material>\d+(?:\.\d+)?)\s+"
    r"(?P<assessment>\d+(?:\.\d+)?)\s+"
    r"(?P<final>\d+(?:\.\d+)?)\s*$"
)


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_collapse_spaces(p) for p in parts) if part)


def parse_doctor_line(line: str, *, source_url: str = SOURCE_URL, title: str = TITLE) -> dict[str, Any] | None:
    match = DOCTOR_ROW_PATTERN.match(_collapse_spaces(line))
    if not match:
        return None
    remarks = _remarks(
        f"material_score {match.group('material')}",
        f"assessment_score {match.group('assessment')}",
        f"final_score {match.group('final')}",
    )
    return crawler._clean_record(
        {
            "school_name": "山东中医药大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": _collapse_spaces(match.group("name")),
            "student_id": match.group("student_id"),
            "college": _collapse_spaces(match.group("college")),
            "admission_major": _collapse_spaces(f"{match.group('major_code')} {match.group('major_name')}"),
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


def curate_records(pdf_path: Path = PDF_PATH) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    unparsed: list[str] = []
    for line in _extract_pdf_lines(pdf_path):
        if not re.match(r"^\s*104419\d{4}\s+", line):
            continue
        record = parse_doctor_line(line)
        if record is None:
            unparsed.append(line)
            continue
        rows.append(record)
    if unparsed:
        raise ValueError(f"Unparsed SDUTCM doctor rows: {len(unparsed)}")
    rows.sort(
        key=lambda row: (
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
    notes = [
        "batch202_sdutcm_doctor_pdf_curated: reparsed official SDUTCM 2026 full-time doctoral admission PDF.",
        "Generic parser did not cover this doctoral table layout; this parser extracts registration id, college, name, major, material score, assessment score, and final score.",
        f"rows={len(rows)}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
