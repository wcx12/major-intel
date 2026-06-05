from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


DEFAULT_PROCESSED_DIR = Path(
    "data/processed/official_site_recommendation_websearch_web_20260603_batch524_bjfu_result_system"
)
DEFAULT_HTML = Path(
    "data/raw/official_site_recommendation_websearch_web_20260603_batch524_bjfu_result_system/"
    "tm.yzb.bjfu.edu.cn/result.html"
)
DEFAULT_OUTPUT_CSV = DEFAULT_PROCESSED_DIR / "records_clean_curated.csv"
DEFAULT_SUMMARY_CSV = DEFAULT_PROCESSED_DIR / "school_year_summary_curated.csv"
DEFAULT_PUBLIC_CSV = DEFAULT_PROCESSED_DIR / "records_public_curated.csv"
SOURCE_URL = "http://tm.yzb.bjfu.edu.cn/result"
TITLE_SUFFIX = "拟录取公示"
EXPECTED_HEADERS = ["id", "姓名", "身份证号", "学院", "专业编码号", "专业", "总分", "状态"]


def _cell_texts(row: Any) -> list[str]:
    return [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]


def _result_title(soup: BeautifulSoup) -> str:
    page_title = soup.title.get_text(" ", strip=True) if soup.title else "北京林业大学硕士推免预报名系统"
    if TITLE_SUFFIX in page_title:
        return page_title
    return f"{page_title}-{TITLE_SUFFIX}"


def curate_result_html(html: str, *, source_url: str = SOURCE_URL) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    title = _result_title(soup)
    rows: list[dict[str, Any]] = []

    for table in soup.find_all("table"):
        table_rows = table.find_all("tr")
        if not table_rows:
            continue
        headers = _cell_texts(table_rows[0])
        if headers != EXPECTED_HEADERS:
            continue

        for raw_row in table_rows[1:]:
            cells = _cell_texts(raw_row)
            if len(cells) != len(EXPECTED_HEADERS):
                continue
            ranking, person_name, student_id, college, major_code, major, total_score, status = cells
            if not ranking or not person_name or not status:
                continue
            remarks = [
                f"major_code {major_code}",
                f"total_score {total_score}",
                f"status {status}",
            ]
            rows.append(
                {
                    "school_name": "北京林业大学",
                    "year": 2026,
                    "document_type": "incoming_recommendation_admission_list",
                    "route": "recommendation_exemption",
                    "person_name": person_name,
                    "student_id": student_id,
                    "undergraduate_school": "",
                    "undergraduate_major": "",
                    "college": college,
                    "major": "",
                    "admission_major": major,
                    "ranking": ranking,
                    "remarks": "; ".join(remarks),
                    "source_url": source_url,
                    "title": title,
                    "needs_review": False,
                }
            )

    return rows


def curate_result_file(html_path: Path, *, source_url: str = SOURCE_URL) -> list[dict[str, Any]]:
    return curate_result_html(html_path.read_text(encoding="utf-8"), source_url=source_url)


def write_outputs(
    *,
    html_path: Path = DEFAULT_HTML,
    output_csv: Path = DEFAULT_OUTPUT_CSV,
    summary_csv: Path = DEFAULT_SUMMARY_CSV,
    public_csv: Path = DEFAULT_PUBLIC_CSV,
) -> dict[str, int | str]:
    clean_rows = [crawler._clean_record(row) for row in curate_result_file(html_path)]
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
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY_CSV)
    parser.add_argument("--public-csv", type=Path, default=DEFAULT_PUBLIC_CSV)
    args = parser.parse_args()
    print(
        write_outputs(
            html_path=args.html,
            output_csv=args.output_csv,
            summary_csv=args.summary_csv,
            public_csv=args.public_csv,
        )
    )


if __name__ == "__main__":
    main()
