from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch254_qqhru_admission/yjs.qqhru.edu.cn/ccb1fb9cc27be2fd.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch254_qqhru_admission_curated"
)

SCHOOL_NAME = "齐齐哈尔大学"
YEAR = 2025
SOURCE_URL = "https://yjs.qqhru.edu.cn/__local/8/F5/EE/02D0C56D2494576D6694F9C54A6_C1B2A0DC_FAA2C.pdf"
TITLE = "齐齐哈尔大学2025年研究生拟录取名单公示"

ROW_RE = re.compile(r"^\s*(\d{1,4})\s+(\d{15})\s+(\S+)\s+(.+?)\s+(全日制|非全日制)\s+(.+)$")
NO_RANK_RE = re.compile(r"^\s*(\d{15})\s+(.+?)\s+(全日制|非全日制)(?:\s+(.+))?$")
RANK_FRAGMENT_RE = re.compile(r"^\s*(\d{1,4})\s+(.+)$")


def _normalize_fragment(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _split_before_mode(value: str, direction_prefix: str) -> tuple[str, str, str] | None:
    columns = [part.strip() for part in re.split(r"\s{2,}", value.strip()) if part.strip()]
    if len(columns) < 3:
        return None
    college = columns[0]
    major = columns[1]
    direction = _normalize_fragment(direction_prefix + "".join(columns[2:]))
    return college, major, direction


def _record_from_parts(
    *,
    ranking: str,
    student_id: str,
    person_name: str,
    before_mode: str,
    study_mode: str,
    note: str,
    direction_prefix: str = "",
) -> dict[str, Any] | None:
    split = _split_before_mode(before_mode, direction_prefix)
    if not split:
        return None
    college, major, direction = split
    admission_note = _normalize_fragment(note)
    if "放弃" in admission_note:
        return None

    record = {
        "school_name": SCHOOL_NAME,
        "year": YEAR,
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "person_name": person_name,
        "student_id": student_id,
        "undergraduate_school": "",
        "undergraduate_major": "",
        "college": college,
        "major": major,
        "admission_major": direction,
        "ranking": ranking,
        "remarks": f"学习方式: {study_mode}; 录取备注: {admission_note}",
        "source_url": SOURCE_URL,
        "title": TITLE,
        "needs_review": False,
    }
    return crawler._clean_record(record)


def _record_from_match(match: re.Match[str], direction_prefix: str, remark_prefix: str) -> dict[str, Any] | None:
    ranking, student_id, person_name, before_mode, study_mode, note_tail = match.groups()
    return _record_from_parts(
        ranking=ranking,
        student_id=student_id,
        person_name=person_name,
        before_mode=before_mode,
        study_mode=study_mode,
        note=remark_prefix + note_tail,
        direction_prefix=direction_prefix,
    )


def _record_from_no_rank_match(
    match: re.Match[str],
    rank_fragment: re.Match[str],
    *,
    pending_major_prefix: str = "",
    pending_name_prefix: str = "",
    pending_remark_prefix: str = "",
) -> dict[str, Any] | None:
    ranking, suffix = rank_fragment.groups()
    student_id, body, study_mode, note_tail = match.groups()
    note_tail = note_tail or ""
    body_columns = [part.strip() for part in re.split(r"\s{2,}", body.strip()) if part.strip()]
    if pending_name_prefix:
        person_name = pending_name_prefix + _normalize_fragment(suffix)
        if len(body_columns) < 3:
            return None
        before_mode = "   ".join(body_columns)
        note = note_tail
    else:
        if len(body_columns) < 3:
            return None
        person_name = body_columns[0]
        if pending_major_prefix:
            before_mode = "   ".join([body_columns[1], pending_major_prefix + _normalize_fragment(suffix), *body_columns[2:]])
            note = note_tail
        else:
            if len(body_columns) < 4:
                return None
            before_mode = "   ".join(body_columns[1:])
            note = pending_remark_prefix + note_tail + suffix
    return _record_from_parts(
        ranking=ranking,
        student_id=student_id,
        person_name=person_name,
        before_mode=before_mode,
        study_mode=study_mode,
        note=note,
    )


def _append_continuation(record: dict[str, Any], fragment: str) -> None:
    if not fragment:
        return
    if "录取" in fragment or "计划" in fragment:
        record["remarks"] = f"{record['remarks']}; 续行: {fragment}"
    else:
        record["admission_major"] = _normalize_fragment(f"{record['admission_major']}{fragment}")


def curate_records(pdf_path: Path | None = None) -> list[dict[str, Any]]:
    path = pdf_path or PDF_PATH
    text = crawler._extract_pdf_text_with_pdftotext(path)
    records: list[dict[str, Any]] = []
    pending_direction_prefix = ""
    pending_major_prefix = ""
    pending_name_prefix = ""
    pending_remark_prefix = ""
    lines = [line for line in text.splitlines() if line.strip()]
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        match = ROW_RE.match(line)
        if match:
            record = _record_from_match(match, pending_direction_prefix, pending_remark_prefix)
            pending_direction_prefix = ""
            pending_major_prefix = ""
            pending_name_prefix = ""
            pending_remark_prefix = ""
            if record:
                records.append(record)
            index += 1
            continue

        no_rank_match = NO_RANK_RE.match(line)
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        rank_fragment = RANK_FRAGMENT_RE.match(next_line)
        if no_rank_match and rank_fragment:
            record = _record_from_no_rank_match(
                no_rank_match,
                rank_fragment,
                pending_major_prefix=pending_major_prefix,
                pending_name_prefix=pending_name_prefix,
                pending_remark_prefix=pending_remark_prefix,
            )
            pending_direction_prefix = ""
            pending_major_prefix = ""
            pending_name_prefix = ""
            pending_remark_prefix = ""
            if record:
                records.append(record)
            index += 2
            continue

        fragment = _normalize_fragment(stripped)
        if not fragment or fragment.startswith("第") or "举报监督电话" in fragment:
            index += 1
            continue
        next_no_rank = bool(index + 1 < len(lines) and NO_RANK_RE.match(lines[index + 1]))
        if not records and not next_no_rank:
            index += 1
            continue
        if next_no_rank and len(fragment) <= 4 and not any(term in fragment for term in ("研究", "技术", "录取", "计划")):
            pending_name_prefix = fragment
        elif "新一代电子信息技术" in fragment:
            pending_major_prefix = fragment
        elif records and (len(fragment) <= 3 or fragment in {"项计划）"}):
            _append_continuation(records[-1], fragment)
        elif "录取" in fragment or "计划" in fragment:
            pending_remark_prefix = fragment
        elif not any(term in fragment for term in ("序号", "考生编号", "齐齐哈尔大学", "公示", "考生", "咨询")):
            pending_direction_prefix = fragment
        index += 1
    return records


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
