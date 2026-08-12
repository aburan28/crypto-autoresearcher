"""Initial backfill and reconciliation.

Backfill walks the source prefix and ingests everything; reconciliation is the
other half, and the one that is easy to forget. An object deleted from the
corpus while no worker was listening leaves points in the index that no longer
have a source. In a research corpus those are the dangerous rows -- a
retracted result that still answers queries -- so the sweep looks for them
explicitly rather than trusting the event stream to have been complete.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crypto_kb.metadata import METADATA_SUFFIX
from crypto_kb.models import IngestState
from crypto_kb.observability import get_logger
from crypto_kb.ingest.pipeline import IngestionPipeline, IngestResult

log = get_logger("crypto_kb.backfill")


@dataclass
class BackfillReport:
    indexed: list[IngestResult] = field(default_factory=list)
    skipped: list[IngestResult] = field(default_factory=list)
    rejected: list[IngestResult] = field(default_factory=list)
    failed: list[IngestResult] = field(default_factory=list)
    orphans_removed: list[str] = field(default_factory=list)

    @property
    def total_seen(self) -> int:
        return len(self.indexed) + len(self.skipped) + len(self.rejected) + len(self.failed)

    def summary(self) -> dict[str, int]:
        return {
            "indexed": len(self.indexed),
            "skipped": len(self.skipped),
            "rejected": len(self.rejected),
            "failed": len(self.failed),
            "orphans_removed": len(self.orphans_removed),
            "chunks": sum(r.chunk_count for r in self.indexed),
        }


#: Documents between flushes of the corpus-wide sparse statistics. The table
#: is corpus-sized, so writing it per document is quadratic over a backfill;
#: a crash between flushes costs only IDF accuracy for the documents since the
#: last one, and `crypto-kb reindex` recomputes it exactly.
STATS_FLUSH_INTERVAL = 250


def backfill(
    pipeline: IngestionPipeline,
    prefix: str | None = None,
    force: bool = False,
    limit: int | None = None,
    reconcile: bool = True,
) -> BackfillReport:
    prefix = prefix or pipeline.settings.source_prefix()
    report = BackfillReport()
    seen_sources: set[str] = set()

    since_flush = 0
    for info in pipeline.store.list(prefix):
        if info.key.endswith(METADATA_SUFFIX):
            continue
        result = pipeline.ingest_key(info.key, force=force, save_stats=False)
        if result.source_id:
            seen_sources.add(result.source_id)
        _record(report, result)

        since_flush += 1
        if since_flush >= STATS_FLUSH_INTERVAL:
            pipeline.sparse.stats.save(pipeline.store)
            since_flush = 0

        if limit is not None and report.total_seen >= limit:
            break

    pipeline.sparse.stats.save(pipeline.store)

    if reconcile:
        report.orphans_removed = remove_orphans(pipeline, seen_sources)

    log.info("backfill_complete", **report.summary())
    return report


def remove_orphans(pipeline: IngestionPipeline, seen_sources: set[str]) -> list[str]:
    """Delete indexed sources whose object no longer exists."""
    removed: list[str] = []
    for manifest in pipeline.manifests.list():
        if manifest.status != IngestState.INDEXED:
            continue
        if manifest.source_id in seen_sources:
            continue
        if pipeline.store.exists(manifest.s3_key):
            continue
        pipeline.delete_source(manifest.source_id)
        removed.append(manifest.source_id)
        log.info("orphan_removed", source_id=manifest.source_id, key=manifest.s3_key)
    return removed


def _record(report: BackfillReport, result: IngestResult) -> None:
    if result.state == IngestState.INDEXED and result.skipped:
        report.skipped.append(result)
    elif result.state == IngestState.INDEXED:
        report.indexed.append(result)
    elif result.state == IngestState.REJECTED:
        report.rejected.append(result)
    elif result.state == IngestState.FAILED:
        report.failed.append(result)
