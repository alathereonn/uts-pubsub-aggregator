# Idempotent Pub-Sub Log Aggregator (Python + FastAPI)

# Step-by-steps:
1. Run and Build Docker:
docker build -t uts-aggregator .
docker run -p 8080:8080 uts-aggregator

Tunjukkan log Uvicorn: “Uvicorn running on http://0.0.0.0:8080”

Bonus: Docker Compose:
docker compose up --build

2. Lihat OpenAPI Docs:
http://localhost:8080/docs

a. POST /publish → kirim batch (2 duplikat + 1 unik):
{
  "events":[
    {"topic":"logs.appA","event_id":"event-0002","timestamp":"2025-01-01T01:00:00Z","source":"cli","payload":{"level":"info","msg":"first log"}},
    {"topic":"logs.appA","event_id":"event-0002","timestamp":"2025-01-01T01:00:00Z","source":"cli","payload":{"level":"info","msg":"duplicate log"}},
    {"topic":"logs.appA","event_id":"event-0003","timestamp":"2025-01-01T02:00:00Z","source":"cli","payload":{"level":"warn","msg":"another event"}}
  ]
}

b. GET /stats 
c. GET /events?topic=logs.appA, hanya 2 baris unik: event-0002 & event-0003.

3. Test Duplikasi Sederhana:
$body = @{
  events = @(
    @{
      topic="logs.appA"; event_id="event-0002"; timestamp="2025-01-01T01:00:00Z"; source="cli";
      payload=@{ level="info"; msg="first log" }
    },
    @{
      topic="logs.appA"; event_id="event-0002"; timestamp="2025-01-01T01:00:00Z"; source="cli";
      payload=@{ level="info"; msg="duplicate log" }
    },
    @{
      topic="logs.appA"; event_id="event-0003"; timestamp="2025-01-01T02:00:00Z"; source="cli";
      payload=@{ level="warn"; msg="another event" }
    }
  )
} | ConvertTo-Json -Depth 6

Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method POST -ContentType "application/json" -Body $body
Invoke-RestMethod -Uri "http://localhost:8080/stats"
Invoke-RestMethod -Uri "http://localhost:8080/events?topic=logs.appA"

4. Uji idempotency
Kirim event lalu cek tersimpan:
$e = @{ topic="persist"; event_id="persist-1"; timestamp="2025-01-01T00:00:00Z"; source="cli"; payload=@{} }
$body = @{ events=@($e) } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method POST -ContentType "application/json" -Body $body
Invoke-RestMethod -Uri "http://localhost:8080/events?topic=persist"

Restart Service:
docker stop $(docker ps -q --filter ancestor=uts-aggregator)
docker run -p 8080:8080 -v aggdata:/app/data uts-aggregator
Compose: 
docker compose down 
docker compose up -d

Kirim Event yang sama lalu di drop:
$e = @{ topic="persist"; event_id="persist-1"; timestamp="2025-01-01T00:00:00Z"; source="cli"; payload=@{} }
$body = @{ events=@($e) } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method POST -ContentType "application/json" -Body $body
Invoke-RestMethod -Uri "http://localhost:8080/stats"
Invoke-RestMethod -Uri "http://localhost:8080/events?topic=persist"

5. Validasi Skema:
$bad = @{ events=@(
  @{ topic="bad"; event_id="id-1"; timestamp="2025-01-01T00:00:00Z"; source="cli"; payload=@{} }
)} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method POST -ContentType "application/json" -Body $bad

6. Stress Mini: 5.000 event dengan 20% duplikat (±60–90 detik)
$base = @{ topic="stress"; source="tester"; timestamp=(Get-Date).ToUniversalTime().ToString("o") }
$events = @()
0..3999 | ForEach-Object { $events += @{ topic=$base.topic; source=$base.source; timestamp=$base.timestamp; event_id="$_"; payload=@{i=$_} } }
0..999  | ForEach-Object { $events += @{ topic=$base.topic; source=$base.source; timestamp=$base.timestamp; event_id="$_"; payload=@{i=$_} } }

$body = @{ events=$events } | ConvertTo-Json -Depth 6
Invoke-RestMethod -Uri "http://localhost:8080/publish" -Method POST -ContentType "application/json" -Body $body
Invoke-RestMethod -Uri "http://localhost:8080/stats"

7. Jalanin Unit Test:
pytest -v

8. Verifikasi langsung SQLite di dalam container:
docker ps
docker exec -it <CONTAINER_ID> sh
sqlite3 /app/data/dedup.db 'SELECT topic,event_id,ts_iso,source FROM processed_events;'
