"""Domain records for volunteer matching benchmarks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AdmissionHistory:
    year: int
    cutoff_rank: int
    cutoff_score: float | None = None
    plan_count: int | None = None
    source: str = "edu_school_admission_stats"


@dataclass(frozen=True)
class ApplicantContext:
    province: str
    subject_type: str
    year: int
    rank: int
    score: float | None = None
    preferred_majors: list[str] = field(default_factory=list)
    avoided_majors: list[str] = field(default_factory=list)
    preferred_cities: list[str] = field(default_factory=list)
    avoided_cities: list[str] = field(default_factory=list)
    accepts_adjustment: bool | None = None
    priority_strategy: str | None = None


@dataclass(frozen=True)
class Opportunity:
    school_id: str
    school_name: str
    major_code: str | None
    major_name: str | None
    province: str
    subject_type: str
    batch: str | None = None
    plan_count: int | None = None
    group_code: str | None = None
    group_name: str | None = None
    subject_requirement: str | None = None


@dataclass(frozen=True)
class RankPrediction:
    method: str
    predicted_rank: int
    predicted_score: float | None
    confidence: float
    evidence_years: list[int]
    warnings: list[str] = field(default_factory=list)
    planning_rank: int | None = None


@dataclass(frozen=True)
class RiskDecision:
    bucket: str
    rank_gap: int
    is_admissible_reference: bool
    confidence: float
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PredictionCase:
    opportunity_key: str
    target_year: int
    actual_rank: int
    actual_score: float | None
    history: list[AdmissionHistory]
    metadata: dict[str, Any] = field(default_factory=dict)


def history_from_dict(row: dict[str, Any]) -> AdmissionHistory:
    return AdmissionHistory(
        year=int(row["year"]),
        cutoff_rank=int(float(row["cutoff_rank"])),
        cutoff_score=_optional_float(row.get("cutoff_score")),
        plan_count=_optional_int(row.get("plan_count")),
        source=str(row.get("source") or "edu_school_admission_stats"),
    )


def case_from_dict(row: dict[str, Any]) -> PredictionCase:
    return PredictionCase(
        opportunity_key=str(row["opportunity_key"]),
        target_year=int(row["target_year"]),
        actual_rank=int(float(row["actual_rank"])),
        actual_score=_optional_float(row.get("actual_score")),
        history=[history_from_dict(item) for item in row.get("history", [])],
        metadata=dict(row.get("metadata") or {}),
    )


def case_to_dict(case: PredictionCase) -> dict[str, Any]:
    return {
        "opportunity_key": case.opportunity_key,
        "target_year": case.target_year,
        "actual_rank": case.actual_rank,
        "actual_score": case.actual_score,
        "history": [
            {
                "year": item.year,
                "cutoff_rank": item.cutoff_rank,
                "cutoff_score": item.cutoff_score,
                "plan_count": item.plan_count,
                "source": item.source,
            }
            for item in case.history
        ],
        "metadata": case.metadata,
    }


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(float(value))
