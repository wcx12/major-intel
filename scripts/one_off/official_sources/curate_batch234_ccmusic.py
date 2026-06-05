from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch234_ccmusic")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch234_ccmusic_curated")

SOURCE_URL = "https://yjsy.ccmusic.edu.cn/docs/2026-05/eac5066c44af43d596ea79dbb6833684.pdf"
SOURCE_TITLE = "中国音乐学院2026年面向港澳台地区研究生招生考试拟录取名单"
PDF_NAME = "a9b3732bc5dd6dd6.pdf"

ROW_RE = re.compile(
    r"^\s*(?P<student_id>\d{15})\s+"
    r"(?P<degree_level>\S+)\s+"
    r"(?P<college>\S+)\s+"
    r"(?P<admission_major>.+?)\s+"
    r"(?P<person_name>[\u4e00-\u9fff·]{2,})\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<study_mode>\S+)\s+"
    r"(?P<admission_category>\S+)"
    r"(?:\s+(?P<note>.+?))?\s*$"
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _pdf_text(path: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.splitlines()


def _record(parsed: dict[str, str]) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": "中国音乐学院",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "source_url": SOURCE_URL,
            "title": SOURCE_TITLE,
            "person_name": parsed["person_name"],
            "student_id": parsed["student_id"],
            "college": parsed["college"],
            "admission_major": parsed["admission_major"],
            "needs_review": False,
            "remarks": _remarks(
                f"degree_level {parsed['degree_level']}",
                f"study_mode {parsed['study_mode']}",
                f"admission_category {parsed['admission_category']}",
                f"total_score {parsed['total_score']}",
                f"initial_score {parsed['initial_score']}",
                f"reexam_score {parsed['reexam_score']}",
                parsed.get("note", ""),
            ),
        }
    )


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    matches = list(raw_dir.glob(f"**/{PDF_NAME}"))
    if not matches:
        return []
    rows: list[dict[str, Any]] = []
    for line in _pdf_text(matches[0]):
        match = ROW_RE.match(line)
        if match:
            rows.append(_record(match.groupdict(default="")))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
