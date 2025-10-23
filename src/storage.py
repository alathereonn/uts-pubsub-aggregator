import os, sqlite3, json, threading, time
from typing import List, Dict, Tuple

# Gunakan path absolut dari project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "dedup.db")

_lock = threading.Lock()

DDL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS processed_events (
  topic TEXT NOT NULL,
  event_id TEXT NOT NULL,
  ts_iso TEXT NOT NULL,
  source TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  processed_at REAL NOT NULL,
  PRIMARY KEY (topic, event_id)
);
"""

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

_conn = connect()
with _lock:
    for stmt in DDL.strip().split(";"):
        s = stmt.strip()
        if s:
            _conn.execute(s)
    _conn.commit()

def insert_if_absent(ev: Dict) -> bool:
    with _lock:
        try:
            _conn.execute(
                "INSERT INTO processed_events VALUES (?,?,?,?,?,?)",
                (ev["topic"], ev["event_id"], ev["timestamp"], ev["source"],
                 json.dumps(ev["payload"]), time.time())
            )
            _conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def list_events(topic: str | None = None, limit: int = 1000) -> List[Dict]:
    q = "SELECT topic,event_id,ts_iso,source,payload_json,processed_at FROM processed_events"
    params: Tuple = ()
    if topic:
        q += " WHERE topic=?"
        params = (topic,)
    q += " ORDER BY processed_at ASC LIMIT ?"
    params += (limit,)
    rows = _conn.execute(q, params).fetchall()
    return [
        {"topic": r[0], "event_id": r[1], "timestamp": r[2],
         "source": r[3], "payload": json.loads(r[4]), "processed_at": r[5]}
        for r in rows
    ]

def count_topics() -> List[str]:
    rows = _conn.execute("SELECT DISTINCT topic FROM processed_events").fetchall()
    return [r[0] for r in rows]
