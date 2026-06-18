import csv
import json
from pathlib import Path

from scripts.ingestion.build_graduate_official_batch_inventory import (
    build_graduate_official_batch_inventory,
)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_build_graduate_official_batch_inventory_keeps_person_records_as_inventory_only(tmp_path):
    input_root = tmp_path / "processed"
    batch = input_root / "graduate_outcomes_official_site_websearch_test"
    late_batch = input_root / "official_site_recommendation_websearch_test"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "reports"
    write_jsonl(
        batch / "documents.jsonl",
        [
            {
                "schema_version": "graduate_outcome_document/v1",
                "captured_at": "2026-05-22T00:00:00+08:00",
                "school_name": "Test University",
                "source_type": "recommendation_exemption",
                "source_url": "https://example.edu/a",
                "start_url": "https://example.edu/a",
                "title": "Test Notice",
                "year": 2026,
                "document_type": "recommendation_exemption_list",
                "matched_keywords": ["recommendation"],
                "content_type": "text/html",
                "content_length": 100,
                "content_hash": "abc",
                "raw_path": "data/raw/a.html",
                "parse_status": "parsed",
                "record_count": 1,
            }
        ],
    )
    write_csv(
        batch / "records_clean.csv",
        [
            {
                "person_name": "Alice",
                "person_name_masked": "A**",
                "student_id": "123",
                "student_id_masked": "1***",
                "undergraduate_major": "Computer Science",
            }
        ],
        ["person_name", "person_name_masked", "student_id", "student_id_masked", "undergraduate_major"],
    )
    write_jsonl(
        batch / "records.jsonl",
        [
            {
                "person_name": "Alice",
                "student_id": "123",
                "undergraduate_major": "Computer Science",
            }
        ],
    )
    write_csv(
        batch / "school_year_summary.csv",
        [{"school_name": "Test University", "year": "2026", "record_count": "1"}],
        ["school_name", "year", "record_count"],
    )
    write_jsonl(
        late_batch / "documents.jsonl",
        [
            {
                "schema_version": "graduate_outcome_document/v1",
                "captured_at": "2026-06-02T00:00:00+08:00",
                "school_name": "Late Test University",
                "source_type": "official_site",
                "source_url": "https://late.example.edu/a",
                "start_url": "https://late.example.edu/a",
                "title": "Late Notice",
                "year": 2025,
                "document_type": "postgraduate_admission_list",
                "matched_keywords": [],
                "content_type": "text/html",
                "content_length": 50,
                "content_hash": "def",
                "raw_path": "data/raw/b.html",
                "parse_status": "parsed_no_records",
                "record_count": 0,
            }
        ],
    )

    manifest = build_graduate_official_batch_inventory(
        input_root=input_root,
        output_dir=output_dir,
        report_dir=report_dir,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["batch_directories"] == 2
    assert manifest["row_counts"]["batch_files"] == 5
    assert manifest["row_counts"]["batch_documents"] == 2
    file_rows = list(
        csv.DictReader(
            (output_dir / "graduate_official_batch_files_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    clean_row = next(row for row in file_rows if row["file_name"] == "records_clean.csv")
    assert clean_row["contains_direct_person_fields"] == "true"
    assert clean_row["publication_level"] == "inventory_only_direct_person_fields_present"
    jsonl_row = next(row for row in file_rows if row["file_name"] == "records.jsonl")
    assert jsonl_row["contains_direct_person_fields"] == "true"
    assert jsonl_row["publication_level"] == "inventory_only_direct_person_fields_present"
    assert (output_dir / "graduate_official_batch_documents_2026.csv").exists()
    assert (report_dir / "graduate_official_batch_inventory_2026.md").exists()
