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


_SOURCE_TRACE_REGISTRY = {
    # The source trace registry is intentionally table-level, not answer-level:
    # it tells the future agent what kind of evidence a tool can surface before
    # the agent decides whether a claim is safe to write in natural language.
    "school_lookup": {
        "source_tables": ["edu_university"],
        "scope_notes": ["学校实体解析来自本地学校基础表。"],
        "reliability": "A",
    },
    "major_lookup": {
        "source_tables": ["edu_major", "entity_aliases"],
        "scope_notes": ["专业实体解析来自专业基础表和已确认别名表。"],
        "reliability": "A",
    },
    "school_profile": {
        "source_tables": ["edu_university", "edu_dual_class", "edu_university_subject_eval", "edu_university_employment"],
        "scope_notes": ["学校画像合并学校基础、双一流、学科评估和学校级就业摘要。"],
        "reliability": "A/B",
    },
    "major_profile": {
        "source_tables": ["edu_major", "entity_aliases"],
        "scope_notes": ["专业画像是专业通用信息，不代表某校某专业真实就业结果。"],
        "reliability": "A/B",
    },
    "school_major_list": {
        "source_tables": ["edu_university", "edu_school_major", "edu_major"],
        "scope_notes": ["学校开设专业不等于某省某年招生计划。"],
        "reliability": "A",
    },
    "major_school_list": {
        "source_tables": ["edu_major", "entity_aliases", "edu_school_major", "edu_university"],
        "scope_notes": ["专业开设学校列表不等于某省当年实际招生。"],
        "reliability": "A",
    },
    "school_major_profile": {
        "source_tables": [
            "edu_university",
            "edu_major",
            "edu_school_major",
            "edu_university_subject_eval",
            "edu_dual_class",
            "edu_university_employment",
            "edu_college_specialty_group",
            "edu_specialty_group_major",
        ],
        "scope_notes": ["校专业画像会合并多个口径，并在校专业级就业/薪资等缺口处返回 data_gaps。"],
        "reliability": "A/B",
    },
    "score_to_rank": {
        "source_tables": ["edu_score_rank"],
        "scope_notes": ["分数转位次只在同省、同科类、同年份内有效。"],
        "reliability": "A",
    },
    "rank_to_school_match": {
        "source_tables": ["edu_score_rank", "edu_school_admission_stats", "edu_university"],
        "scope_notes": ["冲稳保匹配基于历史位次参考，不代表未来录取保证。"],
        "reliability": "A/B",
    },
    "rank_to_major_match": {
        "source_tables": ["edu_major", "entity_aliases", "edu_score_rank", "edu_school_admission_stats", "edu_university"],
        "scope_notes": ["历史录取位次和专业行匹配只能作为志愿参考，不代表未来录取保证。"],
        "reliability": "A/B",
    },
    "admission_history": {
        "source_tables": ["edu_university", "edu_major", "entity_aliases", "edu_school_admission_stats"],
        "scope_notes": ["历史录取按省份、科类、年份理解；缺少上下文时只能作为宽泛样本。"],
        "reliability": "A",
    },
    "specialty_group_lookup": {
        "source_tables": ["edu_university", "edu_major", "edu_college_specialty_group", "edu_specialty_group_major"],
        "scope_notes": ["专业组构成是招生口径样本，不等于入学后真实分流结果。"],
        "reliability": "A",
    },
    "subject_requirement_lookup": {
        "source_tables": ["edu_major", "entity_aliases", "edu_college_specialty_group", "edu_specialty_group_major"],
        "scope_notes": ["选科要求来自招生计划/专业组样本，必须按省份、年份和科类解释。"],
        "reliability": "A/B",
    },
    "school_department_major_list": {
        "source_tables": ["edu_university", "edu_university_department", "edu_university_department_major"],
        "scope_notes": ["院系专业关系来自学校院系专业表，不等于某省某年招生计划。"],
        "reliability": "A",
    },
    "plan_history": {
        "source_tables": ["edu_university", "edu_major", "entity_aliases", "edu_qjjh_plan"],
        "scope_notes": ["招生计划按学校、省份、年份和专业理解；计划数不等于实际录取人数。"],
        "reliability": "A",
    },
    "employment_summary": {
        "source_tables": ["edu_university", "edu_university_employment"],
        "scope_notes": ["就业摘要是学校级数据，不能当作某专业真实就业结果。"],
        "reliability": "B",
    },
    "source_trace_lookup": {
        "source_tables": ["_SOURCE_TRACE_REGISTRY"],
        "scope_notes": ["来源解释是工具级口径说明，不替代具体回答中的原始来源链接。"],
        "reliability": "B",
    },
    "transfer_policy_lookup": {
        "source_tables": ["edu_university", "rysxai_transfer_policies"],
        "scope_notes": ["转专业政策当前来自第三方线索，需要官方来源复核。"],
        "reliability": "C",
    },
    "fee_and_campus_lookup": {
        "source_tables": ["edu_university", "edu_major", "edu_university_plan_config", "edu_university_plan_special_group", "edu_university_plan_special"],
        "scope_notes": ["当前可提供学费线索；本地库没有稳定校区字段时不会猜测校区。"],
        "reliability": "B/C",
    },
    "specialty_group_risk": {
        "source_tables": ["edu_university", "edu_major", "edu_college_specialty_group", "edu_specialty_group_major"],
        "scope_notes": ["风险仅来自专业组构成初筛，不代表真实调剂概率或真实分流比例。"],
        "reliability": "B",
    },
    "comparison_query": {
        "source_tables": [
            "edu_university",
            "edu_major",
            "entity_aliases",
            "edu_school_major",
            "edu_university_subject_eval",
            "edu_dual_class",
            "edu_university_employment",
            "edu_school_admission_stats",
            "rysxai_major_market_snapshots",
            "rysxai_major_job_samples",
        ],
        "scope_notes": ["对比工具复用画像、录取、就业摘要和市场样本；第一版只做结构化并列，不直接替用户下最终选择。"],
        "reliability": "B",
    },
    "major_market_reference": {
        "source_tables": ["edu_major", "entity_aliases", "rysxai_major_market_snapshots", "rysxai_major_job_samples"],
        "scope_notes": ["专业市场参考来自第三方招聘样本，不代表学校毕业去向或官方薪资。"],
        "reliability": "B",
    },
    "civil_service_role_search": {
        "source_tables": ["edu_major", "entity_aliases", "civil_service_major_role_candidates", "rysxai_civil_service_roles"],
        "scope_notes": ["考公岗位结果是岗位专业文本命中样本，不等于最终可报判定。"],
        "reliability": "C",
    },
    "data_gap_detection": {
        "source_tables": [],
        "scope_notes": ["缺口检测只描述当前本地库无法支撑的回答边界。"],
        "reliability": "A",
    },
}


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


def _source_trace_for_tool(tool_name: str) -> dict[str, Any] | None:
    trace = _SOURCE_TRACE_REGISTRY.get(tool_name)
    return dict(trace) if trace else None


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

    def rank_to_major_match(
        self,
        province: str,
        major_text: str,
        subject_type: str | None = None,
        score: int | float | str | None = None,
        rank: int | str | None = None,
        year: int | None = None,
        reference_years: list[int] | None = None,
        preferred_regions: list[str] | None = None,
        school_level_filter: str | None = None,
        limit: int = 30,
    ) -> dict[str, Any]:
        """Match an applicant rank to major-level historical rows.

        This tool is narrower than `rank_to_school_match`: it resolves the
        user's major first, then only searches admission rows that look like the
        requested major or a close textual variant.  It still uses historical
        rank thresholds, so the result is a planning reference rather than a
        promise that the school or major can be admitted in a future year.
        """

        missing = _missing_slots({"province": province, "major_text": major_text})
        if missing:
            return _needs(
                "rank_to_major_match",
                {
                    "province": province,
                    "major_text": major_text,
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
                    "rank_to_major_match",
                    {
                        "province": province,
                        "major_text": major_text,
                        "subject_type": subject_type,
                        "score": score,
                        "rank": rank,
                        "year": year,
                    },
                    ["rank_or_score"],
                )
            if not subject_type:
                return _needs(
                    "rank_to_major_match",
                    {
                        "province": province,
                        "major_text": major_text,
                        "subject_type": subject_type,
                        "score": score,
                        "rank": rank,
                        "year": year,
                    },
                    ["subject_type"],
                )

        major_result = self.major_lookup(major_text, limit=1)
        if major_result["status"] != "ok":
            return major_result | {"tool_name": "rank_to_major_match"}
        major = major_result["data"]["selected_major"]

        if applicant_rank is None:
            score_rank_result = self.score_to_rank(province, subject_type, score, year)
            if score_rank_result["status"] != "ok":
                return score_rank_result | {"tool_name": "rank_to_major_match"}
            applicant_rank = _as_int(score_rank_result["data"]["rank_range"].get("lowest_rank"))
            rank_source = "score_to_rank"

        if applicant_rank is None:
            return _needs(
                "rank_to_major_match",
                {
                    "province": province,
                    "major_text": major_text,
                    "subject_type": subject_type,
                    "score": score,
                    "rank": rank,
                    "year": year,
                },
                ["rank_or_score"],
            )

        rows = self.client.query(
            _rank_to_major_match_sql(
                major=major,
                raw_major_text=major_text,
                province=province,
                subject_type=subject_type,
                applicant_rank=applicant_rank,
                requested_year=year,
                reference_years=reference_years,
                preferred_regions=preferred_regions,
                school_level_filter=school_level_filter,
                limit=max(limit * 10, 100),
            )
        )
        buckets, selected_rows = _bucket_major_matches(rows, applicant_rank, limit)
        reference_year_values = sorted(
            {year_value for row in selected_rows if (year_value := _as_int(row.get("year"))) is not None},
            reverse=True,
        )
        history_fallback = bool(year and reference_year_values and year not in reference_year_values)

        input_data = {
            "province": province,
            "major_text": major_text,
            "subject_type": subject_type,
            "score": score,
            "rank": rank,
            "year": year,
            "reference_years": reference_years,
            "preferred_regions": preferred_regions,
            "school_level_filter": school_level_filter,
            "limit": limit,
        }
        source_tables = _merge_source_tables(
            major_result["source_tables"],
            score_rank_result["source_tables"] if score_rank_result else [],
            ["edu_school_admission_stats", "edu_university"],
        )
        normalized_slots = {
            **major_result["normalized_slots"],
            "province": province,
            "subject_type": subject_type,
            "rank": applicant_rank,
        }

        if not selected_rows:
            return tool_result(
                "rank_to_major_match",
                "not_found",
                input_data,
                normalized_slots=normalized_slots,
                data={
                    "applicant": _applicant_rank_payload(
                        province, subject_type, score, applicant_rank, rank_source, score_rank_result
                    ),
                    "major": major,
                    "buckets": {"rush": [], "stable": [], "safe": []},
                },
                data_gaps=["本地专业录取历史"],
                source_tables=source_tables,
                warnings=["本地库未命中该省份/科类/专业可用于位次匹配的专业历史录取参考。"],
            )

        subject_unknown_count = sum(1 for row in selected_rows if not _text(row.get("subject_type")))
        warnings = []
        if history_fallback:
            warnings.append("本地库缺少请求年份的专业录取结果，已使用最近可用历史年份作为参考。")
        if subject_unknown_count:
            warnings.append("部分专业历史记录没有科类字段，已按省份历史参考纳入，需谨慎解读。")

        return tool_result(
            "rank_to_major_match",
            "ok",
            input_data,
            normalized_slots=normalized_slots,
            data={
                "applicant": _applicant_rank_payload(
                    province, subject_type, score, applicant_rank, rank_source, score_rank_result
                ),
                "major": major,
                "reference": {
                    "requested_year": year,
                    "reference_years": reference_year_values,
                    "history_fallback": history_fallback,
                    "matching_rule": "safe: rank<=bao_rank; stable: rank<=stable_rank; rush: rank<=chong_rank",
                    "subject_unknown_count": subject_unknown_count,
                    "major_filter": _major_match_filter_payload(major, major_text),
                },
                "buckets": buckets,
                "coverage": {
                    "candidate_rows": len(rows),
                    "returned_major_rows": sum(len(items) for items in buckets.values()),
                },
            },
            scope_notes=[
                "本工具使用历史专业录取位次做学校-专业行参考，不代表未来录取保证。",
                "专业名称包含大类、试验班、方向等变体时，需要结合当年招生计划和专业组继续确认。",
            ],
            source_tables=source_tables,
            warnings=warnings,
        )

    def specialty_group_lookup(
        self,
        school_text: str,
        major_text: str | None = None,
        province: str | None = None,
        subject_type: str | None = None,
        year: int | None = None,
        group_code: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Return specialty groups and all majors inside each matched group.

        The important product detail is that a user usually cares about the
        whole group, not only the one preferred major.  If the query asks for
        "杭电计科在哪个组", this tool first finds groups containing 计科 and
        then returns every major in those groups so later risk tools can inspect
        adjustment exposure.
        """

        missing = _missing_slots({"school_text": school_text})
        if missing:
            return _needs(
                "specialty_group_lookup",
                {
                    "school_text": school_text,
                    "major_text": major_text,
                    "province": province,
                    "subject_type": subject_type,
                    "year": year,
                    "group_code": group_code,
                },
                missing,
            )

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "specialty_group_lookup"}

        major = None
        major_result: dict[str, Any] | None = None
        if major_text:
            major_result = self.major_lookup(major_text, limit=1)
            if major_result["status"] != "ok":
                return major_result | {"tool_name": "specialty_group_lookup"}
            major = major_result["data"]["selected_major"]

        school = school_result["data"]["selected_school"]
        rows = self.client.query(
            _specialty_group_lookup_sql(
                school=school,
                major=major,
                province=province,
                subject_type=subject_type,
                year=year,
                group_code=group_code,
                limit=max(limit * 20, 100),
            )
        )
        groups = _group_specialty_group_rows(rows, limit)
        normalized = {
            **school_result["normalized_slots"],
            **(major_result["normalized_slots"] if major_result else {}),
            "province": province,
            "subject_type": subject_type,
            "year": year,
            "group_code": group_code,
        }
        source_tables = _merge_source_tables(
            school_result["source_tables"],
            major_result["source_tables"] if major_result else [],
            ["edu_college_specialty_group", "edu_specialty_group_major"],
        )
        if not groups:
            return tool_result(
                "specialty_group_lookup",
                "not_found",
                {
                    "school_text": school_text,
                    "major_text": major_text,
                    "province": province,
                    "subject_type": subject_type,
                    "year": year,
                    "group_code": group_code,
                    "limit": limit,
                },
                normalized_slots=normalized,
                data={"school": school, "major": major or {}, "groups": []},
                data_gaps=["专业组样本"],
                source_tables=source_tables,
                warnings=["本地库未命中符合条件的专业组样本，不能推断该专业组不存在。"],
            )

        return tool_result(
            "specialty_group_lookup",
            "ok",
            {
                "school_text": school_text,
                "major_text": major_text,
                "province": province,
                "subject_type": subject_type,
                "year": year,
                "group_code": group_code,
                "limit": limit,
            },
            normalized_slots=normalized,
            data={"school": school, "major": major or {}, "groups": groups},
            scope_notes=[
                "专业组样本来自本地招生专业组表；专业组构成不等于入学后真实分流比例。",
                "省份、科类、年份都会影响专业组，缺少这些条件时只能作为宽泛样本。",
            ],
            source_tables=source_tables,
        )

    def subject_requirement_lookup(
        self,
        major_text: str,
        school_text: str | None = None,
        province: str | None = None,
        subject_type: str | None = None,
        year: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Return subject requirements observed for a major.

        This is a focused version of professional-group lookup.  It keeps the
        raw rows because requirements can vary by school/province/year, while
        also returning a de-duplicated summary list for quick agent answers.
        """

        missing = _missing_slots({"major_text": major_text})
        if missing:
            return _needs(
                "subject_requirement_lookup",
                {
                    "major_text": major_text,
                    "school_text": school_text,
                    "province": province,
                    "subject_type": subject_type,
                    "year": year,
                },
                missing,
            )

        major_result = self.major_lookup(major_text, limit=1)
        if major_result["status"] != "ok":
            return major_result | {"tool_name": "subject_requirement_lookup"}

        school = None
        school_result: dict[str, Any] | None = None
        if school_text:
            school_result = self.school_lookup(school_text, limit=1)
            if school_result["status"] != "ok":
                return school_result | {"tool_name": "subject_requirement_lookup"}
            school = school_result["data"]["selected_school"]

        major = major_result["data"]["selected_major"]
        rows = self.client.query(_subject_requirement_lookup_sql(major, school, province, subject_type, year, limit))
        requirements = _distinct_texts(row.get("subject_requirement") for row in rows)
        status = "ok" if requirements else "not_found"
        return tool_result(
            "subject_requirement_lookup",
            status,
            {
                "major_text": major_text,
                "school_text": school_text,
                "province": province,
                "subject_type": subject_type,
                "year": year,
                "limit": limit,
            },
            normalized_slots={
                **major_result["normalized_slots"],
                **(school_result["normalized_slots"] if school_result else {}),
                "province": province,
                "subject_type": subject_type,
                "year": year,
            },
            data={"major": major, "school": school or {}, "requirements": requirements, "records": rows},
            scope_notes=["选科要求来自招生计划/专业组样本，必须按省份、年份和科类理解。"],
            data_gaps=[] if requirements else ["选科要求样本"],
            source_tables=_merge_source_tables(
                major_result["source_tables"],
                school_result["source_tables"] if school_result else [],
                ["edu_college_specialty_group", "edu_specialty_group_major"],
            ),
            warnings=[] if requirements else ["本地库未命中该条件下的选科要求样本。"],
        )

    def school_department_major_list(
        self,
        school_text: str,
        department_text: str | None = None,
        major_text: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Return departments and their recorded majors for one school."""

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "school_department_major_list"}

        major = None
        major_result: dict[str, Any] | None = None
        if major_text:
            major_result = self.major_lookup(major_text, limit=1)
            if major_result["status"] != "ok":
                return major_result | {"tool_name": "school_department_major_list"}
            major = major_result["data"]["selected_major"]

        school = school_result["data"]["selected_school"]
        rows = self.client.query(_school_department_major_list_sql(school, department_text, major, limit))
        departments = _group_department_major_rows(rows)
        return tool_result(
            "school_department_major_list",
            "ok" if departments else "not_found",
            {
                "school_text": school_text,
                "department_text": department_text,
                "major_text": major_text,
                "limit": limit,
            },
            normalized_slots={
                **school_result["normalized_slots"],
                **(major_result["normalized_slots"] if major_result else {}),
            },
            data={"school": school, "departments": departments},
            scope_notes=["院系专业关系来自学校院系专业表，不等于某省某年招生计划。"],
            data_gaps=[] if departments else ["院系专业关系"],
            source_tables=_merge_source_tables(
                school_result["source_tables"],
                major_result["source_tables"] if major_result else [],
                ["edu_university_department", "edu_university_department_major"],
            ),
        )

    def plan_history(
        self,
        school_text: str,
        major_text: str | None = None,
        province: str | None = None,
        years: list[int] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Return招生计划 rows from the normalized qjjh plan table."""

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "plan_history"}

        major = None
        major_result: dict[str, Any] | None = None
        if major_text:
            major_result = self.major_lookup(major_text, limit=1)
            if major_result["status"] != "ok":
                return major_result | {"tool_name": "plan_history"}
            major = major_result["data"]["selected_major"]

        school = school_result["data"]["selected_school"]
        rows = self.client.query(_plan_history_sql(school, major, province, years, limit))
        return tool_result(
            "plan_history",
            "ok" if rows else "not_found",
            {
                "school_text": school_text,
                "major_text": major_text,
                "province": province,
                "years": years,
                "limit": limit,
            },
            normalized_slots={
                **school_result["normalized_slots"],
                **(major_result["normalized_slots"] if major_result else {}),
                "province": province,
            },
            data={"school": school, "major": major or {}, "records": rows},
            scope_notes=["招生计划按学校、省份、年份和专业理解；计划数不等于实际录取人数。"],
            data_gaps=[] if rows else ["招生计划历史"],
            source_tables=_merge_source_tables(
                school_result["source_tables"],
                major_result["source_tables"] if major_result else [],
                ["edu_qjjh_plan"],
            ),
        )

    def employment_summary(self, school_text: str, limit: int = 5) -> dict[str, Any]:
        """Return school-level employment and further-study summaries."""

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "employment_summary"}

        school = school_result["data"]["selected_school"]
        rows = [
            _decode_json_fields(
                row,
                ["employment_data", "top_employment_industries", "top_employment_regions", "top_employers"],
            )
            for row in self.client.query(_employment_summary_sql(school, limit))
        ]
        return tool_result(
            "employment_summary",
            "ok" if rows else "not_found",
            {"school_text": school_text, "limit": limit},
            normalized_slots=school_result["normalized_slots"],
            data={"school": school, "records": rows},
            scope_notes=[
                "学校级就业/升学摘要不能代表某个专业的真实就业去向、薪资或升学率。",
            ],
            data_gaps=[] if rows else ["学校级就业/升学摘要"],
            source_tables=_merge_source_tables(school_result["source_tables"], ["edu_university_employment"]),
        )

    def source_trace_lookup(self, tool_name: str | None = None) -> dict[str, Any]:
        """Explain source tables, data scope, and reliability for retrieval tools."""

        if tool_name:
            trace = _source_trace_for_tool(tool_name)
            if not trace:
                return tool_result(
                    "source_trace_lookup",
                    "not_found",
                    {"tool_name": tool_name},
                    warnings=["暂未登记该工具的数据来源说明。"],
                )
            return tool_result(
                "source_trace_lookup",
                "ok",
                {"tool_name": tool_name},
                data=trace,
                scope_notes=trace.get("scope_notes", []),
                source_tables=trace.get("source_tables", []),
            )

        traces = {name: _source_trace_for_tool(name) for name in _SOURCE_TRACE_REGISTRY}
        return tool_result(
            "source_trace_lookup",
            "ok",
            {"tool_name": tool_name},
            data={"tools": traces},
            scope_notes=["来源解释是工具级口径说明，不替代具体回答中的原始来源链接。"],
        )

    def transfer_policy_lookup(self, school_text: str) -> dict[str, Any]:
        """Return crawled transfer-policy clues for one school."""

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "transfer_policy_lookup"}

        school = school_result["data"]["selected_school"]
        row = _first_row(self.client.query(_transfer_policy_lookup_sql(school)))
        if not row:
            return tool_result(
                "transfer_policy_lookup",
                "not_found",
                {"school_text": school_text},
                normalized_slots=school_result["normalized_slots"],
                data={"school": school, "policy": {}},
                data_gaps=["转专业政策线索"],
                source_tables=_merge_source_tables(school_result["source_tables"], ["rysxai_transfer_policies"]),
                warnings=["本地库未命中该学校的转专业政策线索。"],
            )

        policy = _decode_json_fields(row, ["tags_json", "warnings_json", "change_profession_by_faculty_json"])
        has_policy = _as_int(policy.get("has_transfer_policy")) == 1
        return tool_result(
            "transfer_policy_lookup",
            "ok" if has_policy else "partial",
            {"school_text": school_text},
            normalized_slots=school_result["normalized_slots"],
            data={"school": school, "policy": policy},
            scope_notes=[
                "转专业政策来自第三方线索库，必须回到学校官网、教务处通知或招生章程复核后再给高风险结论。",
            ],
            data_gaps=[] if has_policy else ["可复核的官方转专业政策"],
            source_tables=_merge_source_tables(school_result["source_tables"], ["rysxai_transfer_policies"]),
            warnings=[] if has_policy else ["该第三方记录未暴露明确转专业政策正文。"],
        )

    def fee_and_campus_lookup(
        self,
        school_text: str,
        major_text: str | None = None,
        province: str | None = None,
        year: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Return fee clues from招生计划 rows and mark campus as a known gap."""

        school_result = self.school_lookup(school_text, limit=1)
        if school_result["status"] != "ok":
            return school_result | {"tool_name": "fee_and_campus_lookup"}

        major = None
        major_result: dict[str, Any] | None = None
        if major_text:
            major_result = self.major_lookup(major_text, limit=1)
            if major_result["status"] != "ok":
                return major_result | {"tool_name": "fee_and_campus_lookup"}
            major = major_result["data"]["selected_major"]

        school = school_result["data"]["selected_school"]
        rows = self.client.query(_fee_and_campus_lookup_sql(school, major, province, year, limit))
        return tool_result(
            "fee_and_campus_lookup",
            "partial" if rows else "not_found",
            {
                "school_text": school_text,
                "major_text": major_text,
                "province": province,
                "year": year,
                "limit": limit,
            },
            normalized_slots={
                **school_result["normalized_slots"],
                **(major_result["normalized_slots"] if major_result else {}),
                "province": province,
                "year": year,
            },
            data={"school": school, "major": major or {}, "fee_items": rows, "campus_items": []},
            scope_notes=["学费线索来自招生计划表；当前库没有稳定校区字段，不能猜测就读校区。"],
            data_gaps=["校区信息"],
            source_tables=_merge_source_tables(
                school_result["source_tables"],
                major_result["source_tables"] if major_result else [],
                ["edu_university_plan_config", "edu_university_plan_special_group", "edu_university_plan_special"],
            ),
            warnings=[] if rows else ["本地库未命中符合条件的学费线索。"],
        )

    def specialty_group_risk(
        self,
        school_text: str,
        province: str | None = None,
        subject_type: str | None = None,
        year: int | None = None,
        group_code: str | None = None,
        major_text: str | None = None,
    ) -> dict[str, Any]:
        """Return a conservative specialty-group risk summary.

        This first version only describes observable group composition and
        adjustment flags.  It deliberately does not infer real streaming ratios,
        because the current database does not contain that outcome evidence.
        """

        group_result = self.specialty_group_lookup(
            school_text=school_text,
            major_text=major_text,
            province=province,
            subject_type=subject_type,
            year=year,
            group_code=group_code,
            limit=10,
        )
        if group_result["status"] != "ok":
            return group_result | {"tool_name": "specialty_group_risk"}

        groups = group_result["data"]["groups"]
        risk = _specialty_group_risk_payload(groups)
        return tool_result(
            "specialty_group_risk",
            "ok",
            {
                "school_text": school_text,
                "province": province,
                "subject_type": subject_type,
                "year": year,
                "group_code": group_code,
                "major_text": major_text,
            },
            normalized_slots=group_result["normalized_slots"],
            data={"risk": risk, "groups": groups},
            scope_notes=[
                "这是基于专业组构成的调剂风险初筛，不等于真实分流比例或最终调剂结果。",
            ],
            data_gaps=["专业组真实分流比例", "冷门专业人工标签"],
            source_tables=group_result["source_tables"],
        )

    def comparison_query(
        self,
        target_type: str,
        target_texts: list[str],
        major_text: str | None = None,
        province: str | None = None,
        subject_type: str | None = None,
        score: int | float | str | None = None,
        rank: int | str | None = None,
        year: int | None = None,
        dimensions: list[str] | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Compare schools, majors, or school-major choices side by side.

        第一版的目标是“把可比信息摆齐”，不是生成最终志愿决策。这里复用已
        有工具的结果，保留每个支撑工具的 scope_notes / data_gaps / warnings，
        让上层 agent 可以诚实说明哪些维度有数据、哪些维度只是缺口。
        """

        clean_targets = _distinct_texts(target_texts or [])
        normalized_type = str(target_type or "").strip()
        missing = []
        if not normalized_type:
            missing.append("target_type")
        if len(clean_targets) < 2:
            missing.append("target_texts")
        if normalized_type == "school_major" and not major_text:
            missing.append("major_text")
        if missing:
            return _needs(
                "comparison_query",
                {
                    "target_type": target_type,
                    "target_texts": target_texts,
                    "major_text": major_text,
                    "province": province,
                    "subject_type": subject_type,
                    "score": score,
                    "rank": rank,
                    "year": year,
                    "dimensions": dimensions,
                    "limit": limit,
                },
                missing,
            )

        if normalized_type not in {"school", "major", "school_major"}:
            return tool_result(
                "comparison_query",
                "needs_clarification",
                {
                    "target_type": target_type,
                    "target_texts": target_texts,
                    "major_text": major_text,
                    "province": province,
                    "subject_type": subject_type,
                    "score": score,
                    "rank": rank,
                    "year": year,
                    "dimensions": dimensions,
                    "limit": limit,
                },
                needs_clarification=["target_type"],
                warnings=["target_type 仅支持 school、major、school_major。"],
            )

        targets = []
        source_tables: list[str] = []
        data_gaps: list[str] = []
        warnings: list[str] = []
        for target_text in clean_targets[: max(int(limit), 1)]:
            supporting_results = self._comparison_supporting_results(
                target_type=normalized_type,
                target_text=target_text,
                major_text=major_text,
                province=province,
                subject_type=subject_type,
                score=score,
                rank=rank,
                year=year,
            )
            for result in supporting_results:
                source_tables = _merge_source_tables(source_tables, result.get("source_tables") or [])
                data_gaps.extend(result.get("data_gaps") or [])
                warnings.extend(result.get("warnings") or [])
            targets.append(
                {
                    "target_text": target_text,
                    "status": _comparison_target_status(supporting_results),
                    "normalized_slots": _merge_normalized_slots(supporting_results),
                    "supporting_results": supporting_results,
                }
            )

        return tool_result(
            "comparison_query",
            _comparison_overall_status(targets),
            {
                "target_type": target_type,
                "target_texts": target_texts,
                "major_text": major_text,
                "province": province,
                "subject_type": subject_type,
                "score": score,
                "rank": rank,
                "year": year,
                "dimensions": dimensions,
                "limit": limit,
            },
            normalized_slots={
                "target_type": normalized_type,
                "target_texts": clean_targets,
                "major_text": major_text,
                "province": province,
                "subject_type": subject_type,
                "year": year,
            },
            data={
                "target_type": normalized_type,
                "targets": targets,
                "dimensions": dimensions or _default_comparison_dimensions(normalized_type, bool(major_text)),
                "decision_policy": "第一版只输出结构化并列信息；最终选择需结合考生偏好、分数位次和官方政策继续判断。",
            },
            scope_notes=[
                "对比工具第一版只做结构化并列，不直接替用户做最终选择。",
                "不同口径不能混用：学校级就业不代表校专业级就业，专业通用薪资不代表某校该专业薪资。",
                "涉及分数/位次时只使用历史参考，不保证未来录取。",
            ],
            data_gaps=_distinct_texts(data_gaps),
            source_tables=source_tables,
            warnings=_distinct_texts(warnings),
        )

    def _comparison_supporting_results(
        self,
        *,
        target_type: str,
        target_text: str,
        major_text: str | None,
        province: str | None,
        subject_type: str | None,
        score: int | float | str | None,
        rank: int | str | None,
        year: int | None,
    ) -> list[dict[str, Any]]:
        """Build the per-target evidence pack for `comparison_query`.

        这里没有直接写 SQL，而是复用已经测试过的工具。这样对比工具天然继承
        原工具的数据口径、缺口提示和来源说明，减少重复 SQL 带来的口径漂移。
        """

        if target_type == "major":
            return [
                self.major_profile(target_text),
                self.major_market_reference(target_text, sample_limit=10),
            ]

        if target_type == "school_major":
            results = [
                self.school_major_profile(target_text, major_text or "", province=province, subject_type=subject_type, year=year),
                self.employment_summary(target_text, limit=3),
            ]
            if province or subject_type or year:
                results.append(
                    self.admission_history(
                        school_text=target_text,
                        major_text=major_text,
                        province=province,
                        subject_type=subject_type,
                        years=[year] if year else None,
                        limit=10,
                    )
                )
            if score or rank:
                results.append(
                    self.rank_to_major_match(
                        province=province or "",
                        major_text=major_text or "",
                        subject_type=subject_type,
                        score=score,
                        rank=rank,
                        year=year,
                        limit=10,
                    )
                )
            return results

        results = [self.school_profile(target_text)]
        if major_text:
            results.append(
                self.school_major_profile(target_text, major_text, province=province, subject_type=subject_type, year=year)
            )
        if province or subject_type or year:
            results.append(
                self.admission_history(
                    school_text=target_text,
                    major_text=major_text,
                    province=province,
                    subject_type=subject_type,
                    years=[year] if year else None,
                    limit=10,
                )
            )
        return results

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
            "comparison_query": {
                "target_profiles": "对比对象画像",
                "admission_context": "录取历史上下文",
                "employment_context": "就业/升学对比口径",
                "decision_preferences": "考生偏好权重",
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


def _specialty_group_lookup_sql(
    school: dict[str, Any],
    major: dict[str, Any] | None,
    province: str | None,
    subject_type: str | None,
    year: int | None,
    group_code: str | None,
    limit: int,
) -> str:
    school_id = str(school.get("school_id") or "")
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
    if group_code:
        clauses.append(f"g.group_code = {sql_quote(group_code)}")
    if major:
        clauses.append(
            f"""g.id IN (
  SELECT gm_filter.group_id
  FROM edu_specialty_group_major gm_filter
  WHERE (gm_filter.deleted IS NULL OR gm_filter.deleted = b'0')
    AND {_major_code_or_name_clause("gm_filter.special_code", "gm_filter.special_name", major)}
)"""
        )

    return f"""
SELECT g.id AS group_db_id, g.year, g.province, g.group_code, g.group_name, g.group_type,
       g.plan_count AS group_plan_count, g.admission_count AS group_admission_count,
       g.min_score AS group_min_score, g.min_rank AS group_min_rank,
       g.allow_adjustment, gm.special_code, gm.special_name,
       gm.plan_count AS major_plan_count, gm.admission_count AS major_admission_count,
       gm.min_score AS major_min_score, gm.min_rank AS major_min_rank,
       gm.subject_requirement, gm.remark, gm.batch
FROM edu_college_specialty_group g
JOIN edu_specialty_group_major gm ON gm.group_id = g.id
WHERE {' AND '.join(clauses)}
ORDER BY g.year DESC, g.province, g.group_code, gm.special_code, gm.special_name
LIMIT {int(limit)}
""".strip()


def _subject_requirement_lookup_sql(
    major: dict[str, Any],
    school: dict[str, Any] | None,
    province: str | None,
    subject_type: str | None,
    year: int | None,
    limit: int,
) -> str:
    clauses = [
        "(g.deleted IS NULL OR g.deleted = b'0')",
        "(gm.deleted IS NULL OR gm.deleted = b'0')",
        _major_code_or_name_clause("gm.special_code", "gm.special_name", major),
        "gm.subject_requirement IS NOT NULL",
        "gm.subject_requirement <> ''",
    ]
    if school:
        clauses.append(f"g.school_id = {sql_quote(school.get('school_id'))}")
    if province:
        province_id = _province_id(province) or str(province)
        clauses.append(f"g.province = {sql_quote(province_id)}")
    if subject_type:
        clauses.append(f"g.group_type = {sql_quote(subject_type)}")
    if year:
        clauses.append(f"g.year = {int(year)}")

    return f"""
SELECT COALESCE(u.name, g.school_id) AS school_name, g.school_id, g.year, g.province,
       g.group_code, g.group_name, g.group_type, gm.special_code, gm.special_name,
       gm.subject_requirement, gm.batch, gm.remark
FROM edu_college_specialty_group g
JOIN edu_specialty_group_major gm ON gm.group_id = g.id
LEFT JOIN edu_university u ON u.school_id = CAST(g.school_id AS UNSIGNED)
WHERE {' AND '.join(clauses)}
ORDER BY g.year DESC, g.province, school_name, g.group_code
LIMIT {int(limit)}
""".strip()


def _school_department_major_list_sql(
    school: dict[str, Any],
    department_text: str | None,
    major: dict[str, Any] | None,
    limit: int,
) -> str:
    school_code = _text(school.get("code"))
    school_id = _text(school.get("school_id"))
    clauses = [
        "(d.deleted IS NULL OR d.deleted = b'0')",
        "(dm.deleted IS NULL OR dm.deleted = b'0')",
        f"(d.school_id = {sql_quote(school_code)} OR d.school_id = {sql_quote(school_id)})",
    ]
    if department_text:
        clauses.append(f"d.dept_name LIKE {sql_quote(f'%{department_text}%')}")
    if major:
        clauses.append(_major_code_or_name_clause("dm.major_code", "dm.major_name", major))

    return f"""
SELECT d.id AS dept_id, d.dept_name, d.website_url, d.major_count,
       dm.major_code, dm.major_name, dm.education_level,
       dm.is_nation_feature, dm.is_nation_first_class, dm.subject_eval_level
FROM edu_university_department d
JOIN edu_university_department_major dm ON dm.dept_id = d.id
WHERE {' AND '.join(clauses)}
ORDER BY d.dept_name, dm.sort_order, dm.major_code
LIMIT {int(limit)}
""".strip()


def _plan_history_sql(
    school: dict[str, Any],
    major: dict[str, Any] | None,
    province: str | None,
    years: list[int] | None,
    limit: int,
) -> str:
    school_code = _text(school.get("code"))
    school_id = _text(school.get("school_id"))
    clauses = [
        "(deleted IS NULL OR deleted = 0)",
        f"(school_id = {sql_quote(school_code)} OR school_id = {sql_quote(school_id)})",
    ]
    if major:
        clauses.append(_major_code_or_name_clause("special_id", "special_name", major))
    if province:
        province_id = _province_id(province) or str(province)
        clauses.append(f"province_id = {sql_quote(province_id)}")
    if years:
        clauses.append("year IN (" + ", ".join(str(int(year)) for year in years) + ")")

    return f"""
SELECT school_id, year, province_id, category_type, special_id, special_name,
       academy_name, group_name, plan_count, subject_requirement_text, remark
FROM edu_qjjh_plan
WHERE {' AND '.join(clauses)}
ORDER BY year DESC, province_id, special_name
LIMIT {int(limit)}
""".strip()


def _employment_summary_sql(school: dict[str, Any], limit: int) -> str:
    school_id = _text(school.get("school_id"))
    return f"""
SELECT year, employment_rate, further_study_rate, employment_data, avg_salary,
       top_employment_industries, top_employment_regions, top_employers
FROM edu_university_employment
WHERE (deleted IS NULL OR deleted = b'0')
  AND school_id = {sql_quote(school_id)}
ORDER BY CAST(year AS UNSIGNED) DESC
LIMIT {int(limit)}
""".strip()


def _transfer_policy_lookup_sql(school: dict[str, Any]) -> str:
    return f"""
SELECT school_id, school_name, province, city, school_type, property, school_level,
       source_name, source_level, data_scope, source_url, source_endpoint,
       has_transfer_policy, has_faculty_policy, faculty_policy_count,
       change_profession, change_profession_application_condition,
       change_profession_admission_requirement, change_profession_assessment,
       change_profession_by_faculty_json, warnings_json
FROM rysxai_transfer_policies
WHERE school_name = {sql_quote(school.get('name'))}
   OR school_id = {sql_quote(school.get('code'))}
   OR school_id = {sql_quote(school.get('school_id'))}
ORDER BY has_transfer_policy DESC, updated_at DESC
LIMIT 1
""".strip()


def _fee_and_campus_lookup_sql(
    school: dict[str, Any],
    major: dict[str, Any] | None,
    province: str | None,
    year: int | None,
    limit: int,
) -> str:
    school_code = _text(school.get("code"))
    school_id = _text(school.get("school_id"))
    clauses = [
        "(cfg.deleted IS NULL OR cfg.deleted = 0)",
        "(pg.deleted IS NULL OR pg.deleted = 0)",
        "(ps.deleted IS NULL OR ps.deleted = 0)",
        f"(cfg.school_id = {sql_quote(school_code)} OR cfg.school_id = {sql_quote(school_id)})",
    ]
    if major:
        clauses.append(_major_code_or_name_clause("ps.special_id", "ps.special_name", major))
    if province:
        province_id = _province_id(province) or str(province)
        clauses.append(f"cfg.province_id = {sql_quote(province_id)}")
    if year:
        clauses.append(f"cfg.year = {int(year)}")

    return f"""
SELECT cfg.year, cfg.province_id, cfg.type_id, cfg.batch_id,
       pg.group_id, pg.group_name, pg.elective_info,
       ps.special_id, ps.special_name, ps.plan_count, ps.tuition_year, ps.tuition_fee
FROM edu_university_plan_special ps
JOIN edu_university_plan_special_group pg ON pg.id = ps.group_id
JOIN edu_university_plan_config cfg ON cfg.id = pg.config_id
WHERE {' AND '.join(clauses)}
ORDER BY cfg.year DESC, cfg.province_id, pg.group_id, ps.special_name
LIMIT {int(limit)}
""".strip()


def _province_id(province: str) -> str | None:
    text = str(province).strip()
    if text.isdigit():
        return text
    text = text.removesuffix("省").removesuffix("市").removesuffix("壮族自治区").removesuffix("自治区").removesuffix("回族自治区").removesuffix("维吾尔自治区")
    return PROVINCE_ID_BY_NAME.get(text)


def _major_code_or_name_clause(code_column: str, name_column: str, major: dict[str, Any]) -> str:
    """Build a resilient major predicate for mixed-source enrollment tables.

    Several local enrollment tables store canonical major codes when they have
    them, but many imported rows only keep a display name such as
    "计算机科学与技术((下沙校区))".  The tool layer therefore combines code exact
    match, name exact match, and name contains match.  This keeps canonical
    matching precise while still recovering rows where the source appended
    campus, tuition, cooperation-program, or health-requirement notes.
    """

    major_code = _text(major.get("code") or major.get("special_id"))
    major_name = _text(major.get("special_name"))
    clauses: list[str] = []
    if major_code:
        clauses.append(f"{code_column} = {sql_quote(major_code)}")
    if major_name:
        clauses.append(f"{name_column} = {sql_quote(major_name)}")
        clauses.append(f"{name_column} LIKE {sql_quote(f'%{major_name}%')}")
    return "(" + " OR ".join(clauses or ["1 = 0"]) + ")"


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


def _rank_to_major_match_sql(
    major: dict[str, Any],
    raw_major_text: str,
    province: str,
    subject_type: str | None,
    applicant_rank: int,
    requested_year: int | None,
    reference_years: list[int] | None,
    preferred_regions: list[str] | None,
    school_level_filter: str | None,
    limit: int,
) -> str:
    major_filter = _major_admission_filter_sql(major, raw_major_text)
    clauses = [
        "(a.deleted IS NULL OR a.deleted = b'0')",
        f"a.province_name = {sql_quote(province)}",
        "a.stable_rank IS NOT NULL AND a.stable_rank > 0",
        "(a.major_name IS NOT NULL AND a.major_name <> '')",
        major_filter,
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
       a.major_code, a.major_name, a.subject_type, a.year,
       a.stable_score, a.stable_rank, a.chong_score, a.chong_rank,
       a.bao_score, a.bao_rank, a.batch, a.subject_requirement,
       a.plan_count, a.admission_count, a.remark
FROM edu_school_admission_stats a
-- Keep the same join rule as school-level matching: admission rows store the
-- national school code in `a.school_id`, not the platform-internal
-- `edu_university.school_id`.  The school name guard prevents metadata drift
-- when codes are missing or imported inconsistently.
LEFT JOIN edu_university u ON u.code = CAST(a.school_id AS CHAR) AND u.name = a.school_name
WHERE {' AND '.join(clauses)}
ORDER BY {subject_order}, a.year DESC, ABS(a.stable_rank - {int(applicant_rank)}), a.school_name, a.major_name
LIMIT {int(limit)}
""".strip()


def _major_admission_filter_sql(major: dict[str, Any], raw_major_text: str) -> str:
    """Build the major-name/code filter for historical admission rows.

    `edu_school_admission_stats` is not perfectly normalized: some rows have a
    major code, some only have names like "计算机类" or "计算机科学与技术(试验班)".
    The filter therefore combines safe exact code matching with controlled name
    matching.  Very short raw nicknames such as "计科" never become a LIKE
    clause; they must first resolve through `entity_aliases`.
    """

    filters: list[str] = []
    major_code = _text(major.get("code")) or _text(major.get("special_id"))
    major_name = _text(major.get("special_name"))
    raw_text = _text(raw_major_text)

    if major_code:
        filters.append(f"a.major_code = {sql_quote(major_code)}")
    if major_name:
        filters.append(f"a.major_name = {sql_quote(major_name)}")
        filters.append(f"a.major_name LIKE {sql_quote(f'%{major_name}%')}")
    if _major_admission_raw_like_allowed(raw_text, major_name):
        filters.append(f"a.major_name LIKE {sql_quote(f'%{raw_text}%')}")

    if not filters:
        # This branch should be rare because `major_lookup` must resolve first,
        # but keeping the SQL valid makes defensive error envelopes possible if
        # a future caller passes an incomplete fake major in tests.
        filters.append("1 = 0")
    return "(" + " OR ".join(filters) + ")"


def _major_admission_raw_like_allowed(raw_text: str, canonical_name: str) -> bool:
    normalized_raw = "".join(raw_text.split()).lower()
    normalized_canonical = "".join(canonical_name.split()).lower()
    return len(normalized_raw) >= 3 and normalized_raw not in {normalized_canonical, ""}


def _major_match_filter_payload(major: dict[str, Any], raw_major_text: str) -> dict[str, Any]:
    return {
        "raw_major_text": raw_major_text,
        "canonical_major_code": _optional_text(major.get("code") or major.get("special_id")),
        "canonical_major_name": _optional_text(major.get("special_name")),
        "raw_text_like_enabled": _major_admission_raw_like_allowed(
            _text(raw_major_text),
            _text(major.get("special_name")),
        ),
    }


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
  AND {_major_code_or_name_clause("gm.special_code", "gm.special_name", major)}
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


def _distinct_texts(values: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _comparison_target_status(results: list[dict[str, Any]]) -> str:
    """Compress several supporting tool statuses into one target status."""

    statuses = [str(result.get("status") or "") for result in results]
    if not statuses:
        return "not_found"
    if any(status == "ok" for status in statuses):
        return "partial" if any(status in {"partial", "not_found", "needs_clarification", "error"} for status in statuses) else "ok"
    if any(status == "partial" for status in statuses):
        return "partial"
    if any(status == "needs_clarification" for status in statuses):
        return "needs_clarification"
    if any(status == "error" for status in statuses):
        return "error"
    return "not_found"


def _comparison_overall_status(targets: list[dict[str, Any]]) -> str:
    """Return an overall status for a comparison result."""

    statuses = [str(target.get("status") or "") for target in targets]
    if not statuses:
        return "not_found"
    if all(status == "ok" for status in statuses):
        return "ok"
    if any(status in {"ok", "partial"} for status in statuses):
        return "partial"
    if any(status == "needs_clarification" for status in statuses):
        return "needs_clarification"
    if any(status == "error" for status in statuses):
        return "error"
    return "not_found"


def _merge_normalized_slots(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge normalized slots from supporting results for easier UI display."""

    merged: dict[str, Any] = {}
    for result in results:
        normalized = result.get("normalized_slots")
        if isinstance(normalized, dict):
            for key, value in normalized.items():
                if value not in (None, "", []):
                    merged.setdefault(key, value)
    return merged


def _default_comparison_dimensions(target_type: str, has_major_context: bool) -> list[str]:
    """Default dimensions shown to users when no explicit dimension is passed."""

    if target_type == "major":
        return ["专业定位", "学习内容", "通用就业方向", "市场样本薪资", "考公/政策缺口"]
    if target_type == "school_major" or has_major_context:
        return ["学校基础", "专业基础", "学科评估", "录取历史", "学校级就业", "校专业级数据缺口"]
    return ["学校基础", "学校层次", "学科评估", "学校级就业/升学", "录取历史上下文"]


def _group_specialty_group_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    group_index: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    for row in rows:
        key = (
            _text(row.get("year")),
            _text(row.get("province")),
            _text(row.get("group_code")),
            _text(row.get("group_name")),
        )
        if key not in group_index:
            if len(groups) >= limit:
                continue
            group = {
                "group_db_id": _optional_text(row.get("group_db_id")),
                "year": _as_int(row.get("year")),
                "province": _optional_text(row.get("province")),
                "group_code": _optional_text(row.get("group_code")),
                "group_name": _optional_text(row.get("group_name")),
                "group_type": _optional_text(row.get("group_type")),
                "group_plan_count": _as_int(row.get("group_plan_count")),
                "group_admission_count": _as_int(row.get("group_admission_count")),
                "group_min_score": _as_int(row.get("group_min_score")),
                "group_min_rank": _as_int(row.get("group_min_rank")),
                "allow_adjustment": _as_int(row.get("allow_adjustment")),
                "majors": [],
            }
            group_index[key] = group
            groups.append(group)
        group_index[key]["majors"].append(
            {
                "special_code": _optional_text(row.get("special_code")),
                "special_name": _optional_text(row.get("special_name")),
                "plan_count": _as_int(row.get("major_plan_count")),
                "admission_count": _as_int(row.get("major_admission_count")),
                "min_score": _as_int(row.get("major_min_score")),
                "min_rank": _as_int(row.get("major_min_rank")),
                "subject_requirement": _optional_text(row.get("subject_requirement")),
                "batch": _optional_text(row.get("batch")),
                "remark": _optional_text(row.get("remark")),
            }
        )

    return groups


def _group_department_major_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    departments: list[dict[str, Any]] = []
    department_index: dict[str, dict[str, Any]] = {}

    for row in rows:
        dept_id = _text(row.get("dept_id")) or _text(row.get("dept_name"))
        if dept_id not in department_index:
            department = {
                "dept_id": _optional_text(row.get("dept_id")),
                "dept_name": _optional_text(row.get("dept_name")),
                "website_url": _optional_text(row.get("website_url")),
                "major_count": _as_int(row.get("major_count")),
                "majors": [],
            }
            department_index[dept_id] = department
            departments.append(department)
        department_index[dept_id]["majors"].append(
            {
                "major_code": _optional_text(row.get("major_code")),
                "major_name": _optional_text(row.get("major_name")),
                "education_level": _optional_text(row.get("education_level")),
                "is_nation_feature": _as_int(row.get("is_nation_feature")),
                "is_nation_first_class": _as_int(row.get("is_nation_first_class")),
                "subject_eval_level": _optional_text(row.get("subject_eval_level")),
            }
        )

    return departments


def _specialty_group_risk_payload(groups: list[dict[str, Any]]) -> dict[str, Any]:
    all_majors = [major for group in groups for major in group.get("majors", [])]
    allow_adjustment_values = [
        value for group in groups if (value := _as_int(group.get("allow_adjustment"))) is not None
    ]
    small_plan_majors = [
        major
        for major in all_majors
        if (plan_count := _as_int(major.get("plan_count"))) is not None and plan_count <= 2
    ]
    unknown_plan_count = sum(1 for major in all_majors if _as_int(major.get("plan_count")) is None)
    risk_flags = []
    if any(value == 1 for value in allow_adjustment_values):
        risk_flags.append("允许调剂，需要关注组内全部专业。")
    if len(all_majors) >= 6:
        risk_flags.append("组内专业数量较多，调剂不确定性较高。")
    if small_plan_majors:
        risk_flags.append("存在计划数很少的专业，需结合当年招生章程谨慎判断。")
    if unknown_plan_count:
        risk_flags.append("部分组内专业缺少计划数，风险判断不完整。")

    return {
        "group_count": len(groups),
        "major_count": len(all_majors),
        "allow_adjustment": any(value == 1 for value in allow_adjustment_values) if allow_adjustment_values else None,
        "small_plan_major_count": len(small_plan_majors),
        "unknown_plan_major_count": unknown_plan_count,
        "risk_flags": risk_flags,
    }


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


def _bucket_major_matches(
    rows: list[dict[str, Any]],
    applicant_rank: int,
    limit: int,
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {"rush": [], "stable": [], "safe": []}
    selected_rows: list[dict[str, Any]] = []
    seen_major_rows: set[str] = set()

    for row in rows:
        school_key = _text(row.get("school_id")) or _text(row.get("school_name"))
        major_key = _text(row.get("major_code")) or _text(row.get("major_name"))
        batch_key = _text(row.get("batch"))
        opportunity_key = "|".join([school_key, major_key, batch_key])
        if not school_key or not major_key or opportunity_key in seen_major_rows:
            continue
        bucket = _school_match_bucket(row, applicant_rank)
        if not bucket:
            continue
        buckets[bucket].append(_major_match_payload(row, applicant_rank, bucket))
        selected_rows.append(row)
        seen_major_rows.add(opportunity_key)
        if len(selected_rows) >= limit:
            break

    return buckets, selected_rows


def _major_match_payload(row: dict[str, Any], applicant_rank: int, bucket: str) -> dict[str, Any]:
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
        "major_code": _optional_text(row.get("major_code")),
        "major_name": _optional_text(row.get("major_name")),
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
        "subject_requirement": _optional_text(row.get("subject_requirement")),
        "plan_count": _as_int(row.get("plan_count")),
        "admission_count": _as_int(row.get("admission_count")),
        "remark": _optional_text(row.get("remark")),
        "row_scope": "major_or_plan_row",
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

    p = subparsers.add_parser("rank_to_major_match")
    p.add_argument("--province", required=True)
    p.add_argument("--major", required=True)
    p.add_argument("--subject-type")
    p.add_argument("--score")
    p.add_argument("--rank")
    p.add_argument("--year", type=int)
    p.add_argument("--reference-years", nargs="*", type=int)
    p.add_argument("--preferred-regions", nargs="*")
    p.add_argument("--school-level-filter")
    p.add_argument("--limit", type=int, default=30)

    p = subparsers.add_parser("specialty_group_lookup")
    p.add_argument("--school", required=True)
    p.add_argument("--major")
    p.add_argument("--province")
    p.add_argument("--subject-type")
    p.add_argument("--year", type=int)
    p.add_argument("--group-code")
    p.add_argument("--limit", type=int, default=20)

    p = subparsers.add_parser("subject_requirement_lookup")
    p.add_argument("--major", required=True)
    p.add_argument("--school")
    p.add_argument("--province")
    p.add_argument("--subject-type")
    p.add_argument("--year", type=int)
    p.add_argument("--limit", type=int, default=50)

    p = subparsers.add_parser("school_department_major_list")
    p.add_argument("--school", required=True)
    p.add_argument("--department")
    p.add_argument("--major")
    p.add_argument("--limit", type=int, default=100)

    p = subparsers.add_parser("plan_history")
    p.add_argument("--school", required=True)
    p.add_argument("--major")
    p.add_argument("--province")
    p.add_argument("--years", nargs="*", type=int)
    p.add_argument("--limit", type=int, default=100)

    p = subparsers.add_parser("employment_summary")
    p.add_argument("--school", required=True)
    p.add_argument("--limit", type=int, default=5)

    p = subparsers.add_parser("source_trace_lookup")
    p.add_argument("--tool-name")

    p = subparsers.add_parser("transfer_policy_lookup")
    p.add_argument("--school", required=True)

    p = subparsers.add_parser("fee_and_campus_lookup")
    p.add_argument("--school", required=True)
    p.add_argument("--major")
    p.add_argument("--province")
    p.add_argument("--year", type=int)
    p.add_argument("--limit", type=int, default=50)

    p = subparsers.add_parser("specialty_group_risk")
    p.add_argument("--school", required=True)
    p.add_argument("--province")
    p.add_argument("--subject-type")
    p.add_argument("--year", type=int)
    p.add_argument("--group-code")
    p.add_argument("--major")

    p = subparsers.add_parser("comparison_query")
    p.add_argument("--target-type", required=True, choices=["school", "major", "school_major"])
    p.add_argument("--target", dest="target_texts", action="append", required=True)
    p.add_argument("--major")
    p.add_argument("--province")
    p.add_argument("--subject-type")
    p.add_argument("--score")
    p.add_argument("--rank")
    p.add_argument("--year", type=int)
    p.add_argument("--dimension", dest="dimensions", action="append")
    p.add_argument("--limit", type=int, default=10)

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
        "rank_to_major_match": lambda: tools.rank_to_major_match(
            args.province,
            args.major,
            args.subject_type,
            args.score,
            args.rank,
            args.year,
            args.reference_years,
            args.preferred_regions,
            args.school_level_filter,
            args.limit,
        ),
        "specialty_group_lookup": lambda: tools.specialty_group_lookup(
            args.school,
            args.major,
            args.province,
            args.subject_type,
            args.year,
            args.group_code,
            args.limit,
        ),
        "subject_requirement_lookup": lambda: tools.subject_requirement_lookup(
            args.major,
            args.school,
            args.province,
            args.subject_type,
            args.year,
            args.limit,
        ),
        "school_department_major_list": lambda: tools.school_department_major_list(
            args.school,
            args.department,
            args.major,
            args.limit,
        ),
        "plan_history": lambda: tools.plan_history(args.school, args.major, args.province, args.years, args.limit),
        "employment_summary": lambda: tools.employment_summary(args.school, args.limit),
        "source_trace_lookup": lambda: tools.source_trace_lookup(args.tool_name),
        "transfer_policy_lookup": lambda: tools.transfer_policy_lookup(args.school),
        "fee_and_campus_lookup": lambda: tools.fee_and_campus_lookup(
            args.school,
            args.major,
            args.province,
            args.year,
            args.limit,
        ),
        "specialty_group_risk": lambda: tools.specialty_group_risk(
            args.school,
            args.province,
            args.subject_type,
            args.year,
            args.group_code,
            args.major,
        ),
        "comparison_query": lambda: tools.comparison_query(
            args.target_type,
            args.target_texts,
            args.major,
            args.province,
            args.subject_type,
            args.score,
            args.rank,
            args.year,
            args.dimensions,
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
