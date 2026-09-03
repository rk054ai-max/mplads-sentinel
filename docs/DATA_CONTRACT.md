# Data Contract

The canonical normalized work record is the boundary between ingestion, analysis,
and the API. Implementations may add fields, but must not silently change the
meaning or type of these fields.

## Required fields

- `work_id`: stable string identifier within the source system.
- `title`: normalized work description.
- `state`, `district`, `constituency`: administrative location labels.
- `latitude`, `longitude`: optional decimal coordinates in WGS84.
- `sanctioned_amount`, `released_amount`, `spent_amount`: non-negative numeric
  values in INR.
- `sanction_date`, `completion_date`: optional ISO 8601 dates.
- `status`: normalized lifecycle status.
- `source`, `source_record_id`: provenance identifiers.
- `ingested_at`: ISO 8601 timestamp in UTC.
- `schema_version`: contract version string.

## Rules

- Preserve the raw source under `data/raw/`; normalized outputs belong under
  `data/processed/`.
- Missing values remain explicit nulls and are not converted to zero.
- Store rule, model, and feature versions alongside derived results.
- Monetary values are INR unless a future contract explicitly states otherwise.
- Mock records must be clearly identified and must not be presented as official data.

## Canonical Work object

The canonical Pydantic model is `backend.schemas.work.Work`. It uses `work_id` as
the only required field. All other fields are nullable because source MPLADS
records may omit location, financial, lifecycle, or agency information.

| Field                 | Type                  | Meaning                                                                                                        |
| --------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------- |
| `work_id`             | string                | Stable identifier for the work. Required.                                                                      |
| `description`         | nullable string       | Description of the proposed or executed work.                                                                  |
| `state`               | nullable string       | Indian state containing the work.                                                                              |
| `district`            | nullable string       | District containing the work.                                                                                  |
| `constituency`        | nullable string       | Parliamentary constituency associated with the work.                                                           |
| `latitude`            | nullable float        | WGS84 latitude in decimal degrees, from -90 to 90.                                                             |
| `longitude`           | nullable float        | WGS84 longitude in decimal degrees, from -180 to 180.                                                          |
| `work_type`           | nullable string       | Normalized category or type of work.                                                                           |
| `recommended_amount`  | nullable Decimal      | Amount recommended for the work, in INR.                                                                       |
| `sanctioned_amount`   | nullable Decimal      | Amount sanctioned for the work, in INR.                                                                        |
| `expenditure`         | nullable Decimal      | Expenditure recorded for the work, in INR.                                                                     |
| `recommendation_date` | nullable date         | Date on which the work was recommended.                                                                        |
| `sanction_date`       | nullable date         | Date on which the work was sanctioned.                                                                         |
| `start_date`          | nullable date         | Date on which work execution started.                                                                          |
| `completion_date`     | nullable date         | Date on which work execution was completed.                                                                    |
| `status`              | nullable `WorkStatus` | Normalized lifecycle status: proposed, recommended, sanctioned, in_progress, completed, delayed, or cancelled. |
| `implementing_agency` | nullable string       | Agency responsible for implementing the work.                                                                  |

Amounts are non-negative and represented as `Decimal` values to avoid losing
monetary precision. Dates use ISO 8601 `YYYY-MM-DD` values. Unknown or missing
values remain null; they are not converted to zero or inferred.

## Collection and validation models

- `WorkList` contains `items: list[Work]` and a non-negative `total`.
- `ValidationError` contains a field `location`, human-readable `message`,
  stable `error_type`, and an optional safe-to-return `input` value.
- `ValidationErrorResponse` contains a list of `ValidationError` objects for API
  responses.

## Mock data

`data/mock/sample_work.json` contains three clearly synthetic records: a normal
completed work, a delayed work without a completion date, and an in-progress
candidate with an unusually high expenditure relative to its sanctioned amount.
