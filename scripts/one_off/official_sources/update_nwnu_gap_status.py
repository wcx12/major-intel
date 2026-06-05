from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCHOOL = "西北师范大学"
SOURCE_URLS = (
    "https://jykxxy.nwnu.edu.cn/2025/0404/c7122a251711/page.htm; "
    "https://jykxxy.nwnu.edu.cn/_upload/article/files/bd/c5/"
    "289f95b04bfe86e89495ed3239ef/1369c3c3-8eeb-42df-b75b-b36687ef3d13.pdf"
)
LOCAL_ARTIFACTS = (
    "data/raw/official_recommendation_nwnu_jykxxy_2025_master_first_choice/"
    "nwnu_jykxxy_2025_master_first_choice.pdf; "
    "data/processed/official_recommendation_nwnu_jykxxy_2025_master_first_choice/"
    "records_clean_curated.csv"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_source_attempts() -> int:
    path = ROOT / "data/processed/graduate_outcomes_official_recommendation_remaining15/source_attempts.csv"
    rows = read_csv(path)
    fieldnames = list(rows[0].keys())
    updated = 0
    for row in rows:
        if row.get("school_name") != SCHOOL:
            continue
        row.update(
            {
                "source_title": "西北师范大学教育科学学院2025年硕士研究生招生复试结果（第一志愿）官方PDF",
                "source_url": SOURCE_URLS,
                "local_artifact": LOCAL_ARTIFACTS,
                "live_status": "HTTP 200 downloaded",
                "content_type": "application/pdf",
                "decision": "ingested",
                "blocker_type": "official_pdf_access_restored",
                "notes": (
                    "学院子站官方PDF可直接下载，含考生编号、姓名、报考专业、成绩、拟录取意见、"
                    "学习方式等行级字段；仅保留拟录取意见为拟录取的106条，排除27条不予录取。"
                ),
                "last_checked_date": "2026-06-04",
            }
        )
        updated += 1
    write_csv(path, rows, fieldnames)
    return updated


def remove_from_remaining(path: Path) -> int:
    rows = read_csv(path)
    fieldnames = list(rows[0].keys())
    kept = [row for row in rows if row.get("school_name") != SCHOOL]
    write_csv(path, kept, fieldnames)
    return len(rows) - len(kept)


def main() -> None:
    updated_attempts = update_source_attempts()
    removed_tracker = remove_from_remaining(ROOT / "outputs/graduate_outcomes/remaining_uncovered_schools.csv")
    removed_recheck = remove_from_remaining(
        ROOT / "outputs/graduate_outcomes/remaining_uncovered_recheck_2026-06-04.csv"
    )
    print(
        {
            "source_attempts_updated": updated_attempts,
            "remaining_tracker_removed": removed_tracker,
            "latest_recheck_removed": removed_recheck,
        }
    )


if __name__ == "__main__":
    main()
