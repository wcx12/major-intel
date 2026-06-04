import unittest

from scripts.one_off.official_sources.curate_batch401_gsau_life_2024_admission import curate_records, parse_segment_tokens


class CurateBatch401GsauLife2024AdmissionTests(unittest.TestCase):
    def test_parse_regular_record_segment(self):
        record = parse_segment_tokens(
            [
                "1",
                "吕硕",
                "107334620202980",
                "071010",
                "生物化学与分子生物学",
                "071010",
                "生物化学与分子生物学",
                "80.53",
                "92.00",
                "93.00",
                "92.50",
                "否",
                "否",
                "否",
                "非定向",
                "全日制",
            ]
        )

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["person_name"], "吕硕")
        self.assertEqual(record["student_id"], "107334620202980")
        self.assertEqual(record["major"], "071010")
        self.assertEqual(record["admission_major"], "生物化学与分子生物学")
        self.assertIn("official_admission_status: 拟录取", record["remarks"])
        self.assertIn("is_adjustment: 否", record["remarks"])

    def test_curate_records_extracts_all_pdf_rows(self):
        rows = curate_records()

        self.assertEqual(len(rows), 41)
        self.assertEqual(rows[0]["person_name"], "吕硕")
        self.assertEqual(rows[0]["student_id"], "107334620202980")
        self.assertEqual(rows[-1]["person_name"], "徐焱")
        self.assertEqual(rows[-1]["student_id"], "107334410502992")
        self.assertTrue(all("official_admission_status: 拟录取" in row["remarks"] for row in rows))


if __name__ == "__main__":
    unittest.main()
