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
DEFAULT_LOG_DIR = ROOT / "data/logs/policy_documents"
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/emerging_major_source_attachments"
DEFAULT_REPORT_DIR = ROOT / "reports/emerging_major_source_attachments"
DEFAULT_STEM = "emerging_major_seed_20260612_v5"


DOCUMENT_FIELDS = [
    "schema_version",
    "doc_id",
    "source_id",
    "title",
    "url",
    "source_domain",
    "source_level",
    "source_type",
    "issuing_org",
    "published_date",
    "source_year",
    "captured_at",
    "raw_path",
    "content_sha256",
    "text_length",
    "attachment_count",
]

ATTACHMENT_FIELDS = [
    "schema_version",
    "parent_doc_id",
    "parent_source_id",
    "source_title",
    "source_url",
    "source_year",
    "source_level",
    "attachment_url",
    "attachment_title",
    "file_type",
    "raw_path",
    "parse_status",
    "row_count",
    "candidate_major_count",
    "warnings_json",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


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


def _join(values: Any) -> str:
    return ";".join(sorted({str(value) for value in values if str(value)}))


def _resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def normalize_attachment_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["warnings_json"] = json.dumps(item.pop("warnings", []), ensure_ascii=False)
        normalized.append(item)
    return normalized


def source_year_summary_rows(
    documents: list[dict[str, Any]], attachments: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for doc in documents:
        key = (str(doc.get("source_year", "")), str(doc.get("source_type", "")))
        item = grouped.setdefault(
            key,
            {
                "source_year": key[0],
                "source_type": key[1],
                "document_ids": set(),
                "source_urls": set(),
                "source_levels": set(),
                "document_attachment_count": 0,
                "attachment_count": 0,
                "ok_attachment_count": 0,
                "warning_attachment_count": 0,
                "parsed_row_count": 0,
                "candidate_major_count": 0,
                "file_types": set(),
            },
        )
        item["document_ids"].add(str(doc.get("doc_id", "")))
        item["source_urls"].add(str(doc.get("url", "")))
        item["source_levels"].add(str(doc.get("source_level", "")))
        item["document_attachment_count"] += int(doc.get("attachment_count") or 0)
    doc_type_by_id = {
        str(doc.get("doc_id", "")): str(doc.get("source_type", "")) for doc in documents
    }
    for attachment in attachments:
        key = (
            str(attachment.get("source_year", "")),
            doc_type_by_id.get(str(attachment.get("parent_doc_id", "")), ""),
        )
        item = grouped.setdefault(
            key,
            {
                "source_year": key[0],
                "source_type": key[1],
                "document_ids": set(),
                "source_urls": set(),
                "source_levels": set(),
                "document_attachment_count": 0,
                "attachment_count": 0,
                "ok_attachment_count": 0,
                "warning_attachment_count": 0,
                "parsed_row_count": 0,
                "candidate_major_count": 0,
                "file_types": set(),
            },
        )
        item["document_ids"].add(str(attachment.get("parent_doc_id", "")))
        item["source_urls"].add(str(attachment.get("source_url", "")))
        item["source_levels"].add(str(attachment.get("source_level", "")))
        item["attachment_count"] += 1
        item["ok_attachment_count"] += 1 if attachment.get("parse_status") == "ok" else 0
        item["warning_attachment_count"] += 1 if attachment.get("warnings") else 0
        item["parsed_row_count"] += int(attachment.get("row_count") or 0)
        item["candidate_major_count"] += int(attachment.get("candidate_major_count") or 0)
        item["file_types"].add(str(attachment.get("file_type", "")))
    rows: list[dict[str, Any]] = []
    for item in grouped.values():
        rows.append(
            {
                "source_year": item["source_year"],
                "source_type": item["source_type"],
                "document_count": len({value for value in item["document_ids"] if value}),
                "source_levels": _join(item["source_levels"]),
                "source_url_count": len({value for value in item["source_urls"] if value}),
                "document_attachment_count": item["document_attachment_count"],
                "attachment_count": item["attachment_count"],
                "ok_attachment_count": item["ok_attachment_count"],
                "warning_attachment_count": item["warning_attachment_count"],
                "parsed_row_count": item["parsed_row_count"],
                "candidate_major_count": item["candidate_major_count"],
                "file_types": _join(item["file_types"]),
                "source_urls": _join(item["source_urls"]),
            }
        )
    return sorted(rows, key=lambda row: (row["source_year"], row["source_type"]))


def attachment_status_rows(attachments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in attachments:
        key = (
            str(row.get("source_year", "")),
            str(row.get("file_type", "")),
            str(row.get("parse_status", "")),
        )
        item = grouped.setdefault(
            key,
            {
                "source_year": key[0],
                "file_type": key[1],
                "parse_status": key[2],
                "attachment_count": 0,
                "parsed_row_count": 0,
                "candidate_major_count": 0,
                "warning_count": 0,
                "parent_docs": set(),
            },
        )
        item["attachment_count"] += 1
        item["parsed_row_count"] += int(row.get("row_count") or 0)
        item["candidate_major_count"] += int(row.get("candidate_major_count") or 0)
        item["warning_count"] += len(row.get("warnings") or [])
        item["parent_docs"].add(str(row.get("parent_doc_id", "")))
    return [
        {
            "source_year": item["source_year"],
            "file_type": item["file_type"],
            "parse_status": item["parse_status"],
            "attachment_count": item["attachment_count"],
            "parsed_row_count": item["parsed_row_count"],
            "candidate_major_count": item["candidate_major_count"],
            "warning_count": item["warning_count"],
            "parent_doc_count": len({value for value in item["parent_docs"] if value}),
        }
        for item in sorted(grouped.values(), key=lambda row: (row["source_year"], row["file_type"], row["parse_status"]))
    ]


def raw_file_inventory_rows(
    documents: list[dict[str, Any]], attachments: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for role, records in [("source_document_page", documents), ("source_attachment", attachments)]:
        for record in records:
            raw_path = str(record.get("raw_path", ""))
            if not raw_path:
                continue
            key = (role, raw_path)
            if key in seen:
                continue
            seen.add(key)
            resolved = _resolve_repo_path(raw_path)
            exists = resolved.exists()
            info = file_info(resolved) if exists and resolved.is_file() else {"bytes": "", "sha256": ""}
            rows.append(
                {
                    "role": role,
                    "source_year": record.get("source_year", ""),
                    "source_title": record.get("title") or record.get("source_title", ""),
                    "source_url": record.get("url") or record.get("source_url", ""),
                    "attachment_url": record.get("attachment_url", ""),
                    "raw_path": raw_path,
                    "exists": "true" if exists else "false",
                    "bytes": info["bytes"],
                    "sha256": info["sha256"],
                }
            )
    return sorted(rows, key=lambda row: (row["role"], str(row["source_year"]), row["raw_path"]))


def build_report(
    report_dir: Path,
    documents: list[dict[str, Any]],
    attachments: list[dict[str, Any]],
    year_rows: list[dict[str, Any]],
    status_rows: list[dict[str, Any]],
    inventory_rows: list[dict[str, Any]],
    generated_at: str,
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "emerging_major_source_attachments_2026.md"
    source_years = sorted({str(row.get("source_year", "")) for row in documents if row.get("source_year")})
    file_type_counts = Counter(str(row.get("file_type", "")) for row in attachments)
    parse_counts = Counter(str(row.get("parse_status", "")) for row in attachments)
    lines = [
        "# Emerging Major Source Attachments",
        "",
        f"- Built at: {generated_at}",
        f"- Official source documents: {len(documents)}",
        f"- Official attachment records: {len(attachments)}",
        f"- Source years: {', '.join(source_years)}",
        f"- File types: {dict(sorted(file_type_counts.items()))}",
        f"- Parse statuses: {dict(sorted(parse_counts.items()))}",
        f"- Raw files found locally: {sum(1 for row in inventory_rows if row['exists'] == 'true')} of {len(inventory_rows)}",
        "",
        "## Outputs",
        "",
        "- `data/processed/emerging_major_source_attachments/emerging_major_source_documents_2026.csv`",
        "- `data/processed/emerging_major_source_attachments/emerging_major_source_attachments_2026.csv`",
        "- `data/processed/emerging_major_source_attachments/emerging_major_source_year_summary_2026.csv`",
        "- `data/processed/emerging_major_source_attachments/emerging_major_attachment_parse_summary_2026.csv`",
        "- `data/processed/emerging_major_source_attachments/emerging_major_source_raw_file_inventory_2026.csv`",
        "",
        "## Source-Year Coverage",
        "",
        "| source_year | source_type | documents | attachments | candidates | parsed_rows | file_types |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in year_rows:
        lines.append(
            "| {source_year} | {source_type} | {document_count} | {attachment_count} | {candidate_major_count} | {parsed_row_count} | {file_types} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Parse Status",
            "",
            "| source_year | file_type | status | attachments | candidates | warnings |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in status_rows:
        lines.append(
            "| {source_year} | {file_type} | {parse_status} | {attachment_count} | {candidate_major_count} | {warning_count} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This package is an official-source provenance index for the emerging-major candidate dataset.",
            "- It contains page and attachment metadata only; it does not contain person-level records.",
            "- The raw file inventory records local path, byte size, and SHA-256 when the file is present.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def build_emerging_major_source_attachments(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    log_dir: Path = DEFAULT_LOG_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    stem: str = DEFAULT_STEM,
    generated_at: str | None = None,
) -> dict[str, Any]:
    input_dir = Path(input_dir)
    log_dir = Path(log_dir)
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    documents_path = input_dir / f"documents_{stem}.jsonl"
    attachments_path = input_dir / f"attachments_{stem}.jsonl"
    crawl_manifest_path = log_dir / f"{stem}_manifest.json"
    failures_path = log_dir / f"{stem}_failures.jsonl"

    documents = read_jsonl(documents_path)
    attachments = read_jsonl(attachments_path)
    attachment_csv_rows = normalize_attachment_rows(attachments)
    year_rows = source_year_summary_rows(documents, attachments)
    status_rows = attachment_status_rows(attachments)
    inventory_rows = raw_file_inventory_rows(documents, attachments)

    write_jsonl(output_dir / "emerging_major_source_documents_2026.jsonl", documents)
    write_csv(output_dir / "emerging_major_source_documents_2026.csv", documents, DOCUMENT_FIELDS)
    write_jsonl(output_dir / "emerging_major_source_attachments_2026.jsonl", attachments)
    write_csv(output_dir / "emerging_major_source_attachments_2026.csv", attachment_csv_rows, ATTACHMENT_FIELDS)
    write_csv(
        output_dir / "emerging_major_source_year_summary_2026.csv",
        year_rows,
        [
            "source_year",
            "source_type",
            "document_count",
            "source_levels",
            "source_url_count",
            "document_attachment_count",
            "attachment_count",
            "ok_attachment_count",
            "warning_attachment_count",
            "parsed_row_count",
            "candidate_major_count",
            "file_types",
            "source_urls",
        ],
    )
    write_csv(
        output_dir / "emerging_major_attachment_parse_summary_2026.csv",
        status_rows,
        [
            "source_year",
            "file_type",
            "parse_status",
            "attachment_count",
            "parsed_row_count",
            "candidate_major_count",
            "warning_count",
            "parent_doc_count",
        ],
    )
    write_csv(
        output_dir / "emerging_major_source_raw_file_inventory_2026.csv",
        inventory_rows,
        [
            "role",
            "source_year",
            "source_title",
            "source_url",
            "attachment_url",
            "raw_path",
            "exists",
            "bytes",
            "sha256",
        ],
    )
    if crawl_manifest_path.exists():
        shutil.copyfile(crawl_manifest_path, output_dir / crawl_manifest_path.name)
    if failures_path.exists():
        shutil.copyfile(failures_path, output_dir / failures_path.name)

    report_path = build_report(report_dir, documents, attachments, year_rows, status_rows, inventory_rows, generated_at)

    output_paths = sorted(path for path in output_dir.iterdir() if path.is_file())
    document_type_counts = Counter(str(row.get("source_type", "")) for row in documents)
    parse_status_counts = Counter(str(row.get("parse_status", "")) for row in attachments)
    manifest = {
        "generated_at": generated_at,
        "dataset": "emerging_major_source_attachments",
        "status": "official_policy_source_page_and_attachment_provenance",
        "source_documents_file": _path_key(documents_path),
        "source_attachments_file": _path_key(attachments_path),
        "row_counts": {
            "source_documents": len(documents),
            "source_attachments": len(attachments),
            "source_year_summary": len(year_rows),
            "attachment_parse_summary": len(status_rows),
            "raw_file_inventory": len(inventory_rows),
            "local_raw_files_found": sum(1 for row in inventory_rows if row["exists"] == "true"),
        },
        "distributions": {
            "document_source_type": dict(sorted(document_type_counts.items())),
            "attachment_parse_status": dict(sorted(parse_status_counts.items())),
        },
        "usage_notes": [
            "Join attachment_url to emerging_major_candidate_details rows to trace candidate majors back to official attachments.",
            "Raw-path inventory includes hashes for local source files when present.",
            "Rows are Ministry/public policy provenance metadata and contain no person-level records.",
        ],
        "report": _path_key(report_path),
        "checksums": {_path_key(path): file_info(path) for path in output_paths},
    }
    manifest_path = output_dir / "emerging_major_source_attachments_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build emerging-major official source attachment tables.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--stem", default=DEFAULT_STEM)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_emerging_major_source_attachments(
        input_dir=args.input_dir,
        log_dir=args.log_dir,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
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
