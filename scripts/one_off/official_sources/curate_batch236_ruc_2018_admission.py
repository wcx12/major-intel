from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch236_ruc_2018_admission"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch236_ruc_2018_admission_curated"
)

SCHOOL_NAME = "中国人民大学"
YEAR = 2018
HEADER = [
    "录取学院",
    "录取专业",
    "录取研究方向",
    "学习形式",
    "考生姓名",
    "考生编号",
    "初试成绩",
    "复试成绩",
    "总成绩 （加权成绩）",
    "备注",
]

SOURCES = [
    {
        "title_key": "中国人民大学2018年硕士研究生全国统考拟录取名单公示（第一批）",
        "source_url": "https://grs.ruc.edu.cn/info/1083/1273.htm",
        "title": "中国人民大学2018年硕士研究生全国统考拟录取名单公示（第一批）",
    },
    {
        "title_key": "中国人民大学2018年硕士研究生全国统考拟录取名单公示（第二批）",
        "source_url": "https://grs.ruc.edu.cn/info/1083/1348.htm",
        "title": "中国人民大学2018年硕士研究生全国统考拟录取名单公示（第二批）",
    },
]


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _record(cells: list[str], source: dict[str, str], ranking: int) -> dict[str, Any]:
    (
        college,
        admission_major,
        research_direction,
        study_mode,
        person_name,
        student_id,
        initial_score,
        reexam_score,
        weighted_score,
        note,
    ) = cells[:10]
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": person_name,
            "student_id": student_id,
            "college": college,
            "admission_major": admission_major,
            "ranking": str(ranking),
            "source_url": source["source_url"],
            "title": source["title"],
            "needs_review": False,
            "remarks": _remarks(
                f"research_direction {research_direction}",
                f"study_mode {study_mode}",
                f"initial_score {initial_score}",
                f"reexam_score {reexam_score}",
                f"weighted_score {weighted_score}",
                note,
            ),
        }
    )


def _parse_source(path: Path, source: dict[str, str]) -> list[dict[str, Any]]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows: list[dict[str, Any]] = []
    ranking = 1
    for tr in soup.find_all("tr"):
        cells = [_clean_text(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
        if cells[: len(HEADER)] == HEADER:
            continue
        if len(cells) < len(HEADER):
            continue
        if not cells[4] or not cells[5] or not cells[0] or not cells[1]:
            continue
        if not re.fullmatch(r"[0-9Xx]{10,}", cells[5]):
            continue
        rows.append(_record(cells, source, ranking))
        ranking += 1
    return rows


def _find_source_file(raw_dir: Path, source: dict[str, str]) -> Path | None:
    for path in sorted(raw_dir.glob("**/*.htm")) + sorted(raw_dir.glob("**/*.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if source["title_key"] in text:
            return path
    return None


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in SOURCES:
        path = _find_source_file(raw_dir, source)
        if path is not None:
            rows.extend(_parse_source(path, source))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
