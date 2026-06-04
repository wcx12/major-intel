from __future__ import annotations

from pathlib import Path

import win32com.client as win32

import graduate_outcome_crawler as crawler


OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260526_batch174_qhu_xls_curated")
XLS_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260525_batch103c/"
    "yjs.qhu.edu.cn/3b8c6bbfc8e6193c.xls"
)
SOURCE_URL = "https://yjs.qhu.edu.cn/docs/2025-04/615da678d8de4fbd974bea45ae6cfaa5.xls"
TITLE = "青海大学2025年硕士研究生招生拟录取名单（一志愿考生）.xls"


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def read_excel_rows(path: Path) -> tuple[tuple[object, ...], ...]:
    excel = win32.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    try:
        workbook = excel.Workbooks.Open(str(path.resolve()))
        try:
            worksheet = workbook.Worksheets(1)
            values = worksheet.UsedRange.Value
            if not isinstance(values, tuple):
                return tuple()
            return values
        finally:
            workbook.Close(False)
    finally:
        excel.Quit()


def make_record(row: tuple[object, ...], index: int) -> dict[str, object] | None:
    if len(row) < 13:
        return None
    student_id = text(row[0])
    person_name = text(row[1])
    if not student_id.isdigit() or len(student_id) < 10 or not person_name:
        return None

    college_code = text(row[2])
    college_name = text(row[3])
    major_code = text(row[4])
    major_name = text(row[5])
    direction_code = text(row[6])
    direction_name = text(row[7])
    plan = text(row[8])
    initial_score = text(row[9])
    reexam_score = text(row[10])
    total_score = text(row[11])
    admission_status = text(row[12])

    college = " ".join(part for part in [college_code, college_name] if part)
    admission_major = " ".join(part for part in [major_code, major_name] if part)
    remarks_parts = []
    if direction_code or direction_name:
        remarks_parts.append("direction " + " ".join(part for part in [direction_code, direction_name] if part))
    if plan:
        remarks_parts.append(f"plan {plan}")
    if initial_score:
        remarks_parts.append(f"initial_score {initial_score}")
    if reexam_score:
        remarks_parts.append(f"reexam_score {reexam_score}")
    if total_score:
        remarks_parts.append(f"total_score {total_score}")
    if admission_status:
        remarks_parts.append(admission_status)

    return crawler._clean_record(
        {
            "school_name": "青海大学",
            "year": 2025,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": person_name,
            "student_id": student_id,
            "college": college,
            "admission_major": admission_major,
            "ranking": str(index),
            "remarks": "; ".join(remarks_parts),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
    )


def main() -> None:
    values = read_excel_rows(XLS_PATH)
    records = []
    for index, row in enumerate(values[2:], start=1):
        record = make_record(row, index)
        if record is not None:
            records.append(record)

    records.sort(
        key=lambda row: (
            row.get("school_name") or "",
            row.get("year") or "",
            row.get("document_type") or "",
            int(str(row.get("ranking") or "0")),
            row.get("person_name") or "",
            row.get("student_id") or "",
        )
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(records, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(records)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch174_qhu_xls_curated: parsed Qinghai University official .xls via local Excel COM because pandas/xlrd was unavailable.",
                f"青海大学 rows: {len(records)}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(records), "summary": summary_rows})


if __name__ == "__main__":
    main()
