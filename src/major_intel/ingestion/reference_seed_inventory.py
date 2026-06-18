from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SEED_DIR = ROOT / "data/seeds"
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/reference_seed_inventory"
DEFAULT_REPORT_DIR = ROOT / "reports/reference_seed_inventory"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _path_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _csv_fields(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            return next(reader, [])
    except (OSError, UnicodeDecodeError):
        return []


def _line_count(path: Path) -> int:
    with path.open("rb") as handle:
        return sum(chunk.count(b"\n") for chunk in iter(lambda: handle.read(1024 * 1024), b""))


def _row_count(path: Path, suffix: str) -> int:
    if suffix == ".csv":
        return max(_line_count(path) - 1, 0)
    if suffix == ".jsonl":
        return _line_count(path)
    return 0


def seed_family(path: Path) -> str:
    name = path.name
    if name.startswith("rysxai_professions"):
        return "rysxai_profession_seed"
    if name.startswith("rysxai_universities"):
        return "rysxai_university_seed"
    if name.startswith("policy_document_sources"):
        return "policy_document_source_seed"
    if name.startswith("policy_evidence_sources"):
        return "policy_evidence_source_seed"
    if name.startswith("official_site_recommendation_websearch"):
        return "graduate_official_site_websearch_seed"
    if name.startswith("official_site_recommendation"):
        return "graduate_official_site_seed"
    if name.startswith("official_site_uncovered"):
        return "graduate_official_site_gap_seed"
    if name.startswith("chsi"):
        return "chsi_source_seed"
    if name.startswith("graduate_outcome"):
        return "graduate_outcome_sample_seed"
    if name.startswith("emerging_major"):
        return "emerging_major_source_query_seed"
    return "other_seed"


def source_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except ValueError:
        return ""


def build_file_manifest(seed_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(seed_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        fields = _csv_fields(path) if suffix == ".csv" else []
        info = file_info(path)
        rows.append(
            {
                "file": _path_key(path),
                "file_name": path.name,
                "seed_family": seed_family(path),
                "suffix": suffix,
                "bytes": info["bytes"],
                "sha256": info["sha256"],
                "row_count": _row_count(path, suffix),
                "fields": ";".join(fields),
            }
        )
    return rows


def official_site_seed_rows(seed_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(seed_dir.glob("*.csv")):
        fields = set(_csv_fields(path))
        if not {"school_name", "start_url"}.issubset(fields):
            continue
        for row in read_csv(path):
            start_url = row.get("start_url", "")
            rows.append(
                {
                    "seed_file": _path_key(path),
                    "seed_family": seed_family(path),
                    "school_name": row.get("school_name", ""),
                    "source_type": row.get("source_type", ""),
                    "start_url": start_url,
                    "source_domain": source_domain(start_url),
                    "year": row.get("year", ""),
                    "document_type": row.get("document_type", ""),
                    "discovery_query": row.get("discovery_query", ""),
                    "discovery_title": row.get("discovery_title", ""),
                    "discovery_rank": row.get("discovery_rank", ""),
                }
            )
    return rows


def official_site_unique_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get("school_name", "")), str(row.get("start_url", "")))
        item = grouped.setdefault(
            key,
            {
                "school_name": key[0],
                "start_url": key[1],
                "source_domain": row.get("source_domain", ""),
                "seed_files": set(),
                "source_types": set(),
                "years": set(),
                "document_types": set(),
                "discovery_queries": set(),
                "discovery_titles": set(),
                "seed_row_count": 0,
            },
        )
        item["seed_files"].add(str(row.get("seed_file", "")))
        item["source_types"].add(str(row.get("source_type", "")))
        item["years"].add(str(row.get("year", "")))
        item["document_types"].add(str(row.get("document_type", "")))
        item["discovery_queries"].add(str(row.get("discovery_query", "")))
        item["discovery_titles"].add(str(row.get("discovery_title", "")))
        item["seed_row_count"] += 1
    return [
        {
            "school_name": item["school_name"],
            "start_url": item["start_url"],
            "source_domain": item["source_domain"],
            "seed_row_count": item["seed_row_count"],
            "seed_file_count": len({value for value in item["seed_files"] if value}),
            "source_types": ";".join(sorted(value for value in item["source_types"] if value)),
            "years": ";".join(sorted(value for value in item["years"] if value)),
            "document_types": ";".join(sorted(value for value in item["document_types"] if value)),
            "discovery_queries": ";".join(sorted(value for value in item["discovery_queries"] if value)),
            "discovery_titles": ";".join(sorted(value for value in item["discovery_titles"] if value)),
        }
        for item in sorted(grouped.values(), key=lambda value: (value["school_name"], value["start_url"]))
    ]


def rysxai_profession_summary(seed_dir: Path) -> list[dict[str, Any]]:
    path = seed_dir / "rysxai_professions.full.csv"
    if not path.exists():
        return []
    grouped: Counter[tuple[str, str, str, str]] = Counter()
    for row in read_csv(path):
        grouped[
            (
                row.get("level", ""),
                row.get("category", ""),
                row.get("subject", ""),
                row.get("is_hot", ""),
            )
        ] += 1
    return [
        {
            "level": level,
            "category": category,
            "subject": subject,
            "is_hot": is_hot,
            "profession_count": count,
        }
        for (level, category, subject, is_hot), count in sorted(grouped.items())
    ]


def rysxai_university_summary(seed_dir: Path) -> list[dict[str, Any]]:
    path = seed_dir / "rysxai_universities.csv"
    if not path.exists():
        return []
    grouped: Counter[tuple[str, str, str, str]] = Counter()
    tag_counts: Counter[str] = Counter()
    for row in read_csv(path):
        grouped[
            (
                row.get("province", ""),
                row.get("type", ""),
                row.get("property", ""),
                row.get("level", ""),
            )
        ] += 1
        try:
            tags = json.loads(row.get("tags", "[]") or "[]")
        except json.JSONDecodeError:
            tags = []
        for tag in tags:
            tag_counts[str(tag)] += 1
    rows = [
        {
            "province": province,
            "type": school_type,
            "property": property_value,
            "level": level,
            "university_count": count,
            "summary_kind": "province_type_property_level",
        }
        for (province, school_type, property_value, level), count in sorted(grouped.items())
    ]
    rows.extend(
        {
            "province": "",
            "type": tag,
            "property": "",
            "level": "",
            "university_count": count,
            "summary_kind": "tag",
        }
        for tag, count in sorted(tag_counts.items())
    )
    return rows


def policy_source_rows(seed_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, family in [
        ("policy_document_sources.csv", "policy_document_source_seed"),
        ("policy_evidence_sources.csv", "policy_evidence_source_seed"),
    ]:
        path = seed_dir / name
        if not path.exists():
            continue
        for row in read_csv(path):
            item = dict(row)
            item["seed_file"] = _path_key(path)
            item["seed_family"] = family
            rows.append(item)
    return rows


def policy_source_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: Counter[tuple[str, str, str, str]] = Counter()
    for row in rows:
        grouped[
            (
                str(row.get("seed_family", "")),
                str(row.get("source_type", "")),
                str(row.get("source_level", "")),
                str(row.get("source_year", "")),
            )
        ] += 1
    return [
        {
            "seed_family": family,
            "source_type": source_type,
            "source_level": source_level,
            "source_year": source_year,
            "source_count": count,
        }
        for (family, source_type, source_level, source_year), count in sorted(grouped.items())
    ]


def build_report(
    report_dir: Path,
    file_rows: list[dict[str, Any]],
    official_rows: list[dict[str, Any]],
    official_unique_rows: list[dict[str, Any]],
    policy_rows: list[dict[str, Any]],
    generated_at: str,
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "reference_seed_inventory_2026.md"
    family_counts = Counter(str(row["seed_family"]) for row in file_rows)
    official_year_counts = Counter(str(row.get("year", "")) for row in official_rows)
    lines = [
        "# Reference Seed Inventory",
        "",
        f"- Built at: {generated_at}",
        f"- Seed files: {len(file_rows)}",
        f"- Official-site seed rows: {len(official_rows)}",
        f"- Unique official-site source URLs: {len(official_unique_rows)}",
        f"- Policy source rows: {len(policy_rows)}",
        "",
        "## Seed Families",
        "",
        "| seed_family | files |",
        "|---|---:|",
    ]
    for family, count in sorted(family_counts.items()):
        lines.append(f"| {family} | {count} |")
    lines.extend(
        [
            "",
            "## Official-Site Seed Years",
            "",
            "| year | seed_rows |",
            "|---|---:|",
        ]
    )
    for year, count in sorted(official_year_counts.items()):
        lines.append(f"| {year} | {count} |")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `data/processed/reference_seed_inventory/reference_seed_file_manifest_2026.csv`",
            "- `data/processed/reference_seed_inventory/reference_seed_official_site_sources_2026.csv`",
            "- `data/processed/reference_seed_inventory/reference_seed_official_site_unique_sources_2026.csv`",
            "- `data/processed/reference_seed_inventory/reference_seed_rysxai_profession_summary_2026.csv`",
            "- `data/processed/reference_seed_inventory/reference_seed_rysxai_university_summary_2026.csv`",
            "- `data/processed/reference_seed_inventory/reference_seed_policy_sources_2026.csv`",
            "- `data/processed/reference_seed_inventory/reference_seed_policy_source_summary_2026.csv`",
            "",
            "## Notes",
            "",
            "- This package preserves all `data/seeds` files and adds normalized inventories for reproducible crawling.",
            "- Official-site seed rows are source URLs and metadata only; person-level extracted records are not included here.",
            "- RYSXAI profession and university seeds are third-party entity dimensions used for joins and should not be treated as official Ministry catalog truth.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def build_reference_seed_inventory(
    *,
    seed_dir: Path = DEFAULT_SEED_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    generated_at: str | None = None,
) -> dict[str, Any]:
    seed_dir = Path(seed_dir)
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    file_rows = build_file_manifest(seed_dir)
    official_rows = official_site_seed_rows(seed_dir)
    unique_official_rows = official_site_unique_rows(official_rows)
    profession_summary_rows = rysxai_profession_summary(seed_dir)
    university_summary_rows = rysxai_university_summary(seed_dir)
    policy_rows = policy_source_rows(seed_dir)
    policy_summary_rows = policy_source_summary(policy_rows)

    write_csv(
        output_dir / "reference_seed_file_manifest_2026.csv",
        file_rows,
        ["file", "file_name", "seed_family", "suffix", "bytes", "sha256", "row_count", "fields"],
    )
    write_csv(
        output_dir / "reference_seed_official_site_sources_2026.csv",
        official_rows,
        [
            "seed_file",
            "seed_family",
            "school_name",
            "source_type",
            "start_url",
            "source_domain",
            "year",
            "document_type",
            "discovery_query",
            "discovery_title",
            "discovery_rank",
        ],
    )
    write_csv(
        output_dir / "reference_seed_official_site_unique_sources_2026.csv",
        unique_official_rows,
        [
            "school_name",
            "start_url",
            "source_domain",
            "seed_row_count",
            "seed_file_count",
            "source_types",
            "years",
            "document_types",
            "discovery_queries",
            "discovery_titles",
        ],
    )
    write_csv(
        output_dir / "reference_seed_rysxai_profession_summary_2026.csv",
        profession_summary_rows,
        ["level", "category", "subject", "is_hot", "profession_count"],
    )
    write_csv(
        output_dir / "reference_seed_rysxai_university_summary_2026.csv",
        university_summary_rows,
        ["province", "type", "property", "level", "university_count", "summary_kind"],
    )
    write_csv(
        output_dir / "reference_seed_policy_sources_2026.csv",
        policy_rows,
        [
            "seed_file",
            "seed_family",
            "source_id",
            "title",
            "url",
            "source_domain",
            "source_level",
            "source_type",
            "issuing_org",
            "published_date",
            "source_year",
            "notes",
        ],
    )
    write_csv(
        output_dir / "reference_seed_policy_source_summary_2026.csv",
        policy_summary_rows,
        ["seed_family", "source_type", "source_level", "source_year", "source_count"],
    )
    report_path = build_report(
        report_dir,
        file_rows,
        official_rows,
        unique_official_rows,
        policy_rows,
        generated_at,
    )

    output_paths = sorted(path for path in output_dir.iterdir() if path.is_file())
    manifest = {
        "generated_at": generated_at,
        "dataset": "reference_seed_inventory",
        "status": "all_seed_files_plus_normalized_reference_indexes",
        "seed_dir": _path_key(seed_dir),
        "row_counts": {
            "seed_files": len(file_rows),
            "official_site_seed_rows": len(official_rows),
            "official_site_unique_sources": len(unique_official_rows),
            "rysxai_profession_summary": len(profession_summary_rows),
            "rysxai_university_summary": len(university_summary_rows),
            "policy_sources": len(policy_rows),
            "policy_source_summary": len(policy_summary_rows),
        },
        "report": _path_key(report_path),
        "checksums": {_path_key(path): file_info(path) for path in output_paths},
    }
    manifest_path = output_dir / "reference_seed_inventory_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build reference seed inventory files.")
    parser.add_argument("--seed-dir", type=Path, default=DEFAULT_SEED_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_reference_seed_inventory(
        seed_dir=args.seed_dir,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        generated_at=args.generated_at,
    )
    print(
        json.dumps(
            {
                "dataset": manifest["dataset"],
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
