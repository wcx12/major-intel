"""Function-call style retrieval tools for Major Intel.

The future agent should not know table names, join keys, or evidence levels.
This module provides a stable tool layer: each public method accepts a small set
of slots, queries local MySQL through a client, and returns the same JSON-like
envelope with data, scope notes, warnings, missing slots, and source tables.

The code is intentionally verbose in comments because the dangerous bugs in
this product are not syntax bugs.  They are scope bugs: treating a school-level
employment rate as a school-major fact, treating a recruitment sample as a
graduate outcome, or guessing a province when score-to-rank conversion needs
an exact province and subject type.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Direct CLI execution (`python scripts/retrieval_tools.py ...`) makes Python
# treat `scripts/` as the import root.  The function-call tools import shared
# helpers through the project package path (`scripts.local_retrieval_mvp`), so
# we explicitly add the repository root before those imports.  This keeps cron,
# agent, and manual CLI entrypoints aligned with the unit-test import mode.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.local_retrieval_mvp import (
    DbConfig,
    MysqlCliClient,
    build_dual_class_sql,
    build_latest_employment_sql,
    build_school_major_sql,
    build_subject_eval_sql,
    resolve_major_sql,
    resolve_school_sql,
    sql_quote,
)


PROVINCE_ID_BY_NAME = {
    # The score-rank table uses numeric province IDs.  We keep a small explicit
    # mapping here so tools can accept natural province names while still
    # producing deterministic SQL.  Numeric province strings are also accepted.
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


SCHOOL_MAJOR_PROFILE_GAPS = [
    "校专业级工作地域分布",
    "校专业级薪资分布",
    "校专业级Top对口公司",
    "考公岗位映射",
    "转专业政策",
    "专业组真实分流比例/冷门专业比例",
    "学校官网专业介绍证据链",
]


def tool_result(
    tool_name: str,
    status: str,
    input_data: dict[str, Any],
    *,
    normalized_slots: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    scope_notes: list[str] | None = None,
    data_gaps: list[str] | None = None,
    needs_clarification: list[str] | None = None,
    source_tables: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Build the common function-call envelope used by every retrieval tool."""

    return {
        "tool_name": tool_name,
        "status": status,
        "input": input_data,
        "normalized_slots": normalized_slots or {},
        "data": data or {},
        "scope_notes": scope_notes or [],
        "data_gaps": data_gaps or [],
        "needs_clarification": needs_clarification or [],
        "source_tables": source_tables or [],
        "warnings": warnings or [],
    }


def _merge_source_tables(*table_groups: list[str] | tuple[str, ...]) -> list[str]:
    """Merge source table lists while preserving their first-seen order.

    Many higher-level tools first normalize a school or major through another
    lookup tool and then run their own SQL.  Returning the merged table list
    keeps the evidence trail honest: if a major nickname was resolved through
    `entity_aliases`, the final tool response should still disclose that.
    """

    merged: list[str] = []
    seen: set[str] = set()
    for table_group in table_groups:
        for table in table_group:
            if table not in seen:
                seen.add(table)
                merged.append(table)
    return merged


class RetrievalTools:
    """Collection of local retrieval functions callable by a future agent.

    The class depends only on a `query(sql) -> list[dict]` client.  In production
    this is the MySQL CLI client from `local_retrieval_mvp.py`; in tests it can
    be a tiny fake.  That boundary keeps SQL generation and result normalization
    testable without requiring a live database for every unit test.
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    def school_lookup(self, school_text: str, limit: int = 5) -> dict[str, Any]:
        """Resolve a school name/code to canonical school rows."""

        missing = _missing_slots({"school_text": school_text})
        if missing:
            return _needs("school_lookup", {"school_text": school_text}, missing)

        rows = self.client.query(resolve_school_sql(school_text, limit=limit))
        if not rows:
            return tool_result(
                "school_lookup",
                "not_found",
                {"school_text": school_text, "limit": limit},
                data={"selected_school": {}, "candidates": []},
                source_tables=["edu_university"],
                warnings=["本地库未命中学校实体，不能猜测学校。"],
            )

        return tool_result(
            "school_lookup",
            "ok",
            {"school_text": school_text, "limit": limit},
            normalized_slots={"school_name": rows[0].get("name"), "school_id": rows[0].get("school_id")},
            data={"selected_school": rows[0], "candidates": rows},
            scope_notes=["学校实体解析来自 edu_university；第一版尚未启用人工确认别名表。"],
            source_tables=["edu_university"],
        )

    def major_lookup(self, major_text: str, limit: int = 5) -> dict[str, Any]:
        """Resolve a major name/code to canonical major rows."""

        missing = _missing_slots({"major_text": major_text})
        if missing:
            return _needs("major_lookup", {"major_text": major_text}, missing)

        rows = self.client.query(resolve_major_sql(major_text, limit=limit))
        if not rows:
            return tool_result(
                "major_lookup",
                "not_found",
                {"major_text": major_text, "limit": limit},
                data={"selected_major": {}, "candidates": []},
                source_tables=["edu_major", "entity_aliases"],
                warnings=["本地库未命中专业实体，不能猜测专业。"],
            )

        return tool_result(
            "major_lookup",
            "ok",
            {"major_text": major_text, "limit": limit},
            normalized_slots={"major_name": rows[0].get("special_name"), "major_code": rows[0].get("code")},
            data={"selected_major": rows[0], "candidates": rows},
            scope_notes=["专业实体解析来自 edu_major 和 entity_aliases；短简称只使用已确认别名，不直接做短词模糊匹配。"],
            source_tables=["edu_major", "entity_aliases"],
        )

    def school_profile(self, school_text: str) -> dict[str, Any]:
        """Return school-level profile data.

        This is intentionally school-level only.  Employment rows returned here
        must never be used as evidence for a specific major unless a later
        source table proves that major-level employment exists.
        """

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "school_profile"}

        school = school_result["data"]["selected_school"]
        dual_class = self.client.query(_dual_class_by_school_sql(school))
        subject_evals = self.client.query(_subject_evals_by_school_sql(school))
        latest_employment = _first_row(self.client.query(build_latest_employment_sql(school)))

        return tool_result(
            "school_profile",
            "ok",
            {"school_text": school_text},
            normalized_slots=school_result["normalized_slots"],
            data={
                "school": school,
                "dual_class": dual_class,
                "subject_evals": subject_evals,
                "latest_employment": latest_employment or {},
            },
            scope_notes=[
                "学校基础信息是学校级事实。",
                "就业升学数据来自学校级表，不代表某个专业。",
            ],
            source_tables=[
                "edu_university",
                "edu_dual_class",
                "edu_university_subject_eval",
                "edu_university_employment",
            ],
        )

    def major_profile(self, major_text: str) -> dict[str, Any]:
        """Return major-level profile data from `edu_major`."""

        major_result = self.major_lookup(major_text, limit=1)
        if major_result["status"] != "ok":
            return major_result | {"tool_name": "major_profile"}

        major = major_result["data"]["selected_major"]
        return tool_result(
            "major_profile",
            "ok",
            {"major_text": major_text},
            normalized_slots=major_result["normalized_slots"],
            data={
                "major": major,
                "salary_reference": {
                    "salaryavg": major.get("salaryavg"),
                    "fivesalaryavg": major.get("fivesalaryavg"),
                },
                "job_directions": _split_text(major.get("job_clean") or major.get("job") or major.get("do_what")),
            },
            scope_notes=[
                "专业资料来自 edu_major，是专业通用级数据。",
                "薪资和就业方向不代表某学校某专业毕业生真实结果。",
            ],
            source_tables=_merge_source_tables(major_result["source_tables"], ["edu_major"]),
        )

    def school_major_list(
        self,
        school_text: str,
        major_category: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Return majors recorded for one school.

        Existing data has a subtle key mismatch: `edu_university.school_id` is
        not the same value as `edu_school_major.school_id`.  The school-major
        table uses the university `code`, so the query must join/filter with
        `selected_school.code`.  The test suite locks this down because using
        `school_id` silently returns wrong-school rows.
        """

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "school_major_list"}

        school = school_result["data"]["selected_school"]
        rows = self.client.query(_school_major_list_sql(school, major_category, limit))
        return tool_result(
            "school_major_list",
            "ok",
            {"school_text": school_text, "major_category": major_category, "limit": limit},
            normalized_slots=school_result["normalized_slots"],
            data={"school": school, "majors": rows},
            scope_notes=["学校开设专业不等于某省当年招生专业；带省份年份时应查询招生计划。"],
            source_tables=["edu_university", "edu_school_major", "edu_major"],
        )

    def major_school_list(
        self,
        major_text: str,
        province_filter: str | None = None,
        school_level_filter: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Return schools recorded as offering a major."""

        major_result = self.major_lookup(major_text, limit=1)
        if major_result["status"] != "ok":
            return major_result | {"tool_name": "major_school_list"}

        major = major_result["data"]["selected_major"]
        rows = self.client.query(_major_school_list_sql(major, province_filter, school_level_filter, limit))
        return tool_result(
            "major_school_list",
            "ok",
            {
                "major_text": major_text,
                "province_filter": province_filter,
                "school_level_filter": school_level_filter,
                "limit": limit,
            },
            normalized_slots=major_result["normalized_slots"],
            data={"major": major, "schools": rows},
            scope_notes=["开设学校列表是学校专业关系口径，不等于某省当年有招生计划。"],
            source_tables=_merge_source_tables(
                major_result["source_tables"],
                ["edu_school_major", "edu_university"],
            ),
        )

    def school_major_profile(
        self,
        school_text: str,
        major_text: str,
        province: str | None = None,
        subject_type: str | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Return a school-major profile with explicit scope boundaries."""

        missing = _missing_slots({"school_text": school_text, "major_text": major_text})
        if missing:
            return _needs(
                "school_major_profile",
                {"school_text": school_text, "major_text": major_text},
                missing,
            )

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "school_major_profile"}

        major_result = self.major_lookup(major_text, limit=1)
        if major_result["status"] != "ok":
            return major_result | {"tool_name": "school_major_profile"}

        school = school_result["data"]["selected_school"]
        major = major_result["data"]["selected_major"]
        school_major = _first_row(self.client.query(build_school_major_sql(school, major)))
        subject_evals = self.client.query(build_subject_eval_sql(school, major))
        dual_class = self.client.query(build_dual_class_sql(school, major))
        employment = _first_row(self.client.query(build_latest_employment_sql(school)))
        groups = self.client.query(_specialty_group_sql(school, major, province, subject_type, year))

        available = ["学校基础信息", "专业基础信息"]
        if school_major:
            available.append("学校-专业开设关系")
        if subject_evals:
            available.append("教育部学科评估")
        if employment:
            available.append("学校级就业/升学")
        if groups:
            available.append("专业组样本")

        return tool_result(
            "school_major_profile",
            "ok" if school_major else "partial",
            {
                "school_text": school_text,
                "major_text": major_text,
                "province": province,
                "subject_type": subject_type,
                "year": year,
            },
            normalized_slots={
                **school_result["normalized_slots"],
                **major_result["normalized_slots"],
                "province": province,
                "subject_type": subject_type,
                "year": year,
            },
            data={
                "school": school,
                "major": major,
                "school_major": school_major or {},
                "subject_evals": subject_evals,
                "dual_class": dual_class,
                "employment": employment or {},
                "specialty_groups": groups,
                "available_fields": available,
            },
            scope_notes=[
                "学校-专业开设关系、专业通用资料、学校级就业、专业组样本是不同口径。",
                "学校级就业/升学不能代表某专业真实就业结果。",
                "专业组样本不等于入学后真实分流比例。",
            ],
            data_gaps=SCHOOL_MAJOR_PROFILE_GAPS,
            source_tables=[
                *_merge_source_tables(school_result["source_tables"], major_result["source_tables"]),
                "edu_school_major",
                "edu_university_subject_eval",
                "edu_dual_class",
                "edu_university_employment",
                "edu_college_specialty_group",
                "edu_specialty_group_major",
            ],
            warnings=[] if school_major else ["本地库未命中明确学校-专业开设关系，不能直接认定已开设。"],
        )

    def score_to_rank(
        self,
        province: str,
        subject_type: str,
        score: int | float | str,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Convert score to rank range in one province/subject/year.

        A score has meaning only inside the exact province, subject type, and
        year.  The tool returns a range because one score can correspond to many
        students.  Later matching should use rank, not raw score.
        """

        missing = _missing_slots({"province": province, "subject_type": subject_type, "score": score})
        if missing:
            return _needs(
                "score_to_rank",
                {"province": province, "subject_type": subject_type, "score": score, "year": year},
                missing,
            )

        province_id = _province_id(province)
        if not province_id:
            return tool_result(
                "score_to_rank",
                "needs_clarification",
                {"province": province, "subject_type": subject_type, "score": score, "year": year},
                needs_clarification=["province"],
                warnings=["暂不认识该省份名称，请提供省份标准名称或 province_id。"],
            )

        rows = self.client.query(_score_to_rank_sql(province_id, subject_type, score, year))
        if not rows:
            return tool_result(
                "score_to_rank",
                "not_found",
                {"province": province, "subject_type": subject_type, "score": score, "year": year},
                normalized_slots={"province_id": province_id},
                source_tables=["edu_score_rank"],
                warnings=["本地库未命中对应一分一段记录。"],
            )

        row = rows[0]
        return tool_result(
            "score_to_rank",
            "ok",
            {"province": province, "subject_type": subject_type, "score": score, "year": year},
            normalized_slots={"province": province, "province_id": province_id, "subject_type": subject_type, "year": row.get("year")},
            data={
                "score": _as_int(row.get("score")),
                "same_count": _as_int(row.get("same_count")),
                "rank_range": {
                    "highest_rank": _as_int(row.get("highest_rank")),
                    "lowest_rank": _as_int(row.get("lowest_rank")),
                },
            },
            scope_notes=["位次优先于分数；分数转位次只在同省、同科类、同年份内有效。"],
            source_tables=["edu_score_rank"],
        )

    def rank_to_school_match(
        self,
        province: str,
        subject_type: str | None = None,
        score: int | float | str | None = None,
        rank: int | str | None = None,
        year: int | None = None,
        reference_years: list[int] | None = None,
        preferred_regions: list[str] | None = None,
        school_level_filter: str | None = None,
        limit: int = 30,
    ) -> dict[str, Any]:
        """Match an applicant rank to school-level historical opportunities.

        This is the first recommendation-shaped tool, so it is intentionally
        conservative.  It uses rank, not raw score, and it keeps the historical
        reference year in every result.  When the requested year is not present
        locally, the SQL falls back to earlier years and the response marks that
        as `history_fallback` instead of pretending those rows are current-year
        admission results.
        """

        missing = _missing_slots({"province": province})
        if missing:
            return _needs(
                "rank_to_school_match",
                {
                    "province": province,
                    "subject_type": subject_type,
                    "score": score,
                    "rank": rank,
                    "year": year,
                },
                missing,
            )

        applicant_rank = _as_int(rank)
        score_rank_result: dict[str, Any] | None = None
        rank_source = "provided_rank" if applicant_rank else ""
        if applicant_rank is None:
            if score in (None, ""):
                return _needs(
                    "rank_to_school_match",
                    {
                        "province": province,
                        "subject_type": subject_type,
                        "score": score,
                        "rank": rank,
                        "year": year,
                    },
                    ["rank_or_score"],
                )
            if not subject_type:
                return _needs(
                    "rank_to_school_match",
                    {
                        "province": province,
                        "subject_type": subject_type,
                        "score": score,
                        "rank": rank,
                        "year": year,
                    },
                    ["subject_type"],
                )

            score_rank_result = self.score_to_rank(province, subject_type, score, year)
            if score_rank_result["status"] != "ok":
                return score_rank_result | {"tool_name": "rank_to_school_match"}
            applicant_rank = _as_int(score_rank_result["data"]["rank_range"].get("lowest_rank"))
            rank_source = "score_to_rank"

        if applicant_rank is None:
            return _needs(
                "rank_to_school_match",
                {
                    "province": province,
                    "subject_type": subject_type,
                    "score": score,
                    "rank": rank,
                    "year": year,
                },
                ["rank_or_score"],
            )

        rows = self.client.query(
            _rank_to_school_match_sql(
                province=province,
                subject_type=subject_type,
                applicant_rank=applicant_rank,
                requested_year=year,
                reference_years=reference_years,
                preferred_regions=preferred_regions,
                school_level_filter=school_level_filter,
                limit=max(limit * 8, 80),
            )
        )
        buckets, selected_rows = _bucket_school_matches(rows, applicant_rank, limit)
        reference_year_values = sorted(
            {year_value for row in selected_rows if (year_value := _as_int(row.get("year"))) is not None},
            reverse=True,
        )
        history_fallback = bool(year and reference_year_values and year not in reference_year_values)

        input_data = {
            "province": province,
            "subject_type": subject_type,
            "score": score,
            "rank": rank,
            "year": year,
            "reference_years": reference_years,
            "preferred_regions": preferred_regions,
            "school_level_filter": school_level_filter,
            "limit": limit,
        }
        if not selected_rows:
            return tool_result(
                "rank_to_school_match",
                "not_found",
                input_data,
                normalized_slots={"province": province, "subject_type": subject_type, "rank": applicant_rank},
                data={
                    "applicant": _applicant_rank_payload(
                        province, subject_type, score, applicant_rank, rank_source, score_rank_result
                    ),
                    "buckets": {"rush": [], "stable": [], "safe": []},
                },
                source_tables=["edu_score_rank", "edu_school_admission_stats"],
                warnings=["本地库未命中可用于该省份/科类/年份的学校历史录取参考。"],
            )

        subject_unknown_count = sum(1 for row in selected_rows if not _text(row.get("subject_type")))
        scope_notes = [
            "本工具使用历史录取位次做学校层面参考，不代表未来录取保证。",
            "学校匹配不等于专业录取保证；具体专业需继续调用 rank_to_major_match 或专业组工具。",
        ]
        warnings = []
        if history_fallback:
            warnings.append("本地库缺少请求年份的录取结果，已使用最近可用历史年份作为参考。")
        if subject_unknown_count:
            warnings.append("部分历史记录没有科类字段，已按省份历史参考纳入，需谨慎解读。")

        return tool_result(
            "rank_to_school_match",
            "ok",
            input_data,
            normalized_slots={"province": province, "subject_type": subject_type, "rank": applicant_rank},
            data={
                "applicant": _applicant_rank_payload(
                    province, subject_type, score, applicant_rank, rank_source, score_rank_result
                ),
                "reference": {
                    "requested_year": year,
                    "reference_years": reference_year_values,
                    "history_fallback": history_fallback,
                    "matching_rule": "safe: rank<=bao_rank; stable: rank<=stable_rank; rush: rank<=chong_rank",
                    "subject_unknown_count": subject_unknown_count,
                },
                "buckets": buckets,
                "coverage": {
                    "candidate_rows": len(rows),
                    "returned_schools": sum(len(items) for items in buckets.values()),
                },
            },
            scope_notes=scope_notes,
            source_tables=["edu_score_rank", "edu_school_admission_stats", "edu_university"],
            warnings=warnings,
        )

    def admission_history(
        self,
        school_text: str | None = None,
        major_text: str | None = None,
        province: str | None = None,
        subject_type: str | None = None,
        years: list[int] | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Return historical admission score/rank records.

        This tool can work with school-only, major-only, or school+major filters,
        but province and subject type are strongly recommended for meaningful
        comparisons.  When those slots are missing the tool still returns data,
        but status is `partial` and the scope note tells the agent to ask for a
        narrower context before giving recommendation-like advice.
        """

        if not school_text and not major_text:
            return _needs(
                "admission_history",
                {
                    "school_text": school_text,
                    "major_text": major_text,
                    "province": province,
                    "subject_type": subject_type,
                    "years": years,
                },
                ["school_text_or_major_text"],
            )

        school = None
        major = None
        normalized: dict[str, Any] = {}
        if school_text:
            school_result = self.school_lookup(school_text, limit=1)
            if school_result["status"] != "ok":
                return school_result | {"tool_name": "admission_history"}
            school = school_result["data"]["selected_school"]
            normalized.update(school_result["normalized_slots"])
        if major_text:
            major_result = self.major_lookup(major_text, limit=1)
            if major_result["status"] != "ok":
                return major_result | {"tool_name": "admission_history"}
            major = major_result["data"]["selected_major"]
            normalized.update(major_result["normalized_slots"])

        rows = self.client.query(_admission_history_sql(school, major, province, subject_type, years, limit))
        missing_context = [slot for slot, value in {"province": province, "subject_type": subject_type}.items() if not value]
        return tool_result(
            "admission_history",
            "partial" if missing_context else "ok",
            {
                "school_text": school_text,
                "major_text": major_text,
                "province": province,
                "subject_type": subject_type,
                "years": years,
                "limit": limit,
            },
            normalized_slots={**normalized, "province": province, "subject_type": subject_type},
            data={"records": rows},
            scope_notes=[
                "录取历史必须带年份、省份、科类、批次理解；跨年份比较优先看位次。",
                "历史录取不代表未来录取保证。",
            ],
            needs_clarification=missing_context,
            source_tables=_merge_source_tables(
                school_result["source_tables"] if school_text else [],
                major_result["source_tables"] if major_text else [],
                ["edu_school_admission_stats"],
            ),
            warnings=["缺少省份或科类时，只能作为宽泛历史样本。"] if missing_context else [],
        )

    def major_market_reference(self, major_text: str, sample_limit: int = 10) -> dict[str, Any]:
        """Return rysxai major-level market observation data.

        This uses the normalized ingestion tables created from crawled rysxai
        data.  It is useful for market observation and representative job
        samples, but it is not official school-major graduate employment
        evidence.  The scope note is part of the tool output so an agent cannot
        responsibly omit it.
        """

        major_result = self.major_lookup(major_text, limit=1)
        if major_result["status"] != "ok":
            return major_result | {"tool_name": "major_market_reference"}

        major = major_result["data"]["selected_major"]
        snapshot = _first_row(self.client.query(_major_market_snapshot_sql(major)))
        if not snapshot:
            return tool_result(
                "major_market_reference",
                "not_found",
                {"major_text": major_text, "sample_limit": sample_limit},
                normalized_slots=major_result["normalized_slots"],
                data={"major": major, "snapshot": {}, "job_samples": []},
                data_gaps=["专业市场观察数据"],
                source_tables=_merge_source_tables(
                    major_result["source_tables"],
                    ["rysxai_major_market_snapshots"],
                ),
                warnings=["本地库未命中该专业的 rysxai 市场快照。"],
            )

        job_samples = self.client.query(_major_market_samples_sql(snapshot, major, sample_limit))
        return tool_result(
            "major_market_reference",
            "ok",
            {"major_text": major_text, "sample_limit": sample_limit},
            normalized_slots=major_result["normalized_slots"],
            data={
                "major": major,
                "snapshot": _decode_json_fields(
                    snapshot,
                    [
                        "macro_employment_json",
                        "demand_ranking_json",
                        "salary_ranking_json",
                        "warnings_json",
                    ],
                ),
                "job_samples": job_samples,
            },
            scope_notes=[
                "这是第三方招聘市场样本和专业市场观察，不代表某学校某专业毕业生真实就业去向或薪资。",
            ],
            source_tables=_merge_source_tables(
                major_result["source_tables"],
                ["rysxai_major_market_snapshots", "rysxai_major_job_samples"],
            ),
        )

    def civil_service_role_search(
        self,
        major_text: str,
        year: int | None = None,
        province: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Search civil-service role samples linked to a major-code candidate."""

        major_result = self.major_lookup(major_text, limit=1)
        if major_result["status"] != "ok":
            return major_result | {"tool_name": "civil_service_role_search"}

        major = major_result["data"]["selected_major"]
        rows = self.client.query(_civil_service_role_search_sql(major, year, province, limit))
        return tool_result(
            "civil_service_role_search",
            "ok" if rows else "not_found",
            {"major_text": major_text, "year": year, "province": province, "limit": limit},
            normalized_slots={**major_result["normalized_slots"], "year": year, "province": province},
            data={"major": major, "roles": rows},
            scope_notes=[
                "以下为岗位专业要求文本命中的考公岗位样本，不等于该专业一定可报。",
                "最终可报范围应以当年官方招录公告和岗位表解释为准。",
            ],
            data_gaps=[] if rows else ["考公岗位专业候选"],
            source_tables=_merge_source_tables(
                major_result["source_tables"],
                ["civil_service_major_role_candidates", "rysxai_civil_service_roles"],
            ),
            warnings=[] if rows else ["本地库未命中该专业代码的考公岗位候选。"],
        )

    def data_gap_detection(
        self,
        question_type: str,
        available_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Return missing data items for one question type."""

        available = set(available_fields or [])
        missing_by_type = {
            "school_major_profile": {
                "school_basic": "学校基础信息",
                "major_basic": "专业基础信息",
                "school_major": "学校-专业开设关系",
                "subject_eval": "教育部学科评估",
                "school_major_salary": "校专业级薪资分布",
                "school_major_regions": "校专业级工作地域分布",
                "top_companies": "校专业级Top对口公司",
                "civil_service_mapping": "考公岗位映射",
                "transfer_policy": "转专业政策",
                "streaming_ratio": "专业组真实分流比例/冷门专业比例",
                "official_major_intro": "学校官网专业介绍证据链",
            },
            "major_market_reference": {
                "market_snapshot": "专业市场观察数据",
                "job_samples": "招聘岗位样本",
                "official_employment": "官方就业质量报告佐证",
            },
            "civil_service_role_search": {
                "role_candidates": "考公岗位候选",
                "official_role_table": "官方招录岗位表来源",
                "manual_mapping": "专业代码人工确认映射",
            },
        }
        expected = missing_by_type.get(question_type, {})
        missing_items = [label for key, label in expected.items() if key not in available]

        return tool_result(
            "data_gap_detection",
            "ok",
            {"question_type": question_type, "available_fields": available_fields or []},
            data={"missing_items": missing_items},
            scope_notes=["缺口检测只描述本地当前缺失，不代表事实不存在。"],
            source_tables=[],
        )


def _needs(tool_name: str, input_data: dict[str, Any], missing: list[str]) -> dict[str, Any]:
    return tool_result(
        tool_name,
        "needs_clarification",
        input_data,
        needs_clarification=missing,
        warnings=["缺少必要槽位，不能猜测后继续检索。"],
    )


def _missing_slots(values: dict[str, Any]) -> list[str]:
    return [key for key, value in values.items() if value is None or str(value).strip() == ""]


def _first_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return rows[0] if rows else None


def _dual_class_by_school_sql(school: dict[str, Any]) -> str:
    return f"""
SELECT class_name, major_code, code, class_type, cycle
FROM edu_dual_class
WHERE deleted = b'0'
  AND school_id = {sql_quote(school.get('school_id'))}
ORDER BY cycle DESC, class_name
""".strip()


def _subject_evals_by_school_sql(school: dict[str, Any]) -> str:
    return f"""
SELECT eval_round, major_name, eval_level, level_code, special_id, special_name
FROM edu_university_subject_eval
WHERE (deleted IS NULL OR deleted = b'0')
  AND school_id = {sql_quote(school.get('school_id'))}
ORDER BY eval_round DESC, level_code IS NULL, level_code, eval_level
""".strip()


def _school_major_list_sql(
    school: dict[str, Any],
    major_category: str | None,
    limit: int,
) -> str:
    category_clause = ""
    if major_category:
        like = sql_quote(f"%{major_category}%")
        category_clause = f"AND (sm.level3_name LIKE {like} OR sm.xueke_name LIKE {like} OR sm.major_name LIKE {like})"
    return f"""
SELECT sm.major_code, sm.major_name, sm.level_name, sm.limit_year, sm.nation_first_class,
       sm.xueke_rank_score, sm.ruanke_level, sm.menlei_name, sm.xueke_name, sm.level3_name
FROM edu_school_major sm
WHERE (sm.deleted IS NULL OR sm.deleted = 0)
  AND sm.school_id = {sql_quote(school.get('code') or school.get('school_id'))}
  AND sm.school_name = {sql_quote(school.get('name'))}
  {category_clause}
ORDER BY sm.major_code
LIMIT {int(limit)}
""".strip()


def _major_school_list_sql(
    major: dict[str, Any],
    province_filter: str | None,
    school_level_filter: str | None,
    limit: int,
) -> str:
    province_clause = f"AND u.province_name = {sql_quote(province_filter)}" if province_filter else ""
    level_clause = ""
    if school_level_filter in {"211", "双一流", "985"}:
        column = {"211": "u.is211", "985": "u.is985", "双一流": "u.is_dual_class"}[school_level_filter]
        level_clause = f"AND {column} = 1"
    return f"""
SELECT sm.school_id, sm.school_name, u.province_name, u.city_name, u.is211, u.is985,
       u.is_dual_class, sm.major_code, sm.major_name, sm.nation_first_class,
       sm.xueke_rank_score, sm.ruanke_level
FROM edu_school_major sm
LEFT JOIN edu_university u ON u.code = CAST(sm.school_id AS CHAR) AND u.name = sm.school_name
WHERE (sm.deleted IS NULL OR sm.deleted = 0)
  AND (sm.major_code = {sql_quote(major.get('code'))} OR sm.major_name = {sql_quote(major.get('special_name'))})
  {province_clause}
  {level_clause}
ORDER BY u.is985 DESC, u.is211 DESC, u.is_dual_class DESC, sm.school_name
LIMIT {int(limit)}
""".strip()


def _province_id(province: str) -> str | None:
    text = str(province).strip()
    if text.isdigit():
        return text
    text = text.removesuffix("省").removesuffix("市").removesuffix("壮族自治区").removesuffix("自治区").removesuffix("回族自治区").removesuffix("维吾尔自治区")
    return PROVINCE_ID_BY_NAME.get(text)


def _score_to_rank_sql(province_id: str, subject_type: str, score: int | float | str, year: int | None) -> str:
    year_clause = f"AND year = {int(year)}" if year else ""
    return f"""
SELECT province_id, year, subject_type, score, same_count, highest_rank, lowest_rank
FROM edu_score_rank
WHERE deleted = 0
  AND province_id = {sql_quote(province_id)}
  AND subject_type = {sql_quote(subject_type)}
  AND score = {int(float(score))}
  {year_clause}
ORDER BY CAST(year AS UNSIGNED) DESC
LIMIT 1
""".strip()


def _rank_to_school_match_sql(
    province: str,
    subject_type: str | None,
    applicant_rank: int,
    requested_year: int | None,
    reference_years: list[int] | None,
    preferred_regions: list[str] | None,
    school_level_filter: str | None,
    limit: int,
) -> str:
    clauses = [
        "(a.deleted IS NULL OR a.deleted = b'0')",
        f"a.province_name = {sql_quote(province)}",
        "a.stable_rank IS NOT NULL AND a.stable_rank > 0",
        (
            f"({int(applicant_rank)} <= a.chong_rank "
            f"OR {int(applicant_rank)} <= a.stable_rank "
            f"OR {int(applicant_rank)} <= a.bao_rank)"
        ),
    ]
    if requested_year:
        clauses.append(f"a.year <= {int(requested_year)}")
    if reference_years:
        years = ", ".join(str(int(value)) for value in reference_years)
        clauses.append(f"a.year IN ({years})")
    if subject_type:
        # Some imported historical rows, notably Guangdong school-level history,
        # have a blank subject_type even though the province now has physics /
        # history tracks.  We keep those rows as a documented fallback instead
        # of incorrectly claiming there is no historical reference at all.
        clauses.append(
            f"(a.subject_type = {sql_quote(subject_type)} OR a.subject_type IS NULL OR a.subject_type = '')"
        )
    if preferred_regions:
        regions = ", ".join(sql_quote(region) for region in preferred_regions if region)
        if regions:
            clauses.append(f"u.province_name IN ({regions})")
    if school_level_filter:
        pattern = f"%{school_level_filter}%"
        clauses.append(
            f"(u.level_name LIKE {sql_quote(pattern)} OR u.school_type LIKE {sql_quote(pattern)})"
        )

    subject_order = "1"
    if subject_type:
        subject_order = (
            f"CASE WHEN a.subject_type = {sql_quote(subject_type)} THEN 0 "
            "WHEN a.subject_type IS NULL OR a.subject_type = '' THEN 1 ELSE 2 END"
        )

    return f"""
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
-- Admission history uses the national school code in `a.school_id`, while
-- edu_university.school_id is an internal platform id.  Join through
-- edu_university.code plus the school name so location/level metadata does not
-- drift to a different school that happens to share the numeric internal id.
LEFT JOIN edu_university u ON u.code = CAST(a.school_id AS CHAR) AND u.name = a.school_name
WHERE {' AND '.join(clauses)}
ORDER BY {subject_order}, a.year DESC, ABS(a.stable_rank - {int(applicant_rank)}), a.school_name
LIMIT {int(limit)}
""".strip()


def _specialty_group_sql(
    school: dict[str, Any],
    major: dict[str, Any],
    province: str | None,
    subject_type: str | None,
    year: int | None,
    limit: int = 8,
) -> str:
    # Professional group data is province/year specific.  If a user asks about
    # Guangdong physics in 2025, returning other provinces' groups would be a
    # subtle factual error rather than merely "extra context", so every provided
    # context slot becomes an SQL filter here.
    school_id = str(school.get("school_id") or "")
    major_code = str(major.get("code") or major.get("special_id") or "")
    major_name = str(major.get("special_name") or "")
    clauses = [
        "(g.deleted IS NULL OR g.deleted = b'0')",
        "(gm.deleted IS NULL OR gm.deleted = b'0')",
        f"g.school_id = {sql_quote(school_id)}",
    ]

    if province:
        province_id = _province_id(province) or str(province)
        clauses.append(f"g.province = {sql_quote(province_id)}")
    if subject_type:
        clauses.append(f"g.group_type = {sql_quote(subject_type)}")
    if year:
        clauses.append(f"g.year = {int(year)}")

    return f"""
SELECT g.year, g.province, g.group_code, g.group_name, g.group_type,
       g.plan_count AS group_plan_count, g.min_score, g.min_rank,
       g.allow_adjustment, gm.special_code, gm.special_name,
       gm.plan_count AS major_plan_count, gm.subject_requirement, gm.remark
FROM edu_college_specialty_group g
JOIN edu_specialty_group_major gm ON gm.group_id = g.id
WHERE {' AND '.join(clauses)}
  AND (
    gm.special_code = {sql_quote(major_code)}
    OR gm.special_name = {sql_quote(major_name)}
  )
ORDER BY g.year DESC, g.province, g.group_code
LIMIT {int(limit)}
""".strip()


def _admission_history_sql(
    school: dict[str, Any] | None,
    major: dict[str, Any] | None,
    province: str | None,
    subject_type: str | None,
    years: list[int] | None,
    limit: int,
) -> str:
    clauses = ["(deleted IS NULL OR deleted = b'0')"]
    if school:
        clauses.append(f"school_name = {sql_quote(school.get('name'))}")
    if major:
        clauses.append(
            f"(major_code = {sql_quote(major.get('code'))} OR major_name = {sql_quote(major.get('special_name'))})"
        )
    if province:
        clauses.append(f"province_name = {sql_quote(province)}")
    if subject_type:
        clauses.append(f"subject_type = {sql_quote(subject_type)}")
    if years:
        clauses.append("year IN (" + ", ".join(str(int(year)) for year in years) + ")")

    return f"""
SELECT province_name, school_id, school_name, major_code, major_name, subject_type,
       year, stable_score, stable_rank, chong_score, chong_rank, bao_score, bao_rank,
       batch, subject_requirement, plan_count, admission_count, remark
FROM edu_school_admission_stats
WHERE {' AND '.join(clauses)}
ORDER BY year DESC, school_name, major_name
LIMIT {int(limit)}
""".strip()


def _major_market_snapshot_sql(major: dict[str, Any]) -> str:
    return f"""
SELECT profession_id, major_code, major_name, major_level, degree, limit_year,
       captured_at, source_name, source_level, data_scope, info_url, positions_url,
       macro_employment_json, demand_ranking_json, salary_ranking_json,
       salary_observations_by_city_json, salary_observations_by_industry_json,
       job_posting_sample_total_reported, job_posting_sample_count, warnings_json
FROM rysxai_major_market_snapshots
WHERE major_code = {sql_quote(major.get('code'))}
   OR major_name = {sql_quote(major.get('special_name'))}
ORDER BY profession_id
LIMIT 1
""".strip()


def _major_market_samples_sql(
    snapshot: dict[str, Any],
    major: dict[str, Any],
    limit: int,
) -> str:
    profession_id = snapshot.get("profession_id")
    return f"""
SELECT job_title, company_name, city, district, industry, salary_raw,
       monthly_salary_min, monthly_salary_max, education, experience,
       company_scale, financing_stage
FROM rysxai_major_job_samples
WHERE profession_id = {sql_quote(profession_id)}
   OR major_code = {sql_quote(major.get('code'))}
ORDER BY monthly_salary_max DESC, monthly_salary_min DESC
LIMIT {int(limit)}
""".strip()


def _civil_service_role_search_sql(
    major: dict[str, Any],
    year: int | None,
    province: str | None,
    limit: int,
) -> str:
    year_clause = f"AND r.year = {int(year)}" if year else ""
    province_clause = f"AND r.province = {sql_quote(province)}" if province else ""
    return f"""
SELECT r.role_id, r.year, r.department_name, r.sub_department, r.job_name,
       r.position_code, r.exam_type, r.plan_num, r.apply_num, r.ratio,
       r.education_level, r.degree_requirement, r.work_location, r.province,
       c.major_code, c.major_name, c.profession_text
FROM civil_service_major_role_candidates c
JOIN rysxai_civil_service_roles r ON r.role_id = c.role_id
WHERE c.major_code = {sql_quote(major.get('code'))}
  {year_clause}
  {province_clause}
ORDER BY r.year DESC, r.ratio ASC, r.role_id
LIMIT {int(limit)}
""".strip()


def _split_text(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    parts = [part.strip() for part in text.replace("；", "，").replace(";", ",").replace("、", ",").split(",")]
    return [part for part in parts if part]


def _text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    # The mysql CLI prints SQL NULL as the literal token "NULL" in batch
    # output.  Treat it as absent data inside retrieval payloads so agents do
    # not mistake a transport placeholder for a real admissions category.
    return "" if text.upper() == "NULL" else text


def _optional_text(value: Any) -> str | None:
    text = _text(value)
    return text or None


def _bucket_school_matches(
    rows: list[dict[str, Any]],
    applicant_rank: int,
    limit: int,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {"rush": [], "stable": [], "safe": []}
    selected_rows: list[dict[str, Any]] = []
    seen_schools: set[str] = set()

    for row in rows:
        school_key = _text(row.get("school_id")) or _text(row.get("school_name"))
        if not school_key or school_key in seen_schools:
            continue
        bucket = _school_match_bucket(row, applicant_rank)
        if not bucket:
            continue
        buckets[bucket].append(_school_match_payload(row, applicant_rank, bucket))
        selected_rows.append(row)
        seen_schools.add(school_key)
        if len(selected_rows) >= limit:
            break

    return buckets, selected_rows


def _school_match_bucket(row: dict[str, Any], applicant_rank: int) -> str | None:
    bao_rank = _as_int(row.get("bao_rank"))
    stable_rank = _as_int(row.get("stable_rank"))
    chong_rank = _as_int(row.get("chong_rank"))

    # Smaller rank means a stronger applicant.  The imported history table
    # already gives three thresholds, so the first version does not invent a new
    # admissions model: it simply maps those thresholds to 保/稳/冲 buckets.
    if bao_rank is not None and applicant_rank <= bao_rank:
        return "safe"
    if stable_rank is not None and applicant_rank <= stable_rank:
        return "stable"
    if chong_rank is not None and applicant_rank <= chong_rank:
        return "rush"
    return None


def _school_match_payload(row: dict[str, Any], applicant_rank: int, bucket: str) -> dict[str, Any]:
    stable_rank = _as_int(row.get("stable_rank"))
    return {
        "school_id": _optional_text(row.get("school_id")),
        "school_name": _optional_text(row.get("school_name")),
        "school_province_name": _optional_text(row.get("school_province_name")),
        "city_name": _optional_text(row.get("city_name")),
        "school_level_name": _optional_text(row.get("school_level_name")),
        "school_type_name": _optional_text(row.get("school_type_name")),
        "is985": _as_int(row.get("is985")),
        "is211": _as_int(row.get("is211")),
        "is_dual_class": _as_int(row.get("is_dual_class")),
        "risk_bucket": bucket,
        "risk_label": {"rush": "冲", "stable": "稳", "safe": "保"}[bucket],
        "reference_year": _as_int(row.get("year")),
        "province_name": _optional_text(row.get("province_name")),
        "subject_type": _optional_text(row.get("subject_type")),
        "batch": _optional_text(row.get("batch")),
        "stable_score": _as_int(row.get("stable_score")),
        "stable_rank": stable_rank,
        "chong_score": _as_int(row.get("chong_score")),
        "chong_rank": _as_int(row.get("chong_rank")),
        "bao_score": _as_int(row.get("bao_score")),
        "bao_rank": _as_int(row.get("bao_rank")),
        "rank_gap_to_stable": applicant_rank - stable_rank if stable_rank is not None else None,
        "representative_major_name": _optional_text(row.get("representative_major_name")),
        "row_scope": _optional_text(row.get("row_scope")),
    }


def _applicant_rank_payload(
    province: str,
    subject_type: str | None,
    score: int | float | str | None,
    rank: int,
    rank_source: str,
    score_rank_result: dict[str, Any] | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "province": province,
        "subject_type": subject_type,
        "score": _as_int(score),
        "rank": rank,
        "rank_source": rank_source,
    }
    if score_rank_result:
        payload["score_rank"] = {
            "year": score_rank_result.get("normalized_slots", {}).get("year"),
            "same_count": score_rank_result.get("data", {}).get("same_count"),
            "rank_range": score_rank_result.get("data", {}).get("rank_range"),
        }
    return payload


def _decode_json_fields(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    decoded = dict(row)
    for field in fields:
        value = decoded.get(field)
        if isinstance(value, str) and value:
            try:
                decoded[field] = json.loads(value)
            except json.JSONDecodeError:
                decoded[field] = value
    return decoded


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def _print_json(value: dict[str, Any]) -> None:
    # Tool callers consume this CLI as JSON, not as a human-only console view.
    # Windows otherwise writes redirected stdout with the local ANSI code page,
    # which corrupts Chinese school/major names for agent pipelines.  Keeping
    # stdout UTF-8 makes the CLI output stable across PowerShell, tests, and
    # future function-call wrappers.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local retrieval function-call tools.")
    subparsers = parser.add_subparsers(dest="tool", required=True)

    p = subparsers.add_parser("school_lookup")
    p.add_argument("--school", required=True)

    p = subparsers.add_parser("major_lookup")
    p.add_argument("--major", required=True)

    p = subparsers.add_parser("school_profile")
    p.add_argument("--school", required=True)

    p = subparsers.add_parser("major_profile")
    p.add_argument("--major", required=True)

    p = subparsers.add_parser("school_major_list")
    p.add_argument("--school", required=True)
    p.add_argument("--major-category")
    p.add_argument("--limit", type=int, default=100)

    p = subparsers.add_parser("major_school_list")
    p.add_argument("--major", required=True)
    p.add_argument("--province-filter")
    p.add_argument("--school-level-filter")
    p.add_argument("--limit", type=int, default=50)

    p = subparsers.add_parser("school_major_profile")
    p.add_argument("--school", required=True)
    p.add_argument("--major", required=True)
    p.add_argument("--province")
    p.add_argument("--subject-type")
    p.add_argument("--year", type=int)

    p = subparsers.add_parser("score_to_rank")
    p.add_argument("--province", required=True)
    p.add_argument("--subject-type", required=True)
    p.add_argument("--score", required=True)
    p.add_argument("--year", type=int)

    p = subparsers.add_parser("rank_to_school_match")
    p.add_argument("--province", required=True)
    p.add_argument("--subject-type")
    p.add_argument("--score")
    p.add_argument("--rank")
    p.add_argument("--year", type=int)
    p.add_argument("--reference-years", nargs="*", type=int)
    p.add_argument("--preferred-regions", nargs="*")
    p.add_argument("--school-level-filter")
    p.add_argument("--limit", type=int, default=30)

    p = subparsers.add_parser("admission_history")
    p.add_argument("--school")
    p.add_argument("--major")
    p.add_argument("--province")
    p.add_argument("--subject-type")
    p.add_argument("--years", nargs="*", type=int)
    p.add_argument("--limit", type=int, default=50)

    p = subparsers.add_parser("major_market_reference")
    p.add_argument("--major", required=True)
    p.add_argument("--sample-limit", type=int, default=10)

    p = subparsers.add_parser("civil_service_role_search")
    p.add_argument("--major", required=True)
    p.add_argument("--year", type=int)
    p.add_argument("--province")
    p.add_argument("--limit", type=int, default=20)

    p = subparsers.add_parser("data_gap_detection")
    p.add_argument("--question-type", required=True)
    p.add_argument("--available-fields", nargs="*", default=[])

    args = parser.parse_args(argv)
    tools = RetrievalTools(MysqlCliClient(DbConfig.from_env()))

    dispatch = {
        "school_lookup": lambda: tools.school_lookup(args.school),
        "major_lookup": lambda: tools.major_lookup(args.major),
        "school_profile": lambda: tools.school_profile(args.school),
        "major_profile": lambda: tools.major_profile(args.major),
        "school_major_list": lambda: tools.school_major_list(args.school, args.major_category, args.limit),
        "major_school_list": lambda: tools.major_school_list(args.major, args.province_filter, args.school_level_filter, args.limit),
        "school_major_profile": lambda: tools.school_major_profile(args.school, args.major, args.province, args.subject_type, args.year),
        "score_to_rank": lambda: tools.score_to_rank(args.province, args.subject_type, args.score, args.year),
        "rank_to_school_match": lambda: tools.rank_to_school_match(
            args.province,
            args.subject_type,
            args.score,
            args.rank,
            args.year,
            args.reference_years,
            args.preferred_regions,
            args.school_level_filter,
            args.limit,
        ),
        "admission_history": lambda: tools.admission_history(args.school, args.major, args.province, args.subject_type, args.years, args.limit),
        "major_market_reference": lambda: tools.major_market_reference(args.major, args.sample_limit),
        "civil_service_role_search": lambda: tools.civil_service_role_search(args.major, args.year, args.province, args.limit),
        "data_gap_detection": lambda: tools.data_gap_detection(args.question_type, args.available_fields),
    }
    _print_json(dispatch[args.tool]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
