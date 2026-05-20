"""Ingest crawled rysxai market and civil-service data into local MySQL.

This module is intentionally placed between raw crawler outputs and later
function-call tools.  The crawler files are useful, but they are file-based and
carry different evidence scopes.  The tables created here preserve that scope
so an agent can later say "market sample" or "role requirement text" instead of
accidentally presenting the data as official school-major employment evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


MARKET_SNAPSHOT_TABLE = "rysxai_major_market_snapshots"
MARKET_SAMPLE_TABLE = "rysxai_major_job_samples"
CIVIL_ROLE_TABLE = "rysxai_civil_service_roles"
CIVIL_CANDIDATE_TABLE = "civil_service_major_role_candidates"
TRANSFER_POLICY_TABLE = "rysxai_transfer_policies"
MOJIBAKE_MARKERS = frozenset(
    "澶嶆棪涓婃捣鏈娴欐睙鍖椾含鏉窞缁煎悎鍏姙鏁欒偛"
    "杞笓涓氭斂绛栫敵璇锋潯浠跺噯鍏ヨ姹傝€冩牳"
    "淇伅瀛﹂櫌鐢宠"
)


@dataclass(frozen=True)
class DbConfig:
    """Connection settings for the local gaokao MySQL database.

    The password deliberately comes only from the process environment.  Keeping
    this object small and explicit makes it harder to accidentally persist local
    credentials into generated SQL, docs, test fixtures, or shell history.
    """

    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    database: str = "gaokao_test_local"
    password: str | None = None

    @classmethod
    def from_env(cls) -> "DbConfig":
        return cls(
            host=os.environ.get("GAOKAO_DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("GAOKAO_DB_PORT", "3306")),
            user=os.environ.get("GAOKAO_DB_USER", "root"),
            database=os.environ.get("GAOKAO_DB_NAME", "gaokao_test_local"),
            password=os.environ.get("GAOKAO_DB_PASSWORD") or os.environ.get("MYSQL_PWD"),
        )


class MysqlCliRunner:
    """Run SQL through the mysql CLI without putting secrets in the SQL text.

    The project environment currently has the mysql command available, while a
    Python MySQL driver is not guaranteed to be installed.  Feeding SQL through
    stdin avoids command-line length limits during bulk inserts and also keeps
    generated SQL files unnecessary for the first ingestion pass.
    """

    def __init__(self, config: DbConfig) -> None:
        self.config = config

    def run(self, sql: str, capture_output: bool = False) -> str:
        env = os.environ.copy()
        if self.config.password:
            env["MYSQL_PWD"] = self.config.password

        args = [
            "mysql",
            f"--host={self.config.host}",
            f"--port={self.config.port}",
            f"--user={self.config.user}",
            "--get-server-public-key",
            "--connect-timeout=10",
            "--default-character-set=utf8mb4",
            "-D",
            self.config.database,
        ]
        result = subprocess.run(
            args,
            input=sql,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "mysql command failed")
        if capture_output:
            return result.stdout
        return ""


def build_schema_sql() -> str:
    """Return idempotent DDL for all rysxai ingestion tables.

    These tables are intentionally separate from the existing gaokao business
    tables.  The separation protects the original imported database while still
    making crawled data queryable by later function-call tools.
    """

    return f"""
CREATE TABLE IF NOT EXISTS {MARKET_SNAPSHOT_TABLE} (
  profession_id BIGINT NOT NULL,
  major_code VARCHAR(32) NULL,
  major_name VARCHAR(200) NULL,
  major_level VARCHAR(50) NULL,
  degree VARCHAR(100) NULL,
  limit_year VARCHAR(50) NULL,
  captured_at VARCHAR(50) NULL,
  source_name VARCHAR(50) NULL,
  source_level VARCHAR(10) NULL,
  data_scope VARCHAR(100) NULL,
  info_url VARCHAR(500) NULL,
  positions_url VARCHAR(500) NULL,
  macro_employment_json JSON NULL,
  demand_ranking_json JSON NULL,
  salary_ranking_json JSON NULL,
  salary_observations_by_city_json JSON NULL,
  salary_observations_by_industry_json JSON NULL,
  job_posting_sample_total_reported INT NULL,
  job_posting_sample_count INT NULL,
  warnings_json JSON NULL,
  raw_snapshot_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (profession_id),
  KEY idx_major_code (major_code),
  KEY idx_major_name (major_name),
  KEY idx_source_scope (source_level, data_scope)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS {MARKET_SAMPLE_TABLE} (
  id BIGINT NOT NULL AUTO_INCREMENT,
  profession_id BIGINT NOT NULL,
  source_item_id VARCHAR(64) NOT NULL DEFAULT '',
  major_code VARCHAR(32) NULL,
  major_name VARCHAR(200) NULL,
  job_title VARCHAR(255) NULL,
  company_name VARCHAR(255) NULL,
  city VARCHAR(100) NULL,
  district VARCHAR(100) NULL,
  industry VARCHAR(255) NULL,
  salary_raw VARCHAR(100) NULL,
  monthly_salary_min INT NULL,
  monthly_salary_max INT NULL,
  education VARCHAR(100) NULL,
  experience VARCHAR(100) NULL,
  skills_json JSON NULL,
  company_tags_json JSON NULL,
  company_scale VARCHAR(100) NULL,
  financing_stage VARCHAR(100) NULL,
  source_level VARCHAR(10) NULL,
  data_scope VARCHAR(100) NULL,
  captured_at VARCHAR(50) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_profession_sample (profession_id, source_item_id),
  KEY idx_major_code (major_code),
  KEY idx_city (city),
  KEY idx_industry (industry)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS {CIVIL_ROLE_TABLE} (
  role_id BIGINT NOT NULL,
  year INT NULL,
  sheet_type VARCHAR(255) NULL,
  department_code VARCHAR(64) NULL,
  department_name VARCHAR(255) NULL,
  sub_department VARCHAR(255) NULL,
  job_name VARCHAR(255) NULL,
  position_code VARCHAR(64) NULL,
  exam_type VARCHAR(100) NULL,
  plan_num INT NULL,
  apply_num INT NULL,
  ratio DECIMAL(10,2) NULL,
  profession_text TEXT NULL,
  education_level VARCHAR(100) NULL,
  degree_requirement VARCHAR(100) NULL,
  work_location VARCHAR(100) NULL,
  province VARCHAR(100) NULL,
  remark TEXT NULL,
  source_url VARCHAR(500) NULL,
  fetched_at VARCHAR(50) NULL,
  raw_role_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (role_id),
  KEY idx_year (year),
  KEY idx_province (province),
  KEY idx_department_code (department_code),
  KEY idx_position_code (position_code)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS {CIVIL_CANDIDATE_TABLE} (
  id BIGINT NOT NULL AUTO_INCREMENT,
  role_id BIGINT NOT NULL,
  candidate_type VARCHAR(50) NOT NULL,
  major_code VARCHAR(32) NOT NULL DEFAULT '',
  major_name VARCHAR(200) NOT NULL DEFAULT '',
  profession_text TEXT NULL,
  match_status VARCHAR(50) NOT NULL DEFAULT 'candidate',
  evidence_text TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_role_candidate (role_id, candidate_type, major_code, major_name),
  KEY idx_major_code (major_code),
  KEY idx_match_status (match_status)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS {TRANSFER_POLICY_TABLE} (
  school_id BIGINT NOT NULL,
  school_name VARCHAR(255) NULL,
  province VARCHAR(100) NULL,
  city VARCHAR(100) NULL,
  town VARCHAR(100) NULL,
  school_type VARCHAR(100) NULL,
  property VARCHAR(100) NULL,
  school_level VARCHAR(50) NULL,
  department VARCHAR(255) NULL,
  tags_json JSON NULL,
  rank_list_json JSON NULL,
  fetched_at VARCHAR(50) NULL,
  source_name VARCHAR(50) NULL,
  source_level VARCHAR(10) NULL,
  data_scope VARCHAR(100) NULL,
  source_url VARCHAR(500) NULL,
  source_endpoint VARCHAR(20) NULL,
  has_transfer_policy TINYINT(1) NOT NULL DEFAULT 0,
  has_faculty_policy TINYINT(1) NOT NULL DEFAULT 0,
  faculty_policy_count INT NULL,
  change_profession_chars INT NULL,
  application_condition_chars INT NULL,
  admission_requirement_chars INT NULL,
  assessment_chars INT NULL,
  is_new_version TINYINT(1) NOT NULL DEFAULT 0,
  change_profession MEDIUMTEXT NULL,
  change_profession_application_condition MEDIUMTEXT NULL,
  change_profession_admission_requirement MEDIUMTEXT NULL,
  change_profession_assessment MEDIUMTEXT NULL,
  change_profession_by_faculty_json JSON NULL,
  warnings_json JSON NULL,
  raw_policy_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (school_id),
  KEY idx_transfer_school_name (school_name),
  KEY idx_transfer_province_level (province, school_level),
  KEY idx_transfer_source_endpoint (source_endpoint),
  KEY idx_transfer_availability (has_transfer_policy, has_faculty_policy)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
""".strip()


def market_snapshot_to_rows(
    snapshot: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Convert one normalized market snapshot JSON into SQL-ready rows.

    The snapshot row stores macro distributions and the raw normalized snapshot
    as JSON.  The sample rows intentionally keep recruiting jobs separate:
    future tools may need to show representative jobs, aggregate salary samples,
    or filter market observations by city/industry without parsing a large JSON
    blob each time.
    """

    profession = snapshot.get("profession") or {}
    source = snapshot.get("source") or {}
    profession_id = _to_int(profession.get("id"))
    if profession_id is None:
        raise ValueError("market snapshot missing profession.id")

    snapshot_row = {
        "profession_id": profession_id,
        "major_code": _text(profession.get("code")),
        "major_name": _text(profession.get("name")),
        "major_level": _text(profession.get("level")),
        "degree": _text(profession.get("degree")),
        "limit_year": _text(profession.get("limit_year")),
        "captured_at": _text(snapshot.get("captured_at")),
        "source_name": _text(source.get("name")),
        "source_level": _text(source.get("source_level")),
        "data_scope": _text(source.get("data_scope")),
        "info_url": _text(source.get("info_url")),
        "positions_url": _text(source.get("positions_url")),
        "macro_employment_json": _json_text(snapshot.get("macro_employment") or {}),
        "demand_ranking_json": _json_text(snapshot.get("demand_ranking") or []),
        "salary_ranking_json": _json_text(snapshot.get("salary_ranking") or []),
        "salary_observations_by_city_json": _json_text(
            snapshot.get("salary_observations_by_city") or {}
        ),
        "salary_observations_by_industry_json": _json_text(
            snapshot.get("salary_observations_by_industry") or {}
        ),
        "job_posting_sample_total_reported": _to_int(
            snapshot.get("job_posting_sample_total_reported")
        ),
        "job_posting_sample_count": _to_int(snapshot.get("job_posting_sample_count")),
        "warnings_json": _json_text(snapshot.get("warnings") or []),
        "raw_snapshot_json": _json_text(snapshot),
    }

    sample_rows = []
    for sample in snapshot.get("job_posting_samples") or []:
        # source_item_id is part of the idempotency key.  Empty string is safer
        # than NULL because MySQL UNIQUE indexes permit multiple NULL values.
        sample_rows.append(
            {
                "profession_id": profession_id,
                "source_item_id": _text(sample.get("source_item_id")),
                "major_code": snapshot_row["major_code"],
                "major_name": snapshot_row["major_name"],
                "job_title": _text(sample.get("job_title")),
                "company_name": _text(sample.get("company_name")),
                "city": _text(sample.get("city")),
                "district": _text(sample.get("district")),
                "industry": _text(sample.get("industry")),
                "salary_raw": _text(sample.get("salary_raw")),
                "monthly_salary_min": _to_int(sample.get("monthly_salary_min")),
                "monthly_salary_max": _to_int(sample.get("monthly_salary_max")),
                "education": _text(sample.get("education")),
                "experience": _text(sample.get("experience")),
                "skills_json": _json_text(sample.get("skills") or []),
                "company_tags_json": _json_text(sample.get("company_tags") or []),
                "company_scale": _text(sample.get("company_scale")),
                "financing_stage": _text(sample.get("financing_stage")),
                "source_level": _text(sample.get("source_level") or source.get("source_level")),
                "data_scope": _text(sample.get("data_scope") or "recruiting_market_sample"),
                "captured_at": snapshot_row["captured_at"],
            }
        )

    return snapshot_row, sample_rows


def civil_role_record_to_rows(
    record: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Convert one civil-service detail record into role and candidate rows.

    The professional requirement field is not a clean major-code list.  It may
    contain exact six-digit undergraduate codes, broad discipline categories,
    free-form "related major" text, or mixed undergraduate/graduate wording.
    This function therefore creates candidates rather than final eligibility
    facts.  Later mapping tools can join candidates to `edu_major` and route
    ambiguous text to human review.
    """

    role = record.get("role") or {}
    role_id = _to_int(role.get("id"))
    if role_id is None:
        raise ValueError("civil-service record missing role.id")

    source = record.get("source") or {}
    profession_text = _text(role.get("profession"))
    role_row = {
        "role_id": role_id,
        "year": _to_int(role.get("year")),
        "sheet_type": _text(role.get("sheet_type")),
        "department_code": _text(role.get("department_code")),
        "department_name": _text(role.get("department_name")),
        "sub_department": _text(role.get("sub_department")),
        "job_name": _text(role.get("job_name")),
        "position_code": _text(role.get("position_code")),
        "exam_type": _text(role.get("exam_type")),
        "plan_num": _to_int(role.get("plan_num")),
        "apply_num": _to_int(role.get("apply_num")),
        "ratio": _to_float(role.get("ratio")),
        "profession_text": profession_text,
        "education_level": _text(role.get("education_level")),
        "degree_requirement": _text(role.get("degree_requirement")),
        "work_location": _text(role.get("work_location")),
        "province": _text(role.get("province")),
        "remark": _text(role.get("remark")),
        "source_url": _text(source.get("source_url")),
        "fetched_at": _text(record.get("fetched_at")),
        "raw_role_json": _json_text(role),
    }

    candidate_rows = _extract_civil_major_candidates(role_id, profession_text)
    return role_row, candidate_rows


def transfer_policy_record_to_row(record: dict[str, Any]) -> dict[str, Any]:
    """Convert one rysxai transfer-policy JSONL record into a SQL-ready row."""

    school = record.get("school") or {}
    school_id = _to_int(school.get("id"))
    if school_id is None:
        raise ValueError("transfer-policy record missing school.id")

    source = record.get("source") or {}
    policy = record.get("transfer_policy") or {}
    availability = record.get("availability") or {}
    source_url = _text(source.get("source_url"))
    repaired_faculty = _repair_text_tree(policy.get("change_profession_by_faculty") or [])

    return {
        "school_id": school_id,
        "school_name": _repair_mojibake(_text(school.get("name"))),
        "province": _repair_mojibake(_text(school.get("province"))),
        "city": _repair_mojibake(_text(school.get("city"))),
        "town": _repair_mojibake(_text(school.get("town"))),
        "school_type": _repair_mojibake(_text(school.get("type"))),
        "property": _repair_mojibake(_text(school.get("property"))),
        "school_level": _repair_mojibake(_text(school.get("level"))),
        "department": _repair_mojibake(_text(school.get("department"))),
        "tags_json": _json_text(_repair_text_tree(school.get("tags") or [])),
        "rank_list_json": _json_text(school.get("rank_list") or []),
        "fetched_at": _text(record.get("fetched_at")),
        "source_name": _text(source.get("name")),
        "source_level": _text(source.get("source_level")),
        "data_scope": _text(source.get("data_scope")),
        "source_url": source_url,
        "source_endpoint": _transfer_source_endpoint(source_url),
        "has_transfer_policy": _bool_int(availability.get("has_transfer_policy")),
        "has_faculty_policy": _bool_int(availability.get("has_faculty_policy")),
        "faculty_policy_count": _to_int(availability.get("faculty_policy_count")),
        "change_profession_chars": _to_int(availability.get("change_profession_chars")),
        "application_condition_chars": _to_int(
            availability.get("application_condition_chars")
        ),
        "admission_requirement_chars": _to_int(
            availability.get("admission_requirement_chars")
        ),
        "assessment_chars": _to_int(availability.get("assessment_chars")),
        "is_new_version": _bool_int(policy.get("is_new_version")),
        "change_profession": _repair_mojibake(_text(policy.get("change_profession"))),
        "change_profession_application_condition": _repair_mojibake(
            _text(policy.get("change_profession_application_condition"))
        ),
        "change_profession_admission_requirement": _repair_mojibake(
            _text(policy.get("change_profession_admission_requirement"))
        ),
        "change_profession_assessment": _repair_mojibake(
            _text(policy.get("change_profession_assessment"))
        ),
        "change_profession_by_faculty_json": _json_text(repaired_faculty),
        "warnings_json": _json_text(_repair_text_tree(record.get("warnings") or [])),
        "raw_policy_json": _json_text(record),
    }


def build_insert_sql(
    table_name: str,
    rows: list[dict[str, Any]],
    key_columns: list[str] | None = None,
) -> str:
    """Build an idempotent MySQL INSERT statement for homogeneous row dicts.

    The function is intentionally dumb about business meaning: callers choose
    the table and key columns.  It only handles SQL literal escaping and the
    `ON DUPLICATE KEY UPDATE` clause.  Keeping this centralized avoids ad-hoc
    string interpolation across ingestion paths.
    """

    if not rows:
        return ""

    columns = _ordered_columns(rows)
    values_sql = []
    for row in rows:
        values_sql.append("(" + ", ".join(_sql_literal(row.get(col)) for col in columns) + ")")

    key_set = set(key_columns or [])
    update_columns = [col for col in columns if col not in key_set]
    update_sql = ", ".join(f"{col}=VALUES({col})" for col in update_columns)
    return (
        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
        + ",\n".join(values_sql)
        + f"\nON DUPLICATE KEY UPDATE {update_sql};"
    )


def load_market_snapshots(processed_dir: Path, limit: int | None = None) -> list[dict[str, Any]]:
    """Load normalized market snapshot JSON files from the processed directory."""

    snapshots = []
    for path in sorted(processed_dir.glob("profession_*_market_snapshot.json")):
        snapshots.append(_read_json(path))
        if limit is not None and len(snapshots) >= limit:
            break
    return snapshots


def load_civil_role_records(jsonl_path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    """Load civil-service role records from JSONL while ignoring blank lines."""

    records = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
            if limit is not None and len(records) >= limit:
                break
    return records


def load_transfer_policy_records(
    jsonl_path: Path, limit: int | None = None
) -> list[dict[str, Any]]:
    """Load transfer-policy records from JSONL while ignoring blank lines."""

    records = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
            if limit is not None and len(records) >= limit:
                break
    return records


def ingest_market(
    runner: MysqlCliRunner,
    processed_dir: Path,
    limit: int | None = None,
    chunk_size: int = 200,
) -> dict[str, int]:
    snapshots = load_market_snapshots(processed_dir, limit=limit)
    snapshot_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []

    for snapshot in snapshots:
        snapshot_row, rows = market_snapshot_to_rows(snapshot)
        snapshot_rows.append(snapshot_row)
        sample_rows.extend(rows)

    for chunk in _chunks(snapshot_rows, chunk_size):
        runner.run(build_insert_sql(MARKET_SNAPSHOT_TABLE, chunk, ["profession_id"]))
    for chunk in _chunks(sample_rows, chunk_size):
        runner.run(
            build_insert_sql(
                MARKET_SAMPLE_TABLE,
                chunk,
                ["profession_id", "source_item_id"],
            )
        )

    return {
        "snapshots": len(snapshot_rows),
        "job_samples": len(sample_rows),
    }


def ingest_civil(
    runner: MysqlCliRunner,
    jsonl_path: Path,
    limit: int | None = None,
    chunk_size: int = 200,
) -> dict[str, int]:
    records = load_civil_role_records(jsonl_path, limit=limit)
    role_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []

    for record in records:
        role_row, rows = civil_role_record_to_rows(record)
        role_rows.append(role_row)
        candidate_rows.extend(rows)

    for chunk in _chunks(role_rows, chunk_size):
        runner.run(build_insert_sql(CIVIL_ROLE_TABLE, chunk, ["role_id"]))
    for chunk in _chunks(candidate_rows, chunk_size):
        runner.run(
            build_insert_sql(
                CIVIL_CANDIDATE_TABLE,
                chunk,
                ["role_id", "candidate_type", "major_code", "major_name"],
            )
        )

    return {
        "roles": len(role_rows),
        "major_candidates": len(candidate_rows),
    }


def ingest_transfer(
    runner: MysqlCliRunner,
    jsonl_path: Path,
    limit: int | None = None,
    chunk_size: int = 200,
) -> dict[str, int]:
    records = load_transfer_policy_records(jsonl_path, limit=limit)
    policy_rows = [transfer_policy_record_to_row(record) for record in records]

    for chunk in _chunks(policy_rows, chunk_size):
        runner.run(build_insert_sql(TRANSFER_POLICY_TABLE, chunk, ["school_id"]))

    return {"policies": len(policy_rows)}


def summarize(runner: MysqlCliRunner) -> str:
    return runner.run(
        f"""
SELECT '{MARKET_SNAPSHOT_TABLE}' AS table_name, COUNT(*) AS row_count FROM {MARKET_SNAPSHOT_TABLE}
UNION ALL
SELECT '{MARKET_SAMPLE_TABLE}', COUNT(*) FROM {MARKET_SAMPLE_TABLE}
UNION ALL
SELECT '{CIVIL_ROLE_TABLE}', COUNT(*) FROM {CIVIL_ROLE_TABLE}
UNION ALL
SELECT '{CIVIL_CANDIDATE_TABLE}', COUNT(*) FROM {CIVIL_CANDIDATE_TABLE}
UNION ALL
SELECT '{TRANSFER_POLICY_TABLE}', COUNT(*) FROM {TRANSFER_POLICY_TABLE};
""".strip(),
        capture_output=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest crawled rysxai data into MySQL.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-schema", help="Create rysxai ingestion tables.")

    market_parser = subparsers.add_parser("ingest-market", help="Ingest market snapshots.")
    market_parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/rysxai"))
    market_parser.add_argument("--limit", type=int)
    market_parser.add_argument("--chunk-size", type=int, default=200)

    civil_parser = subparsers.add_parser("ingest-civil", help="Ingest civil-service role JSONL.")
    civil_parser.add_argument(
        "--jsonl",
        type=Path,
        default=Path("data/raw/rysxai_civil_service_2026.jsonl"),
    )
    civil_parser.add_argument("--limit", type=int)
    civil_parser.add_argument("--chunk-size", type=int, default=200)

    transfer_parser = subparsers.add_parser(
        "ingest-transfer",
        help="Ingest school transfer-major policy JSONL.",
    )
    transfer_parser.add_argument(
        "--jsonl",
        type=Path,
        default=Path("data/raw/rysxai_transfer_policies.jsonl"),
    )
    transfer_parser.add_argument("--limit", type=int)
    transfer_parser.add_argument("--chunk-size", type=int, default=200)

    subparsers.add_parser("summarize", help="Show ingestion table counts.")

    args = parser.parse_args(argv)
    runner = MysqlCliRunner(DbConfig.from_env())

    if args.command == "init-schema":
        runner.run(build_schema_sql())
        print("schema initialized")
        return 0

    if args.command == "ingest-market":
        stats = ingest_market(
            runner,
            processed_dir=args.processed_dir,
            limit=args.limit,
            chunk_size=args.chunk_size,
        )
        print(json.dumps(stats, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "ingest-civil":
        stats = ingest_civil(
            runner,
            jsonl_path=args.jsonl,
            limit=args.limit,
            chunk_size=args.chunk_size,
        )
        print(json.dumps(stats, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "ingest-transfer":
        stats = ingest_transfer(
            runner,
            jsonl_path=args.jsonl,
            limit=args.limit,
            chunk_size=args.chunk_size,
        )
        print(json.dumps(stats, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "summarize":
        print(summarize(runner), end="")
        return 0

    raise ValueError(f"Unknown command: {args.command}")


def _extract_civil_major_candidates(role_id: int, profession_text: str) -> list[dict[str, Any]]:
    """Extract conservative major-code candidates from a role requirement string."""

    candidates = []
    seen: set[tuple[str, str]] = set()
    for match in re.finditer(r"(?P<code>\d{6})(?P<name>[^,，、；;\s。]*)", profession_text):
        code = match.group("code")
        name = _clean_major_name(match.group("name"))
        key = (code, name)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            {
                "role_id": role_id,
                "candidate_type": "major_code",
                "major_code": code,
                "major_name": name,
                "profession_text": profession_text,
                "match_status": "candidate",
                "evidence_text": match.group(0),
            }
        )

    if candidates:
        return candidates

    # Many roles list only broad categories such as "computer category" or
    # "related majors".  Keeping one raw candidate prevents data loss while
    # clearly signalling that no precise major-code mapping exists yet.
    return [
        {
            "role_id": role_id,
            "candidate_type": "raw_profession_text",
            "major_code": "",
            "major_name": "",
            "profession_text": profession_text,
            "match_status": "candidate",
            "evidence_text": profession_text,
        }
    ]


def _clean_major_name(value: str | None) -> str:
    text = _text(value)
    return text.strip(" ：:()（）")


def _transfer_source_endpoint(source_url: str) -> str:
    if "/docs/new/" in source_url:
        return "new"
    if "/docs/" in source_url:
        return "legacy"
    return "unknown"


def _repair_text_tree(value: Any) -> Any:
    if isinstance(value, str):
        return _repair_mojibake(value)
    if isinstance(value, list):
        return [_repair_text_tree(item) for item in value]
    if isinstance(value, dict):
        return {key: _repair_text_tree(item) for key, item in value.items()}
    return value


def _repair_mojibake(value: str) -> str:
    if not value or value.isascii():
        return value
    try:
        # Some upstream strings already contain replacement/private-use
        # characters.  Strict reverse decoding would abandon the whole field,
        # but a tolerant pass still recovers the useful Chinese policy text
        # around the damaged bytes, such as "申请转专业".
        repaired = value.encode("gb18030", errors="replace").decode("utf-8", errors="replace")
    except UnicodeError:
        return value
    if repaired == value:
        return value

    original_damage = _encoding_damage_count(value)
    repaired_damage = _encoding_damage_count(repaired)
    marker_count = _mojibake_marker_count(value)

    if original_damage > repaired_damage and _looks_like_better_chinese(value, repaired):
        return repaired
    if (
        marker_count >= 2
        and repaired_damage <= original_damage
        and _looks_like_better_chinese(value, repaired)
    ):
        return repaired
    if (
        marker_count >= 1
        and len(value) < 200
        and repaired_damage <= original_damage
        and _looks_like_better_chinese(value, repaired)
    ):
        return repaired
    return value


def _looks_like_better_chinese(original: str, repaired: str) -> bool:
    if "\ufffd" in repaired:
        return False
    original_cjk = _cjk_count(original)
    repaired_cjk = _cjk_count(repaired)
    if original_cjk == 0:
        return repaired_cjk > 0
    return repaired_cjk >= max(1, int(original_cjk * 0.6))


def _encoding_damage_count(value: str) -> int:
    return _private_use_count(value) + value.count("\ufffd")


def _cjk_count(value: str) -> int:
    return sum(1 for char in value if "\u4e00" <= char <= "\u9fff")


def _private_use_count(value: str) -> int:
    return sum(1 for char in value if 0xE000 <= ord(char) <= 0xF8FF)


def _mojibake_marker_count(value: str) -> int:
    return sum(1 for char in value if char in MOJIBAKE_MARKERS)


def _bool_int(value: Any) -> int:
    return 1 if bool(value) else 0


def _ordered_columns(rows: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    seen = set()
    for row in rows:
        for column in row.keys():
            if column not in seen:
                columns.append(column)
                seen.add(column)
    return columns


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    text = (
        text.replace("\\", "\\\\")
        .replace("\0", "")
        .replace("'", "''")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )
    return f"'{text}'"


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _chunks(values: list[dict[str, Any]], size: int) -> Iterable[list[dict[str, Any]]]:
    if size <= 0:
        raise ValueError("chunk size must be positive")
    for index in range(0, len(values), size):
        yield values[index : index + size]


if __name__ == "__main__":
    raise SystemExit(main())
