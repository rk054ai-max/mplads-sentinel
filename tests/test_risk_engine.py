import pytest

from ml.scoring.risk_engine import calculate_risk_score


@pytest.mark.parametrize(
    ("score", "level"),
    [(0, "LOW"), (39.99, "LOW"), (40, "MEDIUM"), (69.99, "MEDIUM"), (70, "HIGH"), (100, "HIGH")],
)
def test_risk_levels(score: float, level: str) -> None:
    result = calculate_risk_score(score, None, None, None, None, None)

    assert result["risk_score"] == score
    assert result["risk_level"] == level


def test_full_score_uses_configured_weights() -> None:
    result = calculate_risk_score(100, 50, 0, 75, 20, 80)

    assert result["risk_score"] == 60
    assert result["risk_level"] == "MEDIUM"
    assert result["component_contributions"] == {
        "financial": 25.0,
        "compliance": 10.0,
        "anomaly": 0.0,
        "duplicate": 15.0,
        "spatial": 2.0,
        "context": 8.0,
    }


def test_missing_component_weight_is_redistributed() -> None:
    result = calculate_risk_score(None, 100, None, None, None, None)

    assert result["risk_score"] == 100
    assert result["component_contributions"]["compliance"] == 100.0
    assert result["component_contributions"]["financial"] == 0.0


def test_all_missing_components_return_low_zero_result() -> None:
    result = calculate_risk_score(None, None, None, None, None, None)

    assert result == {
        "risk_score": 0.0,
        "risk_level": "LOW",
        "component_contributions": {
            "financial": 0.0,
            "compliance": 0.0,
            "anomaly": 0.0,
            "duplicate": 0.0,
            "spatial": 0.0,
            "context": 0.0,
        },
    }


@pytest.mark.parametrize("invalid_score", [-0.01, 100.01, float("nan"), float("inf")])
def test_scores_must_be_normalized(invalid_score: float) -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        calculate_risk_score(invalid_score, None, None, None, None, None)


def test_calculation_is_deterministic() -> None:
    inputs = (65, 20, 80, None, 35, 50)

    assert calculate_risk_score(*inputs) == calculate_risk_score(*inputs)
