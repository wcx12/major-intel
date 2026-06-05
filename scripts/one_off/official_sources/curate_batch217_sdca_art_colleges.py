from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch217_sdca_art_colleges")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch217_sdca_art_colleges_curated")

MSXY_PDF = RAW_DIR / "msxy.sdca.edu.cn" / "5e6220db16b839ae.pdf"
MSXY_PAGE_URL = "https://msxy.sdca.edu.cn/info/1031/5793.htm"
MSXY_SOURCE_URL = (
    "https://msxy.sdca.edu.cn/system/_content/download.jsp?"
    "urltype=news.DownloadAttachUrl&owner=1302396566&wbfileid=1B0D6EB37D9B0E7C74800362ACADB78F"
)
MSXY_TITLE = "美术学院2026年推荐免试攻读硕士研究生资格名单公示.pdf"

MSXY_ROW_RE = re.compile(
    r"^(?P<student_id>\d{9})\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<gender>男|女)\s+"
    r"(?P<political>.+?)\s+"
    r"(?P<major_code>\d{6}[A-Z]?)\s+"
    r"(?P<major_name>绘画|雕塑|中国画|美术学)\s+"
    r"(?P<details>.+?)\s+是$"
)
MAJOR_GROUPS = (
    "油画第一工作室",
    "油画第二工作室",
    "油画第三工作室",
    "油画第五工作室",
    "版画",
    "壁画",
    "美术教育",
    "实验艺术",
    "工笔画",
    "山水花鸟画",
    "意笔人物画",
)


def _collapse_spaces(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_collapse_spaces(part) for part in parts) if part)


def _extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _iter_msxy_records(pdf_path: Path) -> list[str]:
    records: list[str] = []
    buffer = ""
    for raw_line in _extract_pdf_text(pdf_path).splitlines():
        line = _collapse_spaces(raw_line)
        if (
            not line
            or line.startswith("美术学院")
            or line.startswith("学号")
            or line.startswith("专业成绩靠前")
            or line.startswith("学生未被推荐")
            or line == "原因"
            or line == "无"
        ):
            continue
        if re.match(r"^\d{9}\s+", line):
            if buffer:
                records.append(_collapse_spaces(buffer))
            buffer = line
        elif buffer and not buffer.endswith(" 是"):
            buffer = f"{buffer} {line}"
    if buffer:
        records.append(_collapse_spaces(buffer))
    return records


def _major_group(details: str) -> str:
    normalized = _collapse_spaces(details)
    normalized = re.sub(r"山水花鸟\d+\s*画", "山水花鸟画", normalized)
    for group in MAJOR_GROUPS:
        if group in normalized:
            return group
    return ""


def parse_msxy_record(
    text: str,
    *,
    ranking: int,
    source_url: str = MSXY_SOURCE_URL,
    title: str = MSXY_TITLE,
) -> dict[str, Any] | None:
    match = MSXY_ROW_RE.match(_collapse_spaces(text))
    if not match:
        return None
    major_code = match.group("major_code")
    major_name = match.group("major_name")
    details = match.group("details")
    group = _major_group(details)
    return crawler._clean_record(
        {
            "school_name": "山东艺术学院",
            "year": 2026,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "college": "美术学院",
            "undergraduate_major": f"{major_code} {major_name}",
            "major": major_name,
            "ranking": str(ranking),
            "remarks": _remarks(
                f"gender {match.group('gender')}",
                f"political_status {match.group('political')}",
                f"undergraduate_major_code {major_code}",
                f"major_group {group}" if group else "",
                "recommendation_status 是",
            ),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def curate_msxy_pdf(pdf_path: Path = MSXY_PDF) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for text in _iter_msxy_records(pdf_path):
        record = parse_msxy_record(text, ranking=len(rows) + 1)
        if record is not None:
            rows.append(record)
    return rows


def curate_records(*, msxy_pdf: Path = MSXY_PDF) -> list[dict[str, Any]]:
    return curate_msxy_pdf(msxy_pdf)


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch217_sdca_art_colleges_curated: normalized Shandong University of Arts Fine Arts School 2026 recommendation qualification PDF.",
        "MSXY: reparsed PDF text to drop header fragments and keep only rows whose recommendation column is 是.",
        "Drama and Art Management pages were image/scanned embedded lists; retained as raw evidence but not transcribed in this batch.",
        f"rows={len(rows)}",
        f"msxy_page={MSXY_PAGE_URL}",
        f"msxy_pdf={MSXY_SOURCE_URL}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
