from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


INPUT_CSV = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch261_ustl_doctor_admission/"
    "records.csv"
)
PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch261_ustl_doctor_admission/"
    "www.ustl.edu.cn/d85c95685aa7006a.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch261_ustl_doctor_admission_curated"
)

SOURCE_URL = "https://www.ustl.edu.cn/__local/B/40/97/A3412639680E6B74A5353D9A038_100A03EA_2749A.pdf"
TITLE = "辽宁科技大学2026年博士研究生拟录取名单"

ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d+)\s+"
    r"(?P<program>.+?)\s+"
    r"(?P<student_id>\d{15})\s+"
    r"(?P<person_name>[\u4e00-\u9fff*·]{1,8})\s+"
    r"(?P<gender>[男女])\s+"
    r"(?P<advisor_id>\d{6})\s+"
    r"(?P<advisor_name>[\u4e00-\u9fff*·]+)\s+"
    r"(?P<rest>.+?)\s*$"
)

MAJOR_NAMES = (
    "材料科学与工程",
    "控制科学与工程",
    "化学工程与技术",
    "低碳技术与工程",
    "冶金工程",
)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _split_program(program: str) -> tuple[str, str]:
    compact = _clean(program)
    for major in MAJOR_NAMES:
        if compact.endswith(major):
            return compact[: -len(major)].strip(), major
    raise ValueError(f"Unable to split USTL college/major text: {program!r}")


def _remarks(match: re.Match[str]) -> str:
    rest = _clean(match.group("rest"))
    return "; ".join(
        part
        for part in (
            f"性别: {match.group('gender')}",
            f"导师编号: {match.group('advisor_id')}",
            f"导师姓名: {match.group('advisor_name')}",
            f"录取信息: {rest}",
        )
        if part
    )


def curate_records(input_csv: Path | None = None, pdf_path: Path | None = None) -> list[dict[str, Any]]:
    _ = input_csv
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = ROW_RE.match(_clean(line))
        if not match:
            continue
        college, major = _split_program(match.group("program"))
        rows.append(
            crawler._clean_record(
                {
                    "school_name": "辽宁科技大学",
                    "year": 2026,
                    "document_type": "postgraduate_admission_list",
                    "route": "postgraduate_exam_or_admission",
                    "person_name": match.group("person_name"),
                    "student_id": match.group("student_id"),
                    "college": college,
                    "major": major,
                    "admission_major": "",
                    "ranking": match.group("ranking"),
                    "remarks": _remarks(match),
                    "source_url": SOURCE_URL,
                    "title": TITLE,
                    "needs_review": False,
                }
            )
        )
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
