import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_dedup_unique_once():
    e = {
        "topic":"t1","event_id":"abc12345","timestamp":"2025-01-01T00:00:00Z",
        "source":"test","payload":{"x":1}
    }
    r1 = client.post("/publish", json={"events":[e,e,e]})
    assert r1.status_code == 200
    client.get("/stats")  # allow consumer to run
    evs = client.get("/events?topic=t1").json()
    assert any(x["event_id"]=="abc12345" for x in evs)
    s = client.get("/stats").json()
    assert s["unique_processed"] >= 1
    assert s["duplicate_dropped"] >= 2
