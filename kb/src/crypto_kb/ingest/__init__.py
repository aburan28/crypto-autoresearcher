"""Ingestion: an idempotent state machine from object key to indexed chunks."""

from crypto_kb.ingest.pipeline import IngestionPipeline, IngestResult, build_pipeline

__all__ = ["IngestionPipeline", "IngestResult", "build_pipeline"]
