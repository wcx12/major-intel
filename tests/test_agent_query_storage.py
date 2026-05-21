import unittest


class AgentQueryStorageTests(unittest.TestCase):
    def test_schema_sql_creates_log_cache_and_trace_tables(self):
        from scripts.agent_query_storage import build_agent_storage_schema_sql

        sql = build_agent_storage_schema_sql()

        self.assertIn("CREATE TABLE IF NOT EXISTS query_logs", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS retrieval_cache", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS agent_tool_traces", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS data_gap_queue", sql)
        self.assertIn("cache_key CHAR(64) NOT NULL", sql)
        self.assertIn("tool_trace_json JSON NULL", sql)
        self.assertIn("gap_key CHAR(64) NOT NULL", sql)
        self.assertIn("UNIQUE KEY uk_data_gap_queue_gap_key", sql)

    def test_cache_key_is_stable_for_sorted_slots_and_tool_plan(self):
        from scripts.agent_query_storage import build_cache_identity

        left_key, left_source = build_cache_identity(
            question="广东物理 580 想学计算机",
            mode="auto",
            route="rules",
            intent="rank_to_major_match",
            slots={"score": 580, "province": "广东", "major_text": "计算机", "subject_type": "物理"},
            tool_plan=[{"tool_name": "rank_to_major_match", "arguments": {"major_text": "计算机", "score": 580}}],
        )
        right_key, right_source = build_cache_identity(
            question=" 广东物理   580 想学计算机 ",
            mode="auto",
            route="rules",
            intent="rank_to_major_match",
            slots={"subject_type": "物理", "major_text": "计算机", "province": "广东", "score": 580},
            tool_plan=[{"arguments": {"score": 580, "major_text": "计算机"}, "tool_name": "rank_to_major_match"}],
        )

        self.assertEqual(left_key, right_key)
        self.assertEqual(left_source, right_source)
        self.assertEqual(len(left_key), 64)
        self.assertEqual(left_source["version"], "agent-cache-v1")

    def test_base64_json_roundtrip_decodes_cached_payload(self):
        from scripts.agent_query_storage import _decode_base64_text, _json_loads
        import base64

        payload = '{"status":"ok","answer_markdown":"第一行\\n第二行"}'
        encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")

        self.assertEqual(_json_loads(_decode_base64_text(encoded), default=None)["status"], "ok")

    def test_build_data_gap_items_uses_normalized_slots_and_stable_key(self):
        from scripts.agent_query_storage import build_data_gap_items

        result = {
            "status": "not_found",
            "route": "rules",
            "intent": "rank_to_major_match",
            "slots": {"province": "广东", "subject_type": "物理", "score": 580, "major_text": "计算机"},
            "data_gaps": ["本地专业录取历史", "学校专业级就业地域分布"],
            "warnings": ["本地库没有命中 2025 年广东物理计算机方向录取样本。"],
        }

        first_items = build_data_gap_items(
            question="广东物理 580 想学计算机",
            mode="auto",
            result=result,
            query_log_id="log_1",
            session_id="s1",
        )
        second_items = build_data_gap_items(
            question=" 广东物理   580 想学计算机 ",
            mode="auto",
            result={**result, "warnings": ["另一次运行的提示不应该改变 gap_key。"]},
            query_log_id="log_2",
            session_id="s2",
        )

        self.assertEqual(len(first_items), 1)
        self.assertEqual(first_items[0]["question_type"], "rank_to_major_match")
        self.assertEqual(first_items[0]["province"], "广东")
        self.assertEqual(first_items[0]["subject_type"], "物理")
        self.assertEqual(first_items[0]["major_text"], "计算机")
        self.assertEqual(first_items[0]["year"], None)
        self.assertEqual(first_items[0]["missing_fields"], ["本地专业录取历史", "学校专业级就业地域分布"])
        self.assertEqual(first_items[0]["status"], "pending")
        self.assertEqual(first_items[0]["priority"], 1)
        self.assertEqual(first_items[0]["query_log_id"], "log_1")
        self.assertEqual(first_items[0]["session_id"], "s1")
        self.assertEqual(len(first_items[0]["gap_key"]), 64)
        self.assertEqual(first_items[0]["gap_key"], second_items[0]["gap_key"])

    def test_write_data_gap_items_uses_sql_null_for_missing_query_log_id(self):
        from scripts.agent_query_storage import MysqlAgentQueryStorage

        statements = []
        storage = object.__new__(MysqlAgentQueryStorage)
        storage.execute = statements.append
        gap_key = "a" * 64

        storage.write_data_gap_items(
            [
                {
                    "id": "b" * 32,
                    "gap_key": gap_key,
                    "query_log_id": None,
                    "session_id": "s1",
                    "question_type": "codex_smoke",
                    "missing_fields": ["missing"],
                    "user_question": "question",
                    "normalized_question": "question",
                }
            ]
        )

        self.assertIn(f"'{gap_key}', NULL, 's1'", statements[0])


if __name__ == "__main__":
    unittest.main()
