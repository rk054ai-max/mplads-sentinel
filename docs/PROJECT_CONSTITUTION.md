# Project Constitution

## Product

**MPLADS Sentinel - Explainable AI Risk & Anomaly Detection for MPLADS works.**

## Purpose

Prioritize MPLADS works for administrative verification using rule-based
compliance checks, statistical/ML anomaly detection, NLP similarity, geospatial
context, and explainable risk scoring.

The system identifies risk indicators and prioritizes human review. It does not
declare fraud, corruption, guilt, or innocence.

## Non-goals

- Do not declare fraud.
- Do not rank politicians by corruption.
- Do not make legal accusations.
- Do not rely on one ML model.
- Do not require external APIs to run.
- Do not implement authentication in the MVP.
- Do not implement a mobile app in the MVP.
- Do not implement satellite-based verification in the MVP.
- Do not implement blockchain.
- Do not implement complex deep learning training.

## MVP features

1. Data ingestion.
2. Compliance and timeline rules.
3. Financial peer benchmark.
4. Isolation Forest anomaly detection.
5. NLP duplicate detection.
6. Spatial proximity.
7. Risk fusion.
8. Dashboard.
9. Investigation page.
10. LLM explanation, only after the previous features work.

External government or geospatial context is optional and must have a local
cached fallback. LLM output is optional and may only summarize existing
deterministic and ML results.

## Technology

Python, FastAPI, Pandas, NumPy, Scikit-learn, Sentence Transformers,
GeoPandas/Geopy, React, Vite, Tailwind, Recharts, Leaflet, and SQLite. The data
access boundary must permit a future PostgreSQL adapter.

## Team ownership

- **Member A:** data, compliance, and anomaly detection.
- **Member B:** NLP, spatial analysis, and external context.
- **Member C:** frontend, API, and integration.

## Signal vocabulary

- **Rule violation:** a deterministic deviation from a configured government or
  project rule; it is not proof of wrongdoing.
- **Anomaly:** an observation statistically unlike its comparison population or
  expected pattern.
- **Potential duplicate:** two works with material textual, financial, temporal,
  or spatial similarity that merits checking.
- **Contextual overlap:** relevant nearby, administrative, or external evidence
  that may explain or increase the importance of a signal.
- **Investigation priority:** an explainable fused ordering used to allocate
  administrative verification effort.
- **Confirmed fraud:** a legal or administrative conclusion established through
  due process; this system never produces it.

The system may produce only the first five outputs. It must never produce
"confirmed fraud" or equivalent language.

## Integration rule

The `main` branch must remain runnable after every merge. Preserve provenance,
reproducibility, schema versioning, stable API contracts, human adjudication,
privacy, and secret-free source control in every implementation.
