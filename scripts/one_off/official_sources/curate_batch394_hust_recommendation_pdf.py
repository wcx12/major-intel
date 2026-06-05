from __future__ import annotations

import csv
import re
from pathlib import Path

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


IN_DIR = Path("data/processed/official_site_recommendation_websearch_web_20260602_batch394_hust_recommendation_pdf")
OUT_DIR = Path("data/processed/official_site_recommendation_websearch_web_20260602_batch394_hust_recommendation_pdf_curated")
IN_CLEAN = IN_DIR / "records_clean.csv"
OUT_CLEAN = OUT_DIR / "records_clean_curated.csv"
OUT_PUBLIC = OUT_DIR / "records_public_curated.csv"
OUT_SUMMARY = OUT_DIR / "school_year_summary_curated.csv"


def is_page_number_name(value: str) -> bool:
    return bool(re.fullmatch(r"\s*\d+\s*/\s*\d+\s*", value or ""))


def curate_clean_rows(path: Path = IN_CLEAN) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return [row for row in rows if not is_page_number_name(row.get("person_name", ""))]


def main() -> None:
    rows = curate_clean_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_CLEAN)
    crawler.export_public_records_csv(OUT_CLEAN, OUT_PUBLIC)
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_SUMMARY)
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch394_hust_recommendation_pdf_curated: filtered PDF page-number footer pseudo-records from the official HUST 2024 recommendation admission PDF.",
                "The removed rows had person_name values matching N/N, e.g. 1/99 through 99/99.",
                f"input_rows={sum(1 for _ in csv.DictReader(IN_CLEAN.open('r', encoding='utf-8-sig', newline='')))}",
                f"curated_rows={len(rows)}",
                "source_pdf=https://gszs.hust.edu.cn/__local/D/9F/71/CE5F0511A0D45E40D020485F894_5E25830F_FCCF6.pdf",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_CLEAN)})


if __name__ == "__main__":
    main()
