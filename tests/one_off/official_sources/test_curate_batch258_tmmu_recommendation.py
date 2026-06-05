import importlib.util
import unittest
from pathlib import Path


class Batch258TmmuRecommendationCurationTests(unittest.TestCase):
    def test_curate_batch258_parses_tmmu_recommendation_pdf_rows(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch258_tmmu_recommendation")
        self.assertIsNotNone(spec, "batch258 curation module should exist")

        from scripts.one_off.official_sources.curate_batch258_tmmu_recommendation import curate_records

        rows = curate_records(
            raw_dir=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch258_tmmu_recommendation"
            )
        )

        self.assertEqual(len(rows), 38)
        self.assertEqual(sum(row["school_name"] == "陆军军医大学" for row in rows), 38)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 38)
        self.assertEqual(
            sum(row["document_type"] == "incoming_recommendation_admission_list" for row in rows),
            38,
        )
        self.assertEqual(sum(row["route"] == "recommendation_exemption" for row in rows), 38)
        self.assertTrue(all(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(row["student_id"] for row in rows))
        self.assertFalse(any(row["admission_major"] for row in rows))
        self.assertFalse(any(row["major"] for row in rows))
        self.assertTrue(all("missing_student_id" in row["quality_flags"] for row in rows))
        self.assertTrue(all("missing_major" in row["quality_flags"] for row in rows))

        local_plan = [row for row in rows if "地方计划" in row["remarks"]]
        enlistment_plan = [row for row in rows if "入伍计划" in row["remarks"]]
        self.assertEqual(len(local_plan), 35)
        self.assertEqual(len(enlistment_plan), 3)

        first_local = local_plan[0]
        self.assertEqual(first_local["person_name"], "陈俊希")
        self.assertEqual(first_local["ranking"], "1")
        self.assertIn("gender 女", first_local["remarks"])
        self.assertTrue(first_local["source_url"].endswith("20251120181938689.pdf"))

        last_local = local_plan[-1]
        self.assertEqual(last_local["person_name"], "邹苗苗")
        self.assertEqual(last_local["ranking"], "35")

        first_enlistment = enlistment_plan[0]
        self.assertEqual(first_enlistment["person_name"], "唐祯濡")
        self.assertEqual(first_enlistment["ranking"], "1")
        self.assertIn("gender 女", first_enlistment["remarks"])
        self.assertTrue(first_enlistment["source_url"].endswith("20251120181948390.pdf"))

        last_enlistment = enlistment_plan[-1]
        self.assertEqual(last_enlistment["person_name"], "甄宁静")
        self.assertEqual(last_enlistment["ranking"], "3")

        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        hard_exclude_terms = (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
            "不合格",
            "名额受限",
            "放弃一志愿录取资格",
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))


if __name__ == "__main__":
    unittest.main()
