"""Deterministic, explainable fusion of normalized MPLADS risk components."""

import json
import math
from pathlib import Path
from typing import TypedDict


_COMPONENT_NAMES = (
    "financial",
    "compliance",
    "anomaly",
    "duplicate",
    "spatial",
    "context",
)
_WEIGHTS_PATH = Path(__file__).resolve().parents[2] / "config" / "risk_weights.json"


class RiskScoreResult(TypedDict):
    """Result returned by :func:`calculate_risk_score`."""

    risk_score: float
    risk_level: str
    component_contributions: dict[str, float]


def _load_weights() -> dict[str, float]:
    """Load and validate the configured component weights."""

    with _WEIGHTS_PATH.open(encoding="utf-8") as weights_file:
        raw_weights = json.load(weights_file)

    if set(raw_weights) != set(_COMPONENT_NAMES):
        raise ValueError("risk_weights.json must contain exactly the six risk components")

    weights = {name: float(raw_weights[name]) for name in _COMPONENT_NAMES}
    if any(weight < 0 or not math.isfinite(weight) for weight in weights.values()):
        raise ValueError("Risk weights must be finite and non-negative")
    if not math.isclose(sum(weights.values()), 100.0):
        raise ValueError("Risk weights must total 100")
    return weights


def _normalize_score(component: str, score: float | None) -> float | None:
    """Validate one normalized score while preserving missing values."""

    if score is None:
        return None
    try:
        normalized_score = float(score)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{component}_score must be a number between 0 and 100") from error
    if not math.isfinite(normalized_score) or not 0 <= normalized_score <= 100:
        raise ValueError(f"{component}_score must be between 0 and 100")
    return normalized_score


def _risk_level(score: float) -> str:
    """Map a final score to the public risk band."""

    if score < 40:
        return "LOW"
    if score < 70:
        return "MEDIUM"
    return "HIGH"


def calculate_risk_score(
    financial_score: float | None,
    compliance_score: float | None,
    anomaly_score: float | None,
    duplicate_score: float | None,
    spatial_score: float | None,
    context_score: float | None,
) -> RiskScoreResult:
    """Calculate a weighted risk score from normalized component scores.

    Missing components have their configured weight redistributed proportionally
    across the available components. The function performs no ML or external I/O
    beyond loading the versioned local weight configuration.
    """

    raw_scores = dict(
        zip(
            _COMPONENT_NAMES,
            (
                financial_score,
                compliance_score,
                anomaly_score,
                duplicate_score,
                spatial_score,
                context_score,
            ),
            strict=True,
        )
    )
    scores = {
        component: _normalize_score(component, score)
        for component, score in raw_scores.items()
    }
    weights = _load_weights()
    available = [component for component, score in scores.items() if score is not None]
    contributions = {component: 0.0 for component in _COMPONENT_NAMES}

    if not available:
        return {
            "risk_score": 0.0,
            "risk_level": "LOW",
            "component_contributions": contributions,
        }

    available_weight = sum(weights[component] for component in available)
    for component in available:
        effective_weight = weights[component] / available_weight * 100
        contributions[component] = scores[component] * effective_weight / 100

    risk_score = max(0.0, min(100.0, sum(contributions.values())))
    return {
        "risk_score": round(risk_score, 2),
        "risk_level": _risk_level(risk_score),
        "component_contributions": {
            component: round(contribution, 2)
            for component, contribution in contributions.items()
        },
    }
