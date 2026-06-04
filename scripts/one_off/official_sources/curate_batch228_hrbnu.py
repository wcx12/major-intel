from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_PDF = Path(
    "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch228_hrbnu/"
    "yjsxy.hrbnu.edu.cn/6edae7b26bf65f7b.pdf"
)
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch228_hrbnu_curated")

SOURCE_URL = (
    "http://yjsxy.hrbnu.edu.cn/system/_content/download.jsp?"
    "urltype=news.DownloadAttachUrl&owner=1255513605&wbfileid=D94C4D5DD4B897AB9BB988B9EB8141C1"
)
TITLE = "哈尔滨师范大学2026年硕士研究生招生一志愿拟录取名单公示"

STUDENT_ID_RE = re.compile(r"\d{15}")
MAJOR_CODE_RE = re.compile(r"^[0-9A-Z]{5,8}$")


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\ufeff", "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean_text(part) for part in parts) if part)


def _strip_watermark_digits(value: str) -> str:
    return re.sub(r"[０-９]{1,4}", " ", value)


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


def _parse_line(line: str, context: dict[str, str]) -> tuple[dict[str, str] | None, dict[str, str]]:
    line = _strip_watermark_digits(line)
    sid_match = STUDENT_ID_RE.search(line)
    if not sid_match:
        return None, context
    before = line[: sid_match.start()]
    after = line[sid_match.end() :]
    parts = [_clean_text(part) for part in re.split(r"\s{2,}", before) if _clean_text(part)]
    score_parts = _clean_text(after).split()
    if len(score_parts) < 3:
        return None, context

    mode_index = next((index for index, part in enumerate(parts) if part in {"全日制", "非全日制"}), -1)
    if mode_index < 0 or mode_index + 1 >= len(parts):
        return None, context

    if mode_index >= 3 and MAJOR_CODE_RE.fullmatch(parts[mode_index - 1]):
        row_context = {
            "college": parts[0],
            "admission_major": parts[1],
            "major_code": parts[mode_index - 1],
        }
    elif mode_index == 2 and MAJOR_CODE_RE.fullmatch(parts[1]) and context.get("college"):
        row_context = {
            "college": context["college"],
            "admission_major": parts[0],
            "major_code": parts[1],
        }
    elif mode_index >= 2:
        joined_major = re.match(r"(?P<admission_major>.+?)\s+(?P<major_code>[0-9A-Z]{5,8})$", parts[mode_index - 1])
        if not joined_major:
            return None, context
        row_context = {
            "college": parts[0],
            "admission_major": joined_major.group("admission_major"),
            "major_code": joined_major.group("major_code"),
        }
    elif mode_index == 0 and context:
        row_context = context
    else:
        return None, context

    parsed = {
        **row_context,
        "study_mode": parts[mode_index],
        "person_name": "".join(parts[mode_index + 1 :]),
        "student_id": sid_match.group(0),
        "initial_score": score_parts[0],
        "reexam_score": score_parts[1],
        "total_score": score_parts[2],
        "extra": " ".join(score_parts[3:]),
    }
    return parsed, row_context


def _record(base: dict[str, Any]) -> dict[str, Any]:
    return crawler._clean_record(
        {
            "school_name": "哈尔滨师范大学",
            "year": 2026,
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
            **base,
        }
    )


def curate_records(raw_pdf: Path = RAW_PDF) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ranking = 0
    context: dict[str, str] = {}
    for line in _pdf_text(raw_pdf):
        parsed, context = _parse_line(line, context)
        if not parsed:
            continue
        ranking += 1
        rows.append(
            _record(
                {
                    "person_name": parsed["person_name"],
                    "student_id": parsed["student_id"],
                    "college": parsed["college"],
                    "major": parsed["major_code"],
                    "admission_major": parsed["admission_major"],
                    "ranking": str(ranking),
                    "remarks": _remarks(
                        "batch 一志愿",
                        f"study_mode {parsed['study_mode']}",
                        f"initial_score {parsed['initial_score']}",
                        f"reexam_score {parsed['reexam_score']}",
                        f"total_score {parsed['total_score']}",
                        parsed["extra"],
                    ),
                }
            )
        )
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
