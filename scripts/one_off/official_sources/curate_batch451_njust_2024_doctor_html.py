from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover
    import graduate_outcome_crawler as crawler


RAW_HTML = Path(
    "data/raw/official_site_recommendation_websearch_web_20260602_batch451_njust_2024_doctor_html/"
    "gs.njust.edu.cn/f724b99590bd44d3.htm"
)
OUT_DIR = Path("data/processed/official_site_recommendation_websearch_web_20260602_batch451_njust_2024_doctor_html_curated")
SOURCE_URL = "https://gs.njust.edu.cn/18/9f/c14687a333983/page.htm"
TITLE = "2024年公开招考博士研究生拟录取名单（四）"
SCHOOL_NAME = "南京理工大学"
YEAR = 2024
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"


def parse_table_rows(html: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for table in _TableParser.tables(html):
        if not table or table[0] != ["序号", "拟录取学院", "拟录取专业代码", "拟录取专业名称", "姓名", "备注"]:
            continue
        for row in table[1:]:
            record = _record_from_row(row)
            if record:
                records.append(record)
    return records


def curate_records(path: Path = RAW_HTML) -> list[dict[str, Any]]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    return parse_table_rows(html)


def _record_from_row(row: list[str]) -> dict[str, Any] | None:
    if len(row) < 5:
        return None
    serial, college, major_code, major_name, person_name = [_clean(value) for value in row[:5]]
    remark = _clean(row[5]) if len(row) > 5 else ""
    if not re.fullmatch(r"\d+", serial):
        return None
    if not re.fullmatch(r"\d{6}", major_code):
        return None
    if not person_name or "电子信箱" in row:
        return None
    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": DOCUMENT_TYPE,
        "route": ROUTE,
        "person_name": person_name,
        "student_id": "",
        "college": college,
        "major": major_code,
        "admission_major": f"{major_code} {major_name}".strip(),
        "ranking": serial,
        "remarks": _remarks(
            [
                ("serial", serial),
                ("official_admission_status", "拟录取"),
                ("source_remark", remark),
            ]
        ),
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key}: {_clean(value)}" for key, value in parts if _clean(value))


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\u200b", " ")).strip()


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    @classmethod
    def tables(cls, html: str) -> list[list[list[str]]]:
        parser = cls()
        parser.feed(html)
        return parser.tables

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append(_clean("".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._table is not None:
            row = [value for value in self._row if value]
            if row:
                self._table.append(row)
            self._row = None
        elif tag == "table" and self._table is not None:
            self.tables.append(self._table)
            self._table = None


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_path = OUT_DIR / "records_clean_curated.csv"
    public_path = OUT_DIR / "records_public_curated.csv"
    summary_path = OUT_DIR / "school_year_summary_curated.csv"
    crawler._write_clean_records_csv(rows, clean_path)
    crawler.export_public_records_csv(clean_path, public_path)
    crawler._write_summary_csv(crawler._build_summary_rows(rows), summary_path)
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch451_njust_2024_doctor_html_curated: parsed the official Nanjing University of Science and Technology 2024 doctoral admission HTML table.",
                "Only the table headed 序号/拟录取学院/拟录取专业代码/拟录取专业名称/姓名/备注 was retained; navigation/contact tables were excluded.",
                f"rows={len(rows)}",
                f"source_url={SOURCE_URL}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "clean_csv": str(clean_path), "public_csv": str(public_path)})


if __name__ == "__main__":
    main()
