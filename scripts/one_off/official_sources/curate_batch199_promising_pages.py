from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


INPUT_CSV = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch199_promising_pages/records.csv")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch199_promising_pages_curated")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _is_batch199_noise(row: dict[str, str]) -> bool:
    name = (row.get("person_name") or "").strip()
    if not name:
        return True
    if re.match(r"^第\s*\d+\s*页，共\s*\d+\s*页$", name):
        return True
    if "哈尔滨商业大学2026年硕士研究生招生考试一志愿拟录取名单" in name:
        return True
    if (row.get("needs_review") or "").lower() == "true":
        return True
    return False


def curate_records(input_csv: Path = INPUT_CSV) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _read_csv(input_csv):
        if _is_batch199_noise(row):
            continue
        normalized: dict[str, Any] = dict(row)
        normalized["needs_review"] = (row.get("needs_review") or "").lower() == "true"
        rows.append(crawler._clean_record(normalized))
    rows.sort(
        key=lambda row: (
            str(row.get("school_name") or ""),
            str(row.get("source_url") or ""),
            str(row.get("college") or ""),
            str(row.get("admission_major") or ""),
            str(row.get("person_name") or ""),
            str(row.get("student_id") or ""),
        )
    )
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch199_promising_pages_curated: retained parsed official PDFs for SXUFE, JMSU, HrbCU, and QHMU.",
        "Dropped HrbCU repeated page numbers and PDF title rows emitted by generic extraction.",
        f"rows={len(rows)}",
        f"schools={len({row.get('school_name') for row in rows})}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
