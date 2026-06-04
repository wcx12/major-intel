"""Independent local-database oracles for rank_to_school_match evaluation."""

from __future__ import annotations

from typing import Any

from major_intel.function_calls.retrieval_tools import PROVINCE_ID_BY_NAME
from major_intel.storage.local_retrieval_mvp import MysqlCliClient, sql_quote


SUBJECT_ALIASES = {
    "理科": ["物理"],
    "物理": ["理科"],
    "文科": ["历史"],
    "历史": ["文科"],
}


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() == "NULL":
        return None
    return int(float(text))


def normalize_digits(text: str) -> str:
    return str(text).replace(",", "").replace("，", "")


def province_id_for_input(province: Any) -> str | None:
    text = str(province or "").strip()
    if text.isdigit():
        return text
    text = (
        text.removesuffix("省")
        .removesuffix("市")
        .removesuffix("壮族自治区")
        .removesuffix("自治区")
        .removesuffix("回族自治区")
        .removesuffix("维吾尔自治区")
    )
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


def resolve_applicant_rank(client: MysqlCliClient, case: dict[str, Any]) -> tuple[int | None, dict[str, Any]]:
    provided_rank = as_int(case.get("rank"))
    if provided_rank is not None:
        return provided_rank, {"rank_source": "provided_rank", "issues": []}

    score = as_int(case.get("score"))
    province_id = province_id_for_input(case.get("province"))
    subjects = subject_candidates(case.get("subject_type"))
    issues: list[str] = []
    if score is None:
        return None, {"rank_source": "", "issues": ["missing_score_or_rank"]}
    if not province_id:
        return None, {"rank_source": "", "issues": ["unknown_province"]}
    if not subjects:
        return None, {"rank_source": "", "issues": ["missing_subject_type"]}

    subject_values = ", ".join(sql_quote(value) for value in subjects)
    year_clause = f"AND year = {int(case['year'])}" if case.get("year") else ""
    subject_order = f"CASE WHEN subject_type = {sql_quote(subjects[0])} THEN 0 ELSE 1 END"
    sql = f"""
SELECT province_id, year, subject_type, score, same_count, highest_rank, lowest_rank, batch_type
FROM edu_score_rank
WHERE deleted = 0
  AND province_id = {sql_quote(province_id)}
  AND subject_type IN ({subject_values})
  AND score = {score}
  {year_clause}
ORDER BY CAST(year AS UNSIGNED) DESC, {subject_order}, batch_type, highest_rank, lowest_rank
LIMIT 2
""".strip()
    rows = client.query(sql)
    if not rows:
        return None, {"rank_source": "score_to_rank", "issues": ["score_rank_not_found"], "score_rank_rows": []}

    row = rows[0]
    if len(rows) > 1:
        issues.append("score_rank_ambiguous")
    matched_subject = str(row.get("subject_type") or "")
    if matched_subject and matched_subject != str(case.get("subject_type") or ""):
        issues.append("score_rank_subject_alias")
    if not case.get("year"):
        issues.append("score_rank_latest_year")

    return as_int(row.get("lowest_rank")), {
        "rank_source": "score_to_rank",
        "issues": issues,
        "score_rank_rows": rows,
        "matched_subject_type": matched_subject,
        "matched_year": as_int(row.get("year")),
    }


def school_level_filter_clause(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    pattern = f"%{text}%"
    text_clause = f"u.level_name LIKE {sql_quote(pattern)}"
    if "双一流" in text or "一流" in text:
        return f"AND ({text_clause} OR u.is_dual_class = 1 OR u.dual_class = '1')"
    if "985" in text:
        return f"AND ({text_clause} OR u.is985 = 1)"
    if "211" in text:
        return f"AND ({text_clause} OR u.is211 = 1)"
    return f"AND {text_clause}"


def oracle_rows(client: MysqlCliClient, case: dict[str, Any], applicant_rank: int) -> list[dict[str, Any]]:
    clauses = [
        "(a.deleted IS NULL OR a.deleted = b'0')",
        f"a.province_name = {sql_quote(str(case.get('province') or ''))}",
        "a.stable_rank IS NOT NULL AND a.stable_rank > 0",
        (
            f"({int(applicant_rank)} <= a.chong_rank "
            f"OR {int(applicant_rank)} <= a.stable_rank "
            f"OR {int(applicant_rank)} <= a.bao_rank)"
        ),
    ]
    if case.get("year"):
        clauses.append(f"a.year <= {int(case['year'])}")
    if case.get("reference_years"):
        years = ", ".join(str(int(value)) for value in case["reference_years"])
        clauses.append(f"a.year IN ({years})")
    subject_type = str(case.get("subject_type") or "").strip()
    if subject_type:
        clauses.append(f"(a.subject_type = {sql_quote(subject_type)} OR a.subject_type IS NULL OR a.subject_type = '')")
    if case.get("preferred_regions"):
        regions = ", ".join(sql_quote(region) for region in case["preferred_regions"] if region)
        if regions:
            clauses.append(f"u.province_name IN ({regions})")

    subject_order = "1"
    if subject_type:
        subject_order = (
            f"CASE WHEN a.subject_type = {sql_quote(subject_type)} THEN 0 "
            "WHEN a.subject_type IS NULL OR a.subject_type = '' THEN 1 ELSE 2 END"
        )
    level_clause = school_level_filter_clause(case.get("school_level_filter"))
    sql = f"""
SELECT a.province_name, a.school_id, a.school_name,
       COALESCE(u.province_name, '') AS school_province_name,
       COALESCE(u.city_name, '') AS city_name,
       COALESCE(u.level_name, '') AS school_level_name,
       COALESCE(u.type_name, '') AS school_type_name,
       COALESCE(u.is985, 0) AS is985,
       COALESCE(u.is211, 0) AS is211,
       COALESCE(u.is_dual_class, 0) AS is_dual_class,
       a.subject_type, a.year, a.stable_score, a.stable_rank,
       a.chong_score, a.chong_rank, a.bao_score, a.bao_rank,
       a.batch, a.major_name AS representative_major_name,
       CASE
         WHEN a.major_code IS NULL OR a.major_code = '' THEN 'school_level'
         ELSE 'major_or_plan_row'
       END AS row_scope
FROM edu_school_admission_stats a
LEFT JOIN edu_university u ON u.code = CAST(a.school_id AS CHAR) AND u.name = a.school_name
WHERE {' AND '.join(clauses)}
{level_clause}
ORDER BY {subject_order}, a.year DESC, ABS(a.stable_rank - {int(applicant_rank)}), a.school_name
LIMIT {max(int(case.get('limit', 30)) * 8, 80)}
""".strip()
    return client.query(sql)


def bucket_for_row(row: dict[str, Any], applicant_rank: int) -> str | None:
    bao_rank = as_int(row.get("bao_rank"))
    stable_rank = as_int(row.get("stable_rank"))
    chong_rank = as_int(row.get("chong_rank"))
    if bao_rank is not None and applicant_rank <= bao_rank:
        return "safe"
    if stable_rank is not None and applicant_rank <= stable_rank:
        return "stable"
    if chong_rank is not None and applicant_rank <= chong_rank:
        return "rush"
    return None


def selected_oracle_rows(rows: list[dict[str, Any]], applicant_rank: int, limit: int) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {"rush": [], "stable": [], "safe": []}
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = str(row.get("school_id") or row.get("school_name") or "").strip()
        if not key or key in seen:
            continue
        bucket = bucket_for_row(row, applicant_rank)
        if not bucket:
            continue
        buckets[bucket].append(row)
        selected.append(row)
        seen.add(key)
        if len(selected) >= limit:
            break
    return buckets, selected
