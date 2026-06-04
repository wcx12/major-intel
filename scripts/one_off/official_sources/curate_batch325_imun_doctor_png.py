from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch325_imun_doctor_png_curated"
)

SCHOOL_NAME = "内蒙古民族大学"
YEAR = 2026
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"
SOURCE_PAGE = "https://myy.imun.edu.cn/info/1063/2220.htm"
SOURCE_IMAGE = "https://myy.imun.edu.cn/__local/0/C8/95/43F3387BE2D24CBC0D43A264999_F64151A5_6B4E.png"
TITLE = "内蒙古民族大学2026年中药学专业博士研究生招生“申请-考核”制拟录取名单公示"
MAJOR_CODE = "100800"
MAJOR = "中药学"

PNG_TRANSCRIPTION_ROWS = [
    ("1", "吴峰", "1013699965", "是"),
    ("2", "模日", "1013699952", "是"),
    ("3", "郝俊生", "1013699958", "是"),
    ("4", "布仁满达", "1013699998", "是"),
    ("5", "宋亚伟", "1013699975", "是"),
    ("6", "娜日苏", "1013699995", "是"),
    ("7", "乌日汉", "1013699972", "是"),
    ("8", "伊力奇", "1013699970", "是"),
    ("9", "包婷婷", "1013699982", "是"),
    ("10", "白青春", "1013699983", "是"),
    ("11", "木西叶乐", "1013699990", "是"),
    ("12", "贾天琦", "1013699960", "是"),
    ("13", "刘淼", "1013699954", "是"),
    ("14", "照日格图", "1013699959", "是"),
    ("15", "牧希乐", "1013699994", "是"),
    ("16", "李聪明", "1013699996", "是"),
    ("17", "白雪", "1013699961", "是"),
    ("18", "张雨涵", "1013699986", "是"),
    ("19", "邢晓茹拉", "1013699968", "是"),
    ("20", "姜鸿运", "1013699966", "是"),
    ("21", "赵梅荣", "1013699988", "是"),
    ("22", "赵长宝", "1013699974", "是"),
    ("23", "曹明未", "1013699984", "否"),
    ("24", "娜琴", "1013699980", "否"),
    ("25", "朱江", "1013699946", "放弃"),
]


def curate_records() -> list[dict[str, Any]]:
    return [_record_from_row(row) for row in PNG_TRANSCRIPTION_ROWS if row[3] == "是"]


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key}: {_clean(value)}" for key, value in parts if _clean(value))


def _record_from_row(row: tuple[str, str, str, str]) -> dict[str, Any]:
    ranking, person_name, student_id, status = row
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": person_name,
            "student_id": student_id,
            "college": "蒙医药学院",
            "major": MAJOR,
            "admission_major": MAJOR,
            "ranking": ranking,
            "remarks": _remarks(
                [
                    ("degree_level", "博士"),
                    ("admission_method", "申请-考核"),
                    ("major_code", MAJOR_CODE),
                    ("official_admission_status", status),
                    ("source_page", SOURCE_PAGE),
                    ("source_image", SOURCE_IMAGE),
                    ("source_image_transcribed", "true"),
                ]
            ),
            "source_url": SOURCE_IMAGE,
            "title": TITLE,
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
                "batch325_imun_doctor_png_curated: manually transcribed the official PNG table from Inner Mongolia Minzu University Mongolian Medicine College.",
                "Only rows with official_admission_status=是 were retained; rows marked 否 or 放弃 were excluded.",
                f"rows={len(rows)}",
                f"source_page={SOURCE_PAGE}",
                f"source_image={SOURCE_IMAGE}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
