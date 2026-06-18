import csv
import json
from pathlib import Path

from scripts.ingestion.build_emerging_major_candidate_details import (
    build_emerging_major_candidate_details,
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


def test_build_emerging_major_candidate_details_writes_jsonl_and_summaries(tmp_path):
    input_dir = tmp_path / "policy_documents"
    output_dir = tmp_path / "out"
    stem = "test"
    row = {
        "schema_version": "emerging_major_candidate/v1",
        "candidate_id": "c1",
        "major_code": "080717T",
        "major_name": "人工智能",
        "major_level": "本科",
        "discipline_category": "工学",
        "major_class": "电子信息类",
        "degree": "工学",
        "study_years": "四年",
        "event_type": "catalog_added",
        "event_year": "2026",
        "candidate_status": "catalog_confirmed",
        "source_title": "测试通知",
        "source_url": "https://example.edu/notice",
        "attachment_url": "https://example.edu/a.pdf",
        "source_level": "A",
        "evidence_text": "080717T 人工智能",
        "raw_path": "data/raw/a.pdf",
        "parsed_from": "pdf",
        "captured_at": "2026-06-14T00:00:00+08:00",
        "warnings": ["sample_warning"],
    }
    write_jsonl(input_dir / f"emerging_major_candidates_{stem}.jsonl", [row])
    csv_fields = [
        "candidate_id",
        "major_code",
        "major_name",
        "major_level",
        "discipline_category",
        "major_class",
        "degree",
        "study_years",
        "event_type",
        "event_year",
        "candidate_status",
        "source_title",
        "source_url",
        "attachment_url",
        "source_level",
        "evidence_text",
        "raw_path",
        "parsed_from",
        "captured_at",
        "warnings_json",
    ]
    csv_row = {field: row.get(field, "") for field in csv_fields}
    csv_row["warnings_json"] = "[]"
    write_csv(input_dir / f"emerging_major_candidates_{stem}.csv", [csv_row], csv_fields)
    write_csv(
        input_dir / f"emerging_major_unique_majors_{stem}.csv",
        [
            {
                "major_key": "080717T|人工智能",
                "major_code": "080717T",
                "major_name": "人工智能",
            }
        ],
        ["major_key", "major_code", "major_name"],
    )
    write_csv(
        input_dir / f"emerging_major_coverage_{stem}.csv",
        [{"source_year": "2026", "row_count": "1"}],
        ["source_year", "row_count"],
    )
    write_csv(input_dir / "undergraduate_major_official_events_20260612_v5.csv", [], ["event_record_id"])
    write_csv(input_dir / "undergraduate_major_official_event_summary_20260612_v5.csv", [], ["event_year"])
    write_csv(input_dir / "undergraduate_major_official_events_rejected_20260612_v5.csv", [], ["candidate_id"])
    (input_dir / "undergraduate_major_official_events_manifest_20260612_v5.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    manifest = build_emerging_major_candidate_details(
        input_dir=input_dir,
        output_dir=output_dir,
        stem=stem,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["candidate_jsonl"] == 1
    assert manifest["row_counts"]["candidate_distribution"] == 1
    assert (output_dir / "emerging_major_candidates_2026.jsonl").exists()
    warning_rows = list(
        csv.DictReader(
            (output_dir / "emerging_major_warning_summary_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    assert warning_rows[0]["warning"] == "sample_warning"
