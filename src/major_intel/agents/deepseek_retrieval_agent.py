"""DeepSeek-backed agent loop for Major Intel retrieval functions.

This module is deliberately thin: it does not know SQL, table names, or gaokao
business facts.  Its job is to expose the existing function-call schemas to a
DeepSeek chat model, execute requested local tools through the registry
dispatcher, and feed structured tool results back to the model so the final
answer is grounded in the retrieval layer rather than model memory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Callable, Iterable

# Direct module execution puts this file's directory on sys.path.  Add `src/`
# so package imports behave the same as they do through the legacy wrapper.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from major_intel.function_calls.registry import call_retrieval_function, get_function_schemas
from major_intel.function_calls.retrieval_tools import _detect_tool_result_gaps


DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"
DEFAULT_MAX_TOOL_ROUNDS = 6
DEFAULT_MAX_TOOL_CALLS_PER_ROUND = 6
DEFAULT_TEMPERATURE = 0.1
LOOKUP_ONLY_TOOLS = {"school_lookup", "major_lookup"}
WEB_EVIDENCE_SEARCH_TOOL = "web_evidence_search"
WEB_EVIDENCE_FETCH_TOOL = "web_evidence_fetch"
WEB_GAP_FILL_TOOL = "web_gap_fill"
WEB_EVIDENCE_TOOL = WEB_EVIDENCE_SEARCH_TOOL
WEB_EVIDENCE_TOOLS = {WEB_EVIDENCE_SEARCH_TOOL, WEB_EVIDENCE_FETCH_TOOL, WEB_GAP_FILL_TOOL}
ANSWER_READY_STATUSES = {"ok", "partial"}
BLOCKING_STATUSES = {"needs_clarification", "not_found", "error", "skipped"}
PLACEHOLDER_API_KEYS = {"your_deepseek_api_key_here", "填入你的 DeepSeek API Key"}

DEFAULT_SYSTEM_PROMPT = """你是 Major Intel 的高考志愿填报小导师。
当用户问题涉及学校、专业、分数、位次、录取历史、就业市场、考公岗位或数据缺口时，优先调用工具。
不要编造本地工具没有返回的数据；如果工具返回 needs_clarification，请先追问缺失信息。
最终回答要保留工具 warnings、scope_notes、data_gaps 中对用户决策有影响的口径。
学校级、专业通用级、校专业级、招生专业组级、录取统计级数据不能混用。
回答要像一位认真帮学生和家长填志愿的小导师：先给明确判断，再解释依据，然后说明适合什么样的考生、不适合什么情况、还需要核实哪些风险。
结尾给出可执行的下一步建议，例如让用户补充省份、科类、分数或位次，以便继续做冲稳保判断。
整体表达保持自然、清晰、有人味。不要机械、严肃到像教科书，也不要像新闻稿或咨询报告。
当用户犹豫或迷茫时，优先帮他收窄选择，给一个可以继续讨论的方向，而不是铺满所有可能性。
当用户选择明显不合理或存在滑档、专业错配、就业预期过高等风险时，要直接指出风险；可以轻轻泼一点冷水，但不能攻击用户、不能阴阳怪气。
用户没有主动要求详细展开时，不要长篇解释；先用短判断回应，再补关键逻辑。
输出风格必须严肃、克制、咨询报告式；不要使用 emoji、装饰性分割线、营销口号或过度口语化表达。
除非用户明确要求，不要使用任何 Markdown 装饰语法，包括 # 标题、**粗体**、表格、--- 分隔线；优先用短段落和简洁条目。"""

DEFAULT_SYSTEM_PROMPT += """
工具收敛规则：
如果工具返回 not_found，不要猜测新的学校、专业、分数、位次或年份继续重试；直接说明当前库查不到，并说明还需要什么信息或数据。
如果工具返回 needs_clarification，不要替用户选择候选项，不要把第一个候选当作已确认实体；直接追问缺失槽位或让用户确认候选。
如果已经有非 lookup 工具返回 ok 或 partial，优先基于已有结果回答，不要继续横向调用更多工具。
如果一轮工具调用没有新增可用数据，停止继续调用工具，基于 warnings、scope_notes、data_gaps 给出受限结论。
"""

DEFAULT_SYSTEM_PROMPT += """
工具选择规则：
school_major_list 不接受 major_text，只用于查询某学校的专业列表，或用 major_category 做宽泛专业类筛选。
用户问“学校+专业”是否开设、某校某专业怎么样、某校某专业证据时，应调用 school_major_profile。
用户问“专业+地区/层次”有哪些学校开设时，应调用 major_school_list。
不要把具体专业名塞进 school_major_list；不要把 school_major_list 当成学校+专业关系查询工具。
"""

DEFAULT_SYSTEM_PROMPT += """
网页搜索规则：优先使用本地数据库工具；只有本地工具返回 not_found/partial、结果包含 data_gaps，或用户明确询问最新、官网、招生章程、政策、选科、学费、校区等时效性信息时，才调用网页证据工具。
web_evidence_search 返回的是外部候选证据，不是本地库事实；最终回答必须说明来源 URL，并区分“本地库记录”和“网页证据”。"""

DEFAULT_SYSTEM_PROMPT += """
严谨网页证据规则：如果 web_gap_fill 可用，应优先使用它，因为它会围绕结构化缺口进行多轮搜索、抓取和证据评估；否则优先使用 web_evidence_fetch，因为它会抓取网页正文并返回 evidence_snippets。web_evidence_search 只代表搜索结果摘要，不能当作已阅读网页正文。回答必须区分本地库事实、官方网页正文证据、第三方网页线索。
web_evidence_fetch 的 search_results 只能作为候选，不能写成事实；最终回答只能使用 pages.evidence_snippets 中能直接支撑结论的正文片段。
如果 web_gap_fill 返回 data.coverage_status=partial/insufficient，或 unfilled_gaps 包含 list_coverage_incomplete，只能说“本轮可确认”“暂未确认其它”，不能写成“只有这些学校”“全部名单”“完整名单”或“其它学校都没有”。"""

ToolDispatcher = Callable[[str, dict[str, Any]], dict[str, Any]]


def load_env_file(path: Path) -> dict[str, str]:
    """Read a tiny dotenv-style file without adding a runtime dependency.

    The agent only needs an API-key placeholder path for local experiments, so a
    small parser is safer than requiring python-dotenv in the repository root.
    It intentionally supports the common KEY=value shape and simple quoting,
    while ignoring comments and malformed lines.
    """

    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_env_files(paths: Iterable[Path]) -> None:
    """Populate missing environment variables from local env files.

    Existing environment variables win.  This prevents a checked example file
    or stale local file from overriding an explicit shell setting.
    """

    for path in paths:
        for key, value in load_env_file(path).items():
            os.environ.setdefault(key, value)


def resolve_deepseek_api_key(explicit_api_key: str | None = None) -> str:
    """Return the DeepSeek API key or raise a user-actionable configuration error."""

    # Load the whole env file before resolving the key.  Besides the API key,
    # the retrieval tools also depend on GAOKAO_DB_* values from the same file.
    load_env_files([PROJECT_ROOT / ".env", PROJECT_ROOT / ".env.deepseek"])
    if explicit_api_key:
        if not _is_placeholder_api_key(explicit_api_key):
            return explicit_api_key
        raise _missing_api_key_error()
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if api_key and not _is_placeholder_api_key(api_key):
        return api_key
    raise _missing_api_key_error()


def _missing_api_key_error() -> RuntimeError:
    return RuntimeError(
        "DEEPSEEK_API_KEY is not set. Copy .env.example to .env and fill in "
        "DEEPSEEK_API_KEY, or pass --api-key when running this script."
    )


def _is_placeholder_api_key(value: str) -> bool:
    return value.strip() in PLACEHOLDER_API_KEYS


def configure_utf8_stdio(stdout: Any = sys.stdout, stderr: Any = sys.stderr) -> None:
    """Keep CLI output usable when model text contains non-GBK characters."""

    for stream in (stdout, stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def clean_answer_text(text: str) -> str:
    """Remove decorative markup that makes CLI answers look noisy.

    This does not rewrite facts or reorder content.  It only strips presentation
    characters that the model may emit despite a plain, serious style prompt.
    """

    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue
        if re.fullmatch(r"[-_*=\s]{3,}", line):
            continue
        line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
        line = line.replace("**", "").replace("__", "")
        line = _remove_emoji(line).strip()
        lines.append(line)

    cleaned = "\n".join(lines).strip()
    return re.sub(r"\n{3,}", "\n\n", cleaned)


def _remove_emoji(text: str) -> str:
    return "".join(char for char in text if not _is_emoji_or_symbol(char))


def _is_emoji_or_symbol(char: str) -> bool:
    codepoint = ord(char)
    if 0x1F000 <= codepoint <= 0x1FAFF:
        return True
    if codepoint in {0xFE0F, 0x200D}:
        return True
    return unicodedata.category(char) == "So"


def build_deepseek_client(api_key: str | None = None, base_url: str = DEFAULT_DEEPSEEK_BASE_URL) -> Any:
    """Create an OpenAI-compatible client for DeepSeek.

    The root project currently does not require the OpenAI SDK for unit tests,
    so the import is lazy.  Runtime users get a clear install hint instead of an
    import traceback before they have filled the API key.
    """

    resolved_api_key = resolve_deepseek_api_key(api_key)
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:  # pragma: no cover - environment-specific.
        raise RuntimeError("The openai package is required. Install it with: pip install openai") from exc

    return OpenAI(api_key=resolved_api_key, base_url=base_url)


class DeepSeekRetrievalAgent:
    """Run a DeepSeek tool-call loop over the local retrieval function registry.

    The model is allowed to choose tools, but every tool execution crosses the
    registry dispatcher.  That boundary keeps validation, unknown-tool handling,
    and common result envelopes in one place instead of scattering safeguards
    through the agent loop.
    """

    def __init__(
        self,
        *,
        client: Any,
        model: str = DEFAULT_DEEPSEEK_MODEL,
        tools: list[dict[str, Any]] | None = None,
        dispatcher: ToolDispatcher = call_retrieval_function,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS,
        max_tool_calls_per_round: int = DEFAULT_MAX_TOOL_CALLS_PER_ROUND,
        disable_thinking: bool = True,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> None:
        self.client = client
        self.model = model
        self.tools = tools if tools is not None else get_function_schemas()
        self.dispatcher = dispatcher
        self.system_prompt = system_prompt
        self.max_tool_rounds = max_tool_rounds
        self.max_tool_calls_per_round = max_tool_calls_per_round
        self.disable_thinking = disable_thinking
        self.temperature = temperature
        self.tool_trace: list[dict[str, Any]] = []

    def run(self, user_text: str, history: list[dict[str, Any]] | None = None) -> str:
        """Answer one user turn, executing local retrieval tools when requested."""

        messages: list[dict[str, Any]] = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history or [])
        messages.append({"role": "user", "content": user_text})

        for _ in range(self.max_tool_rounds):
            response = self._create_completion(messages)
            message = response.choices[0].message
            tool_calls = list(getattr(message, "tool_calls", None) or [])
            if not tool_calls:
                return clean_answer_text(getattr(message, "content", None) or "")

            messages.append(_message_to_dict(message))
            round_results: list[dict[str, Any]] = []
            for index, tool_call in enumerate(tool_calls):
                if index >= self.max_tool_calls_per_round:
                    tool_result = self._skipped_tool_call_result(tool_call)
                else:
                    tool_result = self._execute_tool_call(tool_call, user_text=user_text)
                round_results.append(
                    {
                        "tool_name": tool_result.get("tool_name", ""),
                        "status": tool_result.get("status"),
                        "result": tool_result,
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": getattr(tool_call, "id", ""),
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )

            final_reason = _forced_final_reason(round_results)
            if final_reason and self._should_auto_web_fallback(round_results):
                web_result = self._execute_auto_web_fallback(user_text, round_results)
                round_results.append(
                    {
                        "tool_name": web_result.get("tool_name", WEB_EVIDENCE_SEARCH_TOOL),
                        "status": web_result.get("status"),
                        "result": web_result,
                    }
                )
                messages.append({"role": "assistant", "content": _auto_web_fallback_context(web_result)})
                final_reason = _forced_final_reason(round_results)
            if final_reason:
                return self._forced_final_answer(messages, final_reason)

        return self._forced_final_answer(messages, "too_many_tool_rounds")

    def _create_completion(self, messages: list[dict[str, Any]], *, allow_tools: bool = True) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "tool_choice": "auto" if allow_tools else "none",
            "temperature": self.temperature,
            "stream": False,
        }
        if allow_tools:
            kwargs["tools"] = self.tools
        # DeepSeek's thinking mode adds extra state-management requirements for
        # reasoning_content.  The first integration keeps thinking disabled so
        # the tool loop mirrors the standard function-call flow.
        if self.disable_thinking:
            kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
        return self.client.chat.completions.create(**kwargs)

    def _execute_tool_call(self, tool_call: Any, *, user_text: str = "") -> dict[str, Any]:
        function = getattr(tool_call, "function", None)
        tool_name = getattr(function, "name", "")
        raw_arguments = getattr(function, "arguments", "") or "{}"

        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError as exc:
            result = _tool_error(
                tool_name,
                {"raw_arguments": raw_arguments},
                f"tool arguments are not valid JSON: {exc}",
            )
            self.tool_trace.append({"tool_name": tool_name, "arguments": raw_arguments, "result": result})
            return result

        if not isinstance(arguments, dict):
            result = _tool_error(tool_name, {"arguments": arguments}, "tool arguments must be a JSON object.")
            self.tool_trace.append({"tool_name": tool_name, "arguments": arguments, "result": result})
            return result

        redirected_from = ""
        redirected = self._redirect_web_evidence_tool(tool_name, arguments, user_text)
        if redirected:
            redirected_from = tool_name
            tool_name, arguments = redirected

        result = self.dispatcher(tool_name, arguments)
        trace_item = {"tool_name": tool_name, "arguments": arguments, "result": result}
        if redirected_from:
            trace_item["redirected_from"] = redirected_from
        self.tool_trace.append(trace_item)
        return result

    def _redirect_web_evidence_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        user_text: str,
    ) -> tuple[str, dict[str, Any]] | None:
        if tool_name not in {WEB_EVIDENCE_SEARCH_TOOL, WEB_EVIDENCE_FETCH_TOOL}:
            return None
        if not _tool_available(self.tools, WEB_GAP_FILL_TOOL):
            return None
        if any(item.get("tool_name") == WEB_GAP_FILL_TOOL for item in self.tool_trace):
            return None

        gap_items = _build_web_fallback_gap_items(
            [
                {
                    "tool_name": item.get("tool_name"),
                    "status": (item.get("result") or {}).get("status") if isinstance(item.get("result"), dict) else None,
                    "result": item.get("result"),
                }
                for item in self.tool_trace
                if isinstance(item, dict)
            ]
        )
        if not gap_items:
            return None

        return (
            WEB_GAP_FILL_TOOL,
            {
                "gap_items": gap_items,
                "question": user_text or _clean_query_part(arguments.get("query")),
                "max_rounds": _web_gap_fill_max_rounds(),
                "max_fetches_per_round": _web_gap_fill_fetches_per_round(),
                "max_seconds": _web_gap_fill_max_seconds(),
                "source_policy": "official_only",
            },
        )

    def _skipped_tool_call_result(self, tool_call: Any) -> dict[str, Any]:
        function = getattr(tool_call, "function", None)
        tool_name = getattr(function, "name", "")
        raw_arguments = getattr(function, "arguments", "") or "{}"
        result = _tool_error(
            tool_name,
            {"raw_arguments": raw_arguments},
            "tool call skipped because the model requested too many tools in one round.",
        )
        result["status"] = "skipped"
        self.tool_trace.append({"tool_name": tool_name, "arguments": raw_arguments, "result": result})
        return result

    def _should_auto_web_fallback(self, round_results: list[dict[str, Any]]) -> bool:
        if not _web_fallback_enabled():
            return False
        if not _web_fallback_tool_name(self.tools):
            return False
        if any(result.get("tool_name") in WEB_EVIDENCE_TOOLS for result in round_results):
            return False

        for round_result in round_results:
            tool_name = str(round_result.get("tool_name") or "")
            if tool_name in LOOKUP_ONLY_TOOLS or tool_name in WEB_EVIDENCE_TOOLS:
                continue
            status = str(round_result.get("status") or "")
            result = round_result.get("result") if isinstance(round_result.get("result"), dict) else {}
            if status == "not_found":
                return True
            if status == "partial" and result.get("data_gaps"):
                return True
        return False

    def _execute_auto_web_fallback(self, user_text: str, round_results: list[dict[str, Any]]) -> dict[str, Any]:
        tool_name = _web_fallback_tool_name(self.tools) or WEB_EVIDENCE_SEARCH_TOOL
        if tool_name == WEB_GAP_FILL_TOOL:
            gap_items = _build_web_fallback_gap_items(round_results)
            if gap_items:
                arguments = {
                    "gap_items": gap_items,
                    "question": user_text,
                    "max_rounds": _web_gap_fill_max_rounds(),
                    "max_fetches_per_round": _web_gap_fill_fetches_per_round(),
                    "max_seconds": _web_gap_fill_max_seconds(),
                    "source_policy": "official_only",
                }
            else:
                tool_name = WEB_EVIDENCE_FETCH_TOOL if _tool_available(self.tools, WEB_EVIDENCE_FETCH_TOOL) else WEB_EVIDENCE_SEARCH_TOOL
                arguments = {
                    "query": _build_web_fallback_query(user_text, round_results),
                    "search_scope": "official",
                    "limit": _web_fallback_limit(),
                }
        else:
            arguments = {
                "query": _build_web_fallback_query(user_text, round_results),
                "search_scope": "official",
                "limit": _web_fallback_limit(),
            }
        if tool_name == WEB_EVIDENCE_FETCH_TOOL:
            arguments.update(
                {
                    "fetch_limit": _web_fetch_limit(),
                    "evidence_limit": _web_evidence_limit(),
                    "source_policy": "official_only",
                }
            )
        result = self.dispatcher(tool_name, arguments)
        self.tool_trace.append({"tool_name": tool_name, "arguments": arguments, "result": result, "auto": True})
        return result

    def _forced_final_answer(self, messages: list[dict[str, Any]], reason: str) -> str:
        final_messages = list(messages)
        final_messages.append({"role": "user", "content": _forced_final_instruction(reason)})
        response = self._create_completion(final_messages, allow_tools=False)
        message = response.choices[0].message
        if list(getattr(message, "tool_calls", None) or []):
            return _fallback_final_answer(reason)
        answer = clean_answer_text(getattr(message, "content", None) or _fallback_final_answer(reason))
        return _apply_final_answer_guardrails(answer, self.tool_trace)


def _forced_final_reason(round_results: list[dict[str, Any]]) -> str | None:
    if not round_results:
        return "no_tool_results"

    statuses = {str(result.get("status") or "") for result in round_results}
    if statuses & {"needs_clarification", "error", "skipped"}:
        return "blocking_status"

    answer_ready = any(
        result.get("tool_name") not in LOOKUP_ONLY_TOOLS
        and result.get("status") in ANSWER_READY_STATUSES
        for result in round_results
    )
    if answer_ready:
        return "answer_ready"

    if "not_found" in statuses:
        return "not_found"

    has_useful_lookup = any(result.get("status") in ANSWER_READY_STATUSES for result in round_results)
    if not has_useful_lookup:
        return "no_useful_tool_data"
    return None


def _web_fallback_enabled() -> bool:
    return os.environ.get("WEB_SEARCH_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}


def _web_fallback_limit() -> int:
    raw = os.environ.get("WEB_SEARCH_MAX_RESULTS", "").strip()
    try:
        value = int(raw)
    except ValueError:
        return 5
    return min(max(value, 1), 10)


def _web_fetch_limit() -> int:
    raw = os.environ.get("WEB_FETCH_MAX_PAGES", "").strip()
    try:
        value = int(raw)
    except ValueError:
        return 3
    return min(max(value, 1), 10)


def _web_evidence_limit() -> int:
    raw = os.environ.get("WEB_FETCH_EVIDENCE_LIMIT", "").strip()
    try:
        value = int(raw)
    except ValueError:
        return 5
    return min(max(value, 1), 10)


def _web_gap_fill_max_rounds() -> int:
    raw = os.environ.get("WEB_GAP_FILL_MAX_ROUNDS", "").strip()
    try:
        value = int(raw)
    except ValueError:
        return 3
    return min(max(value, 1), 5)


def _web_gap_fill_fetches_per_round() -> int:
    raw = os.environ.get("WEB_GAP_FILL_FETCHES_PER_ROUND", "").strip()
    try:
        value = int(raw)
    except ValueError:
        return _web_fetch_limit()
    return min(max(value, 1), 10)


def _web_gap_fill_max_seconds() -> float:
    raw = os.environ.get("WEB_GAP_FILL_MAX_SECONDS", "").strip()
    try:
        value = float(raw)
    except ValueError:
        return 45.0
    return min(max(value, 1.0), 300.0)


def _web_fallback_tool_name(tools: list[dict[str, Any]]) -> str | None:
    if _tool_available(tools, WEB_GAP_FILL_TOOL):
        return WEB_GAP_FILL_TOOL
    if _tool_available(tools, WEB_EVIDENCE_FETCH_TOOL):
        return WEB_EVIDENCE_FETCH_TOOL
    if _tool_available(tools, WEB_EVIDENCE_SEARCH_TOOL):
        return WEB_EVIDENCE_SEARCH_TOOL
    return None


def _tool_available(tools: list[dict[str, Any]], tool_name: str) -> bool:
    for schema in tools:
        function = schema.get("function") if isinstance(schema, dict) else None
        if isinstance(function, dict) and function.get("name") == tool_name:
            return True
    return False


def _build_web_fallback_query(user_text: str, round_results: list[dict[str, Any]]) -> str:
    parts = [_clean_query_part(user_text)]
    for round_result in round_results:
        result = round_result.get("result") if isinstance(round_result.get("result"), dict) else {}
        _extend_query_parts(parts, result.get("input"))
        _extend_query_parts(parts, result.get("normalized_slots"))
        _extend_query_parts(parts, result.get("data_gaps"))
    return _dedupe_query_parts(parts)


def _build_web_fallback_gap_items(round_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gap_items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for round_result in round_results:
        tool_name = str(round_result.get("tool_name") or "")
        result = round_result.get("result") if isinstance(round_result.get("result"), dict) else {}
        for gap in _detect_tool_result_gaps(tool_name, result):
            if not gap.get("resolvable_by_web"):
                continue
            key = json.dumps(
                {
                    "gap_key": gap.get("gap_key"),
                    "normalized_slots": gap.get("normalized_slots") or {},
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            if key in seen:
                continue
            seen.add(key)
            gap_items.append(gap)
    return gap_items


def _extend_query_parts(parts: list[str], value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"limit", "reference_years", "available_fields"}:
                continue
            _extend_query_parts(parts, item)
        return
    if isinstance(value, list):
        for item in value[:3]:
            _extend_query_parts(parts, item)
        return
    text = _clean_query_part(value)
    if text:
        parts.append(text)


def _dedupe_query_parts(parts: list[str]) -> str:
    seen: set[str] = set()
    deduped: list[str] = []
    for part in parts:
        if not part or part in seen:
            continue
        seen.add(part)
        deduped.append(part)
    query = " ".join(deduped)
    return query[:240].strip() or "招生 官网"


def _clean_query_part(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text.upper() == "NULL":
        return ""
    return re.sub(r"\s+", " ", text)


def _auto_web_fallback_context(web_result: dict[str, Any]) -> str:
    return (
        "自动网页证据结果（本地检索缺口后的外部候选证据，回答时必须区分本地库、accepted_evidence、rejected_evidence 和 unfilled_gaps）：\n"
        + json.dumps(web_result, ensure_ascii=False, indent=2)
    )


def _forced_final_instruction(reason: str) -> str:
    return (
        "不要继续调用工具。请只根据上面的工具结果回答用户。"
        "如果工具状态是 needs_clarification，请追问缺失信息或让用户确认候选，不能替用户猜。"
        "如果工具状态是 not_found 或 error，请说明当前库查不到或无法验证，不能更换参数继续猜。"
        "如果已有 ok 或 partial 结果，请基于已有结果、warnings、scope_notes 和 data_gaps 给出受限结论。"
        "如果上文包含 web_gap_fill 结果，只能把 accepted_evidence / filled_items 写成事实，并说明 unfilled_gaps；rejected_evidence 只能作为未确认线索。"
        "如果 web_gap_fill 的 data.coverage_status 是 partial/insufficient，或 unfilled_gaps 包含 list_coverage_incomplete，只能写成本轮已确认结果；不能使用“只有这些学校”“全部名单”“完整名单”或“其它学校都没有”这类完整性结论。"
        "如果上文包含 web_evidence_search 结果，必须明确列出使用的 URL；如果来源为第三方，要说明只能作为线索。"
        f"收口原因：{reason}。"
    )


def _fallback_final_answer(reason: str) -> str:
    return (
        "当前工具调用已经触发收口条件。请根据已有工具结果判断："
        "如果需要澄清，先追问；如果查不到数据，明确说明当前库没有命中；"
        "如果已有可用结果，基于结果和 warnings 给出受限回答。"
        f"收口原因：{reason}。"
    )


def _apply_final_answer_guardrails(answer: str, tool_trace: list[dict[str, Any]]) -> str:
    guarded = answer
    if _has_partial_list_coverage(tool_trace):
        guarded = guarded.replace("只有一所", "本轮只确认到一所")
        guarded = guarded.replace("仅有一所", "本轮只确认到一所")
        guarded = guarded.replace("只有以下", "本轮可确认以下")
        guarded = guarded.replace("仅有以下", "本轮可确认以下")

        if "不代表完整名单" not in guarded and "可能存在遗漏" not in guarded and "部分覆盖" not in guarded:
            guarded = guarded.rstrip() + "\n\n注意：网页证据只完成部分覆盖，以上不代表完整名单。"

    unfilled_labels = _web_gap_unfilled_labels(tool_trace)
    if unfilled_labels and "不能作为已核验结论" not in guarded:
        guarded = (
            guarded.rstrip()
            + "\n\n注意：web_gap_fill 仍未填补："
            + "、".join(unfilled_labels)
            + "；这些点不能作为已核验结论。"
        )
    return guarded


def _web_gap_unfilled_labels(tool_trace: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    seen: set[str] = set()
    for item in tool_trace:
        result = item.get("result") if isinstance(item, dict) else None
        if not isinstance(result, dict) or result.get("tool_name") != WEB_GAP_FILL_TOOL:
            continue
        data = result.get("data") if isinstance(result.get("data"), dict) else {}
        for gap in data.get("unfilled_gaps") or []:
            if not isinstance(gap, dict):
                continue
            label = _clean_query_part(gap.get("label") or gap.get("gap_key"))
            if not label or label in seen:
                continue
            seen.add(label)
            labels.append(label)
    return labels


def _has_partial_list_coverage(tool_trace: list[dict[str, Any]]) -> bool:
    for item in tool_trace:
        result = item.get("result") if isinstance(item, dict) else None
        if not isinstance(result, dict) or result.get("tool_name") != WEB_GAP_FILL_TOOL:
            continue
        data = result.get("data") if isinstance(result.get("data"), dict) else {}
        if data.get("coverage_status") in {"partial", "insufficient"}:
            return True
        for gap in data.get("unfilled_gaps") or []:
            if isinstance(gap, dict) and gap.get("unfilled_reason") == "list_coverage_incomplete":
                return True
    return False


def _tool_error(tool_name: str, input_data: dict[str, Any], warning: str) -> dict[str, Any]:
    return {
        "tool_name": tool_name,
        "status": "error",
        "input": input_data,
        "normalized_slots": {},
        "data": {},
        "scope_notes": [],
        "data_gaps": [],
        "needs_clarification": [],
        "source_tables": [],
        "warnings": [warning],
    }


def _message_to_dict(message: Any) -> dict[str, Any]:
    if isinstance(message, dict):
        return message
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)

    payload: dict[str, Any] = {
        "role": getattr(message, "role", "assistant"),
        "content": getattr(message, "content", None),
    }
    tool_calls = list(getattr(message, "tool_calls", None) or [])
    if tool_calls:
        payload["tool_calls"] = [_tool_call_to_dict(tool_call) for tool_call in tool_calls]
    return payload


def _tool_call_to_dict(tool_call: Any) -> dict[str, Any]:
    if isinstance(tool_call, dict):
        return tool_call
    if hasattr(tool_call, "model_dump"):
        return tool_call.model_dump(exclude_none=True)

    function = getattr(tool_call, "function", None)
    return {
        "id": getattr(tool_call, "id", ""),
        "type": getattr(tool_call, "type", "function"),
        "function": {
            "name": getattr(function, "name", ""),
            "arguments": getattr(function, "arguments", "{}"),
        },
    }


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Run a DeepSeek tool-call agent over local retrieval tools.")
    parser.add_argument("prompt", help="User question to answer.")
    parser.add_argument("--api-key", help="DeepSeek API key. Prefer DEEPSEEK_API_KEY in .env for normal use.")
    parser.add_argument("--base-url", default=DEFAULT_DEEPSEEK_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_DEEPSEEK_MODEL)
    parser.add_argument("--max-tool-rounds", type=int, default=DEFAULT_MAX_TOOL_ROUNDS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--show-trace", action="store_true", help="Print executed tool calls after the answer.")
    args = parser.parse_args(argv)

    try:
        client = build_deepseek_client(api_key=args.api_key, base_url=args.base_url)
        agent = DeepSeekRetrievalAgent(
            client=client,
            model=args.model,
            max_tool_rounds=args.max_tool_rounds,
            temperature=args.temperature,
        )
        answer = agent.run(args.prompt)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(answer)
    if args.show_trace:
        print(json.dumps(agent.tool_trace, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
