import asyncio
from . import storage

class Stats:
    def __init__(self):
        loop = asyncio.get_event_loop()
        self.started_at = loop.time()
        self.received = 0
        self.unique_processed = 0
        self.duplicate_dropped = 0

stats = Stats()

async def consumer_loop(queue: asyncio.Queue):
    # Loop konsumen di event loop yang sama dengan FastAPI
    while True:
        e = await queue.get()
        stats.received += 1
        if storage.insert_if_absent(e):
            stats.unique_processed += 1
        else:
            stats.duplicate_dropped += 1
        queue.task_done()
