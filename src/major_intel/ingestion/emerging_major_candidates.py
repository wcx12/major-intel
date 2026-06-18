"""Build CSV and coverage artifacts for emerging-major candidates."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CANDIDATE_CSV_FIELDS = [
    "candidate_id",
    "major_code",
    "major_name",
    "major_level",
    "discipline_category",
    "major_class",
    "degree",
    "study_years",
    "event_type",
    "event_year",
    "candidate_status",
    "source_title",
    "source_url",
    "attachment_url",
    "source_level",
    "evidence_text",
    "raw_path",
    "parsed_from",
    "captured_at",
    "warnings_json",
]

COVERAGE_CSV_FIELDS = [
    "source_year",
    "file_type",
    "parse_status",
    "attachment_count",
    "candidate_major_count",
    "row_count",
]

UNIQUE_MAJOR_CSV_FIELDS = [
    "major_key",
    "major_code",
    "major_name",
    "major_level",
    "discipline_category",
    "major_class",
    "first_event_year",
    "latest_event_year",
    "event_types",
    "candidate_statuses",
    "source_levels",
    "source_count",
    "attachment_count",
    "evidence_count",
    "first_source_title",
    "first_source_url",
    "sample_evidence_text",
]


def build_outputs(
    *,
    candidates_jsonl: Path,
    attachments_jsonl: Path,
    output_csv: Path,
    coverage_report: Path,
    coverage_csv: Path | None = None,
    unique_major_csv: Path | None = None,
) -> dict[str, Any]:
    candidates = read_jsonl(candidates_jsonl)
    attachments = read_jsonl(attachments_jsonl)
    write_candidates_csv(candidates, output_csv)
    unique_major_rows = build_unique_major_rows(candidates)
    if unique_major_csv:
        write_unique_major_csv(unique_major_rows, unique_major_csv)
    coverage_rows = build_coverage_rows(attachments)
    if coverage_csv:
        write_coverage_csv(coverage_rows, coverage_csv)
    write_coverage_report(candidates, attachments, coverage_rows, coverage_report, unique_major_count=len(unique_major_rows))
    return {
        "candidate_count": len(candidates),
        "unique_major_count": len(unique_major_rows),
        "attachment_count": len(attachments),
        "output_csv": str(output_csv),
        "unique_major_csv": str(unique_major_csv) if unique_major_csv else None,
        "coverage_report": str(coverage_report),
        "coverage_csv": str(coverage_csv) if coverage_csv else None,
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_candidates_csv(candidates: list[dict[str, Any]], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_CSV_FIELDS)
        writer.writeheader()
        for row in candidates:
            writer.writerow(
                {
                    **{field: row.get(field, "") for field in CANDIDATE_CSV_FIELDS},
                    "warnings_json": json.dumps(row.get("warnings", []), ensure_ascii=False),
                }
            )


def build_unique_major_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        major_code = str(row.get("major_code") or "").strip()
        major_name = str(row.get("major_name") or "").strip()
        if not major_code and not major_name:
            continue
        grouped[f"{major_code}|{major_name}"].append(row)

    rows: list[dict[str, Any]] = []
    for major_key, group in grouped.items():
        first_row = min(group, key=lambda row: (_event_year_sort_key(row), str(row.get("candidate_id") or "")))
        event_years = [int(row["event_year"]) for row in group if str(row.get("event_year") or "").isdigit()]
        source_urls = {str(row.get("source_url") or "") for row in group if row.get("source_url")}
        attachment_urls = {str(row.get("attachment_url") or "") for row in group if row.get("attachment_url")}
        rows.append(
            {
                "major_key": major_key,
                "major_code": str(first_row.get("major_code") or ""),
                "major_name": str(first_row.get("major_name") or ""),
                "major_level": _first_non_empty(group, "major_level"),
                "discipline_category": _first_non_empty(group, "discipline_category"),
                "major_class": _first_non_empty(group, "major_class"),
                "first_event_year": min(event_years) if event_years else "",
                "latest_event_year": max(event_years) if event_years else "",
                "event_types": ";".join(sorted({str(row.get("event_type") or "") for row in group if row.get("event_type")})),
                "candidate_statuses": ";".join(
                    sorted({str(row.get("candidate_status") or "") for row in group if row.get("candidate_status")})
                ),
                "source_levels": ";".join(sorted({str(row.get("source_level") or "") for row in group if row.get("source_level")})),
                "source_count": len(source_urls),
                "attachment_count": len(attachment_urls),
                "evidence_count": len(group),
                "first_source_title": str(first_row.get("source_title") or ""),
                "first_source_url": str(first_row.get("source_url") or ""),
                "sample_evidence_text": str(first_row.get("evidence_text") or ""),
            }
        )
    return sorted(rows, key=lambda row: (str(row["major_code"]), str(row["major_name"])))


def write_unique_major_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=UNIQUE_MAJOR_CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_coverage_rows(attachments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "attachment_count": 0,
            "candidate_major_count": 0,
            "row_count": 0,
        }
    )
    for attachment in attachments:
        key = (
            str(attachment.get("source_year") or ""),
            str(attachment.get("file_type") or ""),
            str(attachment.get("parse_status") or ""),
        )
        grouped[key]["attachment_count"] += 1
        grouped[key]["candidate_major_count"] += int(attachment.get("candidate_major_count") or 0)
        grouped[key]["row_count"] += int(attachment.get("row_count") or 0)

    rows: list[dict[str, Any]] = []
    for (source_year, file_type, parse_status), metrics in sorted(grouped.items()):
        rows.append(
            {
                "source_year": source_year,
                "file_type": file_type,
                "parse_status": parse_status,
                **metrics,
            }
        )
    return rows


def write_coverage_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COVERAGE_CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_coverage_report(
    candidates: list[dict[str, Any]],
    attachments: list[dict[str, Any]],
    coverage_rows: list[dict[str, Any]],
    path: Path,
    *,
    unique_major_count: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(str(row.get("candidate_status") or "") for row in candidates)
    event_counts = Counter(str(row.get("event_type") or "") for row in candidates)
    needs_review = [row for row in attachments if row.get("parse_status") != "ok"]

    lines = [
        "# 新兴专业候选覆盖报告",
        "",
        f"- 候选专业数：{len(candidates)}",
        f"- 去重专业数：{unique_major_count}",
        f"- 附件数：{len(attachments)}",
        f"- 需要复核附件数：{len(needs_review)}",
        "",
        "## 候选状态",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- `{status}`: {count}")

    lines.extend(["", "## 事件类型", ""])
    for event_type, count in sorted(event_counts.items()):
        lines.append(f"- `{event_type}`: {count}")

    lines.extend(["", "## 附件覆盖", ""])
    if not coverage_rows:
        lines.append("- 无附件记录")
    for row in coverage_rows:
        lines.append(
            "- "
            f"{row['source_year']} / {row['file_type']} / parse_status={row['parse_status']}: "
            f"attachments={row['attachment_count']}, "
            f"candidate_majors={row['candidate_major_count']}, "
            f"rows={row['row_count']}"
        )

    lines.extend(["", "## 需要复核的附件", ""])
    if not needs_review:
        lines.append("- 无")
    for row in needs_review[:100]:
        lines.append(
            "- "
            f"{row.get('source_year', '')} {row.get('file_type', '')} "
            f"{row.get('parse_status', '')} {row.get('attachment_url', '')}"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _event_year_sort_key(row: dict[str, Any]) -> int:
    value = row.get("event_year")
    return int(value) if str(value or "").isdigit() else 9999


def _first_non_empty(rows: list[dict[str, Any]], key: str) -> str:
    for row in rows:
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build emerging-major CSV and coverage report.")
    parser.add_argument("--candidates-jsonl", type=Path, required=True)
    parser.add_argument("--attachments-jsonl", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--unique-major-csv", type=Path, default=None)
    parser.add_argument("--coverage-report", type=Path, required=True)
    parser.add_argument("--coverage-csv", type=Path, default=None)
    args = parser.parse_args(argv)

    summary = build_outputs(
        candidates_jsonl=args.candidates_jsonl,
        attachments_jsonl=args.attachments_jsonl,
        output_csv=args.output_csv,
        unique_major_csv=args.unique_major_csv,
        coverage_report=args.coverage_report,
        coverage_csv=args.coverage_csv,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
