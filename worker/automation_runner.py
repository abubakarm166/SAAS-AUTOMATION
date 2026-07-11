"""
Run SnapShot automation on Windows EC2 from a claimed job payload.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from worker.api_client import load_worker_env
from worker.config import get_third_party_config

REPO_ROOT = Path(__file__).resolve().parents[1]


def _apply_api_keys() -> None:
    """Load third-party API keys into the environment for the legacy pipeline."""
    for key, value in get_third_party_config().items():
        if key.endswith("_API_KEY") and value:
            os.environ[key] = value
        if key.startswith("SMTP_") and value:
            os.environ[key] = str(value)


def run_automation(job: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """
    Execute the legacy headless pipeline in an isolated subprocess.

    Returns output_rows and file metadata for the worker complete endpoint.
    """
    load_worker_env()
    _apply_api_keys()

    inputs = job.get("inputs", {})
    addresses = inputs.get("addresses", [])
    if not addresses:
        raise ValueError("Job inputs.addresses must contain at least one address")

    recipient = inputs.get("recipient_email")
    skip_email = os.getenv("SNAPSHOT_SKIP_EMAIL", "").lower() == "true"
    if skip_email:
        pass
    elif recipient:
        os.environ["SNAPSHOT_SKIP_EMAIL"] = "false"
    else:
        os.environ.setdefault("SNAPSHOT_SKIP_EMAIL", "true")

    work_base = os.getenv("SNAPSHOT_WORK_DIR")
    work_dir = tempfile.mkdtemp(prefix="snapshot-job-", dir=work_base or None)
    config = {
        "work_dir": work_dir,
        "source_url": job.get("source_url"),
        "inputs": inputs,
    }
    config_path = Path(work_dir) / "job.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    env = os.environ.copy()
    env["SNAPSHOT_JOB_CONFIG"] = str(config_path)
    env["PYTHONPATH"] = os.pathsep.join(
        p for p in (str(REPO_ROOT), env.get("PYTHONPATH", "")) if p
    )

    completed = subprocess.run(
        [sys.executable, "-m", "worker.legacy.headless_main", str(config_path)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=int(os.getenv("SNAPSHOT_JOB_TIMEOUT_SECONDS", "3600")),
        check=False,
    )

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "headless automation failed").strip()
        raise RuntimeError(detail[-4000:])

    output_path = Path(work_dir) / "output.json"
    if not output_path.exists():
        raise RuntimeError("Headless automation finished without output.json")

    with output_path.open(encoding="utf-8") as handle:
        output = json.load(handle)

    rows = output.get("rows", [])
    files = output.get("files", [])
    if not rows:
        raise RuntimeError("Automation produced no output rows")

    return rows, files
