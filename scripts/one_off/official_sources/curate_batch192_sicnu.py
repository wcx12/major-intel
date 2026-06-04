from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


INPUT_CSV = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch192_sicnu/records.csv")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch192_sicnu_curated")
DROP_SOURCE_URLS = {
    "https://yjsc.sicnu.edu.cn/files/yjs/news/639129848568869336_d.pdf",
}
DROP_BAD_TERMS = (
    "是否拟录取: 否",
    "放弃复试",
    "拟不录取",
    "不予录取",
    "进入复试名单",
    "复试不合格",
    "不录取",
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _keep_row(row: dict[str, str]) -> bool:
    if row.get("source_url") in DROP_SOURCE_URLS:
        return False
    if not row.get("person_name"):
        return False
    if (row.get("needs_review") or "").lower() == "true":
        return False
    haystack = " ".join(str(value) for value in row.values())
    return not any(term in haystack for term in DROP_BAD_TERMS)


def curate_records(input_csv: Path = INPUT_CSV) -> list[dict[str, Any]]:
    rows = []
    for row in _read_csv(input_csv):
        if not _keep_row(row):
            continue
        normalized: dict[str, Any] = dict(row)
        normalized["needs_review"] = (row.get("needs_review") or "").lower() == "true"
        rows.append(crawler._clean_record(normalized))
    rows.sort(
        key=lambda row: (
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
        "batch192_sicnu_curated: retained official SICNU 2026 first and second batch master admission PDF rows.",
        "Dropped third-batch PDF row because generic extraction produced one shifted score-only noise record.",
        f"rows={len(rows)}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
