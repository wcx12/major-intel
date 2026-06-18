import csv
import json
from pathlib import Path

from scripts.ingestion.build_graduate_source_discovery import build_graduate_source_discovery


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_build_graduate_source_discovery_outputs_queue_summaries(tmp_path):
    input_dir = tmp_path / "graduate_outcomes"
    output_dir = tmp_path / "out"
    input_dir.mkdir()
    task_fields = [
        "school_id",
        "school_name",
        "province",
        "level",
        "year",
        "source_type",
        "document_type",
        "eligibility_hint",
        "search_query",
        "preferred_domains",
        "status",
        "found_url",
        "notes",
    ]
    task_row = {
        "school_id": "1",
        "school_name": "测试大学",
        "province": "测试省",
        "level": "本科",
        "year": "2026",
        "source_type": "recommendation_exemption",
        "document_type": "recommendation_exemption_list",
        "eligibility_hint": "recommended",
        "search_query": '"测试大学" "推荐免试"',
        "preferred_domains": "测试大学 研究生院",
        "status": "pending",
        "found_url": "",
        "notes": "",
    }
    write_csv(input_dir / "discovery_tasks_2024_2026.csv", [task_row], task_fields)
    write_csv(
        input_dir / "discovery_tasks_recommendation_exemption_recommended_2024_2026.csv",
        [task_row],
        task_fields,
    )
    write_csv(
        input_dir / "official_site_discovery_queue_recommendation_exemption.csv",
        [
            {
                "school_id": "1",
                "school_name": "测试大学",
                "province": "测试省",
                "city": "测试市",
                "department": "教育部",
                "status": "needs_official_homepage",
                "notes": "priority",
            }
        ],
        ["school_id", "school_name", "province", "city", "department", "status", "notes"],
    )
    write_csv(
        input_dir / "school_official_sites_recommended_laosheng.csv",
        [
            {
                "school_id": "1",
                "school_name": "测试大学",
                "province": "测试省",
                "level": "本科",
                "eligibility_hint": "recommended",
                "official_url": "https://example.edu.cn",
                "matched_link_text": "测试大学",
                "source_url": "https://source.example/list",
                "source_rank": "1",
            }
        ],
        [
            "school_id",
            "school_name",
            "province",
            "level",
            "eligibility_hint",
            "official_url",
            "matched_link_text",
            "source_url",
            "source_rank",
        ],
    )
    write_csv(
        input_dir / "search_results_recommendation_exemption_probe.csv",
        [
            {
                "search_query": '"测试大学" "推荐免试"',
                "result_rank": "1",
                "result_title": "测试大学研究生院",
                "result_url": "https://yz.example.edu.cn/a",
                "result_snippet": "公告",
                "provider": "bing-rss",
                "captured_at": "2026-06-14T00:00:00+08:00",
            }
        ],
        [
            "search_query",
            "result_rank",
            "result_title",
            "result_url",
            "result_snippet",
            "provider",
            "captured_at",
        ],
    )
    write_csv(
        input_dir / "official_site_recommendation_probe_seeds.csv",
        [
            {
                "school_name": "测试大学",
                "source_type": "recommendation_exemption",
                "start_url": "https://yz.example.edu.cn/a",
                "year": "2026",
                "document_type": "recommendation_exemption_list",
                "discovery_query": "official_site_link",
                "discovery_title": "推免名单",
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
        input_dir / "official_site_seeds_recommended_laosheng_1_5_candidate.failures.jsonl",
        [
            {
                "captured_at": "2026-06-14T00:00:00+08:00",
                "school_name": "测试大学",
                "url": "https://yz.example.edu.cn/a",
                "error": "HTTP 502",
                "error_type": "FetchError",
                "status_code": 502,
            }
        ],
    )

    manifest = build_graduate_source_discovery(
        input_dir=input_dir,
        output_dir=output_dir,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["graduate_discovery_tasks_2024_2026.csv"] == 1
    assert manifest["row_counts"]["graduate_search_results_probe_2026.csv"] == 1
    assert manifest["row_counts"]["graduate_official_site_seed_failures_2026.csv"] == 1
    school_summary = list(
        csv.DictReader(
            (output_dir / "graduate_discovery_school_summary_2026.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    assert school_summary[0]["has_official_url"] == "true"
