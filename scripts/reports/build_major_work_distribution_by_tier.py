"""Build major-level work-distribution readings by university tier.

The output combines RYSXAI major market observations with the three-tier
university classification. It is an inferential market view, not school-level
official graduate outcome evidence.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MARKET_PROFILES_PATH = ROOT / "data/processed/rysxai_market/market_major_profiles_2026.csv"
UNIVERSITY_TIERS_PATH = (
    ROOT
    / "reports/remote_db_university_tiers/remote_edu_university_three_tiers_20260614.csv"
)
OUTPUT_DIR = ROOT / "reports/rysxai_market"
OUTPUT_CSV = OUTPUT_DIR / "major_work_distribution_by_university_tier_20260614.csv"
OUTPUT_MD = OUTPUT_DIR / "major_work_distribution_by_university_tier_20260614.md"


OUTPUT_COLUMNS = [
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "major_level",
    "category",
    "subject",
    "domain_group",
    "market_demand_count",
    "market_salary_reference",
    "market_demand_signal_level",
    "market_activity_signal_level",
    "job_posting_sample_count",
    "top_industries",
    "top_regions",
    "top_job_directions",
    "top_job_titles",
    "top_skills",
    "market_evidence_summary",
    "tier1_head_research_work_distribution",
    "tier2_regional_feature_work_distribution",
    "tier3_applied_vocational_work_distribution",
    "tier_comparison_summary",
    "inference_confidence",
    "source_scope_note",
]


DOMAIN_RULES = [
    (
        "数字技术/计算机",
        [
            "计算机",
            "软件",
            "人工智能",
            "数据",
            "网络",
            "信息安全",
            "区块链",
            "物联网",
            "智能科学",
            "密码",
        ],
    ),
    (
        "电子信息/电气自动化",
        [
            "电子",
            "通信",
            "集成电路",
            "微电子",
            "光电",
            "电气",
            "自动化",
            "电力",
            "能源动力",
            "新能源科学",
            "机器人",
        ],
    ),
    (
        "机械制造/车辆装备",
        [
            "机械",
            "车辆",
            "汽车",
            "机电",
            "智能制造",
            "装备",
            "飞行器",
            "船舶",
            "轮机",
        ],
    ),
    (
        "土建交通/工程建设",
        [
            "土木",
            "建筑",
            "工程管理",
            "工程造价",
            "城乡",
            "水利",
            "测绘",
            "交通",
            "道路",
            "铁道",
            "轨道",
            "市政",
            "给排水",
        ],
    ),
    (
        "医药卫生/生命健康",
        [
            "临床",
            "医学",
            "口腔",
            "护理",
            "药学",
            "中医",
            "检验",
            "康复",
            "影像",
            "公共卫生",
            "助产",
            "眼视光",
        ],
    ),
    (
        "财经金融/会计审计",
        ["会计", "财务", "审计", "金融", "保险", "经济", "财政", "税收", "投资", "精算"],
    ),
    (
        "法学/公共治理",
        ["法学", "法律", "公安", "侦查", "政治", "社会工作", "公共管理", "行政管理", "知识产权"],
    ),
    (
        "教育人文/语言传媒",
        [
            "教育",
            "学前",
            "小学",
            "体育",
            "汉语言",
            "英语",
            "外语",
            "新闻",
            "传播",
            "历史",
            "哲学",
            "图书",
            "档案",
            "翻译",
        ],
    ),
    (
        "商贸服务/运营管理",
        [
            "旅游",
            "酒店",
            "电子商务",
            "市场营销",
            "物流",
            "工商管理",
            "人力资源",
            "国际商务",
            "贸易",
            "供应链",
            "餐饮",
            "会展",
        ],
    ),
    (
        "艺术设计/内容创意",
        ["艺术", "设计", "音乐", "美术", "动画", "影视", "舞蹈", "戏剧", "数字媒体"],
    ),
    (
        "农业环境/食品资源",
        [
            "农业",
            "农学",
            "林业",
            "水产",
            "动物",
            "植物",
            "园艺",
            "食品",
            "环境",
            "生态",
            "地理",
            "资源",
            "园林",
        ],
    ),
    (
        "材料化工/能源安全",
        ["化学", "材料", "矿业", "石油", "安全", "核", "冶金", "高分子", "化工", "轻化"],
    ),
]


TEMPLATES = {
    "数字技术/计算机": {
        "tier1": "更偏算法、平台研发、后端核心工程、数据/AI工程和产品技术中台；头部平台、金融科技、科研院所或升学后研发岗占优。",
        "tier2": "更偏企业应用开发、测试、数据分析、政企信息化、系统集成和区域互联网岗位。",
        "tier3": "更偏运维、实施、技术支持、测试、电商/信息系统维护、低代码应用和基础开发岗位。",
    },
    "电子信息/电气自动化": {
        "tier1": "更偏芯片/通信/电力电子/自动控制研发、能源系统设计和高端装备技术岗。",
        "tier2": "更偏电气工程师、自动化项目、PLC/嵌入式、区域电力设备和制造企业工程岗。",
        "tier3": "更偏设备调试、维修维护、售后技术支持、产线自动化、质检和现场工程岗位。",
    },
    "机械制造/车辆装备": {
        "tier1": "更偏研发设计、仿真、智能制造、新能源汽车/机器人/高端装备研发和工艺平台岗。",
        "tier2": "更偏区域制造企业的机械设计、工艺、质量、设备、项目工程和供应链技术岗。",
        "tier3": "更偏设备维护、生产管理、技工、质检、售后服务、车间工艺和现场改善岗位。",
    },
    "土建交通/工程建设": {
        "tier1": "更偏规划设计院、大型央国企、工程咨询、BIM/数字建造和复杂项目管理岗位。",
        "tier2": "更偏区域设计施工、项目管理、造价、监理、市政交通和工程技术岗位。",
        "tier3": "更偏施工员、资料员、测量员、现场管理、物业工程和基层运维岗位。",
    },
    "医药卫生/生命健康": {
        "tier1": "更偏三甲医院、科研型医院、药企医学/临床研究、器械研发和继续深造后专业岗。",
        "tier2": "更偏区域医院、专科医院、医药/器械企业、检验康复和护理骨干岗位。",
        "tier3": "更偏基层医疗、护理、药店/DTP、康养、母婴护理、医药推广和医疗服务执行岗。",
    },
    "财经金融/会计审计": {
        "tier1": "更偏金融机构总部、四大/头部审计咨询、投研风控、管培和复合型数据财务岗位。",
        "tier2": "更偏区域银行、企业财务、事务所、税务、审计、经营分析和财务管理岗位。",
        "tier3": "更偏出纳、会计助理、门店财务、税务助理、销售支持和基础运营结算岗位。",
    },
    "法学/公共治理": {
        "tier1": "更偏头部律所、金融/科技合规、知识产权、政策研究、公务员和继续深造路径。",
        "tier2": "更偏区域律所、企业法务、基层公检法、政府/事业单位和合规风控岗位。",
        "tier3": "更偏法务助理、合同/行政合规、人事行政、销售合同支持和基层治理服务岗位。",
    },
    "教育人文/语言传媒": {
        "tier1": "更偏重点学校、出版传媒、研究生深造、内容策划、国际交流和机关/平台文字岗位。",
        "tier2": "更偏区域中小学、教培、编辑运营、行政文秘、人力和区域媒体岗位。",
        "tier3": "更偏幼教/教辅/培训机构、文员、客服、新媒体执行、门店运营和本地服务岗位。",
    },
    "商贸服务/运营管理": {
        "tier1": "更偏总部管培、平台运营、品牌策略、商业分析、供应链管理和咨询类岗位。",
        "tier2": "更偏区域市场、渠道销售、电商运营、门店/酒店/文旅管理和物流运营岗位。",
        "tier3": "更偏运营助理、客服、销售、门店执行、直播电商、旅游服务和酒店基层管理岗位。",
    },
    "艺术设计/内容创意": {
        "tier1": "更偏头部内容平台、品牌创意、交互/工业/视觉设计、艺术研究和策展传播岗位。",
        "tier2": "更偏区域文创、广告、新媒体、设计执行、展陈和品牌运营岗位。",
        "tier3": "更偏美工、短视频剪辑、门店视觉、摄影摄像、教培和基础设计制作岗位。",
    },
    "农业环境/食品资源": {
        "tier1": "更偏科研院所、龙头企业研发、生态规划、食品/种业研发和政策咨询岗位。",
        "tier2": "更偏区域农业、环保、检测、园林、食品企业和自然资源技术岗位。",
        "tier3": "更偏生产技术员、检测员、基层农技、园区运维、食品质检和现场服务岗位。",
    },
    "材料化工/能源安全": {
        "tier1": "更偏材料研发、化工研发、能源新材料、核/安全技术、实验平台和研究院岗位。",
        "tier2": "更偏工艺、质量、EHS、实验室、区域化工/材料企业工程师岗位。",
        "tier3": "更偏化验员、质检、生产操作、安全员、设备巡检和现场工艺执行岗位。",
    },
    "通用/交叉专业": {
        "tier1": "更偏研究、复合型专业岗、总部职能、咨询分析和继续深造后高阶岗位。",
        "tier2": "更偏区域行业骨干、专业执行、项目管理、企业职能和事业单位岗位。",
        "tier3": "更偏本地应用执行、基础职能、销售/运营/客服、现场服务和基层管理岗位。",
    },
}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    profiles = _read_csv(MARKET_PROFILES_PATH)
    universities = _read_csv(UNIVERSITY_TIERS_PATH)

    rows = [_build_row(row) for row in profiles]
    _write_csv(OUTPUT_CSV, rows, OUTPUT_COLUMNS)
    OUTPUT_MD.write_text(_render_report(rows, universities), encoding="utf-8-sig")

    print(OUTPUT_CSV)
    print(OUTPUT_MD)
    print(f"rows={len(rows)}")
    return 0


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _build_row(row: dict[str, str]) -> dict[str, str]:
    domain = _classify_domain(row)
    top_industries = _top_items(row.get("top_industries", ""), 3)
    top_regions = _top_items(row.get("top_regions", ""), 3)
    top_jobs = _top_items(row.get("top_job_directions", ""), 3)
    top_titles = _top_items(row.get("top_job_titles", ""), 3)
    top_skills = _top_items(row.get("top_skills", ""), 5)
    major_level = row.get("level", "")
    templates = TEMPLATES.get(domain, TEMPLATES["通用/交叉专业"])

    market_evidence = _market_evidence(row, top_industries, top_jobs, top_regions)
    confidence = _confidence(row, top_industries, top_jobs)

    tier1 = _tier_text(
        "头部/强研究型高校",
        templates["tier1"],
        row,
        top_industries,
        top_jobs,
        top_regions,
        major_level,
    )
    tier2 = _tier_text(
        "区域重点/特色优势高校",
        templates["tier2"],
        row,
        top_industries,
        top_jobs,
        top_regions,
        major_level,
    )
    tier3 = _tier_text(
        "普通应用/职业供给高校",
        templates["tier3"],
        row,
        top_industries,
        top_jobs,
        top_regions,
        major_level,
    )

    if major_level == "专科":
        tier1 = (
            "该专业属于专科目录，头部/强研究型高校通常不是直接供给主体；若通过专升本、"
            "高水平校企项目或技能竞赛衔接，"
            + tier1
        )

    return {
        "rysxai_profession_id": row.get("rysxai_profession_id", ""),
        "major_code": row.get("major_code", ""),
        "major_name": row.get("major_name", ""),
        "major_level": major_level,
        "category": row.get("category", ""),
        "subject": row.get("subject", ""),
        "domain_group": domain,
        "market_demand_count": row.get("demand_count_national", ""),
        "market_salary_reference": row.get("salary_reference_national", ""),
        "market_demand_signal_level": row.get("market_demand_signal_level", ""),
        "market_activity_signal_level": row.get("market_activity_signal_level", ""),
        "job_posting_sample_count": row.get("job_posting_sample_count", ""),
        "top_industries": top_industries,
        "top_regions": top_regions,
        "top_job_directions": top_jobs,
        "top_job_titles": top_titles,
        "top_skills": top_skills,
        "market_evidence_summary": market_evidence,
        "tier1_head_research_work_distribution": tier1,
        "tier2_regional_feature_work_distribution": tier2,
        "tier3_applied_vocational_work_distribution": tier3,
        "tier_comparison_summary": _comparison_summary(domain, major_level),
        "inference_confidence": confidence,
        "source_scope_note": (
            "Source level C: RYSXAI third-party market observation and recruiting samples; "
            "not official school-major graduate outcome evidence."
        ),
    }


def _classify_domain(row: dict[str, str]) -> str:
    primary_text = "".join(
        [
            row.get("major_name", ""),
            row.get("category", ""),
            row.get("subject", ""),
        ]
    )
    for domain, keywords in DOMAIN_RULES:
        if any(keyword in primary_text for keyword in keywords):
            return domain
    market_text = "".join([row.get("top_industries", ""), row.get("top_job_directions", "")])
    for domain, keywords in DOMAIN_RULES:
        if any(keyword in market_text for keyword in keywords):
            return domain
    return "通用/交叉专业"


def _top_items(value: str, limit: int) -> str:
    parts = [part.strip() for part in (value or "").split("|") if part.strip()]
    return "；".join(parts[:limit])


def _market_evidence(
    row: dict[str, str], top_industries: str, top_jobs: str, top_regions: str
) -> str:
    demand = row.get("demand_count_national") or "未知"
    salary = row.get("salary_reference_national") or "未知"
    demand_level = row.get("market_demand_signal_level") or "unknown"
    return (
        f"全国需求参考 {demand}（{demand_level}），月薪参考 {salary}；"
        f"行业Top：{top_industries or '无'}；岗位方向Top：{top_jobs or '无'}；"
        f"地区Top：{top_regions or '无'}。"
    )


def _tier_text(
    tier_name: str,
    base: str,
    row: dict[str, str],
    top_industries: str,
    top_jobs: str,
    top_regions: str,
    major_level: str,
) -> str:
    evidence = []
    if top_industries:
        evidence.append(f"主要对接行业：{top_industries}")
    if top_jobs:
        evidence.append(f"常见岗位方向：{top_jobs}")
    if top_regions:
        evidence.append(f"主要城市/区域：{top_regions}")
    evidence_text = "；".join(evidence)
    level_note = ""
    if tier_name == "普通应用/职业供给高校" and major_level == "本科":
        level_note = "普通本科场景下，岗位层级通常介于区域骨干与基层执行之间；"
    return f"{level_note}{base} 结合市场样本，{evidence_text or '该专业市场样本有限，需结合本地产业和学校培养方向复核'}。"


def _comparison_summary(domain: str, major_level: str) -> str:
    if major_level == "专科":
        return (
            "专科专业的主要直接供给层级通常在普通应用/职业供给高校；区域重点层级看校企合作和地方产业，"
            "头部层级更多体现为升学衔接或高水平项目带来的岗位上移。"
        )
    if domain in {"数字技术/计算机", "电子信息/电气自动化", "机械制造/车辆装备", "材料化工/能源安全"}:
        return "层级差异主要体现在研发深度、项目复杂度和进入头部企业/央国企/研究院的概率。"
    if domain == "医药卫生/生命健康":
        return "层级差异主要体现在医院等级、规培/科研机会、药企医学岗位和专业资质门槛。"
    if domain in {"财经金融/会计审计", "法学/公共治理"}:
        return "层级差异主要体现在机构层级、客户复杂度、牌照/考试路径和总部岗位机会。"
    if domain in {"教育人文/语言传媒", "商贸服务/运营管理", "艺术设计/内容创意"}:
        return "层级差异主要体现在城市平台、品牌机构、内容/管理岗位层级和本地服务岗位占比。"
    return "层级差异主要体现在平台、城市、岗位复杂度和本地就业半径。"


def _confidence(row: dict[str, str], top_industries: str, top_jobs: str) -> str:
    sample_count = _to_int(row.get("job_posting_sample_count"))
    distribution_count = _to_int(row.get("industry_distribution_count")) + _to_int(
        row.get("job_direction_distribution_count")
    )
    demand = _to_int(row.get("demand_count_national"))
    if sample_count >= 5 and distribution_count >= 10 and demand >= 10_000:
        return "medium-high"
    if top_industries and top_jobs:
        return "medium"
    return "low"


def _to_int(value: str | None) -> int:
    try:
        return int(float(str(value or "").strip()))
    except ValueError:
        return 0


def _render_report(rows: list[dict[str, str]], universities: list[dict[str, str]]) -> str:
    tier_counts = Counter(row.get("university_tier_name", "") for row in universities)
    level_counts = Counter(row.get("major_level", "") for row in rows)
    domain_counts = Counter(row.get("domain_group", "") for row in rows)

    lines = [
        "# 全专业工作分布分层判断",
        "",
        "## 输出说明",
        "",
        f"- 专业行数：{len(rows)}",
        f"- 本科专业：{level_counts.get('本科', 0)}",
        f"- 专科专业：{level_counts.get('专科', 0)}",
        f"- 头部/强研究型高校数：{tier_counts.get('头部/强研究型高校', 0)}",
        f"- 区域重点/特色优势高校数：{tier_counts.get('区域重点/特色优势高校', 0)}",
        f"- 普通应用/职业供给高校数：{tier_counts.get('普通应用/职业供给高校', 0)}",
        "",
        "## 口径",
        "",
        "- 这是专业市场观察 + 院校层级的推断结果，不是某校某专业官方就业质量报告。",
        "- 三档院校层级用于解释岗位层级、平台、城市和就业半径差异。",
        "- RYSXAI 数据源等级为 C，适合筛选、召回、初步判断，不适合直接当成毕业生真实流向比例。",
        "",
        "## 专业领域覆盖",
        "",
        "| 领域 | 专业数 |",
        "|---|---:|",
    ]
    for domain, count in domain_counts.most_common():
        lines.append(f"| {domain} | {count} |")

    lines.extend(
        [
            "",
            "## 样例",
            "",
            "| 专业 | 层次 | 领域 | 市场证据摘要 |",
            "|---|---|---|---|",
        ]
    )
    for row in rows[:12]:
        lines.append(
            "| {major_name} | {major_level} | {domain_group} | {summary} |".format(
                major_name=row["major_name"],
                major_level=row["major_level"],
                domain_group=row["domain_group"],
                summary=row["market_evidence_summary"].replace("|", "/"),
            )
        )
    lines.extend(["", f"完整结果见 `{OUTPUT_CSV.relative_to(ROOT).as_posix()}`。", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
