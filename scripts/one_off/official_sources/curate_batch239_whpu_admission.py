from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch239_whpu_admission")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch239_whpu_admission_curated")

SCHOOL_NAME = "武汉轻工大学"
YEAR = 2025
SOURCE_URL = "https://xxgkw.whpu.edu.cn/__local/0/12/BB/9B2441AF41EA488AA5E18F18FF3_3E926D35_5B255.pdf"
SOURCE_TITLE = "武汉轻工大学2025年硕士研究生拟录取名单"

ROW_RE = re.compile(
    r"^\s*(?P<student_id>\d{12,})\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<major_code>[0-9A-ZJ]+)\s+"
    r"(?P<admission_major>\S+)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<college>.+?)\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)"
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


def _record(parsed: dict[str, str], ranking: int) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": parsed["person_name"],
            "student_id": parsed["student_id"],
            "college": parsed["college"],
            "major": parsed["major_code"],
            "admission_major": parsed["admission_major"],
            "ranking": str(ranking),
            "source_url": SOURCE_URL,
            "title": SOURCE_TITLE,
            "needs_review": False,
            "remarks": _remarks(
                f"initial_score {parsed['initial_score']}",
                f"reexam_score {parsed['reexam_score']}",
                f"total_score {parsed['total_score']}",
                f"study_mode {parsed['study_mode']}",
                parsed.get("note", ""),
            ),
        }
    )


def _parse_pdf(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = ROW_RE.match(line)
        if match:
            rows.append(_record(match.groupdict(default=""), len(rows) + 1))
    return rows


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    for path in sorted(raw_dir.glob("**/*.pdf")):
        text = _pdf_text(path)
        if SOURCE_TITLE in text:
            return _parse_pdf(text)
    return []


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
