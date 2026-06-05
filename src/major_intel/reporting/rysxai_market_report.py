"""Render readable reports from rysxai market snapshot JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def render_markdown_report(snapshot: dict[str, Any], top_n: int = 10) -> str:
    profession = snapshot.get("profession") or {}
    source = snapshot.get("source") or {}
    macro = snapshot.get("macro_employment") or {}
    name = profession.get("name") or "未知专业"
    code = profession.get("code") or "-"
    level = profession.get("level") or "-"

    lines = [
        f"# {name} 市场观察报告",
        "",
        "## 基本信息",
        "",
        f"- 专业代码：{code}",
        f"- 层次：{level}",
        f"- 抓取时间：{snapshot.get('captured_at', '-')}",
        f"- 来源：{source.get('name', '-')}",
        f"- 来源等级：{source.get('source_level', '-')}",
        f"- 数据口径：{source.get('data_scope', '-')}",
        f"- 岗位样本：接口声称 {snapshot.get('job_posting_sample_total_reported', '-')} 条，实际返回 {snapshot.get('job_posting_sample_count', '-')} 条",
        "",
        "## 行业分布",
        "",
        _table(
            ["行业", "占比"],
            [
                [row.get("label", "-"), _percent(row.get("rate_percent"))]
                for row in _first(macro.get("industry_distribution"), top_n)
            ],
        ),
        "",
        "## 地区分布",
        "",
        _table(
            ["地区", "占比"],
            [
                [row.get("label", "-"), _percent(row.get("rate_percent"))]
                for row in _first(macro.get("region_distribution"), top_n)
            ],
        ),
        "",
        "## 岗位方向",
        "",
        _table(
            ["方向", "占比", "岗位示例"],
            [
                [
                    row.get("label", "-"),
                    _percent(row.get("rate_percent")),
                    "、".join(_first(row.get("detail_jobs"), 5)),
                ]
                for row in _first(macro.get("job_direction_distribution"), top_n)
            ],
        ),
        "",
        "## 需求排行",
        "",
        _table(
            ["地区", "需求量"],
            [
                [row.get("region", "-"), row.get("demand_count", "-")]
                for row in _first(snapshot.get("demand_ranking"), top_n)
            ],
        ),
        "",
        "## 薪资排行",
        "",
        _table(
            ["地区", "月薪参考"],
            [
                [row.get("region", "-"), row.get("monthly_salary_reference", "-")]
                for row in _first(snapshot.get("salary_ranking"), top_n)
            ],
        ),
        "",
        "## 城市薪资样本聚合",
        "",
        _salary_city_table(snapshot.get("salary_observations_by_city") or {}, top_n),
        "",
        "## 招聘岗位样本",
        "",
        _table(
            ["岗位", "公司", "城市", "行业", "薪资", "学历", "经验"],
            [
                [
                    row.get("job_title", "-"),
                    row.get("company_name", "-"),
                    row.get("city", "-"),
                    row.get("industry", "-"),
                    row.get("salary_raw", "-"),
                    row.get("education", "-"),
                    row.get("experience", "-"),
                ]
                for row in _first(snapshot.get("job_posting_samples"), top_n)
            ],
        ),
        "",
        "## 口径提醒",
        "",
    ]

    warnings = snapshot.get("warnings") or []
    if warnings:
        lines.extend([f"- {_normalize_warning(warning)}" for warning in warnings])
    else:
        lines.append("- 招聘岗位和薪资样本只能作为专业市场观察，不能代表某校某专业毕业生实际薪资。")

    return "\n".join(lines).rstrip() + "\n"


def write_markdown_report(
    snapshot: dict[str, Any], output_path: Path, top_n: int = 10
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_markdown_report(snapshot, top_n=top_n),
        encoding="utf-8-sig",
    )


def load_snapshot(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a readable Markdown report from a rysxai market snapshot."
    )
    parser.add_argument("snapshot", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="Markdown output path. Defaults to reports/rysxai/{snapshot_stem}.md",
    )
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args(argv)

    output_path = args.output or Path("reports/rysxai") / f"{args.snapshot.stem}.md"
    write_markdown_report(load_snapshot(args.snapshot), output_path, top_n=args.top_n)
    print(output_path)
    return 0


def _salary_city_table(city_data: dict[str, Any], top_n: int) -> str:
    rows = []
    for city, values in _first(list(city_data.items()), top_n):
        rows.append(
            [
                city,
                values.get("sample_count", "-"),
                values.get("monthly_salary_min_observed", "-"),
                values.get("monthly_salary_max_observed", "-"),
                values.get("monthly_salary_midpoint_avg", "-"),
            ]
        )
    return _table(["城市", "样本数", "最低", "最高", "区间中位均值"], rows)


def _table(headers: list[Any], rows: list[list[Any]]) -> str:
    clean_headers = [_escape_cell(header) for header in headers]
    lines = [
        "| " + " | ".join(clean_headers) + " |",
        "| " + " | ".join(["---"] * len(clean_headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_escape_cell(cell) for cell in row) + " |")
    return "\n".join(lines)


def _escape_cell(value: Any) -> str:
    text = "-" if value is None or value == "" else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _percent(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.2f}%"


def _normalize_warning(value: Any) -> str:
    text = str(value)
    return text.replace("不代表某校某专业毕业生实际薪资", "不能代表某校某专业毕业生实际薪资")


def _first(value: Any, limit: int) -> list[Any]:
    if not isinstance(value, list):
        return []
    return value[:limit]


if __name__ == "__main__":
    raise SystemExit(main())
