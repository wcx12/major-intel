from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


RAW_DIR = Path("data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch258_tmmu_recommendation")
OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260601_batch258_tmmu_recommendation_curated"
)

SCHOOL_NAME = "陆军军医大学"
YEAR = 2026
DOCUMENT_TYPE = "incoming_recommendation_admission_list"
ROUTE = "recommendation_exemption"

LOCAL_PLAN = "地方计划"
ENLISTMENT_PLAN = "入伍计划"

PDF_METADATA = {
    LOCAL_PLAN: {
        "source_url": "https://zs.tmmu.edu.cn/zsjy/houtai/eWebEditorV12/uploads/20251120/20251120181938689.pdf",
        "title": "陆军军医大学2026年地方计划推荐免试硕士研究生拟录取名单",
    },
    ENLISTMENT_PLAN: {
        "source_url": "https://zs.tmmu.edu.cn/zsjy/houtai/eWebEditorV12/uploads/20251120/20251120181948390.pdf",
        "title": "陆军军医大学2026年入伍计划推荐免试硕士研究生拟录取名单",
    },
}

ROW_RE = re.compile(
    r"^(?P<person_name>[\u4e00-\u9fff·]{2,8})\s+"
    r"(?P<gender>[男女])\s+"
    r"(?P<birth_date>\d{8})$"
)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _remarks(*parts: str) -> str:
    return "; ".join(part for part in (_clean(part) for part in parts) if part)


def _plan_from_text(text: str) -> str | None:
    if "地方计划推荐免试硕士研究生拟录取名单" in text:
        return LOCAL_PLAN
    if "入伍计划推荐免试硕士研究生拟录取名单" in text:
        return ENLISTMENT_PLAN
    return None


def _parse_pdf_text(text: str, plan: str) -> list[dict[str, Any]]:
    metadata = PDF_METADATA[plan]
    rows: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = _clean(raw_line)
        match = ROW_RE.match(line)
        if not match:
            continue
        rows.append(
            crawler._clean_record(
                {
                    "school_name": SCHOOL_NAME,
                    "year": YEAR,
                    "document_type": DOCUMENT_TYPE,
                    "route": ROUTE,
                    "person_name": match.group("person_name"),
                    "ranking": str(len(rows) + 1),
                    "remarks": _remarks(f"plan {plan}", f"gender {match.group('gender')}"),
                    "source_url": metadata["source_url"],
                    "title": metadata["title"],
                    "needs_review": True,
                }
            )
        )
    return rows


def curate_records(raw_dir: Path = RAW_DIR) -> list[dict[str, Any]]:
    records_by_plan: dict[str, list[dict[str, Any]]] = {LOCAL_PLAN: [], ENLISTMENT_PLAN: []}
    for pdf_path in sorted(raw_dir.glob("**/*.pdf")):
        text = crawler._extract_pdf_text_with_pdftotext(pdf_path)
        plan = _plan_from_text(text)
        if plan is None:
            continue
        records_by_plan[plan] = _parse_pdf_text(text, plan)
    return [*records_by_plan[LOCAL_PLAN], *records_by_plan[ENLISTMENT_PLAN]]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
