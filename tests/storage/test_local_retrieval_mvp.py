import unittest

from scripts.local_retrieval_mvp import (
    _parse_mysql_tsv,
    build_profile,
    build_school_major_sql,
    normalize_major_query,
    render_markdown_answer,
    resolve_major_alias_candidates_sql,
    resolve_major_sql,
    resolve_school_alias_candidates_sql,
    resolve_school_sql,
)


SCHOOL = {
    "school_id": "10124",
    "code": "10336",
    "name": "杭州电子科技大学",
    "province_name": "浙江",
    "city_name": "杭州市",
    "is211": "0",
    "is_dual_class": "0",
    "school_site": "https://www.hdu.edu.cn/main.htm",
}

MAJOR = {
    "code": "080202",
    "special_name": "机械设计制造及其自动化",
    "level2_name": "工学",
    "level3_name": "机械类",
    "limit_year": "四年",
    "degree": "工学学士",
    "salaryavg": "115748",
    "fivesalaryavg": "16900",
    "job": "面向机械设计、制造、自动化相关岗位。",
}

SCHOOL_MAJOR = {
    "major_code": "080202",
    "major_name": "机械设计制造及其自动化",
    "nation_first_class": "0",
    "ruanke_level": "",
}

EMPLOYMENT = {
    "year": "2025",
    "employment_rate": "",
    "further_study_rate": "40.00",
    "avg_salary": "",
}


class LocalRetrievalMvpTests(unittest.TestCase):
    def test_major_lookup_alias_avoids_short_fuzzy_match(self):
        sql = resolve_major_sql("计科")

        self.assertIn("FROM entity_aliases", sql)
        self.assertIn("alias_normalized = '计科'", sql)
        self.assertNotIn("计算机科学与技术", sql)
        self.assertNotIn("special_name LIKE '%计科%'", sql)

    def test_major_lookup_normalizes_common_admission_suffixes_before_sql(self):
        self.assertEqual(normalize_major_query(" 软件工程专业 "), "软件工程")
        self.assertEqual(normalize_major_query("软件工程(中外合作办学)"), "软件工程")
        self.assertEqual(normalize_major_query("计算机科学与技术（师范）"), "计算机科学与技术")
        self.assertEqual(normalize_major_query("临床医学五年制"), "临床医学")

        sql = resolve_major_sql("软件工程(中外合作办学)")

        self.assertIn("special_name = '软件工程'", sql)
        self.assertNotIn("中外合作办学", sql)

    def test_major_alias_candidate_sql_uses_confirmed_alias_table(self):
        sql = resolve_major_alias_candidates_sql("电信")

        self.assertIn("FROM entity_aliases a", sql)
        self.assertIn("JOIN edu_major m", sql)
        self.assertIn("a.entity_type = 'major'", sql)
        self.assertIn("a.alias_normalized = '电信'", sql)
        self.assertIn("ORDER BY a.confidence DESC", sql)

    def test_major_lookup_orders_undergraduate_before_specialist_for_same_name(self):
        sql = resolve_major_sql("临床医学")

        self.assertIn("WHEN code REGEXP '^(0[1-9]|1[0-4])' THEN 0", sql)
        self.assertIn("WHEN type_name LIKE '本科%' THEN 0", sql)

    def test_school_lookup_uses_confirmed_alias_table_for_short_names(self):
        sql = resolve_school_sql("杭电")

        self.assertIn("FROM entity_aliases", sql)
        self.assertIn("entity_type = 'school'", sql)
        self.assertIn("alias_normalized = '杭电'", sql)
        self.assertIn("name IN (", sql)
        self.assertIn("code IN (", sql)

    def test_school_lookup_orders_current_name_matches_before_old_name_matches(self):
        sql = resolve_school_sql("中国地质大学")

        name_rank = sql.index("WHEN name LIKE '%中国地质大学%' THEN")
        old_name_rank = sql.index("WHEN old_name LIKE '%中国地质大学%' THEN")

        self.assertLess(name_rank, old_name_rank)

    def test_school_alias_candidate_sql_orders_without_distinct_mysql_conflict(self):
        sql = resolve_school_alias_candidates_sql("中大")

        self.assertNotIn("SELECT DISTINCT", sql)
        self.assertIn("FROM entity_aliases a", sql)
        self.assertIn("JOIN edu_university u", sql)
        self.assertIn("ORDER BY a.confidence DESC, u.hits DESC", sql)

    def test_parse_mysql_tsv_decodes_escaped_newlines_and_nulls(self):
        rows = _parse_mysql_tsv("id\tdescription\toptional\n1\t第一行\\r\\n第二行\tNULL\n")

        self.assertEqual(rows, [{"id": "1", "description": "第一行\r\n第二行", "optional": None}])

    def test_parse_mysql_tsv_keeps_carriage_return_inside_text_field(self):
        rows = _parse_mysql_tsv("id\tdescription\toptional\r\n1\t第一行\r\\n第二行\tNULL\r\n")

        self.assertEqual(rows, [{"id": "1", "description": "第一行\r\n第二行", "optional": None}])

    def test_school_major_lookup_uses_university_code_and_name(self):
        sql = build_school_major_sql(SCHOOL, MAJOR)

        self.assertIn("sm.school_id = '10336'", sql)
        self.assertIn("sm.school_name = '杭州电子科技大学'", sql)
        self.assertIn("sm.major_code = '080202'", sql)
        self.assertNotIn("sm.school_id = '10124'", sql)

    def test_latest_employment_sql_includes_structured_employment_data(self):
        from scripts.local_retrieval_mvp import build_latest_employment_sql

        sql = build_latest_employment_sql(SCHOOL)

        self.assertIn("employment_data", sql)
        self.assertIn("top_employment_industries", sql)

    def test_build_profile_marks_available_and_missing_data(self):
        profile = build_profile(
            school=SCHOOL,
            major=MAJOR,
            school_major=SCHOOL_MAJOR,
            subject_evals=[],
            dual_classes=[],
            employment=EMPLOYMENT,
            specialty_groups=[],
        )

        self.assertTrue(profile["facts"]["school_major_opened"])
        self.assertIn("学校-专业开设关系", profile["available_data"])
        self.assertIn("学校层面就业/升学数据", profile["available_data"])
        self.assertIn("校专业级工作地域分布", profile["missing_data"])
        self.assertIn("校专业级薪资分布", profile["missing_data"])
        self.assertIn("转专业政策", profile["missing_data"])
        self.assertIn("考公岗位映射", profile["missing_data"])

    def test_render_markdown_labels_scope_and_missing_data(self):
        profile = build_profile(
            school=SCHOOL,
            major=MAJOR,
            school_major=SCHOOL_MAJOR,
            subject_evals=[],
            dual_classes=[],
            employment=EMPLOYMENT,
            specialty_groups=[],
        )

        markdown = render_markdown_answer(profile)

        self.assertIn("# 杭州电子科技大学 机械设计制造及其自动化 本地库检索结果", markdown)
        self.assertIn("已在本地库查到该校开设这个专业", markdown)
        self.assertIn("专业通用参考，不代表杭州电子科技大学该专业毕业生真实薪资", markdown)
        self.assertIn("学校层面数据，不代表某个专业", markdown)
        self.assertIn("## 仍缺的数据", markdown)
        self.assertIn("校专业级工作地域分布", markdown)


if __name__ == "__main__":
    unittest.main()
