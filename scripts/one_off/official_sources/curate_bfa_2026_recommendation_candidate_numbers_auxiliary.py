from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.one_off.official_sources.curate_bift_2026_doctor_second_assessment_auxiliary import _load_or_run_ocr, clean_text

RAW_PDF = (
    ROOT
    / "data/raw/official_non_final_row_level_bfa_2026_recommendation_candidate_numbers/"
    "bfa_2026_recommendation_candidate_numbers.pdf"
)
OUTPUT_DIR = ROOT / "data/processed/official_non_final_row_level_bfa_2026_recommendation_candidate_numbers"
OUTPUT_CSV = OUTPUT_DIR / "records_clean.csv"
DEFAULT_PAGE_DIR = ROOT / "tmp/pdfs/bfa_2026_recommendation_candidate_numbers"
DEFAULT_OCR_JSONL = OUTPUT_DIR / "ocr_items.jsonl"
SOURCE_URL = "https://www.bfa.edu.cn/yanjiusheng/2026niantuimiankaoshengkaoshengbianhao.pdf"
TITLE = "2026\u5e74\u7855\u58eb\u7814\u7a76\u751f\u63a8\u514d\u8003\u751f\u8003\u751f\u7f16\u53f7"
LOCAL_ARTIFACT = (
    "data/raw/official_non_final_row_level_bfa_2026_recommendation_candidate_numbers/"
    "bfa_2026_recommendation_candidate_numbers.pdf"
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

CANDIDATE_NUMBER_RE = re.compile(r"100506\d{9}")


def _same_row_items(page_items: list[dict[str, Any]], anchor: dict[str, Any]) -> list[dict[str, Any]]:
    cy = float(anchor.get("cy", 0))
    return [
        item
        for item in page_items
        if abs(float(item.get("cy", 0)) - cy) <= 4.0
        or (
            float(item.get("y1", 0)) <= cy <= float(item.get("y2", 0))
            and abs(float(item.get("cy", 0)) - cy) <= 6.0
        )
    ]


def _field_text(items: list[dict[str, Any]], x_min: float, x_max: float) -> str:
    return "".join(
        clean_text(item.get("text"))
        for item in sorted(items, key=lambda row: float(row.get("x1", 0)))
        if x_min <= float(item.get("cx", 0)) < x_max and clean_text(item.get("text"))
    )


def records_from_ocr_items(items: list[dict[str, Any]], *, source_url: str = SOURCE_URL) -> list[dict[str, str]]:
    by_page: dict[int, list[dict[str, Any]]] = {}
    for item in items:
        by_page.setdefault(int(item.get("page") or 0), []).append(item)

    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for page, page_items in sorted(by_page.items()):
        anchors = [
            item
            for item in page_items
            if CANDIDATE_NUMBER_RE.fullmatch(clean_text(item.get("text")))
        ]
        for anchor in sorted(anchors, key=lambda row: (float(row.get("cy", 0)), float(row.get("x1", 0)))):
            candidate_number = clean_text(anchor.get("text"))
            if candidate_number in seen:
                continue
            seen.add(candidate_number)
            row_items = _same_row_items(page_items, anchor)
            if float(anchor.get("cx", 0)) < 700:
                person_name = _field_text(row_items, 120, 330)
            else:
                person_name = _field_text(row_items, 620, 830)
            rows.append(
                {
                    "source_dataset": "official_non_final_row_level",
                    "school_name": "\u5317\u4eac\u7535\u5f71\u5b66\u9662",
                    "year": "2026",
                    "source_scope": "non_final_recommendation_candidate_number_list",
                    "coverage_counted": "false",
                    "exclusion_reason": (
                        "not_final_admitted_list; candidate_number_list_only; "
                        "no_final_admission_status"
                    ),
                    "person_name": person_name,
                    "student_id": candidate_number,
                    "college": "",
                    "major": "",
                    "study_mode": "",
                    "soldier_plan": "",
                    "english_score": "",
                    "politics_score": "",
                    "business_course_1_score": "",
                    "business_course_2_score": "",
                    "initial_total_score": "",
                    "retest_score": "",
                    "additional_exam_1_score": "",
                    "additional_exam_2_score": "",
                    "admission_score": "",
                    "source_url": source_url,
                    "title": TITLE,
                    "local_artifact": LOCAL_ARTIFACT,
                    "notes": (
                        "Official recommendation-exemption candidate number list; "
                        "retained as auxiliary data only."
                    ),
                }
            )
    return rows


def parse_official_pdf(
    pdf_path: Path = RAW_PDF,
    *,
    page_dir: Path = DEFAULT_PAGE_DIR,
    ocr_jsonl: Path = DEFAULT_OCR_JSONL,
) -> list[dict[str, str]]:
    items = _load_or_run_ocr(pdf_path, page_dir, ocr_jsonl)
    return records_from_ocr_items(items)


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = parse_official_pdf()
    write_rows(OUTPUT_CSV, rows)
    print({"output": str(OUTPUT_CSV), "rows": len(rows)})


if __name__ == "__main__":
    main()
