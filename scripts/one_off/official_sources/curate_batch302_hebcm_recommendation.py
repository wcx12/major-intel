from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


XLS_PATH = Path("tmp/hebcm_reco_batch1.xls")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch302_hebcm_recommendation_curated")

SCHOOL_NAME = "河北中医药大学"
YEAR = 2026
DOCUMENT_TYPE = "incoming_recommendation_admission_list"
ROUTE = "recommendation_exemption"
SOURCE_URL = "https://yjsxy.hebcm.edu.cn/download.jsp?pathfile=/atm/7/20250926184432892.xls"
TITLE = "河北中医药大学2026年拟录取推免生公示（第一批）"


def _load_xlrd():
    try:
        import xlrd  # type: ignore[import-not-found]

        return xlrd
    except ImportError:
        local_package_dir = Path("tmp/xlrd_pkg")
        if local_package_dir.exists():
            sys.path.insert(0, str(local_package_dir.resolve()))
            import xlrd  # type: ignore[import-not-found]

            return xlrd
        raise RuntimeError("xlrd is required to parse batch302 legacy .xls attachments.")


def _clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return re.sub(r"\s+", " ", str(value)).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean(part) for part in parts) if part)


def _is_admitted_status(status: str) -> bool:
    status = _clean(status)
    return status.startswith("待录取")


def _record_from_row(values: list[Any]) -> dict[str, Any] | None:
    padded = values[:11] + [""] * max(0, 11 - len(values))
    (
        ranking,
        person_name,
        college_code,
        college,
        major_code,
        admission_major,
        direction_code,
        direction,
        learning_mode,
        interview_score,
        status,
    ) = [_clean(value) for value in padded[:11]]
    if not person_name or person_name == "姓名" or not _is_admitted_status(status):
        return None

    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": person_name,
            "student_id": "",
            "college": college,
            "major": admission_major,
            "admission_major": admission_major,
            "ranking": ranking,
            "remarks": _remarks(
                f"college_code: {college_code}" if college_code else "",
                f"major_code: {major_code}" if major_code else "",
                f"direction_code: {direction_code}" if direction_code else "",
                f"research_direction: {direction}" if direction else "",
                f"learning_mode: {learning_mode}" if learning_mode else "",
                f"interview_score: {interview_score}" if interview_score else "",
                f"admission_status: {status}",
            ),
            "source_url": SOURCE_URL,
            "title": TITLE,
            "needs_review": False,
        }
    )


def curate_records(*, xls_path: Path = XLS_PATH) -> list[dict[str, Any]]:
    xlrd = _load_xlrd()
    workbook = xlrd.open_workbook(str(xls_path))
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for sheet in workbook.sheets():
        for row_index in range(sheet.nrows):
            record = _record_from_row(sheet.row_values(row_index))
            if not record:
                continue
            key = (record["person_name"], record["admission_major"], record["remarks"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(record)
    return sorted(rows, key=lambda row: (row["ranking"], row["person_name"]))


def main() -> None:
    rows = curate_records()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    crawler._write_summary_csv(crawler._build_summary_rows(rows), OUT_DIR / "school_year_summary_curated.csv")
    (OUT_DIR / "curation_notes.txt").write_text(
        "\n".join(
            [
                "batch302_hebcm_recommendation_curated: parsed Hebei University of Chinese Medicine 2026 recommendation admission xls.",
                "Only rows whose remarks start with 待录取 are retained; 未参加复试/放弃待录取通知/拒绝待录取通知/拒绝复试通知/已被其他院校录取 rows are excluded.",
                f"rows={len(rows)}",
                "source=https://yjsxy.hebcm.edu.cn/col/1628824153772/2025/09/26/1758884165127.html",
                f"attachment={SOURCE_URL}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print({"rows": len(rows), "output": str(OUT_DIR / "records_clean_curated.csv")})


if __name__ == "__main__":
    main()
