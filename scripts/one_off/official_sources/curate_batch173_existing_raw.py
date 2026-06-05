from __future__ import annotations

import re
from pathlib import Path

import graduate_outcome_crawler as crawler


OUT_DIR = Path(
    "data/processed/"
    "graduate_outcomes_official_site_websearch_web_20260526_batch173_existing_raw_curated"
)


def clean(row: dict[str, object]) -> dict[str, object]:
    return crawler._clean_record(dict(row))


def add_xjtu(rows: list[dict[str, object]]) -> None:
    pdf_path = Path(
        "data/raw/graduate_outcomes_official_site_websearch_web_20260524_batch45/"
        "medgs.xjtu.edu.cn/f1c123eb87cab05c.pdf"
    )
    text = crawler._extract_pdf_text_with_pdftotext(pdf_path)
    lines = text.splitlines()
    source_url = "https://medgs.xjtu.edu.cn/202641.pdf"
    title = "西安交通大学医学部2026年硕士研究生拟录取名单公示"

    pattern = re.compile(
        r"\s*(\d{1,4})\s+(\d{15})\s+"
        r"(?:(?P<name>[\u4e00-\u9fff·]{2,8})\s+)?"
        r"(?P<major>[0-9A-Z]{6})\s+"
        r"(?P<initial>\d{2,3})\s+"
        r"(?P<reexam>[0-9.]+)\s+"
        r"(?P<total>[0-9.]+)\s*$"
    )
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        name = match.group("name") or ""
        if not name:
            prev_piece = ""
            next_piece = ""
            if index > 0:
                prev_match = re.search(r"([\u4e00-\u9fff·]{1,8})\s+全国统", lines[index - 1])
                if prev_match:
                    prev_piece = prev_match.group(1)
            if index + 1 < len(lines):
                next_match = re.search(r"([\u4e00-\u9fff·]{1,8})\s+一考试", lines[index + 1])
                if next_match:
                    next_piece = next_match.group(1)
            name = prev_piece + next_piece

        nearby = " ".join(lines[index + 1 : index + 4])
        degree = "学术型" if "学术" in nearby else ("专业型" if "专业" in nearby else "")
        study_mode = "非全日制" if "非全日" in nearby else ("全日制" if "全日" in nearby else "")
        remarks = (
            f"initial_score {match.group('initial')} "
            f"reexam_score {match.group('reexam')} "
            f"total_score {match.group('total')} 全国统一考试 {degree} {study_mode}"
        ).strip()
        rows.append(
            clean(
                {
                    "school_name": "西安交通大学",
                    "year": 2026,
                    "document_type": "postgraduate_admission_list",
                    "route": "postgraduate_exam_or_admission",
                    "person_name": name,
                    "student_id": match.group(2),
                    "college": "医学部",
                    "admission_major": match.group("major"),
                    "ranking": match.group(1),
                    "remarks": remarks,
                    "source_url": source_url,
                    "title": title,
                    "needs_review": False,
                }
            )
        )


def add_sysu(rows: list[dict[str, object]]) -> None:
    pdf_path = Path(
        "data/raw/graduate_outcomes_official_site_websearch_web_20260522/"
        "ise.sysu.edu.cn/de2ba89b026e10a5.pdf"
    )
    text = crawler._extract_pdf_text_with_pdftotext(pdf_path)
    source_url = (
        "https://ise.sysu.edu.cn/sites/default/files/2025-09/"
        "%E6%99%BA%E8%83%BD%E5%B7%A5%E7%A8%8B%E5%AD%A6%E9%99%A22026"
        "%E5%B1%8A%E6%9C%AC%E7%A7%91%E6%AF%95%E4%B8%9A%E7%94%9F"
        "%E5%85%8D%E8%AF%95%E6%94%BB%E8%AF%BB%E7%A0%94%E7%A9%B6"
        "%E7%94%9F%E5%AD%A6%E4%BD%8D%E6%8B%9F%E6%8E%A8%E8%8D%90"
        "%E5%90%8D%E5%8D%95%EF%BC%88%E5%90%AB%E5%80%99%E8%A1%A5"
        "%EF%BC%89.pdf"
    )
    title = "智能工程学院2026届本科毕业生免试攻读研究生学位拟推荐名单（含候补）.pdf"
    pattern = re.compile(r"\s*(\d{1,3})\s+(\d{6,12})\s+([\u4e00-\u9fff·]{2,8})\s+(.+?)\s*$")
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        rows.append(
            clean(
                {
                    "school_name": "中山大学",
                    "year": 2026,
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": match.group(3),
                    "student_id": match.group(2),
                    "college": "智能工程学院",
                    "ranking": match.group(1),
                    "remarks": match.group(4),
                    "source_url": source_url,
                    "title": title,
                    "needs_review": False,
                }
            )
        )


def add_changan(rows: list[dict[str, object]]) -> None:
    pdf_path = Path(
        "data/raw/graduate_outcomes_official_site_websearch_batch2/"
        "ndxy.chd.edu.cn/8b395b35c108d2ca.pdf"
    )
    text = crawler._extract_pdf_text_with_pdftotext(pdf_path)
    source_url = "https://ndxy.chd.edu.cn/__local/2/C6/2C/0592A417ABE23CB7EFE0DD4954B_F7E86CF6_11390.pdf"
    title = "能电学院2026年优秀应届本科毕业生免试攻读研究生拟推荐及递补拟推荐名单"
    pattern = re.compile(r"\s*(\d{1,3})\s+(\d{10})\s+([\u4e00-\u9fff·]{2,8})\s+(.+?)\s*$")
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        tail = re.sub(r"\s+", " ", match.group(4)).strip()
        status_match = re.match(r"(.+?)\s*(递补拟推荐.*|拟推荐.*)$", tail)
        major = status_match.group(1).strip() if status_match else tail
        status = status_match.group(2).strip() if status_match else ""
        rows.append(
            clean(
                {
                    "school_name": "长安大学",
                    "year": 2026,
                    "document_type": "recommendation_exemption_list",
                    "route": "recommendation_exemption",
                    "person_name": match.group(3),
                    "student_id": match.group(2),
                    "college": "能源与电气工程学院",
                    "major": major,
                    "ranking": match.group(1),
                    "remarks": status,
                    "source_url": source_url,
                    "title": title,
                    "needs_review": False,
                }
            )
        )


def sort_key(row: dict[str, object]) -> tuple[object, ...]:
    ranking = str(row.get("ranking") or "")
    return (
        row.get("school_name") or "",
        row.get("year") or "",
        row.get("document_type") or "",
        int(ranking) if ranking.isdigit() else 0,
        row.get("person_name") or "",
        row.get("student_id") or "",
    )


def main() -> None:
    rows: list[dict[str, object]] = []
    add_xjtu(rows)
    add_sysu(rows)
    add_changan(rows)
    rows.sort(key=sort_key)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(rows)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch173_existing_raw_curated: parsed existing official raw files that prior generic batches fetched but could not structure.",
                f"西安交通大学医学部 rows: {sum(1 for r in rows if r['school_name'] == '西安交通大学')}",
                f"中山大学智能工程学院 rows: {sum(1 for r in rows if r['school_name'] == '中山大学')}",
                f"长安大学能电学院 rows: {sum(1 for r in rows if r['school_name'] == '长安大学')}",
            ]
        ),
        encoding="utf-8",
    )
    print({"rows": len(rows), "summary": summary_rows})


if __name__ == "__main__":
    main()
