"""Unsupervised Isolation Forest anomaly detection for MPLADS works."""

from collections.abc import Sequence

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


CANDIDATE_FEATURES: tuple[str, ...] = (
    "sanctioned_amount",
    "expenditure",
    "utilisation_ratio",
    "recommendation_to_sanction_days",
    "sanction_to_completion_days",
    "cost_deviation",
    "payment_delay",
)
_MONETARY_FEATURES = {"sanctioned_amount", "expenditure"}
_CONTEXT_THRESHOLD = 1.5


def _signed_log(values: np.ndarray) -> np.ndarray:
    """Reduce monetary skew while retaining the sign of any invalid negatives."""

    return np.sign(values) * np.log1p(np.abs(values))


def _empty_result(dataset: pd.DataFrame, features: Sequence[str]) -> pd.DataFrame:
    """Return a stable result when no model can be fitted."""

    result = dataset.copy()
    result["raw_isolation_score"] = 0.0
    result["anomaly_score"] = 0.0
    context = "No usable numeric features were available for anomaly detection."
    result["anomaly_context"] = [context] * len(result)
    result.attrs["anomaly_features"] = list(features)
    return result


def _normalized_anomaly_scores(raw_scores: np.ndarray) -> np.ndarray:
    """Convert lower-is-more-anomalous Isolation Forest scores to 0-100 ranks."""

    if len(raw_scores) <= 1 or np.ptp(raw_scores) == 0:
        return np.zeros(len(raw_scores), dtype=float)
    order = np.argsort(raw_scores, kind="mergesort")
    ranks = np.empty(len(raw_scores), dtype=float)
    ranks[order] = np.arange(len(raw_scores), dtype=float)
    return (1.0 - ranks / (len(raw_scores) - 1)) * 100.0


def _contexts(
    transformed: np.ndarray,
    feature_names: Sequence[str],
    available_mask: pd.DataFrame,
) -> list[str]:
    """Describe available features with notable standardized deviations."""

    contexts: list[str] = []
    for row_index in range(len(transformed)):
        deviations = np.abs(transformed[row_index])
        candidates = [
            (feature_names[column_index], deviations[column_index])
            for column_index in range(len(feature_names))
            if available_mask.iloc[row_index, column_index]
            and deviations[column_index] >= _CONTEXT_THRESHOLD
        ]
        candidates.sort(key=lambda item: (-item[1], item[0]))
        if candidates:
            feature_text = ", ".join(
                f"{name} (standardized deviation {deviation:.2f})"
                for name, deviation in candidates
            )
            contexts.append(f"Available features contributing context: {feature_text}.")
        else:
            contexts.append(
                "No individual available feature exceeded the context threshold; "
                "the score reflects multivariate isolation."
            )
    return contexts


def run_isolation_forest(
    dataset: pd.DataFrame,
    *,
    random_state: int = 42,
    n_estimators: int = 200,
) -> pd.DataFrame:
    """Add explainable Isolation Forest anomaly outputs to a dataset.

    Only numeric columns from :data:`CANDIDATE_FEATURES` that are present and
    contain at least one usable value are used. Missing values are median-imputed
    using this unlabeled input dataset only; no labels, future outcomes, or
    external data are used. The returned copy preserves all original columns.

    Added columns are ``raw_isolation_score`` (the model decision function,
    where lower values are more isolated), ``anomaly_score`` (rank-normalized
    to 0-100, where higher values are more anomalous), and ``anomaly_context``.
    The used feature names are also available at ``result.attrs`` under
    ``anomaly_features``.
    """

    if not isinstance(dataset, pd.DataFrame):
        raise TypeError("dataset must be a pandas DataFrame")
    if random_state is None:
        raise ValueError("random_state must be deterministic and cannot be None")
    if n_estimators < 1:
        raise ValueError("n_estimators must be at least 1")

    result = dataset.copy()
    feature_names = [
        feature
        for feature in CANDIDATE_FEATURES
        if feature in dataset.columns
        and pd.to_numeric(dataset[feature], errors="coerce").notna().any()
    ]
    if dataset.empty or not feature_names:
        return _empty_result(result, feature_names)

    numeric_features = pd.DataFrame(
        {
            feature: pd.to_numeric(dataset[feature], errors="coerce")
            for feature in feature_names
        },
        index=dataset.index,
    )
    available_mask = numeric_features.notna()
    imputed = SimpleImputer(strategy="median").fit_transform(numeric_features)
    transformed = imputed.copy()
    monetary_indexes = [
        index for index, feature in enumerate(feature_names) if feature in _MONETARY_FEATURES
    ]
    if monetary_indexes:
        transformed[:, monetary_indexes] = _signed_log(transformed[:, monetary_indexes])
    transformed = StandardScaler().fit_transform(transformed)

    model = IsolationForest(n_estimators=n_estimators, random_state=random_state)
    raw_scores = model.fit(transformed).decision_function(transformed)
    anomaly_scores = _normalized_anomaly_scores(raw_scores)

    result["raw_isolation_score"] = raw_scores
    result["anomaly_score"] = np.round(np.clip(anomaly_scores, 0, 100), 2)
    result["anomaly_context"] = _contexts(transformed, feature_names, available_mask)
    result.attrs["anomaly_features"] = feature_names
    return result
