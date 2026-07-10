# SnapShot SaaS — Project Status Report

> **Living document** — update Section 13 (Update Log) and Section 5 (Phase tables) after each milestone.  
> **Last updated:** 2026-07-10  
> **Project:** Dextersol / Hatem — Cloud-Hosted Automation SaaS Platform  
> **Product name (in code):** SnapShot Property Report  
> **Current phase:** Phase 2 — Cloud Automation Core (early)  
> **Overall status:** 🟢 Major milestone — end-to-end cloud automation verified on Windows EC2

---

## 1. Executive Summary (for PM / client)

We have successfully wrapped the client's Windows automation in a **multi-user SaaS backend** and proven that **real property reports** (PDF + Excel) can be generated on **AWS Windows EC2** when triggered via API — without Chrome capture or tkinter on the worker.

**What works today (demonstrable):**
- User signup/login (JWT)
- Job creation via API (addresses + financial inputs as JSON)
- Windows EC2 worker polls API, claims job, runs headless automation
- RentCast + API Ninjas + Google Street View + calculations + PDF/Excel
- Job status returns `completed` with output row data in database

**What does not exist yet:**
- No web dashboard or Chrome extension
- No S3 file downloads via API (files land in temp folder on EC2 only)
- API still runs on dev laptop + ngrok (not production AWS)
- Email delivery not wired in cloud
- Subscription webhooks need production hardening

**Bottom line for client:** The hardest technical risk (running automation in the cloud) is **proven**. Next work is storage, production hosting, and user-facing UI.

---

## 2. Demonstrable Results (with evidence)

### 2.1 End-to-end API flow (local dev + ngrok)

| Step | Result | How verified |
|------|--------|--------------|
| `POST /auth/signup` + `POST /auth/login` | ✅ Works | Postman — JWT returned |
| `POST /jobs` (with Bearer token) | ✅ Works | Job created with `status: queued` |
| Worker claims job | ✅ Works | `POST /worker/jobs/claim` → 200 |
| Worker completes job | ✅ Works | `POST /worker/jobs/{id}/complete` → 200 |
| `GET /jobs/{id}` | ✅ Works | `status: completed`, timestamps set |

**Sample completed job:** `57d00746-7c36-412d-bfc2-a9965b396884` (2026-07-09)

### 2.2 Windows EC2 headless automation (Phase 2 milestone)

| Test | Address | Result |
|------|---------|--------|
| Dry-run (Linux) | Any | ✅ Simulated completion ~50ms |
| Real automation (EC2) | `123 Main St, Richmond, KY 40475` | ✅ Completed (~7s) |
| Real automation (EC2) | `2202 Clifton Ave, Baltimore, MD 21216` | ✅ Completed — PDF + Excel verified |

**Validated outputs on EC2:**
- `{address} Property Report.pdf` — property report with Street View, calculations, charts
- `Listings Report Data.xlsx` — summary spreadsheet (same as desktop tool)

**Test auction URL used:** https://www.ashlandauction.com/auctions/33350

### 2.3 Earlier EC2 spike (manual / GUI mode)

| Item | Result |
|------|--------|
| Chrome URL + OCR address capture | ✅ Works |
| Tkinter confirm + inputs | ✅ Works |
| RentCast + PDF + Excel | ✅ Works |
| Email from EC2 (Gmail SMTP) | ❌ Failed — deferred (client decision: Gmail vs SES) |

### 2.4 Stripe billing (test mode)

| Item | Result |
|------|--------|
| Checkout session creation | ✅ Works |
| Stripe CLI webhooks | ✅ Configured |
| Subscription status auto-update | 🟡 Partial — manual SQL used for dev; webhooks need prod hardening |
| Dev bypass for job creation | ✅ `BYPASS_SUBSCRIPTION_CHECK=true` in local `.env` |

---

## 3. Current Architecture (dev environment)

```
┌─────────────────┐     ngrok      ┌──────────────────┐     HTTPS      ┌─────────────────────┐
│  Linux dev PC   │ ──────────────►│  ngrok tunnel    │◄───────────────│  Windows EC2        │
│  PostgreSQL     │                │                  │                │  worker/runner.py   │
│  FastAPI :8000  │                │                  │                │  headless automation│
└─────────────────┘                └──────────────────┘                └─────────────────────┘
        ▲                                                                         │
        │ Postman / future UI                                                     ▼
   Developer testing                                                    Temp: PDF + Excel
                                                                        (S3 next)
```

**Important:** This is a **development** topology. Production will move API + DB to AWS and remove ngrok.

---

## 4. Project Goals

| Goal | Description | Status |
|------|-------------|--------|
| Commercial SaaS | Sell subscriptions to multiple paying users | 🟡 Backend only |
| Cloud execution | Run automation on AWS Windows EC2 | ✅ Proven |
| Chrome extension | Users trigger jobs from browser (MV3) | ⬜ Phase 3 |
| Web dashboard | Session history, charts, downloads | ⬜ Phase 3 |
| Payments | Stripe subscriptions gate access | 🟡 Test mode works |
| Security | API keys in Secrets Manager | ⬜ Still in `.env` |

---

## 5. Phase Plan & Status

### Phase 1 — Backend Foundation + EC2 Spike

| Task | Status | Notes |
|------|--------|-------|
| Receive Python source | ✅ Done | `worker/legacy/address_capture_v1.58.py` |
| Receive API keys & sample URLs | ✅ Done | `secrets/information` |
| AWS console access | ✅ Done | IAM user: Abubakar_Mahmood |
| Stripe access | ✅ Done | Test product ~$99/mo |
| FastAPI backend + auth | ✅ Done | signup, login, JWT, `/auth/me` |
| PostgreSQL schema | ✅ Done | `db/schema.sql` — users, jobs, subscriptions, job_files, output_rows, logs |
| Stripe checkout + webhooks | ✅ Done | Local test mode |
| Worker poll / claim / complete / fail | ✅ Done | Secured with `WORKER_API_KEY` |
| End-to-end dry-run (Linux) | ✅ Done | Full API → worker → completed |
| EC2 spike (GUI mode) | ✅ Done | PDF/Excel OK; email blocked |
| Secrets → AWS Secrets Manager | ⬜ Not started | Keys still in `.env` |
| Production subscription flow | 🟡 Partial | Bypass flag for dev testing |

**Phase 1 verdict:** ✅ **Complete** (API demonstrable via Postman; no UI)

---

### Phase 2 — Cloud Automation Core

| Task | Status | Notes |
|------|--------|-------|
| Headless worker (no tkinter) | ✅ Done | `worker/legacy/headless_main.py` |
| Job inputs from API JSON | ✅ Done | All financial fields mapped |
| Windows EC2 worker connected to API | ✅ Done | Via ngrok (dev) |
| Real PDF + Excel on EC2 | ✅ Done | Baltimore address verified |
| S3 bucket created | ✅ Done | `snapshot-reports-dev-cloud` (eu-north-1) |
| S3 upload from worker | ⬜ Not started | IAM role setup in progress |
| API download endpoint (presigned URL) | ⬜ Not started | After S3 upload |
| Deploy API on AWS Linux EC2 | ⬜ Not started | Replace ngrok |
| Redis + Celery job queue | ⬜ Not started | |
| Job timeouts, retries, crash recovery | ⬜ Not started | |
| Email (SES or Gmail) | ⬜ Blocked | Awaiting client decision |
| API keys → Secrets Manager | ⬜ Not started | |

**Phase 2 verdict:** 🟡 **~40% complete** — automation proven; storage + production hosting next

---

### Phase 3 — Extension, Dashboard & Launch

| Task | Status | Notes |
|------|--------|-------|
| Chrome extension (Manifest V3) | ⬜ Not started | |
| React/Next.js dashboard | ⬜ Not started | |
| Power BI embedding | ⬜ Blocked | Awaiting client license |
| Admin panel | ⬜ Not started | |
| Production deployment + domain + SSL | ⬜ Not started | |
| Branding | ⬜ Blocked | Logo, colors, name |
| Chrome Web Store decision | ⬜ Blocked | Public vs private |

**Phase 3 verdict:** ⬜ **Not started**

---

## 6. What We Built (code inventory)

| Component | Location | Purpose |
|-----------|----------|---------|
| FastAPI app | `backend/app/` | Auth, jobs, billing, worker endpoints |
| DB schema | `db/schema.sql` | PostgreSQL tables |
| Worker runner | `worker/runner.py` | Poll API, process jobs |
| Worker API client | `worker/api_client.py` | Claim/complete/fail + ngrok header |
| Headless automation | `worker/legacy/headless_main.py` | Runs legacy pipeline from JSON |
| Automation runner | `worker/automation_runner.py` | Subprocess wrapper for EC2 |
| Legacy script | `worker/legacy/address_capture_v1.58.py` | Original automation (patched for SaaS) |
| PM report | `docs/pm/PROJECT_REPORT.md` | This document |

### Key API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/auth/signup` | Register user |
| POST | `/auth/login` | Get JWT |
| GET | `/auth/me` | Current user |
| POST | `/jobs` | Create job (subscription or dev bypass) |
| GET | `/jobs` | List jobs |
| GET | `/jobs/{id}` | Job status + details |
| POST | `/billing/checkout-session` | Stripe checkout |
| POST | `/billing/webhook` | Stripe events |
| POST | `/worker/jobs/claim` | Worker claims next queued job |
| POST | `/worker/jobs/{id}/complete` | Worker reports success |
| POST | `/worker/jobs/{id}/fail` | Worker reports failure |

---

## 7. Bugs Fixed During Development

| Issue | Fix |
|-------|-----|
| Worker 401 Unauthorized | Synced `WORKER_API_KEY`; restart API after `.env` change |
| Postgres connection refused | `podman start snapshot-postgres` |
| EC2 can't reach local API | ngrok tunnel + `API_BASE_URL` |
| ngrok browser warning blocks API | `ngrok-skip-browser-warning` header |
| `KeyError: 1` on single address | Removed debug lines in legacy script (`[1]` index) |
| Zip_Response None crash | Patched legacy script (earlier EC2 spike) |
| pandas dict `.loc` assignment | Patched to `.at[]` (earlier EC2 spike) |
| Empty bar chart crash | Skip chart when no data (earlier EC2 spike) |
| `num_months_holding` not saved in tkinter | ⬜ Not fixed (headless uses API JSON — OK for SaaS) |

---

## 8. Pending from Client

| # | Item | Phase | Priority | Status |
|---|------|-------|----------|--------|
| 1 | Email: Gmail SMTP vs AWS SES | 2 | 🔴 High | Awaiting reply |
| 2 | Stripe plan confirmation (pricing tiers) | 1 | 🔴 High | Test $99/mo exists |
| 3 | IAM: confirm EC2/S3/Secrets Manager scope | 2 | 🟡 Medium | S3 bucket created; role attach in progress |
| 4 | API key rotation after Secrets Manager | 2 | 🟡 Medium | After migration |
| 5 | Branding (logo, colors, name) | 3 | 🟢 Low | |
| 6 | Power BI licensing | 3 | 🟢 Low | |
| 7 | Chrome Web Store public vs private | 3 | 🟢 Low | |

---

## 9. What's Left — Recommended Order

### Immediate (this week)
1. **Finish IAM role** on Windows EC2 → verify S3 upload test (`SUCCESS`)
2. **Implement S3 upload** in worker + presigned download in API
3. Set `SNAPSHOT_WORK_DIR=C:\snapshot\output` on EC2 for easier file inspection

### Short term (next 2–3 weeks)
4. **Deploy API + Postgres** on Linux EC2 (same VPC as Windows worker)
5. Remove ngrok dependency
6. Stripe webhook hardening — subscriptions auto-activate
7. Migrate secrets to **AWS Secrets Manager**

### Medium term
8. **Redis + Celery** — proper job queue, retries, timeouts
9. **Email** — once client chooses Gmail vs SES
10. Chrome extension + React dashboard (Phase 3)

---

## 10. Technical Risks (updated)

| Risk | Severity | Status |
|------|----------|--------|
| GUI automation on Windows EC2 | 🔴 High | ✅ Mitigated — headless mode works |
| Worker orchestration (crashes) | 🔴 High | 🟡 Basic poll only; Celery pending |
| Secrets in source / `.env` | 🔴 High | ⬜ Not migrated yet |
| ngrok URL changes on restart | 🟡 Medium | Dev only — replace with AWS deploy |
| RentCast rate limits | 🟡 Medium | Not hit yet in testing |
| Email from EC2 | 🟡 Medium | Blocked — needs SES or client Gmail approval |
| IAM role attach on Windows EC2 | 🟡 Medium | In progress — metadata 404 = no role attached |

---

## 11. Cost Responsibilities (Client)

- AWS: EC2 Windows (worker), future Linux EC2 (API), S3, Secrets Manager, data transfer
- Stripe transaction fees
- Third-party APIs: RentCast, API Ninjas, Google Maps
- Power BI license (Phase 3)
- Chrome Web Store fee if public listing (Phase 3)

---

## 12. Update Log

> Add new entries at the **top**.

### 2026-07-10 — Phase 2 milestone: EC2 headless automation end-to-end

- **Done:** Windows EC2 worker connects to API via ngrok
- **Done:** Real job completed with `2202 Clifton Ave, Baltimore, MD 21216` — PDF + Excel verified
- **Done:** Headless pipeline (`headless_main.py`) — no Chrome/tkinter on worker
- **Done:** S3 bucket created: `snapshot-reports-dev-cloud` (eu-north-1)
- **In progress:** IAM role `SnapshotWindowsWorkerRole` for EC2 → S3 (metadata 404 — role attach pending)
- **Blocked:** S3 upload code not implemented yet
- **Next:** Attach IAM role → S3 upload → API download endpoint → deploy API on AWS

### 2026-07-09 — Worker integration + subscription bypass

- **Done:** Full dry-run flow: create job → worker → `completed`
- **Done:** Dev subscription bypass (`BYPASS_SUBSCRIPTION_CHECK`)
- **Done:** Worker env loading from `.env`; ngrok support
- **Done:** Fixed debug line crash (`KeyError: 1`) for single-address jobs
- **Failed then fixed:** Worker API key mismatch (API restart required after `.env` change)

### 2026-07-08 — Backend foundation

- **Done:** FastAPI auth, jobs, Stripe, worker endpoints
- **Done:** PostgreSQL schema applied locally
- **Done:** Worker scaffold with dry-run mode

### 2026-07-04 — EC2 spike (GUI mode)

- **Done:** Automation runs on Windows Server 2022
- **Done:** PDF + Excel generated on cloud
- **Skipped:** Email from EC2 (Gmail SMTP refused)

### 2026-07-01 — Onboarding

- Stripe access, code review, AWS credentials, project report created

### 2026-06-29 — Client deliverables

- Python source, API keys, sample URLs, tkinter field mapping

---

## 13. PM Message Template (copy/paste)

**Subject:** SnapShot SaaS — Phase 2 milestone: cloud automation verified

Hi Hatem,

**Completed since last update:**
- Full API backend (auth, jobs, Stripe test mode, worker endpoints)
- End-to-end test: API job → Windows EC2 worker → completed status
- Real property report generated in the cloud (PDF + Excel) for Baltimore auction address
- Matches desktop tool output — without manual Chrome/tkinter on the worker

**Demonstrable today:** Postman → create job → worker processes → `status: completed`

**In progress:**
- S3 storage for report downloads (bucket created; IAM permissions being configured)
- Production API hosting on AWS (currently dev laptop + temporary tunnel)

**Blocked on client:**
- Email delivery: Gmail SMTP vs AWS SES?
- Final Stripe subscription pricing confirmation

**Next 2–3 weeks:**
- S3 uploads + download links
- API deployed on AWS (remove dev tunnel)
- Secrets Manager for API keys

Happy to demo the end-to-end flow on a call.

Best,  
[Your name]

---

## 14. Contacts & Key Files

| Role | Name |
|------|------|
| Client | Hatem |
| Dev agency | Dextersol |
| Dev team | Abubakar Mahmood |

| File | Purpose |
|------|---------|
| `docs/pm/PROJECT_REPORT.md` | This report |
| `docs/spec/Dextersol_Developer_Build_Guide.docx` | Build specification |
| `worker/legacy/address_capture_v1.58.py` | Automation source |
| `secrets/information` | Client API keys + field mapping |
| `db/schema.sql` | Database schema |

---

*End of report — update after each milestone.*
