from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch318_shanghaitech_historic/"
    "yanzhao.shanghaitech.edu.cn"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch318_shanghaitech_historic_curated"
)

SCHOOL_NAME = "上海科技大学"


@dataclass(frozen=True)
class PageConfig:
    source_url: str
    raw_path: Path
    title: str
    year: int
    document_type: str
    route: str
    table_shape: str


PAGE_CONFIGS = [
    PageConfig(
        source_url="https://yanzhao.shanghaitech.edu.cn/2016/1026/c1616a12865/page.htm",
        raw_path=RAW_DIR / "f91aee357470a405.htm",
        title="上海科技大学2017年推荐免试研究生拟录取名单公示",
        year=2017,
        document_type="incoming_recommendation_admission_list",
        route="recommendation_exemption",
        table_shape="recommendation_major_secondary",
    ),
    PageConfig(
        source_url="https://yanzhao.shanghaitech.edu.cn/2017/0502/c1616a12870/page.htm",
        raw_path=RAW_DIR / "3013a7f6795b44e6.htm",
        title="上海科技大学2017年硕士研究生统考复试拟录取名单公示",
        year=2017,
        document_type="postgraduate_admission_list",
        route="postgraduate_exam_or_admission",
        table_shape="master_college_only",
    ),
    PageConfig(
        source_url="https://yanzhao.shanghaitech.edu.cn/2017/0612/c1616a12871/page.htm",
        raw_path=RAW_DIR / "b18c4f1456a6a4cf.htm",
        title="上海科技大学硕博连读2017年秋季入学博士研究生拟录取名单公示",
        year=2017,
        document_type="postgraduate_admission_list",
        route="postgraduate_exam_or_admission",
        table_shape="doctor_season_only",
    ),
    PageConfig(
        source_url="https://yanzhao.shanghaitech.edu.cn/2017/1116/c1616a12872/page.htm",
        raw_path=RAW_DIR / "8d3695c3a65be101.htm",
        title="上海科技大学2018年推荐免试研究生拟录取名单公示",
        year=2018,
        document_type="incoming_recommendation_admission_list",
        route="recommendation_exemption",
        table_shape="recommendation_code_major",
    ),
]


def curate_records() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for config in PAGE_CONFIGS:
        if not config.raw_path.exists():
            continue
        html = config.raw_path.read_text(encoding="utf-8", errors="replace")
        rows.extend(curate_html_records(html, config, starting_rank=len(rows) + 1))
    return rows


def curate_html_records(raw_html: str, config: PageConfig, *, starting_rank: int = 1) -> list[dict[str, Any]]:
    soup = BeautifulSoup(raw_html, "html.parser")
    rows: list[dict[str, Any]] = []
    for table in soup.find_all("table"):
        for cells in _iter_table_cells(table):
            parsed = _parse_cells(cells, config)
            if not parsed:
                continue
            parsed["ranking"] = parsed.get("ranking") or str(starting_rank + len(rows))
            rows.append(_record_from_data(parsed, config))
    return rows


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\xa0", " ")).strip()


def _iter_table_cells(table: Any) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = [_clean(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return rows


def _parse_cells(cells: list[str], config: PageConfig) -> dict[str, str] | None:
    if not cells or not re.fullmatch(r"\d+", cells[0]):
        return None
    if config.table_shape == "recommendation_major_secondary":
        return _parse_recommendation_major_secondary(cells)
    if config.table_shape == "master_college_only":
        return _parse_master_college_only(cells)
    if config.table_shape == "doctor_season_only":
        return _parse_doctor_season_only(cells)
    if config.table_shape == "recommendation_code_major":
        return _parse_recommendation_code_major(cells)
    return None


def _parse_recommendation_major_secondary(cells: list[str]) -> dict[str, str] | None:
    if len(cells) < 5:
        return None
    ranking, person_name, major, secondary_subject, admission_type = cells[:5]
    if not _looks_like_person_name(person_name) or not major:
        return None
    return {
        "ranking": ranking,
        "person_name": person_name,
        "college": "",
        "major": major,
        "admission_major": major,
        "remarks": _remarks(
            [
                ("second_level_subject", secondary_subject),
                ("admission_type", admission_type),
                ("source_columns", "序号/姓名/一级学科/二级学科/拟录取类型"),
            ]
        ),
    }


def _parse_master_college_only(cells: list[str]) -> dict[str, str] | None:
    if len(cells) < 3:
        return None
    ranking, person_name, college = cells[:3]
    if not _looks_like_person_name(person_name) or not college:
        return None
    return {
        "ranking": ranking,
        "person_name": person_name,
        "college": college,
        "major": "",
        "admission_major": "",
        "remarks": _remarks(
            [
                ("degree_level", "硕士"),
                ("source_columns", "序号/姓名/拟录取学院"),
            ]
        ),
    }


def _parse_doctor_season_only(cells: list[str]) -> dict[str, str] | None:
    if len(cells) < 3:
        return None
    ranking, person_name, admission_season = cells[:3]
    if not _looks_like_person_name(person_name) or not admission_season:
        return None
    return {
        "ranking": ranking,
        "person_name": person_name,
        "college": "",
        "major": "",
        "admission_major": "",
        "remarks": _remarks(
            [
                ("degree_level", "博士"),
                ("admission_season", admission_season),
                ("source_columns", "序号/考生姓名/录取季别"),
            ]
        ),
    }


def _parse_recommendation_code_major(cells: list[str]) -> dict[str, str] | None:
    if len(cells) < 5:
        return None
    ranking, person_name, subject_code, major, admission_type = cells[:5]
    if not _looks_like_person_name(person_name) or not major:
        return None
    return {
        "ranking": ranking,
        "person_name": person_name,
        "college": "",
        "major": major,
        "admission_major": major,
        "remarks": _remarks(
            [
                ("subject_code", subject_code),
                ("admission_type", admission_type),
                ("source_columns", "序号/姓名/学科代码/学科名称/拟录取类型"),
            ]
        ),
    }


def _looks_like_person_name(value: str) -> bool:
    if value in {"姓名", "考生姓名", "学科名称", "二级学科", "一级学科"}:
        return False
    return bool(re.fullmatch(r"[\u4e00-\u9fff·]{2,12}", value))


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key}: {_clean(value)}" for key, value in parts if _clean(value))


def _record_from_data(data: dict[str, str], config: PageConfig) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": config.year,
            "document_type": config.document_type,
            "route": config.route,
            "person_name": data["person_name"],
            "student_id": "",
            "college": data.get("college", ""),
            "major": data.get("major", ""),
            "admission_major": data.get("admission_major", ""),
            "ranking": data.get("ranking", ""),
            "remarks": _remarks(
                [
                    ("source_page", config.source_url),
                    ("source_table_shape", config.table_shape),
                ]
            )
            + ("; " + data.get("remarks", "") if data.get("remarks") else ""),
            "source_url": config.source_url,
            "title": config.title,
            "needs_review": False,
        }
    )


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch318_shanghaitech_historic_curated: parsed ShanghaiTech official historical HTML admission tables.",
                "The current 2026 adjustment page returned HTTP 410, so only still-public official historical pages were curated.",
                f"rows={len(rows)}",
                *[f"source_page={config.source_url}" for config in PAGE_CONFIGS],
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
