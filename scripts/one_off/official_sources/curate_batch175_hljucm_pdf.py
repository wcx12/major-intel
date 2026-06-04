from __future__ import annotations

import re
from pathlib import Path

import graduate_outcome_crawler as crawler


OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch175_hljucm_curated")
PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260526_batch159/"
    "yjsy.hljucm.net/06c5335569ff3d69.pdf"
)
SOURCE_URL = (
    "https://yjsy.hljucm.net/system/_content/download.jsp?"
    "urltype=news.DownloadAttachUrl&owner=1139447238&wbfileid=B9EC50127D176F5D5C41A17BAA6CCB23"
)
TITLE = "附件：黑龙江中医药大学2026年接收推荐免试攻读硕士研究生名单.pdf"

UNDERGRAD_SCHOOLS = (
    "黑龙江中医药大学",
    "辽宁中医药大学",
    "北京中医药大学",
    "成都中医药大学",
    "延边大学",
)

ROW_PATTERN = re.compile(
    r"^\s*(?P<rank>\d{1,3})\s+"
    r"(?P<category>\S+)\s+"
    r"(?P<name>[\u4e00-\u9fff·]{2,8})\s+"
    r"(?P<gender>[男女])\s+"
    r"(?P<college>.+?)\s+"
    r"(?P<major_code>[0-9A-Z]{6})\s+"
    r"(?P<degree_type>学术学位|专业学位)\s+"
    r"(?P<admission_major>.+?)\s{2,}"
    r"(?P<tail>.+)$"
)


def split_tail(tail: str) -> tuple[str, str, str, str, str]:
    school_pattern = "|".join(re.escape(school) for school in UNDERGRAD_SCHOOLS)
    match = re.match(
        rf"(?P<school>{school_pattern})\s+"
        r"(?P<body>.+?)\s+"
        r"(?P<score>\d+\.\d{2})\s+"
        r"(?P<teacher_and_notes>.+)$",
        tail.strip(),
    )
    if not match:
        raise ValueError(f"could not split tail: {tail!r}")

    body_parts = re.split(r"\s{2,}", match.group("body").strip(), maxsplit=1)
    undergraduate_college = body_parts[0].strip()
    undergraduate_major = body_parts[1].strip() if len(body_parts) > 1 else ""

    teacher_parts = match.group("teacher_and_notes").strip().split(maxsplit=1)
    teacher = teacher_parts[0]
    notes = teacher_parts[1] if len(teacher_parts) > 1 else ""
    return (
        match.group("school"),
        undergraduate_college,
        undergraduate_major,
        match.group("score"),
        " ".join(part for part in [teacher, notes] if part),
    )


def make_record(line: str) -> dict[str, object] | None:
    match = ROW_PATTERN.match(line)
    if not match:
        return None

    undergraduate_school, undergraduate_college, undergraduate_major, score, teacher_notes = split_tail(
        match.group("tail")
    )
    remarks_parts = [
        match.group("category"),
        match.group("degree_type"),
        f"gender {match.group('gender')}",
        f"reexam_score {score}",
    ]
    if undergraduate_college:
        remarks_parts.append(f"undergraduate_college {undergraduate_college}")
    if teacher_notes:
        remarks_parts.append(f"advisor_or_note {teacher_notes}")

    return crawler._clean_record(
        {
            "school_name": "黑龙江中医药大学",
            "year": 2026,
            "document_type": "recommendation_exemption_list",
            "route": "recommendation_exemption",
            "person_name": match.group("name"),
            "undergraduate_school": undergraduate_school,
            "undergraduate_major": undergraduate_major,
            "college": match.group("college").strip(),
            "admission_major": f"{match.group('major_code')} {match.group('admission_major').strip()}",
            "ranking": match.group("rank"),
            "remarks": "; ".join(remarks_parts),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
    )


def main() -> None:
    text = crawler._extract_pdf_text_with_pdftotext(PDF_PATH)
    records = []
    skipped = []
    for line in text.splitlines():
        if not re.match(r"^\s*\d{1,3}\s+", line):
            continue
        try:
            record = make_record(line)
        except ValueError as exc:
            skipped.append(f"{exc}: {line}")
            continue
        if record is not None:
            records.append(record)

    records.sort(key=lambda row: int(str(row.get("ranking") or "0")))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(records, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(records)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch175_hljucm_curated: parsed the official Hljucm PDF table with pdftotext layout output.",
                f"黑龙江中医药大学 rows: {len(records)}",
                f"skipped candidate lines: {len(skipped)}",
                *skipped,
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(records), "skipped": len(skipped), "summary": summary_rows})


if __name__ == "__main__":
    main()
