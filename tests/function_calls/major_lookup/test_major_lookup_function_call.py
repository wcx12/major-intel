import subprocess
import sys
import unittest

from scripts.retrieval_tools import RetrievalTools
from tests.test_retrieval_tools import FakeClient, MAJOR


class MajorLookupFunctionCallTests(unittest.TestCase):
    def test_prefers_undergraduate_when_same_name_exists(self):
        specialist = {
            **MAJOR,
            "special_id": "520101",
            "code": "520101",
            "special_name": "临床医学",
            "type_name": "专科(普通)",
            "level2_name": "医药卫生大类",
            "degree": "",
        }
        undergraduate = {
            **MAJOR,
            "special_id": "100201K",
            "code": "100201K",
            "special_name": "临床医学",
            "type_name": "",
            "level2_name": "医学",
            "degree": "医学学士",
        }
        tools = RetrievalTools(FakeClient([("FROM edu_major", [specialist, undergraduate])]))

        result = tools.major_lookup("临床医学")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["normalized_slots"]["major_code"], "100201K")
        self.assertEqual(result["data"]["selected_major"]["code"], "100201K")
        self.assertIn("同名专业存在多个层次", result["warnings"][0])

    def test_returns_clarification_for_ambiguous_confirmed_alias(self):
        electronic = {**MAJOR, "code": "080701", "special_name": "电子信息工程"}
        communication = {**MAJOR, "code": "080703", "special_name": "通信工程"}
        tools = RetrievalTools(
            FakeClient(
                [
                    ("FROM entity_aliases a", [electronic, communication]),
                    ("FROM edu_major", [electronic, communication]),
                ]
            )
        )

        result = tools.major_lookup("电信")

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["data"]["selected_major"], {})
        self.assertEqual({row["code"] for row in result["data"]["candidates"]}, {"080701", "080703"})
        self.assertEqual(result["needs_clarification"], ["major_text"])
        self.assertEqual(len(tools.client.queries), 1)

    def test_orders_ambiguous_alias_candidates_by_seed_confidence(self):
        lower_confidence = {
            **MAJOR,
            "code": "080421T",
            "special_name": "电子信息材料",
            "alias_confidence": "0.750",
            "ruanke_rank": "1",
        }
        higher_confidence = {
            **MAJOR,
            "code": "080701",
            "special_name": "电子信息工程",
            "alias_confidence": "0.950",
            "ruanke_rank": "999",
        }
        tools = RetrievalTools(FakeClient([("FROM entity_aliases a", [lower_confidence, higher_confidence])]))

        result = tools.major_lookup("电子信息")

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["data"]["candidates"][0]["code"], "080701")

    def test_normalizes_admission_suffixes_before_querying(self):
        tools = RetrievalTools(FakeClient([("special_name = '软件工程'", [{**MAJOR, "code": "080902", "special_name": "软件工程"}])]))

        result = tools.major_lookup("软件工程(中外合作办学)")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["normalized_slots"]["major_name"], "软件工程")
        self.assertEqual(result["normalized_slots"]["normalized_major_text"], "软件工程")
        self.assertIn("special_name = '软件工程'", tools.client.queries[-1])
        self.assertNotIn("中外合作办学", tools.client.queries[-1])

    def test_returns_clarification_for_multi_candidate_fuzzy_match(self):
        enforcement_specialist = {
            **MAJOR,
            "code": "580202",
            "special_name": "网络安全与执法",
            "type_name": "专科(普通)",
            "level2_name": "公安与司法大类",
            "degree": "",
        }
        enforcement_undergraduate = {
            **MAJOR,
            "code": "083108TK",
            "special_name": "网络安全与执法",
            "type_name": "",
            "level2_name": "工学",
            "degree": "工学学士",
        }
        tools = RetrievalTools(FakeClient([("FROM edu_major", [enforcement_specialist, enforcement_undergraduate])]))

        result = tools.major_lookup("网络安全")

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(result["data"]["selected_major"], {})
        self.assertEqual(result["needs_clarification"], ["major_text"])
        self.assertIn("命中多个候选", result["warnings"][0])

    def test_respects_limit_for_clarification_candidates(self):
        rows = [
            {**MAJOR, "code": "080901", "special_name": "计算机科学与技术"},
            {**MAJOR, "code": "080909T", "special_name": "电子与计算机工程"},
            {**MAJOR, "code": "510201", "special_name": "计算机应用技术", "degree": ""},
        ]
        tools = RetrievalTools(FakeClient([("FROM edu_major", rows)]))

        result = tools.major_lookup("计算机", limit=2)

        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual(len(result["data"]["candidates"]), 2)

    def test_cli_exposes_limit_option(self):
        completed = subprocess.run(
            [sys.executable, "scripts/retrieval_tools.py", "major_lookup", "--help"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--limit", completed.stdout)


if __name__ == "__main__":
    unittest.main()
