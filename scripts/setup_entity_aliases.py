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


SCHOOL_ALIAS_SEEDS = [
    ("杭电", "杭州电子科技大学", "10336", "manual_seed", 1.000),
    ("HDU", "杭州电子科技大学", "10336", "manual_seed", 0.950),
    ("浙大", "浙江大学", "10335", "manual_seed", 1.000),
    ("ZJU", "浙江大学", "10335", "manual_seed", 0.950),
    ("紫金港职业技术学院", "浙江大学", "10335", "manual_seed", 0.800),
    ("浙工大", "浙江工业大学", "10337", "manual_seed", 1.000),
    ("北大", "北京大学", "10001", "manual_seed", 1.000),
    ("P大", "北京大学", "10001", "manual_seed", 0.900),
    ("PKU", "北京大学", "10001", "manual_seed", 0.950),
    ("清华", "清华大学", "10003", "manual_seed", 1.000),
    ("THU", "清华大学", "10003", "manual_seed", 0.950),
    ("五道口职业技术学院", "清华大学", "10003", "manual_seed", 0.800),
    ("人大", "中国人民大学", "10002", "manual_seed", 0.950),
    ("RUC", "中国人民大学", "10002", "manual_seed", 0.950),
    ("北航", "北京航空航天大学", "10006", "manual_seed", 1.000),
    ("BUAA", "北京航空航天大学", "10006", "manual_seed", 0.950),
    ("北理", "北京理工大学", "10007", "manual_seed", 0.950),
    ("北理工", "北京理工大学", "10007", "manual_seed", 1.000),
    ("BIT", "北京理工大学", "10007", "manual_seed", 0.950),
    ("北工大", "北京工业大学", "10005", "manual_seed", 1.000),
    ("北邮", "北京邮电大学", "10013", "manual_seed", 1.000),
    ("BUPT", "北京邮电大学", "10013", "manual_seed", 0.950),
    ("北交大", "北京交通大学", "10004", "manual_seed", 1.000),
    ("交大", "北京交通大学", "10004", "manual_seed", 0.600),
    ("北师大", "北京师范大学", "10027", "manual_seed", 1.000),
    ("BNU", "北京师范大学", "10027", "manual_seed", 0.950),
    ("北外", "北京外国语大学", "10030", "manual_seed", 1.000),
    ("央财", "中央财经大学", "10034", "manual_seed", 1.000),
    ("南开", "南开大学", "10055", "manual_seed", 1.000),
    ("NKU", "南开大学", "10055", "manual_seed", 0.950),
    ("天大", "天津大学", "10056", "manual_seed", 0.950),
    ("哈工大", "哈尔滨工业大学", "10213", "manual_seed", 1.000),
    ("哈工", "哈尔滨工业大学", "10213", "manual_seed", 0.850),
    ("HIT", "哈尔滨工业大学", "10213", "manual_seed", 0.950),
    ("吉大", "吉林大学", "10183", "manual_seed", 1.000),
    ("JLU", "吉林大学", "10183", "manual_seed", 0.950),
    ("大工", "大连理工大学", "10141", "manual_seed", 1.000),
    ("DUT", "大连理工大学", "10141", "manual_seed", 0.950),
    ("复旦", "复旦大学", "10246", "manual_seed", 1.000),
    ("FDU", "复旦大学", "10246", "manual_seed", 0.950),
    ("同济", "同济大学", "10247", "manual_seed", 1.000),
    ("上交", "上海交通大学", "10248", "manual_seed", 1.000),
    ("交大", "上海交通大学", "10248", "manual_seed", 0.700),
    ("SJTU", "上海交通大学", "10248", "manual_seed", 0.950),
    ("华工", "华东理工大学", "10251", "manual_seed", 0.600),
    ("华东师大", "华东师范大学", "10269", "manual_seed", 1.000),
    ("华师", "华东师范大学", "10269", "manual_seed", 0.650),
    ("ECNU", "华东师范大学", "10269", "manual_seed", 0.950),
    ("上外", "上海外国语大学", "10271", "manual_seed", 1.000),
    ("上财", "上海财经大学", "10272", "manual_seed", 1.000),
    ("NJU", "南京大学", "10284", "manual_seed", 0.950),
    ("南大", "南京大学", "10284", "manual_seed", 0.700),
    ("九乡河文理学院", "南京大学", "10284", "manual_seed", 0.800),
    ("东南", "东南大学", "10286", "manual_seed", 0.950),
    ("SEU", "东南大学", "10286", "manual_seed", 0.950),
    ("南航", "南京航空航天大学", "10287", "manual_seed", 1.000),
    ("NUAA", "南京航空航天大学", "10287", "manual_seed", 0.950),
    ("南理工", "南京理工大学", "10288", "manual_seed", 1.000),
    ("NJUST", "南京理工大学", "10288", "manual_seed", 0.950),
    ("南邮", "南京邮电大学", "10293", "manual_seed", 1.000),
    ("南师大", "南京师范大学", "10319", "manual_seed", 1.000),
    ("中科大", "中国科学技术大学", "10358", "manual_seed", 1.000),
    ("USTC", "中国科学技术大学", "10358", "manual_seed", 0.950),
    ("南七技校", "中国科学技术大学", "10358", "manual_seed", 0.800),
    ("南大", "南昌大学", "10403", "manual_seed", 0.600),
    ("厦大", "厦门大学", "10384", "manual_seed", 1.000),
    ("XMU", "厦门大学", "10384", "manual_seed", 0.950),
    ("山大", "山东大学", "10422", "manual_seed", 0.700),
    ("河大", "河南大学", "10475", "manual_seed", 0.650),
    ("武大", "武汉大学", "10486", "manual_seed", 1.000),
    ("WHU", "武汉大学", "10486", "manual_seed", 0.950),
    ("珞珈山职业技术学院", "武汉大学", "10486", "manual_seed", 0.800),
    ("华科", "华中科技大学", "10487", "manual_seed", 1.000),
    ("HUST", "华中科技大学", "10487", "manual_seed", 0.950),
    ("关山口职业技术学院", "华中科技大学", "10487", "manual_seed", 0.800),
    ("马房山男子职业技术学院", "武汉理工大学", "10497", "manual_seed", 0.750),
    ("湖大", "湖北大学", "10512", "manual_seed", 0.600),
    ("华中师大", "华中师范大学", "10511", "manual_seed", 1.000),
    ("华师", "华中师范大学", "10511", "manual_seed", 0.650),
    ("CCNU", "华中师范大学", "10511", "manual_seed", 0.950),
    ("河大", "河北大学", "10075", "manual_seed", 0.650),
    ("湖大", "湖南大学", "10532", "manual_seed", 0.700),
    ("中大", "中南大学", "10533", "manual_seed", 0.600),
    ("SYSU", "中山大学", "10558", "manual_seed", 0.950),
    ("双鸭山大学", "中山大学", "10558", "manual_seed", 0.800),
    ("中大", "中山大学", "10558", "manual_seed", 0.700),
    ("暨大", "暨南大学", "10559", "manual_seed", 1.000),
    ("华工", "华南理工大学", "10561", "manual_seed", 0.700),
    ("华南师大", "华南师范大学", "10574", "manual_seed", 1.000),
    ("华师", "华南师范大学", "10574", "manual_seed", 0.650),
    ("山大", "山西大学", "10108", "manual_seed", 0.600),
    ("川大", "四川大学", "10610", "manual_seed", 1.000),
    ("成电", "电子科技大学", "10614", "manual_seed", 1.000),
    ("UESTC", "电子科技大学", "10614", "manual_seed", 0.950),
    ("重邮", "重庆邮电大学", "10617", "manual_seed", 1.000),
    ("西南交大", "西南交通大学", "10613", "manual_seed", 1.000),
    ("交大", "西南交通大学", "10613", "manual_seed", 0.600),
    ("SWJTU", "西南交通大学", "10613", "manual_seed", 0.950),
    ("西财", "西南财经大学", "10651", "manual_seed", 1.000),
    ("西交", "西安交通大学", "10698", "manual_seed", 0.950),
    ("西交大", "西安交通大学", "10698", "manual_seed", 1.000),
    ("交大", "西安交通大学", "10698", "manual_seed", 0.700),
    ("XJTU", "西安交通大学", "10698", "manual_seed", 0.950),
    ("西工大", "西北工业大学", "10699", "manual_seed", 1.000),
    ("NPU", "西北工业大学", "10699", "manual_seed", 0.950),
    ("西电", "西安电子科技大学", "10701", "manual_seed", 1.000),
    ("XDU", "西安电子科技大学", "10701", "manual_seed", 0.950),
    ("南科大", "南方科技大学", "14325", "manual_seed", 1.000),
    ("国科大", "中国科学院大学", "14430", "manual_seed", 1.000),
]


def normalize_alias(value: Any) -> str:
    return "".join(str(value or "").split()).lower()


def build_major_alias_seed_sql() -> str:
    return build_alias_seed_sql("major", MAJOR_ALIAS_SEEDS)


def build_school_alias_seed_sql() -> str:
    return build_alias_seed_sql("school", SCHOOL_ALIAS_SEEDS)


def build_alias_seed_sql(entity_type: str, seeds: list[tuple[str, str, str, str, float]]) -> str:
    """Build an idempotent seed statement for confirmed aliases.

    The same table stores school and major aliases, so the SQL builder is shared
    while each seed list stays separate and reviewable.  `ON DUPLICATE KEY`
    lets us safely re-run the script after adding aliases without creating
    duplicate rows or leaving old confidence/status values behind.
    """

    values = []
    for alias_text, canonical_name, canonical_code, source, confidence in seeds:
        values.append(
            "("
            f"{sql_quote(entity_type)}, "
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
    client.query(build_school_alias_seed_sql())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create and seed local entity alias tables.")
    parser.parse_args(argv)

    setup_entity_aliases(MysqlCliClient(DbConfig.from_env()))
    print("entity_aliases ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
