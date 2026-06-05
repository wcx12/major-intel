import unittest


class Batch486EcnuOcrPdfTests(unittest.TestCase):
    def test_records_from_ocr_items_reconstructs_rows_by_coordinates(self):
        from scripts.one_off.official_sources.curate_batch486_ecnu_2025_ocr_pdf import records_from_ocr_items

        items = [
            {"page": 1, "text": "姓名", "x1": 24, "y1": 90, "x2": 75, "y2": 115, "cx": 49.5, "cy": 102.5},
            {"page": 1, "text": "考生编号", "x1": 125, "y1": 92, "x2": 195, "y2": 113, "cx": 160, "cy": 102.5},
            {"page": 1, "text": "潘*蔚", "x1": 24, "y1": 113, "x2": 78, "y2": 138, "cx": 51, "cy": 125.5},
            {"page": 1, "text": "102695******069", "x1": 86, "y1": 114, "x2": 227, "y2": 137, "cx": 156.5, "cy": 125.5},
            {"page": 1, "text": "中国语言文学系", "x1": 236, "y1": 114, "x2": 372, "y2": 137, "cx": 304, "cy": 125.5},
            {"page": 1, "text": "教育", "x1": 690, "y1": 113, "x2": 736, "y2": 138, "cx": 713, "cy": 125.5},
            {"page": 1, "text": "非全日制", "x1": 1028, "y1": 114, "x2": 1109, "y2": 138, "cx": 1069.5, "cy": 125.5},
            {"page": 1, "text": "343", "x1": 1162, "y1": 115, "x2": 1201, "y2": 138, "cx": 1181.5, "cy": 126.5},
            {"page": 1, "text": "462", "x1": 1244, "y1": 113, "x2": 1285, "y2": 139, "cx": 1264.5, "cy": 126},
            {"page": 1, "text": "390.6", "x1": 1314, "y1": 115, "x2": 1367, "y2": 137, "cx": 1340.5, "cy": 126},
            {"page": 1, "text": "张*蕊", "x1": 25, "y1": 139, "x2": 77, "y2": 161, "cx": 51, "cy": 150},
            {"page": 1, "text": "102695*****702", "x1": 86, "y1": 138, "x2": 227, "y2": 161, "cx": 156.5, "cy": 149.5},
            {"page": 1, "text": "中国语言文学系", "x1": 237, "y1": 139, "x2": 371, "y2": 159, "cx": 304, "cy": 149.5},
            {"page": 1, "text": "教育", "x1": 691, "y1": 138, "x2": 734, "y2": 161, "cx": 712.5, "cy": 149.5},
            {"page": 1, "text": "非全日制", "x1": 1029, "y1": 137, "x2": 1109, "y2": 161, "cx": 1069, "cy": 149},
            {"page": 1, "text": "347", "x1": 1162, "y1": 138, "x2": 1201, "y2": 161, "cx": 1181.5, "cy": 149.5},
            {"page": 1, "text": "414", "x1": 1244, "y1": 138, "x2": 1284, "y2": 161, "cx": 1264, "cy": 149.5},
            {"page": 1, "text": "373.8", "x1": 1314, "y1": 139, "x2": 1368, "y2": 161, "cx": 1341, "cy": 150},
        ]

        rows = records_from_ocr_items(items, source_url="https://example.edu/ecnu.pdf")

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["person_name"], "潘*蔚")
        self.assertEqual(rows[0]["student_id"], "102695******069")
        self.assertEqual(rows[0]["college"], "中国语言文学系")
        self.assertEqual(rows[0]["admission_major"], "教育")
        self.assertIn("study_mode 非全日制", rows[0]["remarks"])
        self.assertIn("initial_score 343", rows[0]["remarks"])
        self.assertIn("reexam_score 462", rows[0]["remarks"])
        self.assertIn("total_score 390.6", rows[0]["remarks"])

    def test_records_from_ocr_items_skips_non_rows(self):
        from scripts.one_off.official_sources.curate_batch486_ecnu_2025_ocr_pdf import records_from_ocr_items

        rows = records_from_ocr_items(
            [
                {"page": 1, "text": "华东师范大学2025年全国硕士研究生招生考试拟录取名单公示", "x1": 538, "x2": 1217, "cx": 878, "cy": 42},
                {"page": 1, "text": "备注", "x1": 1526, "x2": 1566, "cx": 1546, "cy": 103},
            ],
            source_url="https://example.edu/ecnu.pdf",
        )

        self.assertEqual(rows, [])

    def test_records_from_ocr_items_repairs_split_and_noisy_student_ids(self):
        from scripts.one_off.official_sources.curate_batch486_ecnu_2025_ocr_pdf import records_from_ocr_items

        rows = records_from_ocr_items(
            [
                {"page": 4, "text": "林*青", "x1": 25, "x2": 78, "cx": 51, "cy": 478.5},
                {"page": 4, "text": "102695*****", "x1": 84, "x2": 178, "cx": 131, "cy": 478.5},
                {"page": 4, "text": "**258", "x1": 178, "x2": 228, "cx": 203, "cy": 478.5},
                {"page": 4, "text": "法学院", "x1": 236, "x2": 300, "cx": 268, "cy": 478.5},
                {"page": 4, "text": "法律（非法学）", "x1": 690, "x2": 810, "cx": 750, "cy": 478.5},
                {"page": 4, "text": "全日制", "x1": 1029, "x2": 1109, "cx": 1069, "cy": 478.5},
                {"page": 4, "text": "370", "x1": 1161, "x2": 1202, "cx": 1181.5, "cy": 478.5},
                {"page": 4, "text": "450", "x1": 1244, "x2": 1283, "cx": 1264, "cy": 478.5},
                {"page": 4, "text": "402", "x1": 1314, "x2": 1368, "cx": 1341, "cy": 478.5},
                {"page": 5, "text": "陈*宁", "x1": 25, "x2": 78, "cx": 51, "cy": 1089},
                {"page": 5, "text": "1026*95******732", "x1": 84, "x2": 228, "cx": 156, "cy": 1089},
                {"page": 5, "text": "软件工程学院", "x1": 236, "x2": 380, "cx": 308, "cy": 1089},
                {"page": 5, "text": "软件工程", "x1": 690, "x2": 780, "cx": 735, "cy": 1089},
                {"page": 5, "text": "全日制", "x1": 1029, "x2": 1109, "cx": 1069, "cy": 1089},
                {"page": 5, "text": "365", "x1": 1161, "x2": 1202, "cx": 1181.5, "cy": 1089},
                {"page": 5, "text": "430", "x1": 1244, "x2": 1283, "cx": 1264, "cy": 1089},
                {"page": 5, "text": "391", "x1": 1314, "x2": 1368, "cx": 1341, "cy": 1089},
            ],
            source_url="https://example.edu/ecnu.pdf",
        )

        self.assertEqual([row["student_id"] for row in rows], ["102695*******258", "102695******732"])
        self.assertEqual(rows[0]["college"], "法学院")
        self.assertEqual(rows[1]["college"], "软件工程学院")


if __name__ == "__main__":
    unittest.main()
