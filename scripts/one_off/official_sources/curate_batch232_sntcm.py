from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_PDF = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch232_sntcm/"
    "img.sntcm.edu.cn/9e1e9668227c91d4.pdf"
)
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch232_sntcm_curated")

SOURCE_URL = "http://img.sntcm.edu.cn/HIWCMyzb/202604/202604040418058.pdf"
TITLE = "2026年陕西中医药大学硕士研究生拟录取考生名单公示（一志愿）"

ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d{3})\s+"
    r"(?P<person_name>.+?)\s+"
    r"(?P<student_id>\d{15})\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<composite_score>\d+(?:\.\d+)?)\s+"
    r"(?P<major_code>\d{6})\s*$"
)

POLICY_MARKERS = (
    ("***", "退役大学生加分"),
    ("**", "三支一扶计划"),
    ("*", "大学生志愿服务西部计划"),
    ("▲", "退役大学生士兵计划"),
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _pdf_text(path: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.splitlines()


def _clean_name_and_policy(value: str) -> tuple[str, str]:
    name = re.sub(r"\s+", "", value)
    policies: list[str] = []
    for marker, policy in POLICY_MARKERS:
        if marker in name:
            name = name.replace(marker, "")
            policies.append(policy)
    return name, "; ".join(policies)


def _parse_line(line: str) -> dict[str, str] | None:
    match = ROW_RE.match(line)
    if not match:
        return None
    parsed = match.groupdict()
    parsed["person_name"], parsed["policy"] = _clean_name_and_policy(parsed["person_name"])
    return parsed


def _record(base: dict[str, Any]) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": "陕西中医药大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
            **base,
        }
    )


def curate_records(raw_pdf: Path = RAW_PDF) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in _pdf_text(raw_pdf):
        parsed = _parse_line(line)
        if not parsed:
            continue
        rows.append(
            _record(
                {
                    "person_name": parsed["person_name"],
                    "student_id": parsed["student_id"],
                    "major": parsed["major_code"],
                    "ranking": parsed["ranking"],
                    "remarks": _remarks(
                        f"initial_score {parsed['initial_score']}",
                        f"reexam_score {parsed['reexam_score']}",
                        f"composite_score {parsed['composite_score']}",
                        parsed["policy"],
                    ),
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
