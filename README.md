## SnapShot SaaS (Dextersol / Hatem) — Phase 1 Workspace

This repository will become the full multi-user SaaS wrapper around the existing SnapShot automation.

### Setup guide
- **[Step-by-step setup guide](docs/SETUP_GUIDE.md)** — local dev, Windows EC2 worker, S3, production Linux EC2

### What we have today
- `worker/legacy/address_capture_v1.58.py`: current working local automation (Windows GUI + APIs + PDF/Excel + email)
- `docs/spec/Dextersol_Developer_Build_Guide.docx`: build specification
- `docs/pm/PROJECT_REPORT.md`: living status report for PM updates
- `artifacts/`: packaged executable + zip

### Phase 1 goal (Foundation)
- Set up backend foundation: **FastAPI + PostgreSQL + Auth + Stripe**
- Establish security baseline: **no secrets in code**, use AWS Secrets Manager
- Run the **Windows EC2 spike** early: one automation job on one cloud Windows desktop session

### Directory layout
- `backend/`: FastAPI service (auth, billing, jobs API)
- `frontend/`: Next.js dashboard
- `extension/`: Chrome extension (MV3) — capture page URL + addresses, submit jobs
- `db/`: database schema/migrations
- `worker/`: Celery worker + automation code
- `infra/`: AWS notes/scripts (EC2, S3, Redis, nginx, etc.)
- `docs/`: project docs (spec + PM updates)
- `secrets/`: sensitive items **(never commit)**

### Notes
- Dashboard, Celery queue, and Chrome extension are implemented — see `extension/README.md` for install steps.
- Do not commit any API keys, SMTP passwords, AWS credentials, or tokens.

