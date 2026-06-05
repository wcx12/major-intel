"""MySQL-backed query logging and cache storage for the retrieval agent.

This module is intentionally separate from `retrieval_tools.py`.  Retrieval
tools should keep owning facts and SQL reads, while this layer owns operational
state: user questions, selected route, tool traces, and reusable answer cache.
That separation makes it easier to later add data-gap queues and human review
without turning every retrieval function into a logging function.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from major_intel.storage.local_retrieval_mvp import DbConfig, MysqlCliClient, sql_quote


CACHE_VERSION = "agent-cache-v1"
DATA_GAP_QUEUE_VERSION = "data-gap-v1"
DATA_GAP_EVIDENCE_TASK_VERSION = "data-gap-evidence-task-v1"

# These statuses mean the retrieval layer did not have enough local evidence to
# answer.  Even if a tool forgets to populate `data_gaps`, we still create a
# queue item so the missing evidence can be investigated instead of silently
# disappearing from operations.
DATA_GAP_STATUSES = {"not_found", "data_gap"}

# The first queue version is intentionally conservative: official pages and
# admissions/employment documents should be tried before open web summaries.
DEFAULT_SOURCE_CONSTRAINTS = {
    "preferred_sources": ["学校官网", "招生章程", "就业质量报告", "教育部/考试院公开数据"],
    "forbidden_behavior": "本地库和可信来源都没有证据时，不允许编造结论，转人工处理。",
}


def build_agent_storage_schema_sql() -> str:
    """Return idempotent DDL for query logs, answer cache, traces, and gaps."""

    return """
CREATE TABLE IF NOT EXISTS query_logs (
  id CHAR(32) NOT NULL,
  session_id VARCHAR(128) NULL,
  question_hash CHAR(64) NOT NULL,
  question_text MEDIUMTEXT NOT NULL,
  mode VARCHAR(32) NOT NULL,
  route VARCHAR(32) NOT NULL,
  cache_key CHAR(64) NULL,
  cache_hit TINYINT(1) NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL,
  intent VARCHAR(128) NULL,
  slots_json JSON NULL,
  tool_plan_json JSON NULL,
  tool_trace_json JSON NULL,
  rule_preflight_json JSON NULL,
  data_gaps_json JSON NULL,
  warnings_json JSON NULL,
  scope_notes_json JSON NULL,
  answer_markdown MEDIUMTEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_query_logs_session_created (session_id, created_at),
  KEY idx_query_logs_question_hash (question_hash),
  KEY idx_query_logs_cache_key (cache_key),
  KEY idx_query_logs_status_intent (status, intent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS retrieval_cache (
  cache_key CHAR(64) NOT NULL,
  cache_key_source_json JSON NOT NULL,
  mode VARCHAR(32) NOT NULL,
  route VARCHAR(32) NOT NULL,
  intent VARCHAR(128) NULL,
  status VARCHAR(32) NOT NULL,
  slots_json JSON NULL,
  tool_plan_json JSON NULL,
  result_json JSON NOT NULL,
  result_text LONGTEXT NULL,
  expires_at DATETIME NULL,
  hit_count INT NOT NULL DEFAULT 0,
  last_hit_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (cache_key),
  KEY idx_retrieval_cache_route_intent (route, intent),
  KEY idx_retrieval_cache_status (status),
  KEY idx_retrieval_cache_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS agent_tool_traces (
  id BIGINT NOT NULL AUTO_INCREMENT,
  query_log_id CHAR(32) NOT NULL,
  tool_order INT NOT NULL,
  tool_name VARCHAR(128) NOT NULL,
  arguments_json JSON NULL,
  result_status VARCHAR(32) NULL,
  result_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_agent_tool_traces_log_order (query_log_id, tool_order),
  KEY idx_agent_tool_traces_tool_name (tool_name),
  CONSTRAINT fk_agent_tool_traces_query_log
    FOREIGN KEY (query_log_id) REFERENCES query_logs(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS data_gap_queue (
  id CHAR(32) NOT NULL,
  gap_key CHAR(64) NOT NULL,
  query_log_id CHAR(32) NULL,
  session_id VARCHAR(128) NULL,
  question_type VARCHAR(128) NOT NULL,
  school_text VARCHAR(255) NULL,
  major_text VARCHAR(255) NULL,
  province VARCHAR(100) NULL,
  subject_type VARCHAR(50) NULL,
  year INT NULL,
  batch VARCHAR(100) NULL,
  missing_fields_json JSON NOT NULL,
  available_fields_json JSON NULL,
  user_question MEDIUMTEXT NOT NULL,
  normalized_question MEDIUMTEXT NULL,
  priority TINYINT NOT NULL DEFAULT 2,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  confidence_level VARCHAR(32) NOT NULL DEFAULT 'low',
  reason MEDIUMTEXT NULL,
  source_constraints_json JSON NULL,
  expected_outputs_json JSON NULL,
  hit_count INT NOT NULL DEFAULT 1,
  first_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  resolved_at DATETIME NULL,
  reviewer VARCHAR(128) NULL,
  review_note MEDIUMTEXT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_data_gap_queue_gap_key (gap_key),
  KEY idx_data_gap_queue_status_priority (status, priority, updated_at),
  KEY idx_data_gap_queue_question_type (question_type),
  KEY idx_data_gap_queue_session (session_id),
  CONSTRAINT fk_data_gap_queue_query_log
    FOREIGN KEY (query_log_id) REFERENCES query_logs(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS source_documents (
  id CHAR(32) NOT NULL,
  source_key CHAR(64) NOT NULL,
  source_type VARCHAR(64) NOT NULL,
  source_url TEXT NULL,
  title VARCHAR(512) NULL,
  publisher VARCHAR(255) NULL,
  publish_date DATE NULL,
  fetched_at DATETIME NULL,
  content_hash CHAR(64) NULL,
  raw_text LONGTEXT NULL,
  metadata_json JSON NULL,
  credibility_level VARCHAR(32) NOT NULL DEFAULT 'unverified',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_source_documents_source_key (source_key),
  KEY idx_source_documents_source_type (source_type),
  KEY idx_source_documents_credibility (credibility_level),
  KEY idx_source_documents_content_hash (content_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS data_gap_evidence_tasks (
  id CHAR(32) NOT NULL,
  task_key CHAR(64) NOT NULL,
  gap_id CHAR(32) NOT NULL,
  gap_key CHAR(64) NOT NULL,
  question_type VARCHAR(128) NOT NULL,
  search_query VARCHAR(512) NOT NULL,
  preferred_sources_json JSON NULL,
  expected_outputs_json JSON NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'ready',
  priority TINYINT NOT NULL DEFAULT 2,
  attempt_count INT NOT NULL DEFAULT 0,
  last_error MEDIUMTEXT NULL,
  result_document_id CHAR(32) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  started_at DATETIME NULL,
  completed_at DATETIME NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_data_gap_evidence_tasks_task_key (task_key),
  KEY idx_data_gap_evidence_tasks_status_priority (status, priority, updated_at),
  KEY idx_data_gap_evidence_tasks_gap_key (gap_key),
  CONSTRAINT fk_data_gap_evidence_tasks_gap
    FOREIGN KEY (gap_id) REFERENCES data_gap_queue(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_data_gap_evidence_tasks_source_document
    FOREIGN KEY (result_document_id) REFERENCES source_documents(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip()


def build_cache_identity(
    *,
    question: str,
    mode: str,
    route: str,
    intent: str | None,
    slots: dict[str, Any] | None,
    tool_plan: list[dict[str, Any]] | None,
) -> tuple[str, dict[str, Any]]:
    """Build a stable cache key and its human-readable source payload.

    The cache should be based on normalized retrieval meaning, not raw text
    alone.  The raw question is still included after whitespace normalization so
    purely conversational DeepSeek questions can be cached before entity
    normalization exists.
    """

    source = {
        "version": CACHE_VERSION,
        "question": " ".join(str(question or "").split()),
        "mode": mode,
        "route": route,
        "intent": intent,
        "slots": slots or {},
        "tool_plan": tool_plan or [],
    }
    encoded = _json_dumps(source)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest(), source


def build_data_gap_items(
    *,
    question: str,
    mode: str,
    result: dict[str, Any],
    query_log_id: str | None = None,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    """Convert one retrieval envelope into queue rows for missing data.

    这个函数只做“缺口识别和规范化”，不直接访问数据库。这样单元测试可以稳定
    验证 gap_key、优先级、槽位抽取等规则，真正的 MySQL 写入则交给
    `MysqlAgentQueryStorage.write_data_gap_items()`。
    """

    if not isinstance(result, dict):
        return []

    missing_fields = _unique_texts(result.get("data_gaps") or [])
    status = str(result.get("status") or "")
    if not missing_fields and status in DATA_GAP_STATUSES:
        missing_fields = ["本地库未命中关键数据"]
    if not missing_fields:
        return []

    slots = _merged_gap_slots(result)
    question_type = _first_non_empty(result.get("intent"), slots.get("intent"), result.get("route"), "unknown")
    normalized_question = " ".join(str(question or "").split())
    year = _coerce_int(_first_non_empty(slots.get("year"), result.get("year")))

    # gap_key deliberately ignores warnings, query_log_id, and session_id.
    # Those values change between runs, while the actual missing evidence has
    # not changed.  This keeps repeated student questions deduplicated.
    gap_key_source = {
        "version": DATA_GAP_QUEUE_VERSION,
        "mode": mode,
        "question_type": question_type,
        "school_text": _slot_text(slots, "school_text", "school_name", "university_name"),
        "major_text": _slot_text(slots, "major_text", "major_name", "special_name"),
        "province": _slot_text(slots, "province", "province_name"),
        "subject_type": _slot_text(slots, "subject_type", "subject"),
        "year": year,
        "batch": _slot_text(slots, "batch", "batch_name"),
        "missing_fields": missing_fields,
    }
    gap_key = hashlib.sha256(_json_dumps(gap_key_source).encode("utf-8")).hexdigest()

    item = {
        "id": uuid.uuid4().hex,
        "gap_key": gap_key,
        "query_log_id": query_log_id,
        "session_id": session_id,
        "question_type": question_type,
        "school_text": gap_key_source["school_text"],
        "major_text": gap_key_source["major_text"],
        "province": gap_key_source["province"],
        "subject_type": gap_key_source["subject_type"],
        "year": year,
        "batch": gap_key_source["batch"],
        "missing_fields": missing_fields,
        "available_fields": _available_gap_fields(result),
        "user_question": str(question or ""),
        "normalized_question": normalized_question,
        "priority": _gap_priority(status=status, missing_fields=missing_fields),
        "status": "pending",
        "confidence_level": "low",
        "reason": _gap_reason(result),
        "source_constraints": DEFAULT_SOURCE_CONSTRAINTS,
        "expected_outputs": {
            "missing_fields": missing_fields,
            "write_targets": ["source_documents", "fact_tables_or_manual_review"],
        },
    }
    return [item]


def build_evidence_tasks(gap_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert queue rows into local source-discovery tasks.

    This is the first non-network step of dynamic RAG.  It turns "what is
    missing" into "what should the next agent search for" while keeping the
    result fully deterministic and easy to review in tests.
    """

    tasks: list[dict[str, Any]] = []
    for gap_item in gap_items:
        task = build_evidence_task(gap_item)
        if task:
            tasks.append(task)
    return tasks


def build_evidence_task(gap_item: dict[str, Any]) -> dict[str, Any] | None:
    """Build one evidence task for a `data_gap_queue` row.

    A single first-version task is enough because the downstream search agent
    can fan out by preferred source.  The stable `task_key` prevents duplicate
    tasks when the same data gap is seen repeatedly.
    """

    gap_id = str(gap_item.get("id") or "").strip()
    gap_key = str(gap_item.get("gap_key") or "").strip()
    if not gap_id or not gap_key:
        return None

    missing_fields = _unique_texts(gap_item.get("missing_fields") or [])
    search_query = _build_gap_search_query(gap_item, missing_fields)
    preferred_sources = _preferred_sources_for_gap(gap_item, missing_fields)
    expected_outputs = gap_item.get("expected_outputs") or {
        "missing_fields": missing_fields,
        "write_targets": ["source_documents", "fact_tables_or_manual_review"],
    }
    task_key_source = {
        "version": DATA_GAP_EVIDENCE_TASK_VERSION,
        "gap_key": gap_key,
        "search_query": search_query,
        "expected_outputs": expected_outputs,
    }
    task_key = hashlib.sha256(_json_dumps(task_key_source).encode("utf-8")).hexdigest()

    return {
        "id": uuid.uuid4().hex,
        "task_key": task_key,
        "gap_id": gap_id,
        "gap_key": gap_key,
        "question_type": str(gap_item.get("question_type") or "unknown"),
        "search_query": search_query,
        "preferred_sources": preferred_sources,
        "expected_outputs": expected_outputs,
        "status": "ready",
        "priority": _coerce_int(gap_item.get("priority")) or 2,
    }


class MysqlAgentQueryStorage:
    """Persist agent query logs, cache entries, and tool traces through mysql CLI."""

    def __init__(self, config: DbConfig | None = None) -> None:
        self.config = config or DbConfig.from_env()
        self.reader = MysqlCliClient(self.config)

    def setup_schema(self) -> None:
        """Create the storage tables if they do not already exist."""

        self.execute(build_agent_storage_schema_sql())
        try:
            self.execute("ALTER TABLE retrieval_cache ADD COLUMN result_text LONGTEXT NULL AFTER result_json")
        except RuntimeError as exc:
            if "Duplicate column" not in str(exc) and "1060" not in str(exc):
                raise

    def get_cached_result(self, cache_key: str) -> dict[str, Any] | None:
        """Return a cached agent envelope and update hit metadata if it exists."""

        rows = self.reader.query(
            f"""
SELECT TO_BASE64(COALESCE(result_text, CAST(result_json AS CHAR CHARACTER SET utf8mb4))) AS result_text_b64
FROM retrieval_cache
WHERE cache_key = {sql_quote(cache_key)}
  AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
LIMIT 1
""".strip()
        )
        if not rows:
            return None

        self.execute(
            f"""
UPDATE retrieval_cache
SET hit_count = hit_count + 1,
    last_hit_at = CURRENT_TIMESTAMP
WHERE cache_key = {sql_quote(cache_key)}
""".strip()
        )
        return _json_loads(_decode_base64_text(rows[0].get("result_text_b64")), default=None)

    def save_cached_result(
        self,
        cache_key: str,
        cache_source: dict[str, Any],
        result: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        """Upsert a reusable result envelope into `retrieval_cache`."""

        expires_sql = "NULL" if ttl_seconds is None else f"DATE_ADD(CURRENT_TIMESTAMP, INTERVAL {int(ttl_seconds)} SECOND)"
        sql = f"""
INSERT INTO retrieval_cache (
  cache_key, cache_key_source_json, mode, route, intent, status,
  slots_json, tool_plan_json, result_json, result_text, expires_at
) VALUES (
  {sql_quote(cache_key)},
  {_json_sql(cache_source)},
  {sql_quote(str(cache_source.get("mode") or ""))},
  {sql_quote(str(cache_source.get("route") or ""))},
  {sql_quote(cache_source.get("intent"))},
  {sql_quote(str(result.get("status") or ""))},
  {_json_sql(result.get("slots") or {})},
  {_json_sql(result.get("tool_plan") or [])},
  {_json_sql(result)},
  {sql_quote(_json_dumps(result))},
  {expires_sql}
)
ON DUPLICATE KEY UPDATE
  cache_key_source_json = VALUES(cache_key_source_json),
  mode = VALUES(mode),
  route = VALUES(route),
  intent = VALUES(intent),
  status = VALUES(status),
  slots_json = VALUES(slots_json),
  tool_plan_json = VALUES(tool_plan_json),
  result_json = VALUES(result_json),
  result_text = VALUES(result_text),
  expires_at = VALUES(expires_at),
  updated_at = CURRENT_TIMESTAMP
""".strip()
        self.execute(sql)

    def write_query_log(self, record: dict[str, Any]) -> str:
        """Insert one query log row and return its generated id."""

        query_log_id = str(record.get("id") or uuid.uuid4().hex)
        question_text = str(record.get("question_text") or "")
        question_hash = hashlib.sha256(question_text.encode("utf-8")).hexdigest()
        result = record.get("result") or {}

        sql = f"""
INSERT INTO query_logs (
  id, session_id, question_hash, question_text, mode, route, cache_key,
  cache_hit, status, intent, slots_json, tool_plan_json, tool_trace_json,
  rule_preflight_json, data_gaps_json, warnings_json, scope_notes_json,
  answer_markdown
) VALUES (
  {sql_quote(query_log_id)},
  {sql_quote(record.get("session_id"))},
  {sql_quote(question_hash)},
  {sql_quote(question_text)},
  {sql_quote(str(record.get("mode") or ""))},
  {sql_quote(str(record.get("route") or ""))},
  {sql_quote(record.get("cache_key"))},
  {1 if record.get("cache_hit") else 0},
  {sql_quote(str(result.get("status") or ""))},
  {sql_quote(result.get("intent"))},
  {_json_sql(result.get("slots") or {})},
  {_json_sql(result.get("tool_plan") or [])},
  {_json_sql(result.get("tool_trace") or [])},
  {_json_sql(result.get("rule_preflight"))},
  {_json_sql(result.get("data_gaps") or [])},
  {_json_sql(result.get("warnings") or [])},
  {_json_sql(result.get("scope_notes") or [])},
  {sql_quote(result.get("answer_markdown"))}
)
""".strip()
        self.execute(sql)
        return query_log_id

    def write_tool_traces(self, query_log_id: str, tool_trace: list[dict[str, Any]]) -> None:
        """Insert expanded tool trace rows for easier later inspection."""

        if not tool_trace:
            return

        values = []
        for index, trace in enumerate(tool_trace):
            result = trace.get("result") if isinstance(trace, dict) else {}
            result = result if isinstance(result, dict) else {}
            values.append(
                "("
                f"{sql_quote(query_log_id)}, "
                f"{index}, "
                f"{sql_quote(str(trace.get('tool_name') or ''))}, "
                f"{_json_sql(trace.get('arguments') or {})}, "
                f"{sql_quote(result.get('status'))}, "
                f"{_json_sql(result)}"
                ")"
            )

        self.execute(
            """
INSERT INTO agent_tool_traces (
  query_log_id, tool_order, tool_name, arguments_json, result_status, result_json
) VALUES
""".strip()
            + "\n"
            + ",\n".join(values)
        )

    def write_data_gap_items(self, items: list[dict[str, Any]]) -> None:
        """Upsert missing-data queue items collected from retrieval results.

        这里使用 gap_key 去重：同一个问题类型、院校/专业/省份/年份和缺失字段组合
        再次出现时，不新增重复任务，只增加 hit_count 并刷新 last_seen_at。这样后续
        动态 RAG 或人工补数可以优先处理“被学生反复问到”的缺口。
        """

        if not items:
            return

        values = []
        for item in items:
            priority = _coerce_int(item.get("priority")) or 2
            year = _coerce_int(item.get("year"))
            year_sql = "NULL" if year is None else str(year)
            values.append(
                "("
                f"{sql_quote(str(item.get('id') or uuid.uuid4().hex))}, "
                f"{sql_quote(str(item.get('gap_key') or ''))}, "
                f"{_nullable_sql(item.get('query_log_id'))}, "
                f"{_nullable_sql(item.get('session_id'))}, "
                f"{sql_quote(str(item.get('question_type') or 'unknown'))}, "
                f"{_nullable_sql(item.get('school_text'))}, "
                f"{_nullable_sql(item.get('major_text'))}, "
                f"{_nullable_sql(item.get('province'))}, "
                f"{_nullable_sql(item.get('subject_type'))}, "
                f"{year_sql}, "
                f"{_nullable_sql(item.get('batch'))}, "
                f"{_json_sql(item.get('missing_fields') or [])}, "
                f"{_json_sql(item.get('available_fields') or {})}, "
                f"{sql_quote(str(item.get('user_question') or ''))}, "
                f"{sql_quote(item.get('normalized_question'))}, "
                f"{priority}, "
                f"{sql_quote(str(item.get('status') or 'pending'))}, "
                f"{sql_quote(str(item.get('confidence_level') or 'low'))}, "
                f"{sql_quote(item.get('reason'))}, "
                f"{_json_sql(item.get('source_constraints') or DEFAULT_SOURCE_CONSTRAINTS)}, "
                f"{_json_sql(item.get('expected_outputs') or {})}"
                ")"
            )

        sql = (
            """
INSERT INTO data_gap_queue (
  id, gap_key, query_log_id, session_id, question_type,
  school_text, major_text, province, subject_type, year, batch,
  missing_fields_json, available_fields_json, user_question, normalized_question,
  priority, status, confidence_level, reason, source_constraints_json,
  expected_outputs_json
) VALUES
""".strip()
            + "\n"
            + ",\n".join(values)
            + "\n"
            + """
ON DUPLICATE KEY UPDATE
  query_log_id = COALESCE(VALUES(query_log_id), query_log_id),
  session_id = COALESCE(VALUES(session_id), session_id),
  missing_fields_json = VALUES(missing_fields_json),
  available_fields_json = VALUES(available_fields_json),
  user_question = VALUES(user_question),
  normalized_question = VALUES(normalized_question),
  priority = LEAST(priority, VALUES(priority)),
  status = IF(status IN ('resolved', 'rejected'), status, VALUES(status)),
  confidence_level = VALUES(confidence_level),
  reason = VALUES(reason),
  source_constraints_json = VALUES(source_constraints_json),
  expected_outputs_json = VALUES(expected_outputs_json),
  hit_count = hit_count + 1,
  last_seen_at = CURRENT_TIMESTAMP,
  updated_at = CURRENT_TIMESTAMP
""".strip()
        )
        self.execute(sql)

    def list_pending_gap_items(self, limit: int = 20, statuses: list[str] | None = None) -> list[dict[str, Any]]:
        """Read queue rows that are ready for evidence discovery.

        The evidence worker should not inspect raw MySQL JSON text directly.
        We base64-encode JSON columns in SQL so multiline Chinese text and JSON
        arrays survive the mysql CLI TSV parser without accidental splitting.
        """

        safe_limit = max(1, min(int(limit), 200))
        wanted_statuses = statuses or ["pending", "failed"]
        status_sql = ", ".join(sql_quote(status) for status in wanted_statuses)
        rows = self.reader.query(
            f"""
SELECT id, gap_key, question_type, school_text, major_text, province, subject_type,
       year, batch, priority, status, confidence_level, user_question,
       normalized_question, reason,
       TO_BASE64(CAST(missing_fields_json AS CHAR CHARACTER SET utf8mb4)) AS missing_fields_json_b64,
       TO_BASE64(CAST(available_fields_json AS CHAR CHARACTER SET utf8mb4)) AS available_fields_json_b64,
       TO_BASE64(CAST(source_constraints_json AS CHAR CHARACTER SET utf8mb4)) AS source_constraints_json_b64,
       TO_BASE64(CAST(expected_outputs_json AS CHAR CHARACTER SET utf8mb4)) AS expected_outputs_json_b64
FROM data_gap_queue
WHERE status IN ({status_sql})
ORDER BY priority ASC, hit_count DESC, updated_at ASC
LIMIT {safe_limit}
""".strip()
        )
        return [_decode_gap_queue_row(row) for row in rows]

    def build_evidence_tasks_from_pending(
        self,
        limit: int = 20,
        statuses: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Build local source-discovery tasks from pending gap rows."""

        return build_evidence_tasks(self.list_pending_gap_items(limit=limit, statuses=statuses))

    def write_evidence_tasks(self, tasks: list[dict[str, Any]]) -> None:
        """Upsert source-discovery tasks generated from `data_gap_queue`.

        The table stores search intent only.  A later web/search agent may pick
        up `ready` rows, fetch sources, and write verified documents into
        `source_documents`.  Keeping this step local makes the pipeline
        testable before any network or LLM behavior is introduced.
        """

        if not tasks:
            return

        values = []
        for task in tasks:
            values.append(
                "("
                f"{sql_quote(str(task.get('id') or uuid.uuid4().hex))}, "
                f"{sql_quote(str(task.get('task_key') or ''))}, "
                f"{sql_quote(str(task.get('gap_id') or ''))}, "
                f"{sql_quote(str(task.get('gap_key') or ''))}, "
                f"{sql_quote(str(task.get('question_type') or 'unknown'))}, "
                f"{sql_quote(str(task.get('search_query') or ''))}, "
                f"{_json_sql(task.get('preferred_sources') or [])}, "
                f"{_json_sql(task.get('expected_outputs') or {})}, "
                f"{sql_quote(str(task.get('status') or 'ready'))}, "
                f"{_coerce_int(task.get('priority')) or 2}"
                ")"
            )

        sql = (
            """
INSERT INTO data_gap_evidence_tasks (
  id, task_key, gap_id, gap_key, question_type, search_query,
  preferred_sources_json, expected_outputs_json, status, priority
) VALUES
""".strip()
            + "\n"
            + ",\n".join(values)
            + "\n"
            + """
ON DUPLICATE KEY UPDATE
  search_query = VALUES(search_query),
  preferred_sources_json = VALUES(preferred_sources_json),
  expected_outputs_json = VALUES(expected_outputs_json),
  status = IF(status IN ('done', 'needs_review'), status, VALUES(status)),
  priority = LEAST(priority, VALUES(priority)),
  updated_at = CURRENT_TIMESTAMP
""".strip()
        )
        self.execute(sql)

    def prepare_evidence_tasks(
        self,
        limit: int = 20,
        statuses: list[str] | None = None,
        dry_run: bool = False,
    ) -> list[dict[str, Any]]:
        """Build evidence tasks and optionally persist them.

        `dry_run=True` powers manual review and CI-style smoke checks.  The
        default path writes idempotently, so rerunning the worker does not create
        duplicate tasks for the same gap/search intent.
        """

        tasks = self.build_evidence_tasks_from_pending(limit=limit, statuses=statuses)
        if not dry_run:
            self.write_evidence_tasks(tasks)
        return tasks

    def execute(self, sql: str) -> None:
        """Run a write/DDL statement through mysql CLI using env-based password."""

        env = os.environ.copy()
        if self.config.password:
            env["MYSQL_PWD"] = self.config.password
        result = subprocess.run(
            [
                "mysql",
                f"--host={self.config.host}",
                f"--port={self.config.port}",
                f"--user={self.config.user}",
                "--get-server-public-key",
                "--connect-timeout=10",
                "--default-character-set=utf8mb4",
                "-D",
                self.config.database,
            ],
            input=sql,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "mysql command failed")


def _json_dumps(value: Any) -> str:
    """Serialize values consistently for hashing and MySQL JSON columns."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_sql(value: Any) -> str:
    """Return a quoted JSON document for MySQL JSON columns.

    MySQL can implicitly validate and store JSON text in a JSON column.  Using a
    plain quoted document matches the existing ingestion scripts and avoids
    version-specific `CAST(... AS JSON)` behavior.
    """

    return sql_quote(_json_dumps(value))


def _nullable_sql(value: Any) -> str:
    """Quote optional SQL text, preserving missing values as real NULL.

    The shared `sql_quote()` helper intentionally converts None to an empty
    string for older read queries.  For operational tables with foreign keys,
    especially `data_gap_queue.query_log_id`, an empty string is not the same
    as SQL NULL and will violate referential integrity.  This helper is used
    only where the schema explicitly allows NULL.
    """

    if value is None:
        return "NULL"
    if isinstance(value, str) and not value.strip():
        return "NULL"
    return sql_quote(value)


def _json_loads(value: Any, *, default: Any) -> Any:
    if value in (None, ""):
        return default
    try:
        return json.loads(str(value))
    except json.JSONDecodeError:
        return default


def _merged_gap_slots(result: dict[str, Any]) -> dict[str, Any]:
    """Merge explicit slots with the first useful tool arguments.

    自然语言入口通常会把省份、科类、学校、专业放在 `slots`；DeepSeek 路径则
    可能只在某个 function call 的 arguments 中出现。缺口队列第一版先做轻量合并，
    让后续人工或联网 agent 至少能看到最重要的检索条件。
    """

    slots: dict[str, Any] = {}
    explicit_slots = result.get("slots")
    if isinstance(explicit_slots, dict):
        slots.update(explicit_slots)

    for trace in result.get("tool_trace") or []:
        if not isinstance(trace, dict):
            continue
        arguments = trace.get("arguments")
        if isinstance(arguments, dict):
            for key, value in arguments.items():
                slots.setdefault(key, value)
    return slots


def _unique_texts(values: Any) -> list[str]:
    """Return non-empty strings in first-seen order."""

    seen: set[str] = set()
    unique: list[str] = []
    for value in values or []:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def _decode_gap_queue_row(row: dict[str, Any]) -> dict[str, Any]:
    """Decode one mysql CLI row from `data_gap_queue`.

    JSON columns are selected as base64 text by `list_pending_gap_items()`.
    Decoding them in one place keeps the rest of the workflow working with
    normal Python dictionaries and lists.
    """

    decoded = dict(row)
    decoded["missing_fields"] = _json_loads(_decode_base64_text(row.get("missing_fields_json_b64")), default=[])
    decoded["available_fields"] = _json_loads(_decode_base64_text(row.get("available_fields_json_b64")), default={})
    decoded["source_constraints"] = _json_loads(_decode_base64_text(row.get("source_constraints_json_b64")), default={})
    decoded["expected_outputs"] = _json_loads(_decode_base64_text(row.get("expected_outputs_json_b64")), default={})
    decoded["year"] = _coerce_int(decoded.get("year"))
    decoded["priority"] = _coerce_int(decoded.get("priority")) or 2
    for raw_key in (
        "missing_fields_json_b64",
        "available_fields_json_b64",
        "source_constraints_json_b64",
        "expected_outputs_json_b64",
    ):
        decoded.pop(raw_key, None)
    return decoded


def _build_gap_search_query(gap_item: dict[str, Any], missing_fields: list[str]) -> str:
    """Create a concise Chinese search query for a missing evidence task."""

    parts = _unique_texts(
        [
            gap_item.get("school_text"),
            gap_item.get("major_text"),
            gap_item.get("province"),
            gap_item.get("year"),
            *_field_search_terms(str(gap_item.get("question_type") or ""), missing_fields),
        ]
    )
    query = " ".join(parts).strip()
    return query[:512] or "高校 专业 官方 来源"


def _field_search_terms(question_type: str, missing_fields: list[str]) -> list[str]:
    """Translate missing fields into source-discovery keywords."""

    text = " ".join([question_type, *missing_fields])
    if any(word in text for word in ("分流", "大类", "冷门")):
        return ["大类分流", "专业分流", "分流办法", "培养方案"]
    if any(word in text for word in ("招生章程", "单科", "身体", "语种", "录取", "调剂", "中外合作")):
        return ["招生章程", "录取规则", "单科限制", "身体条件", "外语语种"]
    if any(word in text for word in ("考公", "公务员", "岗位", "职位表")):
        return ["公务员职位表", "专业要求", "专业目录"]
    if any(word in text for word in ("就业", "薪资", "Top", "公司", "升学")):
        return ["就业质量报告", "毕业生就业去向", "薪资", "重点就业单位"]
    if "转专业" in text:
        return ["转专业", "管理办法", "教务处"]
    return missing_fields[:4]


def _preferred_sources_for_gap(gap_item: dict[str, Any], missing_fields: list[str]) -> list[str]:
    """Return preferred source labels for a gap item.

    The queue may already contain `source_constraints`.  We preserve those first
    and append field-specific official sources, keeping the downstream web
    agent focused on auditable sources rather than general search snippets.
    """

    constraints = gap_item.get("source_constraints") or {}
    preferred: list[str] = []
    if isinstance(constraints, dict):
        for key in ("preferred_sources", "preferred_domains"):
            value = constraints.get(key)
            if isinstance(value, list):
                preferred.extend(str(item) for item in value)
    elif isinstance(constraints, list):
        preferred.extend(str(item) for item in constraints)

    field_text = " ".join(missing_fields)
    if any(word in field_text for word in ("招生章程", "单科", "身体", "语种", "录取", "分流", "转专业")):
        preferred.extend(["学校官网", "本科招生网", "教务处", "学院官网", "招生章程"])
    if any(word in field_text for word in ("就业", "薪资", "公司", "升学")):
        preferred.extend(["就业质量报告", "学校就业网", "学院官网"])
    if any(word in field_text for word in ("考公", "岗位", "职位表", "专业代码")):
        preferred.extend(["国家公务员局", "省公务员考试网", "官方职位表", "专业目录"])

    return _unique_texts(preferred or DEFAULT_SOURCE_CONSTRAINTS["preferred_sources"])


def _first_non_empty(*values: Any) -> Any:
    """Return the first value that is not None and not an empty string."""

    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _slot_text(slots: dict[str, Any], *keys: str) -> str | None:
    """Read a slot as clean text from several possible key names."""

    value = _first_non_empty(*(slots.get(key) for key in keys))
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_int(value: Any) -> int | None:
    """Best-effort integer conversion for year, score, rank, and priority."""

    if value in (None, ""):
        return None
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _available_gap_fields(result: dict[str, Any]) -> dict[str, Any]:
    """Record what the system already knew when it detected the gap."""

    available: dict[str, Any] = {}
    for key in ("route", "intent", "status", "slots", "tool_plan", "scope_notes", "warnings"):
        value = result.get(key)
        if value not in (None, "", [], {}):
            available[key] = value
    return available


def _gap_priority(*, status: str, missing_fields: list[str]) -> int:
    """Map missing evidence to a small priority number; 1 is most urgent."""

    high_signal_words = ("录取", "就业", "薪资", "转专业", "分流", "考公")
    if status in DATA_GAP_STATUSES:
        return 1
    if any(any(word in field for word in high_signal_words) for field in missing_fields):
        return 1
    return 2


def _gap_reason(result: dict[str, Any]) -> str:
    """Build a compact human-readable reason for reviewers and future agents."""

    warnings = _unique_texts(result.get("warnings") or [])
    if warnings:
        return "；".join(warnings)
    status = str(result.get("status") or "")
    if status in DATA_GAP_STATUSES:
        return f"工具返回 {status}，本地库无法支撑完整回答。"
    return "工具返回 data_gaps，等待联网检索或人工补充。"

def _decode_base64_text(value: Any) -> str | None:
    """Decode base64 text returned by MySQL without TSV escape side effects."""

    if value in (None, ""):
        return None
    try:
        return base64.b64decode(str(value)).decode("utf-8")
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create Major Intel agent query-log and cache tables.")
    parser.add_argument("--print-sql", action="store_true", help="只打印建表 SQL，不连接数据库。")
    parser.add_argument("--plan-gap-tasks", action="store_true", help="读取 pending 缺口并输出待搜索证据任务，不写库。")
    parser.add_argument("--enqueue-gap-tasks", action="store_true", help="读取 pending 缺口并写入 data_gap_evidence_tasks。")
    parser.add_argument("--limit", type=int, default=20, help="处理的缺口数量上限。")
    args = parser.parse_args(argv)

    if args.print_sql:
        print(build_agent_storage_schema_sql())
        return 0

    storage = MysqlAgentQueryStorage()
    if args.plan_gap_tasks:
        tasks = storage.prepare_evidence_tasks(limit=args.limit, dry_run=True)
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
        return 0

    if args.enqueue_gap_tasks:
        storage.setup_schema()
        tasks = storage.prepare_evidence_tasks(limit=args.limit, dry_run=False)
        print(json.dumps({"status": "ok", "task_count": len(tasks)}, ensure_ascii=False, indent=2))
        return 0

    storage.setup_schema()
    print("agent query storage tables ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
