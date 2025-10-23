import httpx, asyncio, random
from datetime import datetime, timezone

async def run(base="http://localhost:8080", n=100, dup_ratio=0.2, topic="logs.appA"):
    events = []
    for i in range(n):
        eid = f"{i}"
        ts = datetime.now(timezone.utc).isoformat()
        ev = {"topic": topic, "event_id": eid, "timestamp": ts, "source": "sim", "payload": {"i": i}}
        events.append(ev)
        if random.random() < dup_ratio:
            events.append(ev)  # duplikat
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.post(f"{base}/publish", json={"events": events})
        r.raise_for_status()
        print(r.json())

if __name__ == "__main__":
    asyncio.run(run())
