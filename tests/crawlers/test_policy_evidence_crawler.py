import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from major_intel.crawlers import policy_evidence_crawler as crawler
from major_intel.crawlers.policy_evidence_crawler import (
    crawl_policy_evidence,
    extract_policy_mentions,
    extract_policy_text,
)


def _source_row() -> dict[str, str]:
    return {
        "source_id": "gwr_2025",
        "title": "政府工作报告",
        "url": "https://www.gov.cn/report.html",
        "source_domain": "www.gov.cn",
        "source_level": "A",
        "source_type": "government_work_report",
        "issuing_org": "国务院",
        "published_date": "2025-03-12",
        "source_year": "2025",
        "notes": "seed",
    }


def test_extract_policy_mentions_from_html_paragraphs():
    html = """
    <html><head><title>政府工作报告</title></head><body>
      <p>持续推进“人工智能+”行动，培育智能产业。</p>
      <p>积极发展低空经济、商业航天等新增长引擎。</p>
    </body></html>
    """
    title, paragraphs = extract_policy_text(html.encode("utf-8"))
    document = {
        "doc_id": "policy_doc:test",
        "title": title,
    }

    mentions = extract_policy_mentions(
        _source_row(),
        document,
        paragraphs,
        captured_at="2026-06-12T00:00:00+08:00",
    )

    assert title == "政府工作报告"
    assert {row["direction"] for row in mentions} >= {
        "artificial_intelligence",
        "low_altitude_economy",
        "commercial_space",
    }
    assert any(row["keyword"] == "人工智能+" for row in mentions)


def test_extract_policy_text_handles_pdf_payload(monkeypatch):
    monkeypatch.setattr(
        crawler,
        "extract_pdf_text_from_bytes",
        lambda raw_bytes: "加快人工智能+创新应用。\n培育低空经济和无人机产业。",
    )

    title, paragraphs = extract_policy_text(b"%PDF-1.7 fake", url="https://www.gov.cn/policy.pdf")

    assert title == ""
    assert paragraphs == ["加快人工智能+创新应用。", "培育低空经济和无人机产业。"]


def test_extract_policy_text_keeps_visible_lines_outside_standard_blocks():
    html = """
    <html><head><title>元宇宙行动计划</title></head><body>
      工业和信息化部关于推动未来产业创新发展。
      元宇宙产业创新发展三年行动计划。
    </body></html>
    """

    title, paragraphs = extract_policy_text(html.encode("utf-8"))

    assert title == "元宇宙行动计划"
    assert any("未来产业" in paragraph for paragraph in paragraphs)
    assert any("元宇宙" in paragraph for paragraph in paragraphs)


def test_extract_policy_mentions_truncates_long_evidence_window():
    long_text = "前文" * 300 + "人工智能+" + "后文" * 300
    mentions = extract_policy_mentions(
        _source_row(),
        {"doc_id": "policy_doc:test", "title": "政策"},
        [long_text],
        captured_at="2026-06-12T00:00:00+08:00",
    )

    ai_mention = next(row for row in mentions if row["keyword"] == "人工智能+")
    assert len(ai_mention["evidence_text"]) < len(long_text)
    assert "人工智能+" in ai_mention["evidence_text"]
    assert ai_mention["evidence_text"].startswith("...")


def test_crawl_policy_evidence_writes_documents_mentions_and_report(tmp_path):
    source_csv = tmp_path / "sources.csv"
    source_csv.write_text(
        "source_id,title,url,source_domain,source_level,source_type,issuing_org,published_date,source_year,notes\n"
        "gwr_2025,政府工作报告,https://www.gov.cn/report.html,www.gov.cn,A,government_work_report,国务院,2025-03-12,2025,seed\n",
        encoding="utf-8",
    )
    html = """
    <html><head><title>政府工作报告</title></head><body>
      <p>推动人工智能、数字经济和绿色低碳产业发展。</p>
    </body></html>
    """

    def fetcher(url, timeout_seconds):
        assert url == "https://www.gov.cn/report.html"
        return html.encode("utf-8")

    summary = crawl_policy_evidence(
        source_csv=source_csv,
        raw_dir=tmp_path / "raw",
        processed_dir=tmp_path / "processed",
        logs_dir=tmp_path / "logs",
        reports_dir=tmp_path / "reports",
        run_id="test_run",
        fetcher=fetcher,
    )

    assert summary["success_count"] == 1
    assert summary["failure_count"] == 0
    assert summary["mention_count"] >= 3
    documents = Path(summary["documents_jsonl"]).read_text(encoding="utf-8").splitlines()
    mentions = [json.loads(line) for line in Path(summary["mentions_jsonl"]).read_text(encoding="utf-8").splitlines()]
    report = Path(summary["coverage_report"]).read_text(encoding="utf-8")
    assert len(documents) == 1
    assert {row["direction"] for row in mentions} >= {"artificial_intelligence", "digital_economy", "green_low_carbon"}
    assert "# 政策语料证据覆盖报告" in report


def test_crawl_policy_evidence_writes_pdf_raw_file(tmp_path, monkeypatch):
    source_csv = tmp_path / "sources.csv"
    source_csv.write_text(
        "source_id,title,url,source_domain,source_level,source_type,issuing_org,published_date,source_year,notes\n"
        "ai_pdf,人工智能政策,https://www.gov.cn/policy.pdf,www.gov.cn,A,state_council_policy,国务院,2025-08-26,2025,seed\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        crawler,
        "extract_pdf_text_from_bytes",
        lambda raw_bytes: "推动人工智能和数字经济融合发展。",
    )

    summary = crawl_policy_evidence(
        source_csv=source_csv,
        raw_dir=tmp_path / "raw",
        processed_dir=tmp_path / "processed",
        logs_dir=tmp_path / "logs",
        reports_dir=tmp_path / "reports",
        run_id="test_pdf_run",
        fetcher=lambda url, timeout_seconds: b"%PDF-1.7 fake",
    )

    document = json.loads(Path(summary["documents_jsonl"]).read_text(encoding="utf-8").splitlines()[0])
    assert document["raw_path"].endswith(".pdf")
    assert summary["mention_count"] >= 2
