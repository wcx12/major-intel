from __future__ import annotations

import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities")
PROCESSED_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities")
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch222_minzu_universities_curated"
)

DEFAULT_NMU_CLEAN_CSV = PROCESSED_DIR / "records_clean.csv"
DEFAULT_XBMU_PDF_PATHS = {
    "ordinary": RAW_DIR / "www.xbmu.edu.cn" / "7e85a7d3965e71aa.pdf",
    "minority_backbone": RAW_DIR / "www.xbmu.edu.cn" / "4d88ffd34d963f64.pdf",
    "retired_soldier": RAW_DIR / "www.xbmu.edu.cn" / "3cfe555dc68509a0.pdf",
}

XBMU_COMMON_START_URL = "https://www.xbmu.edu.cn/yz/info/1351/3771.htm"


@dataclass(frozen=True)
class XbmuPlanConfig:
    plan_type: str
    source_url: str
    title: str
    score_labels: tuple[str, ...]
    trailing_label: str = ""


XBMU_PLAN_CONFIGS = {
    "ordinary": XbmuPlanConfig(
        plan_type="普通计划含照顾政策",
        source_url=(
            "https://www.xbmu.edu.cn/system/_content/download.jsp?"
            "urltype=news.DownloadAttachUrl&owner=1867476930&wbfileid=49CB0FDB0E003E86DC589CB2AEB17C43"
        ),
        title="西北民族大学2026年全国硕士研究生招生一志愿拟录取考生名单（普通计划含照顾政策）.pdf",
        score_labels=("initial_score", "retest_score", "total_score"),
        trailing_label="note",
    ),
    "minority_backbone": XbmuPlanConfig(
        plan_type="少数民族高层次骨干人才计划",
        source_url=(
            "https://www.xbmu.edu.cn/system/_content/download.jsp?"
            "urltype=news.DownloadAttachUrl&owner=1867476930&wbfileid=BE44F92838B97297D30483C9712CE660"
        ),
        title="西北民族大学2026年全国硕士研究生招生一志愿拟录取考生名单（少数民族高层次骨干人才计划）.pdf",
        score_labels=("initial_score", "retest_score", "total_score"),
        trailing_label="source_province",
    ),
    "retired_soldier": XbmuPlanConfig(
        plan_type="退役大学生士兵专项计划",
        source_url=(
            "https://www.xbmu.edu.cn/system/_content/download.jsp?"
            "urltype=news.DownloadAttachUrl&owner=1867476930&wbfileid=EC3EF7210D4C7FC587258D47929B0A7A"
        ),
        title="西北民族大学2026年全国硕士研究生招生一志愿拟录取考生名单（退役大学生士兵专项计划）.pdf",
        score_labels=("initial_score", "retest_score", "initial_converted_score", "total_score"),
    ),
}

STUDENT_ID_RE = re.compile(r"\d{15}")
MAJOR_CODE_RE = re.compile(r"\d{4}[A-Z0-9]\d")
SCORE_RE = re.compile(r"\d+(?:\.\d+)?")


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _extract_pdf_raw_text(pdf_path: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-raw", str(pdf_path), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return crawler._decode_pdftotext_output(completed.stdout)


def _read_nmu_clean_rows(nmu_clean_csv: Path = DEFAULT_NMU_CLEAN_CSV) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with nmu_clean_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("school_name") != "北方民族大学":
                continue
            normalized = {field: row.get(field, "") for field in crawler.CLEAN_RECORD_CSV_FIELDS}
            normalized["year"] = int(normalized["year"]) if str(normalized["year"]).isdigit() else normalized["year"]
            normalized["needs_review"] = _parse_bool(normalized["needs_review"])
            rows.append(normalized)
    return rows


def _token_index(tokens: list[str], pattern: re.Pattern[str], start: int, end: int) -> int:
    for index in range(start, end):
        if pattern.fullmatch(tokens[index]):
            return index
    return -1


def _parse_xbmu_row_line(line: str, config: XbmuPlanConfig) -> dict[str, Any] | None:
    tokens = line.split()
    if len(tokens) < 12:
        return None
    if not tokens[0].isdigit() or not re.fullmatch(r"\d{3}", tokens[1]):
        return None

    student_index = _token_index(tokens, STUDENT_ID_RE, 2, len(tokens))
    if student_index < 0:
        return None
    major_index = _token_index(tokens, MAJOR_CODE_RE, 2, student_index)
    if major_index < 0:
        return None
    direction_index = _token_index(tokens, re.compile(r"\d{2}"), major_index + 1, student_index - 1)
    if direction_index < 0:
        return None

    score_start = student_index + 1
    score_end = score_start + len(config.score_labels)
    scores = tokens[score_start:score_end]
    if len(scores) != len(config.score_labels) or any(not SCORE_RE.fullmatch(score) for score in scores):
        return None

    college_name = "".join(tokens[2:major_index])
    major_name = "".join(tokens[major_index + 1 : direction_index])
    direction_name = "".join(tokens[direction_index + 1 : student_index - 1])
    person_name = tokens[student_index - 1]
    trailing = "".join(tokens[score_end:])

    remark_parts = [
        f"plan_type {config.plan_type}",
        f"college_code {tokens[1]}",
        f"direction_code {tokens[direction_index]}",
        f"research_direction {direction_name}",
    ]
    remark_parts.extend(
        f"{label} {score}" for label, score in zip(config.score_labels, scores, strict=True)
    )
    if config.trailing_label and trailing:
        remark_parts.append(f"{config.trailing_label} {trailing}")

    major_code = tokens[major_index]
    return crawler._clean_record(
        {
            "school_name": "西北民族大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": person_name,
            "student_id": tokens[student_index],
            "college": college_name,
            "major": major_code,
            "admission_major": _clean_text(f"{major_code} {major_name}"),
            "ranking": tokens[0],
            "remarks": _remarks(*remark_parts),
            "source_url": config.source_url,
            "title": config.title,
            "needs_review": False,
        }
    )


def curate_xbmu_pdf(plan_key: str, pdf_path: Path) -> list[dict[str, Any]]:
    config = XBMU_PLAN_CONFIGS[plan_key]
    rows: list[dict[str, Any]] = []
    for raw_line in _extract_pdf_raw_text(pdf_path).splitlines():
        line = raw_line.replace("\f", "").strip()
        record = _parse_xbmu_row_line(line, config)
        if record:
            rows.append(record)
    return rows


def curate_records(
    *,
    nmu_clean_csv: Path = DEFAULT_NMU_CLEAN_CSV,
    xbmu_pdf_paths: dict[str, Path] | None = None,
) -> list[dict[str, Any]]:
    pdf_paths = xbmu_pdf_paths or DEFAULT_XBMU_PDF_PATHS
    rows: list[dict[str, Any]] = []
    rows.extend(_read_nmu_clean_rows(nmu_clean_csv))
    for plan_key in ("ordinary", "minority_backbone", "retired_soldier"):
        rows.extend(curate_xbmu_pdf(plan_key, pdf_paths[plan_key]))
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    notes = [
        "batch222_minzu_universities_curated: kept valid North Minzu University generic clean rows and reparsed Northwest Minzu University admission PDFs with pdftotext -raw.",
        "Northwest Minzu generic extraction shifted PDF table columns; curated parser uses row-level student id, major code, direction code, and score positions.",
        "Official PDF row counts: ordinary=433, minority_backbone=47, retired_soldier=10.",
        f"rows={len(rows)}",
        f"source={XBMU_COMMON_START_URL}",
    ]
    for config in XBMU_PLAN_CONFIGS.values():
        notes.append(f"source={config.source_url}")
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
