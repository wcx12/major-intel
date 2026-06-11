"""Read-only MySQL export for volunteer matching backtests."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import AdmissionHistory, PredictionCase


def _column(name: str, alias: str | None = None) -> str:
    return f"{alias}.{name}" if alias else name


def _major_key_sql(alias: str | None = None) -> str:
    return "COALESCE(NULLIF({major_code}, ''), NULLIF({major_name}, ''), '')".format(
        major_code=_column("major_code", alias),
        major_name=_column("major_name", alias),
    )


def _opportunity_grain_sql(alias: str | None = None) -> str:
    return f"CASE WHEN {_major_key_sql(alias)} <> '' THEN 'major' ELSE 'school' END"


def _subject_key_sql(alias: str | None = None) -> str:
    remark = _column("remark", alias)
    subject_type = _column("subject_type", alias)
    return (
        f"COALESCE(NULLIF({subject_type}, ''), "
        f"CASE WHEN {remark} LIKE '史%' OR {remark} LIKE '历史%' THEN 'history' "
        f"WHEN {remark} LIKE '物%' OR {remark} LIKE '物理%' THEN 'physics' END)"
    )


def _batch_key_sql(alias: str | None = None) -> str:
    remark = _column("remark", alias)
    batch = _column("batch", alias)
    return (
        f"COALESCE(NULLIF({batch}, ''), "
        f"CASE WHEN {remark} LIKE '%/%' THEN NULLIF(TRIM(SUBSTRING_INDEX({remark}, '/', -1)), '') END)"
    )


def _opportunity_key_sql(alias: str | None = None) -> str:
    school_id = _column("school_id", alias)
    province_id = _column("province_id", alias)
    return (
        f"CONCAT({school_id}, ':', {_major_key_sql(alias)}, ':', {province_id}, ':', "
        f"COALESCE({_subject_key_sql(alias)}, ''), ':', COALESCE({_batch_key_sql(alias)}, ''))"
    )


def build_actual_sql(target_year: int, limit: int = 500, sample_mode: str = "sequential") -> str:
    if sample_mode == "stratified":
        return _build_stratified_actual_sql(target_year=target_year, limit=limit)
    if sample_mode != "sequential":
        raise ValueError(f"unknown sample mode: {sample_mode}")
    return f"""
SELECT
  {_opportunity_key_sql()} AS opportunity_key,
  year,
  stable_rank AS actual_rank,
  stable_score AS actual_score,
  school_id,
  school_name,
  major_code,
  major_name,
  {_opportunity_grain_sql()} AS opportunity_grain,
  province_id,
  province_name,
  {_subject_key_sql()} AS subject_type,
  {_batch_key_sql()} AS batch
FROM edu_school_admission_stats
WHERE deleted = 0
  AND year = {int(target_year)}
  AND stable_rank IS NOT NULL
  AND stable_rank > 0
ORDER BY id
LIMIT {int(limit)}
""".strip()


def _build_stratified_actual_sql(target_year: int, limit: int = 25) -> str:
    return f"""
SELECT
  opportunity_key,
  year,
  actual_rank,
  actual_score,
  school_id,
  school_name,
  major_code,
  major_name,
  opportunity_grain,
  province_id,
  province_name,
  subject_type,
  batch
FROM (
  SELECT
    {_opportunity_key_sql("t")} AS opportunity_key,
    t.year,
    t.stable_rank AS actual_rank,
    t.stable_score AS actual_score,
    t.school_id,
    t.school_name,
    t.major_code,
    t.major_name,
    {_opportunity_grain_sql("t")} AS opportunity_grain,
    t.province_id,
    t.province_name,
    {_subject_key_sql("t")} AS subject_type,
    {_batch_key_sql("t")} AS batch,
    ROW_NUMBER() OVER (
      PARTITION BY t.province_id, COALESCE({_subject_key_sql("t")}, ''), COALESCE({_batch_key_sql("t")}, '')
      ORDER BY t.id
    ) AS stratum_row_number
  FROM edu_school_admission_stats t
  WHERE t.deleted = 0
    AND t.year = {int(target_year)}
    AND t.stable_rank IS NOT NULL
    AND t.stable_rank > 0
    AND EXISTS (
      SELECT 1
      FROM edu_school_admission_stats h
      WHERE h.deleted = 0
        AND h.year < {int(target_year)}
        AND h.stable_rank IS NOT NULL
        AND h.stable_rank > 0
        AND h.school_id=t.school_id
        AND {_major_key_sql("h")}={_major_key_sql("t")}
        AND h.province_id=t.province_id
        AND COALESCE({_subject_key_sql("h")}, '')=COALESCE({_subject_key_sql("t")}, '')
        AND COALESCE({_batch_key_sql("h")}, '')=COALESCE({_batch_key_sql("t")}, '')
    )
) stratified_targets
WHERE stratum_row_number <= {int(limit)}
ORDER BY province_id, subject_type, batch, stratum_row_number
""".strip()


def build_history_sql(target_year: int) -> str:
    return f"""
SELECT
  {_opportunity_key_sql()} AS opportunity_key,
  year,
  stable_rank AS cutoff_rank,
  stable_score AS cutoff_score,
  plan_count
FROM edu_school_admission_stats
WHERE deleted = 0
  AND year < {int(target_year)}
  AND stable_rank IS NOT NULL
  AND stable_rank > 0
ORDER BY opportunity_key, year DESC
""".strip()


def build_score_rank_sql(target_year: int) -> str:
    return f"""
SELECT
  province_id,
  subject_type,
  score,
  lowest_rank
FROM edu_score_rank
WHERE deleted = 0
  AND year = {int(target_year)}
  AND lowest_rank IS NOT NULL
  AND lowest_rank > 0
ORDER BY province_id, subject_type, lowest_rank
""".strip()


@dataclass(frozen=True)
class DbConfig:
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    database: str = "gaokao_test_local"
    password: str | None = None

    @classmethod
    def from_env(cls) -> "DbConfig":
        load_env_file(Path(".env"), os.environ)
        return cls(
            host=os.environ.get("GAOKAO_DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("GAOKAO_DB_PORT", "3306")),
            user=os.environ.get("GAOKAO_DB_USER", "root"),
            database=os.environ.get("GAOKAO_DB_NAME", "gaokao_test_local"),
            password=os.environ.get("GAOKAO_DB_PASSWORD") or os.environ.get("MYSQL_PWD"),
        )


class MysqlCliClient:
    def __init__(self, config: DbConfig) -> None:
        self.config = config

    def query(self, sql: str) -> list[dict[str, str | None]]:
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
            "--batch",
            "-D",
            self.config.database,
            "-e",
            sql,
        ]
        result = subprocess.run(args, capture_output=True, env=env, check=False)
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        if result.returncode != 0:
            raise RuntimeError(stderr.strip() or "mysql query failed")
        return _parse_mysql_tsv(stdout)


def export_cases_from_env(
    target_year: int,
    limit: int = 500,
    sample_mode: str = "sequential",
) -> list[PredictionCase]:
    return export_cases(
        MysqlCliClient(DbConfig.from_env()),
        target_year=target_year,
        limit=limit,
        sample_mode=sample_mode,
    )


def export_cases(
    client: MysqlCliClient,
    target_year: int,
    limit: int = 500,
    sample_mode: str = "sequential",
) -> list[PredictionCase]:
    actual_rows = client.query(build_actual_sql(target_year=target_year, limit=limit, sample_mode=sample_mode))
    history_rows = client.query(build_history_sql(target_year=target_year))
    score_rank_rows = client.query(build_score_rank_sql(target_year=target_year))
    history_by_key: dict[str, list[AdmissionHistory]] = {}
    for row in history_rows:
        key = str(row["opportunity_key"])
        history_by_key.setdefault(key, []).append(
            AdmissionHistory(
                year=int(str(row["year"])),
                cutoff_rank=int(float(str(row["cutoff_rank"]))),
                cutoff_score=_optional_float(row.get("cutoff_score")),
                plan_count=_optional_int(row.get("plan_count")),
            )
        )
    score_points_by_group: dict[tuple[str | None, str | None], list[dict[str, int]]] = {}
    for row in score_rank_rows:
        group_key = (row.get("province_id"), row.get("subject_type"))
        score_points_by_group.setdefault(group_key, []).append(
            {
                "lowest_rank": int(float(str(row["lowest_rank"]))),
                "score": int(float(str(row["score"]))),
            }
        )

    cases: list[PredictionCase] = []
    for row in actual_rows:
        key = str(row["opportunity_key"])
        history = history_by_key.get(key, [])
        if not history:
            continue
        cases.append(
            PredictionCase(
                opportunity_key=key,
                target_year=target_year,
                actual_rank=int(float(str(row["actual_rank"]))),
                actual_score=_optional_float(row.get("actual_score")),
                history=history,
                metadata={
                    "school_id": row.get("school_id"),
                    "school_name": row.get("school_name"),
                    "major_code": row.get("major_code"),
                    "major_name": row.get("major_name"),
                    "opportunity_grain": row.get("opportunity_grain"),
                    "province_id": row.get("province_id"),
                    "province_name": row.get("province_name"),
                    "subject_type": row.get("subject_type"),
                    "batch": row.get("batch"),
                    "target_score_rank_points": score_points_by_group.get((row.get("province_id"), row.get("subject_type")), []),
                },
            )
        )
    return cases


def load_env_file(path: Path, environ: Any = os.environ) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if not key or key in environ:
            continue
        environ[key] = value.strip().strip('"').strip("'")


def _parse_mysql_tsv(text: str) -> list[dict[str, str | None]]:
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    lines = [line[:-1] if line.endswith("\r") else line for line in lines]
    rows = [line.split("\t") for line in lines]
    if not rows:
        return []
    headers = rows[0]
    parsed = []
    for row in rows[1:]:
        padded = row + [""] * max(0, len(headers) - len(row))
        parsed.append({header: _decode_cell(value) for header, value in zip(headers, padded[: len(headers)])})
    return parsed


def _decode_cell(value: str) -> str | None:
    if value == "NULL":
        return None
    return value.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").replace("\\\\", "\\")


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(float(value))
