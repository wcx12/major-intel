from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


SCHOOL_NAME = "华东师范大学"
YEAR = 2025
TITLE = "华东师范大学2025年全国硕士研究生招生考试拟录取名单公示（已包括成绩）"

PROCESSED_DIR = Path("data/processed/official_site_recommendation_websearch_web_20260602_batch486_cupl_ecnu_ouc_2025_2026")
OUT_DIR = Path(
    "data/processed/official_site_recommendation_websearch_web_20260602_batch486_cupl_ecnu_ouc_2025_2026_ecnu_curated"
)
DEFAULT_DOCUMENTS_JSONL = PROCESSED_DIR / "documents.jsonl"
DEFAULT_PAGE_DIR = Path("tmp/pdfs/ecnu486")
DEFAULT_OCR_JSONL = DEFAULT_PAGE_DIR / "ocr_items.jsonl"

STUDENT_ID_RE = re.compile(r"\d{5,6}\*{2,}\d{2,4}")
STUDENT_ID_FRAGMENT_RE = re.compile(r"\d[\d*]{8,}\d")


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (part.strip() for part in parts) if part)


def _load_rapidocr():
    try:
        from rapidocr_onnxruntime import RapidOCR  # type: ignore[import-not-found]

        return RapidOCR
    except ImportError:
        local_package_dir = Path("tmp/rapidocr_pkg")
        if local_package_dir.exists():
            sys.path.insert(0, str(local_package_dir.resolve()))
            from rapidocr_onnxruntime import RapidOCR  # type: ignore[import-not-found]

            return RapidOCR
        raise RuntimeError(
            "rapidocr_onnxruntime is required to parse the ECNU image-only PDF. "
            "Install it with: python -m pip install rapidocr_onnxruntime==1.3.24 -t tmp/rapidocr_pkg"
        )


def _read_documents(documents_jsonl: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with documents_jsonl.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _pdf_document(documents_jsonl: Path) -> dict[str, Any]:
    for document in _read_documents(documents_jsonl):
        raw_path = Path(document.get("raw_path") or "")
        source_url = str(document.get("source_url") or "")
        if raw_path.suffix.lower() == ".pdf" and "ecnu.edu.cn" in source_url:
            return document
    raise RuntimeError(f"No ECNU PDF document found in {documents_jsonl}")


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
            text = _clean_text(item[1])
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
        print(
            f"ocr page {page}/{len(image_paths)} items={len(page_rows)} total_items={len(rows)}",
            flush=True,
        )
    _write_ocr_jsonl(rows, ocr_jsonl)
    return rows


def _join_column(items: list[dict[str, Any]], x_min: float, x_max: float) -> str:
    texts = [
        _clean_text(item.get("text"))
        for item in sorted(items, key=lambda row: (float(row.get("x1", 0)), float(row.get("cy", 0))))
        if x_min <= float(item.get("cx", 0)) < x_max and _clean_text(item.get("text"))
    ]
    return "".join(texts)


def _same_row_items(page_items: list[dict[str, Any]], id_item: dict[str, Any]) -> list[dict[str, Any]]:
    cy = float(id_item.get("cy", 0))
    return [
        item
        for item in page_items
        if abs(float(item.get("cy", 0)) - cy) <= 9.0
        or (
            float(item.get("y1", 0)) <= cy <= float(item.get("y2", 0))
            and abs(float(item.get("cy", 0)) - cy) <= 13.0
        )
    ]


def _group_page_rows(page_items: list[dict[str, Any]], tolerance: float = 9.0) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    for item in sorted(page_items, key=lambda row: (float(row.get("cy", 0)), float(row.get("x1", 0)))):
        if groups:
            mean_y = sum(float(row.get("cy", 0)) for row in groups[-1]) / len(groups[-1])
            if abs(float(item.get("cy", 0)) - mean_y) <= tolerance:
                groups[-1].append(item)
                continue
        groups.append([item])
    return [sorted(group, key=lambda row: float(row.get("x1", 0))) for group in groups]


def _normalise_student_id(value: str) -> str:
    match = STUDENT_ID_FRAGMENT_RE.search(_clean_text(value))
    if not match:
        return ""
    candidate = re.sub(r"(?<=\d)\*(?=\d)", "", match.group())
    return candidate if STUDENT_ID_RE.fullmatch(candidate) else ""


def _split_around_student_id(value: str) -> tuple[str, str]:
    text = _clean_text(value)
    match = STUDENT_ID_FRAGMENT_RE.search(text)
    if not match:
        return "", ""
    return text[: match.start()], text[match.end() :]


def records_from_ocr_items(items: list[dict[str, Any]], *, source_url: str, title: str = TITLE) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()
    by_page: dict[int, list[dict[str, Any]]] = {}
    for item in items:
        by_page.setdefault(int(item.get("page") or 0), []).append(item)

    for page, page_items in sorted(by_page.items()):
        for row_items in _group_page_rows(page_items):
            if not row_items or float(row_items[0].get("cy", 0)) < 105:
                continue
            left_text = "".join(
                _clean_text(item.get("text"))
                for item in row_items
                if float(item.get("cx", 0)) < 690
            )
            student_id = _normalise_student_id(left_text)
            if not student_id:
                continue
            person_name = _join_column(row_items, 0, 84)
            college = _join_column(row_items, 230, 690)
            major = _join_column(row_items, 680, 1020)
            study_mode = _join_column(row_items, 1018, 1128)
            initial_score = _join_column(row_items, 1128, 1224)
            reexam_score = _join_column(row_items, 1224, 1298)
            total_score = _join_column(row_items, 1298, 1388)
            extra_remarks = _join_column(row_items, 1388, 1800)
            for item in row_items:
                before_id, after_id = _split_around_student_id(str(item.get("text") or ""))
                if not person_name and before_id:
                    person_name = before_id
                if after_id and not college and re.search(r"[\u4e00-\u9fff]", after_id):
                    college = after_id
            key = (student_id, person_name, page)
            if key in seen:
                continue
            if not (student_id and person_name and college and major):
                continue
            seen.add(key)
            record = crawler._clean_record(
                {
                    "school_name": SCHOOL_NAME,
                    "year": YEAR,
                    "document_type": "postgraduate_admission_list",
                    "route": "postgraduate_exam_or_admission",
                    "person_name": person_name,
                    "student_id": student_id,
                    "college": college,
                    "major": major,
                    "admission_major": major,
                    "remarks": _remarks(
                        f"study_mode {study_mode}" if study_mode else "",
                        f"initial_score {initial_score}" if initial_score else "",
                        f"reexam_score {reexam_score}" if reexam_score else "",
                        f"total_score {total_score}" if total_score else "",
                        f"extra_remarks {extra_remarks}" if extra_remarks else "",
                        f"source_page {page}" if page else "",
                    ),
                    "source_url": source_url,
                    "title": title,
                    "needs_review": False,
                }
            )
            rows.append(record)

    return rows


def curate_records(
    *,
    documents_jsonl: Path = DEFAULT_DOCUMENTS_JSONL,
    page_dir: Path = DEFAULT_PAGE_DIR,
    ocr_jsonl: Path = DEFAULT_OCR_JSONL,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    document = _pdf_document(documents_jsonl)
    pdf_path = Path(document.get("raw_path") or "")
    if not pdf_path.exists():
        raise RuntimeError(f"PDF raw file not found: {pdf_path}")
    _ensure_page_images(pdf_path, page_dir)
    ocr_items = _load_or_run_ocr(pdf_path, page_dir, ocr_jsonl)
    rows = records_from_ocr_items(ocr_items, source_url=str(document.get("source_url") or ""), title=TITLE)

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (row.get("person_name", ""), row.get("student_id", ""), row.get("source_url", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped, document


def write_outputs(rows: list[dict[str, Any]], document: dict[str, Any], output_dir: Path) -> dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    records_jsonl = output_dir / "records.jsonl"
    with records_jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    out_document = dict(document)
    out_document.update(
        {
            "title": TITLE,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "parse_status": "curated_from_official_image_pdf_ocr",
            "record_count": len(rows),
        }
    )
    (output_dir / "documents.jsonl").write_text(json.dumps(out_document, ensure_ascii=False) + "\n", encoding="utf-8")

    clean_csv = output_dir / "records_clean_curated.csv"
    public_csv = output_dir / "records_public_curated.csv"
    summary_csv = output_dir / "school_year_summary_curated.csv"
    crawler._write_clean_records_csv(rows, clean_csv)
    crawler._write_summary_csv(crawler._build_summary_rows(rows), summary_csv)
    public_summary = crawler.export_public_records_csv(clean_csv, public_csv)

    (output_dir / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch486_ecnu_2025_ocr_pdf_curated: parsed ECNU official 2025 master admission image-only PDF.",
                "Pages rendered with pdftoppm at 150 dpi; OCR words parsed with RapidOCR by fixed table columns.",
                f"rows={len(rows)}",
                f"source={document.get('source_url')}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {"clean_rows": len(rows), **public_summary}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents-jsonl", type=Path, default=DEFAULT_DOCUMENTS_JSONL)
    parser.add_argument("--page-dir", type=Path, default=DEFAULT_PAGE_DIR)
    parser.add_argument("--ocr-jsonl", type=Path, default=DEFAULT_OCR_JSONL)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    rows, document = curate_records(
        documents_jsonl=args.documents_jsonl,
        page_dir=args.page_dir,
        ocr_jsonl=args.ocr_jsonl,
    )
    result = write_outputs(rows, document, args.output_dir)
    print(json.dumps(result | {"output_dir": str(args.output_dir)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
