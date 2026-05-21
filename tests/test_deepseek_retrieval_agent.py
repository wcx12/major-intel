import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


def _message(content=None, tool_calls=None):
    return SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls or [])


def _tool_call(call_id, name, arguments):
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(name=name, arguments=arguments),
    )


def _response(message):
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeCompletions:
    def __init__(self, messages):
        self._messages = list(messages)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _response(self._messages.pop(0))


class FakeClient:
    def __init__(self, messages):
        self.completions = FakeCompletions(messages)
        self.chat = SimpleNamespace(completions=self.completions)


class DeepSeekRetrievalAgentTests(unittest.TestCase):
    def test_registers_tools_and_disables_thinking_for_first_pass(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        client = FakeClient([_message(content="最终回答")])
        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "school_lookup"}}],
        )

        result = agent.run("杭电怎么样？")

        self.assertEqual(result, "最终回答")
        call = client.completions.calls[0]
        self.assertEqual(call["model"], "deepseek-v4-pro")
        self.assertEqual(call["tools"][0]["function"]["name"], "school_lookup")
        self.assertEqual(call["tool_choice"], "auto")
        self.assertEqual(call["extra_body"], {"thinking": {"type": "disabled"}})
        self.assertEqual(call["temperature"], 0.1)
        self.assertIn("不要使用 emoji", call["messages"][0]["content"])
        self.assertIn("Markdown", call["messages"][0]["content"])
        self.assertIn("---", call["messages"][0]["content"])
        self.assertIn("志愿填报小导师", call["messages"][0]["content"])
        self.assertIn("先给明确判断", call["messages"][0]["content"])
        self.assertIn("适合什么样的考生", call["messages"][0]["content"])
        self.assertIn("下一步建议", call["messages"][0]["content"])
        self.assertIn("自然、清晰、有人味", call["messages"][0]["content"])
        self.assertIn("帮他收窄选择", call["messages"][0]["content"])
        self.assertIn("直接指出风险", call["messages"][0]["content"])
        self.assertIn("不要长篇解释", call["messages"][0]["content"])
        self.assertIn("不能攻击用户", call["messages"][0]["content"])

    def test_temperature_can_be_overridden_for_style_experiments(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        client = FakeClient([_message(content="最终回答")])
        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "school_lookup"}}],
            temperature=0.0,
        )

        agent.run("杭电怎么样？")

        self.assertEqual(client.completions.calls[0]["temperature"], 0.0)

    def test_executes_tool_call_and_sends_tool_result_back_to_model(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        tool_call = _tool_call(
            "call_1",
            "school_lookup",
            json.dumps({"school_text": "杭电"}, ensure_ascii=False),
        )
        client = FakeClient([
            _message(tool_calls=[tool_call]),
            _message(content="杭电的工具结果已经整理好了。"),
        ])
        dispatcher_calls = []

        def dispatch(name, arguments):
            dispatcher_calls.append((name, arguments))
            return {
                "tool_name": name,
                "status": "ok",
                "data": {"selected_school": {"name": "杭州电子科技大学"}},
                "warnings": [],
                "scope_notes": [],
            }

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "school_lookup"}}],
            dispatcher=dispatch,
        )

        result = agent.run("杭电怎么样？")

        self.assertEqual(result, "杭电的工具结果已经整理好了。")
        self.assertEqual(dispatcher_calls, [("school_lookup", {"school_text": "杭电"})])
        second_messages = client.completions.calls[1]["messages"]
        tool_messages = [message for message in second_messages if message.get("role") == "tool"]
        self.assertEqual(tool_messages[0]["tool_call_id"], "call_1")
        payload = json.loads(tool_messages[0]["content"])
        self.assertEqual(payload["data"]["selected_school"]["name"], "杭州电子科技大学")

    def test_invalid_tool_arguments_are_returned_as_tool_error_without_dispatching(self):
        from scripts.deepseek_retrieval_agent import DeepSeekRetrievalAgent

        tool_call = _tool_call("call_bad", "school_lookup", "{bad json")
        client = FakeClient([
            _message(tool_calls=[tool_call]),
            _message(content="我需要你重新提供学校名称。"),
        ])

        def dispatch(name, arguments):  # pragma: no cover - should not be called
            raise AssertionError("dispatcher should not receive invalid JSON arguments")

        agent = DeepSeekRetrievalAgent(
            client=client,
            tools=[{"type": "function", "function": {"name": "school_lookup"}}],
            dispatcher=dispatch,
        )

        result = agent.run("查一下")

        self.assertEqual(result, "我需要你重新提供学校名称。")
        tool_message = [
            message for message in client.completions.calls[1]["messages"] if message.get("role") == "tool"
        ][0]
        payload = json.loads(tool_message["content"])
        self.assertEqual(payload["tool_name"], "school_lookup")
        self.assertEqual(payload["status"], "error")
        self.assertIn("not valid JSON", payload["warnings"][0])

    def test_load_env_file_reads_deepseek_api_key_placeholder_location(self):
        from scripts.deepseek_retrieval_agent import load_env_file

        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text('DEEPSEEK_API_KEY="sk-test"\nOTHER=value\n', encoding="utf-8")

            values = load_env_file(env_path)

        self.assertEqual(values["DEEPSEEK_API_KEY"], "sk-test")
        self.assertEqual(values["OTHER"], "value")

    def test_placeholder_api_key_is_not_accepted_as_configured(self):
        from scripts.deepseek_retrieval_agent import resolve_deepseek_api_key

        with self.assertRaisesRegex(RuntimeError, "fill in DEEPSEEK_API_KEY"):
            resolve_deepseek_api_key("your_deepseek_api_key_here")

    def test_configure_utf8_stdio_reconfigures_print_streams(self):
        from scripts.deepseek_retrieval_agent import configure_utf8_stdio

        class FakeStream:
            def __init__(self):
                self.calls = []

            def reconfigure(self, **kwargs):
                self.calls.append(kwargs)

        stdout = FakeStream()
        stderr = FakeStream()

        configure_utf8_stdio(stdout=stdout, stderr=stderr)

        self.assertEqual(stdout.calls, [{"encoding": "utf-8"}])
        self.assertEqual(stderr.calls, [{"encoding": "utf-8"}])

    def test_clean_answer_text_removes_decorative_markdown_and_emoji(self):
        from scripts.deepseek_retrieval_agent import clean_answer_text

        raw = "## 🏫 学校定位\n\n---\n\n杭电**计算机**不错。\n"

        self.assertEqual(clean_answer_text(raw), "学校定位\n\n杭电计算机不错。")


if __name__ == "__main__":
    unittest.main()
