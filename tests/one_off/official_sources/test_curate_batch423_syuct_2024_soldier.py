import unittest

from scripts.one_off.official_sources.curate_batch423_syuct_2024_soldier import curate_records, parse_segment_tokens


class CurateBatch423Syuct2024SoldierTests(unittest.TestCase):
    def test_parse_admitted_soldier_plan_segment(self):
        record = parse_segment_tokens(
            [
                "101494000000660",
                "齐*冉",
                "信息工程学院 085406 控制工程",
                "全日制",
                "279",
                "207",
                "96.38",
                "拟录取",
            ]
        )

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["school_name"], "沈阳化工大学")
        self.assertEqual(record["student_id"], "101494000000660")
        self.assertEqual(record["person_name"], "齐*冉")
        self.assertEqual(record["college"], "信息工程学院")
        self.assertEqual(record["major"], "085406")
        self.assertEqual(record["admission_major"], "控制工程")
        self.assertIn("official_admission_status: 拟录取", record["remarks"])

    def test_rejects_policy_text_and_non_admitted_segments(self):
        self.assertIsNone(parse_segment_tokens(["考生思想政治品德考核不合格者不予录取。"]))
        self.assertIsNone(
            parse_segment_tokens(
                [
                    "101494000000660",
                    "齐*冉",
                    "信息工程学院 085406 控制工程",
                    "全日制",
                    "279",
                    "207",
                    "96.38",
                    "不予录取",
                ]
            )
        )

    def test_curate_records_extracts_only_five_soldier_plan_admissions(self):
        rows = curate_records()

        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["student_id"], "101494000000660")
        self.assertEqual(rows[-1]["student_id"], "101494000001529")
        self.assertTrue(all("official_admission_status: 拟录取" in row["remarks"] for row in rows))
        self.assertFalse(any("不予录取" in row["remarks"] for row in rows))


if __name__ == "__main__":
    unittest.main()
