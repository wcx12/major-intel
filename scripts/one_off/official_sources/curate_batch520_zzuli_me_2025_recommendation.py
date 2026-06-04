from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


DEFAULT_PROCESSED_DIR = Path(
    "data/processed/official_site_recommendation_websearch_web_20260602_batch520_zzuli_me_2025_recommendation"
)
DEFAULT_RAW_PDF = Path(
    "data/raw/official_site_recommendation_websearch_web_20260602_batch520_zzuli_me_2025_recommendation/"
    "me.zzuli.edu.cn/d4276e77c63beee0.pdf"
)
DEFAULT_OUTPUT_CSV = DEFAULT_PROCESSED_DIR / "records_clean_curated.csv"
DEFAULT_SUMMARY_CSV = DEFAULT_PROCESSED_DIR / "school_year_summary_curated.csv"
DEFAULT_PUBLIC_CSV = DEFAULT_PROCESSED_DIR / "records_public_curated.csv"
SOURCE_URL = (
    "https://me.zzuli.edu.cn/_upload/article/files/c8/7e/"
    "524b816646a98f098b2d8564a02d/fdf19b57-c0a2-43e4-9f69-dfacd7b8ab3d.pdf"
)
TITLE = "公示材料--机电工程学院研究生推免.pdf"
SCHOOL_NAME = "郑州轻工业大学"
COLLEGE = "机电工程学院"
MECHANICAL_MAJOR = "机械设计制造及其自动化"

MAJOR_BY_NAME = {
    "王佳音": MECHANICAL_MAJOR,
    "潘学立": MECHANICAL_MAJOR,
    "许晴": MECHANICAL_MAJOR,
    "冯喆林": MECHANICAL_MAJOR,
    "殷文豪": MECHANICAL_MAJOR,
    "刘少英": MECHANICAL_MAJOR,
    "秦存鑫": MECHANICAL_MAJOR,
    "李思博": MECHANICAL_MAJOR,
    "孙雪婷": "车辆工程",
    "张开贻": "测控技术与仪器",
    "黄福": "智能制造工程",
}

ROW_RE = re.compile(
    r"(?P<prefix>.*?)"
    r"(?P<student_id>54\d{10})\s+"
    r"(?P<name>[\u4e00-\u9fff]{2,4})\s+"
    r"(?P<rank>\d+)\s+"
    r"(?P<score_a>\d+(?:\.\d+)?)\s+"
    r"(?P<score_b>\d+(?:\.\d+)?)"
    r"(?P<trailing>.*同意推免)"
)


def extract_approved_rows_from_text(
    text: str,
    *,
    source_url: str = SOURCE_URL,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_major = MECHANICAL_MAJOR
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "二、科研成果" in line:
            break
        if "车辆工程" in line:
            current_major = "车辆工程"
        elif "测控技术" in line or "与仪器" in line:
            current_major = "测控技术与仪器"
        elif "智能" in line or "制造工程" in line:
            current_major = "智能制造工程"

        match = ROW_RE.search(line)
        if not match:
            continue
        name = match.group("name")
        major = MAJOR_BY_NAME.get(name, current_major)
        rows.append(
            {
                "school_name": SCHOOL_NAME,
                "year": 2025,
                "document_type": "recommendation_exemption_list",
                "route": "recommendation_exemption",
                "person_name": name,
                "student_id": match.group("student_id"),
                "undergraduate_school": "",
                "undergraduate_major": "",
                "college": COLLEGE,
                "major": major,
                "admission_major": "",
                "ranking": match.group("rank"),
                "remarks": (
                    "recommendation_status 同意推免; "
                    f"综合成绩 {match.group('score_a')}; "
                    f"综合素质分 {match.group('score_b')}"
                ),
                "source_url": source_url,
                "title": TITLE,
                "needs_review": False,
            }
        )
    return rows


def extract_pdf_text(pdf_path: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), "-"],
        check=True,
        capture_output=True,
    )
    return completed.stdout.decode("utf-8", errors="replace")


def write_outputs(
    *,
    pdf_path: Path = DEFAULT_RAW_PDF,
    output_csv: Path = DEFAULT_OUTPUT_CSV,
    summary_csv: Path = DEFAULT_SUMMARY_CSV,
    public_csv: Path = DEFAULT_PUBLIC_CSV,
) -> dict[str, int | str]:
    text = extract_pdf_text(pdf_path)
    curated_raw_rows = extract_approved_rows_from_text(text)
    clean_rows = [crawler._clean_record(row) for row in curated_raw_rows]
    crawler._write_clean_records_csv(clean_rows, output_csv)
    crawler._write_summary_csv(crawler._build_summary_rows(clean_rows), summary_csv)
    crawler.export_public_records_csv(output_csv, public_csv)
    return {
        "curated": len(clean_rows),
        "output_csv": str(output_csv),
        "summary_csv": str(summary_csv),
        "public_csv": str(public_csv),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=DEFAULT_RAW_PDF)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY_CSV)
    parser.add_argument("--public-csv", type=Path, default=DEFAULT_PUBLIC_CSV)
    args = parser.parse_args()
    print(
        write_outputs(
            pdf_path=args.pdf,
            output_csv=args.output_csv,
            summary_csv=args.summary_csv,
            public_csv=args.public_csv,
        )
    )


if __name__ == "__main__":
    main()
