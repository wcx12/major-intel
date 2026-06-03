import json
import subprocess
from pathlib import Path

import pytest

from scripts.build_dialogue_assets import (
    build_claude_prompt,
    build_common_questions_markdown,
    build_eval_case,
    build_quality_report,
    build_mentor_strategy_markdown,
    build_question_bank,
    candidate_for_claude_prompt,
    build_source_inventory,
    build_strategy_records,
    classify_question,
    extract_question_candidates_from_segments,
    infer_mentor_strategy,
    load_asr_document,
    normalize_question_record,
    parse_claude_stdout,
    resolve_claude_command,
    summarize_subprocess_error,
    validate_llm_cleaned_record,
    write_jsonl,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_source_inventory_labels_known_repositories():
    inventory = build_source_inventory(PROJECT_ROOT)
    by_name = {item["source_name"]: item for item in inventory}

    assert by_name["Xue-Feng-Skill"]["source_type"] == "public_asr"
    assert by_name["zhangxuefeng-skillset"]["source_type"] == "methodology_md"
    assert by_name["gaokao-mentor-wisdom"]["source_type"] == "quote_paraphrase"
    assert by_name["zhangxuefeng-skill"]["source_type"] == "style_prompt"
    assert by_name["zhang-xuefeng-memorial"]["source_type"] == "methodology_md"
    assert by_name["Xue-Feng-Skill"]["source_url"] == "https://github.com/SPA3K/Xue-Feng-Skill"
    assert by_name["Xue-Feng-Skill"]["license"] == "MIT"
    assert by_name["Xue-Feng-Skill"]["attribution_note"]


def test_source_inventory_marks_synthetic_demo_as_not_real_dialogue():
    inventory = build_source_inventory(PROJECT_ROOT)
    demo = next(item for item in inventory if item["source_name"] == "zhangxuefeng-skill-demo")

    assert demo["source_type"] == "synthetic_demo"
    assert demo["is_real_dialogue"] is False
    assert demo["usable_for"] == ["strategy_reference", "style_reference"]


def test_load_asr_document_reads_segments(tmp_path):
    path = tmp_path / "sample.json"
    path.write_text(
        json.dumps(
            {
                "bvid": "BVtest",
                "text": "河北物理580能报什么学校",
                "segments": [
                    {"start": 0, "end": 3, "text": "河北物理580能报什么学校"},
                    {"start": 3, "end": 8, "text": "先看位次不要只看分数"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    doc = load_asr_document(path)

    assert doc["bvid"] == "BVtest"
    assert len(doc["segments"]) == 2


def test_extract_question_candidates_pairs_following_response_segments():
    segments = [
        {"start": 0, "end": 3, "text": "老师河北物理580分能报计算机吗"},
        {"start": 3, "end": 10, "text": "你先别看分数先看位次"},
        {"start": 10, "end": 18, "text": "再看这个专业近三年的最低位次"},
    ]

    candidates = extract_question_candidates_from_segments("BVtest", segments, "sample.json")

    assert len(candidates) == 1
    assert candidates[0]["question_raw"] == "老师河北物理580分能报计算机吗"
    assert candidates[0]["response_candidate_raw"].startswith("你先别看分数")
    assert candidates[0]["source_ref"] == "sample.json#segment=0"
    assert candidates[0]["response_candidate_ref"] == "sample.json#segments=1-2"


def test_classify_rank_to_major_match_question():
    result = classify_question("河北物理580分想学计算机能报什么学校")

    assert result["question_family"] == "rank_to_major_match"
    assert result["slots"]["province"] == "河北"
    assert result["slots"]["subject_type"] == "物理"
    assert result["slots"]["score"] == 580
    assert result["slots"]["major_preference"] == "计算机"
    assert result["expected_tools"] == [
        "score_to_rank",
        "rank_to_major_match",
        "admission_history",
        "data_gap_detection",
    ]


def test_classify_missing_slots_for_vague_score_question():
    result = classify_question("我这个分数怎么填志愿")

    assert result["question_family"] == "rank_to_school_match"
    assert result["missing_slots"] == ["province", "subject_type", "score_or_rank"]
    assert result["coverage_level"] == "partial"


def test_normalize_question_record_preserves_style_fields():
    raw = {
        "question_raw": "老师河北物理580分能报计算机吗",
        "response_candidate_raw": "你先别看分数先看位次",
        "source_type": "public_asr",
        "source_repo": "Xue-Feng-Skill",
        "source_ref": "x.json#segment=1",
        "response_candidate_ref": "x.json#segments=2-4",
    }

    record = normalize_question_record(raw, index=1)

    assert record["id"] == "qb_000001"
    assert record["question_raw"] == raw["question_raw"]
    assert record["question_colloquial_clean"].startswith("老师")
    assert record["question_formal_clean"]
    assert record["question_normalized"].endswith("？")
    assert record["response_candidate_raw"] == raw["response_candidate_raw"]
    assert record["source_candidate_id"] is None
    assert record["source_ref"] == "x.json#segment=1"


def test_infer_mentor_strategy_extracts_response_rules():
    strategies = infer_mentor_strategy("先看位次，再看近三年最低位次。色弱专业要避开。", "rank_to_major_match")

    assert any("位次" in item for item in strategies)
    assert any("体检受限" in item for item in strategies)


def test_validate_llm_cleaned_record_keeps_style_fields():
    record = {
        "question_raw": "老师我家孩子河北物理五百八想那个计算机能不能冲一下",
        "question_colloquial_clean": "老师，我家孩子河北物理580，想学计算机，能不能冲一下？",
        "question_formal_clean": "河北物理类考生约580分，意向报考计算机相关专业，希望评估可冲刺的院校或专业。",
        "question_normalized": "河北物理类580分，想学计算机，是否可以冲刺相关学校或专业？",
        "question_family": "rank_to_major_match",
        "slots": {"province": "河北", "subject_type": "物理", "score": 580, "major_preference": "计算机"},
        "missing_slots": [],
        "expected_tools": ["score_to_rank", "rank_to_major_match", "admission_history", "data_gap_detection"],
        "mentor_strategy": ["先转位次", "再看近三年最低位次", "不要承诺录取"],
        "style_features": ["口语化", "家长咨询", "冲刺语气"],
    }

    validated = validate_llm_cleaned_record(record)

    assert validated["question_colloquial_clean"].startswith("老师")
    assert validated["question_formal_clean"].startswith("河北")
    assert validated["question_normalized"].endswith("？")
    assert validated["expected_tools"] == record["expected_tools"]


def test_validate_llm_cleaned_record_normalizes_question_family_alias():
    record = {
        "question_raw": "想听您科普一下南京大学。",
        "question_colloquial_clean": "想听您科普一下南京大学。",
        "question_formal_clean": "请介绍一下南京大学的基本信息。",
        "question_normalized": "南京大学的基本信息是什么？",
        "question_family": "school_profile",
        "slots": {"school_name": "南京大学"},
        "missing_slots": ["score", "rank"],
        "expected_tools": ["school_profile"],
        "mentor_strategy": ["先判断是否只是学校科普，再提醒分数差距。"],
        "style_features": ["口语化"],
    }

    validated = validate_llm_cleaned_record(record)

    assert validated["question_family"] == "school_major_profile"


def test_validate_llm_cleaned_record_normalizes_tool_family_alias():
    record = {
        "question_raw": "专项计划是怎么报的？",
        "question_colloquial_clean": "专项计划是怎么报的？",
        "question_formal_clean": "请问专项计划应如何填报？",
        "question_normalized": "专项计划应如何填报？",
        "question_family": "specialty_group_lookup",
        "slots": {},
        "missing_slots": ["province", "score"],
        "expected_tools": ["specialty_group_lookup"],
        "mentor_strategy": ["先查专项计划规则，再看名额差异。"],
        "style_features": ["口语化"],
    }

    validated = validate_llm_cleaned_record(record)

    assert validated["question_family"] == "specialty_group_risk"


def test_validate_llm_cleaned_record_accepts_colloquial_field_typo():
    record = {
        "question_raw": "我这个分数如果不够公办法学怎么办？",
        "question_colformal_clean": "我这个分数如果不够公办法学，怎么办？",
        "question_formal_clean": "如果分数不够报考公办法学，应如何制定志愿策略？",
        "question_normalized": "分数不够公办法学时应如何制定志愿策略？",
        "question_family": "rank_to_major_match",
        "slots": {"major": "法学"},
        "missing_slots": ["province", "score"],
        "expected_tools": ["rank_to_major_match", "admission_history"],
        "mentor_strategy": ["先看位次，再安排备选专业或批次。"],
        "style_features": ["口语化"],
    }

    validated = validate_llm_cleaned_record(record)

    assert validated["question_colloquial_clean"].startswith("我这个分数")


def test_validate_llm_cleaned_record_requires_formal_clean_text():
    record = {
        "question_raw": "河北物理580分能报计算机吗？",
        "question_colloquial_clean": "河北物理580分，能报计算机吗？",
        "question_normalized": "河北物理580分，想报计算机，能匹配哪些学校或专业？",
        "question_family": "rank_to_major_match",
        "slots": {"province": "河北", "subject_type": "物理", "score": 580, "major_preference": "计算机"},
        "missing_slots": [],
        "expected_tools": ["score_to_rank", "rank_to_major_match", "admission_history", "data_gap_detection"],
        "mentor_strategy": ["先看位次"],
        "style_features": ["口语化"],
    }

    with pytest.raises(ValueError, match="question_formal_clean"):
        validate_llm_cleaned_record(record)


def test_validate_llm_cleaned_record_rejects_unknown_tool():
    record = {
        "question_raw": "我这个分数怎么报",
        "question_colloquial_clean": "我这个分数怎么报？",
        "question_formal_clean": "该分数应如何填报高考志愿？",
        "question_normalized": "这个分数如何填报志愿？",
        "question_family": "rank_to_school_match",
        "slots": {},
        "missing_slots": ["province", "subject_type", "score_or_rank"],
        "expected_tools": ["made_up_tool"],
        "mentor_strategy": [],
        "style_features": ["口语化"],
    }

    with pytest.raises(ValueError, match="unknown tool"):
        validate_llm_cleaned_record(record)


def test_resolve_claude_command_prefers_cmd_on_windows(monkeypatch):
    def fake_which(command):
        return {"claude.cmd": "C:/Program Files/nodejs/node_global/claude.cmd"}.get(command)

    monkeypatch.setattr("scripts.build_dialogue_assets.shutil.which", fake_which)
    monkeypatch.setattr("scripts.build_dialogue_assets.sys.platform", "win32")

    assert resolve_claude_command().endswith("claude.cmd")


def test_summarize_subprocess_error_omits_full_command():
    exc = subprocess.CalledProcessError(
        returncode=1,
        cmd=["claude", "--json-schema", "very-large-schema"],
        stderr="schema failed",
    )

    summary = summarize_subprocess_error(exc)

    assert "exit=1" in summary
    assert "schema failed" in summary
    assert "very-large-schema" not in summary


def test_parse_claude_stdout_extracts_json_from_result_text():
    stdout = json.dumps({"result": "```json\n{\"records\":[{\"question_raw\":\"q\"}]}\n```"})

    records = parse_claude_stdout(stdout)

    assert records == [{"question_raw": "q"}]


def test_parse_claude_stdout_extracts_json_from_event_stream():
    stdout = "\n".join(
        [
            json.dumps({"type": "system", "subtype": "init"}),
            json.dumps({"type": "result", "subtype": "success", "result": "{\"records\":[{\"question_raw\":\"q\"}]}"}),
        ]
    )

    records = parse_claude_stdout(stdout)

    assert records == [{"question_raw": "q"}]


def test_parse_claude_stdout_accepts_single_record_object():
    stdout = json.dumps({"result": "{\"candidate_id\":\"cand_1\",\"question_raw\":\"q\"}"})

    records = parse_claude_stdout(stdout)

    assert records == [{"candidate_id": "cand_1", "question_raw": "q"}]


def test_parse_claude_stdout_tolerates_hook_text_before_json():
    stdout = 'SessionEnd hook failed\n' + json.dumps({"result": "{\"records\":[{\"question_raw\":\"q\"}]}"})

    records = parse_claude_stdout(stdout)

    assert records == [{"question_raw": "q"}]


def test_build_claude_prompt_includes_output_path_and_full_source_text():
    long_response = "先看位次。" * 200
    payload = json.loads(
        build_claude_prompt(
            [
                {
                    "id": "cand_000001",
                    "bvid": "BVtest",
                    "segment_index": 1,
                    "question_raw": "河北物理580分能报计算机吗？",
                    "response_candidate_raw": long_response,
                    "source_ref": "x.json#segment=1",
                }
            ],
            output_path=Path("clean/dialogue_claude_full/_batch.json"),
        )
    )

    assert payload["output_file_path"].endswith("_batch.json")
    assert payload["candidates"][0]["response_candidate_raw"] == long_response


def test_candidate_for_claude_prompt_keeps_full_source_text():
    long_response = "先看位次。" * 200
    prompt_candidate = candidate_for_claude_prompt(
        {
            "id": "cand_000001",
            "bvid": "BVtest",
            "segment_index": 1,
            "question_raw": "河北物理580分能报计算机吗？",
            "response_candidate_raw": long_response,
            "source_ref": "x.json#segment=1",
        }
    )

    assert prompt_candidate["candidate_id"] == "cand_000001"
    assert prompt_candidate["response_candidate_raw"] == long_response
    assert "response_candidate_excerpt" not in prompt_candidate


def test_build_question_bank_keeps_rule_fallback_for_uncleaned_candidate():
    candidates = [
        {
            "id": "cand_000001",
            "question_raw": "河北物理580分能报计算机吗？",
            "response_candidate_raw": "先看位次。",
            "source_type": "public_asr",
            "source_repo": "Xue-Feng-Skill",
            "source_ref": "x.json#segment=1",
        },
        {
            "id": "cand_000002",
            "question_raw": "普通家庭报什么专业好？",
            "response_candidate_raw": "先看就业。",
            "source_type": "public_asr",
            "source_repo": "Xue-Feng-Skill",
            "source_ref": "x.json#segment=2",
        },
    ]
    llm_records = [
        {
            "source_candidate_id": "cand_000001",
            "question_raw": "河北物理580分能报计算机吗？",
            "question_colloquial_clean": "河北物理580分，能报计算机吗？",
            "question_formal_clean": "河北物理类考生580分，意向报考计算机相关专业，需评估可报院校和专业。",
            "question_normalized": "河北物理580分，想报计算机，能匹配哪些学校或专业？",
            "question_family": "rank_to_major_match",
            "slots": {"province": "河北", "subject_type": "物理", "score": 580, "major_preference": "计算机"},
            "missing_slots": [],
            "expected_tools": ["score_to_rank", "rank_to_major_match", "admission_history", "data_gap_detection"],
            "mentor_strategy": ["先看位次"],
            "style_features": ["口语化"],
            "quality_label": "A",
            "quality_score": 0.9,
        }
    ]

    questions = build_question_bank(candidates, llm_records)

    assert len(questions) == 2
    assert questions[0]["cleaner"]["method"] == "claude_code"
    assert questions[0]["question_formal_clean"].startswith("河北")
    assert questions[1]["cleaner"]["method"] == "rules"
    assert questions[1]["question_formal_clean"]


def test_build_eval_case_marks_clarification_needed():
    question = {
        "id": "qb_000001",
        "question_normalized": "我这个分数怎么填志愿？",
        "question_family": "rank_to_school_match",
        "expected_tools": ["score_to_rank", "rank_to_school_match", "data_gap_detection"],
        "slots": {
            "province": None,
            "subject_type": None,
            "score": None,
            "rank": None,
            "major_preference": None,
            "city_preference": None,
        },
        "missing_slots": ["province", "subject_type", "score_or_rank"],
    }

    case = build_eval_case(question, index=1)

    assert case["id"] == "eval_000001"
    assert case["should_clarify"] is True
    assert case["missing_slots"] == ["province", "subject_type", "score_or_rank"]
    assert "不能在缺少省份、科类、分数或位次时推荐学校" in case["must_not_do"]


def test_build_strategy_records_contains_core_strategies():
    records = build_strategy_records()
    by_family = {record["applies_to_question_family"]: record for record in records}

    major = by_family["major_profile"]
    rank = by_family["rank_to_major_match"]

    assert "就业面" in major["strategy_title"]
    assert "major_profile" in major["must_call_tools"]
    assert "把专业通用薪资说成某校某专业薪资" in major["avoid"]
    assert "位次" in rank["strategy_title"]
    assert rank["must_call_tools"] == [
        "score_to_rank",
        "rank_to_major_match",
        "admission_history",
        "data_gap_detection",
    ]


def test_write_jsonl_writes_one_json_object_per_line(tmp_path):
    path = tmp_path / "out.jsonl"
    write_jsonl(path, [{"id": "a", "text": "甲"}, {"id": "b", "text": "乙"}])

    lines = path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2
    assert json.loads(lines[0])["text"] == "甲"


def test_build_quality_report_includes_counts():
    questions = [
        {"question_family": "rank_to_major_match", "quality_label": "A", "source_type": "public_asr"},
        {"question_family": "major_profile", "quality_label": "B", "source_type": "public_asr"},
    ]
    eval_cases = [{"id": "eval_000001"}, {"id": "eval_000002"}]
    strategies = [{"id": "ms_000001"}]

    report = build_quality_report(questions, eval_cases, strategies, asr_candidates_count=3, llm_cleaned_count=0)

    assert "# 对话数据质量报告" in report
    assert "ASR 问题候选数：3" in report
    assert "问题记录数：2" in report
    assert "rank_to_major_match: 1" in report
    assert "Function-call 评测用例数：2" in report


def test_markdown_summaries_include_questions_and_strategies():
    questions = [
        {
            "question_family": "rank_to_school_match",
            "question_colloquial_clean": "普通家庭报什么专业好？",
            "question_normalized": "普通家庭如何选择专业？",
            "expected_tools": ["score_to_rank", "rank_to_school_match"],
            "missing_slots": ["province"],
            "mentor_strategy": ["先追问关键信息"],
            "quality_label": "B",
        }
    ]
    strategies = [
        {
            "strategy_title": "位次优先",
            "applies_to_question_family": "rank_to_school_match",
            "must_call_tools": ["score_to_rank"],
            "must_clarify": ["province"],
            "avoid": ["承诺录取"],
        }
    ]

    question_summary = build_common_questions_markdown(questions)
    strategy_summary = build_mentor_strategy_markdown(questions, strategies)

    assert "普通家庭" in question_summary
    assert "先追问关键信息" in strategy_summary
