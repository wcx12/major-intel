"""Build tier-adjusted major AI replacement risk datasets.

This module takes the independent major AI replacement ranking and expands it
to the three university tiers used by the remote university tier report.  It
does not require a school-major offering table: every major is evaluated under
each tier as an interpretive scenario.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATA_VERSION = "major_ai_replacement_by_university_tier/v1.0-20260614"
DEFAULT_MAJOR_RANKING = Path("data/processed/ai_replacement/major_ai_replacement_ranking.csv")
DEFAULT_TIER_FILE = Path(
    "reports/remote_db_university_tiers/remote_edu_university_three_tiers_20260614.csv"
)
DEFAULT_OUTPUT_DIR = Path("data/processed/ai_replacement")
DEFAULT_REPORT_DIR = Path("reports/ai_replacement")

TIER_ORDER = ["1", "2", "3"]
TIER_NAMES = {
    "1": "头部/强研究型高校",
    "2": "区域重点/特色优势高校",
    "3": "普通应用/职业供给高校",
}


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def risk_level(score: float) -> str:
    if score >= 75:
        return "很高"
    if score >= 65:
        return "较高"
    if score >= 50:
        return "中等"
    if score >= 35:
        return "较低"
    return "低"


def load_tier_counts(path: Path) -> dict[str, int]:
    counts: Counter[str] = Counter()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            tier = str(row.get("university_tier") or "").strip()
            if tier:
                counts[tier] += 1
    return {tier: counts.get(tier, 0) for tier in TIER_ORDER}


def load_major_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def infer_driver(row: dict[str, Any]) -> str:
    text = "；".join(
        [
            str(row.get("top_risky_jobs") or ""),
            str(row.get("main_reasons") or ""),
            str(row.get("major_name") or ""),
        ]
    )
    if any(token in text for token in ["编辑", "文案", "翻译", "秘书", "文员", "出版", "校对", "新媒体", "内容"]):
        return "文本/内容/文档型"
    if any(token in text for token in ["运营", "电商", "市场", "广告", "客服", "销售", "投放", "策划"]):
        return "运营/营销/客服型"
    if any(token in text for token in ["软件", "开发", "代码", "测试", "数据", "报表", "算法", "程序"]):
        return "代码/数据/报表型"
    if any(token in text for token in ["会计", "财务", "审计", "税务", "核算"]):
        return "财务/合规流程型"
    if any(token in text for token in ["医生", "医学", "护理", "护士", "药", "临床", "口腔"]):
        return "医学/照护/强资质型"
    if any(token in text for token in ["法学", "法律", "律师", "法务", "合同"]):
        return "法律/责任/强资质型"
    if any(token in text for token in ["维修", "设备", "操作", "施工", "机电", "航空", "物流", "仓储", "电气", "机械"]):
        return "线下工程/设备/执行型"
    if any(token in text for token in ["教师", "教学", "教育", "培训", "小学"]):
        return "教育/人际信任型"
    return "混合/待复核型"


def tier_adjustment(row: dict[str, Any], tier: str) -> tuple[float, str, str]:
    base = to_float(row.get("ai_replacement_score"))
    exposure = to_float(row.get("ai_exposure_score"))
    automation = to_float(row.get("automation_score"))
    barrier = to_float(row.get("human_barrier_score"))
    driver = infer_driver(row)

    exposure_pressure = max(0.0, exposure - 60.0) * 0.08
    automation_pressure = max(0.0, automation - 50.0) * 0.08
    low_barrier_pressure = max(0.0, 50.0 - barrier) * 0.07
    high_barrier_relief = max(0.0, barrier - 55.0) * 0.08

    if tier == "1":
        relief = 2.0 + exposure_pressure + automation_pressure
        if driver in {"文本/内容/文档型", "运营/营销/客服型", "代码/数据/报表型", "财务/合规流程型"}:
            relief += 2.2
        if driver in {"医学/照护/强资质型", "法律/责任/强资质型", "线下工程/设备/执行型", "教育/人际信任型"}:
            relief += 1.0
        adjustment = -min(9.5, relief)
        logic = "头部平台、升学/科研、高阶岗位和复杂责任会缓冲低阶任务替代风险"
        advice = "重点看能否进入研究、复杂工程、策略、平台治理、强责任岗位；低阶任务仍会被 AI 压缩"
    elif tier == "2":
        adjustment = 0.0
        if driver in {"文本/内容/文档型", "运营/营销/客服型", "财务/合规流程型"}:
            adjustment += min(2.0, low_barrier_pressure)
        if driver in {"医学/照护/强资质型", "法律/责任/强资质型", "线下工程/设备/执行型"}:
            adjustment -= min(2.0, high_barrier_relief)
        logic = "区域重点和特色资源能提供部分缓冲，但就业结构更接近专业市场基准"
        advice = "重点看区域行业资源、实习质量、证书资质、项目深度和岗位层级"
    else:
        pressure = 1.5 + exposure_pressure + automation_pressure + low_barrier_pressure
        if driver in {"文本/内容/文档型", "运营/营销/客服型", "代码/数据/报表型", "财务/合规流程型"}:
            pressure += 2.5
        if driver in {"医学/照护/强资质型", "法律/责任/强资质型", "线下工程/设备/执行型", "教育/人际信任型"}:
            pressure -= min(4.0, high_barrier_relief + 1.5)
        adjustment = max(-3.5, min(9.5, pressure))
        logic = "普通应用/职业供给路径更容易进入初级、执行、流程型岗位，低阶任务替代压力更直接"
        advice = "避免只获得模板化技能；应叠加行业场景、线下能力、客户转化、证书或 AI 工具链落地能力"

    adjusted = clamp(base + adjustment)
    return round(adjusted, 2), logic, advice


def build_long_rows(
    major_rows: list[dict[str, Any]],
    tier_counts: dict[str, int],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in major_rows:
        driver = infer_driver(row)
        for tier in TIER_ORDER:
            adjusted, logic, advice = tier_adjustment(row, tier)
            adjustment = round(adjusted - to_float(row.get("ai_replacement_score")), 2)
            rows.append(
                {
                    "data_version": DATA_VERSION,
                    "base_data_version": row.get("data_version", ""),
                    "base_rank": row.get("rank", ""),
                    "profession_id": row.get("profession_id", ""),
                    "major_code": row.get("major_code", ""),
                    "major_name": row.get("major_name", ""),
                    "level": row.get("level", ""),
                    "university_tier": tier,
                    "university_tier_name": TIER_NAMES[tier],
                    "tier_school_count": tier_counts.get(tier, 0),
                    "base_ai_replacement_score": row.get("ai_replacement_score", ""),
                    "base_ai_replacement_level": row.get("ai_replacement_level", ""),
                    "tier_adjusted_score": adjusted,
                    "tier_adjusted_level": risk_level(adjusted),
                    "tier_adjustment_points": adjustment,
                    "ai_exposure_score": row.get("ai_exposure_score", ""),
                    "automation_score": row.get("automation_score", ""),
                    "human_barrier_score": row.get("human_barrier_score", ""),
                    "ai_assist_value_score": row.get("ai_assist_value_score", ""),
                    "confidence_score": row.get("confidence_score", ""),
                    "risk_driver_type": driver,
                    "tier_adjustment_logic": logic,
                    "tier_specific_advice": advice,
                    "top_risky_jobs": row.get("top_risky_jobs", ""),
                    "top_resilient_jobs": row.get("top_resilient_jobs", ""),
                    "main_reasons": row.get("main_reasons", ""),
                    "source_level": row.get("source_level", ""),
                    "data_scope": row.get("data_scope", ""),
                    "warning": "院校层次调整是解释性场景，不代表某校某专业官方就业去向；需结合学校-专业开设和真实就业数据复核。",
                }
            )
    return rows


def build_wide_rows(long_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in long_rows:
        key = (row["profession_id"], row["major_code"], row["major_name"])
        if key not in grouped:
            grouped[key] = {
                "data_version": DATA_VERSION,
                "base_data_version": row["base_data_version"],
                "base_rank": row["base_rank"],
                "profession_id": row["profession_id"],
                "major_code": row["major_code"],
                "major_name": row["major_name"],
                "level": row["level"],
                "base_ai_replacement_score": row["base_ai_replacement_score"],
                "base_ai_replacement_level": row["base_ai_replacement_level"],
                "ai_exposure_score": row["ai_exposure_score"],
                "automation_score": row["automation_score"],
                "human_barrier_score": row["human_barrier_score"],
                "ai_assist_value_score": row["ai_assist_value_score"],
                "confidence_score": row["confidence_score"],
                "risk_driver_type": row["risk_driver_type"],
                "top_risky_jobs": row["top_risky_jobs"],
                "top_resilient_jobs": row["top_resilient_jobs"],
                "main_reasons": row["main_reasons"],
                "warning": row["warning"],
            }
        tier = row["university_tier"]
        prefix = f"tier{tier}"
        grouped[key][f"{prefix}_name"] = row["university_tier_name"]
        grouped[key][f"{prefix}_score"] = row["tier_adjusted_score"]
        grouped[key][f"{prefix}_level"] = row["tier_adjusted_level"]
        grouped[key][f"{prefix}_adjustment_points"] = row["tier_adjustment_points"]
        grouped[key][f"{prefix}_logic"] = row["tier_adjustment_logic"]
        grouped[key][f"{prefix}_advice"] = row["tier_specific_advice"]
    return sorted(grouped.values(), key=lambda row: int(row.get("base_rank") or 999999))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_report(path: Path, long_rows: list[dict[str, Any]], wide_rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter((row["university_tier"], row["tier_adjusted_level"]) for row in long_rows)
    lines = [
        "# 全专业三类院校层次 AI 可替代性数据集说明",
        "",
        f"生成日期：2026-06-14",
        f"数据版本：`{DATA_VERSION}`",
        "",
        "## 产物",
        "",
        "- `major_ai_replacement_by_university_tier.csv`: 长表，每个专业在 3 个院校层次下各一行。",
        "- `major_ai_replacement_by_university_tier_wide.csv`: 宽表，每个专业一行，同时包含 3 个层次的分数和解释。",
        "- `major_ai_replacement_by_university_tier.jsonl`: 长表 JSONL。",
        "",
        "## 覆盖",
        "",
        f"- 专业数：{len(wide_rows)}",
        f"- 长表行数：{len(long_rows)}",
        "- 院校层次：1 头部/强研究型高校；2 区域重点/特色优势高校；3 普通应用/职业供给高校。",
        "",
        "## 各层调整后风险等级分布",
        "",
        "| 院校层次 | 风险等级 | 专业数 |",
        "|---|---|---:|",
    ]
    for tier in TIER_ORDER:
        for level in ["很高", "较高", "中等", "较低", "低"]:
            lines.append(f"| {tier} {TIER_NAMES[tier]} | {level} | {counts.get((tier, level), 0)} |")
    lines.extend(
        [
            "",
            "## 调整逻辑",
            "",
            "- 第 1 层：对低阶岗位替代风险适度下调，因为头部高校更容易进入研究、平台、复杂工程、策略和强责任岗位。",
            "- 第 2 层：基本保留专业市场基准，只根据行业特色和资质/线下阻力做轻微修正。",
            "- 第 3 层：对文本、行政、运营、客服、基础代码、基础财务等初级执行岗位适度上调；对强线下、强资质、强责任专业不强行上调。",
            "",
            "## 使用边界",
            "",
            "- 这是“专业 × 院校层次”的解释性场景表，不是学校-专业真实开设表。",
            "- 输出不代表某校某专业官方就业去向。",
            "- 需要精确到学校时，还要接学校-专业开设、招生批次和官方就业数据。",
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_dataset(
    major_ranking_path: Path,
    tier_file_path: Path,
    output_dir: Path,
    report_dir: Path,
) -> dict[str, Any]:
    tier_counts = load_tier_counts(tier_file_path)
    major_rows = load_major_rows(major_ranking_path)
    long_rows = build_long_rows(major_rows, tier_counts)
    wide_rows = build_wide_rows(long_rows)

    long_path = output_dir / "major_ai_replacement_by_university_tier.csv"
    wide_path = output_dir / "major_ai_replacement_by_university_tier_wide.csv"
    jsonl_path = output_dir / "major_ai_replacement_by_university_tier.jsonl"
    report_path = report_dir / "major_ai_replacement_by_university_tier_all_20260614.md"
    manifest_path = output_dir / "major_ai_replacement_by_university_tier_manifest.json"

    write_csv(long_path, long_rows)
    write_csv(wide_path, wide_rows)
    write_jsonl(jsonl_path, long_rows)
    write_report(report_path, long_rows, wide_rows)

    manifest = {
        "data_version": DATA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "major_count": len(wide_rows),
        "long_row_count": len(long_rows),
        "tier_counts": tier_counts,
        "output_files": [
            str(long_path),
            str(wide_path),
            str(jsonl_path),
            str(report_path),
        ],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build all-major AI replacement risk tables adjusted by university tier."
    )
    parser.add_argument("--major-ranking", type=Path, default=DEFAULT_MAJOR_RANKING)
    parser.add_argument("--tier-file", type=Path, default=DEFAULT_TIER_FILE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args(argv)

    manifest = build_dataset(args.major_ranking, args.tier_file, args.output_dir, args.report_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
