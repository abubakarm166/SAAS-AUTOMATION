# SnapShot SaaS — Project Status Report

> **Living document** — update this file after each milestone, client delivery, or blockers change.  
> **Last updated:** 2026-07-02  
> **Project:** Dextersol / Hatem — Cloud-Hosted Automation SaaS Platform  
> **Product name (in code):** SnapShot Property Report  
> **Current phase:** Phase 1 — Pre-development / Kickoff  
> **Overall status:** 🟡 Onboarding — awaiting final client confirmations to begin build

---

## 1. Executive Summary

The client (Hatem) has a working **Windows desktop automation tool** that analyzes real estate auction listings. It captures property addresses from Chrome, enriches them with RentCast and mortgage data, runs investment calculations, generates PDF reports + Excel, and emails results.

**Our job:** Wrap this tool in a multi-user SaaS product — auth, Stripe payments, cloud Windows workers, Chrome extension, web dashboard, and admin panel. **We are not rewriting the core automation logic.**

Development has **not started yet**. Discovery and onboarding are largely complete. Stripe access is now available to the dev team.

---

## 2. Project Goals

| Goal | Description |
|------|-------------|
| Commercial SaaS | Sell subscriptions to multiple paying users |
| Cloud execution | Run automation on AWS Windows EC2 (not user's local PC) |
| Chrome extension | Users trigger jobs from their browser (Manifest V3) |
| Web dashboard | Session history, cumulative data, charts, downloads |
| Payments | Stripe subscriptions gate access to automation |
| Security | All API keys in AWS Secrets Manager — never in code or extension |

---

## 3. What the Automation Does

### High-level flow

```
Chrome tab (auction listing page)
    → Read URL + page text + screenshot OCR
    → User confirms addresses + financial inputs
    → RentCast APIs (property, value, rent, market stats)
    → API Ninjas mortgage rates
    → Pandas calculations (cap rate, DSCR, BRRRR scores, etc.)
    → PDF per property + Excel summary
    → Google Street View image in PDF
    → Email PDFs + Excel to recipient
```

### Sample target URLs (from client)

- https://www.ashlandauction.com/auctions/33350
- https://www.ashlandauction.com/auctions/33872

### User inputs (replacing tkinter popups in SaaS)

**Window 1 — Addresses:** Auto-detected, user can edit/add/remove.

**Window 2 — Financial inputs:**

| Field | Default |
|-------|---------|
| Recipient Email | (empty) |
| Interest Rate | 0.06 |
| Loan Length (Years) | 30 |
| Discount Percentage | 0.25 |
| Closing Costs % | 0.04 |
| Money Down % | 0.20 |
| Operating Expenses % | 0.02 |
| Additional Income | 0 |
| Vacancy Allowance % | 0.05 |
| Lender LTV Ratio | 0.75 |
| Rehab Costs % | 0.25 |
| Refi Loan Amount % | 0.50 |
| Refi Closing Costs % | 0.04 |
| Months Holding Property | 3 |

### APIs integrated

| API | Endpoints used | Status |
|-----|----------------|--------|
| RentCast | Property Records, Value Estimate, Rent Estimate, Market Statistics | Keys received |
| API Ninjas | Mortgage Rate (`/v1/mortgagerate` in code) | Keys received |
| Google Maps | Street View Static API | Keys received |
| Gmail SMTP | `smtp.gmail.com:465` | Credentials in source — must move to Secrets Manager |

---

## 4. Technology Stack (Agreed)

| Layer | Technology |
|-------|------------|
| Frontend dashboard | React / Next.js |
| Backend API | Python FastAPI |
| Database | PostgreSQL |
| Cloud workers | AWS Windows EC2 |
| File storage | AWS S3 |
| Job queue | Redis + Celery |
| Secrets | AWS Secrets Manager |
| Payments | Stripe |
| Email (production) | AWS SES recommended; Gmail SMTP as fallback |
| Browser extension | Chrome Manifest V3 |
| Analytics | Power BI embed + custom charts/tables |
| OCR | Tesseract (on EC2 image) |

---

## 5. Phase Plan & Status

### Phase 1 — Backend Foundation + EC2 Spike

| Task | Status | Notes |
|------|--------|-------|
| Receive Python source | ✅ Done | `address_capture_v1.58.py` (2,627 lines) |
| Receive API keys & sample URLs | ✅ Done | Documented in `information` |
| Receive tkinter field mapping | ✅ Done | Documented in `information` |
| AWS console access | ✅ Done | IAM user created |
| Stripe access | ✅ Done | Dev team logged in (2026-07-01) |
| FastAPI backend + auth | ⬜ Not started | |
| PostgreSQL schema | ⬜ Not started | |
| Stripe integration | ⬜ Not started | |
| Script refactor (split at line 484) | ⬜ Not started | |
| Secrets → AWS Secrets Manager | ⬜ Not started | |
| EC2 spike (1 job on 1 Windows instance) | ⬜ Not started | **Critical de-risk step** |

**Phase 1 deliverable:** Working backend with auth + payments, demonstrable via API. No dashboard UI yet.

---

### Phase 2 — Cloud Automation Core

| Task | Status | Notes |
|------|--------|-------|
| Migrate script to Windows EC2 workers | ⬜ Not started | Highest technical risk |
| Redis + Celery job queue | ⬜ Not started | |
| S3 storage for PDFs/Excel | ⬜ Not started | |
| Replace tkinter with API parameters | ⬜ Not started | |
| Job timeouts, retries, crash recovery | ⬜ Not started | |
| Email via SES or Gmail | ⬜ Blocked | Awaiting client decision |

**Phase 2 deliverable:** Automation runs in AWS; jobs triggered via API produce same outputs as local exe.

---

### Phase 3 — Extension, Dashboard & Launch

| Task | Status | Notes |
|------|--------|-------|
| Chrome extension (Manifest V3) | ⬜ Not started | |
| React/Next.js dashboard | ⬜ Not started | |
| Power BI embedding | ⬜ Blocked | Awaiting client license |
| Admin panel | ⬜ Not started | |
| Production deployment | ⬜ Not started | |
| Branding | ⬜ Blocked | Logo, colors, name |
| Chrome Web Store decision | ⬜ Blocked | Public vs private distribution |

**Phase 3 deliverable:** Full live product — sign up, subscribe, extension, dashboard, admin.

---

## 6. Assets Received from Client

| Asset | File / Location | Date received |
|-------|-----------------|---------------|
| Build guide | `Dextersol_Developer_Build_Guide.docx` | 2026-06-11 |
| Packaged executable | `Snapshot/Snapshot.exe` | 2026-06-11 |
| Python source | `address_capture_v1.58.py` | 2026-06-29 |
| API keys, URLs, input fields | `information` | 2026-06-29 |
| AWS IAM credentials | `Abubakar_Mahmood_credentials.csv` | 2026-06-29 |

---

## 7. Pending from Client

| # | Item | Phase | Priority | Status |
|---|------|-------|----------|--------|
| 1 | Confirm where to start (Phase 1 kickoff approval) | 1 | 🔴 High | Awaiting reply |
| 2 | Email setup decision — Gmail SMTP vs AWS SES | 2 | 🔴 High | Awaiting reply |
| 3 | Stripe subscription plans (tiers, monthly/yearly pricing) | 1 | 🔴 High | Awaiting reply |
| 4 | Confirm AWS IAM permissions (EC2, S3, Secrets Manager) | 1 | 🟡 Medium | Partial — verify scope |
| 5 | Rotate API keys after Secrets Manager setup | 1 | 🟡 Medium | After migration |
| 6 | Branding (logo, colors, platform name) | 3 | 🟢 Low | Not yet needed |
| 7 | Power BI licensing | 3 | 🟢 Low | Not yet needed |
| 8 | Chrome Web Store publishing decision | 3 | 🟢 Low | Not yet needed |

---

## 8. Team Access Status

| System | Access | Notes |
|--------|--------|-------|
| AWS Console | ✅ Yes | User: Abubakar_Mahmood |
| Stripe Dashboard | ✅ Yes | Logged in 2026-07-01 |
| RentCast API | ✅ Keys received | Move to Secrets Manager |
| API Ninjas API | ✅ Keys received | Move to Secrets Manager |
| Google Maps API | ✅ Keys received | Move to Secrets Manager |
| Gmail SMTP | ⚠️ In source code | Must secure + rotate |

---

## 9. Technical Findings & Risks

### Risks (from build guide + code review)

| Risk | Severity | Mitigation |
|------|----------|------------|
| GUI automation on Windows EC2 | 🔴 High | EC2 spike in first week of Phase 1 |
| Worker orchestration (freezes/crashes) | 🔴 High | Celery timeouts, retries, session isolation |
| Chrome extension + Web Store review | 🟡 Medium | Start extension early in Phase 3 |
| RentCast rate limits (20 req/sec) | 🟡 Medium | Queue throttling per job |
| Secrets exposed in source files | 🔴 High | Migrate to Secrets Manager immediately in Phase 1 |

### Code issues found (pre-migration)

| Issue | Location | Action |
|-------|----------|--------|
| Monolithic 2,627-line script | `address_capture_v1.58.py` | Refactor into modules at line 484 split |
| Hardcoded API keys + Gmail password | `.py` + `information` | Remove; use Secrets Manager |
| Windows-only paths (Tesseract, pywinauto) | `.py` line 217+ | Configure on EC2 image |
| `num_months_holding` not saved on submit | `.py` submit() | Fix during refactor |
| API Ninjas v1 in code vs v2 in docs | `.py` line 934 | Test and align endpoint |
| Excel attachment MIME type set as `pdf` | `.py` line 2615-2619 | Fix during refactor |

---

## 10. Recommended Start Order

Once client confirms kickoff:

```
Week 1
  ├── Set up repo + dev environment
  ├── FastAPI skeleton + PostgreSQL schema
  ├── Move secrets to AWS Secrets Manager
  └── EC2 spike: 1 Windows instance, 1 end-to-end job

Week 2–3
  ├── Auth (signup, login, JWT, email verify)
  ├── Stripe checkout + webhooks + subscription gating
  └── Refactor address_capture into worker modules

Week 4+
  └── Phase 2: Celery queue, S3, production workers
```

---

## 11. Scope Guardrails (Do Not Creep)

- MVP caps concurrent workers — **not** 1,000 simultaneous jobs
- Ongoing maintenance, high-concurrency scaling, Power BI licensing = separate paid items
- New client requests outside agreed scope = change request

---

## 12. Cost Responsibilities (Client Side)

- AWS infrastructure (EC2, S3, Secrets Manager, data transfer)
- Power BI licensing
- Stripe transaction fees
- Third-party API usage (RentCast, API Ninjas, Google Maps)

---

## 13. Update Log

> Add a new entry at the **top** of this section after each project update.

### 2026-07-01 — Onboarding progress

- **Done:** Stripe dashboard access obtained by dev team
- **Done:** Deep code review of `address_capture_v1.58.py` completed
- **Done:** Client delivered source, API keys, sample URLs, tkinter field mapping
- **Done:** AWS console login received
- **Done:** This project report created
- **Blocked:** Awaiting client confirmation on email setup (Gmail vs SES)
- **Blocked:** Awaiting Stripe subscription plan details
- **Blocked:** Awaiting client approval to begin Phase 1 build
- **Next:** Send client kickoff message; begin repo setup once approved

### 2026-07-02 — Phase 1 workspace + secrets baseline

- **Done:** Created Phase 1 repo folder structure (`backend/`, `db/`, `worker/`, `infra/`, `docs/`)
- **Done:** Organized received artifacts into folders (`docs/`, `worker/legacy/`, `artifacts/`, `secrets/`)
- **Done:** Added `.env.example` and secrets runbook (`infra/secrets.md`)
- **Next:** Create AWS Secrets Manager secret `snapshot/prod/third_party` and move runtime to use it (no hardcoded keys)

### 2026-06-29 — Client deliverables received

- Received Python source (`address_capture_v1.58.py`)
- Received `information` file with API keys, sample URLs, input fields
- Received AWS credentials CSV

### 2026-06-11 — Project intake

- Received `Dextersol_Developer_Build_Guide.docx`
- Received `Snapshot.exe` (packaged executable)
- Initial scope and phase plan documented

---

## 14. Open Questions for Client

1. **Where should we start?** — Confirm Phase 1 kickoff approval
2. **Email:** Keep Gmail SMTP or switch to AWS SES for production?
3. **Stripe plans:** What subscription tiers and pricing (monthly/yearly)?
4. **AWS IAM:** Can you confirm our user has EC2, S3, and Secrets Manager permissions?
5. **MVP worker cap:** How many concurrent automation jobs should MVP support?

---

## 15. Contacts & References

| Role | Name | Notes |
|------|------|-------|
| Client | Hatem | Product owner |
| Dev agency | Dextersol | Build guide author |
| Dev team | Abubakar Mahmood | AWS + Stripe access |

**Key files in repo:**

| File | Purpose |
|------|---------|
| `Dextersol_Developer_Build_Guide.docx` | Full build specification |
| `address_capture_v1.58.py` | Client automation source |
| `information` | Client-provided API/URL/input details |
| `PROJECT_REPORT.md` | This living status report |

---

*End of report — update Section 13 (Update Log) and Section 5 (Phase status tables) after each milestone.*
