from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


SCHOOL_NAME = "甘肃中医药大学"
YEAR = 2024
SOURCE_URL = "https://yjsc.gszy.edu.cn/ueditor/php/upload/file/20240507/1715071988136303.pdf"
TITLE = "甘肃中医药大学2024年硕士研究生招生考试拟录取名单公示"


def _normalize_code(code: str) -> str:
    code = (code or "").strip()
    if code.isdigit() and len(code) == 5:
        return code.zfill(6)
    return code


def _compact_major(value: str) -> str:
    return "".join((value or "").split())


def _base_record() -> dict[str, Any]:
    return {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "undergraduate_major": "",
        "college": "",
        "source_url": SOURCE_URL,
        "title": TITLE,
    }


def parse_exam_records_from_text(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse unified-exam/adjustment rows from the PDF text layer.

    The school PDF does not publish names for this section. It does publish
    candidate IDs, majors, scores, admission status, source type, and physical
    exam result. Rows are kept only when both admission status and physical
    result prove they are admitted and qualified.
    """

    starts = list(re.finditer(r"(?m)^\s*\d+\s+\d{15}\b", text or ""))
    rows: list[dict[str, Any]] = []
    skipped: list[str] = []
    pattern = re.compile(
        r"^(?P<ranking>\d+)\s+"
        r"(?P<student_id>\d{15})\s+"
        r"(?P<code>[0-9A-Z]{5,6})\s+"
        r"(?P<major>.+?)\s+"
        r"(?P<initial_score>\d{3})\s+"
        r"(?P<reexam_score>[0-9.]+)\s+"
        r"(?P<composite_score>[0-9.]+)\s+"
        r"(?P<status>拟录取(?:\s*（士兵计\s*划）)?|拟淘汰)\s+"
        r"(?P<application_type>一志愿|调剂)\s+"
        r"(?P<physical_exam>合格|不合格)\b"
    )

    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[start.start() : end]
        compact = " ".join(block.split())
        match = pattern.match(compact)
        if not match:
            skipped.append(compact[:240])
            continue

        data = match.groupdict()
        status = re.sub(r"\s+", "", data["status"]).replace("士兵计划", "士兵计划")
        if "拟录取" not in status or data["physical_exam"] != "合格":
            skipped.append("excluded_status " + compact[:220])
            continue

        code = _normalize_code(data["code"])
        major = _compact_major(data["major"])
        record = _base_record()
        record.update(
            {
                "document_type": "master_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name": "",
                "student_id": data["student_id"],
                "undergraduate_school": "",
                "major": f"{code}|{major}",
                "admission_major": f"{code}|{major}",
                "ranking": data["ranking"],
                "remarks": "; ".join(
                    [
                        f"official_admission_status: {status}",
                        f"application_type: {data['application_type']}",
                        f"physical_exam: {data['physical_exam']}",
                        f"initial_score: {data['initial_score']}",
                        f"reexamination_score: {data['reexam_score']}",
                        f"composite_score: {data['composite_score']}",
                    ]
                ),
            }
        )
        rows.append(record)

    return rows, skipped


def parse_recommendation_records_from_layout(layout_text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^\s*(?P<ranking>\d+)\s+"
        r"(?P<person_name>[\u4e00-\u9fff·]{2,4})\s+"
        r"(?P<code>[0-9A-Z]{5,6})\s+"
        r"(?P<major>.+?)\s+"
        r"拟录取\s+推免及“5\+3”\s+合格\s*$",
        re.M,
    )

    for match in pattern.finditer(layout_text or ""):
        data = match.groupdict()
        code = _normalize_code(data["code"])
        major = _compact_major(data["major"])
        record = _base_record()
        record.update(
            {
                "document_type": "recommendation_admission_list",
                "route": "recommendation_exemption",
                "person_name": data["person_name"],
                "student_id": "",
                "undergraduate_school": SCHOOL_NAME,
                "major": f"{code}|{major}",
                "admission_major": f"{code}|{major}",
                "ranking": data["ranking"],
                "remarks": 'official_admission_status: 拟录取; admission_method: 推免及"5+3"; physical_exam: 合格',
            }
        )
        rows.append(record)

    return rows


def curate_records(pdf_path: Path, layout_text_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    reader = PdfReader(str(pdf_path))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    exam_rows, skipped = parse_exam_records_from_text(text)
    recommendation_rows = parse_recommendation_records_from_layout(
        layout_text_path.read_text(encoding="utf-8", errors="ignore")
    )
    return exam_rows + recommendation_rows, skipped


def write_outputs(rows: list[dict[str, Any]], skipped: list[str], output_dir: Path, pdf_path: Path) -> dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    records_jsonl = output_dir / "records.jsonl"
    with records_jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    document = {
        "schema_version": "graduate_outcome_document/v1",
        "captured_at": "2026-06-02T20:20:00+08:00",
        "school_name": SCHOOL_NAME,
        "source_type": "official_site",
        "source_url": SOURCE_URL,
        "start_url": SOURCE_URL,
        "title": TITLE,
        "year": YEAR,
        "document_type": "master_admission_list",
        "matched_keywords": ["拟录取名单"],
        "content_type": "application/pdf",
        "parse_status": "curated_from_official_pdf_text_layer",
        "record_count": len(rows),
        "raw_path": str(pdf_path),
    }
    (output_dir / "documents.jsonl").write_text(json.dumps(document, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "curation_notes.txt").write_text(
        "官方 PDF 文本层定向抽取。保留拟录取且体检合格记录；"
        f"跳过未解析、缺少明确体检结果或非拟录取记录 {len(skipped)} 条。"
        "统考/调剂记录无姓名列，保留考生编号；推免及 5+3 记录无考生编号，保留姓名。\n\n"
        + "Skipped examples:\n"
        + "\n".join(skipped[:30]),
        encoding="utf-8",
    )

    clean_csv = output_dir / "records_clean_curated.csv"
    summary_csv = output_dir / "school_year_summary_curated.csv"
    public_csv = output_dir / "records_public_curated.csv"
    summary = crawler.clean_records_to_outputs(records_jsonl, clean_csv, summary_csv)
    public_summary = crawler.export_public_records_csv(clean_csv, public_csv)
    return {
        "curated_rows": len(rows),
        "skipped": len(skipped),
        **summary,
        **public_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pdf-path",
        type=Path,
        default=Path(
            "data/raw/official_site_recommendation_websearch_web_20260602_batch483_gszy_2024_master_pdf/"
            "yjsc.gszy.edu.cn/ff354842b2d38997.pdf"
        ),
    )
    parser.add_argument("--layout-text-path", type=Path, default=Path("tmp/gszy_2024_master_layout.txt"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/official_site_recommendation_websearch_web_20260602_batch483_gszy_2024_master_pdf_curated"),
    )
    args = parser.parse_args()

    rows, skipped = curate_records(args.pdf_path, args.layout_text_path)
    result = write_outputs(rows, skipped, args.output_dir, args.pdf_path)
    print(json.dumps(result | {"output_dir": str(args.output_dir)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
