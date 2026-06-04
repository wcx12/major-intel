"""Offline natural-language entrypoint for Major Intel retrieval tools.

This module is the first, deliberately conservative layer above the existing
function-call registry.  It does not use model memory, network search, or hidden
table knowledge.  Its job is to turn high-frequency Chinese gaokao questions
into normalized slots and a safe tool plan, then execute that plan through the
same registry boundary that future LLM agents will use.

The implementation starts rule-first on purpose.  A small deterministic router
is much easier to test than a prompt-only agent, and it gives us a stable
fallback even after an LLM tool-call loop is added later.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

# Direct CLI execution (`python scripts/natural_language_entrypoint.py ...`)
# puts `scripts/` on sys.path.  Add the repository root so imports behave the
# same way in unit tests, cron jobs, and manual local runs.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.retrieval_function_registry import call_retrieval_function


Dispatcher = Callable[[str, dict[str, Any]], dict[str, Any]]


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


SUBJECT_TYPES = ["物理", "历史", "综合", "理科", "文科", "化学", "生物", "政治", "思想政治", "地理", "技术"]


SCHOOL_ALIASES = {
    # This list is not meant to replace `school_lookup`.  It only gives the
    # offline router enough signal to decide which tool to call before the real
    # entity resolver normalizes the school.
    "杭电": "杭州电子科技大学",
    "浙大": "浙江大学",
    "北交": "北京交通大学",
    "北交大": "北京交通大学",
    "央民": "中央民族大学",
    "海大": "中国海洋大学",
}


MAJOR_ALIASES = [
    "计算机科学与技术",
    "计算机",
    "计科",
    "软件工程",
    "软工",
    "人工智能",
    "自动化",
    "电子信息",
    "电气工程",
    "机械",
    "临床医学",
    "法学",
    "金融学",
]


INTENT_TOOL = {
    "school_lookup": "school_lookup",
    "major_lookup": "major_lookup",
    "school_profile": "school_profile",
    "major_profile": "major_profile",
    "school_major_list": "school_major_list",
    "major_school_list": "major_school_list",
    "school_major_profile": "school_major_profile",
    "score_to_rank": "score_to_rank",
    "rank_to_school_match": "rank_to_school_match",
    "rank_to_major_match": "rank_to_major_match",
    "admission_history": "admission_history",
    "plan_history": "plan_history",
    "specialty_group_lookup": "specialty_group_lookup",
    "subject_requirement_lookup": "subject_requirement_lookup",
    "specialty_group_risk": "specialty_group_risk",
    "comparison_query": "comparison_query",
    "major_streaming_policy_lookup": "major_streaming_policy_lookup",
    "civil_service_mapping": "civil_service_mapping",
    "policy_rule_lookup": "policy_rule_lookup",
    "school_department_major_list": "school_department_major_list",
    "employment_summary": "employment_summary",
    "transfer_policy_lookup": "transfer_policy_lookup",
    "fee_and_campus_lookup": "fee_and_campus_lookup",
    "source_trace_lookup": "source_trace_lookup",
    "major_market_reference": "major_market_reference",
}


CIVIL_SERVICE_MAPPING_WARNING = "考公岗位文本命中只能作为样本，不是正式可报判定。"


class NaturalLanguageEntryPoint:
    """Route one Chinese user question to local retrieval function calls.

    The entrypoint returns a JSON-like envelope instead of only natural
    language.  That makes manual testing, future UI integration, and later cache
    writes straightforward: the caller can inspect intent, slots, tool plan,
    executed traces, warnings, and data gaps independently from the answer text.
    """

    def __init__(self, dispatcher: Dispatcher = call_retrieval_function) -> None:
        self.dispatcher = dispatcher

    def run(
        self,
        question: str,
        session_context: dict[str, Any] | None = None,
        *,
        execute: bool = True,
    ) -> dict[str, Any]:
        """Route and optionally execute one natural-language question."""

        cleaned_question = _clean_question(question)
        slots = _merge_slots(_extract_slots(cleaned_question), session_context or {})
        intent = _detect_intent(cleaned_question, slots)
        needs_clarification = _missing_required_slots(intent, slots)
        tool_plan = [] if needs_clarification else _build_tool_plan(intent, slots)

        if needs_clarification:
            return _entrypoint_result(
                status="needs_clarification",
                question=question,
                intent=intent,
                slots=slots,
                needs_clarification=needs_clarification,
                tool_plan=[],
                tool_trace=[],
                answer_markdown=_clarification_answer(needs_clarification),
            )

        if not execute:
            return _entrypoint_result(
                status="planned",
                question=question,
                intent=intent,
                slots=slots,
                tool_plan=tool_plan,
                tool_trace=[],
                answer_markdown="已生成工具调用计划，尚未执行本地检索。",
            )

        tool_trace = [self._execute_call(call) for call in tool_plan]
        status = _aggregate_status(intent, tool_trace)
        data_gaps = _collect_unique(tool_trace, "data_gaps")
        scope_notes = _collect_unique(tool_trace, "scope_notes")
        warnings = _collect_unique(tool_trace, "warnings")
        if intent == "civil_service_mapping" and CIVIL_SERVICE_MAPPING_WARNING not in warnings:
            # 考公工具目前只是把岗位文本样本按专业关键词召回出来，
            # 还没有做“专业代码、学历、学位、政治面貌、基层经历”等正式资格条件判定。
            warnings.append(CIVIL_SERVICE_MAPPING_WARNING)

        return _entrypoint_result(
            status=status,
            question=question,
            intent=intent,
            slots=slots,
            tool_plan=tool_plan,
            tool_trace=tool_trace,
            data_gaps=data_gaps,
            scope_notes=scope_notes,
            warnings=warnings,
            answer_markdown=_answer_summary(intent, status, tool_trace, data_gaps, warnings),
        )

    def _execute_call(self, call: dict[str, Any]) -> dict[str, Any]:
        """Execute one planned function call and keep call metadata with result."""

        tool_name = call["tool_name"]
        arguments = call["arguments"]
        result = self.dispatcher(tool_name, arguments)
        return {"tool_name": tool_name, "arguments": arguments, "result": result}


def _clean_question(question: str) -> str:
    """Normalize whitespace while preserving Chinese punctuation and entities."""

    return re.sub(r"\s+", " ", str(question or "").strip())


def _extract_slots(question: str) -> dict[str, Any]:
    """Extract high-signal slots with conservative regex and alias rules.

    This is not a replacement for the database-backed resolvers.  It only gives
    the router enough structured information to choose the right tool and pass
    the user's raw wording to that tool.
    """

    slots: dict[str, Any] = {}

    for province in PROVINCES:
        if province in question:
            slots["province"] = province
            break

    for subject_type in SUBJECT_TYPES:
        if subject_type in question:
            slots["subject_type"] = subject_type
            break

    year_match = re.search(r"(20\d{2})", question)
    if year_match:
        slots["year"] = int(year_match.group(1))

    rank_match = re.search(r"(\d{3,8})\s*(?:位次|名|排名)", question)
    if not rank_match:
        rank_match = re.search(r"(?:位次|排名)\s*(\d{3,8})", question)
    if rank_match:
        slots["rank"] = int(rank_match.group(1))

    # Treat a plain three-digit number as score only when it is not already
    # consumed as rank.  This handles "广东物理 580" while avoiding "45000 位次".
    if "rank" not in slots:
        score_match = re.search(r"(?<![\d.])([1-9]\d{2})(?:\s*分)?(?![\d.])", question)
        if not score_match:
            score_match = re.search(r"(?<![\d.])(\d{1,2})\s*分(?![\d.])", question)
        if score_match:
            slots["score"] = int(score_match.group(1))

    group_match = re.search(r"(?:专业组|第)?([A-Z]?\d{2,4})\s*组", question, re.IGNORECASE)
    if group_match:
        slots["group_code"] = group_match.group(1)

    department_match = re.search(r"([\u4e00-\u9fff]{2,12}学院)", question)
    if department_match:
        slots["department_text"] = department_match.group(1)

    school_text = _extract_school_text(question)
    if school_text:
        slots["school_text"] = school_text

    major_text = _extract_major_text(question)
    if major_text:
        slots["major_text"] = major_text

    comparison_slots = _extract_comparison_slots(question)
    if comparison_slots:
        slots.update(comparison_slots)

    if "稳" in question:
        slots["risk_preference"] = "稳"
    elif "冲" in question:
        slots["risk_preference"] = "冲"
    elif "保" in question:
        slots["risk_preference"] = "保"

    policy_type = _extract_policy_type(question)
    if policy_type:
        slots["policy_type"] = policy_type

    return slots


def _extract_school_text(question: str) -> str | None:
    for alias in sorted(SCHOOL_ALIASES, key=len, reverse=True):
        if alias in question:
            return SCHOOL_ALIASES[alias]

    # Match full school names ending at the institutional suffix.  The reluctant
    # prefix avoids swallowing the following major in "杭州电子科技大学计算机".
    match = re.search(r"([\u4e00-\u9fff]{2,30}?(?:大学|学院|学校|职业技术大学|职业学院))", question)
    return match.group(1) if match else None


def _extract_major_text(question: str) -> str | None:
    for major in sorted(MAJOR_ALIASES, key=len, reverse=True):
        if major in question:
            return major
    return None


def _extract_comparison_slots(question: str) -> dict[str, Any]:
    """Extract obvious A/B comparison targets without doing fuzzy guessing.

    这里只识别非常明确的“甲和乙”“甲还是乙”“对比甲乙”场景。真正实体归一
    仍交给底层 `comparison_query` 复用的 school/major lookup 工具完成。
    """

    if not any(marker in question for marker in ["对比", "哪个好", "怎么选", "比一比", "还是", " 和 ", "和", "vs", "VS"]):
        return {}

    school_targets = _ordered_alias_hits(question, SCHOOL_ALIASES)
    if len(school_targets) >= 2:
        return {"target_type": "school", "comparison_targets": school_targets}

    major_targets = _ordered_literal_hits(question, MAJOR_ALIASES)
    if len(major_targets) >= 2:
        return {"target_type": "major", "comparison_targets": major_targets}

    return {}


def _extract_policy_type(question: str) -> str | None:
    """Map common policy wording to a compact policy type label."""

    policy_keywords = [
        "单科限制",
        "身体条件",
        "外语语种",
        "中外合作",
        "校区规则",
        "录取规则",
        "批次规则",
        "投档",
        "退档",
        "招生章程",
    ]
    for keyword in policy_keywords:
        if keyword in question:
            return keyword
    if "单科" in question:
        return "单科限制"
    if "语种" in question:
        return "外语语种"
    return None


def _ordered_alias_hits(question: str, aliases: dict[str, str]) -> list[str]:
    """Return alias hits ordered by where they appear in the question."""

    hits: list[tuple[int, int, str]] = []
    for alias, canonical in aliases.items():
        index = question.find(alias)
        if index >= 0:
            hits.append((index, -len(alias), canonical))
    return _distinct_preserving_order(value for _, _, value in sorted(hits))


def _ordered_literal_hits(question: str, values: list[str]) -> list[str]:
    """Return literal value hits ordered by position, preferring longer names."""

    hits: list[tuple[int, int, str]] = []
    for value in values:
        index = question.find(value)
        if index >= 0:
            hits.append((index, -len(value), value))
    return _distinct_preserving_order(value for _, _, value in sorted(hits))


def _distinct_preserving_order(values: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _merge_slots(extracted: dict[str, Any], session_context: dict[str, Any]) -> dict[str, Any]:
    """Merge context first, then let the current user turn override it."""

    merged = {key: value for key, value in session_context.items() if value not in (None, "")}
    merged.update({key: value for key, value in extracted.items() if value not in (None, "")})
    return merged


def _detect_intent(question: str, slots: dict[str, Any]) -> str:
    """Detect the primary intent using ordered high-confidence rules."""

    if any(word in question for word in ["来源", "靠谱吗", "可信", "哪里来", "数据"]):
        return "source_trace_lookup"

    if any(word in question for word in ["招生章程", "单科", "身体条件", "语种", "录取规则", "批次规则", "投档", "退档"]):
        return "policy_rule_lookup"

    if any(word in question for word in ["大类分流", "专业分流", "分流比例", "分流政策"]):
        return "major_streaming_policy_lookup"

    if any(word in question for word in ["专业组", "组内", "调剂", "冷门", "风险"]):
        if any(word in question for word in ["调剂", "冷门", "风险"]):
            return "specialty_group_risk"
        return "specialty_group_lookup"

    if any(word in question for word in ["转专业", "换专业"]):
        return "transfer_policy_lookup"

    if any(word in question for word in ["学费", "校区", "住宿费", "中外合作"]):
        return "fee_and_campus_lookup"

    if any(word in question for word in ["选科", "再选", "科目要求", "物化", "要选什么科"]):
        return "subject_requirement_lookup"

    if any(word in question for word in ["考公", "公务员", "岗位", "编制"]):
        return "civil_service_mapping"

    if _looks_like_score_to_rank_question(question, slots):
        return "score_to_rank"

    if _looks_like_major_market_question(question, slots):
        return "major_market_reference"

    if any(word in question for word in ["对比", "哪个好", "怎么选", "比一比", "还是"]):
        return "comparison_query"

    if _looks_like_score_or_rank_question(question, slots):
        return "rank_to_major_match" if slots.get("major_text") else "rank_to_school_match"

    if any(word in question for word in ["录取", "分数线", "最低分", "位次是多少"]):
        return "admission_history"

    if any(word in question for word in ["招生计划", "计划数", "招多少"]):
        return "plan_history"

    if any(word in question for word in ["有什么专业", "哪些专业", "专业列表", "开设专业"]):
        return "school_major_list" if slots.get("school_text") else "major_school_list"

    if any(word in question for word in ["学院", "院系"]):
        return "school_department_major_list"

    if any(word in question for word in ["就业", "升学", "保研"]):
        if slots.get("school_text") and slots.get("major_text"):
            return "school_major_profile"
        if slots.get("school_text"):
            return "employment_summary"
        if slots.get("major_text"):
            return "major_profile"

    if slots.get("school_text") and slots.get("major_text"):
        return "school_major_profile"
    if slots.get("school_text"):
        return "school_profile"
    if slots.get("major_text"):
        if any(word in question for word in ["哪些学校", "有什么学校", "开设", "能看哪些学校"]):
            return "major_school_list"
        return "major_profile"

    return "unknown"


def _looks_like_score_or_rank_question(question: str, slots: dict[str, Any]) -> bool:
    if "score" in slots or "rank" in slots:
        return True
    return any(word in question for word in ["能上", "能冲", "稳一点", "保底", "可报", "志愿"])


def _looks_like_score_to_rank_question(question: str, slots: dict[str, Any]) -> bool:
    """Recognize pure score-to-rank conversion before recommendation routing."""

    if slots.get("school_text") or slots.get("major_text"):
        return False
    if not any(word in question for word in ["对应多少位次", "多少位次", "位次多少", "换算位次", "排名多少", "排多少名"]):
        return False
    return bool(slots.get("score") or slots.get("province") or slots.get("subject_type"))


def _looks_like_major_market_question(question: str, slots: dict[str, Any]) -> bool:
    """Route major-only employment/salary/company questions to market samples.

    如果用户已经给了学校 + 专业，就不能直接用专业通用市场样本替代校专业级就业；
    那种情况仍交给 `school_major_profile`，让工具明确标出校专业级数据缺口。
    """

    if not slots.get("major_text") or slots.get("school_text"):
        return False
    market_words = ["就业", "薪资", "工资", "公司", "企业", "行业", "招聘", "城市", "地域", "去向"]
    return any(word in question for word in market_words)


def _missing_required_slots(intent: str, slots: dict[str, Any]) -> list[str]:
    """Return missing slots that the entrypoint should ask before tool calls."""

    if intent == "rank_to_major_match":
        required = ["province", "major_text"]
        missing = [slot for slot in required if not slots.get(slot)]
        if not slots.get("province") and not slots.get("subject_type"):
            missing.append("subject_type")
        if not slots.get("score") and not slots.get("rank"):
            missing.append("score_or_rank")
        return missing

    if intent == "rank_to_school_match":
        missing = [slot for slot in ["province"] if not slots.get(slot)]
        if not slots.get("province") and not slots.get("subject_type"):
            missing.append("subject_type")
        if not slots.get("score") and not slots.get("rank"):
            missing.append("score_or_rank")
        return missing

    if intent == "score_to_rank":
        missing = [slot for slot in ["province", "score"] if not slots.get(slot)]
        if not slots.get("province") and not slots.get("subject_type"):
            missing.append("subject_type")
        return missing

    if intent == "school_major_profile":
        return [slot for slot in ["school_text", "major_text"] if not slots.get(slot)]

    if intent == "specialty_group_risk":
        missing = [slot for slot in ["school_text", "province", "year", "group_code"] if not slots.get(slot)]
        return missing

    required_by_intent = {
        "school_lookup": ["school_text"],
        "school_profile": ["school_text"],
        "school_major_list": ["school_text"],
        "school_department_major_list": ["school_text"],
        "employment_summary": ["school_text"],
        "transfer_policy_lookup": ["school_text"],
        "fee_and_campus_lookup": ["school_text"],
        "major_lookup": ["major_text"],
        "major_profile": ["major_text"],
        "major_school_list": ["major_text"],
        "major_market_reference": ["major_text"],
        "subject_requirement_lookup": ["major_text"],
        "civil_service_mapping": ["major_text"],
        "major_streaming_policy_lookup": ["school_text"],
        "policy_rule_lookup": ["school_text"],
    }
    if intent == "comparison_query":
        missing = []
        if not slots.get("target_type"):
            missing.append("target_type")
        targets = slots.get("comparison_targets")
        if not isinstance(targets, list) or len(targets) < 2:
            missing.append("comparison_targets")
        return missing
    if intent == "unknown":
        return ["intent"]
    return [slot for slot in required_by_intent.get(intent, []) if not slots.get(slot)]


def _build_tool_plan(intent: str, slots: dict[str, Any]) -> list[dict[str, Any]]:
    """Build ordered function calls for the detected intent."""

    if intent == "rank_to_major_match":
        args = _compact_args(
            {
                "province": slots.get("province"),
                "subject_type": slots.get("subject_type"),
                "score": slots.get("score"),
                "rank": slots.get("rank"),
                "major_text": slots.get("major_text"),
                "year": slots.get("year"),
                "limit": 30,
            }
        )
        return [_call("rank_to_major_match", args)]

    if intent == "rank_to_school_match":
        args = _compact_args(
            {
                "province": slots.get("province"),
                "subject_type": slots.get("subject_type"),
                "score": slots.get("score"),
                "rank": slots.get("rank"),
                "year": slots.get("year"),
                "limit": 30,
            }
        )
        return [_call("rank_to_school_match", args)]

    if intent == "school_major_profile":
        profile_args = _compact_args(
            {
                "school_text": slots.get("school_text"),
                "major_text": slots.get("major_text"),
                "province": slots.get("province"),
                "subject_type": slots.get("subject_type"),
                "year": slots.get("year"),
            }
        )
        admission_args = _compact_args(
            {
                "school_text": slots.get("school_text"),
                "major_text": slots.get("major_text"),
                "province": slots.get("province"),
                "subject_type": slots.get("subject_type"),
                "years": [slots["year"]] if slots.get("year") else None,
                "limit": 20,
            }
        )
        return [
            _call("school_major_profile", profile_args),
            _call("employment_summary", {"school_text": slots.get("school_text"), "limit": 5}),
            _call("admission_history", admission_args),
            _call("data_gap_detection", {"question_type": "school_major_profile", "available_fields": []}),
        ]

    if intent == "civil_service_mapping":
        return [_call("civil_service_mapping", {"major_text": slots.get("major_text"), "limit": 20})]

    if intent == "major_streaming_policy_lookup":
        return [
            _call(
                "major_streaming_policy_lookup",
                _compact_args(
                    {
                        "school_text": slots.get("school_text"),
                        "major_text": slots.get("major_text"),
                        "province": slots.get("province"),
                        "year": slots.get("year"),
                        "limit": 10,
                    }
                ),
            )
        ]

    if intent == "policy_rule_lookup":
        return [
            _call(
                "policy_rule_lookup",
                _compact_args(
                    {
                        "school_text": slots.get("school_text"),
                        "policy_type": slots.get("policy_type"),
                        "province": slots.get("province"),
                        "year": slots.get("year"),
                    }
                ),
            )
        ]

    if intent == "specialty_group_risk":
        return [
            _call(
                "specialty_group_risk",
                _compact_args(
                    {
                        "school_text": slots.get("school_text"),
                        "province": slots.get("province"),
                        "subject_type": slots.get("subject_type"),
                        "year": slots.get("year"),
                        "group_code": slots.get("group_code"),
                        "major_text": slots.get("major_text"),
                    }
                ),
            )
        ]

    if intent == "source_trace_lookup":
        previous_tools = slots.get("previous_tool_names") or []
        if previous_tools:
            return [_call("source_trace_lookup", {"tool_name": tool_name}) for tool_name in previous_tools]
        return [_call("source_trace_lookup", {})]

    if intent == "comparison_query":
        return [
            _call(
                "comparison_query",
                _compact_args(
                    {
                        "target_type": slots.get("target_type"),
                        "target_texts": slots.get("comparison_targets"),
                        "major_text": slots.get("major_text") if slots.get("target_type") != "major" else None,
                        "province": slots.get("province"),
                        "subject_type": slots.get("subject_type"),
                        "score": slots.get("score"),
                        "rank": slots.get("rank"),
                        "year": slots.get("year"),
                        "limit": 10,
                    }
                ),
            )
        ]

    tool_name = INTENT_TOOL.get(intent)
    if not tool_name:
        return []

    return [_call(tool_name, _arguments_for_simple_tool(tool_name, slots))]


def _arguments_for_simple_tool(tool_name: str, slots: dict[str, Any]) -> dict[str, Any]:
    """Map slots to a registered tool's public argument names."""

    if tool_name in {"school_lookup", "school_profile", "school_major_list", "employment_summary", "transfer_policy_lookup"}:
        args = {"school_text": slots.get("school_text")}
        if tool_name == "school_major_list":
            args["limit"] = 50
        if tool_name == "employment_summary":
            args["limit"] = 5
        return _compact_args(args)

    if tool_name in {"major_lookup", "major_profile", "major_school_list", "major_market_reference", "subject_requirement_lookup"}:
        args = {"major_text": slots.get("major_text")}
        if tool_name == "major_school_list":
            args["limit"] = 50
        if tool_name == "major_market_reference":
            args["sample_limit"] = 10
        return _compact_args(args)

    if tool_name == "score_to_rank":
        return _compact_args(
            {
                "province": slots.get("province"),
                "subject_type": slots.get("subject_type"),
                "score": slots.get("score"),
                "year": slots.get("year"),
            }
        )

    if tool_name == "admission_history":
        return _compact_args(
            {
                "school_text": slots.get("school_text"),
                "major_text": slots.get("major_text"),
                "province": slots.get("province"),
                "subject_type": slots.get("subject_type"),
                "years": [slots["year"]] if slots.get("year") else None,
                "limit": 20,
            }
        )

    if tool_name == "plan_history":
        return _compact_args(
            {
                "school_text": slots.get("school_text"),
                "major_text": slots.get("major_text"),
                "province": slots.get("province"),
                "years": [slots["year"]] if slots.get("year") else None,
                "limit": 50,
            }
        )

    if tool_name == "specialty_group_lookup":
        return _compact_args(
            {
                "school_text": slots.get("school_text"),
                "major_text": slots.get("major_text"),
                "province": slots.get("province"),
                "subject_type": slots.get("subject_type"),
                "year": slots.get("year"),
                "group_code": slots.get("group_code"),
                "limit": 20,
            }
        )

    if tool_name == "school_department_major_list":
        return _compact_args(
            {
                "school_text": slots.get("school_text"),
                "department_text": slots.get("department_text"),
                "major_text": slots.get("major_text"),
                "limit": 100,
            }
        )

    if tool_name == "fee_and_campus_lookup":
        return _compact_args(
            {
                "school_text": slots.get("school_text"),
                "major_text": slots.get("major_text"),
                "province": slots.get("province"),
                "year": slots.get("year"),
                "limit": 20,
            }
        )

    return {}


def _call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return {"tool_name": tool_name, "arguments": arguments}


def _compact_args(arguments: dict[str, Any]) -> dict[str, Any]:
    """Drop absent optional arguments while preserving explicit zero values."""

    return {key: value for key, value in arguments.items() if value not in (None, "", [])}


def _aggregate_status(intent: str, tool_trace: list[dict[str, Any]]) -> str:
    if intent == "civil_service_mapping":
        return "partial"
    if not tool_trace:
        return "data_gap" if intent == "comparison_query" else "needs_clarification"

    statuses = [trace["result"].get("status") for trace in tool_trace]
    if any(status == "error" for status in statuses):
        return "error"
    if any(status == "needs_clarification" for status in statuses):
        return "needs_clarification"
    if any(status == "ok" for status in statuses):
        return "partial" if any(status == "partial" for status in statuses) else "ok"
    if any(status == "partial" for status in statuses):
        return "partial"
    if all(status == "not_found" for status in statuses):
        return "not_found"
    return "partial"


def _collect_unique(tool_trace: list[dict[str, Any]], key: str) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for trace in tool_trace:
        for item in trace["result"].get(key, []) or []:
            text = str(item)
            if text not in seen:
                seen.add(text)
                values.append(text)
    return values


def _entrypoint_result(
    *,
    status: str,
    question: str,
    intent: str,
    slots: dict[str, Any],
    tool_plan: list[dict[str, Any]],
    tool_trace: list[dict[str, Any]],
    needs_clarification: list[str] | None = None,
    data_gaps: list[str] | None = None,
    scope_notes: list[str] | None = None,
    warnings: list[str] | None = None,
    answer_markdown: str = "",
) -> dict[str, Any]:
    return {
        "status": status,
        "question": question,
        "intent": intent,
        "slots": slots,
        "needs_clarification": needs_clarification or [],
        "tool_plan": tool_plan,
        "tool_trace": tool_trace,
        "data_gaps": data_gaps or [],
        "scope_notes": scope_notes or [],
        "warnings": warnings or [],
        "answer_markdown": answer_markdown,
    }


def _clarification_answer(missing_slots: list[str]) -> str:
    names = {
        "province": "省份",
        "subject_type": "科类",
        "score": "分数",
        "score_or_rank": "分数或位次",
        "major_text": "专业",
        "school_text": "学校",
        "year": "年份",
        "group_code": "专业组代码",
        "comparison_targets": "对比对象",
        "intent": "你想查询的具体问题",
    }
    readable = "、".join(names.get(slot, slot) for slot in missing_slots)
    return f"这个问题还需要补充：{readable}。补齐后我再调用本地检索工具，避免猜测。"


def _answer_summary(
    intent: str,
    status: str,
    tool_trace: list[dict[str, Any]],
    data_gaps: list[str],
    warnings: list[str],
) -> str:
    if intent == "score_to_rank":
        return _score_to_rank_answer_summary(status, tool_trace, warnings)

    called = "、".join(trace["tool_name"] for trace in tool_trace) or "无"
    parts = [f"已按 `{intent}` 处理，调用工具：{called}。"]
    if status == "partial":
        parts.append("当前结果是部分口径，不能当作完整结论。")
    if data_gaps:
        parts.append("仍缺：" + "、".join(data_gaps) + "。")
    if warnings:
        parts.append("注意：" + "；".join(warnings) + "。")
    if intent == "civil_service_mapping" and CIVIL_SERVICE_MAPPING_WARNING not in warnings:
        parts.append(CIVIL_SERVICE_MAPPING_WARNING)
    return "\n".join(parts)


def _score_to_rank_answer_summary(status: str, tool_trace: list[dict[str, Any]], warnings: list[str]) -> str:
    result = next((trace.get("result") or {} for trace in tool_trace if trace.get("tool_name") == "score_to_rank"), None)
    if not result:
        return "这个问题需要先调用分数转位次工具；当前还没有可用的本地检索结果。"

    result_status = result.get("status") or status
    input_data = result.get("input") or {}
    normalized = result.get("normalized_slots") or {}
    data = result.get("data") or {}

    if result_status == "ok":
        rank_range = data.get("rank_range") or {}
        province = normalized.get("province") or input_data.get("province") or "该省"
        subject_type = normalized.get("matched_subject_type") or input_data.get("subject_type") or "该科类"
        score = data.get("score") if data.get("score") is not None else input_data.get("score")
        year = normalized.get("year") or input_data.get("year") or "命中年份"
        highest = rank_range.get("highest_rank")
        lowest = rank_range.get("lowest_rank")
        same_count = data.get("same_count")
        parts = [
            f"{year}年{province}{subject_type}{score}分，对应位次区间约为 {highest}-{lowest} 名，同分人数 {same_count} 人。",
            "这个换算只在同省、同科类、同年份内有效，后续做学校或专业匹配时应优先使用位次。",
        ]
        if input_data.get("year") in (None, ""):
            parts.append(f"你没有指定年份，这里按本地库命中的 {year} 年返回。")
        if warnings:
            parts.append("注意：" + "；".join(warnings) + "。")
        return "\n".join(parts)

    if result_status == "not_found":
        parts = ["本地库未命中对应的一分一段记录，不能给出可靠位次。"]
        if warnings:
            parts.append("注意：" + "；".join(warnings) + "。")
        return "\n".join(parts)

    if result_status == "needs_clarification":
        missing = result.get("needs_clarification") or []
        return _clarification_answer(missing or ["score"])

    if result_status == "error":
        warning_text = "；".join(result.get("warnings") or warnings)
        return f"分数转位次执行失败，当前不能给出可靠位次。{('原因：' + warning_text + '。') if warning_text else ''}"

    return "当前分数转位次结果口径不完整，不能给出可靠位次。"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        # Windows 终端经常默认使用 GBK/CP936；这里把 CLI 输出固定成 UTF-8，
        # 这样脚本既能给人看，也能被单元测试、Node/Python 服务稳定解析。
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Route a natural-language gaokao question to retrieval tools.")
    parser.add_argument("question", help="用户自然语言问题。")
    parser.add_argument("--context-json", help="可选，会话槽位 JSON，例如 {\"province\":\"广东\"}。")
    parser.add_argument("--no-execute", action="store_true", help="只输出工具计划，不连接数据库执行工具。")
    args = parser.parse_args(argv)

    context: dict[str, Any] = {}
    if args.context_json:
        try:
            context = json.loads(args.context_json)
        except json.JSONDecodeError as exc:
            print(f"ERROR: --context-json is not valid JSON: {exc}", file=sys.stderr)
            return 2
        if not isinstance(context, dict):
            print("ERROR: --context-json must decode to a JSON object.", file=sys.stderr)
            return 2

    result = NaturalLanguageEntryPoint().run(args.question, session_context=context, execute=not args.no_execute)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
