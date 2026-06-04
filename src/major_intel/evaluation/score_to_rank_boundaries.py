"""Evaluate score_to_rank boundary behavior against local data and answers.

This runner is deliberately stricter than the smoke test runner. It checks
three layers for each case:

1. Database oracle: what exact score-rank rows exist locally.
2. Tool envelope: whether score_to_rank returns the right structured result.
3. Answer text: whether the natural-language entrypoint actually tells the
   user the rank range, year, warnings, and scope.
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
from major_intel.function_calls.registry import call_retrieval_function
from major_intel.function_calls.retrieval_tools import PROVINCE_ID_BY_NAME, RetrievalTools, tool_result
from major_intel.storage.local_retrieval_mvp import DbConfig, MysqlCliClient, sql_quote


DEFAULT_CASES_PATH = PROJECT_ROOT / "data" / "score_to_rank_boundary_cases.json"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports"
SCORE_TABLE = "edu_score_rank"

SUBJECT_ALIASES = {
    "理科": ["物理"],
    "物理": ["理科"],
    "文科": ["历史"],
    "历史": ["文科"],
}
SELECTED_SUBJECT_NAMES = {"物理", "化学", "生物", "政治", "思想政治", "历史", "地理", "技术"}
PROVINCE_NAME_BY_ID = {value: key for key, value in PROVINCE_ID_BY_NAME.items()}


def load_env_file(path: Path) -> None:
    """Load a local .env file into os.environ without printing secrets."""

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_manual_cases(path: Path = DEFAULT_CASES_PATH) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_cases = payload if isinstance(payload, list) else payload.get("cases", [])
    cases: list[dict[str, Any]] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        case = dict(raw_case)
        case.setdefault("id", f"manual_{index}")
        case.setdefault("category", "manual")
        case.setdefault("question", build_question(case))
        cases.append(case)
    return cases


def build_question(case: dict[str, Any]) -> str:
    year_prefix = f"{case['year']}年" if case.get("year") else ""
    subject = case.get("subject_type") or ""
    return f"{year_prefix}{case['province']}{subject}{case['score']}分对应多少位次？"


def province_id_for_input(province: Any) -> str | None:
    text = str(province or "").strip()
    if text.isdigit():
        return text
    text = text.removesuffix("省").removesuffix("市").removesuffix("壮族自治区").removesuffix("自治区").removesuffix("回族自治区").removesuffix("维吾尔自治区")
    return PROVINCE_ID_BY_NAME.get(text)


def subject_candidates(subject_type: Any) -> list[str]:
    primary = str(subject_type or "").strip()
    candidates = [primary] + SUBJECT_ALIASES.get(primary, [])
    seen: set[str] = set()
    result: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            result.append(candidate)
    return result


def oracle_subject_candidates(client: MysqlCliClient, province_id: str, subject_type: Any, year: Any) -> tuple[list[str], list[str]]:
    primary = str(subject_type or "").strip()

    if year:
        year_clause = f"AND year = {int(year)}"
    else:
        year_clause = f"""
AND CAST(year AS UNSIGNED) = (
  SELECT MAX(CAST(year AS UNSIGNED))
  FROM {SCORE_TABLE}
  WHERE deleted = 0 AND province_id = {sql_quote(province_id)}
)
""".strip()
    sql = f"""
SELECT subject_type
FROM {SCORE_TABLE}
WHERE deleted = 0
  AND province_id = {sql_quote(province_id)}
  {year_clause}
GROUP BY subject_type
ORDER BY subject_type
""".strip()
    available = sorted({str(row.get("subject_type") or "").strip() for row in client.query(sql) if str(row.get("subject_type") or "").strip()})
    if not primary:
        if available == ["综合"]:
            return ["综合"], []
        return [], ["missing_subject_type"]
    if available == ["综合"] and primary in SELECTED_SUBJECT_NAMES:
        return ["综合"], []
    candidates = subject_candidates(primary)
    if available and not any(candidate in available for candidate in candidates):
        return candidates, ["invalid_subject_type"]
    return candidates, []


def parse_integral_score(value: Any) -> tuple[int | None, list[str]]:
    """Return an integer score and issue codes for invalid/boundary input."""

    if value is None or str(value).strip() == "":
        return None, ["missing_score"]
    text = str(value).strip()
    if re.fullmatch(r"[+-]?\d+", text):
        return int(text), []
    if re.fullmatch(r"[+-]?\d+\.\d+", text):
        numeric = float(text)
        if numeric.is_integer():
            return int(numeric), ["decimal_integral_score"]
        return int(numeric), ["non_integral_score"]
    return None, ["nonnumeric_score"]


def oracle_rows(client: MysqlCliClient, case: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    province_id = province_id_for_input(case.get("province"))
    score, score_issues = parse_integral_score(case.get("score"))
    if not province_id:
        return [], ["unknown_province"]
    if score is None:
        return [], score_issues

    candidates, subject_issues = oracle_subject_candidates(client, province_id, case.get("subject_type"), case.get("year"))
    score_issues = [*score_issues, *subject_issues]
    if not candidates:
        return [], score_issues
    subject_values = ", ".join(sql_quote(value) for value in candidates)
    year_clause = f"AND year = {int(case['year'])}" if case.get("year") else ""
    sql = f"""
SELECT province_id, year, subject_type, score, same_count, highest_rank, lowest_rank, batch_type
FROM {SCORE_TABLE}
WHERE deleted = 0
  AND province_id = {sql_quote(province_id)}
  AND subject_type IN ({subject_values})
  AND score = {score}
  {year_clause}
ORDER BY CAST(year AS UNSIGNED) DESC, subject_type, batch_type, highest_rank, lowest_rank
""".strip()
    return client.query(sql), score_issues


def classify_oracle(rows: list[dict[str, Any]], input_issues: list[str] | None = None) -> dict[str, Any]:
    issues = list(input_issues or [])
    if any(
        issue in {"missing_score", "nonnumeric_score", "non_integral_score", "unknown_province", "missing_subject_type", "invalid_subject_type"}
        for issue in issues
    ):
        return {
            "expected_status": "invalid_input",
            "expected_data": {},
            "rows_count": len(rows),
            "issue_codes": issues,
            "batch_types": [],
        }
    if not rows:
        return {
            "expected_status": "not_found",
            "expected_data": {},
            "rows_count": 0,
            "issue_codes": issues,
            "batch_types": [],
        }

    batch_types = sorted({str(row.get("batch_type") or "") for row in rows if str(row.get("batch_type") or "")})
    years = sorted({str(row.get("year") or "") for row in rows if str(row.get("year") or "")})
    subjects = sorted({str(row.get("subject_type") or "") for row in rows if str(row.get("subject_type") or "")})
    for row in rows:
        same_count = as_int(row.get("same_count"))
        highest = as_int(row.get("highest_rank"))
        lowest = as_int(row.get("lowest_rank"))
        if highest is None or lowest is None or highest > lowest:
            issues.append("bad_rank_range")
        elif same_count is not None and same_count != lowest - highest + 1:
            issues.append("same_count_mismatch")

    if len(rows) > 1:
        if len(batch_types) > 1:
            issues.append("ambiguous_batch_key")
        if len(years) > 1:
            issues.append("ambiguous_year_key")
        if len(subjects) > 1:
            issues.append("ambiguous_subject_key")
        issues.append("ambiguous_exact_key")
        return {
            "expected_status": "ambiguous",
            "expected_data": {},
            "rows_count": len(rows),
            "issue_codes": sorted(set(issues)),
            "batch_types": batch_types,
            "years": years,
            "subject_types": subjects,
            "sample_rows": rows[:5],
        }

    row = rows[0]
    return {
        "expected_status": "ok",
        "expected_data": {
            "score": as_int(row.get("score")),
            "same_count": as_int(row.get("same_count")),
            "rank_range": {
                "highest_rank": as_int(row.get("highest_rank")),
                "lowest_rank": as_int(row.get("lowest_rank")),
            },
        },
        "expected_year": str(row.get("year") or ""),
        "expected_subject_type": str(row.get("subject_type") or ""),
        "rows_count": 1,
        "issue_codes": sorted(set(issues)),
        "batch_types": batch_types,
        "years": years,
        "subject_types": subjects,
        "sample_rows": rows[:1],
    }


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "NULL":
        return None
    return int(float(text))


def tool_failures(case: dict[str, Any], oracle: dict[str, Any], result: dict[str, Any]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    expected = oracle.get("expected_status")
    status = result.get("status")

    if expected == "ok":
        if status != "ok":
            failures.append(failure("hard_fail", "tool_status_mismatch", f"expected ok, got {status}"))
            return failures
        expected_data = oracle.get("expected_data") or {}
        actual_data = result.get("data") or {}
        if actual_data.get("score") != expected_data.get("score"):
            failures.append(failure("hard_fail", "tool_score_mismatch", f"expected score {expected_data.get('score')}, got {actual_data.get('score')}"))
        if actual_data.get("same_count") != expected_data.get("same_count"):
            failures.append(
                failure("hard_fail", "tool_same_count_mismatch", f"expected same_count {expected_data.get('same_count')}, got {actual_data.get('same_count')}")
            )
        if (actual_data.get("rank_range") or {}) != (expected_data.get("rank_range") or {}):
            failures.append(
                failure(
                    "hard_fail",
                    "tool_rank_range_mismatch",
                    f"expected rank_range {expected_data.get('rank_range')}, got {actual_data.get('rank_range')}",
                )
            )
        normalized = result.get("normalized_slots") or {}
        if str(normalized.get("year") or "") != str(oracle.get("expected_year") or ""):
            failures.append(failure("hard_fail", "tool_year_mismatch", f"expected year {oracle.get('expected_year')}, got {normalized.get('year')}"))
        if str(normalized.get("matched_subject_type") or "") != str(oracle.get("expected_subject_type") or ""):
            failures.append(
                failure(
                    "hard_fail",
                    "tool_subject_type_mismatch",
                    f"expected subject {oracle.get('expected_subject_type')}, got {normalized.get('matched_subject_type')}",
                )
            )

    elif expected == "not_found":
        if status != "not_found":
            failures.append(failure("hard_fail", "tool_status_mismatch", f"expected not_found, got {status}"))

    elif expected == "invalid_input":
        if status not in {"needs_clarification", "error"}:
            failures.append(failure("hard_fail", "tool_accepts_invalid_score", f"expected invalid-input status, got {status}"))

    elif expected == "ambiguous":
        if status == "error":
            failures.append(failure("hard_fail", "tool_error_on_ambiguous_key", "ambiguous database key should not crash tool"))
        if status == "ok" and not result.get("warnings") and not case.get("allow_ambiguous_ok"):
            failures.append(failure("answer_fail", "tool_missing_ambiguity_warning", "ambiguous exact key returned without warning"))

    return failures


def answer_failures(case: dict[str, Any], entry_result: dict[str, Any]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    answer = str(entry_result.get("answer_markdown") or "")
    trace_result = first_score_to_rank_result(entry_result)
    if not trace_result:
        if (
            entry_result.get("status") == "needs_clarification"
            and entry_result.get("intent") == "score_to_rank"
            and "score" in (entry_result.get("needs_clarification") or [])
            and "分数" in answer
        ):
            return []
        failures.append(failure("answer_fail", "answer_missing_score_to_rank_trace", "entrypoint did not execute score_to_rank"))
        return failures

    status = trace_result.get("status")
    data = trace_result.get("data") or {}
    normalized = trace_result.get("normalized_slots") or {}

    if status == "ok":
        rank_range = data.get("rank_range") or {}
        highest = rank_range.get("highest_rank")
        lowest = rank_range.get("lowest_rank")
        if highest is not None and lowest is not None and not contains_number(answer, highest, lowest):
            failures.append(failure("answer_fail", "answer_missing_rank_range", f"answer omits rank range {highest}-{lowest}"))
        if normalized.get("year") and str(normalized.get("year")) not in answer:
            failures.append(failure("answer_fail", "answer_missing_year", f"answer omits matched year {normalized.get('year')}"))
        if data.get("same_count") is not None and str(data.get("same_count")) not in normalize_digits(answer):
            failures.append(failure("answer_fail", "answer_missing_same_count", f"answer omits same_count {data.get('same_count')}"))
        if trace_result.get("scope_notes") and not mentions_scope(answer):
            failures.append(failure("answer_fail", "answer_missing_scope_note", "answer omits same-province/subject/year scope"))
        input_subject = str((trace_result.get("input") or {}).get("subject_type") or normalized.get("subject_type") or "")
        matched_subject = str(normalized.get("matched_subject_type") or "")
        if matched_subject and input_subject and matched_subject != input_subject:
            if matched_subject not in answer or not any(token in answer for token in ("复核", "口径", "按")):
                failures.append(failure("answer_fail", "answer_missing_subject_alias_warning", "answer omits matched subject-type warning"))
        for warning_text in trace_result.get("warnings") or []:
            if not answer_mentions_warning(answer, warning_text):
                failures.append(failure("answer_fail", "answer_missing_tool_warning", "answer omits tool warning"))

    elif status == "not_found":
        if not any(token in answer for token in ("未命中", "没有", "查不到", "暂无")):
            failures.append(failure("answer_fail", "answer_missing_not_found", "not_found answer does not say data was not found"))
        if has_rank_range_text(answer):
            failures.append(failure("answer_fail", "answer_invents_rank_for_not_found", "not_found answer contains a rank-like range"))
        for warning_text in trace_result.get("warnings") or []:
            if not answer_mentions_warning(answer, warning_text):
                failures.append(failure("answer_fail", "answer_missing_tool_warning", "answer omits not_found warning"))

    elif status in {"needs_clarification", "error"}:
        if not any(token in answer for token in ("补充", "缺少", "错误", "不能", "失败")):
            failures.append(failure("answer_fail", "answer_missing_failure_explanation", f"{status} answer does not explain failure"))

    return failures


def first_score_to_rank_result(entry_result: dict[str, Any]) -> dict[str, Any] | None:
    for trace in entry_result.get("tool_trace") or []:
        if trace.get("tool_name") == "score_to_rank":
            return trace.get("result") or {}
    return None


def contains_number(text: str, *numbers: Any) -> bool:
    normalized = normalize_digits(text)
    return all(str(number) in normalized for number in numbers)


def normalize_digits(text: str) -> str:
    return str(text).replace(",", "").replace("，", "")


def mentions_scope(text: str) -> bool:
    return all(token in text for token in ("同省", "同科类")) and any(token in text for token in ("同年份", "年份", "年"))


def answer_mentions_warning(answer: str, warning_text: str) -> bool:
    if not warning_text:
        return True
    if warning_text in answer:
        return True
    return any(token in answer for token in ("未命中", "复核", "口径", "注意"))


def has_rank_range_text(text: str) -> bool:
    return bool(re.search(r"\d{3,}\s*(?:-|—|到|至|~)\s*\d{3,}", normalize_digits(text)))


def failure(severity: str, code: str, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message}


def generated_boundary_cases(client: MysqlCliClient, limit_groups: int) -> list[dict[str, Any]]:
    if limit_groups <= 0:
        return []
    latest_year = client.query(f"SELECT MAX(CAST(year AS UNSIGNED)) AS max_year FROM {SCORE_TABLE} WHERE deleted = 0")[0]["max_year"]
    sql = f"""
SELECT province_id, subject_type, year, MIN(score) AS min_score, MAX(score) AS max_score
FROM {SCORE_TABLE}
WHERE deleted = 0
  AND year = {int(latest_year)}
GROUP BY province_id, subject_type, year
ORDER BY province_id, subject_type
LIMIT {int(limit_groups)}
""".strip()
    cases: list[dict[str, Any]] = []
    for row in client.query(sql):
        province = PROVINCE_NAME_BY_ID.get(str(row["province_id"]), str(row["province_id"]))
        subject = str(row["subject_type"])
        year = int(row["year"])
        min_score = int(row["min_score"])
        max_score = int(row["max_score"])
        for label, score in (
            ("min", min_score),
            ("below_min", min_score - 1),
            ("max", max_score),
            ("above_max", max_score + 1),
        ):
            case = {
                "id": f"auto_{row['province_id']}_{subject}_{year}_{label}_{score}",
                "category": f"auto_{label}",
                "province": province,
                "subject_type": subject,
                "score": score,
                "year": year,
            }
            case["question"] = build_question(case)
            cases.append(case)
    return cases


def generated_ambiguous_cases(client: MysqlCliClient, limit_cases: int) -> list[dict[str, Any]]:
    if limit_cases <= 0:
        return []
    sql = f"""
SELECT province_id, subject_type, year, score, COUNT(*) AS row_count
FROM {SCORE_TABLE}
WHERE deleted = 0
GROUP BY province_id, subject_type, year, score
HAVING row_count > 1
ORDER BY CAST(year AS UNSIGNED) DESC, province_id, subject_type, score
LIMIT {int(limit_cases)}
""".strip()
    cases: list[dict[str, Any]] = []
    for row in client.query(sql):
        province = PROVINCE_NAME_BY_ID.get(str(row["province_id"]), str(row["province_id"]))
        case = {
            "id": f"auto_ambiguous_{row['province_id']}_{row['subject_type']}_{row['year']}_{row['score']}",
            "category": "auto_ambiguous_exact_key",
            "province": province,
            "subject_type": row["subject_type"],
            "score": int(row["score"]),
            "year": int(row["year"]),
            "allow_ambiguous_ok": True,
        }
        case["question"] = build_question(case)
        cases.append(case)
    return cases


def generated_subject_mode_cases(client: MysqlCliClient, limit_groups: int) -> list[dict[str, Any]]:
    if limit_groups <= 0:
        return []
    latest_year = client.query(f"SELECT MAX(CAST(year AS UNSIGNED)) AS max_year FROM {SCORE_TABLE} WHERE deleted = 0")[0]["max_year"]
    sql = f"""
SELECT province_id, year, subject_type, MIN(score) AS sample_score
FROM {SCORE_TABLE}
WHERE deleted = 0
  AND year = {int(latest_year)}
GROUP BY province_id, year, subject_type
ORDER BY CAST(province_id AS UNSIGNED), subject_type
""".strip()
    grouped: dict[tuple[str, int], dict[str, int]] = {}
    for row in client.query(sql):
        key = (str(row["province_id"]), int(row["year"]))
        grouped.setdefault(key, {})[str(row["subject_type"])] = int(row["sample_score"])

    cases: list[dict[str, Any]] = []
    for (province_id, year), scores_by_subject in grouped.items():
        province = PROVINCE_NAME_BY_ID.get(province_id, province_id)
        subjects = set(scores_by_subject)
        if subjects == {"综合"}:
            score = scores_by_subject["综合"]
            cases.extend(
                [
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_3plus3_missing_subject",
                        "category": "auto_subject_mode_3plus3_missing_subject",
                        "province": province,
                        "score": score,
                        "year": year,
                        "question": f"{year}年{province}{score}分对应多少位次？",
                    },
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_3plus3_physics_selected",
                        "category": "auto_subject_mode_3plus3_selected_subject",
                        "province": province,
                        "subject_type": "物理",
                        "score": score,
                        "year": year,
                        "question": f"{year}年{province}物理{score}分对应多少位次？",
                    },
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_3plus3_chemistry_selected",
                        "category": "auto_subject_mode_3plus3_selected_subject",
                        "province": province,
                        "subject_type": "化学",
                        "score": score,
                        "year": year,
                        "question": f"{year}年{province}化学{score}分对应多少位次？",
                    },
                ]
            )
        elif {"历史", "物理"}.issubset(subjects):
            physics_score = scores_by_subject["物理"]
            history_score = scores_by_subject["历史"]
            cases.extend(
                [
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_3plus12_missing_subject",
                        "category": "auto_subject_mode_3plus12_missing_subject",
                        "province": province,
                        "score": physics_score,
                        "year": year,
                        "question": f"{year}年{province}{physics_score}分对应多少位次？",
                    },
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_3plus12_chemistry_without_track",
                        "category": "auto_subject_mode_3plus12_selected_subject_without_track",
                        "province": province,
                        "subject_type": "化学",
                        "score": physics_score,
                        "year": year,
                        "question": f"{year}年{province}化学{physics_score}分对应多少位次？",
                    },
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_3plus12_physics_valid",
                        "category": "auto_subject_mode_3plus12_valid_track",
                        "province": province,
                        "subject_type": "物理",
                        "score": physics_score,
                        "year": year,
                        "question": f"{year}年{province}物理{physics_score}分对应多少位次？",
                    },
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_3plus12_history_valid",
                        "category": "auto_subject_mode_3plus12_valid_track",
                        "province": province,
                        "subject_type": "历史",
                        "score": history_score,
                        "year": year,
                        "question": f"{year}年{province}历史{history_score}分对应多少位次？",
                    },
                ]
            )
        elif {"文科", "理科"}.issubset(subjects):
            science_score = scores_by_subject["理科"]
            arts_score = scores_by_subject["文科"]
            cases.extend(
                [
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_traditional_missing_subject",
                        "category": "auto_subject_mode_traditional_missing_subject",
                        "province": province,
                        "score": science_score,
                        "year": year,
                        "question": f"{year}年{province}{science_score}分对应多少位次？",
                    },
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_traditional_physics_alias",
                        "category": "auto_subject_mode_traditional_alias",
                        "province": province,
                        "subject_type": "物理",
                        "score": science_score,
                        "year": year,
                        "question": f"{year}年{province}物理{science_score}分对应多少位次？",
                    },
                    {
                        "id": f"auto_subject_mode_{province_id}_{year}_traditional_history_alias",
                        "category": "auto_subject_mode_traditional_alias",
                        "province": province,
                        "subject_type": "历史",
                        "score": arts_score,
                        "year": year,
                        "question": f"{year}年{province}历史{arts_score}分对应多少位次？",
                    },
                ]
            )
        if len(cases) >= limit_groups:
            return cases[:limit_groups]
    return cases[:limit_groups]


def evaluate_case(case: dict[str, Any], client: MysqlCliClient, tools: RetrievalTools, entrypoint: NaturalLanguageEntryPoint) -> dict[str, Any]:
    rows, input_issues = oracle_rows(client, case)
    oracle = classify_oracle(rows, input_issues)
    arguments = {key: case[key] for key in ("province", "subject_type", "score", "year") if key in case}
    tool_result_payload = call_retrieval_function("score_to_rank", arguments, tools=tools)
    entry_result = entrypoint.run(case.get("question") or build_question(case), execute=True)
    input_issue_codes = {"missing_score", "missing_subject_type", "invalid_subject_type", "nonnumeric_score", "non_integral_score", "unknown_province"}
    data_warnings = [failure("data_warning", code, f"oracle issue: {code}") for code in oracle.get("issue_codes", []) if code not in input_issue_codes]
    return {
        "id": case["id"],
        "category": case.get("category"),
        "input": arguments,
        "question": case.get("question") or build_question(case),
        "oracle": oracle,
        "tool_result": tool_result_payload,
        "entry_result": compact_entry_result(entry_result),
        "tool_failures": tool_failures(case, oracle, tool_result_payload),
        "answer_failures": answer_failures(case, entry_result),
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
    for record in records:
        status_counts[str((record.get("tool_result") or {}).get("status"))] += 1
        category_counts[str(record.get("category"))] += 1
        for group in ("tool_failures", "answer_failures", "data_warnings"):
            for item in record.get(group) or []:
                counts[item.get("severity", "unknown")] += 1
    return {
        "total": len(records),
        "hard_fail": counts["hard_fail"],
        "answer_fail": counts["answer_fail"],
        "data_warning": counts["data_warning"],
        "status_counts": dict(sorted(status_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
    }


def write_reports(records: list[dict[str, Any]], report_dir: Path, stamp: str | None = None) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = stamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = report_dir / f"score_to_rank_boundary_eval_{stamp}.jsonl"
    md_path = report_dir / f"score_to_rank_boundary_eval_{stamp}.md"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    md_path.write_text(render_markdown(records, jsonl_path), encoding="utf-8")
    return jsonl_path, md_path


def render_markdown(records: list[dict[str, Any]], jsonl_path: Path) -> str:
    summary = summarize_records(records)
    lines = [
        "# score_to_rank Boundary Evaluation",
        "",
        f"- JSONL: `{jsonl_path.as_posix()}`",
        f"- Total cases: {summary['total']}",
        f"- Hard failures: {summary['hard_fail']}",
        f"- Answer failures: {summary['answer_fail']}",
        f"- Data warnings: {summary['data_warning']}",
        f"- Tool statuses: `{json.dumps(summary['status_counts'], ensure_ascii=False, sort_keys=True)}`",
        "",
        "## Top Failures",
        "",
    ]
    failing = [
        record
        for record in records
        if record.get("tool_failures") or record.get("answer_failures") or record.get("data_warnings")
    ]
    if not failing:
        lines.append("No failures or warnings.")
    for record in failing[:30]:
        codes = [item["code"] for item in record.get("tool_failures", []) + record.get("answer_failures", []) + record.get("data_warnings", [])]
        lines.append(f"- `{record['id']}` [{record.get('category')}] status={record['tool_result'].get('status')} codes={', '.join(codes)}")
        answer = str((record.get("entry_result") or {}).get("answer_markdown") or "").replace("\n", " ")
        if answer:
            lines.append(f"  answer: {answer[:220]}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `hard_fail`: tool output disagrees with the local oracle or accepts invalid input.",
            "- `answer_fail`: structured retrieval succeeded or failed correctly, but the user-facing answer omitted required facts or warnings.",
            "- `data_warning`: local `edu_score_rank` data has ambiguity or quality issues the tool may need to surface.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_evaluation(args: argparse.Namespace) -> tuple[list[dict[str, Any]], Path, Path]:
    load_env_file(PROJECT_ROOT / ".env")
    client = MysqlCliClient(DbConfig.from_env())
    tools = RetrievalTools(client)
    entrypoint = NaturalLanguageEntryPoint(dispatcher=lambda tool_name, arguments: call_retrieval_function(tool_name, arguments, tools=tools))
    cases = load_manual_cases(args.cases)
    if not args.manual_only:
        cases.extend(generated_boundary_cases(client, args.auto_groups))
        cases.extend(generated_ambiguous_cases(client, args.ambiguous_cases))
        cases.extend(generated_subject_mode_cases(client, args.subject_mode_cases))
    records = [evaluate_case(case, client, tools, entrypoint) for case in cases]
    jsonl_path, md_path = write_reports(records, args.report_dir, args.stamp)
    return records, jsonl_path, md_path


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Evaluate score_to_rank tool and answer boundaries.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--stamp")
    parser.add_argument("--manual-only", action="store_true")
    parser.add_argument("--auto-groups", type=int, default=8)
    parser.add_argument("--ambiguous-cases", type=int, default=8)
    parser.add_argument("--subject-mode-cases", type=int, default=16)
    args = parser.parse_args(argv)

    try:
        records, jsonl_path, md_path = run_evaluation(args)
    except Exception as exc:
        print(json.dumps(tool_result("score_to_rank_boundary_eval", "error", {}, warnings=[f"{type(exc).__name__}: {exc}"]), ensure_ascii=False))
        return 1

    summary = summarize_records(records)
    print(
        json.dumps(
            {
                "status": "ok",
                "summary": summary,
                "jsonl_report": str(jsonl_path),
                "markdown_report": str(md_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
