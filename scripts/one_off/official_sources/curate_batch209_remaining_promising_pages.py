from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch209_remaining_promising_pages_curated")

HLJ_PDF = RAW_DIR / "yjsy.hlju.edu.cn" / "461b15ecfd01f1ec.pdf"
CQNU_PDF = RAW_DIR / "jwc.cqnu.edu.cn" / "8c281b25ccf76a48.pdf"
WTU_HTML = RAW_DIR / "fashion.wtu.edu.cn" / "d647428c0b6553a1.htm"
WHSU_HTML = RAW_DIR / "jtxy.whsu.edu.cn" / "56217fa14bad29d6.htm"

HLJ_SOURCE_URL = "https://yjsy.hlju.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1784155087&wbfileid=16028760"
CQNU_SOURCE_URL = "https://jwc.cqnu.edu.cn/__local/B/F6/4A/74BE256853C47E3593F9E096CEF_C5029819_BF71A.pdf"
WTU_SOURCE_URL = "https://fashion.wtu.edu.cn/info/1006/14611.htm"
WHSU_SOURCE_URL = "https://jtxy.whsu.edu.cn/info/1327/8401.htm"

HLJ_TITLE = "黑龙江大学2026年硕士研究生拟录取公示"
CQNU_TITLE = "重庆师范大学推荐2026届优秀本科毕业生免试攻读硕士学位研究生名单公示"
WTU_TITLE = "武汉纺织大学服装学院拟推荐2026届毕业生免试攻读硕士研究生名单公示"
WHSU_TITLE = "武汉体育学院竞技体育学院2026届优秀应届本科生毕业生免试攻读硕士学位研究生拟推荐名单公示"

HLJ_RECORD_RE = re.compile(
    r"^(?P<school_record_no>226\d{4})\s+"
    r"(?P<name>.+?)\s+"
    r"(?P<candidate_id>102126\d{9})\s+"
    r"(?P<college>\d{3}\.[^\s]+)\s+"
    r"(?P<major>\d{6}[A-Z]?\d?\.[^\s]+)\s+"
    r"(?P<direction>\d{2}\..+?)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+免试\s+"
    r"(?P<retest_score>\d+(?:\.\d+)?)\s+"
    r"(?P<final_score>\d+(?:\.\d+)?)\s+"
    r"(?P<admission_category>非定向|定向)\s+推免生$"
)


def _collapse_spaces(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_collapse_spaces(part) for part in parts) if part)


def _extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def parse_hlju_record(
    text: str,
    *,
    source_url: str = HLJ_SOURCE_URL,
    title: str = HLJ_TITLE,
) -> dict[str, Any] | None:
    match = HLJ_RECORD_RE.match(_collapse_spaces(text))
    if not match:
        return None
    major = match.group("major")
    direction = match.group("direction")
    return crawler._clean_record(
        {
            "school_name": "黑龙江大学",
            "year": 2026,
            "document_type": "incoming_recommendation_admission_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "student_id": match.group("candidate_id"),
            "college": match.group("college"),
            "major": major,
            "admission_major": f"{major} {direction}",
            "remarks": _remarks(
                f"school_record_no {match.group('school_record_no')}",
                f"study_mode {match.group('study_mode')}",
                "initial_total 免试",
                f"retest_score {match.group('retest_score')}",
                f"final_score {match.group('final_score')}",
                f"admission_category {match.group('admission_category')}",
                "remark 推免生",
            ),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _curate_hlju(pdf_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    buffer = ""
    for raw_line in _extract_pdf_text(pdf_path).splitlines():
        line = _collapse_spaces(raw_line)
        if not line:
            continue
        if re.match(r"^226\d{4}\b", line):
            buffer = line
        elif buffer:
            buffer = _collapse_spaces(f"{buffer} {line}")
        if buffer and "推免生" in buffer:
            record = parse_hlju_record(buffer)
            if record is not None:
                rows.append(record)
            buffer = ""
    return rows


def parse_cqnu_ranked_line(
    line: str,
    *,
    category: str,
    source_url: str = CQNU_SOURCE_URL,
    title: str = CQNU_TITLE,
) -> dict[str, Any] | None:
    text = _collapse_spaces(line)
    match = re.match(r"^(?P<seq>\d+)\s+(?P<college>\S+)\s+(?P<major>\S+)\s+(?P<name>\S+)\s+(?P<rank>\d+)$", text)
    if not match:
        return None
    return crawler._clean_record(
        {
            "school_name": "重庆师范大学",
            "year": 2026,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "college": match.group("college"),
            "major": match.group("major"),
            "ranking": match.group("rank"),
            "remarks": _remarks(f"sequence {match.group('seq')}", f"category {category}"),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def parse_cqnu_support_line(
    line: str,
    *,
    source_url: str = CQNU_SOURCE_URL,
    title: str = CQNU_TITLE,
) -> dict[str, Any] | None:
    text = _collapse_spaces(line)
    match = re.match(r"^(?P<college>\S+)\s+(?P<major>\S+)\s+(?P<name>\S+)\s+(?P<rank>\d+)$", text)
    if not match or match.group("college") == "院系所名称":
        return None
    return crawler._clean_record(
        {
            "school_name": "重庆师范大学",
            "year": 2026,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "college": match.group("college"),
            "major": match.group("major"),
            "ranking": match.group("rank"),
            "remarks": "category 研究生支教团",
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _curate_cqnu(pdf_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    category = ""
    for raw_line in _extract_pdf_text(pdf_path).splitlines():
        line = _collapse_spaces(raw_line)
        if not line:
            continue
        if "普通类推免学生公示名单" in line:
            category = "普通类"
            continue
        if "农村硕士计划推免学生公示名单" in line:
            category = "农村硕士计划"
            continue
        if "研究生支教团推免学生公示名单" in line:
            category = "研究生支教团"
            continue
        if category in {"普通类", "农村硕士计划"}:
            record = parse_cqnu_ranked_line(line, category=category)
        elif category == "研究生支教团":
            record = parse_cqnu_support_line(line)
        else:
            record = None
        if record is not None:
            rows.append(record)
    return rows


def _html_table_rows(html_path: Path) -> list[list[str]]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows: list[list[str]] = []
    for tr in soup.find_all("tr"):
        cells = [_collapse_spaces(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return rows


def _curate_wtu(html_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cells in _html_table_rows(html_path):
        if len(cells) != 5 or cells[0] == "序号":
            continue
        sequence, student_id, name, major, college_rank = cells
        rows.append(
            crawler._clean_record(
                {
                    "school_name": "武汉纺织大学",
                    "year": 2026,
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": name,
                    "student_id": student_id,
                    "college": "服装学院",
                    "major": major,
                    "ranking": college_rank,
                    "remarks": f"sequence {sequence}",
                    "source_url": WTU_SOURCE_URL,
                    "title": WTU_TITLE,
                    "needs_review": False,
                }
            )
        )
    return rows


def _curate_whsu(html_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cells in _html_table_rows(html_path):
        if len(cells) != 4 or cells[0] == "专业":
            continue
        major, recommendation_type, name, rank = cells
        rows.append(
            crawler._clean_record(
                {
                    "school_name": "武汉体育学院",
                    "year": 2026,
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": name,
                    "college": "竞技体育学院",
                    "major": major,
                    "ranking": rank,
                    "remarks": f"recommendation_type {recommendation_type}",
                    "source_url": WHSU_SOURCE_URL,
                    "title": WHSU_TITLE,
                    "needs_review": False,
                }
            )
        )
    return rows


def curate_records(
    *,
    hlj_pdf: Path = HLJ_PDF,
    cqnu_pdf: Path = CQNU_PDF,
    wtu_html: Path = WTU_HTML,
    whsu_html: Path = WHSU_HTML,
) -> list[dict[str, Any]]:
    rows = [*_curate_hlju(hlj_pdf), *_curate_cqnu(cqnu_pdf), *_curate_wtu(wtu_html), *_curate_whsu(whsu_html)]
    rows.sort(
        key=lambda row: (
            str(row.get("school_name") or ""),
            str(row.get("source_url") or ""),
            str(row.get("college") or ""),
            str(row.get("major") or ""),
            str(row.get("ranking") or ""),
            str(row.get("person_name") or ""),
            str(row.get("student_id") or ""),
        )
    )
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    counts: dict[str, int] = {}
    for row in rows:
        school = str(row.get("school_name") or "")
        counts[school] = counts.get(school, 0) + 1
    notes = [
        "batch209_remaining_promising_pages_curated: reparsed HljU PDF, CQNU PDF, WTU HTML, and WHSU HTML.",
        "Dropped SDUT page without static list, TUST 302 failure, WTU backup ranking table, and WHSU implementation-rule table noise.",
        f"rows={len(rows)}",
        f"counts={counts}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv"), "counts": counts})


if __name__ == "__main__":
    main()
