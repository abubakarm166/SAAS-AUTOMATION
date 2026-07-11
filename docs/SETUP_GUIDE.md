# SnapShot SaaS — Step-by-Step Setup Guide

Complete walkthrough for local development, Windows EC2 worker, S3 storage, and (later) production API hosting.

**Last updated:** 2026-07-10

---

## Table of contents

1. [Architecture overview](#1-architecture-overview)
2. [What you need (by phase)](#2-what-you-need-by-phase)
3. [Prerequisites](#3-prerequisites)
4. [Step 1 — Clone the repo](#step-1--clone-the-repo)
5. [Step 2 — PostgreSQL database](#step-2--postgresql-database)
6. [Step 3 — Backend API (Linux)](#step-3--backend-api-linux)
7. [Step 4 — Environment variables](#step-4--environment-variables)
8. [Step 5 — Test API with Postman](#step-5--test-api-with-postman)
9. [Step 6 — Local dry-run worker (Linux)](#step-6--local-dry-run-worker-linux)
10. [Step 7 — Expose API with ngrok (dev only)](#step-7--expose-api-with-ngrok-dev-only)
11. [Step 8 — AWS S3 bucket](#step-8--aws-s3-bucket)
12. [Step 9 — Windows EC2 worker](#step-9--windows-ec2-worker)
13. [Step 10 — End-to-end test (real automation)](#step-10--end-to-end-test-real-automation)
14. [Step 11 — Download files from S3 via API](#step-11--download-files-from-s3-via-api)
15. [Step 12 — Production: Linux EC2 for API (future)](#step-12--production-linux-ec2-for-api-future)
16. [Troubleshooting](#troubleshooting)
17. [Quick checklist](#quick-checklist)

---

## 1. Architecture overview

### Development (what you use now)

```
┌─────────────────┐     ngrok      ┌──────────────────┐     HTTPS      ┌─────────────────────┐
│  Linux dev PC   │ ──────────────►│  ngrok tunnel    │◄───────────────│  Windows EC2        │
│  PostgreSQL     │                │                  │                │  worker/runner.py   │
│  FastAPI :8000  │                │                  │                │  headless automation│
└─────────────────┘                └──────────────────┘                └─────────────────────┘
        ▲                                                                         │
        │ Postman / future UI                                                     ▼
   Developer testing                                                    S3: PDF + Excel
```

### Production (target)

```
┌─────────────────┐                              ┌─────────────────────┐
│  Linux EC2      │◄──── private VPC network ───►│  Windows EC2        │
│  FastAPI + DB   │                              │  worker only        │
└─────────────────┘                              └─────────────────────┘
        │                                                   │
        ▼                                                   ▼
   Users / Stripe                                      S3 bucket
```

**Rule of thumb**

| Machine | What runs there |
|---------|-----------------|
| **Linux** (laptop now, EC2 later) | API + PostgreSQL |
| **Windows EC2** | Automation worker only |
| **S3** | Stored PDF + Excel reports |

---

## 2. What you need (by phase)

| Phase | Goal | Machines needed |
|-------|------|-----------------|
| **A** | API + auth + jobs work locally | Linux laptop only |
| **B** | Worker dry-run on laptop | Linux laptop only |
| **C** | Real PDF/Excel in cloud | Linux laptop + **Windows EC2** + ngrok |
| **D** | File downloads | Above + **S3** + AWS keys |
| **E** | Production (no ngrok) | **Linux EC2** (API) + Windows EC2 (worker) |

You do **not** need Linux EC2 until Phase E. Your laptop is enough for Phases A–D.

---

## 3. Prerequisites

### On your Linux dev machine

- Python 3.11+
- Git
- PostgreSQL client (`psql`) — optional but useful
- Docker **or** Podman (for PostgreSQL container)
- [ngrok](https://ngrok.com/) account (free tier works for dev)
- Postman or `curl`

### On Windows EC2 (Phase C+)

- Windows Server 2022 (or similar)
- Python 3.11+
- RDP access
- Git or copy project to `C:\snapshot\`

### AWS (Phase D+)

- AWS account with access to EC2, S3, IAM
- Region used in this project: **eu-north-1**
- S3 bucket: **snapshot-reports-dev-cloud**

### Third-party API keys (for real automation)

- RentCast API key
- API Ninjas API key
- Google Maps API key

### Stripe (optional for dev)

- Stripe test keys — or use `BYPASS_SUBSCRIPTION_CHECK=true` for local job testing

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/abubakarm166/SAAS-AUTOMATION.git
cd SAAS-AUTOMATION
```

Or use your existing path:

```bash
cd /home/abubakar/Documents/Projects/manger/automation
```

---

## Step 2 — PostgreSQL database

Pick **one** option below. On **Ubuntu EC2**, use **Option C** (native install) — Docker is often not pre-installed and `docker.io` may not be available.

### Option A — Docker (local dev laptop)

```bash
docker run --name snapshot-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=snapshot \
  -p 5432:5432 \
  -d postgres:16
```

If `docker` is not installed on Ubuntu, either use Option C below or install Docker from the official repo:

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${VERSION_CODENAME}) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
# log out and back in, then re-run the docker run command above
```

### Option B — Podman (if you use Podman)

```bash
podman run --name snapshot-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=snapshot \
  -p 5432:5432 \
  -d docker.io/library/postgres:16
```

**Start again after reboot:**

```bash
podman start snapshot-postgres
# or: docker start snapshot-postgres
```

### Option C — Native PostgreSQL on Ubuntu EC2 (recommended for Linux server)

Use this on your **Linux EC2** API server when Docker is not available:

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Create database and set postgres password
sudo -u postgres psql -c "CREATE DATABASE snapshot;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

Apply schema (from repo root):

```bash
cd ~/SAAS-AUTOMATION
sudo -u postgres psql -d snapshot -f db/schema.sql
```

**Verify:**

```bash
sudo -u postgres psql -d snapshot -c "\dt"
`

You should see `users`, `jobs`, `subscriptions`, `job_files`, etc.

**`backend/.env` connection string** (same for all options):

```env
``DATABASE_URL=postgresql://postgres:postgres@localhost:5432/snapshot
```

**Start PostgreSQL after reboot** (native install):

```bash
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### Apply schema (Docker / Podman only)

If you used Docker or Podman instead of Option C:

```bash
psql postgresql://postgres:postgres@localhost:5432/snapshot -f db/schema.sql
```

**Verify:** `\dt` in `psql` should show `users`, `jobs`, `subscriptions`, `job_files`, etc.

---

## Step 3 — Backend API (Linux)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run the API** (must be from `backend/` directory):

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:**

- Open http://localhost:8000/docs
- `GET http://localhost:8000/health` → `{"status":"ok"}`

> **Important:** Always run `uvicorn` from the `backend/` folder. Running from repo root causes `No module named 'app'`.

---

## Step 4 — Environment variables

Create `backend/.env` (never commit this file):

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/snapshot

# Auth
JWT_SECRET=change-me-to-a-long-random-string

# Worker auth (must match worker .env)
WORKER_API_KEY=change-me-worker-key

# Dev only — skip Stripe subscription check when creating jobs
BYPASS_SUBSCRIPTION_CHECK=true

# Stripe (test mode — optional if bypass is true)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# S3 (needed for file upload/download)
AWS_REGION=eu-north-1
S3_BUCKET_NAME=snapshot-reports-dev-cloud
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_PRESIGN_EXPIRE_SECONDS=3600
```

For **Windows EC2 worker**, create `C:\snapshot\.env` (or repo root `.env`):

```env
API_BASE_URL=http://localhost:8000
WORKER_API_KEY=change-me-worker-key
WORKER_POLL_SECONDS=5
WORKER_DRY_RUN=false

# Third-party APIs (real automation)
RENTCAST_API_KEY=...
API_NINJAS_API_KEY=...
GOOGLE_MAPS_API_KEY=...

# S3 upload from worker
AWS_REGION=eu-north-1
S3_BUCKET_NAME=snapshot-reports-dev-cloud
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Optional
SNAPSHOT_WORK_DIR=C:\snapshot\output
SNAPSHOT_SKIP_EMAIL=true
```

**Rules:**

1. `WORKER_API_KEY` must be **identical** in `backend/.env` and worker `.env`
2. After changing `backend/.env`, **restart uvicorn**
3. Never commit `.env` files or access key CSVs to Git

---

## Step 5 — Test API with Postman

### 5.1 Health check

```
GET http://localhost:8000/health
```

### 5.2 Sign up

```
POST http://localhost:8000/auth/signup
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```

### 5.3 Log in

```
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```

Copy the `access_token` from the response.

### 5.4 Create a job

```
POST http://localhost:8000/jobs
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "source_url": "https://www.ashlandauction.com/auctions/33350",
  "inputs": {
    "addresses": ["2202 Clifton Ave, Baltimore, MD 21216"],
    "interest_rate": 0.06,
    "years": 30,
    "discount_percentage": 0.25,
    "closing_costs_input": 0.04,
    "money_down_input": 0.2,
    "operating_expenses_input": 0.02,
    "num_months_holding": 3
  }
}
```

Expected: `status: "queued"` and a `job_id`.

### 5.5 Check job status

```
GET http://localhost:8000/jobs/<job_id>
Authorization: Bearer <access_token>
```

---

## Step 6 — Local dry-run worker (Linux)

Terminal 1 — API (already running from Step 3).

Terminal 2 — worker:

```bash
cd /path/to/automation
source backend/venv/bin/activate   # or use a separate venv
pip install -r worker/requirements.txt

export WORKER_DRY_RUN=true
export WORKER_API_KEY=change-me-worker-key
export API_BASE_URL=http://localhost:8000

python -m worker.runner
```

**Flow:**

1. Create job in Postman → status `queued`
2. Worker logs: claimed job → processing → completed
3. `GET /jobs/<id>` → status `completed`

---

## Step 7 — Expose API with ngrok (dev only)

Windows EC2 cannot reach `localhost` on your laptop. Use ngrok:

```bash
ngrok http 8000
```

Copy the HTTPS URL, e.g. `https://abc123.ngrok-free.app`.

Update Windows worker `.env`:

```env
API_BASE_URL=https://abc123.ngrok-free.app
```

> ngrok URL changes every time you restart ngrok (free tier). Update `API_BASE_URL` on EC2 each time.

The worker client automatically sends `ngrok-skip-browser-warning: true` when the URL contains `ngrok`.

---

## Step 8 — AWS S3 bucket

### 8.1 Create bucket (if not already done)

1. AWS Console → S3 → Create bucket
2. Name: `snapshot-reports-dev-cloud`
3. Region: `eu-north-1`
4. Block public access: **on** (files accessed via presigned URLs only)

### 8.2 IAM policy for S3

Create policy `SnapshotReportsS3Policy` (adjust bucket name if needed):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::snapshot-reports-dev-cloud",
        "arn:aws:s3:::snapshot-reports-dev-cloud/*"
      ]
    }
  ]
}
```

### 8.3 Attach credentials

**Option A — IAM user access keys** (what works today):

1. Create IAM user `snapshot-s3-dev`
2. Attach `SnapshotReportsS3Policy`
3. Create access key → put in `backend/.env` and Windows `.env`

**Option B — EC2 instance role** (preferred for production):

1. Create role `SnapshotWindowsWorkerRole` with the S3 policy
2. Attach role to Windows EC2 instance
3. Remove access keys from `.env` once role works

> If `curl http://169.254.169.254/latest/meta-data/iam/security-credentials/` returns 404, the instance role is **not** attached — use access keys until fixed.

### 8.4 Test S3 from Windows EC2

```powershell
aws s3 cp C:\test.txt s3://snapshot-reports-dev-cloud/test/test.txt
```

Or use Python/boto3 with the same keys from `.env`.

---

## Step 9 — Windows EC2 worker

### 9.1 Launch EC2 instance

- AMI: **Windows Server 2022**
- Instance type: `t3.medium` or larger (automation uses CPU/RAM)
- Security group: allow RDP (3389) from your IP only
- Same VPC as future Linux API EC2 (for production)

### 9.2 Connect via RDP

Download `.rdp` file from AWS Console → connect with Administrator password.

### 9.3 Install software

1. **Python 3.11+** — https://www.python.org/downloads/windows/
   - Check "Add Python to PATH"
2. **Git** (optional) — or copy project as zip
3. **Tesseract OCR** — required by legacy script
4. **Chrome** — if testing GUI mode (headless mode does not need Chrome)

### 9.4 Clone / copy project

```powershell
cd C:\
git clone https://github.com/abubakarm166/SAAS-AUTOMATION.git snapshot
cd C:\snapshot
```

Or unzip the project to `C:\snapshot\`.

### 9.5 Install Python dependencies

```powershell
cd C:\snapshot
pip install -r worker\requirements.txt
pip install pywinauto pytesseract opencv-python pyautogui boto3
```

### 9.6 Configure `.env`

Create `C:\snapshot\.env` — see [Step 4](#step-4--environment-variables).

Set:

```env
WORKER_DRY_RUN=false
API_BASE_URL=https://<your-ngrok-url>
WORKER_API_KEY=<same as backend>
```

### 9.7 Run worker

```powershell
cd C:\snapshot
python -m worker.runner
```

Leave this terminal open. Worker polls every `WORKER_POLL_SECONDS` (default 5).

**Optional — run as Windows Service** (later): use NSSM or Task Scheduler to auto-start on boot.

---

## Step 10 — End-to-end test (real automation)

1. **Linux:** API running + ngrok tunnel active
2. **Windows EC2:** `python -m worker.runner` running with `WORKER_DRY_RUN=false`
3. **Postman:** Create job with a real US address

Example address that was verified:

```
2202 Clifton Ave, Baltimore, MD 21216
```

4. Watch Windows worker logs — should show claim → process → complete (~7–30 seconds)
5. Check job:

```
GET http://localhost:8000/jobs/<job_id>
```

Expected: `"status": "completed"`

6. Check S3 bucket for files under:

```
jobs/<user_id>/<job_id>/
```

---

## Step 11 — Download files from S3 via API

### List files

```
GET http://localhost:8000/jobs/<job_id>/files
Authorization: Bearer <access_token>
```

### Get presigned download URL

```
GET http://localhost:8000/jobs/<job_id>/files/<file_id>/download
Authorization: Bearer <access_token>
```

Response includes a temporary `url` — open in browser or download with `curl`.

> If you get `NoCredentialsError`, ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set in `backend/.env` and restart uvicorn.

---

## Step 12 — Production: Linux EC2 for API (future)

When you are ready to stop using your laptop + ngrok:

### 12.1 Launch Linux EC2

- AMI: **Ubuntu 22.04 LTS**
- Instance type: `t3.small` or `t3.medium`
- Security group:
  - Port 22 (SSH) from your IP
  - Port 8000 or 443 from VPC / load balancer only
- **Same VPC** as Windows worker EC2

### 12.2 Install on Linux EC2

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql-client

# Clone repo
git clone https://github.com/abubakarm166/SAAS-AUTOMATION.git
cd SAAS-AUTOMATION/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 12.3 PostgreSQL on Linux EC2

Either:

- **RDS** (recommended for production) — managed PostgreSQL in same VPC
- **Postgres on same EC2** — simpler but less resilient

Apply schema: `psql $DATABASE_URL -f db/schema.sql`

### 12.4 Configure production `.env`

```env
DATABASE_URL=postgresql://user:pass@<db-host>:5432/snapshot
JWT_SECRET=<strong-random-secret>
WORKER_API_KEY=<strong-random-key>
BYPASS_SUBSCRIPTION_CHECK=false
AWS_REGION=eu-north-1
S3_BUCKET_NAME=snapshot-reports-dev-cloud
# Use IAM role on EC2 instead of keys when possible
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 12.5 Run API as a service

Use **systemd** or **gunicorn + nginx**:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Add nginx + Let's Encrypt SSL for `api.yourdomain.com`.

### 12.6 Update Windows worker

```env
API_BASE_URL=http://<linux-ec2-private-ip>:8000
# or https://api.yourdomain.com
```

No ngrok needed. Worker and API talk inside the VPC.

### 12.7 Remaining production tasks

- [ ] Redis + Celery job queue
- [ ] AWS Secrets Manager (rotate keys out of `.env`)
- [ ] Stripe webhook URL → production API
- [ ] Email (SES or Gmail — client decision)
- [ ] Monitoring / alerts
- [ ] Chrome extension + dashboard (Phase 3)

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `No module named 'app'` | Wrong working directory | Run uvicorn from `backend/` |
| Worker `401 Unauthorized` | API key mismatch | Sync `WORKER_API_KEY`; restart API |
| Postgres connection refused | Container stopped | `podman start snapshot-postgres` |
| EC2 can't reach API | No public URL | Start ngrok; set `API_BASE_URL` |
| ngrok blocks requests | Browser warning page | Worker sends skip header automatically |
| `NoCredentialsError` on download | Missing AWS keys in backend | Add keys to `backend/.env`; restart API |
| S3 upload fails on EC2 | No IAM role / bad keys | Attach role or use IAM user keys |
| Job stays `queued` | Worker not running | Start `python -m worker.runner` |
| `KeyError: 1` on single address | Old legacy script bug | Use latest `worker/legacy/` code |
| Subscription required | No active Stripe sub | Set `BYPASS_SUBSCRIPTION_CHECK=true` for dev |

---

## Quick checklist

### Local dev (Phase A–B)

- [ ] PostgreSQL running + schema applied
- [ ] `backend/.env` configured
- [ ] API runs on http://localhost:8000
- [ ] Signup / login works in Postman
- [ ] Create job → dry-run worker → `completed`

### Cloud automation (Phase C–D)

- [ ] ngrok tunnel to port 8000
- [ ] Windows EC2 with Python + deps
- [ ] Worker `.env` with ngrok URL + API keys
- [ ] `WORKER_DRY_RUN=false`
- [ ] Real job completes with PDF + Excel
- [ ] Files appear in S3
- [ ] `GET /jobs/{id}/files` + download URL works

### Production (Phase E)

- [ ] Linux EC2 for API + DB (or RDS)
- [ ] Windows EC2 worker in same VPC
- [ ] Domain + SSL
- [ ] No ngrok
- [ ] Secrets in AWS Secrets Manager
- [ ] Stripe live mode + webhooks

---

## Related docs

- `backend/README.md` — API quick reference
- `worker/README.md` — Worker quick reference
- `db/README.md` — Database schema
- `docs/pm/PROJECT_REPORT.md` — Project status for PM/client
- `infra/secrets.md` — Secrets Manager plan
