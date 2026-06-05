from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


INPUT_CSV = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch183_cug/records_clean.csv")
OUT_DIR = Path("data/processed/graduate_outcomes_official_site_websearch_web_20260527_batch183_cug_curated")
NON_ADMISSION_TERMS = ("放弃复试", "拟不录取", "不予录取", "未录取", "复试不合格")


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _append_remark(existing: str, note: str) -> str:
    existing = re.sub(r"\s+", " ", existing or "").strip()
    if not existing:
        return note
    if note in existing:
        return existing
    return f"{existing}; {note}"


def _numeric_fragment(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9.\s]+", value or "")) and bool(re.search(r"\d", value or ""))


def _looks_like_chinese_name(value: str) -> bool:
    return bool(re.fullmatch(r"[\u4e00-\u9fff]{2,4}", value or ""))


def repair_record(row: dict[str, Any]) -> dict[str, Any] | None:
    working = {field: row.get(field, "") for field in crawler.CLEAN_RECORD_CSV_FIELDS}
    working["needs_review"] = _truthy(row.get("needs_review"))

    if not working.get("person_name") and _looks_like_chinese_name(str(working.get("major") or "")):
        working["person_name"] = working.get("major")
        working["major"] = ""
        working["needs_review"] = False

    if _numeric_fragment(str(working.get("college") or "")):
        working["remarks"] = _append_remark(
            str(working.get("remarks") or ""),
            f"misparsed_college {working.get('college')}",
        )
        working["college"] = ""

    if any(term in " ".join(str(working.get(field) or "") for field in crawler.CLEAN_RECORD_CSV_FIELDS) for term in NON_ADMISSION_TERMS):
        return None

    if not working.get("person_name"):
        return None

    if working.get("needs_review"):
        return None

    clean = crawler._clean_record(working)
    if not clean.get("person_name"):
        return None
    return clean


def _person_source_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("person_name") or ""),
        str(row.get("student_id") or ""),
        str(row.get("source_url") or ""),
    )


def _preference_score(row: dict[str, Any]) -> int:
    score = 0
    admission_major = str(row.get("admission_major") or "")
    remarks = str(row.get("remarks") or "")
    if re.search(r"\d+\s+[\u4e00-\u9fff]", admission_major):
        score += 5
    if "拟录取" in remarks:
        score += 5
    if row.get("student_id"):
        score += 2
    if not row.get("needs_review"):
        score += 1
    return score


def _clean_for_output(row: dict[str, Any]) -> dict[str, Any]:
    working = {field: row.get(field, "") for field in crawler.CLEAN_RECORD_CSV_FIELDS}
    working["needs_review"] = _truthy(row.get("needs_review"))
    return crawler._clean_record(working)


def collapse_duplicate_person_source_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    order: list[tuple[str, str, str]] = []
    for row in rows:
        key = _person_source_key(row)
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(row)

    merged_rows: list[dict[str, Any]] = []
    for key in order:
        group = grouped[key]
        best = dict(max(group, key=_preference_score))
        for row in group:
            if row is best:
                continue
            if not best.get("ranking") and row.get("ranking"):
                best["ranking"] = row.get("ranking")
            if not best.get("major") and row.get("major"):
                best["major"] = row.get("major")
            if not best.get("college") and row.get("college"):
                best["college"] = row.get("college")
            if len(str(row.get("admission_major") or "")) > len(str(best.get("admission_major") or "")):
                best["admission_major"] = row.get("admission_major")
            row_remarks = str(row.get("remarks") or "").strip()
            if row_remarks and row_remarks not in str(best.get("remarks") or ""):
                best["remarks"] = _append_remark(str(best.get("remarks") or ""), f"detail {row_remarks}")
        best["needs_review"] = False
        merged_rows.append(_clean_for_output(best))
    return merged_rows


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    input_rows = _read_csv(INPUT_CSV)
    rows: list[dict[str, Any]] = []
    dropped = 0
    for row in input_rows:
        repaired = repair_record(row)
        if repaired is None:
            dropped += 1
            continue
        rows.append(repaired)
    before_collapse = len(rows)
    rows = collapse_duplicate_person_source_records(rows)

    rows.sort(
        key=lambda row: (
            str(row.get("source_url") or ""),
            int(str(row.get("ranking") or "0") if str(row.get("ranking") or "").isdigit() else 0),
            str(row.get("person_name") or ""),
            str(row.get("student_id") or ""),
        )
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    crawler._write_clean_records_csv(rows, OUT_DIR / "records_clean_curated.csv")
    summary_rows = crawler._build_summary_rows(rows)
    crawler._write_summary_csv(summary_rows, OUT_DIR / "school_year_summary_curated.csv")
    notes = [
        "batch183_cug_curated: repaired China University of Geosciences (Wuhan) official college admission-list rows.",
        "Repairs: move GIS rows where person_name shifted into major; move numeric score/rank fragments out of college.",
        f"input_rows={len(input_rows)}",
        f"kept={len(rows)}",
        f"dropped={dropped}",
        f"collapsed_duplicates={before_collapse - len(rows)}",
        f"summary_rows={summary_rows}",
    ]
    (OUT_DIR / "curation_notes.txt").write_text("\n".join(notes), encoding="utf-8")
    print({"input_rows": len(input_rows), "rows": len(rows), "dropped": dropped, "summary": summary_rows})


if __name__ == "__main__":
    main()
