from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch240_swpu_admission_pdfs"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch240_swpu_admission_pdfs_curated"
)

SCHOOL_NAME = "西南石油大学"
YEAR = 2025

PETRO_TITLE = "西南石油大学石油与天然气工程学院2025年硕士研究生递补拟录取名单公示"
PETRO_SOURCE_URL = "https://www.swpu.edu.cn/__local/8/15/C7/92E70E0AC85E6ADA3E0D0EB5EEC_5CAC0528_2642D.pdf"
PETRO_COLLEGE = "石油与天然气工程学院"

CIVIL_TITLE = "西南石油大学土木工程与测绘学院2025年硕士研究生调剂第一批拟录取名单公示"
CIVIL_SOURCE_URL = "https://www.swpu.edu.cn/__local/2/3D/18/462CA89B77DEAFBE7381FAAFCB4_3FD01EB0_FB65.pdf"
CIVIL_COLLEGE = "土木工程与测绘学院"

PETRO_ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<admission_major>\d{6}-\S+)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<student_id>[0-9*Xx]{10,})\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)\s*$"
)

CIVIL_ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<major_name>.+?)\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<student_id>[0-9*Xx]{10,})\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)\s*$"
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _pdf_text(path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def _record(
    *,
    parsed: dict[str, str],
    college: str,
    source_url: str,
    title: str,
    admission_major: str,
) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": parsed["person_name"],
            "student_id": parsed["student_id"],
            "college": college,
            "major": admission_major,
            "admission_major": admission_major,
            "ranking": parsed["ranking"],
            "source_url": source_url,
            "title": title,
            "needs_review": False,
            "remarks": _remarks(
                f"study_mode {parsed['study_mode']}",
                f"initial_score {parsed['initial_score']}",
                f"reexam_score {parsed['reexam_score']}",
                f"total_score {parsed['total_score']}",
            ),
        }
    )


def _parse_petro(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = PETRO_ROW_RE.match(line)
        if match:
            parsed = match.groupdict(default="")
            rows.append(
                _record(
                    parsed=parsed,
                    college=PETRO_COLLEGE,
                    source_url=PETRO_SOURCE_URL,
                    title=PETRO_TITLE,
                    admission_major=parsed["admission_major"],
                )
            )
    return rows


def _parse_civil(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = CIVIL_ROW_RE.match(line)
        if match:
            parsed = match.groupdict(default="")
            admission_major = f"{parsed['major_code']} {_clean_text(parsed['major_name'])}"
            rows.append(
                _record(
                    parsed=parsed,
                    college=CIVIL_COLLEGE,
                    source_url=CIVIL_SOURCE_URL,
                    title=CIVIL_TITLE,
                    admission_major=admission_major,
                )
            )
    return rows


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("**/*.pdf")):
        text = _pdf_text(path)
        if "石油与天然气工程学院 2025 年硕士研究生递补拟录取名单" in text:
            rows.extend(_parse_petro(text))
        elif "土木工程与" in text and "调剂第一批次" in text:
            rows.extend(_parse_civil(text))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
