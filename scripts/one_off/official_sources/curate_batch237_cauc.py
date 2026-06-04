from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch237_cauc")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch237_cauc_curated")

SCHOOL_NAME = "中国民航大学"
YEAR = 2025
ADMISSION_SOURCE_URL = (
    "https://www.cauc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1787525762&wbfileid=11984439"
)
RECOMMENDATION_SOURCE_URL = (
    "https://www.cauc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1787525762&wbfileid=11977509"
)
ADMISSION_TITLE = "中国民航大学2025年硕士研究生拟录取名单公示"
RECOMMENDATION_TITLE = "中国民航大学2025年接收推免生拟录取名单"

ADMISSION_ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<student_id>\d{12,})\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<admission_major>[0-9A-ZJ]+)\s+"
    r"(?P<college>\d{3})\s+"
    r"(?:(?P<initial_score>\d{2,3})\s+)?"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<admission_category>非定向|定向)\s+"
    r"(?P<admission_status>拟录取)"
    r"(?:\s+(?P<note>.+?))?\s*$"
)

RECOMMENDATION_ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<identity_id>[0-9*Xx]{10,})\s+"
    r"(?P<undergraduate_school>\S+)\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<college>\d{3}【[^】]+】)\s+"
    r"(?P<admission_major>[0-9A-ZJ]+【[^】]+】)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)"
    r"(?:\s+(?P<note>.+?))?\s*$"
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _pdf_text(path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def _admission_record(parsed: dict[str, str]) -> dict[str, Any] | None:
    if parsed["admission_status"] != "拟录取":
        return None
    admission_major = _clean_text(parsed["admission_major"])
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": parsed["person_name"],
            "student_id": parsed["student_id"],
            "college": parsed["college"],
            "major": admission_major,
            "admission_major": admission_major,
            "ranking": parsed["ranking"],
            "source_url": ADMISSION_SOURCE_URL,
            "title": ADMISSION_TITLE,
            "needs_review": False,
            "remarks": _remarks(
                f"initial_score {parsed.get('initial_score', '')}",
                f"reexam_score {parsed['reexam_score']}",
                f"total_score {parsed['total_score']}",
                f"study_mode {parsed['study_mode']}",
                f"admission_category {parsed['admission_category']}",
                f"admission_status {parsed['admission_status']}",
                parsed.get("note", ""),
            ),
        }
    )


def _recommendation_record(parsed: dict[str, str]) -> dict[str, Any]:
    admission_major = _clean_text(parsed["admission_major"])
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "incoming_recommendation_admission_list",
            "route": "recommendation_exemption",
            "person_name": parsed["person_name"],
            "student_id": parsed["identity_id"],
            "undergraduate_school": parsed["undergraduate_school"],
            "college": parsed["college"],
            "major": admission_major,
            "admission_major": admission_major,
            "ranking": parsed["ranking"],
            "source_url": RECOMMENDATION_SOURCE_URL,
            "title": RECOMMENDATION_TITLE,
            "needs_review": False,
            "remarks": _remarks(
                f"reexam_score {parsed['reexam_score']}",
                parsed.get("note", ""),
            ),
        }
    )


def _parse_admission_pdf(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = ADMISSION_ROW_RE.match(line)
        if not match:
            continue
        record = _admission_record(match.groupdict(default=""))
        if record is not None:
            rows.append(record)
    return rows


def _parse_recommendation_pdf(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = RECOMMENDATION_ROW_RE.match(line)
        if match:
            rows.append(_recommendation_record(match.groupdict(default="")))
    return rows


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    admission_rows: list[dict[str, Any]] = []
    recommendation_rows: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("**/*.pdf")):
        text = _pdf_text(path)
        if ADMISSION_TITLE in text:
            admission_rows = _parse_admission_pdf(text)
        elif RECOMMENDATION_TITLE in text:
            recommendation_rows = _parse_recommendation_pdf(text)
    return admission_rows + recommendation_rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
