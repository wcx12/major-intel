"""Fetch and normalize rysxai major introduction sections.

This crawler only calls the profession info endpoint. It is intentionally
separate from the market crawler so a full intro crawl does not also fetch job
posting samples.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .rysxai_market_crawler import (
    INFO_PATH,
    _build_url,
    _expect_success,
    _now_iso,
    _safe_timestamp,
    _to_int,
    _write_json,
    fetch_json_with_retries,
    list_professions_from_api,
    read_profession_rows,
    write_profession_list_csv,
)


SCHEMA_VERSION = "rysxai_major_introduction_snapshot/v1"
CSV_FIELDS = [
    "rysxai_profession_id",
    "major_code",
    "major_name",
    "level",
    "degree",
    "limit_year",
    "selection_advice",
    "enrollment_scale",
    "univ_count",
    "apply_plan_ratio",
    "major_detail",
    "major_course",
    "undergraduate_to_graduate",
    "similar_majors",
    "captured_at",
    "info_url",
]
SECTION_LABELS = {
    "major_detail": "专业详情",
    "major_course": "专业课程",
    "undergraduate_to_graduate": "本研衔接",
    "similar_majors": "相似专业",
}


def normalize_major_intro(payload: dict[str, Any], captured_at: str) -> dict[str, Any]:
    data = _expect_success(payload)
    profession_id = data.get("id")

    major_detail, major_detail_source = _first_text_with_source(
        ("content", data.get("content")),
        ("ai_info", data.get("ai_info")),
        ("info", data.get("info")),
    )
    major_course, major_course_source = _first_text_with_source(
        ("course", data.get("course")),
        ("ai_course", data.get("ai_course")),
    )
    undergraduate_to_graduate, undergraduate_to_graduate_source = _first_text_with_source(
        ("master_prof", data.get("master_prof")),
        ("ai_master_prof", data.get("ai_master_prof")),
    )
    similar_majors, similar_majors_source = _first_text_with_source(
        ("similar_prof", data.get("similar_prof")),
        ("ai_similar_prof", data.get("ai_similar_prof")),
    )

    sections = {
        "major_detail": major_detail,
        "major_course": major_course,
        "undergraduate_to_graduate": undergraduate_to_graduate,
        "similar_majors": similar_majors,
    }
    section_source_fields = {
        "major_detail": major_detail_source,
        "major_course": major_course_source,
        "undergraduate_to_graduate": undergraduate_to_graduate_source,
        "similar_majors": similar_majors_source,
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "captured_at": captured_at,
        "source": {
            "name": "rysxai",
            "source_level": "C",
            "data_scope": "major_level_introduction",
            "info_url": _build_url(INFO_PATH, {"id": profession_id}),
        },
        "profession": {
            "id": profession_id,
            "name": data.get("name"),
            "code": data.get("code"),
            "level": data.get("level"),
            "degree": data.get("degree"),
            "limit_year": data.get("limit_year"),
            "selection_advice": data.get("sel_adv"),
            "enrollment_scale": data.get("enrollment_scale"),
            "gender_ratio": _as_dict(data.get("gender_ratio")),
            "ncee_ratio": _as_dict(data.get("NCEE_ratio")),
            "univ_count": _to_int(data.get("univ_count")),
            "apply_plan_ratio": _to_int(data.get("apply_plan_ratio")),
        },
        "section_labels": SECTION_LABELS,
        "sections": sections,
        "section_source_fields": section_source_fields,
        "featured_video": {
            "id": data.get("featured_video_id"),
            "title": data.get("featured_video_title"),
        },
        "profession_intro_videos": _normalize_intro_videos(data.get("profession_intro")),
        "warnings": _section_warnings(sections),
    }


def crawl_major_intro(
    profession_id: int,
    raw_dir: Path,
    processed_dir: Path,
    timeout_seconds: float = 20,
    run_id: str | None = None,
    fetcher=None,
    max_retries: int = 2,
    retry_base_seconds: float = 5,
    sleeper=time.sleep,
) -> Path:
    captured_at = _now_iso()
    raw_run_dir = raw_dir / (run_id or _safe_timestamp(captured_at))
    raw_run_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    info_url = _build_url(INFO_PATH, {"id": profession_id})
    info_payload = fetch_json_with_retries(
        info_url,
        timeout_seconds=timeout_seconds,
        fetcher=fetcher,
        max_retries=max_retries,
        retry_base_seconds=retry_base_seconds,
        sleeper=sleeper,
    )

    _write_json(raw_run_dir / f"profession_{profession_id}_info.raw.json", info_payload)
    snapshot = normalize_major_intro(info_payload, captured_at)
    output_path = processed_dir / f"profession_{profession_id}_major_intro_snapshot.json"
    _write_json(output_path, snapshot)
    return output_path


def crawl_major_intro_batch(
    profession_rows: list[dict[str, Any]],
    raw_dir: Path,
    processed_dir: Path,
    logs_dir: Path,
    resume: bool = False,
    max_count: int | None = None,
    sleep_seconds: float = 0.5,
    timeout_seconds: float = 20,
    run_id: str | None = None,
    max_retries: int = 2,
    retry_base_seconds: float = 5,
    max_consecutive_errors: int = 20,
    concurrency: int = 1,
    fetcher=None,
    sleeper=time.sleep,
    progress: bool = False,
) -> dict[str, Any]:
    actual_run_id = run_id or _safe_timestamp(_now_iso())
    logs_dir.mkdir(parents=True, exist_ok=True)
    failure_log = logs_dir / f"{actual_run_id}_intro_failures.jsonl"
    manifest_path = logs_dir / f"{actual_run_id}_intro_manifest.json"

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
        "aggregate_jsonl": None,
        "aggregate_csv": None,
        "failure_log": str(failure_log),
    }

    snapshots: list[dict[str, Any]] = []
    consecutive_errors = _crawl_selected_rows(
        selected_rows=selected_rows,
        snapshots=snapshots,
        manifest=manifest,
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        failure_log=failure_log,
        actual_run_id=actual_run_id,
        resume=resume,
        sleep_seconds=sleep_seconds,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_base_seconds=retry_base_seconds,
        max_consecutive_errors=max_consecutive_errors,
        concurrency=max(1, concurrency),
        fetcher=fetcher,
        sleeper=sleeper,
        progress=progress,
    )

    if consecutive_errors >= max_consecutive_errors and manifest["stopped_reason"] is None:
        manifest["stopped_reason"] = f"max_consecutive_errors:{max_consecutive_errors}"

    aggregate_paths = write_aggregate_outputs(snapshots, processed_dir, actual_run_id)
    manifest["aggregate_jsonl"] = str(aggregate_paths["jsonl"])
    manifest["aggregate_csv"] = str(aggregate_paths["csv"])
    manifest["finished_at"] = _now_iso()
    _write_json(manifest_path, manifest)
    return manifest


def write_aggregate_outputs(
    snapshots: list[dict[str, Any]],
    processed_dir: Path,
    run_id: str,
) -> dict[str, Path]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = processed_dir / f"major_introductions_{run_id}.jsonl"
    csv_path = processed_dir / f"major_introductions_{run_id}.csv"
    ordered_snapshots = sorted(
        snapshots,
        key=lambda snapshot: int((snapshot.get("profession") or {}).get("id") or 0),
    )

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for snapshot in ordered_snapshots:
            handle.write(json.dumps(snapshot, ensure_ascii=True))
            handle.write("\n")

    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for snapshot in ordered_snapshots:
            writer.writerow(intro_snapshot_to_csv_row(snapshot))

    return {"jsonl": jsonl_path, "csv": csv_path}


def intro_snapshot_to_csv_row(snapshot: dict[str, Any]) -> dict[str, Any]:
    profession = snapshot.get("profession") or {}
    sections = snapshot.get("sections") or {}
    source = snapshot.get("source") or {}
    return {
        "rysxai_profession_id": profession.get("id"),
        "major_code": profession.get("code"),
        "major_name": profession.get("name"),
        "level": profession.get("level"),
        "degree": profession.get("degree"),
        "limit_year": profession.get("limit_year"),
        "selection_advice": profession.get("selection_advice"),
        "enrollment_scale": profession.get("enrollment_scale"),
        "univ_count": profession.get("univ_count"),
        "apply_plan_ratio": profession.get("apply_plan_ratio"),
        "major_detail": sections.get("major_detail"),
        "major_course": sections.get("major_course"),
        "undergraduate_to_graduate": sections.get("undergraduate_to_graduate"),
        "similar_majors": sections.get("similar_majors"),
        "captured_at": snapshot.get("captured_at"),
        "info_url": source.get("info_url"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Crawl rysxai major introduction sections."
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
    parser.add_argument("--level", help="Filter CSV/discovered professions by level.")
    parser.add_argument("--max-count", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw/rysxai_major_intros"),
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed/rysxai_major_intros"),
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=Path("data/logs/rysxai_major_intros"),
    )
    parser.add_argument("--sleep-seconds", type=float, default=0.5)
    parser.add_argument("--timeout-seconds", type=float, default=20)
    parser.add_argument("--run-id")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-base-seconds", type=float, default=5)
    parser.add_argument("--max-consecutive-errors", type=int, default=20)
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Number of concurrent profession info requests.",
    )
    parser.add_argument("--progress", action="store_true")
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

    manifest = crawl_major_intro_batch(
        profession_rows,
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        logs_dir=args.logs_dir,
        resume=args.resume,
        max_count=args.max_count,
        sleep_seconds=args.sleep_seconds,
        timeout_seconds=args.timeout_seconds,
        run_id=args.run_id,
        max_retries=args.max_retries,
        retry_base_seconds=args.retry_base_seconds,
        max_consecutive_errors=args.max_consecutive_errors,
        concurrency=args.concurrency,
        progress=args.progress,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


def _first_text_with_source(*items: tuple[str, Any]) -> tuple[str, str | None]:
    for field, value in items:
        if isinstance(value, str) and value.strip():
            return value.strip(), field
    return "", None


def _section_warnings(sections: dict[str, str]) -> list[str]:
    warnings = []
    for key, label in SECTION_LABELS.items():
        if not sections.get(key):
            warnings.append(f"missing section: {label}")
    return warnings


def _normalize_intro_videos(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    videos = []
    for item in value:
        if not isinstance(item, dict):
            continue
        videos.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "video_url": item.get("video_url"),
            }
        )
    return videos


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _crawl_selected_rows(
    selected_rows: list[dict[str, Any]],
    snapshots: list[dict[str, Any]],
    manifest: dict[str, Any],
    raw_dir: Path,
    processed_dir: Path,
    failure_log: Path,
    actual_run_id: str,
    resume: bool,
    sleep_seconds: float,
    timeout_seconds: float,
    max_retries: int,
    retry_base_seconds: float,
    max_consecutive_errors: int,
    concurrency: int,
    fetcher,
    sleeper,
    progress: bool,
) -> int:
    if concurrency <= 1:
        return _crawl_selected_rows_sequential(
            selected_rows,
            snapshots,
            manifest,
            raw_dir,
            processed_dir,
            failure_log,
            actual_run_id,
            resume,
            sleep_seconds,
            timeout_seconds,
            max_retries,
            retry_base_seconds,
            max_consecutive_errors,
            fetcher,
            sleeper,
            progress,
        )
    return _crawl_selected_rows_concurrent(
        selected_rows,
        snapshots,
        manifest,
        raw_dir,
        processed_dir,
        failure_log,
        actual_run_id,
        resume,
        sleep_seconds,
        timeout_seconds,
        max_retries,
        retry_base_seconds,
        max_consecutive_errors,
        concurrency,
        fetcher,
        sleeper,
        progress,
    )


def _crawl_selected_rows_sequential(
    selected_rows: list[dict[str, Any]],
    snapshots: list[dict[str, Any]],
    manifest: dict[str, Any],
    raw_dir: Path,
    processed_dir: Path,
    failure_log: Path,
    actual_run_id: str,
    resume: bool,
    sleep_seconds: float,
    timeout_seconds: float,
    max_retries: int,
    retry_base_seconds: float,
    max_consecutive_errors: int,
    fetcher,
    sleeper,
    progress: bool,
) -> int:
    consecutive_errors = 0
    for index, row in enumerate(selected_rows, start=1):
        result = _crawl_or_load_one(
            index=index,
            total=len(selected_rows),
            row=row,
            raw_dir=raw_dir,
            processed_dir=processed_dir,
            actual_run_id=actual_run_id,
            resume=resume,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_base_seconds=retry_base_seconds,
            fetcher=fetcher,
            sleeper=sleeper,
        )
        consecutive_errors = _apply_row_result(
            result,
            snapshots=snapshots,
            manifest=manifest,
            failure_log=failure_log,
            progress=progress,
            consecutive_errors=consecutive_errors,
        )
        if consecutive_errors >= max_consecutive_errors:
            manifest["stopped_reason"] = f"max_consecutive_errors:{max_consecutive_errors}"
            break
        if index < len(selected_rows) and sleep_seconds > 0:
            sleeper(sleep_seconds)
    return consecutive_errors


def _crawl_selected_rows_concurrent(
    selected_rows: list[dict[str, Any]],
    snapshots: list[dict[str, Any]],
    manifest: dict[str, Any],
    raw_dir: Path,
    processed_dir: Path,
    failure_log: Path,
    actual_run_id: str,
    resume: bool,
    sleep_seconds: float,
    timeout_seconds: float,
    max_retries: int,
    retry_base_seconds: float,
    max_consecutive_errors: int,
    concurrency: int,
    fetcher,
    sleeper,
    progress: bool,
) -> int:
    consecutive_errors = 0
    total = len(selected_rows)
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        for batch_start in range(0, total, concurrency):
            batch = selected_rows[batch_start : batch_start + concurrency]
            futures = [
                executor.submit(
                    _crawl_or_load_one,
                    index=batch_start + offset,
                    total=total,
                    row=row,
                    raw_dir=raw_dir,
                    processed_dir=processed_dir,
                    actual_run_id=actual_run_id,
                    resume=resume,
                    timeout_seconds=timeout_seconds,
                    max_retries=max_retries,
                    retry_base_seconds=retry_base_seconds,
                    fetcher=fetcher,
                    sleeper=sleeper,
                )
                for offset, row in enumerate(batch, start=1)
            ]
            for future in as_completed(futures):
                result = future.result()
                consecutive_errors = _apply_row_result(
                    result,
                    snapshots=snapshots,
                    manifest=manifest,
                    failure_log=failure_log,
                    progress=progress,
                    consecutive_errors=consecutive_errors,
                )
            if consecutive_errors >= max_consecutive_errors:
                manifest["stopped_reason"] = (
                    f"max_consecutive_errors:{max_consecutive_errors}"
                )
                break
            if batch_start + concurrency < total and sleep_seconds > 0:
                sleeper(sleep_seconds)
    return consecutive_errors


def _crawl_or_load_one(
    index: int,
    total: int,
    row: dict[str, Any],
    raw_dir: Path,
    processed_dir: Path,
    actual_run_id: str,
    resume: bool,
    timeout_seconds: float,
    max_retries: int,
    retry_base_seconds: float,
    fetcher,
    sleeper,
) -> dict[str, Any]:
    profession_id = int(row["rysxai_profession_id"])
    output_path = processed_dir / f"profession_{profession_id}_major_intro_snapshot.json"
    if resume and output_path.exists():
        return {
            "status": "skipped",
            "index": index,
            "total": total,
            "profession_id": profession_id,
            "snapshot": _read_json(output_path),
        }

    try:
        output_path = crawl_major_intro(
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
        return {
            "status": "success",
            "index": index,
            "total": total,
            "profession_id": profession_id,
            "snapshot": _read_json(output_path),
        }
    except Exception as exc:
        return {
            "status": "failure",
            "index": index,
            "total": total,
            "profession_id": profession_id,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "status_code": getattr(exc, "status_code", None),
            "row": row,
        }


def _apply_row_result(
    result: dict[str, Any],
    snapshots: list[dict[str, Any]],
    manifest: dict[str, Any],
    failure_log: Path,
    progress: bool,
    consecutive_errors: int,
) -> int:
    status = result["status"]
    profession_id = result["profession_id"]
    index = result["index"]
    total = result["total"]
    if status == "skipped":
        manifest["skipped_count"] += 1
        snapshots.append(result["snapshot"])
        if progress:
            print(f"[{index}/{total}] skip profession {profession_id}")
        return 0
    if status == "success":
        manifest["success_count"] += 1
        snapshots.append(result["snapshot"])
        if progress:
            print(f"[{index}/{total}] ok profession {profession_id}")
        return 0

    manifest["failure_count"] += 1
    _append_jsonl(
        failure_log,
        {
            "run_id": manifest["run_id"],
            "profession_id": profession_id,
            "index": index,
            "error_type": result["error_type"],
            "error": result["error"],
            "status_code": result.get("status_code"),
            "row": result.get("row"),
            "created_at": _now_iso(),
        },
    )
    if progress:
        print(f"[{index}/{total}] fail profession {profession_id}: {result['error_type']}")
    return consecutive_errors + 1


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True))
        handle.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
