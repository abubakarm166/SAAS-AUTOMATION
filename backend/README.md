## SnapShot Backend (FastAPI)

### Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

Copy env vars from repo root `.env.example` into `backend/.env` (or repo root `.env`).

Apply database schema first: see `db/README.md`.

### Run

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Phase 1 endpoints
- `GET /health`
- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `POST /jobs` (requires active subscription)
- `GET /jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/files`
- `GET /jobs/{job_id}/files/{file_id}/download` (presigned S3 URL)
- `POST /billing/checkout-session`
- `POST /billing/webhook`
- `POST /worker/jobs/claim` (worker key)
- `POST /worker/jobs/{id}/complete` (worker key)
- `POST /worker/jobs/{id}/fail` (worker key)
