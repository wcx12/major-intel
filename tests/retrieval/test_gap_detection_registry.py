from scripts.retrieval_tools import (
    _core_field_empty,
    _detect_tool_result_gaps,
    _infer_available_fields,
)


def test_core_field_empty_detects_empty_core_lists():
    assert _core_field_empty({"data": {"schools": []}}, "data.schools")
    assert _core_field_empty({"data": {"majors": []}}, "data.majors")
    assert _core_field_empty({"data": {"records": []}}, "data.records")
    assert _core_field_empty({"data": {}}, "data.records")


def test_infer_available_fields_from_non_empty_core_result():
    result = {"data": {"schools": [{"name": "上海交通大学"}]}}

    assert _infer_available_fields("major_school_list", result) == ["major_school_relation"]


def test_detect_tool_result_gaps_from_not_found_major_school_list():
    result = {
        "tool_name": "major_school_list",
        "status": "not_found",
        "data": {"major": {"special_name": "人工智能", "code": "080717T"}, "schools": []},
        "normalized_slots": {
            "major_name": "人工智能",
            "major_code": "080717T",
            "province_filter": "上海",
            "school_level_filter": "本科",
        },
        "data_gaps": ["开设该专业的学校记录"],
        "needs_clarification": [],
    }

    gaps = _detect_tool_result_gaps("major_school_list", result)

    assert gaps
    assert gaps[0]["gap_key"] == "major_school_relation"
    assert gaps[0]["trigger"] in {"status_not_found", "core_result_empty"}
    assert gaps[0]["resolvable_by_web"] is True
    assert gaps[0]["normalized_slots"]["major_name"] == "人工智能"
    assert gaps[0]["normalized_slots"]["province_filter"] == "上海"


def test_detect_tool_result_gaps_skips_complete_major_school_list():
    result = {
        "tool_name": "major_school_list",
        "status": "ok",
        "data": {"schools": [{"name": "上海交通大学"}]},
        "normalized_slots": {"major_name": "人工智能"},
        "data_gaps": [],
        "needs_clarification": [],
    }

    assert _detect_tool_result_gaps("major_school_list", result) == []


def test_detect_tool_result_gaps_skips_tool_schema_errors():
    result = {
        "tool_name": "school_major_list",
        "status": "error",
        "input": {"arguments": {"school_text": "上海大学", "major_text": "人工智能"}},
        "data": {},
        "warnings": ["unexpected argument(s): major_text"],
        "needs_clarification": [],
    }

    assert _detect_tool_result_gaps("school_major_list", result) == []
