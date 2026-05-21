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

# Direct execution (`python scripts/deepseek_retrieval_agent.py ...`) puts the
# scripts directory on sys.path.  Add the repository root so imports match unit
# tests and other project entrypoints.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.retrieval_function_registry import call_retrieval_function, get_function_schemas


DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"
DEFAULT_MAX_TOOL_ROUNDS = 6
DEFAULT_TEMPERATURE = 0.1
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
        disable_thinking: bool = True,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> None:
        self.client = client
        self.model = model
        self.tools = tools if tools is not None else get_function_schemas()
        self.dispatcher = dispatcher
        self.system_prompt = system_prompt
        self.max_tool_rounds = max_tool_rounds
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
            for tool_call in tool_calls:
                tool_result = self._execute_tool_call(tool_call)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": getattr(tool_call, "id", ""),
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )

        return "工具调用轮次过多，建议先把问题收窄到一个学校、专业、分数或位次场景。"

    def _create_completion(self, messages: list[dict[str, Any]]) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto",
            "temperature": self.temperature,
            "stream": False,
        }
        # DeepSeek's thinking mode adds extra state-management requirements for
        # reasoning_content.  The first integration keeps thinking disabled so
        # the tool loop mirrors the standard function-call flow.
        if self.disable_thinking:
            kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
        return self.client.chat.completions.create(**kwargs)

    def _execute_tool_call(self, tool_call: Any) -> dict[str, Any]:
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

        result = self.dispatcher(tool_name, arguments)
        self.tool_trace.append({"tool_name": tool_name, "arguments": arguments, "result": result})
        return result


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
