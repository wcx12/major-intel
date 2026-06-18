import csv
import json
from pathlib import Path

from scripts.ingestion.build_graduate_chsi_public_sources import build_graduate_chsi_public_sources


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


def test_build_graduate_chsi_public_sources_excludes_unmasked_records(tmp_path):
    input_dir = tmp_path / "chsi"
    output_dir = tmp_path / "out"
    input_dir.mkdir()
    write_csv(
        input_dir / "master_records_public.csv",
        [
            {
                "public_record_id": "p1",
                "school_name": "测试大学",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name_masked": "张*",
                "student_id_masked": "",
                "undergraduate_school": "",
                "undergraduate_major": "",
                "college": "",
                "major": "",
                "admission_major": "计算机",
                "ranking": "",
                "remarks": "",
                "source_url": "https://yzst.chsi.com.cn/sch/viewBulletin--infoId-1.dhtml",
                "title": "测试大学_院校信息_中国研究生招生信息网",
                "needs_review": "false",
                "quality_score": "90",
                "quality_flags": "",
            }
        ],
        [
            "public_record_id",
            "school_name",
            "year",
            "document_type",
            "route",
            "person_name_masked",
            "student_id_masked",
            "undergraduate_school",
            "undergraduate_major",
            "college",
            "major",
            "admission_major",
            "ranking",
            "remarks",
            "source_url",
            "title",
            "needs_review",
            "quality_score",
            "quality_flags",
        ],
    )
    write_csv(
        input_dir / "school_year_summary.csv",
        [
            {
                "school_name": "测试大学",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "record_count": "1",
                "unique_person_count": "1",
                "needs_review_count": "0",
                "with_undergraduate_school_count": "0",
                "with_admission_major_count": "1",
                "source_document_count": "1",
            }
        ],
        [
            "school_name",
            "year",
            "document_type",
            "route",
            "record_count",
            "unique_person_count",
            "needs_review_count",
            "with_undergraduate_school_count",
            "with_admission_major_count",
            "source_document_count",
        ],
    )
    write_csv(
        input_dir / "chsi_schools_sample.csv",
        [
            {
                "chsi_school_name": "测试大学",
                "chsi_sch_id": "1",
                "chsi_school_url": "https://yzst.chsi.com.cn/sch/schoolInfo--schId-1.dhtml",
            }
        ],
        ["chsi_school_name", "chsi_sch_id", "chsi_school_url"],
    )
    write_csv(
        input_dir / "chsi_seeds_sample.csv",
        [
            {
                "school_name": "测试大学",
                "source_type": "postgraduate_admission",
                "start_url": "https://yzst.chsi.com.cn/sch/viewBulletin--infoId-1.dhtml",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "discovery_query": "chsi_bulletin",
                "discovery_title": "2026拟录取",
                "discovery_rank": "1",
            }
        ],
        [
            "school_name",
            "source_type",
            "start_url",
            "year",
            "document_type",
            "discovery_query",
            "discovery_title",
            "discovery_rank",
        ],
    )
    write_jsonl(
        input_dir / "crawl_sample/documents.jsonl",
        [
            {
                "captured_at": "2026-06-14T00:00:00+08:00",
                "school_name": "测试大学",
                "source_type": "postgraduate_admission",
                "source_url": "https://yzst.chsi.com.cn/sch/viewBulletin--infoId-1.dhtml",
                "title": "测试大学_院校信息_中国研究生招生信息网",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "content_type": "text/html",
                "content_length": "100",
            }
        ],
    )
    write_jsonl(
        input_dir / "crawl_sample/records.jsonl",
        [{"person_name": "张三", "school_name": "测试大学"}],
    )
    write_csv(
        input_dir / "master_records_clean.csv",
        [{"person_name": "张三", "school_name": "测试大学"}],
        ["person_name", "school_name"],
    )

    manifest = build_graduate_chsi_public_sources(
        input_dir=input_dir,
        output_dir=output_dir,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["public_records"] == 1
    assert manifest["row_counts"]["school_index_inventory"] == 1
    assert manifest["row_counts"]["document_inventory"] == 1
    source_manifest = list(
        csv.DictReader(
            (output_dir / "chsi_source_file_manifest_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    sensitive = [row for row in source_manifest if row["contains_unmasked_person_level_fields"] == "true"]
    assert sensitive
    assert all(row["included_or_summarized_in_dataset"] == "false" for row in sensitive)
