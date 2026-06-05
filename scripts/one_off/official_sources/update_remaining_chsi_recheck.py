from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ATTEMPTS = (
    ROOT / "data/processed/graduate_outcomes_official_recommendation_remaining15/source_attempts.csv"
)
REMAINING = ROOT / "outputs/graduate_outcomes/remaining_uncovered_schools.csv"
RECHECK = ROOT / "outputs/graduate_outcomes/remaining_uncovered_recheck_2026-06-04.csv"


CHSI_EVIDENCE = {
    "北京电影学院": {
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368276.dhtml",
        "artifact": "data/raw/official_recommendation_bfa_historical_412/bfa_chsi_schoolinfo_20260604.html",
        "note": "2026-06-04 CHSI recheck: official CHSI schoolInfo page returned HTTP 200, but the public school page exposes admissions/bulletin information rather than a person-level final recommendation/admission list.",
    },
    "成都体育学院": {
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368492.dhtml",
        "artifact": "data/raw/official_recommendation_cdsu_waf_current/cdsu_chsi_schoolinfo_20260604.html",
        "note": "2026-06-04 CHSI recheck: official CHSI schoolInfo page returned HTTP 200, but no public person-level final recommendation/admission rows were exposed.",
    },
    "西藏农牧大学": {
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-2107935185.dhtml",
        "artifact": "data/raw/official_site_recommendation_websearch_web_20260602_batch491_xza_2025_adjustment_score_probe/xza_chsi_schoolinfo_20260604.html",
        "note": "2026-06-04 CHSI recheck: official CHSI schoolInfo page returned HTTP 200 and lists招生简章/复试录取办法/调剂公告, but no person-level final admitted-list rows.",
    },
    "重庆邮电大学": {
        "url": "https://yz.chsi.com.cn/sch/schoolInfo--schId-368454.dhtml",
        "artifact": "data/raw/official_recommendation_cqupt_blocked_pages/cqupt_chsi_schoolinfo_20260604.html",
        "note": "2026-06-04 CHSI recheck: official CHSI schoolInfo page returned HTTP 200, but public CHSI school information does not expose the row-level final lists blocked on the graduate-school detail pages.",
    },
}

CHSI_MDGS_EVIDENCE = {
    "url": "https://yz.chsi.com.cn/zsgs/mdgs/?entrytype=yzgr",
    "artifact": "data/raw/official_recommendation_chsi_mdgs_login_required_20260604.html",
    "note": "2026-06-04 CHSI admission-list portal recheck: the official 全国硕士研究生招生信息公开平台录取名单入口 redirects to account.chsi.com.cn login, so no public row-level list body is available without an authenticated user session.",
}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_value(current: str, addition: str, separator: str) -> str:
    parts = [part.strip() for part in current.split(separator) if part.strip()]
    if addition not in parts:
        parts.append(addition)
    return separator.join(parts)


def append_sentence(current: str, sentence: str) -> str:
    current = current.strip()
    if sentence in current:
        return current
    if not current:
        return sentence
    return f"{current}; {sentence}"


def update_source_attempts() -> None:
    fieldnames, rows = read_rows(SOURCE_ATTEMPTS)
    for row in rows:
        evidence = CHSI_EVIDENCE.get(row["school_name"])
        if evidence:
            row["source_url"] = append_value(row["source_url"], evidence["url"], "; ")
            row["local_artifact"] = append_value(row["local_artifact"], evidence["artifact"], "; ")
            row["notes"] = append_sentence(row["notes"], evidence["note"])
        if row["school_name"] in {
            "北京电影学院",
            "成都体育学院",
            "宁波诺丁汉大学",
            "西藏农牧大学",
            "重庆邮电大学",
        }:
            row["source_url"] = append_value(
                row["source_url"], CHSI_MDGS_EVIDENCE["url"], "; "
            )
            row["local_artifact"] = append_value(
                row["local_artifact"], CHSI_MDGS_EVIDENCE["artifact"], "; "
            )
            row["notes"] = append_sentence(row["notes"], CHSI_MDGS_EVIDENCE["note"])
        if evidence or row["school_name"] in {
            "北京电影学院",
            "成都体育学院",
            "宁波诺丁汉大学",
            "西藏农牧大学",
            "重庆邮电大学",
        }:
            row["last_checked_date"] = "2026-06-04"
    write_rows(SOURCE_ATTEMPTS, fieldnames, rows)


def update_remaining() -> None:
    fieldnames, rows = read_rows(REMAINING)
    for row in rows:
        evidence = CHSI_EVIDENCE.get(row["school_name"])
        if evidence:
            row["official_candidate_urls"] = append_value(
                row["official_candidate_urls"], evidence["url"], "|"
            )
            row["current_status"] = append_sentence(row["current_status"], evidence["note"])
        if row["school_name"] in {
            "北京电影学院",
            "成都体育学院",
            "宁波诺丁汉大学",
            "西藏农牧大学",
            "重庆邮电大学",
        }:
            row["official_candidate_urls"] = append_value(
                row["official_candidate_urls"], CHSI_MDGS_EVIDENCE["url"], "|"
            )
            row["current_status"] = append_sentence(
                row["current_status"], CHSI_MDGS_EVIDENCE["note"]
            )
    write_rows(REMAINING, fieldnames, rows)


def update_recheck() -> None:
    fieldnames, rows = read_rows(RECHECK)
    for row in rows:
        evidence = CHSI_EVIDENCE.get(row["school_name"])
        if evidence:
            row["official_evidence_urls"] = append_value(
                row["official_evidence_urls"], evidence["url"], "|"
            )
            row["recheck_result"] = append_sentence(row["recheck_result"], evidence["note"])
        if row["school_name"] in {
            "北京电影学院",
            "成都体育学院",
            "宁波诺丁汉大学",
            "西藏农牧大学",
            "重庆邮电大学",
        }:
            row["official_evidence_urls"] = append_value(
                row["official_evidence_urls"], CHSI_MDGS_EVIDENCE["url"], "|"
            )
            row["recheck_result"] = append_sentence(
                row["recheck_result"], CHSI_MDGS_EVIDENCE["note"]
            )
    write_rows(RECHECK, fieldnames, rows)


def main() -> None:
    update_source_attempts()
    update_remaining()
    update_recheck()


if __name__ == "__main__":
    main()
