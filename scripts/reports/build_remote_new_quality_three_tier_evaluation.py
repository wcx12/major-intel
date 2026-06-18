"""Evaluate remote edu_major rows as new-quality-productivity majors by 3 school tiers."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
NQ_RULES_PATH = ROOT / "scripts/reports/build_new_quality_major_evaluation.py"
REMOTE_MAJOR_CSV = ROOT / "reports/remote_db_current_majors/remote_edu_major_majors_20260614.csv"
REMOTE_TIER_CSV = ROOT / "reports/remote_db_university_tiers/remote_edu_university_three_tiers_20260614.csv"
POLICY_MENTIONS_CSV = ROOT / "data/processed/policy_evidence/policy_mentions_policy_evidence_seed_20260612_v5.csv"
EMERGING_UNIQUE_CSV = ROOT / "data/processed/policy_documents/emerging_major_unique_majors_emerging_major_seed_20260612_v5.csv"
OFFICIAL_CATALOG_CSV = ROOT / "data/processed/official_major_catalog/official_major_catalog_records_official_major_catalog_20260612_v2.csv"

TIER_ORDER = ["1", "2", "3"]
TIER_NAMES = {
    "1": "头部/强研究型高校",
    "2": "区域重点/特色优势高校",
    "3": "普通应用/职业供给高校",
}

OUTPUT_FIELDS = [
    "major_special_id",
    "major_code",
    "major_name",
    "major_type",
    "major_level2",
    "major_level3",
    "evaluation_label",
    "is_new_quality_productivity_major",
    "directions",
    "confidence",
    "score",
    "rationale",
    "tier1_examples",
    "tier1_offer_count",
    "tier1_interpretation",
    "tier2_examples",
    "tier2_offer_count",
    "tier2_interpretation",
    "tier3_examples",
    "tier3_offer_count",
    "tier3_interpretation",
    "policy_source_ids",
    "policy_evidence_excerpt",
    "official_major_source",
    "sample_basis",
    "estimation_note",
    "needs_review",
]

DETAIL_FIELDS = [
    "major_special_id",
    "major_code",
    "major_name",
    "school_tier",
    "school_tier_name",
    "sample_school_id",
    "sample_school_name",
    "sample_school_rank",
    "sample_school_province",
    "offer_count_in_tier",
    "evaluation_label",
    "directions",
    "confidence",
    "tier_interpretation",
    "sample_basis",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build remote 3-tier new-quality major evaluation table.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/new_quality_major_three_tier_20260614")
    parser.add_argument("--examples-per-tier", type=int, default=5)
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rules = load_rules_module()
    load_env_file(ROOT / ".env")

    tier_by_school = load_tier_rows(REMOTE_TIER_CSV)
    remote_major_ids = load_remote_major_ids(REMOTE_MAJOR_CSV)
    majors = fetch_remote_edu_majors(remote_major_ids)
    offerings = fetch_remote_school_major_offerings()
    policies = rules.load_policy_evidence(POLICY_MENTIONS_CSV)
    emerging_index = rules.load_official_major_index(EMERGING_UNIQUE_CSV, key_fields=("major_code", "major_name"))
    catalog_index = rules.load_official_major_index(OFFICIAL_CATALOG_CSV, key_fields=("major_code", "major_name"))

    offerings_by_special_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    offerings_by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    offerings_by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in offerings:
        tier_row = tier_by_school.get(row.get("school_id", ""))
        if not tier_row:
            continue
        merged = {**row, **tier_row}
        if merged.get("special_id"):
            offerings_by_special_id[merged["special_id"]].append(merged)
        if merged.get("major_code"):
            offerings_by_code[rules.normalize_code(merged["major_code"])].append(merged)
        if merged.get("major_name"):
            offerings_by_name[rules.normalize_name(merged["major_name"])].append(merged)

    output_rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    for major in majors:
        major_offerings = rules.pick_major_offerings(major, offerings_by_special_id, offerings_by_code, offerings_by_name)
        tier_samples = {
            tier: pick_tier_examples(major_offerings, tier, args.examples_per_tier)
            for tier in TIER_ORDER
        }
        evaluation = rules.evaluate_major(major, policies, emerging_index, catalog_index)
        output_rows.append(build_output_row(major, evaluation, tier_samples))
        for tier in TIER_ORDER:
            detail_rows.extend(build_detail_rows(major, evaluation, tier, tier_samples[tier]))

    source_rows = rules.build_source_rows(policies)
    stats = build_stats(output_rows, detail_rows, tier_by_school)

    write_csv(args.output_dir / "remote_major_new_quality_three_tier_evaluation_20260614.csv", OUTPUT_FIELDS, output_rows)
    write_csv(args.output_dir / "remote_major_new_quality_three_tier_detail_20260614.csv", DETAIL_FIELDS, detail_rows)
    write_csv(args.output_dir / "remote_major_new_quality_policy_sources_20260614.csv", rules.SOURCE_FIELDS, source_rows)
    (args.output_dir / "remote_major_new_quality_three_tier_stats_20260614.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "remote_major_new_quality_three_tier_workbook_data_20260614.json").write_text(
        json.dumps(
            {
                "rows": output_rows,
                "details": detail_rows,
                "sources": source_rows,
                "stats": stats,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    write_markdown(args.output_dir / "remote_major_new_quality_three_tier_summary_20260614.md", output_rows, stats)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


def load_rules_module():
    spec = importlib.util.spec_from_file_location("nq_rules", NQ_RULES_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load rules module: {NQ_RULES_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key.startswith("GAOKAO_REMOTE_DB_"):
            os.environ.setdefault(key, value)


def load_tier_rows(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            school_id = str(row.get("school_id", "")).strip()
            if not school_id:
                continue
            rows[school_id] = {
                "school_id": school_id,
                "school_name": row.get("name", ""),
                "school_province": row.get("province_name", ""),
                "school_city": row.get("city_name", ""),
                "university_tier": row.get("university_tier", ""),
                "university_tier_name": row.get("university_tier_name", ""),
                "tier_reason": row.get("tier_reason", ""),
                "ranking": row.get("ranking", "") or row.get("ruanke_rank", "") or "999999",
            }
    return rows


def load_remote_major_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            special_id = str(row.get("special_id", "")).strip()
            if special_id:
                ids.add(special_id)
    return ids


def fetch_remote_edu_majors(remote_major_ids: set[str]) -> list[dict[str, str]]:
    clean = remote_clean_expr
    sql = f"""
SELECT
  CAST(id AS CHAR) AS id,
  CAST(special_id AS CHAR) AS special_id,
  {clean('code')},
  {clean('special_name')},
  {clean('special_type')},
  {clean('type_name')},
  {clean('level2_name')},
  {clean('level3_name')},
  {clean('degree')},
  {clean('content')},
  {clean('job')},
  {clean('is_what')},
  {clean('learn_what')},
  {clean('do_what')},
  {clean('direction')},
  {clean('course')},
  {clean('skill')},
  {clean('mostemploymentindustry')},
  {clean('mostemployedeposition')}
FROM edu_major
WHERE COALESCE(deleted + 0, 0) = 0
ORDER BY special_type, code, special_name, special_id;
"""
    rows = remote_mysql_query(sql)
    if not remote_major_ids:
        return rows
    filtered = [row for row in rows if row.get("special_id") in remote_major_ids]
    return filtered or rows


def remote_clean_expr(field: str) -> str:
    alias = field.split(".")[-1].replace("`", "")
    return (
        "REPLACE(REPLACE(REPLACE(REPLACE(COALESCE("
        + field
        + ", ''), CHAR(13), ' '), CHAR(10), ' '), CHAR(9), ' '), '  ', ' ') AS "
        + alias
    )


def fetch_remote_school_major_offerings() -> list[dict[str, str]]:
    sql = """
SELECT
  CAST(id AS CHAR) AS school_major_id,
  CAST(special_id AS CHAR) AS special_id,
  REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(major_code, ''), CHAR(13), ' '), CHAR(10), ' '), CHAR(9), ' '), '  ', ' ') AS major_code,
  REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(major_name, ''), CHAR(13), ' '), CHAR(10), ' '), CHAR(9), ' '), '  ', ' ') AS major_name,
  CAST(school_id AS CHAR) AS school_id,
  REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(school_name, ''), CHAR(13), ' '), CHAR(10), ' '), CHAR(9), ' '), '  ', ' ') AS school_name
FROM edu_school_major
WHERE COALESCE(deleted, 0) = 0;
"""
    return remote_mysql_query(sql)


def remote_mysql_query(sql: str) -> list[dict[str, str]]:
    host = os.environ.get("GAOKAO_REMOTE_DB_HOST")
    port = os.environ.get("GAOKAO_REMOTE_DB_PORT", "3306")
    user = os.environ.get("GAOKAO_REMOTE_DB_USER")
    database = os.environ.get("GAOKAO_REMOTE_DB_NAME")
    password = os.environ.get("GAOKAO_REMOTE_DB_PASSWORD")
    if not host or not user or not database:
        raise RuntimeError("Missing GAOKAO_REMOTE_DB_* environment variables")
    env = os.environ.copy()
    if password:
        env["MYSQL_PWD"] = password
    command = [
        "mysql",
        "--batch",
        "--raw",
        "--default-character-set=utf8mb4",
        "-h",
        host,
        "-P",
        port,
        "-u",
        user,
        database,
        "-e",
        sql,
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "remote mysql query failed")
    return parse_tsv(result.stdout)


def parse_tsv(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = lines[0].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        values = line.split("\t")
        if len(values) < len(header):
            values += [""] * (len(header) - len(values))
        rows.append({key: decode_mysql_cell(value) for key, value in zip(header, values)})
    return rows


def decode_mysql_cell(value: str) -> str:
    return "" if value == "NULL" else value.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").strip()


def pick_tier_examples(offerings: list[dict[str, str]], tier: str, max_examples: int) -> dict[str, Any]:
    rows = [row for row in offerings if row.get("university_tier") == tier]
    rows.sort(key=lambda row: (to_int(row.get("ranking"), 999999), row.get("school_name", "")))
    return {
        "count": len(rows),
        "examples": rows[:max_examples],
    }


def build_output_row(
    major: dict[str, str],
    evaluation: dict[str, Any],
    tier_samples: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    row = {
        "major_special_id": major.get("special_id", ""),
        "major_code": major.get("code", ""),
        "major_name": major.get("special_name", ""),
        "major_type": major.get("special_type", ""),
        "major_level2": major.get("level2_name", ""),
        "major_level3": major.get("level3_name", ""),
        "evaluation_label": evaluation["label"],
        "is_new_quality_productivity_major": evaluation["is_new_quality"],
        "directions": evaluation["directions"],
        "confidence": evaluation["confidence"],
        "score": evaluation["score"],
        "rationale": evaluation["rationale"],
        "policy_source_ids": evaluation["policy_source_ids"],
        "policy_evidence_excerpt": evaluation["policy_evidence_excerpt"],
        "official_major_source": evaluation["official_major_source"],
        "sample_basis": "远程 edu_school_major 开设关系 + remote_edu_university_three_tiers_20260614.csv 三层院校分类；政策证据来自 policy_evidence_seed_20260612_v5。",
        "estimation_note": estimation_note(tier_samples),
        "needs_review": evaluation["needs_review"],
    }
    for tier in TIER_ORDER:
        row[f"tier{tier}_examples"] = format_examples(tier_samples[tier]["examples"])
        row[f"tier{tier}_offer_count"] = tier_samples[tier]["count"]
        row[f"tier{tier}_interpretation"] = tier_interpretation(tier, evaluation, tier_samples[tier]["count"])
    return row


def build_detail_rows(
    major: dict[str, str],
    evaluation: dict[str, Any],
    tier: str,
    sample: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    examples = sample["examples"] or [{}]
    for item in examples:
        rows.append(
            {
                "major_special_id": major.get("special_id", ""),
                "major_code": major.get("code", ""),
                "major_name": major.get("special_name", ""),
                "school_tier": tier,
                "school_tier_name": TIER_NAMES[tier],
                "sample_school_id": item.get("school_id", ""),
                "sample_school_name": item.get("school_name", ""),
                "sample_school_rank": "" if item.get("ranking") == "999999" else item.get("ranking", ""),
                "sample_school_province": item.get("school_province", ""),
                "offer_count_in_tier": sample["count"],
                "evaluation_label": evaluation["label"],
                "directions": evaluation["directions"],
                "confidence": evaluation["confidence"],
                "tier_interpretation": tier_interpretation(tier, evaluation, sample["count"]),
                "sample_basis": "远程 edu_school_major + 三层院校表" if item else "该层级未找到开设样本，按专业属性估算",
            }
        )
    return rows


def format_examples(examples: list[dict[str, str]]) -> str:
    if not examples:
        return "未找到该层级开设样本"
    parts = []
    for item in examples:
        rank = item.get("ranking", "")
        rank_text = "" if not rank or rank == "999999" else f"/排名{rank}"
        province = item.get("school_province", "")
        province_text = f"/{province}" if province else ""
        parts.append(f"{item.get('school_name', '')}{province_text}{rank_text}")
    return "；".join(parts)


def estimation_note(tier_samples: dict[str, dict[str, Any]]) -> str:
    missing = [TIER_NAMES[tier] for tier, sample in tier_samples.items() if sample["count"] == 0]
    if not missing:
        return "三个层级均找到远程开设样本；样本用于解释层级差异，专业定性仍按专业属性和政策证据判断。"
    return "未找到开设样本的层级：" + "、".join(missing) + "；这些层级仅按专业属性和政策证据估算。"


def tier_interpretation(tier: str, evaluation: dict[str, Any], count: int) -> str:
    label = evaluation["label"]
    directions = evaluation.get("directions", "") or "未命中明确方向"
    sample_text = "有开设样本" if count else "未找到开设样本"
    if tier == "1":
        if label == "是":
            return f"头部/强研究型高校中{sample_text}；更偏前沿科研、交叉学科和原创技术供给，方向为{directions}。"
        if label in {"相关", "弱相关"}:
            return f"头部/强研究型高校中{sample_text}；可作为新质生产力基础学科或平台型支撑，方向为{directions}。"
        return f"头部/强研究型高校中{sample_text}；当前规则未把该专业作为新质生产力核心或直接支撑。"
    if tier == "2":
        if label == "是":
            return f"区域重点/特色优势高校中{sample_text}；更偏工程转化、区域产业链和特色学科建设，方向为{directions}。"
        if label in {"相关", "弱相关"}:
            return f"区域重点/特色优势高校中{sample_text}；适合解释为产业应用支撑或交叉赋能专业，方向为{directions}。"
        return f"区域重点/特色优势高校中{sample_text}；当前更像传统专业供给，需结合具体学校特色复核。"
    if label == "是":
        return f"普通应用/职业供给高校中{sample_text}；更偏岗位技能、应用场景落地和产业人才供给，方向为{directions}。"
    if label in {"相关", "弱相关"}:
        return f"普通应用/职业供给高校中{sample_text}；可作为新技术应用、设备运维或产业服务支撑，方向为{directions}。"
    return f"普通应用/职业供给高校中{sample_text}；当前不建议直接标为新质生产力专业。"


def build_stats(rows: list[dict[str, Any]], detail_rows: list[dict[str, Any]], tier_by_school: dict[str, dict[str, str]]) -> dict[str, Any]:
    label_counts = Counter(row["evaluation_label"] for row in rows)
    confidence_counts = Counter(row["confidence"] for row in rows)
    direction_counts: Counter[str] = Counter()
    for row in rows:
        for direction in str(row["directions"]).split(";"):
            if direction:
                direction_counts[direction] += 1
    tier_offer_counts = {
        tier: sum(1 for row in rows if int(row[f"tier{tier}_offer_count"]) > 0)
        for tier in TIER_ORDER
    }
    return {
        "major_count": len(rows),
        "detail_row_count": len(detail_rows),
        "tier_school_counts": dict(Counter(row["university_tier"] for row in tier_by_school.values())),
        "label_counts": dict(label_counts),
        "confidence_counts": dict(confidence_counts),
        "direction_counts": dict(direction_counts.most_common()),
        "major_with_tier_sample_counts": tier_offer_counts,
        "remote_major_csv": str(REMOTE_MAJOR_CSV.relative_to(ROOT)),
        "remote_tier_csv": str(REMOTE_TIER_CSV.relative_to(ROOT)),
        "policy_mentions_csv": str(POLICY_MENTIONS_CSV.relative_to(ROOT)),
    }


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_markdown(path: Path, rows: list[dict[str, Any]], stats: dict[str, Any]) -> None:
    tier_examples = {
        tier: [row for row in rows if row["evaluation_label"] == "是" and not row[f"tier{tier}_examples"].startswith("未找到")][:8]
        for tier in TIER_ORDER
    }
    top_yes = [row for row in rows if row["evaluation_label"] == "是"][:10]
    related = [row for row in rows if row["evaluation_label"] == "相关"][:8]
    lines = [
        "# 远程专业新质生产力三层院校口径评价",
        "",
        "日期：2026-06-14",
        "",
        "## 口径",
        "",
        "- 专业范围：远程 `edu_major` 当前专业清单。",
        "- 院校层级：`remote_edu_university_three_tiers_20260614.csv` 的三层分类。",
        "- 开设样本：远程 `edu_school_major` 只读查询后按三层院校表匹配。",
        "- 政策证据：`policy_evidence_seed_20260612_v5`，包含政府工作报告、未来产业、人工智能+、低空经济、数据要素、生物经济、民航 AI、人形机器人等政策。",
        "",
        "## 总体分布",
        "",
    ]
    for label, count in stats["label_counts"].items():
        lines.append(f"- `{label}`：{count}")
    lines.extend(["", "## 按三层院校口径的示例", ""])
    for tier in TIER_ORDER:
        lines.extend(["", f"### 第 {tier} 层：{TIER_NAMES[tier]}", ""])
        lines.append("| 专业 | 方向 | 该层级样例 | 层级解读 |")
        lines.append("|---|---|---|---|")
        for row in tier_examples[tier][:6]:
            lines.append(
                f"| {row['major_name']} | {row['directions']} | {row[f'tier{tier}_examples']} | {row[f'tier{tier}_interpretation']} |"
            )

    lines.extend(["", "## 明确新质生产力专业示例（跨层总览）", ""])
    lines.append("| 专业 | 方向 | 头部/强研究型样例 | 区域重点/特色优势样例 | 普通应用/职业供给样例 |")
    lines.append("|---|---|---|---|---|")
    for row in top_yes:
        lines.append(
            "| {major_name} | {directions} | {tier1_examples} | {tier2_examples} | {tier3_examples} |".format(**row)
        )
    lines.extend(["", "## 相关支撑专业示例", ""])
    lines.append("| 专业 | 方向 | 判断理由 |")
    lines.append("|---|---|---|")
    for row in related:
        lines.append(f"| {row['major_name']} | {row['directions']} | {row['rationale']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


if __name__ == "__main__":
    raise SystemExit(main())
