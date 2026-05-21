"""Unified retrieval entrypoint that coordinates rules and DeepSeek tool calls.

The project now has two useful ways to turn a student question into local
retrieval work:

1. `NaturalLanguageEntryPoint` is deterministic and cheap.  It is good for
   high-frequency questions where rules can safely extract slots and build a
   tool plan.
2. `DeepSeekRetrievalAgent` is flexible.  It exposes the same local function
   schemas to an LLM and lets the model choose tools for fuzzy, multi-intent, or
   conversational questions.

This module is the thin official boundary above both.  It keeps the routing
decision explicit so later cache, query-log, and data-gap queue code has one
place to hook into instead of duplicating logic across scripts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

# Direct CLI execution (`python scripts/retrieval_agent_entrypoint.py ...`) puts
# `scripts/` on sys.path.  Add the repository root so imports behave the same
# in unit tests, scheduled jobs, and manual runs.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.deepseek_retrieval_agent import (
    DEFAULT_DEEPSEEK_BASE_URL,
    DEFAULT_DEEPSEEK_MODEL,
    DEFAULT_MAX_TOOL_ROUNDS,
    DEFAULT_TEMPERATURE,
    DeepSeekRetrievalAgent,
    build_deepseek_client,
    configure_utf8_stdio,
)
from scripts.agent_query_storage import MysqlAgentQueryStorage, build_cache_identity, build_data_gap_items
from scripts.natural_language_entrypoint import NaturalLanguageEntryPoint


DeepSeekAgentFactory = Callable[[], Any]


RULE_TERMINAL_STATUSES = {"ok", "partial", "not_found", "needs_clarification", "planned"}
LLM_FALLBACK_INTENTS = {"unknown", "comparison_query"}


class HybridRetrievalEntryPoint:
    """Choose between deterministic routing and the DeepSeek tool-call loop.

    The class returns a structured envelope rather than only text.  This is
    intentional: the next phase will write `route`, `rule_preflight`,
    `tool_trace`, `warnings`, and `data_gaps` into cache/log tables.  Keeping
    those fields stable now makes that database work much less surprising.
    """

    def __init__(
        self,
        *,
        rule_entrypoint: Any | None = None,
        deepseek_agent_factory: DeepSeekAgentFactory | None = None,
        storage: Any | None = None,
        cache_ttl_seconds: int | None = None,
    ) -> None:
        self.rule_entrypoint = rule_entrypoint or NaturalLanguageEntryPoint()
        self.deepseek_agent_factory = deepseek_agent_factory or _default_deepseek_agent_factory
        self.storage = storage
        self.cache_ttl_seconds = cache_ttl_seconds

    def run(
        self,
        question: str,
        *,
        mode: str = "auto",
        session_id: str | None = None,
        session_context: dict[str, Any] | None = None,
        execute: bool = True,
    ) -> dict[str, Any]:
        """Answer one question through `rules`, `deepseek`, or `auto` mode."""

        if mode not in {"auto", "rules", "deepseek"}:
            result = _error_envelope(
                question,
                route="none",
                warning=f"unknown entrypoint mode: {mode}",
                rule_preflight=None,
            )
            return self._persist_and_return(
                question,
                mode=mode,
                session_id=session_id,
                result=result,
                cache_key=None,
                cache_source=None,
                cacheable=False,
            )

        if mode == "deepseek":
            return self._run_deepseek_with_cache(question, mode=mode, session_id=session_id, rule_preflight=None)

        # With storage enabled we first ask the deterministic router for a cheap
        # plan (`execute=False`).  That gives us a stable cache identity before
        # hitting MySQL retrieval tools or a remote LLM.
        if self.storage is not None:
            rule_preflight = self.rule_entrypoint.run(question, session_context=session_context or {}, execute=False)
            route = "rules" if mode == "rules" or _should_keep_rule_result(rule_preflight) else "deepseek"
            cache_key, cache_source = build_cache_identity(
                question=question,
                mode=mode,
                route=route,
                intent=rule_preflight.get("intent"),
                slots=rule_preflight.get("slots") or {},
                tool_plan=rule_preflight.get("tool_plan") or [],
            )
            cached = self._try_cache_hit(question, mode=mode, session_id=session_id, cache_key=cache_key)
            if cached is not None:
                return cached

            if route == "rules":
                rule_result = rule_preflight if not execute else self.rule_entrypoint.run(
                    question,
                    session_context=session_context or {},
                    execute=True,
                )
                return self._persist_and_return(
                    question,
                    mode=mode,
                    session_id=session_id,
                    result=_wrap_rule_result(question, rule_result),
                    cache_key=cache_key,
                    cache_source=cache_source,
                    cacheable=execute,
                )

            return self._run_deepseek_with_cache(
                question,
                mode=mode,
                session_id=session_id,
                rule_preflight=rule_preflight,
                cache_key=cache_key,
                cache_source=cache_source,
            )

        rule_result = self.rule_entrypoint.run(question, session_context=session_context or {}, execute=execute)
        if mode == "rules" or _should_keep_rule_result(rule_result):
            return _wrap_rule_result(question, rule_result)

        return self._run_deepseek(question, rule_preflight=rule_result)

    def _run_deepseek_with_cache(
        self,
        question: str,
        *,
        mode: str,
        session_id: str | None,
        rule_preflight: dict[str, Any] | None,
        cache_key: str | None = None,
        cache_source: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run DeepSeek with optional cache lookup/persistence around it."""

        if self.storage is not None and cache_key is None:
            cache_key, cache_source = build_cache_identity(
                question=question,
                mode=mode,
                route="deepseek",
                intent=rule_preflight.get("intent") if rule_preflight else None,
                slots=rule_preflight.get("slots") if rule_preflight else {},
                tool_plan=rule_preflight.get("tool_plan") if rule_preflight else [],
            )
            cached = self._try_cache_hit(question, mode=mode, session_id=session_id, cache_key=cache_key)
            if cached is not None:
                return cached

        result = self._run_deepseek(question, rule_preflight=rule_preflight)
        return self._persist_and_return(
            question,
            mode=mode,
            session_id=session_id,
            result=result,
            cache_key=cache_key,
            cache_source=cache_source,
            cacheable=True,
        )

    def _run_deepseek(self, question: str, *, rule_preflight: dict[str, Any] | None) -> dict[str, Any]:
        """Run DeepSeek safely and convert its answer into the shared envelope."""

        try:
            agent = self.deepseek_agent_factory()
            answer = agent.run(question)
        except Exception as exc:
            # Missing API keys, SDK installation problems, or upstream LLM
            # failures should be visible to the caller as operational errors.
            # We do not fall back to model memory or invent an answer.
            return _error_envelope(
                question,
                route="deepseek",
                warning=f"{type(exc).__name__}: {exc}",
                rule_preflight=rule_preflight,
            )

        tool_trace = list(getattr(agent, "tool_trace", []) or [])
        return {
            "status": "ok",
            "route": "deepseek",
            "question": question,
            "intent": None,
            "slots": {},
            "needs_clarification": [],
            "tool_plan": [],
            "tool_trace": tool_trace,
            "rule_preflight": rule_preflight,
            "data_gaps": _collect_from_trace(tool_trace, "data_gaps"),
            "scope_notes": _collect_from_trace(tool_trace, "scope_notes"),
            "warnings": _collect_from_trace(tool_trace, "warnings"),
            "answer_markdown": answer,
        }

    def _try_cache_hit(
        self,
        question: str,
        *,
        mode: str,
        session_id: str | None,
        cache_key: str,
    ) -> dict[str, Any] | None:
        """Return a cached result and write a cache-hit query log if available."""

        if self.storage is None:
            return None
        cached = self.storage.get_cached_result(cache_key)
        if cached is None:
            return None
        result = dict(cached)
        result["cache_hit"] = True
        result["cache_key"] = cache_key
        self._write_storage_records(
            question,
            mode=mode,
            session_id=session_id,
            result=result,
            cache_key=cache_key,
            cache_hit=True,
            cacheable=False,
        )
        return result

    def _persist_and_return(
        self,
        question: str,
        *,
        mode: str,
        session_id: str | None,
        result: dict[str, Any],
        cache_key: str | None,
        cache_source: dict[str, Any] | None,
        cacheable: bool,
    ) -> dict[str, Any]:
        """Attach cache metadata, persist operational records, and return result."""

        if self.storage is None:
            return result

        enriched = dict(result)
        enriched["cache_hit"] = False
        enriched["cache_key"] = cache_key
        self._write_storage_records(
            question,
            mode=mode,
            session_id=session_id,
            result=enriched,
            cache_key=cache_key,
            cache_hit=False,
            cacheable=cacheable,
            cache_source=cache_source,
        )
        return enriched

    def _write_storage_records(
        self,
        question: str,
        *,
        mode: str,
        session_id: str | None,
        result: dict[str, Any],
        cache_key: str | None,
        cache_hit: bool,
        cacheable: bool,
        cache_source: dict[str, Any] | None = None,
    ) -> None:
        """Persist logs/cache while keeping retrieval answers available on failure."""

        if self.storage is None:
            return

        try:
            if cacheable and cache_key and cache_source and result.get("status") not in {"error", "planned"}:
                self.storage.save_cached_result(cache_key, cache_source, result, ttl_seconds=self.cache_ttl_seconds)

            query_log_id = self.storage.write_query_log(
                {
                    "session_id": session_id,
                    "question_text": question,
                    "mode": mode,
                    "route": result.get("route") or "",
                    "cache_key": cache_key,
                    "cache_hit": cache_hit,
                    "result": result,
                }
            )
            self.storage.write_tool_traces(query_log_id, result.get("tool_trace") or [])
            if hasattr(self.storage, "write_data_gap_items"):
                gap_items = build_data_gap_items(
                    question=question,
                    mode=mode,
                    result=result,
                    query_log_id=query_log_id,
                    session_id=session_id,
                )
                self.storage.write_data_gap_items(gap_items)
        except Exception as exc:
            # Logging/cache must not be allowed to force the answer layer to
            # fabricate or drop an otherwise valid retrieval result.  Surface the
            # operational failure as a warning so the caller can inspect it.
            warnings = list(result.get("warnings") or [])
            warnings.append(f"agent_storage_error: {type(exc).__name__}: {exc}")
            result["warnings"] = warnings


def _default_deepseek_agent_factory(
    *,
    api_key: str | None = None,
    base_url: str = DEFAULT_DEEPSEEK_BASE_URL,
    model: str = DEFAULT_DEEPSEEK_MODEL,
    max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> DeepSeekRetrievalAgent:
    """Build the default DeepSeek agent lazily so rules-only runs need no key."""

    client = build_deepseek_client(api_key=api_key, base_url=base_url)
    return DeepSeekRetrievalAgent(
        client=client,
        model=model,
        max_tool_rounds=max_tool_rounds,
        temperature=temperature,
    )


def build_hybrid_entrypoint(
    *,
    api_key: str | None = None,
    base_url: str = DEFAULT_DEEPSEEK_BASE_URL,
    model: str = DEFAULT_DEEPSEEK_MODEL,
    max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS,
    temperature: float = DEFAULT_TEMPERATURE,
    enable_storage: bool = False,
    cache_ttl_seconds: int | None = None,
) -> HybridRetrievalEntryPoint:
    """Create the production hybrid entrypoint with CLI-provided LLM settings."""

    def factory() -> DeepSeekRetrievalAgent:
        return _default_deepseek_agent_factory(
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_tool_rounds=max_tool_rounds,
            temperature=temperature,
        )

    storage = MysqlAgentQueryStorage() if enable_storage else None
    return HybridRetrievalEntryPoint(
        deepseek_agent_factory=factory,
        storage=storage,
        cache_ttl_seconds=cache_ttl_seconds,
    )


def _should_keep_rule_result(rule_result: dict[str, Any]) -> bool:
    """Return True when the deterministic router is confident enough to answer."""

    intent = rule_result.get("intent")
    status = rule_result.get("status")
    if intent in LLM_FALLBACK_INTENTS:
        return False
    if status in RULE_TERMINAL_STATUSES:
        return True
    return bool(rule_result.get("tool_plan"))


def _wrap_rule_result(question: str, rule_result: dict[str, Any]) -> dict[str, Any]:
    """Add route metadata while preserving the rule entrypoint's envelope."""

    wrapped = dict(rule_result)
    wrapped.setdefault("question", question)
    wrapped["route"] = "rules"
    wrapped["rule_preflight"] = None
    return wrapped


def _error_envelope(
    question: str,
    *,
    route: str,
    warning: str,
    rule_preflight: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "status": "error",
        "route": route,
        "question": question,
        "intent": None,
        "slots": {},
        "needs_clarification": [],
        "tool_plan": [],
        "tool_trace": [],
        "rule_preflight": rule_preflight,
        "data_gaps": [],
        "scope_notes": [],
        "warnings": [warning],
        "answer_markdown": "当前统一入口执行失败，不能给出可靠结论。",
    }


def _collect_from_trace(tool_trace: list[dict[str, Any]], key: str) -> list[str]:
    """Collect unique `warnings`, `scope_notes`, or `data_gaps` from tool traces."""

    seen: set[str] = set()
    collected: list[str] = []
    for trace in tool_trace:
        result = trace.get("result", {}) if isinstance(trace, dict) else {}
        for item in result.get(key, []) or []:
            text = str(item)
            if text not in seen:
                seen.add(text)
                collected.append(text)
    return collected


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Run the unified Major Intel retrieval entrypoint.")
    parser.add_argument("prompt", help="用户自然语言问题。")
    parser.add_argument("--mode", choices=["auto", "rules", "deepseek"], default="auto")
    parser.add_argument("--context-json", help="可选，会话槽位 JSON，例如 {\"province\":\"广东\"}。")
    parser.add_argument("--no-execute", action="store_true", help="规则入口只生成工具计划，不执行本地检索。")
    parser.add_argument("--json", action="store_true", help="输出完整结构化结果，而不是只输出回答文本。")
    parser.add_argument("--session-id", help="可选，会话 ID；启用存储时会写入 query_logs。")
    parser.add_argument("--enable-storage", action="store_true", help="启用 MySQL 查询日志、缓存和工具轨迹记录。")
    parser.add_argument("--cache-ttl-seconds", type=int, help="可选，缓存过期秒数；不传表示不过期。")
    parser.add_argument("--api-key", help="DeepSeek API key。优先使用环境变量或 .env。")
    parser.add_argument("--base-url", default=DEFAULT_DEEPSEEK_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_DEEPSEEK_MODEL)
    parser.add_argument("--max-tool-rounds", type=int, default=DEFAULT_MAX_TOOL_ROUNDS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
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

    entrypoint = build_hybrid_entrypoint(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
        max_tool_rounds=args.max_tool_rounds,
        temperature=args.temperature,
        enable_storage=args.enable_storage,
        cache_ttl_seconds=args.cache_ttl_seconds,
    )
    result = entrypoint.run(
        args.prompt,
        mode=args.mode,
        session_id=args.session_id,
        session_context=context,
        execute=not args.no_execute,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result.get("answer_markdown", ""))
    return 0 if result.get("status") != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
