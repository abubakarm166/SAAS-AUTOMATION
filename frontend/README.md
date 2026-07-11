## SnapShot Web Dashboard (Next.js)

User-facing UI for Phase 3: login, jobs, downloads, and Stripe billing.

### Requirements

- **Node.js 20.9+** (Next.js 16 does not run on Node 18)
- Check: `node -v`

If you see `You are using Node.js 18.x` when running `npm run build`, upgrade Node first (see below).

### Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit NEXT_PUBLIC_API_URL to your API (local or EC2)
npm run dev
```

Open http://localhost:3000

### Upgrade Node.js (Ubuntu / Linux)

**Option A — nvm (recommended)**

```bash
# Install nvm if needed
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc

cd frontend
nvm install    # reads .nvmrc (Node 20)
nvm use
node -v        # should show v20.x or v22.x
```

**Option B — NodeSource (system-wide)**

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
```

Then reinstall deps and run:

```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Backend requirements

The API must allow CORS from the dashboard origin. In `backend/.env`:

```env
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

For production dashboard URL, add it to `CORS_ORIGINS` and set `FRONTEND_URL` for Stripe redirect URLs.

Restart API after changes: `sudo systemctl restart snapshot-api`

### Pages

| Route | Purpose |
|-------|---------|
| `/login` | Sign in |
| `/signup` | Register |
| `/dashboard` | Job list |
| `/jobs/new` | Create job |
| `/jobs/[id]` | Job detail + downloads |
| `/billing` | Subscription status + Stripe checkout |
| `/billing/success` | Post-checkout redirect |
| `/billing/cancel` | Checkout cancelled |

### Production deploy

#### Option A — Vercel (recommended)

1. Push repo to GitHub
2. Import project in [Vercel](https://vercel.com) — root directory: `frontend`
3. Environment variable: `NEXT_PUBLIC_API_URL=https://your-api-host:8000`
4. Deploy
5. On API EC2 `backend/.env`:
   ```env
   FRONTEND_URL=https://your-app.vercel.app
   CORS_ORIGINS=https://your-app.vercel.app
   ```
6. `sudo systemctl restart snapshot-api`

#### Option B — Same Linux EC2 (nginx)

Build and run on the API server:

```bash
cd frontend
npm run build
npm run start   # port 3000
```

Or use the systemd unit in `infra/snapshot-dashboard.service`.

Nginx config: `infra/nginx-snapshot.conf` — serves dashboard on `/` and proxies `/api` or use separate ports.

Update `backend/.env`:

```env
FRONTEND_URL=http://16.170.241.9
CORS_ORIGINS=http://16.170.241.9,http://16.170.241.9:3000
```

Open security group port 3000 (or 80/443 via nginx).

### Stripe

Checkout success/cancel URLs use `FRONTEND_URL` from the backend:

- `{FRONTEND_URL}/billing/success`
- `{FRONTEND_URL}/billing/cancel`

Ensure Stripe webhook points to `{API_URL}/billing/webhook`.
