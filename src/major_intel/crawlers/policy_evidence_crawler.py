"""Crawl policy documents and extract direction-level evidence mentions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from http.client import IncompleteRead
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DOCUMENT_SCHEMA_VERSION = "policy_evidence_document/v1"
MENTION_SCHEMA_VERSION = "policy_direction_mention/v1"
DEFAULT_USER_AGENT = "major-intel-policy-evidence-crawler/1.0"

REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "title",
    "url",
    "source_domain",
    "source_level",
    "source_type",
    "issuing_org",
    "published_date",
    "source_year",
    "notes",
}

DIRECTION_KEYWORDS = {
    "future_industries": ["未来产业", "未来制造", "未来信息", "未来材料", "未来能源", "未来空间", "未来健康", "前沿技术"],
    "artificial_intelligence": ["人工智能+", "人工智能", "大模型", "智能体", "智能经济", "算力", "具身智能", "脑机接口"],
    "low_altitude_economy": ["低空经济", "低空飞行", "低空空域", "低空技术", "低空航空器", "通用航空", "无人机"],
    "commercial_space": ["商业航天", "航空航天", "卫星互联网", "空天信息", "航天运输", "深空探测"],
    "bio_manufacturing": ["生物制造", "生物医药", "生物育种", "生物技术", "生物经济", "合成生物"],
    "quantum_technology": ["量子科技", "量子信息", "量子计算", "量子"],
    "integrated_circuit": ["集成电路", "半导体", "芯片", "先进计算"],
    "advanced_manufacturing": ["智能制造", "高端装备", "工业互联网", "机器人", "人形机器人", "智能网联汽车", "车路云"],
    "green_low_carbon": ["绿色低碳", "碳中和", "新能源", "储能", "新型储能", "氢能", "绿色能源"],
    "digital_economy": ["数字经济", "数据要素", "数字产业", "数字技术", "数据资源", "元宇宙", "虚拟现实", "增强现实", "数字孪生"],
    "new_materials": ["新材料", "先进材料", "前沿新材料", "先进结构材料", "高端材料"],
}

DOCUMENT_FIELDS = [
    "doc_id",
    "source_id",
    "title",
    "url",
    "source_domain",
    "source_level",
    "source_type",
    "issuing_org",
    "published_date",
    "source_year",
    "text_length",
    "paragraph_count",
    "mention_count",
    "raw_path",
    "captured_at",
]

MENTION_FIELDS = [
    "mention_id",
    "doc_id",
    "source_id",
    "source_title",
    "source_url",
    "source_level",
    "source_type",
    "source_year",
    "issuing_org",
    "direction",
    "keyword",
    "paragraph_index",
    "evidence_text",
    "captured_at",
]


def load_source_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    if not rows:
        raise ValueError(f"{path} has no source rows")
    missing = REQUIRED_SOURCE_FIELDS - set(rows[0])
    if missing:
        raise ValueError(f"{path} missing required fields: {sorted(missing)}")
    return rows


def crawl_policy_evidence(
    *,
    source_csv: Path,
    raw_dir: Path,
    processed_dir: Path,
    logs_dir: Path,
    reports_dir: Path,
    run_id: str,
    fetcher=None,
    timeout_seconds: float = 20,
    sleep_seconds: float = 0.0,
) -> dict[str, Any]:
    sources = load_source_rows(source_csv)
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    documents_jsonl = processed_dir / f"policy_documents_{run_id}.jsonl"
    mentions_jsonl = processed_dir / f"policy_mentions_{run_id}.jsonl"
    mentions_csv = processed_dir / f"policy_mentions_{run_id}.csv"
    report_path = reports_dir / f"policy_evidence_coverage_{run_id}.md"
    failure_log = logs_dir / f"{run_id}_failures.jsonl"
    manifest_path = logs_dir / f"{run_id}_manifest.json"

    actual_fetcher = fetcher or fetch_url_bytes
    documents: list[dict[str, Any]] = []
    mentions: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    captured_at = _now_iso()

    for source in sources:
        try:
            raw_bytes = actual_fetcher(source["url"], timeout_seconds)
            raw_path = _write_raw_bytes(raw_bytes, raw_dir=raw_dir, run_id=run_id, url=source["url"])
            title, paragraphs = extract_policy_text(raw_bytes, url=source["url"])
            doc = _build_document(source, title=title, paragraphs=paragraphs, raw_path=raw_path, captured_at=captured_at)
            doc_mentions = extract_policy_mentions(source, doc, paragraphs, captured_at=captured_at)
            doc["mention_count"] = len(doc_mentions)
            documents.append(doc)
            mentions.extend(doc_mentions)
        except Exception as exc:
            failures.append(_failure_row(source, exc))
        if sleep_seconds:
            time.sleep(sleep_seconds)

    write_jsonl(documents_jsonl, documents)
    write_jsonl(mentions_jsonl, mentions)
    write_mentions_csv(mentions, mentions_csv)
    write_report(documents, mentions, failures, report_path)
    write_jsonl(failure_log, failures)

    summary = {
        "run_id": run_id,
        "source_count": len(sources),
        "success_count": len(documents),
        "failure_count": len(failures),
        "mention_count": len(mentions),
        "documents_jsonl": str(documents_jsonl),
        "mentions_jsonl": str(mentions_jsonl),
        "mentions_csv": str(mentions_csv),
        "coverage_report": str(report_path),
        "failure_log": str(failure_log),
        "manifest_path": str(manifest_path),
        "finished_at": _now_iso(),
    }
    manifest_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def fetch_url_bytes(url: str, timeout_seconds: float = 20, max_attempts: int = 3) -> bytes:
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                return response.read()
        except IncompleteRead as exc:
            last_exc = exc
        except Exception as exc:
            status = getattr(exc, "code", None)
            if status is not None and status < 500:
                raise
            last_exc = exc
        if attempt < max_attempts:
            time.sleep(min(2 ** (attempt - 1), 4))
    try:
        import requests

        response = requests.get(url, headers={"User-Agent": DEFAULT_USER_AGENT}, timeout=timeout_seconds)
        response.raise_for_status()
        return response.content
    except Exception:
        if last_exc is not None:
            raise last_exc
        raise


def extract_policy_text(raw_bytes: bytes, url: str = "") -> tuple[str, list[str]]:
    if _is_pdf_payload(raw_bytes, url):
        text = extract_pdf_text_from_bytes(raw_bytes)
        paragraphs = [_clean_space(part) for part in re.split(r"[\r\n]+", text) if _clean_space(part)]
        return "", paragraphs

    html = _decode_bytes(raw_bytes)
    title = _extract_title(html)
    text = _html_to_text(html)
    paragraphs = [_clean_space(part) for part in re.split(r"[\r\n]+", text) if _clean_space(part)]
    return title, paragraphs


def extract_pdf_text_from_bytes(raw_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as handle:
        handle.write(raw_bytes)
        temp_path = Path(handle.name)
    try:
        return extract_pdf_text(temp_path)
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass


def extract_pdf_text(path: Path) -> str:
    pdftotext_text = _extract_pdf_text_with_pdftotext(path)
    if pdftotext_text:
        return pdftotext_text
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception:
        return ""


def extract_policy_mentions(
    source_row: dict[str, str],
    document: dict[str, Any],
    paragraphs: list[str],
    *,
    captured_at: str,
) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()
    for paragraph_index, paragraph in enumerate(paragraphs, start=1):
        for direction, keywords in DIRECTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword not in paragraph:
                    continue
                key = (direction, keyword, paragraph_index)
                if key in seen:
                    continue
                seen.add(key)
                mention_id = "policy_mention:" + _sha256_text(
                    "|".join([document["doc_id"], direction, keyword, str(paragraph_index), paragraph])
                )
                evidence_text = _evidence_window(paragraph, keyword)
                mentions.append(
                    {
                        "schema_version": MENTION_SCHEMA_VERSION,
                        "mention_id": mention_id,
                        "doc_id": document["doc_id"],
                        "source_id": source_row["source_id"],
                        "source_title": document["title"],
                        "source_url": source_row["url"],
                        "source_level": source_row["source_level"],
                        "source_type": source_row["source_type"],
                        "source_year": source_row["source_year"],
                        "issuing_org": source_row["issuing_org"],
                        "direction": direction,
                        "keyword": keyword,
                        "paragraph_index": paragraph_index,
                        "evidence_text": evidence_text,
                        "captured_at": captured_at,
                    }
                )
    return mentions


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_mentions_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MENTION_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in MENTION_FIELDS})


def write_report(
    documents: list[dict[str, Any]],
    mentions: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    path: Path,
) -> None:
    by_direction: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for mention in mentions:
        by_direction[mention["direction"]] = by_direction.get(mention["direction"], 0) + 1
        by_source[mention["source_id"]] = by_source.get(mention["source_id"], 0) + 1

    lines = [
        "# 政策语料证据覆盖报告",
        "",
        f"- 成功文档数：{len(documents)}",
        f"- 失败文档数：{len(failures)}",
        f"- 方向证据段落数：{len(mentions)}",
        "",
        "## 方向覆盖",
        "",
    ]
    for direction, count in sorted(by_direction.items()):
        lines.append(f"- `{direction}`: {count}")
    if not by_direction:
        lines.append("- 无")

    lines.extend(["", "## 来源覆盖", ""])
    for source_id, count in sorted(by_source.items()):
        lines.append(f"- `{source_id}`: {count}")
    if not by_source:
        lines.append("- 无")

    lines.extend(["", "## 失败来源", ""])
    if not failures:
        lines.append("- 无")
    for failure in failures:
        lines.append(f"- {failure['source_id']} {failure['url']} {failure['error_type']}: {failure['error']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_document(
    source_row: dict[str, str],
    *,
    title: str,
    paragraphs: list[str],
    raw_path: Path,
    captured_at: str,
) -> dict[str, Any]:
    doc_id = "policy_doc:" + _sha256_text(source_row["url"])
    full_text = "\n".join(paragraphs)
    return {
        "schema_version": DOCUMENT_SCHEMA_VERSION,
        "doc_id": doc_id,
        "source_id": source_row["source_id"],
        "title": title or source_row["title"],
        "url": source_row["url"],
        "source_domain": source_row["source_domain"],
        "source_level": source_row["source_level"],
        "source_type": source_row["source_type"],
        "issuing_org": source_row["issuing_org"],
        "published_date": source_row["published_date"],
        "source_year": source_row["source_year"],
        "text_length": len(full_text),
        "paragraph_count": len(paragraphs),
        "mention_count": 0,
        "raw_path": str(raw_path),
        "captured_at": captured_at,
    }


def _write_raw_bytes(raw_bytes: bytes, *, raw_dir: Path, run_id: str, url: str) -> Path:
    domain = (urlparse(url).hostname or "unknown").replace(":", "_")
    target_dir = raw_dir / run_id / domain
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{_sha256_text(url)}{_raw_file_extension(raw_bytes, url)}"
    target.write_bytes(raw_bytes)
    return target


def _raw_file_extension(raw_bytes: bytes, url: str) -> str:
    return ".pdf" if _is_pdf_payload(raw_bytes, url) else ".html"


def _is_pdf_payload(raw_bytes: bytes, url: str = "") -> bool:
    parsed_path = urlparse(url).path.lower()
    return raw_bytes.lstrip().startswith(b"%PDF") or parsed_path.endswith(".pdf")


def _failure_row(source_row: dict[str, str], exc: Exception) -> dict[str, Any]:
    return {
        "source_id": source_row.get("source_id", ""),
        "url": source_row.get("url", ""),
        "error_type": type(exc).__name__,
        "error": str(exc),
    }


def _html_to_text(html: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError:  # pragma: no cover - BeautifulSoup exists in repo env.
        return re.sub(r"<[^>]+>", "\n", html)
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    blocks = []
    for element in soup.find_all(["p", "li", "td", "h1", "h2", "h3"]):
        text = element.get_text(" ", strip=True)
        if text:
            blocks.append(text)

    seen = {_clean_space(block) for block in blocks}
    if len("\n".join(blocks)) < 1000:
        for element in soup.find_all(["div", "article", "section", "main"]):
            _append_unique_block(blocks, seen, element.get_text(" ", strip=True), min_length=120)

    for raw_line in soup.get_text("\n").splitlines():
        text = _clean_space(raw_line)
        _append_unique_block(blocks, seen, text)
    return "\n".join(blocks)


def _append_unique_block(blocks: list[str], seen: set[str], text: str, *, min_length: int = 1) -> None:
    clean = _clean_space(text)
    if len(clean) < min_length or clean in seen:
        return
    if any(clean in existing for existing in seen if len(existing) > len(clean)):
        return
    blocks.append(clean)
    seen.add(clean)


def _extract_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    return _clean_space(re.sub(r"<[^>]+>", "", match.group(1))) if match else ""


def _decode_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "gb18030", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _extract_pdf_text_with_pdftotext(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["pdftotext", "-layout", str(path.resolve()), "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return ""
    if not completed.stdout:
        return ""
    return _decode_bytes(completed.stdout).strip()


def _clean_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _evidence_window(text: str, keyword: str, window: int = 260) -> str:
    clean = _clean_space(text)
    if len(clean) <= window * 2:
        return clean
    index = clean.find(keyword)
    if index < 0:
        return clean[: window * 2]
    start = max(0, index - window)
    end = min(len(clean), index + len(keyword) + window)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(clean) else ""
    return prefix + clean[start:end] + suffix


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Crawl policy documents and extract direction evidence.")
    parser.add_argument("--source-csv", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/policy_evidence"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/policy_evidence"))
    parser.add_argument("--logs-dir", type=Path, default=Path("data/logs/policy_evidence"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports/policy_evidence"))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=20)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    args = parser.parse_args(argv)

    summary = crawl_policy_evidence(
        source_csv=args.source_csv,
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        logs_dir=args.logs_dir,
        reports_dir=args.reports_dir,
        run_id=args.run_id,
        timeout_seconds=args.timeout_seconds,
        sleep_seconds=args.sleep_seconds,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
