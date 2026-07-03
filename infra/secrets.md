## Secrets & Credentials (Phase 1 baseline)

### Goal
Keep **all secrets out of code** and out of the Chrome extension.

During Phase 1 (local dev), code may read secrets from environment variables.
For cloud environments (Windows EC2 workers, backend), secrets must live in **AWS Secrets Manager**
and be accessed via **IAM roles**.

---

## Source of truth

### Recommended AWS Secrets Manager structure (single JSON secret)

- **Secret name**: `snapshot/prod/third_party`
- **Secret value** (JSON):

```json
{
  "RENTCAST_API_KEY": "...",
  "API_NINJAS_API_KEY": "...",
  "GOOGLE_MAPS_API_KEY": "...",
  "SMTP_HOST": "smtp.gmail.com",
  "SMTP_PORT": "465",
  "SMTP_USERNAME": "...",
  "SMTP_PASSWORD": "..."
}
```

Notes:
- We use **one JSON secret** so rotation and permissions stay simple.
- For non-prod, use a separate secret like `snapshot/dev/third_party`.

---

## Environment variables (local dev)

See `.env.example` for the list of required variables.

Minimum required to run the automation logic:
- `RENTCAST_API_KEY`
- `API_NINJAS_API_KEY`
- `GOOGLE_MAPS_API_KEY`
- SMTP variables (until we switch to SES)

---

## IAM permissions (workers/backend)

The runtime role (EC2 instance role) will need:
- `secretsmanager:GetSecretValue`
- `kms:Decrypt` (only if using a custom KMS key)

---

## Rotation policy

Because API keys and SMTP credentials were previously shared in plaintext, plan to:
- migrate secrets into AWS Secrets Manager
- then **rotate** keys/passwords
- update Secrets Manager values (no code change)

