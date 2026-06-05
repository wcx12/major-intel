from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch313_cwnu_nenu_probe/"
    "yjsy.cwnu.edu.cn"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch313_cwnu_admission_curated"
)

SCHOOL_NAME = "西华师范大学"
YEAR = 2025
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"

FIRST_BATCH_SOURCE_PAGE = "https://yjsy.cwnu.edu.cn/info/1014/16892.htm"
SECOND_BATCH_SOURCE_PAGE = "https://yjsy.cwnu.edu.cn/info/1014/17022.htm"
DOCTOR_SOURCE_PAGE = "https://yjsy.cwnu.edu.cn/info/1014/17372.htm"

PDF_ROW_ID_RE = re.compile(r"\b(?P<student_id>\d{15})\b")
RIGHT_RE = re.compile(
    r"^\s*(?P<person_name>\S+)\s+"
    r"(?P<initial_score>\d+(?:\.\d+)?)\s+"
    r"(?P<interview_score>\d+(?:\.\d+)?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)\s+"
    r"(?P<admission_category>非定向|定向)"
    r"(?:\s+(?P<note>.+))?\s*$"
)
LEFT_RE = re.compile(
    r"^\s*(?:(?P<college>.*?)\s+)?"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<body>.+?)"
    r"(?P<learning_mode>非全日制|全日制)\s*$"
)

NOISE_FRAGMENTS = (
    "西华师范大学2025年硕士研究生拟录取名单公示",
    "学院名称",
    "专业名称",
    "研究方向",
    "考生编号",
    "初试成",
    "复试成",
    "录取类",
    "总成绩",
)


@dataclass(frozen=True)
class PdfSource:
    path: Path
    source_url: str
    source_page: str
    title: str


PDF_SOURCES = [
    PdfSource(
        path=RAW_DIR / "9a15ff5d47c8ab2f.pdf",
        source_url=(
            "https://yjsy.cwnu.edu.cn/system/_content/download.jsp?"
            "urltype=news.DownloadAttachUrl&owner=1514373409&wbfileid=00C2D4C07C9B7982EC071FBCFCCFA53B"
        ),
        source_page=FIRST_BATCH_SOURCE_PAGE,
        title="西华师范大学2025年硕士研究生拟录取名单公示",
    ),
    PdfSource(
        path=RAW_DIR / "8ecba832bc90fdcb.pdf",
        source_url=(
            "https://yjsy.cwnu.edu.cn/system/_content/download.jsp?"
            "urltype=news.DownloadAttachUrl&owner=1514373409&wbfileid=F95E88AA4D8F2CE21F1AB4D8695B1F7B"
        ),
        source_page=SECOND_BATCH_SOURCE_PAGE,
        title="西华师范大学2025年硕士研究生拟录取名单公示（第二批）",
    ),
]

DOCTOR_HTML_PATH = RAW_DIR / "9d3840ac777a35a9.htm"
DOCTOR_TITLE = "西华师范大学2025年博士研究生拟录取名单公示"


def curate_records() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in PDF_SOURCES:
        text = crawler._extract_pdf_text_with_pdftotext(source.path)
        rows.extend(curate_pdf_records(text, source, starting_rank=len(rows) + 1))
    if DOCTOR_HTML_PATH.exists():
        html = DOCTOR_HTML_PATH.read_text(encoding="utf-8", errors="ignore")
        rows.extend(curate_doctor_html_records(html, starting_rank=len(rows) + 1))
    return rows


def curate_pdf_records(raw_text: str, source: PdfSource, *, starting_rank: int = 1) -> list[dict[str, Any]]:
    lines = raw_text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    rows: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not PDF_ROW_ID_RE.search(line):
            continue
        parsed = _parse_pdf_line(line, lines, index)
        if not parsed:
            continue
        parsed["ranking"] = str(starting_rank + len(rows))
        rows.append(_pdf_record_from_data(parsed, source))
    return rows


def curate_doctor_html_records(raw_html: str, *, starting_rank: int = 1) -> list[dict[str, Any]]:
    soup = BeautifulSoup(raw_html, "html.parser")
    rows: list[dict[str, Any]] = []
    for table in soup.find_all("table"):
        for cells in _iter_table_cells(table):
            if len(cells) < 9 or not cells[0].isdigit():
                continue
            rows.append(_doctor_record_from_cells(cells, starting_rank + len(rows)))
    return rows


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\x0c", " ")).strip()


def _is_noise_line(line: str) -> bool:
    value = _clean(line)
    if not value:
        return True
    if PDF_ROW_ID_RE.search(value):
        return True
    return any(fragment in value for fragment in NOISE_FRAGMENTS)


def _parse_pdf_line(line: str, lines: list[str], index: int) -> dict[str, str] | None:
    id_match = PDF_ROW_ID_RE.search(line)
    if not id_match:
        return None

    left = line[: id_match.start()]
    right = line[id_match.end() :]
    right_match = RIGHT_RE.match(_clean(right))
    left_match = LEFT_RE.match(left)
    if not right_match or not left_match:
        return None

    context_college, context_secondary = _context_columns(lines, index)
    left_data = left_match.groupdict(default="")
    major, direction = _split_major_direction(left_data["body"], context_secondary)
    college = _best_college(left_data.get("college", ""), context_college)

    return {
        "college": college,
        "major_code": left_data["major_code"],
        "major": major,
        "research_direction": direction,
        "learning_mode": left_data["learning_mode"],
        "student_id": id_match.group("student_id"),
        **right_match.groupdict(default=""),
    }


def _context_columns(lines: list[str], index: int) -> tuple[str, str]:
    previous_line = _layout_line(lines[index - 1]) if index > 0 and not _is_noise_line(lines[index - 1]) else ""
    next_line = _layout_line(lines[index + 1]) if index + 1 < len(lines) and not _is_noise_line(lines[index + 1]) else ""
    previous_chunks = _layout_chunks(previous_line)
    next_chunks = _layout_chunks(next_line)

    college = ""
    secondary = ""
    if previous_chunks:
        college = previous_chunks[0]
        if next_chunks and _looks_like_college_suffix(next_chunks[0]):
            college += next_chunks[0]
        if len(previous_chunks) >= 2:
            secondary = previous_chunks[-1]
            if len(next_chunks) >= 2:
                secondary += next_chunks[-1]
    return _clean(college), _clean(secondary)


def _layout_line(line: str) -> str:
    return (line or "").replace("\x0c", " ").strip()


def _layout_chunks(line: str) -> list[str]:
    if not line:
        return []
    return [chunk.strip() for chunk in re.split(r"\s{2,}", line.strip()) if chunk.strip()]


def _looks_like_college_suffix(value: str) -> bool:
    return value in {"院", "系", "部", "所", "中心", "研究院"}


def _best_college(parsed_college: str, context_college: str) -> str:
    parsed = _clean(parsed_college)
    context = _clean(context_college)
    if context and (not parsed or context.startswith(parsed) or not _looks_complete_org(parsed)):
        return context
    return parsed


def _looks_complete_org(value: str) -> bool:
    return value.endswith(("学院", "研究院", "中心", "系", "部", "所"))


def _split_major_direction(body: str, context_secondary: str) -> tuple[str, str]:
    value = body.strip()
    if value.startswith("不区分研究方向"):
        return _clean(context_secondary), _clean(value)
    if "不区分研究方向" in value:
        major, _, tail = value.partition("不区分研究方向")
        return _clean(major), _clean("不区分研究方向" + tail)

    chunks = _layout_chunks(value)
    if len(chunks) >= 2:
        return _clean(chunks[0]), _clean(" ".join(chunks[1:]))
    return _clean(value), _clean(context_secondary)


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key}: {_clean(value)}" for key, value in parts if _clean(value))


def _pdf_record_from_data(data: dict[str, str], source: PdfSource) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": data["person_name"],
            "student_id": data["student_id"],
            "college": data["college"],
            "major": data["major"],
            "admission_major": data["major"],
            "ranking": data["ranking"],
            "remarks": _remarks(
                [
                    ("major_code", data.get("major_code", "")),
                    ("research_direction", data.get("research_direction", "")),
                    ("learning_mode", data.get("learning_mode", "")),
                    ("initial_score", data.get("initial_score", "")),
                    ("interview_score", data.get("interview_score", "")),
                    ("total_score", data.get("total_score", "")),
                    ("admission_category", data.get("admission_category", "")),
                    ("note", data.get("note", "")),
                    ("source_page", source.source_page),
                    ("source_person_name_masked", "true"),
                ]
            ),
            "source_url": source.source_url,
            "title": source.title,
            "needs_review": False,
        }
    )


def _iter_table_cells(table: Any) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = [_clean(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return rows


def _doctor_record_from_cells(cells: list[str], ranking: int) -> dict[str, Any]:
    source_ranking, name, major, direction, advisor, material_score, assessment_score, total_score, applicant_type = (
        cells[:9]
    )
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": name,
            "student_id": "",
            "college": "",
            "major": major,
            "admission_major": major,
            "ranking": source_ranking or str(ranking),
            "remarks": _remarks(
                [
                    ("degree_level", "博士"),
                    ("research_direction", direction),
                    ("advisor", advisor),
                    ("material_review_score", material_score),
                    ("comprehensive_assessment_score", assessment_score),
                    ("total_score", total_score),
                    ("applicant_type", applicant_type),
                    ("source_page", DOCTOR_SOURCE_PAGE),
                ]
            ),
            "source_url": DOCTOR_SOURCE_PAGE,
            "title": DOCTOR_TITLE,
            "needs_review": False,
        }
    )


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch313_cwnu_admission_curated: parsed Xihua Normal University 2025 master admission PDFs and doctoral admission HTML table.",
                "The master PDFs publish masked names; values are retained as officially published and public exports mask them again.",
                f"rows={len(rows)}",
                f"first_batch_page={FIRST_BATCH_SOURCE_PAGE}",
                f"second_batch_page={SECOND_BATCH_SOURCE_PAGE}",
                f"doctor_page={DOCTOR_SOURCE_PAGE}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
