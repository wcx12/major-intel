import unittest

from scripts.setup_entity_aliases import (
    ENTITY_ALIAS_SCHEMA_SQL,
    MAJOR_ALIAS_SEEDS,
    SCHOOL_ALIAS_SEEDS,
    build_major_alias_seed_sql,
    build_school_alias_seed_sql,
)


class SetupEntityAliasesTests(unittest.TestCase):
    def test_schema_creates_confirmed_and_candidate_alias_tables(self):
        schema_sql = "\n".join(ENTITY_ALIAS_SCHEMA_SQL)

        self.assertIn("CREATE TABLE IF NOT EXISTS entity_aliases", schema_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS entity_alias_candidates", schema_sql)
        self.assertIn("alias_normalized", schema_sql)
        self.assertIn("canonical_code", schema_sql)
        self.assertIn("UNIQUE KEY uk_entity_alias", schema_sql)
        self.assertIn("utf8mb4_0900_ai_ci", schema_sql)
        self.assertIn("ALTER TABLE entity_aliases CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci", schema_sql)

    def test_major_alias_seed_sql_contains_common_confirmed_short_names(self):
        seed_sql = build_major_alias_seed_sql()

        self.assertIn("计科", seed_sql)
        self.assertIn("计算机科学与技术", seed_sql)
        self.assertIn("080901", seed_sql)
        self.assertIn("软工", seed_sql)
        self.assertGreaterEqual(len(MAJOR_ALIAS_SEEDS), 10)

    def test_school_alias_seed_sql_contains_common_confirmed_short_names(self):
        seed_sql = build_school_alias_seed_sql()

        self.assertIn("杭电", seed_sql)
        self.assertIn("杭州电子科技大学", seed_sql)
        self.assertIn("10336", seed_sql)
        self.assertIn("北大", seed_sql)
        self.assertIn("P大", seed_sql)
        self.assertIn("北京大学", seed_sql)
        self.assertIn("清华", seed_sql)
        self.assertIn("五道口职业技术学院", seed_sql)
        self.assertIn("北邮", seed_sql)
        self.assertIn("重邮", seed_sql)
        self.assertIn("重庆邮电大学", seed_sql)
        self.assertIn("北工大", seed_sql)
        self.assertIn("北京工业大学", seed_sql)
        self.assertIn("哈工", seed_sql)
        self.assertIn("哈尔滨工业大学", seed_sql)
        self.assertIn("紫金港职业技术学院", seed_sql)
        self.assertIn("南京航空航天大学", seed_sql)
        self.assertIn("九乡河文理学院", seed_sql)
        self.assertIn("中科大", seed_sql)
        self.assertIn("南七技校", seed_sql)
        self.assertIn("珞珈山职业技术学院", seed_sql)
        self.assertIn("关山口职业技术学院", seed_sql)
        self.assertIn("马房山男子职业技术学院", seed_sql)
        self.assertIn("武汉理工大学", seed_sql)
        self.assertIn("10497", seed_sql)
        self.assertIn("国科大", seed_sql)
        self.assertIn("SYSU", seed_sql)
        self.assertIn("双鸭山大学", seed_sql)
        self.assertIn("中山大学", seed_sql)
        self.assertIn("10558", seed_sql)
        self.assertIn("'school'", seed_sql)
        self.assertGreaterEqual(len(SCHOOL_ALIAS_SEEDS), 50)

    def test_school_alias_seeds_keep_ambiguous_short_names_as_multi_candidates(self):
        names_by_alias = {}
        for alias_text, canonical_name, _canonical_code, _source, _confidence in SCHOOL_ALIAS_SEEDS:
            names_by_alias.setdefault(alias_text, set()).add(canonical_name)

        self.assertEqual({"中山大学", "中南大学"}, names_by_alias["中大"])
        self.assertEqual({"南京大学", "南昌大学"}, names_by_alias["南大"])
        self.assertEqual({"山东大学", "山西大学"}, names_by_alias["山大"])
        self.assertEqual({"河南大学", "河北大学"}, names_by_alias["河大"])
        self.assertEqual({"华南理工大学", "华东理工大学"}, names_by_alias["华工"])
        self.assertEqual({"华东师范大学", "华中师范大学", "华南师范大学"}, names_by_alias["华师"])
        self.assertEqual({"湖南大学", "湖北大学"}, names_by_alias["湖大"])
        self.assertEqual(
            {"上海交通大学", "西安交通大学", "北京交通大学", "西南交通大学"},
            names_by_alias["交大"],
        )


if __name__ == "__main__":
    unittest.main()
