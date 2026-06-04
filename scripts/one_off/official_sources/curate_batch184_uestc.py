from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc_curated")
PDFS = [
    {
        "path": Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc/www.sice.uestc.edu.cn/aae3e0e5af8893f2.pdf"),
        "source_url": "https://www.sice.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1938011446&wbfileid=16789389",
        "title": "2026年“骨干计划”南疆高校教师专项硕士研究生招生拟录取名单.pdf",
        "college": "信息与通信工程学院",
        "kind": "master",
        "extra_note": "专项计划 南疆高校教师专项",
    },
    {
        "path": Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc/www.sice.uestc.edu.cn/34eae367edf23975.pdf"),
        "source_url": "https://www.sice.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1938011446&wbfileid=16787168",
        "title": "信息与通信工程学院2026年硕士研究生招生拟录取名单（调剂）.pdf",
        "college": "信息与通信工程学院",
        "kind": "master",
        "extra_note": "调剂",
    },
    {
        "path": Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc/www.sice.uestc.edu.cn/4a133e55437e99ce.pdf"),
        "source_url": "https://www.sice.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1938011446&wbfileid=16800526",
        "title": "2026年电子科技大学信息与通信工程学院博士研究生招生拟录取名单.pdf",
        "college": "信息与通信工程学院",
        "kind": "doctor",
        "extra_note": "",
    },
    {
        "path": Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc/www.mba.uestc.edu.cn/9ab9ae9af1a60a7e.pdf"),
        "source_url": "https://www.mba.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2019218082&wbfileid=16781468",
        "title": "附件1 2026年电子科技大学经济与管理学院工商管理硕士（MBA）招生拟录取名单.pdf",
        "college": "经济与管理学院MBA",
        "kind": "master",
        "extra_note": "",
    },
    {
        "path": Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc/www.mba.uestc.edu.cn/ad3877e89b1ca698.pdf"),
        "source_url": "https://www.mba.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=2019218082&wbfileid=16787567",
        "title": "附件4 2026年电子科技大学经济与管理学院工商管理硕士（MBA）招生递补拟录取名单.pdf",
        "college": "经济与管理学院MBA",
        "kind": "master",
        "extra_note": "递补拟录取",
    },
    {
        "path": Path("data/raw/graduate_outcomes_official_site_websearch_web_20260527_batch184_uestc/mpa.uestc.edu.cn/659311491b88613d.pdf"),
        "source_url": "https://mpa.uestc.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1877930436&wbfileid=17965777",
        "title": "5-附件-公共管理学院2026年MPA硕士研究生招生拟录取名单.pdf",
        "college": "公共管理学院MPA",
        "kind": "master",
        "extra_note": "",
    },
]

MASTER_ROW_PATTERN = re.compile(
    r"^\s*(?P<student_id>\d{12,15})\s+"
    r"(?P<name>[\u4e00-\u9fff]{2,4})\s+"
    r"(?P<initial>\d+)\s+"
    r"(?P<political>\d+)\s+"
    r"(?P<foreign>\d+)\s+"
    r"(?P<interview>\d+)\s+"
    r"(?P<retest>\d+)\s+"
    r"(?P<weighted>\d+(?:\.\d+)?)\s+"
    r"(?P<major>.+?)\s+"
    r"(?P<direction>\d{2})\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<category>非定向就业|定向就业)\s*"
    r"(?P<notes>.*)$"
)

DOCTOR_ROW_PATTERN = re.compile(
    r"^\s*(?P<student_id>\d{12,15})\s+"
    r"(?P<name>[\u4e00-\u9fff]{2,4})\s+"
    r"(?P<exam_method>申请考核|硕博连读|本科直博|直博)\s+"
    r"(?P<interview>\d+(?:\.\d+)?)\s+"
    r"(?P<foreign>\d+(?:\.\d+)?)\s+"
    r"(?P<retest>\d+(?:\.\d+)?)\s+"
    r"(?P<major>[0-9A-Z]{6}\s+.+?)\s+"
    r"(?P<direction>不区分招生方向|.+?)\s+"
    r"(?P<category_code>\d{2})\s+"
    r"(?P<category>非定向|定向)\s*"
    r"(?P<notes>.*)$"
)


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _clean(row: dict[str, object]) -> dict[str, Any]:
    return crawler._clean_record(row)


def _remarks(parts: list[str]) -> str:
    return "; ".join(part for part in (_collapse_spaces(p) for p in parts) if part and part != "无")


def parse_master_line(
    line: str,
    *,
    college: str,
    source_url: str,
    title: str,
    extra_note: str = "",
) -> dict[str, Any] | None:
    match = MASTER_ROW_PATTERN.match(line)
    if not match:
        return None
    remarks = _remarks(
        [
            f"initial_score {match.group('initial')}",
            f"political_or_written_score {match.group('political')}",
            f"foreign_score {match.group('foreign')}",
            f"interview_score {match.group('interview')}",
            f"retest_score {match.group('retest')}",
            f"weighted_score {match.group('weighted')}",
            f"direction_code {match.group('direction')}",
            f"study_mode {match.group('study_mode')}",
            f"admission_category {match.group('category')}",
            match.group("notes"),
            extra_note,
        ]
    )
    return _clean(
        {
            "school_name": "电子科技大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "college": college,
            "admission_major": _collapse_spaces(match.group("major")),
            "remarks": remarks,
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def parse_doctor_line(
    line: str,
    *,
    college: str,
    source_url: str,
    title: str,
    extra_note: str = "",
) -> dict[str, Any] | None:
    match = DOCTOR_ROW_PATTERN.match(line)
    if not match:
        return None
    remarks = _remarks(
        [
            f"exam_method {match.group('exam_method')}",
            f"interview_score {match.group('interview')}",
            f"foreign_score {match.group('foreign')}",
            f"retest_score {match.group('retest')}",
            f"direction {match.group('direction')}",
            f"admission_category {match.group('category_code')} {match.group('category')}",
            match.group("notes"),
            extra_note,
        ]
    )
    return _clean(
        {
            "school_name": "电子科技大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": match.group("name"),
            "student_id": match.group("student_id"),
            "college": college,
            "admission_major": _collapse_spaces(match.group("major")),
            "remarks": remarks,
            "source_url": source_url,
            "title": title,
            "needs_review": False,
        }
    )


def _parse_pdf(spec: dict[str, Any]) -> tuple[list[dict[str, Any]], int, int]:
    text = crawler._extract_pdf_text_with_pdftotext(spec["path"])
    records: list[dict[str, Any]] = []
    candidates = 0
    skipped = 0
    parser = parse_doctor_line if spec["kind"] == "doctor" else parse_master_line
    for line in text.splitlines():
        if not re.match(r"^\s*\d{12,15}\s+", line):
            continue
        candidates += 1
        record = parser(
            line,
            college=spec["college"],
            source_url=spec["source_url"],
            title=spec["title"],
            extra_note=spec.get("extra_note", ""),
        )
        if record is None:
            skipped += 1
            continue
        records.append(record)
    return records, candidates, skipped


def main() -> None:
    rows: list[dict[str, Any]] = []
    notes = [
        "batch184_uestc_curated: parsed official UESTC MBA/MPA/SICE master and doctoral admission PDFs.",
        "The generic parser mis-split score columns and dropped MBA/MPA person names; this parser uses the PDF text row layout.",
    ]
    for spec in PDFS:
        parsed, candidates, skipped = _parse_pdf(spec)
        rows.extend(parsed)
        notes.append(
            f"{spec['title']}: candidate_lines={candidates}, kept={len(parsed)}, skipped={skipped}"
        )

    rows.sort(
        key=lambda row: (
            str(row.get("source_url") or ""),
            str(row.get("college") or ""),
            str(row.get("person_name") or ""),
            str(row.get("student_id") or ""),
        )
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(rows)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    notes.extend([f"total_rows={len(rows)}", f"summary_rows={summary_rows}"])
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes), encoding="utf-8")
    print({"rows": len(rows), "summary": summary_rows})


if __name__ == "__main__":
    main()
