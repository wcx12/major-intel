import json
from pathlib import Path

from scripts.build_dialogue_eval_summary import build_dialogue_eval_summary


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_build_dialogue_eval_summary_writes_counts(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    write_jsonl(
        input_dir / "asr_question_candidates.jsonl",
        [{"id": "cand_1", "question_raw": "q", "source_repo": "repo"}],
    )
    write_jsonl(
        input_dir / "llm_cleaned_dialogues.jsonl",
        [
            {
                "candidate_id": "cand_1",
                "question_family": "major_profile",
                "question_raw": "q",
                "quality_label": "A",
                "quality_score": 0.9,
            }
        ],
    )
    question = {
        "id": "qb_1",
        "source_question_id": "cand_1",
        "question_family": "major_profile",
        "coverage_level": "covered_or_partial",
        "expected_tools": ["major_profile", "employment_summary"],
        "quality_label": "A",
        "quality_score": 0.9,
    }
    write_jsonl(input_dir / "question_bank.jsonl", [question])
    write_jsonl(input_dir / "usable_question_bank.jsonl", [question])
    eval_case = {
        "id": "eval_1",
        "source_question_id": "qb_1",
        "expected_tools": ["major_profile"],
        "should_clarify": False,
    }
    write_jsonl(input_dir / "function_call_eval_cases.jsonl", [eval_case])
    write_jsonl(input_dir / "usable_function_call_eval_cases.jsonl", [eval_case])
    write_jsonl(input_dir / "mentor_strategy_bank.jsonl", [{"id": "s1"}])
    write_jsonl(
        input_dir / "review_queue.jsonl",
        [{"id": "r1", "source_question_id": "qb_1", "reason": "check"}],
    )
    (input_dir / "source_inventory.json").write_text(
        json.dumps(
            [
                {
                    "source_name": "repo",
                    "source_type": "public_asr",
                    "source_url": "https://example.test/repo",
                    "license": "MIT",
                    "is_real_dialogue": False,
                    "usable_for": ["question_candidates"],
                    "risk_notes": ["review"],
                }
            ]
        ),
        encoding="utf-8",
    )
    for name in [
        "README.md",
        "SOURCES.md",
        "mentor_reply_strategies.md",
        "student_common_questions.md",
        "dialogue_quality_report.md",
    ]:
        (input_dir / name).write_text(name, encoding="utf-8")

    manifest = build_dialogue_eval_summary(
        input_dir=input_dir,
        output_dir=output_dir,
        generated_at="2026-06-14",
    )

    assert manifest["row_counts"]["question_bank"] == 1
    assert manifest["row_counts"]["function_call_eval_cases"] == 1
    assert manifest["distributions"]["question_family"] == {"major_profile": 1}
    assert (output_dir / "dialogue_question_family_summary_2026.csv").exists()
    assert (output_dir / "dialogue_eval_manifest_2026.json").exists()
