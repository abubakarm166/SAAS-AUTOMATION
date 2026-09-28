## SnapShot SaaS (Dextersol / Hatem)

Multi-user cloud platform wrapping the SnapShot property-report automation.

**Status: Completed** — dashboard, Chrome extension, cloud worker, S3 downloads, Stripe billing, and email delivery are live.

### Client documents (send these)
- **[Delivery Document](docs/SnapShot_Delivery_Guide.md)** — formal handover, deliverables, acceptance checklist  
- **[User Guide](docs/SnapShot_User_Guide.md)** — how to use the dashboard, extension, downloads, and email  

### Developer / ops
- **[Setup guide](docs/SETUP_GUIDE.md)** — local dev, Windows EC2 worker, S3, Linux API  
- Component READMEs: `backend/`, `frontend/`, `extension/`, `worker/`, `db/`

### Directory layout
- `backend/` — FastAPI (auth, billing, jobs, worker API)
- `frontend/` — Next.js dashboard
- `extension/` — Chrome MV3 extension
- `worker/` — Celery worker + legacy automation
- `db/` — PostgreSQL schema
- `infra/` — nginx, systemd, Redis notes
- `docs/` — delivery, user guide, setup, PM notes
- `secrets/` — never commit real credentials

### Notes
- Do not commit API keys, SMTP passwords, AWS credentials, or tokens.
