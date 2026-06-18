import csv
import json

from scripts.ingestion.build_rysxai_transfer_policy_profiles import (
    build_rysxai_transfer_policy_profiles,
)


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


POLICY_FIELDS = [
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

MAJOR_FIELDS = [
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


def test_build_transfer_policy_profiles_extracts_flags_faculties_and_major_mentions(tmp_path):
    transfer = tmp_path / "transfer.csv"
    seed = tmp_path / "seed.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    ai = tmp_path / "ai.csv"
    schools = tmp_path / "schools.csv"
    faculties = tmp_path / "faculties.csv"
    majors = tmp_path / "majors.csv"
    summary = tmp_path / "summary.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    law = "\u6cd5\u5b66"
    computer = "\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f"
    nursing = "\u62a4\u7406\u5b66"
    gpa = "GPA"
    ranking = "\u6392\u540d"
    written_exam = "\u7b14\u8bd5"
    interview = "\u9762\u8bd5"
    quota = "\u540d\u989d"
    no_accept = "\u4e0d\u63a5\u6536"
    strong_base = "\u5f3a\u57fa"
    color_blind = "\u8272\u76f2"
    law_class = "\u6cd5\u5b66\u7c7b"

    write_csv(
        seed,
        [
            {
                "rysxai_profession_id": "1",
                "major_code": "030101",
                "major_name": law,
                "level": "\u672c\u79d1",
                "category": "\u6cd5\u5b66",
                "subject": law_class,
                "degree": "",
                "limit_year": "",
                "heat": "",
                "is_hot": "",
            },
            {
                "rysxai_profession_id": "2",
                "major_code": "080901",
                "major_name": computer,
                "level": "\u672c\u79d1",
                "category": "\u5de5\u5b66",
                "subject": "\u8ba1\u7b97\u673a\u7c7b",
                "degree": "",
                "limit_year": "",
                "heat": "",
                "is_hot": "",
            },
            {
                "rysxai_profession_id": "3",
                "major_code": "101101",
                "major_name": nursing,
                "level": "\u672c\u79d1",
                "category": "\u533b\u5b66",
                "subject": "\u62a4\u7406\u5b66\u7c7b",
                "degree": "",
                "limit_year": "",
                "heat": "",
                "is_hot": "",
            },
        ],
        MAJOR_FIELDS,
    )
    faculty_json = [
        {
            "faculty_name": "\u8ba1\u7b97\u673a\u5b66\u9662",
            "columns": [{"key": "condition", "title": "\u7533\u8bf7\u6761\u4ef6"}],
            "condition": f"{computer}\u9700{gpa}\u4e0d\u4f4e\u4e8e3.5\uff0c\u7ec4\u7ec7{written_exam}\u548c{interview}\u3002",
        }
    ]
    policy_text = (
        f"\u5b66\u751f\u53ef\u7533\u8bf7\u8f6c\u4e13\u4e1a\uff0c{law_class}\u6309\u5b66\u9662\u8981\u6c42\u590d\u6838\u3002"
        f"{nursing}{no_accept}{color_blind}\u8003\u751f\uff0c{strong_base}\u8ba1\u5212\u539f\u5219\u4e0a\u4e0d\u5f97\u8f6c\u51fa\u3002"
    )
    write_csv(
        transfer,
        [
            {
                "fetched_at": "2026-05-20T12:00:00+08:00",
                "school_id": "1",
                "school_name": "Test University",
                "province": "Test",
                "city": "Test City",
                "type": "\u7efc\u5408",
                "property": "\u516c\u529e",
                "level": "\u672c\u79d1",
                "department": "\u6559\u80b2\u90e8",
                "tags_json": json.dumps(["985", "211"], ensure_ascii=False),
                "source_url": "https://example.test/transfer",
                "has_transfer_policy": "true",
                "has_faculty_policy": "true",
                "faculty_policy_count": "1",
                "change_profession_chars": str(len(policy_text)),
                "application_condition_chars": "0",
                "admission_requirement_chars": "0",
                "assessment_chars": "0",
                "is_new_version": "true",
                "change_profession": policy_text,
                "change_profession_application_condition": "",
                "change_profession_admission_requirement": "",
                "change_profession_assessment": f"{ranking}\u548c{quota}\u63a7\u5236",
                "change_profession_by_faculty_json": json.dumps(faculty_json, ensure_ascii=False),
            },
            {
                "fetched_at": "2026-05-20T12:00:00+08:00",
                "school_id": "2",
                "school_name": "No Policy College",
                "province": "Test",
                "city": "Test City",
                "type": "\u7406\u5de5",
                "property": "\u6c11\u529e",
                "level": "\u672c\u79d1",
                "department": "",
                "tags_json": "[]",
                "source_url": "https://example.test/empty",
                "has_transfer_policy": "false",
                "has_faculty_policy": "false",
                "faculty_policy_count": "0",
                "change_profession_chars": "0",
                "application_condition_chars": "0",
                "admission_requirement_chars": "0",
                "assessment_chars": "0",
                "is_new_version": "false",
                "change_profession": "",
                "change_profession_application_condition": "",
                "change_profession_admission_requirement": "",
                "change_profession_assessment": "",
                "change_profession_by_faculty_json": "[]",
            },
        ],
        POLICY_FIELDS,
    )
    write_csv(
        employment,
        [
            {
                "record_id": "risk1",
                "report_year": "2025",
                "risk_level": "red",
                "reported_major_name": nursing,
                "standard_major_name": nursing,
            }
        ],
        ["record_id", "report_year", "risk_level", "reported_major_name", "standard_major_name"],
    )
    write_csv(
        policy,
        [
            {
                "warning_id": "policy1",
                "policy_year": "2024",
                "record_type": "major_cancel",
                "reported_major_name": computer,
                "standard_major_name": computer,
            }
        ],
        ["warning_id", "policy_year", "record_type", "reported_major_name", "standard_major_name"],
    )
    write_csv(
        ai,
        [
            {
                "major_name": computer,
                "rank": "3",
                "ai_replacement_score": "65.5",
                "ai_replacement_level": "medium",
                "confidence_score": "80",
                "candidate_count": "12",
            }
        ],
        [
            "major_name",
            "rank",
            "ai_replacement_score",
            "ai_replacement_level",
            "confidence_score",
            "candidate_count",
        ],
    )

    result = build_rysxai_transfer_policy_profiles(
        transfer_policies_csv=transfer,
        major_seed_csv=seed,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        ai_replacement_csv=ai,
        output_school_profiles_csv=schools,
        output_faculty_profiles_csv=faculties,
        output_major_mentions_csv=majors,
        output_summary_csv=summary,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    school_rows = {row["school_name"]: row for row in read_rows(schools)}
    faculty_rows = read_rows(faculties)
    major_rows = {row["major_name"]: row for row in read_rows(majors)}
    assert result["input_school_count"] == 2
    assert result["faculty_profile_count"] == 1
    assert school_rows["Test University"]["has_gpa_requirement"] == "true"
    assert school_rows["Test University"]["has_rank_requirement"] == "true"
    assert school_rows["Test University"]["has_quota_limit"] == "true"
    assert school_rows["Test University"]["has_major_restriction"] == "true"
    assert school_rows["Test University"]["has_special_enrollment_restriction"] == "true"
    assert school_rows["Test University"]["has_physical_requirement"] == "true"
    assert school_rows["No Policy College"]["transfer_difficulty_level"] == "unknown"
    assert faculty_rows[0]["faculty_name"] == "\u8ba1\u7b97\u673a\u5b66\u9662"
    assert faculty_rows[0]["has_exam_requirement"] == "true"
    assert major_rows[computer]["mentioned_in_school_count"] == "1"
    assert major_rows[computer]["mentioned_in_faculty_count"] == "1"
    assert major_rows[computer]["has_official_policy_warning"] == "true"
    assert major_rows[computer]["ai_replacement_score"] == "65.5"
    assert major_rows[nursing]["has_employment_red_warning"] == "true"
    assert major_rows[law]["mentioned_in_school_count"] == "0"
    assert json.loads(manifest.read_text(encoding="utf-8"))["school_profile_count"] == 2
