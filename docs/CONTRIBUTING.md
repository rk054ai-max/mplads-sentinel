# Contributing

MPLADS Sentinel is developed as a coordinated three-person MVP for SIH26102. The
main branch must remain runnable throughout development.

## Working agreement

1. Inspect the repository and relevant contracts before making changes.
2. Pull the latest `main` before creating a feature branch.
3. Use one feature per branch and keep commits small and focused.
4. Keep changes typed, testable, documented, and easy to review.
5. Every feature must include a test or a reproducible example.
6. Open a pull request before merging where possible. Do not force push to `main`.
7. Never commit secrets, credentials, raw personal data, or generated artifacts.
8. Keep model decisions reproducible through versioned configuration and inputs.
9. Do not change a shared contract or another developer's owned module without
   explicit coordination recorded in the pull request or issue.

## Branches and ownership

- `main`: integrated, demonstrable, and runnable code only.
- `feature/member-a-*`: data ingestion, normalization, compliance and timeline
  rules, financial benchmarking, Isolation Forest, and related tests.
- `feature/member-b-*`: NLP similarity, duplicate detection, geospatial analysis,
  external spatial data, and related tests.
- `feature/member-c-*`: frontend, FastAPI integration, dashboard, investigation
  page, and optional LLM summaries.

Each developer may update shared contracts only after notifying the other owners.
The owner of the affected module reviews changes to that module.

## Integration checklist

- Confirm the change matches `docs/DATA_CONTRACT.md` and `docs/API_CONTRACT.md`.
- Run the focused tests, then the full `pytest` suite.
- Verify external APIs remain optional and cached fallbacks still work.
- Verify outputs describe risk or anomaly indicators and never claim fraud.
- Update documentation and configuration when behavior or assumptions change.
