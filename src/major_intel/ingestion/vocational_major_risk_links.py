"""Build risk-linkable outputs for MOE vocational major register records."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "vocational_major_risk_links/v1"
VOCATIONAL_REGISTER_SOURCE = "https://zwfw.moe.gov.cn/zyyxzy/"

ANNOTATED_FIELDS = [
    "record_id",
    "source_record_id",
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
    "duplicate_group_size",
    "duplicate_ordinal",
    "is_duplicate_api_row",
    "employment_warning_count",
    "employment_risk_levels",
    "employment_warning_years",
    "employment_warning_match_basis",
    "has_employment_high_risk_warning",
    "has_employment_red_warning",
    "has_employment_yellow_warning",
    "has_employment_green_signal",
    "official_policy_warning_count",
    "official_policy_record_types",
    "official_policy_years",
    "official_policy_match_basis",
    "has_official_policy_warning",
]

SUMMARY_FIELDS = [
    "major_key",
    "major_code",
    "major_name",
    "first_year",
    "latest_year",
    "years",
    "record_count",
    "province_count",
    "school_count",
    "latest_year_record_count",
    "latest_year_province_count",
    "latest_year_school_count",
    "sample_schools_latest_year",
    "api_duplicate_group_count",
    "api_duplicate_excess_row_count",
    "employment_warning_count",
    "employment_risk_levels",
    "employment_warning_years",
    "employment_warning_match_basis",
    "employment_warning_record_ids",
    "has_employment_high_risk_warning",
    "has_employment_red_warning",
    "has_employment_yellow_warning",
    "has_employment_green_signal",
    "official_policy_warning_count",
    "official_policy_record_types",
    "official_policy_years",
    "official_policy_match_basis",
    "official_policy_warning_ids",
    "has_official_policy_warning",
]


def build_vocational_major_risk_links(
    *,
    vocational_records_csv: Path,
    employment_warnings_csv: Path,
    official_policy_warnings_csv: Path,
    output_annotated_csv: Path,
    output_summary_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    """Annotate vocational major register rows with known warning link fields."""

    build_latest_year_counts_from_csv(vocational_records_csv)
    employment_refs = load_employment_warning_refs(employment_warnings_csv)
    policy_refs = load_policy_warning_refs(official_policy_warnings_csv)
    employment_by_code, employment_by_name = build_ref_indexes(employment_refs)
    policy_by_code, policy_by_name = build_ref_indexes(policy_refs)

    source_id_counts: Counter[str] = Counter()
    source_id_major_keys: dict[str, tuple[str, str]] = {}
    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    total_rows = 0
    years: set[str] = set()
    missing_counts: Counter[str] = Counter()

    for row in read_csv_rows(vocational_records_csv):
        total_rows += 1
        major_code = text(row.get("major_code"))
        major_name = text(row.get("major_name"))
        source_record_id = source_record_id_for(row)
        major_key = (major_code, major_name)
        source_id_counts[source_record_id] += 1
        source_id_major_keys.setdefault(source_record_id, major_key)
        if row.get("year"):
            years.add(text(row.get("year")))
        for field in ("record_id", "year", "province_name", "major_code", "major_name", "school_name", "source_url"):
            if not text(row.get(field)):
                missing_counts[field] += 1
        update_summary_seed(summaries, row)

    duplicate_group_count = sum(1 for value in source_id_counts.values() if value > 1)
    duplicate_excess_row_count = sum(value - 1 for value in source_id_counts.values() if value > 1)
    for source_record_id, count in source_id_counts.items():
        if count <= 1:
            continue
        key = source_id_major_keys[source_record_id]
        summary = summaries[key]
        summary["api_duplicate_group_count"] += 1
        summary["api_duplicate_excess_row_count"] += count - 1

    output_annotated_csv.parent.mkdir(parents=True, exist_ok=True)
    annotated_record_ids: set[str] = set()
    annotated_duplicate_ids = 0
    annotated_rows = 0
    linked_employment_rows = 0
    linked_policy_rows = 0
    occurrence_counts: Counter[str] = Counter()
    with output_annotated_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ANNOTATED_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in read_csv_rows(vocational_records_csv):
            source_record_id = source_record_id_for(row)
            occurrence_counts[source_record_id] += 1
            duplicate_size = source_id_counts[source_record_id]
            annotated = build_annotated_row(
                row,
                source_record_id=source_record_id,
                duplicate_size=duplicate_size,
                duplicate_ordinal=occurrence_counts[source_record_id],
                employment_by_code=employment_by_code,
                employment_by_name=employment_by_name,
                policy_by_code=policy_by_code,
                policy_by_name=policy_by_name,
            )
            if annotated["record_id"] in annotated_record_ids:
                annotated_duplicate_ids += 1
            annotated_record_ids.add(annotated["record_id"])
            if int(annotated["employment_warning_count"]):
                linked_employment_rows += 1
            if int(annotated["official_policy_warning_count"]):
                linked_policy_rows += 1
            writer.writerow(annotated)
            annotated_rows += 1

    summary_rows = build_summary_rows(
        summaries,
        employment_by_code=employment_by_code,
        employment_by_name=employment_by_name,
        policy_by_code=policy_by_code,
        policy_by_name=policy_by_name,
    )
    write_csv(output_summary_csv, summary_rows, SUMMARY_FIELDS)

    latest_year = max(years) if years else ""
    linked_employment_summary_rows = [row for row in summary_rows if int(row["employment_warning_count"])]
    linked_policy_summary_rows = [row for row in summary_rows if int(row["official_policy_warning_count"])]
    high_risk_summary_rows = [row for row in summary_rows if row["has_employment_high_risk_warning"] == "true"]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "source": VOCATIONAL_REGISTER_SOURCE,
        "vocational_records_csv": str(vocational_records_csv),
        "employment_warnings_csv": str(employment_warnings_csv),
        "official_policy_warnings_csv": str(official_policy_warnings_csv),
        "output_annotated_csv": str(output_annotated_csv),
        "output_summary_csv": str(output_summary_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "record_count": total_rows,
        "annotated_record_count": annotated_rows,
        "annotated_duplicate_record_id_count": annotated_duplicate_ids,
        "unique_major_count": len(summary_rows),
        "year_count": len(years),
        "first_year": min(years) if years else "",
        "latest_year": latest_year,
        "duplicate_group_count": duplicate_group_count,
        "duplicate_excess_row_count": duplicate_excess_row_count,
        "linked_employment_row_count": linked_employment_rows,
        "linked_employment_major_count": len(linked_employment_summary_rows),
        "linked_high_risk_major_count": len(high_risk_summary_rows),
        "linked_policy_row_count": linked_policy_rows,
        "linked_policy_major_count": len(linked_policy_summary_rows),
        "missing_counts": dict(missing_counts),
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(output_report_md, manifest, summary_rows)
    return manifest


def load_employment_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        if not is_vocational_level(row.get("education_level")):
            continue
        refs.append(
            {
                "id": text(row.get("record_id")),
                "major_code": text(row.get("major_code")),
                "major_name": major_name_from_warning(row),
                "year": text(row.get("report_year")),
                "risk_level": text(row.get("risk_level")),
                "education_level": text(row.get("education_level")),
            }
        )
    return refs


def load_policy_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        if not is_vocational_level(row.get("education_level")):
            continue
        refs.append(
            {
                "id": text(row.get("warning_id")),
                "major_code": text(row.get("major_code")),
                "major_name": major_name_from_warning(row),
                "year": text(row.get("policy_year")),
                "record_type": text(row.get("record_type")),
                "education_level": text(row.get("education_level")),
            }
        )
    return refs


def build_ref_indexes(refs: list[dict[str, str]]) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for ref in refs:
        if ref["major_code"]:
            by_code[ref["major_code"]].append(ref)
        if ref["major_name"]:
            by_name[ref["major_name"]].append(ref)
    return by_code, by_name


def build_annotated_row(
    row: dict[str, str],
    *,
    source_record_id: str,
    duplicate_size: int,
    duplicate_ordinal: int,
    employment_by_code: dict[str, list[dict[str, str]]],
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_code: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    major_code = text(row.get("major_code"))
    major_name = text(row.get("major_name"))
    employment_refs, employment_basis = match_refs(major_code, major_name, employment_by_code, employment_by_name)
    policy_refs, policy_basis = match_refs(major_code, major_name, policy_by_code, policy_by_name)
    employment_summary = summarize_employment_refs(employment_refs, employment_basis)
    policy_summary = summarize_policy_refs(policy_refs, policy_basis)
    record_id = source_record_id if duplicate_size == 1 else f"{source_record_id}:{duplicate_ordinal:03d}"
    return {
        "record_id": record_id,
        "source_record_id": source_record_id,
        "year": text(row.get("year")),
        "province_name": text(row.get("province_name")),
        "major_code": major_code,
        "major_name": major_name,
        "school_code": text(row.get("school_code")),
        "school_name": text(row.get("school_name")),
        "school_system": text(row.get("school_system")),
        "remark": text(row.get("remark")),
        "source_level": text(row.get("source_level")),
        "source_url": text(row.get("source_url")),
        "captured_at": text(row.get("captured_at")),
        "duplicate_group_size": duplicate_size,
        "duplicate_ordinal": duplicate_ordinal,
        "is_duplicate_api_row": bool_text(duplicate_size > 1),
        **employment_summary,
        **policy_summary,
    }


def update_summary_seed(summaries: dict[tuple[str, str], dict[str, Any]], row: dict[str, str]) -> None:
    major_code = text(row.get("major_code"))
    major_name = text(row.get("major_name"))
    key = (major_code, major_name)
    summary = summaries.setdefault(
        key,
        {
            "major_code": major_code,
            "major_name": major_name,
            "years": set(),
            "record_count": 0,
            "provinces": set(),
            "schools": set(),
            "latest_year_record_count": 0,
            "latest_year_provinces": set(),
            "latest_year_schools": set(),
            "api_duplicate_group_count": 0,
            "api_duplicate_excess_row_count": 0,
        },
    )
    year = text(row.get("year"))
    province = text(row.get("province_name"))
    school = text(row.get("school_name"))
    summary["record_count"] += 1
    if year:
        summary["years"].add(year)
    if province:
        summary["provinces"].add(province)
    if school:
        summary["schools"].add(school)


def build_summary_rows(
    summaries: dict[tuple[str, str], dict[str, Any]],
    *,
    employment_by_code: dict[str, list[dict[str, str]]],
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_code: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    latest_year = max((year for summary in summaries.values() for year in summary["years"]), default="")
    for summary in summaries.values():
        summary["latest_year_record_count"] = 0
        summary["latest_year_provinces"] = set()
        summary["latest_year_schools"] = set()

    # A second pass over summaries is not enough for latest-year counts; callers
    # populate all-year sets in the first pass, so compute latest-year detail in
    # build_latest_year_counts when producing outputs from the CSV.
    rows: list[dict[str, Any]] = []
    latest_counts = build_latest_year_counts.cache
    for key, summary in summaries.items():
        major_code, major_name = key
        years = sorted(summary["years"])
        latest = latest_year_for(years)
        latest_detail = latest_counts.get(key, {"records": 0, "provinces": set(), "schools": set()})
        employment_refs, employment_basis = match_refs(major_code, major_name, employment_by_code, employment_by_name)
        policy_refs, policy_basis = match_refs(major_code, major_name, policy_by_code, policy_by_name)
        employment_summary = summarize_employment_refs(employment_refs, employment_basis, include_ids=True)
        policy_summary = summarize_policy_refs(policy_refs, policy_basis, include_ids=True)
        rows.append(
            {
                "major_key": major_key(major_code, major_name),
                "major_code": major_code,
                "major_name": major_name,
                "first_year": years[0] if years else "",
                "latest_year": latest,
                "years": "|".join(years),
                "record_count": summary["record_count"],
                "province_count": len(summary["provinces"]),
                "school_count": len(summary["schools"]),
                "latest_year_record_count": latest_detail["records"],
                "latest_year_province_count": len(latest_detail["provinces"]),
                "latest_year_school_count": len(latest_detail["schools"]),
                "sample_schools_latest_year": "、".join(sorted(latest_detail["schools"])[:8]),
                "api_duplicate_group_count": summary["api_duplicate_group_count"],
                "api_duplicate_excess_row_count": summary["api_duplicate_excess_row_count"],
                **employment_summary,
                **policy_summary,
            }
        )
    return sorted(rows, key=lambda item: (item["major_code"], item["major_name"]))


def build_latest_year_counts_from_csv(path: Path) -> None:
    latest_year_by_key: dict[tuple[str, str], str] = {}
    for row in read_csv_rows(path):
        key = (text(row.get("major_code")), text(row.get("major_name")))
        year = text(row.get("year"))
        if year and year > latest_year_by_key.get(key, ""):
            latest_year_by_key[key] = year
    counts: dict[tuple[str, str], dict[str, Any]] = {}
    for row in read_csv_rows(path):
        key = (text(row.get("major_code")), text(row.get("major_name")))
        if text(row.get("year")) != latest_year_by_key.get(key):
            continue
        detail = counts.setdefault(key, {"records": 0, "provinces": set(), "schools": set()})
        detail["records"] += 1
        if text(row.get("province_name")):
            detail["provinces"].add(text(row.get("province_name")))
        if text(row.get("school_name")):
            detail["schools"].add(text(row.get("school_name")))
    build_latest_year_counts.cache = counts


def build_latest_year_counts() -> None:
    return None


build_latest_year_counts.cache = {}


def match_refs(
    major_code: str,
    major_name: str,
    by_code: dict[str, list[dict[str, str]]],
    by_name: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, str]], str]:
    refs_by_id: dict[str, dict[str, str]] = {}
    basis: list[str] = []
    if major_code and major_code in by_code:
        basis.append("code")
        for ref in by_code[major_code]:
            refs_by_id[ref["id"]] = ref
    if major_name and major_name in by_name:
        basis.append("name")
        for ref in by_name[major_name]:
            refs_by_id[ref["id"]] = ref
    refs = sorted(refs_by_id.values(), key=lambda item: (item.get("year", ""), item.get("id", "")))
    return refs, "+".join(basis)


def summarize_employment_refs(refs: list[dict[str, str]], basis: str, *, include_ids: bool = False) -> dict[str, Any]:
    risk_levels = ordered_unique([ref["risk_level"] for ref in refs], order=["red", "yellow", "green"])
    years = ordered_unique([ref["year"] for ref in refs])
    has_red = "red" in risk_levels
    has_yellow = "yellow" in risk_levels
    has_green = "green" in risk_levels
    summary: dict[str, Any] = {
        "employment_warning_count": len(refs),
        "employment_risk_levels": "|".join(risk_levels),
        "employment_warning_years": "|".join(years),
        "employment_warning_match_basis": basis,
        "has_employment_high_risk_warning": bool_text(has_red or has_yellow),
        "has_employment_red_warning": bool_text(has_red),
        "has_employment_yellow_warning": bool_text(has_yellow),
        "has_employment_green_signal": bool_text(has_green),
    }
    if include_ids:
        summary["employment_warning_record_ids"] = "|".join(ordered_unique([ref["id"] for ref in refs]))
    return summary


def summarize_policy_refs(refs: list[dict[str, str]], basis: str, *, include_ids: bool = False) -> dict[str, Any]:
    record_types = ordered_unique([ref["record_type"] for ref in refs])
    years = ordered_unique([ref["year"] for ref in refs])
    summary: dict[str, Any] = {
        "official_policy_warning_count": len(refs),
        "official_policy_record_types": "|".join(record_types),
        "official_policy_years": "|".join(years),
        "official_policy_match_basis": basis,
        "has_official_policy_warning": bool_text(bool(refs)),
    }
    if include_ids:
        summary["official_policy_warning_ids"] = "|".join(ordered_unique([ref["id"] for ref in refs]))
    return summary


def write_report(path: Path, manifest: dict[str, Any], summary_rows: list[dict[str, Any]]) -> None:
    latest_year = manifest.get("latest_year") or ""
    latest_rows = [row for row in summary_rows if row["latest_year"] == latest_year]
    red_or_yellow = [row for row in summary_rows if row["has_employment_high_risk_warning"] == "true"]
    policy_linked = [row for row in summary_rows if row["has_official_policy_warning"] == "true"]
    lines = [
        "# 高职专科专业设置备案明细与风险关联报告",
        "",
        f"- 源平台：{VOCATIONAL_REGISTER_SOURCE}",
        f"- 覆盖年份：{manifest['first_year']}-{manifest['latest_year']}（{manifest['year_count']} 年）",
        f"- 官方专业点明细行数：{manifest['record_count']}",
        f"- 跨年去重专业数：{manifest['unique_major_count']}",
        f"- 最新年份 {latest_year} 覆盖专业数：{len(latest_rows)}",
        f"- API 完全重复自然键组数：{manifest['duplicate_group_count']}",
        f"- API 完全重复超额行数：{manifest['duplicate_excess_row_count']}",
        f"- 可关联红/黄就业预警的高职专科专业数：{len(red_or_yellow)}",
        f"- 可关联官方政策/停招/撤销/控制专业记录的高职专科专业数：{len(policy_linked)}",
        f"- 行级就业预警关联数：{manifest['linked_employment_row_count']}",
        f"- 行级官方政策关联数：{manifest['linked_policy_row_count']}",
        "",
        "## 输出文件",
        "",
        f"- 明细增强表：`{manifest['output_annotated_csv']}`",
        f"- 专业级关联汇总：`{manifest['output_summary_csv']}`",
        f"- Manifest：`{manifest['output_manifest_json']}`",
        "",
        "## 使用说明",
        "",
        "- `record_id` 是增强表唯一行 ID；`source_record_id` 保留原始自然键哈希，因此可用于识别教育部接口返回的重复自然键。",
        "- `has_employment_high_risk_warning=true` 表示该高职专科专业在已抓取就业预警中出现过红牌或黄牌记录。",
        "- `has_official_policy_warning=true` 表示该专业可按专业代码或专业名关联到已抓取的官方停招、撤销、低就业、控制专业审批等政策记录。",
        "- 关联只使用高职高专/专科口径的就业预警和政策记录；本科口径保留在主数据集，不混入本表。",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def source_record_id_for(row: dict[str, str]) -> str:
    existing = text(row.get("record_id"))
    if existing:
        return existing
    key = "|".join(
        [
            text(row.get("year")),
            text(row.get("province_name")),
            text(row.get("major_code")),
            text(row.get("major_name")),
            text(row.get("school_code")),
            text(row.get("school_name")),
            text(row.get("school_system")),
        ]
    )
    return "vocational_major:" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def major_name_from_warning(row: dict[str, str]) -> str:
    return text(row.get("standard_major_name")) or text(row.get("reported_major_name"))


def major_key(major_code: str, major_name: str) -> str:
    return hashlib.sha256(f"{major_code}|{major_name}".encode("utf-8")).hexdigest()[:24]


def latest_year_for(years: list[str]) -> str:
    return years[-1] if years else ""


def ordered_unique(values: list[str], *, order: list[str] | None = None) -> list[str]:
    seen = {value for value in values if value}
    if order:
        return [value for value in order if value in seen] + sorted(seen - set(order))
    return sorted(seen)


def is_vocational_level(value: Any) -> bool:
    text_value = text(value)
    return "高职" in text_value or "高专" in text_value or "专科" in text_value


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build high-vocational major risk linkage outputs.")
    parser.add_argument(
        "--vocational-records-csv",
        type=Path,
        default=Path("data/processed/vocational_major_register/vocational_major_records_2013_2026.csv"),
    )
    parser.add_argument(
        "--employment-warnings-csv",
        type=Path,
        default=Path("data/processed/major_risk_warnings/major_risk_warning_records.csv"),
    )
    parser.add_argument(
        "--official-policy-warnings-csv",
        type=Path,
        default=Path("data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv"),
    )
    parser.add_argument(
        "--output-annotated-csv",
        type=Path,
        default=Path("data/processed/vocational_major_register/vocational_major_records_2013_2026_annotated.csv"),
    )
    parser.add_argument(
        "--output-summary-csv",
        type=Path,
        default=Path("data/processed/vocational_major_register/vocational_major_risk_link_summary_2013_2026.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/vocational_major_register/vocational_major_risk_links_manifest_2013_2026.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/vocational_major_register/vocational_major_risk_links_2013_2026.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_vocational_major_risk_links(
        vocational_records_csv=args.vocational_records_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        output_annotated_csv=args.output_annotated_csv,
        output_summary_csv=args.output_summary_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
