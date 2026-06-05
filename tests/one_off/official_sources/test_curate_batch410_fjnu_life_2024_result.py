import unittest

from scripts.one_off.official_sources.curate_batch410_fjnu_life_2024_result import curate_records, parse_segment_tokens


class CurateBatch410FjnuLife2024ResultTests(unittest.TestCase):
    def test_parse_suggested_admission_segment(self):
        record = parse_segment_tokens(
            [
                "1",
                "103944025007134",
                "郭婵娟",
                "071000",
                "生物学",
                "82.40",
                "77.50",
                "40%",
                "80.44",
                "建议录取",
                "全日制",
            ]
        )

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["person_name"], "郭婵娟")
        self.assertEqual(record["student_id"], "103944025007134")
        self.assertEqual(record["major"], "071000")
        self.assertEqual(record["admission_major"], "生物学")
        self.assertIn("official_admission_status: 建议录取", record["remarks"])
        self.assertIn("study_mode: 全日制", record["remarks"])

    def test_rejects_non_admitted_or_blank_status_segments(self):
        self.assertIsNone(
            parse_segment_tokens(
                [
                    "102",
                    "103944025007129",
                    "林钦",
                    "071000",
                    "生物学",
                    "77.40",
                    "放弃复试",
                    "40%",
                    "46.44",
                    "不予录取",
                    "全日制",
                ]
            )
        )
        self.assertIsNone(
            parse_segment_tokens(
                [
                    "35",
                    "103944025007357",
                    "郑安娜",
                    "086001",
                    "生物技术与工程",
                    "63.20",
                    "68.20",
                    "40%",
                    "65.20",
                    "全日制",
                ]
            )
        )

    def test_curate_records_extracts_only_suggested_admission_rows(self):
        rows = curate_records()

        self.assertEqual(len(rows), 148)
        self.assertEqual(rows[0]["person_name"], "郭婵娟")
        self.assertEqual(rows[0]["student_id"], "103944025007134")
        self.assertEqual(rows[-1]["person_name"], "余宣炳")
        self.assertEqual(rows[-1]["student_id"], "103944025010435")
        self.assertTrue(all("official_admission_status: 建议录取" in row["remarks"] for row in rows))
        self.assertFalse(any("不予录取" in row["remarks"] or "放弃复试" in row["remarks"] for row in rows))


if __name__ == "__main__":
    unittest.main()
