import unittest

from scripts.one_off.official_sources.curate_batch483_gszy_2024_master_pdf import (
    parse_exam_records_from_text,
    parse_recommendation_records_from_layout,
)


class CurateBatch483Gszy2024MasterPdfTests(unittest.TestCase):
    def test_parse_exam_records_keeps_admitted_qualified_rows(self):
        text = (
            "1 106984622120194 83100 生物医学工程 316 82.45 70.90 拟录取 调剂 合格\n"
            "2 102524210009342 83100 生物医学工程 303 85.62 70.61 拟淘汰 调剂 合格\n"
            "3 106214081204160 83100 生物医学工程 292 86.14 69.50 拟录取 调剂 不合格\n"
        )

        rows, skipped = parse_exam_records_from_text(text)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["student_id"], "106984622120194")
        self.assertEqual(rows[0]["admission_major"], "083100|生物医学工程")
        self.assertIn("official_admission_status: 拟录取", rows[0]["remarks"])
        self.assertEqual(len(skipped), 2)

    def test_parse_exam_records_handles_multiline_major_and_soldier_plan(self):
        text = (
            "111 107354051051232 105105 精神病与精神卫生\n"
            "学\n"
            "325 79.51 70.80 拟录取 一志愿 合格\n"
            "361 107354051231808 105123 放射影像学 301 74.80 66.04 \n"
            "拟录取\n"
            "（士兵计\n"
            "划）\n"
            "一志愿 合格\n"
            "186 104414376606345 1005Z3 卫生事业管理学 354 90.94 86.60 拟录取 调剂\n"
        )

        rows, skipped = parse_exam_records_from_text(text)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["admission_major"], "105105|精神病与精神卫生学")
        self.assertIn("拟录取（士兵计划）", rows[1]["remarks"])
        self.assertEqual(rows[1]["student_id"], "107354051231808")
        self.assertEqual(len(skipped), 1)

    def test_parse_recommendation_records_from_layout(self):
        layout = (
            " 1   包彩银           83100 生物医学工程                    拟录取 推免及“5+3”   合格\n"
            "48   王正平   105703   中医骨伤科学    拟录取   推免及“5+3”   合格\n"
            "49   张喆    105703   中医骨伤科学    拟淘汰   推免及“5+3”   合格\n"
        )

        rows = parse_recommendation_records_from_layout(layout)

        self.assertEqual([row["person_name"] for row in rows], ["包彩银", "王正平"])
        self.assertEqual(rows[0]["admission_major"], "083100|生物医学工程")
        self.assertEqual(rows[1]["admission_major"], "105703|中医骨伤科学")
        self.assertIn("admission_method: 推免及\"5+3\"", rows[0]["remarks"])


if __name__ == "__main__":
    unittest.main()
