"""Orchestrate per-work analyses and combine with the risk engine."""
from pathlib import Path
import json
import math
from typing import Any, Dict, Optional

from backend.schemas.work import Work
from ml.scoring.risk_engine import calculate_risk_score

ROOT = Path(__file__).resolve().parents[2]
WORKS_PATH = ROOT / "data" / "mock" / "sample_work.json"


def _load_works() -> list[dict]:
    with WORKS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _find_work(work_id: str) -> Optional[dict]:
    works = _load_works()
    return next((w for w in works if w.get("work_id") == work_id), None)


def _safe_float(v) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def run_compliance_analysis(work: Work) -> dict:
    evidence = []
    score = 0.0
    if work.sanction_date is None:
        score = 90.0
        evidence.append("Missing sanction date")
    else:
        score = 10.0
        evidence.append("Sanction paperwork present")
    return {"score": round(score, 2), "evidence": evidence}


def run_financial_analysis(work: Work) -> dict:
    evidence = []
    sanctioned = _safe_float(work.sanctioned_amount) if work.sanctioned_amount is not None else 0.0
    expenditure = _safe_float(work.expenditure) if work.expenditure is not None else 0.0
    if sanctioned <= 0:
        score = 80.0 if expenditure > 0 else 0.0
        evidence.append("No sanctioned amount recorded")
    else:
        ratio = expenditure / sanctioned
        if ratio > 1.5:
            score = 85.0
            evidence.append(f"Expenditure exceeds sanctioned amount (ratio={ratio:.2f})")
        elif ratio > 1.0:
            score = 60.0
            evidence.append(f"Expenditure slightly exceeds sanctioned amount (ratio={ratio:.2f})")
        else:
            score = 10.0
            evidence.append("Expenditure within sanctioned amount")
    return {"score": round(score, 2), "evidence": evidence}


def run_anomaly_analysis(work: Work) -> dict:
    # Placeholder for Isolation Forest — deterministic heuristic here
    evidence = []
    expenditure = _safe_float(work.expenditure)
    if expenditure > 1_000_000:
        score = 80.0
        evidence.append("Very large expenditure flagged for review")
    else:
        score = 5.0
        evidence.append("No strong anomalies detected by heuristic")
    return {"score": round(score, 2), "evidence": evidence}


def run_duplicate_detection(work: Work, all_works: list[dict]) -> dict:
    evidence = []
    desc = (work.description or "").lower()
    duplicates = [w for w in all_works if w.get("work_id") != work.work_id and desc and desc in (w.get("description") or "").lower()]
    if duplicates:
        score = 90.0
        evidence.append(f"Found {len(duplicates)} similar works by description")
    else:
        score = 0.0
    return {"score": round(score, 2), "evidence": evidence}


def run_spatial_analysis(work: Work, all_works: list[dict]) -> dict:
    evidence = []
    lat = work.latitude
    lon = work.longitude
    if lat is None or lon is None:
        score = 50.0
        evidence.append("Missing coordinates")
    else:
        # crude check: lat/lon within India's bounding box
        if not (6.0 <= lat <= 36.0 and 68.0 <= lon <= 98.0):
            score = 90.0
            evidence.append("Coordinates outside expected India bounding box")
        else:
            # context: nearby works
            near = 0
            for w in all_works:
                wl = w.get("latitude")
                wo = w.get("longitude")
                if wl is None or wo is None:
                    continue
                # simple euclidean approx
                if math.hypot(lat - wl, lon - wo) < 0.05:
                    near += 1
            if near > 0:
                score = 30.0
                evidence.append(f"{near} nearby works within small radius")
            else:
                score = 5.0
    return {"score": round(score, 2), "evidence": evidence}


def run_context_analysis(work: Work, all_works: list[dict]) -> dict:
    # Context captures external signals such as nearby similar works
    evidence = []
    # re-use duplicate and spatial information in a simple way
    dup = run_duplicate_detection(work, all_works)
    spatial = run_spatial_analysis(work, all_works)
    score = max(dup["score"], spatial["score"] / 2)
    if dup["evidence"]:
        evidence.extend(dup["evidence"])
    if spatial["evidence"]:
        evidence.extend(spatial["evidence"])
    return {"score": round(score, 2), "evidence": evidence}


def analyze_work(work_id: str) -> Dict[str, Any]:
    raw = _find_work(work_id)
    if raw is None:
        raise KeyError("work_not_found")

    # parse canonical work via pydantic model
    work = Work(**raw)
    all_works = _load_works()

    financial = run_financial_analysis(work)
    compliance = run_compliance_analysis(work)
    anomaly = run_anomaly_analysis(work)
    duplicate = run_duplicate_detection(work, all_works)
    spatial = run_spatial_analysis(work, all_works)
    context = run_context_analysis(work, all_works)

    # combine via risk engine (order: financial, compliance, anomaly, duplicate, spatial, context)
    risk = calculate_risk_score(
        financial["score"],
        compliance["score"],
        anomaly["score"],
        duplicate["score"],
        spatial["score"],
        context["score"],
    )

    analysis_result = {
        "work_id": work.work_id,
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "components": {
            "financial": financial,
            "compliance": compliance,
            "anomaly": anomaly,
            "duplicate": duplicate,
            "spatial": spatial,
            "context": context,
        },
        "recommendations": [],
        "ai_summary": None,
    }

    # small, deterministic recommendations
    recs = []
    if financial["score"] >= 80:
        recs.append("Prioritise financial audit")
    if compliance["score"] >= 80:
        recs.append("Request missing sanction paperwork")
    if anomaly["score"] >= 60:
        recs.append("Perform anomaly review with ML team")
    analysis_result["recommendations"] = recs
    analysis_result["ai_summary"] = (
        f"Computed risk {analysis_result['risk_score']} ({analysis_result['risk_level']})."
    )

    return analysis_result
