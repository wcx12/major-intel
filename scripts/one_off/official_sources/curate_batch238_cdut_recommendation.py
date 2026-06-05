from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch238_cdut_recommendation"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch238_cdut_recommendation_curated"
)

SCHOOL_NAME = "成都理工大学"
YEAR = 2025
SOURCE_URL = "https://cist.cdut.edu.cn/__local/1/3C/A8/76104FAC3A34A88B53467FDBB02_B5BB8255_2AFE1.pdf"
SOURCE_TITLE = "成都理工大学2025年推荐免试研究生拟录取名单"
SOURCE_PAGE = "https://gra.cdut.edu.cn/info/1007/3934.htm"
COLLEGE = "计算机与网络安全学院（示范性软件学院）"

ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<person_name>.+?)\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<major_name>\S+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<degree_category>硕士)\s*$"
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _clean_name(value: str) -> str:
    return re.sub(r"\s+", "", _clean_text(value))


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


def _record(parsed: dict[str, str]) -> dict[str, Any]:
    admission_major = f"{parsed['major_code']} {_clean_text(parsed['major_name'])}"
    note = "研究生支教团" if parsed["ranking"] == "1" else ""
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": _clean_name(parsed["person_name"]),
            "college": COLLEGE,
            "major": admission_major,
            "admission_major": admission_major,
            "ranking": parsed["ranking"],
            "source_url": SOURCE_URL,
            "title": SOURCE_TITLE,
            "needs_review": False,
            "remarks": _remarks(
                f"reexam_score {parsed['reexam_score']}",
                f"degree_category {parsed['degree_category']}",
                note,
                f"source_page {SOURCE_PAGE}",
            ),
        }
    )


def _parse_pdf(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = ROW_RE.match(line)
        if match:
            rows.append(_record(match.groupdict(default="")))
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
