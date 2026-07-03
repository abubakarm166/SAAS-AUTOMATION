## secrets/

This folder contains **sensitive material** (API keys, passwords, cloud credentials).

- Do **not** commit anything here.
- Rotate keys if they were shared in plaintext.
- Long-term, move all secrets to **AWS Secrets Manager** and remove local copies.

