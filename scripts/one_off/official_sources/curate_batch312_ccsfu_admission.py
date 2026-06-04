from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


PDF_PATH = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch312_ccsfu_attachment_probe/"
    "yjs.ccsfu.edu.cn/7f2cc96859938fd9.pdf"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch312_ccsfu_admission_curated"
)

SCHOOL_NAME = "长春师范大学"
YEAR = 2026
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"
SOURCE_URL = "https://yjs.ccsfu.edu.cn/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner=1321085661&wbfileid=0C498A5A7D40ACAC245F44889FE994B2"
SOURCE_PAGE = "https://yjs.ccsfu.edu.cn/info/1007/265600.htm"
TITLE = "长春师范大学2026年硕士研究生招生考试一志愿拟录取名单及未录取名单公示"

START_RE = re.compile(r"^(?P<name>\S+)\s+(?P<student_id>102056\d{9})\s+(?P<mode>全日制|非全日制)(?:\s+(?P<tail>.*))?$")
SCORE_RE = re.compile(
    r"^(?P<initial_score>\d{3})\s+"
    r"(?P<foreign_language_score>\d+(?:\.\d+)?)\s+"
    r"(?P<business_score>\d+(?:\.\d+)?)\s+"
    r"(?P<professional_score>\d+(?:\.\d+)?)\s+"
    r"(?:(?P<additional_score_1>\d+(?:\.\d+)?)\s+(?P<additional_score_2>\d+(?:\.\d+)?)\s+)?"
    r"(?P<interview_score>\d+(?:\.\d+)?)\s+"
    r"(?P<composite_score>\d+(?:\.\d+)?)\s+"
    r"(?P<status>是|否)"
    r"(?:\s+(?P<note>.+))?$"
)
NOISE_TOKENS = {
    "长春师范大学2026年硕士研究生招生考试",
    "一志愿考生成绩及拟录取结果",
    "考生姓名 考生编号 学习方式",
    "报考学院名",
    "报考专业名",
    "称",
    "初试",
    "总成绩",
    "外国语",
    "听说能",
    "力测试",
    "业务素",
    "质测试",
    "专业综",
    "合测试",
    "复试",
    "折算",
    "是否",
    "拟录取",
    "专项计划 备注",
}


def curate_records(*, raw_text: str | None = None, pdf_path: Path = PDF_PATH) -> list[dict[str, Any]]:
    if raw_text is None:
        raw_text = _extract_pdf_text_raw(pdf_path)
    rows = []
    for index, chunk in enumerate(_record_chunks(raw_text), start=1):
        parsed = _parse_chunk(chunk, index)
        if parsed and parsed["status"] == "是":
            rows.append(_record_from_data(parsed))
    return rows


def _extract_pdf_text_raw(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["pdftotext", "-raw", str(path), "-"],
            capture_output=True,
            text=False,
            timeout=30,
            check=False,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    return crawler._decode_pdftotext_output(completed.stdout).strip()


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _record_chunks(raw_text: str) -> list[list[str]]:
    chunks: list[list[str]] = []
    current: list[str] = []
    for raw_line in raw_text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        line = _clean(raw_line.replace("\x0c", " "))
        if not line or line in NOISE_TOKENS:
            continue
        if START_RE.match(line):
            if current:
                chunks.append(current)
            current = [line]
            continue
        if current:
            current.append(line)
    if current:
        chunks.append(current)
    return chunks


def _split_college_major(text: str) -> tuple[str, str]:
    value = _clean(text).replace(" ", "")
    if not value:
        return "", ""
    marker = "学院"
    if marker in value:
        index = value.index(marker) + len(marker)
        return value[:index], value[index:].strip()
    parts = value.split()
    if len(parts) >= 2:
        return parts[0], "".join(parts[1:])
    return value, ""


def _parse_chunk(chunk: list[str], ranking: int) -> dict[str, str] | None:
    start_match = START_RE.match(chunk[0])
    if not start_match:
        return None
    data = start_match.groupdict(default="")
    tail_parts = [data.pop("tail", "")]
    for line in chunk[1:]:
        if line not in NOISE_TOKENS:
            tail_parts.append(line)
    tail = _clean(" ".join(part for part in tail_parts if part))
    score_match, prefix = _find_score_match(tail)
    if not score_match:
        return None
    college, major = _split_college_major(prefix)
    parsed = {
        "ranking": str(ranking),
        "person_name": data["name"],
        "student_id": data["student_id"],
        "learning_mode": data["mode"],
        "college": college,
        "major": major,
        **score_match.groupdict(default=""),
    }
    return parsed


def _find_score_match(text: str) -> tuple[re.Match[str] | None, str]:
    parts = text.split()
    for index in range(len(parts)):
        candidate = " ".join(parts[index:])
        match = SCORE_RE.match(candidate)
        if match:
            return match, " ".join(parts[:index])
    return None, ""


def _remarks(data: dict[str, str]) -> str:
    parts = [
        f"learning_mode: {data.get('learning_mode', '')}",
        f"admission_status: {data.get('status', '')}",
        f"initial_score: {data.get('initial_score', '')}",
        f"foreign_language_score: {data.get('foreign_language_score', '')}",
        f"business_score: {data.get('business_score', '')}",
        f"professional_score: {data.get('professional_score', '')}",
        f"additional_score_1: {data.get('additional_score_1', '')}",
        f"additional_score_2: {data.get('additional_score_2', '')}",
        f"interview_score: {data.get('interview_score', '')}",
        f"composite_score: {data.get('composite_score', '')}",
        f"专项计划: {data.get('note', '')}",
        f"source_page: {SOURCE_PAGE}",
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
            "college": data["college"],
            "major": data["major"],
            "admission_major": data["major"],
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
                "batch312_ccsfu_admission_curated: parsed Changchun Normal University 2026 first-choice master admission PDF.",
                "The source PDF includes both admitted and not-admitted candidates; only rows with admission_status=是 were retained.",
                f"rows={len(rows)}",
                f"source_page={SOURCE_PAGE}",
                f"attachment={SOURCE_URL}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
