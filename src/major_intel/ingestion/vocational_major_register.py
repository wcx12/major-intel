"""Build combined indexes for MOE vocational major register crawl outputs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


RECORD_FIELDS = [
    "record_id",
    "year",
    "province_name",
    "major_code",
    "major_name",
    "school_code",
    "school_name",
    "school_system",
    "remark",
    "source_level",
    "source_url",
    "captured_at",
]
UNIQUE_FIELDS = [
    "major_key",
    "major_code",
    "major_name",
    "first_year",
    "latest_year",
    "years",
    "record_count",
    "province_count",
    "school_count",
    "sample_schools",
]


def load_records(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
    return records


def build_cross_year_unique_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        major_code = _text(record.get("major_code"))
        major_name = _text(record.get("major_name"))
        if not major_code and not major_name:
            continue
        key = (major_code, major_name)
        row = grouped.setdefault(
            key,
            {
                "major_key": f"{major_code}|{major_name}",
                "major_code": major_code,
                "major_name": major_name,
                "years": set(),
                "record_count": 0,
                "provinces": set(),
                "schools": set(),
            },
        )
        row["record_count"] += 1
        if record.get("year"):
            row["years"].add(str(record["year"]))
        if record.get("province_name"):
            row["provinces"].add(str(record["province_name"]))
        if record.get("school_name"):
            row["schools"].add(str(record["school_name"]))

    output_rows: list[dict[str, Any]] = []
    for row in grouped.values():
        years = sorted(row.pop("years"))
        provinces = sorted(row.pop("provinces"))
        schools = sorted(row.pop("schools"))
        row["first_year"] = years[0] if years else ""
        row["latest_year"] = years[-1] if years else ""
        row["years"] = ",".join(years)
        row["province_count"] = len(provinces)
        row["school_count"] = len(schools)
        row["sample_schools"] = "、".join(schools[:5])
        output_rows.append(row)
    return sorted(output_rows, key=lambda item: (item["major_code"], item["major_name"]))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_coverage_report(path: Path, records: list[dict[str, Any]], unique_rows: list[dict[str, Any]]) -> None:
    year_counts = Counter(str(row.get("year") or "") for row in records)
    lines = [
        "# 高职专科专业设置备案历史覆盖报告",
        "",
        f"- 记录数：{len(records)}",
        f"- 跨年去重专业数：{len(unique_rows)}",
        f"- 覆盖年份数：{len([year for year in year_counts if year])}",
        "",
        "## 年份覆盖",
        "",
    ]
    for year in sorted(year_counts):
        if year:
            lines.append(f"- {year}: {year_counts[year]} 条")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_index(
    *,
    input_jsonls: list[Path],
    output_records_csv: Path,
    output_unique_csv: Path,
    coverage_report: Path,
) -> dict[str, Any]:
    records = load_records(input_jsonls)
    unique_rows = build_cross_year_unique_rows(records)
    records.sort(
        key=lambda item: (
            str(item.get("year") or ""),
            str(item.get("province_name") or ""),
            str(item.get("major_code") or ""),
            str(item.get("school_name") or ""),
            str(item.get("school_system") or ""),
        )
    )
    write_csv(output_records_csv, records, RECORD_FIELDS)
    write_csv(output_unique_csv, unique_rows, UNIQUE_FIELDS)
    write_coverage_report(coverage_report, records, unique_rows)
    return {
        "record_count": len(records),
        "unique_major_count": len(unique_rows),
        "input_count": len(input_jsonls),
        "output_records_csv": str(output_records_csv),
        "output_unique_csv": str(output_unique_csv),
        "coverage_report": str(coverage_report),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build combined MOE vocational major register indexes.")
    parser.add_argument(
        "--input-jsonl",
        type=Path,
        action="append",
        dest="input_jsonls",
        required=True,
        help="Input vocational_major_records_*.jsonl. Pass multiple times.",
    )
    parser.add_argument(
        "--output-records-csv",
        type=Path,
        default=Path("data/processed/vocational_major_register/vocational_major_records_all_years.csv"),
    )
    parser.add_argument(
        "--output-unique-csv",
        type=Path,
        default=Path("data/processed/vocational_major_register/vocational_major_unique_all_years.csv"),
    )
    parser.add_argument(
        "--coverage-report",
        type=Path,
        default=Path("reports/vocational_major_register/vocational_major_register_coverage_all_years.md"),
    )
    args = parser.parse_args(argv)
    summary = build_index(
        input_jsonls=args.input_jsonls,
        output_records_csv=args.output_records_csv,
        output_unique_csv=args.output_unique_csv,
        coverage_report=args.coverage_report,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


if __name__ == "__main__":
    raise SystemExit(main())
