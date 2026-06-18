"""Build major-level civil-service opportunity profiles from rysxai role data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "rysxai_civil_service_major_opportunities/v1"

ROLE_SUMMARY_FIELDS = [
    "role_id",
    "year",
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
    "competition_ratio",
    "profession_text",
    "education_level",
    "degree_requirement",
    "identity",
    "work_year",
    "work_experience",
    "need_test",
    "is_new_graduate",
    "is_low_restriction_role",
    "matched_major_count",
    "matched_major_names_sample",
    "matched_subjects",
    "matched_categories",
    "match_methods",
    "unmatched_terms",
    "source_url",
    "source_level",
    "data_scope",
]

ROLE_MAJOR_MATCH_FIELDS = [
    "role_major_match_id",
    "role_id",
    "year",
    "position_code",
    "department_name",
    "job_name",
    "department_level",
    "exam_type",
    "province",
    "work_location",
    "plan_num",
    "apply_num",
    "competition_ratio",
    "profession_text",
    "education_level",
    "degree_requirement",
    "identity",
    "work_year",
    "work_experience",
    "need_test",
    "is_new_graduate",
    "is_low_restriction_role",
    "major_code",
    "major_name",
    "major_level",
    "category",
    "subject",
    "match_scope",
    "match_methods",
    "matched_terms",
    "source_url",
    "source_level",
    "data_scope",
]

MAJOR_FIELDS = [
    "civil_service_major_id",
    "major_code",
    "major_name",
    "major_level",
    "category",
    "subject",
    "has_civil_service_match",
    "opportunity_level",
    "rank_by_role_match_count",
    "rank_by_plan_num_sum",
    "role_match_count",
    "exact_role_match_count",
    "broad_role_match_count",
    "plan_num_sum",
    "apply_num_sum",
    "weighted_competition_ratio",
    "avg_competition_ratio",
    "median_competition_ratio",
    "min_competition_ratio",
    "max_competition_ratio",
    "avg_plan_num",
    "new_graduate_role_count",
    "low_restriction_role_count",
    "central_role_count",
    "provincial_role_count",
    "city_role_count",
    "county_or_below_role_count",
    "need_test_role_count",
    "party_member_role_count",
    "bachelor_only_role_count",
    "bachelor_or_above_role_count",
    "master_or_above_role_count",
    "province_count",
    "department_count",
    "sample_provinces",
    "sample_departments",
    "sample_job_names",
    "sample_profession_texts",
    "employment_warning_count",
    "employment_risk_levels",
    "employment_warning_years",
    "employment_warning_record_ids",
    "has_employment_high_risk_warning",
    "has_employment_red_warning",
    "has_employment_yellow_warning",
    "has_employment_green_signal",
    "official_policy_warning_count",
    "official_policy_record_types",
    "official_policy_years",
    "official_policy_warning_ids",
    "has_official_policy_warning",
    "ai_replacement_match_count",
    "ai_replacement_rank",
    "ai_replacement_score",
    "ai_replacement_level",
    "ai_confidence_score",
    "ai_candidate_count",
    "source_level",
    "data_scope",
]

UNMATCHED_FIELDS = [
    "unmatched_term",
    "role_count",
    "plan_num_sum",
    "sample_role_ids",
    "sample_profession_texts",
    "source_level",
    "data_scope",
]

NO_LIMIT = "\u4e0d\u9650"
UNLIMITED = "\u65e0\u9650\u5236"
PARTY = "\u515a\u5458"
YES = "\u662f"

ALIAS_SUBJECT_TERMS = {
    "\u7ecf\u6d4e\u91d1\u878d\u7c7b": [
        "\u7ecf\u6d4e\u5b66\u7c7b",
        "\u8d22\u653f\u5b66\u7c7b",
        "\u91d1\u878d\u5b66\u7c7b",
        "\u7ecf\u6d4e\u4e0e\u8d38\u6613\u7c7b",
    ],
    "\u8d22\u4f1a\u5ba1\u8ba1\u7c7b": [
        "\u8d22\u52a1\u4f1a\u8ba1\u7c7b",
    ],
    "\u6c14\u8c61\u7c7b": [
        "\u5927\u6c14\u79d1\u5b66\u7c7b",
        "\u6c14\u8c61\u7c7b",
    ],
    "\u6570\u5b66": [
        "\u6570\u5b66\u7c7b",
    ],
    "\u7edf\u8ba1": [
        "\u7edf\u8ba1\u5b66\u7c7b",
        "\u7edf\u8ba1\u7c7b",
    ],
}

ALIAS_MAJOR_TERMS = {
    "\u8d22\u4f1a\u5ba1\u8ba1\u7c7b": [
        "\u4f1a\u8ba1\u5b66",
        "\u8d22\u52a1\u7ba1\u7406",
        "\u5ba1\u8ba1\u5b66",
        "\u8d44\u4ea7\u8bc4\u4f30",
        "\u8d22\u52a1\u4f1a\u8ba1\u6559\u80b2",
        "\u5927\u6570\u636e\u4e0e\u4f1a\u8ba1",
        "\u5927\u6570\u636e\u4e0e\u8d22\u52a1\u7ba1\u7406",
        "\u5927\u6570\u636e\u4e0e\u5ba1\u8ba1",
        "\u4f1a\u8ba1\u4fe1\u606f\u7ba1\u7406",
    ],
    "\u4f1a\u8ba1": [
        "\u4f1a\u8ba1\u5b66",
        "\u5927\u6570\u636e\u4e0e\u4f1a\u8ba1",
    ],
    "\u5ba1\u8ba1": [
        "\u5ba1\u8ba1\u5b66",
        "\u5927\u6570\u636e\u4e0e\u5ba1\u8ba1",
    ],
    "\u793e\u4f1a\u4fdd\u969c\u7c7b": [
        "\u52b3\u52a8\u4e0e\u793e\u4f1a\u4fdd\u969c",
    ],
    "\u82f1\u8bed\u76f8\u5173\u4e13\u4e1a": [
        "\u82f1\u8bed",
        "\u5546\u52a1\u82f1\u8bed",
        "\u5e94\u7528\u82f1\u8bed",
        "\u65c5\u6e38\u82f1\u8bed",
        "\u5c0f\u5b66\u82f1\u8bed\u6559\u80b2",
    ],
}


@dataclass(frozen=True)
class MajorRef:
    key: str
    major_code: str
    major_name: str
    level: str
    category: str
    subject: str


@dataclass
class MatchEvidence:
    major: MajorRef
    methods: set[str]
    terms: set[str]


@dataclass
class ParsedRole:
    row: dict[str, str]
    matches: dict[str, MatchEvidence]
    unmatched_terms: list[str]


class MajorMatcher:
    def __init__(self, majors: list[MajorRef]):
        self.majors = majors
        self.by_code: dict[str, list[MajorRef]] = defaultdict(list)
        self.by_code_digits: dict[str, list[MajorRef]] = defaultdict(list)
        self.by_name: dict[str, list[MajorRef]] = defaultdict(list)
        self.by_subject: dict[str, list[MajorRef]] = defaultdict(list)
        self.by_category: dict[str, list[MajorRef]] = defaultdict(list)
        for major in majors:
            self.by_code[major.major_code.upper()].append(major)
            self.by_code_digits[code_digits(major.major_code)].append(major)
            self.by_name[major.major_name].append(major)
            self.by_subject[major.subject].append(major)
            self.by_category[major.category].append(major)
        self.subject_terms = sorted(self.by_subject, key=len, reverse=True)
        self.category_terms = sorted(self.by_category, key=len, reverse=True)
        self.major_names = sorted(self.by_name, key=len, reverse=True)

    def parse_role(self, row: dict[str, str]) -> ParsedRole:
        profession = text(row.get("profession"))
        matches: dict[str, MatchEvidence] = {}
        matched_terms: set[str] = set()

        for code in extract_codes(profession):
            for major, method in self.match_code(code):
                add_match(matches, major, method, code)
                matched_terms.add(code)

        no_parens = strip_parenthetical_text(profession)
        tokens = extract_terms(no_parens)
        for token in tokens:
            before_count = len(matches)
            for major in self.by_name.get(token, []):
                add_match(matches, major, "exact_major_name", token)
            for subject in ALIAS_SUBJECT_TERMS.get(token, []):
                for major in self.by_subject.get(subject, []):
                    add_match(matches, major, "alias_subject", token)
            for major_name in ALIAS_MAJOR_TERMS.get(token, []):
                for major in self.by_name.get(major_name, []):
                    add_match(matches, major, "alias_major_name", token)
            if len(matches) > before_count:
                matched_terms.add(token)

        for subject in self.subject_terms:
            if subject and subject in no_parens:
                for major in self.by_subject[subject]:
                    add_match(matches, major, "subject_name", subject)
                matched_terms.add(subject)

        for name in self.major_names:
            if len(name) < 3:
                continue
            if name_occurs_as_major(no_parens, name):
                for major in self.by_name[name]:
                    add_match(matches, major, "exact_major_name", name)
                matched_terms.add(name)

        unmatched_terms = [
            term
            for term in tokens
            if term not in matched_terms and looks_like_profession_term(term)
        ]
        return ParsedRole(row=row, matches=matches, unmatched_terms=unmatched_terms[:20])

    def match_code(self, code: str) -> list[tuple[MajorRef, str]]:
        normalized = normalize_code(code)
        digits = code_digits(normalized)
        exact_codes = [normalized]
        if normalized and normalized[-1:].isalpha():
            exact_codes.append(normalized.rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        matches: list[tuple[MajorRef, str]] = []
        if len(digits) >= 6:
            for exact_code in exact_codes:
                for major in self.by_code.get(exact_code, []):
                    matches.append((major, "exact_major_code"))
                for major in self.by_code_digits.get(code_digits(exact_code), []):
                    matches.append((major, "exact_major_code"))
        elif len(digits) == 4:
            for major in self.majors:
                if code_digits(major.major_code).startswith(digits):
                    matches.append((major, "code_prefix_4"))
        elif len(digits) == 2:
            for major in self.majors:
                if code_digits(major.major_code).startswith(digits):
                    matches.append((major, "code_prefix_2"))
        return dedupe_major_method(matches)


def build_rysxai_civil_service_major_opportunities(
    *,
    civil_service_csv: Path,
    major_seed_csv: Path,
    employment_warnings_csv: Path,
    official_policy_warnings_csv: Path,
    ai_replacement_csv: Path,
    output_major_csv: Path,
    output_role_summary_csv: Path,
    output_role_major_matches_csv: Path,
    output_unmatched_terms_csv: Path,
    output_manifest_json: Path,
    output_report_md: Path,
) -> dict[str, Any]:
    majors = load_major_refs(major_seed_csv)
    matcher = MajorMatcher(majors)
    employment_by_name = build_warning_name_index(load_employment_warning_refs(employment_warnings_csv))
    policy_by_name = build_warning_name_index(load_policy_warning_refs(official_policy_warnings_csv))
    ai_by_name = build_ai_name_index(load_ai_replacement_refs(ai_replacement_csv))

    role_summary_rows: list[dict[str, Any]] = []
    role_major_rows: list[dict[str, Any]] = []
    unmatched_counter: dict[str, dict[str, Any]] = defaultdict(lambda: {"role_ids": set(), "plan_num_sum": 0, "profession_texts": set()})

    input_role_count = 0
    matched_role_count = 0
    for row in read_csv_rows(civil_service_csv):
        input_role_count += 1
        parsed = matcher.parse_role(row)
        if parsed.matches:
            matched_role_count += 1
        role_summary_rows.append(build_role_summary_row(parsed))
        role_major_rows.extend(build_role_major_rows(parsed))
        for term in parsed.unmatched_terms:
            entry = unmatched_counter[term]
            add_if(entry["role_ids"], row.get("id"))
            entry["plan_num_sum"] += to_int(row.get("plan_num"))
            add_if(entry["profession_texts"], row.get("profession"))

    write_csv(output_role_summary_csv, role_summary_rows, ROLE_SUMMARY_FIELDS)
    write_csv(output_role_major_matches_csv, role_major_rows, ROLE_MAJOR_MATCH_FIELDS)

    unmatched_rows = build_unmatched_rows(unmatched_counter)
    write_csv(output_unmatched_terms_csv, unmatched_rows, UNMATCHED_FIELDS)

    major_rows = build_major_rows(
        majors,
        role_major_rows,
        employment_by_name=employment_by_name,
        policy_by_name=policy_by_name,
        ai_by_name=ai_by_name,
    )
    write_csv(output_major_csv, major_rows, MAJOR_FIELDS)

    linked_employment = [row for row in major_rows if int(row["employment_warning_count"])]
    linked_high_risk = [row for row in major_rows if row["has_employment_high_risk_warning"] == "true"]
    linked_policy = [row for row in major_rows if int(row["official_policy_warning_count"])]
    linked_ai = [row for row in major_rows if int(row["ai_replacement_match_count"])]
    matched_majors = [row for row in major_rows if row["has_civil_service_match"] == "true"]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "civil_service_csv": str(civil_service_csv),
        "major_seed_csv": str(major_seed_csv),
        "employment_warnings_csv": str(employment_warnings_csv),
        "official_policy_warnings_csv": str(official_policy_warnings_csv),
        "ai_replacement_csv": str(ai_replacement_csv),
        "output_major_csv": str(output_major_csv),
        "output_role_summary_csv": str(output_role_summary_csv),
        "output_role_major_matches_csv": str(output_role_major_matches_csv),
        "output_unmatched_terms_csv": str(output_unmatched_terms_csv),
        "output_manifest_json": str(output_manifest_json),
        "output_report_md": str(output_report_md),
        "input_role_count": input_role_count,
        "matched_role_count": matched_role_count,
        "unmatched_role_count": input_role_count - matched_role_count,
        "major_seed_count": len(majors),
        "major_opportunity_row_count": len(major_rows),
        "matched_major_count": len(matched_majors),
        "role_major_match_count": len(role_major_rows),
        "role_summary_row_count": len(role_summary_rows),
        "unmatched_term_count": len(unmatched_rows),
        "linked_employment_major_count": len(linked_employment),
        "linked_high_risk_major_count": len(linked_high_risk),
        "linked_policy_major_count": len(linked_policy),
        "linked_ai_replacement_major_count": len(linked_ai),
        "source_level": "C",
    }
    output_manifest_json.parent.mkdir(parents=True, exist_ok=True)
    output_manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(output_report_md, manifest, major_rows)
    return manifest


def build_role_summary_row(parsed: ParsedRole) -> dict[str, Any]:
    row = parsed.row
    matches = list(parsed.matches.values())
    majors = sorted({match.major.major_name for match in matches})
    subjects = sorted({match.major.subject for match in matches})
    categories = sorted({match.major.category for match in matches})
    methods = sorted({method for match in matches for method in match.methods})
    return {
        "role_id": text(row.get("id")),
        "year": text(row.get("year")),
        "position_code": text(row.get("position_code")),
        "department_name": text(row.get("department_name")),
        "sub_department": text(row.get("sub_department")),
        "job_name": text(row.get("job_name")),
        "department_level": text(row.get("department_level")),
        "exam_type": text(row.get("exam_type")),
        "province": text(row.get("province")),
        "work_location": text(row.get("work_location")),
        "plan_num": to_int(row.get("plan_num")),
        "apply_num": to_int(row.get("apply_num")),
        "competition_ratio": number_text(to_float(row.get("ratio"))),
        "profession_text": text(row.get("profession")),
        "education_level": text(row.get("education_level")),
        "degree_requirement": text(row.get("degree_requirement")),
        "identity": text(row.get("identity")),
        "work_year": text(row.get("work_year")),
        "work_experience": text(row.get("work_experience")),
        "need_test": text(row.get("need_test")),
        "is_new_graduate": lower_bool_text(row.get("is_new_graduate")),
        "is_low_restriction_role": bool_text(is_low_restriction_role(row)),
        "matched_major_count": len(parsed.matches),
        "matched_major_names_sample": join_sample(majors, limit=20),
        "matched_subjects": join_sample(subjects, limit=20),
        "matched_categories": join_sample(categories, limit=20),
        "match_methods": "|".join(methods),
        "unmatched_terms": "|".join(parsed.unmatched_terms),
        "source_url": text(row.get("source_url")),
        "source_level": "C",
        "data_scope": "rysxai_civil_service_role_major_parse",
    }


def build_role_major_rows(parsed: ParsedRole) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    row = parsed.row
    role_id = text(row.get("id"))
    for match in sorted(parsed.matches.values(), key=lambda item: (item.major.major_code, item.major.major_name, item.major.level)):
        major = match.major
        methods = sorted(match.methods)
        match_scope = "exact" if any(method.startswith("exact") for method in methods) else "broad"
        rows.append(
            {
                "role_major_match_id": role_major_match_id(role_id, major.key),
                "role_id": role_id,
                "year": text(row.get("year")),
                "position_code": text(row.get("position_code")),
                "department_name": text(row.get("department_name")),
                "job_name": text(row.get("job_name")),
                "department_level": text(row.get("department_level")),
                "exam_type": text(row.get("exam_type")),
                "province": text(row.get("province")),
                "work_location": text(row.get("work_location")),
                "plan_num": to_int(row.get("plan_num")),
                "apply_num": to_int(row.get("apply_num")),
                "competition_ratio": number_text(to_float(row.get("ratio"))),
                "profession_text": text(row.get("profession")),
                "education_level": text(row.get("education_level")),
                "degree_requirement": text(row.get("degree_requirement")),
                "identity": text(row.get("identity")),
                "work_year": text(row.get("work_year")),
                "work_experience": text(row.get("work_experience")),
                "need_test": text(row.get("need_test")),
                "is_new_graduate": lower_bool_text(row.get("is_new_graduate")),
                "is_low_restriction_role": bool_text(is_low_restriction_role(row)),
                "major_code": major.major_code,
                "major_name": major.major_name,
                "major_level": major.level,
                "category": major.category,
                "subject": major.subject,
                "match_scope": match_scope,
                "match_methods": "|".join(methods),
                "matched_terms": "|".join(sorted(match.terms)),
                "source_url": text(row.get("source_url")),
                "source_level": "C",
                "data_scope": "rysxai_civil_service_role_major_match",
            }
        )
    return rows


def build_major_rows(
    majors: list[MajorRef],
    role_major_rows: list[dict[str, Any]],
    *,
    employment_by_name: dict[str, list[dict[str, str]]],
    policy_by_name: dict[str, list[dict[str, str]]],
    ai_by_name: dict[str, list[dict[str, str]]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in role_major_rows:
        key = major_key(row["major_code"], row["major_name"], row["major_level"])
        grouped[key].append(row)

    raw_rows: list[dict[str, Any]] = []
    for major in sorted(majors, key=lambda item: (item.level, item.major_code, item.major_name)):
        rows = grouped.get(major.key, [])
        ratios = [to_float(row.get("competition_ratio")) for row in rows if to_float(row.get("competition_ratio")) is not None]
        plan_sum = sum(to_int(row.get("plan_num")) for row in rows)
        apply_sum = sum(to_int(row.get("apply_num")) for row in rows)
        employment_refs = employment_by_name.get(major.major_name, [])
        policy_refs = policy_by_name.get(major.major_name, [])
        ai_refs = ai_by_name.get(major.major_name, [])
        best_ai = min(ai_refs, key=ai_sort_key) if ai_refs else None
        raw_rows.append(
            {
                "civil_service_major_id": civil_service_major_id(major.key),
                "major_code": major.major_code,
                "major_name": major.major_name,
                "major_level": major.level,
                "category": major.category,
                "subject": major.subject,
                "has_civil_service_match": bool_text(bool(rows)),
                "role_match_count": len(rows),
                "exact_role_match_count": sum(1 for row in rows if row["match_scope"] == "exact"),
                "broad_role_match_count": sum(1 for row in rows if row["match_scope"] == "broad"),
                "plan_num_sum": plan_sum,
                "apply_num_sum": apply_sum,
                "weighted_competition_ratio": number_text(apply_sum / plan_sum if plan_sum else None),
                "avg_competition_ratio": number_text(sum(ratios) / len(ratios) if ratios else None),
                "median_competition_ratio": number_text(statistics.median(ratios) if ratios else None),
                "min_competition_ratio": number_text(min(ratios) if ratios else None),
                "max_competition_ratio": number_text(max(ratios) if ratios else None),
                "avg_plan_num": number_text(plan_sum / len(rows) if rows else None),
                "new_graduate_role_count": sum(1 for row in rows if row_bool(row.get("is_new_graduate"))),
                "low_restriction_role_count": sum(1 for row in rows if is_match_row_low_restriction(row)),
                "central_role_count": count_contains(rows, "department_level", "\u4e2d\u592e"),
                "provincial_role_count": count_contains(rows, "department_level", "\u7701"),
                "city_role_count": count_contains(rows, "department_level", "\u5e02"),
                "county_or_below_role_count": count_contains(rows, "department_level", "\u53bf"),
                "need_test_role_count": sum(1 for row in rows if text(row.get("need_test")) == YES),
                "party_member_role_count": sum(1 for row in rows if PARTY in text(row.get("identity"))),
                "bachelor_only_role_count": count_contains(rows, "education_level", "\u4ec5\u9650\u672c\u79d1"),
                "bachelor_or_above_role_count": count_contains(rows, "education_level", "\u672c\u79d1\u53ca\u4ee5\u4e0a"),
                "master_or_above_role_count": count_contains(rows, "education_level", "\u7855\u58eb"),
                "province_count": len({text(row.get("province")) for row in rows if text(row.get("province"))}),
                "department_count": len({text(row.get("department_name")) for row in rows if text(row.get("department_name"))}),
                "sample_provinces": join_sample({row["province"] for row in rows}),
                "sample_departments": join_sample({row["department_name"] for row in rows}),
                "sample_job_names": join_sample({row["job_name"] for row in rows}),
                "sample_profession_texts": join_sample({row["profession_text"] for row in rows}, limit=5),
                **summarize_employment_refs(employment_refs),
                **summarize_policy_refs(policy_refs),
                **summarize_ai_refs(ai_refs, best_ai),
                "source_level": "C",
                "data_scope": "rysxai_civil_service_major_opportunity",
            }
        )
    add_major_ranks_and_levels(raw_rows)
    return raw_rows


def build_unmatched_rows(unmatched_counter: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for term, value in sorted(unmatched_counter.items(), key=lambda item: (-len(item[1]["role_ids"]), item[0])):
        rows.append(
            {
                "unmatched_term": term,
                "role_count": len(value["role_ids"]),
                "plan_num_sum": value["plan_num_sum"],
                "sample_role_ids": join_sample(value["role_ids"], limit=12),
                "sample_profession_texts": join_sample(value["profession_texts"], limit=5),
                "source_level": "C",
                "data_scope": "rysxai_civil_service_unmatched_profession_term",
            }
        )
    return rows


def add_major_ranks_and_levels(rows: list[dict[str, Any]]) -> None:
    by_role = sorted(rows, key=lambda row: (-int(row["role_match_count"]), row["major_code"], row["major_name"]))
    by_plan = sorted(rows, key=lambda row: (-int(row["plan_num_sum"]), row["major_code"], row["major_name"]))
    for rank, row in enumerate(by_role, start=1):
        row["rank_by_role_match_count"] = rank
    for rank, row in enumerate(by_plan, start=1):
        row["rank_by_plan_num_sum"] = rank
    matched_counts = sorted([int(row["role_match_count"]) for row in rows if int(row["role_match_count"])])
    p50 = percentile_nearest(matched_counts, 0.50)
    p75 = percentile_nearest(matched_counts, 0.75)
    p90 = percentile_nearest(matched_counts, 0.90)
    for row in rows:
        count = int(row["role_match_count"])
        if count == 0:
            level = "none"
        elif count >= p90:
            level = "very_high"
        elif count >= p75:
            level = "high"
        elif count >= p50:
            level = "medium"
        else:
            level = "limited"
        row["opportunity_level"] = level


def load_major_refs(path: Path) -> list[MajorRef]:
    refs: list[MajorRef] = []
    for row in read_csv_rows(path):
        major_code = text(row.get("major_code"))
        major_name = text(row.get("major_name"))
        level = text(row.get("level"))
        if not major_code or not major_name:
            continue
        refs.append(
            MajorRef(
                key=major_key(major_code, major_name, level),
                major_code=major_code,
                major_name=major_name,
                level=level,
                category=text(row.get("category")),
                subject=text(row.get("subject")),
            )
        )
    return refs


def load_employment_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        refs.append(
            {
                "id": text(row.get("record_id")),
                "major_name": major_name_from_warning(row),
                "year": text(row.get("report_year")),
                "risk_level": text(row.get("risk_level")),
            }
        )
    return refs


def load_policy_warning_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        refs.append(
            {
                "id": text(row.get("warning_id")),
                "major_name": major_name_from_warning(row),
                "year": text(row.get("policy_year")),
                "record_type": text(row.get("record_type")),
            }
        )
    return refs


def load_ai_replacement_refs(path: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for row in read_csv_rows(path):
        refs.append(
            {
                "major_name": text(row.get("major_name")),
                "rank": text(row.get("rank")),
                "score": text(row.get("ai_replacement_score")),
                "level": text(row.get("ai_replacement_level")),
                "confidence_score": text(row.get("confidence_score")),
                "candidate_count": text(row.get("candidate_count")),
            }
        )
    return refs


def build_warning_name_index(refs: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    by_name: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for ref in refs:
        if ref["major_name"]:
            by_name[ref["major_name"]][ref["id"]] = ref
    return {
        name: sorted(items.values(), key=lambda item: (item.get("year", ""), item.get("id", "")))
        for name, items in by_name.items()
    }


def build_ai_name_index(refs: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for ref in refs:
        if ref["major_name"]:
            by_name[ref["major_name"]].append(ref)
    return {name: sorted(items, key=ai_sort_key) for name, items in by_name.items()}


def summarize_employment_refs(refs: list[dict[str, str]]) -> dict[str, Any]:
    risk_levels = ordered_unique([ref["risk_level"] for ref in refs], order=["red", "yellow", "green"])
    has_red = "red" in risk_levels
    has_yellow = "yellow" in risk_levels
    has_green = "green" in risk_levels
    return {
        "employment_warning_count": len(refs),
        "employment_risk_levels": "|".join(risk_levels),
        "employment_warning_years": "|".join(ordered_unique([ref["year"] for ref in refs])),
        "employment_warning_record_ids": "|".join(ordered_unique([ref["id"] for ref in refs])),
        "has_employment_high_risk_warning": bool_text(has_red or has_yellow),
        "has_employment_red_warning": bool_text(has_red),
        "has_employment_yellow_warning": bool_text(has_yellow),
        "has_employment_green_signal": bool_text(has_green),
    }


def summarize_policy_refs(refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "official_policy_warning_count": len(refs),
        "official_policy_record_types": "|".join(ordered_unique([ref["record_type"] for ref in refs])),
        "official_policy_years": "|".join(ordered_unique([ref["year"] for ref in refs])),
        "official_policy_warning_ids": "|".join(ordered_unique([ref["id"] for ref in refs])),
        "has_official_policy_warning": bool_text(bool(refs)),
    }


def summarize_ai_refs(refs: list[dict[str, str]], best_ai: dict[str, str] | None) -> dict[str, Any]:
    return {
        "ai_replacement_match_count": len(refs),
        "ai_replacement_rank": text(best_ai.get("rank") if best_ai else ""),
        "ai_replacement_score": text(best_ai.get("score") if best_ai else ""),
        "ai_replacement_level": text(best_ai.get("level") if best_ai else ""),
        "ai_confidence_score": text(best_ai.get("confidence_score") if best_ai else ""),
        "ai_candidate_count": text(best_ai.get("candidate_count") if best_ai else ""),
    }


def write_report(path: Path, manifest: dict[str, Any], major_rows: list[dict[str, Any]]) -> None:
    top_rows = sorted(major_rows, key=lambda row: (-int(row["role_match_count"]), row["major_code"]))[:20]
    lines = [
        "# RYSXAI Civil-Service Major Opportunity Report",
        "",
        f"- Input role rows: {manifest['input_role_count']}",
        f"- Parsed roles with at least one major match: {manifest['matched_role_count']}",
        f"- Role-major match rows: {manifest['role_major_match_count']}",
        f"- Major opportunity rows: {manifest['major_opportunity_row_count']}",
        f"- Majors with at least one role match: {manifest['matched_major_count']}",
        f"- Employment-warning linked majors: {manifest['linked_employment_major_count']}",
        f"- Red/yellow linked majors: {manifest['linked_high_risk_major_count']}",
        f"- Official-policy linked majors: {manifest['linked_policy_major_count']}",
        f"- AI replacement-risk linked majors: {manifest['linked_ai_replacement_major_count']}",
        "",
        "## Top Majors By Matched Role Count",
        "",
        "| Major | Level | Roles | Plans | Weighted ratio | Match level |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in top_rows:
        lines.append(
            "| {major_name} | {major_level} | {role_match_count} | {plan_num_sum} | "
            "{weighted_competition_ratio} | {opportunity_level} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Major opportunities: `{manifest['output_major_csv']}`",
            f"- Role parse summary: `{manifest['output_role_summary_csv']}`",
            f"- Role-major matches: `{manifest['output_role_major_matches_csv']}`",
            f"- Unmatched terms: `{manifest['output_unmatched_terms_csv']}`",
            f"- Manifest: `{manifest['output_manifest_json']}`",
            "",
            "## Use Notes",
            "",
            "- Source level is `C`: this is a third-party API mirror of civil-service role data.",
            "- Exact matches come from six-digit major codes or exact major names.",
            "- Broad matches come from discipline/category codes, major-class terms, and documented aliases.",
            "- A matched role is evidence of a textual eligibility clue, not a final application eligibility judgment.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


CODE_RE = re.compile(r"(?<!\d)(\d{2,6}[A-Za-z]{0,2})(?!\d)")
PAREN_RE = re.compile(r"[\(\uff08][^\)\uff09]*[\)\uff09]")
SPLIT_RE = re.compile(r"[\s,;:/\uff0c\u3001\uff1b\uff1a]+")
LEADING_CODE_RE = re.compile(r"^\d{2,6}[A-Za-z]{0,2}")
HAN_RE = re.compile(r"[\u4e00-\u9fff]")


def extract_codes(value: str) -> list[str]:
    return ordered_unique([match.group(1).upper() for match in CODE_RE.finditer(value)])


def extract_terms(value: str) -> list[str]:
    terms: list[str] = []
    for raw_part in SPLIT_RE.split(value):
        term = normalize_term(raw_part)
        if term:
            terms.append(term)
    return ordered_unique(terms)


def normalize_term(value: str) -> str:
    term = text(value)
    if not term:
        return ""
    term = LEADING_CODE_RE.sub("", term).strip()
    for prefix in [
        "\u5927\u5b66\u672c\u79d1",
        "\u7814\u7a76\u751f",
        "\u672c\u79d1",
        "\u4e13\u79d1",
        "\u5927\u4e13",
    ]:
        if term.startswith(prefix):
            term = term[len(prefix) :].lstrip("\uff1a: ")
    for suffix in [
        "\u7b49\u4e13\u4e1a",
        "\u76f8\u5173\u4e13\u4e1a",
        "\u4e13\u4e1a",
    ]:
        if term.endswith(suffix) and term not in ALIAS_MAJOR_TERMS:
            term = term[: -len(suffix)]
    return term.strip("\uff08\uff09() ")


def strip_parenthetical_text(value: str) -> str:
    return PAREN_RE.sub("", value)


def looks_like_profession_term(term: str) -> bool:
    if len(term) < 2 or not HAN_RE.search(term):
        return False
    if term.startswith("\u4e0d\u542b"):
        return False
    if term in {
        "\u5927\u5b66\u672c\u79d1",
        "\u672c\u79d1",
        "\u7814\u7a76\u751f",
        "\u4e13\u79d1",
        "\u5927\u4e13",
    }:
        return False
    return True


def name_occurs_as_major(value: str, name: str) -> bool:
    start = 0
    while True:
        index = value.find(name, start)
        if index < 0:
            return False
        next_index = index + len(name)
        if next_index >= len(value) or value[next_index] != "\u7c7b":
            return True
        start = next_index


def add_match(matches: dict[str, MatchEvidence], major: MajorRef, method: str, term: str) -> None:
    evidence = matches.setdefault(major.key, MatchEvidence(major=major, methods=set(), terms=set()))
    evidence.methods.add(method)
    evidence.terms.add(term)


def dedupe_major_method(matches: list[tuple[MajorRef, str]]) -> list[tuple[MajorRef, str]]:
    seen: set[tuple[str, str]] = set()
    result: list[tuple[MajorRef, str]] = []
    for major, method in matches:
        key = (major.key, method)
        if key not in seen:
            seen.add(key)
            result.append((major, method))
    return result


def major_name_from_warning(row: dict[str, str]) -> str:
    return text(row.get("standard_major_name")) or text(row.get("reported_major_name"))


def major_key(code: str, name: str, level: str) -> str:
    return f"{code}|{name}|{level}"


def civil_service_major_id(key: str) -> str:
    return "civil_major:" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]


def role_major_match_id(role_id: str, key: str) -> str:
    return "civil_role_major:" + hashlib.sha256(f"{role_id}|{key}".encode("utf-8")).hexdigest()[:24]


def normalize_code(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z]", "", text(value)).upper()


def code_digits(value: str) -> str:
    return re.sub(r"\D", "", text(value))


def is_low_restriction_role(row: dict[str, str]) -> bool:
    return (
        text(row.get("identity")) == NO_LIMIT
        and text(row.get("work_year")) == UNLIMITED
        and text(row.get("work_experience")) == UNLIMITED
    )


def is_match_row_low_restriction(row: dict[str, Any]) -> bool:
    return row_bool(row.get("is_low_restriction_role"))


def count_contains(rows: list[dict[str, Any]], field: str, needle: str) -> int:
    return sum(1 for row in rows if needle in text(row.get(field)))


def ai_sort_key(ref: dict[str, str]) -> tuple[int, str]:
    return (to_int(ref.get("rank"), default=10**9), ref.get("major_name", ""))


def ordered_unique(values: list[str], *, order: list[str] | None = None) -> list[str]:
    seen = {value for value in values if value}
    if order:
        return [value for value in order if value in seen] + sorted(seen - set(order))
    return sorted(seen)


def percentile_nearest(values: list[int], percentile: float) -> int:
    if not values:
        return 0
    index = round((len(values) - 1) * percentile)
    return values[index]


def join_sample(values: Any, *, limit: int = 8) -> str:
    return "|".join(sorted(text(value) for value in values if text(value))[:limit])


def add_if(values: set[str], value: Any) -> None:
    value_text = text(value)
    if value_text:
        values.add(value_text)


def to_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def to_float(value: Any) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def number_text(value: float | None) -> str:
    if value is None:
        return ""
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def row_bool(value: Any) -> bool:
    return text(value).lower() == "true"


def lower_bool_text(value: Any) -> str:
    value_text = text(value)
    if not value_text:
        return ""
    if value_text.lower() in {"true", "1", "yes", "y"}:
        return "true"
    if value_text.lower() in {"false", "0", "no", "n"}:
        return "false"
    return value_text


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build major-level civil-service opportunity profiles from rysxai role data."
    )
    parser.add_argument(
        "--civil-service-csv",
        type=Path,
        default=Path("data/processed/rysxai_civil_service_2026.csv"),
    )
    parser.add_argument(
        "--major-seed-csv",
        type=Path,
        default=Path("data/seeds/rysxai_professions.full.csv"),
    )
    parser.add_argument(
        "--employment-warnings-csv",
        type=Path,
        default=Path("data/processed/major_risk_warnings/major_risk_warning_records.csv"),
    )
    parser.add_argument(
        "--official-policy-warnings-csv",
        type=Path,
        default=Path("data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv"),
    )
    parser.add_argument(
        "--ai-replacement-csv",
        type=Path,
        default=Path("data/processed/ai_replacement/major_ai_replacement_ranking.csv"),
    )
    parser.add_argument(
        "--output-major-csv",
        type=Path,
        default=Path("data/processed/rysxai_civil_service/civil_service_major_opportunities_2026.csv"),
    )
    parser.add_argument(
        "--output-role-summary-csv",
        type=Path,
        default=Path("data/processed/rysxai_civil_service/civil_service_role_match_summary_2026.csv"),
    )
    parser.add_argument(
        "--output-role-major-matches-csv",
        type=Path,
        default=Path("data/processed/rysxai_civil_service/civil_service_role_major_matches_2026.csv"),
    )
    parser.add_argument(
        "--output-unmatched-terms-csv",
        type=Path,
        default=Path("data/processed/rysxai_civil_service/civil_service_unmatched_profession_terms_2026.csv"),
    )
    parser.add_argument(
        "--output-manifest-json",
        type=Path,
        default=Path("data/processed/rysxai_civil_service/civil_service_major_opportunities_manifest_2026.json"),
    )
    parser.add_argument(
        "--output-report-md",
        type=Path,
        default=Path("reports/rysxai_civil_service/civil_service_major_opportunities_2026.md"),
    )
    args = parser.parse_args(argv)
    manifest = build_rysxai_civil_service_major_opportunities(
        civil_service_csv=args.civil_service_csv,
        major_seed_csv=args.major_seed_csv,
        employment_warnings_csv=args.employment_warnings_csv,
        official_policy_warnings_csv=args.official_policy_warnings_csv,
        ai_replacement_csv=args.ai_replacement_csv,
        output_major_csv=args.output_major_csv,
        output_role_summary_csv=args.output_role_summary_csv,
        output_role_major_matches_csv=args.output_role_major_matches_csv,
        output_unmatched_terms_csv=args.output_unmatched_terms_csv,
        output_manifest_json=args.output_manifest_json,
        output_report_md=args.output_report_md,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
