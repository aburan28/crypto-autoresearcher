"""The object-store interface the rest of the pipeline codes against."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Protocol, runtime_checkable


@dataclass(frozen=True)
class ObjectInfo:
    """One stored object. ``version_id``/``etag`` are None for backends without them."""

    key: str
    size: int
    etag: str | None = None
    version_id: str | None = None
    last_modified: str | None = None
    extra: dict[str, str] = field(default_factory=dict)

    @property
    def uri(self) -> str:  # overridden per backend via ObjectStore.uri()
        return self.key


@runtime_checkable
class ObjectStore(Protocol):
    """Minimal read/write surface. S3 and the filesystem both satisfy it."""

    def list(self, prefix: str) -> Iterator[ObjectInfo]: ...

    def head(self, key: str) -> ObjectInfo | None: ...

    def get(self, key: str) -> bytes: ...

    def put(self, key: str, data: bytes, content_type: str | None = None) -> ObjectInfo: ...

    def delete(self, key: str) -> None: ...

    def exists(self, key: str) -> bool: ...

    def uri(self, key: str) -> str: ...
