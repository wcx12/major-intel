from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


DEFAULT_PROCESSED_DIR = Path(
    "data/processed/official_site_recommendation_websearch_web_20260602_batch518_synu_2026_recommendation"
)
DEFAULT_INPUT_CSV = DEFAULT_PROCESSED_DIR / "records.csv"
DEFAULT_OUTPUT_CSV = DEFAULT_PROCESSED_DIR / "records_clean_curated.csv"
DEFAULT_SUMMARY_CSV = DEFAULT_PROCESSED_DIR / "school_year_summary_curated.csv"
DEFAULT_PUBLIC_CSV = DEFAULT_PROCESSED_DIR / "records_public_curated.csv"

PDF_NAME_RE = re.compile(r"^\s*\d{17}[\dXx]\s+([\u4e00-\u9fff]{2,4})\s+[男女]\s*$")
CHINESE_NAME_RE = re.compile(r"^[\u4e00-\u9fff]{2,4}$")


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _base_row(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "school_name": "沈阳师范大学",
        "year": 2026,
        "document_type": "recommendation_exemption_list",
        "route": "recommendation_exemption",
        "person_name": "",
        "student_id": _clean(record.get("student_id")),
        "undergraduate_school": "",
        "undergraduate_major": "",
        "college": _clean(record.get("college")),
        "major": _clean(record.get("major")),
        "admission_major": _clean(record.get("admission_major")),
        "ranking": _clean(record.get("ranking")),
        "remarks": _clean(record.get("remarks")),
        "source_url": _clean(record.get("source_url")),
        "title": _clean(record.get("title")),
        "needs_review": False,
    }


def _curate_pdf_row(record: dict[str, Any]) -> dict[str, Any] | None:
    if _clean(record.get("ranking")) != "正选":
        return None

    match = PDF_NAME_RE.match(_clean(record.get("person_name")))
    if not match:
        return None

    row = _base_row(record)
    row["person_name"] = match.group(1)
    row["college"] = _clean(record.get("major")) or _clean(record.get("college"))
    row["major"] = ""
    row["ranking"] = "正选"
    row["remarks"] = "selection_status 正选"
    return row


def _curate_wxy_row(record: dict[str, Any]) -> dict[str, Any] | None:
    name = _clean(record.get("person_name"))
    if not CHINESE_NAME_RE.fullmatch(name):
        return None

    row = _base_row(record)
    row["person_name"] = name
    row["college"] = "文学院"
    row["ranking"] = ""
    return row


def curate_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        source_url = _clean(record.get("source_url"))
        if "hxhg.synu.edu.cn" in source_url:
            curated = _curate_pdf_row(record)
        elif "wxy.synu.edu.cn" in source_url:
            curated = _curate_wxy_row(record)
        else:
            curated = None
        if curated:
            rows.append(curated)
    return rows


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_outputs(
    *,
    input_csv: Path = DEFAULT_INPUT_CSV,
    output_csv: Path = DEFAULT_OUTPUT_CSV,
    summary_csv: Path = DEFAULT_SUMMARY_CSV,
    public_csv: Path = DEFAULT_PUBLIC_CSV,
) -> dict[str, int | str]:
    source_rows = _read_csv(input_csv)
    curated_raw_rows = curate_rows(source_rows)
    clean_rows = [crawler._clean_record(row) for row in curated_raw_rows]
    crawler._write_clean_records_csv(clean_rows, output_csv)
    crawler._write_summary_csv(crawler._build_summary_rows(clean_rows), summary_csv)
    crawler.export_public_records_csv(output_csv, public_csv)
    return {
        "input": len(source_rows),
        "curated": len(clean_rows),
        "output_csv": str(output_csv),
        "summary_csv": str(summary_csv),
        "public_csv": str(public_csv),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT_CSV)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY_CSV)
    parser.add_argument("--public-csv", type=Path, default=DEFAULT_PUBLIC_CSV)
    args = parser.parse_args()
    print(
        write_outputs(
            input_csv=args.input_csv,
            output_csv=args.output_csv,
            summary_csv=args.summary_csv,
            public_csv=args.public_csv,
        )
    )


if __name__ == "__main__":
    main()
