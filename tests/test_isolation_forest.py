import pandas as pd

from ml.anomaly.isolation_forest import run_isolation_forest


def synthetic_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "work_id": ["w-1", "w-2", "w-3", "w-4", "w-5"],
            "sanctioned_amount": [100_000, 105_000, 98_000, 110_000, 5_000_000],
            "expenditure": [80_000, 85_000, 75_000, 90_000, 4_500_000],
            "utilisation_ratio": [0.8, 0.81, 0.76, 0.82, 0.9],
        }
    )


def test_returns_raw_and_normalized_scores_with_context() -> None:
    result = run_isolation_forest(synthetic_dataset(), n_estimators=50)

    assert "raw_isolation_score" in result
    assert "anomaly_score" in result
    assert "anomaly_context" in result
    assert result["anomaly_score"].between(0, 100).all()
    assert result.loc[result["work_id"] == "w-5", "anomaly_score"].iloc[0] > 50
    assert result.attrs["anomaly_features"] == [
        "sanctioned_amount",
        "expenditure",
        "utilisation_ratio",
    ]
    assert any("sanctioned_amount" in context for context in result["anomaly_context"])


def test_preserves_original_columns_and_handles_missing_values() -> None:
    dataset = synthetic_dataset()
    dataset.loc[1, "expenditure"] = None

    result = run_isolation_forest(dataset, n_estimators=25)

    assert list(result["work_id"]) == list(dataset["work_id"])
    assert result.loc[1, "expenditure"] != result.loc[1, "expenditure"]
    assert result["anomaly_score"].notna().all()


def test_same_input_and_random_state_are_deterministic() -> None:
    dataset = synthetic_dataset()

    first = run_isolation_forest(dataset, n_estimators=50)
    second = run_isolation_forest(dataset, n_estimators=50)

    pd.testing.assert_series_equal(
        first["raw_isolation_score"], second["raw_isolation_score"], check_names=False
    )
    pd.testing.assert_series_equal(
        first["anomaly_score"], second["anomaly_score"], check_names=False
    )


def test_all_missing_candidate_features_return_zero_scores() -> None:
    dataset = pd.DataFrame({"work_id": ["w-1", "w-2"], "sanctioned_amount": [None, None]})

    result = run_isolation_forest(dataset)

    assert result["raw_isolation_score"].tolist() == [0.0, 0.0]
    assert result["anomaly_score"].tolist() == [0.0, 0.0]
    assert result.attrs["anomaly_features"] == []


def test_no_candidate_columns_return_zero_scores() -> None:
    result = run_isolation_forest(pd.DataFrame({"work_id": ["w-1", "w-2"]}))

    assert result["anomaly_score"].tolist() == [0.0, 0.0]
    assert all("No usable numeric features" in context for context in result["anomaly_context"])
