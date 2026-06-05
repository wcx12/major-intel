from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


DEFAULT_PROCESSED_DIR = Path(
    "data/processed/official_site_recommendation_websearch_web_20260603_batch523_cnu_2026_hmt_admission"
)
DEFAULT_PDF = Path(
    "data/raw/official_site_recommendation_websearch_web_20260603_batch523_cnu_2026_hmt_admission/"
    "grad.cnu.edu.cn/cnu_2026_hmt_admission.pdf"
)
DEFAULT_OUTPUT_CSV = DEFAULT_PROCESSED_DIR / "records_clean_curated.csv"
DEFAULT_SUMMARY_CSV = DEFAULT_PROCESSED_DIR / "school_year_summary_curated.csv"
DEFAULT_PUBLIC_CSV = DEFAULT_PROCESSED_DIR / "records_public_curated.csv"
SOURCE_URL = "https://grad.cnu.edu.cn/docs/2026-05/bde11359fb1b491cb1d06454f3965b8e.pdf"
TITLE = "首都师范大学2026年面向港澳台地区招收硕士研究生拟录取名单"

ADMISSION_ROW_RE = re.compile(
    r"^(?P<student_id>\d{12,})\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<initial_score>\d+(?:\.\d+)?)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<admission_score>\d+(?:\.\d+)?)\s+"
    r"(?P<study_mode>\S+)$"
)


def curate_pdf_text(text: str, *, source_url: str = SOURCE_URL) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        match = ADMISSION_ROW_RE.match(line)
        if not match:
            continue

        data = match.groupdict()
        remarks = [
            f"initial_score {data['initial_score']}",
            f"reexam_score {data['reexam_score']}",
            f"admission_score {data['admission_score']}",
            f"study_mode {data['study_mode']}",
            "region 港澳台",
        ]
        rows.append(
            {
                "school_name": "首都师范大学",
                "year": 2026,
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name": data["person_name"],
                "student_id": data["student_id"],
                "undergraduate_school": "",
                "undergraduate_major": "",
                "college": "",
                "major": "",
                "admission_major": "",
                "ranking": "",
                "remarks": "; ".join(remarks),
                "source_url": source_url,
                "title": TITLE,
                "needs_review": False,
            }
        )

    return rows


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def curate_pdf(pdf_path: Path, *, source_url: str = SOURCE_URL) -> list[dict[str, Any]]:
    return curate_pdf_text(extract_pdf_text(pdf_path), source_url=source_url)


def write_outputs(
    *,
    pdf_path: Path = DEFAULT_PDF,
    output_csv: Path = DEFAULT_OUTPUT_CSV,
    summary_csv: Path = DEFAULT_SUMMARY_CSV,
    public_csv: Path = DEFAULT_PUBLIC_CSV,
) -> dict[str, int | str]:
    clean_rows = [crawler._clean_record(row) for row in curate_pdf(pdf_path)]
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
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
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
