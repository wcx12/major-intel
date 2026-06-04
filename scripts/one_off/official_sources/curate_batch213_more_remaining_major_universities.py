from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch213_more_remaining_major_universities")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch213_more_remaining_major_universities_curated")

WHUT_PDF = RAW_DIR / "stle.whut.edu.cn" / "1f294b0c26383986.pdf"
WHUT_PAGE_URL = "https://stle.whut.edu.cn/yjsjx/zsxx/202512/t20251223_1375280.shtml"
WHUT_SOURCE_URL = "https://stle.whut.edu.cn/yjsjx/zsxx/202512/P020251223575245846523.pdf"
WHUT_TITLE = "交通与物流工程学院2026年接收推荐免试攻读硕士学位和直接攻读博士学位研究生拟录取名单公示.pdf"

WHUT_ROW_RE = re.compile(
    r"^(?P<name>\S+)\s+"
    r"(?P<college>交通与物流工程学院)\s+"
    r"(?P<admission_type>直博生|硕士)\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<major_name>.+?)\s+"
    r"(?P<status>拟录取)$"
)


def _collapse_spaces(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_collapse_spaces(part) for part in parts) if part)


def _extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_whut_line(
    line: str,
    *,
    ranking: int,
    source_url: str = WHUT_SOURCE_URL,
    title: str = WHUT_TITLE,
) -> dict[str, Any] | None:
    match = WHUT_ROW_RE.match(_collapse_spaces(line))
    if not match:
        return None
    major_code = match.group("major_code")
    major_name = match.group("major_name")
    return crawler._clean_record(
        {
            "school_name": "武汉理工大学",
            "year": 2026,
            "document_type": "incoming_recommendation_admission_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "college": match.group("college"),
            "major": major_code,
            "admission_major": f"{major_code} {major_name}",
            "ranking": str(ranking),
            "remarks": _remarks(
                f"admission_type {match.group('admission_type')}",
                f"list_status {match.group('status')}",
            ),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def curate_whut_pdf(pdf_path: Path = WHUT_PDF) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in _extract_pdf_text(pdf_path).splitlines():
        record = parse_whut_line(raw_line, ranking=len(rows) + 1)
        if record is not None:
            rows.append(record)
    return rows


def curate_records(*, whut_pdf: Path = WHUT_PDF) -> list[dict[str, Any]]:
    return curate_whut_pdf(whut_pdf)


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch213_more_remaining_major_universities_curated: normalized WHUT School of Transportation and Logistics 2026 recommendation admission PDF.",
        "WHUT: corrected the crawler's URL-date year inference from 2025 to title year 2026 and mapped the list to incoming_recommendation_admission_list.",
        "NENU public query links now return 'not yet announced'; PUMC formal-result system currently shows 2027 empty table; CUPL returned a JavaScript challenge page, so these were retained as crawl evidence only.",
        f"rows={len(rows)}",
        f"whut_page={WHUT_PAGE_URL}",
        f"whut_pdf={WHUT_SOURCE_URL}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
