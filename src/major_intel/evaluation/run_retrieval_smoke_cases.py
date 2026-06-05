"""Run broad CLI smoke cases for retrieval_tools.py.

The case file is intentionally data-first.  It can list explicit cases and
compact matrices that expand into many concrete CLI calls.  The runner checks
the function-call envelope for every result, then reports both hard failures
and softer quality misses such as an expected `ok` case returning `not_found`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CASES_PATH = PROJECT_ROOT / "data" / "retrieval_smoke_cases.json"
DEFAULT_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "retrieval_tools.py"
ENVELOPE_KEYS = [
    "tool_name",
    "status",
    "input",
    "normalized_slots",
    "data",
    "scope_notes",
    "data_gaps",
    "needs_clarification",
    "source_tables",
    "warnings",
]
DEFAULT_ALLOWED_STATUSES = ["ok", "partial", "not_found", "needs_clarification"]
REPEATABLE_LIST_FLAGS_BY_TOOL = {
    # The JSON smoke matrix represents multi-value arguments as Python lists,
    # but argparse has two incompatible list styles. `action="append"` options
    # must repeat the flag (`--target A --target B`), while `nargs="*"` options
    # intentionally keep one flag followed by many values (`--years 2025 2024`).
    # Keeping this map explicit makes future CLI shape changes visible in tests
    # instead of silently generating commands that argparse rejects.
    "comparison_query": {"target", "dimension"},
}


def load_cases(path: str | Path = DEFAULT_CASES_PATH) -> list[dict[str, Any]]:
    """Load explicit cases and expand matrix definitions."""

    case_path = Path(path)
    payload = json.loads(case_path.read_text(encoding="utf-8"))
    raw_cases = payload if isinstance(payload, list) else payload.get("cases", [])
    matrices = [] if isinstance(payload, list) else payload.get("matrices", [])

    cases = [_normalize_case(case, case_path, index) for index, case in enumerate(raw_cases, start=1)]
    for matrix in matrices:
        cases.extend(_expand_matrix(matrix, case_path))

    seen: set[str] = set()
    duplicates: list[str] = []
    for case in cases:
        if case["id"] in seen:
            duplicates.append(case["id"])
        seen.add(case["id"])
    if duplicates:
        raise ValueError(f"Duplicate case ids in {case_path}: {', '.join(sorted(duplicates))}")
    return cases


def build_command(python_executable: str, script_path: str | Path, case: dict[str, Any]) -> list[str]:
    """Convert one case into a retrieval_tools.py CLI command."""

    command = [python_executable, Path(script_path).as_posix(), case["tool"]]
    repeatable_flags = REPEATABLE_LIST_FLAGS_BY_TOOL.get(case["tool"], set())
    for key, value in case.get("args", {}).items():
        if value is None or value is False:
            continue
        flag = "--" + key.replace("_", "-")
        if isinstance(value, list):
            if not value:
                continue
            if key in repeatable_flags:
                for item in value:
                    command.extend([flag, str(item)])
            else:
                command.append(flag)
                command.extend(str(item) for item in value)
        elif value is True:
            command.append(flag)
        else:
            command.extend([flag, str(value)])
    return command


def validate_payload(case: dict[str, Any], payload: Any) -> tuple[list[str], list[str]]:
    """Validate the stable function-call envelope and target-status quality."""

    errors: list[str] = []
    quality_misses: list[str] = []
    if not isinstance(payload, dict):
        return ["payload is not a JSON object"], quality_misses

    for key in ENVELOPE_KEYS:
        if key not in payload:
            errors.append(f"missing envelope key: {key}")

    if payload.get("tool_name") != case.get("tool"):
        errors.append(f"tool_name mismatch: expected {case.get('tool')}, got {payload.get('tool_name')}")

    allowed_statuses = case.get("allowed_statuses") or DEFAULT_ALLOWED_STATUSES
    status = payload.get("status")
    if status not in allowed_statuses:
        errors.append(f"status {status!r} not in allowed_statuses {allowed_statuses!r}")

    data = payload.get("data")
    if not isinstance(data, dict):
        errors.append("data is not a JSON object")
        data = {}

    key_statuses = case.get("expected_data_key_statuses", ["ok", "partial"])
    if status in key_statuses:
        for key in case.get("expected_data_keys", []):
            if key not in data:
                errors.append(f"missing data key: {key}")

    required_source_tables = case.get("required_source_tables", [])
    if status in case.get("required_source_table_statuses", ["ok", "partial"]):
        source_tables = set(payload.get("source_tables") or [])
        for table in required_source_tables:
            if table not in source_tables:
                errors.append(f"missing source table: {table}")

    target_status = case.get("target_status")
    if target_status and status != target_status:
        quality_misses.append(f"expected target status {target_status}, got {status}")

    return errors, quality_misses


def run_case(
    case: dict[str, Any],
    *,
    python_executable: str,
    script_path: str | Path,
    timeout: int,
    cwd: str | Path,
) -> dict[str, Any]:
    """Execute one CLI case and return a structured runner result."""

    started = time.perf_counter()
    command = build_command(python_executable, script_path, case)
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "id": case["id"],
            "tool": case["tool"],
            "status": "timeout",
            "ok": False,
            "duration_ms": round((time.perf_counter() - started) * 1000, 1),
            "command": command,
            "errors": [f"timed out after {timeout}s"],
            "quality_misses": [],
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }

    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    if completed.returncode != 0:
        return {
            "id": case["id"],
            "tool": case["tool"],
            "status": "process_error",
            "ok": False,
            "duration_ms": duration_ms,
            "command": command,
            "errors": [f"exit code {completed.returncode}"],
            "quality_misses": [],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {
            "id": case["id"],
            "tool": case["tool"],
            "status": "json_error",
            "ok": False,
            "duration_ms": duration_ms,
            "command": command,
            "errors": [f"invalid JSON output: {exc}"],
            "quality_misses": [],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    errors, quality_misses = validate_payload(case, payload)
    return {
        "id": case["id"],
        "tool": case["tool"],
        "status": payload.get("status", "missing_status"),
        "ok": not errors,
        "duration_ms": duration_ms,
        "command": command,
        "errors": errors,
        "quality_misses": quality_misses,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "payload": payload,
    }


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate runner results by status and tool."""

    by_tool: dict[str, Counter[str]] = defaultdict(Counter)
    by_status: Counter[str] = Counter()
    for result in results:
        by_tool[result["tool"]][result["status"]] += 1
        by_status[result["status"]] += 1

    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.get("ok")),
        "failed": sum(1 for result in results if not result.get("ok")),
        "quality_misses": sum(len(result.get("quality_misses", [])) for result in results),
        "by_status": dict(sorted(by_status.items())),
        "by_tool": {tool: dict(counter) for tool, counter in sorted(by_tool.items())},
    }


def filter_cases(
    cases: list[dict[str, Any]],
    *,
    tools: set[str] | None = None,
    categories: set[str] | None = None,
    case_ids: set[str] | None = None,
    limit: int | None = None,
    sample_per_tool: int | None = None,
) -> list[dict[str, Any]]:
    """Apply CLI filters while preserving case-file order."""

    selected = []
    per_tool_counts: Counter[str] = Counter()
    for case in cases:
        if tools and case["tool"] not in tools:
            continue
        if categories and case.get("category") not in categories:
            continue
        if case_ids and case["id"] not in case_ids:
            continue
        if sample_per_tool is not None and per_tool_counts[case["tool"]] >= sample_per_tool:
            continue
        selected.append(case)
        per_tool_counts[case["tool"]] += 1
        if limit is not None and len(selected) >= limit:
            break
    return selected


def _normalize_case(case: dict[str, Any], case_path: Path, index: int) -> dict[str, Any]:
    required = ["id", "tool"]
    for key in required:
        if key not in case:
            raise ValueError(f"Case #{index} in {case_path} is missing {key!r}")
    normalized = dict(case)
    normalized.setdefault("category", "general")
    normalized.setdefault("args", {})
    normalized.setdefault("allowed_statuses", DEFAULT_ALLOWED_STATUSES)
    if not isinstance(normalized["args"], dict):
        raise ValueError(f"Case {normalized['id']} args must be an object")
    return normalized


def _expand_matrix(matrix: dict[str, Any], case_path: Path) -> list[dict[str, Any]]:
    id_prefix = matrix["id_prefix"]
    base = {
        key: value
        for key, value in matrix.items()
        if key not in {"id_prefix", "arg_name", "values", "fixed_args", "args_list"}
    }
    fixed_args = dict(matrix.get("fixed_args", {}))
    expanded = []

    if "args_list" in matrix:
        for index, item in enumerate(matrix["args_list"], start=1):
            entry = dict(item)
            args = dict(fixed_args)
            args.update(entry.pop("args", entry))
            id_suffix = entry.pop("id_suffix", f"{index:03d}")
            case = {**base, **entry, "id": f"{id_prefix}_{id_suffix}", "args": args}
            expanded.append(_normalize_case(case, case_path, index))
        return expanded

    arg_name = matrix["arg_name"]
    for index, raw_value in enumerate(matrix["values"], start=1):
        entry = raw_value if isinstance(raw_value, dict) else {"value": raw_value}
        args = dict(fixed_args)
        args[arg_name] = entry["value"]
        args.update(entry.get("args", {}))
        id_suffix = entry.get("id_suffix", f"{index:03d}")
        overrides = {key: value for key, value in entry.items() if key not in {"value", "args", "id_suffix"}}
        case = {**base, **overrides, "id": f"{id_prefix}_{id_suffix}", "args": args}
        expanded.append(_normalize_case(case, case_path, index))
    return expanded


def _write_report(path: Path, results: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    report = {
        "generated_at_epoch": int(time.time()),
        "summary": summary,
        "results": [
            {
                key: result[key]
                for key in ["id", "tool", "status", "ok", "duration_ms", "errors", "quality_misses", "command"]
                if key in result
            }
            for result in results
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run retrieval_tools.py smoke cases.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT_PATH)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--tool", action="append", dest="tools")
    parser.add_argument("--category", action="append", dest="categories")
    parser.add_argument("--case-id", action="append", dest="case_ids")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--sample-per-tool", type=int)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--strict-targets", action="store_true")
    parser.add_argument("--list-cases", action="store_true")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "reports" / "retrieval_smoke_results.json")
    args = parser.parse_args(argv)

    cases = filter_cases(
        load_cases(args.cases),
        tools=set(args.tools) if args.tools else None,
        categories=set(args.categories) if args.categories else None,
        case_ids=set(args.case_ids) if args.case_ids else None,
        limit=args.limit,
        sample_per_tool=args.sample_per_tool,
    )

    if args.list_cases:
        print(json.dumps(cases, ensure_ascii=False, indent=2))
        return 0

    results = [
        run_case(
            case,
            python_executable=args.python,
            script_path=args.script,
            timeout=args.timeout,
            cwd=PROJECT_ROOT,
        )
        for case in cases
    ]
    summary = summarize_results(results)
    _write_report(args.report, results, summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    failed = summary["failed"] > 0
    missed_targets = args.strict_targets and summary["quality_misses"] > 0
    return 1 if failed or missed_targets else 0


if __name__ == "__main__":
    raise SystemExit(main())
