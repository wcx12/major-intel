from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


DEFAULT_PROCESSED_DIR = Path(
    "data/processed/official_site_recommendation_websearch_web_20260602_batch519_gdpu_2026_recommendation"
)
DEFAULT_INPUT_CSV = DEFAULT_PROCESSED_DIR / "records.csv"
DEFAULT_OUTPUT_CSV = DEFAULT_PROCESSED_DIR / "records_clean_curated.csv"
DEFAULT_SUMMARY_CSV = DEFAULT_PROCESSED_DIR / "school_year_summary_curated.csv"
DEFAULT_PUBLIC_CSV = DEFAULT_PROCESSED_DIR / "records_public_curated.csv"
FORMAL_RECOMMENDATION_COUNT = 12


def _clean(value: Any) -> str:
    return str(value or "").strip()


def curate_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records[:FORMAL_RECOMMENDATION_COUNT]:
        name = _clean(record.get("person_name"))
        if not name:
            continue
        row = {
            "school_name": "广东药科大学",
            "year": 2026,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": name,
            "student_id": _clean(record.get("student_id")),
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": "第一临床医学院",
            "major": _clean(record.get("major")),
            "admission_major": _clean(record.get("admission_major")),
            "ranking": "",
            "remarks": "recommendation_status 正式推荐",
            "source_url": _clean(record.get("source_url")),
            "title": _clean(record.get("title")),
            "needs_review": False,
        }
        rows.append(row)
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
