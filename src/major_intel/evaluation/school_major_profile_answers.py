"""Evaluate school_major_profile tool evidence and final answer safety.

This runner is intentionally stricter than the broad retrieval smoke suite.  A
school-major answer can have valid JSON and still be unsafe if it turns partial
evidence into a confident recommendation, treats school-level employment as a
major-level fact, or ignores province/subject/year mismatches.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CASES_PATH = PROJECT_ROOT / "data" / "school_major_profile_answer_eval_cases.json"
DEFAULT_STRONG_ORACLE_PATH = PROJECT_ROOT / "data" / "school_major_profile_strong_oracle_cases.json"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "school_major_profile_answer_eval.md"

from major_intel.agents.deepseek_retrieval_agent import DeepSeekRetrievalAgent, build_deepseek_client, load_env_files
from major_intel.function_calls.retrieval_tools import RetrievalTools
from major_intel.storage.local_retrieval_mvp import DbConfig, MysqlCliClient


PROVINCE_ID_BY_NAME = {
    "北京": "11",
    "天津": "12",
    "河北": "13",
    "山西": "14",
    "内蒙古": "15",
    "辽宁": "21",
    "吉林": "22",
    "黑龙江": "23",
    "上海": "31",
    "江苏": "32",
    "浙江": "33",
    "安徽": "34",
    "福建": "35",
    "江西": "36",
    "山东": "37",
    "河南": "41",
    "湖北": "42",
    "湖南": "43",
    "广东": "44",
    "广西": "45",
    "海南": "46",
    "重庆": "50",
    "四川": "51",
    "贵州": "52",
    "云南": "53",
    "西藏": "54",
    "陕西": "61",
    "甘肃": "62",
    "青海": "63",
    "宁夏": "64",
    "新疆": "65",
}

CONTEXT_EVIDENCE_TYPES = {"admission_history", "plan", "specialty_group"}
SUBJECT_FAMILY_BY_ALIAS = {
    "物理": "physics",
    "physical": "physics",
    "physics": "physics",
    "理科": "physics",
    "science": "physics",
    "1": "physics",
    "2073": "physics",
    "历史": "history",
    "history": "history",
    "文科": "history",
    "arts": "history",
    "liberal": "history",
    "2": "history",
    "2074": "history",
    "综合": "comprehensive",
    "comprehensive": "comprehensive",
    "3": "comprehensive",
    "艺术": "art",
    "艺术类": "art",
    "art": "art",
    "4": "art",
    "体育": "sports",
    "体育类": "sports",
    "sports": "sports",
    "5": "sports",
}
PARTIAL_CAVEAT_TERMS = ["部分", "口径", "缺", "不能", "未命中", "不足", "核实", "不完整"]
CONTEXT_MISMATCH_TERMS = ["科类", "上下文", "不一致", "未确认", "代码", "不能确认", "不完全匹配", "需核实"]
SCHOOL_MAJOR_EMPLOYMENT_GAPS = {
    "校专业级工作地域分布",
    "校专业级薪资分布",
    "校专业级Top对口公司",
}


def load_cases(path: str | Path = DEFAULT_CASES_PATH) -> list[dict[str, Any]]:
    """Load metadata-wrapped or raw-list evaluation cases."""

    case_path = Path(path)
    payload = json.loads(case_path.read_text(encoding="utf-8"))
    raw_cases = payload if isinstance(payload, list) else payload.get("cases", [])
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw_case in enumerate(raw_cases, start=1):
        case = dict(raw_case)
        if "id" not in case:
            raise ValueError(f"Case #{index} in {case_path} is missing 'id'")
        if "question" not in case:
            raise ValueError(f"Case {case['id']} is missing 'question'")
        if "tool_args" not in case or not isinstance(case["tool_args"], dict):
            raise ValueError(f"Case {case['id']} is missing object 'tool_args'")
        if case["id"] in seen:
            raise ValueError(f"Duplicate case id in {case_path}: {case['id']}")
        seen.add(case["id"])
        case.setdefault("risk_checks", ["partial_caveat", "employment_scope", "admission_scope", "context_mismatch"])
        case.setdefault("expected_tool", {})
        case.setdefault("expected_answer", {})
        cases.append(case)
    return cases


def evaluate_tool_expectations(case: dict[str, Any], profile_result: dict[str, Any]) -> list[dict[str, str]]:
    """Check expected tool status and evidence fields for one case."""

    expected = case.get("expected_tool") or {}
    findings: list[dict[str, str]] = []
    if not expected:
        return findings

    status = expected.get("status")
    if status and profile_result.get("status") != status:
        findings.append(
            _finding(
                "tool_status_mismatch",
                f"expected tool status {status!r}, got {profile_result.get('status')!r}",
            )
        )

    summary = profile_result.get("data", {}).get("evidence_summary", {}) or {}
    for key, expected_value in (expected.get("evidence_summary") or {}).items():
        if summary.get(key) != expected_value:
            findings.append(
                _finding(
                    "tool_evidence_summary_mismatch",
                    f"expected evidence_summary.{key}={expected_value!r}, got {summary.get(key)!r}",
                )
            )

    evidence_gaps = set(profile_result.get("data", {}).get("evidence_gaps") or [])
    for gap in expected.get("must_have_evidence_gaps") or []:
        if gap not in evidence_gaps:
            findings.append(_finding("missing_tool_evidence_gap", f"missing evidence gap: {gap}"))

    warnings_text = "\n".join(str(warning) for warning in profile_result.get("warnings") or [])
    for needle in expected.get("must_have_warning_contains") or []:
        if needle not in warnings_text:
            findings.append(_finding("missing_tool_warning", f"tool warnings do not contain: {needle}"))

    return findings


def evaluate_strong_oracle(case: dict[str, Any], profile_result: dict[str, Any]) -> list[dict[str, str]]:
    """Evaluate a tool result against independent, human-curated oracle truth."""

    oracle = case.get("strong_oracle") or {}
    findings: list[dict[str, str]] = []
    if not oracle:
        return findings

    expected_status = oracle.get("expected_status")
    if expected_status and profile_result.get("status") != expected_status:
        findings.append(
            _finding(
                "oracle_status_mismatch",
                f"oracle expected status {expected_status!r}, got {profile_result.get('status')!r}",
            )
        )

    canonical = oracle.get("canonical") or {}
    normalized = profile_result.get("normalized_slots") or {}
    school_name = normalized.get("school_name") or profile_result.get("data", {}).get("school", {}).get("name")
    major_name = normalized.get("major_name") or profile_result.get("data", {}).get("major", {}).get("special_name")
    if canonical.get("school_name") and school_name != canonical["school_name"]:
        findings.append(
            _finding(
                "oracle_canonical_school_mismatch",
                f"oracle expected school {canonical['school_name']!r}, got {school_name!r}",
            )
        )
    if canonical.get("major_name") and major_name != canonical["major_name"]:
        findings.append(
            _finding(
                "oracle_canonical_major_mismatch",
                f"oracle expected major {canonical['major_name']!r}, got {major_name!r}",
            )
        )

    evidence = profile_result.get("data", {}).get("school_major_evidence") or []
    source_types = {str(row.get("source_type") or "") for row in evidence if isinstance(row, dict)}
    evidence_oracle = oracle.get("evidence") or {}
    for source_type in evidence_oracle.get("required_source_types") or []:
        if source_type not in source_types:
            findings.append(_finding("oracle_missing_source_type", f"oracle expected source_type {source_type!r}"))
    for source_type in evidence_oracle.get("forbidden_source_types") or []:
        if source_type in source_types:
            findings.append(_finding("oracle_forbidden_source_type", f"oracle forbids source_type {source_type!r}"))

    context_source_types = {
        str(row.get("source_type") or "")
        for row in _context_rows(profile_result)
        if isinstance(row, dict)
    }
    for source_type in evidence_oracle.get("forbidden_context_source_types") or []:
        if source_type in context_source_types:
            findings.append(
                _finding("oracle_forbidden_context_source_type", f"oracle forbids contextual source_type {source_type!r}")
            )

    context_oracle = oracle.get("context") or {}
    expected_match = context_oracle.get("expected_match")
    exact_context_matches = _strict_context_matches(context_oracle, profile_result)
    if expected_match == "strict_match" and not exact_context_matches:
        findings.append(_finding("oracle_missing_strict_context_match", "oracle expected at least one exact context evidence row."))
    if expected_match == "no_strict_context_match" and exact_context_matches:
        findings.append(_finding("oracle_unexpected_strict_context_match", "oracle expected no exact context evidence row."))

    warnings_text = "\n".join(str(warning) for warning in profile_result.get("warnings") or [])
    for needle in context_oracle.get("required_warning_contains") or []:
        if needle not in warnings_text:
            findings.append(_finding("oracle_missing_warning", f"oracle expected warning containing: {needle}"))

    return findings


def evaluate_answer(case: dict[str, Any], answer: str, profile_result: dict[str, Any]) -> list[dict[str, str]]:
    """Evaluate final answer text against case-specific and generic safety rules."""

    answer_text = str(answer or "")
    findings: list[dict[str, str]] = []
    expected = case.get("expected_answer") or {}

    for needle in expected.get("must_include") or []:
        if needle not in answer_text:
            findings.append(_finding("missing_required_answer_text", f"answer must include: {needle}"))

    for group in expected.get("must_include_any") or []:
        if not any(term in answer_text for term in group):
            findings.append(_finding("missing_required_answer_text", f"answer must include one of: {', '.join(group)}"))

    for needle in expected.get("must_not_include") or []:
        if needle in answer_text:
            findings.append(_finding("forbidden_answer_text", f"answer must not include: {needle}"))

    risk_checks = set(case.get("risk_checks") or [])
    if "partial_caveat" in risk_checks:
        findings.extend(_check_partial_caveat(answer_text, profile_result))
    if "employment_scope" in risk_checks:
        findings.extend(_check_employment_scope(answer_text, profile_result))
    if "admission_scope" in risk_checks:
        findings.extend(_check_admission_scope(answer_text, profile_result))
    if "context_mismatch" in risk_checks:
        findings.extend(_check_context_mismatch(case, answer_text, profile_result))

    return findings


def run_tool_case(case: dict[str, Any], tools: RetrievalTools) -> dict[str, Any]:
    """Run school_major_profile directly against local retrieval tools."""

    args = dict(case["tool_args"])
    return tools.school_major_profile(
        args.get("school_text") or args.get("school") or "",
        args.get("major_text") or args.get("major") or "",
        args.get("province"),
        args.get("subject_type"),
        args.get("year"),
    )


def run_agent_case(case: dict[str, Any], agent: DeepSeekRetrievalAgent) -> tuple[str, dict[str, Any] | None, list[dict[str, Any]]]:
    """Run the real agent and return answer plus the profile tool result it used."""

    agent.tool_trace = []
    answer = agent.run(case["question"])
    profile_result = _first_profile_result(agent.tool_trace)
    return answer, profile_result, list(agent.tool_trace)


def evaluate_case(
    case: dict[str, Any],
    *,
    tools: RetrievalTools,
    agent: DeepSeekRetrievalAgent | None = None,
) -> dict[str, Any]:
    """Evaluate one case in tool-only or real-agent mode."""

    started = time.perf_counter()
    tool_trace: list[dict[str, Any]] = []
    answer = case.get("answer_fixture", "")
    if agent is not None:
        answer, profile_result, tool_trace = run_agent_case(case, agent)
        if profile_result is None:
            profile_result = run_tool_case(case, tools)
            tool_trace.append({"tool_name": "school_major_profile", "arguments": case["tool_args"], "result": profile_result})
            missing_profile_finding = _finding(
                "agent_missing_school_major_profile",
                "agent did not call school_major_profile; evaluated fallback direct tool result.",
            )
        else:
            missing_profile_finding = None
    else:
        profile_result = run_tool_case(case, tools)
        tool_trace.append({"tool_name": "school_major_profile", "arguments": case["tool_args"], "result": profile_result})
        missing_profile_finding = None

    findings = []
    if missing_profile_finding:
        findings.append(missing_profile_finding)
    findings.extend(evaluate_tool_expectations(case, profile_result))
    findings.extend(evaluate_strong_oracle(case, profile_result))
    if answer:
        findings.extend(evaluate_answer(case, answer, profile_result))
    elif agent is not None:
        findings.append(_finding("empty_answer", "agent returned an empty answer."))

    return {
        "id": case["id"],
        "question": case["question"],
        "ok": not findings,
        "duration_ms": round((time.perf_counter() - started) * 1000, 1),
        "findings": findings,
        "answer": answer,
        "profile_result": profile_result,
        "tool_trace": tool_trace,
    }


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result["ok"]),
        "failed": sum(1 for result in results if not result["ok"]),
    }


def write_markdown_report(path: str | Path, results: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    """Write a human-readable audit report with evidence and answer excerpts."""

    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# school_major_profile Answer Evaluation",
        "",
        f"- Total: {summary['total']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        "",
    ]
    for result in results:
        profile = result["profile_result"]
        summary_data = profile.get("data", {}).get("evidence_summary", {}) or {}
        lines.extend(
            [
                f"## {result['id']}",
                "",
                f"- Status: {'PASS' if result['ok'] else 'FAIL'}",
                f"- Question: {result['question']}",
                f"- Tool status: {profile.get('status')}",
                f"- Evidence summary: `{json.dumps(summary_data, ensure_ascii=False)}`",
                f"- Warnings: {'；'.join(profile.get('warnings') or []) or '无'}",
                f"- Data gaps: {'；'.join(profile.get('data_gaps') or []) or '无'}",
                "",
            ]
        )
        if result["findings"]:
            lines.append("Findings:")
            for finding in result["findings"]:
                lines.append(f"- [{finding['kind']}] {finding['message']}")
            lines.append("")
        if result.get("tool_trace"):
            lines.append("Tool trace:")
            for trace in result["tool_trace"]:
                arguments = json.dumps(trace.get("arguments") or {}, ensure_ascii=False)
                trace_result = trace.get("result") if isinstance(trace.get("result"), dict) else {}
                lines.append(f"- `{trace.get('tool_name')}` status=`{trace_result.get('status')}` args=`{arguments}`")
            lines.append("")
        if result.get("answer"):
            lines.extend(["Answer excerpt:", "", "```text", _excerpt(result["answer"]), "```", ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _first_profile_result(tool_trace: list[dict[str, Any]]) -> dict[str, Any] | None:
    for trace in tool_trace:
        if trace.get("tool_name") == "school_major_profile":
            result = trace.get("result")
            return result if isinstance(result, dict) else None
    return None


def _check_partial_caveat(answer: str, profile_result: dict[str, Any]) -> list[dict[str, str]]:
    if profile_result.get("status") != "partial":
        return []
    if any(term in answer for term in PARTIAL_CAVEAT_TERMS):
        return []
    return [_finding("missing_partial_caveat", "partial tool result was answered without a visible caveat.")]


def _check_employment_scope(answer: str, profile_result: dict[str, Any]) -> list[dict[str, str]]:
    gaps = set(profile_result.get("data_gaps") or [])
    if not gaps.intersection(SCHOOL_MAJOR_EMPLOYMENT_GAPS):
        return []
    unsafe_patterns = [
        r"专业就业率(?:很高|较高|不错|好|为|达到)",
        r"专业薪资(?:很高|较高|不错|好|为|在)",
        r"该专业(?:就业率|薪资|工资|Top雇主)",
        r"本专业(?:就业率|薪资|工资|Top雇主)",
    ]
    for pattern in unsafe_patterns:
        if re.search(pattern, answer):
            return [
                _finding(
                    "unsafe_school_major_employment_claim",
                    "answer asserts school-major employment/salary despite school-major employment gaps.",
                )
            ]
    return []


def _check_admission_scope(answer: str, profile_result: dict[str, Any]) -> list[dict[str, str]]:
    evidence = profile_result.get("data", {}).get("school_major_evidence") or []
    source_types = {str(row.get("source_type") or "") for row in evidence if isinstance(row, dict)}
    findings: list[dict[str, str]] = []
    if "specialty_group" in source_types and re.search(r"(专业|该专业).{0,8}(录取线|最低分|最低位次)", answer):
        findings.append(
            _finding(
                "specialty_group_as_major_line",
                "answer treats specialty-group evidence as a standalone major admission line.",
            )
        )
    has_admission_or_plan = bool(profile_result.get("data", {}).get("evidence_summary", {}).get("has_admission_or_plan"))
    if not has_admission_or_plan and re.search(r"(最低分|最低位次|录取线|能上)", answer) and not _has_negative_context(answer):
        findings.append(
            _finding(
                "unsupported_admission_claim",
                "answer mentions admission scores/ranks without admission or plan evidence.",
            )
        )
    return findings


def _check_context_mismatch(case: dict[str, Any], answer: str, profile_result: dict[str, Any]) -> list[dict[str, str]]:
    mismatch = _context_mismatch(case.get("tool_args") or {}, profile_result)
    if not mismatch:
        return []
    if all(term not in answer for term in CONTEXT_MISMATCH_TERMS):
        return [
            _finding(
                "undisclosed_context_mismatch",
                "tool evidence does not fully match requested province/subject/year, but answer did not disclose it.",
            )
        ]
    return []


def _context_mismatch(tool_args: dict[str, Any], profile_result: dict[str, Any]) -> bool:
    requested_subject = _text(tool_args.get("subject_type"))
    requested_province = _text(tool_args.get("province"))
    requested_year = _text(tool_args.get("year"))
    if not any([requested_subject, requested_province, requested_year]):
        return False

    evidence = [
        row
        for row in profile_result.get("data", {}).get("school_major_evidence") or []
        if isinstance(row, dict) and row.get("source_type") in CONTEXT_EVIDENCE_TYPES
    ]
    if not evidence:
        return False

    comparable_rows = 0
    matched_rows = 0
    for row in evidence:
        comparable = False
        matched = True
        if requested_province:
            comparable = True
            matched = matched and _province_matches(requested_province, row.get("province"))
        if requested_year:
            comparable = True
            matched = matched and _text(row.get("year")) == requested_year
        if requested_subject:
            comparable = True
            matched = matched and _subject_matches(requested_subject, row.get("subject_type"))
        if comparable:
            comparable_rows += 1
            matched_rows += 1 if matched else 0
    return comparable_rows > 0 and matched_rows == 0


def _context_rows(profile_result: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in profile_result.get("data", {}).get("school_major_evidence") or []
        if isinstance(row, dict) and row.get("source_type") in CONTEXT_EVIDENCE_TYPES
    ]


def _strict_context_matches(context_oracle: dict[str, Any], profile_result: dict[str, Any]) -> list[dict[str, Any]]:
    province = _text(context_oracle.get("province"))
    year = _text(context_oracle.get("year"))
    subject_type = _text(context_oracle.get("subject_type"))
    matches = []
    for row in _context_rows(profile_result):
        if province and not _province_matches(province, row.get("province")):
            continue
        if year and _text(row.get("year")) != year:
            continue
        if subject_type and not _subject_matches(subject_type, row.get("subject_type")):
            continue
        matches.append(row)
    return matches


def _province_matches(requested: str, actual: Any) -> bool:
    actual_text = _text(actual)
    if not actual_text:
        return False
    requested_id = PROVINCE_ID_BY_NAME.get(requested, requested)
    return actual_text in {requested, requested_id}


def _subject_matches(requested: str, actual: Any) -> bool:
    actual_text = _text(actual)
    if not actual_text:
        return False
    requested_family = SUBJECT_FAMILY_BY_ALIAS.get(requested) or SUBJECT_FAMILY_BY_ALIAS.get(requested.lower())
    actual_family = SUBJECT_FAMILY_BY_ALIAS.get(actual_text) or SUBJECT_FAMILY_BY_ALIAS.get(actual_text.lower())
    if requested_family and actual_family:
        return requested_family == actual_family
    return actual_text == requested


def _has_negative_context(answer: str) -> bool:
    return any(term in answer for term in ["没有", "未命中", "缺少", "不能", "无法", "不代表"])


def _finding(kind: str, message: str, level: str = "error") -> dict[str, str]:
    return {"level": level, "kind": kind, "message": message}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _excerpt(text: str, limit: int = 1200) -> str:
    cleaned = str(text or "").strip()
    return cleaned if len(cleaned) <= limit else cleaned[:limit].rstrip() + "\n..."


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Evaluate school_major_profile evidence and answer safety.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--case-id", action="append", dest="case_ids")
    parser.add_argument("--mode", choices=["tool", "agent"], default="tool")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any case fails.")
    parser.add_argument("--model", default=None, help="Override DeepSeek model in agent mode.")
    args = parser.parse_args(argv)

    load_env_files([PROJECT_ROOT / ".env", PROJECT_ROOT / ".env.deepseek"])
    cases = load_cases(args.cases)
    if args.case_ids:
        wanted = set(args.case_ids)
        cases = [case for case in cases if case["id"] in wanted]

    tools = RetrievalTools(MysqlCliClient(DbConfig.from_env()))
    agent = None
    if args.mode == "agent":
        client = build_deepseek_client()
        agent_kwargs = {"client": client}
        if args.model:
            agent_kwargs["model"] = args.model
        agent = DeepSeekRetrievalAgent(**agent_kwargs)

    results = [evaluate_case(case, tools=tools, agent=agent) for case in cases]
    summary = summarize_results(results)
    write_markdown_report(args.report, results, summary)
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if args.strict and summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
