from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import fitz

try:
    from scripts import graduate_outcome_crawler as crawler
    from scripts.one_off.official_sources.curate_batch203_ecust_image_ocr import ocr_image_words
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler
    from curate_batch203_ecust_image_ocr import ocr_image_words


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch255_ksu_recommendation/"
    "yjsc.ksu.edu.cn/9c7cd0d132eb3846.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch255_ksu_recommendation_curated"
)

SCHOOL_NAME = "喀什大学"
YEAR = 2026
DOCUMENT_TYPE = "recommendation_exemption_list"
ROUTE = "recommendation_exemption"
TITLE = "喀什大学2026年拟接收推荐免试攻读全日制硕士研究生拟录取名单公示"
SOURCE_URL = (
    "https://yjsc.ksu.edu.cn/virtual_attach_file.vsb?"
    "afc=tU8nj2UlLDnRU8nwzf7ozl4Uz94LR9XZMRf2MRNZnzCDMRL0gihFp2hmCIa0LYyaLYh7MkhVMNM7MzQVLN7bnRfVUlMkM87snRr2U4-4UzQFMNnRMl-iUzVFM7LZLNlJv2nto4OeosT/vDL0qIbtpYyPLRL8g4-ZL4-Jqd/nx"
    "&oid=1120997853&tid=1034&nid=2832&e=.pdf"
)

ROW_COUNT = 60
FIRST_ROW_Y = 409
ROW_HEIGHT = 90
Y_TOLERANCE = 35

BANDS = {
    "name": (250, 680),
    "identity": (680, 1325),
    "college": (1325, 1980),
    "major_code": (1980, 2520),
    "major_name": (2520, 3330),
    "remark": (3330, 3800),
}

OCR_NAME_FIXES = {
    36: "高雅萱",
    46: "姜宁",
    50: "申志豪",
    55: "穆开代斯·赛买提",
}


def _render_pdf_page(pdf_path: Path, output_path: Path) -> Path:
    if output_path.exists() and output_path.stat().st_size > 0:
        return output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = fitz.open(pdf_path)
    try:
        page = document.load_page(0)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False)
        pixmap.save(output_path)
    finally:
        document.close()
    return output_path


def _words_for_pdf(pdf_path: Path) -> list[dict[str, Any]]:
    image_path = _render_pdf_page(pdf_path, OUT_DIR / "rendered" / "page001.png")
    cache_path = OUT_DIR / "ocr_words" / "page001.json"
    return ocr_image_words(image_path, cache_path)


def _band_text(words: list[dict[str, Any]], low_x: int, high_x: int) -> str:
    selected = [word for word in words if low_x <= int(word["x"]) < high_x]
    return "".join(str(word["text"]) for word in sorted(selected, key=lambda word: int(word["x"]))).strip()


def _clean_visible_text(value: str) -> str:
    return re.sub(r"\s+", "", value or "").replace("，", "·").replace(".", "·")


def _masked_identity(value: str) -> str:
    compact = _clean_visible_text(value).upper()
    compact = re.sub(r"[^0-9X*]", "", compact)
    if "*" in compact:
        return compact
    if len(compact) == 10:
        return f"{compact[:6]}********{compact[-4:]}"
    return compact


def _row_words(words: list[dict[str, Any]], row_number: int) -> list[dict[str, Any]]:
    center_y = FIRST_ROW_Y + (row_number - 1) * ROW_HEIGHT
    return [
        word
        for word in words
        if center_y - Y_TOLERANCE <= int(word["y"]) <= center_y + Y_TOLERANCE
    ]


def _record_from_row(words: list[dict[str, Any]], row_number: int) -> dict[str, Any]:
    row_words = _row_words(words, row_number)
    values = {
        key: _clean_visible_text(_band_text(row_words, low_x, high_x))
        for key, (low_x, high_x) in BANDS.items()
    }
    person_name = OCR_NAME_FIXES.get(row_number, values["name"])
    identity = _masked_identity(values["identity"])
    college = values["college"]
    major_code = values["major_code"]
    major_name = values["major_name"]
    remark = values["remark"]
    remarks = "来源名单: 接收推荐免试硕士研究生拟录取"
    if remark:
        remarks = f"{remarks}; 备注: {remark}"

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": identity,
        "undergraduate_school": "",
        "undergraduate_major": "",
        "college": college,
        "major": major_name,
        "admission_major": f"{major_code} {major_name}".strip(),
        "ranking": str(row_number),
        "remarks": remarks,
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    words = _words_for_pdf(path)
    records = [_record_from_row(words, row_number) for row_number in range(1, ROW_COUNT + 1)]
    missing = [
        row["ranking"]
        for row in records
        if not row["person_name"] or not row["student_id"] or not row["college"] or not row["admission_major"]
    ]
    if missing:
        raise ValueError(f"Missing core OCR fields in KSU rows: {json.dumps(missing, ensure_ascii=False)}")
    return records


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
