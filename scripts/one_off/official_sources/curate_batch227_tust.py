from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch227_tust_sdut_qut/yjs.tust.edu.cn"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch227_tust_sdut_qut_curated"
)


PDF_SOURCES = {
    "tust_2026_first_choice_batch1.pdf": {
        "source_url": "https://yjs.tust.edu.cn/docs/2026-04/7414a2ce0537420ca7e856a6b70b2e55.pdf",
        "title": "天津科技大学2026年硕士研究生一志愿拟录取考生名单公示(第一批）",
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "batch": "一志愿第一批",
    },
    "tust_2026_first_choice_batch2.pdf": {
        "source_url": "https://yjs.tust.edu.cn/docs/2026-04/54ecfe55e97e4e97bc0416c12b306082.pdf",
        "title": "天津科技大学2026年硕士研究生一志愿拟录取考生名单公示(第二批）",
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "batch": "一志愿第二批",
    },
    "tust_2026_transfer_batch1.pdf": {
        "source_url": "https://yjs.tust.edu.cn/docs/2026-04/ecdd6c14b30a4e068ef92eb6c4665c68.pdf",
        "title": "天津科技大学2026年硕士研究生调剂拟录取考生名单公示(第一批）",
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "batch": "调剂第一批",
    },
    "tust_2026_transfer_batch2.pdf": {
        "source_url": "https://yjs.tust.edu.cn/docs/2026-04/dfe203e574714bc5b85395b7b4003eec.pdf",
        "title": "天津科技大学2026年硕士研究生调剂拟录取考生名单公示(第二批）",
        "document_type": "postgraduate_admission_list",
        "route": "postgraduate_exam_or_admission",
        "batch": "调剂第二批",
    },
    "tust_2026_recommendation.pdf": {
        "source_url": "https://yjs.tust.edu.cn/docs/2025-10/afc63544fd1844949e14307bc46f3de1.pdf",
        "title": "天津科技大学接收2026届优秀应届本科毕业生免试攻读硕士学位研究生拟录取名单公示",
        "document_type": "incoming_recommendation_admission_list",
        "route": "recommendation_exemption",
        "batch": "接收推免",
    },
}


ADMISSION_ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d{1,4})\s+"
    r"(?P<student_id>\d{15})\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<college>.+?(?:学院|中心|部))\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<rest>.+?)\s*$"
)

ADMISSION_ROW_WITHOUT_NAME_RE = re.compile(
    r"^\s*(?P<ranking>\d{1,4})\s+"
    r"(?P<student_id>\d{15})\s+"
    r"(?P<college>.+?(?:学院|中心|部))\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<rest>.+?)\s*$"
)

ADMISSION_TAIL_RE = re.compile(
    r"^(?P<body>.+?)\s*"
    r"(?P<degree_type>学术学位|专业学位)\s*"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<composite_score>\d+(?:\.\d+)?)"
    r"(?:\s+(?P<extra>.*))?$"
)

SPLIT_DIRECTION_TAIL_RE = re.compile(
    r"^(?P<admission_major>\S+)\s+"
    r"(?P<direction_code>\d{2})\s+"
    r"(?P<study_mode>全日制|非全日制)\s+"
    r"(?P<initial_score>\d+)\s+"
    r"(?P<reexam_score>\d+(?:\.\d+)?)\s+"
    r"(?P<composite_score>\d+(?:\.\d+)?)"
    r"(?:\s+(?P<extra>.*))?$"
)

RECOMMENDATION_ROW_RE = re.compile(
    r"^\s*(?P<ranking>\d{1,3})\s+"
    r"(?P<college>.+?学院)\s+"
    r"(?P<person_name>\S+)\s+"
    r"(?P<gender>[男女])\s+"
    r"(?P<major_code>\d{6})\s+"
    r"(?P<admission_major>.+?)\s+"
    r"(?P<degree_type>学术学位|专业学位)\s+"
    r"(?P<assessment_score>\d+(?:\.\d+)?)\s+"
    r"(?P<undergraduate_school>\S+)\s+"
    r"(?P<undergraduate_major>.+?)\s*$"
)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _pdf_text(path: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.splitlines()


def _split_admission_body(body: str) -> tuple[str, str, str]:
    parts = _clean_text(body).split()
    if not parts:
        return "", "", ""
    admission_major = parts[0]
    direction_code = ""
    direction_name = ""
    if len(parts) >= 2 and re.fullmatch(r"\d{2}", parts[1]):
        direction_code = parts[1]
        direction_name = " ".join(parts[2:])
    elif len(parts) > 1:
        direction_name = " ".join(parts[1:])
    return admission_major, direction_code, direction_name


def _is_admission_record_start(line: str) -> bool:
    return bool(re.match(r"^\s*\d{1,4}\s+\d{15}\s+", line))


def _first_token(line: str) -> str:
    parts = _clean_text(line).split()
    if not parts:
        return ""
    token = parts[0]
    if token.isdigit() or re.fullmatch(r"\d+(?:\.\d+)?", token):
        return ""
    if _is_admission_record_start(line):
        return ""
    return token


def _nearby_wrapped_name(lines: list[str], index: int) -> str:
    previous = _first_token(lines[index - 1]) if index > 0 else ""
    following = _first_token(lines[index + 1]) if index + 1 < len(lines) else ""
    return f"{previous}{following}" or previous or following


def _combined_tail(lines: list[str], index: int, rest: str) -> str:
    parts = [rest]
    for offset in range(1, 4):
        next_index = index + offset
        if next_index >= len(lines) or _is_admission_record_start(lines[next_index]):
            break
        fragment = _clean_text(lines[next_index])
        if fragment:
            parts.append(fragment)
        if ADMISSION_TAIL_RE.search(_clean_text(" ".join(parts))):
            break
    return _clean_text(" ".join(parts))


def _record(base: dict[str, Any]) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": "天津科技大学",
            "year": 2026,
            "needs_review": False,
            **base,
        }
    )


def _parse_admission_pdf(path: Path, metadata: dict[str, str]) -> list[dict[str, Any]]:
    raw_rows: list[dict[str, Any]] = []
    lines = _pdf_text(path)
    for index, line in enumerate(lines):
        match = ADMISSION_ROW_RE.match(line)
        wrapped_name = ""
        if not match:
            match = ADMISSION_ROW_WITHOUT_NAME_RE.match(line)
            wrapped_name = _nearby_wrapped_name(lines, index) if match else ""
        if not match:
            continue
        tail_text = _clean_text(match.group("rest"))
        tail = ADMISSION_TAIL_RE.match(tail_text)
        if not tail:
            tail_text = _combined_tail(lines, index, match.group("rest"))
            tail = ADMISSION_TAIL_RE.match(tail_text)
        split_tail = None
        split_degree_type = ""
        split_direction_name = ""
        if not tail:
            split_tail = SPLIT_DIRECTION_TAIL_RE.match(tail_text)
            previous = _clean_text(lines[index - 1]) if index > 0 else ""
            degree_match = re.match(r"(?P<direction>.+?)\s*(?P<degree_type>学术学位|专业学位)$", previous)
            if split_tail and degree_match:
                split_degree_type = degree_match.group("degree_type")
                split_direction_name = _clean_text(f"{degree_match.group('direction')}{_first_token(lines[index + 1]) if index + 1 < len(lines) else ''}")
            else:
                split_tail = None
        if not tail and not split_tail:
            continue
        if tail:
            admission_major, direction_code, direction_name = _split_admission_body(tail.group("body"))
            degree_type = tail.group("degree_type")
            study_mode = tail.group("study_mode")
            initial_score = tail.group("initial_score")
            reexam_score = tail.group("reexam_score")
            composite_score = tail.group("composite_score")
            extra = tail.group("extra") or ""
        else:
            admission_major = split_tail.group("admission_major") if split_tail else ""
            direction_code = split_tail.group("direction_code") if split_tail else ""
            direction_name = split_direction_name
            degree_type = split_degree_type
            study_mode = split_tail.group("study_mode") if split_tail else ""
            initial_score = split_tail.group("initial_score") if split_tail else ""
            reexam_score = split_tail.group("reexam_score") if split_tail else ""
            composite_score = split_tail.group("composite_score") if split_tail else ""
            extra = split_tail.group("extra") or "" if split_tail else ""
        raw_rows.append(
            {
                "document_type": metadata["document_type"],
                "route": metadata["route"],
                "person_name": wrapped_name or match.groupdict().get("person_name", ""),
                "student_id": match.group("student_id"),
                "college": match.group("college"),
                "major": match.group("major_code"),
                "admission_major": admission_major,
                "ranking": match.group("ranking"),
                "remarks": _remarks(
                    f"batch {metadata['batch']}",
                    f"research_direction_code {direction_code}" if direction_code else "",
                    f"research_direction {direction_name}" if direction_name else "",
                    f"degree_type {degree_type}",
                    f"study_mode {study_mode}",
                    f"initial_score {initial_score}",
                    f"reexam_score {reexam_score}",
                    f"composite_score {composite_score}",
                    extra,
                ),
                "source_url": metadata["source_url"],
                "title": metadata["title"],
            }
        )
    code_major: dict[str, str] = {}
    for row in raw_rows:
        admission_major = str(row.get("admission_major") or "")
        if admission_major and not admission_major.isdigit():
            code_major.setdefault(str(row.get("major") or ""), admission_major)
    for row in raw_rows:
        if not row.get("admission_major") or str(row.get("admission_major")).isdigit():
            row["admission_major"] = code_major.get(str(row.get("major") or ""), row.get("admission_major") or "")
    return [_record(row) for row in raw_rows]


def _parse_recommendation_pdf(path: Path, metadata: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    lines = _pdf_text(path)
    for index, line in enumerate(lines):
        match = RECOMMENDATION_ROW_RE.match(line)
        first = _clean_text(line).split()
        if not match and first and first[0].isdigit() and index + 1 < len(lines):
            match = RECOMMENDATION_ROW_RE.match(_clean_text(f"{line} {lines[index + 1]}"))
        if not match:
            continue
        rows.append(
            _record(
                {
                    "document_type": metadata["document_type"],
                    "route": metadata["route"],
                    "person_name": match.group("person_name"),
                    "student_id": "",
                    "undergraduate_school": match.group("undergraduate_school"),
                    "undergraduate_major": match.group("undergraduate_major"),
                    "college": match.group("college"),
                    "major": match.group("major_code"),
                    "admission_major": match.group("admission_major"),
                    "ranking": match.group("ranking"),
                    "remarks": _remarks(
                        f"batch {metadata['batch']}",
                        f"gender {match.group('gender')}",
                        f"degree_type {match.group('degree_type')}",
                        f"assessment_score {match.group('assessment_score')}",
                    ),
                    "source_url": metadata["source_url"],
                    "title": metadata["title"],
                }
            )
        )
    return rows


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for filename, metadata in PDF_SOURCES.items():
        path = raw_dir / filename
        if not path.exists():
            continue
        if metadata["document_type"] == "incoming_recommendation_admission_list":
            rows.extend(_parse_recommendation_pdf(path, metadata))
        else:
            rows.extend(_parse_admission_pdf(path, metadata))
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
