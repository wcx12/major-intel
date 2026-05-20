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
        "查询某学校在本地库记录的开设专业列表。它不等于某省某年的招生专业列表。",
        _object_schema(
            {
                "school_text": _string("学校名称、简称或代码。"),
                "major_category": _string("可选的专业类/门类筛选词，例如 计算机类、工学。"),
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
                "subject_type": _string("科类，例如 物理、历史、综合。"),
                "score": _number("高考分数。"),
                "year": _integer("可选，一分一段年份；不填时默认查本地最新年份。", minimum=2000, maximum=2100),
            },
            ["province", "subject_type", "score"],
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
