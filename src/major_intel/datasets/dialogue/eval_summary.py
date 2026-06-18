from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_INPUT_DIR = ROOT / "datasets/dialogue/claude_full"
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/dialogue_function_call_eval"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def manifest_path_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def _list_values(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


def build_dialogue_eval_summary(
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    asr_candidates = read_jsonl(input_dir / "asr_question_candidates.jsonl")
    cleaned = read_jsonl(input_dir / "llm_cleaned_dialogues.jsonl")
    questions = read_jsonl(input_dir / "question_bank.jsonl")
    usable_questions = read_jsonl(input_dir / "usable_question_bank.jsonl")
    eval_cases = read_jsonl(input_dir / "function_call_eval_cases.jsonl")
    usable_eval_cases = read_jsonl(input_dir / "usable_function_call_eval_cases.jsonl")
    strategy_rows = read_jsonl(input_dir / "mentor_strategy_bank.jsonl")
    review_rows = read_jsonl(input_dir / "review_queue.jsonl")
    source_inventory = json.loads((input_dir / "source_inventory.json").read_text(encoding="utf-8"))

    usable_question_ids = {row["id"] for row in usable_questions}
    question_by_id = {row["id"]: row for row in questions}
    family_scores: dict[str, list[float]] = defaultdict(list)
    family_counts: Counter[str] = Counter()
    family_usable_counts: Counter[str] = Counter()
    for row in questions:
        family = str(row.get("question_family") or "unknown")
        family_counts[family] += 1
        if row.get("id") in usable_question_ids:
            family_usable_counts[family] += 1
        try:
            family_scores[family].append(float(row.get("quality_score", 0) or 0))
        except (TypeError, ValueError):
            family_scores[family].append(0.0)

    family_eval_counts: Counter[str] = Counter()
    family_clarify_counts: Counter[str] = Counter()
    family_no_clarify_counts: Counter[str] = Counter()
    for row in eval_cases:
        question = question_by_id.get(str(row.get("source_question_id")))
        family = str((question or {}).get("question_family") or row.get("expected_intent") or "unknown")
        family_eval_counts[family] += 1
        if bool(row.get("should_clarify")):
            family_clarify_counts[family] += 1
        else:
            family_no_clarify_counts[family] += 1

    family_summary_rows = [
        {
            "question_family": family,
            "question_count": family_counts[family],
            "usable_question_count": family_usable_counts[family],
            "eval_case_count": family_eval_counts[family],
            "should_clarify_count": family_clarify_counts[family],
            "no_clarify_count": family_no_clarify_counts[family],
            "avg_quality_score": _average(family_scores[family]),
        }
        for family in sorted(family_counts)
    ]

    quality_counts: Counter[str] = Counter(str(row.get("quality_label") or "unknown") for row in questions)
    quality_usable_counts: Counter[str] = Counter(
        str(row.get("quality_label") or "unknown") for row in questions if row.get("id") in usable_question_ids
    )
    quality_scores: dict[str, list[float]] = defaultdict(list)
    for row in questions:
        quality = str(row.get("quality_label") or "unknown")
        try:
            quality_scores[quality].append(float(row.get("quality_score", 0) or 0))
        except (TypeError, ValueError):
            quality_scores[quality].append(0.0)
    quality_summary_rows = [
        {
            "quality_label": quality,
            "question_count": quality_counts[quality],
            "usable_question_count": quality_usable_counts[quality],
            "avg_quality_score": _average(quality_scores[quality]),
        }
        for quality in sorted(quality_counts)
    ]

    question_tool_counts: Counter[str] = Counter()
    usable_tool_counts: Counter[str] = Counter()
    eval_tool_counts: Counter[str] = Counter()
    for row in questions:
        for tool in _list_values(row.get("expected_tools")):
            question_tool_counts[tool] += 1
            if row.get("id") in usable_question_ids:
                usable_tool_counts[tool] += 1
    for row in eval_cases:
        for tool in _list_values(row.get("expected_tools")):
            eval_tool_counts[tool] += 1
    tool_summary_rows = [
        {
            "expected_tool": tool,
            "question_count": question_tool_counts[tool],
            "usable_question_count": usable_tool_counts[tool],
            "eval_case_count": eval_tool_counts[tool],
        }
        for tool in sorted(set(question_tool_counts) | set(eval_tool_counts))
    ]

    source_summary_rows = [
        {
            "source_name": str(row.get("source_name", "")),
            "source_type": str(row.get("source_type", "")),
            "source_url": str(row.get("source_url", "")),
            "license": str(row.get("license", "")),
            "is_real_dialogue": str(bool(row.get("is_real_dialogue"))).lower(),
            "usable_for": ";".join(_list_values(row.get("usable_for"))),
            "risk_notes": ";".join(_list_values(row.get("risk_notes"))),
        }
        for row in source_inventory
    ]

    outputs = {
        "dialogue_question_family_summary_2026.csv": family_summary_rows,
        "dialogue_quality_summary_2026.csv": quality_summary_rows,
        "dialogue_expected_tool_summary_2026.csv": tool_summary_rows,
        "dialogue_source_inventory_summary_2026.csv": source_summary_rows,
    }
    write_csv(
        output_dir / "dialogue_question_family_summary_2026.csv",
        family_summary_rows,
        [
            "question_family",
            "question_count",
            "usable_question_count",
            "eval_case_count",
            "should_clarify_count",
            "no_clarify_count",
            "avg_quality_score",
        ],
    )
    write_csv(
        output_dir / "dialogue_quality_summary_2026.csv",
        quality_summary_rows,
        ["quality_label", "question_count", "usable_question_count", "avg_quality_score"],
    )
    write_csv(
        output_dir / "dialogue_expected_tool_summary_2026.csv",
        tool_summary_rows,
        ["expected_tool", "question_count", "usable_question_count", "eval_case_count"],
    )
    write_csv(
        output_dir / "dialogue_source_inventory_summary_2026.csv",
        source_summary_rows,
        ["source_name", "source_type", "source_url", "license", "is_real_dialogue", "usable_for", "risk_notes"],
    )

    source_files = [
        "README.md",
        "SOURCES.md",
        "asr_question_candidates.jsonl",
        "llm_cleaned_dialogues.jsonl",
        "question_bank.jsonl",
        "usable_question_bank.jsonl",
        "function_call_eval_cases.jsonl",
        "usable_function_call_eval_cases.jsonl",
        "mentor_strategy_bank.jsonl",
        "mentor_reply_strategies.md",
        "student_common_questions.md",
        "source_inventory.json",
        "dialogue_quality_report.md",
        "review_queue.jsonl",
    ]
    manifest = {
        "generated_at": generated_at,
        "dataset": "dialogue_function_call_eval",
        "source_snapshot": input_dir.as_posix(),
        "status": "public_asr_derived_support_dataset",
        "row_counts": {
            "asr_question_candidates": len(asr_candidates),
            "llm_cleaned_dialogues": len(cleaned),
            "question_bank": len(questions),
            "usable_question_bank": len(usable_questions),
            "function_call_eval_cases": len(eval_cases),
            "usable_function_call_eval_cases": len(usable_eval_cases),
            "mentor_strategy_bank": len(strategy_rows),
            "review_queue": len(review_rows),
            "source_inventory": len(source_inventory),
            "question_family_summary": len(family_summary_rows),
            "quality_summary": len(quality_summary_rows),
            "expected_tool_summary": len(tool_summary_rows),
            "source_inventory_summary": len(source_summary_rows),
        },
        "distributions": {
            "question_family": dict(sorted(family_counts.items())),
            "quality_label": dict(sorted(quality_counts.items())),
            "coverage_level": dict(sorted(Counter(str(row.get("coverage_level") or "unknown") for row in questions).items())),
            "should_clarify": dict(sorted(Counter(str(bool(row.get("should_clarify"))).lower() for row in eval_cases).items())),
        },
        "usage_limits": [
            "Public ASR-derived support data; do not treat as official admission, employment, or major-risk facts.",
            "Use official evidence tables in this project for factual claims about schools, majors, scores, employment, and policies.",
            "Review raw ASR-derived text before product-facing display.",
        ],
        "checksums": {
            **{f"datasets/dialogue/claude_full/{name}": file_info(input_dir / name) for name in source_files},
            **{f"data/processed/dialogue_function_call_eval/{name}": file_info(output_dir / name) for name in outputs},
        },
    }
    manifest_path = output_dir / "dialogue_eval_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][manifest_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build dialogue function-call eval summary tables.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_dialogue_eval_summary(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        generated_at=args.generated_at,
    )
    print(
        json.dumps(
            {
                "dataset": manifest["dataset"],
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
