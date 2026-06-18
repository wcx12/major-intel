"""Crawl the MOE vocational college major registration query API."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests


SCHEMA_VERSION = "vocational_major_register/v1"
UNIQUE_SCHEMA_VERSION = "vocational_major_unique/v1"
API_BASE = "https://zwfw.moe.gov.cn/eduSearch/api"
REGISTER_PAGE = "https://zwfw.moe.gov.cn/zyyxzy/result.html"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 major-intel/1.0"
)
CSV_FIELDS = [
    "record_id",
    "year",
    "province_name",
    "major_code",
    "major_name",
    "school_code",
    "school_name",
    "school_system",
    "remark",
    "source_level",
    "source_url",
    "captured_at",
]
UNIQUE_CSV_FIELDS = [
    "major_key",
    "year",
    "major_code",
    "major_name",
    "record_count",
    "province_count",
    "school_count",
    "sample_schools",
]


def build_headers() -> dict[str, str]:
    return {
        "User-Agent": DEFAULT_USER_AGENT,
        "Referer": REGISTER_PAGE,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }


def fetch_json(url: str, *, timeout_seconds: float = 30, attempts: int = 3) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, headers=build_headers(), timeout=timeout_seconds)
            response.raise_for_status()
            response.encoding = "utf-8"
            data = response.json()
            if not data.get("success"):
                raise RuntimeError(f"MOE API returned failure for {url}: {data.get('msg')}")
            return data
        except (requests.RequestException, ValueError, RuntimeError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(min(2 * attempt, 6))
    raise RuntimeError(f"failed to fetch {url} after {attempts} attempts: {last_error}") from last_error


def fetch_years(*, timeout_seconds: float = 30) -> list[str]:
    data = fetch_json(f"{API_BASE}/years", timeout_seconds=timeout_seconds)
    return [str(year) for year in data.get("data") or []]


def fetch_provinces(*, timeout_seconds: float = 30) -> list[dict[str, str]]:
    data = fetch_json(f"{API_BASE}/provinces", timeout_seconds=timeout_seconds)
    return [{"code": str(item.get("code", "")), "name": str(item.get("name", ""))} for item in data.get("data") or []]


def register_url(*, year: str, page: int, page_size: int = 50, province: str | None = None) -> str:
    params: dict[str, str | int] = {"year": year, "page": page, "pageSize": page_size}
    if province:
        params["province"] = province
    return f"{API_BASE}/major-register?{urlencode(params)}"


def fetch_register_page(
    *,
    year: str,
    page: int,
    page_size: int = 50,
    province: str | None = None,
    timeout_seconds: float = 30,
) -> dict[str, Any]:
    return fetch_json(
        register_url(year=year, page=page, page_size=page_size, province=province),
        timeout_seconds=timeout_seconds,
    )


def normalize_register_item(
    item: dict[str, Any],
    *,
    year: str,
    source_url: str,
    captured_at: str,
) -> dict[str, Any]:
    major_code = _text(item.get("major_code"))
    major_name = _text(item.get("major_name"))
    school_code = _text(item.get("school_code"))
    school_name = _text(item.get("school_name"))
    school_system = _text(item.get("school_system"))
    province_name = _text(item.get("prov_name"))
    record_id = "vocational_major:" + _sha256_text(
        "|".join([year, province_name, major_code, major_name, school_code, school_name, school_system])
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "record_id": record_id,
        "year": year,
        "province_name": province_name,
        "major_code": major_code,
        "major_name": major_name,
        "school_code": school_code,
        "school_name": school_name,
        "school_system": school_system,
        "remark": _text(item.get("remark")),
        "major_level": "高职专科",
        "source_name": "教育部政务服务平台",
        "source_level": "A",
        "source_type": "vocational_major_register",
        "source_url": source_url,
        "captured_at": captured_at,
        "raw_item": item,
    }


def build_unique_major_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in records:
        key = (record["year"], record["major_code"], record["major_name"])
        row = grouped.setdefault(
            key,
            {
                "schema_version": UNIQUE_SCHEMA_VERSION,
                "major_key": "vocational_major_unique:" + _sha256_text("|".join(key)),
                "year": record["year"],
                "major_code": record["major_code"],
                "major_name": record["major_name"],
                "record_count": 0,
                "provinces": set(),
                "schools": set(),
            },
        )
        row["record_count"] += 1
        if record["province_name"]:
            row["provinces"].add(record["province_name"])
        if record["school_name"]:
            row["schools"].add(record["school_name"])

    rows: list[dict[str, Any]] = []
    for row in grouped.values():
        schools = sorted(row.pop("schools"))
        provinces = sorted(row.pop("provinces"))
        row["province_count"] = len(provinces)
        row["school_count"] = len(schools)
        row["sample_schools"] = "、".join(schools[:5])
        rows.append(row)
    return sorted(rows, key=lambda item: (item["year"], item["major_code"], item["major_name"]))


def crawl_vocational_major_register(
    *,
    year: str,
    raw_dir: Path,
    processed_dir: Path,
    logs_dir: Path,
    reports_dir: Path,
    run_id: str,
    page_size: int = 50,
    max_pages: int | None = None,
    workers: int = 4,
    timeout_seconds: float = 30,
    sleep_seconds: float = 0.0,
) -> dict[str, Any]:
    raw_run_dir = raw_dir / run_id
    raw_run_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    captured_at = datetime.now(timezone.utc).astimezone().isoformat()
    failures_path = logs_dir / f"{run_id}_failures.jsonl"
    manifest_path = logs_dir / f"{run_id}_manifest.json"
    records_jsonl = processed_dir / f"vocational_major_records_{run_id}.jsonl"
    records_csv = processed_dir / f"vocational_major_records_{run_id}.csv"
    unique_csv = processed_dir / f"vocational_major_unique_{run_id}.csv"
    coverage_report = reports_dir / f"vocational_major_register_coverage_{run_id}.md"

    years = fetch_years(timeout_seconds=timeout_seconds)
    provinces = fetch_provinces(timeout_seconds=timeout_seconds)
    _write_json(raw_run_dir / "years.json", years)
    _write_json(raw_run_dir / "provinces.json", provinces)
    if year not in years:
        raise ValueError(f"year {year} is not available from MOE API; available years: {years}")

    first = fetch_register_page(
        year=year,
        page=1,
        page_size=page_size,
        timeout_seconds=timeout_seconds,
    )
    first_payload = first["data"]
    total = int(first_payload.get("total") or 0)
    api_page_size = int(first_payload.get("pageSize") or page_size)
    total_pages = math.ceil(total / api_page_size) if api_page_size else 0
    if max_pages is not None:
        total_pages = min(total_pages, max_pages)

    records = [
        normalize_register_item(
            item,
            year=year,
            source_url=register_url(year=year, page=1, page_size=page_size),
            captured_at=captured_at,
        )
        for item in first_payload.get("list") or []
    ]
    _write_json(raw_run_dir / f"{year}_page_000001.json", first)
    failures: list[dict[str, Any]] = []

    pages = list(range(2, total_pages + 1))
    if workers <= 1:
        for page in pages:
            try:
                records.extend(
                    _fetch_and_normalize_page(
                        year=year,
                        page=page,
                        page_size=page_size,
                        raw_run_dir=raw_run_dir,
                        captured_at=captured_at,
                        timeout_seconds=timeout_seconds,
                    )
                )
            except Exception as exc:  # pragma: no cover - covered by integration runs.
                failures.append({"page": page, "error": str(exc)})
            if sleep_seconds:
                time.sleep(sleep_seconds)
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_page = {
                executor.submit(
                    _fetch_and_normalize_page,
                    year=year,
                    page=page,
                    page_size=page_size,
                    raw_run_dir=raw_run_dir,
                    captured_at=captured_at,
                    timeout_seconds=timeout_seconds,
                ): page
                for page in pages
            }
            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    records.extend(future.result())
                except Exception as exc:
                    failures.append({"page": page, "error": str(exc)})
                if sleep_seconds:
                    time.sleep(sleep_seconds)

    records.sort(key=lambda item: (item["year"], item["province_name"], item["major_code"], item["school_name"], item["school_system"]))
    unique_rows = build_unique_major_rows(records)
    _write_jsonl(records_jsonl, records)
    _write_csv(records_csv, records, CSV_FIELDS)
    _write_csv(unique_csv, unique_rows, UNIQUE_CSV_FIELDS)
    _write_jsonl(failures_path, failures)
    _write_coverage_report(
        coverage_report,
        year=year,
        total=total,
        crawled_records=len(records),
        unique_count=len(unique_rows),
        page_count=total_pages,
        failure_count=len(failures),
    )

    manifest = {
        "run_id": run_id,
        "year": year,
        "source": REGISTER_PAGE,
        "records_jsonl": str(records_jsonl),
        "records_csv": str(records_csv),
        "unique_csv": str(unique_csv),
        "coverage_report": str(coverage_report),
        "raw_dir": str(raw_run_dir),
        "total_reported": total,
        "record_count": len(records),
        "unique_major_count": len(unique_rows),
        "page_count": total_pages,
        "failure_count": len(failures),
        "finished_at": datetime.now(timezone.utc).astimezone().isoformat(),
    }
    _write_json(manifest_path, manifest)
    return manifest


def repair_vocational_major_register_run(
    *,
    year: str,
    base_run_id: str,
    raw_dir: Path,
    processed_dir: Path,
    logs_dir: Path,
    reports_dir: Path,
    run_id: str,
    pages: list[int],
    page_size: int = 50,
    timeout_seconds: float = 30,
    sleep_seconds: float = 0.0,
) -> dict[str, Any]:
    if not pages:
        raise ValueError("at least one page is required for repair")

    raw_run_dir = raw_dir / run_id
    raw_run_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_records_jsonl = processed_dir / f"vocational_major_records_{base_run_id}.jsonl"
    base_manifest_path = logs_dir / f"{base_run_id}_manifest.json"
    if not base_records_jsonl.exists():
        raise FileNotFoundError(f"base records file not found: {base_records_jsonl}")
    if not base_manifest_path.exists():
        raise FileNotFoundError(f"base manifest file not found: {base_manifest_path}")

    base_manifest = json.loads(base_manifest_path.read_text(encoding="utf-8"))
    total = int(base_manifest.get("total_reported") or 0)
    page_count = int(base_manifest.get("page_count") or 0)
    repair_pages = sorted({int(page) for page in pages if int(page) > 0})
    captured_at = datetime.now(timezone.utc).astimezone().isoformat()

    failures_path = logs_dir / f"{run_id}_failures.jsonl"
    manifest_path = logs_dir / f"{run_id}_manifest.json"
    records_jsonl = processed_dir / f"vocational_major_records_{run_id}.jsonl"
    records_csv = processed_dir / f"vocational_major_records_{run_id}.csv"
    unique_csv = processed_dir / f"vocational_major_unique_{run_id}.csv"
    coverage_report = reports_dir / f"vocational_major_register_coverage_{run_id}.md"

    records = [record for record in _read_jsonl(base_records_jsonl) if _record_page(record) not in repair_pages]
    failures: list[dict[str, Any]] = []
    for page in repair_pages:
        try:
            records.extend(
                _fetch_and_normalize_page(
                    year=year,
                    page=page,
                    page_size=page_size,
                    raw_run_dir=raw_run_dir,
                    captured_at=captured_at,
                    timeout_seconds=timeout_seconds,
                )
            )
        except Exception as exc:  # pragma: no cover - covered by integration runs.
            failures.append({"page": page, "error": str(exc)})
        if sleep_seconds:
            time.sleep(sleep_seconds)

    records = sorted(
        records,
        key=lambda item: (item["year"], item["province_name"], item["major_code"], item["school_name"], item["school_system"]),
    )
    unique_rows = build_unique_major_rows(records)
    _write_jsonl(records_jsonl, records)
    _write_csv(records_csv, records, CSV_FIELDS)
    _write_csv(unique_csv, unique_rows, UNIQUE_CSV_FIELDS)
    _write_jsonl(failures_path, failures)
    _write_coverage_report(
        coverage_report,
        year=year,
        total=total,
        crawled_records=len(records),
        unique_count=len(unique_rows),
        page_count=page_count,
        failure_count=len(failures),
    )

    manifest = {
        "run_id": run_id,
        "base_run_id": base_run_id,
        "year": year,
        "source": REGISTER_PAGE,
        "records_jsonl": str(records_jsonl),
        "records_csv": str(records_csv),
        "unique_csv": str(unique_csv),
        "coverage_report": str(coverage_report),
        "raw_dir": str(raw_run_dir),
        "repair_pages": repair_pages,
        "total_reported": total,
        "record_count": len(records),
        "unique_major_count": len(unique_rows),
        "page_count": page_count,
        "failure_count": len(failures),
        "finished_at": datetime.now(timezone.utc).astimezone().isoformat(),
    }
    _write_json(manifest_path, manifest)
    return manifest


def read_failure_pages(path: Path) -> list[int]:
    pages: list[int] = []
    for row in _read_jsonl(path):
        page = row.get("page")
        if page is not None:
            pages.append(int(page))
    return sorted(set(pages))


def _fetch_and_normalize_page(
    *,
    year: str,
    page: int,
    page_size: int,
    raw_run_dir: Path,
    captured_at: str,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    data = fetch_register_page(
        year=year,
        page=page,
        page_size=page_size,
        timeout_seconds=timeout_seconds,
    )
    _write_json(raw_run_dir / f"{year}_page_{page:06d}.json", data)
    return [
        normalize_register_item(
            item,
            year=year,
            source_url=register_url(year=year, page=page, page_size=page_size),
            captured_at=captured_at,
        )
        for item in data["data"].get("list") or []
    ]


def _write_coverage_report(
    path: Path,
    *,
    year: str,
    total: int,
    crawled_records: int,
    unique_count: int,
    page_count: int,
    failure_count: int,
) -> None:
    path.write_text(
        "\n".join(
            [
                "# 高职专科专业设置备案覆盖报告",
                "",
                f"- 年份：{year}",
                f"- API 报告记录数：{total}",
                f"- 已抓取记录数：{crawled_records}",
                f"- 去重专业数：{unique_count}",
                f"- 分页数：{page_count}",
                f"- 失败页数：{failure_count}",
                "",
                "来源：教育部政务服务平台“高等职业教育专科专业设置备案结果查询”。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _record_page(record: dict[str, Any]) -> int | None:
    source_url = _text(record.get("source_url"))
    if not source_url:
        return None
    values = parse_qs(urlparse(source_url).query).get("page")
    if not values:
        return None
    try:
        return int(values[0])
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Crawl MOE vocational major register records.")
    parser.add_argument("--year", default="2026")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/vocational_major_register"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/vocational_major_register"))
    parser.add_argument("--logs-dir", type=Path, default=Path("data/logs/vocational_major_register"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports/vocational_major_register"))
    parser.add_argument("--run-id", default="vocational_major_register")
    parser.add_argument("--page-size", type=int, default=50)
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--base-run-id")
    parser.add_argument("--failure-jsonl", type=Path)
    parser.add_argument("--repair-page", type=int, action="append", dest="repair_pages", default=[])
    args = parser.parse_args(argv)

    if args.base_run_id:
        repair_pages = list(args.repair_pages or [])
        if args.failure_jsonl:
            repair_pages.extend(read_failure_pages(args.failure_jsonl))
        manifest = repair_vocational_major_register_run(
            year=args.year,
            base_run_id=args.base_run_id,
            raw_dir=args.raw_dir,
            processed_dir=args.processed_dir,
            logs_dir=args.logs_dir,
            reports_dir=args.reports_dir,
            run_id=args.run_id,
            pages=repair_pages,
            page_size=args.page_size,
            timeout_seconds=args.timeout_seconds,
            sleep_seconds=args.sleep_seconds,
        )
    else:
        manifest = crawl_vocational_major_register(
            year=args.year,
            raw_dir=args.raw_dir,
            processed_dir=args.processed_dir,
            logs_dir=args.logs_dir,
            reports_dir=args.reports_dir,
            run_id=args.run_id,
            page_size=args.page_size,
            max_pages=args.max_pages,
            workers=args.workers,
            timeout_seconds=args.timeout_seconds,
            sleep_seconds=args.sleep_seconds,
        )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
