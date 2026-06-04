from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[3]
RAW_HTML = (
    ROOT
    / "data/raw/official_recommendation_cmu_2026_doctor_minority_admission/"
    "cmu_2026_doctor_minority_admission.html"
)
OUTPUT_CSV = (
    ROOT
    / "data/processed/official_recommendation_cmu_2026_doctor_minority_admission/"
    "records_clean_curated.csv"
)
SOURCE_URL = "https://www.cmu.edu.cn/cmuyjs/info/1901/9841.htm"
TITLE = (
    "\u4e2d\u56fd\u533b\u79d1\u5927\u5b662026\u5e74"
    "\u201c\u5c11\u6570\u6c11\u65cf\u9ad8\u5c42\u6b21\u9aa8\u5e72\u4eba\u624d\u8ba1\u5212"
    "\u201d\u535a\u58eb\u7814\u7a76\u751f\u62df\u5f55\u53d6\u540d\u5355\u516c\u793a"
)

CLEAN_RECORD_CSV_FIELDS = [
    "record_id",
    "school_name",
    "year",
    "document_type",
    "route",
    "person_name",
    "person_name_masked",
    "student_id",
    "student_id_masked",
    "undergraduate_school",
    "undergraduate_major",
    "college",
    "major",
    "admission_major",
    "ranking",
    "remarks",
    "source_url",
    "title",
    "needs_review",
    "quality_score",
    "quality_flags",
]


def csv_value(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def mask_name(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 1:
        return "*"
    return value[0] + "*" * (len(value) - 1)


def mask_identifier(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return value[:4] + "*" * max(2, len(value) - 4)


def quality_score(record: dict[str, Any], flags: list[str]) -> int:
    score = 100
    score -= 12 * len(flags)
    if record.get("source_url"):
        score += 5
    return max(0, min(100, score))


def record_id(record: dict[str, Any]) -> str:
    parts = [
        str(record.get("school_name") or ""),
        str(record.get("year") or ""),
        str(record.get("document_type") or ""),
        str(record.get("person_name") or ""),
        str(record.get("student_id") or ""),
        str(record.get("undergraduate_school") or ""),
        str(record.get("admission_major") or record.get("major") or ""),
        str(record.get("source_url") or ""),
        f"rank:{record.get('ranking') or ''}",
    ]
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()


def cell_text(cell) -> str:
    return " ".join(cell.get_text(" ", strip=True).split())


def parse_html_rows(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, str]] = []
    for tr in soup.find_all("tr"):
        cells = [cell_text(td) for td in tr.find_all(["td", "th"])]
        if len(cells) != 7:
            continue
        application_no, person_name, college, major_code, major, department, total_score = cells
        if not (application_no.isdigit() and application_no.startswith("101599")):
            continue

        ranking = str(len(records) + 1)
        remark_parts = [
            f"major_code {major_code}",
            f"department {department}",
            f"total_score {total_score}",
            "minority_backbone_plan true",
            "official_html_table true",
            f"source_page {SOURCE_URL}",
            f"local_artifact {RAW_HTML.relative_to(ROOT).as_posix()}",
        ]
        record = {
            "school_name": "\u4e2d\u56fd\u533b\u79d1\u5927\u5b66",
            "year": "2026",
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": person_name,
            "person_name_masked": mask_name(person_name),
            "student_id": application_no,
            "student_id_masked": mask_identifier(application_no),
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": college,
            "major": major,
            "admission_major": major,
            "ranking": ranking,
            "remarks": "; ".join(remark_parts),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": "false",
        }
        flags = ["missing_undergraduate_school"]
        record["quality_score"] = str(quality_score(record, flags))
        record["quality_flags"] = ";".join(flags)
        record["record_id"] = record_id(record)
        records.append({field: record.get(field, "") for field in CLEAN_RECORD_CSV_FIELDS})
    return records


def curate_records(html_path: Path = RAW_HTML) -> list[dict[str, str]]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    return parse_html_rows(html)


def main() -> None:
    records = curate_records(RAW_HTML)
    if len(records) != 3:
        raise ValueError(f"expected 3 CMU doctoral minority admission records, got {len(records)}")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLEAN_RECORD_CSV_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow({field: csv_value(record.get(field)) for field in CLEAN_RECORD_CSV_FIELDS})
    print({"output": str(OUTPUT_CSV), "records": len(records)})


if __name__ == "__main__":
    main()
