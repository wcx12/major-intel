import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.ingest_policy_data import (
    EMERGING_MAJOR_CANDIDATE_TABLE,
    EMERGING_MAJOR_UNIQUE_TABLE,
    POLICY_DOCUMENT_TABLE,
    POLICY_MENTION_TABLE,
    build_schema_sql,
    candidate_record_to_row,
    ingest_emerging_majors,
    ingest_policy_evidence,
    policy_document_record_to_row,
    policy_mention_record_to_row,
)


EMERGING_CANDIDATE = {
    "candidate_id": "cand-001",
    "major_code": "080717T",
    "major_name": "人工智能",
    "major_level": "本科",
    "discipline_category": "工学",
    "major_class": "电子信息类",
    "degree": "工学",
    "study_years": "四年",
    "event_type": "new_major",
    "event_year": "2018",
    "candidate_status": "approved",
    "source_title": "教育部关于公布年度普通高等学校本科专业备案和审批结果的通知",
    "source_url": "https://example.edu.cn/source.html",
    "attachment_url": "https://example.edu.cn/source.xlsx",
    "source_level": "A",
    "evidence_text": "080717T 人工智能",
    "raw_path": "data/raw/policy_documents/source.xlsx",
    "parsed_from": "xlsx",
    "captured_at": "2026-06-12T00:00:00+08:00",
    "warnings": ["sample warning"],
}


POLICY_DOCUMENT = {
    "doc_id": "doc-001",
    "source_id": "gov-work-report-2026",
    "title": "政府工作报告",
    "url": "https://example.gov.cn/report.html",
    "source_domain": "example.gov.cn",
    "source_level": "A",
    "source_type": "government_work_report",
    "issuing_org": "国务院",
    "published_date": "2026-03-12",
    "source_year": "2026",
    "text_length": "1000",
    "paragraph_count": "20",
    "mention_count": "2",
    "raw_path": "data/raw/policy_evidence/report.html",
    "captured_at": "2026-06-12T00:00:00+08:00",
}


POLICY_MENTION = {
    "mention_id": "mention-001",
    "doc_id": "doc-001",
    "source_id": "gov-work-report-2026",
    "source_title": "政府工作报告",
    "source_url": "https://example.gov.cn/report.html",
    "source_level": "A",
    "source_type": "government_work_report",
    "source_year": "2026",
    "issuing_org": "国务院",
    "direction": "人工智能",
    "keyword": "人工智能",
    "paragraph_index": "3",
    "evidence_text": "加快发展人工智能。",
    "captured_at": "2026-06-12T00:00:00+08:00",
}


class FakeRunner:
    def __init__(self):
        self.sql_statements = []

    def run(self, sql, capture_output=False):
        self.sql_statements.append(sql)
        return ""


class PolicyDataIngestionTests(unittest.TestCase):
    def test_build_schema_sql_contains_official_policy_tables(self):
        schema_sql = build_schema_sql()

        self.assertIn(f"CREATE TABLE IF NOT EXISTS {EMERGING_MAJOR_CANDIDATE_TABLE}", schema_sql)
        self.assertIn(f"CREATE TABLE IF NOT EXISTS {EMERGING_MAJOR_UNIQUE_TABLE}", schema_sql)
        self.assertIn(f"CREATE TABLE IF NOT EXISTS {POLICY_DOCUMENT_TABLE}", schema_sql)
        self.assertIn(f"CREATE TABLE IF NOT EXISTS {POLICY_MENTION_TABLE}", schema_sql)
        self.assertIn("PRIMARY KEY (candidate_id)", schema_sql)
        self.assertIn("PRIMARY KEY (major_key)", schema_sql)
        self.assertIn("PRIMARY KEY (doc_id)", schema_sql)
        self.assertIn("PRIMARY KEY (mention_id)", schema_sql)

    def test_candidate_record_to_row_preserves_source_scope_and_raw_json(self):
        row = candidate_record_to_row(EMERGING_CANDIDATE)

        self.assertEqual(row["candidate_id"], "cand-001")
        self.assertEqual(row["major_code"], "080717T")
        self.assertEqual(row["major_name"], "人工智能")
        self.assertEqual(row["event_year"], 2018)
        self.assertEqual(row["source_level"], "A")
        self.assertEqual(json.loads(row["warnings_json"]), ["sample warning"])
        self.assertEqual(json.loads(row["raw_candidate_json"])["candidate_id"], "cand-001")

    def test_policy_rows_convert_numeric_fields_and_keep_evidence(self):
        document_row = policy_document_record_to_row(POLICY_DOCUMENT)
        mention_row = policy_mention_record_to_row(POLICY_MENTION)

        self.assertEqual(document_row["source_year"], 2026)
        self.assertEqual(document_row["text_length"], 1000)
        self.assertEqual(document_row["paragraph_count"], 20)
        self.assertEqual(document_row["mention_count"], 2)
        self.assertEqual(json.loads(document_row["raw_document_json"])["doc_id"], "doc-001")

        self.assertEqual(mention_row["source_year"], 2026)
        self.assertEqual(mention_row["paragraph_index"], 3)
        self.assertEqual(mention_row["direction"], "人工智能")
        self.assertIn("人工智能", mention_row["evidence_text"])
        self.assertEqual(json.loads(mention_row["raw_mention_json"])["mention_id"], "mention-001")

    def test_ingest_emerging_majors_builds_candidate_and_unique_tables(self):
        with TemporaryDirectory() as temp_dir:
            candidates_jsonl = Path(temp_dir) / "candidates.jsonl"
            candidates_jsonl.write_text(
                json.dumps(EMERGING_CANDIDATE, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            runner = FakeRunner()

            stats = ingest_emerging_majors(runner, candidates_jsonl, chunk_size=1)

            self.assertEqual(stats, {"candidates": 1, "unique_majors": 1})
            self.assertEqual(len(runner.sql_statements), 2)
            self.assertIn(EMERGING_MAJOR_CANDIDATE_TABLE, runner.sql_statements[0])
            self.assertIn(EMERGING_MAJOR_UNIQUE_TABLE, runner.sql_statements[1])
            self.assertTrue(all("ON DUPLICATE KEY UPDATE" in sql for sql in runner.sql_statements))

    def test_ingest_policy_evidence_builds_document_and_mention_tables(self):
        with TemporaryDirectory() as temp_dir:
            documents_jsonl = Path(temp_dir) / "documents.jsonl"
            mentions_jsonl = Path(temp_dir) / "mentions.jsonl"
            documents_jsonl.write_text(
                json.dumps(POLICY_DOCUMENT, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            mentions_jsonl.write_text(
                json.dumps(POLICY_MENTION, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            runner = FakeRunner()

            stats = ingest_policy_evidence(
                runner,
                documents_jsonl=documents_jsonl,
                mentions_jsonl=mentions_jsonl,
                chunk_size=1,
            )

            self.assertEqual(stats, {"documents": 1, "mentions": 1})
            self.assertEqual(len(runner.sql_statements), 2)
            self.assertIn(POLICY_DOCUMENT_TABLE, runner.sql_statements[0])
            self.assertIn(POLICY_MENTION_TABLE, runner.sql_statements[1])
            self.assertTrue(all("ON DUPLICATE KEY UPDATE" in sql for sql in runner.sql_statements))


if __name__ == "__main__":
    unittest.main()
