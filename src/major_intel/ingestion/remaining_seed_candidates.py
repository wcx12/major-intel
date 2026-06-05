"""Summarize official seed URLs for the remaining uncovered schools."""

from __future__ import annotations

import csv
import json
from pathlib import Path


SCHOOLS = [
    "北京电影学院",
    "北京服装学院",
    "成都体育学院",
    "宁波诺丁汉大学",
    "西北师范大学",
    "西藏农牧大学",
    "中国医科大学",
    "重庆邮电大学",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except UnicodeDecodeError:
        with path.open("r", encoding="gb18030", newline="") as handle:
            return list(csv.DictReader(handle))


def collect_recheck_urls(path: Path) -> set[str]:
    urls: set[str] = set()
    if not path.exists():
        return urls
    for row in read_csv(path):
        for value in row.values():
            if not value:
                continue
            for token in str(value).replace("|", " ").replace(";", " ").split():
                if token.startswith(("http://", "https://")):
                    urls.add(token.strip().strip(",，。)）"))
    return urls


def main() -> None:
    seed_dir = Path("data/seeds")
    recheck_urls = collect_recheck_urls(
        Path("outputs/graduate_outcomes/remaining_uncovered_recheck_2026-06-04.csv")
    )
    by_school: dict[str, dict[str, dict[str, object]]] = {school: {} for school in SCHOOLS}

    for path in sorted(seed_dir.glob("*.csv")):
        for row in read_csv(path):
            line = " ".join(str(value or "") for value in row.values())
            for school in SCHOOLS:
                if school not in line:
                    continue
                url = (
                    row.get("url")
                    or row.get("source_url")
                    or row.get("official_url")
                    or row.get("page_url")
                    or row.get("start_url")
                    or ""
                ).strip()
                if not url:
                    continue
                item = by_school[school].setdefault(
                    url,
                    {
                        "url": url,
                        "years": set(),
                        "doc_types": set(),
                        "titles": set(),
                        "files": set(),
                    },
                )
                item["years"].add(str(row.get("year") or ""))
                item["doc_types"].add(
                    str(
                        row.get("document_type")
                        or row.get("source_type")
                        or row.get("category")
                        or ""
                    )
                )
                item["titles"].add(
                    str(
                        row.get("title")
                        or row.get("source_title")
                        or row.get("discovery_title")
                        or row.get("query")
                        or row.get("discovery_query")
                        or ""
                    )
                )
                item["files"].add(path.name)

    output: dict[str, object] = {}
    for school, url_map in by_school.items():
        items = []
        for url, item in sorted(url_map.items()):
            files = sorted(str(value) for value in item["files"] if value)
            titles = sorted(str(value) for value in item["titles"] if value)
            items.append(
                {
                    "url": url,
                    "already_in_latest_recheck": url in recheck_urls,
                    "years": sorted(str(value) for value in item["years"] if value),
                    "doc_types": sorted(str(value) for value in item["doc_types"] if value),
                    "titles": titles[:4],
                    "files": files[:6],
                    "file_count": len(files),
                }
            )
        output[school] = {
            "candidate_url_count": len(items),
            "not_in_latest_recheck_count": sum(
                1 for item in items if not item["already_in_latest_recheck"]
            ),
            "candidates": items,
        }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
