import json
from pathlib import Path

from scripts.ingestion.build_vocational_major_register_index import (
    build_cross_year_unique_rows,
    build_index,
)


def test_build_cross_year_unique_rows_merges_years_and_counts_schools():
    rows = build_cross_year_unique_rows(
        [
            {
                "year": "2025",
                "major_code": "510111",
                "major_name": "低空安全与技术",
                "province_name": "北京市",
                "school_name": "北京工业职业技术学院",
            },
            {
                "year": "2026",
                "major_code": "510111",
                "major_name": "低空安全与技术",
                "province_name": "河北省",
                "school_name": "河北样例职业学院",
            },
        ]
    )

    assert len(rows) == 1
    assert rows[0]["first_year"] == "2025"
    assert rows[0]["latest_year"] == "2026"
    assert rows[0]["years"] == "2025,2026"
    assert rows[0]["record_count"] == 2
    assert rows[0]["province_count"] == 2
    assert rows[0]["school_count"] == 2


def test_build_index_writes_outputs(tmp_path):
    input_path = tmp_path / "records.jsonl"
    input_path.write_text(
        json.dumps(
            {
                "record_id": "r1",
                "year": "2026",
                "province_name": "北京市",
                "major_code": "510111",
                "major_name": "低空安全与技术",
                "school_name": "北京工业职业技术学院",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    records_csv = tmp_path / "records.csv"
    unique_csv = tmp_path / "unique.csv"
    report = tmp_path / "coverage.md"

    summary = build_index(
        input_jsonls=[input_path],
        output_records_csv=records_csv,
        output_unique_csv=unique_csv,
        coverage_report=report,
    )

    assert summary["record_count"] == 1
    assert summary["unique_major_count"] == 1
    assert records_csv.exists()
    assert unique_csv.exists()
    assert "2026: 1 条" in report.read_text(encoding="utf-8")
