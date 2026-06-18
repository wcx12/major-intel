from __future__ import annotations

import csv
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAJOR_FIT = ROOT / "reports/major_subject_fit_20260614/major_subject_fit_all_20260614.csv"
UNIVERSITY_TIERS = ROOT / "reports/remote_db_university_tiers/remote_edu_university_three_tiers_20260614.csv"
OUTCOMES = ROOT / "data/cleaned/graduate_outcomes/master_records_public.csv"
OUTPUT_DIR = ROOT / "reports/major_graduate_study_fit_20260615"
OUTPUT_CSV = OUTPUT_DIR / "major_graduate_study_fit_by_tier_20260615.csv"
OUTPUT_MD = OUTPUT_DIR / "major_graduate_study_fit_summary_20260615.md"


TIER_NAMES = {
    "1": "头部/强研究型高校",
    "2": "区域重点/特色优势高校",
    "3": "普通应用/职业供给高校",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def norm_text(value: str) -> str:
    value = (value or "").strip()
    value = value.replace("（", "(").replace("）", ")")
    value = re.sub(r"^\d{4,6}[A-ZKTYM]*\s*", "", value)
    value = re.sub(r"\([^)]*\)", "", value)
    value = value.replace("专业", "")
    value = re.sub(r"[\s·・、,，;；:/|｜\-—_]+", "", value)
    return value


def norm_school(value: str) -> str:
    value = norm_text(value)
    value = value.replace("學", "学")
    return value


def int_value(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def float_fmt(value: float) -> str:
    if value == 0:
        return "0"
    return f"{value:.2f}"


def build_school_lookup(university_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for row in university_rows:
        name = row.get("name", "")
        if not name:
            continue
        keys = {norm_school(name)}
        stripped = re.sub(r"\([^)]*\)", "", name.replace("（", "(").replace("）", ")"))
        keys.add(norm_school(stripped))
        for key in keys:
            if key and key not in lookup:
                lookup[key] = row
    return lookup


def prestige_flags(school_name: str, school_lookup: dict[str, dict[str, str]]) -> dict[str, bool]:
    normalized = norm_school(school_name)
    row = school_lookup.get(normalized)
    if row is None and normalized.endswith("医学院"):
        row = school_lookup.get(normalized.replace("医学院", "大学"))
    qingbei = "清华大学" in school_name or "北京大学" in school_name
    is985 = bool(row and row.get("is985") == "1") or qingbei
    is211 = bool(row and row.get("is211") == "1") or is985
    dual = bool(row and row.get("is_dual_class") == "1") or is211
    tier = row.get("university_tier", "") if row else ""
    return {
        "qingbei": qingbei,
        "is985": is985,
        "is211": is211,
        "dual": dual,
        "tier1": tier == "1",
        "tier2": tier == "2",
        "tier3": tier == "3",
    }


def prestige_score(school_name: str, school_lookup: dict[str, dict[str, str]]) -> int:
    flags = prestige_flags(school_name, school_lookup)
    if flags["qingbei"]:
        return 100
    if flags["is985"]:
        return 92
    if flags["tier1"] or flags["dual"]:
        return 82
    if flags["is211"]:
        return 75
    if flags["tier2"]:
        return 58
    if flags["tier3"]:
        return 38
    return 30


def split_candidates(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[;；,，、/|｜\n]+", value)
    candidates = []
    for part in parts:
        cleaned = norm_text(part)
        if cleaned:
            candidates.append(cleaned)
    return candidates


def build_outcome_indexes(outcome_rows: list[dict[str, str]]) -> tuple[dict[str, set[int]], dict[int, dict[str, object]]]:
    index: dict[str, set[int]] = defaultdict(set)
    summaries: dict[int, dict[str, object]] = {}
    for idx, row in enumerate(outcome_rows):
        school_name = row.get("school_name", "")
        year = row.get("year", "")
        route = row.get("route", "")
        record_summary = {
            "school_name": school_name,
            "year": year,
            "route": route,
        }
        summaries[idx] = record_summary
        fields = [
            row.get("undergraduate_major", ""),
            row.get("major", ""),
            row.get("admission_major", ""),
        ]
        for field in fields:
            for candidate in split_candidates(field):
                if 2 <= len(candidate) <= 24:
                    index[candidate].add(idx)
    return index, summaries


def match_major_records(major_name: str, outcome_index: dict[str, set[int]]) -> set[int]:
    target = norm_text(major_name)
    if not target:
        return set()
    matches = set(outcome_index.get(target, set()))
    # Allow conservative substring matching only for longer, specific major names.
    if len(target) >= 5:
        for candidate, ids in outcome_index.items():
            if len(candidate) >= 5 and (target in candidate or candidate in target):
                matches.update(ids)
    return matches


def subject_adjustment(level2: str, level3: str, major_name: str, major_type: str) -> int:
    text = f"{level2} {level3} {major_name}"
    adjustment = 0
    if "专科" in major_type or "高职" in major_type:
        adjustment -= 14
    if any(key in text for key in ["理学", "数学", "物理", "化学", "生物", "统计"]):
        adjustment += 12
    if any(key in text for key in ["医学", "临床", "口腔", "药学", "中医"]):
        adjustment += 10
    if any(key in text for key in ["工学", "计算机", "电子", "自动化", "软件", "人工智能", "电气", "机械", "材料", "信息", "低空"]):
        adjustment += 8
    if any(key in text for key in ["法学", "马克思", "政治", "社会学"]):
        adjustment += 7
    if any(key in text for key in ["农学", "植物", "动物", "水产"]):
        adjustment += 6
    if any(key in text for key in ["经济", "金融", "会计", "财政", "税收"]):
        adjustment += 5
    if any(key in text for key in ["教育", "师范", "心理"]):
        adjustment += 4
    if any(key in text for key in ["管理", "旅游", "酒店", "物流", "电子商务"]):
        adjustment -= 2
    if any(key in text for key in ["艺术", "音乐", "舞蹈", "美术", "设计", "表演", "体育"]):
        adjustment -= 6
    if any(key in text for key in ["护理", "康复", "助产"]):
        adjustment -= 3
    return adjustment


def base_score(tier: str, major_type: str) -> int:
    score = {"1": 68, "2": 53, "3": 34}[tier]
    if "专科" in major_type or "高职" in major_type:
        score -= 8 if tier != "3" else 4
    return score


def fit_level(score: int, offer_count: int) -> str:
    if offer_count == 0:
        return "暂无开设样本"
    if score >= 82:
        return "高"
    if score >= 68:
        return "较高"
    if score >= 52:
        return "中"
    if score >= 38:
        return "偏低"
    return "低"


def rate_band(tier: str, level2: str, major_type: str, score: int) -> tuple[str, str]:
    if "专科" in major_type or "高职" in major_type:
        if tier == "3":
            return "升本/转段约10%-35%，直接考研需先取得本科资格", "通常无推免资格"
        return "样本少，不建议按普通本科升学率理解", "通常无可比推免率"
    high_research = any(key in level2 for key in ["理学", "医学", "农学", "法学"])
    if tier == "1":
        return ("45%-75%" if high_research or score >= 75 else "35%-60%", "10%-30%，头部强校/强专业可更高")
    if tier == "2":
        return ("28%-55%" if high_research or score >= 65 else "20%-45%", "2%-10%，有推免资格学校和强专业更高")
    return ("12%-35%" if score >= 45 else "8%-25%", "0%-3%，多数学校无推免或名额很少")


def interpretation(tier: str, major_name: str, level2: str, offer_count: int, evidence_count: int, best: str, score: int) -> str:
    if offer_count == 0:
        return f"第{tier}层未匹配到该专业开设样本，升学适配度不单独评价；可参考其他层级样本。"
    if tier == "1":
        base = "头部/强研究型高校更适合把该专业走成科研、保研、直博或强校专硕路径"
    elif tier == "2":
        base = "区域重点/特色优势高校适合通过校内强学科、竞赛科研和考研把该专业向上迁移"
    else:
        base = "普通应用/职业供给高校更适合先确认本科层次、考研资格和实践作品/证书，再争取区域双一流或专硕通道"
    evidence = f"公开去向样本命中{evidence_count}条" if evidence_count else "公开去向样本暂无稳定命中"
    best_text = f"，已见较好去向包括{best}" if best else ""
    level = fit_level(score, offer_count)
    return f"{base}；{major_name}属于{level2 or '未标明门类'}方向，综合判断为{level}；{evidence}{best_text}。"


def main() -> None:
    majors = read_csv(MAJOR_FIT)
    universities = read_csv(UNIVERSITY_TIERS)
    outcomes = read_csv(OUTCOMES)
    school_lookup = build_school_lookup(universities)
    outcome_index, outcome_summaries = build_outcome_indexes(outcomes)

    output_rows: list[dict[str, object]] = []
    per_major_evidence: dict[str, dict[str, object]] = {}

    for major in majors:
        major_name = major.get("专业名称", "")
        record_ids = match_major_records(major_name, outcome_index)
        years = {str(outcome_summaries[i]["year"]) for i in record_ids if outcome_summaries[i].get("year")}
        year_count = max(len(years), 1)
        destination_counter: Counter[str] = Counter()
        route_counter: Counter[str] = Counter()
        prestige_counts = Counter()
        for idx in record_ids:
            summary = outcome_summaries[idx]
            school_name = str(summary["school_name"])
            route_counter[str(summary["route"])] += 1
            if school_name:
                destination_counter[school_name] += 1
            flags = prestige_flags(school_name, school_lookup)
            for flag_name, active in flags.items():
                if active:
                    prestige_counts[flag_name] += 1
        best_destinations = [
            name
            for name, _ in sorted(
                destination_counter.items(),
                key=lambda item: (prestige_score(item[0], school_lookup), item[1], item[0]),
                reverse=True,
            )[:6]
        ]
        evidence = {
            "record_count": len(record_ids),
            "recommendation_count": route_counter.get("recommendation_exemption", 0),
            "qingbei_avg": prestige_counts["qingbei"] / year_count,
            "985_avg": prestige_counts["is985"] / year_count,
            "211_avg": prestige_counts["is211"] / year_count,
            "dual_avg": prestige_counts["dual"] / year_count,
            "best": "、".join(best_destinations),
            "years": len(years),
        }
        per_major_evidence[major_name] = evidence

        for tier in ["1", "2", "3"]:
            offer_count = int_value(major.get(f"第{tier}层开设数", "0"))
            examples = major.get(f"第{tier}层样例学校", "")
            score = base_score(tier, major.get("专业类型", ""))
            score += subject_adjustment(
                major.get("门类/大类", ""),
                major.get("专业类", ""),
                major_name,
                major.get("专业类型", ""),
            )
            score += min(8, int(math.log1p(evidence["record_count"]) * 2)) if evidence["record_count"] else 0
            if evidence["dual_avg"] >= 5:
                score += 5
            if evidence["985_avg"] >= 2:
                score += 4
            if evidence["qingbei_avg"] > 0:
                score += 2
            if offer_count > 0:
                score += min(4, int(math.log1p(offer_count)))
            else:
                score = min(score, 32)
            score = max(0, min(100, score))
            grad_band, reco_band = rate_band(tier, major.get("门类/大类", ""), major.get("专业类型", ""), score)
            output_rows.append(
                {
                    "special_id": major.get("special_id", ""),
                    "专业代码": major.get("专业代码", ""),
                    "专业名称": major_name,
                    "专业类型": major.get("专业类型", ""),
                    "门类/大类": major.get("门类/大类", ""),
                    "专业类": major.get("专业类", ""),
                    "学校层级": tier,
                    "学校层级名称": TIER_NAMES[tier],
                    "本层开设数": offer_count,
                    "本层样例学校": examples,
                    "升学适配度评分": score,
                    "升学适配度等级": fit_level(score, offer_count),
                    "估计平均升学/考研率区间": grad_band,
                    "估计平均保研率区间": reco_band,
                    "公开样本命中记录数": evidence["record_count"],
                    "公开样本推免/保研记录数": evidence["recommendation_count"],
                    "公开样本覆盖年份数": evidence["years"],
                    "公开样本年均去清北": float_fmt(evidence["qingbei_avg"]),
                    "公开样本年均去985": float_fmt(evidence["985_avg"]),
                    "公开样本年均去211": float_fmt(evidence["211_avg"]),
                    "公开样本年均去双一流": float_fmt(evidence["dual_avg"]),
                    "公开样本最佳去向举例": evidence["best"],
                    "适配度解读": interpretation(
                        tier,
                        major_name,
                        major.get("门类/大类", ""),
                        offer_count,
                        evidence["record_count"],
                        evidence["best"],
                        score,
                    ),
                    "口径说明": "升学/保研率为经验估计区间；清北/985/211/双一流为本地公开抓取样本年均命中数，不等同于官方全量升学率。",
                }
            )

    fieldnames = list(output_rows[0].keys()) if output_rows else []
    write_csv(OUTPUT_CSV, fieldnames, output_rows)

    by_tier_level = Counter((row["学校层级"], row["升学适配度等级"]) for row in output_rows)
    top_examples = sorted(
        (row for row in output_rows if row["本层开设数"] and row["升学适配度等级"] in {"高", "较高"}),
        key=lambda row: (row["学校层级"], -int(row["升学适配度评分"]), row["专业名称"]),
    )

    lines = [
        "# 专业升学适配度粗评估",
        "",
        "生成日期：2026-06-15",
        "",
        "## 口径",
        "",
        "- 院校层级来自 `remote_edu_university_three_tiers_20260614.csv`。",
        "- 专业开设层级样本来自 `major_subject_fit_all_20260614.csv`。",
        "- 去向证据来自 `master_records_public.csv` 的公开人员级推免/拟录取记录。",
        "- `公开样本年均去清北/985/211/双一流` 是本地抓取样本命中数除以该专业命中年份数，不是官方真实全口径升学率。",
        "- `估计平均升学/考研率区间` 和 `估计平均保研率区间` 是按院校层级、专业门类、专业类型和公开去向信号给出的经验判断。",
        "",
        "## 输出",
        "",
        f"- 明细 CSV：`{OUTPUT_CSV.relative_to(ROOT)}`",
        f"- 明细行数：{len(output_rows)}（{len(majors)} 个专业 × 3 个院校层级）",
        "",
        "## 各层级等级分布",
        "",
        "| 层级 | 高 | 较高 | 中 | 偏低 | 低 | 暂无开设样本 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for tier in ["1", "2", "3"]:
        lines.append(
            "| "
            + TIER_NAMES[tier]
            + " | "
            + " | ".join(
                str(by_tier_level.get((tier, label), 0))
                for label in ["高", "较高", "中", "偏低", "低", "暂无开设样本"]
            )
            + " |"
        )
    lines.extend(["", "## 高适配/较高适配样例", ""])
    for tier in ["1", "2", "3"]:
        lines.append(f"### {TIER_NAMES[tier]}")
        examples = [row for row in top_examples if row["学校层级"] == tier][:8]
        if not examples:
            lines.append("")
            lines.append("暂无。")
            lines.append("")
            continue
        lines.append("")
        for row in examples:
            lines.append(
                f"- {row['专业名称']}：{row['升学适配度等级']}（{row['升学适配度评分']}分）；"
                f"样例学校：{row['本层样例学校'] or '未列出'}；"
                f"最佳去向样本：{row['公开样本最佳去向举例'] or '暂无稳定样本'}。"
            )
        lines.append("")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8-sig")
    print({"rows": len(output_rows), "csv": str(OUTPUT_CSV), "summary": str(OUTPUT_MD)})


if __name__ == "__main__":
    main()
