from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCAN_ROOTS = (
    ROOT / "data/processed",
    ROOT / "data/cleaned",
    ROOT / "reports",
    ROOT / "docs/datasets",
)
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/processed_asset_inventory"
DEFAULT_REPORT_DIR = ROOT / "reports/processed_asset_inventory"
DEFAULT_OUTPUTS_DIR = ROOT / "outputs"
DEFAULT_HASH_MAX_BYTES = 20_000_000
DEFAULT_ROW_COUNT_MAX_BYTES = 50_000_000

DIRECT_PERSON_FIELDS = {
    "person_name",
    "student_id",
    "phone",
    "id_card",
    "identity_card",
    "candidate_name",
}
MASKED_PERSON_FIELDS = {"person_name_masked", "student_id_masked", "phone_masked"}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def file_info(path: Path, hash_max_bytes: int | None) -> dict[str, Any]:
    size = path.stat().st_size
    if hash_max_bytes is not None and size > hash_max_bytes:
        return {"bytes": size, "sha256": "", "sha256_status": "skipped_large_file"}
    digest = hashlib.sha256()
    total = 0
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                total += len(chunk)
                digest.update(chunk)
    except OSError:
        return {"bytes": size, "sha256": "", "sha256_status": "unreadable"}
    return {"bytes": total, "sha256": digest.hexdigest(), "sha256_status": "computed"}


def _path_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def inventory_file_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        parts = path.parts
        for marker in [("data", "processed"), ("data", "cleaned"), ("docs", "datasets")]:
            for index in range(len(parts) - 1):
                if parts[index] == marker[0] and parts[index + 1] == marker[1]:
                    return Path(*parts[index:]).as_posix()
        for index, part in enumerate(parts):
            if part == "reports":
                return Path(*parts[index:]).as_posix()
    return path.as_posix()


def package_key(zip_path: Path, outputs_dir: Path) -> str:
    try:
        return zip_path.relative_to(ROOT).as_posix()
    except ValueError:
        try:
            return zip_path.relative_to(outputs_dir.parent).as_posix()
        except ValueError:
            return zip_path.as_posix()


def collect_zip_memberships(outputs_dir: Path) -> dict[str, list[str]]:
    memberships: dict[str, list[str]] = defaultdict(list)
    for zip_path in sorted(outputs_dir.glob("*.zip")):
        try:
            with zipfile.ZipFile(zip_path) as archive:
                for name in archive.namelist():
                    memberships[name].append(package_key(zip_path, outputs_dir))
        except zipfile.BadZipFile:
            continue
    return memberships


def first_csv_fields(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.reader(handle)
            return next(reader, [])
    except (OSError, StopIteration):
        return []


def first_json_keys(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            return []
        value = json.loads(text)
        if isinstance(value, dict):
            return list(value.keys())
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return list(value[0].keys())
    except (OSError, json.JSONDecodeError):
        return []
    return []


def first_jsonl_keys(path: Path) -> list[str]:
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


def file_fields(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return first_csv_fields(path)
    if suffix == ".json":
        return first_json_keys(path)
    if suffix == ".jsonl":
        return first_jsonl_keys(path)
    return []


def count_lines(path: Path) -> int:
    lines = 0
    last_byte = b""
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                lines += chunk.count(b"\n")
                if chunk:
                    last_byte = chunk[-1:]
    except OSError:
        return -1
    if path.stat().st_size and last_byte != b"\n":
        lines += 1
    return lines


def row_count(path: Path, suffix: str, size: int, row_count_max_bytes: int | None) -> tuple[str, str]:
    if suffix not in {".csv", ".jsonl"}:
        return "", "not_applicable"
    if row_count_max_bytes is not None and size > row_count_max_bytes:
        return "", "skipped_large_file"
    lines = count_lines(path)
    if lines < 0:
        return "", "unreadable"
    if suffix == ".csv":
        return str(max(0, lines - 1)), "computed"
    return str(lines), "computed"


def root_name_from_key(file_key: str) -> str:
    parts = Path(file_key).parts
    if parts and parts[0] == "reports":
        return "reports"
    if len(parts) >= 2 and parts[0] in {"data", "docs"}:
        return f"{parts[0]}/{parts[1]}"
    return parts[0] if parts else ""


def asset_group_from_key(file_key: str) -> str:
    parts = Path(file_key).parts
    if parts and parts[0] == "reports":
        return parts[1] if len(parts) > 2 else "<reports_root>"
    if len(parts) >= 3 and parts[0] in {"data", "docs"}:
        return parts[2]
    return parts[0] if parts else ""


def publication_level(file_key: str, fields: set[str], package_names: list[str]) -> str:
    if fields & DIRECT_PERSON_FIELDS:
        return "metadata_only_direct_person_fields_present"
    if fields & MASKED_PERSON_FIELDS:
        return "metadata_only_masked_person_fields_present"
    if file_key.startswith("reports/volunteer_matching/"):
        return "metadata_only_non_crawl_eval_artifact"
    if package_names:
        return "packaged_content_available"
    return "metadata_only_unpackaged_intermediate_or_legacy"


def inventory_rows(
    scan_roots: list[Path],
    memberships: dict[str, list[str]],
    *,
    hash_max_bytes: int | None,
    row_count_max_bytes: int | None,
    exclude_dirs: list[Path] | tuple[Path, ...] = (),
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    resolved_excludes = [path.resolve() for path in exclude_dirs if path.exists()]
    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for path in sorted(item for item in scan_root.rglob("*") if item.is_file()):
            resolved_path = path.resolve()
            if any(resolved_path.is_relative_to(exclude) for exclude in resolved_excludes):
                continue
            rel = inventory_file_key(path)
            suffix = path.suffix.lower()
            info = file_info(path, hash_max_bytes)
            fields = file_fields(path)
            row_count_value, row_count_status = row_count(
                path, suffix, int(info["bytes"]), row_count_max_bytes
            )
            package_names = sorted(memberships.get(rel, []))
            field_set = set(fields)
            rows.append(
                {
                    "file": rel,
                    "root": root_name_from_key(rel),
                    "asset_group": asset_group_from_key(rel),
                    "suffix": suffix,
                    "bytes": info["bytes"],
                    "sha256": info["sha256"],
                    "sha256_status": info["sha256_status"],
                    "row_count": row_count_value,
                    "row_count_status": row_count_status,
                    "fields": ";".join(fields),
                    "contains_direct_person_fields": "true" if field_set & DIRECT_PERSON_FIELDS else "false",
                    "contains_masked_person_fields": "true" if field_set & MASKED_PERSON_FIELDS else "false",
                    "in_any_zip_package": "true" if package_names else "false",
                    "package_count": len(package_names),
                    "package_memberships": ";".join(package_names),
                    "publication_level": publication_level(rel, field_set, package_names),
                }
            )
    return rows


def summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row.get("root", "")),
            str(row.get("asset_group", "")),
            str(row.get("in_any_zip_package", "")),
            str(row.get("publication_level", "")),
        )
        item = grouped.setdefault(
            key,
            {
                "root": key[0],
                "asset_group": key[1],
                "in_any_zip_package": key[2],
                "publication_level": key[3],
                "file_count": 0,
                "total_bytes": 0,
                "suffixes": Counter(),
            },
        )
        item["file_count"] += 1
        item["total_bytes"] += int(row.get("bytes") or 0)
        item["suffixes"][str(row.get("suffix", ""))] += 1
    return [
        {
            "root": item["root"],
            "asset_group": item["asset_group"],
            "in_any_zip_package": item["in_any_zip_package"],
            "publication_level": item["publication_level"],
            "file_count": item["file_count"],
            "total_bytes": item["total_bytes"],
            "suffix_counts_json": json.dumps(dict(sorted(item["suffixes"].items())), ensure_ascii=False),
        }
        for item in sorted(grouped.values(), key=lambda row: (row["root"], row["asset_group"], row["publication_level"]))
    ]


def privacy_summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: Counter[tuple[str, str, str, str]] = Counter()
    for row in rows:
        grouped[
            (
                str(row.get("root", "")),
                str(row.get("contains_direct_person_fields", "")),
                str(row.get("contains_masked_person_fields", "")),
                str(row.get("publication_level", "")),
            )
        ] += 1
    return [
        {
            "root": root,
            "contains_direct_person_fields": direct,
            "contains_masked_person_fields": masked,
            "publication_level": level,
            "file_count": count,
        }
        for (root, direct, masked, level), count in sorted(grouped.items())
    ]


def build_report(
    report_dir: Path,
    rows: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
    privacy_rows: list[dict[str, Any]],
    generated_at: str,
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "processed_asset_inventory_2026.md"
    packaged = [row for row in rows if row["in_any_zip_package"] == "true"]
    root_counts = Counter(str(row["root"]) for row in rows)
    level_counts = Counter(str(row["publication_level"]) for row in rows)
    lines = [
        "# Processed Asset Inventory",
        "",
        f"- Built at: {generated_at}",
        f"- Files inventoried: {len(rows)}",
        f"- Total bytes: {sum(int(row['bytes']) for row in rows)}",
        f"- Files already present in a zip package: {len(packaged)}",
        f"- Metadata-only files: {len(rows) - len(packaged)}",
        "",
        "## Roots",
        "",
        "| root | files |",
        "|---|---:|",
    ]
    for root, count in sorted(root_counts.items()):
        lines.append(f"| {root} | {count} |")
    lines.extend(
        [
            "",
            "## Publication Levels",
            "",
            "| publication_level | files |",
            "|---|---:|",
        ]
    )
    for level, count in sorted(level_counts.items()):
        lines.append(f"| {level} | {count} |")
    lines.extend(
        [
            "",
            "## Largest Unpackaged Groups",
            "",
            "| root | asset_group | publication_level | files | bytes |",
            "|---|---|---|---:|---:|",
        ]
    )
    unpackaged_summaries = [
        row for row in summaries if row["in_any_zip_package"] == "false"
    ]
    for row in sorted(unpackaged_summaries, key=lambda item: int(item["total_bytes"]), reverse=True)[:40]:
        lines.append(
            "| {root} | {asset_group} | {publication_level} | {file_count} | {total_bytes} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Privacy Summary",
            "",
            "| root | direct_person_fields | masked_person_fields | publication_level | files |",
            "|---|---|---|---|---:|",
        ]
    )
    for row in privacy_rows:
        lines.append(
            "| {root} | {contains_direct_person_fields} | {contains_masked_person_fields} | {publication_level} | {file_count} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `data/processed/processed_asset_inventory/processed_asset_file_inventory_2026.csv`",
            "- `data/processed/processed_asset_inventory/processed_asset_group_summary_2026.csv`",
            "- `data/processed/processed_asset_inventory/processed_asset_privacy_summary_2026.csv`",
            "",
            "## Notes",
            "",
            "- This is a metadata-only catalog for processed, cleaned, report, and dataset-document assets.",
            "- Files containing direct or masked person fields are not copied by this package; they are represented by path, size, fields, and hash status.",
            "- Large files may have `sha256_status=skipped_large_file` and/or `row_count_status=skipped_large_file` to keep the inventory build practical.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def build_processed_asset_inventory(
    *,
    scan_roots: list[Path] | tuple[Path, ...] = DEFAULT_SCAN_ROOTS,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    outputs_dir: Path = DEFAULT_OUTPUTS_DIR,
    hash_max_bytes: int | None = DEFAULT_HASH_MAX_BYTES,
    row_count_max_bytes: int | None = DEFAULT_ROW_COUNT_MAX_BYTES,
    generated_at: str | None = None,
) -> dict[str, Any]:
    scan_roots = [Path(path) for path in scan_roots]
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    outputs_dir = Path(outputs_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    memberships = collect_zip_memberships(outputs_dir)
    rows = inventory_rows(
        scan_roots,
        memberships,
        hash_max_bytes=hash_max_bytes,
        row_count_max_bytes=row_count_max_bytes,
        exclude_dirs=[output_dir],
    )
    summaries = summary_rows(rows)
    privacy_rows = privacy_summary_rows(rows)

    write_csv(
        output_dir / "processed_asset_file_inventory_2026.csv",
        rows,
        [
            "file",
            "root",
            "asset_group",
            "suffix",
            "bytes",
            "sha256",
            "sha256_status",
            "row_count",
            "row_count_status",
            "fields",
            "contains_direct_person_fields",
            "contains_masked_person_fields",
            "in_any_zip_package",
            "package_count",
            "package_memberships",
            "publication_level",
        ],
    )
    write_csv(
        output_dir / "processed_asset_group_summary_2026.csv",
        summaries,
        [
            "root",
            "asset_group",
            "in_any_zip_package",
            "publication_level",
            "file_count",
            "total_bytes",
            "suffix_counts_json",
        ],
    )
    write_csv(
        output_dir / "processed_asset_privacy_summary_2026.csv",
        privacy_rows,
        [
            "root",
            "contains_direct_person_fields",
            "contains_masked_person_fields",
            "publication_level",
            "file_count",
        ],
    )
    report_path = build_report(report_dir, rows, summaries, privacy_rows, generated_at)

    output_paths = sorted(path for path in output_dir.iterdir() if path.is_file())
    manifest = {
        "generated_at": generated_at,
        "dataset": "processed_asset_inventory",
        "status": "metadata_only_inventory_for_processed_cleaned_reports_and_dataset_docs",
        "scan_roots": [_path_key(path) for path in scan_roots],
        "hash_max_bytes": hash_max_bytes,
        "row_count_max_bytes": row_count_max_bytes,
        "row_counts": {
            "file_inventory": len(rows),
            "group_summary": len(summaries),
            "privacy_summary": len(privacy_rows),
            "files_in_any_zip_package": sum(1 for row in rows if row["in_any_zip_package"] == "true"),
            "files_not_in_zip_package": sum(1 for row in rows if row["in_any_zip_package"] == "false"),
        },
        "report": _path_key(report_path),
        "checksums": {_path_key(path): file_info(path, None) for path in output_paths},
    }
    manifest_path = output_dir / "processed_asset_inventory_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path, None)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build metadata-only processed asset inventory.")
    parser.add_argument(
        "--scan-roots",
        default=",".join(_path_key(path) for path in DEFAULT_SCAN_ROOTS),
        help="Comma-separated roots to scan.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--outputs-dir", type=Path, default=DEFAULT_OUTPUTS_DIR)
    parser.add_argument("--hash-max-bytes", type=int, default=DEFAULT_HASH_MAX_BYTES)
    parser.add_argument("--row-count-max-bytes", type=int, default=DEFAULT_ROW_COUNT_MAX_BYTES)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    scan_roots = [ROOT / value.strip() for value in args.scan_roots.split(",") if value.strip()]
    manifest = build_processed_asset_inventory(
        scan_roots=scan_roots,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        outputs_dir=args.outputs_dir,
        hash_max_bytes=args.hash_max_bytes,
        row_count_max_bytes=args.row_count_max_bytes,
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
