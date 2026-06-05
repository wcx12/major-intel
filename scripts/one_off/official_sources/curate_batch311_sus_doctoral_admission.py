from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_TEXT_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch311_sus_doctoral_admission/"
    "yjsc.sus.edu.cn/sus_2020_doctoral_admission_web_pdf_text.txt"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch311_sus_doctoral_admission_curated"
)

SCHOOL_NAME = "上海体育大学"
SOURCE_SCHOOL_NAME = "上海体育学院"
YEAR = 2020
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"
SOURCE_URL = "https://yjsc.sus.edu.cn/__local/C/9B/29/2E3E4C2B32BCCD234FFA36D4DE2_850177CB_4B537.pdf?e=.pdf"
TITLE = "上海体育学院2020年博士研究生“申请-考核”制拟录取名单公示"

START_RE = re.compile(r"(?m)^201900\d{2}\s+")
SCORE_RE = re.compile(
    r"(?P<category>非定向就业|定向就业)\s+"
    r"(?P<foreign_score>\d+(?:\.\d+)?)\s+"
    r"(?P<written_score>\d+(?:\.\d+)?)\s+"
    r"(?P<interview_score>\d+(?:\.\d+)?)\s+"
    r"(?P<composite_score>\d+(?:\.\d+)?)"
    r"(?:\s+(?P<note>.+))?$"
)
ENGLISH_MARKERS = ("六级", "四级", "雅思", "境外学", "在重要岗位")


def curate_records(*, raw_text: str | None = None, raw_text_path: Path | None = None) -> list[dict[str, Any]]:
    if raw_text is None:
        path = raw_text_path or RAW_TEXT_PATH
        raw_text = path.read_text(encoding="utf-8")
    rows = []
    for index, chunk in enumerate(_split_candidate_chunks(raw_text), start=1):
        parsed = _parse_candidate_chunk(chunk, index)
        if parsed:
            rows.append(_record_from_data(parsed))
    return rows


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _compact(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def _split_candidate_chunks(raw_text: str) -> list[str]:
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"(?<!\n)\s+(?=201900\d{2}\s+)", "\n", normalized)
    starts = list(START_RE.finditer(normalized))
    chunks = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(normalized)
        chunks.append(normalized[start.start() : end].strip())
    return chunks


def _parse_name_and_gender(line: str, remaining_lines: list[str]) -> tuple[str, str, list[str]]:
    match = re.match(r"^(?P<student_id>201900\d{2})\s+(?P<name_gender>.+)$", line)
    if not match:
        return "", "", remaining_lines
    name_gender = _clean(match.group("name_gender"))
    if name_gender.endswith(("男", "女")):
        return name_gender[:-1].strip(), name_gender[-1], remaining_lines
    if remaining_lines and remaining_lines[0] in {"男", "女"}:
        return name_gender, remaining_lines[0], remaining_lines[1:]
    return name_gender, "", remaining_lines


def _english_marker_position(line: str) -> int | None:
    positions = [line.find(marker) for marker in ENGLISH_MARKERS if marker in line]
    return min(positions) if positions else None


def _is_english_continuation(line: str, current: str) -> bool:
    compact_line = _compact(line)
    compact_current = _compact(current)
    if compact_current.startswith("境外学") and compact_line == "习一年":
        return True
    if "（2003" in compact_current and compact_line == "年）":
        return True
    return False


def _extract_major_and_english(lines: list[str]) -> tuple[str, str]:
    major_parts: list[str] = []
    english_parts: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.search(r"(非定向|定向)\s*就", line):
            break
        marker_pos = _english_marker_position(line)
        if marker_pos is not None:
            before_marker = line[:marker_pos]
            after_marker = line[marker_pos:]
            if before_marker.strip():
                major_parts.append(before_marker)
            if after_marker.strip() and not after_marker.startswith("在重要岗位"):
                english_parts.append(after_marker)
                lookahead = index + 1
                while lookahead < len(lines) and _is_english_continuation(
                    lines[lookahead], " ".join(english_parts)
                ):
                    english_parts.append(lines[lookahead])
                    lookahead += 1
            break
        major_parts.append(line)
        index += 1
    return _compact("".join(major_parts)), _clean(" ".join(english_parts))


def _parse_scores(chunk_text: str) -> dict[str, str]:
    normalized = _clean(chunk_text)
    normalized = re.sub(r"非定向\s*就\s*业", "非定向就业", normalized)
    normalized = re.sub(r"定向\s*就\s*业", "定向就业", normalized)
    score_match = SCORE_RE.search(normalized)
    return score_match.groupdict(default="") if score_match else {}


def _parse_candidate_chunk(chunk: str, ranking: int) -> dict[str, str] | None:
    lines = [_clean(line) for line in chunk.splitlines() if _clean(line)]
    if not lines:
        return None
    student_match = re.match(r"^(?P<student_id>201900\d{2})\s+", lines[0])
    if not student_match:
        return None
    person_name, gender, body_lines = _parse_name_and_gender(lines[0], lines[1:])
    major, english_level = _extract_major_and_english(body_lines)
    scores = _parse_scores(" ".join(body_lines))
    if not person_name or not major or not scores:
        return None
    return {
        "ranking": str(ranking),
        "student_id": student_match.group("student_id"),
        "person_name": person_name,
        "gender": gender,
        "admission_major": major,
        "english_level": english_level,
        **scores,
    }


def _remarks(data: dict[str, str]) -> str:
    parts = [
        f"official_source_school_name: {SOURCE_SCHOOL_NAME}",
        f"gender: {data.get('gender', '')}",
        f"english_level: {data.get('english_level', '')}",
        f"admission_category: {data.get('category', '')}",
        f"foreign_language_score: {data.get('foreign_score', '')}",
        f"written_score: {data.get('written_score', '')}",
        f"interview_score: {data.get('interview_score', '')}",
        f"composite_score: {data.get('composite_score', '')}",
        f"note: {data.get('note', '')}",
    ]
    return "; ".join(_clean(part) for part in parts if not part.endswith(": "))


def _record_from_data(data: dict[str, str]) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": data["person_name"],
            "student_id": data["student_id"],
            "major": data["admission_major"],
            "admission_major": data["admission_major"],
            "ranking": data["ranking"],
            "remarks": _remarks(data),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
    )


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch311_sus_doctoral_admission_curated: parsed official Shanghai University of Sport 2020 doctoral admission PDF text.",
                "The source PDF was readable through the web index text layer, while direct curl from this workspace was blocked by the source site.",
                "Only rows with 201900xx candidate numbers and final admission scores were retained.",
                f"rows={len(rows)}",
                f"source={SOURCE_URL}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
