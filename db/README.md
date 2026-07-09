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
- `jobs` — automation runs (status + inputs JSON)
- `output_rows` — cumulative per-user dataframe rows
- `job_files` — PDF/Excel metadata (S3 keys in Phase 2)
- `logs` — job/user logs
