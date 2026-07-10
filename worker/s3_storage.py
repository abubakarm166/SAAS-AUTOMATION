"""Upload job output files to S3."""
from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Any


def s3_enabled() -> bool:
    return bool(os.getenv("S3_BUCKET_NAME", "").strip())


def _s3_client():
    import boto3

    region = os.getenv("AWS_REGION", "eu-north-1")
    return boto3.client("s3", region_name=region)


def build_s3_key(user_id: str, job_id: str, filename: str) -> str:
    safe_name = filename.replace("\\", "/").split("/")[-1]
    return f"jobs/{user_id}/{job_id}/{safe_name}"


def upload_job_files(job: dict[str, Any], files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Upload local files to S3 and return file metadata with s3_key set.

    Skips upload when S3_BUCKET_NAME is unset or local_path is missing.
    """
    if not s3_enabled():
        return [{k: v for k, v in f.items() if k != "local_path"} for f in files]

    bucket = os.environ["S3_BUCKET_NAME"].strip()
    user_id = str(job["user_id"])
    job_id = str(job["id"])
    client = _s3_client()
    uploaded: list[dict[str, Any]] = []

    for file_info in files:
        local_path = file_info.get("local_path")
        filename = file_info.get("filename", "report.pdf")
        file_type = file_info.get("file_type", "pdf")
        entry = {
            "file_type": file_type,
            "filename": filename,
            "s3_key": file_info.get("s3_key"),
        }

        if not local_path:
            uploaded.append(entry)
            continue

        path = Path(local_path)
        if not path.is_file():
            raise RuntimeError(f"Output file not found for upload: {local_path}")

        s3_key = build_s3_key(user_id, job_id, filename)
        content_type, _ = mimetypes.guess_type(filename)
        extra_args: dict[str, str] = {}
        if content_type:
            extra_args["ContentType"] = content_type

        if extra_args:
            client.upload_file(str(path), bucket, s3_key, ExtraArgs=extra_args)
        else:
            client.upload_file(str(path), bucket, s3_key)
        entry["s3_key"] = s3_key
        uploaded.append(entry)

    return uploaded
