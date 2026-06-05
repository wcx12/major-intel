"""Evaluate DeepSeek retrieval-agent tool selection traces.

The real DeepSeek call is intentionally outside unit tests.  This module keeps
the evaluation contract data-driven: run the agent, save its tool_trace, then
validate that trace against stable expectations for high-frequency questions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CASES_PATH = PROJECT_ROOT / "data" / "deepseek_tool_selection_eval_cases.json"


def load_cases(path: str | Path = DEFAULT_CASES_PATH) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    cases = payload.get("cases", payload) if isinstance(payload, dict) else payload
    if not isinstance(cases, list):
        raise ValueError("tool selection eval cases must be a list or an object with a cases list")
    return cases


def trace_tool_names(trace: list[dict[str, Any]]) -> list[str]:
    names = []
    for item in trace or []:
        tool_name = item.get("tool_name") or (item.get("result") or {}).get("tool_name")
        if tool_name:
            names.append(str(tool_name))
    return names


def validate_trace(case: dict[str, Any], trace: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    names = trace_tool_names(trace)
    expected = set(case.get("expected_answer_tools") or [])
    allowed = set(case.get("allowed_support_tools") or [])
    forbidden = set(case.get("forbidden_tools") or [])
    max_calls = int(case.get("max_executed_tool_calls") or 0)
    statuses = {str((item.get("result") or {}).get("status") or item.get("status") or "") for item in trace or []}
    blocking_stop_allowed = bool(case.get("allow_blocking_stop_before_expected")) and bool(
        statuses & {"needs_clarification", "not_found", "error", "skipped"}
    )

    if not blocking_stop_allowed:
        for tool_name in sorted(expected):
            if tool_name not in names:
                errors.append(f"missing expected answer tool: {tool_name}")

    for tool_name in names:
        if tool_name in forbidden:
            errors.append(f"forbidden tool called: {tool_name}")
        elif tool_name not in expected and tool_name not in allowed:
            errors.append(f"unexpected tool called: {tool_name}")

    if max_calls and len(names) > max_calls:
        errors.append(f"tool call count {len(names)} exceeds max_executed_tool_calls {max_calls}")

    return errors


def validate_report(cases: list[dict[str, Any]], report: Any) -> list[dict[str, Any]]:
    rows = report.get("results", report) if isinstance(report, dict) else report
    if not isinstance(rows, list):
        raise ValueError("trace report must be a list or an object with a results list")
    traces_by_id = {str(row.get("id") or row.get("label")): row.get("tool_trace") or row.get("trace") or [] for row in rows}
    results = []
    for case in cases:
        case_id = str(case["id"])
        trace = traces_by_id.get(case_id, [])
        results.append({"id": case_id, "errors": validate_trace(case, trace), "tool_names": trace_tool_names(trace)})
    return results


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Validate DeepSeek agent tool-selection traces.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--trace-report", type=Path)
    args = parser.parse_args(argv)

    cases = load_cases(args.cases)
    if not args.trace_report:
        print(json.dumps({"case_count": len(cases), "cases": cases}, ensure_ascii=False, indent=2))
        return 0

    report = json.loads(args.trace_report.read_text(encoding="utf-8"))
    results = validate_report(cases, report)
    failed = [result for result in results if result["errors"]]
    print(json.dumps({"total": len(results), "failed": len(failed), "results": results}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
