import importlib.util
import unittest
from pathlib import Path


class Batch254QqhruAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch254_keeps_admitted_qqhru_rows_only(self):
        spec = importlib.util.find_spec("scripts.one_off.official_sources.curate_batch254_qqhru_admission")
        self.assertIsNotNone(spec, "batch254 curation module should exist")

        from scripts.one_off.official_sources.curate_batch254_qqhru_admission import curate_records

        rows = curate_records(
            pdf_path=Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260601_batch254_qqhru_admission/yjs.qqhru.edu.cn/ccb1fb9cc27be2fd.pdf"
            )
        )

        self.assertEqual(len(rows), 1190)
        self.assertEqual(sum(row["school_name"] == "齐齐哈尔大学" for row in rows), 1190)
        self.assertEqual(sum(row["year"] == 2025 for row in rows), 1190)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 1190)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 1190)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["major"] for row in rows))

        first = rows[0]
        self.assertEqual(first["person_name"], "刘卓")
        self.assertEqual(first["student_id"], "102325305000940")
        self.assertEqual(first["college"], "马克思主义学院")
        self.assertEqual(first["major"], "马克思主义理论")
        self.assertEqual(first["admission_major"], "马克思主义基本原理")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("学习方式: 全日制", first["remarks"])
        self.assertIn("录取备注: 一志愿录取", first["remarks"])

        soldier = next(row for row in rows if row["person_name"] == "李春浩")
        self.assertEqual(soldier["ranking"], "32")
        self.assertEqual(soldier["admission_major"], "马克思主义中国化研究")
        self.assertIn("退役大学生士兵专项计划", soldier["remarks"])

        hard_exclude_terms = (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "放弃一志愿录取资格",
            "复试不合格",
            "缺考",
            "候补",
            "不合格",
            "名额受限",
        )
        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("title", "remarks", "major", "admission_major"))
            for row in rows
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))
        self.assertNotIn(("102325951330883", "1191"), {(row["student_id"], row["ranking"]) for row in rows})
        self.assertNotIn(("102325253002261", "1192"), {(row["student_id"], row["ranking"]) for row in rows})

        last = rows[-1]
        self.assertEqual(last["person_name"], "滕美玲")
        self.assertEqual(last["student_id"], "102325859002225")
        self.assertEqual(last["college"], "建筑与土木工程学院")
        self.assertEqual(last["major"], "土木水利")
        self.assertEqual(last["admission_major"], "土木工程")
        self.assertEqual(last["ranking"], "1190")
        self.assertIn("学习方式: 非全日制", last["remarks"])
        self.assertEqual(
            last["source_url"],
            "https://yjs.qqhru.edu.cn/__local/8/F5/EE/02D0C56D2494576D6694F9C54A6_C1B2A0DC_FAA2C.pdf",
        )


if __name__ == "__main__":
    unittest.main()
