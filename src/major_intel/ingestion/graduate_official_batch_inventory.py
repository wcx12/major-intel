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
DEFAULT_INPUT_ROOT = ROOT / "data/processed"
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/graduate_official_batch_inventory"
DEFAULT_REPORT_DIR = ROOT / "reports/graduate_official_batch_inventory"
DEFAULT_PATTERNS = (
    "graduate_outcomes_official_site*",
    "official_site_recommendation_websearch*",
)

DIRECT_PERSON_FIELDS = {"person_name", "student_id"}
MASKED_PERSON_FIELDS = {"person_name_masked", "student_id_masked"}
PERSON_CONTEXT_FIELDS = {"ranking", "remarks"}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def file_info(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            total += len(chunk)
            digest.update(chunk)
    return {"bytes": total, "sha256": digest.hexdigest()}


def count_rows(path: Path, *, has_header: bool) -> int:
    lines = 0
    last_byte = b""
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            lines += chunk.count(b"\n")
            if chunk:
                last_byte = chunk[-1:]
    if path.stat().st_size and last_byte != b"\n":
        lines += 1
    if has_header:
        return max(0, lines - 1)
    return lines


def csv_fields(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.reader(handle)
            return next(reader, [])
    except OSError:
        return []


def jsonl_fields(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                value = json.loads(line)
                if isinstance(value, dict):
                    return list(value.keys())
                return []
    except (OSError, json.JSONDecodeError):
        return []
    return []


def read_documents(path: Path, batch_dir: str) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                row = {
                    "schema_version": "graduate_outcome_document_parse_error/v1",
                    "parse_status": "json_decode_error",
                    "record_count": 0,
                    "source_url": "",
                    "title": "",
                    "raw_path": "",
                    "year": "",
                    "document_type": "",
                    "school_name": "",
                    "error_line_number": line_number,
                }
            item = dict(row)
            item["batch_dir"] = batch_dir
            item["document_inventory_id"] = "graduate_doc:" + hashlib.sha256(
                f"{batch_dir}|{item.get('source_url','')}|{item.get('raw_path','')}".encode("utf-8")
            ).hexdigest()[:24]
            item["source_domain"] = urlparse(str(item.get("source_url", ""))).netloc
            item["matched_keywords_json"] = json.dumps(item.get("matched_keywords", []), ensure_ascii=False)
            documents.append(item)
    return documents


def _path_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _join(values: Any) -> str:
    return ";".join(sorted({str(value) for value in values if str(value)}))


def safe_level(file_name: str, fields: set[str]) -> str:
    if fields & DIRECT_PERSON_FIELDS:
        return "inventory_only_direct_person_fields_present"
    if fields & MASKED_PERSON_FIELDS:
        return "inventory_only_masked_person_fields_present"
    if file_name == "documents.jsonl":
        return "publishable_document_metadata_source"
    if file_name.endswith("summary.csv") or file_name.endswith("_summary.csv"):
        return "publishable_aggregate_source"
    return "inventory_only_or_log"


def classify_file(path: Path, batch_dir: str) -> dict[str, Any]:
    suffix = path.suffix.lower()
    row_count = ""
    fields: list[str] = []
    if suffix == ".csv":
        fields = csv_fields(path)
        row_count = count_rows(path, has_header=True)
    elif suffix == ".jsonl":
        fields = jsonl_fields(path)
        row_count = count_rows(path, has_header=False)
    info = file_info(path)
    field_set = set(fields)
    return {
        "batch_dir": batch_dir,
        "file": _path_key(path),
        "file_name": path.name,
        "suffix": suffix,
        "bytes": info["bytes"],
        "sha256": info["sha256"],
        "row_count": row_count,
        "fields": ";".join(fields),
        "contains_direct_person_fields": "true" if field_set & DIRECT_PERSON_FIELDS else "false",
        "contains_masked_person_fields": "true" if field_set & MASKED_PERSON_FIELDS else "false",
        "contains_person_context_fields": "true" if field_set & PERSON_CONTEXT_FIELDS else "false",
        "publication_level": safe_level(path.name, field_set),
    }


def batch_directory_rows(
    batch_dirs: list[Path],
    file_rows: list[dict[str, Any]],
    documents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    files_by_batch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    docs_by_batch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in file_rows:
        files_by_batch[str(row["batch_dir"])].append(row)
    for row in documents:
        docs_by_batch[str(row["batch_dir"])].append(row)

    output: list[dict[str, Any]] = []
    for batch_path in batch_dirs:
        batch = batch_path.name
        files = files_by_batch.get(batch, [])
        docs = docs_by_batch.get(batch, [])
        rows_by_name = defaultdict(int)
        for row in files:
            value = row.get("row_count")
            if isinstance(value, int):
                rows_by_name[str(row["file_name"])] += value
        output.append(
            {
                "batch_dir": batch,
                "file_count": len(files),
                "total_bytes": sum(int(row["bytes"]) for row in files),
                "file_names": _join(row["file_name"] for row in files),
                "document_count": len(docs),
                "document_school_count": len({str(row.get("school_name", "")) for row in docs if row.get("school_name")}),
                "source_years": _join(row.get("year", "") for row in docs),
                "document_types": _join(row.get("document_type", "") for row in docs),
                "parse_statuses": _join(row.get("parse_status", "") for row in docs),
                "document_record_count_sum": sum(int(row.get("record_count") or 0) for row in docs),
                "records_csv_rows": rows_by_name["records.csv"],
                "records_jsonl_rows": rows_by_name["records.jsonl"],
                "records_clean_rows": rows_by_name["records_clean.csv"] + rows_by_name["records_clean_curated.csv"],
                "records_public_rows": rows_by_name["records_public.csv"],
                "school_year_summary_rows": rows_by_name["school_year_summary.csv"]
                + rows_by_name["school_year_summary_curated.csv"],
                "direct_person_field_file_count": sum(
                    1 for row in files if row["contains_direct_person_fields"] == "true"
                ),
                "masked_person_field_file_count": sum(
                    1 for row in files if row["contains_masked_person_fields"] == "true"
                ),
            }
        )
    return sorted(output, key=lambda row: row["batch_dir"])


def document_summary_rows(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in documents:
        key = (
            str(row.get("year", "")),
            str(row.get("document_type", "")),
            str(row.get("parse_status", "")),
        )
        item = grouped.setdefault(
            key,
            {
                "year": key[0],
                "document_type": key[1],
                "parse_status": key[2],
                "document_count": 0,
                "record_count_sum": 0,
                "schools": set(),
                "batches": set(),
                "domains": set(),
            },
        )
        item["document_count"] += 1
        item["record_count_sum"] += int(row.get("record_count") or 0)
        item["schools"].add(str(row.get("school_name", "")))
        item["batches"].add(str(row.get("batch_dir", "")))
        item["domains"].add(str(row.get("source_domain", "")))
    return [
        {
            "year": item["year"],
            "document_type": item["document_type"],
            "parse_status": item["parse_status"],
            "document_count": item["document_count"],
            "record_count_sum": item["record_count_sum"],
            "school_count": len({value for value in item["schools"] if value}),
            "batch_count": len({value for value in item["batches"] if value}),
            "source_domain_count": len({value for value in item["domains"] if value}),
        }
        for item in sorted(grouped.values(), key=lambda row: (row["year"], row["document_type"], row["parse_status"]))
    ]


def privacy_summary_rows(file_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: Counter[tuple[str, str, str, str]] = Counter()
    for row in file_rows:
        grouped[
            (
                str(row.get("file_name", "")),
                str(row.get("contains_direct_person_fields", "")),
                str(row.get("contains_masked_person_fields", "")),
                str(row.get("publication_level", "")),
            )
        ] += 1
    return [
        {
            "file_name": file_name,
            "contains_direct_person_fields": direct,
            "contains_masked_person_fields": masked,
            "publication_level": level,
            "file_count": count,
        }
        for (file_name, direct, masked, level), count in sorted(grouped.items())
    ]


def build_report(
    report_dir: Path,
    directory_rows: list[dict[str, Any]],
    file_rows: list[dict[str, Any]],
    document_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    privacy_rows: list[dict[str, Any]],
    generated_at: str,
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "graduate_official_batch_inventory_2026.md"
    publication_counts = Counter(str(row["publication_level"]) for row in file_rows)
    years = sorted({str(row.get("year", "")) for row in document_rows if row.get("year")})
    lines = [
        "# Graduate Official Batch Inventory",
        "",
        f"- Built at: {generated_at}",
        f"- Batch directories scanned: {len(directory_rows)}",
        f"- Files inventoried: {len(file_rows)}",
        f"- Document metadata rows: {len(document_rows)}",
        f"- Source years: {', '.join(years)}",
        f"- Publication-level file counts: {dict(sorted(publication_counts.items()))}",
        "",
        "## Outputs",
        "",
        "- `data/processed/graduate_official_batch_inventory/graduate_official_batch_directories_2026.csv`",
        "- `data/processed/graduate_official_batch_inventory/graduate_official_batch_files_2026.csv`",
        "- `data/processed/graduate_official_batch_inventory/graduate_official_batch_documents_2026.csv`",
        "- `data/processed/graduate_official_batch_inventory/graduate_official_batch_document_summary_2026.csv`",
        "- `data/processed/graduate_official_batch_inventory/graduate_official_batch_privacy_summary_2026.csv`",
        "",
        "## Largest Batches",
        "",
        "| batch_dir | files | bytes | documents | public_rows | clean_rows |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(directory_rows, key=lambda item: int(item["total_bytes"]), reverse=True)[:20]:
        lines.append(
            "| {batch_dir} | {file_count} | {total_bytes} | {document_count} | {records_public_rows} | {records_clean_rows} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Document Summary",
            "",
            "| year | document_type | parse_status | documents | records | schools | batches |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in summary_rows:
        lines.append(
            "| {year} | {document_type} | {parse_status} | {document_count} | {record_count_sum} | {school_count} | {batch_count} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Privacy Handling",
            "",
            "- Person-level source files are not copied into this package.",
            "- The package includes file-level hashes and row counts so those sources remain auditable without redistributing direct identifiers.",
            "- Public masked graduate-outcome records are delivered separately in the graduate outcome and CHSI public-source packages.",
            "",
            "| file_name | direct_person_fields | masked_person_fields | publication_level | file_count |",
            "|---|---|---|---|---:|",
        ]
    )
    for row in privacy_rows:
        lines.append(
            "| {file_name} | {contains_direct_person_fields} | {contains_masked_person_fields} | {publication_level} | {file_count} |".format(
                **row
            )
        )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def resolve_batch_dirs(input_root: Path, patterns: list[str] | tuple[str, ...]) -> list[Path]:
    found: dict[str, Path] = {}
    for pattern in patterns:
        for path in input_root.glob(pattern):
            if path.is_dir():
                found[path.resolve().as_posix()] = path
    return sorted(found.values(), key=lambda path: path.name)


def build_graduate_official_batch_inventory(
    *,
    input_root: Path = DEFAULT_INPUT_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    pattern: str | None = None,
    patterns: list[str] | tuple[str, ...] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    input_root = Path(input_root)
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()
    scan_patterns: list[str]
    if patterns is not None:
        scan_patterns = list(patterns)
    elif pattern is not None:
        scan_patterns = [pattern]
    else:
        scan_patterns = list(DEFAULT_PATTERNS)

    batch_dirs = resolve_batch_dirs(input_root, scan_patterns)
    file_rows: list[dict[str, Any]] = []
    document_rows: list[dict[str, Any]] = []
    for batch_path in batch_dirs:
        batch = batch_path.name
        for path in sorted(item for item in batch_path.rglob("*") if item.is_file()):
            file_rows.append(classify_file(path, batch))
            if path.name == "documents.jsonl":
                document_rows.extend(read_documents(path, batch))

    directory_rows = batch_directory_rows(batch_dirs, file_rows, document_rows)
    summary_rows = document_summary_rows(document_rows)
    privacy_rows = privacy_summary_rows(file_rows)

    write_csv(
        output_dir / "graduate_official_batch_directories_2026.csv",
        directory_rows,
        [
            "batch_dir",
            "file_count",
            "total_bytes",
            "file_names",
            "document_count",
            "document_school_count",
            "source_years",
            "document_types",
            "parse_statuses",
            "document_record_count_sum",
            "records_csv_rows",
            "records_jsonl_rows",
            "records_clean_rows",
            "records_public_rows",
            "school_year_summary_rows",
            "direct_person_field_file_count",
            "masked_person_field_file_count",
        ],
    )
    write_csv(
        output_dir / "graduate_official_batch_files_2026.csv",
        file_rows,
        [
            "batch_dir",
            "file",
            "file_name",
            "suffix",
            "bytes",
            "sha256",
            "row_count",
            "fields",
            "contains_direct_person_fields",
            "contains_masked_person_fields",
            "contains_person_context_fields",
            "publication_level",
        ],
    )
    write_csv(
        output_dir / "graduate_official_batch_documents_2026.csv",
        document_rows,
        [
            "document_inventory_id",
            "batch_dir",
            "schema_version",
            "captured_at",
            "school_name",
            "source_type",
            "source_url",
            "source_domain",
            "start_url",
            "title",
            "year",
            "document_type",
            "matched_keywords_json",
            "content_type",
            "content_length",
            "content_hash",
            "raw_path",
            "parse_status",
            "record_count",
        ],
    )
    write_csv(
        output_dir / "graduate_official_batch_document_summary_2026.csv",
        summary_rows,
        [
            "year",
            "document_type",
            "parse_status",
            "document_count",
            "record_count_sum",
            "school_count",
            "batch_count",
            "source_domain_count",
        ],
    )
    write_csv(
        output_dir / "graduate_official_batch_privacy_summary_2026.csv",
        privacy_rows,
        [
            "file_name",
            "contains_direct_person_fields",
            "contains_masked_person_fields",
            "publication_level",
            "file_count",
        ],
    )
    report_path = build_report(
        report_dir,
        directory_rows,
        file_rows,
        document_rows,
        summary_rows,
        privacy_rows,
        generated_at,
    )

    output_paths = sorted(path for path in output_dir.iterdir() if path.is_file())
    manifest = {
        "generated_at": generated_at,
        "dataset": "graduate_official_batch_inventory",
        "status": "metadata_only_inventory_for_official_site_batch_outputs",
        "input_root": _path_key(input_root),
        "patterns": scan_patterns,
        "row_counts": {
            "batch_directories": len(directory_rows),
            "batch_files": len(file_rows),
            "batch_documents": len(document_rows),
            "document_summary": len(summary_rows),
            "privacy_summary": len(privacy_rows),
        },
        "privacy_policy": [
            "This package does not copy records.csv, records.jsonl, records_clean.csv, or records_public.csv from batch directories.",
            "File inventory reports hashes, byte sizes, row counts, and field names for auditability.",
            "Document metadata is retained because it describes public official pages and source provenance.",
        ],
        "report": _path_key(report_path),
        "checksums": {_path_key(path): file_info(path) for path in output_paths},
    }
    manifest_path = output_dir / "graduate_official_batch_inventory_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a metadata-only inventory of graduate official-site batches.")
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument(
        "--patterns",
        default=",".join(DEFAULT_PATTERNS),
        help="Comma-separated directory glob patterns under input-root.",
    )
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_graduate_official_batch_inventory(
        input_root=args.input_root,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        patterns=[value.strip() for value in args.patterns.split(",") if value.strip()],
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
