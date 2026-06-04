from __future__ import annotations

import csv
import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RAW_PDF = (
    ROOT
    / "data/raw/official_recommendation_bift_2026_doctor_admission_first/"
    "bift_2026_doctor_admission_first.pdf"
)
OUTPUT_CSV = (
    ROOT
    / "data/processed/official_recommendation_bift_2026_doctor_admission_first/"
    "records_clean_curated.csv"
)
SOURCE_PAGE = "https://yjs.bift.edu.cn/zsgz/zsxx/592661e0e6f74dac8942679a9dfe0882.htm"
SOURCE_URL = "https://yjs.bift.edu.cn/docs//2026-06/85b36649ec7b43d79acd889705f02a2d.pdf"
TITLE = (
    "\u5317\u4eac\u670d\u88c5\u5b66\u96622026\u5e74"
    "\u535a\u58eb\u7814\u7a76\u751f\u62db\u751f\u8003\u8bd5"
    "\u62df\u5f55\u53d6\u7ed3\u679c\u516c\u793a\uff08\u7b2c\u4e00\u6279\uff09"
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

ROW_RE = re.compile(
    r"^\s*(?P<rank>\d+)\s+"
    r"(?P<direction>.*?)\s*"
    r"(?P<student_id>100126\d{9})\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<material_review_score>\d+(?:\.\d+)?)\s+"
    r"(?P<comprehensive_assessment_score>\d+(?:\.\d+)?)\s+"
    r"(?P<total_score>\d+(?:\.\d+)?)\s+"
    r"(?P<admission_status>拟录取|拟不录取)\s*$"
)


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


def extract_pdf_text(pdf_path: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.decode("utf-8", errors="replace")


def looks_like_direction_line(line: str) -> bool:
    stripped = line.strip()
    return bool(re.match(r"^\d{2}\S+", stripped)) and "100126" not in stripped


def parse_records_from_text(text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current_direction = ""

    for line in text.splitlines():
        match = ROW_RE.match(line)
        if match:
            values = {key: (value or "").strip() for key, value in match.groupdict().items()}
            direction = values["direction"] or current_direction
            if direction:
                current_direction = direction
            if values["admission_status"] != "拟录取":
                continue

            remark_parts = [
                f"material_review_score {values['material_review_score']}",
                f"comprehensive_assessment_score {values['comprehensive_assessment_score']}",
                f"total_score {values['total_score']}",
                f"admission_status {values['admission_status']}",
                "official_pdf_download true",
                f"source_page {SOURCE_PAGE}",
                f"local_artifact {RAW_PDF.relative_to(ROOT).as_posix()}",
            ]
            record = {
                "school_name": "\u5317\u4eac\u670d\u88c5\u5b66\u9662",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name": values["person_name"],
                "person_name_masked": mask_name(values["person_name"]),
                "student_id": values["student_id"],
                "student_id_masked": mask_identifier(values["student_id"]),
                "undergraduate_school": "",
                "undergraduate_major": "",
                "college": "",
                "major": direction,
                "admission_major": direction,
                "ranking": values["rank"],
                "remarks": "; ".join(remark_parts),
                "source_url": SOURCE_URL,
                "title": TITLE,
                "needs_review": "false",
            }
            flags = ["missing_undergraduate_school"]
            if not direction:
                flags.append("missing_admission_major")
            record["quality_score"] = str(quality_score(record, flags))
            record["quality_flags"] = ";".join(flags)
            record["record_id"] = record_id(record)
            records.append({field: record.get(field, "") for field in CLEAN_RECORD_CSV_FIELDS})
            continue

        if looks_like_direction_line(line):
            current_direction = line.strip()

    return records


def curate_records(pdf_path: Path = RAW_PDF) -> list[dict[str, str]]:
    return parse_records_from_text(extract_pdf_text(pdf_path))


def main() -> None:
    records = curate_records(RAW_PDF)
    if len(records) != 35:
        raise ValueError(f"expected 35 BIFT doctoral admission records, got {len(records)}")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLEAN_RECORD_CSV_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow({field: csv_value(record.get(field)) for field in CLEAN_RECORD_CSV_FIELDS})
    print({"output": str(OUTPUT_CSV), "records": len(records)})


if __name__ == "__main__":
    main()
