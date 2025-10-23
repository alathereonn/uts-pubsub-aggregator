from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)

def test_schema_validation():
    bad = {"topic":"","event_id":"x","timestamp":"not-a-time","source":"","payload":{}}
    r = client.post("/publish", json={"events":[bad]})
    assert r.status_code in (400,422)
