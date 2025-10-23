from fastapi.testclient import TestClient
from src.main import app
from datetime import datetime, timezone
client = TestClient(app)

def test_stress_5k_events():
    base = {
        "topic":"stress","source":"tester",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    events=[]
    for i in range(4000):
        events.append({**base,"event_id":f"{i}","payload":{"i":i}})
    for i in range(1000):   # duplikasi 20%
        events.append({**base,"event_id":f"{i}","payload":{"i":i}})
    r = client.post("/publish", json={"events":events})
    assert r.status_code == 200
    s = client.get("/stats").json()
    assert s["unique_processed"] >= 4000
    assert s["duplicate_dropped"] >= 1000
