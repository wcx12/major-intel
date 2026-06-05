from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

from bs4 import BeautifulSoup

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch220_zafu_doctoral_supplement")
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch220_zafu_doctoral_supplement_curated"
)

DEFAULT_HTML_PATHS = [
    RAW_DIR / "yjszs.zafu.edu.cn" / "8414edbb79258d73.htm",
    RAW_DIR / "yjszs.zafu.edu.cn" / "ff61cc3ef777664c.htm",
]
SOURCE_URLS = {
    "8414edbb79258d73.htm": "https://yjszs.zafu.edu.cn/info/1109/3307.htm",
    "ff61cc3ef777664c.htm": "https://yjszs.zafu.edu.cn/info/1109/3304.htm",
}
SCHOOL_NAME = "\u6d59\u6c5f\u519c\u6797\u5927\u5b66"
TITLE = "\u6d59\u6c5f\u519c\u6797\u5927\u5b662026\u5e74\u535a\u58eb\u7814\u7a76\u751f\u62df\u5f55\u53d6\u540d\u5355\uff08\u8865\u5f55\uff09\u516c\u793a"


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _table_rows(html_path: Path) -> list[list[str]]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    rows: list[list[str]] = []
    for table in soup.select(".v_news_content table, table"):
        for tr in table.find_all("tr"):
            values = [_clean_text(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
            if values:
                rows.append(values)
    return rows


def curate_zafu_html(html_path: Path) -> list[dict[str, Any]]:
    source_url = SOURCE_URLS.get(html_path.name, "")
    rows: list[dict[str, Any]] = []
    for values in _table_rows(html_path):
        if len(values) < 9 or not values[0].isdigit():
            continue
        ranking, person_name, student_id, college, major_name, major_code, direction, score, method = values[:9]
        rows.append(
            crawler._clean_record(
                {
                    "school_name": SCHOOL_NAME,
                    "year": 2026,
                    "document_type": "postgraduate_admission_list",
                    "route": "postgraduate_exam_or_admission",
                    "person_name": person_name,
                    "student_id": student_id,
                    "college": college,
                    "major": major_code,
                    "admission_major": _clean_text(f"{major_code} {major_name}"),
                    "ranking": ranking,
                    "remarks": _remarks(
                        f"research_direction {direction}",
                        f"composite_score {score}",
                        f"admission_method {method}",
                    ),
                    "source_url": source_url,
                    "title": TITLE,
                    "needs_review": False,
                }
            )
        )
    return rows


def curate_records(html_paths: Iterable[Path] = DEFAULT_HTML_PATHS) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for html_path in html_paths:
        rows.extend(curate_zafu_html(html_path))
    return rows


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    notes = [
        "batch220_zafu_doctoral_supplement_curated: normalized Zhejiang A&F University 2026 doctoral admission supplement HTML tables.",
        "Kept candidate id, college, major code/name, research direction, composite score, and admission method.",
        f"rows={len(rows)}",
        *[f"source={url}" for url in SOURCE_URLS.values()],
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
