from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch233_lut_embedded_pdfs")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch233_lut_embedded_pdfs_curated")

SOURCES = {
    "3de938a6aa6fd1fc.pdf": {
        "source_url": "https://weidianzi.lut.edu.cn/__local/6/43/26/A4180401571DB8887F1DE1E3243_60345B89_AD3E.pdf",
        "title": "兰州理工大学微电子现代产业学院2026年硕士研究生招生复试一志愿拟录取结果公示",
        "college": "微电子现代产业学院",
        "batch": "一志愿",
    },
    "21131955f9c22a93.pdf": {
        "source_url": "https://jidian.lut.edu.cn/__local/0/7B/F1/83EF0F22F94E82FE64142ED0575_B962DAF0_1D137.pdf",
        "title": "兰州理工大学机电工程学院2026年硕士研究生招生复试（二次调剂）拟录取结果公示",
        "college": "机电工程学院",
        "batch": "二次调剂",
    },
}

WEIDIANZI_ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d{1,3})\s+"
    r"(?P<person_name>.+?)\s+"
    r"(?P<student_id>\d{15,16})\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)\s+"
    r"(?P<admission_major>\S+)\s+拟录取\s*$"
)

JIDIAN_ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d{1,3})\s+"
    r"(?P<person_name>.+?)\s+"
    r"(?P<student_id>\d{15,16})\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)\s+"
    r"(?P<admission_major>\S+)(?:\s+\S.*)?\s*$"
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _clean_name(value: str) -> str:
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


def _record(source: dict[str, str], base: dict[str, Any]) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": "兰州理工大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "source_url": source["source_url"],
            "title": source["title"],
            "college": source["college"],
            "needs_review": False,
            **base,
        }
    )


def _parse_weidianzi(path: Path, source: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in _pdf_text(path):
        match = WEIDIANZI_ROW_RE.match(line)
        if not match:
            continue
        parsed = match.groupdict()
        rows.append(
            _record(
                source,
                {
                    "person_name": _clean_name(parsed["person_name"]),
                    "student_id": parsed["student_id"],
                    "admission_major": parsed["admission_major"],
                    "ranking": parsed["ranking"],
                    "remarks": _remarks(
                        f"batch {source['batch']}",
                        f"initial_score {parsed['initial_score']}",
                        f"reexam_score {parsed['reexam_score']}",
                        f"total_score {parsed['total_score']}",
                    ),
                },
            )
        )
    return rows


def _parse_jidian(path: Path, source: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in _pdf_text(path):
        match = JIDIAN_ROW_RE.match(line)
        if not match:
            continue
        parsed = match.groupdict()
        rows.append(
            _record(
                source,
                {
                    "person_name": _clean_name(parsed["person_name"]),
                    "student_id": parsed["student_id"],
                    "admission_major": parsed["admission_major"],
                    "ranking": parsed["ranking"],
                    "remarks": _remarks(
                        f"batch {source['batch']}",
                        "admission_status 拟录取",
                        "立功表彰退役军人免初试专项计划",
                        f"reexam_score {parsed['reexam_score']}",
                        f"total_score {parsed['total_score']}",
                    ),
                },
            )
        )
    return rows


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative_name, source in SOURCES.items():
        matches = list(raw_dir.glob(f"**/{relative_name}"))
        if not matches:
            continue
        if source["college"] == "微电子现代产业学院":
            rows.extend(_parse_weidianzi(matches[0], source))
        else:
            rows.extend(_parse_jidian(matches[0], source))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
