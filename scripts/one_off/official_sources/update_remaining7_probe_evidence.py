from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_unique_list(existing: str, additions: list[str], separator: str = "; ") -> str:
    parts = [part.strip() for part in existing.replace("|", separator).split(separator) if part.strip()]
    for addition in additions:
        if addition and addition not in parts:
            parts.append(addition)
    return separator.join(parts)


def append_note(existing: str, addition: str) -> str:
    if addition in existing:
        return existing
    if not existing:
        return addition
    return existing.rstrip("；; ") + "；" + addition


def update_source_attempts() -> None:
    path = ROOT / "data/processed/graduate_outcomes_official_recommendation_remaining15/source_attempts.csv"
    rows = read_csv(path)
    fieldnames = list(rows[0].keys())

    for row in rows:
        school = row.get("school_name")
        if school == "北京电影学院":
            row["source_url"] = add_unique_list(
                row["source_url"],
                [
                    "http://www.bfa.edu.cn/yanjiusheng/info/1049/2939.htm",
                    "http://www.bfa.edu.cn/yanjiusheng/info/1031/3724.htm",
                    "http://www.bfa.edu.cn/yanjiusheng/info/1031/4405.htm",
                ],
            )
            row["local_artifact"] = add_unique_list(
                row["local_artifact"],
                [
                    "tmp/bfa_2022_reco_2939_http.html",
                    "tmp/bfa_2022_reco_2939_http.headers.txt",
                    "tmp/bfa_2023_reco_3724_http.html",
                    "tmp/bfa_2023_reco_3724_http.headers.txt",
                    "tmp/bfa_2025_master_4405_http.html",
                    "tmp/bfa_2025_master_4405_http.headers.txt",
                ],
            )
            row["live_status"] = "HTTP 412 JS challenge; official candidate-number PDF available but auxiliary"
            row["content_type"] = "HTML JavaScript challenge; application/pdf auxiliary"
            row["notes"] = append_note(
                row["notes"],
                (
                    "2026-06-04复测http旧页2939/3724/4405，响应头均为HTTP 412 "
                    "Precondition Failed，正文为防护挑战脚本，不含官方名单正文。"
                ),
            )
            row["last_checked_date"] = "2026-06-04"

        elif school == "中国医科大学":
            row["local_artifact"] = add_unique_list(
                row["local_artifact"],
                [
                    "tmp/cmu_2025_reco_1905_9515.html",
                    "tmp/cmu_2025_reco_1905_9515.headers.txt",
                    "tmp/cmu_2025_directdoctor_1905_9514.html",
                    "tmp/cmu_2025_directdoctor_1905_9514.headers.txt",
                    "tmp/cmu_2024_reco_1905_9236.html",
                    "tmp/cmu_2024_reco_1905_9236.headers.txt",
                ],
            )
            row["live_status"] = "HTTP 200 captcha download bridge; HTTP 404 article candidates"
            row["content_type"] = "HTML verification page and 404 pages"
            row["notes"] = append_note(
                row["notes"],
                (
                    "2026-06-04复测官方cmuyjs/info/1905/9515、9514、9236精确路径，"
                    "三者均返回HTTP 404，正文为1693字节系统提示页。"
                ),
            )
            row["last_checked_date"] = "2026-06-04"

        elif school == "重庆邮电大学":
            row["source_url"] = add_unique_list(
                row["source_url"],
                [
                    "https://eccs.cqupt.edu.cn/info/1012/1163.htm",
                    "https://eccs.cqupt.edu.cn/info/1012/1143.htm",
                    "https://eccs.cqupt.edu.cn/info/1012/1103.htm",
                ],
            )
            row["local_artifact"] = add_unique_list(
                row["local_artifact"],
                [
                    "tmp/cqupt_eccs_2026_master_1163.html",
                    "tmp/cqupt_eccs_2026_master_1163.headers.txt",
                    "tmp/cqupt_eccs_2025_master_1143.html",
                    "tmp/cqupt_eccs_2025_master_1143.headers.txt",
                    "tmp/cqupt_eccs_2024_master_1103.html",
                    "tmp/cqupt_eccs_2024_master_1103.headers.txt",
                ],
            )
            row["live_status"] = "Homepage HTTP 200; graduate-school and ECCS detail pages HTTP 412"
            row["content_type"] = "HTML homepage link list; HTML JavaScript challenge"
            row["notes"] = append_note(
                row["notes"],
                (
                    "2026-06-04复测通信软件技术工程研究中心子站1163/1143/1103详情页，"
                    "均返回HTTP 412 Precondition Failed防护页面，不暴露行级正文或附件。"
                ),
            )
            row["last_checked_date"] = "2026-06-04"

    write_csv(path, rows, fieldnames)


def update_remaining_tracker() -> None:
    path = ROOT / "outputs/graduate_outcomes/remaining_uncovered_schools.csv"
    rows = read_csv(path)
    fieldnames = list(rows[0].keys())
    for row in rows:
        school = row.get("school_name")
        if school == "北京电影学院":
            row["current_status"] = (
                "official final-list pages and 2022/2023/2025 historical http pages return "
                "HTTP 412 JS challenge; available candidate-number PDF is auxiliary non-final"
            )
            row["official_candidate_urls"] = add_unique_list(
                row["official_candidate_urls"],
                [
                    "http://www.bfa.edu.cn/yanjiusheng/info/1049/2939.htm",
                    "http://www.bfa.edu.cn/yanjiusheng/info/1031/3724.htm",
                    "http://www.bfa.edu.cn/yanjiusheng/info/1031/4405.htm",
                ],
                separator="|",
            )
        elif school == "中国医科大学":
            row["official_candidate_urls"] = (
                "https://www.cmu.edu.cn/system/_content/download.jsp?owner=1778759152&urltype=news.DownloadAttachUrl&wbfileid=13255969|"
                "https://www.cmu.edu.cn/cmuyjs/info/1905/9236.htm|"
                "https://www.cmu.edu.cn/cmuyjs/info/1905/9515.htm|"
                "https://www.cmu.edu.cn/cmuyjs/info/1905/9514.htm|"
                "https://www.cmu.edu.cn/cmuyjs/info/1900/9811.htm|"
                "https://www.cmu.edu.cn/cmuyjs/info/1900/9398.htm|"
                "https://www.cmu.edu.cn/cmuyjs/info/1900/9608.htm|"
                "https://www.cmu.edu.cn/cmuyjs/info/1901/9660.htm|"
                "https://www.cmu.edu.cn/cmuyjs/info/1901/9671.htm"
            )
            row["current_status"] = (
                "official attachment requires verification-code bridge and precise article candidates "
                "currently return HTTP 404 system pages"
            )
        elif school == "重庆邮电大学":
            row["official_candidate_urls"] = add_unique_list(
                row["official_candidate_urls"],
                [
                    "https://eccs.cqupt.edu.cn/info/1012/1163.htm",
                    "https://eccs.cqupt.edu.cn/info/1012/1143.htm",
                    "https://eccs.cqupt.edu.cn/info/1012/1103.htm",
                ],
                separator="|",
            )
            row["current_status"] = (
                "homepage is visible but graduate-school and ECCS official detail pages return HTTP 412 challenge"
            )
    write_csv(path, rows, fieldnames)


def update_recheck() -> None:
    path = ROOT / "outputs/graduate_outcomes/remaining_uncovered_recheck_2026-06-04.csv"
    rows = read_csv(path)
    fieldnames = list(rows[0].keys())
    for row in rows:
        school = row.get("school_name")
        if school == "北京电影学院":
            row["official_evidence_urls"] = add_unique_list(
                row["official_evidence_urls"],
                [
                    "http://www.bfa.edu.cn/yanjiusheng/info/1049/2939.htm",
                    "http://www.bfa.edu.cn/yanjiusheng/info/1031/3724.htm",
                    "http://www.bfa.edu.cn/yanjiusheng/info/1031/4405.htm",
                ],
                separator="|",
            )
            row["recheck_result"] = (
                "final-list and first-choice admitted-list pages still not accessible from public fetch; "
                "2022/2023/2025 historical http pages also return HTTP 412 challenge; "
                "official candidate-number PDF remains readable but non-final"
            )
        elif school == "中国医科大学":
            row["official_evidence_urls"] = add_unique_list(
                row["official_evidence_urls"],
                [
                    "https://www.cmu.edu.cn/cmuyjs/info/1905/9515.htm",
                    "https://www.cmu.edu.cn/cmuyjs/info/1905/9514.htm",
                    "https://www.cmu.edu.cn/cmuyjs/info/1905/9236.htm",
                ],
                separator="|",
            )
            row["recheck_result"] = (
                "old download bridge and cmuyjs official candidate pages currently return HTTP 404 "
                "or HTML download bridge; 1905/9515, 1905/9514, and 1905/9236 precise paths "
                "also return 1693-byte HTTP 404 system pages"
            )
        elif school == "重庆邮电大学":
            row["official_evidence_urls"] = add_unique_list(
                row["official_evidence_urls"],
                [
                    "https://eccs.cqupt.edu.cn/info/1012/1163.htm",
                    "https://eccs.cqupt.edu.cn/info/1012/1143.htm",
                    "https://eccs.cqupt.edu.cn/info/1012/1103.htm",
                ],
                separator="|",
            )
            row["recheck_result"] = (
                "official homepage is readable and exact 2026 direct-doctoral/recommendation-exempt "
                "candidate URL is known; graduate-school detail fetch still returns HTTP 412; "
                "ECCS subsite 2026/2025/2024 candidate detail pages also return HTTP 412"
            )
    write_csv(path, rows, fieldnames)


def main() -> None:
    update_source_attempts()
    update_remaining_tracker()
    update_recheck()
    print({"updated_schools": ["北京电影学院", "中国医科大学", "重庆邮电大学"]})


if __name__ == "__main__":
    main()
