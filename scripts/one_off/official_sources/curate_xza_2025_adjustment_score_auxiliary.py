from __future__ import annotations

import csv
import html
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW_HTML = (
    ROOT
    / "data/raw/official_site_recommendation_websearch_web_20260602_batch491_xza_2025_adjustment_score_probe/"
    "www.xza.edu.cn/5e8c5de0a6671c67.htm"
)
OUTPUT_CSV = (
    ROOT
    / "data/processed/official_non_final_row_level_xza_2025_adjustment_score/records_clean.csv"
)
SOURCE_URL = "http://www.xza.edu.cn/yjsc/info/1040/5983.htm"
TITLE = "西藏农牧学院2025年硕士研究生招生调剂考生复试成绩-西藏农牧大学研究生处"
LOCAL_ARTIFACT = (
    "data/raw/official_site_recommendation_websearch_web_20260602_batch491_xza_2025_adjustment_score_probe/"
    "www.xza.edu.cn/5e8c5de0a6671c67.htm"
)

FIELDS = [
    "source_dataset",
    "school_name",
    "year",
    "source_scope",
    "coverage_counted",
    "exclusion_reason",
    "person_name",
    "student_id",
    "college",
    "major",
    "study_mode",
    "soldier_plan",
    "english_score",
    "politics_score",
    "business_course_1_score",
    "business_course_2_score",
    "initial_total_score",
    "retest_score",
    "additional_exam_1_score",
    "additional_exam_2_score",
    "admission_score",
    "source_url",
    "title",
    "local_artifact",
    "notes",
]


class TableCellTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_cell = False
        self.current_parts: list[str] = []
        self.cells: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"td", "th"}:
            self.in_cell = True
            self.current_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"td", "th"} and self.in_cell:
            self.cells.append(clean_text("".join(self.current_parts)))
            self.current_parts = []
            self.in_cell = False

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.current_parts.append(data)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def format_decimal_score(value: str) -> str:
    value = clean_text(value)
    if not value:
        return ""
    try:
        return f"{float(value):.2f}"
    except ValueError:
        return value


def extract_cells(raw_html: str) -> list[str]:
    parser = TableCellTextParser()
    parser.feed(raw_html)
    return parser.cells


def parse_official_score_rows(raw_html: str) -> list[dict[str, str]]:
    cells = extract_cells(raw_html)
    expected_header = [
        "姓名",
        "考生编号",
        "调剂复试院（所）",
        "调剂复试专业",
        "学习形式",
        "士兵计划",
        "英语",
        "政治",
        "业务课一",
        "业务课二",
        "初试总分（含加分）",
        "复试成绩",
        "加试一成绩",
        "加试二成绩",
        "录取成绩",
    ]
    header_start = next(
        index for index in range(len(cells)) if cells[index : index + len(expected_header)] == expected_header
    )
    data_cells = cells[header_start + len(expected_header) :]
    width = len(expected_header)
    rows: list[dict[str, str]] = []
    for offset in range(0, len(data_cells), width):
        values = data_cells[offset : offset + width]
        if len(values) < width or not values[0]:
            continue
        rows.append(
            {
                "source_dataset": "official_non_final_row_level",
                "school_name": "西藏农牧大学",
                "year": "2025",
                "source_scope": "non_final_adjustment_score_table",
                "coverage_counted": "false",
                "exclusion_reason": "not_final_admitted_list; no_final_admission_status",
                "person_name": values[0],
                "student_id": values[1],
                "college": values[2],
                "major": values[3],
                "study_mode": values[4],
                "soldier_plan": values[5],
                "english_score": values[6],
                "politics_score": values[7],
                "business_course_1_score": values[8],
                "business_course_2_score": values[9],
                "initial_total_score": values[10],
                "retest_score": format_decimal_score(values[11]),
                "additional_exam_1_score": format_decimal_score(values[12]),
                "additional_exam_2_score": format_decimal_score(values[13]),
                "admission_score": format_decimal_score(values[14]),
                "source_url": SOURCE_URL,
                "title": TITLE,
                "local_artifact": LOCAL_ARTIFACT,
                "notes": "Official row-level adjustment re-exam score table; retained as auxiliary data only.",
            }
        )
    return rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = parse_official_score_rows(RAW_HTML.read_text(encoding="utf-8"))
    write_rows(OUTPUT_CSV, rows)
    print({"output": str(OUTPUT_CSV), "rows": len(rows)})


if __name__ == "__main__":
    main()
