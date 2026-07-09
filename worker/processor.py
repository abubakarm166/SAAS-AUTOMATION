import os
import platform
from typing import Any


def process_job(job: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """
    Run automation for a claimed job.

    - Linux/dev: WORKER_DRY_RUN=true simulates success.
    - Windows EC2: runs legacy headless pipeline via automation_runner.
    """
    inputs = job.get("inputs", {})
    addresses = inputs.get("addresses", [])
    dry_run = os.getenv("WORKER_DRY_RUN", "false").lower() == "true"
    is_windows = platform.system().lower() == "windows"

    if dry_run or not is_windows:
        rows = []
        for address in addresses:
            rows.append(
                {
                    "address": address,
                    "source_url": job.get("source_url"),
                    "status": "simulated",
                    "note": "Dry run — set WORKER_DRY_RUN=false on Windows EC2 for real automation",
                }
            )
        files = [
            {
                "file_type": "pdf",
                "filename": f"{addresses[0]} Property Report.pdf" if addresses else "report.pdf",
                "s3_key": None,
            },
            {
                "file_type": "xlsx",
                "filename": "Listings Report Data.xlsx",
                "s3_key": None,
            },
        ]
        return rows, files

    from worker.automation_runner import run_automation

    return run_automation(job)
