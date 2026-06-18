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
DEFAULT_SCAN_ROOTS = (ROOT / "data/raw", ROOT / "data/logs")
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/raw_source_inventory"
DEFAULT_REPORT_DIR = ROOT / "reports/raw_source_inventory"
DEFAULT_OUTPUTS_DIR = ROOT / "outputs"
DEFAULT_HASH_MAX_BYTES = 20_000_000


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def file_info(path: Path, hash_max_bytes: int | None = None) -> dict[str, Any]:
    size = path.stat().st_size
    if hash_max_bytes is not None and size > hash_max_bytes:
        return {"bytes": size, "sha256": "", "sha256_status": "skipped_large_file"}
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            total += len(chunk)
            digest.update(chunk)
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
        for index in range(len(parts) - 2):
            if parts[index] == "data" and parts[index + 1] in {"raw", "logs"}:
                return Path(*parts[index:]).as_posix()
    return path.as_posix()


def storage_layer_from_key(file_key: str) -> str:
    parts = Path(file_key).parts
    if len(parts) >= 2 and parts[0] == "data":
        return parts[1]
    return ""


def raw_family_from_key(file_key: str) -> str:
    parts = Path(file_key).parts
    if len(parts) >= 3 and parts[0] == "data":
        return parts[2]
    return Path(file_key).parent.name


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
                    if name.startswith("data/raw/") or name.startswith("data/logs/"):
                        memberships[name].append(package_key(zip_path, outputs_dir))
        except zipfile.BadZipFile:
            continue
    return memberships


def inventory_rows(
    scan_roots: list[Path],
    memberships: dict[str, list[str]],
    *,
    hash_max_bytes: int | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for root in scan_roots:
        if not root.exists():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            rel = inventory_file_key(path)
            info = file_info(path, hash_max_bytes=hash_max_bytes)
            package_names = sorted(memberships.get(rel, []))
            rows.append(
                {
                    "file": rel,
                    "storage_layer": storage_layer_from_key(rel),
                    "source_family": raw_family_from_key(rel),
                    "suffix": path.suffix.lower(),
                    "bytes": info["bytes"],
                    "sha256": info["sha256"],
                    "sha256_status": info["sha256_status"],
                    "in_any_zip_package": "true" if package_names else "false",
                    "package_count": len(package_names),
                    "package_memberships": ";".join(package_names),
                }
            )
    return rows


def summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row.get("storage_layer", "")),
            str(row.get("source_family", "")),
            str(row.get("in_any_zip_package", "")),
        )
        item = grouped.setdefault(
            key,
            {
                "storage_layer": key[0],
                "source_family": key[1],
                "in_any_zip_package": key[2],
                "file_count": 0,
                "total_bytes": 0,
                "suffixes": Counter(),
            },
        )
        item["file_count"] += 1
        item["total_bytes"] += int(row.get("bytes") or 0)
        item["suffixes"][str(row.get("suffix", ""))] += 1
    output: list[dict[str, Any]] = []
    for item in grouped.values():
        output.append(
            {
                "storage_layer": item["storage_layer"],
                "source_family": item["source_family"],
                "in_any_zip_package": item["in_any_zip_package"],
                "file_count": item["file_count"],
                "total_bytes": item["total_bytes"],
                "suffix_counts_json": json.dumps(dict(sorted(item["suffixes"].items())), ensure_ascii=False),
            }
        )
    return sorted(output, key=lambda row: (row["storage_layer"], row["source_family"], row["in_any_zip_package"]))


def package_summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        memberships = [value for value in str(row.get("package_memberships", "")).split(";") if value]
        if not memberships:
            memberships = ["<not_packaged>"]
        for package in memberships:
            item = grouped.setdefault(package, {"package": package, "file_count": 0, "total_bytes": 0})
            item["file_count"] += 1
            item["total_bytes"] += int(row.get("bytes") or 0)
    return sorted(grouped.values(), key=lambda row: (row["package"] == "<not_packaged>", row["package"]))


def build_report(
    report_dir: Path,
    rows: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
    package_summaries: list[dict[str, Any]],
    generated_at: str,
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "raw_source_inventory_2026.md"
    packaged = [row for row in rows if row["in_any_zip_package"] == "true"]
    unpackaged = [row for row in rows if row["in_any_zip_package"] == "false"]
    family_counts = Counter(str(row["source_family"]) for row in rows)
    lines = [
        "# Raw Source Inventory",
        "",
        f"- Built at: {generated_at}",
        f"- Files inventoried: {len(rows)}",
        f"- Total bytes: {sum(int(row['bytes']) for row in rows)}",
        f"- Files already present in a zip package: {len(packaged)}",
        f"- Metadata-only unpackaged files: {len(unpackaged)}",
        "",
        "## Largest Source Families",
        "",
        "| source_family | files |",
        "|---|---:|",
    ]
    for family, count in family_counts.most_common(30):
        lines.append(f"| {family} | {count} |")
    lines.extend(
        [
            "",
            "## Package Coverage",
            "",
            "| package | files | bytes |",
            "|---|---:|---:|",
        ]
    )
    for row in package_summaries[:60]:
        lines.append(f"| {row['package']} | {row['file_count']} | {row['total_bytes']} |")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `data/processed/raw_source_inventory/raw_source_file_inventory_2026.csv`",
            "- `data/processed/raw_source_inventory/raw_source_family_summary_2026.csv`",
            "- `data/processed/raw_source_inventory/raw_source_package_summary_2026.csv`",
            "",
            "## Notes",
            "",
        "- This is a metadata-only inventory. It does not redistribute raw webpages, PDFs, images, JSON payloads, or crawl logs.",
        "- SHA-256 is computed for files at or below the configured size threshold; larger files keep byte size and `sha256_status=skipped_large_file`.",
        "- `package_memberships` records which existing zip packages contain the raw/log file when available.",
        "- Unpackaged raw files remain auditable through path, byte size, and SHA-256 without exposing source contents.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def build_raw_source_inventory(
    *,
    scan_roots: list[Path] | tuple[Path, ...] = DEFAULT_SCAN_ROOTS,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    outputs_dir: Path = DEFAULT_OUTPUTS_DIR,
    hash_max_bytes: int | None = DEFAULT_HASH_MAX_BYTES,
    generated_at: str | None = None,
) -> dict[str, Any]:
    scan_roots = [Path(path) for path in scan_roots]
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    outputs_dir = Path(outputs_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    memberships = collect_zip_memberships(outputs_dir)
    rows = inventory_rows(scan_roots, memberships, hash_max_bytes=hash_max_bytes)
    summaries = summary_rows(rows)
    package_summaries = package_summary_rows(rows)

    write_csv(
        output_dir / "raw_source_file_inventory_2026.csv",
        rows,
        [
            "file",
            "storage_layer",
            "source_family",
            "suffix",
            "bytes",
            "sha256",
            "sha256_status",
            "in_any_zip_package",
            "package_count",
            "package_memberships",
        ],
    )
    write_csv(
        output_dir / "raw_source_family_summary_2026.csv",
        summaries,
        [
            "storage_layer",
            "source_family",
            "in_any_zip_package",
            "file_count",
            "total_bytes",
            "suffix_counts_json",
        ],
    )
    write_csv(
        output_dir / "raw_source_package_summary_2026.csv",
        package_summaries,
        ["package", "file_count", "total_bytes"],
    )
    report_path = build_report(report_dir, rows, summaries, package_summaries, generated_at)

    output_paths = sorted(path for path in output_dir.iterdir() if path.is_file())
    manifest = {
        "generated_at": generated_at,
        "dataset": "raw_source_inventory",
        "status": "metadata_only_inventory_for_raw_and_log_sources",
        "scan_roots": [_path_key(path) for path in scan_roots],
        "hash_max_bytes": hash_max_bytes,
        "row_counts": {
            "file_inventory": len(rows),
            "family_summary": len(summaries),
            "package_summary": len(package_summaries),
            "files_in_any_zip_package": sum(1 for row in rows if row["in_any_zip_package"] == "true"),
            "files_not_in_zip_package": sum(1 for row in rows if row["in_any_zip_package"] == "false"),
        },
        "report": _path_key(report_path),
        "checksums": {_path_key(path): file_info(path) for path in output_paths},
    }
    manifest_path = output_dir / "raw_source_inventory_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a metadata-only raw/log source inventory.")
    parser.add_argument(
        "--scan-roots",
        default=",".join(_path_key(path) for path in DEFAULT_SCAN_ROOTS),
        help="Comma-separated roots to scan.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--outputs-dir", type=Path, default=DEFAULT_OUTPUTS_DIR)
    parser.add_argument("--hash-max-bytes", type=int, default=DEFAULT_HASH_MAX_BYTES)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    scan_roots = [ROOT / value.strip() for value in args.scan_roots.split(",") if value.strip()]
    manifest = build_raw_source_inventory(
        scan_roots=scan_roots,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        outputs_dir=args.outputs_dir,
        hash_max_bytes=args.hash_max_bytes,
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
