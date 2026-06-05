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
    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch231_sxnu_doctor/"
    "grc.sxnu.edu.cn/93e5100ec3f18af1.pdf"
)
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch231_sxnu_doctor_curated")

SOURCE_URL = "https://grc.sxnu.edu.cn/__local/9/76/BC/DE6CBD556A901D06BAEC8EA2DAD_7E02CD11_13685.pdf"
TITLE = "山西师范大学2026年招收以普通招考方式攻读博士学位研究生拟录取名单公示"

STUDENT_ID_RE = re.compile(r"\d{15}")
DISCIPLINE_RE = re.compile(r"^(?P<major_code>\d{6})\s+(?P<admission_major>.+)$")
TAIL_RE = re.compile(
    r"^(?P<person_name>.+?)\s+"
    r"(?P<english_score>\d+(?:\.\d+)?)\s+"
    r"(?P<subject1_score>\d+(?:\.\d+)?)\s+"
    r"(?P<subject2_score>\d+(?:\.\d+)?)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<weighted_score>\d+(?:\.\d+)?)$"
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _clean_person_name(value: str) -> str:
    return re.sub(r"\s+", "", value)


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


def _parse_line(line: str) -> dict[str, str] | None:
    sid_match = STUDENT_ID_RE.search(line)
    if not sid_match:
        return None

    discipline = _clean_text(line[: sid_match.start()])
    tail = _clean_text(line[sid_match.end() :])
    discipline_match = DISCIPLINE_RE.match(discipline)
    tail_match = TAIL_RE.match(tail)
    if not discipline_match or not tail_match:
        return None

    parsed = {
        "student_id": sid_match.group(0),
        "major": discipline_match.group("major_code"),
        "admission_major": _clean_text(discipline_match.group("admission_major")),
        **tail_match.groupdict(),
    }
    parsed["person_name"] = _clean_person_name(parsed["person_name"])
    return parsed


def _record(base: dict[str, Any]) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": "山西师范大学",
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
                    "major": parsed["major"],
                    "admission_major": parsed["admission_major"],
                    "ranking": str(len(rows) + 1),
                    "remarks": _remarks(
                        "degree 博士",
                        f"english_score {parsed['english_score']}",
                        f"subject1_score {parsed['subject1_score']}",
                        f"subject2_score {parsed['subject2_score']}",
                        f"reexam_score {parsed['reexam_score']}",
                        f"weighted_score {parsed['weighted_score']}",
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
