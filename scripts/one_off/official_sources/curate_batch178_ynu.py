from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch178_ynu_curated")
APPLICATION_PDF = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch178_ynu/"
    "www.swugs.ynu.edu.cn/69663fd5f5572ee9.pdf"
)
MASTER_PHD_PDF = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch178_ynu/"
    "www.swugs.ynu.edu.cn/3bd63d532ff1aee8.pdf"
)
APPLICATION_SOURCE_URL = "https://www.swugs.ynu.edu.cn/upload/c7874379671c1812327452dcd.pdf"
MASTER_PHD_SOURCE_URL = "https://www.swugs.ynu.edu.cn/upload/c7874379671c1812327452dca.pdf"
APPLICATION_TITLE = "云南大学2026年博士研究生“申请-考核”制（第一批次）拟录取名单"
MASTER_PHD_TITLE = "云南大学2026年硕博连读拟录取名单"

APPLICATION_PATTERN = re.compile(
    r"^\s*(?P<college_code>\d{3})\s+"
    r"(?P<college>.+?)\s+"
    r"(?P<major_code>[0-9A-Z]{6})\s+"
    r"(?P<major_name>.+?)\s+"
    r"(?P<direction>.+?)\s+"
    r"(?P<student_id>\d{5})\s+"
    r"(?P<name>[\u4e00-\u9fff·]{1,12})\s+"
    r"(?P<score>[0-9.]+)\s*$"
)

MASTER_PHD_PATTERN = re.compile(
    r"^\s*(?P<college_code>\d{3})\s+"
    r"(?P<college>.+?)\s+"
    r"(?P<name>[\u4e00-\u9fff·]{2,12})\s+"
    r"(?P<student_id>\d{11})\s+"
    r"(?P<master_major>.+?)\s+"
    r"(?P<doctoral_code>[0-9A-Z]{6})\s+"
    r"(?P<doctoral_major>.+?)\s+"
    r"(?P<advisor>[*\u4e00-\u9fff·]{1,12})\s+"
    r"(?P<score>[0-9.]+)\s*"
    r"(?P<notes>.*)$"
)


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _clean(row: dict[str, object]) -> dict[str, Any]:
    return crawler._clean_record(row)


def parse_application_line(
    line: str,
    *,
    source_url: str,
    title: str,
) -> dict[str, Any] | None:
    match = APPLICATION_PATTERN.match(line)
    if not match:
        return None

    remarks = [
        f"research_direction {_collapse_spaces(match.group('direction'))}",
        f"comprehensive_score {match.group('score')}",
        "admission_method application_assessment",
        "candidate_registration_last5",
    ]
    return _clean(
        {
            "school_name": "云南大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "college": f"{match.group('college_code')} {_collapse_spaces(match.group('college'))}",
            "major": match.group("major_code"),
            "admission_major": f"{match.group('major_code')} {_collapse_spaces(match.group('major_name'))}",
            "remarks": "; ".join(remarks),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def parse_master_phd_line(
    line: str,
    *,
    source_url: str,
    title: str,
) -> dict[str, Any] | None:
    match = MASTER_PHD_PATTERN.match(line)
    if not match:
        return None

    notes = _collapse_spaces(match.group("notes"))
    remarks = [
        "admission_method master_phd_continuous",
        f"advisor {_collapse_spaces(match.group('advisor'))}",
        f"comprehensive_score {match.group('score')}",
    ]
    if notes:
        remarks.append(notes)

    return _clean(
        {
            "school_name": "云南大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "undergraduate_major": _collapse_spaces(match.group("master_major")),
            "college": f"{match.group('college_code')} {_collapse_spaces(match.group('college'))}",
            "major": _collapse_spaces(match.group("master_major")),
            "admission_major": f"{match.group('doctoral_code')} {_collapse_spaces(match.group('doctoral_major'))}",
            "remarks": "; ".join(remarks),
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _parse_pdf(path: Path, parser, source_url: str, title: str) -> tuple[list[dict[str, Any]], int, int]:
    text = crawler._extract_pdf_text_with_pdftotext(path)
    records = []
    candidate_lines = 0
    skipped_candidate_lines = 0
    for line in text.splitlines():
        if not re.match(r"^\s*\d{3}\s+", line):
            continue
        candidate_lines += 1
        record = parser(line, source_url=source_url, title=title)
        if record is None:
            skipped_candidate_lines += 1
            continue
        records.append(record)
    return records, candidate_lines, skipped_candidate_lines


def _dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    deduped = []
    for row in rows:
        key = (
            row.get("person_name") or "",
            row.get("student_id") or "",
            row.get("admission_major") or "",
            row.get("source_url") or "",
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def main() -> None:
    rows: list[dict[str, Any]] = []
    notes = [
        "batch178_ynu_curated: parsed Yunnan University official PDF text rows with strict complete-row regexes.",
        "The generic parser output is not merged because it treats wrapped research directions and major names as person names.",
    ]
    application_rows, application_candidates, application_skipped = _parse_pdf(
        APPLICATION_PDF,
        parse_application_line,
        APPLICATION_SOURCE_URL,
        APPLICATION_TITLE,
    )
    master_phd_rows, master_phd_candidates, master_phd_skipped = _parse_pdf(
        MASTER_PHD_PDF,
        parse_master_phd_line,
        MASTER_PHD_SOURCE_URL,
        MASTER_PHD_TITLE,
    )
    rows.extend(application_rows)
    rows.extend(master_phd_rows)
    rows = _dedupe(rows)
    rows.sort(
        key=lambda row: (
            str(row.get("source_url") or ""),
            str(row.get("college") or ""),
            str(row.get("admission_major") or ""),
            str(row.get("person_name") or ""),
            str(row.get("student_id") or ""),
        )
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(rows)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    notes.extend(
        [
            f"application_assessment: candidate_lines={application_candidates}, kept={len(application_rows)}, skipped_fragments={application_skipped}",
            f"master_phd_continuous: candidate_lines={master_phd_candidates}, kept={len(master_phd_rows)}, skipped_fragments={master_phd_skipped}",
            f"total_rows={len(rows)}",
            f"summary_rows={summary_rows}",
        ]
    )
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes), encoding="utf-8")
    print({"rows": len(rows), "summary": summary_rows, "notes": notes[2:]})


if __name__ == "__main__":
    main()
