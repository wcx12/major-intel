from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RECORDS_CSV = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch241_xidian_math_admission/records.csv"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch241_xidian_math_admission_curated"
)

SCHOOL_NAME = "西安电子科技大学"
YEAR = 2025
COLLEGE = "数学与统计学院"


def _clean_text(value: Any) -> str:
    return str(value or "").replace("\ufeff", "").strip()


def curate_records(records_csv: Path = RECORDS_CSV) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with records_csv.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if _clean_text(row.get("school_name")) != SCHOOL_NAME:
                continue
            record = {
                **row,
                "school_name": SCHOOL_NAME,
                "year": YEAR,
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "college": COLLEGE,
                "major": _clean_text(row.get("admission_major")),
                "admission_major": _clean_text(row.get("admission_major")),
                "person_name": _clean_text(row.get("person_name")),
                "student_id": _clean_text(row.get("student_id")),
                "source_url": _clean_text(row.get("source_url")),
                "title": _clean_text(row.get("title")),
                "needs_review": False,
            }
            rows.append(crawler._clean_record(record))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
