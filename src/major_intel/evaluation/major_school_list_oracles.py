"""Reference SQL helpers for auditing major_school_list.

These helpers are intentionally separate from `RetrievalTools.major_school_list`.
The audit needs an independent reference query so it can detect missed schools
caused by mixed `edu_school_major.school_id` conventions or input normalization
gaps.
"""

from __future__ import annotations

from typing import Any

from major_intel.storage.local_retrieval_mvp import sql_quote


def build_oracle_major_school_sql(
    major: dict[str, Any],
    province_filter: str | None = None,
    school_level_filter: str | None = None,
    *,
    limit: int | None = None,
) -> str:
    """Return reference SQL for schools recorded as offering one major.

    `edu_school_major.school_id` may store either `edu_university.code` or
    `edu_university.school_id`.  The oracle uses both keys while keeping exact
    school-name matching, because otherwise same-number rows from another school
    can leak into the result.
    """

    province_clause = _province_clause(province_filter)
    level_clause = _school_level_clause(school_level_filter)
    limit_clause = "" if limit is None else f"\nLIMIT {int(limit)}"
    return f"""
SELECT DISTINCT
       sm.school_id,
       sm.school_name,
       u.province_name,
       u.city_name,
       u.is211,
       u.is985,
       u.is_dual_class,
       sm.major_code,
       sm.major_name,
       sm.nation_first_class,
       sm.xueke_rank_score,
       sm.ruanke_level,
       u.level_name AS school_level_name,
       u.type_name AS school_type_name,
       sm.level_name AS major_level_name
FROM edu_school_major sm
LEFT JOIN edu_university u
  ON (
      u.code = CAST(sm.school_id AS CHAR)
      OR CAST(u.school_id AS CHAR) = CAST(sm.school_id AS CHAR)
  )
  AND u.name = sm.school_name
WHERE (sm.deleted IS NULL OR sm.deleted = 0)
  AND {_major_match_clause(major)}
  {province_clause}
  {level_clause}
ORDER BY COALESCE(u.is985, 0) DESC,
         COALESCE(u.is211, 0) DESC,
         COALESCE(u.is_dual_class, 0) DESC,
         sm.school_name{limit_clause}
""".strip()


def build_oracle_major_school_relation_sql(
    major: dict[str, Any],
    province_filter: str | None = None,
    school_level_filter: str | None = None,
) -> str:
    """Count which school key convention matching major-school rows use."""

    province_clause = _province_clause(province_filter)
    level_clause = _school_level_clause(school_level_filter)
    return f"""
SELECT
  SUM(CASE WHEN u.code = CAST(sm.school_id AS CHAR) THEN 1 ELSE 0 END) AS matches_code,
  SUM(CASE WHEN CAST(u.school_id AS CHAR) = CAST(sm.school_id AS CHAR) THEN 1 ELSE 0 END) AS matches_school_id,
  SUM(
    CASE
      WHEN u.name IS NULL THEN 1
      WHEN u.code <> CAST(sm.school_id AS CHAR)
       AND CAST(u.school_id AS CHAR) <> CAST(sm.school_id AS CHAR) THEN 1
      ELSE 0
    END
  ) AS other
FROM edu_school_major sm
LEFT JOIN edu_university u
  ON (
      u.code = CAST(sm.school_id AS CHAR)
      OR CAST(u.school_id AS CHAR) = CAST(sm.school_id AS CHAR)
  )
  AND u.name = sm.school_name
WHERE (sm.deleted IS NULL OR sm.deleted = 0)
  AND {_major_match_clause(major)}
  {province_clause}
  {level_clause}
""".strip()


def normalize_province_filter(province_filter: str | None) -> str | None:
    """Normalize common province suffixes for oracle comparisons."""

    text = str(province_filter or "").strip()
    if not text:
        return None
    direct = {
        "北京市": "北京",
        "上海市": "上海",
        "天津市": "天津",
        "重庆市": "重庆",
        "广西壮族自治区": "广西",
        "宁夏回族自治区": "宁夏",
        "新疆维吾尔自治区": "新疆",
        "内蒙古自治区": "内蒙古",
        "西藏自治区": "西藏",
    }
    if text in direct:
        return direct[text]
    for suffix in ("省", "市"):
        if text.endswith(suffix) and len(text) > len(suffix):
            return text[: -len(suffix)]
    return text


def _province_clause(province_filter: str | None) -> str:
    province = normalize_province_filter(province_filter)
    if not province:
        return ""
    return f"AND u.province_name = {sql_quote(province)}"


def _school_level_clause(school_level_filter: str | None) -> str:
    if not school_level_filter:
        return ""
    pattern = f"%{school_level_filter}%"
    text_clause = f"u.level_name LIKE {sql_quote(pattern)}"
    if "双一流" in school_level_filter or "一流" in school_level_filter:
        return f"AND ({text_clause} OR u.is_dual_class = 1 OR u.dual_class = '1')"
    if "985" in school_level_filter:
        return f"AND ({text_clause} OR u.is985 = 1)"
    if "211" in school_level_filter:
        return f"AND ({text_clause} OR u.is211 = 1)"
    return f"AND {text_clause}"


def _major_match_clause(major: dict[str, Any]) -> str:
    code = str(major.get("code") or major.get("special_id") or "").strip()
    name = str(major.get("special_name") or major.get("major_name") or "").strip()
    clauses = []
    if code:
        clauses.append(f"sm.major_code = {sql_quote(code)}")
    if name:
        clauses.append(f"sm.major_name = {sql_quote(name)}")
    return "(" + " OR ".join(clauses or ["1 = 0"]) + ")"
