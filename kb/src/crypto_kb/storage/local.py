"""Filesystem-backed object store.

Not a test double: it is how the vertical slice runs against this repository's
own corpus without an AWS account, and how the eval harness gets a real,
byte-identical fixture set. Keys use S3 semantics (forward slashes, no leading
slash) so the same code paths run against either backend.
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from crypto_kb.storage.base import ObjectInfo


class LocalObjectStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()

    # -- key/path mapping --------------------------------------------------

    def _path(self, key: str) -> Path:
        if key.startswith("/"):
            raise ValueError(f"object keys must be relative, got {key!r}")
        candidate = (self.root / key).resolve()
        # Traversal guard: keys arrive from S3 event payloads and CLI input,
        # and a `../` in one must not let a write escape the corpus root.
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError(f"key {key!r} escapes the store root")
        return candidate

    def uri(self, key: str) -> str:
        return f"file://{self._path(key)}"

    # -- reads -------------------------------------------------------------

    def list(self, prefix: str) -> Iterator[ObjectInfo]:
        base = self.root / prefix
        # A prefix need not be a directory boundary; walk the nearest existing
        # ancestor and filter, matching S3's prefix semantics.
        walk_root = base if base.is_dir() else base.parent
        if not walk_root.exists():
            return
        for dirpath, _dirnames, filenames in os.walk(walk_root):
            for name in sorted(filenames):
                path = Path(dirpath) / name
                key = str(path.relative_to(self.root)).replace(os.sep, "/")
                if not key.startswith(prefix):
                    continue
                yield self._info(key, path)

    def head(self, key: str) -> ObjectInfo | None:
        path = self._path(key)
        if not path.is_file():
            return None
        return self._info(key, path)

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    # -- writes ------------------------------------------------------------

    def put(self, key: str, data: bytes, content_type: str | None = None) -> ObjectInfo:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write-then-rename: a crashed ingest must not leave a half-written
        # manifest that the next pass reads as authoritative state.
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)
        return self._info(key, path)

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.is_file():
            path.unlink()

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _info(key: str, path: Path) -> ObjectInfo:
        stat = path.stat()
        digest = hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        return ObjectInfo(
            key=key,
            size=stat.st_size,
            etag=digest,
            version_id=None,
            last_modified=modified.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )
