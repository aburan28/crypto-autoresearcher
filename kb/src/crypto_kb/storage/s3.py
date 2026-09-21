"""S3-backed object store.

boto3 is imported inside ``__init__`` so importing ``crypto_kb.storage`` does
not require the aws extra. Retries are bounded and jittered -- an ingestion
worker that hammers S3 through a throttle only makes the backlog worse.
"""

from __future__ import annotations

from typing import Any, Iterator

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from crypto_kb.storage.base import ObjectInfo


class S3ObjectStore:
    def __init__(
        self,
        bucket: str,
        region: str | None = None,
        profile: str | None = None,
        endpoint_url: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.bucket = bucket
        if client is not None:
            self.client = client
        else:
            import boto3

            session = boto3.Session(profile_name=profile, region_name=region)
            self.client = session.client("s3", endpoint_url=endpoint_url)

    def uri(self, key: str) -> str:
        return f"s3://{self.bucket}/{key}"

    # -- reads -------------------------------------------------------------

    def list(self, prefix: str) -> Iterator[ObjectInfo]:
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                yield ObjectInfo(
                    key=item["Key"],
                    size=item["Size"],
                    etag=(item.get("ETag") or "").strip('"') or None,
                    last_modified=_iso(item.get("LastModified")),
                )

    def head(self, key: str) -> ObjectInfo | None:
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=key)
        except Exception as exc:  # botocore ClientError, without importing it
            if _is_not_found(exc):
                return None
            raise
        return ObjectInfo(
            key=key,
            size=response.get("ContentLength", 0),
            etag=(response.get("ETag") or "").strip('"') or None,
            version_id=response.get("VersionId"),
            last_modified=_iso(response.get("LastModified")),
        )

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential_jitter(initial=1, max=16),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def get(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def exists(self, key: str) -> bool:
        return self.head(key) is not None

    # -- writes ------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential_jitter(initial=1, max=16),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def put(self, key: str, data: bytes, content_type: str | None = None) -> ObjectInfo:
        kwargs: dict[str, Any] = {"Bucket": self.bucket, "Key": key, "Body": data}
        if content_type:
            kwargs["ContentType"] = content_type
        response = self.client.put_object(**kwargs)
        return ObjectInfo(
            key=key,
            size=len(data),
            etag=(response.get("ETag") or "").strip('"') or None,
            version_id=response.get("VersionId"),
        )

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_not_found(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    if not isinstance(response, dict):
        return False
    code = str(response.get("Error", {}).get("Code", ""))
    return code in {"404", "NoSuchKey", "NotFound"}
