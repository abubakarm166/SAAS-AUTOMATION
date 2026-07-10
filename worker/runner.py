import os
import time

from worker.api_client import WorkerApiClient, load_worker_env, poll_interval_seconds
from worker.processor import process_job


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
        output_rows, files = process_job(job)
        from worker.s3_storage import s3_enabled, upload_job_files

        if s3_enabled():
            files = upload_job_files(job, files)
            print(f"Uploaded {len(files)} file(s) to S3 for job {job_id}")
        result = client.complete_job(job_id, output_rows=output_rows, files=files)
        print(f"Job {job_id} completed with status={result.get('status')}")
    except Exception as exc:
        client.fail_job(job_id, str(exc))
        print(f"Job {job_id} failed: {exc}")

    return True


def main() -> None:
    load_worker_env()
    client = WorkerApiClient()
    interval = poll_interval_seconds()
    key_hint = f"...{client.api_key[-8:]}" if len(client.api_key) >= 8 else "(short)"
    print(f"Worker started. API={client.base_url} key={key_hint} poll={interval}s")

    while True:
        processed = run_once(client)
        if not processed:
            time.sleep(interval)


if __name__ == "__main__":
    main()
