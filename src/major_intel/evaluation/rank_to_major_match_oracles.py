"""Independent local-database oracles for rank_to_major_match evaluation."""

from __future__ import annotations

from typing import Any

from major_intel.evaluation.rank_to_school_match_oracles import as_int, province_id_for_input, school_level_filter_clause, subject_candidates
from major_intel.function_calls.retrieval_tools import _major_row_exact, _rank_major_rows
from major_intel.storage.local_retrieval_mvp import MysqlCliClient, normalize_major_query, resolve_major_sql, sql_quote


BUCKETS = ("rush", "stable", "safe")
SELECTED_SUBJECT_NAMES = {"物理", "化学", "生物", "政治", "思想政治", "历史", "地理", "技术"}


def resolve_major_candidate(client: MysqlCliClient, major_text: Any) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    text = str(major_text or "").strip()
    if not text:
        return None, {"issues": ["missing_major_text"], "candidate_count": 0, "candidates": []}
    normalized_text = normalize_major_query(text)
    rows = _rank_major_rows(client.query(resolve_major_sql(text, limit=20)), normalized_text)
    issues: list[str] = []
    if not rows:
        return None, {"issues": ["major_not_found"], "candidate_count": 0, "candidates": []}
    if len(rows) > 1 and not _major_row_exact(rows[0], normalized_text):
        issues.append("major_ambiguous")
        return None, {"issues": issues, "candidate_count": len(rows), "candidates": rows[:5]}
    if len(rows) > 1:
        issues.append("major_cross_level_candidates")
    return rows[0], {"issues": issues, "candidate_count": len(rows), "candidates": rows[:5]}


def resolve_rank_and_subject(client: MysqlCliClient, case: dict[str, Any]) -> tuple[int | None, str | None, dict[str, Any]]:
    provided_rank = as_int(case.get("rank"))
    province_id = province_id_for_input(case.get("province"))
    if not province_id:
        return provided_rank, str(case.get("subject_type") or "").strip() or None, {"issues": ["unknown_province"]}

    subject_meta = resolve_rank_subject(client, province_id, case.get("subject_type"), case.get("year"))
    issues = list(subject_meta["issues"])
    rank_subject_type = subject_meta.get("rank_subject_type") or None
    if provided_rank is not None:
        if not rank_subject_type and case.get("subject_type"):
            rank_subject_type = str(case.get("subject_type") or "").strip()
        if not rank_subject_type:
            issues.append("missing_subject_type")
        return provided_rank, rank_subject_type, {**subject_meta, "issues": sorted(set(issues)), "rank_source": "provided_rank"}

    score = as_int(case.get("score"))
    if score is None:
        return None, rank_subject_type, {**subject_meta, "issues": sorted(set(issues + ["missing_score_or_rank"])), "rank_source": ""}
    if not rank_subject_type:
        return None, rank_subject_type, {**subject_meta, "issues": sorted(set(issues + ["missing_subject_type"])), "rank_source": "score_to_rank"}

    rows = score_rank_rows(client, province_id, rank_subject_type, score, case.get("year"))
    if not rows:
        return None, rank_subject_type, {**subject_meta, "issues": sorted(set(issues + ["score_rank_not_found"])), "rank_source": "score_to_rank"}
    if len(rows) > 1:
        issues.append("score_rank_ambiguous")
    row = rows[0]
    matched_subject = str(row.get("subject_type") or "")
    if matched_subject and matched_subject != str(case.get("subject_type") or "").strip():
        issues.append("score_rank_subject_alias")
    if not case.get("year"):
        issues.append("score_rank_latest_year")
    return as_int(row.get("lowest_rank")), matched_subject or rank_subject_type, {
        **subject_meta,
        "issues": sorted(set(issues)),
        "rank_source": "score_to_rank",
        "score_rank_rows": rows,
        "matched_subject_type": matched_subject,
        "matched_year": as_int(row.get("year")),
    }


def resolve_rank_subject(client: MysqlCliClient, province_id: str, subject_type: Any, year: Any) -> dict[str, Any]:
    rows = client.query(score_rank_subject_mode_sql(province_id, year))
    available = distinct_texts(row.get("subject_type") for row in rows)
    input_subject = str(subject_type or "").strip()
    mode = score_rank_subject_mode(available)
    issues: list[str] = []
    selected_subjects: list[str] = []
    rank_subject_type = ""

    if mode == "3+3":
        rank_subject_type = "综合"
        if input_subject and input_subject != "综合" and input_subject in SELECTED_SUBJECT_NAMES:
            selected_subjects = [input_subject]
            issues.append("selected_subject_mapped_to_comprehensive")
        elif input_subject and input_subject != "综合":
            issues.append("subject_mapped_to_comprehensive")
        elif not input_subject:
            issues.append("subject_defaulted_to_comprehensive")
    elif mode in {"3+1+2", "traditional"}:
        if input_subject:
            candidates = subject_candidates(input_subject)
            matching = [candidate for candidate in candidates if candidate in available]
            if matching:
                rank_subject_type = matching[0]
                if rank_subject_type != input_subject:
                    issues.append("subject_alias")
            else:
                issues.append("subject_type_not_available")
        else:
            issues.append("missing_subject_type")
    else:
        rank_subject_type = input_subject
        if not available:
            issues.append("subject_mode_unknown")
        if not input_subject:
            issues.append("missing_subject_type")

    return {
        "subject_mode": mode,
        "available_subject_types": available,
        "rank_subject_type": rank_subject_type,
        "selected_subjects": selected_subjects,
        "issues": issues,
    }


def score_rank_rows(client: MysqlCliClient, province_id: str, subject_type: str, score: int, year: Any) -> list[dict[str, Any]]:
    year_clause = f"AND year = {int(year)}" if year else ""
    sql = f"""
SELECT province_id, year, subject_type, score, same_count, highest_rank, lowest_rank, batch_type
FROM edu_score_rank
WHERE deleted = 0
  AND province_id = {sql_quote(province_id)}
  AND subject_type = {sql_quote(subject_type)}
  AND score = {int(score)}
  {year_clause}
ORDER BY CAST(year AS UNSIGNED) DESC, batch_type, highest_rank, lowest_rank
LIMIT 2
""".strip()
    return client.query(sql)


def score_rank_subject_mode_sql(province_id: str, year: Any) -> str:
    if year:
        year_clause = f"AND year = {int(year)}"
    else:
        year_clause = f"""
AND CAST(year AS UNSIGNED) = (
  SELECT MAX(CAST(year AS UNSIGNED))
  FROM edu_score_rank
  WHERE deleted = 0 AND province_id = {sql_quote(province_id)}
)
""".strip()
    return f"""
SELECT year, subject_type
FROM edu_score_rank
WHERE deleted = 0
  AND province_id = {sql_quote(province_id)}
  AND subject_type IS NOT NULL AND subject_type <> ''
  {year_clause}
GROUP BY year, subject_type
ORDER BY CAST(year AS UNSIGNED) DESC, subject_type
LIMIT 20
""".strip()


def score_rank_subject_mode(available_subject_types: list[str]) -> str:
    subject_set = set(available_subject_types)
    if subject_set == {"综合"}:
        return "3+3"
    if {"物理", "历史"} & subject_set:
        return "3+1+2"
    if {"理科", "文科"} & subject_set:
        return "traditional"
    return "unknown"


def oracle_rows(
    client: MysqlCliClient,
    case: dict[str, Any],
    major: dict[str, Any],
    applicant_rank: int,
    rank_subject_type: str | None,
) -> list[dict[str, Any]]:
    major_filter = major_admission_filter_clause(major, str(case.get("major_text") or ""))
    clauses = [
        "(a.deleted IS NULL OR a.deleted = b'0')",
        f"a.province_name = {sql_quote(str(case.get('province') or ''))}",
        "a.stable_rank IS NOT NULL AND a.stable_rank > 0",
        "(a.major_name IS NOT NULL AND a.major_name <> '')",
        major_filter,
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
    if rank_subject_type:
        clauses.append(f"(a.subject_type = {sql_quote(rank_subject_type)} OR a.subject_type IS NULL OR a.subject_type = '')")
    if case.get("preferred_regions"):
        regions = ", ".join(sql_quote(region) for region in case["preferred_regions"] if region)
        if regions:
            clauses.append(f"u.province_name IN ({regions})")

    subject_order = "1"
    if rank_subject_type:
        subject_order = (
            f"CASE WHEN a.subject_type = {sql_quote(rank_subject_type)} THEN 0 "
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
       a.major_code, a.major_name, a.subject_type, a.year,
       a.stable_score, a.stable_rank, a.chong_score, a.chong_rank,
       a.bao_score, a.bao_rank, a.batch, a.subject_requirement,
       a.plan_count, a.admission_count, a.remark
FROM edu_school_admission_stats a
LEFT JOIN edu_university u ON u.code = CAST(a.school_id AS CHAR) AND u.name = a.school_name
WHERE {' AND '.join(clauses)}
{level_clause}
ORDER BY {subject_order}, a.year DESC, ABS(a.stable_rank - {int(applicant_rank)}), a.school_name, a.major_name
LIMIT {max(int(case.get('limit', 30)) * 10, 100)}
""".strip()
    return client.query(sql)


def major_admission_filter_clause(major: dict[str, Any], raw_major_text: str) -> str:
    filters: list[str] = []
    major_code = text_value(major.get("code")) or text_value(major.get("special_id"))
    major_name = text_value(major.get("special_name"))
    raw_text = text_value(raw_major_text)
    if major_code:
        filters.append(f"a.major_code = {sql_quote(major_code)}")
    if major_name:
        filters.append(f"a.major_name = {sql_quote(major_name)}")
        filters.append(f"a.major_name LIKE {sql_quote(f'%{major_name}%')}")
    if raw_like_allowed(raw_text, major_name):
        filters.append(f"a.major_name LIKE {sql_quote(f'%{raw_text}%')}")
    return "(" + " OR ".join(filters or ["1 = 0"]) + ")"


def raw_like_allowed(raw_text: str, canonical_name: str) -> bool:
    normalized_raw = "".join(raw_text.split()).lower()
    normalized_canonical = "".join(canonical_name.split()).lower()
    return len(normalized_raw) >= 3 and normalized_raw not in {normalized_canonical, ""}


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


def selected_oracle_rows(
    rows: list[dict[str, Any]],
    applicant_rank: int,
    limit: int,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {"rush": [], "stable": [], "safe": []}
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = opportunity_key(row)
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


def opportunity_key(row: dict[str, Any]) -> str:
    school_key = text_value(row.get("school_id")) or text_value(row.get("school_name"))
    major_key = text_value(row.get("major_code")) or text_value(row.get("major_name"))
    batch_key = text_value(row.get("batch"))
    if not school_key or not major_key:
        return ""
    return "|".join([school_key, major_key, batch_key])


def major_row_label(row: dict[str, Any]) -> str:
    return "|".join(
        [
            text_value(row.get("school_name")),
            text_value(row.get("major_name")),
            text_value(row.get("batch")) or "未标批次",
        ]
    )


def distinct_texts(values: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = text_value(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def text_value(value: Any) -> str:
    return str(value or "").strip()
