from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from typing import Any

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
WORKS_PATH = ROOT / "data" / "mock" / "sample_work.json"
ANALYSIS_PATH = ROOT / "data" / "mock" / "mock_analysis.json"


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@router.get("/health")
def api_health() -> dict[str, str]:
    return {"status": "ok", "api": "v1"}


@router.get("/works")
def list_works() -> dict[str, Any]:
    works = _load_json(WORKS_PATH)
    analysis = {}
    if ANALYSIS_PATH.exists():
        analysis = {a["work_id"]: a for a in _load_json(ANALYSIS_PATH)}

    # Attach minimal analysis metadata to each work (frontend consumes AnalysisResult separately)
    items = []
    for w in works:
        a = analysis.get(w["work_id"])
        items.append({"work_id": w["work_id"], "status": w.get("status"), "latitude": w.get("latitude"), "longitude": w.get("longitude"), "risk_score": a.get("risk_score") if a else None, "risk_level": a.get("risk_level") if a else None, "sanctioned_amount": w.get("sanctioned_amount"), "expenditure": w.get("expenditure")})

    return {"items": items, "page": 1, "page_size": len(items), "total": len(items)}


@router.get("/works/{work_id}")
def get_work(work_id: str) -> dict[str, Any]:
    works = _load_json(WORKS_PATH)
    work = next((w for w in works if w["work_id"] == work_id), None)
    if work is None:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Work not found"})

    analysis = None
    if ANALYSIS_PATH.exists():
        analysis_list = _load_json(ANALYSIS_PATH)
        analysis = next((a for a in analysis_list if a.get("work_id") == work_id), None)

    return {"work": work, "analysis": analysis}


@router.get("/summary")
def summary() -> dict[str, Any]:
    works = _load_json(WORKS_PATH)
    analysis = {}
    if ANALYSIS_PATH.exists():
        analysis = {a["work_id"]: a for a in _load_json(ANALYSIS_PATH)}

    total = len(works)
    total_expenditure = sum(float(w.get("expenditure") or 0) for w in works)
    completed = sum(1 for w in works if w.get("status") == "completed")
    delayed = sum(1 for w in works if w.get("status") == "delayed")
    high_risk = sum(1 for w in works if analysis.get(w["work_id"], {}).get("risk_level") == "HIGH")

    # risk distribution
    dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for w in works:
        lvl = analysis.get(w["work_id"], {}).get("risk_level")
        if lvl in dist:
            dist[lvl] += 1

    return {
        "total_works": total,
        "total_expenditure": total_expenditure,
        "completed_works": completed,
        "delayed_works": delayed,
        "high_risk_works": high_risk,
        "risk_distribution": dist,
    }
