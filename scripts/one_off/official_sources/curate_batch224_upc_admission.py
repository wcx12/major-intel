from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PROCESSED_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch224_upc_admission")
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch224_upc_admission_curated"
)

DEFAULT_DOCUMENTS_JSONL = PROCESSED_DIR / "documents.jsonl"
DEFAULT_PAGE_DIR = Path("tmp/pdfs/upc224")
DEFAULT_OCR_JSONL = DEFAULT_PAGE_DIR / "ocr_items.jsonl"

COLLEGE_RE = re.compile(r"^(\d{3})(?!\d)(.+)")
MAJOR_RE = re.compile(r"^(\d{6,8}[A-Z]?)(.+)")
STUDENT_ID_RE = re.compile(r"\d{15}")
MODE_RE = re.compile(r"(非全日制|全日制)")

NAME_CORRECTIONS = {
    "104256540002040": "程坤",
    "104256540001829": "冯焱",
    "104256540010025": "王丫",
    "104256540008215": "张跃",
    "100016000290719": "李冉",
}

MAJOR_NAME_CORRECTIONS = {
    "085401": "新一代电子信息技术（含量子技术等）",
    "085402": "通信工程（含宽带网络、移动通信等）",
    "085906": "人工环境工程（含供热、通风及空调等）",
}


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
            "rapidocr_onnxruntime is required to parse the scanned UPC PDF. "
            "Install it with: python -m pip install rapidocr_onnxruntime==1.3.24 -t tmp/rapidocr_pkg"
        )


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", "", str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (part.strip() for part in parts) if part)


def _read_documents(documents_jsonl: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    with documents_jsonl.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                docs.append(json.loads(line))
    return docs


def _pdf_document(documents_jsonl: Path) -> dict[str, Any]:
    for document in _read_documents(documents_jsonl):
        raw_path = Path(document.get("raw_path") or "")
        if raw_path.suffix.lower() == ".pdf" or document.get("content_type") == "application/pdf":
            return document
    raise RuntimeError(f"No PDF document found in {documents_jsonl}")


def _ensure_page_images(pdf_path: Path, page_dir: Path) -> list[Path]:
    page_dir.mkdir(parents=True, exist_ok=True)
    images = sorted(page_dir.glob("page-*.png"))
    if images:
        return images
    subprocess.run(
        ["pdftoppm", "-png", "-r", "200", str(pdf_path), str(page_dir / "page")],
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
    if ocr_jsonl.exists():
        return _read_ocr_jsonl(ocr_jsonl)

    RapidOCR = _load_rapidocr()
    ocr = RapidOCR()
    rows: list[dict[str, Any]] = []
    for image_path in _ensure_page_images(pdf_path, page_dir):
        page_match = re.search(r"page-(\d+)\.png$", image_path.name)
        page = int(page_match.group(1)) if page_match else 0
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        height, width = image.shape[:2] if image is not None else (0, 0)
        result, _ = ocr(str(image_path))
        for item in result or []:
            x1, y1, x2, y2 = _box_bounds(item[0])
            text = _clean_text(item[1])
            if not text:
                continue
            rows.append(
                {
                    "page": page,
                    "width": width,
                    "height": height,
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
    _write_ocr_jsonl(rows, ocr_jsonl)
    return rows


def _is_college_header(text: str) -> bool:
    return bool(COLLEGE_RE.match(text))


def _parse_code_name(text: str, pattern: re.Pattern[str]) -> tuple[str, str]:
    match = pattern.match(text)
    if not match:
        return "", text
    return match.group(1), match.group(2)


def _group_rows(items: list[dict[str, Any]], tolerance: float = 15.0) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    for item in sorted(items, key=lambda row: (row["cy"], row["x1"])):
        if groups:
            mean_y = sum(row["cy"] for row in groups[-1]) / len(groups[-1])
            if abs(item["cy"] - mean_y) <= tolerance:
                groups[-1].append(item)
                continue
        groups.append([item])
    return [sorted(group, key=lambda row: row["x1"]) for group in groups]


def _detect_horizontal_lines(image_path: Path, column: int) -> list[float]:
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return []
    width = image.shape[1]
    split_x = width / 2
    if column == 1:
        x1, x2 = int(width * 0.12), int(split_x * 0.92)
    else:
        x1, x2 = int(split_x * 1.02), int(width * 0.86)
    crop = image[:, x1:x2]
    dark = crop < 180
    counts = dark.sum(axis=1)
    threshold = max(260, int((x2 - x1) * 0.55))
    ys = np.where(counts >= threshold)[0].tolist()
    groups: list[list[int]] = []
    for y in ys:
        if groups and y - groups[-1][-1] <= 2:
            groups[-1].append(y)
        else:
            groups.append([y])
    return [sum(group) / len(group) for group in groups]


def _row_band_for(item: dict[str, Any], lines: list[float]) -> tuple[float, float]:
    y = item["cy"]
    above = [line for line in lines if line < y - 1]
    below = [line for line in lines if line > y + 1]
    if above and below:
        return max(above) + 1, min(below) - 1
    return y - 23, y + 23


def _mode_and_plan(text: str) -> tuple[str, str]:
    mode_match = MODE_RE.search(text)
    mode = mode_match.group(1) if mode_match else ""
    plans = []
    if "少干" in text:
        plans.append("少干")
    if "士兵" in text:
        plans.append("士兵")
    if "南疆计划" in text:
        plans.append("南疆计划")
    return mode, ",".join(plans)


def _extract_record_fields(
    id_item: dict[str, Any],
    column_items: list[dict[str, Any]],
    band: tuple[float, float],
) -> tuple[str, str, str]:
    upper, lower = band
    mode_x_start = id_item["x2"] + 165
    in_band = [
        row
        for row in column_items
        if upper <= row["cy"] <= lower
        and row["x1"] > id_item["x2"] - 5
        and row["text"] != id_item["text"]
    ]
    name_parts = []
    mode_parts = []
    for row in sorted(in_band, key=lambda value: (value["cy"], value["x1"])):
        cell = row["text"]
        if MODE_RE.search(cell) or row["x1"] >= mode_x_start:
            mode_parts.append(cell)
            continue
        if re.search(r"[\u4e00-\u9fff]", cell):
            name_parts.append(cell)

    mode_text = "".join(mode_parts)
    mode, plan = _mode_and_plan(mode_text)
    name = "".join(name_parts)
    name = MODE_RE.sub("", name)
    for token in ("少干", "士兵", "南疆计划"):
        name = name.replace(token, "")
    return name, mode, plan


def _normalise_major_name(code: str, name: str) -> str:
    name = MAJOR_NAME_CORRECTIONS.get(code, name)
    if "（" in name:
        name = name.replace("(", "（").replace(")", "）")
    return name


def _parse_ocr_records(ocr_items: list[dict[str, Any]], page_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current_college_code = ""
    current_college = ""
    current_major_code = ""
    current_major = ""
    pending_college_continuation = False
    pending_major_continuation = False

    for page in sorted({int(row["page"]) for row in ocr_items}):
        page_items = [row for row in ocr_items if int(row["page"]) == page]
        width = max((row.get("width") or row["x2"] for row in page_items), default=0)
        split_x = width / 2 if width else 820
        lines_by_column = {
            1: _detect_horizontal_lines(page_dir / f"page-{page:02d}.png", 1),
            2: _detect_horizontal_lines(page_dir / f"page-{page:02d}.png", 2),
        }
        columns = [
            [row for row in page_items if row["cx"] < split_x],
            [row for row in page_items if row["cx"] >= split_x],
        ]

        for column_index, column_items in enumerate(columns, start=1):
            for group in _group_rows(column_items):
                text = "".join(row["text"] for row in group)
                if not text:
                    continue
                if "考生编号" in text or text == "姓名" or "拟录取名单" in text:
                    continue
                if _is_college_header(text):
                    current_college_code, current_college = _parse_code_name(text, COLLEGE_RE)
                    current_major_code = ""
                    current_major = ""
                    pending_college_continuation = True
                    pending_major_continuation = False
                    continue

                major_match = MAJOR_RE.match(text)
                if major_match and not STUDENT_ID_RE.search(text):
                    current_major_code, current_major = major_match.group(1), major_match.group(2)
                    current_major = _normalise_major_name(current_major_code, current_major)
                    pending_college_continuation = False
                    pending_major_continuation = True
                    continue

                ids = [row for row in group if STUDENT_ID_RE.fullmatch(row["text"])]
                if not ids:
                    maybe = STUDENT_ID_RE.search(text)
                    if not maybe:
                        if (
                            pending_college_continuation
                            and current_college
                            and not re.search(r"\d{6}", text)
                            and re.search(r"[\u4e00-\u9fff]", text)
                        ):
                            current_college += text
                            continue
                        if (
                            pending_major_continuation
                            and current_major
                            and not _is_college_header(text)
                            and not MAJOR_RE.match(text)
                            and re.search(r"[\u4e00-\u9fff)]", text)
                        ):
                            current_major = _normalise_major_name(current_major_code, current_major + text)
                        continue
                    ids = [
                        {
                            "text": maybe.group(),
                            "x1": group[0]["x1"],
                            "x2": group[0]["x2"],
                            "cy": group[0]["cy"],
                        }
                    ]

                pending_major_continuation = False
                for id_item in ids:
                    band = _row_band_for(id_item, lines_by_column[column_index])
                    person_name, study_mode, special_plan = _extract_record_fields(id_item, column_items, band)
                    student_id = id_item["text"]
                    person_name = NAME_CORRECTIONS.get(student_id, person_name)
                    if not person_name:
                        continue
                    records.append(
                        {
                            "page": page,
                            "column": column_index,
                            "student_id": student_id,
                            "person_name": person_name,
                            "college_code": current_college_code,
                            "college": current_college,
                            "major_code": current_major_code,
                            "major_name": _normalise_major_name(current_major_code, current_major),
                            "study_mode": study_mode,
                            "special_plan": special_plan,
                        }
                    )
    return records


def curate_records(
    *,
    documents_jsonl: Path = DEFAULT_DOCUMENTS_JSONL,
    page_dir: Path = DEFAULT_PAGE_DIR,
    ocr_jsonl: Path = DEFAULT_OCR_JSONL,
) -> list[dict[str, Any]]:
    document = _pdf_document(documents_jsonl)
    pdf_path = Path(document.get("raw_path") or "")
    if not pdf_path.exists():
        raise RuntimeError(f"PDF raw file not found: {pdf_path}")

    _ensure_page_images(pdf_path, page_dir)
    ocr_items = _load_or_run_ocr(pdf_path, page_dir, ocr_jsonl)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for parsed in _parse_ocr_records(ocr_items, page_dir):
        major_code = parsed["major_code"]
        major_name = _normalise_major_name(major_code, parsed["major_name"])
        admission_major = f"{major_code} {major_name}".strip()
        remarks = _remarks(
            f"college_code {parsed['college_code']}" if parsed["college_code"] else "",
            f"study_mode {parsed['study_mode']}" if parsed["study_mode"] else "",
            f"special_plan {parsed['special_plan']}" if parsed["special_plan"] else "",
            f"source_page {parsed['page']}",
        )
        record = crawler._clean_record(
            {
                "school_name": "中国石油大学（华东）",
                "year": 2026,
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name": parsed["person_name"],
                "student_id": parsed["student_id"],
                "college": parsed["college"],
                "major": major_code,
                "admission_major": admission_major,
                "remarks": remarks,
                "source_url": document.get("source_url", ""),
                "title": document.get("title", ""),
                "needs_review": False,
            }
        )
        key = (record.get("person_name", ""), record.get("student_id", ""), record.get("source_url", ""))
        if key in seen:
            continue
        seen.add(key)
        rows.append(record)
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    notes = [
        "batch224_upc_admission_curated: parsed China University of Petroleum (East China) 2026 master admission scanned PDF.",
        "The official PDF is image-only; pages are rendered with pdftoppm at 200 dpi and parsed with RapidOCR plus table-line reconstruction.",
        "Manual visual corrections applied for five OCR-missed rare/single-character name cells and three long major titles.",
        f"rows={len(rows)}",
        "source=https://yz.upc.edu.cn/2026/0513/c10708a490438/page.htm",
        "source=https://yz.upc.edu.cn/_upload/article/files/0c/d5/e987be3444428e06eb7652dac2ed/17989726-14ad-4441-bb76-17ff5ffe0695.pdf",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
