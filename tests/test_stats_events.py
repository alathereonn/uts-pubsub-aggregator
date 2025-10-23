from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)

def test_stats_and_events_consistency():
    e1 = {"topic":"t3","event_id":"e1","timestamp":"2025-01-01T00:00:00Z","source":"test","payload":{"a":1}}
    e2 = {"topic":"t3","event_id":"e2","timestamp":"2025-01-01T00:00:01Z","source":"test","payload":{"a":2}}
    client.post("/publish", json={"events":[e1,e2,e2]})
    s = client.get("/stats").json()
    assert "received" in s and "unique_processed" in s and "duplicate_dropped" in s
    evs = client.get("/events?topic=t3").json()
    ids = [x["event_id"] for x in evs]
    assert "e1" in ids and "e2" in ids
