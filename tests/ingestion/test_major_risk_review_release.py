import csv
import json
from pathlib import Path

from scripts.ingestion import build_major_risk_review_release as release_module


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_build_major_risk_review_release_shortlists_and_indexes_sources(tmp_path, monkeypatch):
    master = tmp_path / "master.csv"
    evidence_summary = tmp_path / "summary.csv"
    evidence = tmp_path / "evidence.csv"
    archive = tmp_path / "archive.csv"
    output_dir = tmp_path / "out"
    report_dir = tmp_path / "report"

    master_fields = [
        "major_master_id",
        "major_code",
        "major_name",
        "major_level",
        "category",
        "subject",
        "overall_review_bucket",
        "risk_signal_count",
        "opportunity_signal_count",
        "primary_risk_reasons",
        "primary_opportunity_reasons",
        "employment_warning_count",
        "employment_red_count",
        "employment_yellow_count",
        "employment_latest_risk_level",
        "employment_latest_report_year",
        "official_policy_warning_count",
        "official_policy_record_types",
        "official_policy_years",
        "ai_replacement_score",
        "ai_replacement_level",
        "market_demand_signal_level",
        "market_salary_signal_level",
        "market_activity_signal_level",
        "civil_service_opportunity_level",
        "new_quality_support_category",
        "is_new_quality_productivity_major",
        "source_presence_flags",
        "source_level_mix",
        "needs_review",
        "review_notes",
    ]
    write_csv(
        master,
        [
            {
                "major_master_id": "m1",
                "major_code": "050201",
                "major_name": "英语",
                "major_level": "本科",
                "category": "文学",
                "subject": "外国语言文学类",
                "overall_review_bucket": "high_risk_review",
                "risk_signal_count": "3",
                "opportunity_signal_count": "1",
                "primary_risk_reasons": "employment_red_or_yellow_warning|official_policy_setting_warning",
                "employment_warning_count": "2",
                "employment_red_count": "1",
                "employment_yellow_count": "1",
                "employment_latest_risk_level": "red",
                "employment_latest_report_year": "2025",
                "official_policy_warning_count": "4",
                "official_policy_record_types": "major_cancel",
                "official_policy_years": "2024|2025",
                "ai_replacement_score": "63",
                "ai_replacement_level": "较高",
                "market_demand_signal_level": "limited",
                "market_salary_signal_level": "medium",
                "market_activity_signal_level": "limited",
                "civil_service_opportunity_level": "limited",
                "source_presence_flags": "employment_warning|official_policy_warning|ai_replacement",
                "source_level_mix": "A|B|C",
                "needs_review": "false",
            },
            {
                "major_master_id": "m2",
                "major_code": "080901",
                "major_name": "计算机科学与技术",
                "major_level": "本科",
                "overall_review_bucket": "baseline_reference",
                "risk_signal_count": "0",
                "opportunity_signal_count": "1",
            },
        ],
        master_fields,
    )
    summary_fields = [
        "major_master_id",
        "evidence_record_count",
        "risk_evidence_count",
        "opportunity_evidence_count",
        "source_url_count",
        "source_title_sample",
        "source_url_sample",
    ]
    write_csv(
        evidence_summary,
        [
            {
                "major_master_id": "m1",
                "evidence_record_count": "4",
                "risk_evidence_count": "3",
                "opportunity_evidence_count": "1",
                "source_url_count": "2",
                "source_title_sample": "来源A|来源B",
                "source_url_sample": "https://example.test/a|https://example.test/b",
            }
        ],
        summary_fields,
    )
    evidence_fields = [
        "evidence_id",
        "major_master_id",
        "major_code",
        "major_name",
        "major_level",
        "overall_review_bucket",
        "evidence_family",
        "signal_direction",
        "source_level",
        "source_table",
        "source_record_id",
        "source_ids",
        "source_titles",
        "source_urls",
        "source_publishers",
        "source_paths",
        "evidence_text",
    ]
    write_csv(
        evidence,
        [
            {
                "evidence_id": "e1",
                "major_master_id": "m1",
                "major_code": "050201",
                "major_name": "英语",
                "major_level": "本科",
                "overall_review_bucket": "high_risk_review",
                "evidence_family": "employment_warning",
                "signal_direction": "risk",
                "source_level": "B",
                "source_table": "warning.csv",
                "source_record_id": "r1",
                "source_ids": "src1",
                "source_titles": "来源A",
                "source_urls": "https://example.test/a",
                "source_publishers": "pub",
                "source_paths": "data/raw/test_source.html",
                "evidence_text": "红牌证据",
            },
            {
                "evidence_id": "e2",
                "major_master_id": "m1",
                "major_code": "050201",
                "major_name": "英语",
                "major_level": "本科",
                "overall_review_bucket": "high_risk_review",
                "evidence_family": "ai_replacement",
                "signal_direction": "risk",
                "source_level": "C",
                "source_table": "ai.csv",
                "source_record_id": "ai1",
                "source_ids": "",
                "source_titles": "",
                "source_urls": "",
                "source_publishers": "",
                "source_paths": "",
                "evidence_text": "AI证据",
            },
            {
                "evidence_id": "e3",
                "major_master_id": "m1",
                "major_code": "050201",
                "major_name": "英语",
                "major_level": "本科",
                "overall_review_bucket": "high_risk_review",
                "evidence_family": "market_observation",
                "signal_direction": "risk",
                "source_level": "C",
                "source_table": "market.csv",
                "source_record_id": "mkt1",
                "source_ids": "",
                "source_titles": "详情API|岗位API",
                "source_urls": "https://example.test/info|https://example.test/jobs",
                "source_publishers": "pub|pub",
                "source_paths": "data/raw/info.json|data/raw/jobs.json",
                "evidence_text": "市场证据",
            },
            {
                "evidence_id": "e3b",
                "major_master_id": "m1",
                "major_code": "050201",
                "major_name": "鑻辫",
                "major_level": "鏈",
                "overall_review_bucket": "high_risk_review",
                "evidence_family": "ai_replacement",
                "signal_direction": "risk",
                "source_level": "C",
                "source_table": "major_ai_replacement_ranking.csv",
                "source_record_id": "ai2",
                "source_ids": "",
                "source_titles": "",
                "source_urls": "",
                "source_publishers": "",
                "source_paths": "",
                "evidence_text": "AI profile evidence",
            },
            {
                "evidence_id": "e4",
                "major_master_id": "m1",
                "major_code": "050201",
                "major_name": "英语",
                "major_level": "本科",
                "overall_review_bucket": "high_risk_review",
                "evidence_family": "official_policy_warning",
                "signal_direction": "risk",
                "source_level": "A",
                "source_table": "policy.csv",
                "source_record_id": "p1",
                "source_ids": "",
                "source_titles": "归档来源",
                "source_urls": "https://example.test/archive",
                "source_publishers": "pub",
                "source_paths": "",
                "evidence_text": "归档证据",
            },
        ],
        evidence_fields,
    )
    write_csv(
        archive,
        [
            {
                "source_url": "https://example.test/archive",
                "crawl_status": "ok",
                "raw_path": "data/raw/archive.html",
                "text_path": "data/raw/archive.txt",
            }
        ],
        ["source_url", "crawl_status", "raw_path", "text_path"],
    )

    # The real AI replacement profile is a large generated asset stored in
    # Release data, not in Git. Patch the path check so this unit test keeps
    # exercising the "available local profile" branch without requiring that
    # ignored data directory to exist in a clean checkout.
    def fake_local_path_exists(path: str) -> bool:
        return path == "data/processed/ai_replacement/major_ai_replacement_ranking.csv"

    monkeypatch.setitem(
        release_module.build_major_risk_review_release.__globals__,
        "local_path_exists",
        fake_local_path_exists,
    )

    manifest = release_module.build_major_risk_review_release(
        master_index_csv=master,
        evidence_major_summary_csv=evidence_summary,
        evidence_records_csv=evidence,
        source_archive_csv=archive,
        output_dir=output_dir,
        report_dir=report_dir,
        generated_at="2026-06-14",
    )

    shortlist = read_rows(output_dir / "major_risk_high_risk_shortlist_2026.csv")
    sources = read_rows(output_dir / "major_risk_source_document_index_2026.csv")
    manifest_data = json.loads(
        (output_dir / "major_risk_review_release_manifest_2026.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["row_counts"]["shortlist"] == 1
    assert shortlist[0]["major_code"] == "050201"
    assert shortlist[0]["review_tier"] == "tier_1_high_risk_review"
    assert float(shortlist[0]["review_priority_score"]) > 0
    assert "verify_official_policy_rows" in shortlist[0]["recommended_review_action"]
    assert {row["source_kind"] for row in sources} == {"url", "local_profile"}
    url_row = next(row for row in sources if row["source_kind"] == "url")
    assert url_row["source_path"] == "data/raw/test_source.html"
    assert url_row["source_path_status"] == "all_paths_missing"
    paired_url = next(row for row in sources if row["source_url"] == "https://example.test/jobs")
    assert paired_url["source_path"] == "data/raw/jobs.json"
    archived_url = next(row for row in sources if row["source_url"] == "https://example.test/archive")
    assert archived_url["source_path"] == "data/raw/archive.html|data/raw/archive.txt"
    profile_row = next(
        row for row in sources if row["source_title"] == "major_ai_replacement_ranking.csv"
    )
    assert profile_row["source_path"] == "data/processed/ai_replacement/major_ai_replacement_ranking.csv"
    assert profile_row["source_path_status"] == "all_paths_available"
    assert "local_path" not in {row["source_kind"] for row in sources}
    assert manifest_data["source_kind_counts"]["url"] == 4
    assert manifest_data["source_archive"]["url_count"] == 1
    assert manifest_data["source_path_status_counts"]["all_paths_missing"] == 5
    assert manifest_data["source_path_status_counts"]["all_paths_available"] == 1
    assert (report_dir / "major_risk_review_release_2026.md").exists()
