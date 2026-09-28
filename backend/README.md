## SnapShot Backend (FastAPI)

### Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

Copy env vars from `backend/.env.example` into `backend/.env`.

CORS for the Next.js dashboard (in `backend/.env`):

```env
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Apply database schema first: see `db/README.md`.

### Stripe (keys → restart → works)

Set in `backend/.env`:

```env
STRIPE_SECRET_KEY=sk_live_...   # or sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
BYPASS_SUBSCRIPTION_CHECK=false
FRONTEND_URL=https://your-dashboard-domain
```

Also activate **Customer Portal** once in Stripe Dashboard → Settings → Billing → Customer portal.

Webhook URL: `https://your-api-domain/billing/webhook`  
Events: `checkout.session.completed`, `customer.subscription.*`, `invoice.paid`, `invoice.payment_failed`

### Password reset email

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=...
SMTP_PASSWORD=...   # app password
SMTP_FROM=...
```

### Run

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints
- `GET /health`
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `GET /auth/me`
- `POST /jobs` (requires active subscription)
- `POST /jobs/{job_id}/retry` (failed jobs only)
- `GET /jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/files`
- `GET /jobs/{job_id}/files/{file_id}/download` (presigned S3 URL)
- `GET /billing/config`
- `GET /billing/subscription`
- `POST /billing/checkout-session`
- `POST /billing/portal-session`
- `POST /billing/sync`
- `POST /billing/webhook`
- `POST /worker/jobs/claim` (worker key)
- `POST /worker/jobs/{id}/complete` (worker key)
- `POST /worker/jobs/{id}/fail` (worker key)
