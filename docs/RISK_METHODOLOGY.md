# Risk Methodology

MPLADS Sentinel produces an explainable investigation-priority score. It does not
produce a fraud probability or a finding of fraud.

## Inputs

The scoring engine accepts six component scores, each normalized to `0-100`:

| Component  | Weight |
| ---------- | -----: |
| Financial  |     25 |
| Compliance |     20 |
| Anomaly    |     15 |
| Duplicate  |     20 |
| Spatial    |     10 |
| Context    |     10 |

Weights are stored in `config/risk_weights.json`. The engine in
`ml/scoring/risk_engine.py` contains no ML logic; anomaly and similarity models
must provide their normalized outputs separately.

## Missing components

A component with a missing value (`None`) is unavailable and contributes `0`.
Its weight is redistributed proportionally across the available components. For
example, if only compliance is available, compliance receives 100% effective
weight regardless of its configured weight. If every component is unavailable,
the score is `0` and the level is `LOW`.

## Calculation

For available components, the effective weight is:

`effective_weight = configured_weight / sum(available_weights) * 100`

The final score is:

`risk_score = sum(component_score * effective_weight / 100)`

The result is clamped to `0-100` and rounded to two decimal places. Component
contributions are returned for explanation and are zero for unavailable inputs.

## Risk levels

- `0-39`: `LOW`
- `40-69`: `MEDIUM`
- `70-100`: `HIGH`

Risk level boundaries are inclusive at 40 for `MEDIUM` and at 70 for `HIGH`.

## Interpretation

A high score means that the work has stronger combined indicators for
administrative verification relative to the configured components. It does not
establish a rule violation, anomaly, duplicate, or wrongdoing by itself. Reviewers
must inspect the underlying evidence and apply due process.
