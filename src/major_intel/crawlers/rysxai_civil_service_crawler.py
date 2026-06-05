"""Fetch 2026 rysxai civil-service role details.

The crawler uses the public detail API observed from the web app. It writes
one JSON record per line so an interrupted run can resume without re-fetching
completed role IDs.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://api.rysxai.cn/api"
INFO_PATH = "/ry_education/civil_servant/info/"
SCHEMA_VERSION = "rysxai_civil_service_role/v1"
DEFAULT_START_ID = 20811
DEFAULT_END_ID = 41524
DEFAULT_OUTPUT_PATH = Path("data/raw/rysxai_civil_service_2026.jsonl")
DEFAULT_FAILURES_PATH = Path("data/logs/rysxai_civil_service_2026_failures.jsonl")
DEFAULT_CSV_PATH = Path("data/processed/rysxai_civil_service_2026.csv")
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
BLOCKING_STATUS_CODES = {401, 403}
ROLE_FIELDS = [
    "id",
    "sheet_type",
    "year",
    "department_code",
    "department_name",
    "sub_department",
    "department_property",
    "job_name",
    "job_property",
    "job_area",
    "job_intro",
    "position_code",
    "department_level",
    "exam_type",
    "plan_num",
    "apply_num",
    "ratio",
    "profession",
    "education_level",
    "edu_lev_lower_limit",
    "degree_requirement",
    "identity",
    "work_year",
    "work_experience",
    "need_test",
    "interview_ratio",
    "work_location",
    "province",
    "residence_location",
    "remark",
    "is_new_graduate",
    "department_website",
    "phone",
    "wuweitu",
    "wuwei_table",
]


class FetchError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class CrawlSummary:
    requested_ids: int
    skipped_existing: int
    fetched: int
    failed: int
    output_path: Path
    failures_path: Path


Fetcher = Callable[[int, float], dict[str, Any]]
Sleeper = Callable[[float], None]


class RequestsDetailFetcher:
    """Fetch role detail with a reusable HTTP session when requests is available."""

    def __init__(self, session: Any | None = None):
        if session is None:
            try:
                import requests
            except ImportError as exc:  # pragma: no cover - exercised only without requests
                raise RuntimeError("requests is not installed") from exc
            session = requests.Session()
        self.session = session

    def __call__(self, role_id: int, timeout_seconds: float = 20) -> dict[str, Any]:
        response = self.session.get(
            build_info_url(role_id),
            timeout=timeout_seconds,
            headers=_request_headers(),
        )
        status_code = getattr(response, "status_code", None)
        if status_code and status_code >= 400:
            raise FetchError(
                f"HTTP {status_code} while fetching role {role_id}",
                status_code=status_code,
            )
        try:
            return response.json()
        except Exception as exc:
            raise FetchError(f"Invalid JSON while fetching role {role_id}") from exc


def normalize_role(
    payload: dict[str, Any],
    fetched_at: str,
    source_url: str,
) -> dict[str, Any]:
    data = _expect_success_data(payload)
    if not isinstance(data, dict):
        raise ValueError("Unexpected civil-service detail shape.")

    return {
        "schema_version": SCHEMA_VERSION,
        "fetched_at": fetched_at,
        "source": {
            "name": "rysxai",
            "source_url": source_url,
            "api_base": API_BASE,
            "data_scope": "civil_service_role_detail",
        },
        "role": dict(data),
    }


def read_completed_ids(jsonl_path: Path) -> set[int]:
    if not jsonl_path.exists():
        return set()

    completed: set[int] = set()
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            role_id = ((record.get("role") or {}).get("id"))
            if isinstance(role_id, int):
                completed.add(role_id)
    return completed


def crawl_id_range(
    start_id: int,
    end_id: int,
    output_path: Path,
    failures_path: Path,
    delay_seconds: float = 0.35,
    jitter_seconds: float = 0.15,
    timeout_seconds: float = 20,
    fetcher: Fetcher | None = None,
    sleeper: Sleeper = time.sleep,
    max_retries: int = 2,
    retry_base_seconds: float = 2,
    progress_every: int = 100,
) -> CrawlSummary:
    if end_id < start_id:
        raise ValueError("end_id must be greater than or equal to start_id.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    failures_path.parent.mkdir(parents=True, exist_ok=True)
    completed = read_completed_ids(output_path)
    base_fetcher = fetcher or _make_default_fetcher()
    actual_fetcher = (
        fetcher
        if fetcher is not None
        else lambda role_id, timeout_seconds=timeout_seconds: fetch_detail_with_retries(
            role_id,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_base_seconds=retry_base_seconds,
            sleeper=sleeper,
            base_fetcher=base_fetcher,
        )
    )

    requested_ids = end_id - start_id + 1
    skipped_existing = 0
    fetched = 0
    failed = 0

    for offset, role_id in enumerate(range(start_id, end_id + 1), start=1):
        if role_id in completed:
            skipped_existing += 1
            continue

        source_url = build_info_url(role_id)
        try:
            payload = actual_fetcher(role_id, timeout_seconds)
            record = normalize_role(payload, _now_iso(), source_url)
            _append_jsonl(output_path, record)
            completed.add(role_id)
            fetched += 1
        except Exception as exc:
            failed += 1
            _append_jsonl(
                failures_path,
                {
                    "id": role_id,
                    "fetched_at": _now_iso(),
                    "source_url": source_url,
                    "status_code": getattr(exc, "status_code", None),
                    "error": str(exc),
                },
            )

        if progress_every > 0 and offset % progress_every == 0:
            print(
                f"progress {offset}/{requested_ids}: fetched={fetched} "
                f"skipped={skipped_existing} failed={failed}",
                flush=True,
            )
        _polite_sleep(delay_seconds, jitter_seconds, sleeper)

    return CrawlSummary(
        requested_ids=requested_ids,
        skipped_existing=skipped_existing,
        fetched=fetched,
        failed=failed,
        output_path=output_path,
        failures_path=failures_path,
    )


def write_csv_from_jsonl(jsonl_path: Path, csv_path: Path) -> int:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["schema_version", "fetched_at", "source_url", *ROLE_FIELDS]
    row_count = 0

    with jsonl_path.open("r", encoding="utf-8") as source, csv_path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for line in source:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            role = record.get("role") or {}
            row = {
                "schema_version": record.get("schema_version"),
                "fetched_at": record.get("fetched_at"),
                "source_url": (record.get("source") or {}).get("source_url"),
            }
            for field in ROLE_FIELDS:
                row[field] = _csv_cell(role.get(field))
            writer.writerow(row)
            row_count += 1
    return row_count


def fetch_detail_with_retries(
    role_id: int,
    timeout_seconds: float = 20,
    max_retries: int = 2,
    retry_base_seconds: float = 2,
    sleeper: Sleeper = time.sleep,
    base_fetcher: Fetcher | None = None,
) -> dict[str, Any]:
    actual_fetcher = base_fetcher or fetch_detail
    for attempt in range(max_retries + 1):
        try:
            return actual_fetcher(role_id, timeout_seconds=timeout_seconds)
        except FetchError as exc:
            if exc.status_code in BLOCKING_STATUS_CODES:
                raise
            if exc.status_code not in RETRYABLE_STATUS_CODES or attempt >= max_retries:
                raise
            sleeper(retry_base_seconds * (2**attempt))
        except URLError:
            if attempt >= max_retries:
                raise
            sleeper(retry_base_seconds * (2**attempt))
    raise FetchError(f"Failed to fetch role {role_id}")


def fetch_detail(role_id: int, timeout_seconds: float = 20) -> dict[str, Any]:
    url = build_info_url(role_id)
    request = Request(
        url,
        headers=_request_headers(),
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        raise FetchError(
            f"HTTP {exc.code} while fetching role {role_id}",
            status_code=exc.code,
        ) from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FetchError(f"Invalid JSON while fetching role {role_id}") from exc


def build_info_url(role_id: int) -> str:
    return f"{API_BASE}{INFO_PATH}?{urlencode({'id': role_id})}"


def _make_default_fetcher() -> Fetcher:
    try:
        return RequestsDetailFetcher()
    except RuntimeError:
        return fetch_detail


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch rysxai 2026 civil-service role details into JSONL and CSV."
    )
    parser.add_argument("--start-id", type=int, default=DEFAULT_START_ID)
    parser.add_argument("--end-id", type=int, default=DEFAULT_END_ID)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--failures", type=Path, default=DEFAULT_FAILURES_PATH)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV_PATH)
    parser.add_argument("--delay", type=float, default=0.35)
    parser.add_argument("--jitter", type=float, default=0.15)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-base", type=float, default=2)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Only write JSONL; skip CSV generation after the crawl.",
    )
    args = parser.parse_args(argv)

    summary = crawl_id_range(
        start_id=args.start_id,
        end_id=args.end_id,
        output_path=args.output,
        failures_path=args.failures,
        delay_seconds=args.delay,
        jitter_seconds=args.jitter,
        timeout_seconds=args.timeout,
        max_retries=args.max_retries,
        retry_base_seconds=args.retry_base,
        progress_every=args.progress_every,
    )
    print(
        json.dumps(
            {
                "requested_ids": summary.requested_ids,
                "skipped_existing": summary.skipped_existing,
                "fetched": summary.fetched,
                "failed": summary.failed,
                "output_path": str(summary.output_path),
                "failures_path": str(summary.failures_path),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    if not args.no_csv:
        row_count = write_csv_from_jsonl(args.output, args.csv)
        print(f"csv_rows={row_count} csv_path={args.csv}", flush=True)

    return 0


def _expect_success_data(payload: dict[str, Any]) -> Any:
    if payload.get("code") != "SUCCESS":
        raise ValueError(payload.get("detail") or payload.get("message") or "API failed")
    return payload.get("data")


def _request_headers() -> dict[str, str]:
    return {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "MajorIntelDataCollector/1.0",
    }


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")


def _csv_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list) and all(not isinstance(item, (dict, list)) for item in value):
        return "；".join(str(item) for item in value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _polite_sleep(delay_seconds: float, jitter_seconds: float, sleeper: Sleeper) -> None:
    if delay_seconds <= 0 and jitter_seconds <= 0:
        return
    delay = max(0, delay_seconds) + random.uniform(0, max(0, jitter_seconds))
    sleeper(delay)


def _now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
