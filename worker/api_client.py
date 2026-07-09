import os
from pathlib import Path
from typing import Any

import requests


def load_worker_env() -> None:
    """Load env vars from backend/.env then repo root .env (files override shell)."""
    root = Path(__file__).resolve().parents[1]
    for env_path in (root / "backend" / ".env", root / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ[key.strip()] = value.strip()


class WorkerApiClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("API_BASE_URL", "http://localhost:8000")).rstrip("/")
        self.api_key = api_key or os.getenv("WORKER_API_KEY", "")
        if not self.api_key:
            raise RuntimeError("WORKER_API_KEY is required")

    def _headers(self) -> dict[str, str]:
        return {"X-Worker-API-Key": self.api_key}

    def claim_next_job(self) -> dict[str, Any] | None:
        response = requests.post(f"{self.base_url}/worker/jobs/claim", headers=self._headers(), timeout=30)
        response.raise_for_status()
        data = response.json()
        return data if data else None

    def complete_job(self, job_id: str, output_rows: list[dict], files: list[dict] | None = None) -> dict[str, Any]:
        payload = {"output_rows": output_rows, "files": files or []}
        response = requests.post(
            f"{self.base_url}/worker/jobs/{job_id}/complete",
            json=payload,
            headers=self._headers(),
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def fail_job(self, job_id: str, error_message: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/worker/jobs/{job_id}/fail",
            json={"error_message": error_message},
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


def poll_interval_seconds() -> int:
    return int(os.getenv("WORKER_POLL_SECONDS", "5"))
