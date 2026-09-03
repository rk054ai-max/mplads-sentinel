# Development Workflow

## First checkout

```text
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
pytest
```

The frontend will receive its own package setup when implementation begins. Do
not make external services a prerequisite for the first demo; use mock or cached
inputs from `data/mock/` and `data/external/`.

## Feature workflow

1. Start from an up-to-date `main`.
2. Create a branch matching the owned area: `feature/member-a-*`,
   `feature/member-b-*`, or `feature/member-c-*`.
3. Inspect and preserve the data and API contracts.
4. Implement the smallest testable slice with typed interfaces.
5. Run focused tests and then `pytest`.
6. Open a pull request describing contract changes, fallback behavior, and
   verification steps.
7. Merge only when `main` remains runnable.

## Coordination points

Coordinate before changing shared schemas, API response shapes, scoring semantics,
configuration keys, or repository-wide dependencies. Record the decision in the
pull request and update the relevant contract document in the same change.
