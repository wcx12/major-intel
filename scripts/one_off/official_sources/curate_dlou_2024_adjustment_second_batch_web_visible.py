from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


DEFAULT_RAW_TEXT = Path(
    "data/raw/official_site_recommendation_web_visible_dlou_2024_adjustment_second_batch/"
    "dlou_2024_adjustment_second_batch_pdf_text.txt"
)
DEFAULT_PROCESSED_DIR = Path(
    "data/processed/official_site_recommendation_web_visible_dlou_2024_adjustment_second_batch"
)
DEFAULT_OUTPUT_CSV = DEFAULT_PROCESSED_DIR / "records_clean_curated.csv"
DEFAULT_SUMMARY_CSV = DEFAULT_PROCESSED_DIR / "school_year_summary_curated.csv"
DEFAULT_PUBLIC_CSV = DEFAULT_PROCESSED_DIR / "records_public_curated.csv"

SCHOOL_NAME = "大连海洋大学"
YEAR = 2024
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"
SOURCE_URL = (
    "https://www.dlou.edu.cn/_upload/article/files/e7/fb/e8bdbb4040f4a9987ac2d09f5ee4/"
    "d048fe33-6d3d-463f-8c74-203b3176890b.pdf"
)
TITLE = "大连海洋大学2024年硕士研究生招生调剂考生拟录取名单（二批）"
LOCAL_FETCH_ARTIFACT = "tmp/dlou_2024_adjustment_second_batch_pdf_current.pdf"
LOCAL_FETCH_HEADERS = "tmp/dlou_2024_adjustment_second_batch_pdf_current.headers.txt"

ROW_RE = re.compile(
    r"^(?P<ranking>\d+)\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<student_id>\d{12,})\s+"
    r"(?P<college_code>\d{3})\s+"
    r"(?P<college>\S+)\s+"
    r"(?P<major>\d{6}\S+)\s+"
    r"(?P<research_direction>\S+)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<admission_score>\d+(?:\.\d+)?)\s+"
    r"(?P<admission_type>非定向|定向)"
    r"(?:\s+(?P<note>.+))?$"
)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key} {_clean(value)}" for key, value in parts if _clean(value))


def _record_from_match(match: re.Match[str]) -> dict[str, Any]:
    data = match.groupdict(default="")
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": data["person_name"],
            "student_id": data["student_id"],
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": data["college"],
            "major": data["major"],
            "admission_major": data["major"],
            "ranking": data["ranking"],
            "remarks": _remarks(
                [
                    ("college_code", data["college_code"]),
                    ("research_direction", data["research_direction"]),
                    ("study_mode", data["study_mode"]),
                    ("admission_score", data["admission_score"]),
                    ("admission_type", data["admission_type"]),
                    ("note", data["note"]),
                    ("official_web_visible_pdf_text", "true"),
                    ("local_pdf_fetch", "HTTP 404 196_byte_html"),
                    ("local_fetch_artifact", LOCAL_FETCH_ARTIFACT),
                ]
            ),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
    )


def curate_text(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = _clean(raw_line)
        match = ROW_RE.match(line)
        if match:
            rows.append(_record_from_match(match))
    return rows


def curate_raw_text(path: Path = DEFAULT_RAW_TEXT) -> list[dict[str, Any]]:
    return curate_text(path.read_text(encoding="utf-8"))


def write_outputs(
    *,
    raw_text: Path = DEFAULT_RAW_TEXT,
    output_csv: Path = DEFAULT_OUTPUT_CSV,
    summary_csv: Path = DEFAULT_SUMMARY_CSV,
    public_csv: Path = DEFAULT_PUBLIC_CSV,
) -> dict[str, int | str]:
    clean_rows = curate_raw_text(raw_text)
    crawler._write_clean_records_csv(clean_rows, output_csv)
    crawler._write_summary_csv(crawler._build_summary_rows(clean_rows), summary_csv)
    crawler.export_public_records_csv(output_csv, public_csv)
    notes_path = output_csv.parent / "curation_notes.txt"
    notes_path.write_text(
        "\n".join(
            [
                "dlou_2024_adjustment_second_batch_web_visible: parsed official web-visible PDF text for Dalian Ocean University 2024 second-batch adjustment admitted list.",
                "Local current PDF fetch returned HTTP 404 and a 196-byte HTML body, so the official web-visible PDF text is retained with explicit provenance.",
                f"rows={len(clean_rows)}",
                f"source_pdf={SOURCE_URL}",
                f"local_fetch_artifact={LOCAL_FETCH_ARTIFACT}",
                f"local_fetch_headers={LOCAL_FETCH_HEADERS}",
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
    parser.add_argument("--raw-text", type=Path, default=DEFAULT_RAW_TEXT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--summary-csv", type=Path, default=DEFAULT_SUMMARY_CSV)
    parser.add_argument("--public-csv", type=Path, default=DEFAULT_PUBLIC_CSV)
    args = parser.parse_args()
    print(
        write_outputs(
            raw_text=args.raw_text,
            output_csv=args.output_csv,
            summary_csv=args.summary_csv,
            public_csv=args.public_csv,
        )
    )


if __name__ == "__main__":
    main()
