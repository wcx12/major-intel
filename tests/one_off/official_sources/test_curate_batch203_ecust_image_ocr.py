import unittest


class Batch203EcustImageOcrCurationTests(unittest.TestCase):
    def test_extract_image_urls_keeps_page_order(self):
        from scripts.one_off.official_sources.curate_batch203_ecust_image_ocr import extract_ecust_image_urls

        html = (
            '<img src="/_upload/article/images/a/page001.jpg" '
            'original-src="2026-list-0001.jpg" />'
            '<img src="/_upload/article/images/a/page002.jpg" '
            'original-src="2026-list-0002.jpg" />'
        )

        self.assertEqual(
            extract_ecust_image_urls(html, "https://gschool.ecust.edu.cn/2026/0506/c12750a190107/page.htm"),
            [
                "https://gschool.ecust.edu.cn/_upload/article/images/a/page001.jpg",
                "https://gschool.ecust.edu.cn/_upload/article/images/a/page002.jpg",
            ],
        )

    def test_records_from_ocr_words_reconstructs_row_by_coordinates(self):
        from scripts.one_off.official_sources.curate_batch203_ecust_image_ocr import records_from_ocr_words

        words = [
            {"text": "1", "x": 305, "y": 459, "w": 9, "h": 26},
            {"text": "102516000005716", "x": 422, "y": 459, "w": 288, "h": 26},
            {"text": "\u7126", "x": 768, "y": 458, "w": 32, "h": 32},
            {"text": "\u6587", "x": 804, "y": 459, "w": 31, "h": 31},
            {"text": "\u7ea2", "x": 840, "y": 459, "w": 31, "h": 29},
            {"text": "\u5316", "x": 1016, "y": 459, "w": 32, "h": 32},
            {"text": "\u5de5", "x": 1052, "y": 459, "w": 31, "h": 31},
            {"text": "\u5b66", "x": 1087, "y": 459, "w": 32, "h": 31},
            {"text": "\u9662", "x": 1124, "y": 459, "w": 31, "h": 31},
            {"text": "081700", "x": 1322, "y": 459, "w": 100, "h": 26},
            {"text": "\u5316", "x": 1450, "y": 459, "w": 32, "h": 32},
            {"text": "\u5b66", "x": 1486, "y": 459, "w": 31, "h": 31},
            {"text": "\u5de5", "x": 1521, "y": 459, "w": 31, "h": 31},
            {"text": "\u7a0b", "x": 1556, "y": 459, "w": 31, "h": 31},
            {"text": "\u4e0e", "x": 1591, "y": 459, "w": 31, "h": 31},
            {"text": "\u6280", "x": 1626, "y": 459, "w": 31, "h": 31},
            {"text": "\u672f", "x": 1662, "y": 459, "w": 31, "h": 31},
            {"text": "\u5168", "x": 1853, "y": 459, "w": 32, "h": 32},
            {"text": "\u65e5", "x": 1894, "y": 459, "w": 31, "h": 31},
            {"text": "\u5236", "x": 1925, "y": 459, "w": 31, "h": 31},
            {"text": "419", "x": 2134, "y": 459, "w": 55, "h": 26},
            {"text": "87", "x": 2327, "y": 459, "w": 37, "h": 26},
            {"text": "\uff0e", "x": 2368, "y": 459, "w": 8, "h": 26},
            {"text": "17", "x": 2377, "y": 459, "w": 37, "h": 26},
            {"text": "84", "x": 2524, "y": 459, "w": 37, "h": 26},
            {"text": "812", "x": 2573, "y": 459, "w": 55, "h": 26},
            {"text": "\u975e", "x": 2733, "y": 459, "w": 31, "h": 31},
            {"text": "\u5b9a", "x": 2769, "y": 459, "w": 31, "h": 31},
            {"text": "\u5411", "x": 2806, "y": 459, "w": 31, "h": 31},
        ]

        records = records_from_ocr_words(
            words,
            source_url="https://gschool.ecust.edu.cn/_upload/article/images/a/page001.jpg",
            title="\u534e\u4e1c\u7406\u5de5\u5927\u5b662026\u5e74\u7855\u58eb\u7814\u7a76\u751f\u62df\u5f55\u53d6\u540d\u5355\u516c\u793a",
        )

        self.assertEqual(len(records), 1)
        row = records[0]
        self.assertEqual(row["school_name"], "\u534e\u4e1c\u7406\u5de5\u5927\u5b66")
        self.assertEqual(row["person_name"], "\u7126\u6587\u7ea2")
        self.assertEqual(row["student_id"], "102516000005716")
        self.assertEqual(row["college"], "\u5316\u5de5\u5b66\u9662")
        self.assertEqual(row["admission_major"], "081700 \u5316\u5b66\u5de5\u7a0b\u4e0e\u6280\u672f")
        self.assertIn("learning_mode \u5168\u65e5\u5236", row["remarks"])
        self.assertIn("initial_score 419", row["remarks"])
        self.assertIn("reexam_score 87.17", row["remarks"])
        self.assertIn("total_score 84.812", row["remarks"])
        self.assertIn("admission_category \u975e\u5b9a\u5411", row["remarks"])
        self.assertFalse(row["needs_review"])

    def test_records_from_ocr_words_accepts_letter_major_code_and_left_shifted_college(self):
        from scripts.one_off.official_sources.curate_batch203_ecust_image_ocr import records_from_ocr_words

        words = [
            {"text": "102516000000830", "x": 422, "y": 459, "w": 288, "h": 26},
            {"text": "\u5f20", "x": 786, "y": 459, "w": 32, "h": 31},
            {"text": "\u9732", "x": 822, "y": 459, "w": 32, "h": 31},
            {"text": "\u9732", "x": 858, "y": 459, "w": 32, "h": 31},
            {"text": "\u836f", "x": 930, "y": 459, "w": 32, "h": 31},
            {"text": "\u5b66", "x": 966, "y": 459, "w": 32, "h": 31},
            {"text": "\u9662", "x": 1002, "y": 459, "w": 32, "h": 31},
            {"text": "0817Z3", "x": 1322, "y": 459, "w": 100, "h": 26},
            {"text": "\u5236", "x": 1450, "y": 459, "w": 32, "h": 32},
            {"text": "\u836f", "x": 1486, "y": 459, "w": 31, "h": 31},
            {"text": "\u5de5", "x": 1521, "y": 459, "w": 31, "h": 31},
            {"text": "\u7a0b", "x": 1556, "y": 459, "w": 31, "h": 31},
            {"text": "\u4e0e", "x": 1591, "y": 459, "w": 31, "h": 31},
            {"text": "\u6280", "x": 1626, "y": 459, "w": 31, "h": 31},
            {"text": "\u672f", "x": 1662, "y": 459, "w": 31, "h": 31},
        ]

        records = records_from_ocr_words(words, source_url="https://example.test/page.jpg")

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["college"], "\u836f\u5b66\u9662")
        self.assertEqual(records[0]["admission_major"], "0817Z3 \u5236\u836f\u5de5\u7a0b\u4e0e\u6280\u672f")
        self.assertFalse(records[0]["needs_review"])

    def test_records_from_ocr_words_repairs_double_zero_major_code_read_as_m(self):
        from scripts.one_off.official_sources.curate_batch203_ecust_image_ocr import records_from_ocr_words

        words = [
            {"text": "102516000000971", "x": 422, "y": 459, "w": 288, "h": 26},
            {"text": "\u738b", "x": 786, "y": 459, "w": 32, "h": 31},
            {"text": "\u7cb2", "x": 822, "y": 459, "w": 32, "h": 31},
            {"text": "\u6750", "x": 930, "y": 459, "w": 32, "h": 31},
            {"text": "\u6599", "x": 966, "y": 459, "w": 32, "h": 31},
            {"text": "\u5b66", "x": 1002, "y": 459, "w": 32, "h": 31},
            {"text": "\u9662", "x": 1038, "y": 459, "w": 32, "h": 31},
            {"text": "0805m", "x": 1322, "y": 459, "w": 100, "h": 26},
            {"text": "\u6750", "x": 1450, "y": 459, "w": 32, "h": 32},
            {"text": "\u6599", "x": 1486, "y": 459, "w": 31, "h": 31},
            {"text": "\u79d1", "x": 1521, "y": 459, "w": 31, "h": 31},
            {"text": "\u5b66", "x": 1556, "y": 459, "w": 31, "h": 31},
            {"text": "\u4e0e", "x": 1591, "y": 459, "w": 31, "h": 31},
            {"text": "\u5de5", "x": 1626, "y": 459, "w": 31, "h": 31},
            {"text": "\u7a0b", "x": 1662, "y": 459, "w": 31, "h": 31},
        ]

        records = records_from_ocr_words(words, source_url="https://example.test/page.jpg")

        self.assertEqual(records[0]["admission_major"], "080500 \u6750\u6599\u79d1\u5b66\u4e0e\u5de5\u7a0b")
        self.assertFalse(records[0]["needs_review"])


if __name__ == "__main__":
    unittest.main()
