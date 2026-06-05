from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260602_batch328_xjmu_2023_admission/"
    "yjsxy.xjmu.edu.cn"
)
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch328_xjmu_2023_admission_curated"
)

SCHOOL_NAME = "新疆医科大学"
YEAR = 2023
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"

ETHNICITY_RE = (
    r"(?:汉|维吾尔|哈萨克|回|土家|藏|满|蒙古|柯尔克孜|哈尼|锡伯|苗|壮|达斡尔|俄罗斯|"
    r"塔吉克|乌孜别克|东乡|羌|白|瑶|布依|朝鲜|畲|黎|侗|彝|裕固|撒拉|佤|"
    r"水|傣|纳西|仫佬|仡佬|拉祜|景颇|土|鄂温克|鄂伦春|赫哲|高山|毛南|"
    r"保安|京|独龙|怒|普米|德昂|珞巴|门巴)\s*族"
)

START_RE = re.compile(r"(?m)^\s*(?P<ranking>\d+)\s+(?P<student_id>\d{12,15})\b")
BAD_STATUS_FRAGMENTS = (
    "不予拟录取",
    "拟不录取",
    "不予录取",
    "不予复试",
    "复试成绩不合",
    "资格审核不通",
    "计划受限",
    "放弃",
    "缺考",
    "候补",
)


@dataclass(frozen=True)
class PdfSource:
    path: Path
    source_url: str
    title: str
    batch_label: str


PDF_SOURCES = [
    PdfSource(
        path=RAW_DIR / "eb5d37a4fba7b548.pdf",
        source_url="https://yjsxy.xjmu.edu.cn/__local/6/B3/61/0EB24D18B758B3BE925C033E05C_22900A4B_98C6E.pdf",
        title="新疆医科大学2023年硕士研究生一志愿考生拟录取名单（不含推免生和本硕生）",
        batch_label="first_choice",
    ),
    PdfSource(
        path=RAW_DIR / "7932b816724cf2e3.pdf",
        source_url="https://yjsxy.xjmu.edu.cn/__local/F/C8/BE/0B5E79C116DC41A6D4B82162359_7DA3B66E_F6164.pdf",
        title="新疆医科大学2023年硕士研究生调剂考生拟录取名单（第一批）",
        batch_label="adjustment_first_batch",
    ),
]


def curate_records() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in PDF_SOURCES:
        raw_text = _extract_pdf_raw_text(source.path)
        rows.extend(curate_pdf_records(raw_text, source, starting_rank=len(rows) + 1))
    return rows


def curate_pdf_records(raw_text: str, source: PdfSource, *, starting_rank: int = 1) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for chunk in _candidate_chunks(raw_text):
        parsed = _parse_candidate_chunk(chunk)
        if not parsed:
            continue
        parsed["ranking"] = parsed.get("ranking") or str(starting_rank + len(rows))
        rows.append(_record_from_data(parsed, source))
    return rows


def _extract_pdf_raw_text(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["pdftotext", "-raw", str(path), "-"],
            capture_output=True,
            text=False,
            timeout=60,
            check=False,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    return crawler._decode_pdftotext_output(completed.stdout)


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\x0c", " ")).strip()


def _compact_name(value: str) -> str:
    return re.sub(r"\s+", "", value or "").strip()


def _candidate_chunks(raw_text: str) -> list[str]:
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    starts = list(START_RE.finditer(normalized))
    chunks: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(normalized)
        chunks.append(normalized[start.start() : end].strip())
    return chunks


def _parse_candidate_chunk(chunk: str) -> dict[str, str] | None:
    clean_chunk = _clean(_drop_page_noise(chunk))
    if not clean_chunk or any(fragment in clean_chunk for fragment in BAD_STATUS_FRAGMENTS):
        return None
    if "拟录取" not in clean_chunk:
        return None
    before_status, _, after_status = clean_chunk.partition("拟录取")
    match = re.match(
        rf"^(?P<ranking>\d+)\s+(?P<student_id>\d{{12,15}})\s+"
        rf"(?P<person_name>.+?)\s+(?P<ethnicity>{ETHNICITY_RE})\s+"
        rf"(?P<college>\d{{3}}.+?)\s+"
        rf"(?P<degree_type>学术学位|专业学位)\s+"
        rf"(?P<major_code>[0-9A-Z]{{5,6}})\s+"
        rf"(?P<major_name>.+?)\s+"
        rf"(?P<direction_code>\d{{2}})\s+"
        rf"(?P<direction_name>.+?)\s+"
        rf"(?P<study_mode>全日制|非全日制)\s+"
        rf"(?P<scores>.+?)\s*$",
        before_status,
    )
    if not match:
        return None
    data = match.groupdict(default="")
    numbers = re.findall(r"\d+(?:\.\d+)?", data["scores"])
    if len(numbers) < 3:
        return None
    data["person_name"] = _compact_name(data["person_name"])
    data["ethnicity"] = _compact_name(data["ethnicity"])
    data["college"] = _clean(data["college"])
    data["initial_score"] = numbers[0]
    data["interview_score"] = numbers[1]
    data["total_score"] = numbers[-1]
    if len(numbers) > 3:
        data["additional_scores"] = ",".join(numbers[2:-1])
    data["note"] = _clean_note(after_status)
    return data


def _drop_page_noise(value: str) -> str:
    lines: list[str] = []
    for line in value.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        clean = _clean(line)
        if not clean:
            continue
        if re.search(r"第\s*\d+\s*页", clean):
            continue
        if clean.startswith(("序号 考生编号", "新疆医科大学2023年硕士研究生")):
            continue
        if clean in {"学位", "类型", "专业", "代码", "研究", "方向", "码", "成绩"}:
            continue
        lines.append(clean)
    return " ".join(lines)


def _clean_note(value: str) -> str:
    note = _clean(_drop_page_noise(value))
    note = re.sub(r"序号 考生编号.*$", "", note).strip()
    return note


def _remarks(parts: list[tuple[str, str]]) -> str:
    return "; ".join(f"{key}: {_clean(value)}" for key, value in parts if _clean(value))


def _record_from_data(data: dict[str, str], source: PdfSource) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": data["person_name"],
            "student_id": data["student_id"],
            "college": data["college"],
            "major": data["major_name"],
            "admission_major": data["major_name"],
            "ranking": data["ranking"],
            "remarks": _remarks(
                [
                    ("admission_batch", source.batch_label),
                    ("ethnicity", data.get("ethnicity", "")),
                    ("degree_type", data.get("degree_type", "")),
                    ("major_code", data.get("major_code", "")),
                    ("direction_code", data.get("direction_code", "")),
                    ("research_direction", data.get("direction_name", "")),
                    ("study_mode", data.get("study_mode", "")),
                    ("initial_score", data.get("initial_score", "")),
                    ("interview_score", data.get("interview_score", "")),
                    ("additional_scores", data.get("additional_scores", "")),
                    ("total_score", data.get("total_score", "")),
                    ("official_admission_status", "拟录取"),
                    ("note", data.get("note", "")),
                ]
            ),
            "source_url": source.source_url,
            "title": source.title,
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
                "batch328_xjmu_2023_admission_curated: parsed Xinjiang Medical University 2023 first-choice and adjustment admission PDFs.",
                "Only chunks with official_admission_status=拟录取 were retained; 放弃/不予拟录取/不予复试/计划受限 rows were excluded.",
                f"rows={len(rows)}",
                *[f"source_pdf={source.source_url}" for source in PDF_SOURCES],
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
