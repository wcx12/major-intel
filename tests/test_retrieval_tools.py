import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.retrieval_tools import RetrievalTools, tool_result


class FakeClient:
    """Tiny SQL client used by tests to keep tool behavior independent of MySQL.

    The production tools call `client.query(sql)` with plain SQL strings.  These
    tests only care that each tool asks for the right kind of data and normalizes
    it into the function-call envelope, so a substring router is enough and keeps
    tests deterministic.
    """

    def __init__(self, routes):
        self.routes = routes
        self.queries = []

    def query(self, sql):
        self.queries.append(sql)
        matches = [(needle, rows) for needle, rows in self.routes if needle in sql]
        if matches:
            return max(matches, key=lambda item: len(item[0]))[1]
        return []


SCHOOL = {
    "school_id": "10124",
    "code": "10336",
    "name": "杭州电子科技大学",
    "province_name": "浙江",
    "city_name": "杭州市",
    "is211": "0",
    "is_dual_class": "0",
    "school_site": "https://www.hdu.edu.cn/main.htm",
}

MAJOR = {
    "special_id": "080901",
    "code": "080901",
    "special_name": "计算机科学与技术",
    "level2_name": "工学",
    "level3_name": "计算机类",
    "limit_year": "四年",
    "degree": "工学学士",
    "salaryavg": "120000",
    "fivesalaryavg": "18000",
    "job_clean": "软件开发、算法、系统研发",
}


class RetrievalToolsTests(unittest.TestCase):
    def test_tool_result_has_function_call_envelope(self):
        result = tool_result(
            "school_lookup",
            "ok",
            {"school_text": "杭电"},
            data={"selected_school": SCHOOL},
            scope_notes=["学校基础信息来自 edu_university。"],
        )

        self.assertEqual(result["tool_name"], "school_lookup")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["selected_school"]["name"], "杭州电子科技大学")
        self.assertEqual(result["data_gaps"], [])
        self.assertEqual(result["needs_clarification"], [])

    def test_school_lookup_returns_selected_school_and_candidates(self):
        tools = RetrievalTools(FakeClient([("FROM edu_university", [SCHOOL])]))

        result = tools.school_lookup("杭州电子科技大学")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["selected_school"]["name"], "杭州电子科技大学")
        self.assertIn("edu_university", result["source_tables"])
        self.assertIn("学校实体解析", result["scope_notes"][0])

    def test_major_lookup_returns_not_found_without_guessing(self):
        tools = RetrievalTools(FakeClient([("FROM edu_major", [])]))

        result = tools.major_lookup("不存在专业")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["data"]["selected_major"], {})
        self.assertIn("本地库未命中专业实体", result["warnings"][0])

    def test_major_lookup_uses_entity_alias_for_common_short_name(self):
        tools = RetrievalTools(FakeClient([("FROM edu_major", [MAJOR])]))

        result = tools.major_lookup("计科")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["normalized_slots"]["major_code"], "080901")
        self.assertIn("entity_aliases", result["source_tables"])
        self.assertIn("entity_aliases", result["scope_notes"][0])
        self.assertIn("FROM entity_aliases", tools.client.queries[-1])
        self.assertIn("alias_normalized = '计科'", tools.client.queries[-1])
        self.assertNotIn("special_name LIKE '%计科%'", tools.client.queries[-1])

    def test_school_major_list_uses_school_code_and_explains_scope(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    (
                        "FROM edu_school_major sm",
                        [
                            {
                                "major_code": "080901",
                                "major_name": "计算机科学与技术",
                                "level_name": "本科",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.school_major_list("杭州电子科技大学")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["majors"][0]["major_name"], "计算机科学与技术")
        self.assertIn("sm.school_id = '10336'", tools.client.queries[-1])
        self.assertIn("开设专业不等于某省当年招生专业", result["scope_notes"][0])

    def test_school_major_profile_filters_specialty_groups_by_context(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    ("FROM edu_major", [MAJOR]),
                    ("FROM edu_school_major sm", [{"major_code": "080901"}]),
                    ("FROM edu_university_subject_eval", []),
                    ("FROM edu_dual_class", []),
                    ("FROM edu_university_employment", []),
                    (
                        "FROM edu_college_specialty_group g",
                        [{"year": "2025", "province": "44", "group_type": "physical"}],
                    ),
                ]
            )
        )

        result = tools.school_major_profile(
            school_text="HDU",
            major_text="CS",
            province="44",
            subject_type="physical",
            year=2025,
        )

        self.assertEqual(result["status"], "ok")
        group_query = tools.client.queries[-1]
        self.assertIn("g.province = '44'", group_query)
        self.assertIn("g.group_type = 'physical'", group_query)
        self.assertIn("g.year = 2025", group_query)

    def test_score_to_rank_requires_province_subject_type_and_score(self):
        tools = RetrievalTools(FakeClient([]))

        result = tools.score_to_rank(province="广东", subject_type="", score=580)

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["needs_clarification"], ["subject_type"])

    def test_score_to_rank_returns_rank_range(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    (
                        "FROM edu_score_rank",
                        [
                            {
                                "province_id": "44",
                                "year": "2025",
                                "subject_type": "物理",
                                "score": "580",
                                "same_count": "2200",
                                "highest_rank": "43000",
                                "lowest_rank": "45200",
                            }
                        ],
                    )
                ]
            )
        )

        result = tools.score_to_rank(province="广东", subject_type="物理", score=580, year=2025)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["rank_range"]["lowest_rank"], 45200)
        self.assertIn("位次优先于分数", result["scope_notes"][0])

    def test_rank_to_school_match_requires_rank_or_score(self):
        tools = RetrievalTools(FakeClient([]))

        result = tools.rank_to_school_match(province="浙江", subject_type="综合")

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["needs_clarification"], ["rank_or_score"])

    def test_rank_to_school_match_uses_score_rank_and_latest_available_history(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    (
                        "FROM edu_score_rank",
                        [
                            {
                                "province_id": "44",
                                "year": "2025",
                                "subject_type": "物理",
                                "score": "580",
                                "same_count": "1035",
                                "highest_rank": "43758",
                                "lowest_rank": "44792",
                            }
                        ],
                    ),
                    (
                        "FROM edu_school_admission_stats a",
                        [
                            {
                                "province_name": "广东",
                                "school_id": "10001",
                                "school_name": "冲刺大学",
                                "school_province_name": "北京",
                                "city_name": "北京市",
                                "is985": "1",
                                "is211": "1",
                                "is_dual_class": "1",
                                "subject_type": "NULL",
                                "year": "2024",
                                "stable_score": "560",
                                "stable_rank": "43000",
                                "chong_score": "555",
                                "chong_rank": "56000",
                                "bao_score": "565",
                                "bao_rank": "30000",
                                "batch": "NULL",
                                "representative_major_name": "",
                                "row_scope": "school_level",
                            },
                            {
                                "province_name": "广东",
                                "school_id": "10002",
                                "school_name": "稳妥大学",
                                "school_province_name": "浙江",
                                "city_name": "杭州市",
                                "is985": "0",
                                "is211": "0",
                                "is_dual_class": "0",
                                "subject_type": "",
                                "year": "2024",
                                "stable_score": "552",
                                "stable_rank": "46000",
                                "chong_score": "547",
                                "chong_rank": "59000",
                                "bao_score": "557",
                                "bao_rank": "33000",
                                "batch": "本科批",
                                "representative_major_name": "",
                                "row_scope": "school_level",
                            },
                            {
                                "province_name": "广东",
                                "school_id": "10003",
                                "school_name": "保底大学",
                                "school_province_name": "江苏",
                                "city_name": "南京市",
                                "is985": "0",
                                "is211": "1",
                                "is_dual_class": "1",
                                "subject_type": "",
                                "year": "2024",
                                "stable_score": "520",
                                "stable_rank": "70000",
                                "chong_score": "515",
                                "chong_rank": "91000",
                                "bao_score": "525",
                                "bao_rank": "50000",
                                "batch": "本科批",
                                "representative_major_name": "",
                                "row_scope": "school_level",
                            },
                        ],
                    ),
                ]
            )
        )

        result = tools.rank_to_school_match(
            province="广东",
            subject_type="物理",
            score=580,
            year=2025,
            limit=10,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["applicant"]["rank"], 44792)
        self.assertEqual(result["data"]["reference"]["requested_year"], 2025)
        self.assertEqual(result["data"]["reference"]["reference_years"], [2024])
        self.assertTrue(result["data"]["reference"]["history_fallback"])
        self.assertEqual(result["data"]["reference"]["subject_unknown_count"], 3)
        self.assertEqual(result["data"]["buckets"]["rush"][0]["school_name"], "冲刺大学")
        self.assertIsNone(result["data"]["buckets"]["rush"][0]["subject_type"])
        self.assertIsNone(result["data"]["buckets"]["rush"][0]["batch"])
        self.assertEqual(result["data"]["buckets"]["stable"][0]["school_name"], "稳妥大学")
        self.assertEqual(result["data"]["buckets"]["safe"][0]["school_name"], "保底大学")
        self.assertIn("a.year <= 2025", tools.client.queries[-1])
        self.assertIn("u.code = CAST(a.school_id AS CHAR)", tools.client.queries[-1])
        self.assertIn("u.name = a.school_name", tools.client.queries[-1])
        self.assertIn("edu_school_admission_stats", result["source_tables"])

    def test_rank_to_school_match_returns_not_found_when_history_missing(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    (
                        "FROM edu_score_rank",
                        [
                            {
                                "province_id": "33",
                                "year": "2025",
                                "subject_type": "综合",
                                "score": "600",
                                "same_count": "1000",
                                "highest_rank": "51000",
                                "lowest_rank": "52000",
                            }
                        ],
                    ),
                    ("FROM edu_school_admission_stats a", []),
                ]
            )
        )

        result = tools.rank_to_school_match(province="浙江", subject_type="综合", score=600, year=2025)

        self.assertEqual(result["status"], "not_found")
        self.assertIn("本地库未命中", result["warnings"][0])

    def test_rank_to_major_match_requires_major_and_rank_or_score(self):
        tools = RetrievalTools(FakeClient([]))

        missing_major = tools.rank_to_major_match(province="浙江", subject_type="综合", major_text="")
        missing_rank = tools.rank_to_major_match(province="浙江", subject_type="综合", major_text="计科")

        self.assertEqual(missing_major["status"], "needs_clarification")
        self.assertEqual(missing_major["needs_clarification"], ["major_text"])
        self.assertEqual(missing_rank["status"], "needs_clarification")
        self.assertEqual(missing_rank["needs_clarification"], ["rank_or_score"])

    def test_rank_to_major_match_uses_major_alias_score_rank_and_history(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_major", [MAJOR]),
                    (
                        "FROM edu_score_rank",
                        [
                            {
                                "province_id": "44",
                                "year": "2025",
                                "subject_type": "物理",
                                "score": "580",
                                "same_count": "1035",
                                "highest_rank": "43758",
                                "lowest_rank": "44792",
                            }
                        ],
                    ),
                    (
                        "FROM edu_school_admission_stats a",
                        [
                            {
                                "province_name": "广东",
                                "school_id": "10001",
                                "school_name": "冲刺大学",
                                "school_province_name": "北京",
                                "city_name": "北京市",
                                "is985": "1",
                                "is211": "1",
                                "is_dual_class": "1",
                                "major_code": "080901",
                                "major_name": "计算机科学与技术",
                                "subject_type": "物理",
                                "year": "2024",
                                "stable_score": "610",
                                "stable_rank": "43000",
                                "chong_score": "600",
                                "chong_rank": "56000",
                                "bao_score": "620",
                                "bao_rank": "30000",
                                "batch": "本科批",
                                "subject_requirement": "物理+化学",
                                "plan_count": "4",
                                "admission_count": "4",
                                "remark": "",
                            },
                            {
                                "province_name": "广东",
                                "school_id": "10002",
                                "school_name": "稳妥大学",
                                "school_province_name": "浙江",
                                "city_name": "杭州市",
                                "is985": "0",
                                "is211": "0",
                                "is_dual_class": "0",
                                "major_code": "080901",
                                "major_name": "计算机科学与技术",
                                "subject_type": "物理",
                                "year": "2024",
                                "stable_score": "590",
                                "stable_rank": "46000",
                                "chong_score": "580",
                                "chong_rank": "59000",
                                "bao_score": "600",
                                "bao_rank": "33000",
                                "batch": "本科批",
                                "subject_requirement": "物理+化学",
                                "plan_count": "8",
                                "admission_count": "8",
                                "remark": "",
                            },
                            {
                                "province_name": "广东",
                                "school_id": "10003",
                                "school_name": "保底大学",
                                "school_province_name": "江苏",
                                "city_name": "南京市",
                                "is985": "0",
                                "is211": "1",
                                "is_dual_class": "1",
                                "major_code": "080901",
                                "major_name": "计算机科学与技术",
                                "subject_type": "",
                                "year": "2024",
                                "stable_score": "560",
                                "stable_rank": "70000",
                                "chong_score": "550",
                                "chong_rank": "91000",
                                "bao_score": "570",
                                "bao_rank": "50000",
                                "batch": "本科批",
                                "subject_requirement": "",
                                "plan_count": "12",
                                "admission_count": "12",
                                "remark": "含创新班",
                            },
                        ],
                    ),
                ]
            )
        )

        result = tools.rank_to_major_match(
            province="广东",
            subject_type="物理",
            major_text="计科",
            score=580,
            year=2025,
            limit=10,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["normalized_slots"]["major_code"], "080901")
        self.assertEqual(result["data"]["applicant"]["rank"], 44792)
        self.assertTrue(result["data"]["reference"]["history_fallback"])
        self.assertEqual(result["data"]["buckets"]["rush"][0]["school_name"], "冲刺大学")
        self.assertEqual(result["data"]["buckets"]["stable"][0]["school_name"], "稳妥大学")
        self.assertEqual(result["data"]["buckets"]["safe"][0]["school_name"], "保底大学")
        self.assertEqual(result["data"]["buckets"]["safe"][0]["major_name"], "计算机科学与技术")
        self.assertEqual(result["data"]["buckets"]["safe"][0]["plan_count"], 12)
        self.assertIn("entity_aliases", result["source_tables"])
        self.assertIn("edu_school_admission_stats", result["source_tables"])
        self.assertIn("a.major_code = '080901'", tools.client.queries[-1])
        self.assertIn("a.year <= 2025", tools.client.queries[-1])

    def test_specialty_group_lookup_returns_group_and_all_group_majors(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    ("FROM edu_major", [MAJOR]),
                    (
                        "FROM edu_college_specialty_group g",
                        [
                            {
                                "year": "2025",
                                "province": "33",
                                "group_code": "001",
                                "group_name": "物理化学组",
                                "group_type": "综合",
                                "group_plan_count": "120",
                                "allow_adjustment": "1",
                                "special_code": "080901",
                                "special_name": "计算机科学与技术",
                                "major_plan_count": "80",
                                "subject_requirement": "物理,化学",
                            },
                            {
                                "year": "2025",
                                "province": "33",
                                "group_code": "001",
                                "group_name": "物理化学组",
                                "group_type": "综合",
                                "group_plan_count": "120",
                                "allow_adjustment": "1",
                                "special_code": "080902",
                                "special_name": "软件工程",
                                "major_plan_count": "40",
                                "subject_requirement": "物理,化学",
                            },
                        ],
                    ),
                ]
            )
        )

        result = tools.specialty_group_lookup(
            school_text="杭州电子科技大学",
            major_text="计科",
            province="浙江",
            subject_type="综合",
            year=2025,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["groups"][0]["group_code"], "001")
        self.assertEqual(len(result["data"]["groups"][0]["majors"]), 2)
        self.assertIn("g.year = 2025", tools.client.queries[-1])
        self.assertIn("gm_filter.special_code = '080901'", tools.client.queries[-1])
        self.assertIn("专业组样本", result["scope_notes"][0])

    def test_subject_requirement_lookup_collects_distinct_requirements(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_major", [MAJOR]),
                    (
                        "FROM edu_college_specialty_group g",
                        [
                            {
                                "school_name": "杭州电子科技大学",
                                "school_id": "10336",
                                "year": "2025",
                                "province": "33",
                                "group_code": "001",
                                "group_name": "物化组",
                                "group_type": "综合",
                                "special_code": "080901",
                                "special_name": "计算机科学与技术",
                                "subject_requirement": "物理,化学",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.subject_requirement_lookup("计科", province="浙江", subject_type="综合", year=2025)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["requirements"], ["物理,化学"])
        self.assertIn("edu_college_specialty_group", result["source_tables"])

    def test_school_department_major_list_returns_departments_and_majors(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    (
                        "FROM edu_university_department d",
                        [
                            {
                                "dept_id": "1",
                                "dept_name": "计算机学院",
                                "website_url": "https://cs.example.edu",
                                "major_code": "080901",
                                "major_name": "计算机科学与技术",
                                "education_level": "本科",
                                "is_nation_first_class": "1",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.school_department_major_list("杭州电子科技大学", department_text="计算机")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["departments"][0]["dept_name"], "计算机学院")
        self.assertEqual(result["data"]["departments"][0]["majors"][0]["major_code"], "080901")
        self.assertIn("d.dept_name LIKE '%计算机%'", tools.client.queries[-1])

    def test_plan_history_reads_qjjh_plan_records(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    ("FROM edu_major", [MAJOR]),
                    (
                        "FROM edu_qjjh_plan",
                        [
                            {
                                "year": "2025",
                                "province_id": "33",
                                "special_name": "计算机科学与技术",
                                "academy_name": "计算机学院",
                                "group_name": "物化组",
                                "plan_count": "80",
                                "subject_requirement_text": "物理,化学",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.plan_history("杭州电子科技大学", major_text="计科", province="浙江")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["records"][0]["plan_count"], "80")
        self.assertIn("school_id = '10336'", tools.client.queries[-1])
        self.assertIn("special_id = '080901'", tools.client.queries[-1])

    def test_employment_summary_returns_school_level_scope(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    (
                        "FROM edu_university_employment",
                        [
                            {
                                "year": "2024",
                                "employment_rate": "96.50",
                                "further_study_rate": "35.20",
                                "avg_salary": "8500.00",
                                "employment_data": "{}",
                                "top_employment_industries": '["IT"]',
                                "top_employment_regions": '["浙江"]',
                                "top_employers": "[]",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.employment_summary("杭州电子科技大学")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["records"][0]["year"], "2024")
        self.assertIn("学校级就业", result["scope_notes"][0])

    def test_source_trace_lookup_explains_registered_tool_sources(self):
        tools = RetrievalTools(FakeClient([]))

        result = tools.source_trace_lookup("rank_to_major_match")

        self.assertEqual(result["status"], "ok")
        self.assertIn("edu_school_admission_stats", result["data"]["source_tables"])
        self.assertIn("历史录取", result["scope_notes"][0])

    def test_transfer_policy_lookup_returns_third_party_policy_line(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    (
                        "FROM rysxai_transfer_policies",
                        [
                            {
                                "school_id": "10336",
                                "school_name": "杭州电子科技大学",
                                "source_name": "rysxai",
                                "source_level": "C",
                                "has_transfer_policy": "1",
                                "change_profession": "学生可在规定时间申请转专业。",
                                "change_profession_application_condition": "成绩合格。",
                                "source_url": "https://example.com/policy",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.transfer_policy_lookup("杭州电子科技大学")

        self.assertEqual(result["status"], "ok")
        self.assertIn("学生可在规定时间", result["data"]["policy"]["change_profession"])
        self.assertIn("第三方线索", result["scope_notes"][0])

    def test_fee_and_campus_lookup_returns_fee_items_and_marks_campus_gap(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    ("FROM edu_major", [MAJOR]),
                    (
                        "FROM edu_university_plan_special ps",
                        [
                            {
                                "year": "2025",
                                "province_id": "33",
                                "group_id": "001",
                                "group_name": "物化组",
                                "elective_info": "物理,化学",
                                "special_name": "计算机科学与技术",
                                "plan_count": "80",
                                "tuition_year": "4",
                                "tuition_fee": "6900",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.fee_and_campus_lookup("杭州电子科技大学", major_text="计科", province="浙江", year=2025)

        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["data"]["fee_items"][0]["tuition_fee"], "6900")
        self.assertIn("校区信息", result["data_gaps"])

    def test_specialty_group_risk_uses_group_composition_without_streaming_ratio(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_university", [SCHOOL]),
                    (
                        "FROM edu_college_specialty_group g",
                        [
                            {
                                "year": "2025",
                                "province": "33",
                                "group_code": "001",
                                "group_name": "物化组",
                                "group_type": "综合",
                                "group_plan_count": "120",
                                "allow_adjustment": "1",
                                "special_code": "080901",
                                "special_name": "计算机科学与技术",
                                "major_plan_count": "80",
                            },
                            {
                                "year": "2025",
                                "province": "33",
                                "group_code": "001",
                                "group_name": "物化组",
                                "group_type": "综合",
                                "group_plan_count": "120",
                                "allow_adjustment": "1",
                                "special_code": "081001",
                                "special_name": "土木工程",
                                "major_plan_count": "40",
                            },
                        ],
                    ),
                ]
            )
        )

        result = tools.specialty_group_risk(
            school_text="杭州电子科技大学",
            province="浙江",
            subject_type="综合",
            year=2025,
            group_code="001",
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["risk"]["major_count"], 2)
        self.assertIn("不等于真实分流比例", result["scope_notes"][0])

    def test_major_market_reference_uses_ingested_market_tables(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_major", [MAJOR]),
                    (
                        "FROM rysxai_major_market_snapshots",
                        [
                            {
                                "profession_id": "341",
                                "major_code": "080901",
                                "major_name": "计算机科学与技术",
                                "macro_employment_json": json.dumps(
                                    {"industry_distribution": [{"label": "互联网", "rate_percent": 30}]},
                                    ensure_ascii=False,
                                ),
                                "salary_ranking_json": json.dumps(
                                    [{"region": "全国", "monthly_salary_reference": 12000}],
                                    ensure_ascii=False,
                                ),
                                "job_posting_sample_count": "5",
                                "warnings_json": json.dumps(["招聘市场样本。"], ensure_ascii=False),
                            }
                        ],
                    ),
                    (
                        "FROM rysxai_major_job_samples",
                        [
                            {
                                "job_title": "后端工程师",
                                "company_name": "示例科技",
                                "city": "深圳",
                                "salary_raw": "20-30K",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.major_market_reference("计算机科学与技术")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["snapshot"]["major_name"], "计算机科学与技术")
        self.assertEqual(result["data"]["job_samples"][0]["job_title"], "后端工程师")
        self.assertIn("招聘市场样本", result["scope_notes"][0])

    def test_civil_service_role_search_returns_role_samples_not_final_eligibility(self):
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM edu_major", [MAJOR]),
                    (
                        "FROM civil_service_major_role_candidates c",
                        [
                            {
                                "role_id": "28167",
                                "year": "2026",
                                "department_name": "中央直属机关事务管理局",
                                "job_name": "信息管理岗位",
                                "position_code": "100110001001",
                                "province": "北京",
                                "major_code": "080901",
                                "major_name": "计算机科学与技术",
                                "profession_text": "080901计算机科学与技术",
                            }
                        ],
                    ),
                ]
            )
        )

        result = tools.civil_service_role_search("计算机科学与技术")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["roles"][0]["department_name"], "中央直属机关事务管理局")
        self.assertIn("不等于该专业一定可报", result["scope_notes"][0])
        self.assertIn("rysxai_civil_service_roles", result["source_tables"])

    def test_data_gap_detection_lists_school_major_gaps(self):
        tools = RetrievalTools(FakeClient([]))

        result = tools.data_gap_detection(
            question_type="school_major_profile",
            available_fields=["school_basic", "major_basic", "subject_eval"],
        )

        self.assertEqual(result["status"], "ok")
        self.assertIn("校专业级薪资分布", result["data"]["missing_items"])
        self.assertIn("转专业政策", result["data"]["missing_items"])


    def test_cli_runs_when_script_path_is_used(self):
        """Protect the function-call CLI from direct-script import regressions.

        Agents, cron jobs, and manual smoke tests often execute tools as
        `python scripts/retrieval_tools.py ...` instead of importing the module.
        That execution mode puts `scripts/` on `sys.path`, so this test catches
        missing project-root path setup before it reaches real tool calls.
        """
        repo_root = Path(__file__).resolve().parents[1]
        script_path = repo_root / "scripts" / "retrieval_tools.py"

        completed = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "data_gap_detection",
                "--question-type",
                "school_major_profile",
            ],
            cwd=repo_root,
            capture_output=True,
        )

        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr.decode("utf-8", errors="replace")
            + completed.stdout.decode("utf-8", errors="replace"),
        )
        payload = json.loads(completed.stdout.decode("utf-8"))
        self.assertEqual(payload["tool_name"], "data_gap_detection")


if __name__ == "__main__":
    unittest.main()
