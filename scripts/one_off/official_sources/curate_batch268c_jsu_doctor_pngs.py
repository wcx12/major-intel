from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from scripts import graduate_outcome_crawler as crawler
except ImportError:  # pragma: no cover - direct script execution path
    import graduate_outcome_crawler as crawler


OUT_DIR = Path(
    "data/processed/graduate_outcomes_official_site_websearch_web_20260602_batch268c_jsu_doctor_pngs_curated"
)

SCHOOL_NAME = "吉首大学"
YEAR = 2026
DOCUMENT_TYPE = "postgraduate_admission_list"
ROUTE = "postgraduate_exam_or_admission"

IMAGE_SOURCES = {
    "人文学院": {
        "title": "人文学院2026年博士研究生招生考试拟录取公示",
        "source_url": "https://yjsc.jsu.edu.cn/docs/2026-06/d913622cbe834762b72c402287fb35dd.png",
    },
    "体育科学学院": {
        "title": "吉首大学2026年拟录取博士研究生情况公示（体育科学学院）",
        "source_url": "https://yjsc.jsu.edu.cn/docs/2026-06/fe46a846c5d24df2885ca40caed4ebf3.png",
    },
    "生命科学学院": {
        "title": "吉首大学2026年博士研究生招生考试拟录取公示（生命科学学院）",
        "source_url": "https://yjsc.jsu.edu.cn/docs/2026-04/c133ae78e2324b2a9329e07ff96fc82e.png",
    },
}


RAW_ROWS = [
    {
        "college": "人文学院",
        "rows": [
            ("1", "10531610000013", "向茜", "民族学", "马克思主义民族理论与政策", "丁建军", "221", "87.15", "80.41", ""),
            ("2", "10531610000018", "杨凡", "民族学", "马克思主义民族理论与政策", "暨爱民", "224", "83.08", "78.87", "研究方向内调剂至龙先琼教授"),
            ("3", "10531610000005", "梁克难", "民族学", "马克思主义民族理论与政策", "暨爱民", "208", "86.78", "78.05", ""),
            ("4", "10531610000009", "黄碧蓉", "民族学", "马克思主义民族理论与政策", "蒋辉", "226", "70.78", "73.05", ""),
            ("5", "10531610000008", "刘兆阳", "民族学", "马克思主义民族理论与政策", "蒋辉", "209", "88.48", "79.07", ""),
            ("6", "10531610000029", "张宝嫔", "民族学", "中华民族学", "廖志坤", "207", "80.25", "74.63", ""),
            ("7", "10531610000028", "彭文佳", "民族学", "中华民族学", "瞿州莲", "244", "87.20", "84.27", ""),
            ("8", "10531610000019", "欧阳卉", "民族学", "中华民族学", "邵侃", "220", "88.65", "80.99", ""),
            ("9", "10531610000022", "曾锐冲", "民族学", "中华民族学", "邵侃", "219", "77.65", "75.33", ""),
            ("10", "10531610000040", "曹佳", "民族学", "人类学与世界民族", "姜又春", "198", "85.47", "75.74", ""),
            ("12", "10531610000038", "李玲", "民族学", "人类学与世界民族", "瞿建慧", "227", "81.39", "78.53", ""),
        ],
    },
    {
        "college": "体育科学学院",
        "rows": [
            ("1", "10531610000056", "李雄杰", "体育学", "运动人体科学", "谌晓安", "223", "89", "89.50", "81.51", "合格", ""),
            ("3", "10531610000049", "罗湘豫", "体育学", "体育人文社会学", "张天成", "209", "90", "83.25", "79.68", "合格", ""),
            ("4", "10531610000047", "寇朝阳", "体育学", "体育人文社会学", "周道平", "192", "87", "91.00", "75.61", "合格", ""),
            ("5", "10531610000043", "方菊艳", "体育学", "体育人文社会学", "周道平", "184", "89", "85.00", "75.06", "合格", ""),
            ("6", "10531610000046", "刘薇", "体育学", "体育人文社会学", "张天成", "187", "79", "85.75", "71.18", "合格", ""),
            ("8", "10531610000061", "赵龙傲", "体育学", "民族传统体育学", "万义", "229", "85", "83.50", "80.77", "合格", ""),
            ("9", "10531610000062", "田纪元", "体育学", "民族传统体育学", "万义", "215", "88", "87.75", "79.91", "合格", ""),
            ("10", "10531610000059", "辛欣", "体育学", "民族传统体育学", "白晋湘", "224", "84", "82.50", "79.35", "合格", ""),
            ("11", "10531610000082", "司玥", "体育学", "民族传统体育学", "吴湘军", "206", "86", "83.50", "77.12", "合格", ""),
            ("12", "10531610000068", "王林圭", "体育学", "民族传统体育学", "郭振华", "205", "86", "86.50", "77.01", "合格", ""),
            ("13", "10531610000074", "龙芳", "体育学", "民族传统体育学", "郭振华", "204", "84", "84.75", "76.22", "合格", "研究方向内调至龙佩林教授"),
            ("14", "10531610000070", "沈鑫", "体育学", "民族传统体育学", "郭振华", "185", "86", "85.50", "73.99", "合格", "研究方向内调至白晋湘教授"),
            ("15", "10531610000090", "王令智", "体育学", "民族传统体育学", "郭振华", "184", "81", "85.40", "71.48", "合格", "研究方向内调至龙佩林教授"),
        ],
    },
    {
        "college": "生命科学学院",
        "rows": [
            ("1", "105316100000102", "苏康妮", "生态学", "植物生态学", "谭敦炎", "199", "86.00", "76.17", ""),
            ("2", "105316100000101", "吴玉", "生态学", "植物生态学", "孟盈", "202", "82.93", "75.13", ""),
            ("3", "105316100000100", "杨丽", "生态学", "植物生态学", "孟盈", "186", "83.08", "72.54", "同方向调剂至李鹂"),
            ("4", "105316100000104", "王丞", "生态学", "动物生态学", "蒋万胜", "237", "89.01", "84.01", ""),
            ("5", "105316100000109", "程俊伟", "生态学", "修复生态学", "周强", "219", "87.64", "80.32", ""),
            ("6", "105316100000106", "吕定红", "生态学", "修复生态学", "周强", "195", "82.80", "73.90", ""),
            ("7", "105316100000108", "米盈", "生态学", "修复生态学", "马陶武", "214", "87.15", "79.24", ""),
            ("8", "105316100000105", "肖锦扬", "生态学", "修复生态学", "马陶武", "169", "73.05", "64.69", "同专业调剂至孟盈"),
            ("9", "105316100000107", "彭胜", "生态学", "修复生态学", "何兴兵", "202", "86.41", "76.87", ""),
            ("10", "105316100000111", "罗玉杰", "生态学", "武陵山区可持续生态学", "吴吉林", "230", "90.46", "83.56", ""),
            ("11", "105316100000115", "李先富", "生态学", "武陵山区可持续生态学", "吴吉林", "236", "83.30", "80.98", ""),
            ("12", "105316100000112", "刘伍洋", "生态学", "武陵山区可持续生态学", "吴吉林", "226", "83.41", "79.37", "同方向调剂至彭清忠"),
            ("13", "105316100000116", "王建霞", "生态学", "武陵山区可持续生态学", "彭清忠", "229", "86.09", "81.21", ""),
        ],
    },
]


def _remarks(
    advisor: str,
    initial_score: str,
    retest_score: str,
    final_score: str,
    note: str = "",
    interview_score: str = "",
    foreign_language_score: str = "",
    political_result: str = "",
) -> str:
    parts = [f"报考导师: {advisor}", f"初试成绩: {initial_score}"]
    if interview_score:
        parts.append(f"面试成绩: {interview_score}")
    if retest_score:
        parts.append(f"复试成绩: {retest_score}")
    if foreign_language_score:
        parts.append(f"外语能力测试成绩: {foreign_language_score}")
    parts.append(f"综合成绩: {final_score}")
    if political_result:
        parts.append(f"政治素质考核结论: {political_result}")
    parts.append("是否拟录取: 拟录取")
    if note:
        parts.append(note)
    return "; ".join(parts)


def _record(
    college: str,
    ranking: str,
    student_id: str,
    person_name: str,
    major: str,
    admission_major: str,
    advisor: str,
    initial_score: str,
    retest_score: str,
    final_score: str,
    note: str = "",
    interview_score: str = "",
    foreign_language_score: str = "",
    political_result: str = "",
) -> dict[str, Any]:
    source = IMAGE_SOURCES[college]
    return crawler._clean_record(
        {
            "school_name": SCHOOL_NAME,
            "year": YEAR,
            "document_type": DOCUMENT_TYPE,
            "route": ROUTE,
            "person_name": person_name,
            "student_id": student_id,
            "undergraduate_school": "",
            "undergraduate_major": "",
            "college": college,
            "major": major,
            "admission_major": admission_major,
            "ranking": ranking,
            "remarks": _remarks(
                advisor,
                initial_score,
                retest_score,
                final_score,
                note=note,
                interview_score=interview_score,
                foreign_language_score=foreign_language_score,
                political_result=political_result,
            ),
            "source_url": source["source_url"],
            "title": source["title"],
            "needs_review": False,
        }
    )


def curate_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for group in RAW_ROWS:
        college = group["college"]
        for row in group["rows"]:
            if college == "体育科学学院":
                (
                    ranking,
                    student_id,
                    person_name,
                    major,
                    admission_major,
                    advisor,
                    initial_score,
                    interview_score,
                    foreign_language_score,
                    final_score,
                    political_result,
                    note,
                ) = row
                records.append(
                    _record(
                        college,
                        ranking,
                        student_id,
                        person_name,
                        major,
                        admission_major,
                        advisor,
                        initial_score,
                        "",
                        final_score,
                        note=note,
                        interview_score=interview_score,
                        foreign_language_score=foreign_language_score,
                        political_result=political_result,
                    )
                )
            else:
                ranking, student_id, person_name, major, admission_major, advisor, initial_score, retest_score, final_score, note = row
                records.append(
                    _record(
                        college,
                        ranking,
                        student_id,
                        person_name,
                        major,
                        admission_major,
                        advisor,
                        initial_score,
                        retest_score,
                        final_score,
                        note=note,
                    )
                )
    return records


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = curate_records()
    output = OUT_DIR / "records_clean_curated.csv"
    crawler._write_clean_records_csv(rows, output)
    print({"records": len(rows), "output": str(output)})


if __name__ == "__main__":
    main()
