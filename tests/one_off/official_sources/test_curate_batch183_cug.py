import unittest


class CugBatch183CurationTests(unittest.TestCase):
    def test_repair_record_moves_name_from_major(self):
        from scripts.one_off.official_sources.curate_batch183_cug import repair_record

        record = repair_record(
            {
                "school_name": "中国地质大学（武汉）",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name": "",
                "student_id": "104916360515662",
                "college": "",
                "major": "王浩林",
                "admission_major": "085400",
                "ranking": "1",
                "remarks": "地理信息软件工程",
                "source_url": "https://gis.cug.edu.cn/example.pdf",
                "title": "2026复试成绩及拟录取名单公示（第一志愿）.pdf",
                "needs_review": "true",
            }
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["person_name"], "王浩林")
        self.assertEqual(record["major"], "")
        self.assertEqual(record["needs_review"], False)
        self.assertNotIn("missing_person_name", record["quality_flags"])
        self.assertNotIn("needs_review", record["quality_flags"])

    def test_repair_record_moves_numeric_college_to_remarks(self):
        from scripts.one_off.official_sources.curate_batch183_cug import repair_record

        record = repair_record(
            {
                "school_name": "中国地质大学（武汉）",
                "year": "2026",
                "document_type": "postgraduate_admission_list",
                "route": "postgraduate_exam_or_admission",
                "person_name": "丁兴",
                "student_id": "104916310517167",
                "college": "115 33",
                "major": "",
                "admission_major": "08570 资源与环境",
                "ranking": "",
                "remarks": "357 71.87 71.59 拟录取 非定向",
                "source_url": "https://ses.cug.edu.cn/example.pdf",
                "title": "环境学院2026年硕士研究生招生复试成绩及拟录取名单公示（一志愿）.pdf",
                "needs_review": "false",
            }
        )

        self.assertIsNotNone(record)
        self.assertEqual(record["college"], "")
        self.assertIn("misparsed_college 115 33", record["remarks"])

    def test_repair_record_drops_unrepairable_empty_name(self):
        from scripts.one_off.official_sources.curate_batch183_cug import repair_record

        self.assertIsNone(
            repair_record(
                {
                    "school_name": "中国地质大学（武汉）",
                    "year": "2026",
                    "document_type": "postgraduate_admission_list",
                    "route": "postgraduate_exam_or_admission",
                    "person_name": "",
                    "student_id": "104916360515662",
                    "college": "",
                    "major": "",
                    "admission_major": "085400",
                    "ranking": "1",
                    "remarks": "地理信息软件工程",
                    "source_url": "https://gis.cug.edu.cn/example.pdf",
                    "title": "2026复试成绩及拟录取名单公示（第一志愿）.pdf",
                    "needs_review": "true",
                }
            )
        )

    def test_repair_record_drops_abandoned_retest_rows(self):
        from scripts.one_off.official_sources.curate_batch183_cug import repair_record

        self.assertIsNone(
            repair_record(
                {
                    "school_name": "中国地质大学（武汉）",
                    "year": "2026",
                    "document_type": "postgraduate_admission_list",
                    "route": "postgraduate_exam_or_admission",
                    "person_name": "于宛彤",
                    "student_id": "103356000911417",
                    "college": "",
                    "major": "化学工程",
                    "admission_major": "放弃复试",
                    "ranking": "",
                    "remarks": "非定向",
                    "source_url": "https://chxy.cug.edu.cn/example.pdf",
                    "title": "材料与化学学院2026年硕士研究生招生调剂复试成绩及拟录取名单公示.pdf",
                    "needs_review": "false",
                }
            )
        )

    def test_dedupe_records_removes_same_person_source_key(self):
        from scripts.one_off.official_sources.curate_batch183_cug import collapse_duplicate_person_source_records

        record = {
            "school_name": "中国地质大学（武汉）",
            "year": "2026",
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": "王浩林",
            "student_id": "104916360515662",
            "college": "",
            "major": "",
            "admission_major": "085400",
            "ranking": "1",
            "source_url": "https://gis.cug.edu.cn/example.pdf",
        }

        self.assertEqual(len(collapse_duplicate_person_source_records([record, dict(record)])), 1)

    def test_collapse_duplicate_person_source_records_merges_direction(self):
        from scripts.one_off.official_sources.curate_batch183_cug import collapse_duplicate_person_source_records

        main = {
            "school_name": "中国地质大学（武汉）",
            "year": "2026",
            "document_type": "postgraduate_admission_list",
            "route": "postgraduate_exam_or_admission",
            "person_name": "何春朝",
            "student_id": "104916360515721",
            "college": "",
            "major": "",
            "admission_major": "085400 电子信息",
            "ranking": "",
            "remarks": "360 81.36 76.68 拟录取 非定向",
            "source_url": "https://gis.cug.edu.cn/example.pdf",
            "title": "2026复试成绩及拟录取名单公示（第一志愿）.pdf",
            "needs_review": False,
        }
        direction = dict(main)
        direction["admission_major"] = "085400"
        direction["ranking"] = "10"
        direction["remarks"] = "地理信息软件工程"

        [merged] = collapse_duplicate_person_source_records([main, direction])

        self.assertEqual(merged["admission_major"], "085400 电子信息")
        self.assertEqual(merged["ranking"], "10")
        self.assertIn("360 81.36 76.68 拟录取 非定向", merged["remarks"])
        self.assertIn("detail 地理信息软件工程", merged["remarks"])


if __name__ == "__main__":
    unittest.main()
