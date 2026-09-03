"""Peer-based financial anomaly indicators for MPLADS works."""

from collections.abc import Iterable
from decimal import Decimal
from statistics import mean, median
from typing import TypedDict

from backend.schemas.work import Work


class FinancialAnomalyResult(TypedDict):
    """Explainable output from :func:`calculate_financial_anomaly`."""

    peer_median_cost: float | None
    peer_mean_cost: float | None
    cost_percentile: float | None
    cost_deviation: float | None
    risk_score: float
    evidence: list[str]


def _as_float(value: Decimal | None) -> float | None:
    return None if value is None else float(value)


def _percentile_rank(value: float, peer_costs: list[float]) -> float:
    """Return an empirical percentile with tied values sharing their rank."""

    less_count = sum(cost < value for cost in peer_costs)
    equal_count = sum(cost == value for cost in peer_costs)
    return (less_count + equal_count / 2) / len(peer_costs) * 100


def _robust_score(observed: float, peer_costs: list[float], peer_median: float) -> float:
    """Score only the upper-side deviation using median absolute deviation."""

    if observed <= peer_median:
        return 0.0

    deviations = [abs(cost - peer_median) for cost in peer_costs]
    mad = median(deviations)
    if mad == 0:
        return 100.0 if observed > peer_median else 0.0

    robust_z = (observed - peer_median) / (1.4826 * mad)
    return min(100.0, robust_z * 25.0)


def calculate_financial_anomaly(
    work: Work,
    peer_group: Iterable[Work],
) -> FinancialAnomalyResult:
    """Compare a work's sanctioned amount with its already-selected peer group.

    The caller is responsible for selecting peers using fields such as
    ``work_type``, location, and sanction year. The target work is excluded by
    ``work_id`` to avoid self-comparison. Missing monetary values are ignored.
    """

    observed = _as_float(work.sanctioned_amount)
    peer_costs = [
        cost
        for peer in peer_group
        if peer.work_id != work.work_id
        for cost in [_as_float(peer.sanctioned_amount)]
        if cost is not None
    ]
    if observed is None:
        return {
            "peer_median_cost": None,
            "peer_mean_cost": None,
            "cost_percentile": None,
            "cost_deviation": None,
            "risk_score": 0.0,
            "evidence": ["Financial anomaly check unavailable: sanctioned amount is missing."],
        }
    if not peer_costs:
        return {
            "peer_median_cost": None,
            "peer_mean_cost": None,
            "cost_percentile": None,
            "cost_deviation": None,
            "risk_score": 0.0,
            "evidence": ["Financial anomaly check unavailable: no peer costs are available."],
        }

    peer_median = median(peer_costs)
    peer_mean = mean(peer_costs)
    percentile = _percentile_rank(observed, peer_costs)
    deviation = 0.0 if peer_median == 0 else (observed - peer_median) / peer_median * 100
    percentile_risk = max(0.0, (percentile - 50.0) * 2.0)
    robust_risk = _robust_score(observed, peer_costs, peer_median)
    risk_score = round(min(100.0, max(0.0, (percentile_risk + robust_risk) / 2)), 2)

    if deviation > 0:
        evidence = [
            f"Observed sanctioned amount is {deviation:.1f}% above comparable-work median.",
            f"Comparable-work sanctioned amount percentile: {percentile:.1f}.",
        ]
    elif deviation < 0:
        evidence = [
            f"Observed sanctioned amount is {abs(deviation):.1f}% below comparable-work median.",
            f"Comparable-work sanctioned amount percentile: {percentile:.1f}.",
        ]
    else:
        evidence = [
            "Observed sanctioned amount matches the comparable-work median.",
            f"Comparable-work sanctioned amount percentile: {percentile:.1f}.",
        ]

    return {
        "peer_median_cost": round(peer_median, 2),
        "peer_mean_cost": round(peer_mean, 2),
        "cost_percentile": round(percentile, 2),
        "cost_deviation": round(deviation, 2),
        "risk_score": risk_score,
        "evidence": evidence,
    }
