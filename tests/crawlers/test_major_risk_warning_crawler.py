from scripts.crawlers.major_risk_warning_crawler import curated_metric_rows, curated_rows


def test_curated_rows_use_fetchable_source_for_2024_undergrad_yellow():
    rows = [
        row
        for row in curated_rows()
        if row["report_year"] == 2024
        and row["education_level"] == "本科"
        and row["risk_level"] == "yellow"
    ]

    assert {row["reported_major_name"] for row in rows} == {
        "公共事业管理",
        "教育技术学",
        "生物技术",
        "汉语国际教育",
    }
    assert {row["source_ids"] for row in rows} == {"china_2025_undergrad_yellow"}
    assert {row["confidence"] for row in rows} == {"medium"}
    assert {row["evidence_type"] for row in rows} == {"explicit_list_secondary"}


def test_curated_metric_rows_include_2026_undergrad_quality_and_industry_metrics():
    rows = curated_metric_rows(None)
    keyed = {
        (
            row["report_year"],
            row["graduate_cohort"],
            row["education_level"],
            row["reported_major_name"],
            row["metric_name"],
        ): row
        for row in rows
    }

    assert keyed[
        (2026, 2025, "本科", "全国本科就业质量统计", "average_monthly_income")
    ]["metric_value"] == 6435
    assert keyed[
        (2026, 2025, "本科", "全国本科就业质量统计", "survey_sample_graduate_count")
    ]["metric_value"] == 195000
    assert keyed[
        (2026, 2025, "本科", "电子电气设备制造业", "employment_industry_share")
    ]["metric_value"] == 7.0
    assert keyed[
        (
            2026,
            2025,
            "本科",
            "机械设备制造业",
            "employment_industry_share_change_since_2021",
        )
    ]["metric_value"] == 1.6


def test_curated_metric_rows_include_2024_yellow_cumulative_counts():
    rows = curated_metric_rows(None)
    keyed = {
        (
            row["report_year"],
            row["education_level"],
            row["reported_major_name"],
            row["metric_name"],
        ): row
        for row in rows
    }

    assert keyed[
        (2024, "本科", "公共事业管理", "cumulative_yellow_warning_count_2010_2024")
    ]["metric_value"] == 6
    assert keyed[
        (2024, "本科", "生物技术", "cumulative_yellow_warning_count_2010_2024")
    ]["metric_value"] == 3
    assert keyed[
        (2024, "本科", "教育技术学", "cumulative_yellow_warning_count_2010_2024")
    ]["metric_value"] == 1
    assert keyed[
        (2024, "本科", "汉语国际教育", "cumulative_yellow_warning_count_2010_2024")
    ]["metric_value"] == 1
