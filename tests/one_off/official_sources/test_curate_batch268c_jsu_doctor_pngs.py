import unittest


class Batch268cJsuDoctorPngCurationTests(unittest.TestCase):
    def test_curate_batch268c_keeps_only_jsu_doctor_rows_marked_admitted(self):
        from scripts.one_off.official_sources.curate_batch268c_jsu_doctor_pngs import curate_records

        rows = curate_records()

        self.assertEqual(len(rows), 37)
        self.assertEqual(sum(row["school_name"] == "吉首大学" for row in rows), 37)
        self.assertEqual(sum(row["year"] == 2026 for row in rows), 37)
        self.assertEqual(sum(row["document_type"] == "postgraduate_admission_list" for row in rows), 37)
        self.assertEqual(sum(row["route"] == "postgraduate_exam_or_admission" for row in rows), 37)
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["college"], "人文学院")
        self.assertEqual(first["student_id"], "10531610000013")
        self.assertEqual(first["person_name"], "向茜")
        self.assertEqual(first["major"], "民族学")
        self.assertEqual(first["admission_major"], "马克思主义民族理论与政策")
        self.assertIn("报考导师: 丁建军", first["remarks"])
        self.assertIn("综合成绩: 80.41", first["remarks"])

        adjusted = next(row for row in rows if row["person_name"] == "杨凡")
        self.assertIn("研究方向内调剂至龙先琼教授", adjusted["remarks"])

        sports = next(row for row in rows if row["person_name"] == "李雄杰")
        self.assertEqual(sports["college"], "体育科学学院")
        self.assertEqual(sports["admission_major"], "运动人体科学")
        self.assertIn("政治素质考核结论: 合格", sports["remarks"])

        life = next(row for row in rows if row["person_name"] == "罗玉杰")
        self.assertEqual(life["college"], "生命科学学院")
        self.assertEqual(life["student_id"], "105316100000111")
        self.assertEqual(life["admission_major"], "武陵山区可持续生态学")

        excluded_names = {"姜泽", "王湘博", "张梦茹", "徐凯", "彭敬宜", "陈俊峰"}
        self.assertFalse(excluded_names & {row["person_name"] for row in rows})

        joined = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("person_name", "ranking", "remarks"))
            for row in rows
        )
        hard_exclude_terms = (
            "放弃复试",
            "未参加面试",
            "自愿放弃拟录取",
            "拟不录取",
            "不予录取",
            "不合格",
            "候补",
        )
        self.assertFalse(any(term in joined for term in hard_exclude_terms))


if __name__ == "__main__":
    unittest.main()
