"""Build an independent major-level AI replacement risk dataset.

The dataset is intentionally file-based and independent from the MySQL-backed
retrieval tools.  It uses the already crawled rysxai market snapshots as a
Chinese-market job evidence source, then applies transparent heuristic scoring
to produce a first-pass ranking of majors that are more exposed to AI
automation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


DATA_VERSION = "major_ai_replacement/v1.0-heuristic-20260612"
DEFAULT_INPUT_DIR = Path("data/processed/rysxai")
DEFAULT_OUTPUT_DIR = Path("data/processed/ai_replacement")
DEFAULT_REPORT_DIR = Path("reports/ai_replacement")
MARKET_SOURCE_LEVEL = "C"
MARKET_SCOPE = "third_party_chinese_recruiting_market_observation"

GENERIC_OR_NOISE_TERMS = {
    "",
    "-",
    "其他",
    "其它",
    "不限",
    "无",
    "未分类",
    "更多",
    "综合",
}

GENERIC_INDUSTRY_TERMS = {
    "互联网",
    "房地产",
    "金融投资",
    "金融",
    "贸易",
    "批发零售",
    "教育培训",
    "加工制造",
    "服装",
    "汽车",
    "媒体",
    "广告",
    "咨询服务",
    "医疗保健",
    "电子技术",
    "机械重工",
    "物流运输",
    "快消",
    "餐饮",
    "旅游",
    "酒店",
    "能源",
    "环保",
    "建筑",
    "建材",
    "医药",
    "农业",
}

TITLE_SUFFIXES = (
    "高级",
    "初级",
    "资深",
    "实习",
    "实习生",
    "助理",
)

SPLIT_PATTERN = re.compile(r"[，,、；;｜|/]+")
BRACKET_PATTERN = re.compile(r"[（(].*?[）)]")
FULLWIDTH_BRACKET_PATTERN = re.compile(r"[【\[].*?[】\]]")
SPACE_PATTERN = re.compile(r"\s+")
SALARY_PATTERN = re.compile(r"\d+(\.\d+)?\s*[-~到至]\s*\d+(\.\d+)?\s*[kK千万元/]*")


@dataclass
class JobScore:
    normalized_job_title: str
    ai_exposure_score: float
    automation_score: float
    physical_barrier_score: float
    license_barrier_score: float
    human_trust_barrier_score: float
    liability_barrier_score: float
    final_job_risk_score: float
    ai_assist_score: float
    confidence_score: float
    risk_level: str
    category: str
    tags: list[str]
    reasons: list[str]

    @property
    def human_barrier_score(self) -> float:
        return max(
            self.physical_barrier_score,
            self.license_barrier_score,
            self.human_trust_barrier_score,
            self.liability_barrier_score,
        )


@dataclass
class CandidateEvidence:
    profession_id: str
    major_code: str
    major_name: str
    major_level: str
    raw_job_text: str
    normalized_job_title: str
    candidate_type: str
    source_field: str
    field_quality_weight: float
    raw_weight: float
    job_group: str = ""
    industry_label: str = ""
    sample_city: str = ""
    sample_industry: str = ""
    sample_education: str = ""
    sample_experience: str = ""
    sample_skills: list[str] = field(default_factory=list)


@dataclass
class AggregatedJobCandidate:
    profession_id: str
    major_code: str
    major_name: str
    major_level: str
    normalized_job_title: str
    candidate_type: str
    source_weight: float = 0.0
    evidence_count: int = 0
    raw_job_texts: Counter[str] = field(default_factory=Counter)
    job_groups: Counter[str] = field(default_factory=Counter)
    industry_labels: Counter[str] = field(default_factory=Counter)
    source_fields: Counter[str] = field(default_factory=Counter)
    sample_cities: Counter[str] = field(default_factory=Counter)
    sample_industries: Counter[str] = field(default_factory=Counter)
    sample_educations: Counter[str] = field(default_factory=Counter)
    sample_experiences: Counter[str] = field(default_factory=Counter)
    sample_skills: Counter[str] = field(default_factory=Counter)

    def add(self, evidence: CandidateEvidence) -> None:
        self.source_weight += evidence.raw_weight * evidence.field_quality_weight
        self.evidence_count += 1
        self.raw_job_texts[evidence.raw_job_text] += 1
        if evidence.job_group:
            self.job_groups[evidence.job_group] += 1
        if evidence.industry_label:
            self.industry_labels[evidence.industry_label] += 1
        self.source_fields[evidence.source_field] += 1
        if evidence.sample_city:
            self.sample_cities[evidence.sample_city] += 1
        if evidence.sample_industry:
            self.sample_industries[evidence.sample_industry] += 1
        if evidence.sample_education:
            self.sample_educations[evidence.sample_education] += 1
        if evidence.sample_experience:
            self.sample_experiences[evidence.sample_experience] += 1
        for skill in evidence.sample_skills:
            skill = clean_text(skill)
            if skill:
                self.sample_skills[skill] += 1


@dataclass
class MajorProfile:
    rank: int
    profession_id: str
    major_code: str
    major_name: str
    major_level: str
    ai_replacement_score: float
    ai_replacement_level: str
    ai_exposure_score: float
    automation_score: float
    human_barrier_score: float
    ai_assist_value_score: float
    confidence_score: float
    candidate_count: int
    evidence_count: int
    source_fields: list[str]
    top_risky_jobs: list[dict[str, Any]]
    top_resilient_jobs: list[dict[str, Any]]
    main_reasons: list[str]


def clean_text(value: Any) -> str:
    text = str(value or "").strip()
    text = text.replace("\ufeff", "").replace("\u3000", " ")
    text = BRACKET_PATTERN.sub("", text)
    text = FULLWIDTH_BRACKET_PATTERN.sub("", text)
    text = SALARY_PATTERN.sub("", text)
    if "招聘" in text and len(text.split("招聘", 1)[-1]) >= 2:
        text = text.split("招聘", 1)[-1]
    for noisy in (
        "周六日双休",
        "周末双休",
        "双休",
        "法休",
        "入职交五险",
        "交五险",
        "提供资源",
        "无责底薪",
        "无责",
    ):
        text = text.replace(noisy, "")
    text = SPACE_PATTERN.sub(" ", text).strip()
    return text.strip(" -_/|，,；;、")


def normalize_job_title(value: Any) -> str:
    text = clean_text(value)
    text = text.replace("　", " ")
    text = text.replace("JAVA", "Java").replace("java", "Java")
    text = text.replace("UI设计", "UI设计师")
    text = text.replace("平面设计 ", "平面设计师")
    text = text.replace("软体工程师", "软件工程师")
    text = text.replace("程式员", "程序员")
    text = text.replace("行政文员", "文员")
    text = text.replace("文秘", "秘书")
    text = text.replace("客服专员", "客服")
    text = text.replace("客户服务", "客服")
    text = text.replace("电话客服", "客服")
    text = text.replace("电商运营专员", "电商运营")
    text = text.replace("新媒体运营专员", "新媒体运营")
    text = text.replace("短视频运营专员", "短视频运营")
    text = text.replace("测试工程师", "软件测试工程师")
    text = text.replace("前端工程师", "前端开发工程师")
    text = text.replace("后端工程师", "后端开发工程师")
    text = text.replace("Java工程师", "Java开发工程师")
    text = text.replace("会计专员", "会计")
    text = text.replace("财务会计", "会计")
    text = text.replace("出纳员", "出纳")

    for suffix in TITLE_SUFFIXES:
        if text.startswith(suffix) and len(text) > len(suffix) + 1:
            text = text[len(suffix) :]

    if text.endswith("岗位"):
        text = text[:-2]
    if text.endswith("人员") and len(text) > 4:
        text = text[:-2]
    return text.strip()


def split_cn_list(value: Any) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    parts = [clean_text(part) for part in SPLIT_PATTERN.split(text)]
    return [part for part in parts if is_useful_job_text(part)]


def is_useful_job_text(value: Any) -> bool:
    text = normalize_job_title(value)
    if not text or text in GENERIC_OR_NOISE_TERMS:
        return False
    if len(text) <= 1:
        return False
    if text.isdigit():
        return False
    return True


def extract_candidate_evidence(snapshot: dict[str, Any]) -> list[CandidateEvidence]:
    profession = snapshot.get("profession") or {}
    macro = snapshot.get("macro_employment") or {}
    profession_id = str(profession.get("id") or "")
    major_code = str(profession.get("code") or "")
    major_name = str(profession.get("name") or "")
    major_level = str(profession.get("level") or "")
    evidence: list[CandidateEvidence] = []

    for row in macro.get("job_direction_distribution") or []:
        label = clean_text(row.get("label"))
        rate = to_float(row.get("rate_percent"), default=0.0)
        detail_jobs = row.get("detail_jobs") or []
        detail_parts: list[str] = []
        for detail in detail_jobs:
            detail_parts.extend(split_cn_list(detail))
        if detail_parts:
            per_job_weight = max(rate, 1.0) / max(len(detail_parts), 1)
            for job_text in detail_parts:
                evidence.append(
                    CandidateEvidence(
                        profession_id=profession_id,
                        major_code=major_code,
                        major_name=major_name,
                        major_level=major_level,
                        raw_job_text=job_text,
                        normalized_job_title=normalize_job_title(job_text),
                        candidate_type="job_title",
                        source_field="job_direction_distribution.detail_jobs",
                        field_quality_weight=1.0,
                        raw_weight=per_job_weight,
                        job_group=label,
                    )
                )
        if is_useful_job_text(label):
            evidence.append(
                CandidateEvidence(
                    profession_id=profession_id,
                    major_code=major_code,
                    major_name=major_name,
                    major_level=major_level,
                    raw_job_text=label,
                    normalized_job_title=normalize_job_title(label),
                    candidate_type="job_group",
                    source_field="job_direction_distribution.label",
                    field_quality_weight=0.85,
                    raw_weight=max(rate, 1.0),
                    job_group=label,
                )
            )

    samples = snapshot.get("job_posting_samples") or []
    sample_weight = 100.0 / max(len(samples), 1)
    for sample in samples:
        title = clean_text(sample.get("job_title"))
        if not is_useful_job_text(title):
            continue
        evidence.append(
            CandidateEvidence(
                profession_id=profession_id,
                major_code=major_code,
                major_name=major_name,
                major_level=major_level,
                raw_job_text=title,
                normalized_job_title=normalize_job_title(title),
                candidate_type="job_posting_sample",
                source_field="job_posting_samples.job_title",
                field_quality_weight=0.7,
                raw_weight=sample_weight,
                sample_city=clean_text(sample.get("city")),
                sample_industry=clean_text(sample.get("industry")),
                sample_education=clean_text(sample.get("education")),
                sample_experience=clean_text(sample.get("experience")),
                sample_skills=[clean_text(skill) for skill in sample.get("skills") or []],
            )
        )

    for row in macro.get("industry_distribution") or []:
        label = clean_text(row.get("label"))
        rate = to_float(row.get("rate_percent"), default=0.0)
        if not is_useful_job_text(label):
            continue
        field_weight = 0.25 if normalize_job_title(label) in GENERIC_INDUSTRY_TERMS else 0.45
        evidence.append(
            CandidateEvidence(
                profession_id=profession_id,
                major_code=major_code,
                major_name=major_name,
                major_level=major_level,
                raw_job_text=label,
                normalized_job_title=normalize_job_title(label),
                candidate_type="industry_or_direction",
                source_field="industry_distribution.label",
                field_quality_weight=field_weight,
                raw_weight=max(rate, 1.0),
                industry_label=label,
            )
        )

    return [
        item
        for item in evidence
        if item.normalized_job_title and item.normalized_job_title not in GENERIC_OR_NOISE_TERMS
    ]


def aggregate_candidates(
    evidence_items: Iterable[CandidateEvidence],
) -> list[AggregatedJobCandidate]:
    by_key: dict[tuple[str, str], AggregatedJobCandidate] = {}
    for item in evidence_items:
        key = (item.profession_id or item.major_code or item.major_name, item.normalized_job_title)
        if key not in by_key:
            by_key[key] = AggregatedJobCandidate(
                profession_id=item.profession_id,
                major_code=item.major_code,
                major_name=item.major_name,
                major_level=item.major_level,
                normalized_job_title=item.normalized_job_title,
                candidate_type=item.candidate_type,
            )
        by_key[key].add(item)
    return sorted(
        by_key.values(),
        key=lambda row: (row.major_level, row.major_code, row.major_name, -row.source_weight),
    )


def score_job_title(title: str) -> JobScore:
    text = normalize_job_title(title)
    rules = [
        (
            "software_development",
            ["软件", "开发", "程序员", "Java", "前端", "后端", "全栈", "测试", "运维", "算法", "数据工程", "数据库"],
            92,
            72,
            20,
            10,
            45,
            35,
            92,
            ["代码生成、测试脚本、文档和运维脚本高度受 AI 影响", "复杂系统责任和业务协同会降低完全替代风险"],
            ["代码/软件", "高AI暴露", "工程协同阻力"],
        ),
        (
            "content_language",
            ["文案", "编辑", "校对", "翻译", "新媒体", "内容", "记者", "采编", "撰稿", "出版", "秘书", "文员", "行政助理", "资料员"],
            93,
            84,
            10,
            5,
            25,
            20,
            94,
            ["文本生成、摘要、改写、翻译和资料整理任务可被 AI 大幅自动化", "深度采访、现场判断和组织责任仍需人工"],
            ["文本内容", "重复文档", "高AI暴露"],
        ),
        (
            "marketing_operations",
            ["运营", "电商", "SEO", "SEM", "投放", "推广", "市场", "品牌", "策划", "广告", "用户增长", "社群"],
            88,
            76,
            10,
            5,
            40,
            25,
            90,
            ["营销素材、投放文案、数据看板和活动方案容易被 AI 压缩", "客户理解、预算责任和组织协同会保留人工价值"],
            ["市场运营", "内容生产", "数据看板"],
        ),
        (
            "customer_service_sales",
            ["客服", "呼叫", "电话销售", "销售助理", "销售专员", "销售代表", "渠道", "招商", "商务专员"],
            84,
            72,
            8,
            5,
            55,
            25,
            86,
            ["标准化问答、线索跟进和话术生成容易被 AI 替代或自动化", "复杂成交和长期客户信任仍有明显人际阻力"],
            ["客服销售", "标准话术", "人际信任阻力"],
        ),
        (
            "finance_accounting",
            ["会计", "出纳", "财务", "审计", "税务", "核算", "成本", "统计", "报表"],
            88,
            74,
            10,
            45,
            25,
            55,
            88,
            ["凭证、核算、报表和基础审计流程高度结构化，AI 和自动化工具替代压力较高", "签字责任、合规和复杂判断会降低完全替代风险"],
            ["财务核算", "结构化流程", "合规责任"],
        ),
        (
            "data_analysis",
            ["数据分析", "数据运营", "商业分析", "BI", "报表分析", "数据处理", "信息管理"],
            92,
            78,
            8,
            5,
            35,
            35,
            92,
            ["数据清洗、图表、SQL 辅助和报告撰写高度受 AI 影响", "业务定义、指标责任和跨部门解释仍需要人工"],
            ["数据分析", "报表", "高AI暴露"],
        ),
        (
            "design_media",
            ["平面设计", "视觉", "美工", "UI", "插画", "剪辑", "后期", "动画", "建模", "包装设计", "广告设计", "室内设计", "家具设计"],
            86,
            70,
            20,
            5,
            45,
            25,
            88,
            ["素材生成、草图、排版和基础视觉产出受到生成式 AI 明显冲击", "品牌判断、现场沟通和最终审美责任仍保留人工价值"],
            ["设计创作", "生成式AI", "审美沟通阻力"],
        ),
        (
            "legal_compliance",
            ["律师", "法务", "法律", "合规", "知识产权", "专利代理", "合同"],
            88,
            62,
            5,
            75,
            45,
            80,
            90,
            ["检索、合同初稿和合规材料可被 AI 强辅助", "执业资格、法律责任和客户信任显著限制完全替代"],
            ["法律合规", "资质阻力", "责任阻力"],
        ),
        (
            "education_training",
            ["教师", "老师", "教学", "教研", "培训", "课程顾问", "辅导员", "班主任", "讲师"],
            78,
            52,
            10,
            55,
            70,
            55,
            86,
            ["备课、题目生成和作业批改可被 AI 强辅助", "育人责任、课堂管理和长期信任关系限制完全替代"],
            ["教育培训", "人际信任阻力", "资质阻力"],
        ),
        (
            "medical_health",
            ["医生", "医师", "护士", "护理", "药师", "医技", "康复", "检验师", "影像", "临床", "口腔", "兽医"],
            80,
            46,
            45,
            82,
            65,
            85,
            88,
            ["医学文书、影像辅助和知识检索会被 AI 强辅助", "执业资质、线下处置、医疗责任和患者信任使完全替代风险较低"],
            ["医疗健康", "强资质", "线下处置"],
        ),
        (
            "engineering_rnd",
            ["工程师", "研发", "工艺", "产品经理", "项目工程", "结构设计", "机械设计", "电气设计", "硬件", "自动化", "嵌入式"],
            76,
            54,
            45,
            25,
            45,
            55,
            80,
            ["方案、制图、仿真、文档和代码可被 AI 辅助", "工程现场、设备约束、质量责任和跨团队协作限制直接替代"],
            ["工程研发", "现场责任", "AI辅助高"],
        ),
        (
            "onsite_operation",
            ["操作工", "普工", "技工", "维修", "装配", "施工", "安装", "电工", "焊工", "钳工", "车工", "铣工", "数控", "机修", "调试", "驾驶", "仓储", "物流"],
            45,
            28,
            88,
            35,
            25,
            55,
            62,
            ["现场操作、设备处理和安全责任较强，短期内更偏 AI 辅助而非直接替代", "标准流程和故障诊断会被 AI 工具增强"],
            ["线下操作", "设备场景", "低替代"],
        ),
        (
            "quality_lab",
            ["质检", "质量", "检测", "检验", "实验", "化验", "分析员", "测试员", "品控"],
            62,
            42,
            65,
            35,
            25,
            60,
            70,
            ["检测报告、异常归因和标准查询可被 AI 辅助", "采样、实验、设备操作和质量责任限制完全替代"],
            ["检测质控", "线下设备", "责任阻力"],
        ),
        (
            "public_sector_security",
            ["公务员", "事业单位", "民警", "警察", "公安", "消防", "安保", "军队", "辅警"],
            62,
            35,
            55,
            75,
            65,
            80,
            70,
            ["材料处理和信息检索可被 AI 辅助", "公共权力、执法责任、编制和组织流程限制直接替代"],
            ["公共部门", "责任阻力", "组织流程"],
        ),
        (
            "agriculture_field",
            ["农艺", "园艺", "畜牧", "养殖", "水产", "林业", "园林", "种植", "动物", "宠物美容"],
            55,
            34,
            78,
            35,
            35,
            55,
            66,
            ["知识问答、病虫害识别和经营建议可被 AI 辅助", "田间、养殖、动植物照护和现场处置限制替代"],
            ["农业现场", "线下照护", "AI辅助"],
        ),
    ]

    matched: list[tuple[str, float, float, float, float, float, float, float, list[str], list[str]]] = []
    for category, keywords, exposure, automation, physical, license_, trust, liability, assist, reasons, tags in rules:
        hits = [keyword for keyword in keywords if keyword and keyword.lower() in text.lower()]
        if hits:
            specificity = min(1.0, 0.78 + 0.08 * len(hits) + min(len(text), 10) / 100)
            matched.append(
                (
                    category,
                    exposure * specificity,
                    automation * specificity,
                    physical,
                    license_,
                    trust,
                    liability,
                    assist * specificity,
                    reasons,
                    tags + [f"命中:{'、'.join(hits[:3])}"],
                )
            )

    if not matched:
        if text in GENERIC_INDUSTRY_TERMS:
            return build_job_score(
                text,
                category="generic_industry",
                exposure=58,
                automation=42,
                physical=35,
                license_=20,
                trust=35,
                liability=30,
                assist=62,
                confidence=45,
                reasons=["该条目更像行业方向而非具体岗位，只能作为低置信度市场信号"],
                tags=["行业词", "低置信度"],
            )
        return build_job_score(
            text,
            category="unknown_or_mixed",
            exposure=60,
            automation=45,
            physical=35,
            license_=20,
            trust=35,
            liability=35,
            assist=65,
            confidence=50,
            reasons=["未命中明确岗位规则，使用中性保守分作为初筛"],
            tags=["未分类", "需复核"],
        )

    exposure = clamp(sum(row[1] for row in matched) / len(matched), 0, 100)
    automation = clamp(sum(row[2] for row in matched) / len(matched), 0, 100)
    physical = max(row[3] for row in matched)
    license_ = max(row[4] for row in matched)
    trust = max(row[5] for row in matched)
    liability = max(row[6] for row in matched)
    assist = clamp(sum(row[7] for row in matched) / len(matched), 0, 100)
    reasons = distinct_preserve_order(reason for row in matched for reason in row[8])
    tags = distinct_preserve_order(tag for row in matched for tag in row[9])
    confidence = clamp(62 + 8 * len(matched) + min(len(text), 12), 55, 95)
    category = "+".join(distinct_preserve_order(row[0] for row in matched))
    return build_job_score(
        text,
        category=category,
        exposure=exposure,
        automation=automation,
        physical=physical,
        license_=license_,
        trust=trust,
        liability=liability,
        assist=assist,
        confidence=confidence,
        reasons=reasons,
        tags=tags,
    )


def build_job_score(
    title: str,
    *,
    category: str,
    exposure: float,
    automation: float,
    physical: float,
    license_: float,
    trust: float,
    liability: float,
    assist: float,
    confidence: float,
    reasons: list[str],
    tags: list[str],
) -> JobScore:
    barrier = max(physical, license_, trust, liability)
    # Keep a small exposure component so high-exposure jobs remain visibly risky,
    # but make the barrier dominate in medical, legal, field, and public roles.
    final_risk = automation * (1 - 0.0065 * barrier) + exposure * 0.15
    final_risk = clamp(final_risk, 0, 100)
    return JobScore(
        normalized_job_title=title,
        ai_exposure_score=round(exposure, 2),
        automation_score=round(automation, 2),
        physical_barrier_score=round(physical, 2),
        license_barrier_score=round(license_, 2),
        human_trust_barrier_score=round(trust, 2),
        liability_barrier_score=round(liability, 2),
        final_job_risk_score=round(final_risk, 2),
        ai_assist_score=round(assist, 2),
        confidence_score=round(confidence, 2),
        risk_level=risk_level(final_risk),
        category=category,
        tags=tags,
        reasons=reasons,
    )


def build_major_profiles(
    candidates: list[AggregatedJobCandidate],
) -> tuple[list[MajorProfile], list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[str, list[AggregatedJobCandidate]] = defaultdict(list)
    for candidate in candidates:
        key = candidate.profession_id or candidate.major_code or candidate.major_name
        grouped[key].append(candidate)

    candidate_rows: list[dict[str, Any]] = []
    job_seed_by_title: dict[str, dict[str, Any]] = {}
    profiles: list[MajorProfile] = []

    for major_candidates in grouped.values():
        total_weight = sum(max(row.source_weight, 0.1) for row in major_candidates)
        if total_weight <= 0:
            continue

        scored_rows: list[tuple[AggregatedJobCandidate, JobScore, float]] = []
        for candidate in major_candidates:
            score = score_job_title(candidate.normalized_job_title)
            normalized_weight = max(candidate.source_weight, 0.1) / total_weight
            scored_rows.append((candidate, score, normalized_weight))
            job_seed_by_title[score.normalized_job_title] = job_score_to_seed_row(score)
            candidate_rows.append(candidate_to_row(candidate, score, normalized_weight))

        ai_replacement_score = weighted_average(
            (score.final_job_risk_score, weight) for _, score, weight in scored_rows
        )
        ai_exposure_score = weighted_average(
            (score.ai_exposure_score, weight) for _, score, weight in scored_rows
        )
        automation_score = weighted_average(
            (score.automation_score, weight) for _, score, weight in scored_rows
        )
        human_barrier_score = weighted_average(
            (score.human_barrier_score, weight) for _, score, weight in scored_rows
        )
        ai_assist_value_score = weighted_average(
            (score.ai_assist_score, weight) for _, score, weight in scored_rows
        )
        evidence_count = sum(candidate.evidence_count for candidate, _, _ in scored_rows)
        avg_score_confidence = weighted_average(
            (score.confidence_score, weight) for _, score, weight in scored_rows
        )
        source_fields = distinct_preserve_order(
            field
            for candidate, _, _ in scored_rows
            for field in candidate.source_fields.keys()
        )
        confidence = major_confidence(
            candidate_count=len(scored_rows),
            evidence_count=evidence_count,
            avg_score_confidence=avg_score_confidence,
            source_fields=source_fields,
        )

        top_risky = top_job_dicts(
            scored_rows,
            sort_key=lambda item: item[1].final_job_risk_score * (0.45 + item[2]),
            reverse=True,
            limit=10,
        )
        top_resilient = top_job_dicts(
            [
                item
                for item in scored_rows
                if item[1].human_barrier_score >= 55 or item[1].final_job_risk_score < 45
            ],
            sort_key=lambda item: (item[1].human_barrier_score, item[2]),
            reverse=True,
            limit=8,
        )
        main_reasons = summarize_major_reasons(scored_rows)
        first = major_candidates[0]
        profiles.append(
            MajorProfile(
                rank=0,
                profession_id=first.profession_id,
                major_code=first.major_code,
                major_name=first.major_name,
                major_level=first.major_level,
                ai_replacement_score=round(ai_replacement_score, 2),
                ai_replacement_level=risk_level(ai_replacement_score),
                ai_exposure_score=round(ai_exposure_score, 2),
                automation_score=round(automation_score, 2),
                human_barrier_score=round(human_barrier_score, 2),
                ai_assist_value_score=round(ai_assist_value_score, 2),
                confidence_score=round(confidence, 2),
                candidate_count=len(scored_rows),
                evidence_count=evidence_count,
                source_fields=source_fields,
                top_risky_jobs=top_risky,
                top_resilient_jobs=top_resilient,
                main_reasons=main_reasons,
            )
        )

    profiles.sort(
        key=lambda row: (
            -row.ai_replacement_score,
            -row.confidence_score,
            row.major_level,
            row.major_code,
        )
    )
    for index, profile in enumerate(profiles, start=1):
        profile.rank = index

    job_seed_rows = sorted(
        job_seed_by_title.values(),
        key=lambda row: (-float(row["final_job_risk_score"]), row["normalized_job_title"]),
    )
    return profiles, candidate_rows, job_seed_rows


def candidate_to_row(
    candidate: AggregatedJobCandidate, score: JobScore, normalized_weight: float
) -> dict[str, Any]:
    return {
        "data_version": DATA_VERSION,
        "profession_id": candidate.profession_id,
        "major_code": candidate.major_code,
        "major_name": candidate.major_name,
        "level": candidate.major_level,
        "normalized_job_title": candidate.normalized_job_title,
        "candidate_type": candidate.candidate_type,
        "source_weight": round(candidate.source_weight, 4),
        "normalized_weight_percent": round(normalized_weight * 100, 4),
        "evidence_count": candidate.evidence_count,
        "raw_job_texts": join_counter(candidate.raw_job_texts, 8),
        "job_groups": join_counter(candidate.job_groups, 6),
        "industry_labels": join_counter(candidate.industry_labels, 6),
        "source_fields": join_counter(candidate.source_fields, 6),
        "sample_cities": join_counter(candidate.sample_cities, 8),
        "sample_industries": join_counter(candidate.sample_industries, 8),
        "sample_educations": join_counter(candidate.sample_educations, 6),
        "sample_experiences": join_counter(candidate.sample_experiences, 6),
        "sample_skills": join_counter(candidate.sample_skills, 15),
        "ai_exposure_score": score.ai_exposure_score,
        "automation_score": score.automation_score,
        "human_barrier_score": score.human_barrier_score,
        "physical_barrier_score": score.physical_barrier_score,
        "license_barrier_score": score.license_barrier_score,
        "human_trust_barrier_score": score.human_trust_barrier_score,
        "liability_barrier_score": score.liability_barrier_score,
        "ai_assist_score": score.ai_assist_score,
        "final_job_risk_score": score.final_job_risk_score,
        "risk_level": score.risk_level,
        "risk_category": score.category,
        "risk_tags": "；".join(score.tags),
        "risk_reasons": "；".join(score.reasons),
        "scoring_confidence": score.confidence_score,
        "source_level": MARKET_SOURCE_LEVEL,
        "data_scope": MARKET_SCOPE,
    }


def job_score_to_seed_row(score: JobScore) -> dict[str, Any]:
    return {
        "data_version": DATA_VERSION,
        "normalized_job_title": score.normalized_job_title,
        "risk_category": score.category,
        "ai_exposure_score": score.ai_exposure_score,
        "automation_score": score.automation_score,
        "human_barrier_score": score.human_barrier_score,
        "physical_barrier_score": score.physical_barrier_score,
        "license_barrier_score": score.license_barrier_score,
        "human_trust_barrier_score": score.human_trust_barrier_score,
        "liability_barrier_score": score.liability_barrier_score,
        "ai_assist_score": score.ai_assist_score,
        "final_job_risk_score": score.final_job_risk_score,
        "risk_level": score.risk_level,
        "risk_tags": "；".join(score.tags),
        "risk_reasons": "；".join(score.reasons),
        "scoring_confidence": score.confidence_score,
        "scoring_method": "keyword_rule_with_china_barrier_adjustment",
    }


def major_profile_to_row(profile: MajorProfile) -> dict[str, Any]:
    return {
        "data_version": DATA_VERSION,
        "rank": profile.rank,
        "profession_id": profile.profession_id,
        "major_code": profile.major_code,
        "major_name": profile.major_name,
        "level": profile.major_level,
        "ai_replacement_score": profile.ai_replacement_score,
        "ai_replacement_level": profile.ai_replacement_level,
        "ai_exposure_score": profile.ai_exposure_score,
        "automation_score": profile.automation_score,
        "human_barrier_score": profile.human_barrier_score,
        "ai_assist_value_score": profile.ai_assist_value_score,
        "confidence_score": profile.confidence_score,
        "candidate_count": profile.candidate_count,
        "evidence_count": profile.evidence_count,
        "source_fields": "；".join(profile.source_fields),
        "top_risky_jobs": format_job_summary(profile.top_risky_jobs),
        "top_resilient_jobs": format_job_summary(profile.top_resilient_jobs),
        "main_reasons": "；".join(profile.main_reasons),
        "source_level": MARKET_SOURCE_LEVEL,
        "data_scope": MARKET_SCOPE,
        "warning": "第三方招聘市场观察和规则化初筛，不代表官方就业去向或确定性预测。",
    }


def major_profile_to_json(profile: MajorProfile) -> dict[str, Any]:
    return {
        **major_profile_to_row(profile),
        "source_fields": profile.source_fields,
        "top_risky_jobs": profile.top_risky_jobs,
        "top_resilient_jobs": profile.top_resilient_jobs,
        "main_reasons": profile.main_reasons,
    }


def top_job_dicts(
    rows: list[tuple[AggregatedJobCandidate, JobScore, float]],
    *,
    sort_key,
    reverse: bool,
    limit: int,
) -> list[dict[str, Any]]:
    sorted_rows = sorted(rows, key=sort_key, reverse=reverse)[:limit]
    return [
        {
            "job": candidate.normalized_job_title,
            "risk_score": score.final_job_risk_score,
            "risk_level": score.risk_level,
            "weight_percent": round(weight * 100, 2),
            "barrier_score": score.human_barrier_score,
            "tags": score.tags[:5],
            "reasons": score.reasons[:2],
        }
        for candidate, score, weight in sorted_rows
    ]


def summarize_major_reasons(
    rows: list[tuple[AggregatedJobCandidate, JobScore, float]], limit: int = 6
) -> list[str]:
    reason_weights: dict[str, float] = defaultdict(float)
    for _, score, weight in rows:
        for reason in score.reasons:
            reason_weights[reason] += weight * max(score.final_job_risk_score, 1)
    return [
        reason
        for reason, _ in sorted(reason_weights.items(), key=lambda item: -item[1])[:limit]
    ]


def major_confidence(
    *,
    candidate_count: int,
    evidence_count: int,
    avg_score_confidence: float,
    source_fields: list[str],
) -> float:
    coverage = clamp(35 + math.log1p(candidate_count) * 14 + math.log1p(evidence_count) * 8, 0, 100)
    if "job_direction_distribution.detail_jobs" in source_fields:
        source_quality = 76
    elif "job_direction_distribution.label" in source_fields:
        source_quality = 68
    else:
        source_quality = 58
    if "job_posting_samples.job_title" in source_fields:
        source_quality += 6
    if "industry_distribution.label" in source_fields and len(source_fields) == 1:
        source_quality -= 14
    return clamp(coverage * 0.35 + avg_score_confidence * 0.4 + source_quality * 0.25, 0, 100)


def load_snapshots(input_dir: Path) -> list[dict[str, Any]]:
    snapshots = []
    for path in sorted(input_dir.glob("profession_*_market_snapshot.json")):
        try:
            with path.open("r", encoding="utf-8-sig") as handle:
                snapshots.append(json.load(handle))
        except (OSError, json.JSONDecodeError):
            continue
    return snapshots


def build_dataset(input_dir: Path) -> tuple[list[MajorProfile], list[dict[str, Any]], list[dict[str, Any]]]:
    snapshots = load_snapshots(input_dir)
    evidence: list[CandidateEvidence] = []
    for snapshot in snapshots:
        evidence.extend(extract_candidate_evidence(snapshot))
    candidates = aggregate_candidates(evidence)
    return build_major_profiles(candidates)


def write_dataset(
    profiles: list[MajorProfile],
    candidate_rows: list[dict[str, Any]],
    job_seed_rows: list[dict[str, Any]],
    output_dir: Path,
    report_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    profile_rows = [major_profile_to_row(profile) for profile in profiles]
    profile_json_rows = [major_profile_to_json(profile) for profile in profiles]
    summary_rows = risk_summary_rows(profiles)

    write_csv(output_dir / "major_ai_replacement_ranking.csv", profile_rows)
    write_csv(output_dir / "major_ai_replacement_top100.csv", profile_rows[:100])
    write_csv(output_dir / "risk_level_summary.csv", summary_rows)
    write_jsonl(output_dir / "major_ai_replacement_ranking.jsonl", profile_json_rows)
    write_csv(output_dir / "major_job_candidates.csv", candidate_rows)
    write_csv(output_dir / "job_ai_risk_seed.csv", job_seed_rows)
    write_methodology(output_dir / "README.md", profiles, candidate_rows, job_seed_rows)
    write_summary_report(report_dir / "major_ai_replacement_summary.md", profiles)

    summary = {
        "data_version": DATA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile_count": len(profiles),
        "candidate_row_count": len(candidate_rows),
        "job_seed_count": len(job_seed_rows),
        "output_files": [
            str(output_dir / "major_ai_replacement_ranking.csv"),
            str(output_dir / "major_ai_replacement_top100.csv"),
            str(output_dir / "risk_level_summary.csv"),
            str(output_dir / "major_ai_replacement_ranking.jsonl"),
            str(output_dir / "major_job_candidates.csv"),
            str(output_dir / "job_ai_risk_seed.csv"),
            str(output_dir / "README.md"),
            str(report_dir / "major_ai_replacement_summary.md"),
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_methodology(
    path: Path,
    profiles: list[MajorProfile],
    candidate_rows: list[dict[str, Any]],
    job_seed_rows: list[dict[str, Any]],
) -> None:
    level_counts = Counter(profile.ai_replacement_level for profile in profiles)
    lines = [
        "# 专业 AI 替代风险独立数据集",
        "",
        f"- 数据版本：`{DATA_VERSION}`",
        f"- 专业画像数：{len(profiles)}",
        f"- 专业-岗位候选行数：{len(candidate_rows)}",
        f"- 岗位风险种子数：{len(job_seed_rows)}",
        "- 数据口径：第三方中文招聘市场观察 + 规则化 AI 替代风险初筛",
        "- 重要提醒：本数据集不代表官方就业去向，不代表确定性预测。",
        "",
        "## 文件",
        "",
        "- `major_ai_replacement_ranking.csv`: 专业级 AI 替代风险排序。",
        "- `major_ai_replacement_top100.csv`: Top100 高风险专业，便于快速查看。",
        "- `risk_level_summary.csv`: 按专业层次和风险等级统计。",
        "- `major_ai_replacement_ranking.jsonl`: 与 CSV 相同主数据，但保留嵌套岗位证据。",
        "- `major_job_candidates.csv`: 从专业市场快照抽取的专业-岗位候选明细。",
        "- `job_ai_risk_seed.csv`: 所有归一岗位的规则化 AI 风险评分种子。",
        "- `manifest.json`: 生成摘要。",
        "",
        "## 风险等级分布",
        "",
        "| 等级 | 专业数 |",
        "|---|---:|",
    ]
    for level in ["很高", "较高", "中等", "较低", "低"]:
        lines.append(f"| {level} | {level_counts.get(level, 0)} |")
    lines.extend(
        [
            "",
            "## 评分口径",
            "",
            "专业风险分由专业对应岗位的加权风险聚合得到：",
            "",
            "```text",
            "专业AI替代风险 = Σ(岗位权重 × 岗位AI替代风险)",
            "岗位AI替代风险 = 自动化分 × (1 - 0.0065 × 最大阻力分) + AI暴露分 × 0.15",
            "最大阻力分 = max(线下操作阻力, 资质阻力, 人际信任阻力, 责任阻力)",
            "```",
            "",
            "岗位权重来自 rysxai 专业市场快照中的岗位方向、招聘样本和行业方向。字段权重依次为：",
            "",
            "| 来源字段 | 说明 | 字段权重 |",
            "|---|---|---:|",
            "| `job_direction_distribution.detail_jobs` | 细分岗位名称 | 1.00 |",
            "| `job_direction_distribution.label` | 岗位族/方向 | 0.85 |",
            "| `job_posting_samples.job_title` | 招聘样本岗位 | 0.70 |",
            "| `industry_distribution.label` | 行业/方向兜底 | 0.45；泛行业词为 0.25 |",
            "",
            "## 主表字段",
            "",
            "| 字段 | 含义 |",
            "|---|---|",
            "| `rank` | 按 AI 替代风险从高到低排序。 |",
            "| `major_code` / `major_name` / `level` | 专业代码、名称和层次。 |",
            "| `ai_replacement_score` | 专业级 AI 替代风险聚合分。 |",
            "| `ai_replacement_level` | 风险等级：很高、较高、中等、较低、低。 |",
            "| `ai_exposure_score` | 专业常见岗位被 AI 影响的程度。 |",
            "| `automation_score` | 任务被 AI 独立完成的可能性。 |",
            "| `human_barrier_score` | 线下、资质、信任、责任阻力聚合分。 |",
            "| `ai_assist_value_score` | AI 作为辅助工具的价值。 |",
            "| `confidence_score` | 由候选岗位覆盖、证据数、评分规则置信度和来源字段综合得到。 |",
            "| `top_risky_jobs` | 对专业分数贡献较高的风险岗位。 |",
            "| `top_resilient_jobs` | 阻力较高或替代风险较低的岗位。 |",
            "| `main_reasons` | 专业级主要风险解释。 |",
            "",
            "## 使用边界",
            "",
            "- 高分表示该专业常见岗位中的文本、数据、内容、流程、代码等任务更容易被 AI 压缩。",
            "- 低分不表示该专业不受 AI 影响，只表示完全替代阻力更强。",
            "- 医疗、法律、教育、工程、公共部门等岗位的 AI 辅助价值可能很高，但替代风险会被资质、责任和线下场景下调。",
            "- 第一版是规则化初筛，应优先用于排序、抽样复核和后续数据采集，不应直接作为面向学生的最终建议。",
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def risk_summary_rows(profiles: list[MajorProfile]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str]] = Counter(
        (profile.major_level or "未知", profile.ai_replacement_level)
        for profile in profiles
    )
    rows: list[dict[str, Any]] = []
    for level in sorted({profile.major_level or "未知" for profile in profiles}):
        total = sum(count for (row_level, _), count in counts.items() if row_level == level)
        for risk in ["很高", "较高", "中等", "较低", "低"]:
            count = counts.get((level, risk), 0)
            rows.append(
                {
                    "data_version": DATA_VERSION,
                    "level": level,
                    "ai_replacement_level": risk,
                    "major_count": count,
                    "level_total": total,
                    "share_percent": round(count / total * 100, 2) if total else 0.0,
                }
            )
    total_profiles = len(profiles)
    for risk in ["很高", "较高", "中等", "较低", "低"]:
        count = sum(1 for profile in profiles if profile.ai_replacement_level == risk)
        rows.append(
            {
                "data_version": DATA_VERSION,
                "level": "全部",
                "ai_replacement_level": risk,
                "major_count": count,
                "level_total": total_profiles,
                "share_percent": round(count / total_profiles * 100, 2)
                if total_profiles
                else 0.0,
            }
        )
    return rows


def write_summary_report(path: Path, profiles: list[MajorProfile], top_n: int = 80) -> None:
    lines = [
        "# 专业 AI 替代风险排序摘要",
        "",
        f"数据版本：`{DATA_VERSION}`",
        "",
        "## Top 高风险专业",
        "",
        "| 排名 | 专业 | 层次 | 风险分 | 等级 | 暴露度 | 自动化 | 阻力 | 置信度 | 主要高风险岗位 |",
        "|---:|---|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for profile in profiles[:top_n]:
        risky = "、".join(job["job"] for job in profile.top_risky_jobs[:5])
        lines.append(
            f"| {profile.rank} | {profile.major_name} | {profile.major_level} | "
            f"{profile.ai_replacement_score:.2f} | {profile.ai_replacement_level} | "
            f"{profile.ai_exposure_score:.2f} | {profile.automation_score:.2f} | "
            f"{profile.human_barrier_score:.2f} | {profile.confidence_score:.2f} | {risky} |"
        )
    lines.extend(
        [
            "",
            "## 解读",
            "",
            "- 排名靠前通常不是专业本身“没有价值”，而是其常见岗位里存在大量文本、内容、营销、客服、数据整理、基础设计或基础软件任务。",
            "- 对强资质、强线下、强责任岗位，AI 更可能先表现为辅助工具，而不是完整替代。",
            "- 结果应结合专业层次、地区、学校、学生能力结构继续修正。",
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def join_counter(counter: Counter[str], limit: int) -> str:
    return "；".join(
        f"{key}({count})"
        for key, count in counter.most_common(limit)
        if key and key not in GENERIC_OR_NOISE_TERMS
    )


def format_job_summary(jobs: list[dict[str, Any]]) -> str:
    return "；".join(
        f"{job['job']}({job['risk_score']:.1f}, 权重{job['weight_percent']:.1f}%)"
        for job in jobs
    )


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


def weighted_average(values: Iterable[tuple[float, float]]) -> float:
    pairs = [(float(value), float(weight)) for value, weight in values if weight > 0]
    total = sum(weight for _, weight in pairs)
    if total <= 0:
        return 0.0
    return sum(value * weight for value, weight in pairs) / total


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def distinct_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = clean_text(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build independent major AI replacement risk datasets from rysxai market snapshots."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = parser.parse_args(argv)

    profiles, candidate_rows, job_seed_rows = build_dataset(args.input_dir)
    summary = write_dataset(
        profiles,
        candidate_rows,
        job_seed_rows,
        args.output_dir,
        args.report_dir,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
