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
    "data/raw/official_site_recommendation_web_visible_ymu_2025_recommendation/"
    "ymu_2025_recommendation_pdf_text.txt"
)
DEFAULT_PROCESSED_DIR = Path(
    "data/processed/official_site_recommendation_web_visible_ymu_2025_recommendation"
)
DEFAULT_OUTPUT_CSV = DEFAULT_PROCESSED_DIR / "records_clean_curated.csv"
DEFAULT_SUMMARY_CSV = DEFAULT_PROCESSED_DIR / "school_year_summary_curated.csv"
DEFAULT_PUBLIC_CSV = DEFAULT_PROCESSED_DIR / "records_public_curated.csv"

SCHOOL_NAME = "云南民族大学"
YEAR = 2025
DOCUMENT_TYPE = "incoming_recommendation_admission_list"
ROUTE = "recommendation_exemption"
SOURCE_PAGE = "https://web.ymu.edu.cn/yjsy/info/1201/3131.htm"
SOURCE_URL = "https://web.ymu.edu.cn/__local/5/86/BA/EC4D50E9EABCAC4B3283EF800D2_ED4BFA46_151C7.pdf"
TITLE = "云南民族大学2025年拟录取推免生名单"
LOCAL_FETCH_ARTIFACT = "tmp/ymu_2025_recommendation_pdf_retest_current.pdf"
LOCAL_FETCH_HEADERS = "tmp/ymu_2025_recommendation_pdf_retest_current.headers.txt"

ROW_RE = re.compile(
    r"^(?P<ranking>\d+)\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<college>\S+)\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<admission_major>\S+)"
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
            "student_id": "",
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": data["college"],
            "major": data["admission_major"],
            "admission_major": data["admission_major"],
            "ranking": data["ranking"],
            "remarks": _remarks(
                [
                    ("reexam_score", data["reexam_score"]),
                    ("major_code", data["major_code"]),
                    ("note", data["note"]),
                    ("official_web_visible_pdf_text", "true"),
                    ("local_pdf_fetch", "HTTP 521 __jsl_clearance_s"),
                    ("local_fetch_artifact", LOCAL_FETCH_ARTIFACT),
                    ("source_page", SOURCE_PAGE),
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
                "ymu_2025_recommendation_web_visible: parsed official web-visible PDF text for Yunnan Minzu University 2025 recommendation-exemption admitted list.",
                "Local current PDF fetch returned HTTP 521 and an __jsl_clearance_s JavaScript response, so the official web-visible PDF text is retained with explicit provenance.",
                f"rows={len(clean_rows)}",
                f"source_page={SOURCE_PAGE}",
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
