"""S3 presigned download URLs for job files."""
from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from app.config import settings


def s3_configured() -> bool:
    if not settings.s3_bucket_name:
        return False
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        return True
    # EC2 instance role / default credential chain
    return True


def _s3_client():
    client_kwargs: dict[str, str] = {"region_name": settings.aws_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
        client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.client("s3", **client_kwargs)


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
