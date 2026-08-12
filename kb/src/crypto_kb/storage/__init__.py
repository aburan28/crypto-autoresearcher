"""Object storage: the corpus source of truth, and where derived artifacts go."""

from crypto_kb.storage.base import ObjectInfo, ObjectStore
from crypto_kb.storage.local import LocalObjectStore
from crypto_kb.storage.manifests import ManifestStore

__all__ = ["ObjectInfo", "ObjectStore", "LocalObjectStore", "ManifestStore", "build_store"]


def build_store(settings=None) -> ObjectStore:
    """Construct the configured object store.

    boto3 is imported only on the s3 path, so a local-only install never needs
    the aws extra.
    """
    from crypto_kb.config import get_settings

    settings = settings or get_settings()
    if settings.store_backend == "local":
        return LocalObjectStore(settings.local_root)
    if settings.store_backend == "s3":
        from crypto_kb.storage.s3 import S3ObjectStore

        return S3ObjectStore(
            bucket=settings.s3_bucket,
            region=settings.aws_region,
            profile=settings.aws_profile,
            endpoint_url=settings.s3_endpoint_url,
        )
    raise ValueError(f"unknown store_backend {settings.store_backend!r} (expected 'local' or 's3')")
