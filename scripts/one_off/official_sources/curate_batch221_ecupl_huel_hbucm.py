from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch221_ecupl_huel_hbucm_curated")

DEFAULT_ECUPL_PDF_PATH = RAW_DIR / "gs.ecupl.edu.cn" / "c66f3bdcd0d339a0.pdf"
DEFAULT_HUEL_HTML_PATH = RAW_DIR / "yjs.huel.edu.cn" / "88b89bc9f0ea6a27.htm"
DEFAULT_HBUCM_HTML_PATH = RAW_DIR / "yjs.hbucm.edu.cn" / "87386a149c83bf78.htm"

ECUPL_SOURCE_URL = (
    "https://gs.ecupl.edu.cn/_upload/article/files/26/cb/dcd083e548c78ce11fb84064ffca/"
    "60fc7d5b-7999-4ce4-8f70-00931a2ade78.pdf"
)
ECUPL_TITLE = "华东政法大学2025年推荐免试攻读硕士学位研究生拟录取名单公示"
HUEL_SOURCE_URL = "https://yjs.huel.edu.cn/info/1007/4302.htm"
HUEL_TITLE = "河南财经政法大学2025年推免生拟录取名单公示"
HBUCM_SOURCE_URL = "https://yjs.hbucm.edu.cn/info/1029/11261.htm"
HBUCM_TITLE = "湖北中医药大学2026年博士研究生补录名单公示"

ECUPL_COLLEGES = {
    "法律学院",
    "经济法学院",
    "国际金融法律学院",
    "国际法学院",
    "刑事法学院",
    "知识产权学院",
    "商学院",
    "政府管理学院",
    "韬奋新闻传播学院",
    "社会发展学院",
    "外语学院",
    "法律硕士管理中心",
    "文伯书院",
    "中国法治战略研究院",
    "涉外法治学院",
    "纪检监察学院",
}
WATERMARK_TOKENS = set("华东政法大学研招未经许可严禁转载")
SCORE_RE = re.compile(r"\d{2,3}(?:\.\d+)?")
NAME_RE = re.compile(r"[\u4e00-\u9fff]{1,5}\*[\u4e00-\u9fff]{0,5}")


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _compact(value: Any) -> str:
    return re.sub(r"\s+", "", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _extract_pdf_raw_text(pdf_path: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-raw", str(pdf_path), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return crawler._decode_pdftotext_output(completed.stdout)


def _is_name_token(value: str) -> bool:
    return bool(NAME_RE.fullmatch(value or ""))


def _is_ignorable_ecupl_line(line: str) -> bool:
    clean = line.replace("\f", "").strip()
    if not clean:
        return True
    if clean.startswith("华东政法大学2025年硕士研究生推免生拟录取名单"):
        return True
    if clean.startswith("姓名 毕业院校 录取院系"):
        return True
    if clean in WATERMARK_TOKENS:
        return True
    if set(clean.replace(" ", "")) <= WATERMARK_TOKENS and len(clean.replace(" ", "")) <= 12:
        return True
    return False


def _ecupl_candidate_chunks(text: str) -> list[list[str]]:
    chunks: list[list[str]] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.replace("\f", "").strip()
        if _is_ignorable_ecupl_line(line):
            continue
        first = line.split()[0] if line.split() else ""
        if _is_name_token(first):
            if current:
                chunks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        chunks.append(current)
    return chunks


def _parse_ecupl_chunk(chunk: list[str], ranking: int) -> dict[str, Any] | None:
    tokens = " ".join(chunk).split()
    if not tokens or not _is_name_token(tokens[0]):
        return None
    score_index = -1
    for index, token in enumerate(tokens[1:], start=1):
        if SCORE_RE.fullmatch(token):
            score_index = index
    if score_index < 0:
        return None

    person_name = tokens[0]
    before_score = tokens[1:score_index]
    after_score = tokens[score_index + 1 :]
    score = tokens[score_index]

    college_index = next((index for index, token in enumerate(before_score) if token in ECUPL_COLLEGES), -1)
    if college_index <= 0 or college_index >= len(before_score) - 1:
        return None

    undergraduate_school = "".join(before_score[:college_index])
    college = before_score[college_index]
    major_and_direction = before_score[college_index + 1 :]
    major = major_and_direction[0]
    direction = "".join(major_and_direction[1:])
    note = "".join(after_score)

    return crawler._clean_record(
        {
            "school_name": "华东政法大学",
            "year": 2025,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": person_name,
            "undergraduate_school": undergraduate_school,
            "college": college,
            "major": major,
            "admission_major": _clean_text(f"{major} {direction}"),
            "ranking": str(ranking),
            "remarks": _remarks(f"interview_score {score}", note),
            "source_url": ECUPL_SOURCE_URL,
            "title": ECUPL_TITLE,
            "needs_review": False,
        }
    )


def curate_ecupl_pdf(pdf_path: Path = DEFAULT_ECUPL_PDF_PATH) -> list[dict[str, Any]]:
    text = _extract_pdf_raw_text(pdf_path)
    rows: list[dict[str, Any]] = []
    for chunk in _ecupl_candidate_chunks(text):
        record = _parse_ecupl_chunk(chunk, len(rows) + 1)
        if record:
            rows.append(record)
    return rows


def curate_huel_html(html_path: Path = DEFAULT_HUEL_HTML_PATH) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows: list[dict[str, Any]] = []
    for tr in soup.find_all("tr"):
        values = [_compact(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
        if len(values) < 5 or values[0] == "姓名":
            continue
        person_name, major_code, major_name, study_mode, score = values[:5]
        if not person_name or not major_code.isdigit():
            continue
        rows.append(
            crawler._clean_record(
                {
                    "school_name": "河南财经政法大学",
                    "year": 2025,
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": person_name,
                    "major": major_code,
                    "admission_major": major_name,
                    "remarks": _remarks(f"study_mode {study_mode}", f"interview_score {score}"),
                    "source_url": HUEL_SOURCE_URL,
                    "title": HUEL_TITLE,
                    "needs_review": False,
                }
            )
        )
    return rows


def curate_hbucm_html(html_path: Path = DEFAULT_HBUCM_HTML_PATH) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    text = _clean_text(soup.get_text(" ", strip=True))
    match = re.search(
        r"补录1名考生(?P<name>[\u4e00-\u9fff]+)（考生编号：(?P<student_id>\d+)，专业代码及名称：(?P<major_code>\d+)(?P<major_name>[^）]+)）",
        text,
    )
    if not match:
        return []
    major_code = match.group("major_code")
    major_name = _compact(match.group("major_name"))
    return [
        crawler._clean_record(
            {
                "school_name": "湖北中医药大学",
                "year": 2026,
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name": match.group("name"),
                "student_id": match.group("student_id"),
                "major": major_code,
                "admission_major": _clean_text(f"{major_code} {major_name}"),
                "remarks": "admission_status 补录",
                "source_url": HBUCM_SOURCE_URL,
                "title": HBUCM_TITLE,
                "needs_review": False,
            }
        )
    ]


def curate_records(
    *,
    ecupl_pdf_path: Path = DEFAULT_ECUPL_PDF_PATH,
    huel_html_path: Path = DEFAULT_HUEL_HTML_PATH,
    hbucm_html_path: Path = DEFAULT_HBUCM_HTML_PATH,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(curate_ecupl_pdf(ecupl_pdf_path))
    rows.extend(curate_huel_html(huel_html_path))
    rows.extend(curate_hbucm_html(hbucm_html_path))
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch221_ecupl_huel_hbucm_curated: repaired ECUPL recommendation PDF extraction with pdftotext -raw and HTML/body parsing for HUEL/HBUCM.",
        "The ECUPL public notice states 349 recommended-admission candidates; curated output keeps 349 ECUPL rows plus 1 HUEL row and 1 HBUCM doctoral supplement row.",
        "Skipped the ECUPL 2025 non-recommendation PDF seed because the direct search-indexed URL returned HTTP 404 during live crawl.",
        f"rows={len(rows)}",
        f"source={ECUPL_SOURCE_URL}",
        f"source={HUEL_SOURCE_URL}",
        f"source={HBUCM_SOURCE_URL}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
