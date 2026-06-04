from pathlib import Path

from scripts.retrieval_function_registry import get_function_schemas


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FUNCTION_CALL_ROOT = PROJECT_ROOT / "tests" / "function_calls"
README_TEMPLATE = FUNCTION_CALL_ROOT / "README_TEMPLATE.md"

REQUIRED_SECTIONS = [
    "## 1. 工具原理",
    "## 2. 输入与输出",
    "## 3. 状态语义",
    "## 4. 测试范围",
    "## 5. 测试结果",
    "## 6. 已知风险与待改善",
    "## 7. 关联文件",
]


def _registered_tool_names() -> list[str]:
    return [schema["function"]["name"] for schema in get_function_schemas()]


def test_function_call_test_directories_match_registered_tools():
    expected = set(_registered_tool_names())
    actual = {path.name for path in FUNCTION_CALL_ROOT.iterdir() if path.is_dir() and not path.name.startswith("__")}

    assert actual == expected


def test_each_function_call_readme_uses_required_structure():
    for tool_name in _registered_tool_names():
        readme_path = FUNCTION_CALL_ROOT / tool_name / "README.md"

        assert readme_path.exists(), f"{tool_name} is missing README.md"
        readme_text = readme_path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            assert section in readme_text, f"{tool_name} README is missing section: {section}"


def test_function_call_readme_template_documents_required_structure():
    assert README_TEMPLATE.exists()
    template_text = README_TEMPLATE.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in template_text
