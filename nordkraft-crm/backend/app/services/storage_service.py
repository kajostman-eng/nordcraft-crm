from __future__ import annotations

import boto3

from app.core.config import settings


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT or None,
        aws_access_key_id=settings.S3_ACCESS_KEY or None,
        aws_secret_access_key=settings.S3_SECRET_KEY or None,
        region_name="auto",
    )


def upload_fileobj(*, fileobj, key: str, content_type: str | None) -> str:
    """
    Upload file-like object to S3-compatible storage and return a public URL if possible.
    For private buckets, callers can still store the key and generate signed URLs later.
    """
    client = _s3_client()
    extra = {}
    if content_type:
        extra["ContentType"] = content_type

    client.upload_fileobj(fileobj, settings.S3_BUCKET, key, ExtraArgs=extra or None)

    endpoint = (settings.S3_ENDPOINT or "").rstrip("/")
    if endpoint:
        return f"{endpoint}/{settings.S3_BUCKET}/{key}"
    return ""

