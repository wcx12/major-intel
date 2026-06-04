"""Agent-facing function registry for the local retrieval tool layer.

`retrieval_tools.py` owns the actual MySQL-backed retrieval behavior.  This
module owns the agent contract around that behavior: JSON schemas that can be
registered as function-call tools, plus a defensive dispatcher that calls the
right retrieval method by name.

Keeping the registry separate is deliberate.  The agent should see concise
business-oriented tool descriptions and typed slots, while the retrieval layer
continues to own SQL, source-table scope, and evidence warnings.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Like `retrieval_tools.py`, this file must work both as an imported module and
# as a direct CLI script.  Direct execution puts `scripts/` on `sys.path`, so we
# add the repository root before importing sibling project modules.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.local_retrieval_mvp import DbConfig, MysqlCliClient
from scripts.retrieval_tools import RetrievalTools, tool_result


JsonSchema = dict[str, Any]


def _string(description: str) -> JsonSchema:
    return {"type": "string", "description": description}


def _integer(description: str, *, minimum: int = 1, maximum: int | None = None) -> JsonSchema:
    schema: JsonSchema = {"type": "integer", "description": description, "minimum": minimum}
    if maximum is not None:
        schema["maximum"] = maximum
    return schema


def _number(description: str) -> JsonSchema:
    return {"type": "number", "description": description}


def _string_array(description: str) -> JsonSchema:
    return {"type": "array", "description": description, "items": {"type": "string"}}


def _integer_array(description: str) -> JsonSchema:
    return {"type": "array", "description": description, "items": {"type": "integer"}}


def _object_schema(properties: dict[str, JsonSchema], required: list[str] | None = None) -> JsonSchema:
    # `additionalProperties: false` is important for function-call safety.  If
    # the model invents a slot name, the dispatcher should reject it instead of
    # silently dropping context that the user might have expected to matter.
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


def _function_schema(name: str, description: str, parameters: JsonSchema) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


_LIMIT = _integer("最多返回多少条候选记录。", minimum=1, maximum=200)


# The order is intentional: entity resolution comes first, then profile/list
# queries, then score/admission, then crawled-market and gap tools.  This order
# makes exported schemas easier to inspect and mirrors the normal agent flow.
_FUNCTION_SCHEMAS: dict[str, dict[str, Any]] = {
    "school_lookup": _function_schema(
        "school_lookup",
        "解析学校名称、简称或代码，返回本地库命中的规范学校实体和候选学校。不要用它回答就业或录取结论。",
        _object_schema(
            {
                "school_text": _string("用户提到的学校名称、简称或学校代码。"),
                "limit": _LIMIT,
            },
            ["school_text"],
        ),
    ),
    "major_lookup": _function_schema(
        "major_lookup",
        "解析专业名称、简称或专业代码，返回本地库命中的规范专业实体和候选专业。不要猜测未命中的专业。",
        _object_schema(
            {
                "major_text": _string("用户提到的专业名称、简称或专业代码。"),
                "limit": _LIMIT,
            },
            ["major_text"],
        ),
    ),
    "school_profile": _function_schema(
        "school_profile",
        "查询学校级画像，包括学校基础信息、双一流、学科评估和学校级就业/升学摘要。学校级就业不能当作专业级就业。",
        _object_schema({"school_text": _string("学校名称、简称或代码。")}, ["school_text"]),
    ),
    "major_profile": _function_schema(
        "major_profile",
        "查询专业通用画像，包括学科门类、专业类、修业年限、学位和专业通用就业方向。它不是某校某专业画像。",
        _object_schema({"major_text": _string("专业名称、简称或代码。")}, ["major_text"]),
    ),
    "school_major_list": _function_schema(
        "school_major_list",
        "查询某学校在本地库记录的开设专业列表。它不等于某省某年的招生专业列表。不要传 major_text；如果要查“学校+专业”是否开设，用 school_major_profile；如果要查“专业+地区”有哪些学校开设，用 major_school_list。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "major_category": _string("可选的专业类/门类筛选词，例如 计算机类、工学；不是具体专业名称，不要传 major_text。"),
                "limit": _LIMIT,
            },
            ["school_text"],
        ),
    ),
    "major_school_list": _function_schema(
        "major_school_list",
        "查询本地库记录中开设某专业的学校列表，可按学校所在省份或学校层次粗筛。它不代表当年招生计划。",
        _object_schema(
            {
                "major_text": _string("专业名称、简称或代码。"),
                "province_filter": _string("可选，学校所在省份名称，例如 浙江。"),
                "school_level_filter": _string("可选，学校层次筛选，例如 本科、专科。"),
                "limit": _LIMIT,
            },
            ["major_text"],
        ),
    ),
    "school_major_profile": _function_schema(
        "school_major_profile",
        "查询学校+专业组合画像，合并学校基础、专业基础、学科评估、学校级就业和专业组样本，并明确缺失的专业级数据。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "major_text": _string("专业名称、简称或代码。"),
                "province": _string("可选，考生所在省份；提供后会过滤专业组样本。"),
                "subject_type": _string("可选，物理/历史/综合等科类；提供后会过滤专业组样本。"),
                "year": _integer("可选，招生或录取年份。", minimum=2000, maximum=2100),
            },
            ["school_text", "major_text"],
        ),
    ),
    "score_to_rank": _function_schema(
        "score_to_rank",
        "把同省、同科类、同年份的高考分数转换为位次区间。后续推荐应优先使用位次，不要跨省跨科类比较分数。",
        _object_schema(
            {
                "province": _string("考生所在省份名称或 province_id。"),
                "subject_type": _string("可选，科类或选考科目，例如 物理、历史、综合；缺省时工具会按省份/年份口径判断。"),
                "score": _number("高考分数。"),
                "year": _integer("可选，一分一段年份；不填时默认查本地最新年份。", minimum=2000, maximum=2100),
            },
            ["province", "score"],
        ),
    ),
    "rank_to_school_match": _function_schema(
        "rank_to_school_match",
        "按考生省份、科类、分数或位次，使用本地历年录取位次推荐冲稳保学校；如果请求年份缺少录取数据，会明确标记为历史参考。",
        _object_schema(
            {
                "province": _string("考生所在省份名称或 province_id。"),
                "subject_type": _string("可选，科类或选考科目，例如 物理、历史、综合；缺省时工具会按省份/年份口径判断，必要时追问。"),
                "score": _number("可选，高考分数；未直接提供位次时，工具会先调用 score_to_rank 得到保守位次。"),
                "rank": _integer("可选，考生位次；提供后会直接用位次匹配学校。"),
                "year": _integer("可选，期望参考的录取年份；本地库没有当年录取时会回退到最近历史年份。", minimum=2000, maximum=2100),
                "reference_years": _integer_array("可选，限定只使用这些历史录取年份。"),
                "preferred_regions": _string_array("可选，只看这些学校所在地省份，例如 浙江、江苏、广东。"),
                "school_level_filter": _string("可选，学校层次或类型粗筛，例如 211、双一流、本科。"),
                "limit": _LIMIT,
            },
            # rank 和 score 是业务二选一关系，JSON schema 的 required 不适合
            # 表达这种约束；统一由工具层返回 needs_clarification，方便 agent
            # 获得同样格式的缺槽提示。
            ["province"],
        ),
    ),
    "rank_to_major_match": _function_schema(
        "rank_to_major_match",
        "按考生省份、专业偏好、科类、分数或位次，使用本地历年专业录取位次返回冲稳保学校-专业行；结果是历史参考，不是录取保证。",
        _object_schema(
            {
                "province": _string("考生所在省份名称或 province_id。"),
                "major_text": _string("专业名称、简称、专业代码或较宽泛的专业兴趣词，例如 计科、软件工程、计算机。"),
                "subject_type": _string("可选，科类或选考科目，例如 物理、历史、综合；缺省时工具会按省份/年份口径判断，必要时追问。"),
                "score": _number("可选，高考分数；未直接提供位次时，工具会先调用 score_to_rank 得到保守位次。"),
                "rank": _integer("可选，考生位次；提供后会直接用位次匹配专业录取历史。"),
                "year": _integer("可选，期望参考的录取年份；本地库没有当年录取时会回退到最近历史年份。", minimum=2000, maximum=2100),
                "reference_years": _integer_array("可选，限定只使用这些历史录取年份。"),
                "preferred_regions": _string_array("可选，只看这些学校所在地省份，例如 浙江、江苏、广东。"),
                "school_level_filter": _string("可选，学校层次或类型粗筛，例如 211、双一流、本科。"),
                "limit": _LIMIT,
            },
            ["province", "major_text"],
        ),
    ),
    "specialty_group_lookup": _function_schema(
        "specialty_group_lookup",
        "查询某学校在指定省份/科类/年份下的专业组，并返回组内全部专业、计划数、选科要求和是否允许调剂。专业组不等于真实分流结果。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "major_text": _string("可选，专业名称、简称或代码；提供后只找包含该专业的专业组。"),
                "province": _string("可选，招生省份名称或 province_id。"),
                "subject_type": _string("可选，科类，例如 物理、历史、综合。"),
                "year": _integer("可选，招生年份。", minimum=2000, maximum=2100),
                "group_code": _string("可选，专业组代码。"),
                "limit": _LIMIT,
            },
            ["school_text"],
        ),
    ),
    "subject_requirement_lookup": _function_schema(
        "subject_requirement_lookup",
        "查询某专业在本地专业组样本中的选科要求，可按学校、省份、科类、年份过滤。选科要求必须结合具体年份和省份理解。",
        _object_schema(
            {
                "major_text": _string("专业名称、简称或代码。"),
                "school_text": _string("可选，学校名称、简称或代码。"),
                "province": _string("可选，招生省份名称或 province_id。"),
                "subject_type": _string("可选，科类，例如 物理、历史、综合。"),
                "year": _integer("可选，招生年份。", minimum=2000, maximum=2100),
                "limit": _LIMIT,
            },
            ["major_text"],
        ),
    ),
    "school_department_major_list": _function_schema(
        "school_department_major_list",
        "查询学校院系和院系下专业关系。它是学校组织结构口径，不等于某省某年的招生计划。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "department_text": _string("可选，院系名称筛选词。"),
                "major_text": _string("可选，专业名称、简称或代码。"),
                "limit": _LIMIT,
            },
            ["school_text"],
        ),
    ),
    "plan_history": _function_schema(
        "plan_history",
        "查询学校/专业在不同省份和年份的招生计划记录。计划数不等于实际录取人数。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "major_text": _string("可选，专业名称、简称或代码。"),
                "province": _string("可选，招生省份名称或 province_id。"),
                "years": _integer_array("可选，需要查询的招生年份列表。"),
                "limit": _LIMIT,
            },
            ["school_text"],
        ),
    ),
    "employment_summary": _function_schema(
        "employment_summary",
        "查询学校级就业和升学摘要。它不能回答某个专业的真实就业去向、薪资或升学率。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "limit": _integer("最多返回多少个年份。", minimum=1, maximum=20),
            },
            ["school_text"],
        ),
    ),
    "source_trace_lookup": _function_schema(
        "source_trace_lookup",
        "解释检索工具使用的数据表、数据口径和可信等级，帮助 agent 在回答中说明来源边界。",
        _object_schema({"tool_name": _string("可选，需要解释的工具名。")}, []),
    ),
    "transfer_policy_lookup": _function_schema(
        "transfer_policy_lookup",
        "查询已接入的转专业政策线索。当前主要来自第三方数据，必须提示回到学校官网或教务处文件复核。",
        _object_schema({"school_text": _string("学校名称、简称或代码。")}, ["school_text"]),
    ),
    "fee_and_campus_lookup": _function_schema(
        "fee_and_campus_lookup",
        "查询招生计划中的学费线索，并明确当前库没有稳定校区字段，不能猜测就读校区。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "major_text": _string("可选，专业名称、简称或代码。"),
                "province": _string("可选，招生省份名称或 province_id。"),
                "year": _integer("可选，招生年份。", minimum=2000, maximum=2100),
                "limit": _LIMIT,
            },
            ["school_text"],
        ),
    ),
    "specialty_group_risk": _function_schema(
        "specialty_group_risk",
        "基于专业组构成、计划数和是否允许调剂做调剂风险初筛。不提供真实分流比例或最终调剂结果。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "province": _string("可选，招生省份名称或 province_id。"),
                "subject_type": _string("可选，科类，例如 物理、历史、综合。"),
                "year": _integer("可选，招生年份。", minimum=2000, maximum=2100),
                "group_code": _string("可选，专业组代码。"),
                "major_text": _string("可选，专业名称、简称或代码。"),
            },
            ["school_text"],
        ),
    ),
    "comparison_query": _function_schema(
        "comparison_query",
        "对学校、专业或学校-专业方案做结构化并列对比。第一版只整理证据、口径和缺口，不替用户直接下最终选择。",
        _object_schema(
            {
                "target_type": _string("对比对象类型：school、major 或 school_major。"),
                "target_texts": _string_array("需要对比的对象文本，至少两个。例如 ['杭州电子科技大学','浙江大学'] 或 ['计算机','软件工程']。"),
                "major_text": _string("可选；当比较多个学校的同一专业时填写，例如 计算机。"),
                "province": _string("可选，考生所在省份；用于录取历史或专业组上下文。"),
                "subject_type": _string("可选，科类，例如 物理、历史、综合。"),
                "score": _number("可选，高考分数；第一版只作为后续位次匹配上下文。"),
                "rank": _integer("可选，考生位次。"),
                "year": _integer("可选，参考年份。", minimum=2000, maximum=2100),
                "dimensions": _string_array("可选，希望重点对比的维度，例如 录取、就业、城市、转专业。"),
                "limit": _integer("最多对比多少个对象。", minimum=2, maximum=10),
            },
            ["target_type", "target_texts"],
        ),
    ),
    "major_streaming_policy_lookup": _function_schema(
        "major_streaming_policy_lookup",
        "查询大类/专业分流政策和分流比例。当前没有官方分流比例事实时，只返回专业组上下文和 data_gaps，不编造比例。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "major_text": _string("可选，专业名称、简称或代码。"),
                "province": _string("可选，招生省份；用于查专业组上下文。"),
                "year": _integer("可选，招生或入学年份。", minimum=2000, maximum=2100),
                "limit": _LIMIT,
            },
            ["school_text"],
        ),
    ),
    "civil_service_mapping": _function_schema(
        "civil_service_mapping",
        "查询专业与考公岗位的映射线索。第一版包装岗位文本命中样本，并明确缺少正式可报条件判定。",
        _object_schema(
            {
                "major_text": _string("专业名称、简称或代码。"),
                "year": _integer("可选，国考/省考岗位年份。", minimum=2000, maximum=2100),
                "province": _string("可选，岗位所在省份。"),
                "limit": _LIMIT,
            },
            ["major_text"],
        ),
    ),
    "policy_rule_lookup": _function_schema(
        "policy_rule_lookup",
        "查询招生章程、批次规则、身体限制、单科要求、语种限制等高风险政策。没有官方来源时只返回缺口。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "policy_type": _string("可选，政策类型，例如 单科限制、身体条件、外语语种、中外合作、校区规则。"),
                "province": _string("可选，招生省份。"),
                "year": _integer("可选，政策年份。", minimum=2000, maximum=2100),
            },
            ["school_text"],
        ),
    ),
    "admission_history": _function_schema(
        "admission_history",
        "查询学校、专业、省份、科类、年份条件下的历史录取记录。历史录取不代表未来保证。",
        _object_schema(
            {
                "school_text": _string("可选，学校名称、简称或代码。"),
                "major_text": _string("可选，专业名称、简称或代码。"),
                "province": _string("可选，考生所在省份。"),
                "subject_type": _string("可选，物理/历史/综合等科类。"),
                "years": _integer_array("可选，需要查询的年份列表。"),
                "limit": _LIMIT,
            },
            [],
        ),
    ),
    "major_market_reference": _function_schema(
        "major_market_reference",
        "查询已接入的第三方专业市场观察数据，包括地域、行业、薪资参考和招聘样本。它不是某校某专业就业质量报告。",
        _object_schema(
            {
                "major_text": _string("专业名称、简称或代码。"),
                "sample_limit": _integer("最多返回多少条招聘样本。", minimum=1, maximum=50),
            },
            ["major_text"],
        ),
    ),
    "civil_service_role_search": _function_schema(
        "civil_service_role_search",
        "查询已接入考公岗位表中专业文本命中的岗位样本。命中不等于最终可报，必须提示以官方岗位表解释为准。",
        _object_schema(
            {
                "major_text": _string("专业名称、简称或代码。"),
                "year": _integer("可选，国考/省考岗位年份。", minimum=2000, maximum=2100),
                "province": _string("可选，岗位所在省份。"),
                "limit": _LIMIT,
            },
            ["major_text"],
        ),
    ),
    "data_gap_detection": _function_schema(
        "data_gap_detection",
        "根据问题类型和当前已有字段，返回回答该问题还缺哪些本地数据。搜不到时应触发补数/人工流程，而不是编造。",
        _object_schema(
            {
                "question_type": _string("问题类型，例如 school_major_profile。"),
                "available_fields": _string_array("当前检索结果已经覆盖的字段名列表。"),
            },
            ["question_type"],
        ),
    ),
    "web_evidence_search": _function_schema(
        "web_evidence_search",
        "通过已配置的免费 SearXNG 服务搜索外部网页证据。只在本地工具 not_found/partial、存在 data_gaps，或用户明确询问最新/官网/招生章程/政策/选科/学费/校区等时使用；结果必须作为外部证据引用 URL，不能当成本地库事实。",
        _object_schema(
            {
                "query": _string("要提交给搜索引擎的中文检索词，应包含学校/专业/年份/政策关键词等已确认实体。"),
                "search_scope": _string("可选检索范围，例如 official、admission、policy、general。"),
                "domains": _string_array("可选，限制搜索的域名列表，例如 hdu.edu.cn、chsi.com.cn。"),
                "limit": _LIMIT,
            },
            ["query"],
        ),
    ),
    "web_evidence_fetch": _function_schema(
        "web_evidence_fetch",
        "严谨版外部网页证据工具：先用 SearXNG 搜索候选来源，再抓取候选网页正文并抽取可引用证据片段。默认只采纳学校官网、省考试院、阳光高考等高可信来源；第三方来源只能作为线索。",
        _object_schema(
            {
                "query": _string("要搜索并核验的中文检索词，应包含学校、专业、年份、政策关键词等已确认实体。"),
                "search_scope": _string("可选检索范围，例如 official、admission、policy、general。"),
                "domains": _string_array("可选，限制搜索的域名列表，例如 sjtu.edu.cn、chsi.com.cn。"),
                "limit": _LIMIT,
                "fetch_limit": _integer("最多抓取多少个候选页面正文。", minimum=1, maximum=10),
                "evidence_limit": _integer("每个页面最多返回多少条证据片段。", minimum=1, maximum=10),
                "source_policy": _string("来源策略：official_only、trusted_first、official_first 或 any。默认 official_only。"),
            },
            ["query"],
        ),
    ),
    "web_gap_fill": _function_schema(
        "web_gap_fill",
        "基于结构化 gap_items 对本地数据库未命中的高考志愿信息进行有限轮次网页补全。它会优先抓取官方/考试院/阳光高考等可信来源，并区分 accepted_evidence、rejected_evidence 和 unfilled_gaps。",
        _object_schema(
            {
                "gap_items": {
                    "type": "array",
                    "description": "结构化缺口数组，通常来自 data_gap_detection 或本地工具结果缺口识别。",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "question": _string("可选，用户原始问题，用于生成更完整的搜索查询。"),
                "max_rounds": _integer("最多搜索补全多少轮。", minimum=1, maximum=5),
                "max_fetches_per_round": _integer("每轮最多抓取多少个候选页面。", minimum=1, maximum=10),
                "source_policy": _string("来源策略：official_only、trusted_first、official_first 或 any。默认 official_only。"),
                "max_seconds": _number("web_gap_fill overall timeout in seconds. When exhausted, the tool returns stop_reason=timeout_reached."),
            },
            ["gap_items"],
        ),
    ),
}


RETRIEVAL_FUNCTION_NAMES = tuple(_FUNCTION_SCHEMAS.keys())


def get_function_schemas() -> list[dict[str, Any]]:
    """Return all retrieval function schemas in deterministic registration order."""

    return [schema_for_tool(name) for name in RETRIEVAL_FUNCTION_NAMES]


def schema_for_tool(tool_name: str) -> dict[str, Any]:
    """Return one OpenAI-style function schema by retrieval tool name."""

    if tool_name not in _FUNCTION_SCHEMAS:
        raise KeyError(f"Unknown retrieval function schema: {tool_name}")
    # Return a deep JSON copy so callers cannot mutate the module-level registry
    # and accidentally affect later agent registrations in the same process.
    return json.loads(json.dumps(_FUNCTION_SCHEMAS[tool_name], ensure_ascii=False))


def call_retrieval_function(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    tools: RetrievalTools | Any | None = None,
) -> dict[str, Any]:
    """Call a retrieval function by name and keep failures inside the envelope."""

    if tool_name not in _FUNCTION_SCHEMAS:
        return tool_result(
            tool_name,
            "error",
            {"arguments": arguments},
            warnings=[f"unknown_tool: {tool_name} is not registered in retrieval function schemas."],
        )

    if not isinstance(arguments, dict):
        return tool_result(
            tool_name,
            "error",
            {"arguments": arguments},
            warnings=["arguments must be a JSON object before dispatching a retrieval function."],
        )

    parameters = _FUNCTION_SCHEMAS[tool_name]["function"]["parameters"]
    allowed = set(parameters.get("properties", {}))
    unexpected = sorted(set(arguments) - allowed)
    if unexpected:
        return tool_result(
            tool_name,
            "error",
            {"arguments": arguments},
            warnings=[f"unexpected argument(s): {', '.join(unexpected)}"],
        )

    missing = [
        name
        for name in parameters.get("required", [])
        if name not in arguments or arguments.get(name) in (None, "")
    ]
    if missing:
        return tool_result(
            tool_name,
            "needs_clarification",
            arguments,
            needs_clarification=missing,
            warnings=["required function-call slot(s) are missing."],
        )

    retrieval_tools = tools or RetrievalTools(MysqlCliClient(DbConfig.from_env()))
    method = getattr(retrieval_tools, tool_name, None)
    if method is None:
        return tool_result(
            tool_name,
            "error",
            arguments,
            warnings=[f"registered tool has no RetrievalTools method: {tool_name}"],
        )

    try:
        result = method(**arguments)
    except Exception as exc:  # pragma: no cover - defensive boundary for agent runtimes.
        return tool_result(
            tool_name,
            "error",
            arguments,
            warnings=[f"{type(exc).__name__}: {exc}"],
        )

    if not isinstance(result, dict):
        return tool_result(
            tool_name,
            "error",
            arguments,
            warnings=[f"{tool_name} returned a non-object result."],
        )
    return result


def _print_json(value: Any) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export or call retrieval function schemas.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-schemas", help="Print all function-call schemas as JSON.")
    subparsers.add_parser("list-names", help="Print registered function names as JSON.")

    call_parser = subparsers.add_parser("call", help="Call one retrieval function with a JSON argument object.")
    call_parser.add_argument("--tool", required=True)
    call_parser.add_argument("--arguments-json", default="{}")

    args = parser.parse_args(argv)
    if args.command == "list-schemas":
        _print_json(get_function_schemas())
        return 0
    if args.command == "list-names":
        _print_json(list(RETRIEVAL_FUNCTION_NAMES))
        return 0

    try:
        arguments = json.loads(args.arguments_json)
    except json.JSONDecodeError as exc:
        _print_json(
            tool_result(
                args.tool,
                "error",
                {"arguments_json": args.arguments_json},
                warnings=[f"arguments-json is not valid JSON: {exc}"],
            )
        )
        return 1

    _print_json(call_retrieval_function(args.tool, arguments))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
