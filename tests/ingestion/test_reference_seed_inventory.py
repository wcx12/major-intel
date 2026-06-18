import csv
import json
from pathlib import Path

from scripts.ingestion.build_reference_seed_inventory import build_reference_seed_inventory


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_reference_seed_inventory_writes_normalized_indexes(tmp_path):
    seed_dir = tmp_path / "seeds"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "reports"
    write_csv(
        seed_dir / "rysxai_professions.full.csv",
        [
            {
                "rysxai_profession_id": "1",
                "major_code": "080717T",
                "major_name": "AI",
                "level": "本科",
                "category": "工学",
                "subject": "电子信息类",
                "degree": "工学",
                "limit_year": "四年",
                "heat": "100",
                "is_hot": "true",
            }
        ],
        [
            "rysxai_profession_id",
            "major_code",
            "major_name",
            "level",
            "category",
            "subject",
            "degree",
            "limit_year",
            "heat",
            "is_hot",
        ],
    )
    write_csv(
        seed_dir / "rysxai_universities.csv",
        [
            {
                "id": "1",
                "name": "Test University",
                "province": "Test",
                "city": "Test City",
                "town": "Test Town",
                "type": "综合",
                "property": "公办",
                "level": "本科",
                "department": "教育部",
                "tags": json.dumps(["双一流"], ensure_ascii=False),
            }
        ],
        ["id", "name", "province", "city", "town", "type", "property", "level", "department", "tags"],
    )
    write_csv(
        seed_dir / "policy_document_sources.csv",
        [
            {
                "source_id": "s1",
                "title": "Policy",
                "url": "https://www.moe.gov.cn/a",
                "source_domain": "www.moe.gov.cn",
                "source_level": "A",
                "source_type": "undergraduate_catalog",
                "issuing_org": "MOE",
                "published_date": "2026-01-01",
                "source_year": "2026",
                "notes": "sample",
            }
        ],
        [
            "source_id",
            "title",
            "url",
            "source_domain",
            "source_level",
            "source_type",
            "issuing_org",
            "published_date",
            "source_year",
            "notes",
        ],
    )
    write_csv(
        seed_dir / "official_site_recommendation_websearch_sample.csv",
        [
            {
                "school_name": "Test University",
                "source_type": "recommendation_exemption",
                "start_url": "https://school.edu.cn/a",
                "year": "2026",
                "document_type": "recommendation_exemption_list",
                "discovery_query": "q",
                "discovery_title": "title",
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

    manifest = build_reference_seed_inventory(
        seed_dir=seed_dir,
        output_dir=output_dir,
        report_dir=report_dir,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["seed_files"] == 4
    assert manifest["row_counts"]["official_site_seed_rows"] == 1
    assert manifest["row_counts"]["policy_sources"] == 1
    rows = list(
        csv.DictReader(
            (output_dir / "reference_seed_official_site_unique_sources_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    assert rows[0]["source_domain"] == "school.edu.cn"
    assert (report_dir / "reference_seed_inventory_2026.md").exists()
