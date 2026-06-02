"""Audit `school_major_list` against independent local-database oracle queries."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.local_retrieval_mvp import DbConfig, MysqlCliClient
from scripts.retrieval_function_registry import call_retrieval_function
from scripts.school_major_list_oracles import (
    build_oracle_category_field_coverage_sql,
    build_oracle_key_relation_sql,
    build_oracle_school_major_sql,
)


DEFAULT_JSONL_REPORT = PROJECT_ROOT / "reports" / "school_major_list_boundary_eval.jsonl"
DEFAULT_MARKDOWN_REPORT = PROJECT_ROOT / "reports" / "school_major_list_boundary_eval.md"
DEFAULT_CASES_PATH = PROJECT_ROOT / "tests" / "function_calls" / "school_major_list" / "boundary_cases.json"


@dataclass(frozen=True)
class AuditCase:
    case_id: str
    school: str
    major_category: str | None = None
    limit: int = 100
    expected_status: str | None = None
    note: str = ""


@dataclass(frozen=True)
class AuditResult:
    case: AuditCase
    tool_status: str
    tool_major_count: int
    oracle_major_count: int
    oracle_all_major_count: int
    relation_counts: dict[str, int]
    missing_major_names: list[str]
    tool_major_names: list[str] | None = None
    oracle_major_names: list[str] | None = None
    category_field_coverage: dict[str, int] | None = None
    normalized_school: dict[str, Any] | None = None
    warnings: list[str] | None = None
    data_gaps: list[str] | None = None
    errors: list[str] | None = None
    classification: str = "unclassified"
    verdict: str = "review"
    reason: str = ""


DEFAULT_CASES = [
    AuditCase("hdu_all", "杭州电子科技大学", limit=100, note="code-key baseline"),
    AuditCase("hdu_cs", "杭州电子科技大学", major_category="计算机", limit=50, note="known local data gap"),
    AuditCase("hdu_software", "杭州电子科技大学", major_category="软件工程", limit=20, note="department-major exact major"),
    AuditCase("hdu_digital_media", "杭州电子科技大学", major_category="数字媒体技术", limit=20, note="code-first catalog join"),
    AuditCase(
        "hdu_vocational_category_noise",
        "杭州电子科技大学",
        major_category="电子与信息大类",
        limit=20,
        expected_status="not_found",
        note="same-name vocational catalog row must not pull undergraduate major into vocational category",
    ),
    AuditCase("hdu_engineering", "杭州电子科技大学", major_category="工学", limit=50, note="broad category semantics"),
    AuditCase("hdu_electronic_info", "杭州电子科技大学", major_category="电子信息类", limit=50, note="catalog level3 category"),
    AuditCase("beijing_language_all", "北京语言大学", limit=100, note="code-key baseline"),
    AuditCase("beijing_language_cs", "北京语言大学", major_category="计算机", limit=50, note="same numeric id as another school's department source"),
    AuditCase("cqupt_all", "重庆邮电大学", limit=100, note="school_id-key mismatch candidate"),
    AuditCase("cqupt_cs", "重庆邮电大学", major_category="计算机", limit=50, note="category plus key mismatch"),
    AuditCase("cqupt_software", "重庆邮电大学", major_category="软件工程", limit=20, note="mixed-key exact major"),
    AuditCase("cqupt_electronics", "重庆邮电大学", major_category="电子信息类", limit=50, note="mixed-key catalog category"),
    AuditCase("nuaa_all", "南京航空航天大学", limit=100, note="mixed-key candidate"),
    AuditCase("nuaa_cs", "南京航空航天大学", major_category="计算机", limit=50, note="mixed-key category"),
    AuditCase("nuaa_aerospace", "南京航空航天大学", major_category="航空航天", limit=50, note="domain/category recall"),
    AuditCase("nankai_all", "南开大学", limit=100, note="mixed-key candidate"),
    AuditCase("nankai_cs", "南开大学", major_category="计算机", limit=50, note="department-domain category"),
    AuditCase("nankai_math", "南开大学", major_category="数学", limit=50, note="department-domain broad term"),
    AuditCase("cupl_cs", "中国政法大学", major_category="计算机", limit=50, note="category positive baseline"),
    AuditCase("cupl_law", "中国政法大学", major_category="法学", limit=50, note="category semantics check"),
    AuditCase("cupl_politics", "中国政法大学", major_category="政治学", limit=50, note="law school category"),
    AuditCase("uestc_cs", "电子科技大学", major_category="计算机", limit=50, note="internal id collides with CUPl code"),
    AuditCase("uestc_electronics", "电子科技大学", major_category="电子信息类", limit=50, note="domain-verified department source"),
    AuditCase("jlu_cs", "吉林大学", major_category="计算机", limit=50, note="internal id collides with BLCU code"),
    AuditCase("jlu_law", "吉林大学", major_category="法学", limit=50, note="domain-verified department source"),
    AuditCase("taizhou_cs", "台州学院", major_category="计算机", limit=50, note="internal id collides with HDU code"),
    AuditCase("taizhou_medical", "台州学院", major_category="临床医学", limit=50, note="domain-verified department exact major"),
    AuditCase("xinzhou_cs", "忻州师范学院", major_category="计算机", limit=50, note="code collides with HDU internal id"),
    AuditCase("nanda_alias", "南大", limit=20, expected_status="needs_clarification", note="ambiguous alias"),
    AuditCase("jiaoda_alias", "交大", limit=20, expected_status="needs_clarification", note="ambiguous alias"),
    AuditCase("huada_alias", "华大", limit=20, expected_status="needs_clarification", note="dangerous fuzzy alias"),
    AuditCase("random_school", "不存在大学测试样本999", limit=20, expected_status="not_found", note="not found school"),
    AuditCase("cupl_limit_1", "中国政法大学", limit=1, note="limit truncation"),
    AuditCase(
        "cupl_limit_0",
        "中国政法大学",
        limit=0,
        expected_status="needs_clarification",
        note="invalid limit should be rejected before SQL",
    ),
    AuditCase(
        "cupl_limit_negative",
        "中国政法大学",
        limit=-1,
        expected_status="needs_clarification",
        note="negative limit should be rejected before SQL",
    ),
]


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
        if result.case.limit < 1:
            return replace(
                result,
                classification="input_validation_gap",
                verdict="fail",
                reason="limit 小于 1 仍进入 SQL 层，未返回结构化参数校验结果。",
            )
        return replace(result, classification="process_error", verdict="fail", reason="；".join(errors))

    if expected_status and result.tool_status == expected_status:
        return replace(result, classification="pass", verdict="pass", reason=f"工具状态符合预期：{expected_status}。")

    if expected_status and result.tool_status != expected_status:
        return replace(
            result,
            classification="status_mismatch",
            verdict="fail",
            reason=f"工具状态不符合预期：期望 {expected_status}，实际 {result.tool_status}。",
        )

    if result.case.limit < 1 and result.tool_status == "needs_clarification":
        return replace(
            result,
            classification="pass",
            verdict="pass",
            reason="limit 小于 1 时已在工具入口返回结构化参数澄清，没有进入 SQL 层。",
        )

    if result.case.limit < 1:
        return replace(
            result,
            classification="input_validation_gap",
            verdict="fail",
            reason="limit 小于 1 时仍返回普通检索结果，未给出参数校验提示。",
        )

    expected_visible = min(result.oracle_major_count, result.case.limit)
    if result.oracle_major_count > result.case.limit and result.tool_major_count == expected_visible:
        return replace(
            result,
            classification="limit_truncated",
            verdict="pass",
            reason="工具按正数 limit 返回了指定条数；参考查询仍有更多记录。",
        )

    school_id_rows = result.relation_counts.get("matches_school_id", 0)
    if result.oracle_major_count > result.tool_major_count and school_id_rows > 0:
        return replace(
            result,
            classification="key_mismatch",
            verdict="fail",
            reason="参考查询通过 school_id/code 双键找到了更多记录，工具返回数量偏少。",
        )

    if result.oracle_major_count == 0 and result.tool_major_count == 0:
        return replace(result, classification="pass", verdict="pass", reason="工具和参考查询都未命中记录。")

    if result.oracle_major_count > 0 and result.tool_major_count == expected_visible:
        return replace(result, classification="pass", verdict="pass", reason="工具返回数量与参考查询一致。")

    if result.case.major_category and result.oracle_major_count == 0 and result.oracle_all_major_count > 0:
        return replace(
            result,
            classification="category_semantics_gap",
            verdict="review",
            reason="学校有开设专业记录，但 major_category 筛选无命中；当前分类字段可能不支持这个筛选词。",
        )

    return replace(
        result,
        classification="coverage_gap",
        verdict="review",
        reason="工具和参考查询不一致，但无法仅由学校关联键分布解释。",
    )


def run_audit_case(case: AuditCase, client: MysqlCliClient) -> AuditResult:
    try:
        tool_payload = call_retrieval_function(
            "school_major_list",
            {"school_text": case.school, "major_category": case.major_category, "limit": case.limit},
        )
    except Exception as exc:
        return AuditResult(
            case=case,
            tool_status="process_error",
            tool_major_count=0,
            oracle_major_count=0,
            oracle_all_major_count=0,
            relation_counts={},
            missing_major_names=[],
            errors=[str(exc)],
        )

    tool_status = str(tool_payload.get("status") or "")
    data = tool_payload.get("data") if isinstance(tool_payload.get("data"), dict) else {}
    school = data.get("school") if isinstance(data.get("school"), dict) else {}
    tool_rows = data.get("majors") if isinstance(data.get("majors"), list) else []
    tool_major_names = _major_names(tool_rows)

    if not school:
        return classify_result(
            AuditResult(
                case=case,
                tool_status=tool_status,
                tool_major_count=len(tool_rows),
                oracle_major_count=0,
                oracle_all_major_count=0,
                relation_counts={},
                missing_major_names=[],
                tool_major_names=tool_major_names,
                oracle_major_names=[],
                normalized_school={},
                warnings=list(tool_payload.get("warnings") or []),
                data_gaps=list(tool_payload.get("data_gaps") or []),
            )
        )

    oracle_rows = client.query(build_oracle_school_major_sql(school, case.major_category))
    oracle_all_rows = client.query(build_oracle_school_major_sql(school, None))
    relation_counts = _first_int_row(client.query(build_oracle_key_relation_sql(school)))
    category_coverage = _first_int_row(client.query(build_oracle_category_field_coverage_sql(school)))
    oracle_major_names = _major_names(oracle_rows)
    missing_major_names = [name for name in oracle_major_names if name not in set(tool_major_names)][:10]

    return classify_result(
        AuditResult(
            case=case,
            tool_status=tool_status,
            tool_major_count=len(tool_rows),
            oracle_major_count=len(oracle_rows),
            oracle_all_major_count=len(oracle_all_rows),
            relation_counts=relation_counts,
            missing_major_names=missing_major_names,
            tool_major_names=tool_major_names,
            oracle_major_names=oracle_major_names,
            category_field_coverage=category_coverage,
            normalized_school=school,
            warnings=list(tool_payload.get("warnings") or []),
            data_gaps=list(tool_payload.get("data_gaps") or []),
        )
    )


def render_markdown_report(results: list[AuditResult]) -> str:
    summary = summarize_results(results)
    lines = [
        "# school_major_list 边界审计报告",
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
        category = case.major_category or "<none>"
        missing = ", ".join(result.missing_major_names[:10]) or "-"
        relation = ", ".join(f"{key}={value}" for key, value in sorted(result.relation_counts.items())) or "-"
        lines.extend(
            [
                f"### {case.case_id}",
                "",
                f"- 输入：school={case.school}, major_category={category}, limit={case.limit}",
                f"- 判定：{_verdict_label(result.verdict)}",
                f"- 分类：{_classification_label(result.classification)}",
                f"- 原因：{result.reason}",
                f"- 工具结果：status={result.tool_status}, 专业数={result.tool_major_count}",
                f"- 参考查询：筛选后专业数={result.oracle_major_count}, 全部专业数={result.oracle_all_major_count}",
                f"- 学校关联键分布：{relation}",
                f"- 漏召回专业样本：{missing}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _verdict_label(verdict: str) -> str:
    return {
        "pass": "通过",
        "fail": "失败",
        "review": "需要复核",
    }.get(verdict, verdict)


def _classification_label(classification: str) -> str:
    labels = {
        "pass": "pass（通过）",
        "key_mismatch": "key_mismatch（学校关联键不一致）",
        "category_semantics_gap": "category_semantics_gap（分类字段语义缺口）",
        "status_mismatch": "status_mismatch（状态不符合预期）",
        "limit_truncated": "limit_truncated（limit 正常截断）",
        "input_validation_gap": "input_validation_gap（输入校验缺口）",
        "process_error": "process_error（进程或 SQL 错误）",
        "coverage_gap": "coverage_gap（覆盖差异待复核）",
    }
    return labels.get(classification, classification)


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
        return DEFAULT_CASES
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_cases = payload.get("cases", payload) if isinstance(payload, dict) else payload
    cases = []
    for raw_case in raw_cases:
        cases.append(
            AuditCase(
                case_id=raw_case["case_id"],
                school=raw_case["school"],
                major_category=raw_case.get("major_category"),
                limit=int(raw_case.get("limit", 100)),
                expected_status=raw_case.get("expected_status"),
                note=raw_case.get("note", ""),
            )
        )
    return cases


def _major_names(rows: list[dict[str, Any]]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for row in rows:
        name = str(row.get("major_name") or "").strip()
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


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit school_major_list against oracle SQL.")
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
