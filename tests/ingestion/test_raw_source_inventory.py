import csv
import zipfile
from pathlib import Path

from scripts.ingestion.build_raw_source_inventory import build_raw_source_inventory


def test_build_raw_source_inventory_records_package_memberships(tmp_path):
    raw_root = tmp_path / "data" / "raw"
    log_root = tmp_path / "data" / "logs"
    outputs_dir = tmp_path / "outputs"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "reports"
    raw_file = raw_root / "source_a" / "page.html"
    log_file = log_root / "source_a" / "crawl_manifest.json"
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text("<html>source</html>", encoding="utf-8")
    log_file.write_text("{}\n", encoding="utf-8")
    outputs_dir.mkdir(parents=True)
    with zipfile.ZipFile(outputs_dir / "source_a_raw.zip", "w") as archive:
        archive.write(raw_file, "data/raw/source_a/page.html")

    manifest = build_raw_source_inventory(
        scan_roots=[raw_root, log_root],
        output_dir=output_dir,
        report_dir=report_dir,
        outputs_dir=outputs_dir,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["file_inventory"] == 2
    rows = list(
        csv.DictReader(
            (output_dir / "raw_source_file_inventory_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    packaged = next(row for row in rows if row["file"].endswith("page.html"))
    assert packaged["in_any_zip_package"] == "true"
    assert packaged["package_memberships"] == "outputs/source_a_raw.zip"
    unpackaged = next(row for row in rows if row["file"].endswith("crawl_manifest.json"))
    assert unpackaged["in_any_zip_package"] == "false"
    assert (report_dir / "raw_source_inventory_2026.md").exists()
