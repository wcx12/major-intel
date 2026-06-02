"""Reference SQL helpers for auditing school_major_list.

These helpers are intentionally separate from `RetrievalTools.school_major_list`.
The audit needs an independent reference query so it can detect when the tool's
current SQL misses rows because of mixed school key conventions.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from scripts.local_retrieval_mvp import sql_quote


def build_oracle_school_major_sql(
    school: dict[str, Any],
    major_category: str | None = None,
    *,
    limit: int | None = None,
) -> str:
    """Return reference SQL for majors recorded under a selected school.

    `edu_school_major.school_id` is not consistent in the local database: some
    rows store `edu_university.code`, while others store `edu_university.school_id`.
    The oracle uses both keys and exact school name matching as the reference
    recall target for the audit.
    """

    key_values = _school_key_values(school)
    key_clause = ", ".join(sql_quote(value) for value in key_values) or "''"
    category_clause = _major_category_clause(major_category)
    department_category_clause = _department_major_category_clause(major_category)
    internal_school_id = sql_quote(school.get("school_id"))
    department_domain_clause = _department_domain_clause(school, "d")
    limit_clause = "" if limit is None else f"\nLIMIT {int(limit)}"
    return f"""
SELECT CONVERT(sm.major_code USING utf8mb4) COLLATE utf8mb4_unicode_ci AS major_code,
       CONVERT(sm.major_name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS major_name,
       CONVERT(sm.level_name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS level_name,
       CONVERT(sm.limit_year USING utf8mb4) COLLATE utf8mb4_unicode_ci AS limit_year,
       sm.nation_first_class,
       CONVERT(sm.xueke_rank_score USING utf8mb4) COLLATE utf8mb4_unicode_ci AS xueke_rank_score,
       CONVERT(sm.ruanke_level USING utf8mb4) COLLATE utf8mb4_unicode_ci AS ruanke_level,
       CONVERT(sm.menlei_name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS menlei_name,
       CONVERT(sm.xueke_name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS xueke_name,
       CONVERT(sm.level3_name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS level3_name,
       CONVERT(sm.school_id USING utf8mb4) COLLATE utf8mb4_unicode_ci AS school_major_school_id,
       CAST('edu_school_major' AS CHAR) COLLATE utf8mb4_unicode_ci AS record_source
FROM edu_school_major sm
WHERE (sm.deleted IS NULL OR sm.deleted = 0)
  AND sm.school_name = {sql_quote(school.get('name'))}
  AND sm.school_id IN ({key_clause})
  {category_clause}
  AND NOT EXISTS (
      SELECT 1
      FROM edu_university_department d
      WHERE (d.deleted IS NULL OR d.deleted = b'0')
        AND d.school_id = {internal_school_id}
        AND {department_domain_clause}
  )
UNION ALL
SELECT CONVERT(dm.major_code USING utf8mb4) COLLATE utf8mb4_unicode_ci AS major_code,
       CONVERT(dm.major_name USING utf8mb4) COLLATE utf8mb4_unicode_ci AS major_name,
       MAX(CONVERT(dm.education_level USING utf8mb4) COLLATE utf8mb4_unicode_ci) AS level_name,
       MAX(CONVERT(m.limit_year USING utf8mb4) COLLATE utf8mb4_unicode_ci) AS limit_year,
       MAX(dm.is_nation_first_class) AS nation_first_class,
       MAX(CONVERT(dm.subject_eval_level USING utf8mb4) COLLATE utf8mb4_unicode_ci) AS xueke_rank_score,
       CAST(NULL AS CHAR) COLLATE utf8mb4_unicode_ci AS ruanke_level,
       MAX(CONVERT(m.level2_name USING utf8mb4) COLLATE utf8mb4_unicode_ci) AS menlei_name,
       CAST(NULL AS CHAR) COLLATE utf8mb4_unicode_ci AS xueke_name,
       MAX(CONVERT(m.level3_name USING utf8mb4) COLLATE utf8mb4_unicode_ci) AS level3_name,
       CONVERT(dm.school_id USING utf8mb4) COLLATE utf8mb4_unicode_ci AS school_major_school_id,
       CAST('edu_university_department_major' AS CHAR) COLLATE utf8mb4_unicode_ci AS record_source
FROM edu_university_department_major dm
JOIN edu_university_department d ON d.id = dm.dept_id
LEFT JOIN edu_major m
  ON (m.deleted IS NULL OR m.deleted = 0 OR m.deleted = b'0')
  AND (
      REPLACE(REPLACE(CONVERT(m.code USING utf8mb4) COLLATE utf8mb4_unicode_ci, 'K', ''), 'T', '') =
      REPLACE(REPLACE(CONVERT(dm.major_code USING utf8mb4) COLLATE utf8mb4_unicode_ci, 'K', ''), 'T', '')
      OR (
          (dm.major_code IS NULL OR dm.major_code = '')
          AND CONVERT(m.special_name USING utf8mb4) COLLATE utf8mb4_unicode_ci = CONVERT(dm.major_name USING utf8mb4) COLLATE utf8mb4_unicode_ci
      )
  )
WHERE (dm.deleted IS NULL OR dm.deleted = b'0')
  AND (d.deleted IS NULL OR d.deleted = b'0')
  AND d.school_id = {internal_school_id}
  AND CONVERT(dm.school_id USING utf8mb4) COLLATE utf8mb4_unicode_ci = CONVERT(d.school_id USING utf8mb4) COLLATE utf8mb4_unicode_ci
  AND dm.major_name IS NOT NULL
  AND dm.major_name <> ''
  AND {department_domain_clause}
  {department_category_clause}
GROUP BY dm.major_code, dm.major_name, dm.school_id
ORDER BY major_code, major_name{limit_clause}
""".strip()


def build_oracle_key_relation_sql(school: dict[str, Any]) -> str:
    """Count which school key convention `edu_school_major` uses for one school."""

    code = sql_quote(school.get("code"))
    school_id = sql_quote(school.get("school_id"))
    return f"""
SELECT
  SUM(sm.school_id = {code}) AS matches_code,
  SUM(sm.school_id = {school_id}) AS matches_school_id,
  SUM(sm.school_id <> {code} AND sm.school_id <> {school_id}) AS other
FROM edu_school_major sm
WHERE (sm.deleted IS NULL OR sm.deleted = 0)
  AND sm.school_name = {sql_quote(school.get('name'))}
""".strip()


def build_oracle_category_field_coverage_sql(school: dict[str, Any]) -> str:
    """Count category-bearing fields for diagnosing category filter semantics."""

    return f"""
SELECT
  COUNT(*) AS total,
  SUM(sm.menlei_name IS NOT NULL AND sm.menlei_name <> '') AS menlei_nonempty,
  SUM(sm.xueke_name IS NOT NULL AND sm.xueke_name <> '') AS xueke_nonempty,
  SUM(sm.level3_name IS NOT NULL AND sm.level3_name <> '') AS level3_nonempty
FROM edu_school_major sm
WHERE (sm.deleted IS NULL OR sm.deleted = 0)
  AND sm.school_name = {sql_quote(school.get('name'))}
""".strip()


def _school_key_values(school: dict[str, Any]) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for key in ("code", "school_id"):
        value = str(school.get(key) or "").strip()
        if value and value not in seen:
            seen.add(value)
            values.append(value)
    return values


def _major_category_clause(major_category: str | None) -> str:
    if not major_category:
        return ""
    like = sql_quote(f"%{major_category}%")
    return f"""
AND (
    sm.menlei_name LIKE {like}
    OR sm.xueke_name LIKE {like}
    OR sm.level3_name LIKE {like}
    OR sm.major_name LIKE {like}
    OR EXISTS (
        SELECT 1
        FROM edu_major m
        WHERE (m.deleted IS NULL OR m.deleted = 0 OR m.deleted = b'0')
          AND (
              REPLACE(REPLACE(CONVERT(m.code USING utf8mb4) COLLATE utf8mb4_unicode_ci, 'K', ''), 'T', '') =
              REPLACE(REPLACE(CONVERT(sm.major_code USING utf8mb4) COLLATE utf8mb4_unicode_ci, 'K', ''), 'T', '')
              OR (
                  (sm.major_code IS NULL OR sm.major_code = '')
                  AND CONVERT(m.special_name USING utf8mb4) COLLATE utf8mb4_unicode_ci = CONVERT(sm.major_name USING utf8mb4) COLLATE utf8mb4_unicode_ci
              )
          )
          AND (
              m.level2_name LIKE {like}
              OR m.level3_name LIKE {like}
              OR m.special_name LIKE {like}
          )
    )
)
""".strip()


def _department_major_category_clause(major_category: str | None) -> str:
    if not major_category:
        return ""
    like = sql_quote(f"%{major_category}%")
    return f"""
AND (
    dm.major_name LIKE {like}
    OR m.level2_name LIKE {like}
    OR m.level3_name LIKE {like}
    OR m.special_name LIKE {like}
)
""".strip()


def _department_domain_clause(school: dict[str, Any], alias: str) -> str:
    domains = _school_domain_candidates(school)
    if not domains:
        return "1 = 0"
    return "(" + " OR ".join(f"{alias}.website_url LIKE {sql_quote(f'%{domain}%')}" for domain in domains) + ")"


def _school_domain_candidates(school: dict[str, Any]) -> list[str]:
    domains: list[str] = []
    seen: set[str] = set()
    for key in ("school_site", "site"):
        host = _hostname_from_url(school.get(key))
        if not host:
            continue
        candidates = [host]
        parts = host.split(".")
        if host.endswith(".edu.cn") and len(parts) >= 3:
            candidates.append(".".join(parts[-3:]))
        elif len(parts) >= 2:
            candidates.append(".".join(parts[-2:]))
        for candidate in candidates:
            if candidate and candidate not in seen:
                seen.add(candidate)
                domains.append(candidate)
    return domains


def _hostname_from_url(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    parsed = urlparse(text if "://" in text else f"https://{text}")
    host = parsed.hostname or ""
    if host.startswith("www."):
        host = host[4:]
    return host
