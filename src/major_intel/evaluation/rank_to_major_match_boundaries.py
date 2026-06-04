"""Evaluate rank_to_major_match boundary behavior and answer quality.

This runner checks four layers for each case:

1. Function-call routing: intent, extracted slots, and generated arguments.
2. Database oracle: independent local SQL for expected school-major buckets.
3. Tool envelope: whether rank_to_major_match agrees with the oracle.
4. Answer text: whether the final answer exposes schools, majors, rank, years,
   warnings, and historical-scope limits without overpromising admission.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]

from major_intel.agents.natural_language_entrypoint import NaturalLanguageEntryPoint
from major_intel.evaluation.rank_to_major_match_oracles import (
    BUCKETS,
    as_int,
    major_row_label,
    oracle_rows,
    resolve_major_candidate,
    resolve_rank_and_subject,
    selected_oracle_rows,
)
from major_intel.evaluation.rank_to_school_match_oracles import normalize_digits
from major_intel.function_calls.registry import call_retrieval_function
from major_intel.function_calls.retrieval_tools import RetrievalTools
from major_intel.storage.local_retrieval_mvp import DbConfig, MysqlCliClient, sql_quote


DEFAULT_CASES_PATH = PROJECT_ROOT / "tests" / "function_calls" / "rank_to_major_match" / "boundary_cases.json"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports"
BUCKET_LABELS = {"rush": "冲", "stable": "稳", "safe": "保"}
OVERPROMISE_RE = re.compile(r"(保证|肯定|一定|稳上|包录|必录)")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_manual_cases(path: Path = DEFAULT_CASES_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_cases = payload if isinstance(payload, list) else payload.get("cases", [])
    cases: list[dict[str, Any]] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        case = dict(raw_case)
        case.setdefault("id", f"manual_{index}")
        case.setdefault("category", "manual")
        case.setdefault("limit", 30)
        case.setdefault("expected_intent", "rank_to_major_match")
        case.setdefault("question", build_question(case))
        cases.append(case)
    return cases


def build_question(case: dict[str, Any]) -> str:
    year_prefix = f"{case['year']}年" if case.get("year") else ""
    score_or_rank = f"{case['score']}分" if case.get("score") not in (None, "") else f"{case.get('rank')}位次"
    subject = case.get("subject_type") or ""
    major = case.get("major_text") or case.get("major") or "目标专业"
    return f"{year_prefix}{case.get('province', '')}{subject}{score_or_rank}想学{major}，能报哪些学校专业？"


def tool_arguments(case: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "province",
        "major_text",
        "subject_type",
        "score",
        "rank",
        "year",
        "reference_years",
        "preferred_regions",
        "school_level_filter",
        "limit",
    )
    return {key: case[key] for key in keys if case.get(key) not in (None, "", [])}


def classify_oracle(
    rows: list[dict[str, Any]],
    applicant_rank: int | None,
    requested_year: int | None = None,
    limit: int = 30,
    input_issues: list[str] | None = None,
    major_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues = list(input_issues or [])
    major_meta = major_meta or {}
    if applicant_rank is None:
        return {
            "expected_status": "invalid_input",
            "issue_codes": sorted(set(issues or ["missing_rank"])),
            "candidate_rows": len(rows),
            "returned_major_rows": 0,
            "bucket_counts": {"rush": 0, "stable": 0, "safe": 0},
            "required_major_rows_by_bucket": {"rush": [], "stable": [], "safe": []},
            "empty_buckets": ["rush", "stable", "safe"],
            "reference_years": [],
            "history_fallback": False,
            "major_meta": major_meta,
        }

    buckets, selected_rows = selected_oracle_rows(rows, applicant_rank, max(int(limit), 0))
    reference_years = sorted(
        {year for row in selected_rows if (year := as_int(row.get("year"))) is not None},
        reverse=True,
    )
    history_fallback = bool(requested_year and reference_years and requested_year not in reference_years)
    required_rows = {
        bucket: [major_row_label(row) for row in bucket_rows]
        for bucket, bucket_rows in buckets.items()
    }
    bucket_counts = {bucket: len(buckets[bucket]) for bucket in BUCKETS}
    empty_buckets = [bucket for bucket, count in bucket_counts.items() if count == 0]
    status = "ok" if selected_rows else "not_found"
    subject_unknown_count = sum(1 for row in selected_rows if not str(row.get("subject_type") or "").strip())
    if subject_unknown_count:
        issues.append("subject_unknown_rows")

    return {
        "expected_status": status,
        "issue_codes": sorted(set(issues)),
        "candidate_rows": len(rows),
        "returned_major_rows": len(selected_rows),
        "bucket_counts": bucket_counts,
        "required_major_rows_by_bucket": required_rows,
        "empty_buckets": empty_buckets,
        "reference_years": reference_years,
        "history_fallback": history_fallback,
        "subject_unknown_count": subject_unknown_count,
        "major_meta": major_meta,
        "sample_rows": selected_rows[:10],
    }


def call_failures(case: dict[str, Any], entry_result: dict[str, Any]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    expected_intent = case.get("expected_intent")
    if expected_intent and entry_result.get("intent") != expected_intent:
        failures.append(
            failure("call_fail", "call_intent_mismatch", f"expected intent {expected_intent}, got {entry_result.get('intent')}")
        )

    expected_missing = case.get("expected_missing")
    if expected_missing is not None:
        actual_missing = entry_result.get("needs_clarification") or []
        if sorted(actual_missing) != sorted(expected_missing):
            failures.append(failure("call_fail", "call_missing_slots_mismatch", f"expected missing {expected_missing}, got {actual_missing}"))

    slots = entry_result.get("slots") or {}
    for key, expected_value in (case.get("expected_slots") or {}).items():
        if slots.get(key) != expected_value:
            failures.append(failure("call_fail", "call_slot_mismatch", f"{key}: expected {expected_value}, got {slots.get(key)}"))

    expected_arguments = case.get("expected_arguments") or {}
    if expected_arguments:
        plan = entry_result.get("tool_plan") or []
        actual_arguments = (plan[0].get("arguments") if plan else {}) or {}
        for key, expected_value in expected_arguments.items():
            if actual_arguments.get(key) != expected_value:
                failures.append(
                    failure("call_fail", "call_argument_mismatch", f"{key}: expected {expected_value}, got {actual_arguments.get(key)}")
                )
    return failures


def tool_failures(case: dict[str, Any], oracle: dict[str, Any], result: dict[str, Any]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    expected_status = case.get("expected_status") or oracle.get("expected_status")
    status = result.get("status")
    if expected_status == "invalid_input":
        if status not in {"needs_clarification", "not_found", "error"}:
            failures.append(failure("hard_fail", "tool_accepts_invalid_input", f"expected invalid-input status, got {status}"))
        return failures
    if expected_status and status != expected_status:
        failures.append(failure("hard_fail", "tool_status_mismatch", f"expected {expected_status}, got {status}"))
        return failures
    if "major_cross_level_candidates" in (oracle.get("issue_codes") or []):
        major_resolution = (result.get("data") or {}).get("major_resolution") or {}
        if not (
            major_resolution.get("candidate_count", 0) >= 2
            and major_resolution.get("candidate_level_summary")
        ):
            failures.append(
                failure(
                    "hard_fail",
                    "tool_missing_cross_level_major_resolution",
                    "oracle found multiple/cross-level major candidates but tool did not expose data.major_resolution candidate summary",
                )
            )
    if status != "ok":
        return failures

    data = result.get("data") or {}
    reference = data.get("reference") or {}
    coverage = data.get("coverage") or {}
    buckets = data.get("buckets") or {}
    if sorted(reference.get("reference_years") or [], reverse=True) != (oracle.get("reference_years") or []):
        failures.append(
            failure(
                "hard_fail",
                "tool_reference_years_mismatch",
                f"expected years {oracle.get('reference_years')}, got {reference.get('reference_years')}",
            )
        )
    if bool(reference.get("history_fallback")) != bool(oracle.get("history_fallback")):
        failures.append(
            failure(
                "hard_fail",
                "tool_history_fallback_mismatch",
                f"expected fallback {oracle.get('history_fallback')}, got {reference.get('history_fallback')}",
            )
        )
    if coverage.get("returned_major_rows") != oracle.get("returned_major_rows"):
        failures.append(
            failure(
                "hard_fail",
                "tool_returned_major_rows_mismatch",
                f"expected {oracle.get('returned_major_rows')}, got {coverage.get('returned_major_rows')}",
            )
        )

    actual_counts = {bucket: len(buckets.get(bucket) or []) for bucket in BUCKETS}
    if actual_counts != oracle.get("bucket_counts"):
        failures.append(failure("hard_fail", "tool_bucket_count_mismatch", f"expected {oracle.get('bucket_counts')}, got {actual_counts}"))

    actual_labels = {
        bucket: {tool_major_row_label(item) for item in buckets.get(bucket) or []}
        for bucket in BUCKETS
    }
    for bucket, expected_rows in (oracle.get("required_major_rows_by_bucket") or {}).items():
        for expected_row in expected_rows:
            if expected_row and expected_row not in actual_labels.get(bucket, set()):
                failures.append(failure("hard_fail", "tool_missing_expected_major_row", f"{bucket} missing {expected_row}"))
                break
    return failures


def answer_failures(case: dict[str, Any], entry_result: dict[str, Any]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    answer = str(entry_result.get("answer_markdown") or "")
    result = first_rank_to_major_result(entry_result)
    if not result:
        if entry_result.get("status") == "needs_clarification" and entry_result.get("intent") == "rank_to_major_match":
            if "补充" in answer and entry_result.get("needs_clarification"):
                return []
        if case.get("expected_intent") != "rank_to_major_match":
            return []
        failures.append(failure("answer_fail", "answer_missing_rank_to_major_trace", "entrypoint did not execute rank_to_major_match"))
        return failures

    if OVERPROMISE_RE.search(answer):
        failures.append(failure("answer_fail", "answer_overpromises_admission", "answer uses guaranteed-admission wording"))

    status = result.get("status")
    data = result.get("data") or {}
    warnings = result.get("warnings") or []
    if status == "ok":
        applicant = data.get("applicant") or {}
        reference = data.get("reference") or {}
        buckets = data.get("buckets") or {}
        all_school_names = [
            str(item.get("school_name") or "")
            for bucket in BUCKETS
            for item in buckets.get(bucket) or []
            if item.get("school_name")
        ]
        all_major_names = [
            str(item.get("major_name") or "")
            for bucket in BUCKETS
            for item in buckets.get(bucket) or []
            if item.get("major_name")
        ]
        if all_school_names and not any(name in answer for name in all_school_names[:8]):
            failures.append(failure("answer_fail", "answer_missing_school_names", "answer omits returned school names"))
        if all_major_names and not any(name in answer for name in all_major_names[:8]):
            failures.append(failure("answer_fail", "answer_missing_major_names", "answer omits returned major names"))
        nonempty_labels = [BUCKET_LABELS[bucket] for bucket in BUCKETS if buckets.get(bucket)]
        if nonempty_labels and not all(label in answer for label in nonempty_labels):
            failures.append(failure("answer_fail", "answer_missing_bucket_labels", f"answer omits bucket labels {nonempty_labels}"))
        rank = applicant.get("rank")
        if rank is not None and str(rank) not in normalize_digits(answer):
            failures.append(failure("answer_fail", "answer_missing_rank", f"answer omits applicant rank {rank}"))
        for year in reference.get("reference_years") or []:
            if year is not None and str(year) not in answer:
                failures.append(failure("answer_fail", "answer_missing_reference_year", f"answer omits reference year {year}"))
                break
        if reference.get("history_fallback") and not any(token in answer for token in ("历史", "回退", "最近可用", "缺少请求年份")):
            failures.append(failure("answer_fail", "answer_missing_fallback_warning", "answer omits history fallback warning"))
        for warning_text in warnings:
            if not answer_mentions_warning(answer, warning_text):
                failures.append(failure("answer_fail", "answer_missing_tool_warning", "answer omits tool warning"))
        if not mentions_scope(answer):
            failures.append(failure("answer_fail", "answer_missing_scope_note", "answer omits historical major-row scope limits"))
        empty_labels = [BUCKET_LABELS[bucket] for bucket in BUCKETS if not buckets.get(bucket)]
        if empty_labels and not mentions_empty_bucket(answer, empty_labels):
            failures.append(failure("answer_fail", "answer_missing_empty_bucket_note", f"answer omits empty bucket note {empty_labels}"))
    elif status == "not_found":
        if not any(token in answer for token in ("未命中", "没有", "查不到", "暂无")):
            failures.append(failure("answer_fail", "answer_missing_not_found", "not_found answer does not say data was not found"))
        if any(token in answer for token in ("冲", "稳", "保")) and re.search(r"[\u4e00-\u9fa5]{2,}大学", answer):
            failures.append(failure("answer_fail", "answer_invents_school_for_not_found", "not_found answer appears to list schools"))
        for warning_text in warnings:
            if not answer_mentions_warning(answer, warning_text):
                failures.append(failure("answer_fail", "answer_missing_tool_warning", "answer omits not_found warning"))
    elif status in {"needs_clarification", "error"}:
        if not any(token in answer for token in ("补充", "缺少", "错误", "不能", "失败")):
            failures.append(failure("answer_fail", "answer_missing_failure_explanation", f"{status} answer does not explain failure"))
    return failures


def first_rank_to_major_result(entry_result: dict[str, Any]) -> dict[str, Any] | None:
    for trace in entry_result.get("tool_trace") or []:
        if trace.get("tool_name") == "rank_to_major_match":
            return trace.get("result") or {}
    return None


def mentions_scope(answer: str) -> bool:
    return (
        "历史" in answer
        and any(token in answer for token in ("不代表", "不保证", "不能保证", "仅供参考", "参考"))
        and "专业" in answer
    )


def mentions_empty_bucket(answer: str, labels: list[str]) -> bool:
    return any(label in answer for label in labels) and any(token in answer for token in ("无", "没有", "暂无", "未给出", "为空"))


def answer_mentions_warning(answer: str, warning_text: str) -> bool:
    if not warning_text:
        return True
    if warning_text in answer:
        return True
    return any(token in answer for token in ("注意", "复核", "谨慎", "历史", "未命中", "缺少", "科类"))


def tool_major_row_label(item: dict[str, Any]) -> str:
    return "|".join(
        [
            str(item.get("school_name") or "").strip(),
            str(item.get("major_name") or "").strip(),
            str(item.get("batch") or "未标批次").strip(),
        ]
    )


def failure(severity: str, code: str, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message}


def generated_coverage_cases(client: MysqlCliClient, limit_groups: int) -> list[dict[str, Any]]:
    if limit_groups <= 0:
        return []
    sql = f"""
SELECT province_name, subject_type, major_name, MAX(CAST(year AS UNSIGNED)) AS max_year, COUNT(*) AS row_count
FROM edu_school_admission_stats
WHERE (deleted IS NULL OR deleted = b'0')
  AND stable_rank IS NOT NULL AND stable_rank > 0
  AND subject_type IS NOT NULL AND subject_type <> ''
  AND major_name IS NOT NULL AND major_name <> ''
GROUP BY province_name, subject_type, major_name
ORDER BY row_count DESC
LIMIT {int(limit_groups)}
""".strip()
    cases: list[dict[str, Any]] = []
    for row in client.query(sql):
        probe = client.query(
            f"""
SELECT stable_rank
FROM edu_school_admission_stats
WHERE (deleted IS NULL OR deleted = b'0')
  AND province_name = {sql_quote(row['province_name'])}
  AND subject_type = {sql_quote(row['subject_type'])}
  AND major_name = {sql_quote(row['major_name'])}
  AND year = {int(row['max_year'])}
  AND stable_rank IS NOT NULL AND stable_rank > 0
ORDER BY ABS(stable_rank - 60000)
LIMIT 1
""".strip()
        )
        if not probe:
            continue
        case = {
            "id": f"auto_major_coverage_{row['province_name']}_{row['subject_type']}_{row['major_name']}_{row['max_year']}",
            "category": "auto_major_coverage",
            "province": row["province_name"],
            "subject_type": row["subject_type"],
            "major_text": row["major_name"],
            "rank": as_int(probe[0].get("stable_rank")),
            "year": int(row["max_year"]),
            "limit": 20,
            "expected_intent": "rank_to_major_match",
        }
        case["question"] = build_question(case)
        cases.append(case)
    return cases


def generated_threshold_cases(client: MysqlCliClient, limit_cases: int) -> list[dict[str, Any]]:
    if limit_cases <= 0:
        return []
    sql = f"""
SELECT province_name, subject_type, year, school_id, school_name, major_name, chong_rank, stable_rank, bao_rank
FROM edu_school_admission_stats
WHERE (deleted IS NULL OR deleted = b'0')
  AND subject_type IS NOT NULL AND subject_type <> ''
  AND major_name IS NOT NULL AND major_name <> ''
  AND chong_rank IS NOT NULL AND stable_rank IS NOT NULL AND bao_rank IS NOT NULL
  AND chong_rank > 0 AND stable_rank > 0 AND bao_rank > 0
ORDER BY CAST(year AS UNSIGNED) DESC, province_name, subject_type, school_name, major_name
LIMIT {int(limit_cases)}
""".strip()
    cases: list[dict[str, Any]] = []
    for row in client.query(sql):
        for label, field, delta in (
            ("chong_equal", "chong_rank", 0),
            ("stable_equal", "stable_rank", 0),
            ("bao_equal", "bao_rank", 0),
            ("stable_miss_by_one", "stable_rank", 1),
        ):
            rank = as_int(row.get(field))
            if rank is None:
                continue
            case = {
                "id": f"auto_major_threshold_{row['province_name']}_{row['school_id']}_{label}_{rank + delta}",
                "category": f"auto_major_threshold_{label}",
                "province": row["province_name"],
                "subject_type": row["subject_type"],
                "major_text": row["major_name"],
                "rank": rank + delta,
                "year": int(row["year"]),
                "limit": 20,
                "expected_intent": "rank_to_major_match",
            }
            case["question"] = build_question(case)
            cases.append(case)
    return cases


def skipped_entry_result(question: str) -> dict[str, Any]:
    return {
        "status": "skipped",
        "intent": "skipped",
        "slots": {},
        "needs_clarification": [],
        "tool_plan": [],
        "tool_trace": [],
        "warnings": [],
        "scope_notes": [],
        "answer_markdown": "",
        "question": question,
    }


def evaluate_case(
    case: dict[str, Any],
    client: MysqlCliClient | None,
    tools: RetrievalTools | None,
    entrypoint: NaturalLanguageEntryPoint | None,
    include_entrypoint: bool = True,
) -> dict[str, Any]:
    question = case.get("question") or build_question(case)
    if include_entrypoint:
        if entrypoint is None:
            raise ValueError("entrypoint is required when include_entrypoint=True")
        entry_result = entrypoint.run(question, execute=True)
    else:
        entry_result = skipped_entry_result(question)
    args = tool_arguments(case)
    direct_tool_result: dict[str, Any] = {}
    oracle: dict[str, Any] = {"expected_status": "skipped"}
    data_warnings: list[dict[str, str]] = []

    if args.get("province") and args.get("major_text"):
        if client is None or tools is None:
            raise ValueError("client and tools are required for direct rank_to_major_match evaluation")
        major, major_meta = resolve_major_candidate(client, args.get("major_text"))
        applicant_rank, rank_subject_type, rank_meta = resolve_rank_and_subject(client, case)
        input_issues = list(major_meta.get("issues", [])) + list(rank_meta.get("issues", []))
        rows = []
        if major is not None and applicant_rank is not None and rank_subject_type:
            oracle_case = dict(case)
            oracle_case["subject_type"] = rank_subject_type
            rows = oracle_rows(client, oracle_case, major, applicant_rank, rank_subject_type)
        oracle = classify_oracle(
            rows,
            applicant_rank,
            case.get("year"),
            case.get("limit", 30),
            input_issues,
            {"major": major, **major_meta, "rank_subject_type": rank_subject_type},
        )
        direct_tool_result = call_retrieval_function("rank_to_major_match", args, tools=tools)
        data_warnings = [
            failure("data_warning", code, f"oracle issue: {code}")
            for code in oracle.get("issue_codes", [])
            if code
            not in {
                "missing_score_or_rank",
                "missing_subject_type",
                "major_not_found",
                "major_ambiguous",
                "score_rank_not_found",
            }
        ]

    return {
        "id": case["id"],
        "category": case.get("category"),
        "question": question,
        "input": args,
        "oracle": oracle,
        "tool_result": direct_tool_result,
        "entry_result": compact_entry_result(entry_result),
        "call_failures": call_failures(case, entry_result) if include_entrypoint else [],
        "tool_failures": tool_failures(case, oracle, direct_tool_result) if direct_tool_result else [],
        "answer_failures": answer_failures(case, entry_result) if include_entrypoint else [],
        "data_warnings": data_warnings,
    }


def compact_entry_result(entry_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": entry_result.get("status"),
        "intent": entry_result.get("intent"),
        "slots": entry_result.get("slots"),
        "needs_clarification": entry_result.get("needs_clarification"),
        "tool_plan": entry_result.get("tool_plan"),
        "tool_trace": entry_result.get("tool_trace"),
        "warnings": entry_result.get("warnings"),
        "scope_notes": entry_result.get("scope_notes"),
        "answer_markdown": entry_result.get("answer_markdown"),
    }


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    intent_counts: Counter[str] = Counter()
    for record in records:
        status_counts[str((record.get("tool_result") or {}).get("status") or "skipped")] += 1
        intent_counts[str((record.get("entry_result") or {}).get("intent"))] += 1
        category_counts[str(record.get("category"))] += 1
        for group in ("call_failures", "tool_failures", "answer_failures", "data_warnings"):
            for item in record.get(group) or []:
                counts[item.get("severity", "unknown")] += 1
    return {
        "total": len(records),
        "call_fail": counts["call_fail"],
        "hard_fail": counts["hard_fail"],
        "answer_fail": counts["answer_fail"],
        "data_warning": counts["data_warning"],
        "status_counts": dict(sorted(status_counts.items())),
        "intent_counts": dict(sorted(intent_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
    }


def write_reports(records: list[dict[str, Any]], report_dir: Path, stamp: str | None = None) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = stamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = report_dir / f"rank_to_major_match_boundary_eval_{stamp}.jsonl"
    md_path = report_dir / f"rank_to_major_match_boundary_eval_{stamp}.md"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    md_path.write_text(render_markdown(records, jsonl_path), encoding="utf-8")
    return jsonl_path, md_path


def render_markdown(records: list[dict[str, Any]], jsonl_path: Path) -> str:
    summary = summarize_records(records)
    lines = [
        "# rank_to_major_match Boundary Evaluation",
        "",
        f"- JSONL: `{jsonl_path.as_posix()}`",
        f"- Total cases: {summary['total']}",
        f"- Function-call failures: {summary['call_fail']}",
        f"- Tool hard failures: {summary['hard_fail']}",
        f"- Answer failures: {summary['answer_fail']}",
        f"- Data warnings: {summary['data_warning']}",
        f"- Tool statuses: `{json.dumps(summary['status_counts'], ensure_ascii=False, sort_keys=True)}`",
        f"- Entrypoint intents: `{json.dumps(summary['intent_counts'], ensure_ascii=False, sort_keys=True)}`",
        "",
        "## Top Findings",
        "",
    ]
    finding_records = [
        record
        for record in records
        if record.get("call_failures") or record.get("tool_failures") or record.get("answer_failures") or record.get("data_warnings")
    ]
    if not finding_records:
        lines.append("No failures or warnings.")
    for record in finding_records[:60]:
        codes = [
            item["code"]
            for group in ("call_failures", "tool_failures", "answer_failures", "data_warnings")
            for item in record.get(group, [])
        ]
        lines.append(
            f"- `{record['id']}` [{record.get('category')}] "
            f"tool_status={(record.get('tool_result') or {}).get('status', 'skipped')} codes={', '.join(codes)}"
        )
        lines.append(f"  question: {record.get('question')}")
        answer = str((record.get("entry_result") or {}).get("answer_markdown") or "").replace("\n", " ")
        if answer:
            lines.append(f"  answer: {answer[:260]}")
        oracle = record.get("oracle") or {}
        if oracle.get("expected_status") == "ok":
            lines.append(
                "  oracle: "
                f"years={oracle.get('reference_years')} buckets={oracle.get('bucket_counts')} "
                f"returned={oracle.get('returned_major_rows')}"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `call_fail`: the natural-language layer chose the wrong tool or extracted unsafe slots.",
            "- `hard_fail`: direct tool output disagrees with the independent local oracle.",
            "- `answer_fail`: structured retrieval may be correct, but the user-facing answer omits required facts or overstates certainty.",
            "- `data_warning`: the local data has ambiguity or quality conditions that should be surfaced or manually reviewed.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_evaluation(args: argparse.Namespace) -> tuple[list[dict[str, Any]], Path, Path]:
    load_env_file(PROJECT_ROOT / ".env")
    client = MysqlCliClient(DbConfig.from_env())
    tools = RetrievalTools(client)
    entrypoint = None
    if not args.tool_only:
        entrypoint = NaturalLanguageEntryPoint(dispatcher=lambda tool_name, arguments: call_retrieval_function(tool_name, arguments, tools=tools))
    cases = load_manual_cases(args.cases)
    if not args.manual_only:
        cases.extend(generated_coverage_cases(client, args.auto_groups))
        cases.extend(generated_threshold_cases(client, args.threshold_cases))
    records = [evaluate_case(case, client, tools, entrypoint, include_entrypoint=not args.tool_only) for case in cases]
    jsonl_path, md_path = write_reports(records, args.report_dir, args.stamp)
    return records, jsonl_path, md_path


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Evaluate rank_to_major_match boundary behavior.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--stamp")
    parser.add_argument("--manual-only", action="store_true")
    parser.add_argument("--tool-only", action="store_true", help="Skip natural-language entrypoint and answer checks; evaluate direct tool plus oracle only.")
    parser.add_argument("--auto-groups", type=int, default=12)
    parser.add_argument("--threshold-cases", type=int, default=6)
    args = parser.parse_args(argv)
    records, jsonl_path, md_path = run_evaluation(args)
    summary = summarize_records(records)
    print(json.dumps({"summary": summary, "jsonl": str(jsonl_path), "markdown": str(md_path)}, ensure_ascii=False, indent=2))
    return 0 if summary["hard_fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
