"""Ingest official emerging-major and policy-evidence crawl outputs into MySQL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from major_intel.ingestion.emerging_major_candidates import build_unique_major_rows
from major_intel.ingestion.rysxai_data import DbConfig, MysqlCliRunner, build_insert_sql


EMERGING_MAJOR_CANDIDATE_TABLE = "official_emerging_major_candidates"
EMERGING_MAJOR_UNIQUE_TABLE = "official_emerging_major_unique_majors"
POLICY_DOCUMENT_TABLE = "policy_evidence_documents"
POLICY_MENTION_TABLE = "policy_direction_mentions"


def build_schema_sql() -> str:
    """Return idempotent DDL for official policy crawl outputs."""

    return f"""
CREATE TABLE IF NOT EXISTS {EMERGING_MAJOR_CANDIDATE_TABLE} (
  candidate_id VARCHAR(96) NOT NULL,
  major_code VARCHAR(32) NULL,
  major_name VARCHAR(200) NULL,
  major_level VARCHAR(50) NULL,
  discipline_category VARCHAR(100) NULL,
  major_class VARCHAR(100) NULL,
  degree VARCHAR(100) NULL,
  study_years VARCHAR(50) NULL,
  event_type VARCHAR(50) NULL,
  event_year INT NULL,
  candidate_status VARCHAR(50) NULL,
  source_title VARCHAR(500) NULL,
  source_url VARCHAR(800) NULL,
  attachment_url VARCHAR(800) NULL,
  source_level VARCHAR(10) NULL,
  evidence_text TEXT NULL,
  raw_path VARCHAR(800) NULL,
  parsed_from VARCHAR(50) NULL,
  captured_at VARCHAR(50) NULL,
  warnings_json JSON NULL,
  raw_candidate_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (candidate_id),
  KEY idx_emerging_major_code (major_code),
  KEY idx_emerging_major_name (major_name),
  KEY idx_emerging_event_year (event_year),
  KEY idx_emerging_event_status (event_type, candidate_status),
  KEY idx_emerging_source_level (source_level)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS {EMERGING_MAJOR_UNIQUE_TABLE} (
  major_key VARCHAR(260) NOT NULL,
  major_code VARCHAR(32) NULL,
  major_name VARCHAR(200) NULL,
  major_level VARCHAR(50) NULL,
  discipline_category VARCHAR(100) NULL,
  major_class VARCHAR(100) NULL,
  first_event_year INT NULL,
  latest_event_year INT NULL,
  event_types VARCHAR(255) NULL,
  candidate_statuses VARCHAR(255) NULL,
  source_levels VARCHAR(100) NULL,
  source_count INT NULL,
  attachment_count INT NULL,
  evidence_count INT NULL,
  first_source_title VARCHAR(500) NULL,
  first_source_url VARCHAR(800) NULL,
  sample_evidence_text TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (major_key),
  KEY idx_unique_major_code (major_code),
  KEY idx_unique_major_name (major_name),
  KEY idx_unique_years (first_event_year, latest_event_year),
  KEY idx_unique_event_types (event_types)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS {POLICY_DOCUMENT_TABLE} (
  doc_id VARCHAR(96) NOT NULL,
  source_id VARCHAR(160) NULL,
  title VARCHAR(500) NULL,
  url VARCHAR(800) NULL,
  source_domain VARCHAR(200) NULL,
  source_level VARCHAR(10) NULL,
  source_type VARCHAR(100) NULL,
  issuing_org VARCHAR(200) NULL,
  published_date VARCHAR(50) NULL,
  source_year INT NULL,
  text_length INT NULL,
  paragraph_count INT NULL,
  mention_count INT NULL,
  raw_path VARCHAR(800) NULL,
  captured_at VARCHAR(50) NULL,
  raw_document_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (doc_id),
  KEY idx_policy_source_id (source_id),
  KEY idx_policy_source_year (source_year),
  KEY idx_policy_source_type (source_type),
  KEY idx_policy_source_level (source_level)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS {POLICY_MENTION_TABLE} (
  mention_id VARCHAR(96) NOT NULL,
  doc_id VARCHAR(96) NOT NULL,
  source_id VARCHAR(160) NULL,
  source_title VARCHAR(500) NULL,
  source_url VARCHAR(800) NULL,
  source_level VARCHAR(10) NULL,
  source_type VARCHAR(100) NULL,
  source_year INT NULL,
  issuing_org VARCHAR(200) NULL,
  direction VARCHAR(100) NULL,
  keyword VARCHAR(100) NULL,
  paragraph_index INT NULL,
  evidence_text TEXT NULL,
  captured_at VARCHAR(50) NULL,
  raw_mention_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (mention_id),
  KEY idx_policy_mention_doc (doc_id),
  KEY idx_policy_direction (direction),
  KEY idx_policy_keyword (keyword),
  KEY idx_policy_mention_year (source_year),
  KEY idx_policy_mention_level (source_level)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
""".strip()


def candidate_record_to_row(record: dict[str, Any]) -> dict[str, Any]:
    candidate_id = _text(record.get("candidate_id"))
    if not candidate_id:
        raise ValueError("emerging-major candidate missing candidate_id")
    return {
        "candidate_id": candidate_id,
        "major_code": _text(record.get("major_code")),
        "major_name": _text(record.get("major_name")),
        "major_level": _text(record.get("major_level")),
        "discipline_category": _text(record.get("discipline_category")),
        "major_class": _text(record.get("major_class")),
        "degree": _text(record.get("degree")),
        "study_years": _text(record.get("study_years")),
        "event_type": _text(record.get("event_type")),
        "event_year": _to_int(record.get("event_year")),
        "candidate_status": _text(record.get("candidate_status")),
        "source_title": _text(record.get("source_title")),
        "source_url": _text(record.get("source_url")),
        "attachment_url": _text(record.get("attachment_url")),
        "source_level": _text(record.get("source_level")),
        "evidence_text": _text(record.get("evidence_text")),
        "raw_path": _text(record.get("raw_path")),
        "parsed_from": _text(record.get("parsed_from")),
        "captured_at": _text(record.get("captured_at")),
        "warnings_json": _json_text(record.get("warnings") or []),
        "raw_candidate_json": _json_text(record),
    }


def unique_major_record_to_row(record: dict[str, Any]) -> dict[str, Any]:
    major_key = _text(record.get("major_key"))
    if not major_key:
        raise ValueError("unique emerging-major row missing major_key")
    return {
        "major_key": major_key,
        "major_code": _text(record.get("major_code")),
        "major_name": _text(record.get("major_name")),
        "major_level": _text(record.get("major_level")),
        "discipline_category": _text(record.get("discipline_category")),
        "major_class": _text(record.get("major_class")),
        "first_event_year": _to_int(record.get("first_event_year")),
        "latest_event_year": _to_int(record.get("latest_event_year")),
        "event_types": _text(record.get("event_types")),
        "candidate_statuses": _text(record.get("candidate_statuses")),
        "source_levels": _text(record.get("source_levels")),
        "source_count": _to_int(record.get("source_count")),
        "attachment_count": _to_int(record.get("attachment_count")),
        "evidence_count": _to_int(record.get("evidence_count")),
        "first_source_title": _text(record.get("first_source_title")),
        "first_source_url": _text(record.get("first_source_url")),
        "sample_evidence_text": _text(record.get("sample_evidence_text")),
    }


def policy_document_record_to_row(record: dict[str, Any]) -> dict[str, Any]:
    doc_id = _text(record.get("doc_id"))
    if not doc_id:
        raise ValueError("policy document missing doc_id")
    return {
        "doc_id": doc_id,
        "source_id": _text(record.get("source_id")),
        "title": _text(record.get("title")),
        "url": _text(record.get("url")),
        "source_domain": _text(record.get("source_domain")),
        "source_level": _text(record.get("source_level")),
        "source_type": _text(record.get("source_type")),
        "issuing_org": _text(record.get("issuing_org")),
        "published_date": _text(record.get("published_date")),
        "source_year": _to_int(record.get("source_year")),
        "text_length": _to_int(record.get("text_length")),
        "paragraph_count": _to_int(record.get("paragraph_count")),
        "mention_count": _to_int(record.get("mention_count")),
        "raw_path": _text(record.get("raw_path")),
        "captured_at": _text(record.get("captured_at")),
        "raw_document_json": _json_text(record),
    }


def policy_mention_record_to_row(record: dict[str, Any]) -> dict[str, Any]:
    mention_id = _text(record.get("mention_id"))
    if not mention_id:
        raise ValueError("policy mention missing mention_id")
    return {
        "mention_id": mention_id,
        "doc_id": _text(record.get("doc_id")),
        "source_id": _text(record.get("source_id")),
        "source_title": _text(record.get("source_title")),
        "source_url": _text(record.get("source_url")),
        "source_level": _text(record.get("source_level")),
        "source_type": _text(record.get("source_type")),
        "source_year": _to_int(record.get("source_year")),
        "issuing_org": _text(record.get("issuing_org")),
        "direction": _text(record.get("direction")),
        "keyword": _text(record.get("keyword")),
        "paragraph_index": _to_int(record.get("paragraph_index")),
        "evidence_text": _text(record.get("evidence_text")),
        "captured_at": _text(record.get("captured_at")),
        "raw_mention_json": _json_text(record),
    }


def load_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows


def ingest_emerging_majors(
    runner: MysqlCliRunner,
    candidates_jsonl: Path,
    *,
    limit: int | None = None,
    chunk_size: int = 200,
) -> dict[str, int]:
    candidates = load_jsonl(candidates_jsonl, limit=limit)
    candidate_rows = [candidate_record_to_row(record) for record in candidates]
    unique_rows = [unique_major_record_to_row(record) for record in build_unique_major_rows(candidates)]

    for chunk in _chunks(candidate_rows, chunk_size):
        runner.run(build_insert_sql(EMERGING_MAJOR_CANDIDATE_TABLE, chunk, ["candidate_id"]))
    for chunk in _chunks(unique_rows, chunk_size):
        runner.run(build_insert_sql(EMERGING_MAJOR_UNIQUE_TABLE, chunk, ["major_key"]))

    return {"candidates": len(candidate_rows), "unique_majors": len(unique_rows)}


def ingest_policy_evidence(
    runner: MysqlCliRunner,
    *,
    documents_jsonl: Path,
    mentions_jsonl: Path,
    limit: int | None = None,
    chunk_size: int = 200,
) -> dict[str, int]:
    documents = load_jsonl(documents_jsonl, limit=limit)
    mentions = load_jsonl(mentions_jsonl, limit=limit)
    document_rows = [policy_document_record_to_row(record) for record in documents]
    mention_rows = [policy_mention_record_to_row(record) for record in mentions]

    for chunk in _chunks(document_rows, chunk_size):
        runner.run(build_insert_sql(POLICY_DOCUMENT_TABLE, chunk, ["doc_id"]))
    for chunk in _chunks(mention_rows, chunk_size):
        runner.run(build_insert_sql(POLICY_MENTION_TABLE, chunk, ["mention_id"]))

    return {"documents": len(document_rows), "mentions": len(mention_rows)}


def summarize(runner: MysqlCliRunner) -> str:
    return runner.run(
        f"""
SELECT '{EMERGING_MAJOR_CANDIDATE_TABLE}' AS table_name, COUNT(*) AS row_count FROM {EMERGING_MAJOR_CANDIDATE_TABLE}
UNION ALL
SELECT '{EMERGING_MAJOR_UNIQUE_TABLE}', COUNT(*) FROM {EMERGING_MAJOR_UNIQUE_TABLE}
UNION ALL
SELECT '{POLICY_DOCUMENT_TABLE}', COUNT(*) FROM {POLICY_DOCUMENT_TABLE}
UNION ALL
SELECT '{POLICY_MENTION_TABLE}', COUNT(*) FROM {POLICY_MENTION_TABLE};
""".strip(),
        capture_output=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest official emerging-major and policy evidence data into MySQL.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-schema", help="Create official policy crawl ingestion tables.")

    emerging_parser = subparsers.add_parser("ingest-emerging", help="Ingest emerging-major candidate JSONL.")
    emerging_parser.add_argument(
        "--candidates-jsonl",
        type=Path,
        default=Path("data/processed/policy_documents/emerging_major_candidates_emerging_major_seed_20260612_v5.jsonl"),
    )
    emerging_parser.add_argument("--limit", type=int)
    emerging_parser.add_argument("--chunk-size", type=int, default=200)

    policy_parser = subparsers.add_parser("ingest-policy", help="Ingest policy evidence document and mention JSONL.")
    policy_parser.add_argument(
        "--documents-jsonl",
        type=Path,
        default=Path("data/processed/policy_evidence/policy_documents_policy_evidence_seed_20260612_v5.jsonl"),
    )
    policy_parser.add_argument(
        "--mentions-jsonl",
        type=Path,
        default=Path("data/processed/policy_evidence/policy_mentions_policy_evidence_seed_20260612_v5.jsonl"),
    )
    policy_parser.add_argument("--limit", type=int)
    policy_parser.add_argument("--chunk-size", type=int, default=200)

    subparsers.add_parser("summarize", help="Show official policy crawl table counts.")

    args = parser.parse_args(argv)
    runner = MysqlCliRunner(DbConfig.from_env())

    if args.command == "init-schema":
        runner.run(build_schema_sql())
        print("schema initialized")
        return 0
    if args.command == "ingest-emerging":
        stats = ingest_emerging_majors(
            runner,
            args.candidates_jsonl,
            limit=args.limit,
            chunk_size=args.chunk_size,
        )
        print(json.dumps(stats, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "ingest-policy":
        stats = ingest_policy_evidence(
            runner,
            documents_jsonl=args.documents_jsonl,
            mentions_jsonl=args.mentions_jsonl,
            limit=args.limit,
            chunk_size=args.chunk_size,
        )
        print(json.dumps(stats, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "summarize":
        print(summarize(runner), end="")
        return 0

    raise ValueError(f"Unknown command: {args.command}")


def _chunks(rows: list[dict[str, Any]], chunk_size: int) -> Iterable[list[dict[str, Any]]]:
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    for index in range(0, len(rows), chunk_size):
        yield rows[index : index + chunk_size]


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    raise SystemExit(main())
