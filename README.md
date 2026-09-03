# MPLADS Sentinel

MPLADS Sentinel is a monitoring and risk-analysis platform for detecting anomalies, identifying similar projects, and prioritizing scrutiny of MPLADS expenditure and development records.

## Repository layout

- `backend/` API, domain logic, services, and schemas
- `ml/` anomaly detection, similarity, and scoring models
- `frontend/` user interface
- `data/` raw, processed, external, and mock data
- `config/` rules and runtime configuration
- `scripts/` data and maintenance utilities
- `tests/` automated tests
- `docs/` project and data contracts

## Governance

Read [PROJECT_CONSTITUTION.md](docs/PROJECT_CONSTITUTION.md),
[DATA_CONTRACT.md](docs/DATA_CONTRACT.md), [API_CONTRACT.md](docs/API_CONTRACT.md),
and [CONTRIBUTING.md](docs/CONTRIBUTING.md) before implementing features.

Development is divided across `feature/member-a-*`, `feature/member-b-*`, and
`feature/member-c-*`. Ownership and coordination rules are documented in
`CONTRIBUTING.md`; changes to shared contracts require explicit coordination.

## Quick start

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and adjust local settings.
4. Run tests with `pytest`.

The application components will be added incrementally under `backend/`, `ml/`, and `frontend/`.

## Development environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```text
pip install -r requirements.txt
```

Run the API:

```text
uvicorn backend.main:app --reload
```
