from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import openpyxl
from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch210_remaining_promising_pages")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch210_remaining_promising_pages_curated")

GZNU_XLSX = RAW_DIR / "jwc.gznu.edu.cn" / "9f0c97d758546d21.xlsx"
CCUCM_PDF = RAW_DIR / "y.ccucm.edu.cn" / "9fb669f338a13013.pdf"

GZNU_SOURCE_URL = (
    "https://jwc.gznu.edu.cn/system/_content/download.jsp?"
    "urltype=news.DownloadAttachUrl&owner=846466970&wbfileid=1F65483464235CA6EC033608A96BEADF"
)
GZNU_PAGE_URL = "https://jwc.gznu.edu.cn/info/2002/89615.htm"
GZNU_TITLE = "贵州师范大学 2026 年推免生拟推荐名单.xlsx"

CCUCM_SOURCE_URL = "https://y.ccucm.edu.cn/__local/4/A7/4A/9631AD6B7EA1C063F1269E068CD_CA2DF7C2_21F1A.pdf"
CCUCM_PAGE_URL = "https://y.ccucm.edu.cn/info/1205/18311.htm"
CCUCM_TITLE = "长春中医药大学2026年接收推免生拟录取公示"

IMAU_PAGE_URL = "https://dky.imau.edu.cn/info/1052/37701.htm"
IMAU_IMAGE_URL = "https://dky.imau.edu.cn/__local/D/CF/0A/3FE4079D006971F76427BC83DF8_9B89890E_26D68.jpeg"
IMAU_TITLE = "动物科学学院2026届推荐优秀应届本科毕业生免试攻读硕士学位研究生名单公示"
IMAU_ROWS = [
    ("1", "2022122010522", "张淑真", "动物科学", "普通理科"),
    ("2", "2022112011376", "周振宇", "动物科学", "普通理科"),
    ("3", "2022112011446", "崔建国", "动物科学", "普通理科"),
    ("4", "2022112011379", "郭奕婷", "动物科学", "普通理科"),
    ("5", "2022112011410", "张静", "动物科学", "普通理科"),
    ("6", "2022122015588", "向莉娟", "动物科学", "普通理科"),
    ("7", "2022112011435", "刘家瑶", "动物科学", "普通理科"),
    ("8", "2022112011404", "许星晨", "动物科学", "普通理科"),
    ("9", "2022122016615", "刘维荣", "动物科学", "普通理科"),
    ("10", "2022122016611", "白什婧", "动物科学", "普通理科"),
    ("11", "2022122015692", "张彤", "动物科学", "普通理科"),
    ("12", "2022122095391", "郑舒丹", "动物科学", "普通理科"),
    ("13", "2022102010142", "石嘉庆", "动物科学", "普通理科"),
    ("14", "2022102010138", "闫姝", "动物科学", "普通理科"),
    ("15", "2022112011437", "刘英姿", "动物科学", "普通理科"),
    ("16", "2022122015097", "田嘉渝", "动物科学", "普通理科"),
    ("17", "2022122015098", "陈科竹", "动物科学", "普通理科"),
    ("18", "2022122015342", "耿志华", "水产养殖学", "普通理科"),
    ("19", "2022122010533", "王雪薇", "水产养殖学", "普通理科"),
    ("20", "2022122013223", "刘毅", "马业科学", "蒙授理科"),
    ("21", "2022122013213", "娜琴", "马业科学", "蒙授理科"),
    ("22", "2022122013255", "朝都必力格", "马业科学", "蒙授理科"),
]

CCUCM_RECORD_RE = re.compile(
    r"^(?P<sequence>\d+)\s+"
    r"(?P<applicant_type>硕士生|直博生)\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<masked_id>[0-9Xx*]+)\s+"
    r"(?P<major_code>[0-9A-Z]{6})\s+"
    r"(?P<major_name>\S+)\s+"
    r"(?P<direction>.+?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)"
    r"(?:\s+(?P<advisor>\S+))?$"
)


def _collapse_spaces(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_collapse_spaces(part) for part in parts) if part)


def _extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def curate_gznu_workbook(xlsx_path: Path = GZNU_XLSX) -> list[dict[str, Any]]:
    workbook = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    worksheet = workbook["Sheet1"]
    rows: list[dict[str, Any]] = []
    for raw_row in worksheet.iter_rows(min_row=2, values_only=True):
        sequence, student_id, name, gender, college, major_name, status = (list(raw_row) + [None] * 7)[:7]
        if _collapse_spaces(status) != "拟推荐":
            continue
        record = crawler._clean_record(
            {
                "school_name": "贵州师范大学",
                "year": 2026,
                "document_type": "recommendation_exemption_list",
                "route": "recommendation_exemption",
                "person_name": _collapse_spaces(name),
                "student_id": _collapse_spaces(student_id),
                "undergraduate_major": _collapse_spaces(major_name),
                "college": _collapse_spaces(college),
                "major": _collapse_spaces(major_name),
                "ranking": _collapse_spaces(sequence),
                "remarks": _remarks(f"gender {_collapse_spaces(gender)}", "recommendation_status 拟推荐"),
                "source_url": GZNU_SOURCE_URL,
                "title": GZNU_TITLE,
                "needs_review": False,
            }
        )
        if record["person_name"] and record["student_id"]:
            rows.append(record)
    return rows


def parse_ccucm_record(
    text: str,
    *,
    source_url: str = CCUCM_SOURCE_URL,
    title: str = CCUCM_TITLE,
) -> dict[str, Any] | None:
    match = CCUCM_RECORD_RE.match(_collapse_spaces(text))
    if not match:
        return None
    major_code = match.group("major_code")
    major_name = match.group("major_name")
    return crawler._clean_record(
        {
            "school_name": "长春中医药大学",
            "year": 2026,
            "document_type": "incoming_recommendation_admission_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "major": major_code,
            "admission_major": f"{major_code} {major_name}",
            "ranking": match.group("sequence"),
            "remarks": _remarks(
                f"applicant_type {match.group('applicant_type')}",
                f"masked_id_card {match.group('masked_id')}",
                f"direction {match.group('direction')}",
                f"total_score {match.group('total_score')}",
                f"advisor {match.group('advisor')}" if match.group("advisor") else "",
            ),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def curate_ccucm_pdf(pdf_path: Path = CCUCM_PDF) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    buffer = ""
    for raw_line in _extract_pdf_text(pdf_path).splitlines():
        line = _collapse_spaces(raw_line)
        if not line or line.startswith("严禁转载") or line in {"序号 类型 姓名 身份证号 专业代码 专业名称 方向 总分", "备注", "（直博生标明导", "师）"}:
            continue
        if re.match(r"^\d+\s+(硕士生|直博生)\s+", line):
            if buffer:
                record = parse_ccucm_record(buffer)
                if record is not None:
                    rows.append(record)
            buffer = line
        elif buffer:
            buffer = f"{buffer} {line}"
    if buffer:
        record = parse_ccucm_record(buffer)
        if record is not None:
            rows.append(record)
    return rows


def curate_imau_image_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sequence, student_id, name, major_name, recommendation_type in IMAU_ROWS:
        rows.append(
            crawler._clean_record(
                {
                    "school_name": "内蒙古农业大学",
                    "year": 2026,
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": name,
                    "student_id": student_id,
                    "college": "动物科学学院",
                    "major": major_name,
                    "ranking": sequence,
                    "remarks": f"recommendation_type {recommendation_type}",
                    "source_url": IMAU_IMAGE_URL,
                    "title": IMAU_TITLE,
                    "needs_review": False,
                }
            )
        )
    return rows


def _rank_number(row: dict[str, Any]) -> int:
    value = _collapse_spaces(row.get("ranking"))
    return int(value) if value.isdigit() else 0


def curate_records(
    *,
    gznu_xlsx: Path = GZNU_XLSX,
    ccucm_pdf: Path = CCUCM_PDF,
) -> list[dict[str, Any]]:
    rows = [*curate_imau_image_rows(), *curate_gznu_workbook(gznu_xlsx), *curate_ccucm_pdf(ccucm_pdf)]
    rows.sort(
        key=lambda row: (
            str(row.get("school_name") or ""),
            str(row.get("source_url") or ""),
            _rank_number(row),
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
        "batch210_remaining_promising_pages_curated: normalized GZNU XLSX, CCUCM PDF, and IMAU image-only public list.",
        "GZNU: kept only Sheet1 rows marked 拟推荐; excluded 候补 rows and unlabelled extra sheets.",
        "CCUCM: reparsed PDF text to recover 70 rows and prevent wrapped direct-PhD rows from becoming false names.",
        "IMAU: downloaded official JPEG and transcribed its 22-row public table.",
        "SYUCT attachments were CAPTCHA-gated; YMU returned HTTP 521; GSAU seed returned 404; HEBEU crawl found non-recommendation postgraduate pages only.",
        f"rows={len(rows)}",
        f"counts={counts}",
        f"gznu_page={GZNU_PAGE_URL}",
        f"ccucm_page={CCUCM_PAGE_URL}",
        f"imau_page={IMAU_PAGE_URL}",
        f"imau_image={IMAU_IMAGE_URL}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv"), "counts": counts})


if __name__ == "__main__":
    main()
