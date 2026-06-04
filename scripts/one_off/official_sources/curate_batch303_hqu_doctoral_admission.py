from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch303_hqu_admission/"
    "grs.hqu.edu.cn/hqu_2026_doctoral_admission_second_batch.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch303_hqu_admission_curated"
)

SCHOOL_NAME = "华侨大学"
YEAR = 2026
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"
SOURCE_URL = "https://grs.hqu.edu.cn/info/1176/18010.htm"
ATTACHMENT_URL = (
    "https://grs.hqu.edu.cn/virtual_attach_file.vsb?afc="
    "wMmAXVM8CDMm6kU/NlDLRnVMlCiL8CKiLmLPLRlaUlU4Lz90gihFp2hmCIa0USh7MYh2L1hVLR6koRNanllDM8CYL8l4UlUiMm-PLzf7M7MFM7L4nlQVUlnFLmU8M87Jv2nto4OeosT/vsTFptrsgDTJQty0Lz7sM1yPoRGPLkbw62O8c"
)
TITLE = "华侨大学2026年第二批次硕博连读和申请审核制博士研究生拟录取名单公示"

LINE_PREFIX_RE = re.compile(
    r"^\s*(?P<ranking>\d{1,3})\s+"
    r"(?P<college_code>\d{3})\s+"
    r"(?P<college>.+?)\s+"
    r"(?P<major_code>[0-9A-Z]{6})\s+"
    r"(?P<tail>.+)$"
)
LINE_SUFFIX_RE = re.compile(
    r"^(?P<prefix>.+?)\s+"
    r"(?P<student_id>\d{10})\s+"
    r"(?P<score>\d+(?:\.\d+)?)\s+"
    r"(?P<learning_mode>全日制)\s+"
    r"(?P<admission_category>非定向就业|定向就业)\s+"
    r"(?P<exam_method>申请审核|硕博连读)"
    r"(?:\s+(?P<note>.+))?$"
)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _compact(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _is_noise_line(value: str) -> bool:
    text = _clean(value).replace("\x0c", "")
    if not text:
        return True
    noise_fragments = (
        "华侨大学2026年第二批次",
        "学院名称",
        "专业名称",
        "考生报名号",
        "考试方式",
        "复试",
        "学习",
        "录取",
        "第 ",
        "页，共",
    )
    return any(fragment in text for fragment in noise_fragments)


def _is_note_line(value: str) -> bool:
    stripped = _compact(value)
    if not stripped:
        return False
    leading_spaces = len(value) - len(value.lstrip())
    return leading_spaces >= 80 or "国际产学研用联" in stripped or "培博士计划" in stripped


def _parse_record_line(line: str) -> dict[str, str] | None:
    prefix_match = LINE_PREFIX_RE.match(line)
    if not prefix_match:
        return None
    suffix_match = LINE_SUFFIX_RE.match(prefix_match.group("tail"))
    if not suffix_match:
        return None
    prefix_parts = re.split(r"\s{2,}", suffix_match.group("prefix").strip())
    if len(prefix_parts) < 3:
        return None
    if len(prefix_parts) == 3:
        major_name = ""
        research_direction, supervisor, person_name = prefix_parts
    else:
        major_name = prefix_parts[0]
        research_direction = " ".join(prefix_parts[1:-2])
        supervisor = prefix_parts[-2]
        person_name = prefix_parts[-1]
    return {
        "ranking": prefix_match.group("ranking"),
        "college_code": prefix_match.group("college_code"),
        "college": _clean(prefix_match.group("college")),
        "major_code": prefix_match.group("major_code"),
        "major_name": _clean(major_name),
        "research_direction": _clean(research_direction),
        "supervisor": _clean(supervisor),
        "person_name": _clean(person_name),
        **suffix_match.groupdict(default=""),
    }


def _remarks(data: dict[str, str], note: str = "") -> str:
    parts = [
        f"college_code: {data['college_code']}",
        f"major_code: {data['major_code']}",
        f"research_direction: {data['research_direction']}",
        f"supervisor: {data['supervisor']}",
        f"interview_score: {data['score']}",
        f"learning_mode: {data['learning_mode']}",
        f"admission_category: {data['admission_category']}",
        f"exam_method: {data['exam_method']}",
    ]
    if note:
        parts.append(f"note: {note}")
    return "; ".join(_clean(part) for part in parts if _clean(part))


def _record_from_data(data: dict[str, str], note: str = "") -> dict[str, Any]:
    major_name = _clean(data["major_name"])
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": data["person_name"],
            "student_id": data["student_id"],
            "college": data["college"],
            "major": major_name,
            "admission_major": major_name,
            "ranking": data["ranking"],
            "remarks": _remarks(data, note),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
    )


def curate_records(*, pdf_path: Path = PDF_PATH) -> list[dict[str, Any]]:
    text = crawler._extract_pdf_text_with_pdftotext(pdf_path)
    lines = text.splitlines()
    records: list[dict[str, Any]] = []
    pending_lines: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        data = _parse_record_line(line)
        if not data:
            if not _is_noise_line(line):
                pending_lines.append(_clean(line))
            index += 1
            continue

        note_lines: list[str] = []
        if not data["major_name"]:
            major_parts = [_compact(part) for part in pending_lines if part]
            pending_lines = []
            lookahead = index + 1
            while lookahead < len(lines) and not _parse_record_line(lines[lookahead]):
                if not _is_noise_line(lines[lookahead]):
                    major_parts.append(_compact(lines[lookahead]))
                    lookahead += 1
                    break
                lookahead += 1
            data["major_name"] = "".join(major_parts)
            index = lookahead
        else:
            note_lines.extend(_compact(part) for part in pending_lines if _is_note_line(part))
            pending_lines = []
            lookahead = index + 1
            while note_lines and lookahead < len(lines) and not _parse_record_line(lines[lookahead]):
                if not _is_noise_line(lines[lookahead]) and _is_note_line(lines[lookahead]):
                    note_lines.append(_compact(lines[lookahead]))
                    lookahead += 1
                    continue
                break
            index = lookahead

        records.append(_record_from_data(data, "".join(note_lines)))

    return sorted(records, key=lambda row: int(row["ranking"]))


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch303_hqu_doctoral_admission_curated: parsed Huaqiao University 2026 second-batch doctoral admission PDF.",
                "Only complete rows with 10-digit candidate registration numbers were retained.",
                "Multiline major names and remarks from the VSB PDF text layer were joined into single fields.",
                f"rows={len(rows)}",
                f"source={SOURCE_URL}",
                f"attachment={ATTACHMENT_URL}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
