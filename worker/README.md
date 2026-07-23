## SnapShot Worker

Processes jobs from the API — either via **Celery + Redis** (production) or **poll loop** (dev fallback).

### Setup

```bash
cd worker
pip install -r requirements.txt
```

Environment variables (repo root or shell):

```env
API_BASE_URL=http://localhost:8000
WORKER_API_KEY=change-me-worker-key
WORKER_POLL_SECONDS=5
WORKER_DRY_RUN=true
```

`WORKER_API_KEY` must match `WORKER_API_KEY` in `backend/.env`.

---

### Mode A — Celery + Redis (recommended for production)

**Linux EC2 (API host):** install Redis and enable Celery enqueue on the API.

```bash
sudo apt install redis-server
# Optional password — see infra/redis-snapshot.conf
```

`backend/.env`:

```env
CELERY_ENABLED=true
CELERY_BROKER_URL=redis://:YOUR_PASSWORD@172.31.40.0:6379/0
CELERY_TASK_QUEUE=snapshot_jobs
```

Restart API: `sudo systemctl restart snapshot-api`

**Windows EC2 (automation host):** run Celery worker instead of poll runner.

```env
API_BASE_URL=http://172.31.40.0:8000
WORKER_API_KEY=<same as backend>
CELERY_BROKER_URL=redis://:YOUR_PASSWORD@172.31.40.0:6379/0
CELERY_TASK_QUEUE=snapshot_jobs
WORKER_DRY_RUN=false
SNAPSHOT_SKIP_EMAIL=true
```

```powershell
cd C:\snapshot
pip install -r worker\requirements.txt
python -m celery -A worker.celery_app worker -Q snapshot_jobs --pool=solo --loglevel=info
```

**Windows must use `--pool=solo`** — the default prefork pool hangs on task execution.

**Stale job recovery** (Linux EC2 — optional timer):

```bash
sudo cp infra/snapshot-recover-stale.service infra/snapshot-recover-stale.timer /etc/systemd/system/
sudo systemctl enable --now snapshot-recover-stale.timer
```

---

### Mode B — Poll worker (dev / fallback)

Terminal 1 — API:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — worker:

```bash
cd ..
export WORKER_DRY_RUN=true
export WORKER_API_KEY=change-me-worker-key
python -m worker.runner
```

Do **not** run poll worker and Celery worker at the same time when `CELERY_ENABLED=true`.

---

### Flow (Celery)

1. User creates job via `POST /jobs`
2. API saves job as `queued` and publishes task to Redis
3. Windows Celery worker calls `POST /worker/jobs/{id}/accept`
4. Worker runs `processor.process_job()` → S3 upload → `/complete` or `/fail`

### Flow (poll — legacy)

1. User creates job via `POST /jobs`
2. Worker calls `POST /worker/jobs/claim`
3. Same processing as above

### EC2 (production automation)

- Run Celery worker on **Windows EC2** with `WORKER_DRY_RUN=false`
- Install legacy runtime deps: `pywinauto`, `pytesseract`, `opencv-python`, `pyautogui`, Tesseract OCR
- Set API keys: `RENTCAST_API_KEY`, `API_NINJAS_API_KEY`, `GOOGLE_MAPS_API_KEY`
- Optional email: `SMTP_USERNAME`, `SMTP_PASSWORD` (or `SNAPSHOT_SKIP_EMAIL=true`)

Job inputs come from `POST /jobs` JSON — no Chrome capture or tkinter on EC2.
