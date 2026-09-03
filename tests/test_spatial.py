from backend.services.spatial import analyze_spatial_proximity
from backend.services.spatial.overpass_client import get_external_context
from backend.schemas.work import Work
from unittest.mock import patch
import httpx
from geopy.distance import geodesic

def test_analyze_spatial_proximity():
    # Base location
    base_lat = 28.6139
    base_lon = 77.2090
    target_work = Work(work_id="W_TARGET", latitude=base_lat, longitude=base_lon, work_type="building")
    
    # 0m (same location)
    work_0m = Work(work_id="W_0M", latitude=base_lat, longitude=base_lon)
    
    # Approx 100m apart (using destination)
    p_100m = geodesic(meters=100).destination((base_lat, base_lon), bearing=90)
    work_100m = Work(work_id="W_100M", latitude=p_100m.latitude, longitude=p_100m.longitude)
    
    # Approx 249m apart (to avoid float precision issues around exactly 250)
    p_250m = geodesic(meters=249).destination((base_lat, base_lon), bearing=90)
    work_250m = Work(work_id="W_250M", latitude=p_250m.latitude, longitude=p_250m.longitude)
    
    # Approx 300m apart (outside 250m radius)
    p_300m = geodesic(meters=300).destination((base_lat, base_lon), bearing=90)
    work_300m = Work(work_id="W_300M", latitude=p_300m.latitude, longitude=p_300m.longitude)
    
    # Missing coordinates
    work_missing = Work(work_id="W_MISSING")

    dataset = [target_work, work_0m, work_100m, work_250m, work_300m, work_missing]
    
    # Test with 250m radius (default or overridden)
    result = analyze_spatial_proximity(target_work, dataset, override_radius_m=250.0)
    
    nearby = result["nearby_works"]
    ids = [w["work_id"] for w in nearby]
    
    assert "W_0M" in ids
    assert "W_100M" in ids
    assert "W_250M" in ids
    assert "W_300M" not in ids
    assert "W_MISSING" not in ids
    
    # Highest score for 0m
    assert result["spatial_score"] == 100.0

def test_analyze_spatial_missing_target_coords():
    target_work = Work(work_id="W_TARGET")
    dataset = [target_work, Work(work_id="W_OTHER", latitude=28.6, longitude=77.2)]
    
    result = analyze_spatial_proximity(target_work, dataset)
    assert result["spatial_score"] == 0.0
    assert len(result["nearby_works"]) == 0
    assert "Missing coordinates" in result["evidence"][0]

@patch('backend.services.spatial.overpass_client.httpx.post')
def test_find_nearby_external_assets_timeout(mock_post):
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    work = Work(work_id="W1", latitude=28.6139, longitude=77.2090)
    assets = get_external_context(work)
    assert assets == []
