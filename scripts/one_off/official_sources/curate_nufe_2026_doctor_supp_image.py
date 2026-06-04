from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


DEFAULT_PROCESSED_DIR = Path(
    "data/processed/official_site_recommendation_websearch_web_20260603_nufe_2026_doctor_supp_image"
)
DEFAULT_OUTPUT_CSV = DEFAULT_PROCESSED_DIR / "records_clean_curated.csv"
DEFAULT_SUMMARY_CSV = DEFAULT_PROCESSED_DIR / "school_year_summary_curated.csv"
DEFAULT_PUBLIC_CSV = DEFAULT_PROCESSED_DIR / "records_public_curated.csv"

SCHOOL_NAME = "南京财经大学"
YEAR = 2026
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"
SOURCE_PAGE = "https://yjsc.nufe.edu.cn/info/1012/6901.htm"
SOURCE_IMAGE = "https://yjsc.nufe.edu.cn/__local/A/C7/31/38635DF087259669397CAD93EEC_C1C13246_111C3.png"
TITLE = "南京财经大学2026年博士研究生递补拟录取名单公示（5月22日）"

PNG_TRANSCRIPTION_ROWS = [
    ("1", "李*林", "10327*******004", "227.5", "84.4", "78.403", "放弃拟录取"),
    ("2", "周*帆", "10327*******062", "214.5", "88.8", "76.690", "拟录取"),
]


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key} {_clean(value)}" for key, value in parts if _clean(value))


def _record_from_row(row: tuple[str, str, str, str, str, str, str]) -> dict[str, Any]:
    ranking, person_name, student_id, initial_score, reexam_score, composite_score, status = row
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": person_name,
            "student_id": student_id,
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": "",
            "major": "",
            "admission_major": "",
            "ranking": ranking,
            "remarks": _remarks(
                [
                    ("degree_level", "博士"),
                    ("admission_method", "普通招考递补"),
                    ("initial_score", initial_score),
                    ("reexam_score", reexam_score),
                    ("composite_score", composite_score),
                    ("official_admission_status", status),
                    ("source_page", SOURCE_PAGE),
                    ("source_image", SOURCE_IMAGE),
                    ("source_image_transcribed", "true"),
                ]
            ),
            "source_url": SOURCE_IMAGE,
            "title": TITLE,
            "needs_review": False,
        }
    )


def curate_records() -> list[dict[str, Any]]:
    return [_record_from_row(row) for row in PNG_TRANSCRIPTION_ROWS if row[6] == "拟录取"]


def write_outputs(
    *,
    output_csv: Path = DEFAULT_OUTPUT_CSV,
    summary_csv: Path = DEFAULT_SUMMARY_CSV,
    public_csv: Path = DEFAULT_PUBLIC_CSV,
) -> dict[str, int | str]:
    clean_rows = curate_records()
    crawler._write_clean_records_csv(clean_rows, output_csv)
    crawler._write_summary_csv(crawler._build_summary_rows(clean_rows), summary_csv)
    crawler.export_public_records_csv(output_csv, public_csv)
    notes_path = output_csv.parent / "curation_notes.txt"
    notes_path.write_text(
        "\n".join(
            [
                "nufe_2026_doctor_supp_image: manually transcribed the official NUFE doctoral supplement PNG table.",
                "Only the row with official_admission_status=拟录取 was retained; the row marked 放弃拟录取 was excluded.",
                f"rows={len(clean_rows)}",
                f"source_page={SOURCE_PAGE}",
                f"source_image={SOURCE_IMAGE}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "curated": len(clean_rows),
        "output_csv": str(output_csv),
        "summary_csv": str(summary_csv),
        "public_csv": str(public_csv),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY_CSV)
    parser.add_argument("--public-csv", type=Path, default=DEFAULT_PUBLIC_CSV)
    args = parser.parse_args()
    print(
        write_outputs(
            output_csv=args.output_csv,
            summary_csv=args.summary_csv,
            public_csv=args.public_csv,
        )
    )


if __name__ == "__main__":
    main()
