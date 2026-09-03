from datetime import date, timedelta
from decimal import Decimal

from backend.core.compliance import run_compliance_checks
from backend.schemas.work import Work, WorkStatus


def make_work(**updates: object) -> Work:
    values: dict[str, object] = {
        "work_id": "TEST-001",
        "recommendation_date": date(2024, 1, 1),
        "sanction_date": date(2024, 1, 15),
        "start_date": date(2024, 2, 1),
        "completion_date": date(2024, 8, 1),
        "status": WorkStatus.COMPLETED,
        "expenditure": Decimal("1000"),
    }
    values.update(updates)
    return Work(**values)


def test_normal_work_has_no_compliance_flags() -> None:
    result = run_compliance_checks(make_work())

    assert result["score"] == 0
    assert result["flags"] == []
    assert result["evidence"]


def test_late_sanction_generates_flag() -> None:
    result = run_compliance_checks(
        make_work(sanction_date=date(2024, 3, 1), start_date=date(2024, 3, 10))
    )

    assert any(flag["type"] == "recommendation_to_sanction_delay" for flag in result["flags"])
    assert result["score"] == 25


def test_no_payment_after_sanction_generates_flag() -> None:
    result = run_compliance_checks(
        make_work(
            sanction_date=date.today() - timedelta(days=91),
            start_date=None,
            completion_date=None,
            status=WorkStatus.IN_PROGRESS,
            expenditure=Decimal("0"),
        )
    )

    assert any(flag["type"] == "sanction_to_payment_inactivity" for flag in result["flags"])


def test_late_completion_generates_flag() -> None:
    result = run_compliance_checks(
        make_work(
            sanction_date=date(2023, 1, 1),
            start_date=date(2023, 2, 1),
            completion_date=date(2024, 1, 2),
        )
    )

    assert any(flag["type"] == "sanction_to_completion_duration" for flag in result["flags"])


def test_missing_completion_date_for_recent_ongoing_work_is_evidence_only() -> None:
    result = run_compliance_checks(
        make_work(
            sanction_date=date.today() - timedelta(days=10),
            start_date=date.today() - timedelta(days=5),
            completion_date=None,
            status=WorkStatus.IN_PROGRESS,
        )
    )

    assert not any(flag["type"] == "sanction_to_completion_duration" for flag in result["flags"])
    assert any("Ongoing sanction-to-completion" in evidence for evidence in result["evidence"])


def test_impossible_date_sequence_is_flagged() -> None:
    result = run_compliance_checks(
        make_work(start_date=date(2024, 1, 10), completion_date=date(2024, 1, 5))
    )

    assert result["flags"][0]["type"] == "impossible_date_sequence"
    assert result["flags"][0]["severity"] == "high"
    assert result["score"] == 100
