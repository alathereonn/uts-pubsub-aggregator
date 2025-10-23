from fastapi.testclient import TestClient
from src.main import app
from src import storage

client = TestClient(app)

def test_persistence_survives_restart_sim():
    e = {"topic":"t2","event_id":"persist-1","timestamp":"2025-01-01T00:00:00Z","source":"test","payload":{}}
    client.post("/publish", json={"events":[e]})
    client.get("/stats")
    # simulasi “restart”: tidak menghapus SQLite; cuma memanggil insert lagi
    client.post("/publish", json={"events":[e]})
    s = client.get("/stats").json()
    # Kedua publish tidak boleh memproses dua kali:
    evs = storage.list_events("t2", 100)
    assert len([x for x in evs if x["event_id"]=="persist-1"]) == 1
    assert s["duplicate_dropped"] >= 1
