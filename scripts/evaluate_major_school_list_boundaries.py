"""Audit `major_school_list` against independent local-database oracle queries."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.local_retrieval_mvp import DbConfig, MysqlCliClient
from scripts.major_school_list_oracles import (
    build_oracle_major_school_relation_sql,
    build_oracle_major_school_sql,
    normalize_province_filter,
)
from scripts.retrieval_function_registry import call_retrieval_function


DEFAULT_JSONL_REPORT = PROJECT_ROOT / "reports" / "major_school_list_boundary_eval.jsonl"
DEFAULT_MARKDOWN_REPORT = PROJECT_ROOT / "reports" / "major_school_list_boundary_eval.md"
DEFAULT_CASES_PATH = PROJECT_ROOT / "tests" / "function_calls" / "major_school_list" / "boundary_cases.json"


@dataclass(frozen=True)
class AuditCase:
    case_id: str
    major: str
    province_filter: str | None = None
    school_level_filter: str | None = None
    limit: Any = 50
    expected_status: str | None = None
    expected_warning_substrings: list[str] = field(default_factory=list)
    note: str = ""


@dataclass(frozen=True)
class AuditResult:
    case: AuditCase
    tool_status: str
    tool_school_count: int
    oracle_school_count: int
    relation_counts: dict[str, int]
    missing_school_names: list[str]
    tool_school_names: list[str] | None = None
    oracle_school_names: list[str] | None = None
    normalized_major: dict[str, Any] | None = None
    normalized_province_filter: str | None = None
    warnings: list[str] | None = None
    data_gaps: list[str] | None = None
    errors: list[str] | None = None
    classification: str = "unclassified"
    verdict: str = "review"
    reason: str = ""


def load_env_file(path: Path) -> dict[str, str]:
    """Load a minimal dotenv file without printing secrets."""

    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def apply_env_file(path: Path) -> None:
    for key, value in load_env_file(path).items():
        os.environ.setdefault(key, value)


def classify_result(result: AuditResult) -> AuditResult:
    """Classify one audit result into a stable issue bucket."""

    errors = result.errors or []
    expected_status = result.case.expected_status
    if errors:
        if _is_invalid_limit(result.case.limit):
            return replace(
                result,
                classification="input_validation_gap",
                verdict="fail",
                reason="limit 小于 1 仍进入 SQL 层或抛出流程错误，未返回结构化参数澄清结果。",
            )
        return replace(result, classification="process_error", verdict="fail", reason="；".join(errors))

    if expected_status and result.tool_status != expected_status:
        return replace(
            result,
            classification="status_mismatch",
            verdict="fail",
            reason=f"工具状态不符合预期：期望 {expected_status}，实际 {result.tool_status}。",
        )

    if _is_invalid_limit(result.case.limit) and result.tool_status == "needs_clarification":
        return replace(
            result,
            classification="pass",
            verdict="pass",
            reason="limit 不是有效正整数时已返回结构化参数澄清，没有进入 SQL 层。",
        )

    if _is_invalid_limit(result.case.limit):
        return replace(
            result,
            classification="input_validation_gap",
            verdict="fail",
            reason="limit 不是有效正整数时仍返回普通检索结果，未给出参数校验提示。",
        )

    if expected_status and result.tool_status == expected_status and expected_status != "ok":
        return replace(result, classification="pass", verdict="pass", reason=f"工具状态符合预期：{expected_status}。")

    missing_warning = _missing_expected_warning(result)
    if missing_warning:
        return replace(
            result,
            classification="warning_propagation_gap",
            verdict="fail",
            reason=f"工具未传播预期 warning：{missing_warning}。",
        )

    requested_province = str(result.case.province_filter or "").strip()
    normalized_province = result.normalized_province_filter or ""
    if requested_province and normalized_province and requested_province != normalized_province:
        if result.oracle_school_count > result.tool_school_count:
            return replace(
                result,
                classification="province_normalization_gap",
                verdict="fail",
                reason=f"省份筛选未归一化：输入 {requested_province}，参考口径 {normalized_province} 有更多记录。",
            )

    limit_value = _limit_as_int(result.case.limit)
    expected_visible = min(result.oracle_school_count, limit_value)
    if result.oracle_school_count > limit_value and result.tool_school_count == limit_value:
        return replace(
            result,
            classification="limit_truncated",
            verdict="pass",
            reason="工具按正数 limit 返回了指定条数；参考查询仍有更多记录。",
        )

    school_id_rows = result.relation_counts.get("matches_school_id", 0)
    if result.oracle_school_count > result.tool_school_count and school_id_rows > 0:
        return replace(
            result,
            classification="key_mismatch",
            verdict="fail",
            reason="参考查询通过 school_id/code 双键找到了更多学校，工具返回数量偏少。",
        )

    if result.oracle_school_count == 0 and result.tool_school_count == 0:
        return replace(result, classification="pass", verdict="pass", reason="工具和参考查询都未命中学校记录。")

    if result.oracle_school_count > 0 and result.tool_school_count == expected_visible:
        return replace(result, classification="pass", verdict="pass", reason="工具返回学校数量与参考查询一致。")

    if result.tool_status != "ok" and result.oracle_school_count > 0:
        return replace(
            result,
            classification="status_mismatch",
            verdict="fail",
            reason="参考查询有学校记录，但工具没有返回 ok。",
        )

    return replace(
        result,
        classification="coverage_gap",
        verdict="review",
        reason="工具和参考查询不一致，但无法仅由学校关联键、省份归一化或 limit 截断解释。",
    )


def run_audit_case(case: AuditCase, client: MysqlCliClient) -> AuditResult:
    try:
        tool_payload = call_retrieval_function(
            "major_school_list",
            {
                "major_text": case.major,
                "province_filter": case.province_filter,
                "school_level_filter": case.school_level_filter,
                "limit": case.limit,
            },
        )
    except Exception as exc:
        return classify_result(
            AuditResult(
                case=case,
                tool_status="process_error",
                tool_school_count=0,
                oracle_school_count=0,
                relation_counts={},
                missing_school_names=[],
                errors=[str(exc)],
                normalized_province_filter=normalize_province_filter(case.province_filter),
            )
        )

    tool_status = str(tool_payload.get("status") or "")
    data = tool_payload.get("data") if isinstance(tool_payload.get("data"), dict) else {}
    major = data.get("major") if isinstance(data.get("major"), dict) else {}
    tool_rows = data.get("schools") if isinstance(data.get("schools"), list) else []
    tool_school_names = _school_names(tool_rows)

    base_result = AuditResult(
        case=case,
        tool_status=tool_status,
        tool_school_count=len(tool_school_names),
        oracle_school_count=0,
        relation_counts={},
        missing_school_names=[],
        tool_school_names=tool_school_names,
        oracle_school_names=[],
        normalized_major=major,
        normalized_province_filter=normalize_province_filter(case.province_filter),
        warnings=list(tool_payload.get("warnings") or []),
        data_gaps=list(tool_payload.get("data_gaps") or []),
    )
    if not major or _is_invalid_limit(case.limit):
        return classify_result(base_result)

    oracle_rows = client.query(build_oracle_major_school_sql(major, case.province_filter, case.school_level_filter))
    relation_counts = _first_int_row(
        client.query(build_oracle_major_school_relation_sql(major, case.province_filter, case.school_level_filter))
    )
    oracle_school_names = _school_names(oracle_rows)
    missing_school_names = [name for name in oracle_school_names if name not in set(tool_school_names)][:10]

    return classify_result(
        replace(
            base_result,
            oracle_school_count=len(oracle_school_names),
            relation_counts=relation_counts,
            missing_school_names=missing_school_names,
            oracle_school_names=oracle_school_names,
        )
    )


def render_markdown_report(results: list[AuditResult]) -> str:
    summary = summarize_results(results)
    lines = [
        "# major_school_list 边界审计报告",
        "",
        f"- 用例总数：{summary['total']}",
        f"- 通过：{summary['by_verdict'].get('pass', 0)}",
        f"- 失败：{summary['by_verdict'].get('fail', 0)}",
        f"- 需要复核：{summary['by_verdict'].get('review', 0)}",
        "",
        "## 分类汇总",
        "",
    ]
    for classification, count in sorted(summary["by_classification"].items()):
        lines.append(f"- {_classification_label(classification)}：{count}")
    lines.extend(["", "## 逐项结果", ""])

    for result in results:
        case = result.case
        province = case.province_filter or "<none>"
        level = case.school_level_filter or "<none>"
        missing = ", ".join(result.missing_school_names[:10]) or "-"
        relation = ", ".join(f"{key}={value}" for key, value in sorted(result.relation_counts.items())) or "-"
        warnings = "；".join(result.warnings or []) or "-"
        data_gaps = "；".join(result.data_gaps or []) or "-"
        lines.extend(
            [
                f"### {case.case_id}",
                "",
                f"- 输入：major={case.major}, province_filter={province}, school_level_filter={level}, limit={case.limit}",
                f"- 判定：{_verdict_label(result.verdict)}",
                f"- 分类：{_classification_label(result.classification)}",
                f"- 原因：{result.reason}",
                f"- 工具结果：status={result.tool_status}, 学校数={result.tool_school_count}",
                f"- 参考查询：学校数={result.oracle_school_count}, 归一化省份={result.normalized_province_filter or '<none>'}",
                f"- 学校关联键分布：{relation}",
                f"- 漏召回学校样本：{missing}",
                f"- warnings：{warnings}",
                f"- data_gaps：{data_gaps}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def summarize_results(results: list[AuditResult]) -> dict[str, Any]:
    by_verdict: dict[str, int] = {}
    by_classification: dict[str, int] = {}
    for result in results:
        by_verdict[result.verdict] = by_verdict.get(result.verdict, 0) + 1
        by_classification[result.classification] = by_classification.get(result.classification, 0) + 1
    return {
        "total": len(results),
        "by_verdict": by_verdict,
        "by_classification": by_classification,
    }


def write_jsonl_report(path: Path, results: list[AuditResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(asdict(result), ensure_ascii=False, default=str) for result in results]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def load_cases(path: Path | None) -> list[AuditCase]:
    if path is None:
        path = DEFAULT_CASES_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_cases = payload.get("cases", payload) if isinstance(payload, dict) else payload
    cases = []
    for raw_case in raw_cases:
        cases.append(
            AuditCase(
                case_id=raw_case["case_id"],
                major=raw_case["major"],
                province_filter=raw_case.get("province_filter"),
                school_level_filter=raw_case.get("school_level_filter"),
                limit=raw_case.get("limit", 50),
                expected_status=raw_case.get("expected_status"),
                expected_warning_substrings=list(raw_case.get("expected_warning_substrings") or []),
                note=raw_case.get("note", ""),
            )
        )
    return cases


def _school_names(rows: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for row in rows:
        name = str(row.get("school_name") or "").strip()
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def _first_int_row(rows: list[dict[str, Any]]) -> dict[str, int]:
    if not rows:
        return {}
    result: dict[str, int] = {}
    for key, value in rows[0].items():
        try:
            result[key] = int(value or 0)
        except (TypeError, ValueError):
            result[key] = 0
    return result


def _missing_expected_warning(result: AuditResult) -> str:
    warnings = result.warnings or []
    for expected in result.case.expected_warning_substrings:
        if not any(expected in warning for warning in warnings):
            return expected
    return ""


def _is_invalid_limit(value: Any) -> bool:
    return not _is_positive_int_like(value)


def _is_positive_int_like(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value >= 1
    if isinstance(value, str):
        text = value.strip()
        return text.isdecimal() and int(text) >= 1
    return False


def _limit_as_int(value: Any) -> int:
    if not _is_positive_int_like(value):
        raise ValueError(f"invalid positive integer limit: {value!r}")
    return int(str(value).strip())


def _verdict_label(verdict: str) -> str:
    return {
        "pass": "通过",
        "fail": "失败",
        "review": "需要复核",
    }.get(verdict, verdict)


def _classification_label(classification: str) -> str:
    return {
        "pass": "pass（通过）",
        "key_mismatch": "key_mismatch（学校关联键漏召回）",
        "province_normalization_gap": "province_normalization_gap（省份归一化缺口）",
        "warning_propagation_gap": "warning_propagation_gap（warning 传播缺口）",
        "input_validation_gap": "input_validation_gap（输入校验缺口）",
        "status_mismatch": "status_mismatch（状态不符合预期）",
        "limit_truncated": "limit_truncated（limit 正常截断）",
        "coverage_gap": "coverage_gap（覆盖不一致待复核）",
        "process_error": "process_error（流程错误）",
    }.get(classification, classification)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit major_school_list against oracle SQL.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT / ".env")
    parser.add_argument("--jsonl-report", type=Path, default=DEFAULT_JSONL_REPORT)
    parser.add_argument("--markdown-report", type=Path, default=DEFAULT_MARKDOWN_REPORT)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any case is classified as fail.")
    args = parser.parse_args(argv)

    apply_env_file(args.env_file)
    client = MysqlCliClient(DbConfig.from_env())
    started = time.perf_counter()
    results = [run_audit_case(case, client) for case in load_cases(args.cases)]
    write_jsonl_report(args.jsonl_report, results)
    args.markdown_report.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_report.write_text(render_markdown_report(results), encoding="utf-8")

    summary = summarize_results(results)
    summary["duration_seconds"] = round(time.perf_counter() - started, 3)
    summary["jsonl_report"] = str(args.jsonl_report)
    summary["markdown_report"] = str(args.markdown_report)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.strict and summary["by_verdict"].get("fail", 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
