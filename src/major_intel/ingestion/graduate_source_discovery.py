from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_DIR = ROOT / "data/processed/graduate_outcomes"
DEFAULT_OUTPUT_DIR = ROOT / "data/processed/graduate_source_discovery"


TASK_FILES = {
    "graduate_discovery_tasks_2024_2026.csv": "discovery_tasks_2024_2026.csv",
    "graduate_recommendation_discovery_tasks_2024_2026.csv": (
        "discovery_tasks_recommendation_exemption_recommended_2024_2026.csv"
    ),
    "graduate_official_site_discovery_queue_2026.csv": (
        "official_site_discovery_queue_recommendation_exemption.csv"
    ),
    "graduate_school_official_sites_2026.csv": "school_official_sites_recommended_laosheng.csv",
}

SEARCH_RESULT_FILES = [
    "search_results_recommendation_exemption_probe.csv",
    "search_results_recommendation_exemption_probe_zh_market.csv",
    "search_results_recommendation_duck_probe.csv",
    "search_results_recommendation_exemption_probe_bing_html.csv",
]

SEED_FILES = [
    "official_site_recommendation_probe_seeds.csv",
    "seeds_recommendation_exemption_probe.csv",
    "gaokao_homepage_file_seed.csv",
    "gaokao_probe_seed.csv",
    "official_site_seeds_recommended_laosheng_0_20.csv",
    "official_site_seeds_recommended_laosheng_0_20_portal.csv",
    "official_site_seeds_recommended_laosheng_0_80.csv",
    "official_site_seeds_recommended_laosheng_1_5_candidate.csv",
    "official_site_seeds_recommended_laosheng_1_5_candidate_ssl.csv",
    "official_site_seeds_recommended_laosheng_1_5_candidate_ssl_http.csv",
    "official_site_seeds_recommended_laosheng_50_50_workers.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def file_info(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _path_key(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def _jsonl_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _host(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except ValueError:
        return ""


def _is_likely_school_or_official_host(host: str) -> bool:
    return host.endswith(".edu.cn") or host.endswith(".edu") or "chsi.com.cn" in host


def _copy_task_files(input_dir: Path, output_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for output_name, input_name in TASK_FILES.items():
        source = input_dir / input_name
        target = output_dir / output_name
        if source.exists():
            shutil.copyfile(source, target)
            counts[output_name] = _csv_row_count(target)
        else:
            counts[output_name] = 0
    return counts


def _task_summary_rows(task_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, str, str], int] = defaultdict(int)
    for row in task_rows:
        grouped[
            (
                row.get("province", ""),
                row.get("level", ""),
                row.get("year", ""),
                row.get("source_type", ""),
                row.get("document_type", ""),
                row.get("status", ""),
            )
        ] += 1
    return [
        {
            "province": province,
            "level": level,
            "year": year,
            "source_type": source_type,
            "document_type": document_type,
            "status": status,
            "task_count": count,
        }
        for (province, level, year, source_type, document_type, status), count in sorted(grouped.items())
    ]


def _school_summary_rows(task_rows: list[dict[str, str]], official_site_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    site_by_school = {row.get("school_name", ""): row for row in official_site_rows}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in task_rows:
        grouped[row.get("school_name", "")].append(row)
    output: list[dict[str, Any]] = []
    for school_name, rows in sorted(grouped.items()):
        site = site_by_school.get(school_name, {})
        output.append(
            {
                "school_id": rows[0].get("school_id", ""),
                "school_name": school_name,
                "province": rows[0].get("province", ""),
                "level": rows[0].get("level", ""),
                "task_count": len(rows),
                "years": ";".join(sorted({row.get("year", "") for row in rows if row.get("year", "")})),
                "source_types": ";".join(
                    sorted({row.get("source_type", "") for row in rows if row.get("source_type", "")})
                ),
                "document_types": ";".join(
                    sorted({row.get("document_type", "") for row in rows if row.get("document_type", "")})
                ),
                "statuses": ";".join(sorted({row.get("status", "") for row in rows if row.get("status", "")})),
                "has_official_url": str(bool(site.get("official_url", ""))).lower(),
                "official_url": site.get("official_url", ""),
                "official_site_source_url": site.get("source_url", ""),
            }
        )
    return output


def _combined_search_results(input_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for input_name in SEARCH_RESULT_FILES:
        path = input_dir / input_name
        if not path.exists():
            continue
        for row in read_csv(path):
            result_url = row.get("result_url", "")
            host = _host(result_url)
            rows.append(
                {
                    "source_file": _path_key(path),
                    "search_query": row.get("search_query", ""),
                    "result_rank": row.get("result_rank", ""),
                    "result_title": row.get("result_title", ""),
                    "result_url": result_url,
                    "result_host": host,
                    "result_snippet": row.get("result_snippet", ""),
                    "provider": row.get("provider", ""),
                    "captured_at": row.get("captured_at", ""),
                    "likely_official_or_school_host": str(_is_likely_school_or_official_host(host)).lower(),
                }
            )
    return rows


def _search_domain_summary_rows(search_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: Counter[tuple[str, str, str]] = Counter()
    for row in search_rows:
        grouped[
            (
                str(row.get("provider", "")),
                str(row.get("result_host", "")),
                str(row.get("likely_official_or_school_host", "")),
            )
        ] += 1
    return [
        {
            "provider": provider,
            "result_host": host,
            "likely_official_or_school_host": likely,
            "result_count": count,
        }
        for (provider, host, likely), count in sorted(grouped.items(), key=lambda item: (-item[1], item[0]))
    ]


def _combined_seed_rows(input_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for input_name in SEED_FILES:
        path = input_dir / input_name
        if not path.exists():
            continue
        for row in read_csv(path):
            start_url = row.get("start_url", "") or row.get("url", "")
            rows.append(
                {
                    "source_file": _path_key(path),
                    "school_name": row.get("school_name", ""),
                    "source_type": row.get("source_type", ""),
                    "start_url": start_url,
                    "start_host": _host(start_url),
                    "year": row.get("year", ""),
                    "document_type": row.get("document_type", ""),
                    "discovery_query": row.get("discovery_query", ""),
                    "discovery_title": row.get("discovery_title", ""),
                    "discovery_rank": row.get("discovery_rank", ""),
                }
            )
    return rows


def _failure_rows(input_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(input_dir.glob("official_site_seeds_recommended_laosheng_*.failures.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    row = {"raw_line": line}
                url = str(row.get("url", ""))
                rows.append(
                    {
                        "source_file": _path_key(path),
                        "captured_at": row.get("captured_at", ""),
                        "school_name": row.get("school_name", ""),
                        "url": url,
                        "url_host": _host(url),
                        "error_type": row.get("error_type", ""),
                        "status_code": row.get("status_code", ""),
                        "error": row.get("error", ""),
                    }
                )
    return rows


def _source_file_manifest(input_dir: Path, output_dir: Path) -> list[dict[str, Any]]:
    relevant_names = set(TASK_FILES.values()) | set(SEARCH_RESULT_FILES) | set(SEED_FILES)
    relevant_names.update(path.name for path in input_dir.glob("official_site_seeds_recommended_laosheng_*.failures.jsonl"))
    rows: list[dict[str, Any]] = []
    for path in sorted(input_dir.iterdir()):
        if not path.is_file() or path.name not in relevant_names:
            continue
        rows.append(
            {
                "file": _path_key(path),
                "file_name": path.name,
                "file_suffix": path.suffix.lower(),
                "bytes": path.stat().st_size,
                "sha256": file_info(path)["sha256"],
                "row_count": _jsonl_row_count(path) if path.suffix.lower() == ".jsonl" else _csv_row_count(path),
                "role": "source_input",
            }
        )
    for path in sorted(output_dir.iterdir()):
        if path.is_file():
            rows.append(
                {
                    "file": _path_key(path),
                    "file_name": path.name,
                    "file_suffix": path.suffix.lower(),
                    "bytes": path.stat().st_size,
                    "sha256": file_info(path)["sha256"],
                    "row_count": _jsonl_row_count(path) if path.suffix.lower() == ".jsonl" else _csv_row_count(path),
                    "role": "derived_output",
                }
            )
    return rows


def build_graduate_source_discovery(
    *,
    input_dir: Path = DEFAULT_INPUT_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    generated_at: str | None = None,
) -> dict[str, Any]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or date.today().isoformat()

    copied_counts = _copy_task_files(input_dir, output_dir)
    task_rows = read_csv(output_dir / "graduate_discovery_tasks_2024_2026.csv")
    official_site_rows = read_csv(output_dir / "graduate_school_official_sites_2026.csv")
    search_rows = _combined_search_results(input_dir)
    seed_rows = _combined_seed_rows(input_dir)
    failure_rows = _failure_rows(input_dir)

    write_csv(
        output_dir / "graduate_discovery_task_summary_2026.csv",
        _task_summary_rows(task_rows),
        ["province", "level", "year", "source_type", "document_type", "status", "task_count"],
    )
    write_csv(
        output_dir / "graduate_discovery_school_summary_2026.csv",
        _school_summary_rows(task_rows, official_site_rows),
        [
            "school_id",
            "school_name",
            "province",
            "level",
            "task_count",
            "years",
            "source_types",
            "document_types",
            "statuses",
            "has_official_url",
            "official_url",
            "official_site_source_url",
        ],
    )
    write_csv(
        output_dir / "graduate_search_results_probe_2026.csv",
        search_rows,
        [
            "source_file",
            "search_query",
            "result_rank",
            "result_title",
            "result_url",
            "result_host",
            "result_snippet",
            "provider",
            "captured_at",
            "likely_official_or_school_host",
        ],
    )
    write_csv(
        output_dir / "graduate_search_result_domain_summary_2026.csv",
        _search_domain_summary_rows(search_rows),
        ["provider", "result_host", "likely_official_or_school_host", "result_count"],
    )
    write_csv(
        output_dir / "graduate_probe_seed_inventory_2026.csv",
        seed_rows,
        [
            "source_file",
            "school_name",
            "source_type",
            "start_url",
            "start_host",
            "year",
            "document_type",
            "discovery_query",
            "discovery_title",
            "discovery_rank",
        ],
    )
    write_csv(
        output_dir / "graduate_official_site_seed_failures_2026.csv",
        failure_rows,
        ["source_file", "captured_at", "school_name", "url", "url_host", "error_type", "status_code", "error"],
    )
    source_manifest_rows = _source_file_manifest(input_dir, output_dir)
    write_csv(
        output_dir / "graduate_source_discovery_file_manifest_2026.csv",
        source_manifest_rows,
        ["file", "file_name", "file_suffix", "bytes", "sha256", "row_count", "role"],
    )

    output_paths = sorted(path for path in output_dir.iterdir() if path.is_file())
    route_counts = Counter(row.get("source_type", "") for row in task_rows)
    document_type_counts = Counter(row.get("document_type", "") for row in task_rows)
    year_counts = Counter(row.get("year", "") for row in task_rows)
    status_counts = Counter(row.get("status", "") for row in task_rows)
    manifest = {
        "generated_at": generated_at,
        "dataset": "graduate_source_discovery",
        "status": "search_and_seed_queue_no_person_level_rows",
        "source_dir": _path_key(input_dir),
        "row_counts": {
            **copied_counts,
            "graduate_discovery_task_summary_2026.csv": _csv_row_count(
                output_dir / "graduate_discovery_task_summary_2026.csv"
            ),
            "graduate_discovery_school_summary_2026.csv": _csv_row_count(
                output_dir / "graduate_discovery_school_summary_2026.csv"
            ),
            "graduate_search_results_probe_2026.csv": len(search_rows),
            "graduate_search_result_domain_summary_2026.csv": _csv_row_count(
                output_dir / "graduate_search_result_domain_summary_2026.csv"
            ),
            "graduate_probe_seed_inventory_2026.csv": len(seed_rows),
            "graduate_official_site_seed_failures_2026.csv": len(failure_rows),
            "graduate_source_discovery_file_manifest_2026.csv": len(source_manifest_rows),
        },
        "distributions": {
            "task_source_type": dict(sorted(route_counts.items())),
            "task_document_type": dict(sorted(document_type_counts.items())),
            "task_year": dict(sorted(year_counts.items())),
            "task_status": dict(sorted(status_counts.items())),
            "search_likely_official_or_school_host": dict(
                sorted(Counter(row["likely_official_or_school_host"] for row in search_rows).items())
            ),
            "failure_status_code": dict(sorted(Counter(str(row["status_code"]) for row in failure_rows).items())),
        },
        "usage_notes": [
            "Discovery tasks are crawler/search queue rows, not evidence that a source exists.",
            "Search probe results may include irrelevant search-engine noise and need review before crawling.",
            "No person-level graduate outcome rows are included in this package.",
        ],
        "checksums": {_path_key(path): file_info(path) for path in output_paths},
    }
    manifest_path = output_dir / "graduate_source_discovery_manifest_2026.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["checksums"][_path_key(manifest_path)] = file_info(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build graduate official-source discovery queue tables.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--generated-at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    manifest = build_graduate_source_discovery(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        generated_at=args.generated_at,
    )
    print(
        json.dumps(
            {
                "dataset": manifest["dataset"],
                "generated_at": manifest["generated_at"],
                "row_counts": manifest["row_counts"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
