import importlib
import unittest


WEB_VISIBLE_TEXT = """云南民族大学2025年拟录取推免生名单
序号 姓名 复试成绩 拟录取学院 拟录取专业代码 拟录取专业名称 备注
1 张雨思 92.4 民族文化学院 065103 戏曲
2 杨海燕 89.0 民族文化学院 065103 戏曲
3 王松茂 93.4 民族文化学院 065103 戏曲
4 王鑫 93.0 民族文化学院 065103 戏曲
5 顾紫欣 89.6 民族文化学院 065103 戏曲
6 黄一格 87.2 民族文化学院 065103 戏曲
7 王梓霖 89.6 民族文化学院 065103 戏曲
8 陆姝杏 90.4 民族文化学院 065103 戏曲
"""


def _load_curate_text():
    module_name = "scripts.one_off.official_sources.curate_ymu_2025_recommendation_web_visible"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name:
            raise AssertionError("YMU 2025 web-visible recommendation curator is missing") from exc
        raise
    return module.curate_text


class Ymu2025RecommendationWebVisibleTests(unittest.TestCase):
    def test_curates_all_web_visible_recommendation_rows(self):
        rows = _load_curate_text()(WEB_VISIBLE_TEXT)

        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["school_name"] == "云南民族大学" for row in rows))
        self.assertTrue(all(row["year"] == 2025 for row in rows))
        self.assertTrue(all(row["document_type"] == "incoming_recommendation_admission_list" for row in rows))
        self.assertTrue(all(row["route"] == "recommendation_exemption" for row in rows))
        self.assertTrue(all(row["admission_major"] == "戏曲" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "张雨思")
        self.assertEqual(first["college"], "民族文化学院")
        self.assertIn("reexam_score 92.4", first["remarks"])
        self.assertIn("major_code 065103", first["remarks"])
        self.assertIn("official_web_visible_pdf_text true", first["remarks"])

        last = rows[-1]
        self.assertEqual(last["ranking"], "8")
        self.assertEqual(last["person_name"], "陆姝杏")
        self.assertIn("local_pdf_fetch HTTP 521 __jsl_clearance_s", last["remarks"])


if __name__ == "__main__":
    unittest.main()
