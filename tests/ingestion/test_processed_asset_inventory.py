import csv
import zipfile
from pathlib import Path

from scripts.ingestion.build_processed_asset_inventory import (
    build_processed_asset_inventory,
)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_processed_asset_inventory_classifies_person_fields_and_packages(tmp_path):
    processed = tmp_path / "data" / "processed"
    cleaned = tmp_path / "data" / "cleaned"
    reports = tmp_path / "reports"
    docs = tmp_path / "docs" / "datasets"
    outputs = tmp_path / "outputs"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "report_out"

    packaged = processed / "safe" / "summary.csv"
    direct = cleaned / "people" / "records_clean.csv"
    eval_file = reports / "volunteer_matching" / "run.json"
    doc_file = docs / "dataset.md"
    write_csv(packaged, [{"metric": "count", "value": "1"}], ["metric", "value"])
    write_csv(direct, [{"person_name": "Alice", "student_id": "123"}], ["person_name", "student_id"])
    eval_file.parent.mkdir(parents=True, exist_ok=True)
    eval_file.write_text("{}\n", encoding="utf-8")
    doc_file.parent.mkdir(parents=True, exist_ok=True)
    doc_file.write_text("# Dataset\n", encoding="utf-8")
    outputs.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(outputs / "safe.zip", "w") as archive:
        archive.write(packaged, "data/processed/safe/summary.csv")

    manifest = build_processed_asset_inventory(
        scan_roots=[processed, cleaned, reports, docs],
        output_dir=output_dir,
        report_dir=report_dir,
        outputs_dir=outputs,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["file_inventory"] == 4
    rows = list(
        csv.DictReader(
            (output_dir / "processed_asset_file_inventory_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    packaged_row = next(row for row in rows if row["file"].endswith("summary.csv"))
    assert packaged_row["in_any_zip_package"] == "true"
    direct_row = next(row for row in rows if row["file"].endswith("records_clean.csv"))
    assert direct_row["publication_level"] == "metadata_only_direct_person_fields_present"
    eval_row = next(row for row in rows if row["file"].endswith("run.json"))
    assert eval_row["publication_level"] == "metadata_only_non_crawl_eval_artifact"
    assert (report_dir / "processed_asset_inventory_2026.md").exists()
