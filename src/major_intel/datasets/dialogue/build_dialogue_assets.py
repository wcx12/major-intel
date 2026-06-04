"""Build dialogue question and mentor-strategy assets for Major Intel.

The pipeline treats the pulled gaokao projects as read-only sources. It keeps
raw ASR text, a colloquial cleaned variant, and a normalized function-call test
question separate so downstream evaluation can preserve real user style without
letting messy ASR become unsupported facts.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


SOURCE_ROOT = "gaokao-zhiyuan-projects"

ALLOWED_TOOLS = {
    "school_lookup",
    "major_lookup",
    "school_profile",
    "major_profile",
    "school_major_profile",
    "score_to_rank",
    "rank_to_school_match",
    "rank_to_major_match",
    "admission_history",
    "major_market_reference",
    "civil_service_role_search",
    "specialty_group_lookup",
    "specialty_group_risk",
    "transfer_policy_lookup",
    "subject_requirement_lookup",
    "comparison_query",
    "employment_summary",
    "data_gap_detection",
}

QUESTION_FAMILY_TOOLS: dict[str, list[str]] = {
    "score_to_rank": ["score_to_rank"],
    "rank_to_school_match": ["score_to_rank", "rank_to_school_match", "data_gap_detection"],
    "rank_to_major_match": ["score_to_rank", "rank_to_major_match", "admission_history", "data_gap_detection"],
    "school_major_profile": ["school_lookup", "major_lookup", "school_major_profile", "data_gap_detection"],
    "major_profile": ["major_lookup", "major_profile", "major_market_reference", "data_gap_detection"],
    "employment_summary": ["school_lookup", "school_profile", "employment_summary", "data_gap_detection"],
    "major_market_reference": ["major_lookup", "major_profile", "major_market_reference", "data_gap_detection"],
    "civil_service_role_search": ["major_lookup", "civil_service_role_search", "data_gap_detection"],
    "specialty_group_risk": ["specialty_group_lookup", "specialty_group_risk", "admission_history", "data_gap_detection"],
    "transfer_policy_lookup": ["school_lookup", "transfer_policy_lookup", "data_gap_detection"],
    "subject_requirement_lookup": ["major_lookup", "subject_requirement_lookup", "data_gap_detection"],
    "comparison_query": ["school_lookup", "major_lookup", "comparison_query", "school_major_profile", "data_gap_detection"],
}

ALLOWED_QUESTION_FAMILIES = set(QUESTION_FAMILY_TOOLS)

QUESTION_FAMILY_ALIASES = {
    "school_profile": "school_major_profile",
    "school_lookup": "school_major_profile",
    "major_lookup": "major_profile",
    "admission_history": "rank_to_school_match",
    "employment": "employment_summary",
    "specialty_group_lookup": "specialty_group_risk",
}

PROVINCES = [
    "北京",
    "天津",
    "河北",
    "山西",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "上海",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "重庆",
    "四川",
    "贵州",
    "云南",
    "西藏",
    "陕西",
    "甘肃",
    "青海",
    "宁夏",
    "新疆",
]

CITY_KEYWORDS = [
    "北京",
    "上海",
    "杭州",
    "南京",
    "苏州",
    "深圳",
    "广州",
    "成都",
    "武汉",
    "西安",
    "长沙",
    "郑州",
    "天津",
    "重庆",
    "青岛",
    "宁波",
]

MAJOR_KEYWORDS = [
    "计算机",
    "软件",
    "电子信息",
    "通信",
    "电气",
    "自动化",
    "机械",
    "金融",
    "经济",
    "新闻",
    "法学",
    "汉语言",
    "师范",
    "医学",
    "口腔",
    "临床",
    "土木",
    "建筑",
    "会计",
    "财务",
    "护理",
    "药学",
    "兽医",
    "动物医学",
    "材料",
    "化工",
    "生物",
    "环境",
    "数学",
    "物理",
    "统计",
    "数据科学",
    "人工智能",
]

SCHOOL_HINTS = [
    "大学",
    "学院",
    "学校",
    "杭电",
    "广工",
    "深大",
    "南邮",
    "西电",
    "成电",
    "哈工大",
    "北邮",
]

QUESTION_PATTERNS = [
    r"能不能",
    r"能报",
    r"能上",
    r"怎么报",
    r"怎么填",
    r"怎么选",
    r"适不适合",
    r"推不推荐",
    r"推荐一下",
    r"能不能推荐",
    r"有没有.*推荐",
    r"怎么样",
    r"咋样",
    r"该不该",
    r"要不要",
    r"值不值得",
    r"分能",
    r"位次.*能",
    r"学.*好吗",
    r"想问",
    r"问一下",
    r"可以.*吗",
]

QUESTION_KEYWORDS = {
    "分数",
    "位次",
    "报",
    "志愿",
    "专业",
    "学校",
    "大学",
    "就业",
    "薪资",
    "工资",
    "考公",
    "考研",
    "转专业",
    "调剂",
    "专业组",
    "物理",
    "历史",
    "理科",
    "文科",
    "选科",
    "物化",
    "物生",
    "护理",
    "金融",
    "计算机",
}

QUESTION_CUES = {
    "吗",
    "什么",
    "哪些",
    "哪个",
    "怎么",
    "咋",
    "能不能",
    "可不可以",
    "适不适合",
    "想问",
    "问一下",
    "推荐一下",
    "能不能推荐",
    "有没有",
    "怎么样",
}

REQUIRED_SLOTS_BY_FAMILY: dict[str, list[str]] = {
    "rank_to_school_match": ["province", "subject_type", "score_or_rank"],
    "rank_to_major_match": ["province", "subject_type", "score_or_rank", "major_preference"],
    "school_major_profile": ["school_name", "major_name"],
    "major_profile": ["major_preference"],
    "major_market_reference": ["major_preference"],
    "specialty_group_risk": ["school_name_or_group", "province", "subject_type"],
    "transfer_policy_lookup": ["school_name"],
}


@dataclass(frozen=True)
class SourceInventoryItem:
    source_name: str
    source_type: str
    source_url: str
    license: str
    path: str
    is_real_dialogue: bool
    usable_for: list[str]
    risk_notes: list[str]
    attribution_note: str


def build_source_inventory(project_root: Path) -> list[dict[str, Any]]:
    def source_path(*parts: str) -> str:
        return str(Path(SOURCE_ROOT, *parts))

    items = [
        SourceInventoryItem(
            source_name="Xue-Feng-Skill",
            source_type="public_asr",
            source_url="https://github.com/SPA3K/Xue-Feng-Skill",
            license="MIT",
            path=source_path("Xue-Feng-Skill", "data", "transcripts"),
            is_real_dialogue=False,
            usable_for=["question_candidates", "strategy_reference", "style_reference"],
            risk_notes=["公开视频ASR，无说话人标注，需清洗后使用"],
            attribution_note="本数据集 152 条对话清洗记录均衍生自该仓库 data/transcripts/ 下的公开视频 ASR 转写。",
        ),
        SourceInventoryItem(
            source_name="zhangxuefeng-skillset",
            source_type="methodology_md",
            source_url="https://github.com/Eric-Yibo-Shen/zhangxuefeng-skillset",
            license="CC BY 4.0 for knowledge/prompts; separate code license in source repo",
            path=source_path("zhangxuefeng-skillset", "knowledge"),
            is_real_dialogue=False,
            usable_for=["mentor_strategy", "rag_methodology"],
            risk_notes=["社区整理的方法论，不是原始对话"],
            attribution_note="仅作为导师策略结构化参考，不作为真实对话来源。",
        ),
        SourceInventoryItem(
            source_name="gaokao-mentor-wisdom",
            source_type="quote_paraphrase",
            source_url="https://github.com/dongsheng123132/gaokao-mentor-wisdom",
            license="MIT",
            path=source_path("gaokao-mentor-wisdom"),
            is_real_dialogue=False,
            usable_for=["mentor_strategy", "quote_reference"],
            risk_notes=["语录多为转述，缺少原始视频链接和日期"],
            attribution_note="仅作为策略整理参考；不得把转述语录当作导师原始逐字回复。",
        ),
        SourceInventoryItem(
            source_name="zhangxuefeng-skill",
            source_type="style_prompt",
            source_url="https://github.com/alchaincyf/zhangxuefeng-skill",
            license="MIT",
            path=source_path("zhangxuefeng-skill"),
            is_real_dialogue=False,
            usable_for=["strategy_reference", "style_reference"],
            risk_notes=["风格和研究整理，不是事实数据源"],
            attribution_note="仅作为风格和策略参考，不作为事实数据源。",
        ),
        SourceInventoryItem(
            source_name="zhangxuefeng-skill-demo",
            source_type="synthetic_demo",
            source_url="https://github.com/alchaincyf/zhangxuefeng-skill",
            license="MIT",
            path=source_path("zhangxuefeng-skill", "examples", "demo-conversation.md"),
            is_real_dialogue=False,
            usable_for=["strategy_reference", "style_reference"],
            risk_notes=["模拟对话，禁止标记为真实对话"],
            attribution_note="该 demo 是模拟对话，禁止混入真实对话数据集。",
        ),
        SourceInventoryItem(
            source_name="zhang-xuefeng-memorial",
            source_type="methodology_md",
            source_url="https://github.com/bcefghj/zhang-xuefeng-memorial",
            license="CC BY 4.0",
            path=source_path("zhang-xuefeng-memorial", "knowledge"),
            is_real_dialogue=False,
            usable_for=["mentor_strategy"],
            risk_notes=["纪念和观点整理，不进入事实主链路"],
            attribution_note="仅作为观点整理参考，不进入事实主链路或真实对话主链路。",
        ),
    ]
    return [asdict(item) for item in items]


def load_asr_document(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        "bvid": str(data.get("bvid") or path.stem),
        "text": str(data.get("text") or ""),
        "segments": list(data.get("segments") or []),
    }


def compact_text(text: str) -> str:
    return re.sub(r"\s+", "", str(text or ""))


def light_clean_colloquial(text: str) -> str:
    cleaned = re.sub(r"\s+", "", str(text or ""))
    cleaned = re.sub(r"(这个|那个){3,}", r"\1", cleaned)
    cleaned = cleaned.replace("?", "？").replace("吗.", "吗？").strip("，。,. ")
    if cleaned and not cleaned.endswith(("？", "。", "！", "…")):
        cleaned += "？" if looks_like_question(cleaned) else "。"
    return cleaned


def looks_like_question(text: str) -> bool:
    normalized = compact_text(text)
    if len(normalized) < 6:
        return False
    if len(normalized) > 280:
        return False
    if "老婆" in normalized:
        return False
    if not any(keyword in normalized for keyword in QUESTION_KEYWORDS):
        return False
    if not any(cue in normalized for cue in QUESTION_CUES):
        return False
    return any(re.search(pattern, normalized) for pattern in QUESTION_PATTERNS)


def extract_question_candidates_from_segments(
    bvid: str,
    segments: list[dict[str, Any]],
    source_relpath: str,
    *,
    response_window: int = 6,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for index, segment in enumerate(segments):
        text = str(segment.get("text") or "").strip()
        if not looks_like_question(text):
            continue
        response_segments = segments[index + 1 : index + 1 + response_window]
        response_texts = [str(item.get("text") or "").strip() for item in response_segments]
        response_text = " ".join(item for item in response_texts if item)
        if len(compact_text(response_text)) < 12:
            continue
        last_response_index = index + len(response_segments)
        candidates.append(
            {
                "bvid": bvid,
                "segment_index": index,
                "question_raw": text,
                "response_candidate_raw": response_text,
                "source_type": "public_asr",
                "source_repo": "Xue-Feng-Skill",
                "source_ref": f"{source_relpath}#segment={index}",
                "response_candidate_ref": f"{source_relpath}#segments={index + 1}-{last_response_index}",
            }
        )
    return candidates


def chinese_digit_value(char: str) -> int:
    values = {
        "零": 0,
        "一": 1,
        "二": 2,
        "两": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
    }
    return values.get(char, 0)


def parse_spoken_score(text: str) -> int | None:
    match = re.search(r"([四五六七八九])百([零一二三四五六七八九十]{0,3})", text)
    if not match:
        return None
    score = chinese_digit_value(match.group(1)) * 100
    rest = match.group(2)
    if not rest:
        return score
    if rest == "十":
        return score + 10
    if rest.startswith("十"):
        return score + 10 + (chinese_digit_value(rest[1]) if len(rest) > 1 else 0)
    if len(rest) == 1:
        return score + chinese_digit_value(rest[0]) * 10
    if len(rest) >= 2:
        return score + chinese_digit_value(rest[0]) * 10 + chinese_digit_value(rest[1])
    return score


def extract_school_hint(text: str) -> str | None:
    compact = compact_text(text)
    for hint in SCHOOL_HINTS:
        if hint in compact:
            if hint in {"大学", "学院", "学校"}:
                match = re.search(r"([\u4e00-\u9fff]{2,12}(?:大学|学院|学校)(?:\([\u4e00-\u9fff]+\))?)", compact)
                if match:
                    return match.group(1)
            return hint
    return None


def extract_slots(text: str) -> dict[str, Any]:
    compact = compact_text(text)
    slots: dict[str, Any] = {
        "province": None,
        "subject_type": None,
        "score": None,
        "rank": None,
        "school_name": extract_school_hint(compact),
        "major_name": None,
        "major_preference": None,
        "city_preference": None,
        "career_preference": None,
    }
    for province in PROVINCES:
        if province in compact:
            slots["province"] = province
            break
    if "物理" in compact:
        slots["subject_type"] = "物理"
    elif "历史" in compact:
        slots["subject_type"] = "历史"
    elif "理科" in compact:
        slots["subject_type"] = "理科"
    elif "文科" in compact:
        slots["subject_type"] = "文科"
    elif "综合" in compact:
        slots["subject_type"] = "综合"

    score_match = re.search(r"(?<!\d)(\d{3})(?:多)?分", compact)
    if score_match:
        slots["score"] = int(score_match.group(1))
    else:
        spoken_score = parse_spoken_score(compact)
        if spoken_score:
            slots["score"] = spoken_score

    rank_match = re.search(r"(?<!\d)(\d{3,7})(?:多)?(?:位次|名|位)(?!分)", compact)
    if rank_match:
        slots["rank"] = int(rank_match.group(1))

    for major in MAJOR_KEYWORDS:
        if major in compact:
            slots["major_preference"] = major
            slots["major_name"] = major
            break

    for city in CITY_KEYWORDS:
        if city in compact and city != slots["province"]:
            slots["city_preference"] = city
            break

    for career in ["考公", "考研", "就业", "稳定", "进体制", "当老师", "医生", "读研", "保研"]:
        if career in compact:
            slots["career_preference"] = career
            break
    return slots


def infer_question_family(text: str, slots: dict[str, Any]) -> str:
    compact = compact_text(text)
    if "转专业" in compact:
        return "transfer_policy_lookup"
    if "专业组" in compact or "调剂" in compact or "冷门" in compact:
        return "specialty_group_risk"
    if "选科" in compact or "物化" in compact or "限物理" in compact:
        return "subject_requirement_lookup"
    if "对比" in compact or "哪个好" in compact or "哪个更好" in compact:
        return "comparison_query"
    if "考公" in compact or "体制" in compact:
        return "civil_service_role_search"
    if any(word in compact for word in ["就业", "薪资", "工资", "毕业去哪", "去哪里"]):
        return "major_market_reference" if slots.get("major_preference") else "employment_summary"
    if slots.get("school_name") and slots.get("major_preference") and any(word in compact for word in ["怎么样", "咋样", "值得", "好吗"]):
        return "school_major_profile"
    if slots.get("score") or slots.get("rank"):
        if slots.get("major_preference"):
            return "rank_to_major_match"
        return "rank_to_school_match"
    if any(word in compact for word in ["分数", "志愿", "怎么填", "怎么报"]):
        return "rank_to_school_match"
    if slots.get("major_preference"):
        return "major_profile"
    return "rank_to_school_match"


def missing_slots_for_family(family: str, slots: dict[str, Any]) -> list[str]:
    if family in {"rank_to_school_match", "rank_to_major_match"}:
        missing: list[str] = []
        if not slots.get("province"):
            missing.append("province")
        if not slots.get("subject_type"):
            missing.append("subject_type")
        if not slots.get("score") and not slots.get("rank"):
            missing.append("score_or_rank")
        if family == "rank_to_major_match" and not slots.get("major_preference"):
            missing.append("major_preference")
        return missing
    if family == "school_major_profile":
        return [slot for slot in ["school_name", "major_name"] if not slots.get(slot)]
    if family == "transfer_policy_lookup" and not slots.get("school_name"):
        return ["school_name"]
    return []


def classify_question(text: str) -> dict[str, Any]:
    slots = extract_slots(text)
    family = infer_question_family(text, slots)
    missing_slots = missing_slots_for_family(family, slots)
    return {
        "question_family": family,
        "slots": slots,
        "missing_slots": missing_slots,
        "expected_tools": QUESTION_FAMILY_TOOLS.get(family, ["data_gap_detection"]),
        "coverage_level": "partial" if missing_slots else "covered_or_partial",
    }


def normalize_question_text(text: str) -> str:
    normalized = light_clean_colloquial(text).strip("，。,. ")
    if not normalized.endswith("？"):
        normalized = normalized.rstrip("。！") + "？"
    return normalized


def formal_clean_question_text(text: str) -> str:
    formal = normalize_question_text(text)
    replacements = {
        "老师，": "",
        "老师": "",
        "我家孩子": "考生",
        "孩子": "考生",
        "能不能": "是否可以",
        "能报": "是否可以报考",
        "想问一下": "咨询",
        "想问问": "咨询",
        "咋样": "怎么样",
    }
    for old, new in replacements.items():
        formal = formal.replace(old, new)
    formal = re.sub(r"(那个|这个|就是|然后|呃|啊|嘛|吧){2,}", r"\1", formal)
    formal = re.sub(r"\s+", "", formal).strip("，。 ")
    if not formal.endswith("？"):
        formal = formal.rstrip("。！？") + "？"
    return formal


def style_features_for_question(text: str, slots: dict[str, Any]) -> list[str]:
    compact = compact_text(text)
    features = ["口语化"]
    if "老师" in compact:
        features.append("称呼导师")
    if "孩子" in compact or "家长" in compact or "我家" in compact:
        features.append("家长咨询")
    if slots.get("score") or slots.get("rank"):
        features.append("分数位次场景")
    if any(word in compact for word in ["冲", "稳", "保"]):
        features.append("冲稳保语境")
    return features


def quality_for_record(classification: dict[str, Any], raw: dict[str, Any]) -> tuple[str, float]:
    question_text = compact_text(raw.get("question_raw", ""))
    slots = classification.get("slots") or {}
    score = 0.46
    if raw.get("response_candidate_raw"):
        score += 0.10
    if not classification["missing_slots"]:
        score += 0.18
    elif len(classification["missing_slots"]) <= 2:
        score += 0.04
    if classification["question_family"] in QUESTION_FAMILY_TOOLS:
        score += 0.08
    if slots.get("score") or slots.get("rank") or slots.get("province") or slots.get("major_preference"):
        score += 0.08
    if 12 <= len(question_text) <= 180:
        score += 0.08
    if len(question_text) > 260:
        score -= 0.16
    if len(question_text) > 420:
        score -= 0.12
    if not re.search(r"问|吗|能|报|选|推荐|专业|学校|分|位次|就业|前景|考研|公务员", question_text):
        score -= 0.18
    if classification["missing_slots"]:
        score = min(score, 0.76)
    if len(question_text) > 260:
        score = min(score, 0.62)
    score = min(score, 0.98)
    if score >= 0.82:
        return "A", round(score, 2)
    if score >= 0.65:
        return "B", round(score, 2)
    if score >= 0.5:
        return "C", round(score, 2)
    return "D", round(score, 2)


def infer_mentor_strategy(response_text: str, question_family: str) -> list[str]:
    text = compact_text(response_text)
    strategies: list[str] = []
    if any(token in text for token in ["位次", "排名", "一分一段"]):
        strategies.append("先把分数转换成位次，再按近年录取位次判断冲稳保")
    if any(token in text for token in ["色弱", "受限", "体检"]):
        strategies.append("先查体检受限专业，避开不符合报考条件的方向")
    if any(token in text for token in ["考研", "读研", "两步到位", "一步到位"]):
        strategies.append("把本科录取和后续考研/升学分成两步规划")
    if any(token in text for token in ["就业", "工作", "前景", "钱景", "薪资"]):
        strategies.append("专业判断要落到就业面、岗位和长期发展，不只看名称")
    if any(token in text for token in ["专业组", "调剂", "大类"]):
        strategies.append("识别专业组和调剂风险，不能只看学校最低分")
    defaults = {
        "rank_to_school_match": "缺省市科类分数时先追问关键信息，再推荐学校",
        "rank_to_major_match": "按专业偏好筛候选，再结合院校层次和录取稳定性排序",
        "major_profile": "先说明专业学习内容、适合人群和就业去向，再给风险提示",
        "employment_summary": "用行业岗位和样本薪资做参考，避免承诺具体收入",
        "specialty_group_risk": "把专业组风险单独列出，提示需要招生章程和组内专业清单",
    }
    if not strategies and question_family in defaults:
        strategies.append(defaults[question_family])
    return strategies[:5]


def normalize_question_record(raw: dict[str, Any], index: int) -> dict[str, Any]:
    question_text = str(raw["question_raw"])
    classification = classify_question(question_text)
    quality_label, quality_score = quality_for_record(classification, raw)
    colloquial = light_clean_colloquial(question_text)
    return {
        "id": f"qb_{index:06d}",
        "question_raw": question_text,
        "question_colloquial_clean": colloquial,
        "question_formal_clean": formal_clean_question_text(question_text),
        "question_normalized": normalize_question_text(question_text),
        "question_family": classification["question_family"],
        "slots": classification["slots"],
        "missing_slots": classification["missing_slots"],
        "expected_tools": classification["expected_tools"],
        "coverage_level": classification["coverage_level"],
        "source_candidate_id": raw.get("id"),
        "source_type": raw["source_type"],
        "source_repo": raw["source_repo"],
        "source_ref": raw["source_ref"],
        "response_candidate_raw": raw.get("response_candidate_raw", ""),
        "response_candidate_ref": raw.get("response_candidate_ref"),
        "style_features": style_features_for_question(question_text, classification["slots"]),
        "mentor_strategy": infer_mentor_strategy(raw.get("response_candidate_raw", ""), classification["question_family"]),
        "cleaner": {"method": "rules", "model": None, "schema_version": "dialogue_cleaning_v1"},
        "quality_label": quality_label,
        "quality_score": quality_score,
    }


def validate_llm_cleaned_record(record: dict[str, Any]) -> dict[str, Any]:
    record = dict(record)
    if "question_colloquial_clean" not in record and "question_colformal_clean" in record:
        record["question_colloquial_clean"] = record["question_colformal_clean"]
    required = [
        "question_raw",
        "question_colloquial_clean",
        "question_formal_clean",
        "question_normalized",
        "question_family",
        "slots",
        "missing_slots",
        "expected_tools",
        "mentor_strategy",
        "style_features",
    ]
    for key in required:
        if key not in record:
            raise ValueError(f"missing required field: {key}")
    for key in ["question_raw", "question_colloquial_clean", "question_formal_clean", "question_normalized"]:
        if not str(record.get(key) or "").strip():
            raise ValueError(f"empty required field: {key}")
    record["question_family"] = QUESTION_FAMILY_ALIASES.get(str(record["question_family"]), record["question_family"])
    if record["question_family"] not in ALLOWED_QUESTION_FAMILIES:
        raise ValueError(f"unknown question family: {record['question_family']}")
    unknown_tools = [tool for tool in record.get("expected_tools", []) if tool not in ALLOWED_TOOLS]
    if unknown_tools:
        raise ValueError(f"unknown tool: {unknown_tools[0]}")
    for key in ["missing_slots", "mentor_strategy", "style_features", "expected_tools"]:
        if not isinstance(record.get(key), list):
            raise ValueError(f"{key} must be a list")
    if not isinstance(record.get("slots"), dict):
        raise ValueError("slots must be an object")
    if not record["question_normalized"].endswith("？"):
        record["question_normalized"] = record["question_normalized"].rstrip("。.!?？") + "？"
    return record


def build_llm_schema() -> dict[str, Any]:
    record_schema = {
        "type": "object",
        "additionalProperties": True,
        "required": [
            "question_raw",
            "question_colloquial_clean",
            "question_formal_clean",
            "question_normalized",
            "question_family",
            "slots",
            "missing_slots",
            "expected_tools",
            "mentor_strategy",
            "style_features",
            "quality_label",
            "quality_score",
        ],
        "properties": {
            "question_raw": {"type": "string"},
            "question_colloquial_clean": {"type": "string"},
            "question_formal_clean": {"type": "string"},
            "question_normalized": {"type": "string"},
            "question_family": {"type": "string", "enum": sorted(ALLOWED_QUESTION_FAMILIES)},
            "slots": {"type": "object"},
            "missing_slots": {"type": "array", "items": {"type": "string"}},
            "expected_tools": {"type": "array", "items": {"type": "string", "enum": sorted(ALLOWED_TOOLS)}},
            "mentor_strategy": {"type": "array", "items": {"type": "string"}},
            "style_features": {"type": "array", "items": {"type": "string"}},
            "quality_label": {"type": "string", "enum": ["A", "B", "C", "D"]},
            "quality_score": {"type": "number"},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["records"],
        "properties": {"records": {"type": "array", "items": record_schema}},
    }


def build_claude_prompt(candidates: list[dict[str, Any]], output_path: Path | str | None = None) -> str:
    payload = {
        "task": "clean_gaokao_dialogue_candidates",
        "output_contract": "Return ONLY minified JSON. The first character must be { and the last character must be }. No markdown, no bullets, no explanations. If output_file_path is provided, also overwrite that exact file with the same JSON.",
        "required_shape": {
            "records": [
                {
                    "candidate_id": "same candidate_id as input",
                    "question_raw": "original question text",
                    "question_colloquial_clean": "lightly cleaned colloquial Chinese; preserve speaking style",
                    "question_formal_clean": "formal written Chinese version; do not add facts",
                    "question_normalized": "normalized question for retrieval/function-call evaluation; must end with ? or ？",
                    "question_family": "one value from allowed_question_families",
                    "slots": "object with extracted facts only",
                    "missing_slots": "array of missing slot names",
                    "expected_tools": "array selected only from allowed_tools",
                    "mentor_strategy": "array of strategy summaries extracted from response_candidate_raw; not quotes",
                    "style_features": "array of style labels",
                    "quality_label": "A, B, C, or D",
                    "quality_score": "number between 0 and 1",
                }
            ]
        },
        "rules": [
            "保留原始口语风格，question_colloquial_clean 只做轻清洗，不要改成书面腔。",
            "为每条数据同时输出 question_formal_clean，把问题清洗成书面表达；不要改变事实、分数、地区、学校或专业。",
            "不得补不存在的省份、分数、位次、学校或专业。",
            "不得编造导师原话，mentor_strategy 只能抽取策略。",
            "expected_tools 只能从 allowed_tools 中选择。",
            "必须为每个 candidate_id 输出一条记录；如果原文不是有效问题，也要输出 D 级记录，并用原文轻清洗结果兜底填充必填文本字段，不得留空。",
            "不要输出 Insight、表格、解释、过程说明，也不要声称已完成；只输出 JSON。",
        ],
        "allowed_question_families": sorted(ALLOWED_QUESTION_FAMILIES),
        "allowed_tools": sorted(ALLOWED_TOOLS),
        "candidates": [candidate_for_claude_prompt(candidate) for candidate in candidates],
    }
    if output_path is not None:
        payload["output_file_path"] = str(output_path)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def truncate_for_prompt(value: Any, max_chars: int) -> str:
    text = compact_text(str(value or ""))
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "...[truncated]"


def candidate_for_claude_prompt(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": candidate.get("id"),
        "bvid": candidate.get("bvid"),
        "segment_index": candidate.get("segment_index"),
        "question_raw": str(candidate.get("question_raw") or ""),
        "response_candidate_raw": str(candidate.get("response_candidate_raw") or ""),
        "source_ref": candidate.get("source_ref"),
        "response_candidate_ref": candidate.get("response_candidate_ref"),
    }


def parse_json_payload(payload: str) -> Any:
    text = payload.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = min([pos for pos in [text.find("{"), text.find("[")] if pos >= 0], default=-1)
        end = max(text.rfind("}"), text.rfind("]"))
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def parse_json_values(payload: str) -> list[Any]:
    text = payload.strip()
    if not text:
        return []
    try:
        return [parse_json_payload(text)]
    except json.JSONDecodeError:
        pass

    values: list[Any] = []
    decoder = json.JSONDecoder()
    cursor = 0
    while cursor < len(text):
        starts = [pos for pos in [text.find("{", cursor), text.find("[", cursor)] if pos >= 0]
        if not starts:
            break
        start = min(starts)
        try:
            value, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            cursor = start + 1
            continue
        values.append(value)
        cursor = start + end
    return values


def records_from_claude_value(value: Any) -> list[dict[str, Any]] | None:
    if isinstance(value, dict):
        if "records" in value:
            return list(value["records"])
        if "candidate_id" in value and "question_raw" in value:
            return [value]
        result = value.get("result")
        if result is not None:
            return records_from_claude_value(result)
    if isinstance(value, list):
        return list(value)
    if isinstance(value, str):
        for parsed in parse_json_values(value):
            records = records_from_claude_value(parsed)
            if records is not None:
                return records
    return None


def parse_claude_stdout(stdout: str) -> list[dict[str, Any]]:
    for value in parse_json_values(stdout):
        records = records_from_claude_value(value)
        if records is not None:
            return records
    raise ValueError("Claude output did not contain records")


def resolve_claude_command() -> str:
    command_names = ["claude.cmd", "claude.exe", "claude"] if sys.platform == "win32" else ["claude"]
    for command_name in command_names:
        command_path = shutil.which(command_name)
        if command_path:
            return command_path
    raise RuntimeError("claude command not found")


def summarize_subprocess_error(exc: Exception) -> str:
    if isinstance(exc, subprocess.CalledProcessError):
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        parts = [f"exit={exc.returncode}"]
        if stderr:
            parts.append(f"stderr={stderr[:1000]}")
        if stdout:
            parts.append(f"stdout={stdout[:1000]}")
        return "; ".join(parts)
    if isinstance(exc, subprocess.TimeoutExpired):
        return f"timeout after {exc.timeout}s"
    return str(exc)


def read_jsonl_if_exists(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def append_jsonl_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def clean_candidates_with_claude(
    candidates: list[dict[str, Any]],
    batch_size: int = 20,
    timeout_seconds: int = 120,
    cache_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    claude_command = resolve_claude_command()
    cleaned_cache_path = cache_dir / "_claude_cleaned_cache.jsonl" if cache_dir else None
    failure_cache_path = cache_dir / "_claude_failures_cache.jsonl" if cache_dir else None
    cleaned: list[dict[str, Any]] = read_jsonl_if_exists(cleaned_cache_path) if cleaned_cache_path else []
    failures: list[dict[str, Any]] = []
    cleaned_ids = {
        str(record.get("source_candidate_id") or record.get("candidate_id") or record.get("id"))
        for record in cleaned
        if record.get("source_candidate_id") or record.get("candidate_id") or record.get("id")
    }
    pending_candidates = [candidate for candidate in candidates if str(candidate.get("id")) not in cleaned_ids]
    if cleaned_ids:
        print(f"Claude resume: loaded {len(cleaned_ids)} cached records, pending {len(pending_candidates)}", file=sys.stderr, flush=True)
    for batch_start in range(0, len(pending_candidates), batch_size):
        batch = pending_candidates[batch_start : batch_start + batch_size]
        batch_number = batch_start // batch_size + 1
        total_batches = (len(pending_candidates) + batch_size - 1) // batch_size
        print(f"Claude batch {batch_number}/{total_batches} ({len(batch)} candidates)", file=sys.stderr, flush=True)
        batch_by_id = {str(candidate.get("id")): candidate for candidate in batch}
        seen_candidate_ids: set[str] = set()
        batch_output_path: Path | None = None
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
            first_id = str(batch[0].get("id") or "unknown")
            last_id = str(batch[-1].get("id") or first_id)
            batch_output_path = cache_dir / f"_claude_batch_output_{batch_number:04d}_{first_id}_{last_id}.json"
            if batch_output_path.exists():
                batch_output_path.unlink()
        prompt = build_claude_prompt(batch, output_path=batch_output_path)
        result: subprocess.CompletedProcess[str] | None = None
        try:
            result = subprocess.run(
                [claude_command, "-p", "--output-format", "json"],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                timeout=timeout_seconds,
            )
            try:
                records = parse_claude_stdout(result.stdout)
            except Exception as stdout_exc:
                if not batch_output_path or not batch_output_path.exists():
                    raise
                try:
                    records = parse_claude_stdout(batch_output_path.read_text(encoding="utf-8"))
                except Exception as file_exc:
                    raise ValueError(f"stdout parse failed: {stdout_exc}; output file parse failed: {file_exc}") from file_exc
        except Exception as exc:  # noqa: BLE001 - batch failures are review data.
            error = summarize_subprocess_error(exc)
            if result is not None:
                stdout_prefix = (result.stdout or "")[:1000].replace("\n", "\\n")
                stderr_prefix = (result.stderr or "")[:1000].replace("\n", "\\n")
                error = f"{error}; stdout_prefix={stdout_prefix!r}; stderr_prefix={stderr_prefix!r}"
            for candidate in batch:
                failure = {"candidate": candidate, "error": error, "reason": "claude_batch_failed"}
                failures.append(failure)
                if failure_cache_path:
                    append_jsonl_record(failure_cache_path, failure)
            print(f"Claude batch {batch_number}/{total_batches} failed: {error[:240]}", file=sys.stderr, flush=True)
            continue
        for record_index, record in enumerate(records):
            if not isinstance(record, dict):
                candidate = batch[record_index] if record_index < len(batch) else {}
                failure = {"candidate": candidate, "record": record, "error": "record is not an object", "reason": "claude_record_invalid"}
                failures.append(failure)
                if failure_cache_path:
                    append_jsonl_record(failure_cache_path, failure)
                continue
            candidate_key = str(record.get("candidate_id") or record.get("id") or "")
            if candidate_key not in batch_by_id:
                failure = {
                    "candidate": {},
                    "record": record,
                    "error": f"record candidate_id not in current batch: {candidate_key}",
                    "reason": "claude_record_out_of_batch",
                }
                failures.append(failure)
                if failure_cache_path:
                    append_jsonl_record(failure_cache_path, failure)
                continue
            candidate = batch_by_id[candidate_key]
            if candidate.get("id"):
                seen_candidate_ids.add(str(candidate["id"]))
            try:
                merged = {
                    **record,
                    "source_candidate_id": candidate.get("id"),
                    "source_type": candidate.get("source_type"),
                    "source_repo": candidate.get("source_repo"),
                    "source_ref": candidate.get("source_ref"),
                    "response_candidate_raw": candidate.get("response_candidate_raw", ""),
                    "response_candidate_ref": candidate.get("response_candidate_ref"),
                    "cleaner": {
                        "method": "claude_code",
                        "model": "default",
                        "schema_version": "dialogue_cleaning_v1",
                    },
                }
                validated = validate_llm_cleaned_record(merged)
                validated_id = str(validated.get("source_candidate_id") or validated.get("candidate_id") or validated.get("id"))
                if validated_id not in cleaned_ids:
                    cleaned.append(validated)
                    cleaned_ids.add(validated_id)
                    if cleaned_cache_path:
                        append_jsonl_record(cleaned_cache_path, validated)
            except Exception as exc:  # noqa: BLE001
                failure = {"candidate": candidate, "record": record, "error": str(exc), "reason": "claude_record_invalid"}
                failures.append(failure)
                if failure_cache_path:
                    append_jsonl_record(failure_cache_path, failure)
        for candidate in batch:
            candidate_id = str(candidate.get("id"))
            if candidate_id not in seen_candidate_ids:
                failure = {"candidate": candidate, "error": "candidate missing from Claude records", "reason": "claude_record_missing"}
                failures.append(failure)
                if failure_cache_path:
                    append_jsonl_record(failure_cache_path, failure)
        print(
            f"Claude batch {batch_number}/{total_batches} done: cleaned={len(cleaned)} failures={len(failures)}",
            file=sys.stderr,
            flush=True,
        )
    return cleaned, failures


def llm_record_to_question_record(record: dict[str, Any], index: int) -> dict[str, Any]:
    quality_label = str(record.get("quality_label") or "B")
    quality_score = float(record.get("quality_score") or 0.75)
    return {
        "id": f"qb_{index:06d}",
        "question_raw": record["question_raw"],
        "question_colloquial_clean": record["question_colloquial_clean"],
        "question_formal_clean": record["question_formal_clean"],
        "question_normalized": record["question_normalized"],
        "question_family": record["question_family"],
        "slots": record.get("slots") or {},
        "missing_slots": record.get("missing_slots") or [],
        "expected_tools": record.get("expected_tools") or QUESTION_FAMILY_TOOLS.get(record["question_family"], ["data_gap_detection"]),
        "coverage_level": "partial" if record.get("missing_slots") else "covered_or_partial",
        "source_candidate_id": record.get("source_candidate_id") or record.get("candidate_id") or record.get("id"),
        "source_type": record.get("source_type", "public_asr"),
        "source_repo": record.get("source_repo", "Xue-Feng-Skill"),
        "source_ref": record.get("source_ref"),
        "response_candidate_raw": record.get("response_candidate_raw", ""),
        "response_candidate_ref": record.get("response_candidate_ref"),
        "style_features": record.get("style_features") or [],
        "mentor_strategy": record.get("mentor_strategy") or [],
        "cleaner": record.get("cleaner") or {"method": "claude_code", "model": "default", "schema_version": "dialogue_cleaning_v1"},
        "quality_label": quality_label,
        "quality_score": round(quality_score, 2),
    }


def provided_slots(slots: dict[str, Any]) -> list[str]:
    provided: list[str] = []
    for key, value in slots.items():
        if value not in (None, "", []):
            provided.append(key)
    if slots.get("score") or slots.get("rank"):
        provided.append("score_or_rank")
    return sorted(set(provided))


def build_eval_case(question: dict[str, Any], index: int) -> dict[str, Any]:
    family = question["question_family"]
    missing_slots = list(question.get("missing_slots") or [])
    must_not_do = ["直接承诺录取", "把公开视频观点当成官方事实"]
    if family in {"rank_to_school_match", "rank_to_major_match"}:
        must_not_do.append("跳过位次转换")
    if missing_slots:
        must_not_do.append("不能在缺少省份、科类、分数或位次时推荐学校")
    return {
        "id": f"eval_{index:06d}",
        "user_question": question["question_normalized"],
        "expected_intent": family,
        "expected_tools": question["expected_tools"],
        "required_slots": REQUIRED_SLOTS_BY_FAMILY.get(family, []),
        "provided_slots": provided_slots(question.get("slots") or {}),
        "missing_slots": missing_slots,
        "should_clarify": bool(missing_slots),
        "must_not_do": must_not_do,
        "source_question_id": question["id"],
    }


def build_strategy_records() -> list[dict[str, Any]]:
    strategies = [
        {
            "applies_to_question_family": "rank_to_major_match",
            "strategy_title": "位次优先，再按专业偏好做冲稳保",
            "strategy_steps": [
                "先确认省份、科类、分数或位次",
                "如果只有分数，调用 score_to_rank 转为位次",
                "调用 rank_to_major_match 查可报学校专业候选",
                "调用 admission_history 查看近年最低分和最低位次",
                "按历史位次差、计划数和偏好解释冲稳保风险",
                "明确历史录取不代表未来录取保证",
            ],
            "must_call_tools": ["score_to_rank", "rank_to_major_match", "admission_history", "data_gap_detection"],
            "must_clarify": ["province", "subject_type", "score_or_rank"],
            "avoid": ["跨省直接比较分数", "只看一年分数线", "承诺一定录取"],
            "risk_notes": ["录取建议必须以位次、年份、省份、科类为口径"],
            "evidence_sources": [
                {"source_type": "methodology_md", "source_ref": "zhangxuefeng-skillset/knowledge/02_volunteer_strategy.md"},
                {"source_type": "public_asr", "source_ref": "Xue-Feng-Skill/data/transcripts"},
            ],
        },
        {
            "applies_to_question_family": "major_profile",
            "strategy_title": "专业判断先看就业面、学校层次和家庭承受力",
            "strategy_steps": [
                "先确认学生目标是就业、读研、考公还是兴趣优先",
                "调用 major_profile 查询专业通用学习内容和就业方向",
                "调用 major_market_reference 查询市场样本和薪资参考",
                "区分顶尖学校专业和普通学校专业，避免一刀切",
                "输出风险、适合人群和可替代专业方向",
            ],
            "must_call_tools": ["major_profile", "major_market_reference", "data_gap_detection"],
            "must_clarify": ["career_preference", "family_constraint"],
            "avoid": ["把专业通用薪资说成某校某专业薪资", "只用一句话说能学或不能学"],
            "risk_notes": ["专业建议属于经验判断，具体就业结果需要来源数据"],
            "evidence_sources": [
                {"source_type": "methodology_md", "source_ref": "zhangxuefeng-skillset/knowledge/01_major_selection.md"},
                {"source_type": "quote_paraphrase", "source_ref": "gaokao-mentor-wisdom/exports/rag_chunks.jsonl"},
            ],
        },
        {
            "applies_to_question_family": "school_major_profile",
            "strategy_title": "学校专业组合要区分学校级、专业级和专业组级口径",
            "strategy_steps": [
                "先调用 school_lookup 和 major_lookup 规范化实体",
                "调用 school_major_profile 获取学校、专业、学科评估和专业组样本",
                "如果只有学校级就业数据，明确不能代表某专业",
                "补充专业通用市场参考，但不要说成该校毕业结果",
                "列出缺失的校专业级就业、薪资、转专业和分流数据",
            ],
            "must_call_tools": ["school_lookup", "major_lookup", "school_major_profile", "data_gap_detection"],
            "must_clarify": ["school_name", "major_name"],
            "avoid": ["把学校级就业率说成某专业就业率", "用观点替代官方来源"],
            "risk_notes": ["校专业级数据缺失时必须进入缺口队列"],
            "evidence_sources": [
                {"source_type": "style_prompt", "source_ref": "zhangxuefeng-skill/SKILL.md"},
                {"source_type": "methodology_md", "source_ref": "zhangxuefeng-skillset/knowledge/04_university_selection.md"},
            ],
        },
        {
            "applies_to_question_family": "specialty_group_risk",
            "strategy_title": "专业组风险只能初筛，不能编真实调剂比例",
            "strategy_steps": [
                "先查专业组包含专业、计划数、选科要求和历史位次",
                "识别组内低热度或用户明显不接受的专业",
                "提示专业组风险是初筛，不等于真实分流或调剂概率",
                "缺少学校官方分流规则时写入 data_gap_detection",
            ],
            "must_call_tools": ["specialty_group_lookup", "specialty_group_risk", "admission_history", "data_gap_detection"],
            "must_clarify": ["school_name_or_group", "province", "subject_type"],
            "avoid": ["编造调剂概率", "把专业组等同于入学后大类分流"],
            "risk_notes": ["需要学校招生章程或教务处规则才能给确定分流结论"],
            "evidence_sources": [
                {"source_type": "methodology_md", "source_ref": "zhangxuefeng-skillset/knowledge/02_volunteer_strategy.md"}
            ],
        },
        {
            "applies_to_question_family": "transfer_policy_lookup",
            "strategy_title": "转专业必须查官方政策，没有来源就标缺口",
            "strategy_steps": [
                "先确认学校和目标专业",
                "调用 transfer_policy_lookup 查询学校官方转专业政策",
                "如果本地没有官方政策，说明当前不能判断难度",
                "把学校、年份和目标专业写入缺口队列",
            ],
            "must_call_tools": ["school_lookup", "transfer_policy_lookup", "data_gap_detection"],
            "must_clarify": ["school_name"],
            "avoid": ["凭经验说转专业容易或很难", "用其他学校政策套用本校"],
            "risk_notes": ["转专业规则强依赖学校和年份"],
            "evidence_sources": [{"source_type": "local_spec", "source_ref": "docs/specs/data-gap-queue.md"}],
        },
    ]
    return [{"id": f"ms_{index:06d}", **record} for index, record in enumerate(strategies, start=1)]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_review_queue(questions: list[dict[str, Any]], failures: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for question in questions:
        if question["quality_label"] in {"C", "D"} or question["missing_slots"]:
            queue.append(
                {
                    "id": question["id"].replace("qb_", "rq_"),
                    "source_question_id": question["id"],
                    "reason": "missing_slots" if question["missing_slots"] else "low_quality",
                    "question_raw": question["question_raw"],
                    "source_ref": question["source_ref"],
                    "suggested_action": "人工复核是否保留、补槽或丢弃",
                }
            )
    for index, failure in enumerate(failures or [], start=len(queue) + 1):
        candidate = failure.get("candidate", {})
        queue.append(
            {
                "id": f"rq_failure_{index:06d}",
                "source_question_id": None,
                "reason": failure.get("reason", "cleaner_failed"),
                "question_raw": candidate.get("question_raw", ""),
                "source_ref": candidate.get("source_ref", ""),
                "suggested_action": f"清洗器失败，需人工复核：{failure.get('error', '')}",
            }
        )
    return queue


def is_usable_question(question: dict[str, Any]) -> bool:
    return question.get("quality_label") in {"A", "B"}


def count_by(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = str(record.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_quality_report(
    questions: list[dict[str, Any]],
    eval_cases: list[dict[str, Any]],
    strategies: list[dict[str, Any]],
    *,
    asr_candidates_count: int,
    llm_cleaned_count: int,
) -> str:
    family_counts = count_by(questions, "question_family")
    quality_counts = count_by(questions, "quality_label")
    source_counts = count_by(questions, "source_type")
    usable_count = sum(1 for question in questions if is_usable_question(question))
    lines = [
        "# 对话数据质量报告",
        "",
        f"ASR 问题候选数：{asr_candidates_count}",
        f"LLM 清洗记录数：{llm_cleaned_count}",
        f"问题记录数：{len(questions)}",
        f"可直接使用问题数：{usable_count}",
        f"Function-call 评测用例数：{len(eval_cases)}",
        f"导师策略记录数：{len(strategies)}",
        "",
        "## 问题族统计",
    ]
    lines.extend(f"- {key}: {value}" for key, value in family_counts.items())
    lines.extend(["", "## 质量标签统计"])
    lines.extend(f"- {key}: {value}" for key, value in quality_counts.items())
    lines.extend(["", "## 来源类型统计"])
    lines.extend(f"- {key}: {value}" for key, value in source_counts.items())
    lines.extend(
        [
            "",
            "## 使用规则",
            "",
            "- `question_bank.jsonl` 用于检索/function-call 覆盖分析。",
            "- `function_call_eval_cases.jsonl` 用于 expected intent 和 expected tools 测试。",
            "- `mentor_strategy_bank.jsonl` 是策略指导，不是事实标准答案。",
            "- `question_colloquial_clean` 保留用户口语风格，适合测试真实问法鲁棒性。",
            "- 模拟内容不能混入真实对话数据。",
            "- 公开视频 ASR 内容在产品中引用前需要人工复核。",
            "",
        ]
    )
    return "\n".join(lines)


def build_common_questions_markdown(questions: list[dict[str, Any]]) -> str:
    family_counts = count_by(questions, "question_family")
    lines = [
        "# 考生/家长常问问题清洗结果",
        "",
        f"共清洗出 {len(questions)} 条问题。`question_colloquial_clean` 保留口语风格，`question_normalized` 用于检索/function-call 测试。",
        "",
        "## 问题类型分布",
    ]
    lines.extend(f"- {family}: {count}" for family, count in sorted(family_counts.items(), key=lambda item: item[1], reverse=True))
    lines.extend(["", "## 分类型样例"])
    for family, _count in sorted(family_counts.items(), key=lambda item: item[1], reverse=True):
        family_questions = [question for question in questions if question["question_family"] == family]
        preferred_questions = [
            question
            for question in family_questions
            if question.get("quality_label") in {"A", "B"} and len(compact_text(question.get("question_colloquial_clean", ""))) <= 220
        ]
        if not preferred_questions:
            preferred_questions = family_questions
        preferred_questions = sorted(
            preferred_questions,
            key=lambda question: (
                -(float(question.get("quality_score") or 0.0)),
                len(question.get("missing_slots") or []),
                len(compact_text(question.get("question_colloquial_clean", ""))),
            ),
        )
        lines.extend(["", f"### {family}", ""])
        for question in preferred_questions[:5]:
            tools = ", ".join(question.get("expected_tools") or [])
            missing = ", ".join(question.get("missing_slots") or []) or "无"
            lines.append(f"- 问法：{truncate_for_prompt(question.get('question_colloquial_clean'), 180)}")
            lines.append(f"  标准化：{truncate_for_prompt(question.get('question_normalized'), 180)}")
            lines.append(f"  预期工具：{tools}；缺槽：{missing}；质量：{question.get('quality_label')}")
    return "\n".join(lines) + "\n"


def build_mentor_strategy_markdown(questions: list[dict[str, Any]], strategies: list[dict[str, Any]]) -> str:
    inferred_counter: dict[str, int] = {}
    for question in questions:
        for strategy in question.get("mentor_strategy") or []:
            inferred_counter[strategy] = inferred_counter.get(strategy, 0) + 1
    lines = [
        "# 导师回复策略清洗结果",
        "",
        "这些策略不是标准答案，而是从公开 ASR 回答片段、方法论仓库和提示词仓库里抽出来的回答路径。后续可用于约束模型：先查什么、该追问什么、哪些话不能说满。",
        "",
        "## 从对话片段归纳出的高频策略",
    ]
    for strategy, count in sorted(inferred_counter.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"- {strategy}（{count} 条问题触发）")
    lines.extend(["", "## 通用策略库"])
    for strategy in strategies:
        lines.extend(
            [
                "",
                f"### {strategy['strategy_title']}",
                f"- 适用问题：{strategy['applies_to_question_family']}",
                f"- 必须调用：{', '.join(strategy.get('must_call_tools') or [])}",
                f"- 必须追问：{', '.join(strategy.get('must_clarify') or []) or '视上下文而定'}",
                f"- 避免：{'; '.join(strategy.get('avoid') or [])}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_asr_question_candidates(project_root: Path, limit: int | None = None) -> list[dict[str, Any]]:
    transcripts_dir = project_root / SOURCE_ROOT / "Xue-Feng-Skill" / "data" / "transcripts"
    raw_candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(transcripts_dir.glob("*.json")):
        doc = load_asr_document(path)
        relpath = str(path.relative_to(project_root)).replace("\\", "/")
        for candidate in extract_question_candidates_from_segments(doc["bvid"], doc["segments"], relpath):
            key = compact_text(candidate["question_raw"])
            if key in seen:
                continue
            seen.add(key)
            raw_candidates.append({"id": f"cand_{len(raw_candidates) + 1:06d}", **candidate})
            if limit is not None and len(raw_candidates) >= limit:
                return raw_candidates
    return raw_candidates


def build_question_bank(
    candidates: list[dict[str, Any]],
    llm_records: list[dict[str, Any]] | None = None,
    *,
    include_rule_fallback: bool = True,
) -> list[dict[str, Any]]:
    llm_by_candidate_id = {
        str(record.get("source_candidate_id") or record.get("candidate_id") or record.get("id")): record
        for record in llm_records or []
        if record.get("source_candidate_id") or record.get("candidate_id") or record.get("id")
    }
    questions: list[dict[str, Any]] = []
    consumed_llm_ids: set[str] = set()
    for candidate in candidates:
        candidate_id = str(candidate.get("id"))
        if candidate_id in llm_by_candidate_id:
            questions.append(llm_record_to_question_record(llm_by_candidate_id[candidate_id], len(questions) + 1))
            consumed_llm_ids.add(candidate_id)
        elif include_rule_fallback:
            questions.append(normalize_question_record(candidate, len(questions) + 1))
    for record in llm_records or []:
        record_id = str(record.get("source_candidate_id") or record.get("candidate_id") or record.get("id") or "")
        if record_id not in consumed_llm_ids:
            questions.append(llm_record_to_question_record(record, len(questions) + 1))
    return questions


def run_pipeline(
    project_root: Path,
    output_dir: Path,
    *,
    limit: int | None = None,
    cleaner: str = "rules",
    claude_batch_size: int = 20,
    claude_timeout_seconds: int = 120,
    include_rule_fallback: bool = True,
) -> dict[str, int]:
    inventory = build_source_inventory(project_root)
    candidates = build_asr_question_candidates(project_root, limit=limit)
    llm_records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    if cleaner == "claude" and candidates:
        llm_records, failures = clean_candidates_with_claude(
            candidates,
            batch_size=claude_batch_size,
            timeout_seconds=claude_timeout_seconds,
            cache_dir=output_dir,
        )
    questions = build_question_bank(candidates, llm_records if llm_records else None, include_rule_fallback=include_rule_fallback)
    eval_cases = [build_eval_case(question, index) for index, question in enumerate(questions, start=1)]
    usable_questions = [question for question in questions if is_usable_question(question)]
    usable_eval_cases = [build_eval_case(question, index) for index, question in enumerate(usable_questions, start=1)]
    strategies = build_strategy_records()
    review_queue = build_review_queue(questions, failures=failures)
    report = build_quality_report(
        questions,
        eval_cases,
        strategies,
        asr_candidates_count=len(candidates),
        llm_cleaned_count=len(llm_records),
    )

    write_json(output_dir / "source_inventory.json", inventory)
    write_jsonl(output_dir / "asr_question_candidates.jsonl", candidates)
    write_jsonl(output_dir / "llm_cleaned_dialogues.jsonl", llm_records)
    write_jsonl(output_dir / "question_bank.jsonl", questions)
    write_jsonl(output_dir / "function_call_eval_cases.jsonl", eval_cases)
    write_jsonl(output_dir / "usable_question_bank.jsonl", usable_questions)
    write_jsonl(output_dir / "usable_function_call_eval_cases.jsonl", usable_eval_cases)
    write_jsonl(output_dir / "mentor_strategy_bank.jsonl", strategies)
    write_jsonl(output_dir / "review_queue.jsonl", review_queue)
    (output_dir / "dialogue_quality_report.md").write_text(report, encoding="utf-8")
    (output_dir / "student_common_questions.md").write_text(build_common_questions_markdown(questions), encoding="utf-8")
    (output_dir / "mentor_reply_strategies.md").write_text(build_mentor_strategy_markdown(questions, strategies), encoding="utf-8")

    return {
        "sources": len(inventory),
        "asr_candidates": len(candidates),
        "llm_cleaned": len(llm_records),
        "questions": len(questions),
        "usable_questions": len(usable_questions),
        "eval_cases": len(eval_cases),
        "usable_eval_cases": len(usable_eval_cases),
        "strategies": len(strategies),
        "review_queue": len(review_queue),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dialogue question and mentor strategy assets.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="Repository root. Defaults to the root inferred from src/major_intel/datasets/dialogue/.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/dialogue"),
        help="Generated output directory. Defaults to ignored local processed data, not the committed snapshot.",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--cleaner", choices=["rules", "claude"], default="rules")
    parser.add_argument("--claude-batch-size", type=int, default=20)
    parser.add_argument("--claude-timeout-seconds", type=int, default=120)
    parser.add_argument("--no-rule-fallback", action="store_true")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir

    summary = run_pipeline(
        project_root,
        output_dir,
        limit=args.limit,
        cleaner=args.cleaner,
        claude_batch_size=args.claude_batch_size,
        claude_timeout_seconds=args.claude_timeout_seconds,
        include_rule_fallback=not args.no_rule_fallback,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
