"""Explainable MPLADS compliance and timeline monitoring checks."""

import json
from datetime import date
from pathlib import Path
from typing import TypedDict

from backend.schemas.work import Work, WorkStatus


_RULES_PATH = Path(__file__).resolve().parents[2] / "config" / "rules.json"
_DATE_FIELDS = ("recommendation_date", "sanction_date", "start_date", "completion_date")


class ComplianceFlag(TypedDict):
    """A triggered monitoring rule."""

    type: str
    severity: str
    message: str
    source: str


class ComplianceResult(TypedDict):
    """Result returned by :func:`run_compliance_checks`."""

    score: int
    flags: list[ComplianceFlag]
    evidence: list[str]


def _load_rules() -> dict[str, dict[str, int | str]]:
    """Load configured compliance benchmarks from the repository."""

    with _RULES_PATH.open(encoding="utf-8") as rules_file:
        configuration = json.load(rules_file)
    compliance_rules = configuration.get("compliance")
    if not isinstance(compliance_rules, dict):
        raise ValueError("config/rules.json must define a compliance object")
    return compliance_rules


def _flag(rule_type: str, rule: dict[str, int | str], message: str) -> ComplianceFlag:
    """Build the stable public shape for a triggered rule."""

    return {
        "type": rule_type,
        "severity": str(rule["severity"]),
        "message": message,
        "source": "MPLADS guideline/official rule",
    }


def _days_between(start: date, end: date) -> int:
    return (end - start).days


def _date_sequence_flags(work: Work, rules: dict[str, dict[str, int | str]]) -> list[ComplianceFlag]:
    """Detect dates that occur before their lifecycle predecessor."""

    available_dates = [(field, getattr(work, field)) for field in _DATE_FIELDS]
    previous_field: str | None = None
    previous_date: date | None = None
    flags: list[ComplianceFlag] = []
    rule = rules["impossible_date_sequence"]
    for field, current_date in available_dates:
        if current_date is None:
            continue
        if previous_date is not None and current_date < previous_date:
            flags.append(
                _flag(
                    "impossible_date_sequence",
                    rule,
                    f"{field} precedes {previous_field}; verify the recorded dates.",
                )
            )
        previous_field = field
        previous_date = current_date
    return flags


def run_compliance_checks(work: Work) -> ComplianceResult:
    """Run configured timeline checks and return explainable monitoring signals."""

    rules = _load_rules()
    flags = _date_sequence_flags(work, rules)
    evidence: list[str] = []

    if work.recommendation_date is None or work.sanction_date is None:
        evidence.append("Recommendation-to-sanction check unavailable: a date is missing.")
    else:
        recommendation_days = _days_between(work.recommendation_date, work.sanction_date)
        rule = rules["recommendation_to_sanction"]
        if recommendation_days > int(rule["threshold_days"]):
            flags.append(
                _flag(
                    "recommendation_to_sanction_delay",
                    rule,
                    f"Sanction followed recommendation by {recommendation_days} days, exceeding the {rule['threshold_days']}-day benchmark.",
                )
            )
        evidence.append(f"Recommendation-to-sanction interval: {recommendation_days} days.")

    if work.sanction_date is None:
        evidence.append("Sanction-to-payment check unavailable: sanction date is missing.")
    elif work.expenditure is None:
        evidence.append("Sanction-to-payment check unavailable: expenditure is missing.")
    elif work.expenditure > 0:
        evidence.append("Payment evidence present: recorded expenditure is greater than zero.")
    else:
        payment_days = _days_between(work.sanction_date, date.today())
        rule = rules["sanction_to_payment"]
        if payment_days > int(rule["threshold_days"]):
            flags.append(
                _flag(
                    "sanction_to_payment_inactivity",
                    rule,
                    f"No recorded expenditure {payment_days} days after sanction, exceeding the {rule['threshold_days']}-day benchmark.",
                )
            )
        evidence.append(f"Sanction-to-payment interval without recorded expenditure: {payment_days} days.")

    completion_date = work.completion_date
    if work.sanction_date is None:
        evidence.append("Sanction-to-completion check unavailable: sanction date is missing.")
    elif completion_date is not None:
        completion_days = _days_between(work.sanction_date, completion_date)
        rule = rules["sanction_to_completion"]
        if completion_days > int(rule["threshold_days"]):
            flags.append(
                _flag(
                    "sanction_to_completion_duration",
                    rule,
                    f"Completion followed sanction by {completion_days} days, exceeding the {rule['threshold_days']}-day benchmark.",
                )
            )
        evidence.append(f"Sanction-to-completion interval: {completion_days} days.")
    elif work.status in {WorkStatus.COMPLETED, WorkStatus.CANCELLED}:
        evidence.append("Sanction-to-completion check unavailable: completion date is missing.")
    else:
        elapsed_days = _days_between(work.sanction_date, date.today())
        rule = rules["sanction_to_completion"]
        if elapsed_days > int(rule["threshold_days"]):
            flags.append(
                _flag(
                    "sanction_to_completion_duration",
                    rule,
                    f"Work remains incomplete {elapsed_days} days after sanction, exceeding the {rule['threshold_days']}-day benchmark.",
                )
            )
        evidence.append(f"Ongoing sanction-to-completion interval: {elapsed_days} days.")

    rule_for_flag = {
        "recommendation_to_sanction_delay": "recommendation_to_sanction",
        "sanction_to_payment_inactivity": "sanction_to_payment",
        "sanction_to_completion_duration": "sanction_to_completion",
        "impossible_date_sequence": "impossible_date_sequence",
    }
    score = min(
        100,
        sum(int(rules[rule_for_flag[flag["type"]]]["score"]) for flag in flags),
    )
    return {"score": score, "flags": flags, "evidence": evidence}