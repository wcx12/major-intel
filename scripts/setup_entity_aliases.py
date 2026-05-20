"""Create and seed local entity alias tables.

The retrieval layer should not need a code change every time a counselor or
operator confirms a new school / major nickname.  This script creates the first
database-backed alias tables and seeds high-confidence major aliases that were
previously hard-coded in Python.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.local_retrieval_mvp import DbConfig, MysqlCliClient, sql_quote


ENTITY_ALIAS_SCHEMA_SQL = [
    """
CREATE TABLE IF NOT EXISTS entity_aliases (
  id BIGINT NOT NULL AUTO_INCREMENT,
  entity_type VARCHAR(32) NOT NULL,
  alias_text VARCHAR(255) NOT NULL,
  alias_normalized VARCHAR(255) NOT NULL,
  canonical_name VARCHAR(255) NOT NULL,
  canonical_code VARCHAR(64) NOT NULL DEFAULT '',
  source VARCHAR(64) NOT NULL DEFAULT 'manual_seed',
  confidence DECIMAL(4,3) NOT NULL DEFAULT 1.000,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted BIT(1) NOT NULL DEFAULT b'0',
  PRIMARY KEY (id),
  UNIQUE KEY uk_entity_alias (entity_type, alias_normalized, canonical_name, canonical_code),
  KEY idx_entity_alias_lookup (entity_type, alias_normalized, status, deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
""".strip(),
    "ALTER TABLE entity_aliases CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci",
    """
CREATE TABLE IF NOT EXISTS entity_alias_candidates (
  id BIGINT NOT NULL AUTO_INCREMENT,
  entity_type VARCHAR(32) NOT NULL,
  alias_text VARCHAR(255) NOT NULL,
  alias_normalized VARCHAR(255) NOT NULL,
  candidate_name VARCHAR(255) NOT NULL DEFAULT '',
  candidate_code VARCHAR(64) NOT NULL DEFAULT '',
  evidence TEXT NULL,
  hit_count INT NOT NULL DEFAULT 1,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted BIT(1) NOT NULL DEFAULT b'0',
  PRIMARY KEY (id),
  UNIQUE KEY uk_entity_alias_candidate (entity_type, alias_normalized, candidate_name, candidate_code),
  KEY idx_entity_alias_candidate_status (entity_type, status, deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
""".strip(),
    "ALTER TABLE entity_alias_candidates CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci",
]


MAJOR_ALIAS_SEEDS = [
    ("计科", "计算机科学与技术", "080901", "manual_seed", 1.000),
    ("软工", "软件工程", "080902", "manual_seed", 1.000),
    ("软件", "软件工程", "080902", "manual_seed", 0.950),
    ("大数据", "数据科学与大数据技术", "080910T", "manual_seed", 0.950),
    ("数科", "数据科学与大数据技术", "080910T", "manual_seed", 0.900),
    ("电信", "电子信息工程", "080701", "manual_seed", 0.850),
    ("电信", "通信工程", "080703", "manual_seed", 0.750),
    ("电子信息", "电子信息工程", "080701", "manual_seed", 0.950),
    ("通信", "通信工程", "080703", "manual_seed", 0.950),
    ("电气", "电气工程及其自动化", "080601", "manual_seed", 0.950),
    ("自动化", "自动化", "080801", "manual_seed", 1.000),
    ("临床", "临床医学", "100201K", "manual_seed", 0.950),
    ("口腔", "口腔医学", "100301K", "manual_seed", 0.950),
    ("会计", "会计学", "120203K", "manual_seed", 0.950),
    ("金融", "金融学", "020301K", "manual_seed", 0.950),
]


def normalize_alias(value: Any) -> str:
    return "".join(str(value or "").split()).lower()


def build_major_alias_seed_sql() -> str:
    values = []
    for alias_text, canonical_name, canonical_code, source, confidence in MAJOR_ALIAS_SEEDS:
        values.append(
            "("
            "'major', "
            f"{sql_quote(alias_text)}, "
            f"{sql_quote(normalize_alias(alias_text))}, "
            f"{sql_quote(canonical_name)}, "
            f"{sql_quote(canonical_code)}, "
            f"{sql_quote(source)}, "
            f"{confidence:.3f}, "
            "'active'"
            ")"
        )

    return f"""
INSERT INTO entity_aliases (
  entity_type, alias_text, alias_normalized, canonical_name, canonical_code,
  source, confidence, status
)
VALUES
  {', '.join(values)}
ON DUPLICATE KEY UPDATE
  alias_text = VALUES(alias_text),
  source = VALUES(source),
  confidence = VALUES(confidence),
  status = VALUES(status),
  deleted = b'0',
  update_time = CURRENT_TIMESTAMP
""".strip()


def setup_entity_aliases(client: MysqlCliClient) -> None:
    for statement in ENTITY_ALIAS_SCHEMA_SQL:
        client.query(statement)
    client.query(build_major_alias_seed_sql())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create and seed local entity alias tables.")
    parser.parse_args(argv)

    setup_entity_aliases(MysqlCliClient(DbConfig.from_env()))
    print("entity_aliases ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
