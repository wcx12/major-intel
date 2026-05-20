import unittest

from scripts.setup_entity_aliases import ENTITY_ALIAS_SCHEMA_SQL, MAJOR_ALIAS_SEEDS, build_major_alias_seed_sql


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


if __name__ == "__main__":
    unittest.main()
