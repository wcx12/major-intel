"""Local MySQL retrieval MVP for school-major intelligence."""

from __future__ import annotations

import argparse
import csv
import html
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_MISSING_DATA = [
    "校专业级工作地域分布",
    "校专业级薪资分布",
    "校专业级Top对口公司",
    "考公岗位映射",
    "转专业政策",
    "专业组真实分流比例/冷门专业比例",
    "学校官网专业介绍证据链",
]


@dataclass(frozen=True)
class DbConfig:
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    database: str = "gaokao_test_local"
    password: str | None = None

    @classmethod
    def from_env(cls) -> "DbConfig":
        password = os.environ.get("GAOKAO_DB_PASSWORD") or os.environ.get("MYSQL_PWD")
        return cls(
            host=os.environ.get("GAOKAO_DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("GAOKAO_DB_PORT", "3306")),
            user=os.environ.get("GAOKAO_DB_USER", "root"),
            database=os.environ.get("GAOKAO_DB_NAME", "gaokao_test_local"),
            password=password,
        )


class MysqlCliClient:
    """Tiny read-only client backed by the local mysql CLI."""

    def __init__(self, config: DbConfig) -> None:
        self.config = config

    def query(self, sql: str) -> list[dict[str, str]]:
        env = os.environ.copy()
        if self.config.password:
            env["MYSQL_PWD"] = self.config.password

        args = [
            "mysql",
            f"--host={self.config.host}",
            f"--port={self.config.port}",
            f"--user={self.config.user}",
            "--get-server-public-key",
            "--connect-timeout=8",
            "--default-character-set=utf8mb4",
            "--batch",
            "--raw",
            "-D",
            self.config.database,
            "-e",
            sql,
        ]
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "mysql query failed")
        return _parse_mysql_tsv(result.stdout)


def resolve_school_sql(text: str, limit: int = 5) -> str:
    query = sql_quote(text)
    like = sql_quote(f"%{text}%")
    return f"""
SELECT school_id, code, name, province_name, city_name, type_name, level_name,
       is985, is211, is_dual_class, dual_class, school_site, site
FROM edu_university
WHERE deleted = b'0'
  AND (
    name = {query}
    OR code = {query}
    OR school_id = {query}
    OR short LIKE {like}
    OR old_name LIKE {like}
    OR name LIKE {like}
  )
ORDER BY
  CASE
    WHEN name = {query} THEN 0
    WHEN code = {query} THEN 1
    WHEN school_id = {query} THEN 2
    WHEN name LIKE {like} THEN 3
    ELSE 9
  END,
  hits DESC
LIMIT {int(limit)}
""".strip()


def resolve_major_sql(text: str, limit: int = 5) -> str:
    query = sql_quote(text)
    like = sql_quote(f"%{text}%")
    return f"""
SELECT special_id, code, special_name, type_name, level2_name, level3_name,
       limit_year, degree, salaryavg, fivesalaryavg, job, is_what, learn_what,
       do_what,
       TRIM(REGEXP_REPLACE(REPLACE(REPLACE(COALESCE(NULLIF(job, ''), NULLIF(do_what, ''), ''), '\\r', ' '), '\\n', ' '), '<[^>]+>', '')) AS job_clean,
       mostemploymentarea, mostemploymentindustry, mostemployedeposition
FROM edu_major
WHERE deleted = b'0'
  AND (
    special_name = {query}
    OR code = {query}
    OR special_id = {query}
    OR special_name LIKE {like}
  )
ORDER BY
  CASE
    WHEN special_name = {query} THEN 0
    WHEN code = {query} THEN 1
    WHEN special_id = {query} THEN 2
    WHEN special_name LIKE {like} THEN 3
    ELSE 9
  END,
  ruanke_rank IS NULL,
  ruanke_rank
LIMIT {int(limit)}
""".strip()


def build_school_major_sql(school: dict[str, Any], major: dict[str, Any]) -> str:
    school_code = str(school.get("code") or school.get("school_id") or "")
    school_name = str(school.get("name") or "")
    major_code = str(major.get("code") or major.get("special_id") or "")
    major_name = str(major.get("special_name") or "")
    return f"""
SELECT sm.school_id, sm.school_name, sm.major_code, sm.major_name, sm.degree_level,
       sm.is_dual_class, sm.nation_first_class, sm.xueke_rank_score, sm.ruanke_level,
       sm.special_id, sm.limit_year, sm.level_name, sm.menlei_name, sm.xueke_name
FROM edu_school_major sm
WHERE (sm.deleted IS NULL OR sm.deleted = 0)
  AND sm.school_id = {sql_quote(school_code)}
  AND sm.school_name = {sql_quote(school_name)}
  AND (
    sm.major_code = {sql_quote(major_code)}
    OR sm.major_name = {sql_quote(major_name)}
  )
ORDER BY
  CASE
    WHEN sm.major_code = {sql_quote(major_code)} THEN 0
    WHEN sm.major_name = {sql_quote(major_name)} THEN 1
    ELSE 9
  END
LIMIT 1
""".strip()


def build_subject_eval_sql(school: dict[str, Any], major: dict[str, Any], limit: int = 5) -> str:
    school_id = str(school.get("school_id") or "")
    major_code = str(major.get("code") or major.get("special_id") or "")
    major_name = str(major.get("special_name") or "")
    related_keyword = _related_subject_keyword(str(major.get("level3_name") or major_name))

    related_clause = ""
    if related_keyword:
        related_clause = f"OR e.major_name LIKE {sql_quote(f'%{related_keyword}%')}"

    return f"""
SELECT e.eval_round, e.major_name, e.eval_level, e.level_code, e.special_id,
       e.special_name,
       CASE
         WHEN e.special_id = {sql_quote(major_code)}
           OR e.special_name = {sql_quote(major_name)}
           OR e.major_name = {sql_quote(major_name)}
         THEN 'exact'
         ELSE 'related'
       END AS match_scope
FROM edu_university_subject_eval e
WHERE (e.deleted IS NULL OR e.deleted = b'0')
  AND e.school_id = {sql_quote(school_id)}
  AND (
    e.special_id = {sql_quote(major_code)}
    OR e.special_name = {sql_quote(major_name)}
    OR e.major_name = {sql_quote(major_name)}
    {related_clause}
  )
ORDER BY match_scope, e.level_code IS NULL, e.level_code, e.eval_level
LIMIT {int(limit)}
""".strip()


def build_dual_class_sql(school: dict[str, Any], major: dict[str, Any], limit: int = 5) -> str:
    school_id = str(school.get("school_id") or "")
    major_code = str(major.get("code") or major.get("special_id") or "")
    major_name = str(major.get("special_name") or "")
    keyword = _related_subject_keyword(str(major.get("level3_name") or major_name))
    keyword_clause = ""
    if keyword:
        keyword_clause = f"OR class_name LIKE {sql_quote(f'%{keyword}%')}"

    return f"""
SELECT class_name, major_code, code, class_type, cycle
FROM edu_dual_class
WHERE deleted = b'0'
  AND school_id = {sql_quote(school_id)}
  AND (
    major_code = {sql_quote(major_code)}
    OR code = {sql_quote(major_code)}
    OR class_name LIKE {sql_quote(f'%{major_name}%')}
    {keyword_clause}
  )
ORDER BY cycle DESC, class_name
LIMIT {int(limit)}
""".strip()


def build_latest_employment_sql(school: dict[str, Any]) -> str:
    school_id = str(school.get("school_id") or "")
    return f"""
SELECT year, employment_rate, further_study_rate, avg_salary,
       top_employment_industries, top_employment_regions, top_employers
FROM edu_university_employment
WHERE (deleted IS NULL OR deleted = b'0')
  AND school_id = {sql_quote(school_id)}
ORDER BY CAST(year AS UNSIGNED) DESC
LIMIT 1
""".strip()


def build_specialty_group_sql(
    school: dict[str, Any], major: dict[str, Any], limit: int = 8
) -> str:
    school_id = str(school.get("school_id") or "")
    major_code = str(major.get("code") or major.get("special_id") or "")
    major_name = str(major.get("special_name") or "")
    return f"""
SELECT g.year, g.province, g.group_code, g.group_name, g.group_type,
       g.plan_count AS group_plan_count, g.min_score, g.min_rank,
       g.allow_adjustment, gm.special_code, gm.special_name,
       gm.plan_count AS major_plan_count, gm.subject_requirement, gm.remark
FROM edu_college_specialty_group g
JOIN edu_specialty_group_major gm ON gm.group_id = g.id
WHERE (g.deleted IS NULL OR g.deleted = b'0')
  AND (gm.deleted IS NULL OR gm.deleted = b'0')
  AND g.school_id = {sql_quote(school_id)}
  AND (
    gm.special_code = {sql_quote(major_code)}
    OR gm.special_name = {sql_quote(major_name)}
  )
ORDER BY g.year DESC, g.province, g.group_code
LIMIT {int(limit)}
""".strip()


def fetch_profile(client: MysqlCliClient, school_text: str, major_text: str) -> dict[str, Any]:
    schools = client.query(resolve_school_sql(school_text, limit=5))
    majors = client.query(resolve_major_sql(major_text, limit=5))
    if not schools:
        raise LookupError(f"本地库没有命中学校：{school_text}")
    if not majors:
        raise LookupError(f"本地库没有命中专业：{major_text}")

    school = schools[0]
    major = majors[0]
    school_major = _first_row(client.query(build_school_major_sql(school, major)))
    subject_evals = client.query(build_subject_eval_sql(school, major))
    dual_classes = client.query(build_dual_class_sql(school, major))
    employment = _first_row(client.query(build_latest_employment_sql(school)))
    specialty_groups = client.query(build_specialty_group_sql(school, major))

    profile = build_profile(
        school=school,
        major=major,
        school_major=school_major,
        subject_evals=subject_evals,
        dual_classes=dual_classes,
        employment=employment,
        specialty_groups=specialty_groups,
    )
    profile["resolution"] = {
        "school_candidates": schools,
        "major_candidates": majors,
        "selected_school": school,
        "selected_major": major,
    }
    return profile


def build_profile(
    *,
    school: dict[str, Any],
    major: dict[str, Any],
    school_major: dict[str, Any] | None,
    subject_evals: list[dict[str, Any]],
    dual_classes: list[dict[str, Any]],
    employment: dict[str, Any] | None,
    specialty_groups: list[dict[str, Any]],
) -> dict[str, Any]:
    available_data = ["学校基础信息", "专业基础信息"]
    missing_data = list(DEFAULT_MISSING_DATA)

    school_major_opened = bool(school_major)
    if school_major_opened:
        available_data.append("学校-专业开设关系")
    else:
        missing_data.insert(0, "学校-专业开设关系")

    if _has_any_value(major, ["salaryavg", "fivesalaryavg", "job", "do_what"]):
        available_data.append("专业通用薪资/就业方向")

    if subject_evals:
        available_data.append("教育部学科评估")

    if _truthy(school.get("is_dual_class")) or dual_classes:
        available_data.append("双一流信息")

    if employment:
        available_data.append("学校层面就业/升学数据")

    if specialty_groups:
        available_data.append("专业组/招生组样本")

    return {
        "school": school,
        "major": major,
        "school_major": school_major,
        "subject_evals": subject_evals,
        "dual_classes": dual_classes,
        "employment": employment,
        "specialty_groups": specialty_groups,
        "facts": {
            "school_major_opened": school_major_opened,
            "school_is_211": _truthy(school.get("is211")),
            "school_is_dual_class": _truthy(school.get("is_dual_class")),
        },
        "available_data": _dedupe(available_data),
        "missing_data": _dedupe(missing_data),
    }


def render_markdown_answer(profile: dict[str, Any]) -> str:
    school = profile["school"]
    major = profile["major"]
    employment = profile.get("employment") or {}
    title = f"{school.get('name', '-')} {major.get('special_name', '-')} 本地库检索结果"
    lines = [
        f"# {title}",
        "",
        "## 命中结论",
        "",
    ]

    if profile["facts"]["school_major_opened"]:
        lines.append(f"- 已在本地库查到该校开设这个专业：{major.get('code', '-')} {major.get('special_name', '-')}")
    else:
        lines.append("- 本地库没有查到明确的学校-专业开设关系，不能直接认定该校开设这个专业。")

    lines.extend(
        [
            f"- 学校：{school.get('name', '-')}，{school.get('province_name', '-')}{school.get('city_name', '')}",
            f"- 专业：{major.get('special_name', '-')}，{major.get('level2_name', '-')} / {major.get('level3_name', '-')}",
            f"- 双一流：{_yes_no(profile['facts']['school_is_dual_class'])}；211：{_yes_no(profile['facts']['school_is_211'])}",
            "",
            "## 专业通用信息",
            "",
            f"- 学制/学位：{_dash(major.get('limit_year'))} / {_dash(major.get('degree'))}",
            f"- 通用薪资参考：平均 {_format_money(major.get('salaryavg'))}，五年后参考 {_format_money(major.get('fivesalaryavg'))}",
            f"- 常见就业方向：{_compact_text(major.get('job_clean') or major.get('job') or major.get('do_what'))}",
            f"- 口径：专业通用参考，不代表{school.get('name', '该校')}该专业毕业生真实薪资。",
            "",
            "## 学校就业/升学",
            "",
        ]
    )

    if employment:
        lines.extend(
            [
                f"- 年份：{_dash(employment.get('year'))}",
                f"- 就业率：{_format_percent(employment.get('employment_rate'))}",
                f"- 升学率：{_format_percent(employment.get('further_study_rate'))}",
                f"- 平均薪资：{_format_money(employment.get('avg_salary'))}",
                "- 口径：学校层面数据，不代表某个专业。",
            ]
        )
    else:
        lines.append("- 本地库暂未命中该校就业/升学数据。")

    lines.extend(["", "## 学科建设", ""])
    if profile.get("subject_evals"):
        for row in profile["subject_evals"]:
            scope = "精确" if row.get("match_scope") == "exact" else "相关"
            lines.append(
                f"- {row.get('eval_round', '-')}：{row.get('major_name', '-')} {row.get('eval_level', '-')}（{scope}匹配）"
            )
    else:
        lines.append("- 本地库暂未命中该专业对应或相关学科评估。")

    if profile.get("dual_classes"):
        for row in profile["dual_classes"]:
            lines.append(f"- 双一流学科：{row.get('class_name', '-')}（{row.get('cycle', '-')}）")
    elif profile["facts"]["school_is_dual_class"]:
        lines.append("- 学校标记为双一流，但本专业未命中具体双一流学科。")
    else:
        lines.append("- 学校未标记为双一流。")

    lines.extend(["", "## 专业组样本", ""])
    if profile.get("specialty_groups"):
        for row in profile["specialty_groups"][:8]:
            lines.append(
                "- "
                f"{row.get('year', '-')} 年 {row.get('province', '-')}："
                f"{row.get('group_name', '-')}，"
                f"专业计划 {_dash(row.get('major_plan_count'))}，"
                f"选科 {_dash(row.get('subject_requirement'))}"
            )
        lines.append("- 口径：这里是招生志愿专业组，不等于入学后的真实分流比例。")
    else:
        lines.append("- 本地库暂未命中包含该专业的专业组样本。")

    lines.extend(["", "## 已有数据", ""])
    lines.extend(f"- {item}" for item in profile["available_data"])

    lines.extend(["", "## 仍缺的数据", ""])
    lines.extend(f"- {item}" for item in profile["missing_data"])

    lines.extend(
        [
            "",
            "## 下一步处理建议",
            "",
            "- 已有字段可直接进入本地 RAG 上下文。",
            "- 缺失字段应进入数据缺口队列，后续由联网 agent 或人工补证据。",
            "- 没有命中的事实不要让模型补写，只能回答“本地库暂未命中”。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_markdown_answer(profile: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_answer(profile), encoding="utf-8-sig")


def sql_quote(value: Any) -> str:
    text = "" if value is None else str(value)
    text = (
        text.replace("\\", "\\\\")
        .replace("\0", "")
        .replace("'", "''")
        .replace("\r", " ")
        .replace("\n", " ")
    )
    return f"'{text}'"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query the local gaokao MySQL database.")
    parser.add_argument("--school", required=True, help="School name/code to resolve.")
    parser.add_argument("--major", required=True, help="Major name/code to resolve.")
    parser.add_argument("--output", type=Path, help="Optional Markdown report path.")
    args = parser.parse_args(argv)

    profile = fetch_profile(MysqlCliClient(DbConfig.from_env()), args.school, args.major)
    markdown = render_markdown_answer(profile)
    if args.output:
        write_markdown_answer(profile, args.output)
        print(str(args.output))
    else:
        print(markdown)
    return 0


def _parse_mysql_tsv(text: str) -> list[dict[str, str]]:
    rows = list(csv.reader(text.splitlines(), delimiter="\t"))
    if not rows:
        return []
    headers = rows[0]
    parsed = []
    for row in rows[1:]:
        if not row:
            continue
        padded = row + [""] * max(0, len(headers) - len(row))
        parsed.append(dict(zip(headers, padded[: len(headers)])))
    return parsed


def _first_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    return rows[0] if rows else None


def _has_any_value(row: dict[str, Any], keys: list[str]) -> bool:
    return any(_dash(row.get(key)) != "-" for key in keys)


def _truthy(value: Any) -> bool:
    return str(value or "").strip() in {"1", "true", "True", "是", "yes"}


def _yes_no(value: bool) -> str:
    return "是" if value else "否"


def _dash(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    return text if text and text.upper() != "NULL" else "-"


def _format_percent(value: Any) -> str:
    text = _dash(value)
    if text == "-":
        return "-"
    try:
        number = float(text)
    except ValueError:
        return text
    return f"{number:.2f}%"


def _format_money(value: Any) -> str:
    text = _dash(value)
    if text == "-":
        return "-"
    try:
        number = float(text)
    except ValueError:
        return text
    if number >= 10000:
        return f"{number:,.0f} 元/年"
    return f"{number:,.0f} 元/月"


def _compact_text(value: Any, max_length: int = 140) -> str:
    text = html.unescape(_dash(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = " ".join(text.split())
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "..."


def _related_subject_keyword(text: str) -> str:
    text = text.strip()
    for suffix in ("类", "学类", "工程类"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
            break
    if len(text) >= 2:
        return text[:4]
    return ""


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
