from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch263_jhun_admission/gs.jhun.edu.cn")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch263_jhun_admission_curated")

SCHOOL_NAME = "江汉大学"
YEAR = 2026
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"

MASTER_TITLE = "2026年江汉大学硕士研究生招生拟录取名单"
MASTER_SOURCE_URL = "https://gs.jhun.edu.cn/_upload/article/files/03/70/0ba7d8654dd49cc10a4b83d080c5/0e8e8a8e-f708-4002-89fa-4d7bc5276fce.pdf"
DOCTOR_TITLE = "江汉大学2026年博士研究生招生拟录取名单公示"
DOCTOR_SOURCE_URL = "https://gs.jhun.edu.cn/_upload/article/files/bb/53/6cf23a744e65af0a031032a991c3/4deb0b5b-02d6-430b-a15e-7c0e2e8dc55e.pdf"

LEARNING_MODES = {"全日制", "非全日制"}
NUMBER_RE = re.compile(r"^\d+(?:\.\d+)?$")
STUDENT_ID_RE = re.compile(r"^\d{15}$")


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalize_record_text(value: str) -> str:
    text = _clean(value)
    text = re.sub(r"\s+院\s+", " ", text)
    text = text.replace("数字建造与爆破工程学 ", "数字建造与爆破工程学院 ")
    return _clean(text)


def _logical_rows(text: str) -> list[str]:
    rows: list[str] = []
    current = ""
    for raw_line in text.splitlines():
        line = _clean(raw_line)
        if not line:
            continue
        if re.match(r"^\d{1,4}\s+", line):
            if current:
                rows.append(_normalize_record_text(current))
            current = line
        elif current:
            current = f"{current} {line}"
    if current:
        rows.append(_normalize_record_text(current))
    return rows


def _take_scores(tokens: list[str], mode_index: int) -> tuple[list[str], list[str], str, str]:
    before_mode = tokens[:mode_index]
    learning_mode = tokens[mode_index]
    extra_remarks = " ".join(tokens[mode_index + 1 :])
    scores: list[str] = []
    while before_mode and NUMBER_RE.match(before_mode[-1]) and len(scores) < 4:
        scores.append(before_mode.pop())
    scores.reverse()
    return before_mode, scores, learning_mode, extra_remarks


def _split_college_major(tokens: list[str]) -> tuple[str, str]:
    if len(tokens) < 2:
        return "", ""
    return tokens[0], " ".join(tokens[1:])


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean(part) for part in parts) if part)


def _master_record(row_text: str) -> dict[str, Any] | None:
    tokens = row_text.split()
    if len(tokens) < 7 or not tokens[0].isdigit():
        return None
    mode_index = next((i for i, token in enumerate(tokens) if token in LEARNING_MODES), -1)
    if mode_index < 0:
        return None
    ranking = tokens[0]
    person_name = tokens[1]
    offset = 2
    student_id = ""
    if offset < len(tokens) and STUDENT_ID_RE.match(tokens[offset]):
        student_id = tokens[offset]
        offset += 1
    before_mode, scores, learning_mode, extra_remarks = _take_scores(tokens[offset:], mode_index - offset)
    college, major = _split_college_major(before_mode)
    if not person_name or not college or not major:
        return None
    score_labels = ["初试成绩", "复试成绩", "录取成绩"][-len(scores) :]
    remarks = _remarks(
        *(f"{label}: {score}" for label, score in zip(score_labels, scores)),
        f"学习方式: {learning_mode}",
        extra_remarks,
    )
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": person_name,
            "student_id": student_id,
            "college": college,
            "major": major,
            "admission_major": major,
            "ranking": ranking,
            "remarks": remarks,
            "source_url": MASTER_SOURCE_URL,
            "title": MASTER_TITLE,
            "needs_review": not bool(student_id),
        }
    )


def _parse_master(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row_text in _logical_rows(text):
        record = _master_record(row_text)
        if record:
            rows.append(record)
    return rows


def _doctor_logical_rows(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    current_section = ""
    current = ""
    for raw_line in text.splitlines():
        line = _clean(raw_line)
        if not line:
            continue
        if line in {"普通招考类", "申请—考核制", "申请-考核制"}:
            if current:
                rows.append((current_section, _normalize_record_text(current)))
                current = ""
            current_section = "申请-考核制" if "申请" in line else "普通招考类"
            continue
        if re.match(r"^\d{1,4}\s+\d{15}\s+", line):
            if current:
                rows.append((current_section, _normalize_record_text(current)))
            current = line
        elif current:
            current = f"{current} {line}"
    if current:
        rows.append((current_section, _normalize_record_text(current)))
    return rows


def _doctor_record(section: str, row_text: str) -> dict[str, Any] | None:
    tokens = row_text.split()
    if len(tokens) < 8 or not tokens[0].isdigit() or not STUDENT_ID_RE.match(tokens[1]):
        return None
    mode_index = next((i for i, token in enumerate(tokens) if token in LEARNING_MODES), -1)
    if mode_index < 0:
        return None
    ranking = f"{section}-{tokens[0]}" if section else tokens[0]
    student_id = tokens[1]
    person_name = tokens[2]
    before_mode, scores, learning_mode, extra_remarks = _take_scores(tokens[3:], mode_index - 3)
    if before_mode == ["化学工程与技术"] and "学院" in extra_remarks:
        college, major = "数字建造与爆破工程学院", "化学工程与技术"
        extra_remarks = (
            extra_remarks.replace("学院 数字建造与爆破工程", "")
            .replace("数字建造与爆破工程 学院", "")
            .replace("学院", "")
        )
    else:
        college, major = _split_college_major(before_mode)
    if not college or not major:
        return None
    score_labels = ["初试成绩", "复试成绩", "录取成绩"] if section == "普通招考类" else ["材料审核成绩", "笔试成绩", "面试成绩", "录取成绩"]
    score_labels = score_labels[-len(scores) :]
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": person_name,
            "student_id": student_id,
            "college": college,
            "major": major,
            "admission_major": major,
            "ranking": ranking,
            "remarks": _remarks(
                f"招考方式: {section}" if section else "",
                *(f"{label}: {score}" for label, score in zip(score_labels, scores)),
                f"学习方式: {learning_mode}",
                extra_remarks,
            ),
            "source_url": DOCTOR_SOURCE_URL,
            "title": DOCTOR_TITLE,
            "needs_review": False,
        }
    )


def _parse_doctor(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for section, row_text in _doctor_logical_rows(text):
        record = _doctor_record(section, row_text)
        if record:
            rows.append(record)
    return rows


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_path in sorted(raw_dir.glob("*.pdf")):
        text = crawler._extract_pdf_text_with_pdftotext(pdf_path)
        if "硕士研究生招生拟录取名单" in text:
            rows.extend(_parse_master(text))
        elif "博士研究生招生拟录取名单" in text:
            rows.extend(_parse_doctor(text))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
