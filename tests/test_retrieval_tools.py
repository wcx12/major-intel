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
        for needle, rows in self.routes:
            if needle in sql:
                return rows
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
