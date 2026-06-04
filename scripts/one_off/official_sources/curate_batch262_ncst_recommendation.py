from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch262_ncst_recommendation/"
    "yjsxy.ncst.edu.cn/bc696a7d17f86a25.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch262_ncst_recommendation_curated"
)

SCHOOL_NAME = "华北理工大学"
YEAR = 2026
DOCUMENT_TYPE = "incoming_recommendation_admission_list"
ROUTE = "recommendation_exemption"
TITLE = "华北理工大学2026年接收推免研究生复试及拟录取名单公示（第一批次）"
SOURCE_URL = "https://yjsxy.ncst.edu.cn/atm/7/20250926144423420.pdf"

ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<person_name>[\u4e00-\u9fff·]{2,8})\s+"
    r"(?P<gender>[男女])\s+"
    r"(?P<score>\d+(?:\.\d+)?)\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<major_name>[\u4e00-\u9fff（）()A-Za-z]+)\s+"
    r"(?P<undergraduate_school>[\u4e00-\u9fff（）()A-Za-z]+)\s+"
    r"(?P<undergraduate_major>[\u4e00-\u9fff（）()A-Za-z]+)\s+"
    r"(?P<status>拟录取|缺考|拒绝待录取|因差额未录取|被其他学校待)\s*$"
)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean(part) for part in parts) if part)


def _parse_rows(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        match = ROW_RE.match(_clean(raw_line))
        if not match or match.group("status") != "拟录取":
            continue

        major_code = match.group("major_code")
        major_name = match.group("major_name")
        rows.append(
            crawler._clean_record(
                {
                    "school_name": SCHOOL_NAME,
                    "year": YEAR,
                    "document_type": DOCUMENT_TYPE,
                    "route": ROUTE,
                    "person_name": match.group("person_name"),
                    "undergraduate_school": match.group("undergraduate_school"),
                    "undergraduate_major": match.group("undergraduate_major"),
                    "college": "",
                    "major": major_name,
                    "admission_major": f"{major_code} {major_name}",
                    "ranking": match.group("ranking"),
                    "remarks": _remarks(
                        f"综合考核成绩: {match.group('score')}",
                        f"性别: {match.group('gender')}",
                        "录取状态: 拟录取",
                    ),
                    "source_url": SOURCE_URL,
                    "title": TITLE,
                    "needs_review": False,
                }
            )
        )
    return rows


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    return _parse_rows(text)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
