## SnapShot Worker

Polls the API for `queued` jobs, runs automation, and reports `completed` / `failed`.

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

### Run (local dry-run)

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

### Flow
1. User creates job via `POST /jobs` (active subscription required)
2. Worker calls `POST /worker/jobs/claim`
3. Worker runs `processor.process_job()`
4. Worker calls `/complete` or `/fail`

### EC2 (production)
- Run worker on **Windows EC2** with `WORKER_DRY_RUN=false`
- Install worker deps: `pip install -r worker/requirements.txt`
- Install legacy runtime deps on Windows (same as original script): `pywinauto`, `pytesseract`, `opencv-python`, `pyautogui`, Tesseract OCR
- Set API keys in `.env` or environment:
  - `RENTCAST_API_KEY`
  - `API_NINJAS_API_KEY`
  - `GOOGLE_MAPS_API_KEY`
- Optional email: `SMTP_USERNAME`, `SMTP_PASSWORD`, `recipient_email` in job inputs
- Headless pipeline: `python -m worker.legacy.headless_main job.json` (used internally by worker)

```powershell
cd C:\path\to\automation
$env:WORKER_DRY_RUN="false"
$env:API_BASE_URL="http://<api-host>:8000"
$env:WORKER_API_KEY="<same as backend>"
python -m worker.runner
```

Job inputs come from `POST /jobs` JSON — no Chrome capture or tkinter on EC2.
