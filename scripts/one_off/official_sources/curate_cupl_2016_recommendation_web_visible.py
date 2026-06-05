from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_TEXT = (
    ROOT
    / "data/raw/official_site_recommendation_web_visible_cupl_2016_recommendation/"
    "cupl_2016_recommendation_pdf_text.txt"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "data/processed/official_site_recommendation_web_visible_cupl_2016_recommendation"
)
SOURCE_URL = "https://yjsy.cupl.edu.cn/__local/F/A7/C1/8ADD9DF90D6785F9E640FEEC6B4_9C484C17_1C7F7.pdf?e=.pdf"
TITLE = "中国政法大学2016年推免生拟录取名单"
SCHOOL_NAME = "中国政法大学"

ROW_RE = re.compile(
    r"^(?P<ranking>\d{1,3})\s+"
    r"(?P<name>[\u4e00-\u9fff*]{2,6})\s+"
    r"(?P<identity>[0-9Xx*]{15,20})\s+"
    r"(?P<college>\S+)\s+"
    r"(?P<major>\S+)\s+"
    r"(?P<score>\d+(?:\.\d+)?)$"
)


def extract_records_from_text(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line.strip())
        if not line:
            continue
        match = ROW_RE.match(line)
        if not match:
            continue
        major = match.group("major")
        rows.append(
            {
                "school_name": SCHOOL_NAME,
                "year": 2016,
                "document_type": "incoming_recommendation_admission_list",
                "route": "recommendation_exemption",
                "person_name": match.group("name"),
                "student_id": match.group("identity"),
                "undergraduate_school": "",
                "undergraduate_major": "",
                "college": match.group("college"),
                "major": major,
                "admission_major": major,
                "ranking": match.group("ranking"),
                "remarks": (
                    "official_web_visible_pdf_text; "
                    "source_columns: 序号/姓名/证件号码/拟录取学院/拟录取专业/复试成绩; "
                    f"复试成绩 {match.group('score')}"
                ),
                "source_url": SOURCE_URL,
                "title": TITLE,
                "needs_review": False,
            }
        )
    return rows


def write_outputs(
    *,
    raw_text_path: Path = DEFAULT_RAW_TEXT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, int | str]:
    text = raw_text_path.read_text(encoding="utf-8")
    clean_rows = [crawler._clean_record(row) for row in extract_records_from_text(text)]
    output_dir.mkdir(parents=True, exist_ok=True)
    clean_csv = output_dir / "records_clean_curated.csv"
    summary_csv = output_dir / "school_year_summary_curated.csv"
    public_csv = output_dir / "records_public_curated.csv"
    crawler._write_clean_records_csv(clean_rows, clean_csv)
    crawler._write_summary_csv(crawler._build_summary_rows(clean_rows), summary_csv)
    crawler.export_public_records_csv(clean_csv, public_csv)
    return {
        "curated": len(clean_rows),
        "output_csv": str(clean_csv),
        "summary_csv": str(summary_csv),
        "public_csv": str(public_csv),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-text-path", type=Path, default=DEFAULT_RAW_TEXT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    print(write_outputs(raw_text_path=args.raw_text_path, output_dir=args.output_dir))


if __name__ == "__main__":
    main()
