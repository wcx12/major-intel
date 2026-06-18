"""Archive unresolved major-risk source URLs to local raw/text files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import shutil
import ssl
import subprocess
import tempfile
import time
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_INDEX_CSV = (
    ROOT
    / "data/processed/major_risk_review_release/major_risk_source_document_index_2026.csv"
)
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/major_risk_source_archive"
DEFAULT_REPORT_DIR = ROOT / "reports/major_risk_source_archive"
DEFAULT_RAW_ROOT = ROOT / "data/raw/major_risk_review_source_archive"
SCHEMA_VERSION = "major_risk_source_archive/v1"
DEFAULT_USER_AGENT = "major-intel-source-archiver/1.0"

ARCHIVE_FIELDS = [
    "archive_id",
    "source_url",
    "final_url",
    "source_domain",
    "source_title_sample",
    "source_publishers",
    "evidence_families",
    "source_tables",
    "source_row_count",
    "evidence_record_count_sum",
    "major_count_max",
    "crawl_status",
    "http_status",
    "content_type",
    "content_length",
    "raw_path",
    "text_path",
    "text_length",
    "sha256",
    "captured_at",
    "error",
]


@dataclass(frozen=True)
class FetchResult:
    body: bytes
    status_code: int = 200
    final_url: str = ""
    content_type: str = ""
    headers: dict[str, str] | None = None


def build_major_risk_source_archive(
    *,
    source_index_csv: Path = DEFAULT_SOURCE_INDEX_CSV,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    raw_root: Path = DEFAULT_RAW_ROOT,
    generated_at: str | None = None,
    run_id: str | None = None,
    fetcher: Callable[[str, float], FetchResult] | None = None,
    timeout_seconds: float = 20,
    sleep_seconds: float = 0.2,
    limit: int | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    generated_at = generated_at or date.today().isoformat()
    run_id = run_id or generated_at.replace("-", "")
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    raw_dir = Path(raw_root) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    archive_csv = output_dir / "major_risk_review_source_archive_2026.csv"
    manifest_json = output_dir / "major_risk_source_archive_manifest_2026.json"
    report_md = report_dir / "major_risk_source_archive_2026.md"

    previous_urls = load_previous_archive_urls(archive_csv)
    target_rows = select_target_source_rows(source_index_csv, previous_urls=previous_urls)
    if limit is not None:
        target_rows = target_rows[:limit]

    actual_fetcher = fetcher or fetch_url
    captured_at = datetime.now(timezone.utc).astimezone().isoformat()
    archive_rows: list[dict[str, Any]] = []
    for index, source in enumerate(target_rows):
        if index and sleep_seconds:
            time.sleep(sleep_seconds)
        archive_rows.append(
            archive_one_url(
                source,
                raw_dir=raw_dir,
                fetcher=actual_fetcher,
                timeout_seconds=timeout_seconds,
                captured_at=captured_at,
                refresh=refresh,
            )
        )

    write_csv(archive_csv, archive_rows, ARCHIVE_FIELDS)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "generated_at": generated_at,
        "run_id": run_id,
        "inputs": {
            "source_index_csv": path_key(source_index_csv),
        },
        "outputs": {
            "archive_csv": path_key(archive_csv),
            "manifest_json": path_key(manifest_json),
            "report_md": path_key(report_md),
            "raw_dir": path_key(raw_dir),
        },
        "row_counts": {
            "archive_rows": len(archive_rows),
            "source_index_target_rows": sum(int(row["source_row_count"]) for row in archive_rows),
            "successful_or_cached": sum(
                1 for row in archive_rows if row["crawl_status"] in {"ok", "cached"}
            ),
            "with_text": sum(1 for row in archive_rows if row["text_path"]),
            "failed": sum(1 for row in archive_rows if row["crawl_status"] == "failed"),
        },
        "crawl_status_counts": dict(
            sorted(Counter(row["crawl_status"] for row in archive_rows).items())
        ),
        "domain_counts": dict(
            sorted(Counter(row["source_domain"] for row in archive_rows).items())
        ),
        "content_type_counts": dict(
            sorted(Counter(row["content_type"] for row in archive_rows if row["content_type"]).items())
        ),
        "checksums": {
            path_key(archive_csv): file_info(archive_csv),
        },
    }
    write_text_atomic(
        manifest_json,
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    manifest["checksums"][path_key(manifest_json)] = file_info(manifest_json)
    write_text_atomic(
        manifest_json,
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    write_report(report_md, manifest, archive_rows)
    return manifest


def select_target_source_rows(
    source_index_csv: Path,
    *,
    previous_urls: set[str],
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in read_csv_rows(source_index_csv):
        source_url = text(row.get("source_url"))
        if row.get("source_kind") != "url" or not source_url:
            continue
        if row.get("source_path_status") != "no_local_path" and source_url not in previous_urls:
            continue
        item = grouped.setdefault(
            source_url,
            {
                "source_url": source_url,
                "source_domain": urlparse(source_url).netloc.lower(),
                "source_titles": set(),
                "source_publishers": set(),
                "evidence_families": set(),
                "source_tables": set(),
                "source_row_count": 0,
                "evidence_record_count_sum": 0,
                "major_count_max": 0,
            },
        )
        item["source_titles"].update(split_values(row.get("source_title")))
        item["source_publishers"].update(split_values(row.get("source_publisher")))
        item["evidence_families"].update(split_values(row.get("evidence_families")))
        item["source_tables"].update(split_values(row.get("source_tables")))
        item["source_row_count"] += 1
        item["evidence_record_count_sum"] += to_int(row.get("evidence_record_count"))
        item["major_count_max"] = max(item["major_count_max"], to_int(row.get("major_count")))
    return sorted(
        (
            {
                **item,
                "source_title_sample": join_sample(item["source_titles"], limit=6),
                "source_publishers": join_sorted(item["source_publishers"]),
                "evidence_families": join_sorted(item["evidence_families"]),
                "source_tables": join_sorted(item["source_tables"]),
            }
            for item in grouped.values()
        ),
        key=lambda row: (-to_int(row["evidence_record_count_sum"]), row["source_url"]),
    )


def archive_one_url(
    source: dict[str, Any],
    *,
    raw_dir: Path,
    fetcher: Callable[[str, float], FetchResult],
    timeout_seconds: float,
    captured_at: str,
    refresh: bool,
) -> dict[str, Any]:
    source_url = text(source.get("source_url"))
    archive_id = stable_id("risk_source_archive", source_url)
    file_stem = archive_file_stem(archive_id)
    cached_raw = find_cached_raw(raw_dir, file_stem)
    try:
        if cached_raw and not refresh:
            body = cached_raw.read_bytes()
            content_type = infer_content_type(source_url, cached_raw.name)
            final_url = source_url
            http_status = ""
            crawl_status = "cached"
            raw_path = path_key(cached_raw)
        else:
            result = fetcher(source_url, timeout_seconds)
            body = result.body
            content_type = text(result.content_type) or header_value(result.headers, "content-type")
            final_url = result.final_url or source_url
            http_status = str(result.status_code)
            suffix = suffix_for(source_url, content_type)
            raw_path_obj = raw_dir / f"{file_stem}.{suffix}"
            raw_path_obj.write_bytes(body)
            raw_path = path_key(raw_path_obj)
            crawl_status = "ok" if 200 <= int(result.status_code) < 400 else "failed"
        text_content = extract_text(body, content_type=content_type, url=source_url)
        text_path = ""
        if text_content:
            text_path_obj = raw_dir / f"{file_stem}.txt"
            text_path_obj.write_text(text_content, encoding="utf-8")
            text_path = path_key(text_path_obj)
        metadata_path = raw_dir / f"{file_stem}.metadata.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "source_url": source_url,
                    "final_url": final_url,
                    "content_type": content_type,
                    "captured_at": captured_at,
                    "raw_path": raw_path,
                    "text_path": text_path,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return archive_row(
            source,
            archive_id=archive_id,
            final_url=final_url,
            crawl_status=crawl_status,
            http_status=http_status,
            content_type=content_type,
            body=body,
            raw_path=raw_path,
            text_path=text_path,
            text_length=len(text_content),
            captured_at=captured_at,
            error="",
        )
    except Exception as exc:
        return archive_row(
            source,
            archive_id=archive_id,
            final_url="",
            crawl_status="failed",
            http_status="",
            content_type="",
            body=b"",
            raw_path="",
            text_path="",
            text_length=0,
            captured_at=captured_at,
            error=f"{type(exc).__name__}: {exc}",
        )


def archive_row(
    source: dict[str, Any],
    *,
    archive_id: str,
    final_url: str,
    crawl_status: str,
    http_status: str,
    content_type: str,
    body: bytes,
    raw_path: str,
    text_path: str,
    text_length: int,
    captured_at: str,
    error: str,
) -> dict[str, Any]:
    return {
        "archive_id": archive_id,
        "source_url": source.get("source_url", ""),
        "final_url": final_url,
        "source_domain": source.get("source_domain", ""),
        "source_title_sample": source.get("source_title_sample", ""),
        "source_publishers": source.get("source_publishers", ""),
        "evidence_families": source.get("evidence_families", ""),
        "source_tables": source.get("source_tables", ""),
        "source_row_count": source.get("source_row_count", ""),
        "evidence_record_count_sum": source.get("evidence_record_count_sum", ""),
        "major_count_max": source.get("major_count_max", ""),
        "crawl_status": crawl_status,
        "http_status": http_status,
        "content_type": content_type,
        "content_length": len(body),
        "raw_path": raw_path,
        "text_path": text_path,
        "text_length": text_length,
        "sha256": hashlib.sha256(body).hexdigest() if body else "",
        "captured_at": captured_at,
        "error": error,
    }


def fetch_url(url: str, timeout_seconds: float) -> FetchResult:
    request = Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf,application/json,*/*;q=0.8",
        },
    )
    try:
        return open_request(request, timeout_seconds=timeout_seconds)
    except HTTPError as exc:
        body = exc.read()
        headers = {key.lower(): value for key, value in exc.headers.items()}
        return FetchResult(
            body=body,
            status_code=exc.code,
            final_url=exc.geturl(),
            content_type=headers.get("content-type", ""),
            headers=headers,
        )
    except URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        return open_request(
            request,
            timeout_seconds=timeout_seconds,
            context=ssl._create_unverified_context(),
        )


def open_request(
    request: Request,
    *,
    timeout_seconds: float,
    context: ssl.SSLContext | None = None,
) -> FetchResult:
    with urlopen(request, timeout=timeout_seconds, context=context) as response:
        body = response.read()
        headers = {key.lower(): value for key, value in response.headers.items()}
        return FetchResult(
            body=body,
            status_code=getattr(response, "status", 200),
            final_url=response.geturl(),
            content_type=headers.get("content-type", ""),
            headers=headers,
        )


def extract_text(raw_bytes: bytes, *, content_type: str, url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    content_type_lower = content_type.lower()
    if raw_bytes.startswith(b"PK\x03\x04"):
        return extract_zip_text(raw_bytes)
    if raw_bytes.startswith(b"%PDF") or "pdf" in content_type_lower or suffix == ".pdf":
        return extract_pdf_text(raw_bytes)
    if "json" in content_type_lower:
        return extract_json_text(raw_bytes)
    if is_office_binary(content_type_lower, suffix, raw_bytes):
        return extract_ole_text(raw_bytes)
    if is_image_binary(content_type_lower, suffix, raw_bytes):
        return extract_image_metadata(raw_bytes)
    if is_html_like(content_type_lower, suffix):
        return extract_html_text(raw_bytes, content_type=content_type)
    if content_type_lower.startswith("text/") or suffix in {".txt", ".csv"}:
        return decode_bytes(raw_bytes, content_type=content_type)
    return ""


def extract_pdf_text(raw_bytes: bytes) -> str:
    for extractor in [extract_pdf_text_pypdf, extract_pdf_text_pymupdf, extract_pdf_text_pdftotext]:
        text_content = extractor(raw_bytes)
        if text_content:
            return text_content
    return extract_pdf_metadata(raw_bytes)


def extract_pdf_text_pypdf(raw_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(raw_bytes))
        text_parts = []
        for page in reader.pages[:200]:
            text_parts.append(page.extract_text() or "")
        return normalize_space("\n".join(text_parts))
    except Exception:
        return ""


def extract_pdf_text_pymupdf(raw_bytes: bytes) -> str:
    try:
        import fitz

        document = fitz.open(stream=raw_bytes, filetype="pdf")
        text_parts = []
        for index in range(min(document.page_count, 200)):
            text_parts.append(document.load_page(index).get_text("text"))
        return normalize_space("\n".join(text_parts))
    except Exception:
        return ""


def extract_pdf_text_pdftotext(raw_bytes: bytes) -> str:
    if not shutil.which("pdftotext"):
        return ""
    with tempfile.TemporaryDirectory() as tmp_dir:
        input_path = Path(tmp_dir) / "source.pdf"
        output_path = Path(tmp_dir) / "source.txt"
        input_path.write_bytes(raw_bytes)
        try:
            subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", str(input_path), str(output_path)],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60,
            )
        except Exception:
            return ""
        if output_path.exists():
            return normalize_space(output_path.read_text(encoding="utf-8", errors="replace"))
    return ""


def extract_pdf_metadata(raw_bytes: bytes) -> str:
    lines = ["PDF source metadata", "text_extraction=empty"]
    try:
        import fitz

        document = fitz.open(stream=raw_bytes, filetype="pdf")
        lines.append(f"page_count={document.page_count}")
        if document.page_count:
            page = document.load_page(0)
            rect = page.rect
            lines.append(f"first_page_width={rect.width:.2f}")
            lines.append(f"first_page_height={rect.height:.2f}")
        return normalize_space("\n".join(lines))
    except Exception:
        return normalize_space("\n".join(lines))


def extract_json_text(raw_bytes: bytes) -> str:
    decoded = decode_bytes(raw_bytes, content_type="application/json")
    try:
        return json.dumps(json.loads(decoded), ensure_ascii=False, indent=2)
    except Exception:
        return decoded


def extract_html_text(raw_bytes: bytes, *, content_type: str) -> str:
    decoded = decode_bytes(raw_bytes, content_type=content_type)
    try:
        import warnings

        from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
            soup = BeautifulSoup(decoded, "html.parser")
        for item in soup(["script", "style", "noscript"]):
            item.decompose()
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        body = soup.get_text("\n", strip=True)
        return normalize_space("\n".join(part for part in [title, body] if part))
    except Exception:
        decoded = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", decoded)
        decoded = re.sub(r"(?s)<[^>]+>", " ", decoded)
        return normalize_space(html.unescape(decoded))


def extract_zip_text(raw_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(raw_bytes)) as archive:
            lines = ["ZIP archive contents:"]
            for info in archive.infolist()[:200]:
                name = normalize_zip_name(info.filename)
                lines.append(f"- {name} ({info.file_size} bytes)")
                if info.is_dir() or info.file_size > 5_000_000:
                    continue
                try:
                    member_bytes = archive.read(info)
                except Exception as exc:
                    lines.append(f"  [read_error] {type(exc).__name__}: {exc}")
                    continue
                member_text = extract_text(
                    member_bytes,
                    content_type=infer_content_type(name, name),
                    url=name,
                )
                if member_text:
                    lines.append(indent_text(member_text, prefix="  "))
            return normalize_space("\n".join(lines))
    except Exception:
        return ""


def extract_ole_text(raw_bytes: bytes) -> str:
    candidates = []
    for encoding in ["utf-16le", "gb18030", "utf-8"]:
        try:
            decoded = raw_bytes.decode(encoding, errors="ignore")
        except Exception:
            continue
        candidates.extend(printable_text_runs(decoded))
    seen = set()
    lines = []
    for candidate in candidates:
        normalized = normalize_space(candidate)
        if len(normalized) < 4 or normalized in seen:
            continue
        seen.add(normalized)
        lines.append(normalized)
        if len(lines) >= 500:
            break
    return "\n".join(lines)


def extract_image_metadata(raw_bytes: bytes) -> str:
    try:
        from PIL import Image

        with Image.open(BytesIO(raw_bytes)) as image:
            return normalize_space(
                "\n".join(
                    [
                        "Image source metadata",
                        f"format={image.format or ''}",
                        f"mode={image.mode}",
                        f"width={image.width}",
                        f"height={image.height}",
                    ]
                )
            )
    except Exception:
        return ""


def printable_text_runs(value: str) -> list[str]:
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", "\n", value)
    pattern = re.compile(
        r"[\u4e00-\u9fffA-Za-z0-9，。、《》；：！？（）()【】\[\]\"'“”‘’、/\\_.\-\s]{4,}"
    )
    return [
        match.group(0).strip()
        for match in pattern.finditer(cleaned)
        if match.group(0).strip()
    ]


def normalize_zip_name(name: str) -> str:
    try:
        return name.encode("cp437").decode("gbk")
    except Exception:
        return name


def indent_text(value: str, *, prefix: str) -> str:
    return "\n".join(prefix + line for line in value.splitlines())


def decode_bytes(raw_bytes: bytes, *, content_type: str) -> str:
    charset_match = re.search(r"charset=([A-Za-z0-9._-]+)", content_type, flags=re.I)
    encodings = [charset_match.group(1)] if charset_match else []
    encodings.extend(["utf-8-sig", "utf-8", "gb18030", "big5"])
    for encoding in encodings:
        try:
            return raw_bytes.decode(encoding)
        except Exception:
            continue
    return raw_bytes.decode("utf-8", errors="replace")


def is_html_like(content_type: str, suffix: str) -> bool:
    return (
        "html" in content_type
        or suffix
        in {
            ".html",
            ".htm",
            ".shtml",
            ".shtm",
            ".jsp",
            ".aspx",
            ".asp",
            ".php",
            ".psp",
        }
        or not suffix
    )


def is_office_binary(content_type: str, suffix: str, raw_bytes: bytes) -> bool:
    return (
        raw_bytes.startswith(b"\xd0\xcf\x11\xe0")
        or "msword" in content_type
        or "excel" in content_type
        or "spreadsheet" in content_type
        or suffix in {".doc", ".xls"}
    )


def is_image_binary(content_type: str, suffix: str, raw_bytes: bytes) -> bool:
    return (
        content_type.startswith("image/")
        or suffix in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
        or raw_bytes.startswith(b"\x89PNG")
    )


def suffix_for(url: str, content_type: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower().lstrip(".")
    if suffix and 1 <= len(suffix) <= 8:
        return sanitize_suffix(suffix)
    content_type = content_type.lower()
    if "pdf" in content_type:
        return "pdf"
    if "json" in content_type:
        return "json"
    if "excel" in content_type or "spreadsheet" in content_type:
        return "xls"
    if "word" in content_type:
        return "doc"
    if "png" in content_type:
        return "png"
    if "jpeg" in content_type or "jpg" in content_type:
        return "jpg"
    if "html" in content_type:
        return "html"
    return "bin"


def sanitize_suffix(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", value) or "bin"


def infer_content_type(url: str, file_name: str) -> str:
    suffix = Path(file_name or urlparse(url).path).suffix.lower()
    return {
        ".pdf": "application/pdf",
        ".json": "application/json",
        ".html": "text/html",
        ".htm": "text/html",
        ".shtml": "text/html",
        ".txt": "text/plain",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }.get(suffix, "")


def find_cached_raw(raw_dir: Path, file_stem: str) -> Path | None:
    matches = sorted(
        path
        for path in raw_dir.glob(f"{file_stem}.*")
        if path.suffix not in {".txt", ".json"} or not path.name.endswith(".metadata.json")
    )
    for path in matches:
        if not path.name.endswith(".metadata.json") and path.suffix != ".txt":
            return path
    return None


def load_previous_archive_urls(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {text(row.get("source_url")) for row in read_csv_rows(path) if text(row.get("source_url"))}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    tmp_path.replace(path)


def write_report(path: Path, manifest: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    status_counts = Counter(row["crawl_status"] for row in rows)
    domain_counts = Counter(row["source_domain"] for row in rows)
    lines = [
        "# Major Risk Source Archive",
        "",
        f"- Built at: {manifest['generated_at']}",
        f"- Archive rows: {manifest['row_counts']['archive_rows']}",
        f"- Successful or cached: {manifest['row_counts']['successful_or_cached']}",
        f"- With extracted text: {manifest['row_counts']['with_text']}",
        f"- Failed: {manifest['row_counts']['failed']}",
        "",
        "## Crawl Status",
        "",
        "| status | rows |",
        "|---|---:|",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## Top Domains", "", "| domain | rows |", "|---|---:|"])
    for domain, count in domain_counts.most_common(30):
        lines.append(f"| {domain} | {count} |")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Archive CSV: `{manifest['outputs']['archive_csv']}`",
            f"- Raw directory: `{manifest['outputs']['raw_dir']}`",
            f"- Manifest: `{manifest['outputs']['manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- This archive targets source-document URL rows that have no local raw/text path in the review-release index, plus URLs already present in the previous archive CSV.",
            "- `raw_path` stores the fetched bytes. `text_path` is populated for HTML, JSON, text, and text-extractable PDFs.",
            "",
        ]
    )
    write_text_atomic(path, "\n".join(lines))


def write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def split_values(value: Any) -> list[str]:
    return [part.strip() for part in text(value).split("|") if part.strip()]


def join_sorted(values: Iterable[Any]) -> str:
    return "|".join(sorted({text(value) for value in values if text(value)}))


def join_sample(values: Iterable[Any], *, limit: int) -> str:
    return "|".join(sorted({text(value) for value in values if text(value)})[:limit])


def normalize_space(value: str) -> str:
    lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line)


def header_value(headers: dict[str, str] | None, key: str) -> str:
    if not headers:
        return ""
    return text(headers.get(key.lower()) or headers.get(key) or "")


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def stable_id(prefix: str, *parts: Any) -> str:
    key = "|".join(text(part) for part in parts)
    return prefix + ":" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def archive_file_stem(archive_id: str) -> str:
    return archive_id.replace(":", "_")


def path_key(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def to_int(value: Any, *, default: int = 0) -> int:
    try:
        value_text = text(value)
        return int(float(value_text)) if value_text else default
    except (TypeError, ValueError):
        return default


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Archive unresolved major-risk source URLs.")
    parser.add_argument("--source-index-csv", type=Path, default=DEFAULT_SOURCE_INDEX_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=20)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--refresh", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_major_risk_source_archive(
        source_index_csv=args.source_index_csv,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        raw_root=args.raw_root,
        generated_at=args.generated_at,
        run_id=args.run_id,
        timeout_seconds=args.timeout_seconds,
        sleep_seconds=args.sleep_seconds,
        limit=args.limit,
        refresh=args.refresh,
    )
    print(
        json.dumps(
            {
                "dataset": "major_risk_source_archive",
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
                "crawl_status_counts": manifest["crawl_status_counts"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
