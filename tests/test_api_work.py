from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_work_analysis():
    resp = client.get('/api/work/MPLADS-MOCK-002')
    assert resp.status_code == 200
    data = resp.json()
    assert data['work_id'] == 'MPLADS-MOCK-002'
    assert 'risk_score' in data
    assert 'risk_level' in data
    assert 'components' in data
    # components should include expected keys
    for key in ['financial','compliance','anomaly','duplicate','spatial','context']:
        assert key in data['components']
