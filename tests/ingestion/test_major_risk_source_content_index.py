import csv
import json
from pathlib import Path

from scripts.ingestion.build_major_risk_source_content_index import (
    build_major_risk_source_content_index,
)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_build_major_risk_source_content_index_extracts_keyword_snippets(tmp_path):
    text_path = tmp_path / "source.txt"
    text_path.write_text(
        "\n".join(
            [
                "学校拟撤销信息管理与信息系统专业，并同步停招。",
                "该专业曾被列入红牌专业，就业率偏低。",
                "另有人工智能教育新增专业申请表。",
            ]
        ),
        encoding="utf-8",
    )
    archive_csv = tmp_path / "archive.csv"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "report"
    fields = [
        "archive_id",
        "source_url",
        "source_domain",
        "source_title_sample",
        "source_publishers",
        "evidence_families",
        "source_tables",
        "crawl_status",
        "content_type",
        "raw_path",
        "text_path",
        "text_length",
    ]
    write_csv(
        archive_csv,
        [
            {
                "archive_id": "a1",
                "source_url": "https://example.test/source",
                "source_domain": "example.test",
                "source_title_sample": "撤销专业公示",
                "source_publishers": "example",
                "evidence_families": "official_policy_warning",
                "source_tables": "policy.csv",
                "crawl_status": "cached",
                "content_type": "text/plain",
                "raw_path": "raw.bin",
                "text_path": str(text_path),
                "text_length": str(text_path.stat().st_size),
            }
        ],
        fields,
    )

    manifest = build_major_risk_source_content_index(
        archive_csv=archive_csv,
        output_dir=output_dir,
        report_dir=report_dir,
        generated_at="2026-06-14",
    )

    docs = read_rows(output_dir / "major_risk_source_content_documents_2026.csv")
    snippets = read_rows(output_dir / "major_risk_source_content_snippets_2026.csv")
    summary = read_rows(output_dir / "major_risk_source_content_keyword_summary_2026.csv")
    manifest_data = json.loads(
        (output_dir / "major_risk_source_content_index_manifest_2026.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["dataset"] == "major_risk_source_content_index"
    assert manifest_data["dataset"] == "major_risk_source_content_index"
    assert manifest["row_counts"]["documents"] == 1
    assert manifest_data["document_coverage"]["documents_with_keyword_hits"] == 1
    assert docs[0]["matched_keyword_count"]
    assert any(row["keyword"] == "撤销" for row in snippets)
    assert any(row["keyword"] == "人工智能" for row in snippets)
    assert any(row["keyword_group"] == "risk_adjustment" for row in summary)
    assert (report_dir / "major_risk_source_content_index_2026.md").exists()
