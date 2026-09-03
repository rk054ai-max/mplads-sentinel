from decimal import Decimal

from backend.schemas.work import Work
from ml.anomaly.financial import calculate_financial_anomaly


def work(work_id: str, amount: str | None) -> Work:
    return Work(
        work_id=work_id,
        work_type="Road",
        state="Karnataka",
        district="Mysuru",
        sanctioned_amount=None if amount is None else Decimal(amount),
    )


def test_calculates_peer_statistics_and_explainable_evidence() -> None:
    target = work("target", "146.2")
    peers = [work("peer-1", "80"), work("peer-2", "100"), work("peer-3", "100"), work("peer-4", "120")]

    result = calculate_financial_anomaly(target, peers)

    assert result["peer_median_cost"] == 100.0
    assert result["peer_mean_cost"] == 100.0
    assert result["cost_percentile"] == 100.0
    assert result["cost_deviation"] == 46.2
    assert 0 <= result["risk_score"] <= 100
    assert "46.2% above comparable-work median" in result["evidence"][0]


def test_robust_benchmark_is_not_driven_by_extreme_peer() -> None:
    target = work("target", "150")
    peers = [work("peer-1", "80"), work("peer-2", "100"), work("peer-3", "100"), work("peer-4", "120"), work("peer-5", "10000")]

    result = calculate_financial_anomaly(target, peers)

    assert result["peer_median_cost"] == 100.0
    assert result["peer_mean_cost"] == 2080.0
    assert result["cost_deviation"] == 50.0
    assert result["risk_score"] < 100


def test_target_is_excluded_from_peer_group() -> None:
    target = work("target", "1000")
    peers = [target, work("peer-1", "100"), work("peer-2", "200")]

    result = calculate_financial_anomaly(target, peers)

    assert result["peer_median_cost"] == 150.0


def test_missing_target_amount_is_handled_without_crashing() -> None:
    result = calculate_financial_anomaly(work("target", None), [work("peer-1", "100")])

    assert result["risk_score"] == 0.0
    assert result["peer_median_cost"] is None
    assert "unavailable" in result["evidence"][0]


def test_missing_peer_amount_is_ignored() -> None:
    result = calculate_financial_anomaly(
        work("target", "100"), [work("peer-1", None), work("peer-2", "80"), work("peer-3", "120")]
    )

    assert result["peer_median_cost"] == 100.0
    assert result["risk_score"] == 0.0
