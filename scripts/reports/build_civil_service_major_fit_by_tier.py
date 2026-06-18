"""Build major-level civil-service fit analysis by university tier.

Inputs are the remote education major catalog, the three-tier university table,
and the derived 2026 rysxai civil-service role-major match tables.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MAJORS_PATH = ROOT / "reports/remote_db_current_majors/remote_edu_major_majors_20260614.csv"
UNIVERSITY_TIERS_PATH = (
    ROOT
    / "reports/remote_db_university_tiers/remote_edu_university_three_tiers_20260614.csv"
)
OPPORTUNITIES_PATH = (
    ROOT
    / "data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv"
)
MATCHES_PATH = (
    ROOT
    / "data/processed/rysxai_civil_service/civil_service_role_major_matches_2026.csv"
)
OUTPUT_CSV = ROOT / "reports/rysxai_civil_service/major_civil_service_fit_20260614.csv"
OUTPUT_MD = (
    ROOT
    / "reports/rysxai_civil_service/major_civil_service_fit_by_university_tier_20260614.md"
)

UNDERGRAD_EDU = {"本科及以上", "仅限本科", "本科或硕士研究生"}
GRAD_EDU = {"硕士研究生及以上", "仅限硕士研究生", "仅限博士研究生"}
COLLEGE_EDU = {"仅限大专", "大专及以上", "大专或本科"}
NO_LIMIT_TEXT = "不限"
LEVELS = [
    ("central", "中央"),
    ("provincial", "省（副省）级"),
    ("city", "市（地）级"),
    ("county_or_below", "县（区）级及以下"),
]
ROLE_TYPE_PATTERNS = [
    ("税务系统", ["税务"]),
    ("海关/边检", ["海关", "边检", "出入境边防"]),
    ("公安/移民/基层执法", ["公安", "移民", "边防", "铁路公安"]),
    ("法院/检察/司法", ["法院", "检察", "司法", "监狱", "戒毒"]),
    ("统计调查", ["统计局", "调查总队", "调查队"]),
    ("财政审计金融监管", ["财政", "审计", "人民银行", "金融", "证券", "外汇"]),
    ("市场监管/知识产权", ["市场监督", "知识产权"]),
    ("网信/通信/信息化", ["网信", "通信管理", "信息中心", "数据"]),
    ("生态环境/自然资源/农业水利", ["生态环境", "自然资源", "农业", "水利", "林业"]),
    ("交通海事民航铁路", ["海事", "民航", "铁路", "交通"]),
    ("党政综合/办公厅", ["办公厅", "组织部", "宣传部", "统战", "纪检", "机关事务"]),
]


def main() -> int:
    majors = pd.read_csv(MAJORS_PATH, encoding="utf-8-sig", dtype=str)
    universities = pd.read_csv(UNIVERSITY_TIERS_PATH, encoding="utf-8-sig")
    opportunities = pd.read_csv(OPPORTUNITIES_PATH, encoding="utf-8-sig", dtype=str)
    matches = pd.read_csv(
        MATCHES_PATH,
        encoding="utf-8-sig",
        dtype=str,
        usecols=[
            "role_id",
            "major_code",
            "major_name",
            "major_level",
            "education_level",
            "plan_num",
            "apply_num",
            "competition_ratio",
            "match_scope",
            "department_level",
            "department_name",
            "job_name",
            "profession_text",
            "is_low_restriction_role",
        ],
    )

    majors["major_code"] = majors["code"].map(_clean_code)
    opportunities["major_code"] = opportunities["major_code"].map(_clean_code)
    matches["major_code"] = matches["major_code"].map(_clean_code)
    matches["plan_num"] = pd.to_numeric(matches["plan_num"], errors="coerce").fillna(0)
    matches["apply_num"] = pd.to_numeric(matches["apply_num"], errors="coerce").fillna(0)
    matches["competition_ratio"] = pd.to_numeric(
        matches["competition_ratio"], errors="coerce"
    )
    matches["is_low_restriction_role"] = (
        matches["is_low_restriction_role"].astype(str).str.lower().eq("true")
    )

    majors["catalog_level"] = majors.apply(_catalog_level, axis=1)
    majors["major_match_key"] = majors.apply(
        lambda row: _major_match_key(
            row.get("major_code"), row.get("special_name"), row.get("catalog_level")
        ),
        axis=1,
    )
    opportunities["major_match_key"] = opportunities.apply(
        lambda row: _major_match_key(
            row.get("major_code"), row.get("major_name"), row.get("major_level")
        ),
        axis=1,
    )
    matches["major_match_key"] = matches.apply(
        lambda row: _major_match_key(
            row.get("major_code"), row.get("major_name"), row.get("major_level")
        ),
        axis=1,
    )
    direct_metrics = _build_direct_metrics(matches, key_col="major_match_key")
    all_metrics = _build_all_textual_metrics(matches, key_col="major_match_key")
    opportunity_cols = [
        "major_match_key",
        "opportunity_level",
        "role_match_count",
        "exact_role_match_count",
        "broad_role_match_count",
        "plan_num_sum",
        "weighted_competition_ratio",
        "central_role_count",
        "provincial_role_count",
        "city_role_count",
        "county_or_below_role_count",
        "low_restriction_role_count",
        "sample_departments",
        "sample_job_names",
    ]

    out = majors.merge(
        opportunities[opportunity_cols].add_prefix("textual_"),
        left_on="major_match_key",
        right_on="textual_major_match_key",
        how="left",
    )
    out = out.merge(direct_metrics, on="major_match_key", how="left")
    out = out.merge(all_metrics, on="major_match_key", how="left")
    out = _fill_metric_nulls(out)
    out = _score(out)
    out = _add_interpretation(out)

    final_cols = [
        "major_code",
        "special_name",
        "special_type",
        "type_name",
        "catalog_level",
        "level2_name",
        "level3_name",
        "civil_service_fit_score",
        "civil_service_fit_level",
        "exam_scope",
        "direct_role_count",
        "direct_exact_role_count",
        "direct_broad_role_count",
        "direct_no_major_limit_role_count",
        "direct_quasi_three_unlimited_role_count",
        "direct_exact_role_pct",
        "direct_broad_role_pct",
        "direct_no_major_limit_role_pct",
        "direct_quasi_three_unlimited_role_pct",
        "position_match_profile",
        "suitable_role_types",
        "direct_plan_num_sum",
        "direct_weighted_competition_ratio",
        "direct_low_restriction_role_count",
        "direct_central_role_count",
        "direct_central_role_pct",
        "direct_central_avg_competition_ratio",
        "direct_provincial_role_count",
        "direct_provincial_role_pct",
        "direct_provincial_avg_competition_ratio",
        "direct_city_role_count",
        "direct_city_role_pct",
        "direct_city_avg_competition_ratio",
        "direct_county_or_below_role_count",
        "direct_county_or_below_role_pct",
        "direct_county_or_below_avg_competition_ratio",
        "graduate_path_role_count",
        "textual_all_role_count",
        "textual_exact_role_match_count",
        "textual_broad_role_match_count",
        "textual_opportunity_level",
        "upgrade_or_graduate_potential_level",
        "fit_basis",
        "tier1_head_research_reading",
        "tier2_regional_reading",
        "tier3_applied_vocational_reading",
        "sample_departments",
        "sample_job_names",
    ]
    out[final_cols].to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    OUTPUT_MD.write_text(_render_report(out, universities), encoding="utf-8")
    print(OUTPUT_CSV)
    print(OUTPUT_MD)
    return 0


def _clean_code(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def _base_major_code(value: object) -> str:
    code = _clean_code(value)
    match = re.match(r"^\d+", code)
    return match.group(0) if match else code


def _major_match_key(code: object, name: object, level: object) -> str:
    return "|".join(
        [
            _base_major_code(code),
            "" if name is None or pd.isna(name) else str(name).strip(),
            "" if level is None or pd.isna(level) else str(level).strip(),
        ]
    )


def _catalog_level(row: pd.Series) -> str:
    special_type = str(row.get("special_type") or "")
    type_name = str(row.get("type_name") or "")
    if "专科" in special_type or "专科" in type_name:
        return "专科"
    if "本科" in special_type or "本科" in type_name:
        return "本科"
    code = _clean_code(row.get("major_code"))
    if code.startswith(("4", "5")):
        return "专科"
    return "本科"


def _build_direct_metrics(
    matches: pd.DataFrame, key_col: str = "major_code"
) -> pd.DataFrame:
    rows = []
    for major_key, group in matches.groupby(key_col, dropna=False):
        undergrad = group[group["education_level"].isin(UNDERGRAD_EDU)]
        college = group[group["education_level"].isin(COLLEGE_EDU)]
        graduate = group[group["education_level"].isin(GRAD_EDU)]
        row = {
            key_col: major_key,
            "graduate_path_role_count": graduate["role_id"].nunique(),
        }
        row.update(_subset_metrics(undergrad, "undergrad"))
        row.update(_subset_metrics(college, "college"))
        rows.append(row)
    metrics = pd.DataFrame(rows)
    for prefix in ("undergrad", "college"):
        metrics[f"{prefix}_weighted_competition_ratio"] = metrics.apply(
            lambda row: _ratio(
                row[f"{prefix}_apply_num_sum"], row[f"{prefix}_plan_num_sum"]
            ),
            axis=1,
        )
    return metrics


def _subset_metrics(group: pd.DataFrame, prefix: str) -> dict[str, object]:
    total_roles = group["role_id"].nunique()
    no_major_limit = _no_major_limit_mask(group)
    quasi_three_unlimited = no_major_limit & group["is_low_restriction_role"]
    metrics: dict[str, object] = {
        f"{prefix}_role_count": total_roles,
        f"{prefix}_exact_role_count": _role_count(group[group["match_scope"].eq("exact")]),
        f"{prefix}_broad_role_count": _role_count(group[group["match_scope"].eq("broad")]),
        f"{prefix}_no_major_limit_role_count": _role_count(group[no_major_limit]),
        f"{prefix}_quasi_three_unlimited_role_count": _role_count(
            group[quasi_three_unlimited]
        ),
        f"{prefix}_plan_num_sum": group["plan_num"].sum(),
        f"{prefix}_apply_num_sum": group["apply_num"].sum(),
        f"{prefix}_low_restriction_role_count": _role_count(
            group[group["is_low_restriction_role"]]
        ),
        f"{prefix}_suitable_role_types": _role_type_summary(group),
    }
    metrics[f"{prefix}_exact_role_pct"] = _pct(metrics[f"{prefix}_exact_role_count"], total_roles)
    metrics[f"{prefix}_broad_role_pct"] = _pct(metrics[f"{prefix}_broad_role_count"], total_roles)
    metrics[f"{prefix}_no_major_limit_role_pct"] = _pct(
        metrics[f"{prefix}_no_major_limit_role_count"], total_roles
    )
    metrics[f"{prefix}_quasi_three_unlimited_role_pct"] = _pct(
        metrics[f"{prefix}_quasi_three_unlimited_role_count"], total_roles
    )
    for key, label in LEVELS:
        level_group = group[group["department_level"].eq(label)]
        count = _role_count(level_group)
        metrics[f"{prefix}_{key}_role_count"] = count
        metrics[f"{prefix}_{key}_role_pct"] = _pct(count, total_roles)
        metrics[f"{prefix}_{key}_avg_competition_ratio"] = _avg_competition(level_group)
    return metrics


def _build_all_textual_metrics(
    matches: pd.DataFrame, key_col: str = "major_code"
) -> pd.DataFrame:
    rows = []
    for major_key, group in matches.groupby(key_col, dropna=False):
        rows.append(
            {
                key_col: major_key,
                "textual_all_role_count": group["role_id"].nunique(),
                "textual_all_plan_num_sum": group["plan_num"].sum(),
                "textual_all_exact_role_count": group.loc[
                    group["match_scope"].eq("exact"), "role_id"
                ].nunique(),
            }
        )
    return pd.DataFrame(rows)


def _count_level(group: pd.DataFrame, level: str) -> int:
    return int(group.loc[group["department_level"].eq(level), "role_id"].nunique())


def _role_count(group: pd.DataFrame) -> int:
    if group.empty:
        return 0
    return int(group["role_id"].nunique())


def _pct(count: object, total: object) -> float:
    total_value = float(total or 0)
    if total_value <= 0:
        return 0.0
    return round(float(count or 0) * 100 / total_value, 1)


def _avg_competition(group: pd.DataFrame) -> float | None:
    if group.empty:
        return None
    values = pd.to_numeric(group["competition_ratio"], errors="coerce").dropna()
    if values.empty:
        return None
    return round(float(values.mean()), 2)


def _no_major_limit_mask(group: pd.DataFrame) -> pd.Series:
    if "profession_text" not in group.columns:
        return pd.Series(False, index=group.index)
    return group["profession_text"].astype(str).str.contains(
        NO_LIMIT_TEXT, regex=False, na=False
    )


def _role_type_summary(group: pd.DataFrame, limit: int = 6) -> str:
    if group.empty:
        return ""
    text = (
        group["department_name"].fillna("").astype(str)
        + "|"
        + group["job_name"].fillna("").astype(str)
    )
    counts: list[tuple[str, int]] = []
    for label, patterns in ROLE_TYPE_PATTERNS:
        mask = pd.Series(False, index=group.index)
        for pattern in patterns:
            mask = mask | text.str.contains(pattern, regex=False, na=False)
        count = _role_count(group[mask])
        if count:
            counts.append((label, count))
    counts.sort(key=lambda item: item[1], reverse=True)
    return "；".join(f"{label}({count})" for label, count in counts[:limit])


def _ratio(apply_num: float, plan_num: float) -> float | None:
    if plan_num <= 0:
        return None
    return round(float(apply_num) / float(plan_num), 2)


def _fill_metric_nulls(out: pd.DataFrame) -> pd.DataFrame:
    count_cols = [
        col
        for col in out.columns
        if col.endswith("_count")
        or col.endswith("_sum")
        or col.endswith("_role_count")
        or col.endswith("_num_sum")
    ]
    for col in count_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)
    for col in [col for col in out.columns if col.endswith("_pct")]:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)
    for col in [col for col in out.columns if col.endswith("_avg_competition_ratio")]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in [col for col in out.columns if col.endswith("_suitable_role_types")]:
        out[col] = out[col].fillna("")
    for col in [
        "textual_role_match_count",
        "textual_exact_role_match_count",
        "textual_broad_role_match_count",
        "textual_plan_num_sum",
        "textual_central_role_count",
        "textual_provincial_role_count",
        "textual_city_role_count",
        "textual_county_or_below_role_count",
        "textual_low_restriction_role_count",
    ]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)
    out["textual_weighted_competition_ratio"] = pd.to_numeric(
        out["textual_weighted_competition_ratio"], errors="coerce"
    )
    return out


def _score(out: pd.DataFrame) -> pd.DataFrame:
    is_college = out["catalog_level"].eq("专科")
    out["direct_role_count"] = out["undergrad_role_count"].where(
        ~is_college, out["college_role_count"]
    )
    out["direct_exact_role_count"] = out["undergrad_exact_role_count"].where(
        ~is_college, out["college_exact_role_count"]
    )
    out["direct_broad_role_count"] = out["undergrad_broad_role_count"].where(
        ~is_college, out["college_broad_role_count"]
    )
    out["direct_no_major_limit_role_count"] = out[
        "undergrad_no_major_limit_role_count"
    ].where(~is_college, out["college_no_major_limit_role_count"])
    out["direct_quasi_three_unlimited_role_count"] = out[
        "undergrad_quasi_three_unlimited_role_count"
    ].where(~is_college, out["college_quasi_three_unlimited_role_count"])
    out["direct_exact_role_pct"] = out["undergrad_exact_role_pct"].where(
        ~is_college, out["college_exact_role_pct"]
    )
    out["direct_broad_role_pct"] = out["undergrad_broad_role_pct"].where(
        ~is_college, out["college_broad_role_pct"]
    )
    out["direct_no_major_limit_role_pct"] = out[
        "undergrad_no_major_limit_role_pct"
    ].where(~is_college, out["college_no_major_limit_role_pct"])
    out["direct_quasi_three_unlimited_role_pct"] = out[
        "undergrad_quasi_three_unlimited_role_pct"
    ].where(~is_college, out["college_quasi_three_unlimited_role_pct"])
    out["suitable_role_types"] = out["undergrad_suitable_role_types"].where(
        ~is_college, out["college_suitable_role_types"]
    )
    out["direct_plan_num_sum"] = out["undergrad_plan_num_sum"].where(
        ~is_college, out["college_plan_num_sum"]
    )
    out["direct_apply_num_sum"] = out["undergrad_apply_num_sum"].where(
        ~is_college, out["college_apply_num_sum"]
    )
    out["direct_low_restriction_role_count"] = out[
        "undergrad_low_restriction_role_count"
    ].where(~is_college, out["college_low_restriction_role_count"])
    out["direct_central_role_count"] = out["undergrad_central_role_count"].where(
        ~is_college, out["college_central_role_count"]
    )
    out["direct_central_role_pct"] = out["undergrad_central_role_pct"].where(
        ~is_college, out["college_central_role_pct"]
    )
    out["direct_central_avg_competition_ratio"] = out[
        "undergrad_central_avg_competition_ratio"
    ].where(~is_college, out["college_central_avg_competition_ratio"])
    out["direct_provincial_role_count"] = out[
        "undergrad_provincial_role_count"
    ].where(~is_college, out["college_provincial_role_count"])
    out["direct_provincial_role_pct"] = out[
        "undergrad_provincial_role_pct"
    ].where(~is_college, out["college_provincial_role_pct"])
    out["direct_provincial_avg_competition_ratio"] = out[
        "undergrad_provincial_avg_competition_ratio"
    ].where(~is_college, out["college_provincial_avg_competition_ratio"])
    out["direct_city_role_count"] = out["undergrad_city_role_count"].where(
        ~is_college, out["college_city_role_count"]
    )
    out["direct_city_role_pct"] = out["undergrad_city_role_pct"].where(
        ~is_college, out["college_city_role_pct"]
    )
    out["direct_city_avg_competition_ratio"] = out[
        "undergrad_city_avg_competition_ratio"
    ].where(~is_college, out["college_city_avg_competition_ratio"])
    out["direct_county_or_below_role_count"] = out[
        "undergrad_county_or_below_role_count"
    ].where(~is_college, out["college_county_or_below_role_count"])
    out["direct_county_or_below_role_pct"] = out[
        "undergrad_county_or_below_role_pct"
    ].where(~is_college, out["college_county_or_below_role_pct"])
    out["direct_county_or_below_avg_competition_ratio"] = out[
        "undergrad_county_or_below_avg_competition_ratio"
    ].where(~is_college, out["college_county_or_below_avg_competition_ratio"])
    out["direct_weighted_competition_ratio"] = out.apply(
        lambda row: _ratio(row["direct_apply_num_sum"], row["direct_plan_num_sum"]),
        axis=1,
    )
    out["position_match_profile"] = out.apply(_position_match_profile, axis=1)

    max_direct = max(out["direct_role_count"].max(), 1)
    max_exact = max(out["direct_exact_role_count"].max(), 1)
    max_plan = max(out["direct_plan_num_sum"].max(), 1)
    max_low = max(out["direct_low_restriction_role_count"].max(), 1)
    max_central_prov = max(
        (out["direct_central_role_count"] + out["direct_provincial_role_count"]).max(),
        1,
    )
    max_grad = max(out["graduate_path_role_count"].max(), 1)
    max_textual = max(out["textual_all_role_count"].max(), 1)

    def score(row: pd.Series) -> float:
        if row["direct_role_count"] <= 0:
            return 0.0
        value = 0.0
        value += 35 * _log_scaled(row["direct_exact_role_count"], max_exact)
        value += 25 * _log_scaled(row["direct_role_count"], max_direct)
        value += 20 * _log_scaled(row["direct_plan_num_sum"], max_plan)
        value += 8 * _log_scaled(row["direct_low_restriction_role_count"], max_low)
        value += 5 * _log_scaled(
            row["direct_central_role_count"] + row["direct_provincial_role_count"],
            max_central_prov,
        )
        if row["catalog_level"] == "本科":
            value += 5 * _log_scaled(row["graduate_path_role_count"], max_grad)
        ratio = row["direct_weighted_competition_ratio"]
        if pd.notna(ratio):
            if ratio <= 80:
                value += 4
            elif ratio <= 120:
                value += 2
            elif ratio > 300:
                value -= 8
            elif ratio > 180:
                value -= 4
        if row["direct_exact_role_count"] <= 0:
            value = min(value, 72)
        return round(max(0, min(100, value)), 1)

    out["civil_service_fit_score"] = out.apply(score, axis=1)
    out["civil_service_fit_level"] = out["civil_service_fit_score"].map(_fit_level)

    def potential(row: pd.Series) -> str:
        if row["catalog_level"] == "本科":
            value = row["graduate_path_role_count"]
        else:
            value = row["textual_all_role_count"]
        scaled = 100 * _log_scaled(value, max_textual)
        if scaled >= 75:
            return "升学后强潜力"
        if scaled >= 55:
            return "升学后较强潜力"
        if scaled >= 30:
            return "升学后中等潜力"
        if scaled > 0:
            return "升学后弱潜力"
        return "暂无明显潜力"

    out["upgrade_or_graduate_potential_level"] = out.apply(potential, axis=1)
    return out


def _log_scaled(value: float, max_value: float) -> float:
    if value <= 0 or max_value <= 0:
        return 0.0
    return math.log1p(float(value)) / math.log1p(float(max_value))


def _fit_level(score: float) -> str:
    if score >= 75:
        return "强适配"
    if score >= 55:
        return "较强适配"
    if score >= 35:
        return "中等适配"
    if score >= 15:
        return "弱适配"
    return "很弱/无直接岗位"


def _position_match_profile(row: pd.Series) -> str:
    if row["direct_role_count"] <= 0:
        return "无直接可报岗位"
    if row["direct_quasi_three_unlimited_role_pct"] >= 20:
        return "三不限/专业不限候选较多"
    if row["direct_exact_role_pct"] >= 30 or row["direct_exact_role_count"] >= 100:
        return "以对口岗位为主"
    if row["direct_broad_role_pct"] >= 70:
        return "主要靠专业大类/门类岗位"
    if row["direct_no_major_limit_role_count"] > 0:
        return "对口+宽口径+专业不限混合"
    return "对口+宽口径混合"


def _add_interpretation(out: pd.DataFrame) -> pd.DataFrame:
    out["exam_scope"] = "2026国考职位表/中央机关及直属机构口径（第三方镜像）"
    out["fit_basis"] = out.apply(_fit_basis, axis=1)
    out["tier1_head_research_reading"] = out.apply(_tier1_reading, axis=1)
    out["tier2_regional_reading"] = out.apply(_tier2_reading, axis=1)
    out["tier3_applied_vocational_reading"] = out.apply(_tier3_reading, axis=1)
    out["sample_departments"] = out["textual_sample_departments"].fillna("")
    out["sample_job_names"] = out["textual_sample_job_names"].fillna("")
    return out


def _fit_basis(row: pd.Series) -> str:
    if row["direct_role_count"] <= 0:
        if row["catalog_level"] == "专科" and row["textual_all_role_count"] > 0:
            return "大专学历直接可报岗位不足；专业文本在本科/升本路径中有匹配线索。"
        return "2026岗位文本中未形成直接可报匹配。"
    if row["direct_exact_role_count"] <= 0:
        return "主要来自专业类/学科门类宽口径匹配，报考前必须核官方专业目录。"
    return "存在专业代码或专业名称精确匹配，并有直接学历兼容岗位。"


def _tier1_reading(row: pd.Series) -> str:
    if row["civil_service_fit_score"] >= 75:
        return "头部院校可把该专业作为中央/省级机关、选调和研究生岗位的主赛道之一。"
    if row["graduate_path_role_count"] > 50:
        return "头部院校优势主要体现在保研/读研后进入更高层级岗位。"
    if row["direct_role_count"] > 0:
        return "可以考，但院校层级优势有限，更依赖岗位地区和限制条件。"
    return "不建议把考公作为该专业在头部院校的核心卖点。"


def _tier2_reading(row: pd.Series) -> str:
    if row["civil_service_fit_score"] >= 55:
        return "区域重点/特色院校可重点面向省市县税务、执法、市场监管和事业单位路径。"
    if row["civil_service_fit_score"] >= 35:
        return "可作为备选路径，适合叠加党员、基层项目、应届身份等条件。"
    if row["direct_role_count"] > 0:
        return "岗位窗口较窄，建议只作为就业备选项。"
    return "直接考公适配弱，应更多看行业就业或升学转换。"


def _tier3_reading(row: pd.Series) -> str:
    if row["catalog_level"] == "专科":
        if row["direct_role_count"] > 0:
            return "少量大专可报基层岗位存在，但数量很少，需逐岗位核验。"
        if row["textual_all_role_count"] > 200:
            return "直接考公弱；若专升本到相近本科专业，考公潜力明显上升。"
        return "普通应用/职业院校下直接考公空间很小，优先看事业单位、基层项目或行业就业。"
    if row["civil_service_fit_score"] >= 55:
        return "应用本科可走县区基层、行政执法和地方单位，学校层级不宜夸大。"
    if row["civil_service_fit_score"] >= 35:
        return "可作为基层备选，但要靠地域、应届和限制条件放大机会。"
    return "不适合作为普通应用院校的考公主卖点。"


def _render_report(out: pd.DataFrame, universities: pd.DataFrame) -> str:
    dist = out["civil_service_fit_level"].value_counts().reindex(
        ["强适配", "较强适配", "中等适配", "弱适配", "很弱/无直接岗位"],
        fill_value=0,
    )
    tier_counts = universities["university_tier_name"].value_counts()
    direct_college_roles = int(
        out.loc[out["catalog_level"].eq("专科"), "direct_role_count"].sum()
    )
    total_college_majors = int(out["catalog_level"].eq("专科").sum())
    lines = [
        "# 专业考公适配度与三档院校解读（2026岗位口径）",
        "",
        "## 口径",
        "",
        "- 院校三档来自 `remote_edu_university_three_tiers_20260614.csv`。",
        "- 专业清单来自 `remote_edu_major_majors_20260614.csv`，共覆盖当前表内 2053 个专业行。",
        "- 考公证据来自 2026 年 20714 条岗位详情及其专业匹配表。",
        "- 分数按“直接学历兼容岗位”计算；本科看本科可报岗位，专科只看大专可报岗位。",
        "- 宽口径门类匹配只作为辅助，不能替代官方报考资格判断。",
        "",
        "## 总体分布",
        "",
        _markdown_table(
            ["适配等级", "专业数"],
            [[level, int(count)] for level, count in dist.items()],
        ),
        "",
        "## 三档院校规模",
        "",
        _markdown_table(
            ["院校层次", "院校数"],
            [[tier, int(count)] for tier, count in tier_counts.items()],
        ),
        "",
        f"- 专科专业数：{total_college_majors}；按大专学历直接匹配到的岗位线索合计很少，聚合计数为 {direct_college_roles}。专科表的“升学后潜力”不能解读为大专直接可报。",
        "",
        "## 强适配专业示例",
        "",
        _major_table(_diverse(out[out["civil_service_fit_score"] >= 75], 14)),
        "",
        "## 中等适配专业示例",
        "",
        _major_table(
            _diverse(
                out[
                    (out["civil_service_fit_score"] >= 35)
                    & (out["civil_service_fit_score"] < 55)
                ],
                12,
            )
        ),
        "",
        "## 低直接适配但升学后有潜力的专科示例",
        "",
        _major_table(
            _diverse(
                out[
                    out["catalog_level"].eq("专科")
                    & out["direct_role_count"].eq(0)
                    & out["textual_all_role_count"].gt(1000)
                ].sort_values("textual_all_role_count", ascending=False),
                12,
            )
        ),
        "",
        "## 三档院校下的判断",
        "",
        "### 1. 头部/强研究型高校",
        "",
        _tier_examples(universities, 1),
        "",
        "- 最值得强调的专业：法学、会计学、审计学、财务管理、财政学/税收学、经济学/金融学、计算机科学与技术、软件工程、网络空间安全、统计学、数据科学、汉语言文学。",
        "- 这些专业在中央机关、省级机关、税务、审计、财政、市场监管、网信/公安技术、统计调查等岗位中有较高匹配度。",
        "- 头部院校的加成不是“所有专业都更好考公”，而是高层级岗位、选调、研究生岗位、复合背景岗位更能吃到学校和培养质量优势。",
        "- 纯艺术、旅游酒店、部分护理/康养、一般农林牧渔专科类，即使在强校或特色强校，也不应作为考公主卖点。",
        "",
        "### 2. 区域重点/特色优势高校",
        "",
        _tier_examples(universities, 2),
        "",
        "- 主打法应是区域省市县岗位：税务、行政执法、市场监管、法院检察辅助、公安技术、统计调查、地方财政审计等。",
        "- 最实用的专业仍是财会审计、法学、计算机/网安/数据、中文新闻、经济金融、统计、电子信息、公共管理、物流管理等。",
        "- 这类学校不要只看“岗位总数”，还要看地区岗位、应届身份、党员/基层项目、是否限户籍等条件。很多中等适配专业在本省本市会比全国口径更有价值。",
        "",
        "### 3. 普通应用/职业供给高校",
        "",
        _tier_examples(universities, 3),
        "",
        "- 如果是应用本科，财会、计算机、法学、汉语言、统计、电子信息等仍有基层岗位空间，但主要面向县区基层和行政执法，不宜包装成中央/省级机关优势。",
        "- 如果是专科，直接国考/省考空间非常有限。专科专业的合理路径是：专升本到财会、法学、计算机、汉语言、统计、公共管理等相近专业，或走事业单位、三支一扶、辅警/司法辅助、基层服务项目。",
        "- 职业院校里的大数据技术、计算机网络技术、大数据与审计、大数据与财务管理等在“升本后”与考公专业要求更贴近；酒店、旅游、艺术设计、表演、宠物、轻工纺织等直接考公适配弱。",
        "",
        "## 输出文件",
        "",
        f"- 全量专业适配度：`{OUTPUT_CSV.relative_to(ROOT)}`",
        "",
    ]
    return "\n".join(lines)


def _diverse(df: pd.DataFrame, limit: int) -> pd.DataFrame:
    if df.empty:
        return df
    ordered = df.sort_values(
        ["civil_service_fit_score", "direct_exact_role_count", "direct_role_count"],
        ascending=False,
    )
    rows = []
    seen_subjects = set()
    for _, row in ordered.iterrows():
        subject = row.get("level3_name") or row.get("level2_name")
        if subject in seen_subjects:
            continue
        rows.append(row)
        seen_subjects.add(subject)
        if len(rows) >= limit:
            break
    if len(rows) < limit:
        for _, row in ordered.iterrows():
            if row.name in [r.name for r in rows]:
                continue
            rows.append(row)
            if len(rows) >= limit:
                break
    return pd.DataFrame(rows)


def _major_table(df: pd.DataFrame) -> str:
    rows = []
    for _, row in df.iterrows():
        rows.append(
            [
                row["special_name"],
                row["catalog_level"],
                row["level3_name"],
                row["civil_service_fit_level"],
                row["civil_service_fit_score"],
                row["position_match_profile"],
                row["suitable_role_types"] or "-",
                int(row["direct_role_count"]),
                int(row["direct_exact_role_count"]),
                int(row["direct_broad_role_count"]),
                int(row["direct_quasi_three_unlimited_role_count"]),
                int(row["direct_plan_num_sum"]),
                _fmt_ratio(row["direct_weighted_competition_ratio"]),
                _level_mix(row),
                _level_avg_competition(row),
            ]
        )
    return _markdown_table(
        [
            "专业",
            "层次",
            "专业类",
            "适配等级",
            "分数",
            "岗位画像",
            "适合岗位类型",
            "直接岗位",
            "精确岗位",
            "大类岗位",
            "三不限候选",
            "招录计划",
            "加权竞争比",
            "层级占比",
            "层级平均竞争比",
        ],
        rows,
    )


def _level_mix(row: pd.Series) -> str:
    return (
        f"中央{_fmt_pct(row['direct_central_role_pct'])}/"
        f"省{_fmt_pct(row['direct_provincial_role_pct'])}/"
        f"市{_fmt_pct(row['direct_city_role_pct'])}/"
        f"县{_fmt_pct(row['direct_county_or_below_role_pct'])}"
    )


def _level_avg_competition(row: pd.Series) -> str:
    return (
        f"中央{_fmt_ratio(row['direct_central_avg_competition_ratio'])}/"
        f"省{_fmt_ratio(row['direct_provincial_avg_competition_ratio'])}/"
        f"市{_fmt_ratio(row['direct_city_avg_competition_ratio'])}/"
        f"县{_fmt_ratio(row['direct_county_or_below_avg_competition_ratio'])}"
    )


def _tier_examples(universities: pd.DataFrame, tier: int) -> str:
    sample = universities.loc[universities["university_tier"].eq(tier)].head(8)
    names = "、".join(sample["name"].astype(str).tolist())
    return f"表内示例：{names}。"


def _markdown_table(headers: list[object], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(map(str, headers)) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_escape_cell(cell) for cell in row) + " |")
    return "\n".join(lines)


def _escape_cell(value: object) -> str:
    if value is None or pd.isna(value):
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _fmt_ratio(value: object) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.1f}"


def _fmt_pct(value: object) -> str:
    if value is None or pd.isna(value):
        return "0.0%"
    return f"{float(value):.1f}%"


if __name__ == "__main__":
    raise SystemExit(main())
