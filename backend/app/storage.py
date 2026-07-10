"""S3 presigned download URLs for job files."""
from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from app.config import settings


def s3_configured() -> bool:
    return bool(settings.s3_bucket_name)


def _s3_client():
    return boto3.client("s3", region_name=settings.aws_region)


def create_presigned_download_url(s3_key: str, filename: str) -> str:
    if not s3_configured():
        raise RuntimeError("S3_BUCKET_NAME is not configured")

    try:
        return _s3_client().generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.s3_bucket_name,
                "Key": s3_key,
                "ResponseContentDisposition": f'attachment; filename="{filename}"',
            },
            ExpiresIn=settings.s3_presign_expire_seconds,
        )
    except ClientError as exc:
        raise RuntimeError("Failed to create download URL") from exc
