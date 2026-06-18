import csv
import json

from scripts.ingestion.build_rysxai_civil_service_major_opportunities import (
    build_rysxai_civil_service_major_opportunities,
)


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))


CIVIL_FIELDS = [
    "id",
    "year",
    "source_url",
    "position_code",
    "department_name",
    "sub_department",
    "job_name",
    "department_level",
    "exam_type",
    "province",
    "work_location",
    "plan_num",
    "apply_num",
    "ratio",
    "profession",
    "education_level",
    "degree_requirement",
    "identity",
    "work_year",
    "work_experience",
    "need_test",
    "is_new_graduate",
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


def test_build_civil_service_major_opportunities_matches_codes_subjects_and_aliases(tmp_path):
    civil = tmp_path / "civil.csv"
    seed = tmp_path / "seed.csv"
    employment = tmp_path / "employment.csv"
    policy = tmp_path / "policy.csv"
    ai = tmp_path / "ai.csv"
    major_out = tmp_path / "major.csv"
    role_summary = tmp_path / "roles.csv"
    role_major = tmp_path / "role_major.csv"
    unmatched = tmp_path / "unmatched.csv"
    manifest = tmp_path / "manifest.json"
    report = tmp_path / "report.md"

    building_env = "\u5efa\u7b51\u73af\u5883\u4e0e\u80fd\u6e90\u5e94\u7528\u5de5\u7a0b"
    computer = "\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f"
    software = "\u8f6f\u4ef6\u5de5\u7a0b"
    accounting = "\u4f1a\u8ba1\u5b66"
    auditing = "\u5ba1\u8ba1\u5b66"
    computer_class = "\u8ba1\u7b97\u673a\u7c7b"
    audit_class = "\u8d22\u4f1a\u5ba1\u8ba1\u7c7b"
    unknown_class = "\u706b\u661f\u5de5\u7a0b\u7c7b"
    no_limit = "\u4e0d\u9650"
    unlimited = "\u65e0\u9650\u5236"
    bachelor_above = "\u672c\u79d1\u53ca\u4ee5\u4e0a"
    bachelor_only = "\u4ec5\u9650\u672c\u79d1"
    central = "\u4e2d\u592e"
    county = "\u53bf\uff08\u533a\uff09\u7ea7\u53ca\u4ee5\u4e0b"
    party = "\u4e2d\u5171\u515a\u5458"
    yes = "\u662f"
    no = "\u5426"

    write_csv(
        seed,
        [
            {
                "rysxai_profession_id": "1",
                "major_code": "081002",
                "major_name": building_env,
                "level": "\u672c\u79d1",
                "category": "\u5de5\u5b66",
                "subject": "\u571f\u6728\u7c7b",
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
                "subject": computer_class,
                "degree": "",
                "limit_year": "",
                "heat": "",
                "is_hot": "",
            },
            {
                "rysxai_profession_id": "3",
                "major_code": "080902",
                "major_name": software,
                "level": "\u672c\u79d1",
                "category": "\u5de5\u5b66",
                "subject": computer_class,
                "degree": "",
                "limit_year": "",
                "heat": "",
                "is_hot": "",
            },
            {
                "rysxai_profession_id": "4",
                "major_code": "120203",
                "major_name": accounting,
                "level": "\u672c\u79d1",
                "category": "\u7ba1\u7406\u5b66",
                "subject": "\u5de5\u5546\u7ba1\u7406\u7c7b",
                "degree": "",
                "limit_year": "",
                "heat": "",
                "is_hot": "",
            },
            {
                "rysxai_profession_id": "5",
                "major_code": "120207",
                "major_name": auditing,
                "level": "\u672c\u79d1",
                "category": "\u7ba1\u7406\u5b66",
                "subject": "\u5de5\u5546\u7ba1\u7406\u7c7b",
                "degree": "",
                "limit_year": "",
                "heat": "",
                "is_hot": "",
            },
        ],
        MAJOR_FIELDS,
    )
    write_csv(
        civil,
        [
            {
                "id": "r1",
                "year": "2026",
                "source_url": "https://example.test/r1",
                "position_code": "p1",
                "department_name": "Dept A",
                "sub_department": "Sub A",
                "job_name": "Role A",
                "department_level": central,
                "exam_type": "exam",
                "province": "Beijing",
                "work_location": "Beijing",
                "plan_num": "2",
                "apply_num": "448",
                "ratio": "224",
                "profession": "081002" + building_env,
                "education_level": bachelor_only,
                "degree_requirement": "",
                "identity": party,
                "work_year": unlimited,
                "work_experience": unlimited,
                "need_test": yes,
                "is_new_graduate": "False",
            },
            {
                "id": "r2",
                "year": "2026",
                "source_url": "https://example.test/r2",
                "position_code": "p2",
                "department_name": "Dept B",
                "sub_department": "Sub B",
                "job_name": "Role B",
                "department_level": county,
                "exam_type": "exam",
                "province": "Zhejiang",
                "work_location": "Zhejiang",
                "plan_num": "3",
                "apply_num": "30",
                "ratio": "10",
                "profession": computer_class,
                "education_level": bachelor_above,
                "degree_requirement": "",
                "identity": no_limit,
                "work_year": unlimited,
                "work_experience": unlimited,
                "need_test": no,
                "is_new_graduate": "True",
            },
            {
                "id": "r3",
                "year": "2026",
                "source_url": "https://example.test/r3",
                "position_code": "p3",
                "department_name": "Dept C",
                "sub_department": "Sub C",
                "job_name": "Role C",
                "department_level": county,
                "exam_type": "exam",
                "province": "Jiangsu",
                "work_location": "Jiangsu",
                "plan_num": "1",
                "apply_num": "2",
                "ratio": "2",
                "profession": audit_class,
                "education_level": bachelor_above,
                "degree_requirement": "",
                "identity": no_limit,
                "work_year": unlimited,
                "work_experience": unlimited,
                "need_test": no,
                "is_new_graduate": "False",
            },
            {
                "id": "r4",
                "year": "2026",
                "source_url": "https://example.test/r4",
                "position_code": "p4",
                "department_name": "Dept D",
                "sub_department": "Sub D",
                "job_name": "Role D",
                "department_level": county,
                "exam_type": "exam",
                "province": "Jiangsu",
                "work_location": "Jiangsu",
                "plan_num": "1",
                "apply_num": "1",
                "ratio": "1",
                "profession": unknown_class,
                "education_level": bachelor_above,
                "degree_requirement": "",
                "identity": no_limit,
                "work_year": unlimited,
                "work_experience": unlimited,
                "need_test": no,
                "is_new_graduate": "False",
            },
        ],
        CIVIL_FIELDS,
    )
    write_csv(
        employment,
        [
            {
                "record_id": "risk1",
                "report_year": "2025",
                "risk_level": "yellow",
                "reported_major_name": software,
                "standard_major_name": software,
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
                "reported_major_name": accounting,
                "standard_major_name": accounting,
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

    result = build_rysxai_civil_service_major_opportunities(
        civil_service_csv=civil,
        major_seed_csv=seed,
        employment_warnings_csv=employment,
        official_policy_warnings_csv=policy,
        ai_replacement_csv=ai,
        output_major_csv=major_out,
        output_role_summary_csv=role_summary,
        output_role_major_matches_csv=role_major,
        output_unmatched_terms_csv=unmatched,
        output_manifest_json=manifest,
        output_report_md=report,
    )

    major_rows = {row["major_name"]: row for row in read_rows(major_out)}
    role_rows = {row["role_id"]: row for row in read_rows(role_summary)}
    match_rows = read_rows(role_major)
    unmatched_rows = {row["unmatched_term"]: row for row in read_rows(unmatched)}

    assert result["input_role_count"] == 4
    assert result["matched_role_count"] == 3
    assert result["role_major_match_count"] == 5
    assert major_rows[building_env]["exact_role_match_count"] == "1"
    assert major_rows[building_env]["weighted_competition_ratio"] == "224"
    assert major_rows[computer]["broad_role_match_count"] == "1"
    assert major_rows[computer]["ai_replacement_score"] == "65.5"
    assert major_rows[software]["has_employment_yellow_warning"] == "true"
    assert major_rows[accounting]["has_official_policy_warning"] == "true"
    assert role_rows["r2"]["is_low_restriction_role"] == "true"
    assert role_rows["r4"]["matched_major_count"] == "0"
    assert unknown_class in unmatched_rows
    assert len({row["role_major_match_id"] for row in match_rows}) == len(match_rows)
    assert json.loads(manifest.read_text(encoding="utf-8"))["major_opportunity_row_count"] == 5
