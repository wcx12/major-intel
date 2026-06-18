"""Build new-quality-productivity major evaluation tables.

The output is intentionally rule-based and auditable.  It does not mutate the
local database; it reads ``edu_major``, ``edu_school_major`` and
``edu_university`` through the local mysql CLI, then joins the result with the
official policy-evidence crawl outputs produced in this repository.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TIER_ORDER = ["清北", "985", "211", "双非"]
QINGBEI_SCHOOL_IDS = {"10001", "10003"}

POLICY_MENTIONS_CSV = Path("data/processed/policy_evidence/policy_mentions_policy_evidence_seed_20260612_v5.csv")
EMERGING_UNIQUE_CSV = Path(
    "data/processed/policy_documents/emerging_major_unique_majors_emerging_major_seed_20260612_v5.csv"
)
OFFICIAL_CATALOG_CSV = Path(
    "data/processed/official_major_catalog/official_major_catalog_records_official_major_catalog_20260612_v2.csv"
)

DETAIL_FIELDS = [
    "major_special_id",
    "major_code",
    "major_name",
    "major_type",
    "major_level2",
    "major_level3",
    "school_tier",
    "sample_school_id",
    "sample_school_name",
    "sample_school_rank",
    "sample_school_found",
    "tier_offer_count",
    "evaluation_label",
    "is_new_quality_productivity_major",
    "directions",
    "confidence",
    "score",
    "rationale",
    "policy_source_ids",
    "policy_evidence_excerpt",
    "official_major_source",
    "school_sample_source",
    "estimation_method",
    "needs_review",
]

SUMMARY_FIELDS = [
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
    "policy_source_ids",
    "policy_evidence_excerpt",
    "official_major_source",
    "qingbei_sample",
    "tier_985_sample",
    "tier_211_sample",
    "shuangfei_sample",
    "sample_coverage",
    "needs_review",
]

SOURCE_FIELDS = [
    "direction",
    "source_id",
    "source_title",
    "source_url",
    "source_year",
    "issuing_org",
    "keyword",
    "evidence_excerpt",
]


DIRECT_DIRECTION_PATTERNS: dict[str, list[str]] = {
    "future_industries": [
        "未来产业",
        "未来技术",
        "智能交互",
        "前沿技术",
    ],
    "artificial_intelligence": [
        "人工智能",
        "智能科学",
        "智能感知",
        "智能工程",
        "智能无人",
        "智能装备",
        "智能建造",
        "智能控制",
        "大数据",
        "数据科学",
        "数据计算",
        "机器人工程",
        "智能机器人",
        "虚拟现实",
        "增强现实",
        "脑机接口",
        "密码科学",
        "网络空间安全",
        "信息安全",
        "区块链",
    ],
    "low_altitude_economy": [
        "低空",
        "无人机",
        "通用航空",
        "飞行器",
        "航空服务",
        "航空运营",
        "航空维修",
        "航空发动机",
    ],
    "commercial_space": [
        "航空航天",
        "航天",
        "空间信息",
        "空天",
        "卫星",
        "遥感",
        "导航工程",
        "探测制导",
        "深空",
    ],
    "bio_manufacturing": [
        "生物制造",
        "合成生物",
        "生物工程",
        "生物技术",
        "生物信息",
        "生物医学工程",
        "生物制药",
        "生物医药",
        "生物育种",
        "智慧农业",
        "种子科学",
    ],
    "quantum_technology": [
        "量子",
    ],
    "integrated_circuit": [
        "集成电路",
        "微电子",
        "芯片",
        "半导体",
        "电子封装",
    ],
    "advanced_manufacturing": [
        "智能制造",
        "工业互联网",
        "机器人工程",
        "过程装备",
        "智能车辆",
        "新能源汽车",
        "智能网联汽车",
        "增材制造",
        "人形机器人",
        "智能装备",
    ],
    "green_low_carbon": [
        "新能源",
        "储能",
        "氢能",
        "碳中和",
        "碳汇",
        "绿色低碳",
        "资源循环",
        "节能",
        "可持续能源",
        "智慧能源",
    ],
    "digital_economy": [
        "数字经济",
        "数据科学",
        "大数据",
        "数据要素",
        "数据管理",
        "电子商务",
        "软件工程",
        "网络工程",
        "物联网",
        "云计算",
        "通信工程",
        "数字媒体",
        "元宇宙",
        "数字孪生",
        "现代物流",
    ],
    "new_materials": [
        "新材料",
        "功能材料",
        "纳米材料",
        "复合材料",
        "高分子材料",
        "新能源材料",
        "先进材料",
        "智能材料",
    ],
}

RELATED_CLASS_PATTERNS: dict[str, list[str]] = {
    "artificial_intelligence": ["计算机类", "电子信息类", "自动化类"],
    "low_altitude_economy": ["航空运输类", "航空航天类"],
    "commercial_space": ["航空航天类", "测绘类", "兵器类"],
    "bio_manufacturing": ["生物科学类", "生物工程类", "食品科学与工程类", "药学类", "农业工程类"],
    "quantum_technology": ["物理学类"],
    "integrated_circuit": ["电子信息类"],
    "advanced_manufacturing": ["机械类", "自动化类", "仪器类", "交通运输类", "装备制造大类"],
    "green_low_carbon": ["能源动力类", "电气类", "环境科学与工程类", "新能源发电工程类"],
    "digital_economy": ["计算机类", "电子商务类", "物流类", "管理科学与工程类"],
    "new_materials": ["材料类", "非金属材料类"],
}

NEGATIVE_LEVEL2 = {
    "哲学",
    "文学",
    "历史学",
    "艺术学",
    "法学",
    "教育学",
}


@dataclass(frozen=True)
class PolicyEvidence:
    source_id: str
    source_title: str
    source_url: str
    source_year: str
    issuing_org: str
    keyword: str
    evidence_text: str


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build new-quality-productivity major evaluation tables.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/new_quality_major_eval_20260613"))
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    load_env_file(Path(".env"))

    majors = fetch_edu_majors()
    offerings = fetch_school_major_offerings()
    policies = load_policy_evidence(POLICY_MENTIONS_CSV)
    emerging_index = load_official_major_index(EMERGING_UNIQUE_CSV, key_fields=("major_code", "major_name"))
    catalog_index = load_official_major_index(OFFICIAL_CATALOG_CSV, key_fields=("major_code", "major_name"))

    offerings_by_special_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    offerings_by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    offerings_by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in offerings:
        if row.get("special_id"):
            offerings_by_special_id[row["special_id"]].append(row)
        if row.get("major_code"):
            offerings_by_code[normalize_code(row["major_code"])].append(row)
        if row.get("major_name"):
            offerings_by_name[normalize_name(row["major_name"])].append(row)

    detail_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for major in majors:
        major_offerings = pick_major_offerings(major, offerings_by_special_id, offerings_by_code, offerings_by_name)
        tier_samples = {tier: pick_tier_sample(major_offerings, tier) for tier in TIER_ORDER}
        evaluation = evaluate_major(major, policies, emerging_index, catalog_index)

        summary_rows.append(build_summary_row(major, evaluation, tier_samples))
        for tier in TIER_ORDER:
            detail_rows.append(build_detail_row(major, evaluation, tier, tier_samples[tier]))

    source_rows = build_source_rows(policies)
    stats = build_stats(majors, detail_rows, summary_rows)

    write_csv(args.output_dir / "new_quality_major_evaluation_detail.csv", DETAIL_FIELDS, detail_rows)
    write_csv(args.output_dir / "new_quality_major_evaluation_summary.csv", SUMMARY_FIELDS, summary_rows)
    write_csv(args.output_dir / "new_quality_policy_sources.csv", SOURCE_FIELDS, source_rows)
    (args.output_dir / "new_quality_major_evaluation_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "new_quality_major_evaluation_workbook_data.json").write_text(
        json.dumps(
            {
                "summary": summary_rows,
                "detail": detail_rows,
                "sources": source_rows,
                "stats": stats,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


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
        if key.startswith("GAOKAO_DB_") or key == "MYSQL_PWD":
            os.environ.setdefault(key, value)


def fetch_edu_majors() -> list[dict[str, str]]:
    clean = sql_clean_expr
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
    return mysql_query(sql)


def fetch_school_major_offerings() -> list[dict[str, str]]:
    clean = sql_clean_expr
    sql = f"""
SELECT
  CAST(sm.id AS CHAR) AS school_major_id,
  CAST(sm.special_id AS CHAR) AS special_id,
  {clean('sm.major_code')},
  {clean('sm.major_name')},
  CAST(sm.school_id AS CHAR) AS school_id,
  {clean('COALESCE(u.name, sm.school_name)')},
  CAST(COALESCE(u.is985, 0) AS CHAR) AS is985,
  CAST(COALESCE(u.is211, 0) AS CHAR) AS is211,
  CAST(COALESCE(u.is_dual_class, 0) AS CHAR) AS is_dual_class,
  CAST(COALESCE(u.ranking, 999999) AS CHAR) AS ranking,
  {clean('u.level_name')},
  {clean('u.province_name')}
FROM edu_school_major sm
LEFT JOIN edu_university u ON CAST(sm.school_id AS CHAR) = CAST(u.school_id AS CHAR)
WHERE COALESCE(sm.deleted, 0) = 0;
"""
    return mysql_query(sql)


def sql_clean_expr(field: str) -> str:
    return (
        "REPLACE(REPLACE(REPLACE(REPLACE(COALESCE("
        + field
        + ", ''), CHAR(13), ' '), CHAR(10), ' '), CHAR(9), ' '), '  ', ' ') AS "
        + alias_from_expr(field)
    )


def alias_from_expr(field: str) -> str:
    field = field.strip()
    if field.startswith("COALESCE("):
        return "school_name"
    return field.split(".")[-1].replace("`", "")


def mysql_query(sql: str) -> list[dict[str, str]]:
    host = os.environ.get("GAOKAO_DB_HOST", "127.0.0.1")
    port = os.environ.get("GAOKAO_DB_PORT", "3306")
    user = os.environ.get("GAOKAO_DB_USER", "root")
    database = os.environ.get("GAOKAO_DB_NAME", "gaokao_test_local")
    password = os.environ.get("GAOKAO_DB_PASSWORD") or os.environ.get("MYSQL_PWD")
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
        raise RuntimeError(result.stderr.strip() or "mysql query failed")
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
    if value == "NULL":
        return ""
    return value.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").strip()


def load_policy_evidence(path: Path) -> dict[str, list[PolicyEvidence]]:
    by_direction: dict[str, list[PolicyEvidence]] = defaultdict(list)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            evidence = PolicyEvidence(
                source_id=row.get("source_id", ""),
                source_title=row.get("source_title", ""),
                source_url=row.get("source_url", ""),
                source_year=row.get("source_year", ""),
                issuing_org=row.get("issuing_org", ""),
                keyword=row.get("keyword", ""),
                evidence_text=compact_text(row.get("evidence_text", ""), 220),
            )
            by_direction[row.get("direction", "")].append(evidence)
    for rows in by_direction.values():
        rows.sort(key=lambda item: (item.source_year, item.source_id), reverse=True)
    return by_direction


def load_official_major_index(path: Path, *, key_fields: tuple[str, str]) -> dict[str, list[dict[str, str]]]:
    code_field, name_field = key_fields
    index: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            code = normalize_code(row.get(code_field, ""))
            name = normalize_name(row.get(name_field, ""))
            if is_noise_major_name(name):
                continue
            if code:
                index[f"code:{code}"].append(row)
            if name:
                index[f"name:{name}"].append(row)
    return index


def pick_major_offerings(
    major: dict[str, str],
    by_special_id: dict[str, list[dict[str, str]]],
    by_code: dict[str, list[dict[str, str]]],
    by_name: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    special_id = major.get("special_id", "")
    code = normalize_code(major.get("code", ""))
    name = normalize_name(major.get("special_name", ""))
    candidates: list[dict[str, str]] = []
    match_type = ""
    if special_id and by_special_id.get(special_id):
        candidates = by_special_id[special_id]
        match_type = "special_id"
    elif code and by_code.get(code):
        candidates = by_code[code]
        match_type = "major_code"
    elif name and by_name.get(name):
        candidates = by_name[name]
        match_type = "major_name"
    deduped: dict[tuple[str, str], dict[str, str]] = {}
    for row in candidates:
        enriched = dict(row)
        enriched["offering_match_type"] = match_type
        deduped[(row.get("school_id", ""), row.get("major_name", ""))] = enriched
    return list(deduped.values())


def pick_tier_sample(offerings: list[dict[str, str]], tier: str) -> dict[str, Any]:
    tier_rows = [row for row in offerings if school_tier(row) == tier]
    tier_rows.sort(key=lambda row: (to_int(row.get("ranking"), 999999), row.get("school_name", "")))
    if not tier_rows:
        return {
            "found": False,
            "count": 0,
            "school_id": "",
            "school_name": "",
            "ranking": "",
            "source": "本地 edu_school_major 未找到该层次开设样本；本行按专业属性和政策证据估算。",
        }
    sample = tier_rows[0]
    return {
        "found": True,
        "count": len(tier_rows),
        "school_id": sample.get("school_id", ""),
        "school_name": sample.get("school_name", ""),
        "ranking": "" if sample.get("ranking") == "999999" else sample.get("ranking", ""),
        "source": f"本地 edu_school_major + edu_university；匹配方式={sample.get('offering_match_type', '')}。",
    }


def school_tier(row: dict[str, str]) -> str:
    school_id = row.get("school_id", "")
    school_name = row.get("school_name", "")
    if school_id in QINGBEI_SCHOOL_IDS or "清华" in school_name or "北京大学" in school_name:
        return "清北"
    if row.get("is985") == "1":
        return "985"
    if row.get("is211") == "1":
        return "211"
    return "双非"


def evaluate_major(
    major: dict[str, str],
    policies: dict[str, list[PolicyEvidence]],
    emerging_index: dict[str, list[dict[str, str]]],
    catalog_index: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    name = major.get("special_name", "")
    code = normalize_code(major.get("code", ""))
    level2 = major.get("level2_name", "")
    level3 = major.get("level3_name", "")
    text = " ".join(
        [
            name,
            code,
            level2,
            level3,
            major.get("content", ""),
            major.get("job", ""),
            major.get("is_what", ""),
            major.get("learn_what", ""),
            major.get("do_what", ""),
            major.get("direction", ""),
            major.get("course", ""),
            major.get("skill", ""),
            major.get("mostemploymentindustry", ""),
            major.get("mostemployedeposition", ""),
        ]
    )

    directions: dict[str, list[str]] = defaultdict(list)
    direct_hit = False
    for direction, patterns in DIRECT_DIRECTION_PATTERNS.items():
        for pattern in patterns:
            if pattern and pattern in text:
                directions[direction].append(pattern)
                if pattern in name or pattern in level3:
                    direct_hit = True

    class_hit = False
    for direction, patterns in RELATED_CLASS_PATTERNS.items():
        for pattern in patterns:
            if pattern and (pattern in level3 or pattern in level2):
                directions[direction].append(f"专业类:{pattern}")
                class_hit = True

    emerging_rows = official_rows_for_major(major, emerging_index)
    catalog_rows = official_rows_for_major(major, catalog_index)
    official_source = official_source_text(emerging_rows, catalog_rows)

    score = 0
    reasons: list[str] = []
    if direct_hit:
        score += 5
        reasons.append("专业名称/专业类直接命中新质生产力方向关键词")
    if class_hit:
        score += 2
        reasons.append("所属门类或专业类属于政策方向的基础支撑领域")
    if directions:
        score += min(2, len(directions))
        reasons.append("专业介绍、课程、就业方向或专业名与政策方向词匹配")
    if emerging_rows and directions:
        score += 1
        reasons.append("教育部目录/备案候选池中可追溯")
    if not directions and level2 in NEGATIVE_LEVEL2:
        score -= 1
        reasons.append("人文社科/艺术/教育等传统门类，未命中产业技术方向")
    if is_noise_major_name(name):
        return {
            "label": "待复核",
            "is_new_quality": "待复核",
            "directions": "",
            "confidence": "low",
            "score": 0,
            "rationale": "专业名称疑似表头/OCR噪声，需人工复核。",
            "policy_source_ids": "",
            "policy_evidence_excerpt": "",
            "official_major_source": official_source,
            "needs_review": "是",
            "method": "noise_filter",
        }

    if score >= 6:
        label = "是"
        is_new_quality = "是"
        confidence = "high" if direct_hit else "medium"
    elif score >= 3:
        label = "相关"
        is_new_quality = "相关"
        confidence = "medium"
    elif score >= 1:
        label = "弱相关"
        is_new_quality = "相关"
        confidence = "low"
    else:
        label = "否"
        is_new_quality = "否"
        confidence = "medium" if level2 in NEGATIVE_LEVEL2 else "low"
        if not reasons:
            reasons.append("未命中已抓取政策方向词、专业类规则或官方新兴候选证据")

    sorted_directions = sorted(directions, key=lambda key: (-len(directions[key]), key))
    source_ids, evidence_excerpt = evidence_for_directions(sorted_directions, policies)
    return {
        "label": label,
        "is_new_quality": is_new_quality,
        "directions": ";".join(sorted_directions),
        "confidence": confidence,
        "score": score,
        "rationale": "；".join(reasons[:4]),
        "policy_source_ids": ";".join(source_ids),
        "policy_evidence_excerpt": evidence_excerpt,
        "official_major_source": official_source,
        "needs_review": "否" if confidence != "low" else "是",
        "method": "direct_name_match+major_class_match+policy_keyword_match+official_candidate_join",
    }


def official_rows_for_major(major: dict[str, str], index: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    code = normalize_code(major.get("code", ""))
    name = normalize_name(major.get("special_name", ""))
    rows: list[dict[str, str]] = []
    if code:
        rows.extend(index.get(f"code:{code}", []))
    if name:
        rows.extend(index.get(f"name:{name}", []))
    deduped: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get("candidate_id") or row.get("catalog_record_id") or json.dumps(row, sort_keys=True, ensure_ascii=False)
        deduped[key] = row
    return list(deduped.values())


def official_source_text(emerging_rows: list[dict[str, str]], catalog_rows: list[dict[str, str]]) -> str:
    parts: list[str] = []
    if emerging_rows:
        first = emerging_rows[0]
        parts.append(
            "教育部本科目录/备案候选："
            + compact_text(
                first.get("first_source_title")
                or first.get("source_title")
                or first.get("sample_evidence_text")
                or "已命中",
                120,
            )
        )
    if catalog_rows:
        first = catalog_rows[0]
        parts.append("官方专业目录：" + compact_text(first.get("source_name") or "已命中", 120))
    return "；".join(parts) if parts else "本地 edu_major 基础信息；未命中本轮官方候选/目录索引。"


def evidence_for_directions(
    directions: list[str],
    policies: dict[str, list[PolicyEvidence]],
    *,
    max_directions: int = 3,
) -> tuple[list[str], str]:
    source_ids: list[str] = []
    snippets: list[str] = []
    for direction in directions[:max_directions]:
        evidence_rows = policies.get(direction, [])
        if not evidence_rows:
            continue
        item = evidence_rows[0]
        source_ids.append(item.source_id)
        snippets.append(f"{direction}: {item.issuing_org}/{item.source_year}/{item.keyword} - {item.evidence_text}")
    return source_ids, " | ".join(snippets)


def build_summary_row(
    major: dict[str, str],
    evaluation: dict[str, Any],
    tier_samples: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
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
        "qingbei_sample": sample_text(tier_samples["清北"]),
        "tier_985_sample": sample_text(tier_samples["985"]),
        "tier_211_sample": sample_text(tier_samples["211"]),
        "shuangfei_sample": sample_text(tier_samples["双非"]),
        "sample_coverage": f"{sum(1 for item in tier_samples.values() if item['found'])}/4",
        "needs_review": evaluation["needs_review"],
    }


def build_detail_row(
    major: dict[str, str],
    evaluation: dict[str, Any],
    tier: str,
    sample: dict[str, Any],
) -> dict[str, Any]:
    return {
        "major_special_id": major.get("special_id", ""),
        "major_code": major.get("code", ""),
        "major_name": major.get("special_name", ""),
        "major_type": major.get("special_type", ""),
        "major_level2": major.get("level2_name", ""),
        "major_level3": major.get("level3_name", ""),
        "school_tier": tier,
        "sample_school_id": sample.get("school_id", ""),
        "sample_school_name": sample.get("school_name", ""),
        "sample_school_rank": sample.get("ranking", ""),
        "sample_school_found": "是" if sample.get("found") else "否",
        "tier_offer_count": sample.get("count", 0),
        "evaluation_label": evaluation["label"],
        "is_new_quality_productivity_major": evaluation["is_new_quality"],
        "directions": evaluation["directions"],
        "confidence": evaluation["confidence"],
        "score": evaluation["score"],
        "rationale": evaluation["rationale"],
        "policy_source_ids": evaluation["policy_source_ids"],
        "policy_evidence_excerpt": evaluation["policy_evidence_excerpt"],
        "official_major_source": evaluation["official_major_source"],
        "school_sample_source": sample.get("source", ""),
        "estimation_method": evaluation["method"],
        "needs_review": evaluation["needs_review"],
    }


def build_source_rows(policies: dict[str, list[PolicyEvidence]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for direction, evidence_rows in sorted(policies.items()):
        seen_sources: set[str] = set()
        for item in evidence_rows:
            key = item.source_id
            if key in seen_sources:
                continue
            seen_sources.add(key)
            rows.append(
                {
                    "direction": direction,
                    "source_id": item.source_id,
                    "source_title": item.source_title,
                    "source_url": item.source_url,
                    "source_year": item.source_year,
                    "issuing_org": item.issuing_org,
                    "keyword": item.keyword,
                    "evidence_excerpt": item.evidence_text,
                }
            )
            if len(seen_sources) >= 3:
                break
    return rows


def build_stats(
    majors: list[dict[str, str]],
    detail_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    label_counts = Counter(row["evaluation_label"] for row in summary_rows)
    confidence_counts = Counter(row["confidence"] for row in summary_rows)
    direction_counts: Counter[str] = Counter()
    for row in summary_rows:
        for direction in str(row["directions"]).split(";"):
            if direction:
                direction_counts[direction] += 1
    tier_found = {
        tier: sum(1 for row in detail_rows if row["school_tier"] == tier and row["sample_school_found"] == "是")
        for tier in TIER_ORDER
    }
    return {
        "major_count": len(majors),
        "detail_row_count": len(detail_rows),
        "summary_row_count": len(summary_rows),
        "label_counts": dict(label_counts),
        "confidence_counts": dict(confidence_counts),
        "direction_counts": dict(direction_counts.most_common()),
        "tier_found_counts": tier_found,
        "policy_mentions_csv": str(POLICY_MENTIONS_CSV),
        "emerging_unique_csv": str(EMERGING_UNIQUE_CSV),
        "official_catalog_csv": str(OFFICIAL_CATALOG_CSV),
    }


def sample_text(sample: dict[str, Any]) -> str:
    if not sample.get("found"):
        return "未找到本地开设样本"
    rank = f"，排名{sample['ranking']}" if sample.get("ranking") else ""
    return f"{sample.get('school_name', '')}{rank}；同层次样本数{sample.get('count', 0)}"


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def compact_text(value: str, limit: int = 180) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def normalize_code(value: str) -> str:
    return re.sub(r"\s+", "", value or "").upper()


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def is_noise_major_name(value: str) -> bool:
    name = normalize_name(value)
    return name in {"", "备注", "序号", "序號", "专业名称", "专业", "名称", "专业代码"} or len(name) <= 1


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


if __name__ == "__main__":
    raise SystemExit(main())
