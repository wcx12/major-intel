from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RAW_PDF = (
    ROOT
    / "data/raw/official_non_final_row_level_bift_2026_doctor_second_assessment/"
    "bift_2026_doctor_second_assessment_list.pdf"
)
OUTPUT_DIR = ROOT / "data/processed/official_non_final_row_level_bift_2026_doctor_second_assessment"
OUTPUT_CSV = OUTPUT_DIR / "records_clean.csv"
DEFAULT_PAGE_DIR = ROOT / "tmp/pdfs/bift_2026_doctor_second_assessment"
DEFAULT_OCR_JSONL = OUTPUT_DIR / "ocr_items.jsonl"
SOURCE_URL = "https://yjs.bift.edu.cn/docs/2026-05/7fa650caeda448448084d81880fcc64e.pdf"
ARTICLE_URL = "https://yjs.bift.edu.cn/zsgz/zsxx/cf66ebac8d524b3bb01f09c540de8258.htm"
TITLE = (
    "\u5317\u4eac\u670d\u88c5\u5b66\u96622026\u5e74\u535a\u58eb\u7814\u7a76\u751f"
    "\u62db\u751f\u8003\u8bd5\u7b2c\u4e8c\u6279\u6b21\u8fdb\u5165\u7efc\u5408\u8003\u6838"
    "\uff08\u590d\u8bd5\uff09\u540d\u5355"
)
LOCAL_ARTIFACT = (
    "data/raw/official_non_final_row_level_bift_2026_doctor_second_assessment/"
    "bift_2026_doctor_second_assessment_list.pdf"
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
    "application_no",
    "research_direction",
    "material_review_score",
    "entered_comprehensive_assessment",
]

APPLICATION_NO_RE = re.compile(r"100129\d{4}")


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).strip()


def format_decimal_score(value: str) -> str:
    value = clean_text(value)
    if not value:
        return ""
    try:
        return f"{float(value):.2f}"
    except ValueError:
        return value


def _load_rapidocr():
    try:
        from rapidocr_onnxruntime import RapidOCR  # type: ignore[import-not-found]

        return RapidOCR
    except ImportError:
        local_package_dir = ROOT / "tmp/rapidocr_pkg"
        if local_package_dir.exists():
            sys.path.insert(0, str(local_package_dir.resolve()))
            from rapidocr_onnxruntime import RapidOCR  # type: ignore[import-not-found]

            return RapidOCR
        raise RuntimeError(
            "rapidocr_onnxruntime is required to parse the BIFT image-style PDF. "
            "Install it with: python -m pip install rapidocr_onnxruntime==1.3.24 -t tmp/rapidocr_pkg"
        )


def _ensure_page_images(pdf_path: Path, page_dir: Path) -> list[Path]:
    page_dir.mkdir(parents=True, exist_ok=True)
    images = sorted(page_dir.glob("page-*.png"))
    if images:
        return images
    subprocess.run(
        ["pdftoppm", "-png", "-r", "150", str(pdf_path), str(page_dir / "page")],
        check=True,
        capture_output=True,
        text=True,
    )
    images = sorted(page_dir.glob("page-*.png"))
    if not images:
        raise RuntimeError(f"pdftoppm did not render any pages for {pdf_path}")
    return images


def _box_bounds(box: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [float(point[0]) for point in box]
    ys = [float(point[1]) for point in box]
    return min(xs), min(ys), max(xs), max(ys)


def _read_ocr_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _write_ocr_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_or_run_ocr(pdf_path: Path, page_dir: Path, ocr_jsonl: Path) -> list[dict[str, Any]]:
    cached_rows = _read_ocr_jsonl(ocr_jsonl) if ocr_jsonl.exists() else []
    image_paths = _ensure_page_images(pdf_path, page_dir)
    done_pages = {int(row.get("page") or 0) for row in cached_rows}
    expected_pages = {
        int(match.group(1))
        for image_path in image_paths
        if (match := re.search(r"page-(\d+)\.png$", image_path.name))
    }
    if expected_pages and expected_pages.issubset(done_pages):
        return cached_rows

    RapidOCR = _load_rapidocr()
    ocr = RapidOCR()
    rows: list[dict[str, Any]] = list(cached_rows)
    for image_path in image_paths:
        page_match = re.search(r"page-(\d+)\.png$", image_path.name)
        page = int(page_match.group(1)) if page_match else 0
        if page in done_pages:
            continue
        result, _ = ocr(str(image_path))
        page_rows: list[dict[str, Any]] = []
        for item in result or []:
            text = clean_text(item[1])
            if not text:
                continue
            x1, y1, x2, y2 = _box_bounds(item[0])
            page_rows.append(
                {
                    "page": page,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "cx": (x1 + x2) / 2,
                    "cy": (y1 + y2) / 2,
                    "text": text,
                    "score": float(item[2]),
                }
            )
        rows.extend(page_rows)
        _write_ocr_jsonl(rows, ocr_jsonl)
        print(f"ocr page {page}/{len(image_paths)} items={len(page_rows)} total_items={len(rows)}", flush=True)
    _write_ocr_jsonl(rows, ocr_jsonl)
    return rows


def _field_text(items: list[dict[str, Any]], x_min: float, x_max: float) -> str:
    return "".join(
        clean_text(item.get("text"))
        for item in sorted(items, key=lambda row: float(row.get("x1", 0)))
        if x_min <= float(item.get("cx", 0)) < x_max and clean_text(item.get("text"))
    )


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


def records_from_ocr_items(items: list[dict[str, Any]], *, source_url: str = SOURCE_URL) -> list[dict[str, str]]:
    by_page: dict[int, list[dict[str, Any]]] = {}
    for item in items:
        by_page.setdefault(int(item.get("page") or 0), []).append(item)

    rows: list[dict[str, str]] = []
    for page, page_items in sorted(by_page.items()):
        anchors = [
            item
            for item in page_items
            if APPLICATION_NO_RE.fullmatch(clean_text(item.get("text")))
            and 900 <= float(item.get("cx", 0)) <= 1065
        ]
        for anchor in sorted(anchors, key=lambda row: float(row.get("cy", 0))):
            row_items = _same_row_items(page_items, anchor)
            application_no = clean_text(anchor.get("text"))
            rows.append(
                {
                    "source_dataset": "official_non_final_row_level",
                    "school_name": "\u5317\u4eac\u670d\u88c5\u5b66\u9662",
                    "year": "2026",
                    "source_scope": "non_final_doctor_second_batch_comprehensive_assessment_list",
                    "coverage_counted": "false",
                    "exclusion_reason": (
                        "not_final_admitted_list; doctoral_comprehensive_assessment_shortlist_only; "
                        "no_final_admission_status; not_master_recommendation_or_admission_final"
                    ),
                    "person_name": _field_text(row_items, 1065, 1185),
                    "student_id": "",
                    "college": _field_text(row_items, 420, 720),
                    "major": _field_text(row_items, 720, 910),
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
                        "Official row-level doctor second-batch comprehensive assessment shortlist; "
                        f"article_page {ARTICLE_URL}; retained as auxiliary data only."
                    ),
                    "application_no": application_no,
                    "research_direction": _field_text(row_items, 150, 390),
                    "material_review_score": format_decimal_score(_field_text(row_items, 1185, 1325)),
                    "entered_comprehensive_assessment": _field_text(row_items, 1375, 1495),
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
