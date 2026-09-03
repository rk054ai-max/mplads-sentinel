import logging
import json
import os
from typing import Any
import httpx
from geopy.distance import geodesic
from backend.schemas.work import Work

logger = logging.getLogger(__name__)

CACHE_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "external", "osm_cache.json")
OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
TIMEOUT_SECONDS = 3.0

def _load_cache() -> dict[str, list[dict[str, Any]]]:
    if not os.path.exists(CACHE_FILE_PATH):
        return {}
    try:
        with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load OSM cache: {e}")
        return {}

def _save_cache(cache_data: dict[str, list[dict[str, Any]]]):
    os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)
    try:
        with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save OSM cache: {e}")

def get_external_context(work: Work, radius_m: float = 1000.0) -> list[dict[str, Any]]:
    """
    Fetches contextual assets from OpenStreetMap via Overpass API.
    NOTE: OSM data is purely contextual and NOT authoritative proof of government asset existence.
    Fails gracefully returning an empty list or persistent cached data if API is unavailable.
    """
    if work.latitude is None or work.longitude is None:
        return []

    cache = _load_cache()
    # Cache key must be a string for JSON serialization
    cache_key = f"{work.latitude}_{work.longitude}_{radius_m}"

    if cache_key in cache:
        logger.info(f"Returning cached assets for {cache_key}")
        return cache[cache_key]

    query = f"""
    [out:json];
    (
      node["amenity"~"hospital|school|police|community_centre"](around:{radius_m},{work.latitude},{work.longitude});
      way["amenity"~"hospital|school|police|community_centre"](around:{radius_m},{work.latitude},{work.longitude});
      node["highway"](around:{radius_m},{work.latitude},{work.longitude});
      way["highway"](around:{radius_m},{work.latitude},{work.longitude});
    );
    out center;
    """

    try:
        response = httpx.post(OVERPASS_URL, data=query, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
        
        assets = []
        target_coords = (work.latitude, work.longitude)

        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name", "Unnamed Asset")
            asset_type = tags.get("amenity") or tags.get("highway", "unknown")
            lat = element.get("lat") or element.get("center", {}).get("lat")
            lon = element.get("lon") or element.get("center", {}).get("lon")
            
            if lat and lon:
                asset_coords = (lat, lon)
                distance_m = geodesic(target_coords, asset_coords).meters
                assets.append({
                    "asset_type": asset_type,
                    "name": name,
                    "latitude": lat,
                    "longitude": lon,
                    "distance_m": round(distance_m, 1),
                    "source": "OpenStreetMap"
                })
        
        cache[cache_key] = assets
        _save_cache(cache)
        return assets
        
    except (httpx.RequestError, httpx.TimeoutException) as e:
        logger.warning(f"Failed to fetch external assets: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return []
