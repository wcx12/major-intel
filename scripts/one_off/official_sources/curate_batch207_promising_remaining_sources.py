from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch207_promising_remaining_sources")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch207_promising_remaining_sources_curated")

XSYU_PDF = RAW_DIR / "yjszs.xsyu.edu.cn" / "cd195ee12b216126.pdf"
XSYU_SOURCE_URL = (
    "https://yjszs.xsyu.edu.cn/system/_content/download.jsp?"
    "urltype=news.DownloadAttachUrl&owner=2074804384&wbfileid=5656530"
)
XSYU_TITLE = "西安石油大学2026年推免生拟录取名单公示"

XSYU_ROW_RE = re.compile(
    r"^(?P<name>\S+)\s+"
    r"(?P<college>\S+)\s+"
    r"(?P<code>\d{6})\s+"
    r"(?P<major>.+?)(?:\s+(?P<remark>直博生|支教团))?$"
)


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _extract_pdf_lines(pdf_path: Path) -> list[str]:
    lines: list[str] = []
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        lines.extend((page.extract_text() or "").splitlines())
    return [_collapse_spaces(line) for line in lines if _collapse_spaces(line)]


def parse_xsyu_pdf_line(
    line: str,
    *,
    source_url: str = XSYU_SOURCE_URL,
    title: str = XSYU_TITLE,
) -> dict[str, Any] | None:
    text = _collapse_spaces(line)
    match = XSYU_ROW_RE.match(text)
    if not match:
        return None
    code = match.group("code")
    major_name = _collapse_spaces(match.group("major"))
    return crawler._clean_record(
        {
            "school_name": "西安石油大学",
            "year": 2026,
            "document_type": "incoming_recommendation_admission_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "college": match.group("college"),
            "major": code,
            "admission_major": f"{code} {major_name}",
            "remarks": _collapse_spaces(match.group("remark") or ""),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def curate_records(*, xsyu_pdf: Path = XSYU_PDF) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    unparsed_candidate_lines: list[str] = []
    for line in _extract_pdf_lines(xsyu_pdf):
        if not re.search(r"\d{6}", line):
            continue
        record = parse_xsyu_pdf_line(line)
        if record is None:
            unparsed_candidate_lines.append(line)
            continue
        rows.append(record)
    if unparsed_candidate_lines:
        raise ValueError(f"Unparsed XSYU PDF rows: {len(unparsed_candidate_lines)}")
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch207_promising_remaining_sources_curated: parsed the school-level XSYU final 2026 recommendation exemption admission PDF.",
        "The earlier economics college preliminary receiving table and chemistry page were kept as raw evidence but not merged because the school-level final PDF is available.",
        "NEEPU returned 404, NJUST returned 410, and ZCMU returned 412 during this run.",
        f"rows={len(rows)}",
        f"direct_doctor_rows={sum(row.get('remarks') == '直博生' for row in rows)}",
        f"support_team_rows={sum(row.get('remarks') == '支教团' for row in rows)}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
