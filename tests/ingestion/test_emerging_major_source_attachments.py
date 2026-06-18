import csv
import json
from pathlib import Path

from scripts.ingestion.build_emerging_major_source_attachments import (
    build_emerging_major_source_attachments,
)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_build_emerging_major_source_attachments_writes_provenance_tables(tmp_path):
    input_dir = tmp_path / "policy_documents"
    log_dir = tmp_path / "logs"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "reports"
    raw_dir = tmp_path / "raw"
    raw_page = raw_dir / "page.html"
    raw_pdf = raw_dir / "attachment.pdf"
    raw_page.parent.mkdir(parents=True)
    raw_page.write_text("<html>notice</html>", encoding="utf-8")
    raw_pdf.write_bytes(b"%PDF-1.4")

    document = {
        "schema_version": "emerging_major_source_document/v1",
        "doc_id": "policy_doc:1",
        "source_id": "moe_test",
        "title": "Test Notice",
        "url": "https://example.edu/notice",
        "source_domain": "example.edu",
        "source_level": "A",
        "source_type": "annual_filing_approval",
        "issuing_org": "MOE",
        "published_date": "2026-01-01",
        "source_year": "2026",
        "captured_at": "2026-06-14T00:00:00+08:00",
        "raw_path": str(raw_page),
        "content_sha256": "abc",
        "text_length": 12,
        "attachment_count": 1,
    }
    attachment = {
        "schema_version": "policy_attachment/v1",
        "parent_doc_id": "policy_doc:1",
        "parent_source_id": "moe_test",
        "source_title": "Test Notice",
        "source_url": "https://example.edu/notice",
        "source_year": "2026",
        "source_level": "A",
        "attachment_url": "https://example.edu/a.pdf",
        "attachment_title": "Test Attachment",
        "file_type": "pdf",
        "raw_path": str(raw_pdf),
        "parse_status": "ok",
        "row_count": 10,
        "candidate_major_count": 8,
        "warnings": ["sample_warning"],
    }
    write_jsonl(input_dir / "documents_test.jsonl", [document])
    write_jsonl(input_dir / "attachments_test.jsonl", [attachment])
    (log_dir / "test_manifest.json").parent.mkdir(parents=True, exist_ok=True)
    (log_dir / "test_manifest.json").write_text("{}\n", encoding="utf-8")
    (log_dir / "test_failures.jsonl").write_text("", encoding="utf-8")

    manifest = build_emerging_major_source_attachments(
        input_dir=input_dir,
        log_dir=log_dir,
        output_dir=output_dir,
        report_dir=report_dir,
        stem="test",
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["source_documents"] == 1
    assert manifest["row_counts"]["source_attachments"] == 1
    assert manifest["row_counts"]["local_raw_files_found"] == 2
    assert (output_dir / "emerging_major_source_documents_2026.csv").exists()
    rows = list(
        csv.DictReader(
            (output_dir / "emerging_major_attachment_parse_summary_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    assert rows[0]["candidate_major_count"] == "8"
    assert (report_dir / "emerging_major_source_attachments_2026.md").exists()
