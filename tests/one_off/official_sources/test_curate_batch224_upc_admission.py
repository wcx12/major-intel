import unittest
from pathlib import Path


class Batch224UpcAdmissionCurationTests(unittest.TestCase):
    def test_curate_batch224_reads_scanned_pdf_ocr_table(self):
        from scripts.one_off.official_sources.curate_batch224_upc_admission import curate_records

        rows = curate_records(
            documents_jsonl=Path(
                "data/processed/graduate_outcomes_official_site_websearch_web_20260528_batch224_upc_admission/"
                "documents.jsonl"
            )
        )

        self.assertEqual(len(rows), 2463)
        self.assertEqual(sum(row["school_name"] == "中国石油大学（华东）" for row in rows), 2463)
        self.assertFalse(any(row["needs_review"] for row in rows))
        self.assertFalse(any(not row["person_name"] for row in rows))
        self.assertFalse(any(not row["student_id"] for row in rows))
        self.assertFalse(any(not row["college"] for row in rows))
        self.assertFalse(any(not row["admission_major"] for row in rows))
        self.assertEqual(len({(row["person_name"], row["student_id"], row["source_url"]) for row in rows}), 2463)

        first_page_row = next(row for row in rows if row["student_id"] == "104236375201918")
        self.assertEqual(first_page_row["person_name"], "王睿杰")
        self.assertEqual(first_page_row["college"], "地球科学与技术学院")
        self.assertEqual(first_page_row["major"], "070700")
        self.assertEqual(first_page_row["admission_major"], "070700 海洋科学")
        self.assertIn("study_mode 全日制", first_page_row["remarks"])

        right_column_row = next(row for row in rows if row["student_id"] == "104256540009390")
        self.assertEqual(right_column_row["person_name"], "张贝贝")
        self.assertEqual(right_column_row["admission_major"], "070900 地质学")

        continuation_row = next(row for row in rows if row["student_id"] == "114146142116533")
        self.assertEqual(continuation_row["person_name"], "张申翰")
        self.assertEqual(
            continuation_row["college"],
            "深层油气全国重点实验室、中国-沙特石油能源“一带一路”联合实验室、光华能源学院",
        )
        self.assertEqual(continuation_row["admission_major"], "085706 石油与天然气工程")

        corrected_names = {
            "104256540002040": "程坤",
            "104256540001829": "冯焱",
            "104256540010025": "王丫",
            "104256540008215": "张跃",
            "100016000290719": "李冉",
            "104256540008611": "陈杨清雪",
        }
        for student_id, expected_name in corrected_names.items():
            with self.subTest(student_id=student_id):
                self.assertEqual(next(row for row in rows if row["student_id"] == student_id)["person_name"], expected_name)

        long_major_row = next(row for row in rows if row["student_id"] == "104256540000099")
        self.assertEqual(long_major_row["admission_major"], "085401 新一代电子信息技术（含量子技术等）")
        telecom_row = next(row for row in rows if row["student_id"] == "104256540000397")
        self.assertEqual(telecom_row["admission_major"], "085402 通信工程（含宽带网络、移动通信等）")
        hvac_row = next(row for row in rows if row["student_id"] == "104256540000192")
        self.assertEqual(hvac_row["admission_major"], "085906 人工环境工程（含供热、通风及空调等）")

        plan_row = next(row for row in rows if row["student_id"] == "103356000921287")
        self.assertEqual(plan_row["person_name"], "崔致源")
        self.assertIn("study_mode 全日制", plan_row["remarks"])
        self.assertIn("special_plan 少干,南疆计划", plan_row["remarks"])

        flattened = "\n".join(str(row) for row in rows)
        for bad_fragment in (
            "进入复试名单",
            "拟不录取",
            "不予录取",
            "是否拟录取: 否",
            "放弃复试",
            "复试不合格",
            "缺考",
            "候补",
        ):
            self.assertNotIn(bad_fragment, flattened)


if __name__ == "__main__":
    unittest.main()
