"""Fetch and normalize rysxai major-level market observation data.

The data handled here is source-level C: useful for market observation, not
official school-major employment evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://api.rysxai.cn/api"
INFO_PATH = "/ry_education/profession/info/"
POSITIONS_PATH = "/ry_education/profession/positions/"
SELECTS_PATH = "/ry_education/profession/search/selects/"
SEARCH_PATH = "/ry_education/profession/search/"
SCHEMA_VERSION = "rysxai_market_snapshot/v1"
BLOCKING_STATUS_CODES = {401, 403}
THROTTLE_STATUS_CODES = {429}
PROFESSION_CSV_FIELDS = [
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "category",
    "subject",
    "degree",
    "limit_year",
    "heat",
    "is_hot",
]


class FetchError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def normalize_profession_info(payload: dict[str, Any], captured_at: str) -> dict[str, Any]:
    data = _expect_success(payload)

    return {
        "captured_at": captured_at,
        "profession": {
            "id": data.get("id"),
            "name": data.get("name"),
            "code": data.get("code"),
            "level": data.get("level"),
            "degree": data.get("degree"),
            "limit_year": data.get("limit_year"),
            "selection_advice": data.get("sel_adv"),
        },
        "macro_employment": {
            "industry_distribution": _parse_jobdetail_distribution(
                data.get("jobdetail"), "1", "name"
            ),
            "region_distribution": _parse_jobdetail_distribution(
                data.get("jobdetail"), "2", "area"
            ),
            "job_direction_distribution": _parse_job_direction_distribution(
                data.get("jobdetail")
            ),
        },
        "demand_ranking": _parse_ranking(
            data.get("demand_ranking"), "demand_count"
        ),
        "salary_ranking": _parse_ranking(
            data.get("salary_ranking"), "monthly_salary_reference"
        ),
    }


def normalize_job_samples(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = _expect_success(payload)
    items = data.get("items") or []
    samples = []

    for item in items:
        source = item.get("_source") or {}
        samples.append(
            {
                "source_item_id": item.get("itemId"),
                "job_title": item.get("jobName") or source.get("title"),
                "company_name": source.get("company_name") or item.get("brandName"),
                "city": item.get("cityName") or source.get("c1"),
                "district": item.get("areaDistrict") or source.get("c2"),
                "industry": item.get("brandIndustry"),
                "salary_raw": source.get("salary_raw") or item.get("salaryDesc"),
                "monthly_salary_min": _to_int(source.get("salary_first")),
                "monthly_salary_max": _to_int(source.get("salary_last")),
                "education": item.get("jobDegree"),
                "experience": item.get("jobExperience"),
                "skills": _as_list(item.get("skills")),
                "company_tags": _as_list(source.get("company_tag")),
                "company_scale": item.get("brandScaleName"),
                "financing_stage": item.get("brandStageName"),
                "source_level": "C",
                "data_scope": "recruiting_market_sample",
            }
        )

    return samples


def build_market_snapshot(
    info_payload: dict[str, Any],
    positions_payload: dict[str, Any],
    captured_at: str,
) -> dict[str, Any]:
    info = normalize_profession_info(info_payload, captured_at)
    samples = normalize_job_samples(positions_payload)
    profession_id = info["profession"].get("id")

    return {
        "schema_version": SCHEMA_VERSION,
        "captured_at": captured_at,
        "source": {
            "name": "rysxai",
            "source_level": "C",
            "data_scope": "major_level_market_observation",
            "api_base": API_BASE,
            "info_url": _build_url(INFO_PATH, {"id": profession_id}),
            "positions_url": _build_url(POSITIONS_PATH, {"id": profession_id}),
        },
        "profession": info["profession"],
        "macro_employment": info["macro_employment"],
        "demand_ranking": info["demand_ranking"],
        "salary_ranking": info["salary_ranking"],
        "job_posting_sample_total_reported": _reported_total(positions_payload),
        "job_posting_sample_count": len(samples),
        "job_posting_samples": samples,
        "salary_observations_by_city": _aggregate_salary_by(samples, "city"),
        "salary_observations_by_industry": _aggregate_salary_by(samples, "industry"),
        "warnings": [
            "招聘岗位和薪资样本只能作为专业市场观察，不代表某校某专业毕业生实际薪资或就业去向。",
            "宏观就业分布来自第三方站内数据，应与官方就业质量报告分级存储、分开展示。",
        ],
    }


def crawl_profession(
    profession_id: int,
    raw_dir: Path,
    processed_dir: Path,
    timeout_seconds: float = 20,
    run_id: str | None = None,
    fetcher= None,
    max_retries: int = 2,
    retry_base_seconds: float = 5,
    sleeper = time.sleep,
) -> Path:
    captured_at = _now_iso()
    raw_run_dir = raw_dir / (run_id or _safe_timestamp(captured_at))
    raw_run_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    info_url = _build_url(INFO_PATH, {"id": profession_id})
    positions_url = _build_url(POSITIONS_PATH, {"id": profession_id})

    actual_fetcher = fetcher or fetch_json
    info_payload = fetch_json_with_retries(
        info_url,
        timeout_seconds=timeout_seconds,
        fetcher=actual_fetcher,
        max_retries=max_retries,
        retry_base_seconds=retry_base_seconds,
        sleeper=sleeper,
    )
    positions_payload = fetch_json_with_retries(
        positions_url,
        timeout_seconds=timeout_seconds,
        fetcher=actual_fetcher,
        max_retries=max_retries,
        retry_base_seconds=retry_base_seconds,
        sleeper=sleeper,
    )

    _write_json(raw_run_dir / f"profession_{profession_id}_info.raw.json", info_payload)
    _write_json(
        raw_run_dir / f"profession_{profession_id}_positions.raw.json",
        positions_payload,
    )

    snapshot = build_market_snapshot(info_payload, positions_payload, captured_at)
    output_path = processed_dir / f"profession_{profession_id}_market_snapshot.json"
    _write_json(output_path, snapshot)
    return output_path


def list_professions_from_api(
    fetcher = None,
    timeout_seconds: float = 20,
) -> list[dict[str, Any]]:
    actual_fetcher = fetcher or fetch_json
    selects_payload = fetch_json_with_retries(
        _build_url(SELECTS_PATH),
        timeout_seconds=timeout_seconds,
        fetcher=actual_fetcher,
    )
    selects = _expect_success_data(selects_payload)
    if not isinstance(selects, list):
        raise ValueError("Unexpected profession selects shape.")

    by_id: dict[int, dict[str, Any]] = {}
    hot_ids: set[int] = set()
    level_order = {"本科": 0, "专科": 1}

    for level_item in selects:
        level_name = level_item.get("name")
        for category_item in level_item.get("category_list") or []:
            category = category_item.get("name")
            search_payload = fetch_json_with_retries(
                _build_url(SEARCH_PATH, {"level": level_name, "category": category}),
                timeout_seconds=timeout_seconds,
                fetcher=actual_fetcher,
            )
            groups = _expect_success_data(search_payload)
            if not isinstance(groups, list):
                continue
            for group in groups:
                group_subject = group.get("subject")
                is_hot_group = group_subject == "热门"
                for item in group.get("profession_list") or []:
                    profession_id = _to_int(item.get("id"))
                    if profession_id is None:
                        continue
                    if is_hot_group:
                        hot_ids.add(profession_id)
                    subject = item.get("subject") or group_subject
                    row = {
                        "rysxai_profession_id": profession_id,
                        "major_code": item.get("code") or "",
                        "major_name": item.get("name") or "",
                        "level": item.get("level") or level_name or "",
                        "category": item.get("category") or category or "",
                        "subject": subject or "",
                        "degree": item.get("degree") or "",
                        "limit_year": item.get("limit_year") or "",
                        "heat": item.get("heat") if item.get("heat") is not None else "",
                        "is_hot": "false",
                    }
                    existing = by_id.get(profession_id)
                    if existing is None or (
                        existing.get("subject") == "热门" and not is_hot_group
                    ):
                        by_id[profession_id] = row

    for profession_id in hot_ids:
        if profession_id in by_id:
            by_id[profession_id]["is_hot"] = "true"

    return sorted(
        by_id.values(),
        key=lambda row: (
            level_order.get(str(row.get("level")), 99),
            str(row.get("major_code") or ""),
            int(row.get("rysxai_profession_id") or 0),
        ),
    )


def write_profession_list_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=PROFESSION_CSV_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def should_skip_profession(
    profession_id: int,
    processed_dir: Path,
    resume: bool,
) -> bool:
    return resume and (
        processed_dir / f"profession_{profession_id}_market_snapshot.json"
    ).exists()


def fetch_json(url: str, timeout_seconds: float = 20) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "MajorIntelDataProbe/0.1",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return json.loads(response.read().decode(charset))
    except HTTPError as exc:
        raise FetchError(
            f"HTTP {exc.code} while fetching {url}",
            status_code=exc.code,
        ) from exc
    except URLError as exc:
        raise FetchError(f"Network error while fetching {url}: {exc}") from exc


def fetch_json_with_retries(
    url: str,
    timeout_seconds: float = 20,
    fetcher = None,
    max_retries: int = 2,
    retry_base_seconds: float = 5,
    sleeper = time.sleep,
) -> dict[str, Any]:
    actual_fetcher = fetcher or fetch_json
    attempt = 0
    while True:
        try:
            return actual_fetcher(url, timeout_seconds)
        except FetchError as exc:
            if exc.status_code in BLOCKING_STATUS_CODES:
                raise
            if attempt >= max_retries:
                raise
            delay = retry_base_seconds * (2**attempt)
            if exc.status_code in THROTTLE_STATUS_CODES:
                delay = max(delay, 60)
            sleeper(delay)
            attempt += 1


def read_profession_rows(
    input_csv: Path | None,
    ids: list[int],
    level: str | None = None,
) -> list[dict[str, Any]]:
    rows = [
        {
            "rysxai_profession_id": profession_id,
            "level": "",
            "major_code": "",
            "major_name": "",
        }
        for profession_id in ids
    ]
    if input_csv is not None:
        with input_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                value = row.get("rysxai_profession_id") or row.get("profession_id")
                if value:
                    row["rysxai_profession_id"] = int(value)
                    rows.append(row)

    deduped: dict[int, dict[str, Any]] = {}
    for row in rows:
        profession_id = _to_int(row.get("rysxai_profession_id"))
        if profession_id is None:
            continue
        if level and row.get("level") and row.get("level") != level:
            continue
        row["rysxai_profession_id"] = profession_id
        deduped[profession_id] = row
    return [deduped[key] for key in sorted(deduped)]


def read_profession_ids(input_csv: Path | None, ids: list[int]) -> list[int]:
    return [row["rysxai_profession_id"] for row in read_profession_rows(input_csv, ids)]


def crawl_profession_batch(
    profession_rows: list[dict[str, Any]],
    raw_dir: Path,
    processed_dir: Path,
    logs_dir: Path,
    reports_dir: Path | None = None,
    resume: bool = False,
    max_count: int | None = None,
    sleep_seconds: float = 1,
    timeout_seconds: float = 20,
    run_id: str | None = None,
    max_retries: int = 2,
    retry_base_seconds: float = 5,
    max_consecutive_errors: int = 20,
    fetcher = None,
    sleeper = time.sleep,
    progress: bool = False,
) -> dict[str, Any]:
    actual_run_id = run_id or _safe_timestamp(_now_iso())
    logs_dir.mkdir(parents=True, exist_ok=True)
    failure_log = logs_dir / f"{actual_run_id}_failures.jsonl"
    manifest_path = logs_dir / f"{actual_run_id}_manifest.json"

    selected_rows = profession_rows[:max_count] if max_count else profession_rows
    manifest: dict[str, Any] = {
        "run_id": actual_run_id,
        "started_at": _now_iso(),
        "finished_at": None,
        "requested_count": len(profession_rows),
        "selected_count": len(selected_rows),
        "success_count": 0,
        "skipped_count": 0,
        "failure_count": 0,
        "stopped_reason": None,
        "raw_dir": str(raw_dir),
        "processed_dir": str(processed_dir),
        "reports_dir": str(reports_dir) if reports_dir else None,
        "failure_log": str(failure_log),
    }

    consecutive_errors = 0
    for index, row in enumerate(selected_rows, start=1):
        profession_id = int(row["rysxai_profession_id"])
        if should_skip_profession(profession_id, processed_dir, resume=resume):
            manifest["skipped_count"] += 1
            if progress:
                print(f"[{index}/{len(selected_rows)}] skip profession {profession_id}")
            continue

        try:
            output_path = crawl_profession(
                profession_id,
                raw_dir=raw_dir,
                processed_dir=processed_dir,
                timeout_seconds=timeout_seconds,
                run_id=actual_run_id,
                fetcher=fetcher,
                max_retries=max_retries,
                retry_base_seconds=retry_base_seconds,
                sleeper=sleeper,
            )
            if reports_dir is not None:
                _write_report(output_path, reports_dir, profession_id)
            manifest["success_count"] += 1
            if progress:
                print(f"[{index}/{len(selected_rows)}] ok profession {profession_id}")
            consecutive_errors = 0
        except Exception as exc:
            consecutive_errors += 1
            manifest["failure_count"] += 1
            _append_jsonl(
                failure_log,
                {
                    "run_id": actual_run_id,
                    "profession_id": profession_id,
                    "index": index,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "status_code": getattr(exc, "status_code", None),
                    "row": row,
                    "created_at": _now_iso(),
                },
            )
            if progress:
                print(
                    f"[{index}/{len(selected_rows)}] fail profession "
                    f"{profession_id}: {type(exc).__name__}"
                )
            if consecutive_errors >= max_consecutive_errors:
                manifest["stopped_reason"] = (
                    f"max_consecutive_errors:{max_consecutive_errors}"
                )
                break

        if index < len(selected_rows) and sleep_seconds > 0:
            sleeper(sleep_seconds)

    manifest["finished_at"] = _now_iso()
    _write_json(manifest_path, manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl rysxai major market observation snapshots."
    )
    parser.add_argument(
        "--profession-id",
        type=int,
        action="append",
        default=[],
        help="Rysxai profession id. Can be passed multiple times.",
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        help="CSV with rysxai_profession_id or profession_id column.",
    )
    parser.add_argument(
        "--refresh-profession-list",
        type=Path,
        help="Write a full rysxai profession list CSV before crawling.",
    )
    parser.add_argument(
        "--all-professions",
        action="store_true",
        help="Use the refreshed/discovered full profession list as crawl input.",
    )
    parser.add_argument(
        "--level",
        choices=["本科", "专科"],
        help="Filter CSV/discovered professions by level.",
    )
    parser.add_argument(
        "--max-count",
        type=int,
        help="Limit selected professions for smoke tests or chunked runs.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip professions with existing processed snapshots.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw/rysxai"),
        help="Directory for raw API payloads.",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed/rysxai"),
        help="Directory for normalized snapshots.",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=Path("data/logs/rysxai"),
        help="Directory for manifest and failure logs.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        help="When set, also render Markdown reports into this directory.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=1,
        help="Delay between professions.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=20)
    parser.add_argument("--run-id", help="Stable id for this crawl run.")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-base-seconds", type=float, default=5)
    parser.add_argument("--max-consecutive-errors", type=int, default=20)
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Print one progress line per selected profession.",
    )
    args = parser.parse_args(argv)

    discovered_rows: list[dict[str, Any]] = []
    if args.refresh_profession_list or args.all_professions:
        discovered_rows = list_professions_from_api(timeout_seconds=args.timeout_seconds)
        if args.refresh_profession_list:
            write_profession_list_csv(discovered_rows, args.refresh_profession_list)

    if args.all_professions:
        profession_rows = discovered_rows
    else:
        profession_rows = read_profession_rows(
            args.input_csv,
            args.profession_id,
            level=args.level,
        )

    if args.level and args.all_professions:
        profession_rows = [
            row for row in profession_rows if row.get("level") == args.level
        ]

    if not profession_rows:
        if args.refresh_profession_list:
            print(args.refresh_profession_list)
            return 0
        parser.error("Provide --profession-id or --input-csv.")

    manifest = crawl_profession_batch(
        profession_rows,
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        logs_dir=args.logs_dir,
        reports_dir=args.reports_dir,
        resume=args.resume,
        max_count=args.max_count,
        sleep_seconds=args.sleep_seconds,
        timeout_seconds=args.timeout_seconds,
        run_id=args.run_id,
        max_retries=args.max_retries,
        retry_base_seconds=args.retry_base_seconds,
        max_consecutive_errors=args.max_consecutive_errors,
        progress=args.progress,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


def _expect_success_data(payload: dict[str, Any]) -> Any:
    if payload.get("code") != "SUCCESS":
        raise ValueError(f"Unexpected API response code: {payload.get('code')}")
    return payload.get("data")


def _expect_success(payload: dict[str, Any]) -> dict[str, Any]:
    data = _expect_success_data(payload)
    if not isinstance(data, dict):
        raise ValueError("Unexpected API response data shape.")
    return data


def _parse_jobdetail_distribution(
    jobdetail: Any, key: str, label_field: str
) -> list[dict[str, Any]]:
    values = _jobdetail_values(jobdetail, key)
    result = []
    for item in values:
        label = item.get(label_field) or item.get("name") or item.get("area")
        if label:
            result.append(
                {
                    "label": label,
                    "rate_percent": _to_float(item.get("rate")),
                }
            )
    return result


def _parse_job_direction_distribution(jobdetail: Any) -> list[dict[str, Any]]:
    values = _jobdetail_values(jobdetail, "3")
    result = []
    for item in values:
        label = item.get("detail_pos") or item.get("name")
        if not label:
            continue
        result.append(
            {
                "label": label,
                "rate_percent": _to_float(item.get("rate")),
                "detail_jobs": _split_cn_list(item.get("detail_job")),
            }
        )
    return result


def _parse_ranking(ranking: Any, value_key: str) -> list[dict[str, Any]]:
    if not isinstance(ranking, dict):
        return []
    categories = ranking.get("categories") or []
    series = ranking.get("series") or []
    data = series[0].get("data") if series and isinstance(series[0], dict) else []
    return [
        {"region": region, value_key: value}
        for region, value in zip(categories, data)
        if region is not None and value is not None
    ]


def _reported_total(payload: dict[str, Any]) -> int | None:
    data = payload.get("data")
    if not isinstance(data, dict):
        return None
    return _to_int(data.get("total"))


def _aggregate_salary_by(
    samples: list[dict[str, Any]], field: str
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sample in samples:
        key = sample.get(field) or "未知"
        if sample.get("monthly_salary_min") is None or sample.get("monthly_salary_max") is None:
            continue
        grouped[key].append(sample)

    result = {}
    for key, rows in sorted(grouped.items()):
        min_values = [row["monthly_salary_min"] for row in rows]
        max_values = [row["monthly_salary_max"] for row in rows]
        midpoints = [(low + high) / 2 for low, high in zip(min_values, max_values)]
        result[key] = {
            "sample_count": len(rows),
            "monthly_salary_min_observed": min(min_values),
            "monthly_salary_max_observed": max(max_values),
            "monthly_salary_midpoint_avg": round(sum(midpoints) / len(midpoints)),
            "data_scope": "recruiting_market_sample",
            "source_level": "C",
        }
    return result


def _jobdetail_values(jobdetail: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(jobdetail, dict):
        values = jobdetail.get(key) or []
    else:
        values = getattr(jobdetail, key, [])
    return values if isinstance(values, list) else []


def _split_cn_list(value: Any) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return []
    normalized = value.replace("、", "，").replace(",", "，")
    return [part.strip() for part in normalized.split("，") if part.strip()]


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _to_float(value: Any) -> float | None:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _build_url(path: str, params: dict[str, Any] | None = None) -> str:
    if not params:
        return f"{API_BASE}{path}"
    return f"{API_BASE}{path}?{urlencode(params)}"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2)
        handle.write("\n")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True))
        handle.write("\n")


def _write_report(snapshot_path: Path, reports_dir: Path, profession_id: int) -> None:
    try:
        from scripts.rysxai_market_report import load_snapshot, write_markdown_report
    except ModuleNotFoundError:
        from rysxai_market_report import load_snapshot, write_markdown_report

    output_path = reports_dir / f"profession_{profession_id}_market_report.md"
    write_markdown_report(load_snapshot(snapshot_path), output_path)


def _safe_timestamp(value: str) -> str:
    return value.replace(":", "").replace("+", "_")


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
