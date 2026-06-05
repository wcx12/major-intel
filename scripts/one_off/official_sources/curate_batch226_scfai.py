from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PROCESSED_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch226_scfai")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch226_scfai_curated")

DEFAULT_DOCUMENTS_JSONL = PROCESSED_DIR / "documents.jsonl"

STUDENT_ID_RE = re.compile(r"^(\d{15})\s+(.+)$")
COLLEGE_RE = re.compile(r"^(\d{3})(?!\d)([\u4e00-\u9fff].+)$")
MAJOR_RE = re.compile(r"^(\d{6})(?!\d)(.+)$")
DIRECTION_RE = re.compile(r"^\d{2,3}[\u4e00-\u9fff].*")
SCORE_RE = re.compile(r"^\d{3}\s+[\d.]+(?:\s+[\d.]+){1,}")

HEADER_FRAGMENTS = (
    "四川美术学院2026年",
    "口语听力",
    "拟录取院系",
    "考生编号",
    "复试成绩",
    "享受",
    "加分",
    "说明：",
    "【共",
    "拟录取学院",
    "考生姓名",
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _read_documents(path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                docs.append(json.loads(line))
    return docs


def _pdf_text(path: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-raw", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lines = []
    for raw_line in result.stdout.splitlines():
        line = _clean_text(raw_line)
        if line:
            lines.append(line)
    return lines


def _is_header(line: str) -> bool:
    return any(fragment in line for fragment in HEADER_FRAGMENTS)


def _is_context_or_record_line(line: str) -> bool:
    return bool(
        STUDENT_ID_RE.match(line)
        or COLLEGE_RE.match(line)
        or MAJOR_RE.match(line)
        or DIRECTION_RE.match(line)
        or SCORE_RE.match(line)
        or _is_header(line)
    )


def _college_name(text: str) -> str:
    match = COLLEGE_RE.match(text)
    return match.group(2) if match else text


def _split_college_major(text: str) -> tuple[str, str, str]:
    match = re.match(r"^(.+?)\s+(\d{6})(?!\d)(.+)$", text)
    if not match:
        return text, "", ""
    return match.group(1), match.group(2), match.group(3)


def _score_parts(line: str) -> tuple[str, str, str]:
    special_plan = "无" if re.search(r"\s无\s", f" {line} ") else ""
    for plan in ("少数民族骨干计划", "退役大学生士兵计划", "大学生士兵计划"):
        if plan in line:
            special_plan = plan
            break
    category = ""
    for value in ("非定向就业", "定向就业"):
        if value in line:
            category = value
            break
    score_match = re.search(r"(\d+\.\d+)\s+(?:无|少数民族骨干计划|退役大学生士兵计划|大学生士兵计划)", line)
    admission_score = score_match.group(1) if score_match else ""
    return admission_score, special_plan, category


def _record(
    *,
    document: dict[str, Any],
    document_type: str,
    route: str,
    person_name: str,
    student_id: str,
    college: str = "",
    major: str = "",
    admission_major: str = "",
    undergraduate_school: str = "",
    remarks: str = "",
) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": "四川美术学院",
            "year": 2026,
            "document_type": document_type,
            "route": route,
            "person_name": person_name,
            "student_id": student_id,
            "undergraduate_school": undergraduate_school,
            "college": college,
            "major": major,
            "admission_major": admission_major,
            "remarks": remarks,
            "source_url": document.get("source_url", ""),
            "title": document.get("title", ""),
            "needs_review": False,
        }
    )


def _parse_admission_pdf(document: dict[str, Any]) -> list[dict[str, Any]]:
    path = Path(document.get("raw_path") or "")
    current_college = ""
    pending_college = ""
    current_major_code = ""
    current_major_name = ""
    current_direction = ""
    pending_score_line = ""
    rows: list[dict[str, Any]] = []

    for line in _pdf_text(path):
        if _is_header(line):
            continue
        college_match = COLLEGE_RE.match(line)
        if college_match:
            current_college, embedded_major_code, embedded_major_name = _split_college_major(_college_name(line))
            if embedded_major_code:
                current_major_code = embedded_major_code
                current_major_name = embedded_major_name
            pending_college = current_college if not any(token in current_college for token in ("学院", "中心", "部")) else ""
            continue
        if pending_college and not _is_context_or_record_line(line):
            current_college = pending_college + line
            pending_college = ""
            continue
        student_match = STUDENT_ID_RE.match(line)
        if student_match:
            student_id, person_name = student_match.groups()
            admission_score, special_plan, category = _score_parts(pending_score_line)
            rows.append(
                _record(
                    document=document,
                    document_type="postgraduate_admission_list",
                    route="postgraduate_exam_or_admission",
                    person_name=person_name,
                    student_id=student_id,
                    college=current_college,
                    major=current_major_code,
                    admission_major=f"{current_major_code} {current_major_name}".strip(),
                    remarks=_remarks(
                        f"research_direction {current_direction}" if current_direction else "",
                        f"admission_score {admission_score}" if admission_score else "",
                        f"special_plan {special_plan}" if special_plan else "",
                        f"admission_category {category}" if category else "",
                    ),
                )
            )
            pending_score_line = ""
            continue
        embedded_student_match = re.match(r"^(.+?)\s+(\d{15})\s+(.+)$", line)
        if embedded_student_match and DIRECTION_RE.match(embedded_student_match.group(1)):
            current_direction = embedded_student_match.group(1)
            student_id = embedded_student_match.group(2)
            person_name = embedded_student_match.group(3)
            admission_score, special_plan, category = _score_parts(pending_score_line)
            rows.append(
                _record(
                    document=document,
                    document_type="postgraduate_admission_list",
                    route="postgraduate_exam_or_admission",
                    person_name=person_name,
                    student_id=student_id,
                    college=current_college,
                    major=current_major_code,
                    admission_major=f"{current_major_code} {current_major_name}".strip(),
                    remarks=_remarks(
                        f"research_direction {current_direction}",
                        f"admission_score {admission_score}" if admission_score else "",
                        f"special_plan {special_plan}" if special_plan else "",
                        f"admission_category {category}" if category else "",
                    ),
                )
            )
            pending_score_line = ""
            continue
        if pending_score_line and re.match(r"^\d+\.\d+\s+", line):
            pending_score_line = f"{pending_score_line} {line}"
            continue
        major_match = MAJOR_RE.match(line)
        if major_match:
            current_major_code = major_match.group(1)
            current_major_name = major_match.group(2)
            current_direction = ""
            continue
        if DIRECTION_RE.match(line) and not SCORE_RE.match(line):
            current_direction = line
            continue
        if current_direction and not _is_context_or_record_line(line):
            current_direction += line
            continue
        if SCORE_RE.match(line):
            pending_score_line = line
            continue
    return rows


def _recommendation_lines(path: Path) -> list[str]:
    return [line for line in _pdf_text(path) if not _is_header(line)]


def _parse_recommendation_pdf(document: dict[str, Any]) -> list[dict[str, Any]]:
    lines = _recommendation_lines(Path(document.get("raw_path") or ""))
    rows: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        id_match = re.fullmatch(r"\d{15}", line)
        if not id_match or index < 2:
            continue
        first = lines[index - 2]
        second = lines[index - 1]
        first_parts = first.split()
        second_parts = second.split()
        if len(first_parts) < 3 or len(second_parts) < 3:
            continue
        score = second_parts[-1]
        if not re.fullmatch(r"\d+(?:\.\d+)?", score):
            continue
        rows.append(
            _record(
                document=document,
                document_type="recommendation_exemption_list",
                route="recommendation_exemption",
                person_name=first_parts[0],
                student_id=line,
                undergraduate_school=first_parts[1],
                college=second_parts[0],
                admission_major="".join(first_parts[2:]),
                remarks=_remarks(
                    f"research_direction {''.join(second_parts[1:-1])}",
                    f"assessment_score {score}",
                ),
            )
        )
    return rows


def curate_records(*, documents_jsonl: Path = DEFAULT_DOCUMENTS_JSONL) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for document in _read_documents(documents_jsonl):
        raw_path = Path(document.get("raw_path") or "")
        if raw_path.suffix.lower() != ".pdf":
            continue
        title = document.get("title", "")
        if "复试成绩查分申请表" in title:
            continue
        parsed = (
            _parse_recommendation_pdf(document)
            if document.get("document_type") == "recommendation_exemption_list"
            else _parse_admission_pdf(document)
        )
        for row in parsed:
            key = (row.get("person_name", ""), row.get("student_id", ""), row.get("source_url", ""))
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
    return sorted(rows, key=lambda row: (row["source_url"], row["student_id"], row["person_name"]))


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    notes = [
        "batch226_scfai_curated: parsed Sichuan Fine Arts Institute 2026 admission/recommendation PDF lists.",
        "Generic PDF extraction misread table headers as records; curated parser uses pdftotext row reconstruction.",
        f"rows={len(rows)}",
        "source=https://www.scfai.edu.cn/zsb/info/1001/4386.htm",
        "source=https://www.scfai.edu.cn/zsb/info/1001/4436.htm",
        "source=https://www.scfai.edu.cn/zsb/info/1001/4106.htm",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
