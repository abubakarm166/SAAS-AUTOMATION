import time

from worker.api_client import WorkerApiClient, load_worker_env, poll_interval_seconds
from worker.job_runner import execute_claimed_job, fail_claimed_job


def run_once(client: WorkerApiClient) -> bool:
    try:
        job = client.claim_next_job()
    except Exception as exc:
        print(f"Claim failed: {exc}")
        return False

    if not job:
        return False

    job_id = str(job["id"])
    print(f"Processing job {job_id} ...")

    try:
        result = execute_claimed_job(client, job)
        print(f"Job {job_id} completed with status={result.get('status')}")
    except Exception as exc:
        fail_claimed_job(client, job_id, str(exc))
        print(f"Job {job_id} failed: {exc}")

    return True


def main() -> None:
    load_worker_env()
    client = WorkerApiClient()
    interval = poll_interval_seconds()
    key_hint = f"...{client.api_key[-8:]}" if len(client.api_key) >= 8 else "(short)"
    print(f"Poll worker started. API={client.base_url} key={key_hint} poll={interval}s")
    print("Tip: set CELERY_BROKER_URL and run Celery worker instead for production.")

    while True:
        processed = run_once(client)
        if not processed:
            time.sleep(interval)


if __name__ == "__main__":
    main()
