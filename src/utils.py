from datetime import datetime, timezone
def uptime_seconds(now_mono: float, started_mono: float) -> float:
    return max(0.0, now_mono - started_mono)
