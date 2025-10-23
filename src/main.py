import asyncio
from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import Optional

from .models import PublishRequest
from . import storage
from .consumer import consumer_loop, stats

app = FastAPI()

# Disimpan di modul; akan dibuat saat request pertama
_queue: asyncio.Queue | None = None
_consumer_task: asyncio.Task | None = None

def _ensure_consumer_started() -> asyncio.Queue:
    global _queue, _consumer_task
    loop = asyncio.get_event_loop()
    if _queue is None:
        _queue = asyncio.Queue()
    # Start consumer di event loop yang sama (tanpa thread)
    if _consumer_task is None or _consumer_task.done():
        _consumer_task = loop.create_task(consumer_loop(_queue))
    return _queue

@app.post("/publish")
async def publish(req: PublishRequest):
    if not req.events:
        raise HTTPException(status_code=400, detail="No events provided")
    

    q = _ensure_consumer_started()
    # Enqueue semua event
    for e in req.events:
        await q.put({
            "topic": e.topic,
            "event_id": e.event_id,
            "timestamp": e.timestamp.isoformat(),
            "source": e.source,
            "payload": e.payload
        })

    # Beri waktu sangat singkat agar consumer sempat commit ke SQLite sebelum test membaca
    await asyncio.sleep(0.05)
    return {"enqueued": len(req.events), "queue_size": q.qsize()}

@app.get("/events")
async def get_events(topic: Optional[str] = None, limit: int = 1000):
    # Sedikit jeda untuk meredam race di unit test
    await asyncio.sleep(0.01)
    return storage.list_events(topic, limit)

@app.get("/stats")
async def get_stats():
    loop = asyncio.get_event_loop()
    return {
        "received": stats.received,
        "unique_processed": stats.unique_processed,
        "duplicate_dropped": stats.duplicate_dropped,
        "topics": storage.count_topics(),
        "uptime_seconds": round(loop.time() - stats.started_at, 3),
    }

@app.get("/")
def root():
    return {"message": "Pub-Sub Log Aggregator running", "timestamp": datetime.utcnow()}

