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
    / "data/raw/official_recommendation_nwnu_jykxxy_2025_master_first_choice/"
    "nwnu_jykxxy_2025_master_first_choice.pdf"
)
OUTPUT_CSV = (
    ROOT
    / "data/processed/official_recommendation_nwnu_jykxxy_2025_master_first_choice/"
    "records_clean_curated.csv"
)
SOURCE_PAGE = "https://jykxxy.nwnu.edu.cn/2025/0404/c7122a251711/page.htm"
SOURCE_URL = (
    "https://jykxxy.nwnu.edu.cn/_upload/article/files/bd/c5/"
    "289f95b04bfe86e89495ed3239ef/1369c3c3-8eeb-42df-b75b-b36687ef3d13.pdf"
)
TITLE = "西北师范大学教育科学学院2025年硕士研究生招生复试结果（第一志愿）"

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
    r"(?P<student_id>\d{15})\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<admission_major>.+?)\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+\.\d+)\s+"
    r"(?P<reexam_weight>\d+(?:\.\d+)?)\s+"
    r"(?P<composite_score>\d+\.\d+)\s+"
    r"(?P<admission_opinion>拟录取|不予录取)\s+"
    r"(?P<study_mode>全日制|非全日制)"
    r"(?:\s+(?P<note>.+?))?\s*$"
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


def parse_pdf_line(line: str) -> dict[str, str] | None:
    match = ROW_RE.match(line)
    if not match:
        return None
    values = {key: (value or "").strip() for key, value in match.groupdict().items()}
    if values["admission_opinion"] != "拟录取":
        return None

    remark_parts = [
        f"major_code {values['major_code']}",
        f"initial_score {values['initial_score']}",
        f"reexam_score {values['reexam_score']}",
        f"reexam_weight {values['reexam_weight']}",
        f"composite_score {values['composite_score']}",
        f"admission_opinion {values['admission_opinion']}",
        f"study_mode {values['study_mode']}",
    ]
    if values["note"]:
        remark_parts.append(f"note {values['note']}")
    remark_parts.extend(
        [
            "official_pdf_download true",
            f"source_page {SOURCE_PAGE}",
            f"local_artifact {RAW_PDF.relative_to(ROOT).as_posix()}",
        ]
    )

    record = {
        "school_name": "西北师范大学",
        "year": "2025",
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "person_name": values["person_name"],
        "person_name_masked": mask_name(values["person_name"]),
        "student_id": values["student_id"],
        "student_id_masked": mask_identifier(values["student_id"]),
        "undergraduate_school": "",
        "undergraduate_major": "",
        "college": "教育科学学院",
        "major": "",
        "admission_major": values["admission_major"],
        "ranking": values["rank"],
        "remarks": "; ".join(remark_parts),
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": "false",
    }
    flags = ["missing_undergraduate_school"]
    record["quality_score"] = str(quality_score(record, flags))
    record["quality_flags"] = ";".join(flags)
    record["record_id"] = record_id(record)
    return {field: record.get(field, "") for field in CLEAN_RECORD_CSV_FIELDS}


def curate_records(pdf_path: Path = RAW_PDF) -> list[dict[str, str]]:
    text = extract_pdf_text(pdf_path)
    records: list[dict[str, str]] = []
    for line in text.splitlines():
        record = parse_pdf_line(line)
        if record:
            records.append(record)
    return records


def main() -> None:
    records = curate_records(RAW_PDF)
    if len(records) != 106:
        raise ValueError(f"expected 106 NWNU JYKXXY records, got {len(records)}")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLEAN_RECORD_CSV_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow({field: csv_value(record.get(field)) for field in CLEAN_RECORD_CSV_FIELDS})
    print({"output": str(OUTPUT_CSV), "records": len(records)})


if __name__ == "__main__":
    main()
