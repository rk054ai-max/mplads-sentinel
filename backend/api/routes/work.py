from fastapi import APIRouter, HTTPException
from typing import Any, Dict
from backend.core.analyzer import analyze_work
from pathlib import Path
import json

router = APIRouter()
ROOT = Path(__file__).resolve().parents[3]
WORKS_PATH = ROOT / "data" / "mock" / "sample_work.json"
ANALYSIS_PATH = ROOT / "data" / "mock" / "mock_analysis.json"


def _load_works():
    with WORKS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


@router.get("/work/{work_id}")
def get_analysis(work_id: str) -> Dict[str, Any]:
    try:
        result = analyze_work(work_id)
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Work not found"})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "internal_error", "message": str(e)})


@router.get("/summary")
def summary() -> Dict[str, Any]:
    works = _load_works()
    total = len(works)
    total_expenditure = sum(float(w.get("expenditure") or 0) for w in works)
    completed = sum(1 for w in works if w.get("status") == "completed")
    ongoing = sum(1 for w in works if w.get("status") == "in_progress")
    delayed = sum(1 for w in works if w.get("status") == "delayed")

    # compute risk buckets by running analyzer; if mock_analysis exists use it to avoid heavy computation
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    if ANALYSIS_PATH.exists():
        with ANALYSIS_PATH.open(encoding="utf-8") as fh:
            analysis_list = json.load(fh)
        for a in analysis_list:
            lvl = a.get("risk_level")
            if lvl in risk_counts:
                risk_counts[lvl] += 1
    else:
        # run analyzer for each work (graceful)
        for w in works:
            try:
                res = analyze_work(w.get("work_id"))
                lvl = res.get("risk_level")
                if lvl in risk_counts:
                    risk_counts[lvl] += 1
            except Exception:
                continue

    return {
        "total_works": total,
        "total_expenditure": total_expenditure,
        "completed_works": completed,
        "ongoing_works": ongoing,
        "delayed_works": delayed,
        "high_risk_works": risk_counts.get("HIGH", 0),
        "medium_risk_works": risk_counts.get("MEDIUM", 0),
        "low_risk_works": risk_counts.get("LOW", 0),
    }
