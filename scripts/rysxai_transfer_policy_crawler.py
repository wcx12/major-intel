"""Fetch rysxai school transfer-major policy documents.

The crawler uses public JSON APIs observed from the rysxai web app. It stores
one school policy record per JSONL line so interrupted runs can resume without
re-fetching completed school IDs.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit
from urllib.request import Request, urlopen


API_BASE = "https://api.rysxai.cn/api"
UNIVERSITY_SEARCH_PATH = "/ry_education/university/search/v2/"
DOCS_NEW_PATH = "/ry_education/university/docs/new/"
DOCS_LEGACY_PATH = "/ry_education/university/docs/"
SCHEMA_VERSION = "rysxai_transfer_policy/v1"
DEFAULT_UNIVERSITY_CSV_PATH = Path("data/seeds/rysxai_universities.csv")
DEFAULT_OUTPUT_PATH = Path("data/raw/rysxai_transfer_policies.jsonl")
DEFAULT_FAILURES_PATH = Path("data/logs/rysxai_transfer_policies_failures.jsonl")
DEFAULT_CSV_PATH = Path("data/processed/rysxai_transfer_policies.csv")
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
BLOCKING_STATUS_CODES = {401, 403}

UNIVERSITY_CSV_FIELDS = [
    "id",
    "name",
    "province",
    "city",
    "town",
    "type",
    "property",
    "level",
    "department",
    "tags",
]

POLICY_CSV_FIELDS = [
    "fetched_at",
    "school_id",
    "school_name",
    "province",
    "city",
    "type",
    "property",
    "level",
    "department",
    "tags_json",
    "source_url",
    "has_transfer_policy",
    "has_faculty_policy",
    "faculty_policy_count",
    "change_profession_chars",
    "application_condition_chars",
    "admission_requirement_chars",
    "assessment_chars",
    "is_new_version",
    "change_profession",
    "change_profession_application_condition",
    "change_profession_admission_requirement",
    "change_profession_assessment",
    "change_profession_by_faculty_json",
]


class FetchError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class CrawlSummary:
    requested_schools: int
    skipped_existing: int
    fetched: int
    failed: int
    output_path: Path
    failures_path: Path


Fetcher = Callable[[str, str, float], dict[str, Any]]
Sleeper = Callable[[float], None]


def normalize_transfer_policy(
    school: dict[str, Any],
    payload: dict[str, Any],
    fetched_at: str,
    source_url: str,
) -> dict[str, Any]:
    data = _expect_success_data(payload)
    if not isinstance(data, dict):
        raise ValueError("Unexpected university docs/new response shape.")

    change_profession = _as_text(data.get("change_profession"))
    application_condition = _as_text(
        data.get("change_profession_application_condition")
    )
    admission_requirement = _as_text(
        data.get("change_profession_admission_requirement")
    )
    assessment = _as_text(data.get("change_profession_assessment"))
    by_faculty = data.get("change_profession_by_faculty")
    if not isinstance(by_faculty, list):
        by_faculty = []

    has_transfer_policy = any(
        [
            bool(change_profession.strip()),
            bool(application_condition.strip()),
            bool(admission_requirement.strip()),
            bool(assessment.strip()),
            bool(by_faculty),
        ]
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "fetched_at": fetched_at,
        "source": {
            "name": "rysxai",
            "source_level": "C",
            "api_base": API_BASE,
            "source_url": source_url,
            "data_scope": "school_transfer_major_policy",
        },
        "school": _normalize_school(school),
        "transfer_policy": {
            "change_profession": change_profession,
            "change_profession_by_faculty": by_faculty,
            "change_profession_application_condition": application_condition,
            "change_profession_admission_requirement": admission_requirement,
            "change_profession_assessment": assessment,
            "is_new_version": bool(data.get("is_new_version")),
        },
        "availability": {
            "has_transfer_policy": has_transfer_policy,
            "has_faculty_policy": bool(by_faculty),
            "faculty_policy_count": len(by_faculty),
            "change_profession_chars": len(change_profession),
            "application_condition_chars": len(application_condition),
            "admission_requirement_chars": len(admission_requirement),
            "assessment_chars": len(assessment),
        },
        "warnings": [
            "Rysxai policy text is a third-party compiled source; verify against official school notices before high-stakes use.",
            "Empty fields mean the site did not expose that section for the school at crawl time, not that no policy exists.",
        ],
    }


def list_universities_from_api(
    fetcher: Fetcher | None = None,
    page_size: int = 100,
    delay_seconds: float = 0.2,
    timeout_seconds: float = 20,
    max_retries: int = 2,
    retry_base_seconds: float = 2,
    sleeper: Sleeper = time.sleep,
) -> list[dict[str, Any]]:
    if page_size <= 0:
        raise ValueError("page_size must be positive.")

    base_fetcher = fetcher or fetch_json
    actual_fetcher = lambda url, method="GET", timeout_seconds=timeout_seconds: fetch_json_with_retries(
        url,
        method=method,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_base_seconds=retry_base_seconds,
        sleeper=sleeper,
        fetcher=base_fetcher,
    )
    page = 1
    total: int | None = None
    by_id: dict[int, dict[str, Any]] = {}

    while True:
        url = _build_url(
            UNIVERSITY_SEARCH_PATH,
            {
                "page_model": "page",
                "page_flag": page,
                "page_size": page_size,
            },
        )
        payload = actual_fetcher(url, "POST", timeout_seconds)
        data = _expect_success_data(payload)
        if not isinstance(data, dict):
            raise ValueError("Unexpected university search response shape.")

        if total is None:
            total = _to_int(data.get("total")) or 0
        items = data.get("items") or []
        if not isinstance(items, list):
            raise ValueError("Unexpected university search items shape.")
        if not items:
            break

        for item in items:
            if not isinstance(item, dict):
                continue
            school_id = _to_int(item.get("id"))
            if school_id is None or school_id in by_id:
                continue
            by_id[school_id] = _normalize_school(item)

        if total and page * page_size >= total:
            break
        page += 1
        if delay_seconds > 0:
            sleeper(delay_seconds)

    return list(by_id.values())


def crawl_transfer_policies(
    schools: list[dict[str, Any]],
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
    workers: int = 1,
) -> CrawlSummary:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    failures_path.parent.mkdir(parents=True, exist_ok=True)
    completed = read_completed_school_ids(output_path)
    base_fetcher = fetcher or fetch_json
    actual_fetcher = (
        fetcher
        if fetcher is not None
        else lambda url, method="GET", timeout_seconds=timeout_seconds: fetch_json_with_retries(
            url,
            method=method,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_base_seconds=retry_base_seconds,
            sleeper=sleeper,
            fetcher=base_fetcher,
        )
    )

    skipped_existing = 0
    fetched = 0
    failed = 0

    if workers > 1:
        for index, school in enumerate(schools, start=1):
            school_id = _to_int(school.get("id"))
            if school_id is None:
                failed += 1
                _append_jsonl(
                    failures_path,
                    {
                        "school_id": None,
                        "school_name": school.get("name"),
                        "error": "Missing school id.",
                        "status_code": None,
                        "failed_at": _now_iso(),
                    },
                )
                continue
            if school_id in completed:
                skipped_existing += 1
                continue

        pending_schools = [
            school
            for school in schools
            if _to_int(school.get("id")) is not None
            and _to_int(school.get("id")) not in completed
        ]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {}
            for school in pending_schools:
                future = pool.submit(
                    _fetch_transfer_policy_record,
                    school,
                    actual_fetcher,
                    timeout_seconds,
                )
                futures[future] = school
                if delay_seconds > 0:
                    sleeper(delay_seconds + random.uniform(0, jitter_seconds))

            completed_futures = 0
            for future in as_completed(futures):
                school = futures[future]
                school_id = _to_int(school.get("id"))
                completed_futures += 1
                try:
                    record = future.result()
                    _append_jsonl(output_path, record)
                    if school_id is not None:
                        completed.add(school_id)
                    fetched += 1
                except Exception as exc:
                    failed += 1
                    _append_jsonl(
                        failures_path,
                        {
                            "school_id": school_id,
                            "school_name": school.get("name"),
                            "source_url": _build_url(DOCS_NEW_PATH, {"id": school_id}),
                            "status_code": getattr(exc, "status_code", None),
                            "error": str(exc),
                            "failed_at": _now_iso(),
                        },
                    )

                if progress_every and completed_futures % progress_every == 0:
                    print(
                        f"progress: {completed_futures}/{len(pending_schools)} "
                        f"fetched={fetched} skipped={skipped_existing} failed={failed}",
                        flush=True,
                    )

        return CrawlSummary(
            requested_schools=len(schools),
            skipped_existing=skipped_existing,
            fetched=fetched,
            failed=failed,
            output_path=output_path,
            failures_path=failures_path,
        )

    for index, school in enumerate(schools, start=1):
        school_id = _to_int(school.get("id"))
        if school_id is None:
            failed += 1
            _append_jsonl(
                failures_path,
                {
                    "school_id": None,
                    "school_name": school.get("name"),
                    "error": "Missing school id.",
                    "status_code": None,
                    "failed_at": _now_iso(),
                },
            )
            continue
        if school_id in completed:
            skipped_existing += 1
            continue

        try:
            record = _fetch_transfer_policy_record(
                school,
                actual_fetcher,
                timeout_seconds,
            )
            _append_jsonl(output_path, record)
            completed.add(school_id)
            fetched += 1
        except Exception as exc:
            failed += 1
            _append_jsonl(
                failures_path,
                {
                    "school_id": school_id,
                    "school_name": school.get("name"),
                    "source_url": _build_url(DOCS_NEW_PATH, {"id": school_id}),
                    "status_code": getattr(exc, "status_code", None),
                    "error": str(exc),
                    "failed_at": _now_iso(),
                },
            )

        if progress_every and index % progress_every == 0:
            print(
                f"progress: {index}/{len(schools)} "
                f"fetched={fetched} skipped={skipped_existing} failed={failed}",
                flush=True,
            )
        if delay_seconds > 0 and index < len(schools):
            sleeper(delay_seconds + random.uniform(0, jitter_seconds))

    return CrawlSummary(
        requested_schools=len(schools),
        skipped_existing=skipped_existing,
        fetched=fetched,
        failed=failed,
        output_path=output_path,
        failures_path=failures_path,
    )


def read_completed_school_ids(jsonl_path: Path) -> set[int]:
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
            school_id = _to_int((record.get("school") or {}).get("id"))
            if school_id is not None:
                completed.add(school_id)
    return completed


def write_csv_from_jsonl(jsonl_path: Path, csv_path: Path) -> int:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with jsonl_path.open("r", encoding="utf-8") as source, csv_path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as target:
        writer = csv.DictWriter(target, fieldnames=POLICY_CSV_FIELDS)
        writer.writeheader()
        for line in source:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            writer.writerow(_csv_row(record))
            count += 1
    return count


def write_university_list_csv(schools: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=UNIVERSITY_CSV_FIELDS)
        writer.writeheader()
        for school in schools:
            row = {field: school.get(field, "") for field in UNIVERSITY_CSV_FIELDS}
            row["tags"] = _json_compact(school.get("tags") or [])
            writer.writerow(row)


def read_university_list_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            tags_value = row.get("tags") or "[]"
            try:
                tags = json.loads(tags_value)
            except json.JSONDecodeError:
                tags = [part.strip() for part in tags_value.split(",") if part.strip()]
            row["tags"] = tags
            row["id"] = _to_int(row.get("id"))
            rows.append(row)
        return rows


def fetch_json_with_retries(
    url: str,
    method: str = "GET",
    timeout_seconds: float = 20,
    fetcher: Fetcher | None = None,
    max_retries: int = 2,
    retry_base_seconds: float = 2,
    sleeper: Sleeper = time.sleep,
) -> dict[str, Any]:
    actual_fetcher = fetcher or fetch_json
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return actual_fetcher(url, method, timeout_seconds)
        except FetchError as exc:
            last_error = exc
            if exc.status_code in BLOCKING_STATUS_CODES:
                raise
            if exc.status_code and exc.status_code not in RETRYABLE_STATUS_CODES:
                raise
        except (URLError, TimeoutError) as exc:
            last_error = exc

        if attempt < max_retries:
            sleeper(retry_base_seconds * (attempt + 1))

    if last_error:
        raise last_error
    raise FetchError("Unknown fetch failure.")


def _fetch_transfer_policy_record(
    school: dict[str, Any],
    fetcher: Fetcher,
    timeout_seconds: float,
) -> dict[str, Any]:
    school_id = _to_int(school.get("id"))
    if school_id is None:
        raise ValueError("Missing school id.")

    source_url = _build_url(DOCS_NEW_PATH, {"id": school_id})
    try:
        payload = fetcher(source_url, "GET", timeout_seconds)
    except FetchError as exc:
        if exc.status_code != 404:
            raise
        source_url = _build_url(DOCS_LEGACY_PATH, {"id": school_id})
        payload = fetcher(source_url, "GET", timeout_seconds)
    return normalize_transfer_policy(
        school,
        payload,
        fetched_at=_now_iso(),
        source_url=source_url,
    )


def fetch_json(url: str, method: str = "GET", timeout_seconds: float = 20) -> dict[str, Any]:
    method = method.upper()
    data = _json_body_from_query(url) if method == "POST" else None
    request = Request(
        url,
        data=data,
        method=method,
        headers=_request_headers(),
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read()
    except HTTPError as exc:
        raise FetchError(f"HTTP {exc.code} while fetching {url}", exc.code) from exc
    except URLError as exc:
        raise FetchError(f"Network error while fetching {url}: {exc}") from exc

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise FetchError(f"Invalid JSON while fetching {url}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl rysxai school transfer-major policy data."
    )
    parser.add_argument(
        "--university-csv",
        type=Path,
        default=DEFAULT_UNIVERSITY_CSV_PATH,
        help="CSV of university IDs. Created from API when missing or refresh is set.",
    )
    parser.add_argument(
        "--refresh-university-list",
        action="store_true",
        help="Refresh the university seed CSV before crawling.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--failures", type=Path, default=DEFAULT_FAILURES_PATH)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV_PATH)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--delay-seconds", type=float, default=0.35)
    parser.add_argument("--jitter-seconds", type=float, default=0.15)
    parser.add_argument("--timeout-seconds", type=float, default=20)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-base-seconds", type=float, default=2)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of concurrent policy fetch workers. Keep small for polite crawling.",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only refresh/read the university list, then exit.",
    )
    args = parser.parse_args(argv)

    if args.refresh_university_list or not args.university_csv.exists():
        schools = list_universities_from_api(
            page_size=args.page_size,
            delay_seconds=max(args.delay_seconds, 0),
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            retry_base_seconds=args.retry_base_seconds,
        )
        write_university_list_csv(schools, args.university_csv)
        print(f"wrote {len(schools)} universities to {args.university_csv}", flush=True)
    else:
        schools = read_university_list_csv(args.university_csv)
        print(f"read {len(schools)} universities from {args.university_csv}", flush=True)

    if args.limit is not None:
        schools = schools[: args.limit]
        print(f"limited crawl to {len(schools)} universities", flush=True)

    if args.list_only:
        return 0

    summary = crawl_transfer_policies(
        schools=schools,
        output_path=args.output,
        failures_path=args.failures,
        delay_seconds=args.delay_seconds,
        jitter_seconds=args.jitter_seconds,
        timeout_seconds=args.timeout_seconds,
        max_retries=args.max_retries,
        retry_base_seconds=args.retry_base_seconds,
        progress_every=args.progress_every,
        workers=args.workers,
    )
    csv_rows = write_csv_from_jsonl(args.output, args.csv)
    print(
        "done: "
        f"requested={summary.requested_schools} "
        f"fetched={summary.fetched} "
        f"skipped={summary.skipped_existing} "
        f"failed={summary.failed} "
        f"csv_rows={csv_rows} "
        f"output={summary.output_path} "
        f"csv={args.csv} "
        f"failures={summary.failures_path}",
        flush=True,
    )
    return 0


def _normalize_school(school: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": _to_int(school.get("id")),
        "name": school.get("name") or "",
        "province": school.get("province") or "",
        "city": school.get("city") or "",
        "town": school.get("town") or "",
        "type": school.get("type") or "",
        "property": school.get("property") or "",
        "level": school.get("level") or "",
        "department": school.get("department") or "",
        "tags": _as_list(school.get("tags")),
        "rank_list": _as_list(school.get("rank_list")),
    }


def _csv_row(record: dict[str, Any]) -> dict[str, Any]:
    school = record.get("school") or {}
    source = record.get("source") or {}
    policy = record.get("transfer_policy") or {}
    availability = record.get("availability") or {}
    return {
        "fetched_at": record.get("fetched_at") or "",
        "school_id": school.get("id") or "",
        "school_name": school.get("name") or "",
        "province": school.get("province") or "",
        "city": school.get("city") or "",
        "type": school.get("type") or "",
        "property": school.get("property") or "",
        "level": school.get("level") or "",
        "department": school.get("department") or "",
        "tags_json": _json_compact(school.get("tags") or []),
        "source_url": source.get("source_url") or "",
        "has_transfer_policy": _bool_text(availability.get("has_transfer_policy")),
        "has_faculty_policy": _bool_text(availability.get("has_faculty_policy")),
        "faculty_policy_count": availability.get("faculty_policy_count") or 0,
        "change_profession_chars": availability.get("change_profession_chars") or 0,
        "application_condition_chars": availability.get("application_condition_chars")
        or 0,
        "admission_requirement_chars": availability.get("admission_requirement_chars")
        or 0,
        "assessment_chars": availability.get("assessment_chars") or 0,
        "is_new_version": _bool_text(policy.get("is_new_version")),
        "change_profession": policy.get("change_profession") or "",
        "change_profession_application_condition": policy.get(
            "change_profession_application_condition"
        )
        or "",
        "change_profession_admission_requirement": policy.get(
            "change_profession_admission_requirement"
        )
        or "",
        "change_profession_assessment": policy.get("change_profession_assessment")
        or "",
        "change_profession_by_faculty_json": _json_compact(
            policy.get("change_profession_by_faculty") or []
        ),
    }


def _expect_success_data(payload: dict[str, Any]) -> Any:
    if payload.get("code") != "SUCCESS":
        message = payload.get("detail") or payload.get("message") or "Request failed."
        raise FetchError(str(message))
    return payload.get("data")


def _build_url(path: str, params: dict[str, Any] | None = None) -> str:
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urlencode(params, doseq=True)
    return url


def _request_headers() -> dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (compatible; major-intel-policy-crawler/1.0; "
            "+https://rysxai.cn/)"
        ),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://rysxai.cn",
        "Referer": "https://rysxai.cn/",
    }


def _json_body_from_query(url: str) -> bytes:
    params = dict(parse_qsl(urlsplit(url).query, keep_blank_values=True))
    return json.dumps(params, ensure_ascii=False).encode("utf-8")


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [part for part in value.split() if part]
    return [value]


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _json_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
