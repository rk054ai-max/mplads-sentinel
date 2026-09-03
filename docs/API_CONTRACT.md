# API Contract

The public API is versioned under `/api/v1`. The frontend depends on these
resource shapes, not on backend or ML implementation details.

## MVP resources

- `GET /api/v1/health`: service availability and contract version.
- `GET /api/v1/works`: paginated work summaries with filters and risk ordering.
- `GET /api/v1/works/{work_id}`: work detail, indicators, evidence, and provenance.
- `GET /api/v1/works/{work_id}/similar`: ranked similar or potentially duplicate works.
- `GET /api/v1/summary`: aggregate counts for dashboard cards and charts.

## Response rules

- Stable JSON schema objects with explicit nullable fields.
- Pagination metadata includes `items`, `page`, `page_size`, and `total`.
- Errors use `{ "detail": { "code": "...", "message": "..." } }`.
- Risk responses include `risk_score`, `risk_band`, and an ordered list of
  `indicators`; each indicator has a source, reason, and supporting values.
- `risk_score` prioritizes verification only. It is never labeled as a fraud
  probability or final finding.
- Optional external and LLM fields include availability/provenance metadata and
  must degrade to cached or null results without failing the core endpoint.
