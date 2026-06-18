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
DEFAULT_INPUT_DIR = ROOT / "data/processed/policy_documents"
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/emerging_major_candidate_details"
DEFAULT_STEM = "emerging_major_seed_20260612_v5"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _path_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _join(values: Any) -> str:
    return ";".join(sorted({str(value) for value in values if str(value)}))


def _candidate_distribution_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: Counter[tuple[str, str, str, str, str, str]] = Counter()
    for row in rows:
        grouped[
            (
                str(row.get("event_year", "")),
                str(row.get("event_type", "")),
                str(row.get("candidate_status", "")),
                str(row.get("major_level", "")),
                str(row.get("source_level", "")),
                str(row.get("parsed_from", "")),
            )
        ] += 1
    return [
        {
            "event_year": event_year,
            "event_type": event_type,
            "candidate_status": candidate_status,
            "major_level": major_level,
            "source_level": source_level,
            "parsed_from": parsed_from,
            "candidate_count": count,
        }
        for (
            event_year,
            event_type,
            candidate_status,
            major_level,
            source_level,
            parsed_from,
        ), count in sorted(grouped.items())
    ]


def _source_document_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (str(row.get("source_title", "")), str(row.get("source_url", "")))
        item = grouped.setdefault(
            key,
            {
                "source_title": key[0],
                "source_url": key[1],
                "source_levels": set(),
                "event_years": set(),
                "event_types": set(),
                "parsed_from_values": set(),
                "attachment_urls": set(),
                "raw_paths": set(),
                "candidate_statuses": set(),
                "candidate_count": 0,
                "unique_major_codes": set(),
                "unique_major_names": set(),
            },
        )
        item["candidate_count"] += 1
        item["source_levels"].add(str(row.get("source_level", "")))
        item["event_years"].add(str(row.get("event_year", "")))
        item["event_types"].add(str(row.get("event_type", "")))
        item["parsed_from_values"].add(str(row.get("parsed_from", "")))
        item["attachment_urls"].add(str(row.get("attachment_url", "")))
        item["raw_paths"].add(str(row.get("raw_path", "")))
        item["candidate_statuses"].add(str(row.get("candidate_status", "")))
        item["unique_major_codes"].add(str(row.get("major_code", "")))
        item["unique_major_names"].add(str(row.get("major_name", "")))
    output: list[dict[str, Any]] = []
    for item in grouped.values():
        output.append(
            {
                "source_title": item["source_title"],
                "source_url": item["source_url"],
                "source_levels": _join(item["source_levels"]),
                "event_years": _join(item["event_years"]),
                "event_types": _join(item["event_types"]),
                "parsed_from_values": _join(item["parsed_from_values"]),
                "candidate_statuses": _join(item["candidate_statuses"]),
                "candidate_count": item["candidate_count"],
                "unique_major_code_count": len({value for value in item["unique_major_codes"] if value}),
                "unique_major_name_count": len({value for value in item["unique_major_names"] if value}),
                "attachment_count": len({value for value in item["attachment_urls"] if value}),
                "raw_path_count": len({value for value in item["raw_paths"] if value}),
                "attachment_urls": _join(item["attachment_urls"]),
            }
        )
    return sorted(output, key=lambda row: (row["event_years"], row["source_title"]))


def _warning_summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: Counter[tuple[int, str]] = Counter()
    for row in rows:
        warnings = row.get("warnings") or []
        if not warnings:
            grouped[(0, "")] += 1
        else:
            for warning in warnings:
                grouped[(len(warnings), str(warning))] += 1
    return [
        {"warning_count_per_row": warning_count, "warning": warning, "row_count": count}
        for (warning_count, warning), count in sorted(grouped.items())
    ]


def build_emerging_major_candidate_details(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    stem: str = DEFAULT_STEM,
    generated_at: str | None = None,
) -> dict[str, Any]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    candidates_jsonl = input_dir / f"emerging_major_candidates_{stem}.jsonl"
    candidates_csv = input_dir / f"emerging_major_candidates_{stem}.csv"
    unique_csv = input_dir / f"emerging_major_unique_majors_{stem}.csv"
    coverage_csv = input_dir / f"emerging_major_coverage_{stem}.csv"
    events_csv = input_dir / "undergraduate_major_official_events_20260612_v5.csv"
    events_summary_csv = input_dir / "undergraduate_major_official_event_summary_20260612_v5.csv"
    rejected_csv = input_dir / "undergraduate_major_official_events_rejected_20260612_v5.csv"
    events_manifest_json = input_dir / "undergraduate_major_official_events_manifest_20260612_v5.json"

    rows = read_jsonl(candidates_jsonl)
    shutil.copyfile(candidates_jsonl, output_dir / "emerging_major_candidates_2026.jsonl")
    shutil.copyfile(candidates_csv, output_dir / "emerging_major_candidates_2026.csv")
    shutil.copyfile(unique_csv, output_dir / "emerging_major_unique_majors_2026.csv")
    shutil.copyfile(coverage_csv, output_dir / "emerging_major_coverage_2026.csv")

    distribution_rows = _candidate_distribution_rows(rows)
    source_rows = _source_document_rows(rows)
    warning_rows = _warning_summary_rows(rows)
    write_csv(
        output_dir / "emerging_major_candidate_distribution_2026.csv",
        distribution_rows,
        [
            "event_year",
            "event_type",
            "candidate_status",
            "major_level",
            "source_level",
            "parsed_from",
            "candidate_count",
        ],
    )
    write_csv(
        output_dir / "emerging_major_source_document_summary_2026.csv",
        source_rows,
        [
            "source_title",
            "source_url",
            "source_levels",
            "event_years",
            "event_types",
            "parsed_from_values",
            "candidate_statuses",
            "candidate_count",
            "unique_major_code_count",
            "unique_major_name_count",
            "attachment_count",
            "raw_path_count",
            "attachment_urls",
        ],
    )
    write_csv(
        output_dir / "emerging_major_warning_summary_2026.csv",
        warning_rows,
        ["warning_count_per_row", "warning", "row_count"],
    )

    optional_inputs = [
        events_csv,
        events_summary_csv,
        rejected_csv,
        events_manifest_json,
    ]
    for path in optional_inputs:
        if path.exists():
            shutil.copyfile(path, output_dir / path.name)

    output_paths = sorted(path for path in output_dir.iterdir() if path.is_file())
    event_type_counts = Counter(str(row.get("event_type", "")) for row in rows)
    event_year_counts = Counter(str(row.get("event_year", "")) for row in rows)
    status_counts = Counter(str(row.get("candidate_status", "")) for row in rows)
    parsed_from_counts = Counter(str(row.get("parsed_from", "")) for row in rows)
    manifest = {
        "generated_at": generated_at,
        "dataset": "emerging_major_candidate_details",
        "status": "official_policy_candidate_jsonl_and_summaries",
        "source_schema_version": rows[0].get("schema_version", "") if rows else "",
        "row_counts": {
            "candidate_jsonl": len(rows),
            "candidate_csv": len(read_csv(candidates_csv)),
            "unique_majors": len(read_csv(unique_csv)),
            "coverage": len(read_csv(coverage_csv)),
            "candidate_distribution": len(distribution_rows),
            "source_document_summary": len(source_rows),
            "warning_summary": len(warning_rows),
            "official_events": len(read_csv(events_csv)) if events_csv.exists() else 0,
            "official_event_summary": len(read_csv(events_summary_csv)) if events_summary_csv.exists() else 0,
            "official_events_rejected": len(read_csv(rejected_csv)) if rejected_csv.exists() else 0,
        },
        "distributions": {
            "event_type": dict(sorted(event_type_counts.items())),
            "event_year": dict(sorted(event_year_counts.items())),
            "candidate_status": dict(sorted(status_counts.items())),
            "parsed_from": dict(sorted(parsed_from_counts.items())),
        },
        "usage_notes": [
            "JSONL preserves typed warning arrays and schema_version for programmatic use.",
            "Rows come from official Ministry policy/catalog/filing documents and contain no person-level data.",
            "Use undergraduate_major_official_events files for normalized event-level joins to risk-warning datasets.",
        ],
        "checksums": {_path_key(path): file_info(path) for path in output_paths},
    }
    manifest_path = output_dir / "emerging_major_candidate_details_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build detailed emerging-major candidate package files.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--stem", default=DEFAULT_STEM)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_emerging_major_candidate_details(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        stem=args.stem,
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
