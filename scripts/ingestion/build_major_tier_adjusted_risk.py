"""Build major risk labels adjusted by university tier.

The dataset uses the remote-test `edu_major` export as the major universe and
joins the local risk-signal profiles built in earlier crawls. It deliberately
keeps the rule set transparent: a base major risk score is computed first, then
three university-tier variants are emitted with tier-specific adjustments.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REMOTE_MAJOR_PATH = ROOT / "reports/remote_db_current_majors/remote_edu_major_majors_20260614.csv"
DEFAULT_NEW_QUALITY_PATH = ROOT / "data/processed/new_quality_major_profiles/new_quality_major_profiles_2026.csv"
DEFAULT_MASTER_INDEX_PATH = ROOT / "data/processed/major_risk_master_index/major_risk_master_index_2026.csv"
DEFAULT_UNIVERSITY_TIER_PATH = ROOT / "reports/remote_db_university_tiers/remote_edu_university_three_tiers_20260614.csv"
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/major_tier_adjusted_risk"
DEFAULT_REPORT_DIR = ROOT / "reports/major_tier_adjusted_risk"

BASE_FIELDS = [
    "major_risk_id",
    "major_special_id",
    "major_code",
    "major_name",
    "major_type",
    "major_level",
    "major_level2",
    "major_level3",
    "base_risk_score",
    "base_risk_level",
    "base_risk_label",
    "base_risk_reasons",
    "positive_reasons",
    "employment_warning_count",
    "employment_red_count",
    "employment_yellow_count",
    "employment_green_count",
    "employment_latest_risk_level",
    "employment_warning_years",
    "official_policy_warning_count",
    "overall_review_bucket",
    "primary_risk_reasons",
    "primary_opportunity_reasons",
    "ai_replacement_score",
    "ai_replacement_level",
    "market_demand_count_national",
    "market_demand_signal_level",
    "market_salary_signal_level",
    "civil_service_opportunity_level",
    "new_quality_support_category",
    "is_new_quality_productivity_major",
    "new_quality_directions",
    "opportunity_risk_balance",
    "source_level",
    "data_scope",
]

ADJUSTED_FIELDS = [
    "major_tier_risk_id",
    "major_risk_id",
    "major_special_id",
    "major_code",
    "major_name",
    "major_type",
    "major_level",
    "university_tier",
    "university_tier_name",
    "university_tier_school_count",
    "is_applicable",
    "applicability_note",
    "base_risk_score",
    "base_risk_level",
    "base_risk_label",
    "tier_score_modifier",
    "tier_adjusted_risk_score",
    "tier_adjusted_risk_level",
    "tier_adjusted_risk_label",
    "tier_adjustment_reason",
    "base_risk_reasons",
    "positive_reasons",
    "evidence_source_fields",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def as_int(value: Any) -> int | None:
    text = str(value or "").strip()
    if not text or text.upper() == "NULL":
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def as_float(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text or text.upper() == "NULL":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def yes(value: Any) -> bool:
    return str(value or "").strip() in {"1", "true", "True", "是", "Y", "yes"}


def major_level_from_type(major_type: str) -> str:
    if "专科" in major_type or "高职" in major_type:
        return "专科"
    return "本科"


def readable_major_type(row: dict[str, str]) -> str:
    special_type = row.get("special_type", "").strip()
    type_name = row.get("type_name", "").strip()
    if special_type in {"1", "2"} and type_name:
        return type_name
    return special_type or type_name


def stable_hash(*parts: Any, length: int = 16) -> str:
    payload = "|".join(str(part or "") for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def risk_label(score: int) -> tuple[str, str]:
    if score >= 70:
        return "high_risk", "高危"
    if score >= 45:
        return "watch", "风险观察"
    if score >= 25:
        return "neutral", "中性/需结合学校"
    return "opportunity", "相对稳健/机会型"


def clamp_score(value: float | int) -> int:
    return max(0, min(100, int(round(value))))


def build_master_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    lookup: dict[tuple[str, str, str], dict[str, str]] = {}
    fallback_by_code_name: dict[tuple[str, str], dict[str, str]] = {}
    fallback_by_name_level: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        code = row.get("major_code", "").strip()
        name = row.get("major_name", "").strip()
        level = row.get("major_level", "").strip()
        if code or name:
            lookup.setdefault((code, name, level), row)
            fallback_by_code_name.setdefault((code, name), row)
            fallback_by_name_level.setdefault((name, level), row)
    for key, row in fallback_by_code_name.items():
        lookup.setdefault((key[0], key[1], ""), row)
    for key, row in fallback_by_name_level.items():
        lookup.setdefault(("", key[0], key[1]), row)
    return lookup


def find_master_row(
    lookup: dict[tuple[str, str, str], dict[str, str]],
    code: str,
    name: str,
    level: str,
) -> dict[str, str]:
    return (
        lookup.get((code, name, level))
        or lookup.get((code, name, ""))
        or lookup.get(("", name, level))
        or {}
    )


def compute_base_risk(profile: dict[str, str], master: dict[str, str]) -> dict[str, Any]:
    score = 20
    risk_reasons: list[str] = []
    positive_reasons: list[str] = []

    red_count = as_int(profile.get("employment_risk_levels", "").count("red")) or 0
    yellow_count = as_int(profile.get("employment_risk_levels", "").count("yellow")) or 0
    employment_warning_count = as_int(profile.get("employment_warning_count")) or 0
    if yes(profile.get("has_employment_red_warning")):
        red_count = max(red_count, 1)
    if yes(profile.get("has_employment_yellow_warning")):
        yellow_count = max(yellow_count, 1)
    if yes(profile.get("has_employment_red_warning")):
        score += min(45, 30 + red_count * 5)
        risk_reasons.append(f"就业红牌信号（红牌次数约{red_count}）")
    elif yes(profile.get("has_employment_yellow_warning")):
        score += min(30, 18 + yellow_count * 4)
        risk_reasons.append(f"就业黄牌信号（黄牌次数约{yellow_count}）")
    elif employment_warning_count:
        score += min(18, employment_warning_count * 4)
        risk_reasons.append(f"历史就业预警记录{employment_warning_count}条")

    if yes(profile.get("has_employment_green_signal")):
        score -= 12
        positive_reasons.append("有就业绿牌/稳健就业信号")

    official_policy_count = as_int(profile.get("official_policy_warning_count")) or 0
    if official_policy_count >= 20:
        score += 26
        risk_reasons.append(f"官方停招/撤销/预警记录较多（{official_policy_count}条）")
    elif official_policy_count >= 5:
        score += 18
        risk_reasons.append(f"存在多条官方专业设置风险记录（{official_policy_count}条）")
    elif official_policy_count > 0:
        score += 10
        risk_reasons.append(f"存在官方专业设置风险记录（{official_policy_count}条）")

    bucket = master.get("overall_review_bucket", "")
    if bucket == "high_risk_review":
        score += 18
        risk_reasons.append("master index 标记为 high_risk_review")
    elif bucket == "employment_or_policy_warning_review":
        score += 12
        risk_reasons.append("master index 标记为就业/政策预警复核")
    elif bucket in {"multi_signal_risk_review", "ai_market_risk_review"}:
        score += 10
        risk_reasons.append(f"master index 多信号风险桶：{bucket}")
    elif bucket == "opportunity_with_risk_flags":
        score += 5
        risk_reasons.append("机会信号同时带风险标记")

    ai_score = as_float(profile.get("ai_replacement_score"))
    ai_level = profile.get("ai_replacement_level", "").strip()
    if ai_level in {"较高", "高"} or (ai_score is not None and ai_score >= 65):
        score += 12
        risk_reasons.append(f"AI替代风险偏高（{ai_level or ai_score}）")
    elif ai_level == "中等" or (ai_score is not None and ai_score >= 55):
        score += 6
        risk_reasons.append(f"AI替代风险中等（{ai_level or ai_score}）")
    elif ai_level in {"低", "较低"}:
        score -= 2
        positive_reasons.append(f"AI替代风险较低（{ai_level}）")

    demand_level = profile.get("market_demand_signal_level", "").strip()
    if demand_level == "limited":
        score += 12
        risk_reasons.append("招聘市场需求信号有限")
    elif demand_level == "medium":
        positive_reasons.append("招聘市场需求中等")
    elif demand_level == "high":
        score -= 6
        positive_reasons.append("招聘市场需求较强")
    elif demand_level == "very_high":
        score -= 10
        positive_reasons.append("招聘市场需求很强")

    salary_level = profile.get("market_salary_signal_level", "").strip()
    if salary_level == "limited":
        score += 5
        risk_reasons.append("薪资信号偏弱")
    elif salary_level == "high":
        score -= 3
        positive_reasons.append("薪资信号较强")

    civil_level = profile.get("civil_service_opportunity_level", "").strip()
    if civil_level == "limited":
        score += 4
        risk_reasons.append("公职/编制岗位匹配较弱")
    elif civil_level in {"medium", "high"}:
        score -= 3
        positive_reasons.append(f"公职岗位匹配{civil_level}")

    support_category = profile.get("support_category", "").strip()
    if support_category == "core":
        score -= 18
        positive_reasons.append("新质生产力核心方向")
    elif support_category == "related":
        score -= 10
        positive_reasons.append("新质生产力相关方向")
    elif support_category == "weak_related":
        score -= 4
        positive_reasons.append("新质生产力弱相关方向")

    if profile.get("opportunity_risk_balance", "").strip() == "opportunity_dominant":
        score -= 5
        positive_reasons.append("机会信号强于风险信号")
    elif profile.get("opportunity_risk_balance", "").strip() == "risk_dominant":
        score += 5
        risk_reasons.append("风险信号强于机会信号")

    score = clamp_score(score)
    level, label = risk_label(score)
    if not risk_reasons:
        risk_reasons.append("未命中红黄牌、官方专业设置风险、AI/市场弱信号等高危条件")
    if not positive_reasons:
        positive_reasons.append("暂无明确机会型抵消信号")
    return {
        "base_risk_score": score,
        "base_risk_level": level,
        "base_risk_label": label,
        "base_risk_reasons": "；".join(risk_reasons),
        "positive_reasons": "；".join(positive_reasons),
    }


def tier_adjustment(base: dict[str, Any], tier: dict[str, Any], major_level: str) -> dict[str, Any]:
    tier_id = str(tier["university_tier"])
    modifier = 0
    reasons: list[str] = []
    is_applicable = "true"
    applicability_note = "适用"

    base_reasons = str(base.get("base_risk_reasons", ""))
    has_hard_warning = any(token in base_reasons for token in ["红牌", "黄牌", "官方停招", "官方专业设置风险", "high_risk_review"])

    if tier_id == "1":
        if major_level == "专科":
            is_applicable = "false"
            applicability_note = "第1层主要为头部本科/强研究型高校；专科/高职专业在该层级通常不适用，仅保留参照评分。"
            modifier = 0
            reasons.append("专科专业与第1层头部本科场景不完全匹配，未做品牌缓冲下调")
        else:
            modifier = -15
            reasons.append("头部/强研究型高校的品牌、升学和平台资源可缓冲就业风险")
            if has_hard_warning:
                modifier += 5
                reasons.append("但存在红黄牌或官方风险信号，缓冲幅度收窄")
    elif tier_id == "2":
        if major_level == "专科":
            modifier = -6
            reasons.append("第2层含双高/示范/骨干高职，优质职业院校能部分缓冲专业风险")
        else:
            modifier = -3
            reasons.append("区域重点/特色优势高校可通过学科特色和区域产业匹配小幅缓冲风险")
    else:
        modifier = 12
        reasons.append("普通应用/职业供给高校中，品牌、升学和平台缓冲较弱，专业风险会被放大")
        if has_hard_warning:
            modifier += 8
            reasons.append("红黄牌或官方风险信号在第3层院校中需要额外上调风险")

    adjusted_score = clamp_score(int(base["base_risk_score"]) + modifier)
    adjusted_level, adjusted_label = risk_label(adjusted_score)
    return {
        "tier_score_modifier": modifier,
        "tier_adjusted_risk_score": adjusted_score,
        "tier_adjusted_risk_level": adjusted_level,
        "tier_adjusted_risk_label": adjusted_label,
        "tier_adjustment_reason": "；".join(reasons),
        "is_applicable": is_applicable,
        "applicability_note": applicability_note,
    }


def build_dataset(
    remote_major_path: Path,
    new_quality_path: Path,
    master_index_path: Path,
    university_tier_path: Path,
    output_dir: Path,
    report_dir: Path,
    generated_at: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    remote_majors = read_csv(remote_major_path)
    profiles = read_csv(new_quality_path)
    profile_by_special_id = {row.get("major_special_id", ""): row for row in profiles}
    profile_by_code_name = {(row.get("major_code", ""), row.get("major_name", "")): row for row in profiles}
    master_lookup = build_master_lookup(read_csv(master_index_path))

    tier_rows = read_csv(university_tier_path)
    tier_summary = Counter((row["university_tier"], row["university_tier_name"]) for row in tier_rows)
    tiers = [
        {"university_tier": "1", "university_tier_name": "头部/强研究型高校"},
        {"university_tier": "2", "university_tier_name": "区域重点/特色优势高校"},
        {"university_tier": "3", "university_tier_name": "普通应用/职业供给高校"},
    ]
    for tier in tiers:
        tier["school_count"] = tier_summary.get((tier["university_tier"], tier["university_tier_name"]), 0)

    base_rows: list[dict[str, Any]] = []
    adjusted_rows: list[dict[str, Any]] = []
    missing_profile_count = 0

    for major in remote_majors:
        special_id = major.get("special_id", "")
        code = major.get("code", "")
        name = major.get("special_name", "")
        major_type = readable_major_type(major)
        profile = profile_by_special_id.get(special_id) or profile_by_code_name.get((code, name)) or {}
        if not profile:
            missing_profile_count += 1
            profile = {
                "major_special_id": special_id,
                "major_code": code,
                "major_name": name,
                "major_type": major_type,
                "major_level2": major.get("level2_name", ""),
                "major_level3": major.get("level3_name", ""),
            }
        level = major_level_from_type(major_type or profile.get("major_type", ""))
        master = find_master_row(master_lookup, code, name, level)
        base = compute_base_risk(profile, master)
        major_risk_id = stable_hash(special_id, code, name, "base")
        base_row = {
            "major_risk_id": major_risk_id,
            "major_special_id": special_id,
            "major_code": code,
            "major_name": name,
            "major_type": major_type,
            "major_level": level,
            "major_level2": major.get("level2_name") or profile.get("major_level2", ""),
            "major_level3": major.get("level3_name") or profile.get("major_level3", ""),
            **base,
            "employment_warning_count": profile.get("employment_warning_count", ""),
            "employment_red_count": str(max(1 if yes(profile.get("has_employment_red_warning")) else 0, profile.get("employment_risk_levels", "").count("red"))),
            "employment_yellow_count": str(max(1 if yes(profile.get("has_employment_yellow_warning")) else 0, profile.get("employment_risk_levels", "").count("yellow"))),
            "employment_green_count": "1" if yes(profile.get("has_employment_green_signal")) else "0",
            "employment_latest_risk_level": master.get("employment_latest_risk_level", ""),
            "employment_warning_years": profile.get("employment_warning_years", ""),
            "official_policy_warning_count": profile.get("official_policy_warning_count", ""),
            "overall_review_bucket": master.get("overall_review_bucket", ""),
            "primary_risk_reasons": master.get("primary_risk_reasons", ""),
            "primary_opportunity_reasons": master.get("primary_opportunity_reasons", ""),
            "ai_replacement_score": profile.get("ai_replacement_score", ""),
            "ai_replacement_level": profile.get("ai_replacement_level", ""),
            "market_demand_count_national": profile.get("market_demand_count_national", ""),
            "market_demand_signal_level": profile.get("market_demand_signal_level", ""),
            "market_salary_signal_level": profile.get("market_salary_signal_level", ""),
            "civil_service_opportunity_level": profile.get("civil_service_opportunity_level", ""),
            "new_quality_support_category": profile.get("support_category", ""),
            "is_new_quality_productivity_major": profile.get("is_new_quality_productivity_major", ""),
            "new_quality_directions": profile.get("directions", ""),
            "opportunity_risk_balance": profile.get("opportunity_risk_balance", ""),
            "source_level": profile.get("source_level", ""),
            "data_scope": profile.get("data_scope", ""),
        }
        base_rows.append(base_row)
        for tier in tiers:
            adjustment = tier_adjustment(base_row, tier, level)
            adjusted_rows.append(
                {
                    "major_tier_risk_id": stable_hash(major_risk_id, tier["university_tier"]),
                    "major_risk_id": major_risk_id,
                    "major_special_id": special_id,
                    "major_code": code,
                    "major_name": name,
                    "major_type": major_type,
                    "major_level": level,
                    "university_tier": tier["university_tier"],
                    "university_tier_name": tier["university_tier_name"],
                    "university_tier_school_count": tier["school_count"],
                    **adjustment,
                    "base_risk_score": base_row["base_risk_score"],
                    "base_risk_level": base_row["base_risk_level"],
                    "base_risk_label": base_row["base_risk_label"],
                    "base_risk_reasons": base_row["base_risk_reasons"],
                    "positive_reasons": base_row["positive_reasons"],
                    "evidence_source_fields": "major_risk_warnings;official_policy_warnings;ai_replacement;rysxai_market;new_quality_profiles;civil_service",
                }
            )

    summary_rows: list[dict[str, Any]] = []
    for (tier, tier_name, risk_level, risk_label), count in sorted(
        Counter(
            (
                row["university_tier"],
                row["university_tier_name"],
                row["tier_adjusted_risk_level"],
                row["tier_adjusted_risk_label"],
            )
            for row in adjusted_rows
        ).items()
    ):
        summary_rows.append(
            {
                "university_tier": tier,
                "university_tier_name": tier_name,
                "risk_level": risk_level,
                "risk_label": risk_label,
                "major_count": count,
            }
        )

    base_path = output_dir / "major_base_risk_2026.csv"
    adjusted_path = output_dir / "major_tier_adjusted_risk_2026.csv"
    summary_path = output_dir / "major_tier_adjusted_risk_summary_2026.csv"
    manifest_path = output_dir / "major_tier_adjusted_risk_manifest_2026.json"
    report_path = report_dir / "major_tier_adjusted_risk_2026.md"

    write_csv(base_path, base_rows, BASE_FIELDS)
    write_csv(adjusted_path, adjusted_rows, ADJUSTED_FIELDS)
    write_csv(summary_path, summary_rows, ["university_tier", "university_tier_name", "risk_level", "risk_label", "major_count"])

    manifest = {
        "dataset": "major_tier_adjusted_risk",
        "generated_at": generated_at,
        "source_tables": {
            "remote_major_export": str(remote_major_path.relative_to(ROOT)),
            "new_quality_profiles": str(new_quality_path.relative_to(ROOT)),
            "major_risk_master_index": str(master_index_path.relative_to(ROOT)),
            "university_tiers": str(university_tier_path.relative_to(ROOT)),
        },
        "row_counts": {
            "base_risk": len(base_rows),
            "tier_adjusted_risk": len(adjusted_rows),
            "summary": len(summary_rows),
            "missing_profile_count": missing_profile_count,
        },
        "risk_level_thresholds": {
            "high_risk": "score >= 70",
            "watch": "45 <= score < 70",
            "neutral": "25 <= score < 45",
            "opportunity": "score < 25",
        },
        "outputs": {
            "base_risk": str(base_path.relative_to(ROOT)),
            "tier_adjusted_risk": str(adjusted_path.relative_to(ROOT)),
            "summary": str(summary_path.relative_to(ROOT)),
            "report": str(report_path.relative_to(ROOT)),
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Major Risk Adjusted by University Tier",
        "",
        f"Generated at: {generated_at}",
        "",
        "## Rule Summary",
        "",
        "- Base score starts at 20 and increases for employment red/yellow warnings, official stop-enrollment/cancellation/policy warnings, high-risk master-index buckets, AI replacement exposure, limited hiring demand, weak salary signals, and weak civil-service opportunity.",
        "- Base score decreases for green-list employment signals, strong market demand, high salary signals, new-quality-productivity support, and opportunity-dominant evidence.",
        "- Tier 1 lowers undergraduate risk because head/strong-research universities have stronger brand, graduate-school, and platform buffers; hard red/yellow or official risk signals reduce that buffer.",
        "- Tier 2 gives a small buffer for regional key/featured universities and quality vocational colleges.",
        "- Tier 3 increases risk because ordinary applied/vocational supply contexts have weaker brand, platform, and pathway buffers.",
        "",
        "## Row Counts",
        "",
        f"- Base major rows: {len(base_rows)}",
        f"- Major x university tier rows: {len(adjusted_rows)}",
        f"- Missing joined risk profiles: {missing_profile_count}",
        "",
        "## Adjusted Risk Counts",
        "",
        "| University tier | Risk label | Major count |",
        "|---|---|---:|",
    ]
    for row in summary_rows:
        lines.append(f"| {row['university_tier']} {row['university_tier_name']} | {row['risk_label']} | {row['major_count']} |")
    lines.extend(["", "## Example Majors", ""])
    examples = ["法学", "公共事业管理", "生物技术", "教育技术学", "微电子科学与工程", "电气工程及其自动化", "新能源汽车技术", "法律事务"]
    for example in examples:
        sample = [row for row in adjusted_rows if row["major_name"] == example]
        if not sample:
            continue
        lines.append(f"### {example}")
        lines.append("")
        for row in sample:
            if row["university_tier"] not in {"1", "2", "3"}:
                continue
            lines.append(
                f"- Tier {row['university_tier']} {row['university_tier_name']}: "
                f"{row['tier_adjusted_risk_label']} ({row['tier_adjusted_risk_score']}); "
                f"{row['tier_adjustment_reason']}"
            )
        lines.append("")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "dataset": "major_tier_adjusted_risk",
        "generated_at": generated_at,
        "row_counts": manifest["row_counts"],
        "base_risk_counts": dict(Counter(row["base_risk_label"] for row in base_rows)),
        "tier_adjusted_counts": {
            f"{key[0]}:{key[1]}": count
            for key, count in Counter((row["university_tier"], row["tier_adjusted_risk_label"]) for row in adjusted_rows).items()
        },
        "outputs": manifest["outputs"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote-major-path", type=Path, default=DEFAULT_REMOTE_MAJOR_PATH)
    parser.add_argument("--new-quality-path", type=Path, default=DEFAULT_NEW_QUALITY_PATH)
    parser.add_argument("--master-index-path", type=Path, default=DEFAULT_MASTER_INDEX_PATH)
    parser.add_argument("--university-tier-path", type=Path, default=DEFAULT_UNIVERSITY_TIER_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--generated-at", default=datetime.now(timezone.utc).astimezone().date().isoformat())
    args = parser.parse_args(argv)
    result = build_dataset(
        args.remote_major_path,
        args.new_quality_path,
        args.master_index_path,
        args.university_tier_path,
        args.output_dir,
        args.report_dir,
        args.generated_at,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
