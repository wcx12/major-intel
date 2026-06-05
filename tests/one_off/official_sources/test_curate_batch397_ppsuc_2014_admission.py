import unittest

from scripts.one_off.official_sources.curate_batch397_ppsuc_2014_admission import curate_records, parse_segment_tokens


class CurateBatch397Ppsuc2014AdmissionTests(unittest.TestCase):
    def test_parse_admitted_segment(self):
        record = parse_segment_tokens(
            [
                "100414201401008",
                "男",
                "325",
                "74",
                "85.00",
                "1.00215100",
                "85.183",
                "131",
                "0.884351736",
                "115.850",
                "600.033",
                "是",
                "01法理学1",
            ]
        )

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["student_id"], "100414201401008")
        self.assertEqual(record["admission_major"], "01法理学1")
        self.assertIn("official_admission_status: 是", record["remarks"])
        self.assertIn("gender: 男", record["remarks"])

    def test_parse_rejects_not_admitted_segment(self):
        record = parse_segment_tokens(
            [
                "100414201401001",
                "女",
                "350",
                "51",
                "90.00",
                "1.00215100",
                "90.194",
                "136",
                "0.884351736",
                "120.272",
                "611.465",
                "否",
            ]
        )

        self.assertIsNone(record)

    def test_parse_adjustment_admitted_segment(self):
        record = parse_segment_tokens(
            [
                "100414201417009",
                "男",
                "291",
                "69",
                "92.80",
                "0.95149300",
                "88.299",
                "102",
                "1.009536424",
                "102.973",
                "551.271",
                "调剂是",
                "24安全工程",
            ]
        )

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["admission_major"], "24安全工程")
        self.assertIn("official_admission_status: 是", record["remarks"])
        self.assertIn("status_prefix: 调剂", record["remarks"])

    def test_curate_records_extracts_only_admitted_rows(self):
        rows = curate_records()

        self.assertEqual(len(rows), 406)
        self.assertEqual(rows[0]["student_id"], "100414201401008")
        self.assertEqual(rows[-1]["student_id"], "100414201425023")
        self.assertTrue(all("official_admission_status: 是" in row["remarks"] for row in rows))


if __name__ == "__main__":
    unittest.main()
