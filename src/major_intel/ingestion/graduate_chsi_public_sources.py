from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_DIR = ROOT / "data/processed/graduate_outcomes_chsi"
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/graduate_chsi_public_sources"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _path_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _csv_row_count(path: Path | None) -> int:
    if path is None or not path.exists() or not path.is_file():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def _jsonl_row_count(path: Path | None) -> int:
    if path is None or not path.exists() or not path.is_file():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _join(values: Any) -> str:
    return ";".join(sorted({str(value) for value in values if str(value)}))


def _school_index_inventory(input_dir: Path) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for path in sorted(input_dir.glob("chsi_schools_*.csv")):
        for row in read_csv(path):
            key = (
                row.get("chsi_school_name", ""),
                row.get("chsi_sch_id", ""),
                row.get("chsi_school_url", ""),
            )
            if any(key):
                grouped[key].add(_path_key(path))
    return [
        {
            "chsi_school_name": school_name,
            "chsi_sch_id": sch_id,
            "chsi_school_url": school_url,
            "source_file_count": len(source_files),
            "source_files": _join(source_files),
        }
        for (school_name, sch_id, school_url), source_files in sorted(grouped.items())
    ]


def _seed_inventory(input_dir: Path) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, str, str, str], set[str]] = defaultdict(set)
    for path in sorted(input_dir.glob("chsi_seeds_*.csv")):
        for row in read_csv(path):
            key = (
                row.get("school_name", ""),
                row.get("source_type", ""),
                row.get("start_url", ""),
                row.get("year", ""),
                row.get("document_type", ""),
                row.get("discovery_query", ""),
                row.get("discovery_title", ""),
            )
            if any(key):
                grouped[key].add(_path_key(path))
    return [
        {
            "school_name": school_name,
            "source_type": source_type,
            "start_url": start_url,
            "year": year,
            "document_type": document_type,
            "discovery_query": discovery_query,
            "discovery_title": discovery_title,
            "source_file_count": len(source_files),
            "source_files": _join(source_files),
        }
        for (
            school_name,
            source_type,
            start_url,
            year,
            document_type,
            discovery_query,
            discovery_title,
        ), source_files in sorted(grouped.items())
    ]


def _document_inventory(input_dir: Path) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, str, str], dict[str, Any]] = {}
    for path in sorted(input_dir.glob("crawl_*/documents.jsonl")):
        batch = path.parent.name
        for row in read_jsonl(path):
            key = (
                str(row.get("school_name", "")),
                str(row.get("source_url", "")),
                str(row.get("year", "")),
                str(row.get("document_type", "")),
                str(row.get("route", "")),
                str(row.get("title", "")),
            )
            item = grouped.setdefault(
                key,
                {
                    "school_name": key[0],
                    "source_url": key[1],
                    "year": key[2],
                    "document_type": key[3],
                    "route": key[4],
                    "title": key[5],
                    "source_type": str(row.get("source_type", "")),
                    "content_type": str(row.get("content_type", "")),
                    "content_length": str(row.get("content_length", "")),
                    "matched_keywords": str(row.get("matched_keywords", "")),
                    "first_captured_at": str(row.get("captured_at", "")),
                    "last_captured_at": str(row.get("captured_at", "")),
                    "source_batch_count": 0,
                    "source_batches": set(),
                },
            )
            captured_at = str(row.get("captured_at", ""))
            if captured_at:
                item["first_captured_at"] = min(str(item["first_captured_at"] or captured_at), captured_at)
                item["last_captured_at"] = max(str(item["last_captured_at"] or captured_at), captured_at)
            item["source_batches"].add(batch)
    rows: list[dict[str, Any]] = []
    for item in grouped.values():
        batches = item.pop("source_batches")
        item["source_batch_count"] = len(batches)
        item["source_batches"] = _join(batches)
        rows.append(item)
    return sorted(rows, key=lambda row: (row["school_name"], row["year"], row["source_url"]))


def _batch_summary(input_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(input_dir.glob("crawl_*")):
        if not path.is_dir():
            continue
        files = {item.name: item for item in path.iterdir() if item.is_file()}
        rows.append(
            {
                "crawl_batch": path.name,
                "documents_jsonl_rows": _jsonl_row_count(files.get("documents.jsonl")),
                "records_jsonl_rows": _jsonl_row_count(files.get("records.jsonl")),
                "records_csv_rows": _csv_row_count(files.get("records.csv")),
                "records_clean_csv_rows": _csv_row_count(files.get("records_clean.csv")),
                "school_year_summary_rows": _csv_row_count(files.get("school_year_summary.csv")),
                "documents_jsonl_bytes": files.get("documents.jsonl").stat().st_size
                if files.get("documents.jsonl")
                else 0,
                "records_sensitive_files_present": str(
                    any(name in files for name in ["records.jsonl", "records.csv", "records_clean.csv"])
                ).lower(),
                "records_sensitive_files_packaged": "false",
                "exclusion_reason": "batch record files include unmasked person-level fields; use chsi_public_records_2026.csv",
            }
        )
    return rows


def _source_file_manifest(input_dir: Path, output_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(input_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = _path_key(path)
        name = path.name
        contains_unmasked = name in {
            "master_records_clean.csv",
            "records.jsonl",
            "records.csv",
            "records_clean.csv",
        } or name.startswith("master_records_clean")
        included = (
            name == "master_records_public.csv"
            or name in {"school_year_summary.csv", "master_school_year_summary.csv"}
            or name.startswith("chsi_schools_")
            or name.startswith("chsi_seeds_")
            or name == "documents.jsonl"
        ) and not contains_unmasked
        rows.append(
            {
                "source_file": rel,
                "file_name": name,
                "file_suffix": path.suffix.lower(),
                "bytes": path.stat().st_size,
                "sha256": file_info(path)["sha256"],
                "contains_unmasked_person_level_fields": str(contains_unmasked).lower(),
                "included_or_summarized_in_dataset": str(included).lower(),
                "packaging_note": (
                    "excluded_unmasked_person_level_file"
                    if contains_unmasked
                    else "included_or_summarized"
                    if included
                    else "auxiliary_or_superseded_intermediate"
                ),
            }
        )
    for path in sorted(output_dir.glob("*")):
        if path.is_file():
            rows.append(
                {
                    "source_file": _path_key(path),
                    "file_name": path.name,
                    "file_suffix": path.suffix.lower(),
                    "bytes": path.stat().st_size,
                    "sha256": file_info(path)["sha256"],
                    "contains_unmasked_person_level_fields": "false",
                    "included_or_summarized_in_dataset": "true",
                    "packaging_note": "derived_output",
                }
            )
    return rows


def build_graduate_chsi_public_sources(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    generated_at: str | None = None,
) -> dict[str, Any]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    public_records_source = input_dir / "master_records_public.csv"
    school_year_source = input_dir / "school_year_summary.csv"
    public_records_target = output_dir / "chsi_public_records_2026.csv"
    school_year_target = output_dir / "chsi_school_year_summary_2026.csv"
    shutil.copyfile(public_records_source, public_records_target)
    shutil.copyfile(school_year_source, school_year_target)

    school_index_rows = _school_index_inventory(input_dir)
    seed_rows = _seed_inventory(input_dir)
    document_rows = _document_inventory(input_dir)
    batch_rows = _batch_summary(input_dir)

    write_csv(
        output_dir / "chsi_school_index_inventory_2026.csv",
        school_index_rows,
        ["chsi_school_name", "chsi_sch_id", "chsi_school_url", "source_file_count", "source_files"],
    )
    write_csv(
        output_dir / "chsi_bulletin_seed_inventory_2026.csv",
        seed_rows,
        [
            "school_name",
            "source_type",
            "start_url",
            "year",
            "document_type",
            "discovery_query",
            "discovery_title",
            "source_file_count",
            "source_files",
        ],
    )
    write_csv(
        output_dir / "chsi_document_inventory_2026.csv",
        document_rows,
        [
            "school_name",
            "source_url",
            "year",
            "document_type",
            "route",
            "title",
            "source_type",
            "content_type",
            "content_length",
            "matched_keywords",
            "first_captured_at",
            "last_captured_at",
            "source_batch_count",
            "source_batches",
        ],
    )
    write_csv(
        output_dir / "chsi_crawl_batch_summary_2026.csv",
        batch_rows,
        [
            "crawl_batch",
            "documents_jsonl_rows",
            "records_jsonl_rows",
            "records_csv_rows",
            "records_clean_csv_rows",
            "school_year_summary_rows",
            "documents_jsonl_bytes",
            "records_sensitive_files_present",
            "records_sensitive_files_packaged",
            "exclusion_reason",
        ],
    )
    source_file_rows = _source_file_manifest(input_dir, output_dir)
    write_csv(
        output_dir / "chsi_source_file_manifest_2026.csv",
        source_file_rows,
        [
            "source_file",
            "file_name",
            "file_suffix",
            "bytes",
            "sha256",
            "contains_unmasked_person_level_fields",
            "included_or_summarized_in_dataset",
            "packaging_note",
        ],
    )

    public_rows = read_csv(public_records_target)
    school_year_rows = read_csv(school_year_target)
    route_counts = Counter(row.get("route", "") for row in public_rows)
    document_type_counts = Counter(row.get("document_type", "") for row in public_rows)
    year_counts = Counter(row.get("year", "") for row in public_rows)
    output_files = [
        public_records_target,
        school_year_target,
        output_dir / "chsi_school_index_inventory_2026.csv",
        output_dir / "chsi_bulletin_seed_inventory_2026.csv",
        output_dir / "chsi_document_inventory_2026.csv",
        output_dir / "chsi_crawl_batch_summary_2026.csv",
        output_dir / "chsi_source_file_manifest_2026.csv",
    ]
    manifest = {
        "generated_at": generated_at,
        "dataset": "graduate_chsi_public_sources",
        "status": "public_masked_chsi_subset_with_source_metadata",
        "source_dir": _path_key(input_dir),
        "row_counts": {
            "public_records": len(public_rows),
            "school_year_summary": len(school_year_rows),
            "school_index_inventory": len(school_index_rows),
            "bulletin_seed_inventory": len(seed_rows),
            "document_inventory": len(document_rows),
            "crawl_batch_summary": len(batch_rows),
            "source_file_manifest": len(source_file_rows),
        },
        "distributions": {
            "route": dict(sorted(route_counts.items())),
            "document_type": dict(sorted(document_type_counts.items())),
            "top_years": dict(year_counts.most_common(20)),
        },
        "privacy_and_packaging_notes": [
            "chsi_public_records_2026.csv keeps masked person and student identifiers only.",
            "Unmasked CHSI clean/master record files and per-batch record files are excluded.",
            "CHSI records are also integrated into data/cleaned/graduate_outcomes/master_records_public.csv with source_dataset=chsi_yanzhao.",
        ],
        "checksums": {_path_key(path): file_info(path) for path in output_files},
    }
    manifest_path = output_dir / "graduate_chsi_public_sources_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build CHSI public graduate outcome support tables.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_graduate_chsi_public_sources(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
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
