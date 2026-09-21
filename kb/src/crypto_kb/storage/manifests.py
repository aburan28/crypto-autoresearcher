"""Manifest persistence.

Manifests live next to the corpus, under ``knowledge/manifests/``, keyed by a
filesystem-safe encoding of the source id. Keeping them in the object store
rather than a database means the derived index and its bookkeeping are deleted
and rebuilt together, and a worker with no local state can resume.
"""

from __future__ import annotations

import json
import re
from typing import Iterator

from crypto_kb.config import MANIFEST_PREFIX
from crypto_kb.models import IngestState, Manifest
from crypto_kb.storage.base import ObjectStore

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def manifest_key(source_id: str) -> str:
    """``paper:eprint-2026-1486`` -> ``knowledge/manifests/paper__eprint-2026-1486.json``."""
    return f"{MANIFEST_PREFIX}{_UNSAFE.sub('__', source_id)}.json"


class ManifestStore:
    def __init__(self, store: ObjectStore) -> None:
        self.store = store

    def get(self, source_id: str) -> Manifest | None:
        key = manifest_key(source_id)
        if not self.store.exists(key):
            return None
        raw = json.loads(self.store.get(key).decode("utf-8"))
        return Manifest.model_validate(raw)

    def put(self, manifest: Manifest) -> None:
        manifest.touch()
        payload = json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True)
        self.store.put(
            manifest_key(manifest.source_id),
            payload.encode("utf-8"),
            content_type="application/json",
        )

    def list(self) -> Iterator[Manifest]:
        for info in self.store.list(MANIFEST_PREFIX):
            if not info.key.endswith(".json"):
                continue
            raw = json.loads(self.store.get(info.key).decode("utf-8"))
            yield Manifest.model_validate(raw)

    def mark_deleted(self, source_id: str) -> Manifest | None:
        """Record a tombstone rather than dropping the manifest.

        A removed manifest is indistinguishable from one that was never
        written, which is exactly the case where a stale Qdrant point would go
        unnoticed. The tombstone keeps the deletion auditable.
        """
        manifest = self.get(source_id)
        if manifest is None:
            return None
        manifest.status = IngestState.DELETED
        manifest.point_ids = []
        manifest.chunk_count = 0
        manifest.parent_chunk_count = 0
        # The document no longer contributes to the corpus statistics; its
        # contribution was retracted before this call.
        manifest.sparse_terms = []
        manifest.sparse_mean_length = 0
        self.put(manifest)
        return manifest

    def by_status(self, status: IngestState) -> list[Manifest]:
        return [m for m in self.list() if m.status == status]
