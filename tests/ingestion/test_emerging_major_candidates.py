import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from major_intel.ingestion.emerging_major_candidates import build_outputs


def test_build_outputs_writes_candidate_csv_and_coverage_report(tmp_path):
    candidates_jsonl = tmp_path / "candidates.jsonl"
    attachments_jsonl = tmp_path / "attachments.jsonl"
    candidates_jsonl.write_text(
        json.dumps(
            {
                "candidate_id": "emerging_major:1",
                "major_code": "080717T",
                "major_name": "人工智能",
                "major_level": "本科",
                "event_type": "filing_added",
                "event_year": 2024,
                "candidate_status": "catalog_confirmed",
                "source_title": "教育部通知",
                "source_url": "http://www.moe.gov.cn/source.html",
                "attachment_url": "http://www.moe.gov.cn/majors.xlsx",
                "source_level": "A",
                "evidence_text": "080717T 人工智能",
                "raw_path": "raw/majors.xlsx",
                "parsed_from": "xlsx",
                "captured_at": "2026-06-12T00:00:00+08:00",
                "warnings": [],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    with candidates_jsonl.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "candidate_id": "emerging_major:2",
                    "major_code": "080717T",
                    "major_name": "人工智能",
                    "major_level": "本科",
                    "event_type": "catalog_added",
                    "event_year": 2025,
                    "candidate_status": "catalog_confirmed",
                    "source_title": "教育部目录",
                    "source_url": "http://www.moe.gov.cn/catalog.html",
                    "attachment_url": "http://www.moe.gov.cn/catalog.pdf",
                    "source_level": "A",
                    "evidence_text": "080717T 人工智能",
                    "raw_path": "raw/catalog.pdf",
                    "parsed_from": "pdf",
                    "captured_at": "2026-06-12T00:00:00+08:00",
                    "warnings": [],
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    attachments_jsonl.write_text(
        json.dumps(
            {
                "attachment_url": "http://www.moe.gov.cn/majors.xlsx",
                "file_type": "xlsx",
                "parse_status": "ok",
                "row_count": 3,
                "candidate_major_count": 1,
                "source_year": "2024",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    output_csv = tmp_path / "candidates.csv"
    unique_major_csv = tmp_path / "unique_majors.csv"
    coverage_report = tmp_path / "coverage.md"
    coverage_csv = tmp_path / "coverage.csv"

    summary = build_outputs(
        candidates_jsonl=candidates_jsonl,
        attachments_jsonl=attachments_jsonl,
        output_csv=output_csv,
        unique_major_csv=unique_major_csv,
        coverage_report=coverage_report,
        coverage_csv=coverage_csv,
    )

    assert summary["candidate_count"] == 2
    assert summary["unique_major_count"] == 1
    assert output_csv.read_text(encoding="utf-8-sig").startswith("candidate_id,")
    unique_text = unique_major_csv.read_text(encoding="utf-8-sig")
    assert "major_key," in unique_text
    assert "080717T|人工智能" in unique_text
    report = coverage_report.read_text(encoding="utf-8")
    assert "# 新兴专业候选覆盖报告" in report
    assert "去重专业数：1" in report
    assert "2024" in report
    assert "parse_status=ok" in report
    assert coverage_csv.exists()
