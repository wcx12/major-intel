import unittest

from scripts.retrieval_tools import RetrievalTools


class FakeClient:
    def __init__(self, routes=None):
        self.routes = routes or []
        self.queries = []

    def query(self, sql):
        self.queries.append(sql)
        matches = [(needle, rows) for needle, rows in self.routes if needle in sql]
        if matches:
            return max(matches, key=lambda item: len(item[0]))[1]
        return []


def school_row(
    name,
    code,
    school_id,
    *,
    province_name="浙江",
    city_name="杭州市",
    type_name="综合",
    level_name="本科",
):
    return {
        "school_id": school_id,
        "code": code,
        "name": name,
        "province_name": province_name,
        "city_name": city_name,
        "type_name": type_name,
        "level_name": level_name,
        "is985": "0",
        "is211": "0",
        "is_dual_class": "0",
        "dual_class": "0",
        "school_site": f"https://example.edu/{code}",
        "site": f"https://example.edu/{code}/admission",
    }


def alias_school_row(alias_text, name, code, school_id, *, confidence="1.000", province_name="浙江"):
    row = school_row(name, code, school_id, province_name=province_name)
    row["alias_text"] = alias_text
    row["alias_confidence"] = confidence
    return row


HDU = school_row("杭州电子科技大学", "10336", "10124", type_name="理工")
PKU = school_row("北京大学", "10001", "10001", province_name="北京", city_name="海淀区")
SYSU = school_row("中山大学", "10558", "10024", province_name="广东", city_name="广州市")
CSU = school_row("中南大学", "10533", "10041", province_name="湖南", city_name="长沙市")
NJU = school_row("南京大学", "10284", "10010", province_name="江苏", city_name="南京市")
NCU = school_row("南昌大学", "10403", "10073", province_name="江西", city_name="南昌市")
SJTU = school_row("上海交通大学", "10248", "10011", province_name="上海", city_name="闵行区")
XJTU = school_row("西安交通大学", "10698", "10025", province_name="陕西", city_name="西安市")
BJTU = school_row("北京交通大学", "10004", "10065", province_name="北京", city_name="海淀区")
SWJTU = school_row("西南交通大学", "10613", "10077", province_name="四川", city_name="成都市")
PKU_MED = school_row("北京大学医学部", "10001", "10002", province_name="北京", city_name="海淀区", type_name="医药")


class SchoolLookupFunctionCallTests(unittest.TestCase):
    def assert_common_envelope(self, result, status):
        self.assertEqual(
            set(result),
            {
                "tool_name",
                "status",
                "input",
                "normalized_slots",
                "data",
                "scope_notes",
                "data_gaps",
                "needs_clarification",
                "source_tables",
                "warnings",
            },
        )
        self.assertEqual(result["tool_name"], "school_lookup")
        self.assertEqual(result["status"], status)
        self.assertIsInstance(result["input"], dict)
        self.assertIsInstance(result["normalized_slots"], dict)
        self.assertIsInstance(result["data"], dict)
        self.assertIsInstance(result["scope_notes"], list)
        self.assertIsInstance(result["data_gaps"], list)
        self.assertIsInstance(result["needs_clarification"], list)
        self.assertIsInstance(result["source_tables"], list)
        self.assertIsInstance(result["warnings"], list)

    def assert_school_payload(self, result):
        self.assertIn("selected_school", result["data"])
        self.assertIn("candidates", result["data"])
        self.assertIsInstance(result["data"]["selected_school"], dict)
        self.assertIsInstance(result["data"]["candidates"], list)

    def test_missing_school_text_needs_clarification_without_querying_database(self):
        for empty_value in [None, "", "   ", "\n\t"]:
            with self.subTest(empty_value=empty_value):
                client = FakeClient()
                result = RetrievalTools(client).school_lookup(empty_value)

                self.assert_common_envelope(result, "needs_clarification")
                self.assertEqual(result["input"], {"school_text": empty_value})
                self.assertEqual(result["needs_clarification"], ["school_text"])
                self.assertEqual(client.queries, [])

    def test_exact_school_name_falls_back_after_no_alias_match(self):
        client = FakeClient([("FROM edu_university", [HDU])])

        result = RetrievalTools(client).school_lookup("杭州电子科技大学", limit=3)

        self.assert_common_envelope(result, "ok")
        self.assert_school_payload(result)
        self.assertEqual(result["input"], {"school_text": "杭州电子科技大学", "limit": 3})
        self.assertEqual(result["normalized_slots"], {"school_name": "杭州电子科技大学", "school_id": "10124"})
        self.assertEqual(result["data"]["selected_school"]["code"], "10336")
        self.assertEqual(result["data"]["candidates"], [HDU])
        self.assertEqual(len(client.queries), 2)
        self.assertIn("FROM entity_aliases a", client.queries[0])
        self.assertIn("LIMIT 20", client.queries[0])
        self.assertIn("FROM edu_university", client.queries[1])
        self.assertIn("name = '杭州电子科技大学'", client.queries[1])
        self.assertIn("LIMIT 3", client.queries[1])

    def test_school_code_and_school_id_use_exact_fallback_conditions(self):
        client = FakeClient([("FROM edu_university", [HDU])])

        result = RetrievalTools(client).school_lookup("10336", limit=1)

        self.assert_common_envelope(result, "ok")
        self.assertEqual(result["data"]["selected_school"]["name"], "杭州电子科技大学")
        self.assertIn("code = '10336'", client.queries[1])
        self.assertIn("school_id = '10336'", client.queries[1])
        self.assertIn("LIMIT 1", client.queries[1])

    def test_duplicate_school_code_candidates_are_preserved_without_alias_clarification(self):
        client = FakeClient([("FROM edu_university", [PKU, PKU_MED])])

        result = RetrievalTools(client).school_lookup("10001", limit=5)

        self.assert_common_envelope(result, "ok")
        self.assertEqual(result["data"]["selected_school"], PKU)
        self.assertEqual(result["data"]["candidates"], [PKU, PKU_MED])
        self.assertEqual(result["normalized_slots"], {"school_name": "北京大学", "school_id": "10001"})
        self.assertEqual(result["needs_clarification"], [])
        self.assertIn("code = '10001'", client.queries[1])
        self.assertIn("school_id = '10001'", client.queries[1])

    def test_unique_confirmed_alias_returns_ok_and_short_circuits_fallback_query(self):
        alias_row = alias_school_row("北大", "北京大学", "10001", "10001", province_name="北京")
        client = FakeClient(
            [
                ("FROM entity_aliases a", [alias_row]),
                ("FROM edu_university", [HDU]),
            ]
        )

        result = RetrievalTools(client).school_lookup("北大")

        self.assert_common_envelope(result, "ok")
        self.assert_school_payload(result)
        self.assertEqual(result["normalized_slots"], {"school_name": "北京大学", "school_id": "10001"})
        self.assertEqual(result["data"]["selected_school"]["alias_text"], "北大")
        self.assertEqual(result["data"]["selected_school"]["alias_confidence"], "1.000")
        self.assertEqual(client.queries, [client.queries[0]])
        self.assertIn("FROM entity_aliases a", client.queries[0])

    def test_alias_lookup_normalizes_whitespace_and_english_case_before_querying(self):
        alias_row = alias_school_row("SYSU", "中山大学", "10558", "10024", confidence="0.950", province_name="广东")
        client = FakeClient([("FROM entity_aliases a", [alias_row])])

        result = RetrievalTools(client).school_lookup(" S Y S U ")

        self.assert_common_envelope(result, "ok")
        self.assertEqual(result["data"]["selected_school"]["name"], "中山大学")
        self.assertEqual(result["normalized_slots"], {"school_name": "中山大学", "school_id": "10024"})
        self.assertEqual(len(client.queries), 1)
        self.assertIn("alias_normalized = 'sysu'", client.queries[0])

    def test_alias_result_takes_priority_over_misleading_fallback_candidate(self):
        alias_row = alias_school_row("P大", "北京大学", "10001", "10001", confidence="0.900", province_name="北京")
        misleading_fallback = school_row("平顶山学院", "10919", "12000", province_name="河南", city_name="平顶山市")
        client = FakeClient(
            [
                ("FROM entity_aliases a", [alias_row]),
                ("FROM edu_university", [misleading_fallback]),
            ]
        )

        result = RetrievalTools(client).school_lookup("P大")

        self.assert_common_envelope(result, "ok")
        self.assertEqual(result["data"]["selected_school"]["name"], "北京大学")
        self.assertEqual(len(client.queries), 1)
        self.assertNotEqual(result["data"]["selected_school"]["name"], "平顶山学院")

    def test_common_unique_aliases_and_informal_nicknames_resolve_to_canonical_school(self):
        cases = [
            ("P大", alias_school_row("P大", "北京大学", "10001", "10001", confidence="0.900", province_name="北京")),
            ("SYSU", alias_school_row("SYSU", "中山大学", "10558", "10024", confidence="0.950", province_name="广东")),
            (
                "双鸭山大学",
                alias_school_row("双鸭山大学", "中山大学", "10558", "10024", confidence="0.800", province_name="广东"),
            ),
        ]

        for alias_text, alias_row in cases:
            with self.subTest(alias_text=alias_text):
                client = FakeClient([("FROM entity_aliases a", [alias_row])])
                result = RetrievalTools(client).school_lookup(alias_text)

                self.assert_common_envelope(result, "ok")
                self.assertEqual(result["data"]["selected_school"]["name"], alias_row["name"])
                self.assertEqual(result["data"]["selected_school"]["alias_text"], alias_text)
                self.assertEqual(len(client.queries), 1)

    def test_ambiguous_confirmed_alias_returns_candidates_and_requires_clarification(self):
        alias_rows = [
            alias_school_row("中大", "中山大学", "10558", "10024", confidence="0.700", province_name="广东"),
            alias_school_row("中大", "中南大学", "10533", "10041", confidence="0.600", province_name="湖南"),
        ]
        client = FakeClient(
            [
                ("FROM entity_aliases a", alias_rows),
                ("FROM edu_university", [SYSU]),
            ]
        )

        result = RetrievalTools(client).school_lookup("中大")

        self.assert_common_envelope(result, "needs_clarification")
        self.assert_school_payload(result)
        self.assertEqual(result["normalized_slots"], {"school_alias": "中大"})
        self.assertEqual(result["data"]["selected_school"], {})
        self.assertEqual({row["name"] for row in result["data"]["candidates"]}, {"中山大学", "中南大学"})
        self.assertEqual(result["needs_clarification"], ["school_text"])
        self.assertIn("歧义", result["warnings"][0])
        self.assertEqual(len(client.queries), 1)

    def test_ambiguous_alias_uses_wide_candidate_query_even_when_user_limit_is_one(self):
        alias_rows = [
            alias_school_row("交大", "上海交通大学", "10248", "10011", confidence="0.700", province_name="上海"),
            alias_school_row("交大", "西安交通大学", "10698", "10025", confidence="0.700", province_name="陕西"),
            alias_school_row("交大", "北京交通大学", "10004", "10065", confidence="0.600", province_name="北京"),
            alias_school_row("交大", "西南交通大学", "10613", "10077", confidence="0.600", province_name="四川"),
        ]
        client = FakeClient([("FROM entity_aliases a", alias_rows)])

        result = RetrievalTools(client).school_lookup("交大", limit=1)

        self.assert_common_envelope(result, "needs_clarification")
        self.assertEqual(len(result["data"]["candidates"]), 4)
        self.assertEqual(result["input"], {"school_text": "交大", "limit": 1})
        self.assertIn("LIMIT 20", client.queries[0])
        self.assertEqual(len(client.queries), 1)

    def test_all_seeded_ambiguous_alias_families_return_multiple_candidates(self):
        ambiguous_cases = {
            "中大": [SYSU, CSU],
            "南大": [NJU, NCU],
            "交大": [SJTU, XJTU, BJTU, SWJTU],
            "山大": [
                school_row("山东大学", "10422", "10022", province_name="山东", city_name="济南市"),
                school_row("山西大学", "10108", "10128", province_name="山西", city_name="太原市"),
            ],
            "华工": [
                school_row("华南理工大学", "10561", "10048", province_name="广东", city_name="广州市"),
                school_row("华东理工大学", "10251", "10067", province_name="上海", city_name="徐汇区"),
            ],
            "华师": [
                school_row("华东师范大学", "10269", "10051", province_name="上海", city_name="闵行区"),
                school_row("华中师范大学", "10511", "10059", province_name="湖北", city_name="武汉市"),
                school_row("华南师范大学", "10574", "10103", province_name="广东", city_name="广州市"),
            ],
            "湖大": [
                school_row("湖南大学", "10532", "10045", province_name="湖南", city_name="长沙市"),
                school_row("湖北大学", "10512", "10215", province_name="湖北", city_name="武汉市"),
            ],
        }

        for alias_text, schools in ambiguous_cases.items():
            with self.subTest(alias_text=alias_text):
                alias_rows = [
                    {
                        **row,
                        "alias_text": alias_text,
                        "alias_confidence": "0.600",
                    }
                    for row in schools
                ]
                client = FakeClient([("FROM entity_aliases a", alias_rows)])

                result = RetrievalTools(client).school_lookup(alias_text)

                self.assert_common_envelope(result, "needs_clarification")
                self.assertEqual(result["data"]["selected_school"], {})
                self.assertEqual([row["name"] for row in result["data"]["candidates"]], [row["name"] for row in schools])
                self.assertEqual(result["needs_clarification"], ["school_text"])
                self.assertEqual(len(client.queries), 1)

    def test_exact_full_name_of_school_with_ambiguous_short_alias_still_resolves_directly(self):
        client = FakeClient([("FROM edu_university", [NJU])])

        result = RetrievalTools(client).school_lookup("南京大学")

        self.assert_common_envelope(result, "ok")
        self.assertEqual(result["data"]["selected_school"]["name"], "南京大学")
        self.assertEqual(result["needs_clarification"], [])
        self.assertIn("name = '南京大学'", client.queries[1])

    def test_not_found_returns_not_found_without_guessing(self):
        client = FakeClient()

        result = RetrievalTools(client).school_lookup("火星第一职业技术学院")

        self.assert_common_envelope(result, "not_found")
        self.assert_school_payload(result)
        self.assertEqual(result["data"]["selected_school"], {})
        self.assertEqual(result["data"]["candidates"], [])
        self.assertEqual(result["data_gaps"], [])
        self.assertEqual(result["needs_clarification"], [])
        self.assertIn("edu_university", result["source_tables"])
        self.assertIn("entity_aliases", result["source_tables"])
        self.assertTrue(result["warnings"])
        self.assertEqual(len(client.queries), 2)

    def test_one_character_unknown_input_returns_not_found_with_stable_payload(self):
        client = FakeClient()

        result = RetrievalTools(client).school_lookup("大")

        self.assert_common_envelope(result, "not_found")
        self.assert_school_payload(result)
        self.assertEqual(result["data"], {"selected_school": {}, "candidates": []})
        self.assertEqual(result["needs_clarification"], [])
        self.assertIn("name LIKE '%大%'", client.queries[1])

    def test_fallback_fuzzy_match_with_multiple_non_exact_candidates_requires_clarification(self):
        candidates = [
            school_row("中国科学技术大学", "10358", "10014", province_name="安徽", city_name="合肥市"),
            school_row("华中科技大学", "10487", "10013", province_name="湖北", city_name="武汉市"),
        ]
        client = FakeClient([("FROM edu_university", candidates)])

        result = RetrievalTools(client).school_lookup("科技大学")

        self.assert_common_envelope(result, "needs_clarification")
        self.assertEqual(result["data"]["selected_school"], {})
        self.assertEqual(result["data"]["candidates"], candidates)
        self.assertEqual(result["normalized_slots"], {"school_query": "科技大学"})
        self.assertEqual(result["needs_clarification"], ["school_text"])
        self.assertIn("name LIKE '%科技大学%'", client.queries[1])

    def test_fallback_fuzzy_single_character_with_candidates_requires_clarification(self):
        candidates = [
            school_row("北京大学", "10001", "10001", province_name="北京"),
            school_row("清华大学", "10003", "10003", province_name="北京"),
        ]
        client = FakeClient([("FROM edu_university", candidates)])

        result = RetrievalTools(client).school_lookup("大")

        self.assert_common_envelope(result, "needs_clarification")
        self.assertEqual(result["data"]["selected_school"], {})
        self.assertEqual(result["data"]["candidates"], candidates)
        self.assertEqual(result["normalized_slots"], {"school_query": "大"})
        self.assertEqual(result["needs_clarification"], ["school_text"])
        self.assertIn("name LIKE '%大%'", client.queries[1])

    def test_fallback_query_includes_short_old_name_and_alias_subquery_conditions(self):
        client = FakeClient([("FROM edu_university", [NJU])])

        result = RetrievalTools(client).school_lookup("国立中央大学")

        self.assert_common_envelope(result, "ok")
        fallback_sql = client.queries[1]
        self.assertEqual(result["data"]["selected_school"]["name"], "南京大学")
        self.assertIn("name IN (", fallback_sql)
        self.assertIn("code IN (", fallback_sql)
        self.assertIn("short LIKE '%国立中央大学%'", fallback_sql)
        self.assertIn("old_name LIKE '%国立中央大学%'", fallback_sql)
        self.assertIn("name LIKE '%国立中央大学%'", fallback_sql)

    def test_alias_candidate_query_shape_joins_confirmed_aliases_to_university_rows(self):
        alias_row = alias_school_row("南七技校", "中国科学技术大学", "10358", "10014", confidence="0.800", province_name="安徽")
        client = FakeClient([("FROM entity_aliases a", [alias_row])])

        result = RetrievalTools(client).school_lookup("南七技校")

        self.assert_common_envelope(result, "ok")
        alias_sql = client.queries[0]
        self.assertIn("JOIN edu_university u", alias_sql)
        self.assertIn("u.name = a.canonical_name", alias_sql)
        self.assertIn("a.status = 'active'", alias_sql)
        self.assertIn("(a.deleted IS NULL OR a.deleted = b'0')", alias_sql)
        self.assertIn("u.deleted = b'0'", alias_sql)

    def test_single_quote_input_is_sql_quoted_in_alias_and_fallback_queries(self):
        client = FakeClient()

        result = RetrievalTools(client).school_lookup("O'Connor大学")

        self.assert_common_envelope(result, "not_found")
        self.assertIn("alias_normalized = 'o''connor大学'", client.queries[0])
        self.assertIn("name = 'O''Connor大学'", client.queries[1])
        self.assertIn("name LIKE '%O''Connor大学%'", client.queries[1])


if __name__ == "__main__":
    unittest.main()
