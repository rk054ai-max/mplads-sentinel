import logging
from typing import Any
import httpx
from geopy.distance import geodesic

from backend.schemas.work import Work

logger = logging.getLogger(__name__)

# Configurable radii by category where practical
_CATEGORY_RADIUS_MAP = {
    "road": 500.0,
    "drain": 500.0,
    "water": 200.0,
    "building": 100.0
}
DEFAULT_RADIUS_M = 250.0

def _get_radius_for_work(work: Work) -> float:
    if work.work_type:
        category = work.work_type.lower()
        for key, radius in _CATEGORY_RADIUS_MAP.items():
            if key in category:
                return radius
    return DEFAULT_RADIUS_M

def analyze_spatial_proximity(work: Work, dataset: list[Work], override_radius_m: float | None = None) -> dict[str, Any]:
    """
    Finds works geographically close to the target work within a configurable radius.
    Does not assume nearby works are duplicates, only returns them as supporting context.
    """
    if work.latitude is None or work.longitude is None:
        return {"spatial_score": 0.0, "nearby_works": [], "evidence": ["Missing coordinates for target work"]}

    radius_m = override_radius_m if override_radius_m is not None else _get_radius_for_work(work)
    target_coords = (work.latitude, work.longitude)
    nearby_works = []
    
    min_distance = float('inf')

    for other_work in dataset:
        if other_work.work_id == work.work_id:
            continue
            
        if other_work.latitude is not None and other_work.longitude is not None:
            other_coords = (other_work.latitude, other_work.longitude)
            distance_m = geodesic(target_coords, other_coords).meters
            
            if distance_m <= radius_m:
                min_distance = min(min_distance, distance_m)
                nearby_works.append({
                    "work_id": other_work.work_id,
                    "distance_m": round(distance_m, 1),
                    "reason": "possible_overlap"
                })

    # Sort ascending by distance (nearest first)
    nearby_works.sort(key=lambda x: x["distance_m"])
    
    spatial_score = 0.0
    evidence = [f"Analyzed {len(dataset) - 1} other works using {radius_m}m radius."]
    
    if nearby_works:
        # Score is 0-100, where 0m = 100 score, and radius_m = 0 score
        spatial_score = max(0.0, 100.0 * (1.0 - (min_distance / radius_m)))
        evidence.append(f"Found {len(nearby_works)} nearby works.")
        evidence.append(f"Nearest work is {round(min_distance, 1)}m away.")
    else:
        evidence.append("No nearby works found within radius.")
        
    return {
        "spatial_score": round(spatial_score, 2),
        "nearby_works": nearby_works,
        "evidence": evidence
    }


