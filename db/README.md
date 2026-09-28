## Database setup

### 1) Start PostgreSQL locally (example with Docker)

```bash
docker run --name snapshot-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=snapshot \
  -p 5432:5432 \
  -d postgres:16
```

### 2) Apply schema

```bash
psql postgresql://postgres:postgres@localhost:5432/snapshot -f db/schema.sql
```

### Tables
- `users`, `subscriptions` — auth + Stripe billing
- `password_reset_tokens` — forgot-password flow
- `jobs` — automation runs (status + inputs JSON)
- `output_rows` — cumulative per-user dataframe rows
- `job_files` — PDF/Excel metadata (S3 keys)
- `logs` — job/user logs

### Migrations (existing DBs)

If the database was created before password reset:

```bash
psql "$DATABASE_URL" -f db/migrations/001_password_reset_tokens.sql
```
