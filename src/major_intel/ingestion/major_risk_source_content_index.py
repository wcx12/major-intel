"""Build searchable content indexes for archived major-risk source texts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ARCHIVE_CSV = (
    ROOT / "data/processed/major_risk_source_archive/major_risk_review_source_archive_2026.csv"
)
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/major_risk_source_content_index"
DEFAULT_REPORT_DIR = ROOT / "reports/major_risk_source_content_index"
SCHEMA_VERSION = "major_risk_source_content_index/v1"

KEYWORD_GROUPS = {
    "risk_adjustment": [
        "\u64a4\u9500",
        "\u505c\u62db",
        "\u505c\u6b62\u62db\u751f",
        "\u6682\u505c\u62db\u751f",
        "\u53d6\u6d88\u62db\u751f",
        "\u9884\u8b66",
        "\u7ea2\u724c",
        "\u9ec4\u724c",
        "\u5931\u4e1a\u98ce\u9669",
        "\u7b7e\u7ea6\u7387",
    ],
    "official_policy": [
        "\u5907\u6848",
        "\u5ba1\u6279",
        "\u65b0\u589e",
        "\u4e13\u4e1a\u8bbe\u7f6e",
        "\u7533\u8bf7\u8868",
        "\u672c\u79d1\u4e13\u4e1a",
        "\u672c\u79d1\u4e13\u4e1a\u76ee\u5f55",
        "\u9ad8\u804c\u4e13\u79d1",
        "\u666e\u901a\u9ad8\u7b49\u5b66\u6821",
    ],
    "employment_signal": [
        "\u5c31\u4e1a",
        "\u6bd5\u4e1a\u751f",
        "\u5c31\u4e1a\u7387",
        "\u7eff\u724c",
        "\u85aa\u916c",
        "\u6536\u5165",
    ],
    "opportunity_signal": [
        "\u4eba\u5de5\u667a\u80fd",
        "\u4f4e\u7a7a",
        "\u751f\u7269\u80b2\u79cd",
        "\u667a\u6167\u80fd\u6e90",
        "\u533b\u7597\u5668\u68b0",
        "\u53e3\u8154\u533b\u5b66",
        "\u96c6\u6210\u7535\u8def",
        "\u65b0\u8d28\u751f\u4ea7\u529b",
    ],
}

KEYWORD_TO_GROUP = {
    keyword: group for group, keywords in KEYWORD_GROUPS.items() for keyword in keywords
}

DOCUMENT_FIELDS = [
    "archive_id",
    "source_url",
    "source_domain",
    "source_title_sample",
    "source_publishers",
    "evidence_families",
    "source_tables",
    "crawl_status",
    "content_type",
    "raw_path",
    "text_path",
    "text_length",
    "text_char_count",
    "paragraph_count",
    "keyword_hit_count",
    "matched_keyword_count",
    "matched_keywords",
    "risk_adjustment_hits",
    "official_policy_hits",
    "employment_signal_hits",
    "opportunity_signal_hits",
    "top_snippet_sample",
]

SNIPPET_FIELDS = [
    "snippet_id",
    "archive_id",
    "source_url",
    "source_domain",
    "source_title_sample",
    "evidence_families",
    "source_tables",
    "keyword_group",
    "keyword",
    "snippet_index",
    "char_start",
    "char_end",
    "snippet_text",
    "raw_path",
    "text_path",
]

KEYWORD_SUMMARY_FIELDS = [
    "keyword_group",
    "keyword",
    "document_count",
    "snippet_count",
    "total_hits",
    "sample_titles",
    "sample_urls",
]


def build_major_risk_source_content_index(
    *,
    archive_csv: Path = DEFAULT_ARCHIVE_CSV,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or date.today().isoformat()
    output_dir = Path(output_dir)
    report_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    archive_rows = list(read_csv_rows(archive_csv))
    document_rows, snippet_rows = build_index_rows(archive_rows)
    keyword_summary_rows = build_keyword_summary_rows(snippet_rows, document_rows)

    documents_csv = output_dir / "major_risk_source_content_documents_2026.csv"
    snippets_csv = output_dir / "major_risk_source_content_snippets_2026.csv"
    keyword_summary_csv = output_dir / "major_risk_source_content_keyword_summary_2026.csv"
    manifest_json = output_dir / "major_risk_source_content_index_manifest_2026.json"
    report_md = report_dir / "major_risk_source_content_index_2026.md"

    write_csv(documents_csv, document_rows, DOCUMENT_FIELDS)
    write_csv(snippets_csv, snippet_rows, SNIPPET_FIELDS)
    write_csv(keyword_summary_csv, keyword_summary_rows, KEYWORD_SUMMARY_FIELDS)

    manifest = {
        "dataset": "major_risk_source_content_index",
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "generated_at": generated_at,
        "inputs": {
            "archive_csv": path_key(archive_csv),
        },
        "outputs": {
            "documents_csv": path_key(documents_csv),
            "snippets_csv": path_key(snippets_csv),
            "keyword_summary_csv": path_key(keyword_summary_csv),
            "manifest_json": path_key(manifest_json),
            "report_md": path_key(report_md),
        },
        "row_counts": {
            "documents": len(document_rows),
            "snippets": len(snippet_rows),
            "keyword_summary": len(keyword_summary_rows),
        },
        "keyword_group_counts": dict(
            sorted(Counter(row["keyword_group"] for row in snippet_rows).items())
        ),
        "document_coverage": {
            "documents_with_text": sum(1 for row in document_rows if to_int(row["text_char_count"])),
            "documents_with_keyword_hits": sum(
                1 for row in document_rows if to_int(row["keyword_hit_count"])
            ),
        },
        "checksums": {
            path_key(documents_csv): file_info(documents_csv),
            path_key(snippets_csv): file_info(snippets_csv),
            path_key(keyword_summary_csv): file_info(keyword_summary_csv),
        },
    }
    manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest["checksums"][path_key(manifest_json)] = file_info(manifest_json)
    manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(report_md, manifest, document_rows, snippet_rows, keyword_summary_rows)
    return manifest


def build_index_rows(
    archive_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    documents: list[dict[str, Any]] = []
    snippets: list[dict[str, Any]] = []
    for archive_row in archive_rows:
        text_path = resolve_path(archive_row.get("text_path"))
        source_text = text_path.read_text(encoding="utf-8", errors="replace") if text_path else ""
        units = text_units(source_text)
        keyword_counts = count_keywords(source_text)
        doc_snippets = snippet_rows_for(archive_row, units)
        snippets.extend(doc_snippets)
        documents.append(document_row(archive_row, source_text, units, keyword_counts, doc_snippets))
    return sorted(documents, key=lambda row: (-to_int(row["keyword_hit_count"]), row["source_url"])), sorted(
        snippets,
        key=lambda row: (row["source_url"], to_int(row["snippet_index"]), row["keyword_group"], row["keyword"]),
    )


def document_row(
    archive_row: dict[str, str],
    source_text: str,
    units: list[dict[str, Any]],
    keyword_counts: dict[str, int],
    snippet_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    group_counts = Counter()
    for keyword, count in keyword_counts.items():
        group_counts[KEYWORD_TO_GROUP[keyword]] += count
    return {
        "archive_id": archive_row.get("archive_id", ""),
        "source_url": archive_row.get("source_url", ""),
        "source_domain": archive_row.get("source_domain", ""),
        "source_title_sample": archive_row.get("source_title_sample", ""),
        "source_publishers": archive_row.get("source_publishers", ""),
        "evidence_families": archive_row.get("evidence_families", ""),
        "source_tables": archive_row.get("source_tables", ""),
        "crawl_status": archive_row.get("crawl_status", ""),
        "content_type": archive_row.get("content_type", ""),
        "raw_path": archive_row.get("raw_path", ""),
        "text_path": archive_row.get("text_path", ""),
        "text_length": archive_row.get("text_length", ""),
        "text_char_count": len(source_text),
        "paragraph_count": len(units),
        "keyword_hit_count": sum(keyword_counts.values()),
        "matched_keyword_count": len(keyword_counts),
        "matched_keywords": "|".join(sorted(keyword_counts)),
        "risk_adjustment_hits": group_counts["risk_adjustment"],
        "official_policy_hits": group_counts["official_policy"],
        "employment_signal_hits": group_counts["employment_signal"],
        "opportunity_signal_hits": group_counts["opportunity_signal"],
        "top_snippet_sample": join_sample(
            [row.get("snippet_text", "") for row in snippet_rows], limit=3
        ),
    }


def snippet_rows_for(
    archive_row: dict[str, str],
    units: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    snippet_index = 0
    for unit in units:
        unit_text = unit["text"]
        matched_keywords = [keyword for keyword in KEYWORD_TO_GROUP if keyword in unit_text]
        if not matched_keywords:
            continue
        snippet_index += 1
        snippet_text = compact_snippet(unit_text)
        for keyword in matched_keywords:
            rows.append(
                {
                    "snippet_id": stable_id(
                        "risk_source_snippet",
                        archive_row.get("archive_id", ""),
                        snippet_index,
                        keyword,
                    ),
                    "archive_id": archive_row.get("archive_id", ""),
                    "source_url": archive_row.get("source_url", ""),
                    "source_domain": archive_row.get("source_domain", ""),
                    "source_title_sample": archive_row.get("source_title_sample", ""),
                    "evidence_families": archive_row.get("evidence_families", ""),
                    "source_tables": archive_row.get("source_tables", ""),
                    "keyword_group": KEYWORD_TO_GROUP[keyword],
                    "keyword": keyword,
                    "snippet_index": snippet_index,
                    "char_start": unit["char_start"],
                    "char_end": unit["char_end"],
                    "snippet_text": snippet_text,
                    "raw_path": archive_row.get("raw_path", ""),
                    "text_path": archive_row.get("text_path", ""),
                }
            )
    return rows


def build_keyword_summary_rows(
    snippet_rows: list[dict[str, Any]],
    document_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    document_lookup = {row["archive_id"]: row for row in document_rows}
    for row in snippet_rows:
        key = (row["keyword_group"], row["keyword"])
        item = grouped.setdefault(
            key,
            {
                "keyword_group": key[0],
                "keyword": key[1],
                "documents": set(),
                "snippet_count": 0,
                "total_hits": 0,
                "sample_titles": set(),
                "sample_urls": set(),
            },
        )
        item["documents"].add(row["archive_id"])
        item["snippet_count"] += 1
        item["total_hits"] += row["snippet_text"].count(row["keyword"])
        doc = document_lookup.get(row["archive_id"], {})
        add_if(item["sample_titles"], doc.get("source_title_sample"))
        add_if(item["sample_urls"], row.get("source_url"))
    return [
        {
            "keyword_group": item["keyword_group"],
            "keyword": item["keyword"],
            "document_count": len(item["documents"]),
            "snippet_count": item["snippet_count"],
            "total_hits": item["total_hits"],
            "sample_titles": join_sample(item["sample_titles"], limit=5),
            "sample_urls": join_sample(item["sample_urls"], limit=5),
        }
        for item in sorted(
            grouped.values(),
            key=lambda row: (row["keyword_group"], -row["snippet_count"], row["keyword"]),
        )
    ]


def text_units(source_text: str) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for match in re.finditer(r"[^\n]+", source_text):
        value = normalize_space(match.group(0))
        if len(value) < 4:
            continue
        units.append({"text": value, "char_start": match.start(), "char_end": match.end()})
    return units


def count_keywords(source_text: str) -> dict[str, int]:
    return {
        keyword: count
        for keyword in KEYWORD_TO_GROUP
        if (count := source_text.count(keyword))
    }


def compact_snippet(value: str, *, max_chars: int = 500) -> str:
    value = normalize_space(value)
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1] + "\u2026"


def resolve_path(path_value: Any) -> Path | None:
    value = text(path_value)
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path if path.exists() else None


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_report(
    path: Path,
    manifest: dict[str, Any],
    document_rows: list[dict[str, Any]],
    snippet_rows: list[dict[str, Any]],
    keyword_summary_rows: list[dict[str, Any]],
) -> None:
    group_counts = Counter(row["keyword_group"] for row in snippet_rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Major Risk Source Content Index",
        "",
        f"- Built at: {manifest['generated_at']}",
        f"- Document rows: {manifest['row_counts']['documents']}",
        f"- Snippet rows: {manifest['row_counts']['snippets']}",
        f"- Keyword summary rows: {manifest['row_counts']['keyword_summary']}",
        f"- Documents with keyword hits: {manifest['document_coverage']['documents_with_keyword_hits']}",
        "",
        "## Keyword Groups",
        "",
        "| group | snippets |",
        "|---|---:|",
    ]
    for group, count in sorted(group_counts.items()):
        lines.append(f"| {group} | {count} |")
    lines.extend(["", "## Top Keywords", "", "| group | keyword | snippets | documents |", "|---|---|---:|---:|"])
    for row in sorted(
        keyword_summary_rows,
        key=lambda item: (-to_int(item["snippet_count"]), item["keyword_group"], item["keyword"]),
    )[:30]:
        lines.append(
            f"| {row['keyword_group']} | {row['keyword']} | {row['snippet_count']} | {row['document_count']} |"
        )
    lines.extend(["", "## Top Documents", "", "| title | keywords | snippets | url |", "|---|---:|---:|---|"])
    snippet_counts = Counter(row["archive_id"] for row in snippet_rows)
    for row in document_rows[:30]:
        lines.append(
            f"| {row['source_title_sample']} | {row['keyword_hit_count']} | "
            f"{snippet_counts[row['archive_id']]} | {row['source_url']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def stable_id(prefix: str, *parts: Any) -> str:
    key = "|".join(text(part) for part in parts)
    return prefix + ":" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def path_key(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", text(value)).strip()


def join_sample(values: Iterable[Any], *, limit: int) -> str:
    return "|".join(sorted({text(value) for value in values if text(value)})[:limit])


def add_if(values: set[str], value: Any) -> None:
    value_text = text(value)
    if value_text:
        values.add(value_text)


def to_int(value: Any, *, default: int = 0) -> int:
    try:
        value_text = text(value)
        return int(float(value_text)) if value_text else default
    except (TypeError, ValueError):
        return default


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build searchable content indexes for archived major-risk sources.")
    parser.add_argument("--archive-csv", type=Path, default=DEFAULT_ARCHIVE_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_major_risk_source_content_index(
        archive_csv=args.archive_csv,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        generated_at=args.generated_at,
    )
    print(
        json.dumps(
            {
                "dataset": "major_risk_source_content_index",
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
                "keyword_group_counts": manifest["keyword_group_counts"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
