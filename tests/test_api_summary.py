from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_summary_endpoint():
    resp = client.get('/api/summary')
    assert resp.status_code == 200
    data = resp.json()
    keys = ['total_works','total_expenditure','completed_works','ongoing_works','delayed_works','high_risk_works','medium_risk_works','low_risk_works']
    for k in keys:
        assert k in data
    assert isinstance(data['total_works'], int)